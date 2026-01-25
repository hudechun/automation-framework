"""
用户认证依赖 - 集成RuoYi用户认证系统
"""
from typing import Optional
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 尝试导入RuoYi的用户认证模块
try:
    from RuoYi_Vue3_FastAPI.ruoyi_fastapi_backend.common.context import RequestContext
    from RuoYi_Vue3_FastAPI.ruoyi_fastapi_backend.module_admin.entity.vo.user_vo import CurrentUserModel
    RUOYI_AVAILABLE = True
except ImportError:
    # 如果RuoYi不可用，使用简单的用户模型
    RUOYI_AVAILABLE = False
    from pydantic import BaseModel
    
    class CurrentUserModel(BaseModel):
        """简单的用户模型（当RuoYi不可用时使用）"""
        user_id: int
        user_name: str
        dept_id: Optional[int] = None


def get_current_user() -> CurrentUserModel:
    """
    获取当前登录用户
    
    Returns:
        CurrentUserModel: 当前用户信息
        
    Raises:
        HTTPException: 如果用户未登录
    """
    if RUOYI_AVAILABLE:
        try:
            # 使用RuoYi的上下文获取当前用户
            return RequestContext.get_current_user()
        except Exception as e:
            # 如果获取失败，抛出401错误
            raise HTTPException(
                status_code=401,
                detail=f"用户未登录或认证失败: {str(e)}"
            )
    else:
        # 如果RuoYi不可用，返回默认用户（开发环境）
        return CurrentUserModel(
            user_id=1,
            user_name="admin"
        )


def get_current_user_id() -> int:
    """
    获取当前用户ID（便捷函数）
    
    Returns:
        int: 当前用户ID
    """
    user = get_current_user()
    return user.user_id


def get_current_user_name() -> str:
    """
    获取当前用户名（便捷函数）
    
    Returns:
        str: 当前用户名
    """
    user = get_current_user()
    return user.user_name
