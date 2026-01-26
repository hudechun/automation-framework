# DOCX Skills 功能详解

## 概述

DOCX Skills 是 Anthropic 提供的专业 Word 文档处理技能，支持创建、编辑、分析和处理 `.docx` 文件。这是一个功能强大的文档处理工具集。

## 核心能力

### 1. 📖 文档读取和分析

#### 文本提取
- **功能**：从 Word 文档中提取纯文本内容
- **方法**：使用 Pandoc 转换为 Markdown
- **特点**：
  - 保留文档结构（标题、段落、列表等）
  - 支持跟踪修订（tracked changes）
  - 可显示插入、删除、修改的内容

**示例**：
```bash
# 提取文本并保留修订标记
pandoc --track-changes=all document.docx -o output.md

# 选项说明：
# --track-changes=accept  # 只显示接受的更改
# --track-changes=reject   # 只显示拒绝的更改
# --track-changes=all     # 显示所有更改
```

#### 原始 XML 访问
- **功能**：直接访问文档的 XML 结构
- **用途**：
  - 读取注释（comments）
  - 获取复杂格式信息
  - 分析文档结构
  - 提取嵌入的媒体文件
  - 读取元数据

**关键文件结构**：
- `word/document.xml` - 主文档内容
- `word/comments.xml` - 文档注释
- `word/media/` - 嵌入的图片和媒体文件
- 修订标记：`<w:ins>`（插入）和 `<w:del>`（删除）

### 2. ✏️ 创建新文档

#### 功能
- 从零开始创建 Word 文档
- 支持完整的格式控制
- 使用 JavaScript/TypeScript（docx-js 库）

#### 支持的操作
- **文档结构**：
  - 创建段落（Paragraph）
  - 添加文本运行（TextRun）
  - 设置标题和样式
  - 添加列表（有序/无序）
  - 插入表格
  - 添加图片和媒体

- **格式控制**：
  - 字体样式（粗体、斜体、下划线）
  - 字体大小和颜色
  - 段落对齐（左、中、右、两端对齐）
  - 行距和段落间距
  - 页眉页脚
  - 分页符和分节符

**工作流程**：
1. 使用 Document、Paragraph、TextRun 组件构建文档
2. 设置格式和样式
3. 使用 `Packer.toBuffer()` 导出为 .docx

### 3. 🔧 编辑现有文档

#### 基础编辑（简单修改）
- **适用场景**：编辑自己的文档，进行简单修改
- **方法**：使用 OOXML 基础编辑
- **支持操作**：
  - 文本替换
  - 添加内容
  - 删除内容
  - 格式修改

#### 修订模式（Redlining Workflow）
- **适用场景**：
  - 编辑他人文档（推荐默认方式）
  - 法律、学术、商业、政府文档（必需）
  - 需要保留修改痕迹的场景

- **核心特性**：
  - **跟踪修订**：所有修改都会标记为修订
  - **批处理策略**：将相关修改分组（3-10个一组）
  - **精确编辑**：只标记实际变化的部分
  - **保留原始格式**：未修改部分保持原样

**修订工作流程**：

1. **获取 Markdown 表示**
   ```bash
   pandoc --track-changes=all document.docx -o current.md
   ```

2. **识别和分组修改**
   - 按章节分组（如"第2节修改"、"第5节更新"）
   - 按类型分组（如"日期更正"、"当事人名称变更"）
   - 按复杂度分组（先简单后复杂）
   - 按位置分组（如"第1-3页"、"第4-6页"）

3. **定位方法**（在 XML 中查找修改位置）：
   - 章节/标题编号（如"第3.2节"、"第IV条"）
   - 段落标识符（如果有编号）
   - Grep 模式匹配（使用唯一上下文文本）
   - 文档结构（如"第一段"、"签名块"）
   - ⚠️ **不要使用 Markdown 行号** - 它们不映射到 XML 结构

4. **实现修改（分批进行）**
   - 每组 3-10 个相关修改
   - 使用 `get_node` 查找节点
   - 实现修改后 `doc.save()`
   - 每次运行脚本前都要重新 grep 获取最新行号

5. **打包文档**
   ```bash
   python ooxml/scripts/pack.py unpacked reviewed-document.docx
   ```

6. **最终验证**
   ```bash
   # 转换为 Markdown 验证
   pandoc --track-changes=all reviewed-document.docx -o verification.md
   
   # 检查所有修改是否正确应用
   grep "原始短语" verification.md  # 应该找不到
   grep "替换短语" verification.md  # 应该找到
   ```

**修订编辑原则**：
- ✅ **最小化、精确编辑**：只标记实际变化的文本
- ❌ **避免重复未变化文本**：不要重复未修改的内容
- ✅ **保留原始 RSID**：未修改文本保留原始运行 ID

**示例 - 正确 vs 错误**：
```python
# ❌ 错误 - 替换整个句子
' The term is 30 days. The term is 60 days. '

# ✅ 正确 - 只标记变化的部分
' The term is 30 60 days. '
```

### 4. 💬 注释处理

#### 功能
- 读取文档中的所有注释
- 添加新注释
- 回复注释
- 删除注释
- 提取注释内容

#### 注释结构
- 注释存储在 `word/comments.xml`
- 注释在文档中通过 `<w:commentRangeStart>` 和 `<w:commentRangeEnd>` 标记
- 支持注释作者、时间戳、内容

### 5. 📊 格式处理

#### 支持的格式操作
- **文本格式**：
  - 字体（名称、大小、颜色）
  - 样式（粗体、斜体、下划线、删除线）
  - 高亮
  - 上标/下标

- **段落格式**：
  - 对齐方式
  - 缩进（左、右、首行）
  - 行距
  - 段落间距
  - 项目符号和编号

- **文档格式**：
  - 页边距
  - 页面方向（横向/纵向）
  - 页眉页脚
  - 分节符
  - 分栏

- **表格格式**：
  - 创建表格
  - 设置边框
  - 单元格合并
  - 表格样式

### 6. 🖼️ 媒体处理

#### 图片操作
- 插入图片
- 提取嵌入图片
- 调整图片大小
- 设置图片位置和环绕方式

#### 媒体文件
- 访问 `word/media/` 目录
- 提取所有嵌入的媒体文件
- 替换媒体文件

### 7. 📄 文档转换

#### 转换为 Markdown
```bash
pandoc document.docx -o output.md
```

#### 转换为 PDF
```bash
soffice --headless --convert-to pdf document.docx
```

#### 转换为图片
```bash
# 步骤1：转换为 PDF
soffice --headless --convert-to pdf document.docx

# 步骤2：PDF 转图片
pdftoppm -jpeg -r 150 document.pdf page

# 选项说明：
# -r 150: 分辨率 150 DPI
# -jpeg: JPEG 格式（可用 -png 改为 PNG）
# -f N: 起始页（如 -f 2 从第2页开始）
# -l N: 结束页（如 -l 5 到第5页结束）
# page: 输出文件前缀
```

### 8. 🔍 文档分析

#### 结构分析
- 提取文档大纲（标题层级）
- 分析段落结构
- 识别表格和列表
- 提取页眉页脚内容

#### 内容分析
- 统计字数、段落数
- 提取关键词
- 分析文档主题
- 识别文档类型（合同、报告、论文等）

#### 元数据分析
- 读取文档属性（作者、创建时间、修改时间）
- 提取自定义属性
- 分析文档统计信息

## 使用场景示例

### 场景1：创建报告文档

**任务**：创建一个包含标题、段落、表格和图片的 Word 报告

**系统处理**：
1. 识别为文档创建任务
2. 使用 DOCX Skill
3. 生成操作序列：
   - 创建文档结构
   - 添加标题和段落
   - 插入表格
   - 添加图片
   - 设置格式
   - 保存文档

### 场景2：批量修改文档

**任务**：将文档中所有的"2024年"替换为"2025年"，并标记为修订

**系统处理**：
1. 识别为文档编辑任务
2. 使用修订模式（Redlining）
3. 生成操作序列：
   - 解包文档
   - 查找所有"2024年"
   - 替换为"2025年"（标记为删除+插入）
   - 打包文档
   - 验证修改

### 场景3：提取文档内容

**任务**：从合同文档中提取所有日期和金额

**系统处理**：
1. 识别为文档分析任务
2. 使用文本提取功能
3. 生成操作序列：
   - 转换为 Markdown
   - 使用正则表达式提取日期和金额
   - 返回结构化数据

### 场景4：文档格式统一

**任务**：将多个文档的格式统一为标准格式

**系统处理**：
1. 识别为批量文档处理任务
2. 使用 DOCX Skill
3. 生成操作序列：
   - 读取每个文档
   - 应用标准格式模板
   - 保存格式化后的文档

### 场景5：添加注释和修订

**任务**：在文档的特定位置添加注释，并标记需要修改的部分

**系统处理**：
1. 识别为文档审查任务
2. 使用修订和注释功能
3. 生成操作序列：
   - 定位目标位置
   - 添加注释
   - 标记需要修改的文本
   - 应用修订标记

## 在自动化平台中的使用

### 通过自然语言使用

```python
# 示例1：创建文档
task = "创建一个包含标题'项目报告'、三个段落和一个表格的 Word 文档"

# 示例2：编辑文档
task = "将 contract.docx 中所有的'甲方'替换为'乙方'，并标记为修订"

# 示例3：提取内容
task = "从 report.docx 中提取所有表格数据"

# 示例4：添加注释
task = "在 document.docx 的第3段添加注释：'需要进一步说明'"

# 示例5：格式转换
task = "将 presentation.docx 转换为 PDF 格式"
```

### 系统自动处理流程

```
用户输入自然语言任务
    ↓
系统识别为文档处理任务
    ↓
加载 DOCX Skill
    ↓
转换为场景模板
    ↓
生成操作序列
    ↓
执行文档操作
```

## 技术实现

### 依赖工具

- **Pandoc**：文档转换工具
  ```bash
  sudo apt-get install pandoc
  ```

- **docx-js**：创建新文档（Node.js）
  ```bash
  npm install -g docx
  ```

- **LibreOffice**：PDF 转换
  ```bash
  sudo apt-get install libreoffice
  ```

- **Poppler**：PDF 转图片
  ```bash
  sudo apt-get install poppler-utils
  ```

- **defusedxml**：安全 XML 解析（Python）
  ```bash
  pip install defusedxml
  ```

### 文档库（Document Library）

- **用途**：Python 库，用于 OOXML 操作
- **功能**：
  - 自动处理基础设施设置
  - 提供高级方法进行文档操作
  - 支持直接访问底层 DOM
  - 处理复杂场景

## 最佳实践

### 1. 修订编辑原则

- ✅ **最小化编辑**：只标记实际变化
- ✅ **保留原始格式**：未修改部分保持原样
- ✅ **批处理**：相关修改分组处理（3-10个一组）
- ✅ **验证**：每次修改后验证结果

### 2. 代码风格

- 编写简洁代码
- 避免冗长的变量名
- 避免不必要的打印语句
- 使用高效的操作方法

### 3. 错误处理

- 每次修改前验证文档结构
- 使用 grep 确认文本位置
- 分批处理，便于调试
- 保留原始文档备份

## 限制和注意事项

1. **格式兼容性**：某些复杂格式可能无法完全保留
2. **修订模式**：编辑他人文档时必须使用修订模式
3. **批处理大小**：建议每组 3-10 个修改，便于调试
4. **XML 结构**：直接操作 XML 需要了解 OOXML 结构
5. **工具依赖**：需要安装相应的工具（Pandoc、LibreOffice 等）

## 与系统集成

### 加载 DOCX Skill

```python
from automation_framework.src.ai.anthropic_skills_loader import load_anthropic_skills
from automation_framework.src.ai.scenario_planner import ScenarioPlanner

# 加载 DOCX Skill
loader = AnthropicSkillsLoader()
skills = loader.load_skills_from_directory(Path("skills/docx"))
docx_skill = skills.get("docx")

if docx_skill:
    template = loader.convert_to_scenario_template(docx_skill)
    scenario_planner.SCENARIO_TEMPLATES[ScenarioType.DESKTOP_FILE] = template
```

### 使用示例

```python
# 通过 Agent 使用
agent = Agent(llm_config, enable_scenario=True)

# 创建文档
result = await agent.execute_task("创建一个包含项目报告的 Word 文档")

# 编辑文档
result = await agent.execute_task("将 contract.docx 中的日期从2024改为2025")

# 提取内容
result = await agent.execute_task("从 report.docx 中提取所有表格")
```

## 总结

DOCX Skills 提供了**完整的 Word 文档处理能力**：

✅ **创建**：从零创建专业文档  
✅ **编辑**：修改现有文档（支持修订模式）  
✅ **分析**：提取和分析文档内容  
✅ **转换**：转换为其他格式（PDF、Markdown、图片）  
✅ **注释**：添加和管理注释  
✅ **格式**：完整的格式控制  
✅ **媒体**：处理嵌入的图片和媒体  

这使得系统可以处理各种 Word 文档相关的自动化任务，从简单的文本提取到复杂的文档审查和修订。
