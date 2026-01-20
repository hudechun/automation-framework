"""
调试模式支持
"""
from typing import Dict, Any, Optional, Set, Callable
from dataclasses import dataclass
import asyncio


@dataclass
class Breakpoint:
    """断点"""
    id: str
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        """
        检查是否应该中断
        
        Args:
            context: 执行上下文
            
        Returns:
            是否中断
        """
        if not self.enabled:
            return False
        
        # 如果没有条件，总是中断
        if not self.condition:
            return True
        
        # 评估条件
        try:
            return eval(self.condition, {}, context)
        except Exception:
            return False


class DebugMode:
    """
    调试模式管理器
    """
    
    def __init__(self):
        self.enabled = False
        self.step_mode = False
        self.breakpoints: Dict[str, Breakpoint] = {}
        self.paused = False
        self._continue_event = asyncio.Event()
        self._continue_event.set()
        self.on_pause_callback: Optional[Callable] = None
    
    def enable(self) -> None:
        """启用调试模式"""
        self.enabled = True
    
    def disable(self) -> None:
        """禁用调试模式"""
        self.enabled = False
        self.step_mode = False
        self.paused = False
        self._continue_event.set()
    
    def enable_step_mode(self) -> None:
        """启用逐步执行模式"""
        self.step_mode = True
        self.enabled = True
    
    def disable_step_mode(self) -> None:
        """禁用逐步执行模式"""
        self.step_mode = False
    
    def set_breakpoint(
        self,
        breakpoint_id: str,
        condition: Optional[str] = None
    ) -> None:
        """
        设置断点
        
        Args:
            breakpoint_id: 断点ID（如操作索引、步骤名称）
            condition: 断点条件（Python表达式）
        """
        self.breakpoints[breakpoint_id] = Breakpoint(
            id=breakpoint_id,
            condition=condition
        )
    
    def remove_breakpoint(self, breakpoint_id: str) -> None:
        """
        移除断点
        
        Args:
            breakpoint_id: 断点ID
        """
        if breakpoint_id in self.breakpoints:
            del self.breakpoints[breakpoint_id]
    
    def enable_breakpoint(self, breakpoint_id: str) -> None:
        """
        启用断点
        
        Args:
            breakpoint_id: 断点ID
        """
        if breakpoint_id in self.breakpoints:
            self.breakpoints[breakpoint_id].enabled = True
    
    def disable_breakpoint(self, breakpoint_id: str) -> None:
        """
        禁用断点
        
        Args:
            breakpoint_id: 断点ID
        """
        if breakpoint_id in self.breakpoints:
            self.breakpoints[breakpoint_id].enabled = False
    
    def list_breakpoints(self) -> Dict[str, Breakpoint]:
        """
        列出所有断点
        
        Returns:
            断点字典
        """
        return self.breakpoints.copy()
    
    async def check_breakpoint(
        self,
        breakpoint_id: str,
        context: Dict[str, Any]
    ) -> None:
        """
        检查断点
        
        Args:
            breakpoint_id: 断点ID
            context: 执行上下文
        """
        if not self.enabled:
            return
        
        # 检查是否有匹配的断点
        if breakpoint_id in self.breakpoints:
            breakpoint = self.breakpoints[breakpoint_id]
            if breakpoint.should_break(context):
                breakpoint.hit_count += 1
                await self.pause(context)
    
    async def check_step(self, context: Dict[str, Any]) -> None:
        """
        检查逐步执行
        
        Args:
            context: 执行上下文
        """
        if not self.enabled or not self.step_mode:
            return
        
        await self.pause(context)
    
    async def pause(self, context: Dict[str, Any]) -> None:
        """
        暂停执行
        
        Args:
            context: 执行上下文
        """
        self.paused = True
        self._continue_event.clear()
        
        # 调用暂停回调
        if self.on_pause_callback:
            try:
                self.on_pause_callback(context)
            except Exception as e:
                print(f"Pause callback error: {e}")
        
        # 等待继续信号
        await self._continue_event.wait()
        self.paused = False
    
    def continue_execution(self) -> None:
        """继续执行"""
        self._continue_event.set()
    
    def step_over(self) -> None:
        """单步执行"""
        self.step_mode = True
        self._continue_event.set()
    
    def is_paused(self) -> bool:
        """
        检查是否暂停
        
        Returns:
            是否暂停
        """
        return self.paused
    
    def capture_error_context(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        捕获错误上下文
        
        Args:
            error: 异常对象
            context: 执行上下文
            
        Returns:
            完整的错误上下文
        """
        import traceback
        
        error_context = {
            "error": str(error),
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc(),
            "context": context.copy()
        }
        
        # 添加变量信息
        if "variables" in context:
            error_context["variables"] = context["variables"]
        
        # 添加调用栈
        if "call_stack" in context:
            error_context["call_stack"] = context["call_stack"]
        
        return error_context
    
    def set_pause_callback(self, callback: Callable) -> None:
        """
        设置暂停回调
        
        Args:
            callback: 回调函数
        """
        self.on_pause_callback = callback


# 全局调试模式实例
debug_mode = DebugMode()


def enable_debug() -> None:
    """启用调试模式"""
    debug_mode.enable()


def disable_debug() -> None:
    """禁用调试模式"""
    debug_mode.disable()


def set_breakpoint(breakpoint_id: str, condition: Optional[str] = None) -> None:
    """
    设置断点
    
    Args:
        breakpoint_id: 断点ID
        condition: 断点条件
    """
    debug_mode.set_breakpoint(breakpoint_id, condition)


def remove_breakpoint(breakpoint_id: str) -> None:
    """
    移除断点
    
    Args:
        breakpoint_id: 断点ID
    """
    debug_mode.remove_breakpoint(breakpoint_id)
