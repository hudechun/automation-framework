"""
桌面驱动抽象层
"""
from abc import abstractmethod
from typing import Any, Dict, Optional, List
import platform

from ..core.interfaces import Driver, Action
from ..core.types import DriverType, Platform


class UIElement:
    """UI元素数据结构"""
    
    def __init__(
        self,
        element_id: str,
        name: str,
        element_type: str,
        rect: Dict[str, int],
        children: Optional[List['UIElement']] = None
    ):
        """
        初始化UI元素
        
        Args:
            element_id: 元素ID
            name: 元素名称
            element_type: 元素类型
            rect: 元素位置和大小 {x, y, width, height}
            children: 子元素列表
        """
        self.id = element_id
        self.name = name
        self.type = element_type
        self.rect = rect
        self.children = children or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典
        
        Returns:
            字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "rect": self.rect,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIElement':
        """
        从字典反序列化
        
        Args:
            data: 字典数据
            
        Returns:
            UI元素实例
        """
        children = [cls.from_dict(child) for child in data.get("children", [])]
        return cls(
            element_id=data["id"],
            name=data["name"],
            element_type=data["type"],
            rect=data["rect"],
            children=children
        )
    
    def find_child(
        self,
        name: Optional[str] = None,
        element_type: Optional[str] = None,
        element_id: Optional[str] = None
    ) -> Optional['UIElement']:
        """
        查找子元素
        
        Args:
            name: 元素名称
            element_type: 元素类型
            element_id: 元素ID
            
        Returns:
            找到的元素，未找到返回None
        """
        for child in self.children:
            if name and child.name == name:
                return child
            if element_type and child.type == element_type:
                return child
            if element_id and child.id == element_id:
                return child
            
            # 递归查找
            result = child.find_child(name, element_type, element_id)
            if result:
                return result
        
        return None


class DesktopDriver(Driver):
    """桌面驱动抽象基类"""
    
    def __init__(self):
        """初始化桌面驱动"""
        super().__init__(DriverType.DESKTOP)
        self.current_window = None
    
    @abstractmethod
    async def start_app(self, app_path: str, **kwargs: Any) -> None:
        """
        启动应用程序
        
        Args:
            app_path: 应用程序路径或名称
            **kwargs: 启动参数
        """
        pass
    
    @abstractmethod
    async def get_ui_tree(self, depth: int = -1) -> UIElement:
        """
        获取UI树
        
        Args:
            depth: 树的深度，-1表示无限深度
            
        Returns:
            UI树根元素
        """
        pass
    
    @abstractmethod
    async def find_element(
        self,
        name: Optional[str] = None,
        element_type: Optional[str] = None,
        element_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        查找元素
        
        Args:
            name: 元素名称
            element_type: 元素类型
            element_id: 元素ID
            
        Returns:
            找到的元素
        """
        pass
    
    @abstractmethod
    async def find_window(self, title: str) -> Optional[Any]:
        """
        查找窗口
        
        Args:
            title: 窗口标题
            
        Returns:
            窗口对象
        """
        pass
    
    @abstractmethod
    async def activate_window(self, window: Any) -> None:
        """
        激活窗口
        
        Args:
            window: 窗口对象
        """
        pass
    
    @abstractmethod
    async def close_window(self, window: Any) -> None:
        """
        关闭窗口
        
        Args:
            window: 窗口对象
        """
        pass


def get_platform() -> Platform:
    """
    检测操作系统平台
    
    Returns:
        平台类型
    """
    system = platform.system().lower()
    
    if system == "windows":
        return Platform.WINDOWS
    elif system == "darwin":
        return Platform.MACOS
    elif system == "linux":
        return Platform.LINUX
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def create_driver() -> DesktopDriver:
    """
    根据平台自动创建驱动
    
    Returns:
        桌面驱动实例
    """
    current_platform = get_platform()
    
    if current_platform == Platform.WINDOWS:
        from .windows_driver import WindowsDriver
        return WindowsDriver()
    elif current_platform == Platform.MACOS:
        from .macos_driver import MacOSDriver
        return MacOSDriver()
    elif current_platform == Platform.LINUX:
        from .linux_driver import LinuxDriver
        return LinuxDriver()
    else:
        raise RuntimeError(f"Unsupported platform: {current_platform}")
