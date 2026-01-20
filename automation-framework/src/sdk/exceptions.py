"""
SDK异常类
"""
from typing import Optional, Dict, Any


class SDKError(Exception):
    """SDK基础异常"""
    pass


class APIError(SDKError):
    """API错误"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(SDKError):
    """认证错误"""
    pass


class ValidationError(SDKError):
    """验证错误"""
    pass


class ResourceNotFoundError(SDKError):
    """资源未找到错误"""
    pass


class TimeoutError(SDKError):
    """超时错误"""
    pass
