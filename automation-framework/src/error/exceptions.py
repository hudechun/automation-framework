"""
异常类定义 - 定义错误层次结构
"""
from typing import Optional, Dict, Any


class AutomationError(Exception):
    """自动化框架基础异常"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class RecoverableError(AutomationError):
    """可恢复错误 - 可以通过重试或其他策略恢复"""
    pass


class UnrecoverableError(AutomationError):
    """不可恢复错误 - 需要人工干预"""
    pass


class SystemError(AutomationError):
    """系统错误 - 系统级别的错误"""
    pass


class NetworkError(RecoverableError):
    """网络错误 - 网络连接相关的错误"""
    pass


class ElementNotFoundError(RecoverableError):
    """元素未找到错误 - UI元素定位失败"""
    
    def __init__(
        self,
        message: str,
        selector: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.selector = selector


class TimeoutError(RecoverableError):
    """超时错误 - 操作超时"""
    
    def __init__(
        self,
        message: str,
        timeout: Optional[float] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.timeout = timeout


class ValidationError(UnrecoverableError):
    """验证错误 - 数据验证失败"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.field = field
        self.value = value


class DriverError(SystemError):
    """驱动错误 - 浏览器或桌面驱动相关错误"""
    pass


class DatabaseError(SystemError):
    """数据库错误 - 数据库操作相关错误"""
    pass


class ConfigurationError(UnrecoverableError):
    """配置错误 - 配置相关错误"""
    pass


class PermissionError(UnrecoverableError):
    """权限错误 - 权限不足"""
    pass


class ResourceError(RecoverableError):
    """资源错误 - 资源不足或不可用"""
    pass
