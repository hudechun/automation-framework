"""
AI智能层模块
"""
from .config import (
    ModelConfig,
    ModelProfile,
    ModelConfigManager,
    get_global_config_manager,
)

from .llm import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
)

from .vision import (
    VisionModel,
    GPT4VisionProvider,
    Claude3VisionProvider,
)

from .agent import (
    Agent,
    TaskPlanner,
)

__all__ = [
    # 配置
    "ModelConfig",
    "ModelProfile",
    "ModelConfigManager",
    "get_global_config_manager",
    # LLM
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    # 视觉
    "VisionModel",
    "GPT4VisionProvider",
    "Claude3VisionProvider",
    # Agent
    "Agent",
    "TaskPlanner",
]
