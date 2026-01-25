"""
反检测和验证码处理
"""
import random
import logging
from typing import Optional, Dict, Any, List
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger(__name__)


class UserAgentRotator:
    """User-Agent轮换器"""
    
    # 常见User-Agent列表
    USER_AGENTS = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """获取随机User-Agent"""
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def get_user_agent_by_browser(cls, browser: str = "chrome") -> str:
        """根据浏览器类型获取User-Agent"""
        browser_lower = browser.lower()
        if "chrome" in browser_lower:
            return cls.USER_AGENTS[0]  # Chrome
        elif "firefox" in browser_lower:
            return cls.USER_AGENTS[3]  # Firefox
        elif "safari" in browser_lower:
            return cls.USER_AGENTS[4]  # Safari
        else:
            return cls.get_random_user_agent()


class AntiDetectionConfig:
    """反检测配置"""
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        locale: Optional[str] = None,
        timezone: Optional[str] = None,
        geolocation: Optional[Dict[str, float]] = None,
        permissions: Optional[List[str]] = None,
        extra_http_headers: Optional[Dict[str, str]] = None,
        ignore_https_errors: bool = False,
        java_script_enabled: bool = True,
        bypass_csp: bool = False
    ):
        """
        初始化反检测配置
        
        Args:
            user_agent: 自定义User-Agent
            viewport: 视口大小
            locale: 语言环境
            timezone: 时区
            geolocation: 地理位置
            permissions: 权限列表
            extra_http_headers: 额外的HTTP头
            ignore_https_errors: 是否忽略HTTPS错误
            java_script_enabled: 是否启用JavaScript
            bypass_csp: 是否绕过CSP
        """
        self.user_agent = user_agent or UserAgentRotator.get_random_user_agent()
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.locale = locale or "en-US"
        self.timezone = timezone or "America/New_York"
        self.geolocation = geolocation
        self.permissions = permissions or []
        self.extra_http_headers = extra_http_headers or {}
        self.ignore_https_errors = ignore_https_errors
        self.java_script_enabled = java_script_enabled
        self.bypass_csp = bypass_csp
    
    def apply_to_context(self, context: BrowserContext) -> None:
        """将配置应用到浏览器上下文"""
        # 注意：这些设置需要在创建context时设置，这里只是示例
        pass
    
    def to_context_options(self) -> Dict[str, Any]:
        """转换为Playwright上下文选项"""
        options = {
            "viewport": self.viewport,
            "locale": self.locale,
            "timezone_id": self.timezone,
            "user_agent": self.user_agent,
            "ignore_https_errors": self.ignore_https_errors,
            "java_script_enabled": self.java_script_enabled,
            "bypass_csp": self.bypass_csp,
        }
        
        if self.geolocation:
            options["geolocation"] = self.geolocation
        
        if self.permissions:
            options["permissions"] = self.permissions
        
        if self.extra_http_headers:
            options["extra_http_headers"] = self.extra_http_headers
        
        return options


class CaptchaHandler:
    """验证码处理器"""
    
    def __init__(
        self,
        ocr_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        manual_fallback: bool = True
    ):
        """
        初始化验证码处理器
        
        Args:
            ocr_provider: OCR服务提供商（如"tesseract", "baidu", "aliyun"）
            api_key: API密钥
            manual_fallback: 是否支持人工介入
        """
        self.ocr_provider = ocr_provider
        self.api_key = api_key
        self.manual_fallback = manual_fallback
    
    async def detect_captcha(self, page: Page) -> bool:
        """
        检测页面是否有验证码
        
        Args:
            page: Playwright Page对象
            
        Returns:
            是否检测到验证码
        """
        # 常见的验证码选择器
        captcha_selectors = [
            "img[alt*='验证码']",
            "img[alt*='captcha']",
            ".captcha",
            "#captcha",
            "[class*='captcha']",
            "[id*='captcha']",
        ]
        
        for selector in captcha_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.warning(f"Captcha detected: {selector}")
                        return True
            except:
                continue
        
        return False
    
    async def solve_captcha(
        self,
        page: Page,
        selector: Optional[str] = None
    ) -> Optional[str]:
        """
        解决验证码
        
        Args:
            page: Playwright Page对象
            selector: 验证码图片选择器
            
        Returns:
            验证码文本，如果失败返回None
        """
        if not selector:
            # 自动查找验证码图片
            captcha_selectors = [
                "img[alt*='验证码']",
                "img[alt*='captcha']",
                ".captcha img",
                "#captcha img",
            ]
            
            for sel in captcha_selectors:
                element = await page.query_selector(sel)
                if element:
                    selector = sel
                    break
        
        if not selector:
            logger.error("Captcha image not found")
            return None
        
        try:
            # 截图验证码
            captcha_element = await page.query_selector(selector)
            if not captcha_element:
                return None
            
            # 获取验证码图片（可以保存为文件或直接处理）
            # 这里简化处理，实际需要调用OCR服务
            
            if self.manual_fallback:
                # 人工介入：等待用户输入
                logger.info("Waiting for manual captcha input...")
                # 这里可以触发一个事件，通知前端需要人工输入验证码
                # 实际实现需要与前端交互
                return None
            
            # 使用OCR识别
            if self.ocr_provider:
                return await self._ocr_recognize(captcha_element)
            
            return None
        except Exception as e:
            logger.error(f"Failed to solve captcha: {e}")
            return None
    
    async def _ocr_recognize(self, element) -> Optional[str]:
        """使用OCR识别验证码"""
        # 这里需要集成OCR服务
        # 示例：可以调用百度OCR、阿里云OCR等
        logger.warning("OCR recognition not implemented yet")
        return None


class ProxyConfig:
    """代理配置"""
    
    def __init__(
        self,
        server: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        初始化代理配置
        
        Args:
            server: 代理服务器地址（如 "http://proxy.example.com:8080"）
            username: 代理用户名
            password: 代理密码
        """
        self.server = server
        self.username = username
        self.password = password
    
    def to_playwright_proxy(self) -> Dict[str, Any]:
        """转换为Playwright代理配置"""
        proxy = {
            "server": self.server
        }
        
        if self.username and self.password:
            proxy["username"] = self.username
            proxy["password"] = self.password
        
        return proxy
