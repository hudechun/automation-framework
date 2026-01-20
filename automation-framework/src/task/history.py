"""
历史任务管理器 - 管理任务执行历史记录
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
from pathlib import Path

from ..core.types import TaskStatus


class ExecutionHistory:
    """
    执行历史记录
    """
    
    def __init__(
        self,
        record_id: Optional[str] = None,
        task_id: str = "",
        task_name: str = "",
        status: TaskStatus = TaskStatus.PENDING,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        duration_ms: Optional[float] = None,
        logs: Optional[List[str]] = None,
        screenshots: Optional[List[str]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = record_id or str(uuid.uuid4())
        self.task_id = task_id
        self.task_name = task_name
        self.status = status
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.duration_ms = duration_ms
        self.logs = logs or []
        self.screenshots = screenshots or []
        self.error = error
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "logs": self.logs,
            "screenshots": self.screenshots,
            "error": self.error,
            "metadata": self.metadata,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionHistory":
        """从字典反序列化"""
        return cls(
            record_id=data["id"],
            task_id=data["task_id"],
            task_name=data["task_name"],
            status=TaskStatus(data["status"]),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            duration_ms=data.get("duration_ms"),
            logs=data.get("logs", []),
            screenshots=data.get("screenshots", []),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )


class HistoryManager:
    """
    历史管理器 - 管理任务执行历史
    """
    
    def __init__(self):
        self._records: Dict[str, ExecutionHistory] = {}
        
    def create_record(
        self,
        task_id: str,
        task_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionHistory:
        """
        创建执行记录
        
        Args:
            task_id: 任务ID
            task_name: 任务名称
            metadata: 元数据
            
        Returns:
            执行记录
        """
        record = ExecutionHistory(
            task_id=task_id,
            task_name=task_name,
            status=TaskStatus.RUNNING,
            metadata=metadata
        )
        self._records[record.id] = record
        return record
        
    def update_record(
        self,
        record_id: str,
        status: Optional[TaskStatus] = None,
        end_time: Optional[datetime] = None,
        duration_ms: Optional[float] = None,
        logs: Optional[List[str]] = None,
        screenshots: Optional[List[str]] = None,
        error: Optional[str] = None
    ) -> Optional[ExecutionHistory]:
        """
        更新执行记录
        
        Args:
            record_id: 记录ID
            status: 状态
            end_time: 结束时间
            duration_ms: 执行时长
            logs: 日志
            screenshots: 截图
            error: 错误信息
            
        Returns:
            更新后的记录，如果不存在返回None
        """
        record = self._records.get(record_id)
        if not record:
            return None
        
        if status is not None:
            record.status = status
        if end_time is not None:
            record.end_time = end_time
        if duration_ms is not None:
            record.duration_ms = duration_ms
        if logs is not None:
            record.logs.extend(logs)
        if screenshots is not None:
            record.screenshots.extend(screenshots)
        if error is not None:
            record.error = error
        
        return record
        
    def get_record(self, record_id: str) -> Optional[ExecutionHistory]:
        """
        获取执行记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            执行记录，如果不存在返回None
        """
        return self._records.get(record_id)
        
    def list_records(
        self,
        task_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExecutionHistory]:
        """
        列出执行记录（支持分页和过滤）
        
        Args:
            task_id: 任务ID过滤
            status: 状态过滤
            start_date: 开始日期过滤
            end_date: 结束日期过滤
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            执行记录列表
        """
        records = list(self._records.values())
        
        # 过滤
        if task_id:
            records = [r for r in records if r.task_id == task_id]
        if status:
            records = [r for r in records if r.status == status]
        if start_date:
            records = [r for r in records if r.start_time >= start_date]
        if end_date:
            records = [r for r in records if r.start_time <= end_date]
        
        # 排序（按开始时间倒序）
        records.sort(key=lambda r: r.start_time, reverse=True)
        
        # 分页
        return records[offset:offset + limit]
        
    def filter_by_task(self, task_id: str) -> List[ExecutionHistory]:
        """按任务过滤"""
        return self.list_records(task_id=task_id)
        
    def filter_by_status(self, status: TaskStatus) -> List[ExecutionHistory]:
        """按状态过滤"""
        return self.list_records(status=status)
        
    def filter_by_date(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[ExecutionHistory]:
        """按日期范围过滤"""
        return self.list_records(start_date=start_date, end_date=end_date)
        
    def rerun_task(
        self,
        record_id: str,
        modified_params: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        重新执行任务
        
        Args:
            record_id: 原记录ID
            modified_params: 修改的参数
            
        Returns:
            新记录ID，如果原记录不存在返回None
        """
        original_record = self._records.get(record_id)
        if not original_record:
            return None
        
        # 创建新记录
        metadata = original_record.metadata.copy()
        if modified_params:
            metadata.update(modified_params)
        metadata["rerun_from"] = record_id
        
        new_record = self.create_record(
            task_id=original_record.task_id,
            task_name=original_record.task_name,
            metadata=metadata
        )
        
        return new_record.id
        
    def export_records(
        self,
        record_ids: List[str],
        file_path: Path,
        format: str = "json"
    ) -> None:
        """
        导出执行记录
        
        Args:
            record_ids: 记录ID列表
            file_path: 导出文件路径
            format: 导出格式（json或csv）
        """
        records = [self._records[rid] for rid in record_ids if rid in self._records]
        
        if format == "json":
            data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "records": [r.to_dict() for r in records]
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        elif format == "csv":
            import csv
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow([
                    "ID", "Task ID", "Task Name", "Status",
                    "Start Time", "End Time", "Duration (ms)", "Error"
                ])
                # 写入数据
                for record in records:
                    writer.writerow([
                        record.id,
                        record.task_id,
                        record.task_name,
                        record.status.value,
                        record.start_time.isoformat(),
                        record.end_time.isoformat() if record.end_time else "",
                        record.duration_ms or "",
                        record.error or ""
                    ])
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def get_statistics(
        self,
        task_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            task_id: 任务ID（可选）
            days: 统计天数
            
        Returns:
            统计信息
        """
        # 获取指定时间范围内的记录
        start_date = datetime.now() - timedelta(days=days)
        records = self.list_records(
            task_id=task_id,
            start_date=start_date,
            limit=10000
        )
        
        if not records:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
            }
        
        total = len(records)
        success = len([r for r in records if r.status == TaskStatus.COMPLETED])
        failed = len([r for r in records if r.status == TaskStatus.FAILED])
        
        # 计算平均执行时间
        durations = [r.duration_ms for r in records if r.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": success / total if total > 0 else 0.0,
            "avg_duration_ms": avg_duration,
        }
        
    def get_trends(
        self,
        task_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取趋势分析
        
        Args:
            task_id: 任务ID（可选）
            days: 分析天数
            
        Returns:
            趋势数据
        """
        start_date = datetime.now() - timedelta(days=days)
        records = self.list_records(
            task_id=task_id,
            start_date=start_date,
            limit=10000
        )
        
        # 按日期分组统计
        daily_stats = {}
        for record in records:
            date_key = record.start_time.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                }
            
            daily_stats[date_key]["total"] += 1
            if record.status == TaskStatus.COMPLETED:
                daily_stats[date_key]["success"] += 1
            elif record.status == TaskStatus.FAILED:
                daily_stats[date_key]["failed"] += 1
        
        return {
            "daily_stats": daily_stats,
            "period_days": days,
        }
        
    def get_error_analysis(
        self,
        task_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取错误分析
        
        Args:
            task_id: 任务ID（可选）
            days: 分析天数
            
        Returns:
            错误分析数据
        """
        start_date = datetime.now() - timedelta(days=days)
        records = self.list_records(
            task_id=task_id,
            status=TaskStatus.FAILED,
            start_date=start_date,
            limit=10000
        )
        
        # 统计错误类型
        error_counts = {}
        for record in records:
            if record.error:
                error_type = record.error.split(":")[0] if ":" in record.error else record.error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # 排序
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_errors": len(records),
            "error_types": dict(sorted_errors),
            "top_errors": sorted_errors[:10],
        }


# 全局历史管理器实例
_global_history_manager: Optional[HistoryManager] = None


def get_global_history_manager() -> HistoryManager:
    """获取全局历史管理器"""
    global _global_history_manager
    if _global_history_manager is None:
        _global_history_manager = HistoryManager()
    return _global_history_manager
