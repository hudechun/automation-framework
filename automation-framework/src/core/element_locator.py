"""
元素定位器 - 支持多种定位策略
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class LocatorType(str, Enum):
    """定位策略类型"""
    CSS = "css"  # CSS选择器
    XPATH = "xpath"  # XPath表达式
    TEXT = "text"  # 文本匹配
    ID = "id"  # 元素ID
    NAME = "name"  # 元素name属性
    CLASS = "class"  # 元素class属性
    ATTRIBUTE = "attribute"  # 属性匹配
    ROLE = "role"  # ARIA角色
    LABEL = "label"  # 标签文本


class ElementLocator:
    """
    元素定位器 - 支持多种定位策略
    """
    
    def __init__(
        self,
        selector: str,
        locator_type: Optional[LocatorType] = None,
        timeout: int = 30000,
        **kwargs
    ):
        """
        初始化元素定位器
        
        Args:
            selector: 选择器或定位值
            locator_type: 定位策略类型（如果为None，自动推断）
            timeout: 超时时间（毫秒）
            **kwargs: 额外参数（如attribute_name用于属性定位）
        """
        self.selector = selector
        self.locator_type = locator_type or self._infer_locator_type(selector)
        self.timeout = timeout
        self.kwargs = kwargs
    
    def _infer_locator_type(self, selector: str) -> LocatorType:
        """
        自动推断定位策略类型
        
        Args:
            selector: 选择器字符串
            
        Returns:
            定位策略类型
        """
        # XPath通常以 / 或 // 开头
        if selector.startswith(('/', '//', './', './/')):
            return LocatorType.XPATH
        
        # ID选择器以 # 开头
        if selector.startswith('#'):
            return LocatorType.CSS
        
        # 如果包含 :: 或包含复杂的XPath语法，可能是XPath
        if '::' in selector or selector.startswith('('):
            return LocatorType.XPATH
        
        # 默认使用CSS选择器
        return LocatorType.CSS
    
    def to_playwright_locator(self, page) -> Any:
        """
        转换为Playwright定位器
        
        Args:
            page: Playwright Page对象
            
        Returns:
            Playwright Locator对象
        """
        if self.locator_type == LocatorType.CSS:
            return page.locator(self.selector)
        elif self.locator_type == LocatorType.XPATH:
            return page.locator(f"xpath={self.selector}")
        elif self.locator_type == LocatorType.TEXT:
            # 文本匹配：精确匹配或包含匹配
            exact = self.kwargs.get('exact', False)
            if exact:
                return page.get_by_text(self.selector, exact=True)
            else:
                return page.get_by_text(self.selector)
        elif self.locator_type == LocatorType.ID:
            return page.locator(f"#{self.selector}")
        elif self.locator_type == LocatorType.NAME:
            return page.locator(f"[name='{self.selector}']")
        elif self.locator_type == LocatorType.CLASS:
            return page.locator(f".{self.selector}")
        elif self.locator_type == LocatorType.ATTRIBUTE:
            # 属性匹配：selector是属性名，kwargs['value']是属性值
            attr_name = self.selector
            attr_value = self.kwargs.get('value', '')
            if attr_value:
                return page.locator(f"[{attr_name}='{attr_value}']")
            else:
                return page.locator(f"[{attr_name}]")
        elif self.locator_type == LocatorType.ROLE:
            # ARIA角色定位
            return page.get_by_role(self.selector)
        elif self.locator_type == LocatorType.LABEL:
            # 标签文本定位
            return page.get_by_label(self.selector)
        else:
            # 默认使用CSS选择器
            return page.locator(self.selector)
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "selector": self.selector,
            "locator_type": self.locator_type.value,
            "timeout": self.timeout,
            **self.kwargs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElementLocator":
        """从字典反序列化"""
        return cls(
            selector=data["selector"],
            locator_type=LocatorType(data.get("locator_type", "css")),
            timeout=data.get("timeout", 30000),
            **{k: v for k, v in data.items() if k not in ["selector", "locator_type", "timeout"]}
        )


class MultiLocatorStrategy:
    """
    多定位策略 - 按优先级尝试多种定位方式
    """
    
    def __init__(self, locators: List[ElementLocator]):
        """
        初始化多定位策略
        
        Args:
            locators: 定位器列表（按优先级排序）
        """
        self.locators = locators
    
    async def find_element(self, page, timeout: Optional[int] = None) -> Optional[Any]:
        """
        尝试多种定位策略查找元素
        
        Args:
            page: Playwright Page对象
            timeout: 总超时时间（如果为None，使用第一个定位器的超时时间）
            
        Returns:
            找到的元素，如果都失败返回None
        """
        if not self.locators:
            return None
        
        total_timeout = timeout or self.locators[0].timeout
        start_time = None
        
        for locator in self.locators:
            try:
                playwright_locator = locator.to_playwright_locator(page)
                element = await playwright_locator.first.wait_for(
                    state="visible",
                    timeout=min(locator.timeout, total_timeout)
                )
                if element:
                    logger.info(f"Element found using {locator.locator_type.value} strategy: {locator.selector}")
                    return element
            except Exception as e:
                logger.debug(f"Locator {locator.locator_type.value}:{locator.selector} failed: {e}")
                continue
        
        return None
