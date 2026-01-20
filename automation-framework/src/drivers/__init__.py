"""
驱动模块 - 提供浏览器和桌面驱动实现
"""
from .browser_driver import BrowserDriver
from .locator import ElementLocator, LocatorWithRetry, LocatorStrategy
from .browser_advanced import (
    FormFiller,
    DynamicContentHandler,
    TabWindowManager,
    SessionManager,
)
from .desktop_driver import DesktopDriver, UIElement, get_platform, create_driver
from .windows_driver import WindowsDriver
from .macos_driver import MacOSDriver
from .linux_driver import LinuxDriver

__all__ = [
    "BrowserDriver",
    "ElementLocator",
    "LocatorWithRetry",
    "LocatorStrategy",
    "FormFiller",
    "DynamicContentHandler",
    "TabWindowManager",
    "SessionManager",
    "DesktopDriver",
    "UIElement",
    "get_platform",
    "create_driver",
    "WindowsDriver",
    "MacOSDriver",
    "LinuxDriver",
]
