"""
FastAPI依赖注入
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import AsyncSessionLocal, USE_RUOYI_DB


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    
    Yields:
        AsyncSession: 数据库会话
    """
    if USE_RUOYI_DB:
        # 使用RuoYi的get_db
        try:
            from config.get_db import get_db as get_ruoyi_db
            async for session in get_ruoyi_db():
                yield session
        except ImportError:
            # 如果无法导入RuoYi的get_db，使用独立会话
            async with AsyncSessionLocal() as session:
                yield session
    else:
        # 使用独立的数据库会话
        async with AsyncSessionLocal() as session:
            yield session
