# 多用户并发控制设计方案

## 📋 问题分析

在多用户环境下，需要解决以下问题：
1. **用户隔离**：确保用户只能看到和操作自己的任务
2. **资源隔离**：每个任务使用独立的浏览器实例，避免相互干扰
3. **并发控制**：合理分配资源，防止资源耗尽
4. **权限控制**：防止用户越权操作其他用户的任务
5. **资源限制**：限制每个用户的并发任务数，防止滥用

---

## 🎯 解决方案

### 1. 用户隔离机制

#### 1.1 数据模型增强

**修改Task模型，添加用户关联**：
```python
class Task(Base):
    # ... 现有字段 ...
    user_id = Column(Integer, ForeignKey('sys_user.user_id'), nullable=False, comment='用户ID')
    user_name = Column(String(50), nullable=True, comment='用户名')
    
    # 添加索引
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_user_status', 'user_id', 'status'),
        # ... 其他索引
    )
```

**修改Session模型，添加用户关联**：
```python
class Session(Base):
    # ... 现有字段 ...
    user_id = Column(Integer, ForeignKey('sys_user.user_id'), nullable=False, comment='用户ID')
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True, comment='关联任务ID')
```

#### 1.2 查询过滤

所有任务查询都需要添加用户过滤：
```python
async def list_tasks(
    user_id: int,
    db_session: AsyncSession,
    skip: int = 0,
    limit: int = 10
):
    """查询用户的任务列表"""
    query = select(Task).where(Task.user_id == user_id)
    # ... 其他过滤条件
```

---

### 2. 资源隔离机制

#### 2.1 浏览器实例隔离

**每个任务使用独立的浏览器上下文**：
```python
class BrowserContextManager:
    """浏览器上下文管理器 - 确保每个任务使用独立的上下文"""
    
    async def create_context(
        self,
        task_id: str,
        user_id: int,
        config: Dict[str, Any]
    ) -> BrowserContext:
        """创建独立的浏览器上下文"""
        # 使用Playwright的context隔离
        context = await browser.new_context(
            # 隔离配置
            viewport={'width': 1920, 'height': 1080},
            user_agent=config.get('user_agent'),
            # 每个上下文独立的Cookie和LocalStorage
            storage_state=None,  # 不使用共享状态
            # 隔离网络请求
            ignore_https_errors=config.get('ignore_https_errors', False)
        )
        
        # 记录上下文与任务的关联
        self._contexts[f"{user_id}_{task_id}"] = context
        return context
```

#### 2.2 会话隔离

**每个任务创建独立的会话**：
```python
async def execute_task(self, task_id: str, user_id: int, db_session: AsyncSession):
    """执行任务 - 自动创建隔离的会话"""
    # 创建独立的会话
    session = await session_manager.create_session(
        driver_type=task.driver_type,
        user_id=user_id,
        task_id=task_id,
        metadata={
            'user_id': user_id,
            'task_id': task_id,
            'isolation_level': 'full'  # 完全隔离
        },
        db_session=db_session
    )
    
    # 使用独立的浏览器上下文
    context = await browser_context_manager.create_context(
        task_id=task_id,
        user_id=user_id,
        config=task.config
    )
    
    # 执行任务...
```

---

### 3. 并发控制机制

#### 3.1 用户级并发限制

**限制每个用户的最大并发任务数**：
```python
class ConcurrencyController:
    """并发控制器"""
    
    def __init__(self):
        self._user_tasks: Dict[int, Set[str]] = {}  # user_id -> set of task_ids
        self._max_concurrent_per_user = 5  # 每个用户最多5个并发任务
        self._lock = asyncio.Lock()
    
    async def can_execute_task(
        self,
        user_id: int,
        task_id: str
    ) -> Tuple[bool, str]:
        """检查是否可以执行任务"""
        async with self._lock:
            user_tasks = self._user_tasks.get(user_id, set())
            
            # 检查是否超过并发限制
            running_tasks = [
                tid for tid in user_tasks 
                if self._is_task_running(tid)
            ]
            
            if len(running_tasks) >= self._max_concurrent_per_user:
                return False, f"用户已达到最大并发任务数限制（{self._max_concurrent_per_user}）"
            
            # 检查任务是否已在运行
            if task_id in user_tasks:
                return False, "任务已在运行中"
            
            # 允许执行
            user_tasks.add(task_id)
            return True, ""
    
    async def release_task(self, user_id: int, task_id: str):
        """释放任务"""
        async with self._lock:
            if user_id in self._user_tasks:
                self._user_tasks[user_id].discard(task_id)
```

#### 3.2 全局资源池管理

**使用浏览器实例池，但确保隔离**：
```python
class IsolatedBrowserPool:
    """隔离的浏览器实例池"""
    
    def __init__(self):
        self._pools: Dict[int, BrowserPool] = {}  # user_id -> BrowserPool
        self._max_pool_size = 3  # 每个用户最多3个浏览器实例
        self._lock = asyncio.Lock()
    
    async def get_browser(
        self,
        user_id: int,
        task_id: str,
        timeout: float = 30.0
    ) -> BrowserInstance:
        """获取浏览器实例（用户隔离）"""
        async with self._lock:
            # 为每个用户创建独立的池
            if user_id not in self._pools:
                self._pools[user_id] = BrowserPool(
                    pool_size=self._max_pool_size,
                    browser_type=BrowserType.CHROMIUM,
                    headless=True
                )
                await self._pools[user_id].start()
            
            pool = self._pools[user_id]
            instance = await pool.acquire_browser(timeout=timeout)
            
            # 为任务创建独立的上下文
            context = await instance.driver.create_context(
                task_id=task_id,
                user_id=user_id
            )
            
            return instance
```

---

### 4. 权限控制机制

#### 4.1 API层权限检查

**在所有任务操作API中添加用户验证**：
```python
@router.post("/{task_id}/execute")
async def execute_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """执行任务 - 检查用户权限"""
    # 获取任务
    task = await get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查用户权限
    if task.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作此任务")
    
    # 检查并发限制
    controller = get_concurrency_controller()
    can_execute, message = await controller.can_execute_task(
        current_user.user_id,
        task_id
    )
    if not can_execute:
        raise HTTPException(status_code=429, detail=message)
    
    # 执行任务
    executor = get_global_executor(db_session=db)
    result = await executor.execute_task(task_id, db_session=db)
    return result
```

#### 4.2 查询过滤

**所有查询都自动过滤用户**：
```python
@router.get("/list")
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """查询任务列表 - 自动过滤用户"""
    task_manager = get_global_task_manager(db_session=db)
    tasks = await task_manager.list_tasks(
        user_id=current_user.user_id,  # 只查询当前用户的任务
        db_session=db,
        skip=skip,
        limit=limit
    )
    return tasks
```

---

### 5. 资源限制配置

#### 5.1 配置项

```python
class ConcurrencyConfig:
    """并发配置"""
    # 每个用户的最大并发任务数
    MAX_CONCURRENT_TASKS_PER_USER = 5
    
    # 每个用户的最大浏览器实例数
    MAX_BROWSER_INSTANCES_PER_USER = 3
    
    # 全局最大并发任务数
    MAX_GLOBAL_CONCURRENT_TASKS = 100
    
    # 浏览器实例池大小
    BROWSER_POOL_SIZE = 10
    
    # 桌面任务互斥锁超时
    DESKTOP_LOCK_TIMEOUT = 300  # 5分钟
```

#### 5.2 动态配置

**支持从数据库或配置文件读取**：
```python
async def get_user_concurrency_limit(user_id: int) -> int:
    """获取用户的并发限制（可以从用户配置或VIP等级获取）"""
    # 普通用户：5个并发任务
    # VIP用户：10个并发任务
    # 企业用户：20个并发任务
    
    user = await get_user(user_id)
    if user.is_vip:
        return 10
    elif user.is_enterprise:
        return 20
    else:
        return 5
```

---

## 🔧 实现步骤

### 阶段一：数据模型增强

1. **修改Task模型**
   - 添加`user_id`字段
   - 添加`user_name`字段（冗余，便于查询）
   - 添加用户相关索引

2. **修改Session模型**
   - 添加`user_id`字段
   - 添加`task_id`字段（关联任务）

3. **数据库迁移**
   - 创建迁移脚本
   - 为现有任务分配默认用户（admin）

### 阶段二：并发控制器实现

1. **实现ConcurrencyController**
   - 用户级并发限制
   - 任务状态跟踪
   - 资源释放机制

2. **实现IsolatedBrowserPool**
   - 用户隔离的浏览器池
   - 上下文创建和管理
   - 资源清理

### 阶段三：API层改造

1. **添加用户认证依赖**
   - 从JWT token获取用户信息
   - 验证用户权限

2. **修改所有任务API**
   - 添加用户过滤
   - 添加权限检查
   - 添加并发控制

### 阶段四：TaskExecutor改造

1. **集成并发控制器**
   - 执行前检查并发限制
   - 执行后释放资源

2. **集成隔离浏览器池**
   - 使用隔离的浏览器实例
   - 确保上下文隔离

---

## 📊 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  User Authentication & Authorization            │   │
│  │  - JWT Token验证                                 │   │
│  │  - 用户权限检查                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Concurrency Controller                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  - 用户级并发限制检查                            │   │
│  │  - 任务状态跟踪                                  │   │
│  │  - 资源分配管理                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Task Executor                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  - 任务执行逻辑                                  │   │
│  │  - 状态管理                                      │   │
│  │  - 错误处理                                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Isolated Browser Pool (Per User)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ User 1 Pool  │  │ User 2 Pool  │  │ User 3 Pool  │  │
│  │ - Instance1 │  │ - Instance1  │  │ - Instance1  │  │
│  │ - Instance2 │  │ - Instance2  │  │ - Instance2  │  │
│  │ - Instance3 │  │ - Instance3   │  │ - Instance3   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Browser Contexts (Per Task)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Context1 │  │ Context2 │  │ Context3 │  ...         │
│  │ (Isolated)│ │(Isolated)│ │(Isolated)│              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## 🔒 安全考虑

### 1. 数据隔离
- ✅ 数据库查询自动过滤用户
- ✅ API层权限验证
- ✅ 防止SQL注入和越权访问

### 2. 资源隔离
- ✅ 每个任务使用独立的浏览器上下文
- ✅ Cookie和LocalStorage完全隔离
- ✅ 网络请求隔离

### 3. 并发控制
- ✅ 用户级并发限制
- ✅ 全局资源池管理
- ✅ 防止资源耗尽

### 4. 审计日志
- ✅ 记录所有任务操作
- ✅ 记录用户操作历史
- ✅ 异常行为监控

---

## 📝 配置示例

### 环境变量配置
```bash
# 并发控制配置
MAX_CONCURRENT_TASKS_PER_USER=5
MAX_BROWSER_INSTANCES_PER_USER=3
MAX_GLOBAL_CONCURRENT_TASKS=100
BROWSER_POOL_SIZE=10

# 资源限制
MAX_TASK_DURATION=3600  # 任务最大执行时长（秒）
MAX_MEMORY_PER_TASK=512  # 每个任务最大内存（MB）
```

### 数据库配置表
```sql
CREATE TABLE sys_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value VARCHAR(255),
    config_type VARCHAR(50),
    remark VARCHAR(500)
);

-- 插入默认配置
INSERT INTO sys_config VALUES 
('automation.max_concurrent_tasks_per_user', '5', 'number', '每个用户最大并发任务数'),
('automation.max_browser_instances_per_user', '3', 'number', '每个用户最大浏览器实例数'),
('automation.max_global_concurrent_tasks', '100', 'number', '全局最大并发任务数');
```

---

## ✅ 验收标准

### 功能验收
- [ ] 用户只能看到和操作自己的任务
- [ ] 每个任务使用独立的浏览器上下文
- [ ] 用户并发任务数不超过限制
- [ ] 资源正确释放，无内存泄漏
- [ ] 权限验证正确，防止越权操作

### 性能验收
- [ ] 支持至少100个并发用户
- [ ] 每个用户最多5个并发任务
- [ ] 浏览器实例正确复用和清理
- [ ] 响应时间 < 2秒

### 安全验收
- [ ] 数据完全隔离，无数据泄露
- [ ] 权限验证正确，无越权访问
- [ ] 资源限制有效，防止滥用
- [ ] 审计日志完整

---

## 🚀 实施优先级

1. **P0（紧急）**：用户隔离、权限控制
2. **P1（重要）**：并发控制、资源隔离
3. **P2（一般）**：资源限制、性能优化
4. **P3（可选）**：动态配置、审计日志
