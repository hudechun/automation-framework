"""
监控API路由
"""
from fastapi import APIRouter
from ...observability.monitor import PerformanceMonitor

router = APIRouter()
monitor = PerformanceMonitor()


@router.get("/system")
async def get_system_metrics():
    """获取系统指标"""
    metrics = monitor.collector.collect_system_metrics()
    return metrics.to_dict()


@router.get("/health")
async def health_check():
    """健康检查"""
    status = monitor.get_status()
    return status


@router.get("/metrics")
async def get_metrics():
    """获取性能指标"""
    recent_metrics = monitor.collector.get_recent_system_metrics(10)
    return [m.to_dict() for m in recent_metrics]


@router.get("/tasks")
async def get_task_status():
    """获取任务状态"""
    # TODO: 实现任务状态查询
    return {"active_tasks": 0, "queued_tasks": 0}
