"""
主客户端类
"""
from typing import Optional
import httpx
from .task_api import TaskAPI
from .session_api import SessionAPI
from .history_api import HistoryAPI
from .config_api import ConfigAPI
from .exceptions import APIError, AuthenticationError


class AutomationClient:
    """
    自动化框架客户端
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            timeout: 请求超时时间
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        
        # 创建HTTP客户端
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        self.http_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout
        )
        
        # 初始化API模块
        self.tasks = TaskAPI(self)
        self.sessions = SessionAPI(self)
        self.history = HistoryAPI(self)
        self.config = ConfigAPI(self)
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def close(self) -> None:
        """关闭客户端"""
        await self.http_client.aclose()
    
    async def request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            path: 请求路径
            **kwargs: 其他参数
            
        Returns:
            响应数据
            
        Raises:
            APIError: API错误
            AuthenticationError: 认证错误
        """
        try:
            response = await self.http_client.request(
                method,
                path,
                **kwargs
            )
            
            # 检查响应状态
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise APIError(
                    f"API error: {response.status_code}",
                    status_code=response.status_code,
                    details=error_data
                )
            
            return response.json() if response.content else {}
            
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {str(e)}")
