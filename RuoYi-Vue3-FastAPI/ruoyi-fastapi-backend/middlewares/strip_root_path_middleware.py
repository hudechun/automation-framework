"""
请求路径去掉 APP_ROOT_PATH 前缀，避免代理转发带 /dev-api 时 404。
例如：/dev-api/student/verification/list -> /student/verification/list
"""
from starlette.types import ASGIApp, Receive, Scope, Send

from config.env import AppConfig


class StripRootPathMiddleware:
    """若请求 path 以 app_root_path 开头，则去掉该前缀再交给路由匹配"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.prefix = (AppConfig.app_root_path or "").rstrip("/")
        if self.prefix and not self.prefix.startswith("/"):
            self.prefix = "/" + self.prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.prefix:
            await self.app(scope, receive, send)
            return
        path = scope.get("path") or ""
        if path.startswith(self.prefix):
            # 去掉前缀，保证路由能匹配
            new_path = path[len(self.prefix) :] or "/"
            scope = dict(scope)
            scope["path"] = new_path
            # 便于下游知道原始根路径
            scope["root_path"] = (scope.get("root_path") or "") + self.prefix.rstrip("/")
        await self.app(scope, receive, send)
