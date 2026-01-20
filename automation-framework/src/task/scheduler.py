"""
任务调度器 - 基于APScheduler实现定时任务调度（数据库持久化版本）
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

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

from ..models.sqlalchemy_models import Schedule as ScheduleModel

logger = logging.getLogger(__name__)


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
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_run: Optional[datetime] = None,
        next_run: Optional[datetime] = None
    ):
        self.id = schedule_id or str(uuid.uuid4())
        self.task_id = task_id
        self.schedule_type = schedule_type
        self.trigger_config = trigger_config or {}
        self.enabled = enabled
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.last_run = last_run
        self.next_run = next_run
    
    @classmethod
    def from_db_model(cls, db_schedule: ScheduleModel) -> "TaskSchedule":
        """
        从数据库模型创建TaskSchedule对象
        
        Args:
            db_schedule: 数据库调度模型
            
        Returns:
            TaskSchedule对象
        """
        return cls(
            schedule_id=str(db_schedule.id),
            task_id=str(db_schedule.task_id),
            schedule_type=ScheduleType(db_schedule.schedule_type),
            trigger_config=db_schedule.schedule_config or {},
            enabled=db_schedule.enabled,
            metadata={},  # metadata可以存储在schedule_config中
            created_at=db_schedule.created_at,
            updated_at=db_schedule.updated_at,
            last_run=db_schedule.last_run_time,
            next_run=db_schedule.next_run_time
        )
    
    def to_db_model(self) -> Dict[str, Any]:
        """
        转换为数据库模型字典（用于创建/更新）
        
        Returns:
            字典，包含数据库字段
        """
        return {
            "task_id": int(self.task_id) if self.task_id.isdigit() else None,
            "schedule_type": self.schedule_type.value,
            "schedule_config": self.trigger_config,
            "enabled": self.enabled,
            "next_run_time": self.next_run,
            "last_run_time": self.last_run,
            "updated_at": datetime.now(),
        }
        
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
    任务调度器 - 管理定时任务的调度（数据库持久化版本）
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        初始化任务调度器
        
        Args:
            db_session: 数据库会话（如果为None，需要在每个方法中传入）
        """
        if not APSCHEDULER_AVAILABLE:
            raise ImportError("APScheduler is not installed. Please install it with: pip install apscheduler")
        
        self.scheduler = AsyncIOScheduler()
        self._db_session = db_session
        self._schedules: Dict[str, TaskSchedule] = {}
        self._jobs: Dict[str, Job] = {}
        self._running = False
        
    async def start_scheduler(self, db_session: Optional[AsyncSession] = None) -> None:
        """
        启动调度器并加载数据库中的调度
        
        Args:
            db_session: 数据库会话（如果为None，使用初始化时的会话）
        """
        if not self._running:
            db = db_session or self._db_session
            if db:
                # 从数据库加载所有启用的调度
                await self._load_schedules_from_db(db)
            
            self.scheduler.start()
            self._running = True
            logger.info("Task scheduler started")
            
    def stop_scheduler(self) -> None:
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            
    async def schedule_once(
        self,
        task_id: str,
        run_date: datetime,
        callback: Callable,
        metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
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
        # 创建调度对象
        schedule = TaskSchedule(
            task_id=task_id,
            schedule_type=ScheduleType.ONCE,
            trigger_config={"run_date": run_date.isoformat()},
            metadata=metadata
        )
        
        # 保存到数据库
        db = db_session or self._db_session
        if db:
            db_schedule = ScheduleModel(**schedule.to_db_model())
            db.add(db_schedule)
            await db.commit()
            await db.refresh(db_schedule)
            schedule.id = str(db_schedule.id)
            schedule.created_at = db_schedule.created_at
            schedule.updated_at = db_schedule.updated_at
        
        # 添加到APScheduler
        trigger = DateTrigger(run_date=run_date)
        job = self.scheduler.add_job(
            callback,
            trigger=trigger,
            id=schedule.id,
            args=[task_id]
        )
        
        schedule.next_run = job.next_run_time
        
        # 更新数据库中的next_run_time
        if db:
            await db.execute(
                update(ScheduleModel)
                .where(ScheduleModel.id == int(schedule.id))
                .values(next_run_time=schedule.next_run)
            )
            await db.commit()
        
        self._schedules[schedule.id] = schedule
        self._jobs[schedule.id] = job
        
        logger.info(f"Created once schedule: {schedule.id} for task {task_id}")
        return schedule.id
        
    async def schedule_interval(
        self,
        task_id: str,
        interval_seconds: int,
        callback: Callable,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
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
        # 创建调度对象
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
        
        # 保存到数据库
        db = db_session or self._db_session
        if db:
            db_schedule = ScheduleModel(**schedule.to_db_model())
            db.add(db_schedule)
            await db.commit()
            await db.refresh(db_schedule)
            schedule.id = str(db_schedule.id)
            schedule.created_at = db_schedule.created_at
            schedule.updated_at = db_schedule.updated_at
        
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
        
        schedule.next_run = job.next_run_time
        
        # 更新数据库中的next_run_time
        if db:
            await db.execute(
                update(ScheduleModel)
                .where(ScheduleModel.id == int(schedule.id))
                .values(next_run_time=schedule.next_run)
            )
            await db.commit()
        
        self._schedules[schedule.id] = schedule
        self._jobs[schedule.id] = job
        
        logger.info(f"Created interval schedule: {schedule.id} for task {task_id}")
        return schedule.id
        
    async def schedule_cron(
        self,
        task_id: str,
        cron_expression: str,
        callback: Callable,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
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
        # 创建调度对象
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
        
        # 保存到数据库
        db = db_session or self._db_session
        if db:
            db_schedule = ScheduleModel(**schedule.to_db_model())
            db.add(db_schedule)
            await db.commit()
            await db.refresh(db_schedule)
            schedule.id = str(db_schedule.id)
            schedule.created_at = db_schedule.created_at
            schedule.updated_at = db_schedule.updated_at
        
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
        
        schedule.next_run = job.next_run_time
        
        # 更新数据库中的next_run_time
        if db:
            await db.execute(
                update(ScheduleModel)
                .where(ScheduleModel.id == int(schedule.id))
                .values(next_run_time=schedule.next_run)
            )
            await db.commit()
        
        self._schedules[schedule.id] = schedule
        self._jobs[schedule.id] = job
        
        logger.info(f"Created cron schedule: {schedule.id} for task {task_id}")
        return schedule.id
        
    async def cancel_schedule(
        self,
        schedule_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> bool:
        """
        取消调度
        
        Args:
            schedule_id: 调度ID
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            是否取消成功
        """
        if schedule_id in self._schedules:
            # 从APScheduler移除
            if schedule_id in self._jobs:
                self.scheduler.remove_job(schedule_id)
                del self._jobs[schedule_id]
            
            # 从数据库删除
            db = db_session or self._db_session
            if db:
                try:
                    await db.execute(
                        delete(ScheduleModel).where(ScheduleModel.id == int(schedule_id))
                    )
                    await db.commit()
                except (ValueError, TypeError):
                    # 如果schedule_id不是数字，尝试通过其他方式查找
                    pass
            
            del self._schedules[schedule_id]
            logger.info(f"Cancelled schedule: {schedule_id}")
            return True
        return False
        
    async def list_schedules(
        self,
        task_id: Optional[str] = None,
        enabled: Optional[bool] = None,
        db_session: Optional[AsyncSession] = None
    ) -> List[TaskSchedule]:
        """
        从数据库列出调度
        
        Args:
            task_id: 任务ID过滤
            enabled: 启用状态过滤
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            调度列表
        """
        db = db_session or self._db_session
        if not db:
            # 如果没有数据库会话，返回内存中的调度
            schedules = list(self._schedules.values())
            if task_id:
                schedules = [s for s in schedules if s.task_id == task_id]
            if enabled is not None:
                schedules = [s for s in schedules if s.enabled == enabled]
            return schedules
        
        # 从数据库查询
        query = select(ScheduleModel)
        
        if task_id:
            try:
                task_id_int = int(task_id)
                query = query.where(ScheduleModel.task_id == task_id_int)
            except (ValueError, TypeError):
                # 如果task_id不是数字，返回空列表
                return []
        
        if enabled is not None:
            query = query.where(ScheduleModel.enabled == enabled)
        
        result = await db.execute(query)
        db_schedules = result.scalars().all()
        
        # 转换为TaskSchedule对象
        schedules = [TaskSchedule.from_db_model(db_schedule) for db_schedule in db_schedules]
        
        # 同步到内存（用于快速访问）
        for schedule in schedules:
            self._schedules[schedule.id] = schedule
        
        return schedules
        
    async def get_schedule(
        self,
        schedule_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[TaskSchedule]:
        """
        从数据库获取调度
        
        Args:
            schedule_id: 调度ID
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            调度对象，如果不存在返回None
        """
        # 先检查内存
        if schedule_id in self._schedules:
            return self._schedules[schedule_id]
        
        # 从数据库查询
        db = db_session or self._db_session
        if db:
            try:
                result = await db.execute(
                    select(ScheduleModel).where(ScheduleModel.id == int(schedule_id))
                )
                db_schedule = result.scalar_one_or_none()
                if db_schedule:
                    schedule = TaskSchedule.from_db_model(db_schedule)
                    self._schedules[schedule.id] = schedule
                    return schedule
            except (ValueError, TypeError):
                pass
        
        return None
        
    async def update_schedule_status(
        self,
        schedule_id: str,
        enabled: bool,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[TaskSchedule]:
        """
        更新调度状态
        
        Args:
            schedule_id: 调度ID
            enabled: 是否启用
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            更新后的调度，如果不存在返回None
        """
        schedule = await self.get_schedule(schedule_id, db_session=db_session)
        if not schedule:
            return None
        
        schedule.enabled = enabled
        schedule.updated_at = datetime.now()
        
        # 更新数据库
        db = db_session or self._db_session
        if db:
            try:
                await db.execute(
                    update(ScheduleModel)
                    .where(ScheduleModel.id == int(schedule_id))
                    .values(enabled=enabled, updated_at=datetime.now())
                )
                await db.commit()
            except (ValueError, TypeError):
                pass
        
        # 暂停或恢复APScheduler中的任务
        if schedule_id in self._jobs:
            if enabled:
                self.scheduler.resume_job(schedule_id)
            else:
                self.scheduler.pause_job(schedule_id)
        
        logger.info(f"Updated schedule {schedule_id} status to {enabled}")
        return schedule
    
    async def _load_schedules_from_db(self, db: AsyncSession) -> None:
        """
        从数据库加载所有启用的调度
        
        Args:
            db: 数据库会话
        """
        try:
            result = await db.execute(
                select(ScheduleModel).where(ScheduleModel.enabled == True)
            )
            db_schedules = result.scalars().all()
            
            for db_schedule in db_schedules:
                schedule = TaskSchedule.from_db_model(db_schedule)
                self._schedules[schedule.id] = schedule
                
                # 重新添加到APScheduler（需要回调函数，这里先跳过，由外部提供）
                # 注意：实际使用时需要在启动时提供回调函数
                logger.info(f"Loaded schedule {schedule.id} from database")
        except Exception as e:
            logger.error(f"Failed to load schedules from database: {e}")


# 全局调度器实例（注意：需要在使用时传入db_session）
_global_scheduler: Optional[TaskScheduler] = None


def get_global_scheduler(db_session: Optional[AsyncSession] = None) -> TaskScheduler:
    """
    获取全局调度器
    
    Args:
        db_session: 数据库会话（如果提供，会创建新的调度器实例）
        
    Returns:
        调度器实例
    """
    global _global_scheduler
    if _global_scheduler is None or db_session is not None:
        _global_scheduler = TaskScheduler(db_session=db_session)
    return _global_scheduler
