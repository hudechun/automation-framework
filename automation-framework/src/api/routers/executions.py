"""
历史记录API路由
"""
from fastapi import APIRouter, Query
from typing import List, Optional

from ...task.history import HistoryManager

router = APIRouter()
history_manager = HistoryManager()


@router.get("", response_model=List[dict])
async def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    task_id: Optional[str] = None,
    status: Optional[str] = None
):
    """列出执行记录"""
    records = await history_manager.list_records(
        skip=skip,
        limit=limit,
        task_id=task_id,
        status=status
    )
    return [r.to_dict() for r in records]


@router.get("/{execution_id}", response_model=dict)
async def get_execution(execution_id: str):
    """获取执行详情"""
    record = await history_manager.get_record(execution_id)
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    return record.to_dict()


@router.post("/export")
async def export_executions(
    format: str = Query("json", regex="^(json|csv)$"),
    task_id: Optional[str] = None
):
    """导出执行记录"""
    # TODO: 实现导出逻辑
    return {"message": "Export started", "format": format}


# 统计端点
@router.get("/statistics/tasks", response_model=dict)
async def get_task_statistics(
    task_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取任务统计信息"""
    stats = await history_manager.get_statistics(
        task_id=task_id,
        start_date=start_date,
        end_date=end_date
    )
    return stats


@router.get("/statistics/success-rate", response_model=dict)
async def get_success_rate(
    task_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取成功率统计"""
    stats = await history_manager.get_statistics(
        task_id=task_id,
        start_date=start_date,
        end_date=end_date
    )
    total = stats.get("total_executions", 0)
    success = stats.get("successful_executions", 0)
    success_rate = (success / total * 100) if total > 0 else 0
    
    return {
        "total_executions": total,
        "successful_executions": success,
        "failed_executions": stats.get("failed_executions", 0),
        "success_rate": round(success_rate, 2)
    }


@router.get("/statistics/trends", response_model=dict)
async def get_trends(
    task_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90)
):
    """获取执行趋势分析"""
    trends = await history_manager.get_trends(task_id=task_id, days=days)
    return trends
