"""
插件安全机制
"""
from enum import Enum
from typing import Set, Optional, Dict, Any
import logging
from pathlib import Path

from .base import Plugin

logger = logging.getLogger(__name__)


class PermissionType(Enum):
    """权限类型"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    NETWORK_ACCESS = "network_access"
    SYSTEM_COMMAND = "system_command"
    DATABASE_ACCESS = "database_access"


class PluginPermission:
    """
    插件权限管理
    """
    
    def __init__(self):
        self.permissions: Dict[str, Set[PermissionType]] = {}
    
    def grant_permission(
        self,
        plugin_name: str,
        permission: PermissionType
    ) -> None:
        """
        授予权限
        
        Args:
            plugin_name: 插件名称
            permission: 权限类型
        """
        if plugin_name not in self.permissions:
            self.permissions[plugin_name] = set()
        
        self.permissions[plugin_name].add(permission)
        logger.info(f"Granted {permission.value} to plugin {plugin_name}")
    
    def revoke_permission(
        self,
        plugin_name: str,
        permission: PermissionType
    ) -> None:
        """
        撤销权限
        
        Args:
            plugin_name: 插件名称
            permission: 权限类型
        """
        if plugin_name in self.permissions:
            self.permissions[plugin_name].discard(permission)
            logger.info(f"Revoked {permission.value} from plugin {plugin_name}")
    
    def check_permission(
        self,
        plugin_name: str,
        permission: PermissionType
    ) -> bool:
        """
        检查权限
        
        Args:
            plugin_name: 插件名称
            permission: 权限类型
            
        Returns:
            是否有权限
        """
        if plugin_name not in self.permissions:
            return False
        
        return permission in self.permissions[plugin_name]
    
    def get_permissions(self, plugin_name: str) -> Set[PermissionType]:
        """
        获取插件的所有权限
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            权限集合
        """
        return self.permissions.get(plugin_name, set())


class PluginSandbox:
    """
    插件沙箱 - 限制插件的访问范围
    """
    
    def __init__(
        self,
        plugin: Plugin,
        permission_manager: PluginPermission,
        allowed_paths: Optional[Set[Path]] = None
    ):
        self.plugin = plugin
        self.permission_manager = permission_manager
        self.allowed_paths = allowed_paths or set()
    
    def check_file_access(self, path: Path, operation: str) -> bool:
        """
        检查文件访问权限
        
        Args:
            path: 文件路径
            operation: 操作类型 (read/write/delete)
            
        Returns:
            是否允许访问
        """
        # 检查路径是否在允许列表中
        if self.allowed_paths:
            path = Path(path).resolve()
            allowed = any(
                path.is_relative_to(allowed_path)
                for allowed_path in self.allowed_paths
            )
            if not allowed:
                logger.warning(
                    f"Plugin {self.plugin.name} attempted to access "
                    f"restricted path: {path}"
                )
                return False
        
        # 检查操作权限
        permission_map = {
            "read": PermissionType.FILE_READ,
            "write": PermissionType.FILE_WRITE,
            "delete": PermissionType.FILE_DELETE
        }
        
        permission = permission_map.get(operation)
        if not permission:
            return False
        
        has_permission = self.permission_manager.check_permission(
            self.plugin.name,
            permission
        )
        
        if not has_permission:
            logger.warning(
                f"Plugin {self.plugin.name} lacks {operation} permission"
            )
        
        return has_permission
    
    def check_network_access(self, url: str) -> bool:
        """
        检查网络访问权限
        
        Args:
            url: URL地址
            
        Returns:
            是否允许访问
        """
        has_permission = self.permission_manager.check_permission(
            self.plugin.name,
            PermissionType.NETWORK_ACCESS
        )
        
        if not has_permission:
            logger.warning(
                f"Plugin {self.plugin.name} lacks network access permission"
            )
        
        return has_permission
    
    def check_system_command(self, command: str) -> bool:
        """
        检查系统命令执行权限
        
        Args:
            command: 命令
            
        Returns:
            是否允许执行
        """
        has_permission = self.permission_manager.check_permission(
            self.plugin.name,
            PermissionType.SYSTEM_COMMAND
        )
        
        if not has_permission:
            logger.warning(
                f"Plugin {self.plugin.name} lacks system command permission"
            )
        
        return has_permission
    
    async def execute_safe(
        self,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        在沙箱中安全执行插件
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果，如果出错返回None
        """
        try:
            # 执行插件
            result = await self.plugin.on_execute(context)
            return result
        except Exception as e:
            # 捕获插件异常，防止影响主程序
            logger.error(
                f"Plugin {self.plugin.name} execution failed: {e}",
                exc_info=True
            )
            return None


def create_sandbox(
    plugin: Plugin,
    permission_manager: PluginPermission,
    allowed_paths: Optional[Set[Path]] = None
) -> PluginSandbox:
    """
    创建插件沙箱
    
    Args:
        plugin: 插件实例
        permission_manager: 权限管理器
        allowed_paths: 允许访问的路径集合
        
    Returns:
        沙箱实例
    """
    return PluginSandbox(plugin, permission_manager, allowed_paths)
