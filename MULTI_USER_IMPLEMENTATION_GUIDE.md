# 多用户并发控制实现指南

## 📋 实现步骤

### 1. 数据库迁移

创建迁移脚本添加用户字段：

```sql
-- 为tasks表添加用户字段
ALTER TABLE tasks 
ADD COLUMN user_id INT NULL COMMENT '用户ID',
ADD COLUMN user_name VARCHAR(50) NULL COMMENT '用户名';

-- 添加索引
CREATE INDEX idx_user_id ON tasks(user_id);
CREATE INDEX idx_user_status ON tasks(user_id, status);

-- 为现有任务分配默认用户（admin，user_id=1）
UPDATE tasks SET user_id = 1, user_name = 'admin' WHERE user_id IS NULL;

-- 为sessions表添加用户字段
ALTER TABLE sessions 
ADD COLUMN user_id INT NULL COMMENT '用户ID',
ADD COLUMN task_id INT NULL COMMENT '关联任务ID';

-- 添加索引
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_task_id ON sessions(task_id);

-- 添加外键约束
ALTER TABLE sessions 
ADD CONSTRAINT fk_sessions_task_id 
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL;
```

### 2. 更新TaskExecutor集成并发控制

在`executor.py`中集成并发控制器：

```python
from ..core.concurrency_controller import get_global_concurrency_controller
from ..core.isolated_browser_pool import get_global_isolated_pool

async def execute_task(
    self,
    task_id: str,
    user_id: int,  # 新增：用户ID参数
    db_session: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """执行任务 - 带并发控制"""
    # 1. 检查并发限制
    controller = get_global_concurrency_controller()
    can_execute, message = await controller.can_execute_task(user_id, task_id)
    if not can_execute:
        return {
            "success": False,
            "message": message,
            "task_id": task_id
        }
    
    try:
        # 2. 注册任务
        await controller.register_task(user_id, task_id, 'running')
        
        # 3. 获取隔离的浏览器实例
        isolated_pool = get_global_isolated_pool()
        browser_instance = await isolated_pool.get_browser(
            user_id=user_id,
            task_id=task_id
        )
        
        # 4. 执行任务...
        # ...
        
    finally:
        # 5. 释放资源
        await isolated_pool.release_browser(user_id, task_id)
        await controller.release_task(user_id, task_id)
```

### 3. 更新API路由添加用户验证

在`tasks.py`路由中添加用户验证：

```python
from fastapi import Depends, HTTPException
from ...auth import get_current_user  # 假设有用户认证依赖

@router.post("/{task_id}/execute")
async def execute_task(
    task_id: str,
    current_user: User = Depends(get_current_user),  # 获取当前用户
    db: AsyncSession = Depends(get_db)
):
    """执行任务 - 带用户验证和并发控制"""
    # 1. 获取任务
    task = await get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 2. 验证用户权限
    if task.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作此任务")
    
    # 3. 执行任务（自动进行并发控制）
    executor = get_global_executor(db_session=db)
    result = await executor.execute_task(
        task_id=task_id,
        user_id=current_user.user_id,  # 传递用户ID
        db_session=db
    )
    return result

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

### 4. 更新TaskManager添加用户过滤

在`task_manager.py`中：

```python
async def list_tasks(
    self,
    user_id: int,  # 新增：用户ID参数
    db_session: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None
) -> List[Task]:
    """查询任务列表 - 按用户过滤"""
    query = select(TaskModel).where(TaskModel.user_id == user_id)
    
    if status:
        query = query.where(TaskModel.status == status)
    
    query = query.order_by(TaskModel.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db_session.execute(query)
    tasks = result.scalars().all()
    
    return [Task.from_db_model(task) for task in tasks]
```

### 5. 启动时初始化并发控制器

在应用启动时：

```python
from automation_framework.src.core.concurrency_controller import get_global_concurrency_controller

@app.on_event("startup")
async def startup_event():
    # 启动并发控制器
    controller = get_global_concurrency_controller()
    await controller.start()

@app.on_event("shutdown")
async def shutdown_event():
    # 停止并发控制器
    controller = get_global_concurrency_controller()
    await controller.stop()
    
    # 停止隔离浏览器池
    from automation_framework.src.core.isolated_browser_pool import get_global_isolated_pool
    isolated_pool = get_global_isolated_pool()
    await isolated_pool.stop_all()
```

---

## 🔧 配置说明

### 环境变量
```bash
# 并发控制配置
AUTOMATION_MAX_CONCURRENT_PER_USER=5
AUTOMATION_MAX_GLOBAL_CONCURRENT=100
AUTOMATION_MAX_BROWSER_INSTANCES_PER_USER=3
AUTOMATION_TASK_TIMEOUT=3600
```

### 配置文件
```python
# config/automation.py
AUTOMATION_CONFIG = {
    "max_concurrent_per_user": 5,
    "max_global_concurrent": 100,
    "max_browser_instances_per_user": 3,
    "task_timeout": 3600,
    "browser_pool_size": 10,
    "max_idle_time": 300
}
```

---

## ✅ 测试检查清单

### 功能测试
- [ ] 用户只能看到自己的任务
- [ ] 用户无法操作其他用户的任务
- [ ] 并发限制正确生效
- [ ] 资源正确释放
- [ ] 浏览器实例隔离

### 性能测试
- [ ] 支持多用户并发
- [ ] 资源使用合理
- [ ] 无内存泄漏
- [ ] 响应时间正常

### 安全测试
- [ ] 权限验证正确
- [ ] 数据隔离完整
- [ ] 无越权访问
- [ ] 审计日志完整

---

## 📝 注意事项

1. **向后兼容**：现有任务需要分配默认用户（admin）
2. **性能考虑**：浏览器实例池大小需要根据服务器资源调整
3. **监控告警**：需要监控并发任务数和资源使用情况
4. **用户配置**：可以考虑支持用户级别的并发限制配置
