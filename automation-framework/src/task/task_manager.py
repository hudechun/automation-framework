"""
任务管理器 - 管理任务的创建、更新、删除和执行
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid

from ..core.types import TaskStatus, DriverType
from ..core.interfaces import Action


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
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = task_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.driver_type = driver_type
        self.actions = actions or []
        self.config = config or {}
        self.metadata = metadata or {}
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.error: Optional[str] = None
        
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
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "driver_type": self.driver_type.value,
            "actions": [action.to_dict() for action in self.actions],
            "config": self.config,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error": self.error,
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
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        task.error = data.get("error")
        # Note: actions需要从registry重建
        return task


class TaskManager:
    """
    任务管理器 - 管理所有任务的CRUD操作
    """
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        
    def create_task(
        self,
        name: str,
        description: str = "",
        driver_type: DriverType = DriverType.BROWSER,
        actions: Optional[List[Action]] = None,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        创建任务
        
        Args:
            name: 任务名称
            description: 任务描述
            driver_type: 驱动类型
            actions: 操作列表
            config: 配置
            metadata: 元数据
            
        Returns:
            创建的任务
        """
        task = Task(
            name=name,
            description=description,
            driver_type=driver_type,
            actions=actions,
            config=config,
            metadata=metadata
        )
        
        # 验证任务
        task.validate()
        
        # 保存任务
        self._tasks[task.id] = task
        
        return task
        
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象，如果不存在返回None
        """
        return self._tasks.get(task_id)
        
    def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        actions: Optional[List[Action]] = None,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
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
            
        Returns:
            更新后的任务，如果不存在返回None
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
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
        
        return task
        
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否删除成功
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
        
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        driver_type: Optional[DriverType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        列出任务（支持分页和过滤）
        
        Args:
            status: 状态过滤
            driver_type: 驱动类型过滤
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            任务列表
        """
        tasks = list(self._tasks.values())
        
        # 过滤
        if status:
            tasks = [t for t in tasks if t.status == status]
        if driver_type:
            tasks = [t for t in tasks if t.driver_type == driver_type]
        
        # 排序（按创建时间倒序）
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # 分页
        return tasks[offset:offset + limit]
        
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        error: Optional[str] = None
    ) -> Optional[Task]:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            error: 错误信息（如果有）
            
        Returns:
            更新后的任务，如果不存在返回None
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        task.status = status
        task.error = error
        task.updated_at = datetime.now()
        
        return task
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            统计信息
        """
        total = len(self._tasks)
        status_counts = {}
        
        for status in TaskStatus:
            count = len([t for t in self._tasks.values() if t.status == status])
            status_counts[status.value] = count
        
        return {
            "total": total,
            "by_status": status_counts,
        }


# 全局任务管理器实例
_global_task_manager: Optional[TaskManager] = None


def get_global_task_manager() -> TaskManager:
    """获取全局任务管理器"""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = TaskManager()
    return _global_task_manager
