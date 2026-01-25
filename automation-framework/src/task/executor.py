"""
任务执行器 - 负责执行、暂停、恢复、停止任务
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, func

from ..core.types import TaskStatus, DriverType, SessionState
from ..core.session import SessionManager, get_global_session_manager
from ..core.interfaces import Driver, Action
from ..core.execution_context import ExecutionContext
from ..core.execution_progress import ExecutionProgress
from ..core.retry_strategy import RetryStrategy, ErrorClassifier, execute_with_retry
from ..drivers.browser_driver import BrowserDriver
from ..drivers.desktop_driver import DesktopDriver
from .task_manager import TaskManager, get_global_task_manager
from ..models.sqlalchemy_models import (
    ExecutionRecord as ExecutionRecordModel,
    SessionCheckpoint as SessionCheckpointModel
)

logger = logging.getLogger(__name__)


class ExecutionState(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskExecutor:
    """
    任务执行器 - 管理任务执行生命周期
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        初始化任务执行器
        
        Args:
            db_session: 数据库会话
        """
        self._db_session = db_session
        self._running_executions: Dict[str, asyncio.Task] = {}
        self._execution_states: Dict[str, ExecutionState] = {}
        self._execution_sessions: Dict[str, str] = {}  # task_id -> session_id
        self._execution_contexts: Dict[str, ExecutionContext] = {}  # task_id -> ExecutionContext
        self._execution_progress: Dict[str, ExecutionProgress] = {}  # task_id -> ExecutionProgress
        
    async def execute_task(
        self,
        task_id: str,
        user_id: Optional[int] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话
            
        Returns:
            执行结果
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 检查任务是否已在运行
        if task_id in self._running_executions:
            return {
                "success": False,
                "message": "Task is already running",
                "task_id": task_id
            }
        
        # 获取任务
        task_manager = get_global_task_manager(db_session=db)
        task = await task_manager.get_task(task_id, db_session=db)
        if not task:
            return {
                "success": False,
                "message": "Task not found",
                "task_id": task_id
            }
        
        # 验证任务状态
        if task.status != TaskStatus.PENDING:
            return {
                "success": False,
                "message": f"Cannot execute task in status: {task.status.value}",
                "task_id": task_id
            }
        
        # 更新任务状态为运行中
        await task_manager.update_task_status(task_id, TaskStatus.RUNNING, db_session=db)
        
        # 创建执行记录
        # 尝试将task_id转换为整数
        task_id_int = None
        try:
            task_id_int = int(task_id)
        except (ValueError, TypeError):
            # 如果task_id不是数字，尝试从数据库查询
            from sqlalchemy import select
            from ..models.sqlalchemy_models import Task as TaskModel
            result = await db.execute(
                select(TaskModel).where(TaskModel.name == task_id).limit(1)
            )
            task_obj = result.scalar_one_or_none()
            if task_obj:
                task_id_int = task_obj.id
        
        if task_id_int is None:
            return {
                "success": False,
                "message": "Invalid task_id",
                "task_id": task_id
            }
        
        execution_record = ExecutionRecordModel(
            task_id=task_id_int,
            status="running",
            start_time=datetime.now()
        )
        db.add(execution_record)
        await db.commit()
        await db.refresh(execution_record)
        
        # 创建会话（将user_id和task_id存储在metadata中）
        session_manager = get_global_session_manager(db_session=db)
        session_metadata = {
            "task_id": task_id,
        }
        if user_id is not None:
            session_metadata["user_id"] = user_id
        
        session = await session_manager.create_session(
            driver_type=task.driver_type,
            metadata=session_metadata,
            db_session=db
        )
        
        # 记录执行状态
        self._execution_states[task_id] = ExecutionState.RUNNING
        self._execution_sessions[task_id] = session.id
        
        # 启动执行任务（后台运行，带超时控制）
        timeout = task.config.get("timeout", 3600)  # 默认1小时
        execution_task = asyncio.create_task(
            self._execute_task_with_timeout(
                task_id, task, session, execution_record.id, db, timeout
            )
        )
        self._running_executions[task_id] = execution_task
        
        logger.info(f"Task {task_id} execution started")
        
        return {
            "success": True,
            "message": "Task execution started",
            "task_id": task_id,
            "session_id": session.id,
            "execution_id": execution_record.id
        }
    
    async def _execute_task_with_timeout(
        self,
        task_id: str,
        task: Any,
        session: Any,
        execution_id: int,
        db: AsyncSession,
        timeout: int = 3600
    ) -> None:
        """
        带超时控制的任务执行
        
        Args:
            task_id: 任务ID
            task: 任务对象
            session: 会话对象
            execution_id: 执行记录ID
            db: 数据库会话
            timeout: 超时时间（秒）
        """
        try:
            await asyncio.wait_for(
                self._execute_task_async(task_id, task, session, execution_id, db),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Task {task_id} execution timeout after {timeout} seconds")
            await self._handle_timeout(task_id, execution_id, db)
            raise
    
    async def _execute_task_async(
        self,
        task_id: str,
        task: Any,
        session: Any,
        execution_id: int,
        db: AsyncSession
    ) -> None:
        """
        异步执行任务
        
        Args:
            task_id: 任务ID
            task: 任务对象
            session: 会话对象
            execution_id: 执行记录ID
            db: 数据库会话
        """
        try:
            # 启动会话
            session.start()
            session_manager = get_global_session_manager(db_session=db)
            await session_manager.update_session_state(
                session.id,
                SessionState.RUNNING,
                db_session=db
            )
            
            # 创建驱动
            driver = await self._create_driver(task.driver_type, task.config or {})
            
            # 初始化执行上下文（尝试从检查点恢复）
            context = await self._load_or_create_context(task_id, session.id, db)
            self._execution_contexts[task_id] = context
            
            # 如果从检查点恢复，记录日志
            if context.current_action_index > 0:
                logger.info(
                    f"Task {task_id} resuming from checkpoint at action {context.current_action_index}"
                )
            
            # 初始化执行进度（如果从检查点恢复，需要设置已完成的操作数）
            progress = ExecutionProgress(total_actions=len(task.actions))
            progress.start()
            if context.current_action_index > 0:
                # 从检查点恢复，设置已完成的操作数
                progress.completed_actions = context.current_action_index
            self._execution_progress[task_id] = progress
            
            # 创建重试策略
            retry_strategy = RetryStrategy(
                max_retries=task.config.get("max_retries", 3),
                initial_delay=task.config.get("retry_delay", 1.0),
                backoff_factor=task.config.get("retry_backoff_factor", 2.0)
            )
            
            # 执行操作循环
            results = []
            start_index = context.current_action_index
            
            for i in range(start_index, len(task.actions)):
                action = task.actions[i]
                
                # 更新当前操作索引
                context.current_action_index = i
                progress.next_action(i)
                
                # 保存检查点（用于恢复）
                await self._save_checkpoint(task_id, session.id, context, db)
                
                # 检查是否被暂停
                if self._execution_states.get(task_id) == ExecutionState.PAUSED:
                    await self._wait_for_resume(task_id)
                
                # 检查是否被停止
                if self._execution_states.get(task_id) == ExecutionState.STOPPED:
                    raise asyncio.CancelledError("Task stopped")
                
                # 执行操作（带重试和验证）
                action_start_time = datetime.now()
                try:
                    # 使用重试策略执行操作
                    success, result, error = await execute_with_retry(
                        self._execute_action_safe,
                        retry_strategy,
                        action,
                        driver,
                        context
                    )
                    
                    execution_time = (datetime.now() - action_start_time).total_seconds()
                    
                    if success:
                        # 操作成功
                        results.append({
                            "action_index": i,
                            "action_type": action.action_type.value,
                            "success": True,
                            "result": result,
                            "execution_time": round(execution_time * 1000, 2),  # 毫秒
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        progress.complete_action(execution_time)
                        context.move_to_next_action()
                        
                        # 添加到会话历史
                        session.add_action(action)
                    else:
                        # 操作失败（重试后仍然失败）
                        results.append({
                            "action_index": i,
                            "action_type": action.action_type.value,
                            "success": False,
                            "error": str(error) if error else "Unknown error",
                            "execution_time": round(execution_time * 1000, 2),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        progress.fail_action(execution_time)
                        
                        # 根据配置决定是否继续
                        if task.config.get("stop_on_error", True):
                            raise error or Exception("Action execution failed")
                        else:
                            # 继续执行下一个操作
                            context.move_to_next_action()
                            continue
                    
                    # 更新执行进度到数据库（用于前端显示）
                    await self._update_execution_progress(execution_id, progress, db)
                    
                except Exception as e:
                    execution_time = (datetime.now() - action_start_time).total_seconds()
                    logger.error(f"Action {i} failed after retries: {e}")
                    
                    results.append({
                        "action_index": i,
                        "action_type": action.action_type.value,
                        "success": False,
                        "error": str(e),
                        "execution_time": round(execution_time * 1000, 2),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    progress.fail_action(execution_time)
                    
                    # 根据配置决定是否继续
                    if task.config.get("stop_on_error", True):
                        raise
                    else:
                        context.move_to_next_action()
                        continue
            
            # 执行成功
            self._execution_states[task_id] = ExecutionState.COMPLETED
            
            # 更新任务状态
            task_manager = get_global_task_manager(db_session=db)
            await task_manager.update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                db_session=db
            )
            
            # 更新执行记录
            await db.execute(
                update(ExecutionRecordModel)
                .where(ExecutionRecordModel.id == execution_id)
                .values(
                    status="completed",
                    end_time=datetime.now(),
                    duration=int((datetime.now() - session.created_at).total_seconds()),
                    result={"results": results}
                )
            )
            await db.commit()
            
            # 停止会话
            session.stop()
            await session_manager.update_session_state(
                session.id,
                SessionState.STOPPED,
                db_session=db
            )
            
            logger.info(f"Task {task_id} execution completed")
            
        except asyncio.CancelledError:
            # 任务被停止
            self._execution_states[task_id] = ExecutionState.STOPPED
            
            # 更新任务状态
            task_manager = get_global_task_manager(db_session=db)
            await task_manager.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error="Task stopped by user",
                db_session=db
            )
            
            # 更新执行记录
            await db.execute(
                update(ExecutionRecordModel)
                .where(ExecutionRecordModel.id == execution_id)
                .values(
                    status="failed",
                    end_time=datetime.now(),
                    error_message="Task stopped by user"
                )
            )
            await db.commit()
            
            # 停止会话
            if session:
                session.stop()
                session_manager = get_global_session_manager(db_session=db)
                await session_manager.update_session_state(
                    session.id,
                    SessionState.STOPPED,
                    db_session=db
                )
            
            logger.info(f"Task {task_id} execution stopped")
            
        except Exception as e:
            # 执行失败
            self._execution_states[task_id] = ExecutionState.FAILED
            
            # 更新任务状态
            task_manager = get_global_task_manager(db_session=db)
            await task_manager.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e),
                db_session=db
            )
            
            # 更新执行记录
            await db.execute(
                update(ExecutionRecordModel)
                .where(ExecutionRecordModel.id == execution_id)
                .values(
                    status="failed",
                    end_time=datetime.now(),
                    error_message=str(e),
                    error_stack=str(e.__traceback__) if hasattr(e, '__traceback__') else None
                )
            )
            await db.commit()
            
            # 终止会话
            if session:
                session.terminate(str(e))
                session_manager = get_global_session_manager(db_session=db)
                await session_manager.update_session_state(
                    session.id,
                    SessionState.FAILED,
                    error=str(e),
                    db_session=db
                )
            
            logger.error(f"Task {task_id} execution failed: {e}")
    
    async def _handle_timeout(
        self,
        task_id: str,
        execution_id: int,
        db: AsyncSession
    ) -> None:
        """
        处理任务超时
        
        Args:
            task_id: 任务ID
            execution_id: 执行记录ID
            db: 数据库会话
        """
        # 标记执行状态为失败
        self._execution_states[task_id] = ExecutionState.FAILED
        
        # 更新任务状态为超时失败
        task_manager = get_global_task_manager(db_session=db)
        await task_manager.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error="Task execution timeout",
            db_session=db
        )
        
        # 更新执行记录为失败状态
        await db.execute(
            update(ExecutionRecordModel)
            .where(ExecutionRecordModel.id == execution_id)
            .set(
                {
                    "status": "failed",
                    "end_time": datetime.now(),
                    "error_message": "Task execution timeout",
                }
            )
        )
        await db.commit()

        # 清理内存中的执行状态
        if task_id in self._running_executions:
            del self._running_executions[task_id]
        if task_id in self._execution_contexts:
            del self._execution_contexts[task_id]
        if task_id in self._execution_progress:
            del self._execution_progress[task_id]
        if task_id in self._execution_sessions:
            del self._execution_sessions[task_id]
    
    async def _create_driver(
        self,
        driver_type: DriverType,
        config: Dict[str, Any]
    ) -> Driver:
        """
        创建驱动实例
        
        Args:
            driver_type: 驱动类型
            config: 配置
            
        Returns:
            驱动实例
        """
        if driver_type == DriverType.BROWSER:
            from ..core.types import BrowserType
            browser_type = BrowserType(config.get("browser_type", "chromium"))
            headless = config.get("headless", False)
            driver = BrowserDriver(browser_type=browser_type, headless=headless)
            await driver.start(**config)
            return driver
        elif driver_type == DriverType.DESKTOP:
            driver = DesktopDriver(config=config)
            await driver.start(**config)
            return driver
        else:
            raise ValueError(f"Unsupported driver type: {driver_type}")
    
    async def pause_task(
        self,
        task_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        暂停任务
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话
            
        Returns:
            操作结果
        """
        if task_id not in self._running_executions:
            return {
                "success": False,
                "message": "Task is not running",
                "task_id": task_id
            }
        
        if self._execution_states.get(task_id) != ExecutionState.RUNNING:
            return {
                "success": False,
                "message": f"Cannot pause task in state: {self._execution_states.get(task_id)}",
                "task_id": task_id
            }
        
        # 更新状态
        self._execution_states[task_id] = ExecutionState.PAUSED
        
        # 更新任务状态
        db = db_session or self._db_session
        if db:
            task_manager = get_global_task_manager(db_session=db)
            await task_manager.update_task_status(
                task_id,
                TaskStatus.PAUSED,
                db_session=db
            )
            
            # 保存检查点（保存当前执行位置）
            context = self._execution_contexts.get(task_id)
            session_id = self._execution_sessions.get(task_id)
            if context and session_id:
                await self._save_checkpoint(task_id, session_id, context, db)
                logger.info(f"Checkpoint saved for paused task {task_id} at action {context.current_action_index}")
            
            # 暂停会话
            if session_id:
                session_manager = get_global_session_manager(db_session=db)
                session = await session_manager.get_session(session_id, db_session=db)
                if session:
                    session.pause()
                    await session_manager.update_session_state(
                        session_id,
                        SessionState.PAUSED,
                        db_session=db
                    )
        
        logger.info(f"Task {task_id} paused")
        
        return {
            "success": True,
            "message": "Task paused",
            "task_id": task_id,
            "checkpoint_saved": context is not None if task_id in self._execution_contexts else False
        }
    
    async def resume_task(
        self,
        task_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        恢复任务（从检查点继续执行）
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话
            
        Returns:
            操作结果
        """
        db = db_session or self._db_session
        if not db:
            return {
                "success": False,
                "message": "Database session is required",
                "task_id": task_id
            }
        
        # 检查任务状态
        task_manager = get_global_task_manager(db_session=db)
        task = await task_manager.get_task(task_id, db_session=db)
        if not task:
            return {
                "success": False,
                "message": "Task not found",
                "task_id": task_id
            }
        
        if task.status != TaskStatus.PAUSED:
            return {
                "success": False,
                "message": f"Cannot resume task in status: {task.status.value}",
                "task_id": task_id
            }
        
        # 获取会话
        session_manager = get_global_session_manager(db_session=db)
        session_id = self._execution_sessions.get(task_id)
        if not session_id:
            # 尝试从数据库查找最新的会话（从metadata中查找task_id）
            from ..models.sqlalchemy_models import Session as SessionModel
            from sqlalchemy import func
            # 使用JSON_EXTRACT从session_metadata中查询task_id
            # 兼容两种字段名：session_metadata 或 metadata
            metadata_field = getattr(SessionModel, 'session_metadata', None) or getattr(SessionModel, 'metadata', None)
            if metadata_field:
                result = await db.execute(
                    select(SessionModel)
                    .where(
                        func.json_extract(metadata_field, '$.task_id') == task_id
                    )
                    .order_by(SessionModel.updated_at.desc())
                    .limit(1)
                )
            else:
                result = None
            session_model = result.scalar_one_or_none()
            if session_model:
                session_id = session_model.session_id
                self._execution_sessions[task_id] = session_id
        
        if not session_id:
            return {
                "success": False,
                "message": "Session not found for task",
                "task_id": task_id
            }
        
        # 加载执行上下文（从检查点恢复）
        context = await self._load_or_create_context(task_id, session_id, db)
        self._execution_contexts[task_id] = context
        
        # 恢复执行进度
        progress = ExecutionProgress(total_actions=len(task.actions))
        progress.completed_actions = context.current_action_index
        self._execution_progress[task_id] = progress
        
        # 更新状态
        self._execution_states[task_id] = ExecutionState.RUNNING
        
        # 更新任务状态
        await task_manager.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            db_session=db
        )
        
        # 恢复会话
        session = await session_manager.get_session(session_id, db_session=db)
        if session:
            session.resume()
            await session_manager.update_session_state(
                session_id,
                SessionState.RUNNING,
                db_session=db
            )
        
        logger.info(
            f"Task {task_id} resumed from checkpoint at action {context.current_action_index}"
        )
        
        return {
            "success": True,
            "message": "Task resumed",
            "task_id": task_id,
            "resume_from_action": context.current_action_index
        }
    
    async def stop_task(
        self,
        task_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        停止任务
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话
            
        Returns:
            操作结果
        """
        if task_id not in self._running_executions:
            return {
                "success": False,
                "message": "Task is not running",
                "task_id": task_id
            }
        
        # 更新状态
        self._execution_states[task_id] = ExecutionState.STOPPED
        
        # 取消执行任务
        execution_task = self._running_executions.get(task_id)
        if execution_task:
            execution_task.cancel()
        
        # 更新任务状态
        db = db_session or self._db_session
        if db:
            task_manager = get_global_task_manager(db_session=db)
            await task_manager.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error="Task stopped by user",
                db_session=db
            )
        
        logger.info(f"Task {task_id} stopped")
        
        return {
            "success": True,
            "message": "Task stopped",
            "task_id": task_id
        }
    
    def is_task_running(self, task_id: str) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否正在运行
        """
        return task_id in self._running_executions
    
    def get_execution_state(self, task_id: str) -> Optional[ExecutionState]:
        """
        获取执行状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            执行状态
        """
        return self._execution_states.get(task_id)
    
    def get_execution_progress(self, task_id: str) -> Optional[ExecutionProgress]:
        """
        获取执行进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            执行进度对象
        """
        return self._execution_progress.get(task_id)
    
    def get_execution_context(self, task_id: str) -> Optional[ExecutionContext]:
        """
        获取执行上下文
        
        Args:
            task_id: 任务ID
            
        Returns:
            执行上下文对象
        """
        return self._execution_contexts.get(task_id)
    
    async def _execute_action_safe(
        self,
        action: Action,
        driver: Driver,
        context: ExecutionContext
    ) -> Any:
        """
        安全执行操作（用于重试）
        
        Args:
            action: 操作对象
            driver: 驱动实例
            context: 执行上下文
            
        Returns:
            操作结果
        """
        return await action.execute(driver)
    
    async def _load_or_create_context(
        self,
        task_id: str,
        session_id: str,
        db: AsyncSession
    ) -> ExecutionContext:
        """
        加载或创建执行上下文
        
        Args:
            task_id: 任务ID
            session_id: 会话ID（字符串格式的session.id）
            db: 数据库会话
            
        Returns:
            执行上下文
        """
        # 尝试从数据库加载最新的检查点
        try:
            # 首先获取session的数据库ID
            from ..models.sqlalchemy_models import Session as SessionModel
            result = await db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id).limit(1)
            )
            session_model = result.scalar_one_or_none()
            
            if session_model:
                # 查找该session的最新检查点
                checkpoint_result = await db.execute(
                    select(SessionCheckpointModel)
                    .where(SessionCheckpointModel.session_id == session_model.id)
                    .order_by(SessionCheckpointModel.created_at.desc())
                    .limit(1)
                )
                checkpoint = checkpoint_result.scalar_one_or_none()
                
                if checkpoint and checkpoint.state_data:
                    # 从检查点恢复上下文
                    context = ExecutionContext.from_dict(checkpoint.state_data)
                    logger.info(
                        f"Restored execution context from checkpoint for task {task_id}, "
                        f"resuming from action {context.current_action_index}"
                    )
                    return context
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}", exc_info=True)
        
        # 创建新的上下文
        logger.info(f"Creating new execution context for task {task_id}")
        return ExecutionContext()
    
    async def _save_checkpoint(
        self,
        task_id: str,
        session_id: str,
        context: ExecutionContext,
        db: AsyncSession
    ) -> None:
        """
        保存检查点
        
        Args:
            task_id: 任务ID
            session_id: 会话ID（字符串格式的session.id）
            context: 执行上下文
            db: 数据库会话
        """
        try:
            # 获取session的数据库ID
            from ..models.sqlalchemy_models import Session as SessionModel
            result = await db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id).limit(1)
            )
            session_model = result.scalar_one_or_none()
            
            if session_model:
                checkpoint = SessionCheckpointModel(
                    session_id=session_model.id,
                    checkpoint_name=f"action_{context.current_action_index}",
                    state_data=context.to_dict(),
                    actions_completed=context.current_action_index
                )
                db.add(checkpoint)
                await db.commit()
                logger.debug(f"Checkpoint saved for task {task_id}, action {context.current_action_index}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")
    
    async def _wait_for_resume(self, task_id: str) -> None:
        """
        等待任务恢复
        
        Args:
            task_id: 任务ID
        """
        while self._execution_states.get(task_id) == ExecutionState.PAUSED:
            await asyncio.sleep(0.1)
            # 检查是否被停止
            if self._execution_states.get(task_id) == ExecutionState.STOPPED:
                raise asyncio.CancelledError("Task stopped")
    
    async def _update_execution_progress(
        self,
        execution_id: int,
        progress: ExecutionProgress,
        db: AsyncSession
    ) -> None:
        """
        更新执行进度到数据库
        
        Args:
            execution_id: 执行记录ID
            progress: 执行进度对象
            db: 数据库会话
        """
        try:
            await db.execute(
                update(ExecutionRecordModel)
                .where(ExecutionRecordModel.id == execution_id)
                .values(
                    result={
                        "progress": progress.to_dict(),
                        "last_update": datetime.now().isoformat()
                    }
                )
            )
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to update execution progress: {e}")


# 全局执行器实例
_global_executor: Optional[TaskExecutor] = None


def get_global_executor(db_session: Optional[AsyncSession] = None) -> TaskExecutor:
    """
    获取全局任务执行器
    
    Args:
        db_session: 数据库会话（如果提供，会创建新的执行器实例）
        
    Returns:
        任务执行器实例
    """
    global _global_executor
    if _global_executor is None or db_session is not None:
        _global_executor = TaskExecutor(db_session=db_session)
    return _global_executor
