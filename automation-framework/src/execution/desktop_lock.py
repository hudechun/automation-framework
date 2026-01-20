"""
桌面操作互斥锁和队列管理 - 确保桌面任务串行执行
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import uuid
from enum import Enum


class DesktopLock:
    """
    桌面操作互斥锁 - 全局互斥锁，确保同一时间只有一个桌面任务执行
    """
    
    def __init__(self, timeout: float = 300.0):
        """
        初始化桌面锁
        
        Args:
            timeout: 锁超时时间（秒）
        """
        self._lock = asyncio.Lock()
        self._timeout = timeout
        self._holder: Optional[str] = None
        self._acquired_at: Optional[datetime] = None
        
    async def acquire_lock(
        self,
        task_id: str,
        timeout: Optional[float] = None
    ) -> bool:
        """
        获取锁
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒），如果为None则使用默认超时
            
        Returns:
            是否成功获取锁
        """
        timeout = timeout or self._timeout
        
        try:
            await asyncio.wait_for(
                self._lock.acquire(),
                timeout=timeout
            )
            self._holder = task_id
            self._acquired_at = datetime.now()
            return True
        except asyncio.TimeoutError:
            return False
            
    async def release_lock(self, task_id: str) -> bool:
        """
        释放锁
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功释放锁
        """
        if self._holder == task_id:
            self._holder = None
            self._acquired_at = None
            self._lock.release()
            return True
        return False
        
    def force_release(self) -> None:
        """强制释放锁"""
        if self._lock.locked():
            self._holder = None
            self._acquired_at = None
            self._lock.release()
            
    def is_locked(self) -> bool:
        """是否已锁定"""
        return self._lock.locked()
        
    def get_holder(self) -> Optional[str]:
        """获取锁持有者"""
        return self._holder
        
    def get_lock_duration(self) -> float:
        """获取锁持有时长（秒）"""
        if self._acquired_at:
            return (datetime.now() - self._acquired_at).total_seconds()
        return 0.0
        
    def check_timeout(self) -> bool:
        """检查是否超时"""
        if self.is_locked():
            duration = self.get_lock_duration()
            return duration > self._timeout
        return False


class TaskQueueItem:
    """队列任务项"""
    
    def __init__(
        self,
        task_id: str,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.priority = priority
        self.metadata = metadata or {}
        self.enqueued_at = datetime.now()
        
    def get_wait_time(self) -> float:
        """获取等待时间（秒）"""
        return (datetime.now() - self.enqueued_at).total_seconds()


class DesktopQueue:
    """
    桌面任务队列 - 管理等待执行的桌面任务
    """
    
    def __init__(self):
        self._queue: List[TaskQueueItem] = []
        self._lock = asyncio.Lock()
        
    async def enqueue(
        self,
        task_id: str,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加任务到队列
        
        Args:
            task_id: 任务ID
            priority: 优先级（数字越大优先级越高）
            metadata: 元数据
        """
        async with self._lock:
            item = TaskQueueItem(task_id, priority, metadata)
            self._queue.append(item)
            # 按优先级排序（优先级高的在前）
            self._queue.sort(key=lambda x: (-x.priority, x.enqueued_at))
            
    async def dequeue(self) -> Optional[TaskQueueItem]:
        """
        从队列取出任务
        
        Returns:
            队列任务项，如果队列为空返回None
        """
        async with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None
            
    async def peek(self) -> Optional[TaskQueueItem]:
        """
        查看队列头部任务（不移除）
        
        Returns:
            队列任务项，如果队列为空返回None
        """
        async with self._lock:
            if self._queue:
                return self._queue[0]
            return None
            
    async def remove(self, task_id: str) -> bool:
        """
        从队列移除指定任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功移除
        """
        async with self._lock:
            for i, item in enumerate(self._queue):
                if item.task_id == task_id:
                    self._queue.pop(i)
                    return True
            return False
            
    async def clear(self) -> None:
        """清空队列"""
        async with self._lock:
            self._queue.clear()
            
    def queue_status(self) -> Dict[str, Any]:
        """
        获取队列状态
        
        Returns:
            队列状态信息
        """
        total = len(self._queue)
        
        if total == 0:
            return {
                "total": 0,
                "next_task": None,
                "avg_wait_time": 0.0,
            }
        
        # 计算平均等待时间
        wait_times = [item.get_wait_time() for item in self._queue]
        avg_wait_time = sum(wait_times) / len(wait_times)
        
        # 获取下一个任务
        next_task = self._queue[0] if self._queue else None
        
        return {
            "total": total,
            "next_task": {
                "task_id": next_task.task_id,
                "priority": next_task.priority,
                "wait_time": next_task.get_wait_time(),
            } if next_task else None,
            "avg_wait_time": avg_wait_time,
        }
        
    def get_position(self, task_id: str) -> Optional[int]:
        """
        获取任务在队列中的位置
        
        Args:
            task_id: 任务ID
            
        Returns:
            位置（从0开始），如果不在队列中返回None
        """
        for i, item in enumerate(self._queue):
            if item.task_id == task_id:
                return i
        return None


class DesktopExecutor:
    """
    桌面任务执行器 - 结合锁和队列管理桌面任务的串行执行
    """
    
    def __init__(self):
        self.lock = DesktopLock()
        self.queue = DesktopQueue()
        self._running = False
        self._executor_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """启动执行器"""
        if not self._running:
            self._running = True
            self._executor_task = asyncio.create_task(self._execution_loop())
            
    async def stop(self) -> None:
        """停止执行器"""
        self._running = False
        if self._executor_task:
            self._executor_task.cancel()
            try:
                await self._executor_task
            except asyncio.CancelledError:
                pass
            
    async def submit_task(
        self,
        task_id: str,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        提交任务
        
        Args:
            task_id: 任务ID
            priority: 优先级
            metadata: 元数据
        """
        await self.queue.enqueue(task_id, priority, metadata)
        
    async def _execution_loop(self) -> None:
        """执行循环"""
        while self._running:
            try:
                # 从队列获取任务
                item = await self.queue.dequeue()
                if not item:
                    await asyncio.sleep(0.1)
                    continue
                
                # 获取锁
                acquired = await self.lock.acquire_lock(item.task_id)
                if not acquired:
                    # 获取锁失败，重新入队
                    await self.queue.enqueue(
                        item.task_id,
                        item.priority,
                        item.metadata
                    )
                    await asyncio.sleep(1)
                    continue
                
                # 执行任务（这里需要实际的任务执行逻辑）
                # TODO: 调用实际的任务执行函数
                
                # 释放锁
                await self.lock.release_lock(item.task_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Execution error: {e}")
                await asyncio.sleep(1)


# 全局桌面锁和队列实例
_global_desktop_lock: Optional[DesktopLock] = None
_global_desktop_queue: Optional[DesktopQueue] = None
_global_desktop_executor: Optional[DesktopExecutor] = None


def get_global_desktop_lock() -> DesktopLock:
    """获取全局桌面锁"""
    global _global_desktop_lock
    if _global_desktop_lock is None:
        _global_desktop_lock = DesktopLock()
    return _global_desktop_lock


def get_global_desktop_queue() -> DesktopQueue:
    """获取全局桌面队列"""
    global _global_desktop_queue
    if _global_desktop_queue is None:
        _global_desktop_queue = DesktopQueue()
    return _global_desktop_queue


def get_global_desktop_executor() -> DesktopExecutor:
    """获取全局桌面执行器"""
    global _global_desktop_executor
    if _global_desktop_executor is None:
        _global_desktop_executor = DesktopExecutor()
    return _global_desktop_executor
