"""
FastAPIAdmin 后台接口 - 按功能分类提供完整的CRUD接口
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from ...models.sqlalchemy_models import (
    Task, Schedule, ExecutionRecord, Session, SessionCheckpoint,
    ModelConfig, ModelMetrics, SystemLog, NotificationConfig,
    FileStorage, Plugin, PerformanceMetrics
)
from ...task.task_manager import get_global_task_manager
from ...task.executor import get_global_executor
from ...task.scheduler import get_global_scheduler
from ...core.session import get_global_session_manager
from ..dependencies import get_db

router = APIRouter(prefix="/admin/api", tags=["admin"])


# ==================== 通用响应模型 ====================

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


# ==================== 1. 任务管理 (Tasks) ====================

class TaskCreate(BaseModel):
    """任务创建模型"""
    name: str
    description: Optional[str] = None
    task_type: str  # browser, desktop, hybrid
    actions: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    """任务更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


@router.get("/tasks", response_model=PaginatedResponse)
async def admin_list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜索任务名称或描述"),
    status: Optional[str] = Query(None, description="任务状态过滤"),
    task_type: Optional[str] = Query(None, description="任务类型过滤"),
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表（分页）"""
    query = select(Task)
    
    # 搜索过滤
    if search:
        query = query.where(
            or_(
                Task.name.like(f"%{search}%"),
                Task.description.like(f"%{search}%")
            )
        )
    
    # 状态过滤
    if status:
        query = query.where(Task.status == status)
    
    # 类型过滤
    if task_type:
        query = query.where(Task.task_type == task_type)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    items = [{
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "task_type": task.task_type,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    } for task in tasks]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def admin_get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "task_type": task.task_type,
        "actions": task.actions,
        "config": task.config,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


@router.post("/tasks", response_model=SuccessResponse)
async def admin_create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建任务"""
    from ...core.types import DriverType
    from ...core.action_serializer import deserialize_actions
    
    task_manager = get_global_task_manager(db_session=db)
    actions = deserialize_actions(task_data.actions) if task_data.actions else []
    
    task = await task_manager.create_task(
        name=task_data.name,
        description=task_data.description or "",
        driver_type=DriverType(task_data.task_type),
        actions=actions,
        config=task_data.config or {},
        db_session=db
    )
    
    return SuccessResponse(
        message="Task created successfully",
        data={"task_id": task.id}
    )


@router.put("/tasks/{task_id}", response_model=SuccessResponse)
async def admin_update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    from ...core.action_serializer import deserialize_actions
    
    task_manager = get_global_task_manager(db_session=db)
    
    actions = None
    if task_data.actions is not None:
        actions = deserialize_actions(task_data.actions)
    
    task = await task_manager.update_task(
        str(task_id),
        name=task_data.name,
        description=task_data.description,
        actions=actions,
        config=task_data.config,
        db_session=db
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.status:
        await task_manager.update_task_status(
            str(task_id),
            task_data.status,
            db_session=db
        )
    
    return SuccessResponse(message="Task updated successfully")


@router.delete("/tasks/{task_id}", response_model=SuccessResponse)
async def admin_delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    task_manager = get_global_task_manager(db_session=db)
    success = await task_manager.delete_task(str(task_id), db_session=db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return SuccessResponse(message="Task deleted successfully")


@router.post("/tasks/{task_id}/execute", response_model=SuccessResponse)
async def admin_execute_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """执行任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.execute_task(str(task_id), db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return SuccessResponse(
        message="Task execution started",
        data=result
    )


@router.post("/tasks/{task_id}/pause", response_model=SuccessResponse)
async def admin_pause_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """暂停任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.pause_task(str(task_id), db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return SuccessResponse(message="Task paused")


@router.post("/tasks/{task_id}/resume", response_model=SuccessResponse)
async def admin_resume_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """恢复任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.resume_task(str(task_id), db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return SuccessResponse(message="Task resumed")


@router.post("/tasks/{task_id}/stop", response_model=SuccessResponse)
async def admin_stop_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """停止任务"""
    executor = get_global_executor(db_session=db)
    result = await executor.stop_task(str(task_id), db_session=db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return SuccessResponse(message="Task stopped")


# ==================== 2. 调度管理 (Schedules) ====================

@router.get("/schedules", response_model=PaginatedResponse)
async def admin_list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: Optional[int] = Query(None),
    enabled: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取调度列表（分页）"""
    query = select(Schedule)
    
    if task_id:
        query = query.where(Schedule.task_id == task_id)
    if enabled is not None:
        query = query.where(Schedule.enabled == enabled)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(Schedule.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    schedules = result.scalars().all()
    
    items = [{
        "id": schedule.id,
        "task_id": schedule.task_id,
        "schedule_type": schedule.schedule_type,
        "schedule_config": schedule.schedule_config,
        "enabled": schedule.enabled,
        "next_run_time": schedule.next_run_time.isoformat() if schedule.next_run_time else None,
        "last_run_time": schedule.last_run_time.isoformat() if schedule.last_run_time else None,
        "created_at": schedule.created_at.isoformat(),
    } for schedule in schedules]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/schedules/{schedule_id}", response_model=Dict[str, Any])
async def admin_get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取调度详情"""
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {
        "id": schedule.id,
        "task_id": schedule.task_id,
        "schedule_type": schedule.schedule_type,
        "schedule_config": schedule.schedule_config,
        "enabled": schedule.enabled,
        "next_run_time": schedule.next_run_time.isoformat() if schedule.next_run_time else None,
        "last_run_time": schedule.last_run_time.isoformat() if schedule.last_run_time else None,
        "created_at": schedule.created_at.isoformat(),
        "updated_at": schedule.updated_at.isoformat(),
    }


@router.put("/schedules/{schedule_id}/enable", response_model=SuccessResponse)
async def admin_enable_schedule(
    schedule_id: int,
    enabled: bool = Body(True),
    db: AsyncSession = Depends(get_db)
):
    """启用/禁用调度"""
    scheduler = get_global_scheduler(db_session=db)
    schedule = await scheduler.update_schedule_status(str(schedule_id), enabled, db_session=db)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return SuccessResponse(message=f"Schedule {'enabled' if enabled else 'disabled'}")


@router.delete("/schedules/{schedule_id}", response_model=SuccessResponse)
async def admin_delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除调度"""
    scheduler = get_global_scheduler(db_session=db)
    success = await scheduler.cancel_schedule(str(schedule_id), db_session=db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return SuccessResponse(message="Schedule deleted successfully")


# ==================== 3. 执行记录 (ExecutionRecords) ====================

@router.get("/executions", response_model=PaginatedResponse)
async def admin_list_executions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取执行记录列表（分页）"""
    query = select(ExecutionRecord)
    
    if task_id:
        query = query.where(ExecutionRecord.task_id == task_id)
    if status:
        query = query.where(ExecutionRecord.status == status)
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.where(ExecutionRecord.start_time >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.where(ExecutionRecord.start_time <= end)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(ExecutionRecord.start_time.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    executions = result.scalars().all()
    
    items = [{
        "id": exec.id,
        "task_id": exec.task_id,
        "status": exec.status,
        "start_time": exec.start_time.isoformat(),
        "end_time": exec.end_time.isoformat() if exec.end_time else None,
        "duration": exec.duration,
        "error_message": exec.error_message,
    } for exec in executions]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/executions/{execution_id}", response_model=Dict[str, Any])
async def admin_get_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取执行记录详情"""
    result = await db.execute(select(ExecutionRecord).where(ExecutionRecord.id == execution_id))
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "id": execution.id,
        "task_id": execution.task_id,
        "status": execution.status,
        "start_time": execution.start_time.isoformat(),
        "end_time": execution.end_time.isoformat() if execution.end_time else None,
        "duration": execution.duration,
        "logs": execution.logs,
        "screenshots": execution.screenshots,
        "error_message": execution.error_message,
        "error_stack": execution.error_stack,
        "result": execution.result,
        "created_at": execution.created_at.isoformat(),
    }


@router.delete("/executions/{execution_id}", response_model=SuccessResponse)
async def admin_delete_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除执行记录"""
    result = await db.execute(delete(ExecutionRecord).where(ExecutionRecord.id == execution_id))
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return SuccessResponse(message="Execution deleted successfully")


# ==================== 4. 会话管理 (Sessions) ====================

@router.get("/sessions", response_model=PaginatedResponse)
async def admin_list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: Optional[str] = Query(None),
    driver_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取会话列表（分页）"""
    session_manager = get_global_session_manager(db_session=db)
    
    from ...core.types import SessionState, DriverType
    state_enum = SessionState(state) if state else None
    driver_type_enum = DriverType(driver_type) if driver_type else None
    
    sessions = await session_manager.list_sessions(
        state=state_enum,
        driver_type=driver_type_enum,
        limit=page_size,
        offset=(page - 1) * page_size,
        db_session=db
    )
    
    # 获取总数
    stats = await session_manager.monitor_sessions(db_session=db)
    total = stats.get("total", 0)
    
    items = [session.to_dict() for session in sessions]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def admin_get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话详情"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@router.delete("/sessions/{session_id}", response_model=SuccessResponse)
async def admin_delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除会话"""
    session_manager = get_global_session_manager(db_session=db)
    success = await session_manager.delete_session(session_id, db_session=db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SuccessResponse(message="Session deleted successfully")


# ==================== 5. 会话检查点 (SessionCheckpoints) ====================

@router.get("/checkpoints", response_model=PaginatedResponse)
async def admin_list_checkpoints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取检查点列表（分页）"""
    query = select(SessionCheckpoint)
    
    if session_id:
        query = query.where(SessionCheckpoint.session_id == session_id)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(SessionCheckpoint.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    checkpoints = result.scalars().all()
    
    items = [{
        "id": cp.id,
        "session_id": cp.session_id,
        "checkpoint_name": cp.checkpoint_name,
        "actions_completed": cp.actions_completed,
        "created_at": cp.created_at.isoformat(),
    } for cp in checkpoints]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/checkpoints/{checkpoint_id}", response_model=Dict[str, Any])
async def admin_get_checkpoint(
    checkpoint_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取检查点详情"""
    result = await db.execute(select(SessionCheckpoint).where(SessionCheckpoint.id == checkpoint_id))
    checkpoint = result.scalar_one_or_none()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    return {
        "id": checkpoint.id,
        "session_id": checkpoint.session_id,
        "checkpoint_name": checkpoint.checkpoint_name,
        "state_data": checkpoint.state_data,
        "actions_completed": checkpoint.actions_completed,
        "created_at": checkpoint.created_at.isoformat(),
    }


# ==================== 6. 模型配置 (ModelConfigs) ====================

class ModelConfigCreate(BaseModel):
    """模型配置创建模型"""
    name: str
    provider: str
    model: str
    api_key: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    enabled: bool = True


class ModelConfigUpdate(BaseModel):
    """模型配置更新模型"""
    name: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


@router.get("/model-configs", response_model=PaginatedResponse)
async def admin_list_model_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取模型配置列表（分页）"""
    query = select(ModelConfig)
    
    if search:
        query = query.where(ModelConfig.name.like(f"%{search}%"))
    if provider:
        query = query.where(ModelConfig.provider == provider)
    if enabled is not None:
        query = query.where(ModelConfig.enabled == enabled)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(ModelConfig.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    configs = result.scalars().all()
    
    items = [{
        "id": config.id,
        "name": config.name,
        "provider": config.provider,
        "model": config.model,
        "enabled": config.enabled,
        "created_at": config.created_at.isoformat(),
    } for config in configs]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/model-configs/{config_id}", response_model=Dict[str, Any])
async def admin_get_model_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取模型配置详情"""
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="Model config not found")
    
    return {
        "id": config.id,
        "name": config.name,
        "provider": config.provider,
        "model": config.model,
        "api_key": config.api_key,  # 注意：生产环境应该隐藏
        "params": config.params,
        "enabled": config.enabled,
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat(),
    }


@router.post("/model-configs", response_model=SuccessResponse)
async def admin_create_model_config(
    config_data: ModelConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建模型配置"""
    config = ModelConfig(
        name=config_data.name,
        provider=config_data.provider,
        model=config_data.model,
        api_key=config_data.api_key,
        params=config_data.params or {},
        enabled=config_data.enabled
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return SuccessResponse(
        message="Model config created successfully",
        data={"config_id": config.id}
    )


@router.put("/model-configs/{config_id}", response_model=SuccessResponse)
async def admin_update_model_config(
    config_id: int,
    config_data: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新模型配置"""
    update_data = config_data.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now()
        await db.execute(
            update(ModelConfig)
            .where(ModelConfig.id == config_id)
            .values(**update_data)
        )
        await db.commit()
    
    return SuccessResponse(message="Model config updated successfully")


@router.delete("/model-configs/{config_id}", response_model=SuccessResponse)
async def admin_delete_model_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除模型配置"""
    result = await db.execute(delete(ModelConfig).where(ModelConfig.id == config_id))
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Model config not found")
    
    return SuccessResponse(message="Model config deleted successfully")


# ==================== 7. 模型指标 (ModelMetrics) ====================

@router.get("/model-metrics", response_model=PaginatedResponse)
async def admin_list_model_metrics(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    model_config_id: Optional[int] = Query(None),
    success: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取模型指标列表（分页）"""
    query = select(ModelMetrics)
    
    if model_config_id:
        query = query.where(ModelMetrics.model_config_id == model_config_id)
    if success is not None:
        query = query.where(ModelMetrics.success == success)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(ModelMetrics.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    items = [{
        "id": metric.id,
        "model_config_id": metric.model_config_id,
        "latency": metric.latency,
        "cost": metric.cost,
        "tokens": metric.tokens,
        "success": metric.success,
        "error_message": metric.error_message,
        "created_at": metric.created_at.isoformat(),
    } for metric in metrics]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ==================== 8. 系统日志 (SystemLogs) ====================

@router.get("/system-logs", response_model=PaginatedResponse)
async def admin_list_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取系统日志列表（分页）"""
    query = select(SystemLog)
    
    if level:
        query = query.where(SystemLog.level == level)
    if module:
        query = query.where(SystemLog.module.like(f"%{module}%"))
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.where(SystemLog.created_at >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.where(SystemLog.created_at <= end)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    items = [{
        "id": log.id,
        "level": log.level,
        "message": log.message,
        "module": log.module,
        "function": log.function,
        "line_number": log.line_number,
        "extra_data": log.extra_data,
        "created_at": log.created_at.isoformat(),
    } for log in logs]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.delete("/system-logs", response_model=SuccessResponse)
async def admin_clear_system_logs(
    days: int = Query(30, ge=1, le=365, description="保留最近N天的日志"),
    db: AsyncSession = Depends(get_db)
):
    """清理系统日志（保留最近N天）"""
    cutoff_date = datetime.now() - timedelta(days=days)
    result = await db.execute(
        delete(SystemLog).where(SystemLog.created_at < cutoff_date)
    )
    await db.commit()
    
    return SuccessResponse(
        message=f"Cleared {result.rowcount} log entries older than {days} days"
    )


# ==================== 9. 通知配置 (NotificationConfigs) ====================

class NotificationConfigCreate(BaseModel):
    """通知配置创建模型"""
    name: str
    notification_type: str
    config: Dict[str, Any]
    enabled: bool = True


@router.get("/notification-configs", response_model=PaginatedResponse)
async def admin_list_notification_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    notification_type: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取通知配置列表（分页）"""
    query = select(NotificationConfig)
    
    if notification_type:
        query = query.where(NotificationConfig.notification_type == notification_type)
    if enabled is not None:
        query = query.where(NotificationConfig.enabled == enabled)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(NotificationConfig.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    configs = result.scalars().all()
    
    items = [{
        "id": config.id,
        "name": config.name,
        "notification_type": config.notification_type,
        "enabled": config.enabled,
        "created_at": config.created_at.isoformat(),
    } for config in configs]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/notification-configs", response_model=SuccessResponse)
async def admin_create_notification_config(
    config_data: NotificationConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建通知配置"""
    config = NotificationConfig(
        name=config_data.name,
        notification_type=config_data.notification_type,
        config=config_data.config,
        enabled=config_data.enabled
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return SuccessResponse(
        message="Notification config created successfully",
        data={"config_id": config.id}
    )


@router.delete("/notification-configs/{config_id}", response_model=SuccessResponse)
async def admin_delete_notification_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除通知配置"""
    result = await db.execute(delete(NotificationConfig).where(NotificationConfig.id == config_id))
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    return SuccessResponse(message="Notification config deleted successfully")


# ==================== 10. 文件存储 (FileStorage) ====================

@router.get("/files", response_model=PaginatedResponse)
async def admin_list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    related_type: Optional[str] = Query(None),
    related_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取文件列表（分页）"""
    query = select(FileStorage)
    
    if file_type:
        query = query.where(FileStorage.file_type == file_type)
    if related_type:
        query = query.where(FileStorage.related_type == related_type)
    if related_id:
        query = query.where(FileStorage.related_id == related_id)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(FileStorage.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    files = result.scalars().all()
    
    items = [{
        "id": file.id,
        "file_name": file.file_name,
        "file_path": file.file_path,
        "file_type": file.file_type,
        "file_size": file.file_size,
        "mime_type": file.mime_type,
        "related_type": file.related_type,
        "related_id": file.related_id,
        "created_at": file.created_at.isoformat(),
    } for file in files]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.delete("/files/{file_id}", response_model=SuccessResponse)
async def admin_delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除文件记录"""
    result = await db.execute(select(FileStorage).where(FileStorage.id == file_id))
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 删除物理文件
    import os
    if os.path.exists(file.file_path):
        try:
            os.remove(file.file_path)
        except Exception as e:
            pass  # 记录错误但不阻止删除记录
    
    # 删除数据库记录
    await db.execute(delete(FileStorage).where(FileStorage.id == file_id))
    await db.commit()
    
    return SuccessResponse(message="File deleted successfully")


# ==================== 11. 插件管理 (Plugins) ====================

@router.get("/plugins", response_model=PaginatedResponse)
async def admin_list_plugins(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plugin_type: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取插件列表（分页）"""
    query = select(Plugin)
    
    if plugin_type:
        query = query.where(Plugin.plugin_type == plugin_type)
    if enabled is not None:
        query = query.where(Plugin.enabled == enabled)
    if search:
        query = query.where(
            or_(
                Plugin.name.like(f"%{search}%"),
                Plugin.description.like(f"%{search}%")
            )
        )
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(Plugin.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    plugins = result.scalars().all()
    
    items = [{
        "id": plugin.id,
        "name": plugin.name,
        "version": plugin.version,
        "description": plugin.description,
        "plugin_type": plugin.plugin_type,
        "enabled": plugin.enabled,
        "created_at": plugin.created_at.isoformat(),
    } for plugin in plugins]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.put("/plugins/{plugin_id}/enable", response_model=SuccessResponse)
async def admin_enable_plugin(
    plugin_id: int,
    enabled: bool = Body(True),
    db: AsyncSession = Depends(get_db)
):
    """启用/禁用插件"""
    await db.execute(
        update(Plugin)
        .where(Plugin.id == plugin_id)
        .values(enabled=enabled, updated_at=datetime.now())
    )
    await db.commit()
    
    return SuccessResponse(message=f"Plugin {'enabled' if enabled else 'disabled'}")


# ==================== 12. 性能指标 (PerformanceMetrics) ====================

@router.get("/performance-metrics", response_model=PaginatedResponse)
async def admin_list_performance_metrics(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    metric_type: Optional[str] = Query(None),
    metric_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取性能指标列表（分页）"""
    query = select(PerformanceMetrics)
    
    if metric_type:
        query = query.where(PerformanceMetrics.metric_type == metric_type)
    if metric_name:
        query = query.where(PerformanceMetrics.metric_name == metric_name)
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.where(PerformanceMetrics.created_at >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.where(PerformanceMetrics.created_at <= end)
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(PerformanceMetrics.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    items = [{
        "id": metric.id,
        "metric_type": metric.metric_type,
        "metric_name": metric.metric_name,
        "value": metric.value,
        "unit": metric.unit,
        "metadata": metric.metadata,
        "created_at": metric.created_at.isoformat(),
    } for metric in metrics]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ==================== 13. 仪表板统计 (Dashboard) ====================

@router.get("/dashboard/stats", response_model=Dict[str, Any])
async def admin_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取仪表板统计数据"""
    # 任务统计
    task_total = await db.execute(select(func.count(Task.id)))
    task_stats = await db.execute(
        select(Task.status, func.count(Task.id))
        .group_by(Task.status)
    )
    task_status_counts = {row[0]: row[1] for row in task_stats.all()}
    
    # 执行记录统计
    execution_total = await db.execute(select(func.count(ExecutionRecord.id)))
    execution_stats = await db.execute(
        select(ExecutionRecord.status, func.count(ExecutionRecord.id))
        .group_by(ExecutionRecord.status)
    )
    execution_status_counts = {row[0]: row[1] for row in execution_stats.all()}
    
    # 会话统计
    session_manager = get_global_session_manager(db_session=db)
    session_stats = await session_manager.monitor_sessions(db_session=db)
    
    # 调度统计
    schedule_total = await db.execute(select(func.count(Schedule.id)))
    schedule_enabled = await db.execute(
        select(func.count(Schedule.id)).where(Schedule.enabled == True)
    )
    
    # 最近24小时执行数
    yesterday = datetime.now() - timedelta(days=1)
    recent_executions = await db.execute(
        select(func.count(ExecutionRecord.id))
        .where(ExecutionRecord.start_time >= yesterday)
    )
    
    return {
        "tasks": {
            "total": task_total.scalar() or 0,
            "by_status": task_status_counts
        },
        "executions": {
            "total": execution_total.scalar() or 0,
            "by_status": execution_status_counts,
            "recent_24h": recent_executions.scalar() or 0
        },
        "sessions": session_stats,
        "schedules": {
            "total": schedule_total.scalar() or 0,
            "enabled": schedule_enabled.scalar() or 0
        }
    }


@router.get("/dashboard/recent-executions", response_model=List[Dict[str, Any]])
async def admin_recent_executions(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取最近执行记录"""
    result = await db.execute(
        select(ExecutionRecord)
        .order_by(ExecutionRecord.start_time.desc())
        .limit(limit)
    )
    executions = result.scalars().all()
    
    return [{
        "id": exec.id,
        "task_id": exec.task_id,
        "status": exec.status,
        "start_time": exec.start_time.isoformat(),
        "duration": exec.duration,
        "error_message": exec.error_message,
    } for exec in executions]


@router.get("/dashboard/task-success-rate", response_model=Dict[str, Any])
async def admin_task_success_rate(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """获取任务成功率统计"""
    start_date = datetime.now() - timedelta(days=days)
    
    total = await db.execute(
        select(func.count(ExecutionRecord.id))
        .where(ExecutionRecord.start_time >= start_date)
    )
    
    success = await db.execute(
        select(func.count(ExecutionRecord.id))
        .where(
            and_(
                ExecutionRecord.start_time >= start_date,
                ExecutionRecord.status == "completed"
            )
        )
    )
    
    failed = await db.execute(
        select(func.count(ExecutionRecord.id))
        .where(
            and_(
                ExecutionRecord.start_time >= start_date,
                ExecutionRecord.status == "failed"
            )
        )
    )
    
    total_count = total.scalar() or 0
    success_count = success.scalar() or 0
    failed_count = failed.scalar() or 0
    
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "total": total_count,
        "success": success_count,
        "failed": failed_count,
        "success_rate": round(success_rate, 2),
        "period_days": days
    }
