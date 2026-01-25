"""
执行进度追踪 - 追踪任务执行进度
"""
from typing import Optional
from datetime import datetime, timedelta


class ExecutionProgress:
    """
    执行进度追踪 - 追踪任务执行进度和统计信息
    """
    
    def __init__(self, total_actions: int):
        """
        初始化执行进度
        
        Args:
            total_actions: 总操作数
        """
        self.total_actions = total_actions
        self.current_action_index = 0
        self.completed_actions = 0
        self.failed_actions = 0
        self.start_time: Optional[datetime] = None
        self.last_update_time: Optional[datetime] = None
        self.action_times: list[float] = []  # 每个操作的执行时间（秒）
    
    def start(self) -> None:
        """开始执行"""
        self.start_time = datetime.now()
        self.last_update_time = datetime.now()
    
    @property
    def progress_percentage(self) -> float:
        """
        计算进度百分比
        
        Returns:
            进度百分比（0-100）
        """
        if self.total_actions == 0:
            return 0.0
        return (self.completed_actions / self.total_actions) * 100
    
    @property
    def remaining_actions(self) -> int:
        """
        获取剩余操作数
        
        Returns:
            剩余操作数
        """
        return self.total_actions - self.completed_actions - self.failed_actions
    
    @property
    def elapsed_time(self) -> float:
        """
        获取已执行时间（秒）
        
        Returns:
            已执行时间
        """
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def estimated_remaining_time(self) -> Optional[float]:
        """
        估算剩余时间（秒）
        
        Returns:
            剩余时间（秒），如果无法估算返回None
        """
        if self.completed_actions == 0 or not self.start_time:
            return None
        
        elapsed = self.elapsed_time
        avg_time_per_action = elapsed / self.completed_actions
        remaining = self.remaining_actions
        return avg_time_per_action * remaining
    
    @property
    def average_action_time(self) -> float:
        """
        获取平均操作执行时间（秒）
        
        Returns:
            平均执行时间
        """
        if not self.action_times:
            return 0.0
        return sum(self.action_times) / len(self.action_times)
    
    def next_action(self, action_index: int) -> None:
        """
        移动到下一个操作
        
        Args:
            action_index: 操作索引
        """
        self.current_action_index = action_index
        self.last_update_time = datetime.now()
    
    def complete_action(self, execution_time: Optional[float] = None) -> None:
        """
        标记操作完成
        
        Args:
            execution_time: 操作执行时间（秒）
        """
        self.completed_actions += 1
        self.last_update_time = datetime.now()
        if execution_time is not None:
            self.action_times.append(execution_time)
    
    def fail_action(self, execution_time: Optional[float] = None) -> None:
        """
        标记操作失败
        
        Args:
            execution_time: 操作执行时间（秒）
        """
        self.failed_actions += 1
        self.last_update_time = datetime.now()
        if execution_time is not None:
            self.action_times.append(execution_time)
    
    def to_dict(self) -> dict:
        """
        转换为字典（用于API返回）
        
        Returns:
            字典表示
        """
        return {
            "total_actions": self.total_actions,
            "current_action_index": self.current_action_index,
            "completed_actions": self.completed_actions,
            "failed_actions": self.failed_actions,
            "remaining_actions": self.remaining_actions,
            "progress_percentage": round(self.progress_percentage, 2),
            "elapsed_time": round(self.elapsed_time, 2),
            "estimated_remaining_time": round(self.estimated_remaining_time, 2) if self.estimated_remaining_time else None,
            "average_action_time": round(self.average_action_time, 3),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None
        }
