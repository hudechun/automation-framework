# Anthropic Skills 集成指南

## 概述

本系统支持加载和使用 [Anthropic Skills](https://github.com/anthropics/skills) 仓库中的 Skills，将它们转换为系统的场景模板，从而扩展自动化能力。

## 什么是 Anthropic Skills？

Anthropic Skills 是包含指令、脚本和资源的文件夹，用于教 AI 如何完成特定任务。每个 Skill 包含一个 `SKILL.md` 文件，其中包含：
- YAML frontmatter（元数据）
- Markdown 指令（操作指南）

## 使用方法

### 方法1：从 GitHub 克隆 Skills 仓库

```bash
# 克隆 Anthropic Skills 仓库
cd automation-framework
git clone https://github.com/anthropics/skills.git
```

### 方法2：使用 Skills 加载器

```python
from automation_framework.src.ai.scenario_planner import ScenarioPlanner
from automation_framework.src.ai.anthropic_skills_loader import load_anthropic_skills
from automation_framework.src.ai.llm import create_llm_provider
from automation_framework.src.ai.config import ModelConfig

# 创建 ScenarioPlanner
llm = create_llm_provider(model_config)
planner = TaskPlanner(llm)
scenario_planner = ScenarioPlanner(llm, planner)

# 加载 Anthropic Skills
skills_dir = "skills"  # Skills 目录路径
count = load_anthropic_skills(scenario_planner, skills_dir)
print(f"Loaded {count} skills")
```

### 方法3：在 Agent 中自动加载

```python
from automation_framework.src.ai.agent import Agent
from automation_framework.src.ai.config import ModelConfig

# 创建 Agent（会自动加载 Skills）
agent = Agent(model_config, enable_scenario=True)

# 使用 Skills
result = await agent.execute_task("使用 PDF skill 提取文档字段")
```

## Skills 转换流程

```
Anthropic Skill (SKILL.md)
    ↓
解析 YAML frontmatter 和 Markdown
    ↓
提取元数据（name, description）
    ↓
提取指令、示例、指南
    ↓
推断场景类型和驱动类型
    ↓
转换为 ScenarioTemplate
    ↓
注册到 ScenarioPlanner
```

## 支持的 Skills

### 文档处理 Skills

- **PDF Skills** - PDF 文档处理
- **DOCX Skills** - Word 文档处理
- **XLSX Skills** - Excel 表格处理
- **PPTX Skills** - PowerPoint 演示文稿处理

### 开发和技术 Skills

- **Web Testing** - Web 应用测试
- **MCP Server Generation** - MCP 服务器生成
- **Code Review** - 代码审查

### 创意和设计 Skills

- **Art Generation** - 艺术生成
- **Music Composition** - 音乐创作
- **Design Guidelines** - 设计指南

### 企业工作流 Skills

- **Communications** - 通信
- **Branding** - 品牌管理
- **Data Analysis** - 数据分析

## 示例：使用 PDF Skill

### 1. 加载 PDF Skill

```python
from automation_framework.src.ai.anthropic_skills_loader import AnthropicSkillsLoader
from automation_framework.src.ai.scenario_planner import ScenarioPlanner

loader = AnthropicSkillsLoader()
scenario_planner = ScenarioPlanner(llm)

# 加载 PDF Skill
skills = loader.load_skills_from_directory(Path("skills/pdf"))
pdf_skill = skills.get("pdf")

if pdf_skill:
    template = loader.convert_to_scenario_template(pdf_skill)
    scenario_planner.SCENARIO_TEMPLATES[ScenarioType.DESKTOP_FILE] = template
```

### 2. 使用 PDF Skill

```python
# 自然语言任务
task = "从 invoice.pdf 中提取所有表单字段"

# 系统会自动使用 PDF Skill
result = await agent.execute_task(task)
```

## 自定义 Skills

### 创建自定义 Skill

1. 在 `skills` 目录下创建新文件夹
2. 创建 `SKILL.md` 文件：

```markdown
---
name: my-custom-skill
description: 我的自定义技能描述
---

# My Custom Skill

## 功能说明
这个技能用于...

## 示例
- 示例1：使用场景1
- 示例2：使用场景2

## 指南
- 指南1：注意事项
- 指南2：最佳实践
```

3. 系统会自动加载并注册

## 场景类型推断

系统会根据 Skill 的内容自动推断场景类型：

| 关键词 | 场景类型 |
|--------|---------|
| wechat, 微信, chat | WECHAT_CHAT |
| login, 登录, auth | BROWSER_LOGIN |
| scrape, crawl, 采集 | BROWSER_SCRAPING |
| file, document, 文件 | DESKTOP_FILE |
| app, application, 应用 | DESKTOP_APP |

## 驱动类型推断

系统会根据 Skill 的内容自动推断驱动类型：

| 关键词 | 驱动类型 |
|--------|---------|
| browser, web, url, http | browser |
| desktop, app, window | desktop |

## 限制和注意事项

1. **Skills 格式**：必须符合 Anthropic Skills 标准格式
2. **场景推断**：自动推断可能不准确，建议手动指定
3. **操作映射**：需要确保 Skill 中的操作与系统支持的操作匹配
4. **测试**：使用前请充分测试

## 最佳实践

1. **选择相关 Skills**：只加载与你的自动化场景相关的 Skills
2. **自定义转换**：对于复杂 Skills，可能需要自定义转换逻辑
3. **定期更新**：定期从 GitHub 更新 Skills 仓库
4. **文档化**：记录你使用的 Skills 和自定义修改

## 故障排查

### 问题1：Skills 未加载

**可能原因**：
- Skills 目录路径不正确
- SKILL.md 文件格式错误

**解决方案**：
```python
# 检查 Skills 目录
loader = AnthropicSkillsLoader()
print(f"Skills directory: {loader.skills_dir}")

# 手动加载并查看错误
skills = loader.load_skills_from_directory(Path("skills"))
print(f"Loaded {len(skills)} skills")
```

### 问题2：场景类型推断错误

**解决方案**：
```python
# 手动指定场景类型
template = loader.convert_to_scenario_template(
    skill,
    scenario_type=ScenarioType.BROWSER_SCRAPING
)
```

### 问题3：操作不匹配

**解决方案**：
- 检查 Skill 中的操作是否与系统支持的操作匹配
- 可能需要自定义操作映射逻辑

## 相关资源

- [Anthropic Skills 仓库](https://github.com/anthropics/skills)
- [Agent Skills 规范](https://agentskills.io)
- [创建自定义 Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)

## 更新日志

- 2026-01-24: 初始版本，支持加载和转换 Anthropic Skills
