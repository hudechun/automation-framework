"""
速率限制中间件
使用 Redis 实现简单的速率限制
"""
from datetime import timedelta
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from utils.log_util import logger
from utils.response_util import ResponseUtil


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件
    """

    def __init__(
        self,
        app: FastAPI,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ) -> None:
        """
        初始化速率限制中间件

        :param app: FastAPI 应用
        :param requests_per_minute: 每分钟最大请求数
        :param requests_per_hour: 每小时最大请求数
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求

        :param request: 请求对象
        :param call_next: 下一个中间件
        :return: 响应对象
        """
        # 排除静态资源和文档
        if request.url.path.startswith(('/static', '/docs', '/redoc', '/openapi.json')):
            return await call_next(request)

        # 排除登录和登出接口（这些接口需要允许重试，且有其他安全机制）
        if request.url.path in ('/login', '/logout'):
            return await call_next(request)

        # 排除验证码接口（登录时需要频繁获取）
        if request.url.path.startswith('/captchaImage'):
            return await call_next(request)

        # 获取客户端 IP
        client_ip = self._get_client_ip(request)

        # 检查速率限制
        is_allowed, message = await self._check_rate_limit(request, client_ip)

        if not is_allowed:
            logger.warning(f'速率限制: {client_ip} - {message}')
            return ResponseUtil.failure(msg=message, dict_content={'code': 429})

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实 IP

        :param request: 请求对象
        :return: 客户端 IP
        """
        # 优先从 X-Real-IP 获取
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        # 其次从 X-Forwarded-For 获取第一个 IP
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # X-Forwarded-For 可能包含多个 IP，取第一个
            return forwarded_for.split(',')[0].strip()

        # 最后使用客户端地址
        return request.client.host if request.client else 'unknown'

    async def _check_rate_limit(self, request: Request, client_ip: str) -> tuple[bool, str]:
        """
        检查速率限制

        :param request: 请求对象
        :param client_ip: 客户端 IP
        :return: (是否允许, 错误消息)
        """
        try:
            redis = request.app.state.redis

            # 每分钟限制
            minute_key = f'rate_limit:minute:{client_ip}'
            minute_count = await redis.incr(minute_key)
            if minute_count == 1:
                await redis.expire(minute_key, timedelta(minutes=1))

            if minute_count > self.requests_per_minute:
                return False, f'请求过于频繁，每分钟最多 {self.requests_per_minute} 次请求'

            # 每小时限制
            hour_key = f'rate_limit:hour:{client_ip}'
            hour_count = await redis.incr(hour_key)
            if hour_count == 1:
                await redis.expire(hour_key, timedelta(hours=1))

            if hour_count > self.requests_per_hour:
                return False, f'请求过于频繁，每小时最多 {self.requests_per_hour} 次请求'

            return True, ''

        except Exception as e:
            # Redis 异常时不阻止请求
            logger.error(f'速率限制检查失败: {e}')
            return True, ''


def add_rate_limit_middleware(app: FastAPI) -> None:
    """
    添加速率限制中间件

    :param app: FastAPI 对象
    :return:
    """
    # 登录接口更严格的限制
    # 其他接口的通用限制
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60,  # 每分钟 60 次
        requests_per_hour=1000,  # 每小时 1000 次
    )
