"""
并发控制器 - 管理多用户环境下的任务并发执行
"""
import asyncio
import logging
from typing import Dict, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConcurrencyController:
    """
    并发控制器 - 管理用户级和全局级的并发限制
    """
    
    def __init__(
        self,
        max_concurrent_per_user: int = 5,
        max_global_concurrent: int = 100,
        task_timeout: int = 3600
    ):
        """
        初始化并发控制器
        
        Args:
            max_concurrent_per_user: 每个用户的最大并发任务数
            max_global_concurrent: 全局最大并发任务数
            task_timeout: 任务超时时间（秒）
        """
        self._max_concurrent_per_user = max_concurrent_per_user
        self._max_global_concurrent = max_global_concurrent
        self._task_timeout = task_timeout
        
        # 用户任务跟踪: user_id -> set of task_ids
        self._user_tasks: Dict[int, Set[str]] = defaultdict(set)
        
        # 任务状态跟踪: task_id -> (user_id, start_time, status)
        self._task_states: Dict[str, Tuple[int, datetime, str]] = {}
        
        # 锁
        self._lock = asyncio.Lock()
        
        # 清理任务
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """启动并发控制器"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("ConcurrencyController started")
    
    async def stop(self) -> None:
        """停止并发控制器"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("ConcurrencyController stopped")
    
    async def can_execute_task(
        self,
        user_id: int,
        task_id: str
    ) -> Tuple[bool, str]:
        """
        检查是否可以执行任务
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            
        Returns:
            (是否可以执行, 错误消息)
        """
        async with self._lock:
            # 检查全局并发限制
            running_count = sum(
                1 for status in self._task_states.values()
                if status[2] == 'running'
            )
            if running_count >= self._max_global_concurrent:
                return False, f"系统已达到最大并发任务数限制（{self._max_global_concurrent}）"
            
            # 检查用户并发限制
            user_tasks = self._user_tasks.get(user_id, set())
            running_user_tasks = [
                tid for tid in user_tasks
                if self._is_task_running(tid)
            ]
            
            if len(running_user_tasks) >= self._max_concurrent_per_user:
                return False, f"您已达到最大并发任务数限制（{self._max_concurrent_per_user}），请等待其他任务完成"
            
            # 检查任务是否已在运行
            if task_id in self._task_states:
                state = self._task_states[task_id]
                if state[2] in ['running', 'paused']:
                    return False, "任务已在运行中或已暂停"
            
            # 允许执行
            self._user_tasks[user_id].add(task_id)
            self._task_states[task_id] = (user_id, datetime.now(), 'running')
            return True, ""
    
    async def register_task(
        self,
        user_id: int,
        task_id: str,
        status: str = 'running'
    ) -> None:
        """
        注册任务（任务开始执行时调用）
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            status: 任务状态
        """
        async with self._lock:
            self._user_tasks[user_id].add(task_id)
            self._task_states[task_id] = (user_id, datetime.now(), status)
            logger.info(f"Task {task_id} registered for user {user_id}")
    
    async def update_task_status(
        self,
        task_id: str,
        status: str
    ) -> None:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
        """
        async with self._lock:
            if task_id in self._task_states:
                user_id, start_time, _ = self._task_states[task_id]
                self._task_states[task_id] = (user_id, start_time, status)
                logger.debug(f"Task {task_id} status updated to {status}")
    
    async def release_task(
        self,
        user_id: int,
        task_id: str
    ) -> None:
        """
        释放任务（任务完成或失败时调用）
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
        """
        async with self._lock:
            if user_id in self._user_tasks:
                self._user_tasks[user_id].discard(task_id)
            
            if task_id in self._task_states:
                del self._task_states[task_id]
            
            logger.info(f"Task {task_id} released for user {user_id}")
    
    def _is_task_running(self, task_id: str) -> bool:
        """检查任务是否正在运行"""
        if task_id not in self._task_states:
            return False
        _, _, status = self._task_states[task_id]
        return status == 'running'
    
    async def get_user_running_tasks(self, user_id: int) -> int:
        """
        获取用户正在运行的任务数
        
        Args:
            user_id: 用户ID
            
        Returns:
            正在运行的任务数
        """
        async with self._lock:
            user_tasks = self._user_tasks.get(user_id, set())
            return sum(
                1 for tid in user_tasks
                if self._is_task_running(tid)
            )
    
    async def get_global_running_tasks(self) -> int:
        """
        获取全局正在运行的任务数
        
        Returns:
            全局正在运行的任务数
        """
        async with self._lock:
            return sum(
                1 for status in self._task_states.values()
                if status[2] == 'running'
            )
    
    async def check_task_timeout(self) -> Set[str]:
        """
        检查超时的任务
        
        Returns:
            超时的任务ID集合
        """
        async with self._lock:
            timeout_tasks = set()
            now = datetime.now()
            
            for task_id, (user_id, start_time, status) in list(self._task_states.items()):
                if status == 'running':
                    elapsed = (now - start_time).total_seconds()
                    if elapsed > self._task_timeout:
                        timeout_tasks.add(task_id)
                        logger.warning(
                            f"Task {task_id} (user {user_id}) timeout after {elapsed}s"
                        )
            
            return timeout_tasks
    
    async def _cleanup_loop(self) -> None:
        """清理循环 - 定期清理超时任务"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                timeout_tasks = await self.check_task_timeout()
                
                for task_id in timeout_tasks:
                    if task_id in self._task_states:
                        user_id, _, _ = self._task_states[task_id]
                        await self.release_task(user_id, task_id)
                        logger.warning(f"Released timeout task {task_id}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")


# 全局并发控制器实例
_global_controller: Optional[ConcurrencyController] = None


def get_global_concurrency_controller() -> ConcurrencyController:
    """获取全局并发控制器"""
    global _global_controller
    if _global_controller is None:
        _global_controller = ConcurrencyController()
    return _global_controller
