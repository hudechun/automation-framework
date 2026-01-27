# 指令系统设计原则与改进方案

## 一、问题分析

### 1.1 当前问题

**用户提出的关键问题**：
1. ❌ **生成的指令可能不准确**：AI提取的格式信息可能不完整或错误
2. ❌ **转换逻辑不靠谱**：硬编码的转换逻辑无法适应不同学校的要求
3. ❌ **缺乏通用性**：换一个学校就需要修改代码
4. ❌ **指令系统未充分利用**：指令系统没有充分运用到大纲和章节内容生成

### 1.2 根本原因

**设计缺陷**：
- 指令系统是**被动的**：只在格式化时使用
- 转换逻辑是**硬编码的**：依赖代码中的固定规则
- 缺乏**描述性规则**：没有通过指令系统本身描述格式要求

---

## 二、指令系统设计原则

### 2.1 核心原则

#### 原则1：指令系统应该是**描述性的**，而不是**转换性的**

**当前问题**：
- 使用硬编码的转换逻辑（如：1.1 → 第一章）
- 依赖代码中的固定规则

**改进方向**：
- 指令系统应该**描述格式要求**（如：一级标题使用"第X章"格式）
- 格式化代码根据指令**应用格式**，而不是转换格式

#### 原则2：指令系统应该**主动参与**整个流程

**当前问题**：
- 指令系统只在格式化时使用
- 大纲和章节生成时没有使用指令系统

**改进方向**：
- **大纲生成时**：根据指令系统生成符合格式要求的大纲结构
- **章节生成时**：根据指令系统生成符合格式要求的章节内容
- **格式化时**：根据指令系统应用格式

#### 原则3：指令系统应该**完全通用**，不依赖硬编码

**当前问题**：
- 转换逻辑硬编码在代码中
- 不同学校需要不同的转换逻辑

**改进方向**：
- 所有格式要求都通过指令系统描述
- 格式化代码只负责**应用**指令，不负责**转换**

---

## 三、指令系统如何运用到大纲和章节内容

### 3.1 大纲生成阶段

**当前流程**：
```
用户输入论文信息 → AI生成大纲 → 保存大纲
```

**改进流程**：
```
用户输入论文信息 → 读取格式指令 → AI根据指令生成符合格式要求的大纲 → 保存大纲
```

**指令系统的作用**：
1. **章节编号格式**：告诉AI使用"第一章"还是"1.1"格式
2. **章节结构**：告诉AI需要哪些章节（摘要、关键词、正文、结论等）
3. **标题层级**：告诉AI标题的层级关系

**实现方式**：
```python
async def generate_outline(thesis_info, format_instructions):
    # 1. 解析格式指令
    format_config = json.loads(format_instructions)
    
    # 2. 提取章节结构要求
    document_structure = format_config.get('application_rules', {}).get('document_structure', {})
    section_order = document_structure.get('section_order', [])
    required_sections = document_structure.get('required_sections', [])
    
    # 3. 提取章节编号格式要求
    heading_detection = format_config.get('application_rules', {}).get('heading_detection', '')
    
    # 4. 构建提示词，告诉AI格式要求
    prompt = f"""
    根据以下格式要求生成论文大纲：
    
    章节结构顺序：{', '.join(section_order)}
    必填章节：{', '.join(required_sections)}
    章节编号格式：{heading_detection}
    
    请生成符合以上格式要求的大纲。
    """
    
    # 5. AI生成大纲（已经符合格式要求）
    outline = await ai.generate(prompt)
    
    return outline
```

---

### 3.2 章节内容生成阶段

**当前流程**：
```
大纲 → AI生成章节内容 → 保存章节
```

**改进流程**：
```
大纲 → 读取格式指令 → AI根据指令生成符合格式要求的章节内容 → 保存章节
```

**指令系统的作用**：
1. **标题格式**：告诉AI标题应该使用什么格式（字体、字号、对齐等）
2. **段落格式**：告诉AI段落应该使用什么格式（行距、缩进等）
3. **特殊章节格式**：告诉AI摘要、关键词等特殊章节的格式要求

**实现方式**：
```python
async def generate_chapter(chapter_info, format_instructions):
    # 1. 解析格式指令
    format_config = json.loads(format_instructions)
    
    # 2. 提取章节格式要求
    chapter_level = chapter_info.get('level', 1)
    heading_config = format_config.get('headings', {}).get(f'h{chapter_level}', {})
    
    # 3. 提取段落格式要求
    paragraph_config = format_config.get('paragraph', {})
    
    # 4. 构建提示词，告诉AI格式要求
    prompt = f"""
    根据以下格式要求生成章节内容：
    
    标题格式：
    - 字体：{heading_config.get('font_name', '黑体')}
    - 字号：{heading_config.get('font_size_pt', 14)}磅
    - 对齐：{heading_config.get('alignment', 'left')}
    
    段落格式：
    - 行距：{paragraph_config.get('line_spacing', 1.5)}倍
    - 首行缩进：{paragraph_config.get('first_line_indent_chars', 0)}字符
    
    请生成符合以上格式要求的章节内容。
    """
    
    # 5. AI生成章节内容（已经符合格式要求）
    chapter_content = await ai.generate(prompt)
    
    return chapter_content
```

---

### 3.3 格式化阶段

**当前流程**：
```
章节内容 → 读取格式指令 → 应用格式 → 生成文档
```

**改进流程**：
```
章节内容（已经符合格式要求） → 读取格式指令 → 应用格式 → 生成文档
```

**指令系统的作用**：
1. **应用格式**：根据指令应用字体、字号、对齐等格式
2. **验证格式**：验证内容是否符合格式要求
3. **调整格式**：如果不符合，进行微调

---

## 四、改进方案

### 4.1 指令系统增强：添加格式描述规则

**当前指令系统**：
- 只描述格式属性（字体、字号等）
- 不描述格式规则（章节编号格式、标题格式等）

**改进方案**：
在指令系统中添加**格式描述规则**，而不是转换规则：

```json
{
  "application_rules": {
    "heading_detection": "通过段落前缀数字识别层级",
    
    // 添加：章节编号格式描述（而不是转换规则）
    "chapter_numbering_format": {
      "level_1": {
        "format_type": "chinese_chapter",  // 中文章节格式：第X章
        "pattern": "第{number}章 {title}",  // 格式模板
        "number_style": "chinese"  // 数字样式：chinese/arabic/roman
      },
      "level_2": {
        "format_type": "numbered",  // 数字格式：1.1
        "pattern": "{parent}.{number} {title}",
        "number_style": "arabic"
      }
    },
    
    // 添加：标题格式描述
    "heading_format_rules": {
      "level_1": {
        "title_prefix": "第",  // 标题前缀
        "title_suffix": "章",  // 标题后缀
        "number_position": "before_title"  // 编号位置：before_title/after_title/none
      }
    },
    
    // 移除：chapter_numbering_conversion（转换规则）
    // 改为：通过格式描述规则，让AI在生成时就使用正确的格式
  }
}
```

---

### 4.2 大纲生成改进：根据指令生成

**改进前**：
```python
# AI生成大纲，格式可能不符合要求
outline = await ai.generate_outline(thesis_info)
```

**改进后**：
```python
# 1. 读取格式指令
format_instructions = await get_format_instructions(template_id)

# 2. 提取格式要求
chapter_numbering_format = format_instructions.get('application_rules', {}).get('chapter_numbering_format', {})

# 3. 告诉AI格式要求
prompt = f"""
生成论文大纲，要求：
1. 一级标题使用格式：{chapter_numbering_format.get('level_1', {}).get('pattern', '第X章 标题')}
2. 二级标题使用格式：{chapter_numbering_format.get('level_2', {}).get('pattern', 'X.Y 标题')}
3. 必须包含以下章节：{required_sections}
"""

# 4. AI生成符合格式要求的大纲
outline = await ai.generate_outline(thesis_info, format_requirements=prompt)
```

---

### 4.3 章节生成改进：根据指令生成

**改进前**：
```python
# AI生成章节内容，格式可能不符合要求
chapter_content = await ai.generate_chapter(chapter_info)
```

**改进后**：
```python
# 1. 读取格式指令
format_instructions = await get_format_instructions(template_id)

# 2. 提取章节格式要求
heading_config = format_instructions.get('headings', {}).get(f'h{chapter_level}', {})
paragraph_config = format_instructions.get('paragraph', {})

# 3. 告诉AI格式要求
prompt = f"""
生成章节内容，要求：
1. 标题格式：{heading_config.get('font_name')} {heading_config.get('font_size_pt')}磅，{heading_config.get('alignment')}对齐
2. 段落格式：行距{paragraph_config.get('line_spacing')}倍，首行缩进{paragraph_config.get('first_line_indent_chars')}字符
"""

# 4. AI生成符合格式要求的章节内容
chapter_content = await ai.generate_chapter(chapter_info, format_requirements=prompt)
```

---

### 4.4 格式化改进：只应用格式，不转换格式

**改进前**：
```python
# 1. 获取章节
chapters = get_chapters()

# 2. 转换格式（硬编码）
chapters = convert_chapter_numbering(chapters)  # 1.1 → 第一章

# 3. 应用格式
apply_format(chapters, format_instructions)
```

**改进后**：
```python
# 1. 获取章节（已经符合格式要求）
chapters = get_chapters()

# 2. 直接应用格式（不需要转换）
apply_format(chapters, format_instructions)
```

---

## 五、指令系统设计改进

### 5.1 添加格式描述规则

在 `application_rules` 中添加：

```json
{
  "application_rules": {
    "heading_detection": "标题识别规则",
    
    // 新增：章节编号格式描述
    "chapter_numbering_format": {
      "level_1": {
        "format_type": "chinese_chapter/numbered/roman",
        "pattern": "格式模板（如：第{number}章 {title}）",
        "number_style": "chinese/arabic/roman",
        "examples": ["第一章 引言", "第二章 研究背景"]
      },
      "level_2": {
        "format_type": "numbered",
        "pattern": "{parent}.{number} {title}",
        "number_style": "arabic",
        "examples": ["1.1 研究背景", "1.2 研究意义"]
      }
    },
    
    // 新增：标题格式规则
    "heading_format_rules": {
      "level_1": {
        "title_prefix": "第",
        "title_suffix": "章",
        "number_position": "before_title",
        "separator": " "  // 编号和标题之间的分隔符
      }
    },
    
    // 新增：特殊章节格式规则
    "special_section_format_rules": {
      "abstract": {
        "title": "摘要",
        "should_have_numbering": false,
        "position": "after_toc"
      },
      "conclusion": {
        "title": "结语",  // 不是"结论"
        "should_have_numbering": false,
        "position": "before_references"
      },
      "references": {
        "title": "参考文献",
        "should_have_numbering": false,
        "position": "before_appendix"
      }
    }
  }
}
```

---

### 5.2 移除转换逻辑

**移除**：
- `chapter_numbering_conversion`（转换规则）
- `abstract_extraction`（提取规则）

**改为**：
- 通过格式描述规则，让AI在生成时就使用正确的格式
- 格式化时只应用格式，不转换格式

---

## 六、实现建议

### 6.1 大纲生成时使用指令系统

```python
async def generate_outline(thesis_info, template_id):
    # 1. 读取格式指令
    template = await get_template(template_id)
    format_instructions = json.loads(template.format_data)
    
    # 2. 提取格式要求
    chapter_numbering = format_instructions.get('application_rules', {}).get('chapter_numbering_format', {})
    document_structure = format_instructions.get('application_rules', {}).get('document_structure', {})
    
    # 3. 构建格式要求提示词
    format_requirements = f"""
    格式要求：
    1. 一级标题格式：{chapter_numbering.get('level_1', {}).get('pattern', '第X章 标题')}
    2. 二级标题格式：{chapter_numbering.get('level_2', {}).get('pattern', 'X.Y 标题')}
    3. 章节顺序：{', '.join(document_structure.get('section_order', []))}
    """
    
    # 4. AI生成符合格式要求的大纲
    outline = await ai.generate_outline(thesis_info, format_requirements)
    
    return outline
```

---

### 6.2 章节生成时使用指令系统

```python
async def generate_chapter(chapter_info, template_id):
    # 1. 读取格式指令
    template = await get_template(template_id)
    format_instructions = json.loads(template.format_data)
    
    # 2. 提取章节格式要求
    chapter_level = chapter_info.get('level', 1)
    heading_config = format_instructions.get('headings', {}).get(f'h{chapter_level}', {})
    paragraph_config = format_instructions.get('paragraph', {})
    
    # 3. 构建格式要求提示词
    format_requirements = f"""
    格式要求：
    1. 标题：{heading_config.get('font_name')} {heading_config.get('font_size_pt')}磅，{heading_config.get('alignment')}对齐
    2. 段落：行距{paragraph_config.get('line_spacing')}倍，首行缩进{paragraph_config.get('first_line_indent_chars')}字符
    """
    
    # 4. AI生成符合格式要求的章节内容
    chapter_content = await ai.generate_chapter(chapter_info, format_requirements)
    
    return chapter_content
```

---

### 6.3 格式化时只应用格式

```python
async def format_thesis(chapters, format_instructions):
    # 1. 读取格式指令
    format_config = json.loads(format_instructions)
    
    # 2. 直接应用格式（不需要转换）
    # 因为大纲和章节生成时已经使用了正确的格式
    apply_format(chapters, format_config)
    
    # 3. 生成文档
    generate_document(chapters)
```

---

## 七、总结

### ✅ 改进方向

1. **指令系统应该是描述性的**：
   - 描述格式要求（章节编号格式、标题格式等）
   - 不描述转换规则

2. **指令系统应该主动参与**：
   - 大纲生成时使用指令系统
   - 章节生成时使用指令系统
   - 格式化时使用指令系统

3. **移除硬编码的转换逻辑**：
   - 不在代码中硬编码转换规则
   - 通过指令系统描述格式要求
   - AI在生成时就使用正确的格式

### 🎯 核心思想

**"指令系统描述格式要求，AI在生成时就遵循格式要求，格式化时只应用格式"**

这样：
- ✅ 指令系统完全通用
- ✅ 不需要硬编码的转换逻辑
- ✅ 适应不同学校的要求
- ✅ 指令系统充分运用到大纲和章节内容
