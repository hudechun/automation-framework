"""
AI模块 - 提供LLM、Agent和场景规划功能
"""
# 先导入不依赖 agent 的模块（避免循环导入）
from .llm import LLMProvider, create_llm_provider
from .config import ModelConfig, ModelProvider, model_config_from_db_model
from .rate_limiter import RateLimiter, RateLimitConfig, get_rate_limiter

# 延迟导入 agent 和 scenario_planner（避免循环导入）
def __getattr__(name):
    """延迟加载属性，避免循环导入"""
    if name in ["Agent", "TaskPlanner", "TaskDescription"]:
        from .agent import Agent, TaskPlanner, TaskDescription
        if name == "Agent":
            return Agent
        elif name == "TaskPlanner":
            return TaskPlanner
        elif name == "TaskDescription":
            return TaskDescription
    elif name in ["ScenarioPlanner", "ScenarioType"]:
        from .scenario_planner import ScenarioPlanner, ScenarioType
        if name == "ScenarioPlanner":
            return ScenarioPlanner
        elif name == "ScenarioType":
            return ScenarioType
    elif name in ["AnthropicSkillsLoader", "load_anthropic_skills"]:
        from .anthropic_skills_loader import AnthropicSkillsLoader, load_anthropic_skills
        if name == "AnthropicSkillsLoader":
            return AnthropicSkillsLoader
        elif name == "load_anthropic_skills":
            return load_anthropic_skills
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "Agent",
    "TaskPlanner",
    "TaskDescription",
    "LLMProvider",
    "create_llm_provider",
    "ModelConfig",
    "ModelProvider",
    "model_config_from_db_model",
    "ScenarioPlanner",
    "ScenarioType",
    "RateLimiter",
    "RateLimitConfig",
    "get_rate_limiter",
    "AnthropicSkillsLoader",
    "load_anthropic_skills",
]
