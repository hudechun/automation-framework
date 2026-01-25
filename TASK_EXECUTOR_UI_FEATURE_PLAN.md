# 任务执行器UI+功能一体化开发计划

## 📋 概述

本文档制定了任务执行器的UI设计和功能实现一体化开发计划。按照"先UI设计，后功能实现"的原则，确保UI和功能完美配合。

## 🎯 核心目标

1. **自然语言任务输入**：用户可以通过自然语言描述任务，系统自动解析为可执行的操作序列
2. **任务执行监控**：实时显示任务执行进度、状态、日志
3. **完善的执行器**：支持状态机、上下文管理、进度追踪、错误处理和重试
4. **AI集成**：将TaskPlanner和Agent集成到TaskExecutor中

---

## 阶段一：UI设计（先完成）

### 1.1 任务创建页面增强 - 自然语言输入模式

#### UI设计要点
- **双模式切换**：支持"自然语言模式"和"手动配置模式"切换
- **自然语言输入框**：大文本区域，支持多行输入，带示例提示
- **实时解析预览**：输入后显示解析后的操作序列预览
- **解析状态指示**：显示"解析中..."、"解析成功"、"解析失败"状态
- **操作序列编辑**：解析后允许用户编辑和调整操作序列

#### 具体实现

**文件**：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/automation/task/create-nl.vue`（新建）

**功能点**：
1. 模式切换组件（自然语言/手动配置）
2. 自然语言输入区域（带示例和提示）
3. 解析按钮和状态显示
4. 解析结果预览（操作序列列表）
5. 操作序列编辑器（可编辑、删除、调整顺序）
6. 保存为任务

**API接口需求**：
- `POST /automation/api/tasks/parse` - 解析自然语言任务
- `POST /automation/api/tasks/validate-actions` - 验证操作序列

---

### 1.2 任务执行监控页面

#### UI设计要点
- **实时进度条**：显示当前执行进度（已完成操作数/总操作数）
- **执行状态卡片**：显示当前状态、开始时间、预计剩余时间
- **操作执行列表**：实时显示每个操作的执行状态（待执行/执行中/成功/失败）
- **实时日志**：显示执行过程中的日志信息
- **控制按钮**：暂停、恢复、停止按钮
- **错误详情**：展开显示错误信息和堆栈

#### 具体实现

**文件**：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/automation/task/execution-monitor.vue`（新建）

**功能点**：
1. 执行进度可视化（进度条、百分比）
2. 实时状态更新（WebSocket或轮询）
3. 操作列表展示（带状态图标）
4. 日志流式显示（自动滚动）
5. 控制操作（暂停/恢复/停止）
6. 错误详情弹窗

**API接口需求**：
- `GET /automation/api/tasks/{task_id}/execution/status` - 获取执行状态
- `GET /automation/api/tasks/{task_id}/execution/progress` - 获取执行进度
- `GET /automation/api/tasks/{task_id}/execution/logs` - 获取执行日志
- `WebSocket /automation/api/tasks/{task_id}/execution/stream` - 实时流式更新（可选）

---

### 1.3 任务列表页面增强

#### UI设计要点
- **执行状态列**：显示任务当前执行状态（待执行/执行中/已暂停/已完成/已失败）
- **快速操作**：执行、暂停、恢复、停止按钮
- **执行进度**：执行中的任务显示进度条
- **最近执行记录**：显示最近一次执行的简要信息

#### 具体实现

**文件**：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/automation/task/index.vue`（修改）

**增强点**：
1. 执行状态列（带状态图标和颜色）
2. 执行进度列（进度条组件）
3. 操作按钮组（执行/暂停/恢复/停止）
4. 点击任务名称跳转到执行监控页面

---

## 阶段二：后端功能实现（UI完成后）

### 2.1 自然语言任务解析API

#### 功能实现

**文件**：`automation-framework/src/api/routers/tasks.py`（修改）

**新增接口**：
```python
@router.post("/parse", response_model=Dict[str, Any])
async def parse_natural_language_task(
    request: NaturalLanguageTaskRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    解析自然语言任务描述为操作序列
    
    Args:
        request: 包含自然语言描述的请求
        db: 数据库会话
        
    Returns:
        解析后的操作序列和任务描述
    """
    # 1. 调用TaskPlanner解析任务
    # 2. 生成操作计划
    # 3. 转换为Action对象列表
    # 4. 返回解析结果
```

**依赖模块**：
- `TaskPlanner.parse_task()` - 解析自然语言
- `TaskPlanner.plan()` - 生成操作计划
- `action_serializer` - 序列化Action对象

---

### 2.2 TaskExecutor集成自然语言解析

#### 功能实现

**文件**：`automation-framework/src/task/executor.py`（修改）

**增强点**：
1. **自然语言任务支持**：
   - 检测任务是否为自然语言描述
   - 如果是，调用TaskPlanner解析
   - 将解析结果转换为Action序列
   - 保存解析后的操作序列到任务

2. **执行前预处理**：
   ```python
   async def _prepare_task(self, task: Task, db: AsyncSession):
       """准备任务执行"""
       # 如果是自然语言任务，先解析
       if task.is_natural_language:
           agent = self._create_agent(task.config)
           parsed = await agent.planner.parse_task(task.description)
           plan = await agent.planner.plan(parsed)
           task.actions = self._convert_plan_to_actions(plan)
           # 保存解析后的操作序列
           await self._save_parsed_actions(task, db)
   ```

---

### 2.3 完善TaskExecutor核心逻辑

#### 2.3.1 执行状态机

**实现**：
```python
class ExecutionStateMachine:
    """执行状态机"""
    TRANSITIONS = {
        ExecutionState.CREATED: [ExecutionState.RUNNING],
        ExecutionState.RUNNING: [ExecutionState.PAUSED, ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.STOPPED],
        ExecutionState.PAUSED: [ExecutionState.RUNNING, ExecutionState.STOPPED],
        ExecutionState.STOPPED: [],
        ExecutionState.COMPLETED: [],
        ExecutionState.FAILED: [ExecutionState.RUNNING]  # 可以重试
    }
    
    def can_transition(self, from_state: ExecutionState, to_state: ExecutionState) -> bool:
        """检查状态转换是否合法"""
        return to_state in self.TRANSITIONS.get(from_state, [])
```

#### 2.3.2 执行上下文管理

**实现**：
```python
class ExecutionContext:
    """执行上下文"""
    def __init__(self):
        self.current_action_index: int = 0
        self.variables: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        self.checkpoint_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "current_action_index": self.current_action_index,
            "variables": self.variables,
            "state": self.state,
            "checkpoint_data": self.checkpoint_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionContext':
        """从字典反序列化"""
        ctx = cls()
        ctx.current_action_index = data.get("current_action_index", 0)
        ctx.variables = data.get("variables", {})
        ctx.state = data.get("state", {})
        ctx.checkpoint_data = data.get("checkpoint_data")
        return ctx
```

#### 2.3.3 执行进度追踪

**实现**：
```python
class ExecutionProgress:
    """执行进度追踪"""
    def __init__(self, total_actions: int):
        self.total_actions = total_actions
        self.completed_actions = 0
        self.failed_actions = 0
        self.current_action_index = 0
        self.start_time: Optional[datetime] = None
        self.last_update_time: Optional[datetime] = None
    
    @property
    def progress_percentage(self) -> float:
        """计算进度百分比"""
        if self.total_actions == 0:
            return 0.0
        return (self.completed_actions / self.total_actions) * 100
    
    @property
    def estimated_remaining_time(self) -> Optional[timedelta]:
        """估算剩余时间"""
        if not self.start_time or self.completed_actions == 0:
            return None
        elapsed = datetime.now() - self.start_time
        avg_time_per_action = elapsed / self.completed_actions
        remaining_actions = self.total_actions - self.completed_actions
        return avg_time_per_action * remaining_actions
```

#### 2.3.4 操作执行结果验证

**实现**：
```python
async def _execute_action_with_validation(
    self,
    action: Action,
    driver: Driver,
    context: ExecutionContext
) -> Dict[str, Any]:
    """执行操作并验证结果"""
    try:
        # 执行操作
        result = await action.execute(driver)
        
        # 验证结果
        if action.has_validation():
            validation_result = await action.validate(result, driver)
            if not validation_result.success:
                raise ActionValidationError(
                    f"Action validation failed: {validation_result.message}"
                )
        
        return {
            "success": True,
            "result": result,
            "validation": validation_result if action.has_validation() else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
```

#### 2.3.5 执行超时控制

**实现**：
```python
async def _execute_task_with_timeout(
    self,
    task: Task,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """带超时控制的任务执行"""
    timeout = timeout or task.config.get("timeout", 3600)  # 默认1小时
    
    try:
        return await asyncio.wait_for(
            self._execute_task_async(task),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        # 超时处理
        await self._handle_timeout(task)
        raise TaskTimeoutError(f"Task execution timeout after {timeout} seconds")
```

---

### 2.4 执行进度追踪API

#### 功能实现

**文件**：`automation-framework/src/api/routers/tasks.py`（修改）

**新增接口**：
```python
@router.get("/{task_id}/execution/status")
async def get_execution_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务执行状态"""
    executor = get_global_executor(db_session=db)
    state = executor.get_execution_state(task_id)
    progress = executor.get_execution_progress(task_id)
    
    return {
        "task_id": task_id,
        "state": state.value if state else None,
        "progress": progress.to_dict() if progress else None
    }

@router.get("/{task_id}/execution/progress")
async def get_execution_progress(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务执行进度"""
    executor = get_global_executor(db_session=db)
    progress = executor.get_execution_progress(task_id)
    
    return progress.to_dict() if progress else {
        "total_actions": 0,
        "completed_actions": 0,
        "progress_percentage": 0.0
    }

@router.get("/{task_id}/execution/logs")
async def get_execution_logs(
    task_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取任务执行日志"""
    # 从ExecutionRecord或SystemLog查询日志
    pass
```

---

### 2.5 错误处理和重试机制

#### 功能实现

**文件**：`automation-framework/src/task/executor.py`（修改）

**实现**：
```python
class RetryStrategy:
    """重试策略"""
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
    
    def get_delay(self, attempt: int) -> float:
        """计算重试延迟（指数退避）"""
        return self.initial_delay * (self.backoff_factor ** attempt)

class ErrorClassifier:
    """错误分类器"""
    RECOVERABLE_ERRORS = [
        "TimeoutError",
        "ElementNotFoundError",
        "NetworkError",
        "TemporaryError"
    ]
    
    UNRECOVERABLE_ERRORS = [
        "InvalidTaskError",
        "PermissionError",
        "ConfigurationError"
    ]
    
    def classify(self, error: Exception) -> str:
        """分类错误"""
        error_type = type(error).__name__
        if error_type in self.RECOVERABLE_ERRORS:
            return "recoverable"
        elif error_type in self.UNRECOVERABLE_ERRORS:
            return "unrecoverable"
        else:
            return "unknown"

async def _execute_action_with_retry(
    self,
    action: Action,
    driver: Driver,
    context: ExecutionContext,
    retry_strategy: RetryStrategy
) -> Dict[str, Any]:
    """带重试的操作执行"""
    error_classifier = ErrorClassifier()
    last_error = None
    
    for attempt in range(retry_strategy.max_retries + 1):
        try:
            result = await self._execute_action_with_validation(action, driver, context)
            if result["success"]:
                return result
            else:
                last_error = Exception(result["error"])
        except Exception as e:
            last_error = e
            
            # 检查错误类型
            error_type = error_classifier.classify(e)
            if error_type == "unrecoverable":
                # 不可恢复错误，直接失败
                raise
            
            # 可恢复错误，尝试重试
            if attempt < retry_strategy.max_retries:
                delay = retry_strategy.get_delay(attempt)
                logger.warning(
                    f"Action failed (attempt {attempt + 1}/{retry_strategy.max_retries + 1}), "
                    f"retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)
            else:
                # 重试次数用尽
                raise
    
    # 所有重试都失败
    raise last_error
```

---

## 阶段三：集成测试

### 3.1 UI功能测试
- [ ] 自然语言输入和解析
- [ ] 操作序列预览和编辑
- [ ] 任务创建和保存
- [ ] 执行监控页面实时更新
- [ ] 控制操作（暂停/恢复/停止）

### 3.2 后端功能测试
- [ ] 自然语言解析准确性
- [ ] 任务执行完整流程
- [ ] 状态机转换正确性
- [ ] 进度追踪准确性
- [ ] 错误处理和重试机制
- [ ] 超时控制

### 3.3 端到端测试
- [ ] 完整任务创建到执行流程
- [ ] 自然语言任务执行
- [ ] 暂停和恢复功能
- [ ] 错误恢复和重试

---

## 📝 开发顺序建议

1. **第一步**：UI设计
   - 创建自然语言任务输入页面
   - 创建任务执行监控页面
   - 增强任务列表页面

2. **第二步**：后端API（与UI对接）
   - 实现自然语言解析API
   - 实现执行状态和进度API
   - 实现日志查询API

3. **第三步**：TaskExecutor核心功能
   - 集成自然语言解析
   - 实现状态机
   - 实现上下文管理
   - 实现进度追踪
   - 实现错误处理和重试

4. **第四步**：集成和测试
   - 前后端联调
   - 功能测试
   - 性能测试

---

## 🔗 相关文件

### UI文件
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/automation/task/create-nl.vue`（新建）
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/automation/task/execution-monitor.vue`（新建）
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/automation/task/index.vue`（修改）

### 后端文件
- `automation-framework/src/task/executor.py`（修改）
- `automation-framework/src/api/routers/tasks.py`（修改）
- `automation-framework/src/ai/agent.py`（可能需要修改）
- `automation-framework/src/core/execution_context.py`（新建）
- `automation-framework/src/core/error_handler.py`（新建）

---

## ✅ 验收标准

1. **UI验收**：
   - 用户可以输入自然语言任务描述
   - 系统能够解析并显示操作序列
   - 用户可以查看实时执行进度
   - 用户可以控制任务执行（暂停/恢复/停止）

2. **功能验收**：
   - 自然语言任务能够正确解析为操作序列
   - 任务能够完整执行所有操作
   - 执行状态能够正确转换
   - 进度能够准确追踪
   - 错误能够自动重试或正确处理

3. **性能验收**：
   - 自然语言解析响应时间 < 5秒
   - 执行状态更新延迟 < 1秒
   - 支持并发执行多个任务
