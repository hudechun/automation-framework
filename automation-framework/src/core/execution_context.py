"""
执行上下文 - 管理任务执行过程中的状态和变量
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json


class ExecutionContext:
    """
    执行上下文 - 保存当前执行状态，支持暂停和恢复
    """
    
    def __init__(self):
        """初始化执行上下文"""
        self.current_action_index = 0  # 当前执行到第几个操作
        self.variables: Dict[str, Any] = {}  # 执行过程中的变量
        self.state: Dict[str, Any] = {}  # 执行状态
        self.checkpoint_data: Optional[Dict[str, Any]] = None  # 检查点数据
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def set_variable(self, key: str, value: Any) -> None:
        """
        设置变量
        
        Args:
            key: 变量名
            value: 变量值
        """
        self.variables[key] = value
        self.updated_at = datetime.now()
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        获取变量
        
        Args:
            key: 变量名
            default: 默认值
            
        Returns:
            变量值
        """
        return self.variables.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        """
        设置状态
        
        Args:
            key: 状态键
            value: 状态值
        """
        self.state[key] = value
        self.updated_at = datetime.now()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        获取状态
        
        Args:
            key: 状态键
            default: 默认值
            
        Returns:
            状态值
        """
        return self.state.get(key, default)
    
    def move_to_next_action(self) -> None:
        """移动到下一个操作"""
        self.current_action_index += 1
        self.updated_at = datetime.now()
    
    def set_checkpoint(self, checkpoint_data: Dict[str, Any]) -> None:
        """
        设置检查点
        
        Args:
            checkpoint_data: 检查点数据
        """
        self.checkpoint_data = checkpoint_data
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典（用于保存到数据库）
        
        Returns:
            字典表示
        """
        return {
            "current_action_index": self.current_action_index,
            "variables": self.variables,
            "state": self.state,
            "checkpoint_data": self.checkpoint_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_json(self) -> str:
        """
        序列化为JSON字符串
        
        Returns:
            JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionContext':
        """
        从字典反序列化（用于从数据库恢复）
        
        Args:
            data: 字典数据
            
        Returns:
            执行上下文实例
        """
        ctx = cls()
        ctx.current_action_index = data.get("current_action_index", 0)
        ctx.variables = data.get("variables", {})
        ctx.state = data.get("state", {})
        ctx.checkpoint_data = data.get("checkpoint_data")
        
        if "created_at" in data:
            ctx.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            ctx.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return ctx
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ExecutionContext':
        """
        从JSON字符串反序列化
        
        Args:
            json_str: JSON字符串
            
        Returns:
            执行上下文实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def reset(self) -> None:
        """重置上下文"""
        self.current_action_index = 0
        self.variables.clear()
        self.state.clear()
        self.checkpoint_data = None
        self.updated_at = datetime.now()
