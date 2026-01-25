"""
核心模块 - 提供核心接口和类型定义
"""
from .interfaces import Action, Driver, Session, Plugin
from .types import (
    ActionType,
    DriverType,
    SessionState,
    TaskStatus,
    BrowserType
)
from .execution_context import ExecutionContext
from .execution_progress import ExecutionProgress
from .retry_strategy import (
    RetryStrategy,
    ErrorClassifier,
    ErrorType,
    execute_with_retry
)

__all__ = [
    # 接口
    "Action",
    "Driver",
    "Session",
    "Plugin",
    # 类型
    "ActionType",
    "DriverType",
    "SessionState",
    "TaskStatus",
    "BrowserType",
    # 执行上下文和进度
    "ExecutionContext",
    "ExecutionProgress",
    # 重试策略
    "RetryStrategy",
    "ErrorClassifier",
    "ErrorType",
    "execute_with_retry",
]
