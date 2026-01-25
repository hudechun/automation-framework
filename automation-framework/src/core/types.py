"""
核心数据类型和枚举定义
"""
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime


class ActionType(str, Enum):
    """操作类型枚举"""
    NAVIGATION = "navigation"
    INTERACTION = "interaction"
    INPUT = "input"
    QUERY = "query"
    WAIT = "wait"
    CONTROL_FLOW = "control_flow"  # 控制流（循环、条件分支）


class DriverType(str, Enum):
    """驱动类型枚举"""
    BROWSER = "browser"
    DESKTOP = "desktop"


class SessionState(str, Enum):
    """会话状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorType(str, Enum):
    """错误类型枚举"""
    RECOVERABLE = "recoverable"
    UNRECOVERABLE = "unrecoverable"
    SYSTEM = "system"
    NETWORK = "network"
    ELEMENT_NOT_FOUND = "element_not_found"


class BrowserType(str, Enum):
    """浏览器类型枚举"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class Platform(str, Enum):
    """操作系统平台枚举"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class TaskType(str, Enum):
    """任务类型枚举（用于并发策略）"""
    BROWSER = "browser"
    DESKTOP = "desktop"
    HYBRID = "hybrid"


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """通知类型枚举"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DINGTALK = "dingtalk"
    WECHAT_WORK = "wechat_work"


class PermissionType(str, Enum):
    """权限类型枚举"""
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    SYSTEM_ACCESS = "system_access"
    DATABASE_ACCESS = "database_access"
