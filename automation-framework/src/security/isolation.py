"""
会话隔离 - 浏览器和进程级隔离
"""
import asyncio
import multiprocessing
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BrowserContext:
    """浏览器上下文"""
    context_id: str
    session_id: str
    isolated: bool = True
    
    def __post_init__(self):
        self.cookies: Dict[str, Any] = {}
        self.local_storage: Dict[str, Any] = {}
        self.session_storage: Dict[str, Any] = {}


class SessionIsolation:
    """
    会话隔离管理器 - 浏览器上下文隔离
    """
    
    def __init__(self):
        self.contexts: Dict[str, BrowserContext] = {}
    
    async def create_isolated_context(
        self,
        session_id: str,
        browser: Any
    ) -> Optional[Any]:
        """
        创建隔离的浏览器上下文
        
        Args:
            session_id: 会话ID
            browser: 浏览器实例
            
        Returns:
            浏览器上下文
        """
        try:
            # 创建新的浏览器上下文
            context = await browser.new_context(
                # 隔离Cookie
                accept_downloads=True,
                # 隔离LocalStorage和SessionStorage
                storage_state=None,
                # 隔离缓存
                bypass_csp=False
            )
            
            # 记录上下文
            context_id = f"context_{session_id}"
            self.contexts[session_id] = BrowserContext(
                context_id=context_id,
                session_id=session_id
            )
            
            logger.info(f"Created isolated context for session: {session_id}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create isolated context: {e}")
            return None
    
    async def cleanup_context(self, session_id: str, context: Any) -> None:
        """
        清理浏览器上下文
        
        Args:
            session_id: 会话ID
            context: 浏览器上下文
        """
        try:
            # 关闭上下文
            await context.close()
            
            # 移除记录
            if session_id in self.contexts:
                del self.contexts[session_id]
            
            logger.info(f"Cleaned up context for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup context: {e}")
    
    def get_context(self, session_id: str) -> Optional[BrowserContext]:
        """
        获取会话上下文
        
        Args:
            session_id: 会话ID
            
        Returns:
            浏览器上下文
        """
        return self.contexts.get(session_id)
    
    def list_contexts(self) -> Dict[str, BrowserContext]:
        """
        列出所有上下文
        
        Returns:
            上下文字典
        """
        return self.contexts.copy()


class ProcessIsolation:
    """
    进程级隔离 - 为每个会话创建独立进程
    """
    
    def __init__(self):
        self.processes: Dict[str, multiprocessing.Process] = {}
        self.queues: Dict[str, multiprocessing.Queue] = {}
    
    def create_isolated_process(
        self,
        session_id: str,
        target: Callable,
        args: tuple = ()
    ) -> bool:
        """
        创建隔离的进程
        
        Args:
            session_id: 会话ID
            target: 目标函数
            args: 函数参数
            
        Returns:
            是否成功
        """
        try:
            # 创建通信队列
            queue = multiprocessing.Queue()
            self.queues[session_id] = queue
            
            # 创建进程
            process = multiprocessing.Process(
                target=target,
                args=args + (queue,),
                name=f"session_{session_id}"
            )
            
            # 启动进程
            process.start()
            
            # 记录进程
            self.processes[session_id] = process
            
            logger.info(f"Created isolated process for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create isolated process: {e}")
            return False
    
    def terminate_process(self, session_id: str, timeout: float = 5.0) -> bool:
        """
        终止进程
        
        Args:
            session_id: 会话ID
            timeout: 超时时间（秒）
            
        Returns:
            是否成功
        """
        if session_id not in self.processes:
            return False
        
        try:
            process = self.processes[session_id]
            
            # 尝试优雅终止
            process.terminate()
            process.join(timeout=timeout)
            
            # 如果还在运行，强制杀死
            if process.is_alive():
                process.kill()
                process.join()
            
            # 清理资源
            del self.processes[session_id]
            if session_id in self.queues:
                self.queues[session_id].close()
                del self.queues[session_id]
            
            logger.info(f"Terminated process for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate process: {e}")
            return False
    
    def is_alive(self, session_id: str) -> bool:
        """
        检查进程是否存活
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否存活
        """
        if session_id not in self.processes:
            return False
        
        return self.processes[session_id].is_alive()
    
    def send_message(self, session_id: str, message: Any) -> bool:
        """
        向进程发送消息
        
        Args:
            session_id: 会话ID
            message: 消息
            
        Returns:
            是否成功
        """
        if session_id not in self.queues:
            return False
        
        try:
            self.queues[session_id].put(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(
        self,
        session_id: str,
        timeout: Optional[float] = None
    ) -> Optional[Any]:
        """
        从进程接收消息
        
        Args:
            session_id: 会话ID
            timeout: 超时时间（秒）
            
        Returns:
            消息
        """
        if session_id not in self.queues:
            return None
        
        try:
            return self.queues[session_id].get(timeout=timeout)
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return None
    
    def list_processes(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有进程
        
        Returns:
            进程信息字典
        """
        result = {}
        for session_id, process in self.processes.items():
            result[session_id] = {
                "pid": process.pid,
                "name": process.name,
                "alive": process.is_alive(),
                "exitcode": process.exitcode
            }
        return result
    
    def cleanup_all(self) -> None:
        """清理所有进程"""
        for session_id in list(self.processes.keys()):
            self.terminate_process(session_id)
