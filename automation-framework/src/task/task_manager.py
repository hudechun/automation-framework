"""
任务管理器 - 管理任务的创建、更新、删除和执行（数据库持久化版本）
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from ..core.types import TaskStatus, DriverType
from ..core.interfaces import Action
from ..core.action_serializer import serialize_actions, deserialize_actions
from ..models.sqlalchemy_models import Task as TaskModel

logger = logging.getLogger(__name__)


class Task:
    """
    任务类 - 表示一个自动化任务
    """
    
    def __init__(
        self,
        task_id: Optional[str] = None,
        name: str = "",
        description: str = "",
        driver_type: DriverType = DriverType.BROWSER,
        actions: Optional[List[Action]] = None,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: TaskStatus = TaskStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        error: Optional[str] = None
    ):
        self.id = task_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.driver_type = driver_type
        self.actions = actions or []
        self.config = config or {}
        self.metadata = metadata or {}
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.error = error
        
    def validate(self) -> bool:
        """
        验证任务配置
        
        Returns:
            是否有效
        """
        if not self.name:
            raise ValueError("Task name is required")
        
        if not self.actions:
            raise ValueError("Task must have at least one action")
        
        # 验证每个操作
        for action in self.actions:
            action.validate()
        
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "driver_type": self.driver_type.value,
            "actions": [action.to_dict() for action in self.actions],
            "config": self.config,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "error": self.error,
        }
    
    @classmethod
    def from_db_model(cls, db_task: TaskModel) -> "Task":
        """
        从数据库模型创建Task对象
        
        Args:
            db_task: 数据库任务模型
            
        Returns:
            Task对象
        """
        # 反序列化actions
        actions = []
        if db_task.actions:
            try:
                actions = deserialize_actions(db_task.actions)
            except Exception as e:
                logger.error(f"Failed to deserialize actions for task {db_task.id}: {e}")
                actions = []
        
        task = cls(
            task_id=str(db_task.id),
            name=db_task.name,
            description=db_task.description or "",
            driver_type=DriverType(db_task.task_type),
            actions=actions,
            config=db_task.config or {},
            metadata={},  # metadata可以存储在config中
            status=TaskStatus(db_task.status),
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            error=None  # 错误信息可以存储在config中
        )
        return task
    
    def to_db_model(self) -> Dict[str, Any]:
        """
        转换为数据库模型字典（用于创建/更新）
        
        Returns:
            字典，包含数据库字段
        """
        return {
            "name": self.name,
            "description": self.description,
            "task_type": self.driver_type.value,
            "actions": serialize_actions(self.actions),
            "config": self.config,
            "status": self.status.value,
            "updated_at": datetime.now(),
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典反序列化"""
        task = cls(
            task_id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            driver_type=DriverType(data["driver_type"]),
            config=data.get("config", {}),
            metadata=data.get("metadata", {})
        )
        task.status = TaskStatus(data["status"])
        if "created_at" in data and data["created_at"]:
            task.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and data["updated_at"]:
            task.updated_at = datetime.fromisoformat(data["updated_at"])
        task.error = data.get("error")
        # actions需要从序列化数据重建
        if "actions" in data:
            task.actions = deserialize_actions(data["actions"])
        return task


class TaskManager:
    """
    任务管理器 - 管理所有任务的CRUD操作（数据库持久化版本）
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        初始化任务管理器
        
        Args:
            db_session: 数据库会话（如果为None，需要在每个方法中传入）
        """
        self._db_session = db_session
        
    async def create_task(
        self,
        name: str,
        description: str = "",
        driver_type: DriverType = DriverType.BROWSER,
        actions: Optional[List[Action]] = None,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Task:
        """
        创建任务并保存到数据库
        
        Args:
            name: 任务名称
            description: 任务描述
            driver_type: 驱动类型
            actions: 操作列表
            config: 配置
            metadata: 元数据
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            创建的任务
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 创建任务对象
        task = Task(
            name=name,
            description=description,
            driver_type=driver_type,
            actions=actions or [],
            config=config or {},
            metadata=metadata or {}
        )
        
        # 验证任务
        task.validate()
        
        # 创建数据库模型
        db_task = TaskModel(**task.to_db_model())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        # 从数据库模型创建Task对象
        task.id = str(db_task.id)
        task.created_at = db_task.created_at
        task.updated_at = db_task.updated_at
        
        logger.info(f"Created task: {task.id} - {task.name}")
        return task
        
    async def get_task(
        self,
        task_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[Task]:
        """
        从数据库获取任务
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            任务对象，如果不存在返回None
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        try:
            task_id_int = int(task_id)
        except ValueError:
            logger.warning(f"Invalid task_id: {task_id}")
            return None
        
        result = await db.execute(
            select(TaskModel).where(TaskModel.id == task_id_int)
        )
        db_task = result.scalar_one_or_none()
        
        if not db_task:
            return None
        
        return Task.from_db_model(db_task)
        
    async def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        actions: Optional[List[Action]] = None,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[Task]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            name: 新名称
            description: 新描述
            actions: 新操作列表
            config: 新配置
            metadata: 新元数据
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            更新后的任务，如果不存在返回None
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 获取现有任务
        task = await self.get_task(task_id, db_session=db)
        if not task:
            return None
        
        # 更新字段
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if actions is not None:
            task.actions = actions
        if config is not None:
            task.config = config
        if metadata is not None:
            task.metadata = metadata
        
        task.updated_at = datetime.now()
        
        # 验证更新后的任务
        task.validate()
        
        # 更新数据库
        try:
            task_id_int = int(task_id)
        except ValueError:
            return None
        
        update_data = task.to_db_model()
        await db.execute(
            update(TaskModel)
            .where(TaskModel.id == task_id_int)
            .values(**update_data)
        )
        await db.commit()
        
        logger.info(f"Updated task: {task_id} - {task.name}")
        return task
        
    async def delete_task(
        self,
        task_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            是否删除成功
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        try:
            task_id_int = int(task_id)
        except ValueError:
            return False
        
        result = await db.execute(
            delete(TaskModel).where(TaskModel.id == task_id_int)
        )
        await db.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted task: {task_id}")
        return deleted
        
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        driver_type: Optional[DriverType] = None,
        limit: int = 100,
        offset: int = 0,
        db_session: Optional[AsyncSession] = None
    ) -> List[Task]:
        """
        从数据库列出任务（支持分页和过滤）
        
        Args:
            status: 状态过滤
            driver_type: 驱动类型过滤
            limit: 每页数量
            offset: 偏移量
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            任务列表
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 构建查询
        query = select(TaskModel)
        
        # 添加过滤条件
        if status:
            query = query.where(TaskModel.status == status.value)
        if driver_type:
            query = query.where(TaskModel.task_type == driver_type.value)
        
        # 排序和分页
        query = query.order_by(TaskModel.created_at.desc()).limit(limit).offset(offset)
        
        # 执行查询
        result = await db.execute(query)
        db_tasks = result.scalars().all()
        
        # 转换为Task对象
        tasks = [Task.from_db_model(db_task) for db_task in db_tasks]
        
        return tasks
        
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        error: Optional[str] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[Task]:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            error: 错误信息（如果有）
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            更新后的任务，如果不存在返回None
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        try:
            task_id_int = int(task_id)
        except ValueError:
            return None
        
        # 更新状态
        update_data = {
            "status": status.value,
            "updated_at": datetime.now()
        }
        
        # 如果有错误信息，存储到config中
        if error:
            # 先获取现有任务
            task = await self.get_task(task_id, db_session=db)
            if task:
                task.config = task.config or {}
                task.config["error"] = error
                update_data["config"] = task.config
        
        await db.execute(
            update(TaskModel)
            .where(TaskModel.id == task_id_int)
            .values(**update_data)
        )
        await db.commit()
        
        # 返回更新后的任务
        return await self.get_task(task_id, db_session=db)
        
    async def get_statistics(
        self,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Args:
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            统计信息
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 总数
        total_result = await db.execute(select(func.count(TaskModel.id)))
        total = total_result.scalar() or 0
        
        # 按状态统计
        status_counts = {}
        for status in TaskStatus:
            count_result = await db.execute(
                select(func.count(TaskModel.id)).where(TaskModel.status == status.value)
            )
            status_counts[status.value] = count_result.scalar() or 0
        
        return {
            "total": total,
            "by_status": status_counts,
        }


# 全局任务管理器实例（注意：需要在使用时传入db_session）
_global_task_manager: Optional[TaskManager] = None


def get_global_task_manager(db_session: Optional[AsyncSession] = None) -> TaskManager:
    """
    获取全局任务管理器
    
    Args:
        db_session: 数据库会话（如果提供，会创建新的管理器实例）
        
    Returns:
        任务管理器实例
    """
    global _global_task_manager
    if _global_task_manager is None or db_session is not None:
        _global_task_manager = TaskManager(db_session=db_session)
    return _global_task_manager
