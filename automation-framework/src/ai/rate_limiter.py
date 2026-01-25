"""
LLM API限流器 - 处理请求频率限制
"""
import asyncio
import time
from typing import Optional, Dict, Any
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RateLimitConfig:
    """限流配置"""
    max_requests: int = 60  # 每分钟最大请求数
    window_seconds: int = 60  # 时间窗口（秒）
    retry_after_header: Optional[str] = None  # 从响应头获取重试时间


class RateLimiter:
    """
    请求限流器 - 控制API调用频率
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        初始化限流器
        
        Args:
            config: 限流配置
        """
        self.config = config or RateLimitConfig()
        self._request_times: Dict[str, list] = defaultdict(list)  # 每个API的请求时间记录
        self._lock = asyncio.Lock()
    
    async def acquire(self, api_key: str = "default") -> None:
        """
        获取请求许可（如果超过限制则等待）
        
        Args:
            api_key: API标识（用于区分不同的API）
        """
        async with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds
            
            # 清理过期的请求记录
            request_times = self._request_times[api_key]
            request_times[:] = [t for t in request_times if t > window_start]
            
            # 检查是否超过限制
            if len(request_times) >= self.config.max_requests:
                # 计算需要等待的时间
                oldest_request = min(request_times)
                wait_time = (oldest_request + self.config.window_seconds) - now
                
                if wait_time > 0:
                    print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                    # 重新清理
                    now = time.time()
                    window_start = now - self.config.window_seconds
                    request_times[:] = [t for t in request_times if t > window_start]
            
            # 记录本次请求
            request_times.append(now)
    
    def reset(self, api_key: str = "default") -> None:
        """重置指定API的请求记录"""
        self._request_times.pop(api_key, None)
    
    def reset_all(self) -> None:
        """重置所有请求记录"""
        self._request_times.clear()
    
    def get_remaining_requests(self, api_key: str = "default") -> int:
        """
        获取剩余请求数
        
        Args:
            api_key: API标识
            
        Returns:
            剩余请求数
        """
        now = time.time()
        window_start = now - self.config.window_seconds
        
        request_times = self._request_times[api_key]
        request_times[:] = [t for t in request_times if t > window_start]
        
        return max(0, self.config.max_requests - len(request_times))


# 全局限流器实例
_global_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """
    获取全局限流器实例
    
    Args:
        config: 限流配置（仅在首次调用时生效）
        
    Returns:
        限流器实例
    """
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(config)
    return _global_rate_limiter


def set_rate_limiter(limiter: RateLimiter) -> None:
    """设置全局限流器"""
    global _global_rate_limiter
    _global_rate_limiter = limiter
