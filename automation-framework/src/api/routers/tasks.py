"""
任务管理API路由
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...task.task_manager import TaskManager, get_global_task_manager
from ...task.scheduler import TaskScheduler
from ...task.executor import get_global_executor
from ...core.types import TaskStatus, DriverType
from ...core.action_serializer import deserialize_actions
from ..dependencies import get_db

router = APIRouter()


class TaskCreate(BaseModel):
    """任务创建模型"""
    name: str
    description: str
    actions: List[dict]
    config: Optional[dict] = None


class TaskUpdate(BaseModel):
    """任务更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    actions: Optional[List[dict]] = None
    config: Optional[dict] = None


@router.post("", response_model=dict)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建任务"""
    # 反序列化actions
    actions = deserialize_actions(task_data.actions) if task_data.actions else []
    
    # 创建TaskManager实例
    task_manager = get_global_task_manager(db_session=db)
    
    # 创建任务
    task = await task_manager.create_task(
        name=task_data.name,
        description=task_data.description,
        driver_type=DriverType.BROWSER,  # 默认浏览器，可以从请求中获取
        actions=actions,
        config=task_data.config or {},
        db_session=db
    )
    return task.to_dict()


@router.get("", response_model=List[dict])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """列出任务"""
    task_manager = get_global_task_manager(db_session=db)
    
    # 转换status字符串为枚举
    status_enum = None
    if status:
        try:
            status_enum = TaskStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    tasks = await task_manager.list_tasks(
        status=status_enum,
        limit=limit,
        offset=skip,
        db_session=db
    )
    return [t.to_dict() for t in tasks]


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    task_manager = get_global_task_manager(db_session=db)
    task = await task_manager.get_task(task_id, db_session=db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    task_manager = get_global_task_manager(db_session=db)
    
    # 处理actions反序列化
    actions = None
    if task_data.actions is not None:
        actions = deserialize_actions(task_data.actions)
    
    task = await task_manager.update_task(
        task_id,
        name=task_data.name,
        description=task_data.description,
        actions=actions,
        config=task_data.config,
        metadata=None,  # metadata可以存储在config中
        db_session=db
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    task_manager = get_global_task_manager(db_session=db)
    success = await task_manager.delete_task(task_id, db_session=db)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/execute")
async def execute_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """执行任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.execute_task(task_id, db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Execution failed"))
    
    return result


@router.post("/{task_id}/pause")
async def pause_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """暂停任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.pause_task(task_id, db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Pause failed"))
    
    return result


@router.post("/{task_id}/resume")
async def resume_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """恢复任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.resume_task(task_id, db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Resume failed"))
    
    return result


@router.post("/{task_id}/stop")
async def stop_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """停止任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.stop_task(task_id, db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Stop failed"))
    
    return result


# 任务调度端点
class ScheduleCreate(BaseModel):
    """调度创建模型"""
    schedule_type: str  # once, interval, cron
    trigger_time: Optional[str] = None  # for once
    interval_seconds: Optional[int] = None  # for interval
    cron_expression: Optional[str] = None  # for cron


@router.post("/{task_id}/schedule", response_model=dict)
async def create_schedule(
    task_id: str,
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建任务调度"""
    from datetime import datetime
    
    task_manager = get_global_task_manager(db_session=db)
    task = await task_manager.get_task(task_id, db_session=db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 获取执行器用于回调
    executor = get_global_executor(db_session=db)
    
    # 定义回调函数
    async def execute_scheduled_task(t_id: str):
        """调度任务执行回调"""
        await executor.execute_task(t_id, db_session=db)
    
    scheduler = get_global_scheduler(db_session=db)
    
    if schedule_data.schedule_type == "once":
        if not schedule_data.trigger_time:
            raise HTTPException(status_code=400, detail="trigger_time required for once schedule")
        try:
            run_date = datetime.fromisoformat(schedule_data.trigger_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid trigger_time format. Use ISO format.")
        schedule_id = await scheduler.schedule_once(
            task_id,
            run_date,
            execute_scheduled_task,
            db_session=db
        )
    elif schedule_data.schedule_type == "interval":
        if not schedule_data.interval_seconds:
            raise HTTPException(status_code=400, detail="interval_seconds required for interval schedule")
        schedule_id = await scheduler.schedule_interval(
            task_id,
            schedule_data.interval_seconds,
            execute_scheduled_task,
            db_session=db
        )
    elif schedule_data.schedule_type == "cron":
        if not schedule_data.cron_expression:
            raise HTTPException(status_code=400, detail="cron_expression required for cron schedule")
        schedule_id = await scheduler.schedule_cron(
            task_id,
            schedule_data.cron_expression,
            execute_scheduled_task,
            db_session=db
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid schedule_type")
    
    return {"schedule_id": schedule_id, "task_id": task_id, "type": schedule_data.schedule_type}


@router.get("/{task_id}/schedules", response_model=List[dict])
async def list_schedules(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """列出任务的所有调度"""
    scheduler = get_global_scheduler(db_session=db)
    schedules = await scheduler.list_schedules(task_id=task_id, db_session=db)
    return [s.to_dict() for s in schedules]


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除调度"""
    scheduler = get_global_scheduler(db_session=db)
    success = await scheduler.cancel_schedule(schedule_id, db_session=db)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully"}
