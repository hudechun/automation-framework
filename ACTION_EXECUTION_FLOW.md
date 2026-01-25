# 指令顺序执行机制详解

## 📋 当前执行流程

### 1. 基本执行流程

当前在 `TaskExecutor._execute_task_async` 中的执行逻辑：

```python
# 执行操作
results = []
for i, action in enumerate(task.actions):
    # 检查是否被暂停
    if self._execution_states.get(task_id) == ExecutionState.PAUSED:
        # 等待恢复
        while self._execution_states.get(task_id) == ExecutionState.PAUSED:
            await asyncio.sleep(0.1)
            if self._execution_states.get(task_id) == ExecutionState.STOPPED:
                raise asyncio.CancelledError("Task stopped")
    
    # 检查是否被停止
    if self._execution_states.get(task_id) == ExecutionState.STOPPED:
        raise asyncio.CancelledError("Task stopped")
    
    try:
        # 执行操作
        result = await action.execute(driver)
        results.append({
            "action_index": i,
            "action_type": action.action_type.value,
            "success": True,
            "result": result
        })
        
        # 添加到会话历史
        session.add_action(action)
        
    except Exception as e:
        logger.error(f"Action {i} failed: {e}")
        results.append({
            "action_index": i,
            "action_type": action.action_type.value,
            "success": False,
            "error": str(e)
        })
        # 根据配置决定是否继续
        if task.config.get("stop_on_error", True):
            raise
```

### 2. 执行特点

**优点**：
- ✅ 使用 `for` 循环顺序遍历 `task.actions` 列表
- ✅ 使用 `await` 确保每个操作完成后再执行下一个
- ✅ 支持暂停/恢复机制
- ✅ 支持停止机制
- ✅ 基本的错误处理

**不足**：
- ❌ 没有执行进度追踪（不知道当前执行到第几个操作）
- ❌ 没有执行上下文保存（暂停后无法从断点恢复）
- ❌ 没有操作执行结果验证
- ❌ 没有执行超时控制
- ❌ 没有错误重试机制
- ❌ 没有操作执行时间统计

---

## 🔧 需要完善的执行机制

### 1. 执行进度追踪

**当前问题**：无法知道任务执行到第几个操作，无法显示进度条

**解决方案**：
```python
class ExecutionProgress:
    """执行进度追踪"""
    def __init__(self, total_actions: int):
        self.total_actions = total_actions
        self.current_action_index = 0
        self.completed_actions = 0
        self.failed_actions = 0
        self.start_time = datetime.now()
    
    @property
    def progress_percentage(self) -> float:
        """计算进度百分比"""
        if self.total_actions == 0:
            return 0.0
        return (self.completed_actions / self.total_actions) * 100
    
    def next_action(self) -> None:
        """移动到下一个操作"""
        self.current_action_index += 1
    
    def complete_action(self) -> None:
        """标记操作完成"""
        self.completed_actions += 1
    
    def fail_action(self) -> None:
        """标记操作失败"""
        self.failed_actions += 1
```

### 2. 执行上下文管理

**当前问题**：暂停后无法从断点恢复，只能从头开始

**解决方案**：
```python
class ExecutionContext:
    """执行上下文 - 保存当前执行状态"""
    def __init__(self):
        self.current_action_index = 0  # 当前执行到第几个操作
        self.variables: Dict[str, Any] = {}  # 执行过程中的变量
        self.state: Dict[str, Any] = {}  # 执行状态
        self.checkpoint_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典（用于保存到数据库）"""
        return {
            "current_action_index": self.current_action_index,
            "variables": self.variables,
            "state": self.state,
            "checkpoint_data": self.checkpoint_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionContext':
        """从字典反序列化（用于从数据库恢复）"""
        ctx = cls()
        ctx.current_action_index = data.get("current_action_index", 0)
        ctx.variables = data.get("variables", {})
        ctx.state = data.get("state", {})
        ctx.checkpoint_data = data.get("checkpoint_data")
        return ctx
```

### 3. 操作执行结果验证

**当前问题**：操作执行后没有验证结果是否正确

**解决方案**：
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
        
        # 验证结果（如果操作有验证方法）
        if hasattr(action, 'validate_result'):
            validation_result = await action.validate_result(result, driver)
            if not validation_result.success:
                raise ActionValidationError(
                    f"Action validation failed: {validation_result.message}"
                )
        
        return {
            "success": True,
            "result": result,
            "validation": validation_result if hasattr(action, 'validate_result') else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
```

### 4. 执行超时控制

**当前问题**：没有超时控制，任务可能无限执行

**解决方案**：
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

### 5. 错误处理和重试

**当前问题**：操作失败后直接停止，没有重试机制

**解决方案**：
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

## 🎯 完善的执行流程

### 完整的执行循环

```python
async def _execute_task_async(
    self,
    task_id: str,
    task: Task,
    session: Session,
    execution_id: int,
    db: AsyncSession
) -> None:
    """完善的异步任务执行"""
    try:
        # 1. 初始化执行上下文
        context = ExecutionContext()
        context.current_action_index = 0  # 从上次暂停点恢复（如果有）
        
        # 2. 初始化执行进度
        progress = ExecutionProgress(total_actions=len(task.actions))
        
        # 3. 创建驱动
        driver = await self._create_driver(task.driver_type, task.config or {})
        
        # 4. 创建重试策略
        retry_strategy = RetryStrategy(
            max_retries=task.config.get("max_retries", 3),
            initial_delay=task.config.get("retry_delay", 1.0)
        )
        
        # 5. 执行操作循环
        results = []
        for i in range(context.current_action_index, len(task.actions)):
            action = task.actions[i]
            
            # 5.1 更新当前操作索引
            context.current_action_index = i
            progress.current_action_index = i
            
            # 5.2 保存检查点（用于恢复）
            await self._save_checkpoint(task_id, context, db)
            
            # 5.3 检查是否被暂停
            if self._execution_states.get(task_id) == ExecutionState.PAUSED:
                await self._wait_for_resume(task_id)
            
            # 5.4 检查是否被停止
            if self._execution_states.get(task_id) == ExecutionState.STOPPED:
                raise asyncio.CancelledError("Task stopped")
            
            # 5.5 执行操作（带重试和验证）
            try:
                start_time = datetime.now()
                result = await self._execute_action_with_retry(
                    action, driver, context, retry_strategy
                )
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # 5.6 记录结果
                results.append({
                    "action_index": i,
                    "action_type": action.action_type.value,
                    "success": True,
                    "result": result.get("result"),
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 5.7 更新进度
                progress.complete_action()
                context.current_action_index = i + 1
                
                # 5.8 添加到会话历史
                session.add_action(action)
                
                # 5.9 更新执行进度到数据库（用于前端显示）
                await self._update_execution_progress(
                    execution_id, progress, db
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                logger.error(f"Action {i} failed after retries: {e}")
                
                results.append({
                    "action_index": i,
                    "action_type": action.action_type.value,
                    "success": False,
                    "error": str(e),
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                })
                
                progress.fail_action()
                
                # 根据配置决定是否继续
                if task.config.get("stop_on_error", True):
                    raise
                else:
                    # 继续执行下一个操作
                    continue
        
        # 6. 执行成功
        self._execution_states[task_id] = ExecutionState.COMPLETED
        
        # 7. 更新任务状态和结果
        await self._update_task_completion(task_id, results, db)
        
    except asyncio.CancelledError:
        # 任务被停止
        await self._handle_task_stopped(task_id, context, db)
    except Exception as e:
        # 执行失败
        await self._handle_task_failed(task_id, e, context, db)
    finally:
        # 清理资源
        await self._cleanup_resources(task_id, driver, session)
```

---

## 📊 执行流程图

```
开始执行任务
    │
    ├─> 初始化执行上下文（从检查点恢复）
    │
    ├─> 初始化执行进度追踪
    │
    ├─> 创建驱动实例
    │
    └─> 开始操作循环
            │
            ├─> 更新当前操作索引
            │
            ├─> 保存检查点（用于恢复）
            │
            ├─> 检查暂停/停止状态
            │
            ├─> 执行操作（带重试）
            │   │
            │   ├─> 尝试执行操作
            │   │
            │   ├─> 验证执行结果
            │   │
            │   └─> 失败则重试（最多3次）
            │
            ├─> 记录执行结果
            │
            ├─> 更新执行进度
            │
            ├─> 添加到会话历史
            │
            └─> 继续下一个操作
                    │
                    └─> 所有操作完成？
                            │
                            ├─> 是 → 标记任务完成
                            │
                            └─> 否 → 继续循环
```

---

## 🔍 关键点说明

### 1. 顺序执行的保证

**使用 `for` 循环 + `await`**：
- `for i, action in enumerate(task.actions)` 确保按列表顺序遍历
- `await action.execute(driver)` 确保每个操作完成后再执行下一个
- 这是**同步顺序执行**，不是并发执行

### 2. 暂停/恢复机制

**当前实现**：
- 暂停：设置状态为 `PAUSED`，循环中检测到暂停状态时等待
- 恢复：设置状态为 `RUNNING`，循环继续执行
- **问题**：暂停后没有保存当前执行位置，恢复时可能丢失进度

**改进方案**：
- 每次循环前保存检查点（当前操作索引）
- 恢复时从检查点位置继续执行

### 3. 错误处理

**当前实现**：
- 捕获异常，记录错误
- 根据 `stop_on_error` 配置决定是否继续

**改进方案**：
- 错误分类（可恢复/不可恢复）
- 可恢复错误自动重试
- 不可恢复错误立即停止

### 4. 进度追踪

**当前问题**：
- 没有实时进度信息
- 前端无法显示进度条

**改进方案**：
- 维护 `ExecutionProgress` 对象
- 每次操作后更新进度到数据库
- 前端轮询获取进度信息

---

## ✅ 总结

**当前执行机制**：
- ✅ 使用 `for` 循环顺序执行
- ✅ 使用 `await` 确保同步执行
- ✅ 基本的暂停/恢复/停止支持
- ✅ 基本的错误处理

**需要完善**：
- ⚠️ 执行进度追踪
- ⚠️ 执行上下文管理（检查点）
- ⚠️ 操作结果验证
- ⚠️ 执行超时控制
- ⚠️ 错误重试机制
- ⚠️ 操作执行时间统计

这些功能在 `DEVELOPMENT_PLAN.md` 的 1.1.6 节中已经规划，需要逐步实现。
