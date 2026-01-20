"""
数据库配置和连接管理 - 统一使用 SQLAlchemy
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加 RuoYi 后端路径
ruoyi_backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend')
)
if ruoyi_backend_path not in sys.path:
    sys.path.insert(0, ruoyi_backend_path)

try:
    # 使用 RuoYi 的数据库配置（统一连接池）
    from config.database import (
        AsyncSessionLocal,
        Base,
        async_engine,
    )
    from config.get_db import get_db as get_ruoyi_db
    
    # 使用 RuoYi 的数据库连接
    USE_RUOYI_DB = True
except ImportError:
    # 如果无法导入 RuoYi 配置，创建独立的数据库连接（用于独立运行）
    from urllib.parse import quote_plus
    from sqlalchemy.ext.asyncio import (
        AsyncAttrs,
        async_sessionmaker,
        create_async_engine,
        AsyncSession
    )
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(AsyncAttrs, DeclarativeBase):
        pass
    
    # 从环境变量读取配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "automation_framework")
    
    ASYNC_SQLALCHEMY_DATABASE_URL = (
        f'mysql+asyncmy://{DB_USER}:{quote_plus(DB_PASSWORD)}@'
        f'{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    
    async_engine = create_async_engine(
        ASYNC_SQLALCHEMY_DATABASE_URL,
        echo=False,
        max_overflow=10,
        pool_size=5,
        pool_recycle=3600,
        pool_timeout=30,
    )
    
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine
    )
    
    USE_RUOYI_DB = False


async def init_db() -> None:
    """
    初始化数据库连接
    注意：如果已挂载到 RuoYi，数据库连接由 RuoYi 管理，这里不需要额外初始化
    """
    if not USE_RUOYI_DB:
        # 独立运行时，创建表结构
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接
    注意：如果已挂载到 RuoYi，数据库连接由 RuoYi 管理，这里不需要关闭
    """
    if not USE_RUOYI_DB:
        await async_engine.dispose()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化数据库"""
        if not self._initialized:
            await init_db()
            self._initialized = True
    
    async def close(self) -> None:
        """关闭数据库"""
        if self._initialized:
            await close_db()
            self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    获取全局数据库管理器实例
    
    Returns:
        数据库管理器实例
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session():
    """
    获取数据库会话生成器
    如果已挂载到 RuoYi，使用 RuoYi 的 get_db
    否则使用独立的 AsyncSessionLocal
    
    Returns:
        数据库会话生成器函数
    """
    if USE_RUOYI_DB:
        # 使用 RuoYi 的数据库会话
        return get_ruoyi_db()
    else:
        # 使用独立的数据库会话
        from sqlalchemy.ext.asyncio import AsyncSession
        
        async def _get_db():
            async with AsyncSessionLocal() as session:
                yield session
        return _get_db()


# 为了向后兼容，保留 TORTOISE_ORM 变量（但不再使用）
TORTOISE_ORM = None
