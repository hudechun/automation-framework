"""
数据模型模块 - 统一使用 SQLAlchemy
"""
from .database import (
    init_db,
    close_db,
    DatabaseManager,
    get_db_manager,
    get_db_session,
    Base,
    AsyncSessionLocal,
    async_engine,
    USE_RUOYI_DB,
)

# 导入 SQLAlchemy 模型
from .sqlalchemy_models import (
    Task,
    Schedule,
    ExecutionRecord,
    Session,
    SessionCheckpoint,
    ModelConfig,
    ModelMetrics,
    SystemLog,
    NotificationConfig,
    FileStorage,
    Plugin,
    PerformanceMetrics,
)

__all__ = [
    # 数据库
    "init_db",
    "close_db",
    "DatabaseManager",
    "get_db_manager",
    "get_db_session",
    "Base",
    "AsyncSessionLocal",
    "async_engine",
    "USE_RUOYI_DB",
    # 任务
    "Task",
    "Schedule",
    "ExecutionRecord",
    # 会话
    "Session",
    "SessionCheckpoint",
    # 配置
    "ModelConfig",
    "ModelMetrics",
    "SystemLog",
    "NotificationConfig",
    # 文件
    "FileStorage",
    "Plugin",
    "PerformanceMetrics",
]

# 向后兼容：保留旧的 Tortoise 模型导入路径（但实际使用 SQLAlchemy）
# 这些导入会失败，但可以提示用户迁移
try:
    from .task import Task as TortoiseTask
    from .session import Session as TortoiseSession
    from .config import ModelConfig as TortoiseModelConfig
    from .file import FileStorage as TortoiseFileStorage
except ImportError:
    # Tortoise 模型已移除，使用 SQLAlchemy 模型
    pass
