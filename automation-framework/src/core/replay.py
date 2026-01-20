"""
会话回放模块 - 实现操作历史记录和回放功能
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .interfaces import Action, Driver
from .session import Session


class ActionRecord:
    """
    操作记录 - 记录单个操作的执行信息
    """
    
    def __init__(
        self,
        action: Action,
        timestamp: datetime,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        self.action = action
        self.timestamp = timestamp
        self.result = result
        self.error = error
        self.duration_ms = duration_ms
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "action": self.action.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionRecord":
        """从字典反序列化"""
        # Note: action需要从registry重建
        return cls(
            action=None,  # 需要外部重建
            timestamp=datetime.fromisoformat(data["timestamp"]),
            result=data.get("result"),
            error=data.get("error"),
            duration_ms=data.get("duration_ms"),
        )


class SessionRecorder:
    """
    会话记录器 - 记录会话中的所有操作
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.records: List[ActionRecord] = []
        
    def record_action(
        self,
        action: Action,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """
        记录操作
        
        Args:
            action: 执行的操作
            result: 操作结果
            error: 错误信息（如果有）
            duration_ms: 执行时长（毫秒）
        """
        record = ActionRecord(
            action=action,
            timestamp=datetime.now(),
            result=result,
            error=error,
            duration_ms=duration_ms
        )
        self.records.append(record)
        
    def get_action_history(
        self,
        start_index: int = 0,
        end_index: Optional[int] = None
    ) -> List[ActionRecord]:
        """
        获取操作历史
        
        Args:
            start_index: 起始索引
            end_index: 结束索引（不包含）
            
        Returns:
            操作记录列表
        """
        if end_index is None:
            return self.records[start_index:]
        return self.records[start_index:end_index]
        
    def get_failed_actions(self) -> List[ActionRecord]:
        """获取失败的操作"""
        return [r for r in self.records if r.error is not None]
        
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.records)
        failed = len(self.get_failed_actions())
        
        if total == 0:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
            }
        
        durations = [r.duration_ms for r in self.records if r.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return {
            "total": total,
            "success": total - failed,
            "failed": failed,
            "success_rate": (total - failed) / total,
            "avg_duration_ms": avg_duration,
        }


class SessionReplayer:
    """
    会话回放器 - 回放会话中的操作
    """
    
    def __init__(self, driver: Driver):
        self.driver = driver
        
    async def replay_session(
        self,
        records: List[ActionRecord],
        start_index: int = 0,
        speed: float = 1.0,
        stop_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        回放会话
        
        Args:
            records: 操作记录列表
            start_index: 从哪个步骤开始回放
            speed: 回放速度（1.0为正常速度，2.0为2倍速）
            stop_on_error: 遇到错误是否停止
            
        Returns:
            回放结果统计
        """
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": [],
        }
        
        for i, record in enumerate(records[start_index:], start=start_index):
            results["total"] += 1
            
            try:
                # 执行操作
                await self.driver.execute_action(record.action)
                results["success"] += 1
                
                # 控制回放速度
                if record.duration_ms and speed > 0:
                    import asyncio
                    await asyncio.sleep(record.duration_ms / 1000 / speed)
                    
            except Exception as e:
                results["failed"] += 1
                error_info = {
                    "index": i,
                    "action": record.action.to_dict(),
                    "error": str(e),
                }
                results["errors"].append(error_info)
                
                if stop_on_error:
                    break
        
        return results
        
    async def replay_from_checkpoint(
        self,
        records: List[ActionRecord],
        checkpoint_index: int,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        从检查点开始回放
        
        Args:
            records: 操作记录列表
            checkpoint_index: 检查点索引
            speed: 回放速度
            
        Returns:
            回放结果统计
        """
        return await self.replay_session(
            records=records,
            start_index=checkpoint_index,
            speed=speed,
            stop_on_error=False
        )
        
    async def replay_failed_actions(
        self,
        records: List[ActionRecord],
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        仅回放失败的操作
        
        Args:
            records: 操作记录列表
            speed: 回放速度
            
        Returns:
            回放结果统计
        """
        failed_records = [r for r in records if r.error is not None]
        return await self.replay_session(
            records=failed_records,
            start_index=0,
            speed=speed,
            stop_on_error=False
        )
