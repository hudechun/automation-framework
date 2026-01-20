"""
并发执行模块
"""
from .classifier import TaskClassifier, TaskType
from .browser_pool import BrowserPool, BrowserInstance
from .desktop_lock import DesktopLock, DesktopQueue

__all__ = [
    # 任务分类
    "TaskClassifier",
    "TaskType",
    # 浏览器池
    "BrowserPool",
    "BrowserInstance",
    # 桌面锁
    "DesktopLock",
    "DesktopQueue",
]
