"""
请求路径去掉 /prod-api 或 /dev-api 前缀，避免代理转发带前缀时 404。
例如：/prod-api/captchaImage -> /captchaImage
"""
from starlette.types import ASGIApp, Receive, Scope, Send

from config.env import AppConfig

# 支持的 API 前缀（任一层级均会去掉）
API_PREFIXES = ("/prod-api", "/dev-api", "/docker-api")


class StripRootPathMiddleware:
    """若请求 path 以 /prod-api、/dev-api 等开头，则去掉该前缀再交给路由匹配"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        # 优先用配置，否则用通用前缀
        cfg = (AppConfig.app_root_path or "").strip().rstrip("/")
        if cfg and cfg.startswith("/"):
            self.prefixes = (cfg,)
        else:
            self.prefixes = API_PREFIXES

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path") or ""
        new_path = path
        for prefix in self.prefixes:
            if path == prefix or path == prefix + "/":
                new_path = "/"
                break
            if path.startswith(prefix + "/"):
                new_path = "/" + path[len(prefix) + 1 :].lstrip("/") or "/"
                break
        if new_path != path:
            scope = dict(scope)
            scope["path"] = new_path
        await self.app(scope, receive, send)
