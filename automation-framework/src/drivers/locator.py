"""
智能元素定位策略实现
"""
from typing import Optional, List, Dict, Any
from enum import Enum
import logging
from playwright.async_api import Page, Locator, ElementHandle


logger = logging.getLogger(__name__)


class LocatorStrategy(str, Enum):
    """定位策略枚举"""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ACCESSIBILITY = "accessibility"


class ElementLocator:
    """智能元素定位器"""
    
    def __init__(self, page: Page):
        """
        初始化定位器
        
        Args:
            page: Playwright页面对象
        """
        self.page = page
        self.strategy_priority = [
            LocatorStrategy.CSS,
            LocatorStrategy.XPATH,
            LocatorStrategy.TEXT,
            LocatorStrategy.ACCESSIBILITY,
        ]
    
    async def locate(
        self,
        selector: str,
        timeout: int = 30000,
        auto_fallback: bool = True
    ) -> Optional[Locator]:
        """
        智能定位元素
        
        Args:
            selector: 选择器字符串
            timeout: 超时时间（毫秒）
            auto_fallback: 是否自动降级尝试其他策略
            
        Returns:
            定位到的元素，失败返回None
        """
        # 首先尝试直接使用选择器
        try:
            locator = self.page.locator(selector)
            await locator.wait_for(timeout=timeout)
            return locator
        except Exception as e:
            logger.debug(f"Direct selector failed: {selector}, error: {e}")
        
        if not auto_fallback:
            return None
        
        # 自动降级：尝试不同的定位策略
        for strategy in self.strategy_priority:
            try:
                locator = await self._locate_with_strategy(
                    selector,
                    strategy,
                    timeout
                )
                if locator:
                    logger.info(f"Located element using {strategy} strategy")
                    return locator
            except Exception as e:
                logger.debug(f"Strategy {strategy} failed: {e}")
                continue
        
        logger.error(f"Failed to locate element with selector: {selector}")
        return None
    
    async def _locate_with_strategy(
        self,
        selector: str,
        strategy: LocatorStrategy,
        timeout: int
    ) -> Optional[Locator]:
        """
        使用指定策略定位元素
        
        Args:
            selector: 选择器
            strategy: 定位策略
            timeout: 超时时间
            
        Returns:
            定位到的元素
        """
        if strategy == LocatorStrategy.CSS:
            return await self._locate_by_css(selector, timeout)
        elif strategy == LocatorStrategy.XPATH:
            return await self._locate_by_xpath(selector, timeout)
        elif strategy == LocatorStrategy.TEXT:
            return await self._locate_by_text(selector, timeout)
        elif strategy == LocatorStrategy.ACCESSIBILITY:
            return await self._locate_by_accessibility(selector, timeout)
        return None
    
    async def _locate_by_css(
        self,
        selector: str,
        timeout: int
    ) -> Optional[Locator]:
        """
        使用CSS选择器定位
        
        Args:
            selector: CSS选择器
            timeout: 超时时间
            
        Returns:
            定位到的元素
        """
        try:
            locator = self.page.locator(f"css={selector}")
            await locator.wait_for(timeout=timeout)
            return locator
        except:
            return None
    
    async def _locate_by_xpath(
        self,
        selector: str,
        timeout: int
    ) -> Optional[Locator]:
        """
        使用XPath定位
        
        Args:
            selector: XPath表达式
            timeout: 超时时间
            
        Returns:
            定位到的元素
        """
        try:
            # 如果不是以//或/开头，尝试添加//
            if not selector.startswith(('/', '//')):
                selector = f"//{selector}"
            
            locator = self.page.locator(f"xpath={selector}")
            await locator.wait_for(timeout=timeout)
            return locator
        except:
            return None
    
    async def _locate_by_text(
        self,
        text: str,
        timeout: int
    ) -> Optional[Locator]:
        """
        使用文本内容定位
        
        Args:
            text: 文本内容
            timeout: 超时时间
            
        Returns:
            定位到的元素
        """
        try:
            # 尝试精确匹配
            locator = self.page.locator(f"text={text}")
            await locator.wait_for(timeout=timeout)
            return locator
        except:
            pass
        
        try:
            # 尝试包含匹配
            locator = self.page.locator(f"text=/{text}/i")
            await locator.wait_for(timeout=timeout)
            return locator
        except:
            return None
    
    async def _locate_by_accessibility(
        self,
        selector: str,
        timeout: int
    ) -> Optional[Locator]:
        """
        使用Accessibility属性定位
        
        Args:
            selector: 属性值
            timeout: 超时时间
            
        Returns:
            定位到的元素
        """
        # 尝试常见的accessibility属性
        attributes = [
            f"[role='{selector}']",
            f"[aria-label='{selector}']",
            f"[aria-labelledby='{selector}']",
            f"[title='{selector}']",
        ]
        
        for attr in attributes:
            try:
                locator = self.page.locator(attr)
                await locator.wait_for(timeout=timeout)
                return locator
            except:
                continue
        
        return None
    
    async def locate_all(
        self,
        selector: str,
        timeout: int = 30000
    ) -> List[Locator]:
        """
        定位所有匹配的元素
        
        Args:
            selector: 选择器
            timeout: 超时时间
            
        Returns:
            元素列表
        """
        try:
            locator = self.page.locator(selector)
            await locator.first.wait_for(timeout=timeout)
            count = await locator.count()
            return [locator.nth(i) for i in range(count)]
        except:
            return []
    
    def set_strategy_priority(self, strategies: List[LocatorStrategy]) -> None:
        """
        设置定位策略优先级
        
        Args:
            strategies: 策略列表（按优先级排序）
        """
        self.strategy_priority = strategies


class LocatorWithRetry:
    """带重试机制的定位器"""
    
    def __init__(
        self,
        locator: ElementLocator,
        max_retries: int = 3,
        retry_delay: int = 1000
    ):
        """
        初始化重试定位器
        
        Args:
            locator: 元素定位器
            max_retries: 最大重试次数
            retry_delay: 重试延迟（毫秒）
        """
        self.locator = locator
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def locate(
        self,
        selector: str,
        timeout: int = 30000
    ) -> Optional[Locator]:
        """
        带重试的元素定位
        
        Args:
            selector: 选择器
            timeout: 超时时间
            
        Returns:
            定位到的元素
        """
        import asyncio
        
        for attempt in range(self.max_retries):
            try:
                element = await self.locator.locate(selector, timeout)
                if element:
                    return element
            except Exception as e:
                logger.debug(f"Locate attempt {attempt + 1} failed: {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay / 1000)
        
        logger.error(f"Failed to locate element after {self.max_retries} attempts")
        return None
