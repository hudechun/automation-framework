"""
模型配置管理器
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class ModelProvider(Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    QWEN = "qwen"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """模型配置"""
    provider: ModelProvider
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """验证配置"""
        if not self.model:
            raise ValueError("Model name is required")
        
        # OpenAI、Anthropic和Qwen需要API key
        if self.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC, ModelProvider.QWEN]:
            if not self.api_key:
                raise ValueError(f"{self.provider.value} requires api_key")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "params": self.params,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        """从字典创建"""
        return cls(
            provider=ModelProvider(data["provider"]),
            model=data["model"],
            api_key=data.get("api_key"),
            api_base=data.get("api_base"),
            params=data.get("params", {}),
        )


@dataclass
class ModelProfile:
    """模型配置文件"""
    name: str
    task_model: ModelConfig
    vision_model: Optional[ModelConfig] = None
    fallback_chain: List[ModelConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "task_model": self.task_model.to_dict(),
            "vision_model": self.vision_model.to_dict() if self.vision_model else None,
            "fallback_chain": [m.to_dict() for m in self.fallback_chain],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelProfile":
        """从字典创建"""
        return cls(
            name=data["name"],
            task_model=ModelConfig.from_dict(data["task_model"]),
            vision_model=ModelConfig.from_dict(data["vision_model"]) if data.get("vision_model") else None,
            fallback_chain=[ModelConfig.from_dict(m) for m in data.get("fallback_chain", [])],
            metadata=data.get("metadata", {}),
        )


class ModelConfigManager:
    """
    模型配置管理器
    """
    
    def __init__(self):
        self._profiles: Dict[str, ModelProfile] = {}
        self._current_profile: Optional[str] = None
        
    def load_config(self, config_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for profile_data in data.get("profiles", []):
            profile = ModelProfile.from_dict(profile_data)
            self._profiles[profile.name] = profile
        
        self._current_profile = data.get("current_profile")
    
    def save_config(self, config_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径
        """
        data = {
            "current_profile": self._current_profile,
            "profiles": [p.to_dict() for p in self._profiles.values()],
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_profile(self, profile: ModelProfile) -> None:
        """
        添加配置文件
        
        Args:
            profile: 模型配置文件
        """
        profile.task_model.validate()
        if profile.vision_model:
            profile.vision_model.validate()
        
        self._profiles[profile.name] = profile
        
        if self._current_profile is None:
            self._current_profile = profile.name
    
    def get_profile(self, name: Optional[str] = None) -> Optional[ModelProfile]:
        """
        获取配置文件
        
        Args:
            name: 配置文件名称，如果为None则返回当前配置
            
        Returns:
            模型配置文件
        """
        if name is None:
            name = self._current_profile
        
        return self._profiles.get(name) if name else None
    
    def list_profiles(self) -> List[str]:
        """
        列出所有配置文件
        
        Returns:
            配置文件名称列表
        """
        return list(self._profiles.keys())
    
    def switch_profile(self, name: str) -> bool:
        """
        切换配置文件
        
        Args:
            name: 配置文件名称
            
        Returns:
            是否切换成功
        """
        if name in self._profiles:
            self._current_profile = name
            return True
        return False
    
    def switch_model(
        self,
        model_type: str,
        model_config: ModelConfig
    ) -> bool:
        """
        切换单个模型
        
        Args:
            model_type: 模型类型（task_model或vision_model）
            model_config: 新的模型配置
            
        Returns:
            是否切换成功
        """
        profile = self.get_profile()
        if not profile:
            return False
        
        model_config.validate()
        
        if model_type == "task_model":
            profile.task_model = model_config
        elif model_type == "vision_model":
            profile.vision_model = model_config
        else:
            return False
        
        return True
    
    def configure_fallback_chain(
        self,
        chain: List[ModelConfig]
    ) -> None:
        """
        配置降级链
        
        Args:
            chain: 降级链（按优先级排序）
        """
        profile = self.get_profile()
        if profile:
            for config in chain:
                config.validate()
            profile.fallback_chain = chain
    
    def get_fallback_model(
        self,
        current_index: int = -1
    ) -> Optional[ModelConfig]:
        """
        获取降级模型
        
        Args:
            current_index: 当前模型在降级链中的索引
            
        Returns:
            下一个降级模型
        """
        profile = self.get_profile()
        if not profile or not profile.fallback_chain:
            return None
        
        next_index = current_index + 1
        if next_index < len(profile.fallback_chain):
            return profile.fallback_chain[next_index]
        
        return None


# 全局配置管理器实例
_global_config_manager: Optional[ModelConfigManager] = None


def get_global_config_manager() -> ModelConfigManager:
    """获取全局配置管理器"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ModelConfigManager()
    return _global_config_manager


def model_config_from_db_model(db_model: Any) -> ModelConfig:
    """
    从数据库模型对象创建ModelConfig
    
    Args:
        db_model: 数据库模型对象（SQLAlchemy或Tortoise ORM）
        
    Returns:
        ModelConfig对象
    """
    # 处理SQLAlchemy模型
    if hasattr(db_model, 'provider') and hasattr(db_model, 'model'):
        params = db_model.params if hasattr(db_model, 'params') and db_model.params else {}
        if isinstance(params, str):
            import json
            try:
                params = json.loads(params)
            except:
                params = {}
        
        return ModelConfig(
            provider=ModelProvider(db_model.provider),
            model=db_model.model,
            api_key=getattr(db_model, 'api_key', None),
            api_base=getattr(db_model, 'api_base', None),
            params=params
        )
    
    # 处理字典格式
    elif isinstance(db_model, dict):
        return ModelConfig.from_dict(db_model)
    
    else:
        raise ValueError(f"Unsupported model type: {type(db_model)}")
