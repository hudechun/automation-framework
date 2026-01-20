"""
Windows桌面驱动实现 - 基于pywinauto
"""
from typing import Any, Optional, List, Dict
import logging

from .desktop_driver import DesktopDriver, UIElement
from ..core.interfaces import Action
from ..core.actions import Click, Type, GetText

logger = logging.getLogger(__name__)


class WindowsDriver(DesktopDriver):
    """Windows桌面驱动 - 使用pywinauto实现"""
    
    def __init__(self):
        """初始化Windows驱动"""
        super().__init__()
        self._app = None
        self._backend = "uia"  # 默认使用UIAutomation后端
    
    async def start(self, **kwargs: Any) -> None:
        """
        启动驱动
        
        Args:
            **kwargs: 启动参数
        """
        self.is_running = True
    
    async def stop(self) -> None:
        """停止驱动"""
        if self._app:
            try:
                self._app.kill()
            except:
                pass
            self._app = None
        self.is_running = False
    
    async def start_app(self, app_path: str, **kwargs: Any) -> None:
        """
        启动Windows应用
        
        Args:
            app_path: 应用程序路径
            **kwargs: 启动参数
        """
        try:
            from pywinauto import Application
            
            backend = kwargs.get("backend", self._backend)
            self._app = Application(backend=backend).start(app_path)
            logger.info(f"Started application: {app_path}")
        except ImportError:
            logger.error("pywinauto not installed. Install with: pip install pywinauto")
            raise
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise
    
    async def find_window(self, title: str) -> Optional[Any]:
        """
        查找窗口
        
        Args:
            title: 窗口标题
            
        Returns:
            窗口对象
        """
        try:
            if not self._app:
                from pywinauto import Application
                self._app = Application(backend=self._backend).connect(title=title)
            
            window = self._app.window(title=title)
            self.current_window = window
            return window
        except Exception as e:
            logger.error(f"Failed to find window: {e}")
            return None
    
    async def activate_window(self, window: Any) -> None:
        """
        激活窗口
        
        Args:
            window: 窗口对象
        """
        try:
            window.set_focus()
            logger.info("Window activated")
        except Exception as e:
            logger.error(f"Failed to activate window: {e}")
            raise
    
    async def close_window(self, window: Any) -> None:
        """
        关闭窗口
        
        Args:
            window: 窗口对象
        """
        try:
            window.close()
            logger.info("Window closed")
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            raise
    
    async def get_ui_tree(self, depth: int = -1) -> UIElement:
        """
        获取UI树
        
        Args:
            depth: 树的深度
            
        Returns:
            UI树根元素
        """
        if not self.current_window:
            raise RuntimeError("No active window")
        
        try:
            # 获取窗口信息
            rect = self.current_window.rectangle()
            root = UIElement(
                element_id=str(self.current_window.handle),
                name=self.current_window.window_text(),
                element_type="Window",
                rect={
                    "x": rect.left,
                    "y": rect.top,
                    "width": rect.width(),
                    "height": rect.height()
                }
            )
            
            # 递归获取子元素
            if depth != 0:
                children = self._get_children(self.current_window, depth - 1)
                root.children = children
            
            return root
        except Exception as e:
            logger.error(f"Failed to get UI tree: {e}")
            raise
    
    def _get_children(self, element: Any, depth: int) -> List[UIElement]:
        """
        递归获取子元素
        
        Args:
            element: 父元素
            depth: 剩余深度
            
        Returns:
            子元素列表
        """
        children = []
        
        try:
            for child in element.children():
                try:
                    rect = child.rectangle()
                    ui_element = UIElement(
                        element_id=str(child.handle) if hasattr(child, 'handle') else "",
                        name=child.window_text(),
                        element_type=child.class_name(),
                        rect={
                            "x": rect.left,
                            "y": rect.top,
                            "width": rect.width(),
                            "height": rect.height()
                        }
                    )
                    
                    # 递归获取子元素
                    if depth != 0:
                        ui_element.children = self._get_children(child, depth - 1)
                    
                    children.append(ui_element)
                except:
                    continue
        except:
            pass
        
        return children
    
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
        if not self.current_window:
            raise RuntimeError("No active window")
        
        try:
            if name:
                return self.current_window.child_window(title=name, found_index=0)
            elif element_type:
                return self.current_window.child_window(class_name=element_type, found_index=0)
            elif element_id:
                return self.current_window.child_window(auto_id=element_id, found_index=0)
        except Exception as e:
            logger.error(f"Failed to find element: {e}")
            return None
    
    async def find_element_by_name(self, name: str) -> Optional[Any]:
        """
        通过名称查找元素
        
        Args:
            name: 元素名称
            
        Returns:
            找到的元素
        """
        return await self.find_element(name=name)
    
    async def find_element_by_id(self, element_id: str) -> Optional[Any]:
        """
        通过ID查找元素
        
        Args:
            element_id: 元素ID
            
        Returns:
            找到的元素
        """
        return await self.find_element(element_id=element_id)
    
    async def find_element_by_type(self, element_type: str) -> Optional[Any]:
        """
        通过类型查找元素
        
        Args:
            element_type: 元素类型
            
        Returns:
            找到的元素
        """
        return await self.find_element(element_type=element_type)
    
    async def execute_action(self, action: Action) -> Any:
        """
        执行操作
        
        Args:
            action: 操作实例
            
        Returns:
            操作结果
        """
        if not self.is_running:
            raise RuntimeError("Desktop driver is not running")
        
        # 根据操作类型分发
        if isinstance(action, Click):
            return await self._handle_click(action)
        elif isinstance(action, Type):
            return await self._handle_type(action)
        elif isinstance(action, GetText):
            return await self._handle_get_text(action)
        else:
            raise NotImplementedError(f"Action {type(action).__name__} not implemented")
    
    async def _handle_click(self, action: Click) -> None:
        """处理点击操作"""
        element = await self.find_element(name=action.selector)
        if element:
            element.click()
    
    async def _handle_type(self, action: Type) -> None:
        """处理输入操作"""
        element = await self.find_element(name=action.selector)
        if element:
            element.type_keys(action.text, pause=action.delay / 1000)
    
    async def _handle_get_text(self, action: GetText) -> str:
        """处理获取文本操作"""
        element = await self.find_element(name=action.selector)
        if element:
            return element.window_text()
        return ""
