"""
任务执行器 - 负责执行、暂停、恢复、停止任务
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from ..core.types import TaskStatus, DriverType, SessionState
from ..core.session import SessionManager, get_global_session_manager
from ..core.interfaces import Driver, Action
from ..drivers.browser_driver import BrowserDriver
from ..drivers.desktop_driver import DesktopDriver
from .task_manager import TaskManager, get_global_task_manager
from ..models.sqlalchemy_models import ExecutionRecord as ExecutionRecordModel

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
        
    async def execute_task(
        self,
        task_id: str,
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
        
        # 创建会话
        session_manager = get_global_session_manager(db_session=db)
        session = await session_manager.create_session(
            driver_type=task.driver_type,
            metadata={"task_id": task_id},
            db_session=db
        )
        
        # 记录执行状态
        self._execution_states[task_id] = ExecutionState.RUNNING
        self._execution_sessions[task_id] = session.id
        
        # 启动执行任务（后台运行）
        execution_task = asyncio.create_task(
            self._execute_task_async(task_id, task, session, execution_record.id, db)
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
            
            # 执行操作
            results = []
            for i, action in enumerate(task.actions):
                # 检查是否被暂停
                if self._execution_states.get(task_id) == ExecutionState.PAUSED:
                    # 等待恢复
                    while self._execution_states.get(task_id) == ExecutionState.PAUSED:
                        await asyncio.sleep(0.1)
                        # 检查是否被停止
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
            
        finally:
            # 清理
            if task_id in self._running_executions:
                del self._running_executions[task_id]
            if task_id in self._execution_states:
                # 保留状态以便查询
                pass
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
            
            # 暂停会话
            session_id = self._execution_sessions.get(task_id)
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
            "task_id": task_id
        }
    
    async def resume_task(
        self,
        task_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        恢复任务
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话
            
        Returns:
            操作结果
        """
        if task_id not in self._execution_states:
            return {
                "success": False,
                "message": "Task execution not found",
                "task_id": task_id
            }
        
        if self._execution_states.get(task_id) != ExecutionState.PAUSED:
            return {
                "success": False,
                "message": f"Cannot resume task in state: {self._execution_states.get(task_id)}",
                "task_id": task_id
            }
        
        # 更新状态
        self._execution_states[task_id] = ExecutionState.RUNNING
        
        # 更新任务状态
        db = db_session or self._db_session
        if db:
            task_manager = get_global_task_manager(db_session=db)
            await task_manager.update_task_status(
                task_id,
                TaskStatus.RUNNING,
                db_session=db
            )
            
            # 恢复会话
            session_id = self._execution_sessions.get(task_id)
            if session_id:
                session_manager = get_global_session_manager(db_session=db)
                session = await session_manager.get_session(session_id, db_session=db)
                if session:
                    session.resume()
                    await session_manager.update_session_state(
                        session_id,
                        SessionState.RUNNING,
                        db_session=db
                    )
        
        logger.info(f"Task {task_id} resumed")
        
        return {
            "success": True,
            "message": "Task resumed",
            "task_id": task_id
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
