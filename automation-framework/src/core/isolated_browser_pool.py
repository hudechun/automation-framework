"""
隔离的浏览器实例池 - 为每个用户提供独立的浏览器实例池
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from ..execution.browser_pool import BrowserPool, BrowserInstance
from ..core.types import BrowserType

logger = logging.getLogger(__name__)


class IsolatedBrowserPool:
    """
    隔离的浏览器实例池 - 确保每个用户使用独立的浏览器实例
    """
    
    def __init__(
        self,
        max_pool_size_per_user: int = 3,
        max_idle_time: int = 300,
        browser_type: BrowserType = BrowserType.CHROMIUM,
        headless: bool = True
    ):
        """
        初始化隔离的浏览器池
        
        Args:
            max_pool_size_per_user: 每个用户的最大浏览器实例数
            max_idle_time: 最大空闲时间（秒）
            browser_type: 浏览器类型
            headless: 是否无头模式
        """
        self._max_pool_size_per_user = max_pool_size_per_user
        self._max_idle_time = max_idle_time
        self._browser_type = browser_type
        self._headless = headless
        
        # 用户池映射: user_id -> BrowserPool
        self._pools: Dict[int, BrowserPool] = {}
        
        # 任务实例映射: (user_id, task_id) -> BrowserInstance
        self._task_instances: Dict[tuple, BrowserInstance] = {}
        
        # 锁
        self._lock = asyncio.Lock()
    
    async def get_browser(
        self,
        user_id: int,
        task_id: str,
        timeout: float = 30.0
    ) -> Optional[BrowserInstance]:
        """
        获取浏览器实例（用户隔离）
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            浏览器实例
        """
        async with self._lock:
            # 检查是否已有实例
            key = (user_id, task_id)
            if key in self._task_instances:
                instance = self._task_instances[key]
                if instance.is_idle():
                    instance.mark_busy()
                    return instance
            
            # 获取或创建用户池
            if user_id not in self._pools:
                self._pools[user_id] = BrowserPool(
                    pool_size=self._max_pool_size_per_user,
                    max_idle_time=self._max_idle_time,
                    browser_type=self._browser_type,
                    headless=self._headless
                )
                await self._pools[user_id].start()
                logger.info(f"Created browser pool for user {user_id}")
            
            pool = self._pools[user_id]
            instance = await pool.acquire_browser(timeout=timeout)
            
            if instance:
                # 为任务创建独立的浏览器上下文
                context = await instance.driver.create_context(
                    task_id=task_id,
                    user_id=user_id
                )
                # 记录任务实例关联
                self._task_instances[key] = instance
                logger.info(f"Acquired browser instance for user {user_id}, task {task_id}")
            
            return instance
    
    async def release_browser(
        self,
        user_id: int,
        task_id: str
    ) -> None:
        """
        释放浏览器实例
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
        """
        async with self._lock:
            key = (user_id, task_id)
            if key in self._task_instances:
                instance = self._task_instances[key]
                
                # 关闭任务专用的浏览器上下文
                if hasattr(instance.driver, 'close_context'):
                    await instance.driver.close_context(task_id)
                
                # 释放到池中
                if user_id in self._pools:
                    await self._pools[user_id].release_browser(instance)
                
                # 移除任务实例关联
                del self._task_instances[key]
                logger.info(f"Released browser instance for user {user_id}, task {task_id}")
    
    async def cleanup_user_pool(self, user_id: int) -> None:
        """
        清理用户的浏览器池（用户退出或长时间不使用时）
        
        Args:
            user_id: 用户ID
        """
        async with self._lock:
            if user_id in self._pools:
                pool = self._pools[user_id]
                await pool.stop()
                del self._pools[user_id]
                
                # 清理相关的任务实例
                keys_to_remove = [
                    key for key in self._task_instances.keys()
                    if key[0] == user_id
                ]
                for key in keys_to_remove:
                    del self._task_instances[key]
                
                logger.info(f"Cleaned up browser pool for user {user_id}")
    
    async def stop_all(self) -> None:
        """停止所有浏览器池"""
        async with self._lock:
            for user_id, pool in list(self._pools.items()):
                await pool.stop()
            self._pools.clear()
            self._task_instances.clear()
            logger.info("All browser pools stopped")


# 全局隔离浏览器池实例
_global_isolated_pool: Optional[IsolatedBrowserPool] = None


def get_global_isolated_pool() -> IsolatedBrowserPool:
    """获取全局隔离浏览器池"""
    global _global_isolated_pool
    if _global_isolated_pool is None:
        _global_isolated_pool = IsolatedBrowserPool()
    return _global_isolated_pool
