"""
会话管理API路由
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.session import SessionManager, get_global_session_manager
from ...core.types import SessionState, DriverType
from ..dependencies import get_db

router = APIRouter()


class SessionCreate(BaseModel):
    """会话创建模型"""
    driver_type: str = "browser"
    metadata: Optional[dict] = None


@router.post("", response_model=dict)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建会话"""
    try:
        driver_type = DriverType(session_data.driver_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid driver_type: {session_data.driver_type}")
    
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.create_session(
        driver_type=driver_type,
        metadata=session_data.metadata,
        db_session=db
    )
    return session.to_dict()


@router.get("", response_model=List[dict])
async def list_sessions(
    state: Optional[str] = Query(None, description="会话状态过滤"),
    driver_type: Optional[str] = Query(None, description="驱动类型过滤"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """列出会话"""
    session_manager = get_global_session_manager(db_session=db)
    
    # 转换状态和驱动类型字符串为枚举
    state_enum = None
    if state:
        try:
            state_enum = SessionState(state)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid state: {state}")
    
    driver_type_enum = None
    if driver_type:
        try:
            driver_type_enum = DriverType(driver_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid driver_type: {driver_type}")
    
    sessions = await session_manager.list_sessions(
        state=state_enum,
        driver_type=driver_type_enum,
        limit=limit,
        offset=offset,
        db_session=db
    )
    return [s.to_dict() for s in sessions]


@router.get("/{session_id}", response_model=dict)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话详情"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除会话"""
    session_manager = get_global_session_manager(db_session=db)
    success = await session_manager.delete_session(session_id, db_session=db)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


@router.post("/{session_id}/start")
async def start_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """启动会话"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session.start()
        await session_manager.update_session_state(
            session_id,
            session.state,
            db_session=db
        )
        return {"message": "Session started", "session_id": session_id, "state": session.state.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """暂停会话"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session.pause()
        await session_manager.update_session_state(
            session_id,
            session.state,
            db_session=db
        )
        return {"message": "Session paused", "session_id": session_id, "state": session.state.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/resume")
async def resume_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """恢复会话"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session.resume()
        await session_manager.update_session_state(
            session_id,
            session.state,
            db_session=db
        )
        return {"message": "Session resumed", "session_id": session_id, "state": session.state.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/stop")
async def stop_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """停止会话"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session.stop()
        await session_manager.update_session_state(
            session_id,
            session.state,
            db_session=db
        )
        return {"message": "Session stopped", "session_id": session_id, "state": session.state.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/restore")
async def restore_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """恢复会话（从检查点）"""
    session_manager = get_global_session_manager(db_session=db)
    session = await session_manager.get_session(session_id, db_session=db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # TODO: 实现从检查点恢复的逻辑
    return {"message": "Session restored", "session_id": session_id}


@router.get("/monitor/stats", response_model=dict)
async def monitor_sessions(
    db: AsyncSession = Depends(get_db)
):
    """获取会话监控统计"""
    session_manager = get_global_session_manager(db_session=db)
    stats = await session_manager.monitor_sessions(db_session=db)
    return stats
