"""
任务分类器 - 自动检测任务类型
"""
from typing import List, Optional
from enum import Enum

from ..core.types import DriverType, ActionType, TaskType as CoreTaskType
from ..core.interfaces import Action
from ..task.task_manager import Task


class TaskType(Enum):
    """任务类型"""
    BROWSER = "browser"  # 纯浏览器任务
    DESKTOP = "desktop"  # 纯桌面任务
    HYBRID = "hybrid"    # 混合任务


class TaskClassifier:
    """
    任务分类器 - 分析任务操作判断类型
    """
    
    def __init__(self):
        self._cache: dict[str, TaskType] = {}
        
    def detect_task_type(self, task: Task) -> TaskType:
        """
        检测任务类型
        
        Args:
            task: 任务对象
            
        Returns:
            任务类型
        """
        # 检查缓存
        if task.id in self._cache:
            return self._cache[task.id]
        
        # 分析操作类型
        has_browser = False
        has_desktop = False
        
        for action in task.actions:
            action_type = action.action_type
            
            # 浏览器特定操作
            if action_type in [
                ActionType.NAVIGATION,
                ActionType.INTERACTION,
                ActionType.INPUT,
            ]:
                # 检查是否有浏览器特定的选择器
                if hasattr(action, 'selector') and action.selector:
                    has_browser = True
            
            # 桌面特定操作
            if action_type == ActionType.QUERY:
                # GetUITree通常用于桌面
                if action.__class__.__name__ == 'GetUITree':
                    has_desktop = True
        
        # 也可以根据driver_type判断
        if task.driver_type == DriverType.BROWSER:
            has_browser = True
        elif task.driver_type == DriverType.DESKTOP:
            has_desktop = True
        
        # 确定任务类型
        if has_browser and has_desktop:
            task_type = TaskType.HYBRID
        elif has_browser:
            task_type = TaskType.BROWSER
        elif has_desktop:
            task_type = TaskType.DESKTOP
        else:
            # 默认为浏览器任务
            task_type = TaskType.BROWSER
        
        # 缓存结果
        self._cache[task.id] = task_type
        
        return task_type
        
    def classify_task(
        self,
        task: Task,
        force_type: Optional[TaskType] = None
    ) -> TaskType:
        """
        分类任务
        
        Args:
            task: 任务对象
            force_type: 强制指定类型
            
        Returns:
            任务类型
        """
        if force_type:
            self._cache[task.id] = force_type
            return force_type
        
        return self.detect_task_type(task)
        
    def clear_cache(self, task_id: Optional[str] = None) -> None:
        """
        清除缓存
        
        Args:
            task_id: 任务ID，如果为None则清除所有缓存
        """
        if task_id:
            self._cache.pop(task_id, None)
        else:
            self._cache.clear()


# 全局分类器实例
_global_classifier: Optional[TaskClassifier] = None


def get_global_classifier() -> TaskClassifier:
    """获取全局分类器"""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = TaskClassifier()
    return _global_classifier
