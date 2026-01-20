"""
操作注册表实现
"""
from typing import Dict, List, Optional, Type, Callable
from .interfaces import Action, Driver
from .types import ActionType, DriverType


class ActionRegistry:
    """操作注册表 - 管理操作类型和驱动路由"""
    
    def __init__(self):
        """初始化注册表"""
        self._actions: Dict[str, Type[Action]] = {}
        self._routing_rules: Dict[str, DriverType] = {}
        self._custom_routes: List[Callable[[Action], Optional[DriverType]]] = []
    
    def register_action(
        self,
        name: str,
        action_class: Type[Action],
        driver_type: Optional[DriverType] = None
    ) -> None:
        """
        注册操作类型
        
        Args:
            name: 操作名称
            action_class: 操作类
            driver_type: 默认驱动类型（可选）
        """
        if not issubclass(action_class, Action):
            raise TypeError(f"{action_class} must be a subclass of Action")
        
        self._actions[name] = action_class
        
        if driver_type:
            self._routing_rules[name] = driver_type
    
    def get_action(self, name: str) -> Optional[Type[Action]]:
        """
        获取操作类
        
        Args:
            name: 操作名称
            
        Returns:
            操作类，如果不存在返回None
        """
        return self._actions.get(name)
    
    def list_actions(
        self,
        action_type: Optional[ActionType] = None
    ) -> List[str]:
        """
        列出所有注册的操作
        
        Args:
            action_type: 操作类型过滤（可选）
            
        Returns:
            操作名称列表
        """
        if action_type is None:
            return list(self._actions.keys())
        
        # 过滤指定类型的操作
        filtered = []
        for name, action_class in self._actions.items():
            # 创建临时实例检查类型
            try:
                temp_instance = action_class.__new__(action_class)
                if hasattr(temp_instance, 'action_type') and temp_instance.action_type == action_type:
                    filtered.append(name)
            except:
                pass
        
        return filtered
    
    def route_to_driver(self, action: Action) -> DriverType:
        """
        根据操作自动判断应该使用的驱动类型
        
        Args:
            action: 操作实例
            
        Returns:
            驱动类型
        """
        # 1. 首先检查自定义路由规则
        for custom_route in self._custom_routes:
            result = custom_route(action)
            if result is not None:
                return result
        
        # 2. 检查操作名称的路由规则
        action_name = action.__class__.__name__
        if action_name in self._routing_rules:
            return self._routing_rules[action_name]
        
        # 3. 根据操作类型自动判断
        # 默认情况下，所有操作都使用浏览器驱动
        # 特定的桌面操作需要显式注册
        return DriverType.BROWSER
    
    def add_routing_rule(
        self,
        action_name: str,
        driver_type: DriverType
    ) -> None:
        """
        添加路由规则
        
        Args:
            action_name: 操作名称
            driver_type: 驱动类型
        """
        self._routing_rules[action_name] = driver_type
    
    def add_custom_route(
        self,
        route_func: Callable[[Action], Optional[DriverType]]
    ) -> None:
        """
        添加自定义路由函数
        
        Args:
            route_func: 路由函数，接收Action返回DriverType或None
        """
        self._custom_routes.append(route_func)
    
    def remove_action(self, name: str) -> bool:
        """
        移除注册的操作
        
        Args:
            name: 操作名称
            
        Returns:
            是否成功移除
        """
        if name in self._actions:
            del self._actions[name]
            if name in self._routing_rules:
                del self._routing_rules[name]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有注册的操作和路由规则"""
        self._actions.clear()
        self._routing_rules.clear()
        self._custom_routes.clear()


# 全局注册表实例
_global_registry = ActionRegistry()


def get_global_registry() -> ActionRegistry:
    """
    获取全局注册表实例
    
    Returns:
        全局ActionRegistry实例
    """
    return _global_registry


def register_action(
    name: str,
    action_class: Type[Action],
    driver_type: Optional[DriverType] = None
) -> None:
    """
    在全局注册表中注册操作
    
    Args:
        name: 操作名称
        action_class: 操作类
        driver_type: 默认驱动类型（可选）
    """
    _global_registry.register_action(name, action_class, driver_type)


def get_action(name: str) -> Optional[Type[Action]]:
    """
    从全局注册表获取操作类
    
    Args:
        name: 操作名称
        
    Returns:
        操作类，如果不存在返回None
    """
    return _global_registry.get_action(name)
