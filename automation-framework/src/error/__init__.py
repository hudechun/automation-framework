"""
错误处理模块
"""
from .exceptions import (
    AutomationError,
    RecoverableError,
    UnrecoverableError,
    SystemError,
    NetworkError,
    ElementNotFoundError,
    TimeoutError,
    ValidationError,
)

from .handler import (
    ErrorHandler,
    ErrorContext,
    get_global_error_handler,
)

from .retry import (
    retry_with_backoff,
    RetryConfig,
)

from .recovery import (
    RecoveryStrategy,
    CheckpointRecovery,
    FallbackRecovery,
)

__all__ = [
    # 异常类
    "AutomationError",
    "RecoverableError",
    "UnrecoverableError",
    "SystemError",
    "NetworkError",
    "ElementNotFoundError",
    "TimeoutError",
    "ValidationError",
    # 错误处理
    "ErrorHandler",
    "ErrorContext",
    "get_global_error_handler",
    # 重试
    "retry_with_backoff",
    "RetryConfig",
    # 恢复策略
    "RecoveryStrategy",
    "CheckpointRecovery",
    "FallbackRecovery",
]
