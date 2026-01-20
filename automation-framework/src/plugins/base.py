"""
插件基础架构
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class PluginType(Enum):
    """插件类型"""
    ACTION = "action"
    DRIVER = "driver"
    AGENT = "agent"
    INTEGRATION = "integration"


@dataclass
class PluginManifest:
    """插件清单"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str]
    permissions: List[str]
    entry_point: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """从字典创建"""
        return cls(
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data["description"],
            plugin_type=PluginType(data["plugin_type"]),
            dependencies=data.get("dependencies", []),
            permissions=data.get("permissions", []),
            entry_point=data["entry_point"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "plugin_type": self.plugin_type.value,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "entry_point": self.entry_point
        }
    
    def validate(self) -> bool:
        """验证清单"""
        if not self.name or not self.version:
            return False
        if not self.entry_point:
            return False
        return True


class Plugin(ABC):
    """
    插件抽象基类
    """
    
    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.enabled = False
        self.config: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """插件名称"""
        return self.manifest.name
    
    @property
    def version(self) -> str:
        """插件版本"""
        return self.manifest.version
    
    @abstractmethod
    async def on_init(self) -> None:
        """
        初始化钩子
        在插件加载时调用
        """
        pass
    
    @abstractmethod
    async def on_register(self) -> None:
        """
        注册钩子
        在插件注册到系统时调用
        """
        pass
    
    @abstractmethod
    async def on_execute(self, context: Dict[str, Any]) -> Any:
        """
        执行钩子
        在插件被调用时执行
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    async def on_cleanup(self) -> None:
        """
        清理钩子
        在插件卸载时调用
        """
        pass
    
    def get_manifest(self) -> PluginManifest:
        """获取插件清单"""
        return self.manifest
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """设置插件配置"""
        self.config = config
    
    def get_config(self) -> Dict[str, Any]:
        """获取插件配置"""
        return self.config
    
    def enable(self) -> None:
        """启用插件"""
        self.enabled = True
    
    def disable(self) -> None:
        """禁用插件"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        return self.enabled
