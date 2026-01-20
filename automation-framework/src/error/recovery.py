"""
恢复策略 - 实现错误恢复机制
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from enum import Enum

from ..core.checkpoint import CheckpointManager
from ..core.session import Session


class RecoveryType(Enum):
    """恢复类型"""
    CHECKPOINT = "checkpoint"  # 从检查点恢复
    FALLBACK = "fallback"      # 降级策略
    RETRY = "retry"            # 重试
    SKIP = "skip"              # 跳过
    ABORT = "abort"            # 中止


class RecoveryStrategy(ABC):
    """
    恢复策略抽象基类
    """
    
    @abstractmethod
    async def recover(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        """
        执行恢复
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            是否恢复成功
        """
        pass
    
    @abstractmethod
    def can_recover(self, error: Exception) -> bool:
        """
        判断是否可以恢复
        
        Args:
            error: 异常对象
            
        Returns:
            是否可以恢复
        """
        pass


class CheckpointRecovery(RecoveryStrategy):
    """
    检查点恢复策略 - 从最近的检查点恢复执行
    """
    
    def __init__(self, checkpoint_manager: Optional[CheckpointManager] = None):
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        
    async def recover(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        """
        从检查点恢复
        
        Args:
            error: 异常对象
            context: 上下文信息（需要包含session_id）
            
        Returns:
            是否恢复成功
        """
        session_id = context.get("session_id")
        if not session_id:
            return False
        
        try:
            # 获取最近的检查点
            checkpoints = self.checkpoint_manager.list_checkpoints(session_id=session_id)
            if not checkpoints:
                return False
            
            latest_checkpoint = checkpoints[0]
            
            # 恢复检查点
            checkpoint_data = self.checkpoint_manager.restore_checkpoint(
                latest_checkpoint["checkpoint_id"]
            )
            
            # TODO: 实际恢复会话状态
            print(f"Recovered from checkpoint: {latest_checkpoint['checkpoint_id']}")
            
            return True
            
        except Exception as e:
            print(f"Checkpoint recovery failed: {e}")
            return False
    
    def can_recover(self, error: Exception) -> bool:
        """检查点恢复适用于大多数可恢复错误"""
        from .exceptions import RecoverableError
        return isinstance(error, RecoverableError)


class FallbackRecovery(RecoveryStrategy):
    """
    降级恢复策略 - 使用备选方案
    """
    
    def __init__(self):
        self._fallback_chains: Dict[str, List[str]] = {}
        
    def register_fallback_chain(
        self,
        operation: str,
        chain: List[str]
    ) -> None:
        """
        注册降级链
        
        Args:
            operation: 操作名称
            chain: 降级链（按优先级排序）
        """
        self._fallback_chains[operation] = chain
        
    async def recover(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        """
        执行降级恢复
        
        Args:
            error: 异常对象
            context: 上下文信息（需要包含operation）
            
        Returns:
            是否恢复成功
        """
        operation = context.get("operation")
        if not operation or operation not in self._fallback_chains:
            return False
        
        chain = self._fallback_chains[operation]
        current_method = context.get("current_method")
        
        # 找到当前方法在链中的位置
        try:
            current_index = chain.index(current_method) if current_method else -1
        except ValueError:
            current_index = -1
        
        # 尝试下一个方法
        next_index = current_index + 1
        if next_index < len(chain):
            next_method = chain[next_index]
            print(f"Falling back from {current_method} to {next_method}")
            context["current_method"] = next_method
            return True
        
        return False
    
    def can_recover(self, error: Exception) -> bool:
        """降级恢复适用于元素定位失败等场景"""
        from .exceptions import ElementNotFoundError, TimeoutError
        return isinstance(error, (ElementNotFoundError, TimeoutError))


class RetryRecovery(RecoveryStrategy):
    """
    重试恢复策略 - 简单重试
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._retry_counts: Dict[str, int] = {}
        
    async def recover(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        """
        执行重试恢复
        
        Args:
            error: 异常对象
            context: 上下文信息（需要包含operation_id）
            
        Returns:
            是否可以重试
        """
        operation_id = context.get("operation_id", "unknown")
        
        # 获取当前重试次数
        retry_count = self._retry_counts.get(operation_id, 0)
        
        if retry_count < self.max_retries:
            self._retry_counts[operation_id] = retry_count + 1
            print(f"Retry {retry_count + 1}/{self.max_retries} for operation {operation_id}")
            return True
        
        # 重置计数
        self._retry_counts.pop(operation_id, None)
        return False
    
    def can_recover(self, error: Exception) -> bool:
        """重试恢复适用于网络错误等临时性错误"""
        from .exceptions import NetworkError, TimeoutError
        return isinstance(error, (NetworkError, TimeoutError))
    
    def reset_retry_count(self, operation_id: str) -> None:
        """重置重试计数"""
        self._retry_counts.pop(operation_id, None)


class SkipRecovery(RecoveryStrategy):
    """
    跳过恢复策略 - 跳过当前操作继续执行
    """
    
    async def recover(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        """
        跳过当前操作
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            总是返回True（跳过）
        """
        operation = context.get("operation", "unknown")
        print(f"Skipping operation: {operation}")
        return True
    
    def can_recover(self, error: Exception) -> bool:
        """跳过策略可以应用于任何错误"""
        return True


class RecoveryManager:
    """
    恢复管理器 - 管理多种恢复策略
    """
    
    def __init__(self):
        self._strategies: List[RecoveryStrategy] = []
        self._recovery_log: List[Dict[str, Any]] = []
        
    def register_strategy(self, strategy: RecoveryStrategy) -> None:
        """
        注册恢复策略
        
        Args:
            strategy: 恢复策略
        """
        self._strategies.append(strategy)
        
    def unregister_strategy(self, strategy: RecoveryStrategy) -> bool:
        """
        注销恢复策略
        
        Args:
            strategy: 恢复策略
            
        Returns:
            是否成功注销
        """
        try:
            self._strategies.remove(strategy)
            return True
        except ValueError:
            return False
    
    async def recover_from_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        """
        尝试从错误恢复
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            是否恢复成功
        """
        for strategy in self._strategies:
            if strategy.can_recover(error):
                try:
                    success = await strategy.recover(error, context)
                    
                    # 记录恢复尝试
                    self._recovery_log.append({
                        "strategy": strategy.__class__.__name__,
                        "error": error.__class__.__name__,
                        "success": success,
                        "context": context,
                    })
                    
                    if success:
                        return True
                        
                except Exception as e:
                    print(f"Recovery strategy {strategy.__class__.__name__} failed: {e}")
        
        return False
    
    def get_recovery_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取恢复日志
        
        Args:
            limit: 返回数量限制
            
        Returns:
            恢复日志列表
        """
        return self._recovery_log[-limit:]
    
    def clear_recovery_log(self) -> None:
        """清空恢复日志"""
        self._recovery_log.clear()


# 全局恢复管理器实例
_global_recovery_manager: Optional[RecoveryManager] = None


def get_global_recovery_manager() -> RecoveryManager:
    """获取全局恢复管理器"""
    global _global_recovery_manager
    if _global_recovery_manager is None:
        _global_recovery_manager = RecoveryManager()
        
        # 注册默认策略
        _global_recovery_manager.register_strategy(RetryRecovery())
        _global_recovery_manager.register_strategy(FallbackRecovery())
        _global_recovery_manager.register_strategy(CheckpointRecovery())
    
    return _global_recovery_manager
