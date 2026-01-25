"""
智能等待 - 等待特定条件而非固定时间
"""
import asyncio
import logging
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta
from .interfaces import Action, Driver
from .types import ActionType

logger = logging.getLogger(__name__)


class WaitCondition:
    """等待条件基类"""
    
    def __init__(self, timeout: int = 30000, poll_interval: int = 100):
        """
        初始化等待条件
        
        Args:
            timeout: 超时时间（毫秒）
            poll_interval: 轮询间隔（毫秒）
        """
        self.timeout = timeout
        self.poll_interval = poll_interval
    
    async def check(self, driver: Any) -> bool:
        """
        检查条件是否满足
        
        Args:
            driver: 驱动实例
            
        Returns:
            条件是否满足
        """
        raise NotImplementedError
    
    async def wait(self, driver: Any) -> bool:
        """
        等待条件满足
        
        Args:
            driver: 驱动实例
            
        Returns:
            是否在超时前满足条件
        """
        start_time = datetime.now()
        timeout_delta = timedelta(milliseconds=self.timeout)
        poll_delta = timedelta(milliseconds=self.poll_interval)
        
        while datetime.now() - start_time < timeout_delta:
            try:
                if await self.check(driver):
                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.debug(f"Wait condition satisfied after {elapsed:.2f}s")
                    return True
            except Exception as e:
                logger.debug(f"Wait condition check failed: {e}")
            
            await asyncio.sleep(self.poll_interval / 1000)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.warning(f"Wait condition timeout after {elapsed:.2f}s")
        return False


class ElementVisibleCondition(WaitCondition):
    """等待元素可见"""
    
    def __init__(self, selector: str, timeout: int = 30000, poll_interval: int = 100):
        super().__init__(timeout, poll_interval)
        self.selector = selector
    
    async def check(self, driver: Any) -> bool:
        """检查元素是否可见"""
        from .element_locator import ElementLocator
        locator = ElementLocator(self.selector)
        playwright_locator = locator.to_playwright_locator(driver._current_page)
        try:
            await playwright_locator.first.wait_for(state="visible", timeout=100)
            return True
        except:
            return False


class ElementNotVisibleCondition(WaitCondition):
    """等待元素不可见"""
    
    def __init__(self, selector: str, timeout: int = 30000, poll_interval: int = 100):
        super().__init__(timeout, poll_interval)
        self.selector = selector
    
    async def check(self, driver: Any) -> bool:
        """检查元素是否不可见"""
        from .element_locator import ElementLocator
        locator = ElementLocator(self.selector)
        playwright_locator = locator.to_playwright_locator(driver._current_page)
        try:
            count = await playwright_locator.count()
            return count == 0 or not await playwright_locator.first.is_visible()
        except:
            return True


class TextPresentCondition(WaitCondition):
    """等待文本出现"""
    
    def __init__(self, text: str, timeout: int = 30000, poll_interval: int = 100):
        super().__init__(timeout, poll_interval)
        self.text = text
    
    async def check(self, driver: Any) -> bool:
        """检查文本是否出现"""
        try:
            content = await driver._current_page.content()
            return self.text in content
        except:
            return False


class NetworkIdleCondition(WaitCondition):
    """等待网络空闲（无未完成的请求）"""
    
    def __init__(self, timeout: int = 30000, poll_interval: int = 100):
        super().__init__(timeout, poll_interval)
        self._pending_requests = set()
    
    async def check(self, driver: Any) -> bool:
        """检查网络是否空闲"""
        # Playwright的wait_for_load_state已经支持networkidle
        # 这里可以检查是否有pending请求
        try:
            # 使用Playwright的networkidle状态
            await driver._current_page.wait_for_load_state("networkidle", timeout=100)
            return True
        except:
            return False


class CustomCondition(WaitCondition):
    """自定义条件"""
    
    def __init__(
        self,
        check_func: Callable[[Any], bool],
        timeout: int = 30000,
        poll_interval: int = 100
    ):
        super().__init__(timeout, poll_interval)
        self.check_func = check_func
    
    async def check(self, driver: Any) -> bool:
        """执行自定义检查函数"""
        try:
            if asyncio.iscoroutinefunction(self.check_func):
                return await self.check_func(driver)
            else:
                return self.check_func(driver)
        except Exception as e:
            logger.debug(f"Custom condition check failed: {e}")
            return False


class SmartWait(Action):
    """
    智能等待操作 - 等待特定条件满足
    """
    
    def __init__(
        self,
        condition: WaitCondition,
        description: Optional[str] = None
    ):
        """
        初始化智能等待
        
        Args:
            condition: 等待条件
            description: 条件描述（用于日志）
        """
        from .types import ActionType
        super().__init__(ActionType.WAIT, condition=condition, description=description)
        self.condition = condition
        self.description = description or f"Wait for condition (timeout={condition.timeout}ms)"
    
    def validate(self) -> bool:
        """验证条件参数"""
        return self.condition is not None
    
    async def execute(self, driver: Driver) -> Any:
        """执行智能等待"""
        if not self.validate():
            raise ValueError("Invalid wait condition")
        
        logger.info(f"Smart wait: {self.description}")
        success = await self.condition.wait(driver)
        if not success:
            raise TimeoutError(f"Wait condition timeout: {self.description}")
        
        return {"success": True, "condition": self.description}


# 便捷函数
def wait_for_element_visible(selector: str, timeout: int = 30000) -> SmartWait:
    """等待元素可见"""
    condition = ElementVisibleCondition(selector, timeout)
    return SmartWait(condition, f"Wait for element visible: {selector}")


def wait_for_element_not_visible(selector: str, timeout: int = 30000) -> SmartWait:
    """等待元素不可见"""
    condition = ElementNotVisibleCondition(selector, timeout)
    return SmartWait(condition, f"Wait for element not visible: {selector}")


def wait_for_text(text: str, timeout: int = 30000) -> SmartWait:
    """等待文本出现"""
    condition = TextPresentCondition(text, timeout)
    return SmartWait(condition, f"Wait for text: {text}")


def wait_for_network_idle(timeout: int = 30000) -> SmartWait:
    """等待网络空闲"""
    condition = NetworkIdleCondition(timeout)
    return SmartWait(condition, "Wait for network idle")


def wait_for_custom(
    check_func: Callable[[Any], bool],
    description: str,
    timeout: int = 30000
) -> SmartWait:
    """等待自定义条件"""
    condition = CustomCondition(check_func, timeout)
    return SmartWait(condition, description)
