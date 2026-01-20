"""
AI Agent和任务规划器
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .llm import LLMProvider, create_llm_provider
from .vision import VisionModel, create_vision_model
from .config import ModelConfig
from ..core.interfaces import Action


@dataclass
class TaskDescription:
    """任务描述"""
    goal: str
    constraints: List[str]
    parameters: Dict[str, Any]
    context: Dict[str, Any]


class TaskPlanner:
    """
    任务规划器 - 将自然语言任务分解为操作序列
    """
    
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        
    async def parse_task(self, natural_language: str) -> TaskDescription:
        """
        解析自然语言任务
        
        Args:
            natural_language: 自然语言任务描述
            
        Returns:
            结构化任务描述
        """
        prompt = f"""Parse the following task description and extract:
1. The main goal
2. Any constraints or requirements
3. Parameters or inputs needed
4. Context information

Task: {natural_language}

Return in JSON format:
{{
    "goal": "<main goal>",
    "constraints": ["<constraint1>", "<constraint2>"],
    "parameters": {{"<key>": "<value>"}},
    "context": {{"<key>": "<value>"}}
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.chat(messages)
        
        # 解析响应
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            data = json.loads(json_str)
            return TaskDescription(
                goal=data.get("goal", ""),
                constraints=data.get("constraints", []),
                parameters=data.get("parameters", {}),
                context=data.get("context", {})
            )
        except Exception as e:
            print(f"Failed to parse task: {e}")
            return TaskDescription(
                goal=natural_language,
                constraints=[],
                parameters={},
                context={}
            )
    
    async def plan(
        self,
        task_description: TaskDescription
    ) -> List[Dict[str, Any]]:
        """
        生成执行计划
        
        Args:
            task_description: 任务描述
            
        Returns:
            操作序列
        """
        prompt = f"""Create a step-by-step automation plan for this task:

Goal: {task_description.goal}
Constraints: {', '.join(task_description.constraints)}
Parameters: {task_description.parameters}

Generate a list of actions in JSON format:
[
    {{
        "action": "<action_type>",
        "params": {{"<key>": "<value>"}},
        "description": "<what this step does>"
    }}
]

Available actions: GoToURL, Click, Type, WaitForElement, GetText, Screenshot"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.chat(messages)
        
        # 解析响应
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse plan: {e}")
            return []
    
    async def replan(
        self,
        original_plan: List[Dict[str, Any]],
        execution_result: Dict[str, Any],
        error: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        重新规划
        
        Args:
            original_plan: 原始计划
            execution_result: 执行结果
            error: 错误信息
            
        Returns:
            新的操作序列
        """
        prompt = f"""The original plan encountered an issue. Create a new plan.

Original plan: {original_plan}
Execution result: {execution_result}
Error: {error}

Generate a revised plan in JSON format."""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.chat(messages)
        
        # 解析响应
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse replan: {e}")
            return original_plan


class Agent:
    """
    AI Agent - 智能自动化代理
    """
    
    def __init__(
        self,
        llm_config: ModelConfig,
        vision_config: Optional[ModelConfig] = None
    ):
        self.llm = create_llm_provider(llm_config)
        self.vision = create_vision_model(vision_config) if vision_config else None
        self.planner = TaskPlanner(self.llm)
        self.memory: List[Dict[str, Any]] = []
        
    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            执行结果
        """
        # 解析任务
        task_desc = await self.planner.parse_task(task)
        
        # 生成计划
        plan = await self.planner.plan(task_desc)
        
        # 记录到记忆
        self.memory.append({
            "task": task,
            "plan": plan,
            "context": context or {}
        })
        
        return {
            "task_description": task_desc,
            "plan": plan,
            "status": "planned"
        }
    
    async def think(
        self,
        situation: str,
        options: List[str]
    ) -> str:
        """
        推理和决策
        
        Args:
            situation: 当前情况
            options: 可选项
            
        Returns:
            决策结果
        """
        prompt = f"""Given the situation: {situation}

Available options:
{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(options))}

Which option should we choose and why? Provide your reasoning."""
        
        messages = [{"role": "user", "content": prompt}]
        return await self.llm.chat(messages)
    
    async def act(
        self,
        action_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行操作
        
        Args:
            action_plan: 操作计划
            
        Returns:
            执行结果
        """
        # TODO: 实际执行操作
        return {
            "action": action_plan,
            "status": "executed",
            "result": "success"
        }
    
    async def recover(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        错误恢复
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            恢复方案
        """
        prompt = f"""An error occurred during automation:

Error: {str(error)}
Context: {context}

Suggest a recovery strategy. Options:
1. Retry with same approach
2. Try alternative approach
3. Skip this step
4. Request human intervention

Provide your recommendation and reasoning."""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.chat(messages)
        
        return {
            "recommendation": response,
            "error": str(error),
            "context": context
        }
    
    def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取记忆
        
        Args:
            limit: 返回数量限制
            
        Returns:
            记忆列表
        """
        return self.memory[-limit:]
    
    def clear_memory(self) -> None:
        """清空记忆"""
        self.memory.clear()
