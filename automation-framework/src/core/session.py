"""
会话管理模块 - 实现会话状态管理和持久化
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json
import pickle
from pathlib import Path

from .types import SessionState, DriverType
from .interfaces import Driver, Action


class Session:
    """
    会话类 - 管理单个自动化会话的状态和生命周期
    """
    
    def __init__(
        self,
        session_id: str,
        driver_type: DriverType,
        driver: Optional[Driver] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = session_id
        self.driver_type = driver_type
        self.driver = driver
        self.state = SessionState.CREATED
        self.actions: List[Action] = []
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.error: Optional[str] = None
        
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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error": self.error,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], driver: Optional[Driver] = None) -> "Session":
        """从字典反序列化"""
        session = cls(
            session_id=data["id"],
            driver_type=DriverType(data["driver_type"]),
            driver=driver,
            metadata=data.get("metadata", {})
        )
        session.state = SessionState(data["state"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.updated_at = datetime.fromisoformat(data["updated_at"])
        session.error = data.get("error")
        # Note: actions需要从registry重建
        return session


class SessionManager:
    """
    会话管理器 - 管理所有会话的生命周期
    """
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._active_sessions: Dict[str, Session] = {}
        
    def create_session(
        self,
        session_id: str,
        driver_type: DriverType,
        driver: Optional[Driver] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """创建新会话"""
        if session_id in self._sessions:
            raise ValueError(f"Session {session_id} already exists")
        
        session = Session(session_id, driver_type, driver, metadata)
        self._sessions[session_id] = session
        return session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self._sessions.get(session_id)
        
    def list_sessions(
        self,
        state: Optional[SessionState] = None,
        driver_type: Optional[DriverType] = None
    ) -> List[Session]:
        """列出会话（支持过滤）"""
        sessions = list(self._sessions.values())
        
        if state:
            sessions = [s for s in sessions if s.state == state]
        if driver_type:
            sessions = [s for s in sessions if s.driver_type == driver_type]
            
        return sessions
        
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            # 确保会话已停止
            if session.state == SessionState.RUNNING:
                session.stop()
            del self._sessions[session_id]
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
            return True
        return False
        
    def monitor_sessions(self) -> Dict[str, Any]:
        """监控会话状态"""
        return {
            "total": len(self._sessions),
            "running": len([s for s in self._sessions.values() if s.state == SessionState.RUNNING]),
            "paused": len([s for s in self._sessions.values() if s.state == SessionState.PAUSED]),
            "stopped": len([s for s in self._sessions.values() if s.state == SessionState.STOPPED]),
            "failed": len([s for s in self._sessions.values() if s.state == SessionState.FAILED]),
        }


# 全局会话管理器实例
_global_session_manager: Optional[SessionManager] = None


def get_global_session_manager() -> SessionManager:
    """获取全局会话管理器"""
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = SessionManager()
    return _global_session_manager
