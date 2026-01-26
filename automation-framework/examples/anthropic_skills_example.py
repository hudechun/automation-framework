"""
Anthropic Skills 使用示例
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.agent import Agent
from src.ai.config import ModelConfig, model_config_from_db_model
from src.ai.anthropic_skills_loader import AnthropicSkillsLoader, load_anthropic_skills
from src.ai.scenario_planner import ScenarioPlanner


async def example_1_load_skills():
    """示例1：加载 Anthropic Skills"""
    print("=" * 60)
    print("示例1：加载 Anthropic Skills")
    print("=" * 60)
    
    # 创建 LLM 配置
    llm_config = ModelConfig(
        provider="openai",
        model="gpt-4",
        api_key="your-api-key"
    )
    
    # 创建 ScenarioPlanner
    from src.ai.llm import create_llm_provider
    from src.ai.agent import TaskPlanner
    
    llm = create_llm_provider(llm_config)
    planner = TaskPlanner(llm)
    scenario_planner = ScenarioPlanner(llm, planner)
    
    # 加载 Anthropic Skills
    skills_dir = Path(__file__).parent.parent / "skills"
    if skills_dir.exists():
        count = load_anthropic_skills(scenario_planner, str(skills_dir))
        print(f"✅ 成功加载 {count} 个 Skills")
    else:
        print(f"⚠️ Skills 目录不存在: {skills_dir}")
        print("请先克隆 Anthropic Skills 仓库：")
        print("  git clone https://github.com/anthropics/skills.git automation-framework/skills")
    
    return scenario_planner


async def example_2_use_pdf_skill():
    """示例2：使用 PDF Skill"""
    print("\n" + "=" * 60)
    print("示例2：使用 PDF Skill")
    print("=" * 60)
    
    llm_config = ModelConfig(
        provider="openai",
        model="gpt-4",
        api_key="your-api-key"
    )
    
    from src.ai.llm import create_llm_provider
    from src.ai.agent import TaskPlanner
    
    llm = create_llm_provider(llm_config)
    planner = TaskPlanner(llm)
    scenario_planner = ScenarioPlanner(llm, planner)
    
    # 加载 PDF Skill
    loader = AnthropicSkillsLoader()
    skills_dir = Path(__file__).parent.parent / "skills" / "pdf"
    
    if skills_dir.exists():
        skills = loader.load_skills_from_directory(skills_dir)
        if skills:
            pdf_skill = list(skills.values())[0]
            print(f"✅ 加载 PDF Skill: {pdf_skill.name}")
            print(f"   描述: {pdf_skill.description}")
            print(f"   示例数量: {len(pdf_skill.examples)}")
    else:
        print("⚠️ PDF Skill 目录不存在")


async def example_3_list_available_skills():
    """示例3：列出所有可用的 Skills"""
    print("\n" + "=" * 60)
    print("示例3：列出所有可用的 Skills")
    print("=" * 60)
    
    loader = AnthropicSkillsLoader()
    skills_dir = Path(__file__).parent.parent / "skills"
    
    if skills_dir.exists():
        skills = loader.load_skills_from_directory(skills_dir)
        print(f"\n找到 {len(skills)} 个 Skills：\n")
        
        for name, skill in skills.items():
            print(f"📦 {name}")
            print(f"   描述: {skill.description[:80]}...")
            print(f"   示例: {len(skill.examples)} 个")
            print()
    else:
        print("⚠️ Skills 目录不存在")
        print("\n要使用 Anthropic Skills，请先克隆仓库：")
        print("  cd automation-framework")
        print("  git clone https://github.com/anthropics/skills.git")


async def example_4_convert_skill_to_scenario():
    """示例4：将 Skill 转换为场景模板"""
    print("\n" + "=" * 60)
    print("示例4：将 Skill 转换为场景模板")
    print("=" * 60)
    
    loader = AnthropicSkillsLoader()
    skills_dir = Path(__file__).parent.parent / "skills"
    
    if skills_dir.exists():
        # 查找第一个 Skill
        skills = loader.load_skills_from_directory(skills_dir)
        if skills:
            skill_name, skill = list(skills.items())[0]
            print(f"转换 Skill: {skill_name}\n")
            
            # 转换为场景模板
            template = loader.convert_to_scenario_template(skill)
            
            if template:
                print(f"✅ 转换成功")
                print(f"   场景类型: {template.scenario_type}")
                print(f"   场景名称: {template.name}")
                print(f"   驱动类型: {template.driver_type}")
                print(f"   常用操作: {', '.join(template.common_actions[:5])}")
                print(f"\n提示词模板预览（前200字符）：")
                print(template.prompt_template[:200] + "...")
    else:
        print("⚠️ Skills 目录不存在")


async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Anthropic Skills 集成示例")
    print("=" * 60)
    print("\n注意：这些示例需要先克隆 Anthropic Skills 仓库")
    print("命令：git clone https://github.com/anthropics/skills.git automation-framework/skills\n")
    
    try:
        # 示例1：加载 Skills
        await example_1_load_skills()
        
        # 示例2：使用 PDF Skill
        await example_2_use_pdf_skill()
        
        # 示例3：列出所有 Skills
        await example_3_list_available_skills()
        
        # 示例4：转换 Skill
        await example_4_convert_skill_to_scenario()
        
        print("\n" + "=" * 60)
        print("所有示例完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
