"""
控制流操作 - 支持循环和条件分支
"""
import asyncio
from typing import List, Optional, Dict, Any, Callable
from .interfaces import Action, Driver
from .types import ActionType
import logging

logger = logging.getLogger(__name__)


class Loop(Action):
    """
    循环操作 - 重复执行一组操作
    """
    
    def __init__(
        self,
        actions: List[Action],
        max_iterations: int = 100,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        break_on_error: bool = False
    ):
        """
        初始化循环操作
        
        Args:
            actions: 要循环执行的操作列表
            max_iterations: 最大循环次数
            condition: 循环条件函数（返回True继续循环，False退出）
            break_on_error: 遇到错误是否中断循环
        """
        super().__init__(
            ActionType.CONTROL_FLOW,
            actions=actions,
            max_iterations=max_iterations,
            break_on_error=break_on_error
        )
        self.actions = actions
        self.max_iterations = max_iterations
        self.condition = condition
        self.break_on_error = break_on_error
    
    def validate(self) -> bool:
        """验证循环参数"""
        return (
            isinstance(self.actions, list) and
            len(self.actions) > 0 and
            isinstance(self.max_iterations, int) and
            self.max_iterations > 0
        )
    
    async def execute(self, driver: Driver) -> Dict[str, Any]:
        """
        执行循环操作
        
        Returns:
            循环执行结果（包含迭代次数、每次迭代的结果）
        """
        if not self.validate():
            raise ValueError("Invalid loop parameters")
        
        results = []
        iteration = 0
        
        for i in range(self.max_iterations):
            iteration = i + 1
            logger.info(f"Loop iteration {iteration}/{self.max_iterations}")
            
            # 检查循环条件
            if self.condition:
                try:
                    # 传递当前上下文（可以从driver或execution context获取）
                    context = getattr(driver, '_context', {})
                    if not self.condition(context):
                        logger.info(f"Loop condition not met, breaking at iteration {iteration}")
                        break
                except Exception as e:
                    logger.warning(f"Loop condition check failed: {e}")
                    if self.break_on_error:
                        raise
            
            # 执行循环体内的操作
            iteration_results = []
            for action in self.actions:
                try:
                    result = await action.execute(driver)
                    iteration_results.append({
                        "action": action.__class__.__name__,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Action failed in loop iteration {iteration}: {e}")
                    iteration_results.append({
                        "action": action.__class__.__name__,
                        "success": False,
                        "error": str(e)
                    })
                    if self.break_on_error:
                        raise
            
            results.append({
                "iteration": iteration,
                "results": iteration_results
            })
        
        return {
            "iterations": iteration,
            "results": results
        }


class If(Action):
    """
    条件分支操作 - 根据条件执行不同的操作
    """
    
    def __init__(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        then_actions: List[Action],
        else_actions: Optional[List[Action]] = None
    ):
        """
        初始化条件分支
        
        Args:
            condition: 条件函数（返回True执行then_actions，False执行else_actions）
            then_actions: 条件为True时执行的操作
            else_actions: 条件为False时执行的操作（可选）
        """
        super().__init__(
            ActionType.CONTROL_FLOW,
            condition=condition,
            then_actions=then_actions,
            else_actions=else_actions
        )
        self.condition = condition
        self.then_actions = then_actions
        self.else_actions = else_actions or []
    
    def validate(self) -> bool:
        """验证条件分支参数"""
        return (
            callable(self.condition) and
            isinstance(self.then_actions, list) and
            isinstance(self.else_actions, list)
        )
    
    async def execute(self, driver: Driver) -> Dict[str, Any]:
        """
        执行条件分支
        
        Returns:
            执行结果
        """
        if not self.validate():
            raise ValueError("Invalid if condition parameters")
        
        # 获取执行上下文
        context = getattr(driver, '_context', {})
        
        # 评估条件
        try:
            if asyncio.iscoroutinefunction(self.condition):
                condition_result = await self.condition(context)
            else:
                condition_result = self.condition(context)
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            raise
        
        # 根据条件执行相应的操作
        actions_to_execute = self.then_actions if condition_result else self.else_actions
        branch_name = "then" if condition_result else "else"
        
        logger.info(f"Executing {branch_name} branch ({len(actions_to_execute)} actions)")
        
        results = []
        for action in actions_to_execute:
            try:
                result = await action.execute(driver)
                results.append({
                    "action": action.__class__.__name__,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Action failed in {branch_name} branch: {e}")
                results.append({
                    "action": action.__class__.__name__,
                    "success": False,
                    "error": str(e)
                })
                raise
        
        return {
            "condition_result": condition_result,
            "branch": branch_name,
            "results": results
        }


class While(Action):
    """
    While循环 - 当条件满足时重复执行操作
    """
    
    def __init__(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        actions: List[Action],
        max_iterations: int = 100,
        break_on_error: bool = False
    ):
        """
        初始化While循环
        
        Args:
            condition: 循环条件（返回True继续循环）
            actions: 要执行的操作列表
            max_iterations: 最大循环次数（防止无限循环）
            break_on_error: 遇到错误是否中断循环
        """
        super().__init__(
            ActionType.CONTROL_FLOW,
            condition=condition,
            actions=actions,
            max_iterations=max_iterations,
            break_on_error=break_on_error
        )
        self.condition = condition
        self.actions = actions
        self.max_iterations = max_iterations
        self.break_on_error = break_on_error
    
    def validate(self) -> bool:
        """验证While循环参数"""
        return (
            callable(self.condition) and
            isinstance(self.actions, list) and
            len(self.actions) > 0 and
            isinstance(self.max_iterations, int) and
            self.max_iterations > 0
        )
    
    async def execute(self, driver: Driver) -> Dict[str, Any]:
        """
        执行While循环
        
        Returns:
            循环执行结果
        """
        if not self.validate():
            raise ValueError("Invalid while loop parameters")
        
        results = []
        iteration = 0
        context = getattr(driver, '_context', {})
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"While loop iteration {iteration}/{self.max_iterations}")
            
            # 检查循环条件
            try:
                if asyncio.iscoroutinefunction(self.condition):
                    condition_result = await self.condition(context)
                else:
                    condition_result = self.condition(context)
            except Exception as e:
                logger.error(f"While condition check failed: {e}")
                if self.break_on_error:
                    raise
                break
            
            if not condition_result:
                logger.info(f"While condition not met, breaking at iteration {iteration}")
                break
            
            # 执行循环体内的操作
            iteration_results = []
            for action in self.actions:
                try:
                    result = await action.execute(driver)
                    iteration_results.append({
                        "action": action.__class__.__name__,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Action failed in while loop iteration {iteration}: {e}")
                    iteration_results.append({
                        "action": action.__class__.__name__,
                        "success": False,
                        "error": str(e)
                    })
                    if self.break_on_error:
                        raise
            
            results.append({
                "iteration": iteration,
                "results": iteration_results
            })
        
        return {
            "iterations": iteration,
            "results": results
        }


import asyncio
