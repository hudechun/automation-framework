"""
任务调度器 - 基于APScheduler实现定时任务调度
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.job import Job
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    AsyncIOScheduler = None
    CronTrigger = None
    IntervalTrigger = None
    DateTrigger = None
    Job = None


class ScheduleType(Enum):
    """调度类型"""
    ONCE = "once"  # 一次性
    INTERVAL = "interval"  # 周期性
    CRON = "cron"  # Cron表达式


class TaskSchedule:
    """
    任务调度配置
    """
    
    def __init__(
        self,
        schedule_id: Optional[str] = None,
        task_id: str = "",
        schedule_type: ScheduleType = ScheduleType.ONCE,
        trigger_config: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = schedule_id or str(uuid.uuid4())
        self.task_id = task_id
        self.schedule_type = schedule_type
        self.trigger_config = trigger_config or {}
        self.enabled = enabled
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "schedule_type": self.schedule_type.value,
            "trigger_config": self.trigger_config,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
        }


class TaskScheduler:
    """
    任务调度器 - 管理定时任务的调度
    """
    
    def __init__(self):
        if not APSCHEDULER_AVAILABLE:
            raise ImportError("APScheduler is not installed. Please install it with: pip install apscheduler")
        
        self.scheduler = AsyncIOScheduler()
        self._schedules: Dict[str, TaskSchedule] = {}
        self._jobs: Dict[str, Job] = {}
        self._running = False
        
    def start_scheduler(self) -> None:
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            
    def stop_scheduler(self) -> None:
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            
    def schedule_once(
        self,
        task_id: str,
        run_date: datetime,
        callback: Callable,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        调度一次性任务
        
        Args:
            task_id: 任务ID
            run_date: 运行时间
            callback: 回调函数
            metadata: 元数据
            
        Returns:
            调度ID
        """
        schedule = TaskSchedule(
            task_id=task_id,
            schedule_type=ScheduleType.ONCE,
            trigger_config={"run_date": run_date.isoformat()},
            metadata=metadata
        )
        
        # 添加到APScheduler
        trigger = DateTrigger(run_date=run_date)
        job = self.scheduler.add_job(
            callback,
            trigger=trigger,
            id=schedule.id,
            args=[task_id]
        )
        
        self._schedules[schedule.id] = schedule
        self._jobs[schedule.id] = job
        schedule.next_run = job.next_run_time
        
        return schedule.id
        
    def schedule_interval(
        self,
        task_id: str,
        interval_seconds: int,
        callback: Callable,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        调度周期性任务
        
        Args:
            task_id: 任务ID
            interval_seconds: 间隔秒数
            callback: 回调函数
            start_date: 开始时间
            end_date: 结束时间
            metadata: 元数据
            
        Returns:
            调度ID
        """
        schedule = TaskSchedule(
            task_id=task_id,
            schedule_type=ScheduleType.INTERVAL,
            trigger_config={
                "interval_seconds": interval_seconds,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            metadata=metadata
        )
        
        # 添加到APScheduler
        trigger = IntervalTrigger(
            seconds=interval_seconds,
            start_date=start_date,
            end_date=end_date
        )
        job = self.scheduler.add_job(
            callback,
            trigger=trigger,
            id=schedule.id,
            args=[task_id]
        )
        
        self._schedules[schedule.id] = schedule
        self._jobs[schedule.id] = job
        schedule.next_run = job.next_run_time
        
        return schedule.id
        
    def schedule_cron(
        self,
        task_id: str,
        cron_expression: str,
        callback: Callable,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        调度Cron任务
        
        Args:
            task_id: 任务ID
            cron_expression: Cron表达式（例如：'0 0 * * *'）
            callback: 回调函数
            start_date: 开始时间
            end_date: 结束时间
            metadata: 元数据
            
        Returns:
            调度ID
        """
        schedule = TaskSchedule(
            task_id=task_id,
            schedule_type=ScheduleType.CRON,
            trigger_config={
                "cron_expression": cron_expression,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            metadata=metadata
        )
        
        # 解析Cron表达式
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression. Expected format: 'minute hour day month day_of_week'")
        
        minute, hour, day, month, day_of_week = parts
        
        # 添加到APScheduler
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            start_date=start_date,
            end_date=end_date
        )
        job = self.scheduler.add_job(
            callback,
            trigger=trigger,
            id=schedule.id,
            args=[task_id]
        )
        
        self._schedules[schedule.id] = schedule
        self._jobs[schedule.id] = job
        schedule.next_run = job.next_run_time
        
        return schedule.id
        
    def cancel_schedule(self, schedule_id: str) -> bool:
        """
        取消调度
        
        Args:
            schedule_id: 调度ID
            
        Returns:
            是否取消成功
        """
        if schedule_id in self._schedules:
            # 从APScheduler移除
            if schedule_id in self._jobs:
                self.scheduler.remove_job(schedule_id)
                del self._jobs[schedule_id]
            
            del self._schedules[schedule_id]
            return True
        return False
        
    def list_schedules(
        self,
        task_id: Optional[str] = None,
        enabled: Optional[bool] = None
    ) -> List[TaskSchedule]:
        """
        列出调度
        
        Args:
            task_id: 任务ID过滤
            enabled: 启用状态过滤
            
        Returns:
            调度列表
        """
        schedules = list(self._schedules.values())
        
        if task_id:
            schedules = [s for s in schedules if s.task_id == task_id]
        if enabled is not None:
            schedules = [s for s in schedules if s.enabled == enabled]
        
        return schedules
        
    def get_schedule(self, schedule_id: str) -> Optional[TaskSchedule]:
        """
        获取调度
        
        Args:
            schedule_id: 调度ID
            
        Returns:
            调度对象，如果不存在返回None
        """
        return self._schedules.get(schedule_id)
        
    def update_schedule_status(self, schedule_id: str, enabled: bool) -> Optional[TaskSchedule]:
        """
        更新调度状态
        
        Args:
            schedule_id: 调度ID
            enabled: 是否启用
            
        Returns:
            更新后的调度，如果不存在返回None
        """
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None
        
        schedule.enabled = enabled
        schedule.updated_at = datetime.now()
        
        # 暂停或恢复APScheduler中的任务
        if schedule_id in self._jobs:
            if enabled:
                self.scheduler.resume_job(schedule_id)
            else:
                self.scheduler.pause_job(schedule_id)
        
        return schedule


# 全局调度器实例
_global_scheduler: Optional[TaskScheduler] = None


def get_global_scheduler() -> TaskScheduler:
    """获取全局调度器"""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = TaskScheduler()
    return _global_scheduler
