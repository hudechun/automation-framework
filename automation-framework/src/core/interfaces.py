"""
核心接口定义
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime

from .types import ActionType, DriverType, SessionState


class Action(ABC):
    """操作抽象基类"""
    
    def __init__(self, action_type: ActionType, **kwargs: Any):
        """
        初始化操作
        
        Args:
            action_type: 操作类型
            **kwargs: 操作参数
        """
        self.action_type = action_type
        self.params = kwargs
        self.timestamp = datetime.now()
    
    @abstractmethod
    async def execute(self, driver: 'Driver') -> Any:
        """
        执行操作
        
        Args:
            driver: 驱动实例
            
        Returns:
            操作结果
        """
        pass
    
    def validate(self) -> bool:
        """
        验证操作参数
        
        Returns:
            验证是否通过
        """
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典
        
        Returns:
            字典表示
        """
        return {
            "action_type": self.action_type.value,
            "params": self.params,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """
        从字典反序列化
        
        Args:
            data: 字典数据
            
        Returns:
            操作实例
        """
        action_type = ActionType(data["action_type"])
        return cls(action_type, **data.get("params", {}))


class Driver(ABC):
    """驱动抽象基类"""
    
    def __init__(self, driver_type: DriverType):
        """
        初始化驱动
        
        Args:
            driver_type: 驱动类型
        """
        self.driver_type = driver_type
        self.is_running = False
    
    @abstractmethod
    async def start(self, **kwargs: Any) -> None:
        """
        启动驱动
        
        Args:
            **kwargs: 启动参数
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """停止驱动"""
        pass
    
    @abstractmethod
    async def execute_action(self, action: Action) -> Any:
        """
        执行操作
        
        Args:
            action: 操作实例
            
        Returns:
            操作结果
        """
        pass


class Session(ABC):
    """会话接口"""
    
    def __init__(self, session_id: str):
        """
        初始化会话
        
        Args:
            session_id: 会话ID
        """
        self.session_id = session_id
        self.state = SessionState.CREATED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @abstractmethod
    async def start(self) -> None:
        """启动会话"""
        pass
    
    @abstractmethod
    async def pause(self) -> None:
        """暂停会话"""
        pass
    
    @abstractmethod
    async def resume(self) -> None:
        """恢复会话"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """停止会话"""
        pass
    
    @abstractmethod
    async def terminate(self) -> None:
        """终止会话"""
        pass
    
    def get_state(self) -> SessionState:
        """
        获取会话状态
        
        Returns:
            会话状态
        """
        return self.state
    
    def set_state(self, state: SessionState) -> None:
        """
        设置会话状态
        
        Args:
            state: 新状态
        """
        self.state = state
        self.updated_at = datetime.now()


class Plugin(ABC):
    """插件接口"""
    
    def __init__(self, name: str, version: str, description: str = ""):
        """
        初始化插件
        
        Args:
            name: 插件名称
            version: 插件版本
            description: 插件描述
        """
        self.name = name
        self.version = version
        self.description = description
        self.enabled = False
    
    @abstractmethod
    async def on_init(self) -> None:
        """插件初始化钩子"""
        pass
    
    @abstractmethod
    async def on_register(self) -> None:
        """插件注册钩子"""
        pass
    
    @abstractmethod
    async def on_execute(self, context: Dict[str, Any]) -> None:
        """
        插件执行钩子
        
        Args:
            context: 执行上下文
        """
        pass
    
    @abstractmethod
    async def on_cleanup(self) -> None:
        """插件清理钩子"""
        pass
    
    def get_manifest(self) -> Dict[str, Any]:
        """
        获取插件清单
        
        Returns:
            插件清单信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled
        }
