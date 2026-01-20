"""
浏览器驱动实现 - 基于Playwright
"""
from typing import Any, Dict, Optional, List
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from ..core.interfaces import Driver, Action
from ..core.types import DriverType, BrowserType
from ..core.actions import (
    GoToURL, GoBack, GoForward, Refresh, WaitForLoad,
    Click, DoubleClick, RightClick, Hover, Drag,
    Type, Press, PressCombo, Upload, Clear,
    GetText, GetAttribute, Screenshot, GetUITree, IsVisible,
    WaitForElement, WaitForText, WaitForCondition, Sleep,
)


class BrowserDriver(Driver):
    """浏览器驱动 - 使用Playwright实现"""
    
    def __init__(
        self,
        browser_type: BrowserType = BrowserType.CHROMIUM,
        headless: bool = False
    ):
        """
        初始化浏览器驱动
        
        Args:
            browser_type: 浏览器类型
            headless: 是否无头模式
        """
        super().__init__(DriverType.BROWSER)
        self.browser_type = browser_type
        self.headless = headless
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._pages: List[Page] = []
        self._current_page: Optional[Page] = None
    
    async def start(self, **kwargs: Any) -> None:
        """
        启动浏览器
        
        Args:
            **kwargs: 浏览器启动参数
        """
        if self.is_running:
            return
        
        # 启动Playwright
        self._playwright = await async_playwright().start()
        
        # 根据浏览器类型启动对应的浏览器
        browser_launch_options = {
            "headless": kwargs.get("headless", self.headless),
            "args": kwargs.get("args", []),
        }
        
        if self.browser_type == BrowserType.CHROMIUM:
            self._browser = await self._playwright.chromium.launch(**browser_launch_options)
        elif self.browser_type == BrowserType.FIREFOX:
            self._browser = await self._playwright.firefox.launch(**browser_launch_options)
        elif self.browser_type == BrowserType.WEBKIT:
            self._browser = await self._playwright.webkit.launch(**browser_launch_options)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # 创建浏览器上下文
        context_options = {
            "viewport": kwargs.get("viewport", {"width": 1280, "height": 720}),
            "user_agent": kwargs.get("user_agent"),
            "locale": kwargs.get("locale"),
        }
        # 移除None值
        context_options = {k: v for k, v in context_options.items() if v is not None}
        
        self._context = await self._browser.new_context(**context_options)
        
        # 创建第一个页面
        self._current_page = await self._context.new_page()
        self._pages.append(self._current_page)
        
        self.is_running = True
    
    async def stop(self) -> None:
        """停止浏览器"""
        if not self.is_running:
            return
        
        # 关闭所有页面
        for page in self._pages:
            await page.close()
        self._pages.clear()
        self._current_page = None
        
        # 关闭上下文
        if self._context:
            await self._context.close()
            self._context = None
        
        # 关闭浏览器
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        # 停止Playwright
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        self.is_running = False
    
    async def execute_action(self, action: Action) -> Any:
        """
        执行操作
        
        Args:
            action: 操作实例
            
        Returns:
            操作结果
        """
        if not self.is_running:
            raise RuntimeError("Browser driver is not running")
        
        if not self._current_page:
            raise RuntimeError("No active page")
        
        # 根据操作类型分发到对应的处理方法
        if isinstance(action, GoToURL):
            return await self._handle_goto(action)
        elif isinstance(action, GoBack):
            return await self._handle_go_back()
        elif isinstance(action, GoForward):
            return await self._handle_go_forward()
        elif isinstance(action, Refresh):
            return await self._handle_refresh()
        elif isinstance(action, WaitForLoad):
            return await self._handle_wait_for_load(action)
        elif isinstance(action, Click):
            return await self._handle_click(action)
        elif isinstance(action, DoubleClick):
            return await self._handle_double_click(action)
        elif isinstance(action, RightClick):
            return await self._handle_right_click(action)
        elif isinstance(action, Hover):
            return await self._handle_hover(action)
        elif isinstance(action, Drag):
            return await self._handle_drag(action)
        elif isinstance(action, Type):
            return await self._handle_type(action)
        elif isinstance(action, Press):
            return await self._handle_press(action)
        elif isinstance(action, PressCombo):
            return await self._handle_press_combo(action)
        elif isinstance(action, Upload):
            return await self._handle_upload(action)
        elif isinstance(action, Clear):
            return await self._handle_clear(action)
        elif isinstance(action, GetText):
            return await self._handle_get_text(action)
        elif isinstance(action, GetAttribute):
            return await self._handle_get_attribute(action)
        elif isinstance(action, Screenshot):
            return await self._handle_screenshot(action)
        elif isinstance(action, GetUITree):
            return await self._handle_get_ui_tree(action)
        elif isinstance(action, IsVisible):
            return await self._handle_is_visible(action)
        elif isinstance(action, WaitForElement):
            return await self._handle_wait_for_element(action)
        elif isinstance(action, WaitForText):
            return await self._handle_wait_for_text(action)
        elif isinstance(action, WaitForCondition):
            return await self._handle_wait_for_condition(action)
        elif isinstance(action, Sleep):
            return await action.execute(self)
        else:
            raise NotImplementedError(f"Action {type(action).__name__} not implemented")
    
    # ==================== 导航操作处理 ====================
    
    async def _handle_goto(self, action: GoToURL) -> None:
        """处理导航到URL操作"""
        await self._current_page.goto(action.url)
    
    async def _handle_go_back(self) -> None:
        """处理后退操作"""
        await self._current_page.go_back()
    
    async def _handle_go_forward(self) -> None:
        """处理前进操作"""
        await self._current_page.go_forward()
    
    async def _handle_refresh(self) -> None:
        """处理刷新操作"""
        await self._current_page.reload()
    
    async def _handle_wait_for_load(self, action: WaitForLoad) -> None:
        """处理等待加载操作"""
        await self._current_page.wait_for_load_state(
            "load",
            timeout=action.timeout
        )
    
    # ==================== 交互操作处理 ====================
    
    async def _handle_click(self, action: Click) -> None:
        """处理点击操作"""
        await self._current_page.click(
            action.selector,
            button=action.button
        )
    
    async def _handle_double_click(self, action: DoubleClick) -> None:
        """处理双击操作"""
        await self._current_page.dblclick(action.selector)
    
    async def _handle_right_click(self, action: RightClick) -> None:
        """处理右键点击操作"""
        await self._current_page.click(action.selector, button="right")
    
    async def _handle_hover(self, action: Hover) -> None:
        """处理悬停操作"""
        await self._current_page.hover(action.selector)
    
    async def _handle_drag(self, action: Drag) -> None:
        """处理拖拽操作"""
        source = await self._current_page.query_selector(action.from_selector)
        target = await self._current_page.query_selector(action.to_selector)
        if source and target:
            await source.drag_to(target)
    
    # ==================== 输入操作处理 ====================
    
    async def _handle_type(self, action: Type) -> None:
        """处理输入操作"""
        await self._current_page.type(
            action.selector,
            action.text,
            delay=action.delay
        )
    
    async def _handle_press(self, action: Press) -> None:
        """处理按键操作"""
        await self._current_page.keyboard.press(action.key)
    
    async def _handle_press_combo(self, action: PressCombo) -> None:
        """处理组合键操作"""
        combo = "+".join(action.keys)
        await self._current_page.keyboard.press(combo)
    
    async def _handle_upload(self, action: Upload) -> None:
        """处理上传操作"""
        await self._current_page.set_input_files(
            action.selector,
            action.file_path
        )
    
    async def _handle_clear(self, action: Clear) -> None:
        """处理清空操作"""
        await self._current_page.fill(action.selector, "")
    
    # ==================== 查询操作处理 ====================
    
    async def _handle_get_text(self, action: GetText) -> str:
        """处理获取文本操作"""
        element = await self._current_page.query_selector(action.selector)
        if element:
            return await element.inner_text()
        return ""
    
    async def _handle_get_attribute(self, action: GetAttribute) -> Optional[str]:
        """处理获取属性操作"""
        return await self._current_page.get_attribute(
            action.selector,
            action.attribute
        )
    
    async def _handle_screenshot(self, action: Screenshot) -> bytes:
        """处理截图操作"""
        return await self._current_page.screenshot(
            path=action.path,
            full_page=action.full_page
        )
    
    async def _handle_get_ui_tree(self, action: GetUITree) -> Dict[str, Any]:
        """处理获取UI树操作"""
        # 简化实现：返回页面的基本信息
        return {
            "url": self._current_page.url,
            "title": await self._current_page.title(),
        }
    
    async def _handle_is_visible(self, action: IsVisible) -> bool:
        """处理可见性检查操作"""
        element = await self._current_page.query_selector(action.selector)
        if element:
            return await element.is_visible()
        return False
    
    # ==================== 等待操作处理 ====================
    
    async def _handle_wait_for_element(self, action: WaitForElement) -> None:
        """处理等待元素操作"""
        await self._current_page.wait_for_selector(
            action.selector,
            timeout=action.timeout
        )
    
    async def _handle_wait_for_text(self, action: WaitForText) -> None:
        """处理等待文本操作"""
        await self._current_page.wait_for_selector(
            f"text={action.text}",
            timeout=action.timeout
        )
    
    async def _handle_wait_for_condition(self, action: WaitForCondition) -> None:
        """处理等待条件操作"""
        await self._current_page.wait_for_function(
            action.condition,
            timeout=action.timeout
        )
    
    # ==================== 页面管理 ====================
    
    async def new_page(self) -> Page:
        """
        创建新页面
        
        Returns:
            新创建的页面
        """
        if not self._context:
            raise RuntimeError("Browser context not initialized")
        
        page = await self._context.new_page()
        self._pages.append(page)
        self._current_page = page
        return page
    
    async def switch_page(self, index: int) -> None:
        """
        切换到指定页面
        
        Args:
            index: 页面索引
        """
        if 0 <= index < len(self._pages):
            self._current_page = self._pages[index]
        else:
            raise IndexError(f"Page index {index} out of range")
    
    async def close_page(self, index: Optional[int] = None) -> None:
        """
        关闭页面
        
        Args:
            index: 页面索引，None表示关闭当前页面
        """
        if index is None:
            if self._current_page:
                await self._current_page.close()
                self._pages.remove(self._current_page)
                self._current_page = self._pages[0] if self._pages else None
        else:
            if 0 <= index < len(self._pages):
                page = self._pages[index]
                await page.close()
                self._pages.remove(page)
                if page == self._current_page:
                    self._current_page = self._pages[0] if self._pages else None
    
    def list_pages(self) -> List[Page]:
        """
        列出所有页面
        
        Returns:
            页面列表
        """
        return self._pages.copy()
    
    def get_current_page(self) -> Optional[Page]:
        """
        获取当前页面
        
        Returns:
            当前页面
        """
        return self._current_page
