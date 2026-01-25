"""
会话工具函数 - 用于从metadata中提取user_id和task_id
"""
from typing import Optional, Dict, Any


def get_user_id_from_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[int]:
    """
    从session metadata中提取user_id
    
    Args:
        metadata: 会话元数据
        
    Returns:
        用户ID，如果不存在返回None
    """
    if not metadata:
        return None
    return metadata.get("user_id")


def get_task_id_from_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[int]:
    """
    从session metadata中提取task_id
    
    Args:
        metadata: 会话元数据
        
    Returns:
        任务ID，如果不存在返回None
    """
    if not metadata:
        return None
    return metadata.get("task_id")


def set_user_id_in_metadata(metadata: Optional[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
    """
    在metadata中设置user_id
    
    Args:
        metadata: 现有元数据
        user_id: 用户ID
        
    Returns:
        更新后的元数据
    """
    if metadata is None:
        metadata = {}
    metadata = metadata.copy()
    metadata["user_id"] = user_id
    return metadata


def set_task_id_in_metadata(metadata: Optional[Dict[str, Any]], task_id: int) -> Dict[str, Any]:
    """
    在metadata中设置task_id
    
    Args:
        metadata: 现有元数据
        task_id: 任务ID
        
    Returns:
        更新后的元数据
    """
    if metadata is None:
        metadata = {}
    metadata = metadata.copy()
    metadata["task_id"] = task_id
    return metadata
