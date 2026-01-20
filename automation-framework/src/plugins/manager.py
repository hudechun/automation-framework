"""
插件管理器
"""
import importlib.util
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
import zipfile
import logging

from .base import Plugin, PluginManifest, PluginType

logger = logging.getLogger(__name__)


class PluginManager:
    """
    插件管理器 - 管理插件的加载、卸载和生命周期
    """
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Plugin] = {}
        self.manifests: Dict[str, PluginManifest] = {}
        
    async def discover_plugins(self) -> List[PluginManifest]:
        """
        发现插件
        扫描插件目录，查找所有插件
        
        Returns:
            插件清单列表
        """
        manifests = []
        
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return manifests
        
        # 扫描目录中的插件
        for item in self.plugin_dir.iterdir():
            if item.is_dir():
                # 从目录加载
                manifest_path = item / "plugin.yaml"
                if manifest_path.exists():
                    manifest = self._load_manifest(manifest_path)
                    if manifest:
                        manifests.append(manifest)
            elif item.suffix == ".zip":
                # 从ZIP包加载
                manifest = self._load_manifest_from_zip(item)
                if manifest:
                    manifests.append(manifest)
        
        return manifests
    
    def _load_manifest(self, manifest_path: Path) -> Optional[PluginManifest]:
        """
        从文件加载插件清单
        
        Args:
            manifest_path: 清单文件路径
            
        Returns:
            插件清单
        """
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            manifest = PluginManifest.from_dict(data)
            
            if not manifest.validate():
                logger.error(f"Invalid manifest: {manifest_path}")
                return None
            
            return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_path}: {e}")
            return None
    
    def _load_manifest_from_zip(self, zip_path: Path) -> Optional[PluginManifest]:
        """
        从ZIP包加载插件清单
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            插件清单
        """
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                if "plugin.yaml" in zf.namelist():
                    with zf.open("plugin.yaml") as f:
                        data = yaml.safe_load(f)
                    
                    manifest = PluginManifest.from_dict(data)
                    
                    if not manifest.validate():
                        logger.error(f"Invalid manifest in ZIP: {zip_path}")
                        return None
                    
                    return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest from ZIP {zip_path}: {e}")
            return None
    
    async def load_plugin(self, manifest: PluginManifest) -> Optional[Plugin]:
        """
        加载插件
        
        Args:
            manifest: 插件清单
            
        Returns:
            插件实例
        """
        try:
            # 构建插件路径
            plugin_path = self.plugin_dir / manifest.name / manifest.entry_point
            
            if not plugin_path.exists():
                logger.error(f"Plugin entry point not found: {plugin_path}")
                return None
            
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                manifest.name,
                plugin_path
            )
            if not spec or not spec.loader:
                logger.error(f"Failed to load plugin spec: {manifest.name}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取插件类
            plugin_class = getattr(module, "PluginClass", None)
            if not plugin_class:
                logger.error(f"Plugin class not found in {manifest.name}")
                return None
            
            # 创建插件实例
            plugin = plugin_class(manifest)
            
            # 调用初始化钩子
            await plugin.on_init()
            
            # 存储插件
            self.plugins[manifest.name] = plugin
            self.manifests[manifest.name] = manifest
            
            logger.info(f"Loaded plugin: {manifest.name} v{manifest.version}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {manifest.name}: {e}")
            return None
    
    async def unload_plugin(self, name: str) -> bool:
        """
        卸载插件
        
        Args:
            name: 插件名称
            
        Returns:
            是否成功
        """
        if name not in self.plugins:
            logger.warning(f"Plugin not found: {name}")
            return False
        
        try:
            plugin = self.plugins[name]
            
            # 调用清理钩子
            await plugin.on_cleanup()
            
            # 移除插件
            del self.plugins[name]
            del self.manifests[name]
            
            logger.info(f"Unloaded plugin: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {name}: {e}")
            return False
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        获取插件
        
        Args:
            name: 插件名称
            
        Returns:
            插件实例
        """
        return self.plugins.get(name)
    
    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        enabled_only: bool = False
    ) -> List[Plugin]:
        """
        列出插件
        
        Args:
            plugin_type: 插件类型过滤
            enabled_only: 仅列出启用的插件
            
        Returns:
            插件列表
        """
        plugins = list(self.plugins.values())
        
        if plugin_type:
            plugins = [
                p for p in plugins
                if p.manifest.plugin_type == plugin_type
            ]
        
        if enabled_only:
            plugins = [p for p in plugins if p.is_enabled()]
        
        return plugins
    
    async def enable_plugin(self, name: str) -> bool:
        """
        启用插件
        
        Args:
            name: 插件名称
            
        Returns:
            是否成功
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return False
        
        try:
            # 调用注册钩子
            await plugin.on_register()
            plugin.enable()
            logger.info(f"Enabled plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable plugin {name}: {e}")
            return False
    
    async def disable_plugin(self, name: str) -> bool:
        """
        禁用插件
        
        Args:
            name: 插件名称
            
        Returns:
            是否成功
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return False
        
        plugin.disable()
        logger.info(f"Disabled plugin: {name}")
        return True
    
    def set_plugin_config(
        self,
        name: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        设置插件配置
        
        Args:
            name: 插件名称
            config: 配置字典
            
        Returns:
            是否成功
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return False
        
        plugin.set_config(config)
        return True
    
    def get_plugin_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取插件配置
        
        Args:
            name: 插件名称
            
        Returns:
            配置字典
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return None
        
        return plugin.get_config()
