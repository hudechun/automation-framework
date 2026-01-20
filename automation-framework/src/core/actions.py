"""
具体操作类实现
"""
from typing import Any, Optional, Dict, List
from .interfaces import Action, Driver
from .types import ActionType


# ==================== 导航操作 ====================

class GoToURL(Action):
    """导航到指定URL"""
    
    def __init__(self, url: str):
        super().__init__(ActionType.NAVIGATION, url=url)
        self.url = url
    
    def validate(self) -> bool:
        """验证URL参数"""
        return bool(self.url and isinstance(self.url, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行导航操作"""
        if not self.validate():
            raise ValueError("Invalid URL parameter")
        return await driver.execute_action(self)


class GoBack(Action):
    """后退到上一页"""
    
    def __init__(self):
        super().__init__(ActionType.NAVIGATION)
    
    async def execute(self, driver: Driver) -> Any:
        """执行后退操作"""
        return await driver.execute_action(self)


class GoForward(Action):
    """前进到下一页"""
    
    def __init__(self):
        super().__init__(ActionType.NAVIGATION)
    
    async def execute(self, driver: Driver) -> Any:
        """执行前进操作"""
        return await driver.execute_action(self)


class Refresh(Action):
    """刷新当前页面"""
    
    def __init__(self):
        super().__init__(ActionType.NAVIGATION)
    
    async def execute(self, driver: Driver) -> Any:
        """执行刷新操作"""
        return await driver.execute_action(self)


class WaitForLoad(Action):
    """等待页面加载完成"""
    
    def __init__(self, timeout: int = 30000):
        super().__init__(ActionType.NAVIGATION, timeout=timeout)
        self.timeout = timeout
    
    def validate(self) -> bool:
        """验证超时参数"""
        return isinstance(self.timeout, int) and self.timeout > 0
    
    async def execute(self, driver: Driver) -> Any:
        """执行等待加载操作"""
        if not self.validate():
            raise ValueError("Invalid timeout parameter")
        return await driver.execute_action(self)


# ==================== 交互操作 ====================

class Click(Action):
    """点击元素"""
    
    def __init__(self, selector: str, button: str = "left"):
        super().__init__(ActionType.INTERACTION, selector=selector, button=button)
        self.selector = selector
        self.button = button
    
    def validate(self) -> bool:
        """验证选择器和按钮参数"""
        return (
            bool(self.selector and isinstance(self.selector, str)) and
            self.button in ["left", "right", "middle"]
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行点击操作"""
        if not self.validate():
            raise ValueError("Invalid selector or button parameter")
        return await driver.execute_action(self)


class DoubleClick(Action):
    """双击元素"""
    
    def __init__(self, selector: str):
        super().__init__(ActionType.INTERACTION, selector=selector)
        self.selector = selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return bool(self.selector and isinstance(self.selector, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行双击操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameter")
        return await driver.execute_action(self)


class RightClick(Action):
    """右键点击元素"""
    
    def __init__(self, selector: str):
        super().__init__(ActionType.INTERACTION, selector=selector)
        self.selector = selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return bool(self.selector and isinstance(self.selector, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行右键点击操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameter")
        return await driver.execute_action(self)


class Hover(Action):
    """悬停在元素上"""
    
    def __init__(self, selector: str):
        super().__init__(ActionType.INTERACTION, selector=selector)
        self.selector = selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return bool(self.selector and isinstance(self.selector, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行悬停操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameter")
        return await driver.execute_action(self)


class Drag(Action):
    """拖拽元素"""
    
    def __init__(self, from_selector: str, to_selector: str):
        super().__init__(
            ActionType.INTERACTION,
            from_selector=from_selector,
            to_selector=to_selector
        )
        self.from_selector = from_selector
        self.to_selector = to_selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return (
            bool(self.from_selector and isinstance(self.from_selector, str)) and
            bool(self.to_selector and isinstance(self.to_selector, str))
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行拖拽操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameters")
        return await driver.execute_action(self)


# ==================== 输入操作 ====================

class Type(Action):
    """输入文本"""
    
    def __init__(self, selector: str, text: str, delay: int = 0):
        super().__init__(
            ActionType.INPUT,
            selector=selector,
            text=text,
            delay=delay
        )
        self.selector = selector
        self.text = text
        self.delay = delay
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.selector and isinstance(self.selector, str)) and
            isinstance(self.text, str) and
            isinstance(self.delay, int) and self.delay >= 0
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行输入操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class Press(Action):
    """按下键盘按键"""
    
    def __init__(self, key: str):
        super().__init__(ActionType.INPUT, key=key)
        self.key = key
    
    def validate(self) -> bool:
        """验证按键参数"""
        return bool(self.key and isinstance(self.key, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行按键操作"""
        if not self.validate():
            raise ValueError("Invalid key parameter")
        return await driver.execute_action(self)


class PressCombo(Action):
    """按下组合键"""
    
    def __init__(self, keys: List[str]):
        super().__init__(ActionType.INPUT, keys=keys)
        self.keys = keys
    
    def validate(self) -> bool:
        """验证组合键参数"""
        return (
            isinstance(self.keys, list) and
            len(self.keys) > 0 and
            all(isinstance(k, str) for k in self.keys)
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行组合键操作"""
        if not self.validate():
            raise ValueError("Invalid keys parameter")
        return await driver.execute_action(self)


class Upload(Action):
    """上传文件"""
    
    def __init__(self, selector: str, file_path: str):
        super().__init__(
            ActionType.INPUT,
            selector=selector,
            file_path=file_path
        )
        self.selector = selector
        self.file_path = file_path
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.selector and isinstance(self.selector, str)) and
            bool(self.file_path and isinstance(self.file_path, str))
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行上传操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class Clear(Action):
    """清空输入框"""
    
    def __init__(self, selector: str):
        super().__init__(ActionType.INPUT, selector=selector)
        self.selector = selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return bool(self.selector and isinstance(self.selector, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行清空操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameter")
        return await driver.execute_action(self)


# ==================== 查询操作 ====================

class GetText(Action):
    """获取元素文本"""
    
    def __init__(self, selector: str):
        super().__init__(ActionType.QUERY, selector=selector)
        self.selector = selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return bool(self.selector and isinstance(self.selector, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行获取文本操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameter")
        return await driver.execute_action(self)


class GetAttribute(Action):
    """获取元素属性"""
    
    def __init__(self, selector: str, attribute: str):
        super().__init__(
            ActionType.QUERY,
            selector=selector,
            attribute=attribute
        )
        self.selector = selector
        self.attribute = attribute
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.selector and isinstance(self.selector, str)) and
            bool(self.attribute and isinstance(self.attribute, str))
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行获取属性操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class Screenshot(Action):
    """截图"""
    
    def __init__(self, path: str, full_page: bool = False):
        super().__init__(
            ActionType.QUERY,
            path=path,
            full_page=full_page
        )
        self.path = path
        self.full_page = full_page
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.path and isinstance(self.path, str)) and
            isinstance(self.full_page, bool)
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行截图操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class GetUITree(Action):
    """获取UI树"""
    
    def __init__(self, depth: int = -1):
        super().__init__(ActionType.QUERY, depth=depth)
        self.depth = depth
    
    def validate(self) -> bool:
        """验证深度参数"""
        return isinstance(self.depth, int)
    
    async def execute(self, driver: Driver) -> Any:
        """执行获取UI树操作"""
        if not self.validate():
            raise ValueError("Invalid depth parameter")
        return await driver.execute_action(self)


class IsVisible(Action):
    """检查元素是否可见"""
    
    def __init__(self, selector: str):
        super().__init__(ActionType.QUERY, selector=selector)
        self.selector = selector
    
    def validate(self) -> bool:
        """验证选择器参数"""
        return bool(self.selector and isinstance(self.selector, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行可见性检查操作"""
        if not self.validate():
            raise ValueError("Invalid selector parameter")
        return await driver.execute_action(self)


# ==================== 等待操作 ====================

class WaitForElement(Action):
    """等待元素出现"""
    
    def __init__(self, selector: str, timeout: int = 30000):
        super().__init__(
            ActionType.WAIT,
            selector=selector,
            timeout=timeout
        )
        self.selector = selector
        self.timeout = timeout
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.selector and isinstance(self.selector, str)) and
            isinstance(self.timeout, int) and self.timeout > 0
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行等待元素操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class WaitForText(Action):
    """等待文本出现"""
    
    def __init__(self, text: str, timeout: int = 30000):
        super().__init__(
            ActionType.WAIT,
            text=text,
            timeout=timeout
        )
        self.text = text
        self.timeout = timeout
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.text and isinstance(self.text, str)) and
            isinstance(self.timeout, int) and self.timeout > 0
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行等待文本操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class WaitForCondition(Action):
    """等待条件满足"""
    
    def __init__(self, condition: str, timeout: int = 30000):
        super().__init__(
            ActionType.WAIT,
            condition=condition,
            timeout=timeout
        )
        self.condition = condition
        self.timeout = timeout
    
    def validate(self) -> bool:
        """验证参数"""
        return (
            bool(self.condition and isinstance(self.condition, str)) and
            isinstance(self.timeout, int) and self.timeout > 0
        )
    
    async def execute(self, driver: Driver) -> Any:
        """执行等待条件操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)


class Sleep(Action):
    """休眠指定时间"""
    
    def __init__(self, duration: int):
        super().__init__(ActionType.WAIT, duration=duration)
        self.duration = duration
    
    def validate(self) -> bool:
        """验证时长参数"""
        return isinstance(self.duration, int) and self.duration > 0
    
    async def execute(self, driver: Driver) -> Any:
        """执行休眠操作"""
        if not self.validate():
            raise ValueError("Invalid duration parameter")
        import asyncio
        await asyncio.sleep(self.duration / 1000)  # 转换为秒
        return None
