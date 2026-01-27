# 指令系统改进方案

## 一、问题分析

### 1.1 当前问题

**用户提出的关键问题**：
1. ❌ **生成的指令可能不准确**：AI提取的格式信息可能不完整或错误
2. ❌ **转换逻辑不靠谱**：硬编码的转换逻辑（如1.1→第一章）无法适应不同学校
3. ❌ **缺乏通用性**：换一个学校就需要修改代码
4. ❌ **指令系统未充分利用**：指令系统没有运用到大纲和章节内容生成

### 1.2 根本原因

**设计缺陷**：
- 指令系统是**被动的**：只在格式化时使用
- 转换逻辑是**硬编码的**：依赖代码中的固定规则
- 缺乏**描述性规则**：没有通过指令系统本身描述格式要求

---

## 二、改进方案

### 2.1 核心思想

**"指令系统描述格式要求，AI在生成时就遵循格式要求，格式化时只应用格式"**

**改进前**：
```
大纲生成 → 章节生成 → 格式化（转换格式） → 应用格式
```

**改进后**：
```
读取格式指令 → 大纲生成（根据指令） → 章节生成（根据指令） → 格式化（只应用格式）
```

---

### 2.2 指令系统改进：从转换规则改为格式描述规则

#### 改进前（转换规则）：
```json
{
  "chapter_numbering_conversion": {
    "enabled": true,
    "source_format": "X.Y",
    "target_format": "第X章",
    "conversion_pattern": "^\\d+\\.\\d+\\s+(.+)$"
  }
}
```

**问题**：
- 这是转换规则，不是格式描述
- 依赖硬编码的转换逻辑
- 不同学校需要不同的转换规则

#### 改进后（格式描述规则）：
```json
{
  "chapter_numbering_format": {
    "level_1": {
      "format_type": "chinese_chapter",
      "pattern": "第{number}章 {title}",
      "number_style": "chinese",
      "examples": ["第一章 引言", "第二章 研究背景"]
    },
    "level_2": {
      "format_type": "numbered",
      "pattern": "{parent}.{number} {title}",
      "number_style": "arabic",
      "examples": ["1.1 研究背景", "1.2 研究意义"]
    }
  },
  "special_section_format_rules": {
    "conclusion": {
      "title": "结语",
      "should_have_numbering": false,
      "position": "before_references"
    }
  }
}
```

**优势**：
- ✅ 这是格式描述，不是转换规则
- ✅ 不依赖硬编码的转换逻辑
- ✅ 不同学校有不同的格式描述
- ✅ AI可以根据格式描述生成正确格式的内容

---

### 2.3 大纲生成改进：根据指令生成

#### 改进前：
```python
# AI生成大纲，格式可能不符合要求
outline = await ai.generate_outline(thesis_info)
```

#### 改进后：
```python
async def generate_outline(thesis_info, template_id):
    # 1. 读取格式指令
    template = await get_template(template_id)
    format_instructions = json.loads(template.format_data)
    
    # 2. 提取格式要求
    chapter_numbering = format_instructions.get('application_rules', {}).get('chapter_numbering_format', {})
    document_structure = format_instructions.get('application_rules', {}).get('document_structure', {})
    special_sections = format_instructions.get('application_rules', {}).get('special_section_format_rules', {})
    
    # 3. 构建格式要求提示词
    format_requirements = f"""
    请根据以下格式要求生成论文大纲：
    
    **章节编号格式**：
    - 一级标题：{chapter_numbering.get('level_1', {}).get('pattern', '第X章 标题')}
      示例：{', '.join(chapter_numbering.get('level_1', {}).get('examples', []))}
    - 二级标题：{chapter_numbering.get('level_2', {}).get('pattern', 'X.Y 标题')}
      示例：{', '.join(chapter_numbering.get('level_2', {}).get('examples', []))}
    
    **章节结构顺序**：
    {', '.join(document_structure.get('section_order', []))}
    
    **特殊章节格式**：
    - 结论：{special_sections.get('conclusion', {}).get('title', '结论')}（无编号）
    - 参考文献：{special_sections.get('references', {}).get('title', '参考文献')}（无编号）
    
    **重要**：请严格按照以上格式要求生成大纲，确保：
    1. 一级标题使用指定的格式（如：第一章、第二章）
    2. 二级标题使用指定的格式（如：1.1、1.2）
    3. 特殊章节（结论、参考文献）不使用章节编号
    4. 章节顺序符合要求
    """
    
    # 4. AI生成符合格式要求的大纲
    outline = await ai.generate_outline(thesis_info, format_requirements)
    
    return outline
```

---

### 2.4 章节生成改进：根据指令生成

#### 改进前：
```python
# AI生成章节内容，格式可能不符合要求
chapter_content = await ai.generate_chapter(chapter_info)
```

#### 改进后：
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
    请根据以下格式要求生成章节内容：
    
    **标题格式**：
    - 字体：{heading_config.get('font_name', '黑体')}
    - 字号：{heading_config.get('font_size_pt', 14)}磅
    - 对齐：{heading_config.get('alignment', 'left')}
    - 加粗：{heading_config.get('bold', True)}
    
    **段落格式**：
    - 字体：{format_instructions.get('default_font', {}).get('name', '宋体')}
    - 字号：{format_instructions.get('default_font', {}).get('size_pt', 12)}磅
    - 行距：{paragraph_config.get('line_spacing', 1.5)}倍
    - 首行缩进：{paragraph_config.get('first_line_indent_chars', 0)}字符
    - 对齐：{paragraph_config.get('alignment', 'justify')}
    
    **重要**：请确保生成的内容符合以上格式要求。
    """
    
    # 4. AI生成符合格式要求的章节内容
    chapter_content = await ai.generate_chapter(chapter_info, format_requirements)
    
    return chapter_content
```

---

### 2.5 格式化改进：只应用格式，不转换格式

#### 改进前：
```python
# 1. 获取章节
chapters = get_chapters()

# 2. 转换格式（硬编码）
chapters = convert_chapter_numbering(chapters)  # 1.1 → 第一章

# 3. 应用格式
apply_format(chapters, format_instructions)
```

#### 改进后：
```python
# 1. 获取章节（已经符合格式要求，因为生成时使用了指令）
chapters = get_chapters()

# 2. 直接应用格式（不需要转换）
apply_format(chapters, format_instructions)
```

---

## 三、指令系统设计改进

### 3.1 移除转换规则，添加格式描述规则

**移除**：
- `chapter_numbering_conversion`（转换规则）
- `abstract_extraction`（提取规则）

**添加**：
- `chapter_numbering_format`（格式描述规则）
- `special_section_format_rules`（特殊章节格式规则）

### 3.2 格式描述规则结构

```json
{
  "application_rules": {
    "chapter_numbering_format": {
      "level_1": {
        "format_type": "chinese_chapter/numbered/roman",
        "pattern": "第{number}章 {title}",
        "number_style": "chinese",
        "examples": ["第一章 引言", "第二章 研究背景"]
      },
      "level_2": {
        "format_type": "numbered",
        "pattern": "{parent}.{number} {title}",
        "number_style": "arabic",
        "examples": ["1.1 研究背景", "1.2 研究意义"]
      }
    },
    "special_section_format_rules": {
      "abstract": {
        "title": "摘要",
        "should_have_numbering": false,
        "position": "after_toc"
      },
      "conclusion": {
        "title": "结语",
        "should_have_numbering": false,
        "position": "before_references"
      }
    }
  }
}
```

---

## 四、实现建议

### 4.1 大纲生成时使用指令系统

**修改位置**：`ai_generation_service.py` 的 `generate_outline()` 方法

**实现**：
```python
async def generate_outline(thesis_info, template_id=None):
    # 1. 如果有模板ID，读取格式指令
    format_requirements = ""
    if template_id:
        template = await get_template(template_id)
        format_instructions = json.loads(template.format_data)
        
        # 提取格式要求
        chapter_numbering = format_instructions.get('application_rules', {}).get('chapter_numbering_format', {})
        document_structure = format_instructions.get('application_rules', {}).get('document_structure', {})
        
        # 构建格式要求提示词
        format_requirements = f"""
        格式要求：
        1. 一级标题格式：{chapter_numbering.get('level_1', {}).get('pattern', '第X章 标题')}
        2. 二级标题格式：{chapter_numbering.get('level_2', {}).get('pattern', 'X.Y 标题')}
        3. 章节顺序：{', '.join(document_structure.get('section_order', []))}
        """
    
    # 2. 构建提示词（包含格式要求）
    prompt = build_outline_prompt(thesis_info, format_requirements)
    
    # 3. AI生成符合格式要求的大纲
    outline = await ai.generate(prompt)
    
    return outline
```

---

### 4.2 章节生成时使用指令系统

**修改位置**：`ai_generation_service.py` 的 `generate_chapter()` 方法

**实现**：
```python
async def generate_chapter(chapter_info, template_id=None):
    # 1. 如果有模板ID，读取格式指令
    format_requirements = ""
    if template_id:
        template = await get_template(template_id)
        format_instructions = json.loads(template.format_data)
        
        # 提取章节格式要求
        chapter_level = chapter_info.get('level', 1)
        heading_config = format_instructions.get('headings', {}).get(f'h{chapter_level}', {})
        paragraph_config = format_instructions.get('paragraph', {})
        
        # 构建格式要求提示词
        format_requirements = f"""
        格式要求：
        1. 标题：{heading_config.get('font_name')} {heading_config.get('font_size_pt')}磅，{heading_config.get('alignment')}对齐
        2. 段落：行距{paragraph_config.get('line_spacing')}倍，首行缩进{paragraph_config.get('first_line_indent_chars')}字符
        """
    
    # 2. 构建提示词（包含格式要求）
    prompt = build_chapter_prompt(chapter_info, format_requirements)
    
    # 3. AI生成符合格式要求的章节内容
    chapter_content = await ai.generate(prompt)
    
    return chapter_content
```

---

### 4.3 格式化时移除转换逻辑

**修改位置**：`format_service.py` 的 `format_thesis()` 方法

**实现**：
```python
# 移除转换逻辑
# 因为大纲和章节生成时已经使用了正确的格式

# 直接应用格式
apply_format(chapters, format_config)
```

---

## 五、优势总结

### ✅ 改进后的优势

1. **完全通用**：
   - 不同学校有不同的格式描述
   - 不需要硬编码的转换逻辑
   - 适应所有学校的格式要求

2. **指令系统充分运用**：
   - 大纲生成时使用指令系统
   - 章节生成时使用指令系统
   - 格式化时使用指令系统

3. **准确性提高**：
   - AI在生成时就使用正确的格式
   - 不需要后续转换
   - 减少格式错误

4. **可维护性提高**：
   - 不需要修改代码
   - 只需要更新格式指令
   - 易于扩展和维护

---

## 六、总结

### ✅ 核心改进

1. **指令系统从转换规则改为格式描述规则**
2. **大纲生成时使用指令系统**
3. **章节生成时使用指令系统**
4. **格式化时只应用格式，不转换格式**

### 🎯 设计原则

- **描述性**：指令系统描述格式要求，而不是转换规则
- **主动性**：指令系统主动参与整个流程（大纲、章节、格式化）
- **通用性**：不依赖硬编码，适应所有学校的要求

**结论**：✅ **改进后的指令系统更加通用、可靠，可以适应所有学校的格式要求！**
