"""
浏览器实例池 - 管理浏览器实例的并发执行
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import uuid
from enum import Enum

from ..drivers.browser_driver import BrowserDriver
from ..core.types import BrowserType


class BrowserInstanceState(Enum):
    """浏览器实例状态"""
    IDLE = "idle"        # 空闲
    BUSY = "busy"        # 忙碌
    CLOSED = "closed"    # 已关闭


class BrowserInstance:
    """
    浏览器实例 - 封装单个浏览器实例
    """
    
    def __init__(
        self,
        instance_id: str,
        driver: BrowserDriver,
        browser_type: BrowserType = BrowserType.CHROMIUM
    ):
        self.id = instance_id
        self.driver = driver
        self.browser_type = browser_type
        self.state = BrowserInstanceState.IDLE
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.usage_count = 0
        
    def mark_busy(self) -> None:
        """标记为忙碌"""
        self.state = BrowserInstanceState.BUSY
        self.last_used = datetime.now()
        self.usage_count += 1
        
    def mark_idle(self) -> None:
        """标记为空闲"""
        self.state = BrowserInstanceState.IDLE
        self.last_used = datetime.now()
        
    def mark_closed(self) -> None:
        """标记为已关闭"""
        self.state = BrowserInstanceState.CLOSED
        
    def is_idle(self) -> bool:
        """是否空闲"""
        return self.state == BrowserInstanceState.IDLE
        
    def is_busy(self) -> bool:
        """是否忙碌"""
        return self.state == BrowserInstanceState.BUSY
        
    def get_idle_time(self) -> float:
        """获取空闲时间（秒）"""
        if self.state == BrowserInstanceState.IDLE:
            return (datetime.now() - self.last_used).total_seconds()
        return 0.0


class BrowserPool:
    """
    浏览器实例池 - 管理多个浏览器实例的并发执行
    """
    
    def __init__(
        self,
        pool_size: int = 5,
        max_idle_time: int = 300,  # 最大空闲时间（秒）
        browser_type: BrowserType = BrowserType.CHROMIUM,
        headless: bool = True
    ):
        """
        初始化浏览器池
        
        Args:
            pool_size: 池大小
            max_idle_time: 最大空闲时间（秒）
            browser_type: 浏览器类型
            headless: 是否无头模式
        """
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.browser_type = browser_type
        self.headless = headless
        
        self._instances: Dict[str, BrowserInstance] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """启动浏览器池"""
        # 启动清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def stop(self) -> None:
        """停止浏览器池"""
        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 关闭所有实例
        for instance in list(self._instances.values()):
            await self._close_instance(instance)
        
    async def acquire_browser(
        self,
        timeout: float = 30.0
    ) -> Optional[BrowserInstance]:
        """
        获取浏览器实例
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            浏览器实例，如果超时返回None
        """
        start_time = datetime.now()
        
        while True:
            async with self._lock:
                # 查找空闲实例
                for instance in self._instances.values():
                    if instance.is_idle():
                        instance.mark_busy()
                        return instance
                
                # 如果池未满，创建新实例
                if len(self._instances) < self.pool_size:
                    instance = await self._create_instance()
                    if instance:
                        instance.mark_busy()
                        return instance
            
            # 检查超时
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= timeout:
                return None
            
            # 等待一段时间后重试
            await asyncio.sleep(0.1)
            
    async def release_browser(self, instance: BrowserInstance) -> None:
        """
        释放浏览器实例
        
        Args:
            instance: 浏览器实例
        """
        async with self._lock:
            if instance.id in self._instances:
                instance.mark_idle()
                
    async def _create_instance(self) -> Optional[BrowserInstance]:
        """创建新的浏览器实例"""
        try:
            instance_id = str(uuid.uuid4())
            driver = BrowserDriver(
                browser_type=self.browser_type,
                headless=self.headless
            )
            await driver.start()
            
            instance = BrowserInstance(
                instance_id=instance_id,
                driver=driver,
                browser_type=self.browser_type
            )
            self._instances[instance_id] = instance
            return instance
            
        except Exception as e:
            print(f"Failed to create browser instance: {e}")
            return None
            
    async def _close_instance(self, instance: BrowserInstance) -> None:
        """关闭浏览器实例"""
        try:
            await instance.driver.stop()
            instance.mark_closed()
            if instance.id in self._instances:
                del self._instances[instance.id]
        except Exception as e:
            print(f"Failed to close browser instance: {e}")
            
    async def _cleanup_loop(self) -> None:
        """清理循环 - 定期清理空闲实例"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                await self._cleanup_idle_instances()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup error: {e}")
                
    async def _cleanup_idle_instances(self) -> None:
        """清理空闲实例"""
        async with self._lock:
            instances_to_close = []
            
            for instance in self._instances.values():
                if instance.is_idle():
                    idle_time = instance.get_idle_time()
                    if idle_time > self.max_idle_time:
                        instances_to_close.append(instance)
            
            # 关闭空闲实例
            for instance in instances_to_close:
                await self._close_instance(instance)
                
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._instances)
        idle = len([i for i in self._instances.values() if i.is_idle()])
        busy = len([i for i in self._instances.values() if i.is_busy()])
        
        return {
            "total": total,
            "idle": idle,
            "busy": busy,
            "pool_size": self.pool_size,
            "utilization": busy / self.pool_size if self.pool_size > 0 else 0.0,
        }


# 全局浏览器池实例
_global_browser_pool: Optional[BrowserPool] = None


def get_global_browser_pool() -> BrowserPool:
    """获取全局浏览器池"""
    global _global_browser_pool
    if _global_browser_pool is None:
        _global_browser_pool = BrowserPool()
    return _global_browser_pool
