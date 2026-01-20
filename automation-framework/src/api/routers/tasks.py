"""
任务管理API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from ...task.task_manager import TaskManager
from ...task.scheduler import TaskScheduler
# 注意：已迁移到 SQLAlchemy，不再使用 Tortoise ORM 模型
# 如需使用数据库模型，请从 ...models.sqlalchemy_models 导入

router = APIRouter()
task_manager = TaskManager()
scheduler = TaskScheduler()


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
async def create_task(task_data: TaskCreate):
    """创建任务"""
    task = await task_manager.create_task(
        name=task_data.name,
        description=task_data.description,
        actions=task_data.actions,
        config=task_data.config or {}
    )
    return task.to_dict()


@router.get("", response_model=List[dict])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None
):
    """列出任务"""
    tasks = await task_manager.list_tasks(
        skip=skip,
        limit=limit,
        status=status
    )
    return [t.to_dict() for t in tasks]


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str):
    """获取任务详情"""
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: str, task_data: TaskUpdate):
    """更新任务"""
    updates = task_data.dict(exclude_unset=True)
    task = await task_manager.update_task(task_id, **updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    success = await task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/execute")
async def execute_task(task_id: str):
    """执行任务"""
    # TODO: 实现任务执行逻辑
    return {"message": "Task execution started", "task_id": task_id}


@router.post("/{task_id}/pause")
async def pause_task(task_id: str):
    """暂停任务"""
    # TODO: 实现任务暂停逻辑
    return {"message": "Task paused", "task_id": task_id}


@router.post("/{task_id}/resume")
async def resume_task(task_id: str):
    """恢复任务"""
    # TODO: 实现任务恢复逻辑
    return {"message": "Task resumed", "task_id": task_id}


@router.post("/{task_id}/stop")
async def stop_task(task_id: str):
    """停止任务"""
    # TODO: 实现任务停止逻辑
    return {"message": "Task stopped", "task_id": task_id}


# 任务调度端点
class ScheduleCreate(BaseModel):
    """调度创建模型"""
    schedule_type: str  # once, interval, cron
    trigger_time: Optional[str] = None  # for once
    interval_seconds: Optional[int] = None  # for interval
    cron_expression: Optional[str] = None  # for cron


@router.post("/{task_id}/schedule", response_model=dict)
async def create_schedule(task_id: str, schedule_data: ScheduleCreate):
    """创建任务调度"""
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if schedule_data.schedule_type == "once":
        if not schedule_data.trigger_time:
            raise HTTPException(status_code=400, detail="trigger_time required for once schedule")
        schedule_id = await scheduler.schedule_once(task_id, schedule_data.trigger_time)
    elif schedule_data.schedule_type == "interval":
        if not schedule_data.interval_seconds:
            raise HTTPException(status_code=400, detail="interval_seconds required for interval schedule")
        schedule_id = await scheduler.schedule_interval(task_id, schedule_data.interval_seconds)
    elif schedule_data.schedule_type == "cron":
        if not schedule_data.cron_expression:
            raise HTTPException(status_code=400, detail="cron_expression required for cron schedule")
        schedule_id = await scheduler.schedule_cron(task_id, schedule_data.cron_expression)
    else:
        raise HTTPException(status_code=400, detail="Invalid schedule_type")
    
    return {"schedule_id": schedule_id, "task_id": task_id, "type": schedule_data.schedule_type}


@router.get("/{task_id}/schedules", response_model=List[dict])
async def list_schedules(task_id: str):
    """列出任务的所有调度"""
    schedules = await scheduler.list_schedules(task_id)
    return schedules


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """删除调度"""
    success = await scheduler.cancel_schedule(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully"}
