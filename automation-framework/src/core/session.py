"""
会话管理模块 - 实现会话状态管理和持久化（数据库持久化版本）
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from .types import SessionState, DriverType
from .interfaces import Driver, Action
from ..models.sqlalchemy_models import Session as SessionModel

logger = logging.getLogger(__name__)


class Session:
    """
    会话类 - 管理单个自动化会话的状态和生命周期
    """
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        driver_type: DriverType = DriverType.BROWSER,
        driver: Optional[Driver] = None,
        metadata: Optional[Dict[str, Any]] = None,
        state: SessionState = SessionState.CREATED,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        error: Optional[str] = None
    ):
        self.id = session_id or str(uuid.uuid4())
        self.driver_type = driver_type
        self.driver = driver  # 注意：driver不持久化到数据库
        self.state = state
        self.actions: List[Action] = []  # 注意：actions不直接存储在Session表中，通过checkpoints管理
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.error = error
        
    def start(self) -> None:
        """启动会话"""
        if self.state != SessionState.CREATED:
            raise ValueError(f"Cannot start session in state {self.state}")
        
        self.state = SessionState.RUNNING
        self.updated_at = datetime.now()
        
    def pause(self) -> None:
        """暂停会话"""
        if self.state != SessionState.RUNNING:
            raise ValueError(f"Cannot pause session in state {self.state}")
        
        self.state = SessionState.PAUSED
        self.updated_at = datetime.now()
        
    def resume(self) -> None:
        """恢复会话"""
        if self.state != SessionState.PAUSED:
            raise ValueError(f"Cannot resume session in state {self.state}")
        
        self.state = SessionState.RUNNING
        self.updated_at = datetime.now()
        
    def stop(self) -> None:
        """停止会话"""
        if self.state in [SessionState.STOPPED, SessionState.FAILED]:
            raise ValueError(f"Session already in terminal state {self.state}")
        
        self.state = SessionState.STOPPED
        self.updated_at = datetime.now()
        
    def terminate(self, error: Optional[str] = None) -> None:
        """终止会话（失败）"""
        self.state = SessionState.FAILED
        self.error = error
        self.updated_at = datetime.now()
        
    def add_action(self, action: Action) -> None:
        """添加操作到会话历史"""
        self.actions.append(action)
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "driver_type": self.driver_type.value,
            "state": self.state.value,
            "actions": [action.to_dict() for action in self.actions],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "error": self.error,
        }
    
    @classmethod
    def from_db_model(cls, db_session: SessionModel, driver: Optional[Driver] = None) -> "Session":
        """
        从数据库模型创建Session对象
        
        Args:
            db_session: 数据库会话模型
            driver: 驱动实例（可选，不持久化）
            
        Returns:
            Session对象
        """
        session = cls(
            session_id=db_session.session_id,
            driver_type=DriverType(db_session.driver_type),
            driver=driver,
            metadata=getattr(db_session, 'session_metadata', None) or getattr(db_session, 'metadata', None) or {},  # 兼容两种字段名
            state=SessionState(db_session.state),
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
            error=None  # 错误信息可以存储在metadata中
        )
        return session
    
    def to_db_model(self) -> Dict[str, Any]:
        """
        转换为数据库模型字典（用于创建/更新）
        
        Returns:
            字典，包含数据库字段
        """
        return {
            "session_id": self.id,
            "driver_type": self.driver_type.value,
            "state": self.state.value,
            "session_metadata": self.metadata,  # 使用 session_metadata 匹配数据库字段
            "updated_at": datetime.now(),
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], driver: Optional[Driver] = None) -> "Session":
        """从字典反序列化"""
        session = cls(
            session_id=data.get("id"),
            driver_type=DriverType(data["driver_type"]),
            driver=driver,
            metadata=data.get("metadata", {})
        )
        if "state" in data:
            session.state = SessionState(data["state"])
        if "created_at" in data and data["created_at"]:
            session.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and data["updated_at"]:
            session.updated_at = datetime.fromisoformat(data["updated_at"])
        session.error = data.get("error")
        # Note: actions需要从registry重建
        return session


class SessionManager:
    """
    会话管理器 - 管理所有会话的生命周期（数据库持久化版本）
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        初始化会话管理器
        
        Args:
            db_session: 数据库会话（如果为None，需要在每个方法中传入）
        """
        self._db_session = db_session
        # 内存中保存活跃会话的driver引用（不持久化）
        self._active_drivers: Dict[str, Driver] = {}
        
    async def create_session(
        self,
        session_id: Optional[str] = None,
        driver_type: DriverType = DriverType.BROWSER,
        driver: Optional[Driver] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Session:
        """
        创建新会话并保存到数据库
        
        Args:
            session_id: 会话ID（如果为None，自动生成）
            driver_type: 驱动类型
            driver: 驱动实例（不持久化，仅保存在内存中）
            metadata: 元数据
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            创建的会话
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 创建会话对象
        session = Session(
            session_id=session_id,
            driver_type=driver_type,
            driver=driver,
            metadata=metadata or {}
        )
        
        # 保存driver到内存（如果提供）
        if driver:
            self._active_drivers[session.id] = driver
        
        # 创建数据库模型
        db_session_model = SessionModel(**session.to_db_model())
        db.add(db_session_model)
        await db.commit()
        await db.refresh(db_session_model)
        
        # 更新会话的创建时间
        session.created_at = db_session_model.created_at
        session.updated_at = db_session_model.updated_at
        
        logger.info(f"Created session: {session.id} - {session.driver_type.value}")
        return session
        
    async def get_session(
        self,
        session_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[Session]:
        """
        从数据库获取会话
        
        Args:
            session_id: 会话ID
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            会话对象，如果不存在返回None
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        result = await db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )
        db_session_model = result.scalar_one_or_none()
        
        if not db_session_model:
            return None
        
        # 尝试从内存中获取driver
        driver = self._active_drivers.get(session_id)
        
        return Session.from_db_model(db_session_model, driver=driver)
        
    async def list_sessions(
        self,
        state: Optional[SessionState] = None,
        driver_type: Optional[DriverType] = None,
        limit: int = 100,
        offset: int = 0,
        db_session: Optional[AsyncSession] = None
    ) -> List[Session]:
        """
        从数据库列出会话（支持分页和过滤）
        
        Args:
            state: 状态过滤
            driver_type: 驱动类型过滤
            limit: 每页数量
            offset: 偏移量
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            会话列表
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 构建查询
        query = select(SessionModel)
        
        # 添加过滤条件
        if state:
            query = query.where(SessionModel.state == state.value)
        if driver_type:
            query = query.where(SessionModel.driver_type == driver_type.value)
        
        # 排序和分页
        query = query.order_by(SessionModel.created_at.desc()).limit(limit).offset(offset)
        
        # 执行查询
        result = await db.execute(query)
        db_sessions = result.scalars().all()
        
        # 转换为Session对象
        sessions = []
        for db_sess in db_sessions:
            driver = self._active_drivers.get(db_sess.session_id)
            sessions.append(Session.from_db_model(db_sess, driver=driver))
        
        return sessions
        
    async def update_session_state(
        self,
        session_id: str,
        state: SessionState,
        error: Optional[str] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Optional[Session]:
        """
        更新会话状态
        
        Args:
            session_id: 会话ID
            state: 新状态
            error: 错误信息（如果有）
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            更新后的会话，如果不存在返回None
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 更新状态
        update_data = {
            "state": state.value,
            "updated_at": datetime.now()
        }
        
        # 如果有错误信息，存储到metadata中
        if error:
            session = await self.get_session(session_id, db_session=db)
            if session:
                session.metadata = session.metadata or {}
                session.metadata["error"] = error
                update_data["metadata"] = session.metadata
        
        await db.execute(
            update(SessionModel)
            .where(SessionModel.session_id == session_id)
            .values(**update_data)
        )
        await db.commit()
        
        # 返回更新后的会话
        return await self.get_session(session_id, db_session=db)
        
    async def delete_session(
        self,
        session_id: str,
        db_session: Optional[AsyncSession] = None
    ) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            是否删除成功
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 先获取会话，确保已停止
        session = await self.get_session(session_id, db_session=db)
        if session and session.state == SessionState.RUNNING:
            await self.update_session_state(session_id, SessionState.STOPPED, db_session=db)
        
        # 删除数据库记录
        result = await db.execute(
            delete(SessionModel).where(SessionModel.session_id == session_id)
        )
        await db.commit()
        
        # 从内存中移除driver引用
        if session_id in self._active_drivers:
            del self._active_drivers[session_id]
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted session: {session_id}")
        return deleted
        
    async def monitor_sessions(
        self,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        监控会话状态
        
        Args:
            db_session: 数据库会话（如果为None，使用初始化时的会话）
            
        Returns:
            统计信息
        """
        db = db_session or self._db_session
        if not db:
            raise ValueError("Database session is required")
        
        # 总数
        total_result = await db.execute(select(func.count(SessionModel.id)))
        total = total_result.scalar() or 0
        
        # 按状态统计
        status_counts = {}
        for state in SessionState:
            count_result = await db.execute(
                select(func.count(SessionModel.id)).where(SessionModel.state == state.value)
            )
            status_counts[state.value] = count_result.scalar() or 0
        
        return {
            "total": total,
            "by_state": status_counts,
        }


# 全局会话管理器实例（注意：需要在使用时传入db_session）
_global_session_manager: Optional[SessionManager] = None


def get_global_session_manager(db_session: Optional[AsyncSession] = None) -> SessionManager:
    """
    获取全局会话管理器
    
    Args:
        db_session: 数据库会话（如果提供，会创建新的管理器实例）
        
    Returns:
        会话管理器实例
    """
    global _global_session_manager
    if _global_session_manager is None or db_session is not None:
        _global_session_manager = SessionManager(db_session=db_session)
    return _global_session_manager
