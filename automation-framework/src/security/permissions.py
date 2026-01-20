"""
权限管理和审计
"""
from enum import Enum
from typing import Set, Dict, Any, Callable, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class Permission(Enum):
    """权限类型"""
    # 文件操作
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    FILE_EXECUTE = "file_execute"
    
    # 网络操作
    NETWORK_ACCESS = "network_access"
    NETWORK_EXTERNAL = "network_external"
    
    # 系统操作
    SYSTEM_COMMAND = "system_command"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_REGISTRY = "system_registry"
    
    # 数据库操作
    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"
    DATABASE_DELETE = "database_delete"
    
    # 任务操作
    TASK_CREATE = "task_create"
    TASK_EXECUTE = "task_execute"
    TASK_DELETE = "task_delete"
    
    # 配置操作
    CONFIG_READ = "config_read"
    CONFIG_WRITE = "config_write"
    
    # 管理操作
    ADMIN_ACCESS = "admin_access"
    USER_MANAGE = "user_manage"


class PermissionManager:
    """
    权限管理器
    """
    
    def __init__(self):
        # 用户权限映射
        self.user_permissions: Dict[str, Set[Permission]] = {}
        
        # 角色权限映射
        self.role_permissions: Dict[str, Set[Permission]] = {}
        
        # 用户角色映射
        self.user_roles: Dict[str, Set[str]] = {}
        
        # 敏感操作列表
        self.sensitive_operations: Set[str] = {
            "delete_file",
            "execute_command",
            "shutdown_system",
            "delete_task",
            "modify_config"
        }
    
    def grant_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> None:
        """
        授予用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限
        """
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        
        self.user_permissions[user_id].add(permission)
        logger.info(f"Granted {permission.value} to user {user_id}")
    
    def revoke_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> None:
        """
        撤销用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限
        """
        if user_id in self.user_permissions:
            self.user_permissions[user_id].discard(permission)
            logger.info(f"Revoked {permission.value} from user {user_id}")
    
    def check_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> bool:
        """
        检查用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限
            
        Returns:
            是否有权限
        """
        # 检查直接权限
        if user_id in self.user_permissions:
            if permission in self.user_permissions[user_id]:
                return True
        
        # 检查角色权限
        if user_id in self.user_roles:
            for role in self.user_roles[user_id]:
                if role in self.role_permissions:
                    if permission in self.role_permissions[role]:
                        return True
        
        return False
    
    def create_role(self, role_name: str, permissions: Set[Permission]) -> None:
        """
        创建角色
        
        Args:
            role_name: 角色名称
            permissions: 权限集合
        """
        self.role_permissions[role_name] = permissions
        logger.info(f"Created role: {role_name}")
    
    def assign_role(self, user_id: str, role_name: str) -> bool:
        """
        分配角色给用户
        
        Args:
            user_id: 用户ID
            role_name: 角色名称
            
        Returns:
            是否成功
        """
        if role_name not in self.role_permissions:
            logger.error(f"Role not found: {role_name}")
            return False
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        
        self.user_roles[user_id].add(role_name)
        logger.info(f"Assigned role {role_name} to user {user_id}")
        return True
    
    def remove_role(self, user_id: str, role_name: str) -> None:
        """
        移除用户角色
        
        Args:
            user_id: 用户ID
            role_name: 角色名称
        """
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role_name)
            logger.info(f"Removed role {role_name} from user {user_id}")
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """
        获取用户的所有权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            权限集合
        """
        permissions = set()
        
        # 添加直接权限
        if user_id in self.user_permissions:
            permissions.update(self.user_permissions[user_id])
        
        # 添加角色权限
        if user_id in self.user_roles:
            for role in self.user_roles[user_id]:
                if role in self.role_permissions:
                    permissions.update(self.role_permissions[role])
        
        return permissions
    
    def is_sensitive_operation(self, operation: str) -> bool:
        """
        检查是否为敏感操作
        
        Args:
            operation: 操作名称
            
        Returns:
            是否敏感
        """
        return operation in self.sensitive_operations
    
    def add_sensitive_operation(self, operation: str) -> None:
        """
        添加敏感操作
        
        Args:
            operation: 操作名称
        """
        self.sensitive_operations.add(operation)
    
    def remove_sensitive_operation(self, operation: str) -> None:
        """
        移除敏感操作
        
        Args:
            operation: 操作名称
        """
        self.sensitive_operations.discard(operation)


# 全局权限管理器实例
_permission_manager = PermissionManager()


def require_permission(permission: Permission):
    """
    权限检查装饰器
    
    Args:
        permission: 所需权限
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 从参数中获取user_id
            user_id = kwargs.get("user_id")
            if not user_id:
                raise PermissionError("User ID not provided")
            
            # 检查权限
            if not _permission_manager.check_permission(user_id, permission):
                raise PermissionError(
                    f"User {user_id} lacks permission: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 从参数中获取user_id
            user_id = kwargs.get("user_id")
            if not user_id:
                raise PermissionError("User ID not provided")
            
            # 检查权限
            if not _permission_manager.check_permission(user_id, permission):
                raise PermissionError(
                    f"User {user_id} lacks permission: {permission.value}"
                )
            
            return func(*args, **kwargs)
        
        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_permission_manager() -> PermissionManager:
    """
    获取全局权限管理器
    
    Returns:
        权限管理器实例
    """
    return _permission_manager
