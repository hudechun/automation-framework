"""
错误处理器 - 统一的错误处理和日志记录
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import traceback

from .exceptions import (
    AutomationError,
    RecoverableError,
    UnrecoverableError,
)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorContext:
    """错误上下文 - 记录错误发生时的上下文信息"""
    
    def __init__(
        self,
        error: Exception,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        action: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.error = error
        self.task_id = task_id
        self.session_id = session_id
        self.action = action
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        error_dict = {}
        if isinstance(self.error, AutomationError):
            error_dict = self.error.to_dict()
        else:
            error_dict = {
                "type": self.error.__class__.__name__,
                "message": str(self.error),
            }
        
        return {
            "error": error_dict,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "action": self.action,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback,
        }


class ErrorHandler:
    """
    错误处理器 - 统一处理和记录错误
    """
    
    def __init__(self):
        self._handlers: Dict[type, List[Callable]] = {}
        self._error_log: List[ErrorContext] = []
        self._error_stats: Dict[str, int] = {}
        
    def register_handler(
        self,
        error_type: type,
        handler: Callable[[ErrorContext], None]
    ) -> None:
        """
        注册错误处理器
        
        Args:
            error_type: 错误类型
            handler: 处理函数
        """
        if error_type not in self._handlers:
            self._handlers[error_type] = []
        self._handlers[error_type].append(handler)
        
    def unregister_handler(
        self,
        error_type: type,
        handler: Callable[[ErrorContext], None]
    ) -> bool:
        """
        注销错误处理器
        
        Args:
            error_type: 错误类型
            handler: 处理函数
            
        Returns:
            是否成功注销
        """
        if error_type in self._handlers:
            try:
                self._handlers[error_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
        
    def handle_error(
        self,
        error: Exception,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        action: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """
        处理错误
        
        Args:
            error: 异常对象
            task_id: 任务ID
            session_id: 会话ID
            action: 操作名称
            metadata: 元数据
            
        Returns:
            错误上下文
        """
        # 创建错误上下文
        context = ErrorContext(
            error=error,
            task_id=task_id,
            session_id=session_id,
            action=action,
            metadata=metadata
        )
        
        # 记录错误
        self.log_error(context)
        
        # 调用注册的处理器
        error_type = type(error)
        if error_type in self._handlers:
            for handler in self._handlers[error_type]:
                try:
                    handler(context)
                except Exception as e:
                    print(f"Error in error handler: {e}")
        
        # 检查父类处理器
        for registered_type, handlers in self._handlers.items():
            if registered_type != error_type and isinstance(error, registered_type):
                for handler in handlers:
                    try:
                        handler(context)
                    except Exception as e:
                        print(f"Error in error handler: {e}")
        
        return context
        
    def log_error(self, context: ErrorContext) -> None:
        """
        记录错误日志
        
        Args:
            context: 错误上下文
        """
        self._error_log.append(context)
        
        # 更新统计
        error_type = context.error.__class__.__name__
        self._error_stats[error_type] = self._error_stats.get(error_type, 0) + 1
        
    def notify_error(
        self,
        context: ErrorContext,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> None:
        """
        发送错误通知
        
        Args:
            context: 错误上下文
            severity: 严重程度
        """
        # TODO: 实现通知逻辑（邮件、Webhook等）
        print(f"[{severity.value.upper()}] Error notification: {context.error}")
        
    def get_error_log(
        self,
        limit: int = 100,
        error_type: Optional[type] = None
    ) -> List[ErrorContext]:
        """
        获取错误日志
        
        Args:
            limit: 返回数量限制
            error_type: 错误类型过滤
            
        Returns:
            错误上下文列表
        """
        logs = self._error_log
        
        if error_type:
            logs = [ctx for ctx in logs if isinstance(ctx.error, error_type)]
        
        return logs[-limit:]
        
    def collect_error_stats(self) -> Dict[str, int]:
        """
        收集错误统计
        
        Returns:
            错误统计信息
        """
        return self._error_stats.copy()
        
    def get_error_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        生成错误报告
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            错误报告
        """
        logs = self._error_log
        
        # 时间过滤
        if start_time:
            logs = [ctx for ctx in logs if ctx.timestamp >= start_time]
        if end_time:
            logs = [ctx for ctx in logs if ctx.timestamp <= end_time]
        
        # 统计
        total = len(logs)
        by_type = {}
        by_severity = {
            "recoverable": 0,
            "unrecoverable": 0,
            "other": 0,
        }
        
        for ctx in logs:
            error_type = ctx.error.__class__.__name__
            by_type[error_type] = by_type.get(error_type, 0) + 1
            
            if isinstance(ctx.error, RecoverableError):
                by_severity["recoverable"] += 1
            elif isinstance(ctx.error, UnrecoverableError):
                by_severity["unrecoverable"] += 1
            else:
                by_severity["other"] += 1
        
        return {
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "period": {
                "start": start_time.isoformat() if start_time else None,
                "end": end_time.isoformat() if end_time else None,
            }
        }
        
    def clear_error_log(self) -> None:
        """清空错误日志"""
        self._error_log.clear()
        
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._error_stats.clear()


# 全局错误处理器实例
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler
