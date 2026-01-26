# Word文档格式识别指南

## 概述

本文档说明如何识别Word文档中的格式要求，包括当前实现方式和可提取的格式信息。

## 识别流程

### 1. 使用 python-docx 读取文档

```python
from docx import Document
doc = Document(word_file_path)
```

### 2. 提取格式信息

当前实现可以识别以下格式要求：

#### 2.1 字体格式
- **字体名称** (`font.name`): 如 "宋体"、"Times New Roman"
- **字体大小** (`font.size`): 以磅为单位，如 12pt、14pt
- **字体颜色** (`font.color.rgb`): RGB颜色值
- **粗体** (`bold`): True/False
- **斜体** (`italic`): True/False
- **下划线** (`underline`): True/False

#### 2.2 段落格式
- **对齐方式** (`alignment`): 
  - `LEFT` (左对齐)
  - `CENTER` (居中)
  - `RIGHT` (右对齐)
  - `JUSTIFY` (两端对齐)
- **行距** (`line_spacing`): 行距值或倍数
- **行距规则** (`line_spacing_rule`): 
  - `SINGLE` (单倍行距)
  - `ONE_POINT_FIVE` (1.5倍行距)
  - `DOUBLE` (双倍行距)
  - `MULTIPLE` (多倍行距)
- **段前间距** (`space_before`): 段落前的间距（磅）
- **段后间距** (`space_after`): 段落后的间距（磅）
- **首行缩进** (`first_line_indent`): 首行缩进量（磅）
- **左缩进** (`left_indent`): 左缩进量（磅）
- **右缩进** (`right_indent`): 右缩进量（磅）

#### 2.3 标题格式
- **标题级别**: 通过样式名称识别（Heading 1, Heading 2, 标题 1, 标题 2等）
- **标题字体**: 标题使用的字体名称和大小
- **标题对齐**: 标题的对齐方式
- **标题样式**: 粗体、斜体等

#### 2.4 页面设置
- **页边距**:
  - `top_margin`: 上边距
  - `bottom_margin`: 下边距
  - `left_margin`: 左边距
  - `right_margin`: 右边距
- **纸张大小**:
  - `page_width`: 页面宽度
  - `page_height`: 页面高度

#### 2.5 样式信息
- **样式名称**: 文档中使用的样式名称
- **样式类型**: 段落样式、字符样式等

## 提取方法

### 方法1: 直接提取（当前实现）

```python
# 提取段落格式
for para in doc.paragraphs:
    # 段落对齐
    alignment = para.alignment
    
    # 段落格式
    if para.paragraph_format:
        line_spacing = para.paragraph_format.line_spacing
        space_before = para.paragraph_format.space_before
        space_after = para.paragraph_format.space_after
        first_line_indent = para.paragraph_format.first_line_indent
    
    # 文本运行格式
    for run in para.runs:
        font_name = run.font.name
        font_size = run.font.size
        bold = run.bold
        italic = run.italic
```

### 方法2: 通过样式提取

```python
# 提取样式信息
for style in doc.styles.styles:
    style_name = style.name
    # 获取样式的默认格式
    if hasattr(style, 'font'):
        default_font = style.font.name
```

### 方法3: 通过节（Section）提取页面设置

```python
# 提取页面设置
section = doc.sections[0]
top_margin = section.top_margin
bottom_margin = section.bottom_margin
left_margin = section.left_margin
right_margin = section.right_margin
page_width = section.page_width
page_height = section.page_height
```

## AI辅助分析

由于Word文档格式复杂，我们使用AI来辅助分析：

### 1. 提取原始格式数据
使用 `python-docx` 提取文档的格式信息（字体、段落、页面等）

### 2. AI分析格式规则
将提取的格式信息发送给AI，让AI分析并生成标准化的格式指令

### 3. 生成格式化指令
AI返回JSON格式的格式化指令，包含：
- 字体设置
- 段落格式
- 标题格式
- 页面设置

## 格式识别示例

### 示例1: 识别正文格式

```python
# 正文段落通常具有以下特征：
# - 样式名称为 "Normal" 或 "正文"
# - 字体：宋体或Times New Roman
# - 字号：12pt
# - 行距：1.5倍或固定值
# - 首行缩进：2字符（约36磅）
```

### 示例2: 识别标题格式

```python
# 标题通常具有以下特征：
# - 样式名称包含 "Heading" 或 "标题"
# - 字体较大（16-18pt）
# - 粗体
# - 居中对齐或左对齐
```

### 示例3: 识别页面设置

```python
# 标准论文格式：
# - 页边距：上2.5cm，下2.5cm，左3cm，右2.5cm
# - 纸张大小：A4 (21cm × 29.7cm)
# - 页眉页脚：可能有页眉页脚设置
```

## 改进建议

### 1. 增强格式识别
- 识别表格格式
- 识别列表格式（项目符号、编号）
- 识别图片格式和位置
- 识别页眉页脚内容

### 2. 样式映射
- 建立样式名称到格式规则的映射
- 识别自定义样式
- 处理样式继承关系

### 3. 格式规则提取
- 提取更详细的格式规则
- 识别格式异常（如不一致的格式）
- 生成格式规范文档

## 注意事项

1. **格式继承**: Word文档中的格式可能继承自样式，需要同时检查段落格式和样式格式
2. **格式覆盖**: 直接格式会覆盖样式格式，需要优先检查直接格式
3. **单位转换**: python-docx 使用不同的单位（磅、英寸等），需要正确转换
4. **空值处理**: 某些格式属性可能为None，需要提供默认值

## 相关代码

- `format_service.py`: 格式提取和分析服务
- `_extract_document_content()`: 提取文档格式信息
- `_analyze_format_with_ai()`: 使用AI分析格式
- `_build_format_analysis_prompt()`: 构建AI提示词
