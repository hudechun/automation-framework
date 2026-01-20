"""
插件类型实现
"""
from abc import abstractmethod
from typing import Dict, Any, Type

from .base import Plugin, PluginManifest
from ..core.interfaces import Action, Driver


class ActionPlugin(Plugin):
    """
    操作插件 - 扩展自定义操作类型
    """
    
    @abstractmethod
    def get_action_class(self) -> Type[Action]:
        """
        获取操作类
        
        Returns:
            操作类
        """
        pass
    
    async def on_register(self) -> None:
        """注册操作到系统"""
        from ..core.registry import ActionRegistry
        
        action_class = self.get_action_class()
        registry = ActionRegistry()
        registry.register_action(action_class)


class DriverPlugin(Plugin):
    """
    驱动插件 - 扩展自定义驱动
    """
    
    @abstractmethod
    def get_driver_class(self) -> Type[Driver]:
        """
        获取驱动类
        
        Returns:
            驱动类
        """
        pass
    
    async def on_register(self) -> None:
        """注册驱动到系统"""
        # TODO: 实现驱动注册逻辑
        pass


class AgentPlugin(Plugin):
    """
    Agent插件 - 扩展自定义AI Agent
    """
    
    @abstractmethod
    def get_agent_class(self) -> Type:
        """
        获取Agent类
        
        Returns:
            Agent类
        """
        pass
    
    async def on_register(self) -> None:
        """注册Agent到系统"""
        # TODO: 实现Agent注册逻辑
        pass


class IntegrationPlugin(Plugin):
    """
    集成插件 - 集成第三方服务
    """
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        连接到第三方服务
        
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    async def send_data(self, data: Dict[str, Any]) -> bool:
        """
        发送数据到第三方服务
        
        Args:
            data: 数据
            
        Returns:
            是否成功
        """
        pass
    
    async def on_register(self) -> None:
        """注册集成到系统"""
        await self.connect()
    
    async def on_cleanup(self) -> None:
        """清理集成"""
        await self.disconnect()
