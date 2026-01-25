"""
重试策略 - 实现操作失败后的重试机制
"""
import asyncio
import logging
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """错误类型"""
    RECOVERABLE = "recoverable"  # 可恢复错误
    UNRECOVERABLE = "unrecoverable"  # 不可恢复错误
    UNKNOWN = "unknown"  # 未知错误


class RetryStrategy:
    """
    重试策略 - 定义重试行为
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0
    ):
        """
        初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            backoff_factor: 退避因子（指数退避）
            max_delay: 最大延迟（秒）
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """
        计算重试延迟（指数退避）
        
        Args:
            attempt: 重试次数（从0开始）
            
        Returns:
            延迟时间（秒）
        """
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            attempt: 当前重试次数
            error: 错误对象
            
        Returns:
            是否应该重试
        """
        if attempt >= self.max_retries:
            return False
        
        # 检查错误类型
        error_type = ErrorClassifier.classify(error)
        return error_type == ErrorType.RECOVERABLE


class ErrorClassifier:
    """
    错误分类器 - 将错误分类为可恢复或不可恢复
    """
    
    # 可恢复错误类型
    RECOVERABLE_ERRORS = [
        "TimeoutError",
        "ElementNotFoundError",
        "ElementNotVisibleError",
        "NetworkError",
        "ConnectionError",
        "TemporaryError",
        "RetryableError"
    ]
    
    # 不可恢复错误类型
    UNRECOVERABLE_ERRORS = [
        "InvalidTaskError",
        "PermissionError",
        "ConfigurationError",
        "ValidationError",
        "SyntaxError"
    ]
    
    @classmethod
    def classify(cls, error: Exception) -> ErrorType:
        """
        分类错误
        
        Args:
            error: 错误对象
            
        Returns:
            错误类型
        """
        error_type_name = type(error).__name__
        
        if error_type_name in cls.RECOVERABLE_ERRORS:
            return ErrorType.RECOVERABLE
        elif error_type_name in cls.UNRECOVERABLE_ERRORS:
            return ErrorType.UNRECOVERABLE
        else:
            # 检查错误消息中是否包含可恢复的关键词
            error_message = str(error).lower()
            recoverable_keywords = [
                "timeout", "not found", "not visible", "network",
                "connection", "temporary", "retry"
            ]
            if any(keyword in error_message for keyword in recoverable_keywords):
                return ErrorType.RECOVERABLE
            
            return ErrorType.UNKNOWN
    
    @classmethod
    def is_recoverable(cls, error: Exception) -> bool:
        """
        判断错误是否可恢复
        
        Args:
            error: 错误对象
            
        Returns:
            是否可恢复
        """
        return cls.classify(error) == ErrorType.RECOVERABLE


async def execute_with_retry(
    func,
    retry_strategy: RetryStrategy,
    *args,
    **kwargs
) -> tuple[bool, any, Optional[Exception]]:
    """
    带重试的执行函数
    
    Args:
        func: 要执行的函数（异步）
        retry_strategy: 重试策略
        *args: 函数位置参数
        **kwargs: 函数关键字参数
        
    Returns:
        (是否成功, 结果, 错误)
    """
    last_error = None
    
    for attempt in range(retry_strategy.max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            return True, result, None
        except Exception as e:
            last_error = e
            
            # 检查是否应该重试
            if not retry_strategy.should_retry(attempt, e):
                logger.error(
                    f"Operation failed after {attempt + 1} attempts: {e}"
                )
                return False, None, e
            
            # 计算延迟并等待
            delay = retry_strategy.get_delay(attempt)
            logger.warning(
                f"Operation failed (attempt {attempt + 1}/{retry_strategy.max_retries + 1}), "
                f"retrying in {delay}s: {e}"
            )
            await asyncio.sleep(delay)
    
    # 所有重试都失败
    return False, None, last_error
