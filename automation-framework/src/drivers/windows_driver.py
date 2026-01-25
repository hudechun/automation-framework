"""
Windows桌面驱动实现 - 基于pywinauto
"""
from typing import Any, Optional, List, Dict
import logging
import asyncio
import os

from .desktop_driver import DesktopDriver, UIElement
from ..core.interfaces import Action
from ..core.actions import (
    Click, DoubleClick, RightClick, Hover, Type, GetText,
    Press, PressCombo, Clear, Sleep,
    StartApp, SwitchWindow, CloseWindow,
    Copy, Paste, Cut,
    OpenFile, SaveFile, SaveAs,
    ClickCoordinate
)
from ..core.wechat_actions import (
    OpenWeChat, FindContact, FindGroup, SendMessage,
    WaitForMessage, SendFile, SendImage, GetChatHistory
)

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
        # 如果current_window为None，尝试查找活动窗口
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                    logger.info("Using default top window for element search")
                except Exception as e:
                    logger.error(f"Failed to get default window: {e}")
                    raise RuntimeError("No active window and cannot find default window")
            else:
                raise RuntimeError("No active window and no application instance")
        
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
        elif isinstance(action, DoubleClick):
            return await self._handle_double_click(action)
        elif isinstance(action, RightClick):
            return await self._handle_right_click(action)
        elif isinstance(action, Hover):
            return await self._handle_hover(action)
        elif isinstance(action, Type):
            return await self._handle_type(action)
        elif isinstance(action, GetText):
            return await self._handle_get_text(action)
        elif isinstance(action, Press):
            return await self._handle_press(action)
        elif isinstance(action, PressCombo):
            return await self._handle_press_combo(action)
        elif isinstance(action, Clear):
            return await self._handle_clear(action)
        elif isinstance(action, Sleep):
            return await self._handle_sleep(action)
        elif isinstance(action, StartApp):
            return await self._handle_start_app(action)
        elif isinstance(action, SwitchWindow):
            return await self._handle_switch_window(action)
        elif isinstance(action, CloseWindow):
            return await self._handle_close_window(action)
        elif isinstance(action, Copy):
            return await self._handle_copy(action)
        elif isinstance(action, Paste):
            return await self._handle_paste(action)
        elif isinstance(action, Cut):
            return await self._handle_cut(action)
        elif isinstance(action, OpenFile):
            return await self._handle_open_file(action)
        elif isinstance(action, SaveFile):
            return await self._handle_save_file(action)
        elif isinstance(action, SaveAs):
            return await self._handle_save_as(action)
        elif isinstance(action, ClickCoordinate):
            return await self._handle_click_coordinate(action)
        # 微信专用操作
        elif isinstance(action, OpenWeChat):
            return await self._handle_open_wechat(action)
        elif isinstance(action, FindContact):
            return await self._handle_find_contact(action)
        elif isinstance(action, FindGroup):
            return await self._handle_find_group(action)
        elif isinstance(action, SendMessage):
            return await self._handle_send_message(action)
        elif isinstance(action, WaitForMessage):
            return await self._handle_wait_for_message(action)
        elif isinstance(action, SendFile):
            return await self._handle_send_file(action)
        elif isinstance(action, SendImage):
            return await self._handle_send_image(action)
        elif isinstance(action, GetChatHistory):
            return await self._handle_get_chat_history(action)
        else:
            raise NotImplementedError(f"Action {type(action).__name__} not implemented")
    
    async def _handle_click(self, action: Click) -> None:
        """处理点击操作"""
        # 支持多种selector格式
        element = await self._find_element_by_selector(action.selector)
        if element:
            element.click()
        else:
            raise RuntimeError(f"Element not found: {action.selector}")
    
    async def _handle_type(self, action: Type) -> None:
        """处理输入操作"""
        # 支持多种selector格式
        element = await self._find_element_by_selector(action.selector)
        if element:
            element.type_keys(action.text, pause=action.delay / 1000)
        else:
            raise RuntimeError(f"Element not found: {action.selector}")
    
    async def _handle_get_text(self, action: GetText) -> str:
        """处理获取文本操作"""
        # 支持多种selector格式
        element = await self._find_element_by_selector(action.selector)
        if element:
            return element.window_text()
        return ""
    
    async def _find_element_by_selector(self, selector: str) -> Optional[Any]:
        """
        根据selector查找元素，支持多种格式
        
        Args:
            selector: 选择器，支持格式：
                - 元素名称: "Button1"
                - 元素ID: "#element_id"
                - 元素类型: ".Button"
                - 坐标: "(100, 200)" (暂不支持，需要pyautogui)
        
        Returns:
            找到的元素
        """
        if not selector:
            return None
        
        # 尝试按ID查找（格式: #element_id）
        if selector.startswith("#"):
            element_id = selector[1:]
            return await self.find_element(element_id=element_id)
        
        # 尝试按类型查找（格式: .Button）
        if selector.startswith("."):
            element_type = selector[1:]
            return await self.find_element(element_type=element_type)
        
        # 尝试按名称查找（默认）
        return await self.find_element(name=selector)
    
    async def _handle_double_click(self, action: DoubleClick) -> None:
        """处理双击操作"""
        element = await self._find_element_by_selector(action.selector)
        if element:
            element.double_click()
        else:
            raise RuntimeError(f"Element not found: {action.selector}")
    
    async def _handle_right_click(self, action: RightClick) -> None:
        """处理右键点击操作"""
        element = await self._find_element_by_selector(action.selector)
        if element:
            element.right_click()
        else:
            raise RuntimeError(f"Element not found: {action.selector}")
    
    async def _handle_hover(self, action: Hover) -> None:
        """处理悬停操作"""
        element = await self._find_element_by_selector(action.selector)
        if element:
            element.hover_input()
        else:
            raise RuntimeError(f"Element not found: {action.selector}")
    
    async def _handle_press(self, action: Press) -> None:
        """处理按键操作"""
        if not self.current_window:
            # 尝试获取当前窗口
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for key press")
            else:
                raise RuntimeError("No active window and no application instance")
        
        # 使用pywinauto的type_keys方法
        try:
            self.current_window.type_keys(action.key)
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            raise
    
    async def _handle_press_combo(self, action: PressCombo) -> None:
        """处理组合键操作"""
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for key combo")
            else:
                raise RuntimeError("No active window and no application instance")
        
        # 组合键格式: ["ctrl", "s"] -> "{Ctrl}s"
        try:
            key_combo = "+".join(action.keys).lower()
            # 转换常见组合键
            key_combo = key_combo.replace("ctrl", "ctrl")
            key_combo = key_combo.replace("alt", "alt")
            key_combo = key_combo.replace("shift", "shift")
            self.current_window.type_keys(f"{{{key_combo}}}")
        except Exception as e:
            logger.error(f"Failed to press combo keys: {e}")
            raise
    
    async def _handle_clear(self, action: Clear) -> None:
        """处理清空输入框操作"""
        element = await self._find_element_by_selector(action.selector)
        if element:
            element.set_text("")
        else:
            raise RuntimeError(f"Element not found: {action.selector}")
    
    async def _handle_sleep(self, action: Sleep) -> None:
        """处理休眠操作"""
        import asyncio
        await asyncio.sleep(action.duration / 1000)
    
    async def _handle_start_app(self, action: StartApp) -> None:
        """处理启动应用操作"""
        await self.start_app(action.app_path, **action.kwargs)
        if action.window_title:
            await asyncio.sleep(1.0)  # 等待应用启动
            window = await self.find_window(action.window_title)
            if window:
                await self.activate_window(window)
    
    async def _handle_switch_window(self, action: SwitchWindow) -> None:
        """处理切换窗口操作"""
        window = await self.find_window(action.window_title)
        if window:
            await self.activate_window(window)
        else:
            raise RuntimeError(f"Window not found: {action.window_title}")
    
    async def _handle_close_window(self, action: CloseWindow) -> None:
        """处理关闭窗口操作"""
        if action.window_title:
            window = await self.find_window(action.window_title)
            if window:
                await self.close_window(window)
            else:
                raise RuntimeError(f"Window not found: {action.window_title}")
        else:
            # 关闭当前窗口
            if self.current_window:
                await self.close_window(self.current_window)
            else:
                raise RuntimeError("No active window to close")
    
    async def _handle_copy(self, action: Copy) -> None:
        """处理复制操作"""
        if action.selector:
            # 如果有selector，先选中元素
            element = await self._find_element_by_selector(action.selector)
            if element:
                element.select()
        # 使用Ctrl+C
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for copy")
            else:
                raise RuntimeError("No active window and no application instance")
        
        try:
            self.current_window.type_keys("^c")  # Ctrl+C
        except Exception as e:
            logger.error(f"Failed to copy: {e}")
            raise
    
    async def _handle_paste(self, action: Paste) -> None:
        """处理粘贴操作"""
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for paste")
            else:
                raise RuntimeError("No active window and no application instance")
        
        try:
            if action.selector:
                # 如果有selector，先定位到元素
                element = await self._find_element_by_selector(action.selector)
                if element:
                    element.set_focus()
            self.current_window.type_keys("^v")  # Ctrl+V
        except Exception as e:
            logger.error(f"Failed to paste: {e}")
            raise
    
    async def _handle_cut(self, action: Cut) -> None:
        """处理剪切操作"""
        if action.selector:
            element = await self._find_element_by_selector(action.selector)
            if element:
                element.select()
        
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for cut")
            else:
                raise RuntimeError("No active window and no application instance")
        
        try:
            self.current_window.type_keys("^x")  # Ctrl+X
        except Exception as e:
            logger.error(f"Failed to cut: {e}")
            raise
    
    async def _handle_open_file(self, action: OpenFile) -> None:
        """处理打开文件操作"""
        import os
        
        if action.app_path:
            # 如果指定了应用，先启动应用
            await self.start_app(action.app_path)
            await asyncio.sleep(1.0)
        
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for open file")
            else:
                raise RuntimeError("No active window and no application instance")
        
        # 使用Ctrl+O打开文件对话框
        try:
            self.current_window.type_keys("^o")  # Ctrl+O
            await asyncio.sleep(0.5)
            
            # 在文件对话框中输入文件路径
            # 注意：这需要文件对话框已经打开
            # 实际实现可能需要更复杂的逻辑来操作文件对话框
            file_path = os.path.abspath(action.file_path)
            self.current_window.type_keys(file_path)
            await asyncio.sleep(0.3)
            self.current_window.type_keys("{ENTER}")
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
            raise
    
    async def _handle_save_file(self, action: SaveFile) -> None:
        """处理保存文件操作"""
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for save file")
            else:
                raise RuntimeError("No active window and no application instance")
        
        try:
            self.current_window.type_keys("^s")  # Ctrl+S
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise
    
    async def _handle_save_as(self, action: SaveAs) -> None:
        """处理另存为操作"""
        if not self.current_window:
            if self._app:
                try:
                    self.current_window = self._app.top_window()
                except:
                    raise RuntimeError("No active window for save as")
            else:
                raise RuntimeError("No active window and no application instance")
        
        try:
            # 使用Ctrl+Shift+S或F12打开另存为对话框
            self.current_window.type_keys("^+s")  # Ctrl+Shift+S
            await asyncio.sleep(0.5)
            
            # 在文件对话框中输入文件路径
            file_path = os.path.abspath(action.file_path)
            self.current_window.type_keys(file_path)
            await asyncio.sleep(0.3)
            self.current_window.type_keys("{ENTER}")
        except Exception as e:
            logger.error(f"Failed to save as: {e}")
            raise
    
    async def _handle_click_coordinate(self, action: ClickCoordinate) -> None:
        """处理坐标点击操作"""
        try:
            import pyautogui
            pyautogui.click(action.x, action.y, button=action.button)
        except ImportError:
            logger.error("pyautogui not installed. Install with: pip install pyautogui")
            raise
        except Exception as e:
            logger.error(f"Failed to click at coordinate ({action.x}, {action.y}): {e}")
            raise
    
    # ==================== 微信专用操作处理 ====================
    
    async def _handle_open_wechat(self, action: OpenWeChat) -> None:
        """处理打开微信操作"""
        try:
            wechat_path = action.wechat_path
            if not wechat_path:
                # 自动查找微信路径
                import winreg
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Tencent\WeChat"
                    )
                    wechat_path = winreg.QueryValueEx(key, "InstallPath")[0] + r"\WeChat.exe"
                    winreg.CloseKey(key)
                except:
                    # 默认路径
                    wechat_path = r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
            
            await self.start_app(wechat_path)
            # 等待微信窗口出现
            await asyncio.sleep(3)
            await self.find_window("微信")
            logger.info("WeChat opened successfully")
        except Exception as e:
            logger.error(f"Failed to open WeChat: {e}")
            raise
    
    async def _handle_find_contact(self, action: FindContact) -> Any:
        """处理查找联系人操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 点击搜索框
            search_box = await self.find_element(name="搜索")
            if search_box:
                search_box.click()
                await asyncio.sleep(0.5)
                
                # 输入联系人名称
                search_box.type_keys(action.contact_name)
                await asyncio.sleep(1)
                
                # 点击第一个搜索结果
                # 注意：这里需要根据实际微信界面调整
                # 微信的UI结构可能因版本而异
                contact_item = await self.find_element(name=action.contact_name)
                if contact_item:
                    contact_item.click()
                    await asyncio.sleep(0.5)
                    return contact_item
                else:
                    raise RuntimeError(f"Contact '{action.contact_name}' not found")
            else:
                raise RuntimeError("Search box not found")
        except Exception as e:
            logger.error(f"Failed to find contact: {e}")
            raise
    
    async def _handle_find_group(self, action: FindGroup) -> Any:
        """处理查找群聊操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 点击搜索框
            search_box = await self.find_element(name="搜索")
            if search_box:
                search_box.click()
                await asyncio.sleep(0.5)
                
                # 输入群聊名称
                search_box.type_keys(action.group_name)
                await asyncio.sleep(1)
                
                # 点击第一个搜索结果
                group_item = await self.find_element(name=action.group_name)
                if group_item:
                    group_item.click()
                    await asyncio.sleep(0.5)
                    return group_item
                else:
                    raise RuntimeError(f"Group '{action.group_name}' not found")
            else:
                raise RuntimeError("Search box not found")
        except Exception as e:
            logger.error(f"Failed to find group: {e}")
            raise
    
    async def _handle_send_message(self, action: SendMessage) -> None:
        """处理发送消息操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 如果指定了联系人，先查找联系人
            if action.contact_name:
                await self._handle_find_contact(FindContact(action.contact_name))
            elif action.group_name:
                await self._handle_find_group(FindGroup(action.group_name))
            
            # 查找输入框（微信消息输入框）
            # 注意：这里需要根据实际微信界面调整
            input_box = await self.find_element(name="输入")
            if not input_box:
                # 尝试其他可能的名称
                input_box = await self.find_element(element_type="Edit")
            
            if input_box:
                input_box.click()
                await asyncio.sleep(0.3)
                input_box.type_keys(action.message)
                await asyncio.sleep(0.5)
                
                # 按Enter发送
                input_box.type_keys("{ENTER}")
                await asyncio.sleep(0.5)
                logger.info(f"Message sent: {action.message}")
            else:
                raise RuntimeError("Message input box not found")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def _handle_wait_for_message(self, action: WaitForMessage) -> Any:
        """处理等待消息操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 如果指定了联系人，先查找联系人
            if action.contact_name:
                await self._handle_find_contact(FindContact(action.contact_name))
            elif action.group_name:
                await self._handle_find_group(FindGroup(action.group_name))
            
            # 等待消息（轮询检查）
            import time
            start_time = time.time()
            timeout_seconds = action.timeout / 1000
            
            while time.time() - start_time < timeout_seconds:
                # 获取最新的消息（这里需要根据实际微信界面实现）
                # 简化实现：检查是否有新消息
                await asyncio.sleep(1)
                
                # TODO: 实现实际的消息检查逻辑
                # 这里需要根据微信的实际UI结构来实现
                
            raise TimeoutError(f"Timeout waiting for message after {timeout_seconds} seconds")
        except Exception as e:
            logger.error(f"Failed to wait for message: {e}")
            raise
    
    async def _handle_send_file(self, action: SendFile) -> None:
        """处理发送文件操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 如果指定了联系人，先查找联系人
            if action.contact_name:
                await self._handle_find_contact(FindContact(action.contact_name))
            elif action.group_name:
                await self._handle_find_group(FindGroup(action.group_name))
            
            # 点击文件按钮（微信界面中的文件发送按钮）
            # 注意：这里需要根据实际微信界面调整
            file_button = await self.find_element(name="文件")
            if file_button:
                file_button.click()
                await asyncio.sleep(0.5)
                
                # 选择文件（使用Windows文件对话框）
                # 这里可以使用pywinauto操作文件对话框
                import pywinauto
                file_dialog = pywinauto.Desktop(backend="uia").window(title="打开")
                if file_dialog.exists():
                    file_dialog.Edit.set_text(action.file_path)
                    file_dialog.Button(name="打开").click()
                    await asyncio.sleep(1)
                    logger.info(f"File sent: {action.file_path}")
                else:
                    raise RuntimeError("File dialog not found")
            else:
                raise RuntimeError("File button not found")
        except Exception as e:
            logger.error(f"Failed to send file: {e}")
            raise
    
    async def _handle_send_image(self, action: SendImage) -> None:
        """处理发送图片操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 如果指定了联系人，先查找联系人
            if action.contact_name:
                await self._handle_find_contact(FindContact(action.contact_name))
            elif action.group_name:
                await self._handle_find_group(FindGroup(action.group_name))
            
            # 点击图片按钮（微信界面中的图片发送按钮）
            image_button = await self.find_element(name="图片")
            if image_button:
                image_button.click()
                await asyncio.sleep(0.5)
                
                # 选择图片（使用Windows文件对话框）
                import pywinauto
                file_dialog = pywinauto.Desktop(backend="uia").window(title="打开")
                if file_dialog.exists():
                    file_dialog.Edit.set_text(action.image_path)
                    file_dialog.Button(name="打开").click()
                    await asyncio.sleep(1)
                    logger.info(f"Image sent: {action.image_path}")
                else:
                    raise RuntimeError("File dialog not found")
            else:
                raise RuntimeError("Image button not found")
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
            raise
    
    async def _handle_get_chat_history(self, action: GetChatHistory) -> List[Dict[str, Any]]:
        """处理获取聊天记录操作"""
        try:
            if not self.current_window:
                await self.find_window("微信")
            
            # 如果指定了联系人，先查找联系人
            if action.contact_name:
                await self._handle_find_contact(FindContact(action.contact_name))
            elif action.group_name:
                await self._handle_find_group(FindGroup(action.group_name))
            
            # 获取聊天记录
            # 注意：这里需要根据实际微信界面实现
            # 微信的聊天记录可能在不同的UI元素中
            messages = []
            
            # TODO: 实现实际的消息提取逻辑
            # 这里需要根据微信的实际UI结构来实现
            # 可能需要滚动、提取文本等操作
            
            logger.info(f"Retrieved {len(messages)} messages from chat history")
            return messages
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            raise
