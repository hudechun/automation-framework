"""
通知基础架构
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import asyncio


class Notifier(ABC):
    """通知器抽象基类"""
    
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    async def send(self, message: str, **kwargs) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置"""
        pass


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.notifiers: Dict[str, Notifier] = {}
    
    def register_notifier(self, name: str, notifier: Notifier):
        """注册通知器"""
        self.notifiers[name] = notifier
    
    async def send_notification(self, channel: str, message: str, **kwargs) -> bool:
        """发送通知"""
        if channel not in self.notifiers:
            raise ValueError(f"Notifier '{channel}' not registered")
        
        notifier = self.notifiers[channel]
        try:
            return await notifier.send(message, **kwargs)
        except Exception as e:
            print(f"Failed to send notification via {channel}: {e}")
            return False
    
    async def broadcast(self, message: str, channels: Optional[List[str]] = None, **kwargs):
        """广播通知到多个渠道"""
        target_channels = channels or list(self.notifiers.keys())
        tasks = [
            self.send_notification(channel, message, **kwargs)
            for channel in target_channels
            if channel in self.notifiers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


# 全局通知管理器
notification_manager = NotificationManager()
