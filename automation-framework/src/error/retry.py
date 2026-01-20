"""
重试机制 - 实现指数退避重试
"""
from typing import Optional, Callable, Any, Type, Tuple
from functools import wraps
import asyncio
import time
from dataclasses import dataclass

from .exceptions import RecoverableError


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0  # 基础延迟（秒）
    max_delay: float = 60.0  # 最大延迟（秒）
    exponential_base: float = 2.0  # 指数基数
    jitter: bool = True  # 是否添加抖动
    retry_on: Tuple[Type[Exception], ...] = (RecoverableError,)


def calculate_delay(
    attempt: int,
    config: RetryConfig
) -> float:
    """
    计算延迟时间
    
    Args:
        attempt: 尝试次数（从0开始）
        config: 重试配置
        
    Returns:
        延迟时间（秒）
    """
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    
    # 添加抖动
    if config.jitter:
        import random
        delay = delay * (0.5 + random.random())
    
    return delay


def retry_with_backoff(
    config: Optional[RetryConfig] = None
):
    """
    指数退避重试装饰器
    
    Args:
        config: 重试配置
        
    Example:
        @retry_with_backoff(RetryConfig(max_retries=5))
        def my_function():
            # 可能失败的操作
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = calculate_delay(attempt, config)
                        print(f"Retry attempt {attempt + 1}/{config.max_retries} after {delay:.2f}s: {e}")
                        time.sleep(delay)
                    else:
                        print(f"Max retries ({config.max_retries}) exceeded")
                        raise
            
            # 不应该到达这里
            if last_exception:
                raise last_exception
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = calculate_delay(attempt, config)
                        print(f"Retry attempt {attempt + 1}/{config.max_retries} after {delay:.2f}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        print(f"Max retries ({config.max_retries}) exceeded")
                        raise
            
            # 不应该到达这里
            if last_exception:
                raise last_exception
        
        # 判断是否为异步函数
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RetryManager:
    """
    重试管理器 - 管理重试策略和统计
    """
    
    def __init__(self):
        self._retry_stats: dict[str, dict[str, Any]] = {}
        
    async def retry_async(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        operation_name: Optional[str] = None
    ) -> Any:
        """
        异步重试执行
        
        Args:
            func: 要执行的函数
            config: 重试配置
            operation_name: 操作名称（用于统计）
            
        Returns:
            函数执行结果
        """
        if config is None:
            config = RetryConfig()
        
        operation_name = operation_name or func.__name__
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                result = await func()
                
                # 记录成功
                self._record_success(operation_name, attempt)
                
                return result
                
            except config.retry_on as e:
                last_exception = e
                
                # 记录失败
                self._record_failure(operation_name, attempt, e)
                
                if attempt < config.max_retries:
                    delay = calculate_delay(attempt, config)
                    await asyncio.sleep(delay)
                else:
                    raise
        
        if last_exception:
            raise last_exception
    
    def retry_sync(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        operation_name: Optional[str] = None
    ) -> Any:
        """
        同步重试执行
        
        Args:
            func: 要执行的函数
            config: 重试配置
            operation_name: 操作名称（用于统计）
            
        Returns:
            函数执行结果
        """
        if config is None:
            config = RetryConfig()
        
        operation_name = operation_name or func.__name__
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                result = func()
                
                # 记录成功
                self._record_success(operation_name, attempt)
                
                return result
                
            except config.retry_on as e:
                last_exception = e
                
                # 记录失败
                self._record_failure(operation_name, attempt, e)
                
                if attempt < config.max_retries:
                    delay = calculate_delay(attempt, config)
                    time.sleep(delay)
                else:
                    raise
        
        if last_exception:
            raise last_exception
    
    def _record_success(self, operation_name: str, attempt: int) -> None:
        """记录成功"""
        if operation_name not in self._retry_stats:
            self._retry_stats[operation_name] = {
                "total_attempts": 0,
                "successes": 0,
                "failures": 0,
                "retry_counts": {},
            }
        
        stats = self._retry_stats[operation_name]
        stats["total_attempts"] += attempt + 1
        stats["successes"] += 1
        stats["retry_counts"][attempt] = stats["retry_counts"].get(attempt, 0) + 1
    
    def _record_failure(
        self,
        operation_name: str,
        attempt: int,
        error: Exception
    ) -> None:
        """记录失败"""
        if operation_name not in self._retry_stats:
            self._retry_stats[operation_name] = {
                "total_attempts": 0,
                "successes": 0,
                "failures": 0,
                "retry_counts": {},
            }
        
        stats = self._retry_stats[operation_name]
        stats["total_attempts"] += 1
    
    def get_stats(self, operation_name: Optional[str] = None) -> dict[str, Any]:
        """
        获取统计信息
        
        Args:
            operation_name: 操作名称，如果为None则返回所有统计
            
        Returns:
            统计信息
        """
        if operation_name:
            return self._retry_stats.get(operation_name, {})
        return self._retry_stats.copy()
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._retry_stats.clear()


# 全局重试管理器实例
_global_retry_manager: Optional[RetryManager] = None


def get_global_retry_manager() -> RetryManager:
    """获取全局重试管理器"""
    global _global_retry_manager
    if _global_retry_manager is None:
        _global_retry_manager = RetryManager()
    return _global_retry_manager
