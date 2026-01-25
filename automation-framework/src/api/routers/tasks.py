"""
任务管理API路由
"""
import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...task.task_manager import TaskManager, get_global_task_manager
from ...task.scheduler import TaskScheduler, get_global_scheduler
from ...task.executor import get_global_executor
from ...core.types import TaskStatus, DriverType
from ...core.action_serializer import deserialize_actions
from ...core.execution_progress import ExecutionProgress
from ..dependencies import get_db
from ..dependencies_user import get_current_user, get_current_user_id

logger = logging.getLogger(__name__)

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
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建任务"""
    # 反序列化actions
    actions = deserialize_actions(task_data.actions) if task_data.actions else []
    
    # 创建TaskManager实例
    task_manager = get_global_task_manager(db_session=db)
    
    # 创建任务
    # 获取当前用户信息
    user_id = get_current_user_id()
    user_name = current_user.user_name if hasattr(current_user, 'user_name') else None
    
    task = await task_manager.create_task(
        name=task_data.name,
        description=task_data.description,
        driver_type=DriverType.BROWSER,  # 默认浏览器，可以从请求中获取
        actions=actions,
        config=task_data.config or {},
        user_id=user_id,
        user_name=user_name,
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
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """执行任务"""
    # 验证任务所有权
    task_manager = get_global_task_manager(db_session=db)
    task = await task_manager.get_task(task_id, db_session=db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 检查用户权限（如果任务有user_id，则验证）
    if hasattr(task, 'user_id') and task.user_id and task.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作此任务")
    
    executor = get_global_executor(db_session=db)
    result = await executor.execute_task(
        task_id, 
        user_id=current_user.user_id,
        db_session=db
    )
    
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


# 执行状态和进度查询端点
@router.get("/{task_id}/execution/status")
async def get_execution_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务执行状态"""
    executor = get_global_executor(db_session=db)
    state = executor.get_execution_state(task_id)
    
    # 获取任务信息
    task_manager = get_global_task_manager(db_session=db)
    task = await task_manager.get_task(task_id, db_session=db)
    
    return {
        "task_id": task_id,
        "task_name": task.name if task else None,
        "state": state.value if state else None,
        "is_running": executor.is_task_running(task_id)
    }


@router.get("/{task_id}/execution/progress")
async def get_execution_progress(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务执行进度"""
    executor = get_global_executor(db_session=db)
    progress = executor.get_execution_progress(task_id)
    
    if progress:
        return progress.to_dict()
    else:
        # 如果没有进度信息，返回默认值
        return {
            "total_actions": 0,
            "current_action_index": 0,
            "completed_actions": 0,
            "failed_actions": 0,
            "remaining_actions": 0,
            "progress_percentage": 0.0,
            "elapsed_time": 0.0,
            "estimated_remaining_time": None,
            "average_action_time": 0.0
        }


@router.get("/{task_id}/execution/logs")
async def get_execution_logs(
    task_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取任务执行日志"""
    from ...models.sqlalchemy_models import ExecutionRecord as ExecutionRecordModel
    from sqlalchemy import select, desc
    
    # 获取最新的执行记录
    result = await db.execute(
        select(ExecutionRecordModel)
        .where(ExecutionRecordModel.task_id == task_id)
        .order_by(desc(ExecutionRecordModel.start_time))
        .limit(1)
    )
    execution_record = result.scalar_one_or_none()
    
    if not execution_record:
        return {"logs": [], "total": 0}
    
    # 从执行记录的logs字段解析日志
    logs = []
    if execution_record.logs:
        import json
        try:
            log_data = json.loads(execution_record.logs) if isinstance(execution_record.logs, str) else execution_record.logs
            if isinstance(log_data, list):
                logs = log_data[skip:skip+limit]
        except:
            # 如果解析失败，返回原始日志文本
            logs = [{"level": "info", "message": execution_record.logs, "timestamp": execution_record.start_time.isoformat()}]
    
    return {
        "logs": logs,
        "total": len(logs),
        "execution_id": execution_record.id
    }


@router.post("/parse")
async def parse_natural_language_task(
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    解析自然语言任务描述为操作序列
    
    Request body:
    {
        "description": "打开京东网站，搜索iPhone 15，获取第一个商品的价格"
    }
    """
    description = request.get("description", "")
    if not description:
        raise HTTPException(status_code=400, detail="Description is required")
    
    try:
        # 导入TaskPlanner
        from ...ai.agent import TaskPlanner
        from ...ai.llm import create_llm_provider
        from ...models.sqlalchemy_models import ModelConfig as ModelConfigModel
        from sqlalchemy import select
        
        # 获取默认的LLM配置
        result = await db.execute(
            select(ModelConfigModel)
            .where(ModelConfigModel.enabled == True)
            .limit(1)
        )
        model_config = result.scalar_one_or_none()
        
        if not model_config:
            raise HTTPException(
                status_code=500,
                detail="No LLM model configured. Please configure a model first."
            )
        
        # 创建LLM提供者和TaskPlanner
        llm = create_llm_provider(model_config)
        planner = TaskPlanner(llm)
        
        # 解析任务
        task_desc = await planner.parse_task(description)
        
        # 生成计划
        plan = await planner.plan(task_desc)
        
        # 转换为Action对象
        from ...core.action_serializer import deserialize_actions
        actions = []
        for step in plan:
            # 将plan步骤转换为Action格式
            action_dict = {
                "action_type": step.get("action", "click"),
                "params": step.get("params", {}),
                "description": step.get("description", "")
            }
            # 这里需要根据实际的plan格式来转换
            # 暂时返回plan的原始格式
            actions.append(step)
        
        return {
            "success": True,
            "task_description": {
                "goal": task_desc.goal,
                "constraints": task_desc.constraints,
                "parameters": task_desc.parameters,
                "context": task_desc.context
            },
            "actions": actions,
            "total_actions": len(actions)
        }
        
    except Exception as e:
        logger.error(f"Failed to parse natural language task: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse task: {str(e)}"
        )


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
