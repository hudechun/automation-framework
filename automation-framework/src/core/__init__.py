"""
核心模块 - 提供核心抽象层的类型和接口
"""
from .types import (
    ActionType,
    DriverType,
    SessionState,
    TaskStatus,
    ErrorType,
    BrowserType,
    Platform,
    TaskType,
    LogLevel,
    NotificationType,
    PermissionType,
)

from .interfaces import (
    Action,
    Driver,
    Session,
    Plugin,
)

from .actions import (
    # 导航操作
    GoToURL,
    GoBack,
    GoForward,
    Refresh,
    WaitForLoad,
    # 交互操作
    Click,
    DoubleClick,
    RightClick,
    Hover,
    Drag,
    # 输入操作
    Type,
    Press,
    PressCombo,
    Upload,
    Clear,
    # 查询操作
    GetText,
    GetAttribute,
    Screenshot,
    GetUITree,
    IsVisible,
    # 等待操作
    WaitForElement,
    WaitForText,
    WaitForCondition,
    Sleep,
)

from .registry import (
    ActionRegistry,
    get_global_registry,
    register_action,
    get_action,
)

from .session import (
    Session,
    SessionManager,
    get_global_session_manager,
)

from .checkpoint import (
    CheckpointManager,
    SessionExporter,
    get_global_checkpoint_manager,
)

from .replay import (
    ActionRecord,
    SessionRecorder,
    SessionReplayer,
)

__all__ = [
    # 枚举类型
    "ActionType",
    "DriverType",
    "SessionState",
    "TaskStatus",
    "ErrorType",
    "BrowserType",
    "Platform",
    "TaskType",
    "LogLevel",
    "NotificationType",
    "PermissionType",
    # 接口
    "Action",
    "Driver",
    "Session",
    "Plugin",
    # 导航操作
    "GoToURL",
    "GoBack",
    "GoForward",
    "Refresh",
    "WaitForLoad",
    # 交互操作
    "Click",
    "DoubleClick",
    "RightClick",
    "Hover",
    "Drag",
    # 输入操作
    "Type",
    "Press",
    "PressCombo",
    "Upload",
    "Clear",
    # 查询操作
    "GetText",
    "GetAttribute",
    "Screenshot",
    "GetUITree",
    "IsVisible",
    # 等待操作
    "WaitForElement",
    "WaitForText",
    "WaitForCondition",
    "Sleep",
    # 注册表
    "ActionRegistry",
    "get_global_registry",
    "register_action",
    "get_action",
    # 会话管理
    "Session",
    "SessionManager",
    "get_global_session_manager",
    # 检查点和持久化
    "CheckpointManager",
    "SessionExporter",
    "get_global_checkpoint_manager",
    # 回放
    "ActionRecord",
    "SessionRecorder",
    "SessionReplayer",
]
