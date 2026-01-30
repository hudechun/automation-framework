from fastapi import FastAPI

from middlewares.context_middleware import add_context_cleanup_middleware
from middlewares.cors_middleware import add_cors_middleware
from middlewares.gzip_middleware import add_gzip_middleware
from middlewares.rate_limit_middleware import add_rate_limit_middleware
from middlewares.strip_root_path_middleware import StripRootPathMiddleware
from middlewares.trace_middleware import add_trace_middleware


def handle_middleware(app: FastAPI) -> None:
    """
    全局中间件处理
    """
    # 最先执行：去掉 /dev-api 前缀，避免带前缀请求 404
    app.add_middleware(StripRootPathMiddleware)
    # 加载上下文清理中间件
    add_context_cleanup_middleware(app)
    # 加载跨域中间件
    add_cors_middleware(app)
    # 加载速率限制中间件
    add_rate_limit_middleware(app)
    # 加载gzip压缩中间件
    add_gzip_middleware(app)
    # 加载trace中间件
    add_trace_middleware(app)
