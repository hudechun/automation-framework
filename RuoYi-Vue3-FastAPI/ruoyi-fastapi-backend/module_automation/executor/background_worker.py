# -*- coding: utf-8 -*-
"""
后台工作线程 - 异步执行任务
"""
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """
    后台工作线程 - 负责异步执行任务
    """
    
    def __init__(self):
        """初始化工作线程"""
        self._tasks: Dict[int, asyncio.Task] = {}
        self._callbacks: Dict[int, Callable] = {}
        
    def submit_task(
        self,
        task_id: int,
        coroutine,
        callback: Optional[Callable] = None
    ) -> None:
        """
        提交任务到后台执行
        
        Args:
            task_id: 任务ID
            coroutine: 协程对象
            callback: 完成回调函数
        """
        # 创建异步任务
        task = asyncio.create_task(coroutine)
        self._tasks[task_id] = task
        
        if callback:
            self._callbacks[task_id] = callback
            # 添加完成回调
            task.add_done_callback(lambda t: self._on_task_complete(task_id, t))
        
        logger.info(f"任务 {task_id} 已提交到后台执行")
    
    def _on_task_complete(self, task_id: int, task: asyncio.Task) -> None:
        """
        任务完成回调
        
        Args:
            task_id: 任务ID
            task: 异步任务对象
        """
        try:
            # 获取任务结果
            result = task.result()
            
            # 调用用户回调
            if task_id in self._callbacks:
                callback = self._callbacks[task_id]
                callback(task_id, result, None)
                del self._callbacks[task_id]
            
            logger.info(f"任务 {task_id} 执行完成")
            
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {str(e)}")
            
            # 调用用户回调（传递错误）
            if task_id in self._callbacks:
                callback = self._callbacks[task_id]
                callback(task_id, None, e)
                del self._callbacks[task_id]
        
        finally:
            # 清理任务
            if task_id in self._tasks:
                del self._tasks[task_id]
    
    def cancel_task(self, task_id: int) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否取消成功
        """
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.cancel()
            del self._tasks[task_id]
            
            if task_id in self._callbacks:
                del self._callbacks[task_id]
            
            logger.info(f"任务 {task_id} 已取消")
            return True
        
        return False
    
    def is_task_running(self, task_id: int) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否正在运行
        """
        return task_id in self._tasks
    
    def get_running_tasks(self) -> list:
        """
        获取所有运行中的任务ID
        
        Returns:
            任务ID列表
        """
        return list(self._tasks.keys())


# 全局工作线程实例
_global_worker: Optional[BackgroundWorker] = None


def get_background_worker() -> BackgroundWorker:
    """获取全局后台工作线程实例"""
    global _global_worker
    if _global_worker is None:
        _global_worker = BackgroundWorker()
    return _global_worker
