"""
Anthropic Skills 加载器 - 从 GitHub 仓库加载和转换 Skills
"""
import os
import re
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

from .scenario_planner import ScenarioPlanner, ScenarioType, ScenarioTemplate

logger = logging.getLogger(__name__)


@dataclass
class AnthropicSkill:
    """Anthropic Skill 数据结构"""
    name: str
    description: str
    instructions: str
    examples: List[str] = None
    guidelines: List[str] = None
    metadata: Dict[str, Any] = None


class AnthropicSkillsLoader:
    """
    Anthropic Skills 加载器
    从 GitHub 仓库或本地目录加载 Skills 并转换为系统场景模板
    """
    
    def __init__(self, skills_dir: Optional[str] = None):
        """
        初始化加载器
        
        Args:
            skills_dir: Skills 目录路径（如果为None，则使用默认路径）
        """
        if skills_dir:
            self.skills_dir = Path(skills_dir)
        else:
            # 默认路径：项目根目录下的 skills 文件夹
            self.skills_dir = Path(__file__).parent.parent.parent / "skills"
        
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_skills: Dict[str, AnthropicSkill] = {}
    
    def parse_skill_file(self, skill_file: Path) -> Optional[AnthropicSkill]:
        """
        解析 SKILL.md 文件
        
        Args:
            skill_file: SKILL.md 文件路径
            
        Returns:
            AnthropicSkill 对象
        """
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # 解析 YAML frontmatter
            frontmatter_match = re.match(
                r'^---\s*\n(.*?)\n---\s*\n(.*)$',
                content,
                re.DOTALL
            )
            
            if not frontmatter_match:
                logger.warning(f"No frontmatter found in {skill_file}")
                return None
            
            frontmatter_str = frontmatter_match.group(1)
            instructions = frontmatter_match.group(2).strip()
            
            # 解析 YAML
            metadata = yaml.safe_load(frontmatter_str) or {}
            
            name = metadata.get('name', skill_file.parent.name)
            description = metadata.get('description', '')
            
            # 提取示例和指南（如果存在）
            examples = []
            guidelines = []
            
            # 查找 Examples 部分
            examples_match = re.search(
                r'##\s+Examples?\s*\n(.*?)(?=\n##|\Z)',
                instructions,
                re.DOTALL | re.IGNORECASE
            )
            if examples_match:
                examples_text = examples_match.group(1)
                examples = [
                    line.strip('- ').strip()
                    for line in examples_text.split('\n')
                    if line.strip().startswith('-')
                ]
            
            # 查找 Guidelines 部分
            guidelines_match = re.search(
                r'##\s+Guidelines?\s*\n(.*?)(?=\n##|\Z)',
                instructions,
                re.DOTALL | re.IGNORECASE
            )
            if guidelines_match:
                guidelines_text = guidelines_match.group(1)
                guidelines = [
                    line.strip('- ').strip()
                    for line in guidelines_text.split('\n')
                    if line.strip().startswith('-')
                ]
            
            return AnthropicSkill(
                name=name,
                description=description,
                instructions=instructions,
                examples=examples or [],
                guidelines=guidelines or [],
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to parse skill file {skill_file}: {e}")
            return None
    
    def load_skills_from_directory(self, directory: Path) -> Dict[str, AnthropicSkill]:
        """
        从目录加载所有 Skills
        
        Args:
            directory: Skills 目录路径
            
        Returns:
            Skills 字典（name -> AnthropicSkill）
        """
        skills = {}
        
        if not directory.exists():
            logger.warning(f"Skills directory not found: {directory}")
            return skills
        
        # 遍历目录，查找所有包含 SKILL.md 的文件夹
        for item in directory.iterdir():
            if item.is_dir():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    skill = self.parse_skill_file(skill_file)
                    if skill:
                        skills[skill.name] = skill
                        logger.info(f"Loaded skill: {skill.name}")
        
        return skills
    
    def convert_to_scenario_template(
        self,
        skill: AnthropicSkill,
        scenario_type: Optional[ScenarioType] = None
    ) -> Optional[ScenarioTemplate]:
        """
        将 Anthropic Skill 转换为 ScenarioTemplate
        
        Args:
            skill: AnthropicSkill 对象
            scenario_type: 场景类型（如果为None则自动推断）
            
        Returns:
            ScenarioTemplate 对象
        """
        # 自动推断场景类型
        if scenario_type is None:
            scenario_type = self._infer_scenario_type(skill)
        
        # 推断驱动类型
        driver_type = self._infer_driver_type(skill)
        
        # 提取常用操作
        common_actions = self._extract_common_actions(skill)
        
        # 构建提示词模板
        prompt_template = self._build_prompt_template(skill)
        
        return ScenarioTemplate(
            scenario_type=scenario_type,
            name=skill.name.replace('-', ' ').title(),
            description=skill.description,
            driver_type=driver_type,
            common_actions=common_actions,
            prompt_template=prompt_template
        )
    
    def _infer_scenario_type(self, skill: AnthropicSkill) -> ScenarioType:
        """推断场景类型"""
        name_lower = skill.name.lower()
        description_lower = skill.description.lower()
        text = f"{name_lower} {description_lower}"
        
        # 微信相关
        if any(kw in text for kw in ["wechat", "微信", "chat", "message"]):
            return ScenarioType.WECHAT_CHAT
        
        # 浏览器登录
        if any(kw in text for kw in ["login", "登录", "auth", "authentication"]):
            return ScenarioType.BROWSER_LOGIN
        
        # 数据采集
        if any(kw in text for kw in ["scrape", "crawl", "采集", "extract", "data"]):
            return ScenarioType.BROWSER_SCRAPING
        
        # 文件操作
        if any(kw in text for kw in ["file", "document", "文件", "pdf", "docx", "excel"]):
            return ScenarioType.DESKTOP_FILE
        
        # 应用操作
        if any(kw in text for kw in ["app", "application", "应用", "desktop"]):
            return ScenarioType.DESKTOP_APP
        
        return ScenarioType.GENERIC
    
    def _infer_driver_type(self, skill: AnthropicSkill) -> str:
        """推断驱动类型"""
        text = f"{skill.name} {skill.description}".lower()
        
        if any(kw in text for kw in ["browser", "web", "url", "http", "html"]):
            return "browser"
        elif any(kw in text for kw in ["desktop", "app", "window", "file"]):
            return "desktop"
        else:
            return "browser"  # 默认浏览器
    
    def _extract_common_actions(self, skill: AnthropicSkill) -> List[str]:
        """从 Skill 中提取常用操作"""
        actions = []
        
        # 从示例中提取
        for example in skill.examples:
            # 简单的关键词匹配
            if "open" in example.lower() or "打开" in example:
                actions.append("打开")
            if "click" in example.lower() or "点击" in example:
                actions.append("点击")
            if "type" in example.lower() or "输入" in example:
                actions.append("输入")
            if "send" in example.lower() or "发送" in example:
                actions.append("发送")
            if "wait" in example.lower() or "等待" in example:
                actions.append("等待")
        
        # 如果没有找到，返回默认操作
        if not actions:
            actions = ["执行操作"]
        
        return list(set(actions))  # 去重
    
    def _build_prompt_template(self, skill: AnthropicSkill) -> str:
        """构建 LLM 提示词模板"""
        template = f"""你是一个{skill.name.replace('-', ' ')}自动化专家。根据用户需求生成自动化指令。

用户需求：{{task_description}}

{skill.instructions}

"""
        
        # 添加示例
        if skill.examples:
            template += "## 示例\n"
            for example in skill.examples[:5]:  # 最多5个示例
                template += f"- {example}\n"
            template += "\n"
        
        # 添加指南
        if skill.guidelines:
            template += "## 指南\n"
            for guideline in skill.guidelines[:5]:  # 最多5个指南
                template += f"- {guideline}\n"
            template += "\n"
        
        template += """返回JSON格式的操作序列：
[
    {
        "action": "<action_type>",
        "params": {"<key>": "<value>"},
        "description": "<操作描述>"
    }
]"""
        
        return template
    
    def load_and_register_skills(
        self,
        scenario_planner: ScenarioPlanner,
        skills_source: Optional[str] = None
    ) -> int:
        """
        加载 Skills 并注册到 ScenarioPlanner
        
        Args:
            scenario_planner: ScenarioPlanner 实例
            skills_source: Skills 来源（GitHub URL 或本地路径）
            
        Returns:
            成功加载的 Skills 数量
        """
        if skills_source:
            if skills_source.startswith('http'):
                # 从 GitHub 下载（需要实现）
                logger.warning("GitHub download not implemented yet. Please clone the repo manually.")
                return 0
            else:
                # 从本地路径加载
                skills_dir = Path(skills_source)
        else:
            skills_dir = self.skills_dir
        
        # 加载 Skills
        skills = self.load_skills_from_directory(skills_dir)
        
        if not skills:
            logger.warning("No skills found")
            return 0
        
        # 转换为场景模板并注册
        registered_count = 0
        for skill_name, skill in skills.items():
            try:
                template = self.convert_to_scenario_template(skill)
                if template:
                    # 使用推断的场景类型或创建新的
                    # 注意：如果场景类型已存在，会覆盖原有模板
                    scenario_planner.SCENARIO_TEMPLATES[template.scenario_type] = template
                    registered_count += 1
                    logger.info(f"Registered skill as scenario: {skill_name}")
            except Exception as e:
                logger.error(f"Failed to register skill {skill_name}: {e}")
        
        return registered_count


def load_anthropic_skills(
    scenario_planner: ScenarioPlanner,
    skills_dir: Optional[str] = None
) -> int:
    """
    便捷函数：加载 Anthropic Skills
    
    Args:
        scenario_planner: ScenarioPlanner 实例
        skills_dir: Skills 目录路径
        
    Returns:
        成功加载的 Skills 数量
    """
    loader = AnthropicSkillsLoader(skills_dir)
    return loader.load_and_register_skills(scenario_planner, skills_dir)
