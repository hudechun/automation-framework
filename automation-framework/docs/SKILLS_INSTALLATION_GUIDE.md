# Anthropic Skills 安装指南

## 安装位置

### 默认安装路径

系统默认会在以下位置查找 Skills：

```
AutoFlow-Platform/          ← 项目根目录
├── automation-framework/
├── RuoYi-Vue3-FastAPI/
└── skills/                 ← Skills 安装在这里（整个平台共享）
    ├── skills/            ← Anthropic Skills 仓库的 skills 文件夹
    │   ├── docx/
    │   │   └── SKILL.md
    │   ├── pdf/
    │   │   └── SKILL.md
    │   ├── xlsx/
    │   │   └── SKILL.md
    │   └── ...
    ├── spec/
    └── README.md
```

**完整路径**：
- Windows: `D:\AUTO-PC\AutoFlow-Platform\skills\`
- Linux/Mac: `{项目根目录}/skills/`

**为什么放在项目根目录？**
- 整个平台（RuoYi-Vue3-FastAPI 和 automation-framework）都可以共享 Skills
- 更符合项目结构，便于统一管理
- 避免重复安装

## 安装步骤

### 步骤1：进入项目根目录

```bash
cd D:\AUTO-PC\AutoFlow-Platform
```

### 步骤2：克隆 Anthropic Skills 仓库

```bash
git clone https://github.com/anthropics/skills.git
```

**或者**，如果你想安装到自定义位置：

```bash
# 安装到自定义位置
git clone https://github.com/anthropics/skills.git /path/to/custom/skills
```

### 步骤3：验证安装

安装后，目录结构应该是：

```
AutoFlow-Platform/              ← 项目根目录
├── automation-framework/
├── RuoYi-Vue3-FastAPI/
└── skills/                     ← 新克隆的目录
    ├── skills/                 ← Skills 文件夹
    │   ├── docx/
    │   ├── pdf/
    │   ├── xlsx/
    │   └── ...
    ├── spec/
    ├── template/
    └── README.md
```

## 使用自定义路径

如果你想把 Skills 安装到其他位置，可以在代码中指定：

### 方法1：在代码中指定路径

```python
from automation_framework.src.ai.anthropic_skills_loader import load_anthropic_skills

# 使用自定义路径
custom_path = "D:/MySkills/skills"
count = load_anthropic_skills(scenario_planner, custom_path)
```

### 方法2：使用 AnthropicSkillsLoader

```python
from automation_framework.src.ai.anthropic_skills_loader import AnthropicSkillsLoader

# 指定自定义路径
loader = AnthropicSkillsLoader(skills_dir="D:/MySkills/skills")
skills = loader.load_skills_from_directory(Path("D:/MySkills/skills"))
```

## 路径说明

### 代码中的默认路径

在 `anthropic_skills_loader.py` 中：

```python
# 默认路径计算
project_root = Path(__file__).parent.parent.parent.parent
self.skills_dir = project_root / "skills"

# 解析：
# __file__ = automation-framework/src/ai/anthropic_skills_loader.py
# .parent = automation-framework/src/ai/
# .parent.parent = automation-framework/src/
# .parent.parent.parent = automation-framework/
# .parent.parent.parent.parent = AutoFlow-Platform/ (项目根目录)
# 最终 = AutoFlow-Platform/skills/
```

### 检查当前路径

```python
from automation_framework.src.ai.anthropic_skills_loader import AnthropicSkillsLoader
from pathlib import Path

loader = AnthropicSkillsLoader()
print(f"默认 Skills 目录: {loader.skills_dir}")
print(f"目录是否存在: {loader.skills_dir.exists()}")
```

## 安装验证

### 验证安装是否成功

```python
from pathlib import Path
from automation_framework.src.ai.anthropic_skills_loader import AnthropicSkillsLoader

# 检查默认路径
loader = AnthropicSkillsLoader()
skills_dir = loader.skills_dir

print(f"Skills 目录: {skills_dir}")
print(f"目录存在: {skills_dir.exists()}")

if skills_dir.exists():
    # 列出所有 Skills
    skills = loader.load_skills_from_directory(skills_dir)
    print(f"找到 {len(skills)} 个 Skills:")
    for name in skills.keys():
        print(f"  - {name}")
else:
    print("⚠️ Skills 目录不存在，请先克隆仓库")
    print(f"运行: git clone https://github.com/anthropics/skills.git {skills_dir}")
```

## 常见问题

### Q1: 我应该安装在哪里？

**A**: 推荐安装在默认位置 `automation-framework/skills/`，这样系统会自动找到。

### Q2: 可以安装到其他位置吗？

**A**: 可以，在代码中指定自定义路径即可。

### Q3: 如何知道当前使用的路径？

**A**: 
```python
loader = AnthropicSkillsLoader()
print(loader.skills_dir)
```

### Q4: 安装后如何更新？

**A**: 
```bash
cd automation-framework/skills
git pull origin main
```

### Q5: 可以只安装部分 Skills 吗？

**A**: 可以，只保留需要的 Skills 文件夹即可。例如，如果只需要 DOCX 和 PDF：
```bash
# 克隆完整仓库
git clone https://github.com/anthropics/skills.git

# 只保留需要的 Skills
cd skills/skills
# 删除不需要的文件夹，只保留 docx/ 和 pdf/
```

## 快速安装命令

### Windows (PowerShell)

```powershell
cd D:\AUTO-PC\AutoFlow-Platform\automation-framework
git clone https://github.com/anthropics/skills.git
```

### Linux/Mac

```bash
cd /path/to/automation-framework
git clone https://github.com/anthropics/skills.git
```

## 目录结构示例

安装后的完整结构：

```
AutoFlow-Platform/                   ← 项目根目录
├── automation-framework/
│   ├── src/
│   │   └── ai/
│   │       └── anthropic_skills_loader.py
│   └── ...
├── RuoYi-Vue3-FastAPI/
│   └── ...
└── skills/                          ← 克隆的仓库（整个平台共享）
    ├── skills/                     ← 实际的 Skills
    │   ├── docx/                   ← DOCX Skill
    │   │   ├── SKILL.md
    │   │   ├── docx-js.md
    │   │   └── ooxml.md
    │   ├── pdf/                    ← PDF Skill
    │   │   └── SKILL.md
    │   ├── xlsx/                   ← Excel Skill
    │   │   └── SKILL.md
    │   └── ...                     ← 其他 Skills
    ├── spec/                       ← 规范文档
    ├── template/                   ← 模板
    └── README.md
```

## 下一步

安装完成后，参考 [ANTHROPIC_SKILLS_INTEGRATION.md](./ANTHROPIC_SKILLS_INTEGRATION.md) 了解如何使用。
