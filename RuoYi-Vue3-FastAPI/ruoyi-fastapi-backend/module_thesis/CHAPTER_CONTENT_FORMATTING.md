# 章节内容格式化说明（Chapter Content Formatting Guide）

## 一、章节内容结构示例

以下是一个典型的章节内容示例：

```
本章作为全文的摘要部分，旨在系统概括本论文的研究动因、核心内容、方法路径与预期贡献。人工智能（Artificial Intelligence, AI）作为21世纪最具变革性的技术之一，正以前所未有的速度重塑社会结构、经济模式与人类生活方式。在此背景下，深入理解其发展脉络、技术逻辑、应用现状及潜在挑战，不仅具有重要的理论价值，也对政策制定、产业实践与公众认知具有现实指导意义。本文立足于本科阶段的学术训练要求，通过文献综述、案例分析与比较研究等方法，对人工智能的关键技术、典型应用场景及其社会影响进行系统梳理与初步探讨，力求在有限篇幅内呈现一个结构清晰、内容充实且具有批判性思考的研究框架。

## 1.1 研究背景与意义

人工智能的概念自20世纪50年代提出以来，经历了多次"寒冬"与"复兴"的周期性演进。早期以符号主义为主导的AI研究聚焦于逻辑推理与知识表示，虽在特定领域取得突破，但受限于计算能力与数据规模，难以实现通用智能。进入21世纪后，随着**大数据**、**高性能计算**和**深度学习**算法的协同发展，人工智能迎来了第三次发展浪潮。

## 1.2 研究内容与方法概述

本论文围绕"人工智能的发展现状、应用实践与社会影响"这一核心议题，构建了由引言、文献综述、研究方法、研究结果、讨论与结论组成的六大部分研究框架。
```

## 二、格式化代码的处理逻辑

### 2.1 内容解析流程

格式化代码会按照以下流程处理章节内容：

1. **按行分割**：`content_lines = chapter.content.split('\n')`
2. **逐行处理**：
   - 空行 → 添加空段落
   - Markdown标题（## 或 ###）→ 应用标题格式
   - 普通段落 → 应用段落格式

### 2.2 Markdown标题识别

代码能够识别以下Markdown标题格式：

- **二级标题**：`## 标题文本`
- **三级标题**：`### 标题文本`

**识别逻辑**：
```python
if line.startswith('##'):
    # 二级标题
    heading_text = line.lstrip('#').strip()
    # 应用h2格式
elif line.startswith('###'):
    # 三级标题
    heading_text = line.lstrip('#').strip()
    # 应用h3格式
```

### 2.3 格式应用对应关系

| 内容类型 | 识别方式 | 格式指令字段 | 应用位置 |
|---------|---------|------------|---------|
| 普通段落 | 非空行且不以##开头 | `paragraph` | 段落文本 |
| Markdown ## | `line.startswith('##')` | `headings.h2` | 二级标题 |
| Markdown ### | `line.startswith('###')` | `headings.h3` | 三级标题 |
| Markdown加粗 | `**文本**` | 段落格式+加粗 | 段落中的加粗文本 |

## 三、示例内容的格式化过程

### 3.1 处理流程

对于您提供的章节内容示例：

**第1行**（普通段落）：
```
本章作为全文的摘要部分，旨在系统概括本论文的研究动因...
```
- 识别：普通段落
- 应用：`paragraph` 格式（宋体12磅，1.5倍行距，首行缩进24磅）

**第2行**（空行）：
```
（空行）
```
- 识别：空行
- 处理：添加空段落

**第3行**（Markdown二级标题）：
```
## 1.1 研究背景与意义
```
- 识别：Markdown二级标题（`##`开头）
- 应用：`headings.h2` 格式（如：黑体14磅加粗左对齐）
- 布局：应用 `layout_rules.heading_spacing.h2.after`（标题后空行）

**第4行**（普通段落）：
```
人工智能的概念自20世纪50年代提出以来...
```
- 识别：普通段落
- 应用：`paragraph` 格式
- 处理：识别并应用Markdown加粗（`**大数据**`、`**高性能计算**`等）

**第5行**（Markdown二级标题）：
```
## 1.2 研究内容与方法概述
```
- 识别：Markdown二级标题
- 应用：`headings.h2` 格式

### 3.2 格式应用细节

#### 3.2.1 普通段落格式

普通段落会应用以下格式（从指令中获取）：

```python
# 字体
run.font.name = default_font_name  # 从 format_rules.font.name 获取
run.font.size = default_font_size  # 从 format_rules.font.size 获取

# 段落格式
para.alignment = para_config.get('alignment', 'left')
para.paragraph_format.line_spacing = para_config.get('line_spacing', 1.5)
para.paragraph_format.first_line_indent = Pt(para_config.get('first_line_indent', 24))
```

#### 3.2.2 Markdown标题格式

Markdown标题（## 或 ###）会应用对应级别的标题格式：

```python
# 二级标题（##）
if headings_config and 'h2' in headings_config:
    h2_style = headings_config['h2']
    heading_run.font.size = Pt(h2_style.get('font_size', 14))
    heading_run.font.name = h2_style.get('font_name', '黑体')
    heading_run.font.bold = h2_style.get('bold', True)
    
    # 应用段间距
    if 'spacing_before' in h2_style:
        heading_para.paragraph_format.space_before = Pt(h2_style['spacing_before'])
    if 'spacing_after' in h2_style:
        heading_para.paragraph_format.space_after = Pt(h2_style['spacing_after'])
    
    # 应用布局规则（标题后空行）
    h2_spacing_config = heading_spacing.get('h2', {})
    after_h2_lines = h2_spacing_config.get('after', 0)
    for _ in range(after_h2_lines):
        doc.add_paragraph()
```

#### 3.2.3 Markdown加粗格式

段落中的 `**文本**` 会被识别并应用加粗：

```python
# 处理Markdown加粗
parts = re.split(r'(\*\*.*?\*\*)', line)
for part in parts:
    if part.startswith('**') and part.endswith('**'):
        # 加粗文本
        bold_text = part.strip('*')
        run = para.add_run(bold_text)
        run.font.bold = True
    else:
        # 普通文本
        run = para.add_run(part)
```

## 四、格式化指令与章节内容的对应关系

### 4.1 完整对应表

| 章节内容特征 | 识别方式 | 格式指令字段 | 应用结果 |
|------------|---------|------------|---------|
| 普通文本段落 | 非空行，不以##开头 | `format_rules.paragraph` | 宋体12磅，1.5倍行距，首行缩进24磅 |
| `## 1.1 标题` | `line.startswith('##')` | `format_rules.headings.h2` | 黑体14磅加粗左对齐 |
| `### 1.1.1 标题` | `line.startswith('###')` | `format_rules.headings.h3` | 黑体12磅加粗左对齐 |
| `**加粗文本**` | `re.split(r'(\*\*.*?\*\*)')` | 段落格式+加粗 | 文本加粗显示 |
| 空行 | `line.strip() == ''` | 无 | 添加空段落 |

### 4.2 布局规则应用

| 布局规则 | 指令字段 | 应用位置 | 示例 |
|---------|---------|---------|------|
| 章节标题后空行 | `layout_rules.heading_spacing.h1.after` | 章节标题后 | 如果after=1，标题后空1行 |
| Markdown二级标题后空行 | `layout_rules.heading_spacing.h2.after` | `## 标题`后 | 如果after=1，标题后空1行 |
| Markdown三级标题后空行 | `layout_rules.heading_spacing.h3.after` | `### 标题`后 | 如果after=0，标题后不空行 |
| 段落之间空行 | `layout_rules.paragraph_spacing.between_paragraphs` | 段落之间 | 如果between_paragraphs=0，段落之间不空行 |

## 五、格式化结果示例

对于您提供的章节内容，格式化后的结果应该是：

### 5.1 格式化后的文档结构

```
[章节标题：摘要]（应用headings.h1格式）
[空行]（根据layout_rules.heading_spacing.h1.after）

[普通段落1]（应用paragraph格式）
人工智能（Artificial Intelligence, AI）作为21世纪最具变革性的技术之一...

[空行]

[二级标题：## 1.1 研究背景与意义]（应用headings.h2格式）
[空行]（根据layout_rules.heading_spacing.h2.after）

[普通段落2]（应用paragraph格式）
人工智能的概念自20世纪50年代提出以来...**大数据**、**高性能计算**和**深度学习**...

[空行]

[二级标题：## 1.2 研究内容与方法概述]（应用headings.h2格式）
[空行]（根据layout_rules.heading_spacing.h2.after）

[普通段落3]（应用paragraph格式）
本论文围绕"人工智能的发展现状、应用实践与社会影响"...
```

### 5.2 格式应用细节

1. **普通段落**：
   - 字体：宋体（从 `format_rules.font.name` 获取）
   - 字号：12磅（从 `format_rules.font.size` 获取）
   - 行距：1.5倍（从 `format_rules.paragraph.line_spacing` 获取）
   - 首行缩进：24磅（从 `format_rules.paragraph.first_line_indent` 获取）
   - 对齐：左对齐（从 `format_rules.paragraph.alignment` 获取）

2. **Markdown二级标题（##）**：
   - 字体：黑体（从 `format_rules.headings.h2.font_name` 获取）
   - 字号：14磅（从 `format_rules.headings.h2.font_size` 获取）
   - 加粗：是（从 `format_rules.headings.h2.bold` 获取）
   - 对齐：左对齐（从 `format_rules.headings.h2.alignment` 获取）
   - 标题后空行：根据 `layout_rules.heading_spacing.h2.after` 决定

3. **Markdown加粗（**文本**）**：
   - 在普通段落中，`**大数据**` 会被识别为加粗文本
   - 应用段落格式，但文本加粗显示

## 六、验证点

### 6.1 格式应用验证

格式化代码能够：

1. ✅ **识别Markdown标题**：正确识别 `##` 和 `###` 开头的行
2. ✅ **应用标题格式**：根据标题级别应用对应的 `headings.h2` 或 `headings.h3` 格式
3. ✅ **应用段落格式**：普通段落应用 `paragraph` 格式
4. ✅ **处理Markdown加粗**：识别并应用 `**文本**` 加粗格式
5. ✅ **应用布局规则**：根据 `layout_rules` 应用空行、间距等

### 6.2 章节内容对应验证

章节内容能够：

1. ✅ **正确对应格式指令**：每种内容类型都能找到对应的格式指令字段
2. ✅ **正确应用格式**：格式指令中的值能正确应用到文档中
3. ✅ **支持布局规则**：空行、间距等布局规则能正确应用

## 七、总结

格式化代码能够：

1. ✅ **正确识别章节内容结构**：识别普通段落、Markdown标题、空行等
2. ✅ **正确应用格式指令**：根据内容类型应用对应的格式指令
3. ✅ **正确应用布局规则**：根据 `layout_rules` 应用空行、间距等
4. ✅ **支持Markdown格式**：支持Markdown标题和加粗格式

**关键保证**：
- 章节内容中的Markdown标题（##、###）能正确识别并应用格式
- 普通段落能正确应用段落格式
- 布局规则能正确应用到标题后、段落之间等位置
- 章节内容与格式指令能够一一对应
