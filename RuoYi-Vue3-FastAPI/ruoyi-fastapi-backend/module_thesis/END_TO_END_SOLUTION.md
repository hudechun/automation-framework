# 端到端动态格式化方案

## 一、核心思想

**"一次性生成准确的指令、大纲和章节内容，格式化时直接应用，无需转换"**

### 1.1 当前问题

**多步骤、多验证的问题**：
1. ❌ 指令提取可能不准确（字体大小异常）
2. ❌ 大纲生成可能不符合格式（章节标题格式）
3. ❌ 章节生成可能不符合格式
4. ❌ 格式化时需要转换和纠正

**结果**：需要多次验证和纠正，容易出错

---

### 1.2 目标方案

**端到端、一次生成、直接应用**：
1. ✅ 从格式模板提取准确的指令（带验证）
2. ✅ 根据指令生成符合格式的大纲（严格约束）
3. ✅ 根据指令生成符合格式的章节内容（严格约束）
4. ✅ 格式化时直接应用，无需转换

**结果**：一次性生成准确，格式化时直接应用

---

## 二、设计方案

### 2.1 方案架构

```
格式模板上传
    ↓
[步骤1] AI提取格式指令（带严格验证）
    ↓
[步骤2] 验证和修正指令（自动修正异常值）
    ↓
[步骤3] 保存准确的指令到数据库
    ↓
[步骤4] 根据指令生成大纲（严格遵循格式要求）
    ↓
[步骤5] 根据指令生成章节内容（严格遵循格式要求）
    ↓
[步骤6] 格式化时直接应用指令（无需转换）
```

---

### 2.2 关键改进点

#### 改进1：指令提取时严格验证

**当前问题**：
- AI提取的指令可能不准确（如字体大小45.72磅）

**改进方案**：
- 提取后立即验证
- 自动修正异常值
- 确保指令准确

**实现**：
```python
async def extract_format_instructions(template_file):
    # 1. AI提取格式指令
    raw_instructions = await ai_extract_format(template_file)
    
    # 2. 立即验证和修正
    validated_instructions = validate_and_fix_instructions(raw_instructions)
    
    # 3. 返回准确的指令
    return validated_instructions
```

---

#### 改进2：大纲生成时严格约束

**当前问题**：
- AI生成的大纲可能不符合格式要求

**改进方案**：
- 在提示词中提供完整的格式示例
- 使用结构化输出（JSON Schema）
- 生成后立即验证和纠正

**实现**：
```python
async def generate_outline(thesis_info, format_instructions):
    # 1. 从指令中提取格式要求
    format_constraints = extract_format_constraints(format_instructions)
    
    # 2. 构建严格约束的提示词
    prompt = build_strict_prompt(thesis_info, format_constraints)
    
    # 3. AI生成大纲（带JSON Schema约束）
    outline = await ai_generate_with_schema(prompt, outline_schema)
    
    # 4. 立即验证和纠正
    validated_outline = validate_and_fix_outline(outline, format_instructions)
    
    return validated_outline
```

---

#### 改进3：章节生成时严格约束

**当前问题**：
- AI生成的章节内容可能不符合格式要求

**改进方案**：
- 在提示词中明确格式要求
- 提供格式示例
- 生成后验证格式

**实现**：
```python
async def generate_chapter(chapter_info, format_instructions):
    # 1. 从指令中提取章节格式要求
    chapter_format = extract_chapter_format(format_instructions, chapter_info)
    
    # 2. 构建严格约束的提示词
    prompt = build_strict_chapter_prompt(chapter_info, chapter_format)
    
    # 3. AI生成章节内容（带格式约束）
    content = await ai_generate_with_format(prompt, chapter_format)
    
    return content
```

---

#### 改进4：格式化时直接应用

**当前问题**：
- 格式化时需要转换和纠正

**改进方案**：
- 因为内容已经符合格式要求，直接应用即可
- 不需要转换逻辑

**实现**：
```python
async def format_thesis(chapters, format_instructions):
    # 直接应用格式（内容已经符合要求）
    formatted_doc = apply_format(chapters, format_instructions)
    return formatted_doc
```

---

## 三、具体实现方案

### 3.1 指令提取增强：严格验证

**文件**：`format_service.py` 的 `read_word_document_with_ai()` 方法

**改进**：
```python
async def read_word_document_with_ai(template_file):
    # 1. AI提取格式指令
    raw_instructions = await ai_extract_format(template_file)
    
    # 2. 立即验证和修正
    validated_instructions = validate_and_fix_format_instructions(raw_instructions)
    
    # 3. 返回准确的指令
    return validated_instructions

def validate_and_fix_format_instructions(instructions):
    """验证和修正格式指令"""
    # 检查字体大小
    if 'format_rules' in instructions:
        format_rules = instructions['format_rules']
        
        # 检查默认字体大小
        if 'default_font' in format_rules:
            size = format_rules['default_font'].get('size_pt', 12)
            if size < 8 or size > 30:
                logger.warning(f"字体大小异常: {size}磅，修正为12磅")
                format_rules['default_font']['size_pt'] = 12
        
        # 检查标题字体大小
        if 'headings' in format_rules:
            for level in ['h1', 'h2', 'h3']:
                if level in format_rules['headings']:
                    size = format_rules['headings'][level].get('font_size_pt', 14)
                    if size < 8 or size > 30:
                        default_size = 14 if level == 'h1' else 12
                        logger.warning(f"{level}标题字体大小异常: {size}磅，修正为{default_size}磅")
                        format_rules['headings'][level]['font_size_pt'] = default_size
    
    return instructions
```

---

### 3.2 大纲生成增强：JSON Schema约束

**文件**：`ai_generation_service.py` 的 `generate_outline()` 方法

**改进**：
```python
async def generate_outline(thesis_info, template_id, format_instructions):
    # 1. 从格式指令中提取约束
    constraints = extract_outline_constraints(format_instructions)
    
    # 2. 构建JSON Schema
    outline_schema = build_outline_schema(constraints)
    
    # 3. AI生成大纲（带Schema约束）
    outline = await ai_generate_with_schema(
        prompt=build_outline_prompt(thesis_info, constraints),
        schema=outline_schema
    )
    
    # 4. 验证和纠正
    validated_outline = validate_and_fix_outline(outline, constraints)
    
    return validated_outline

def build_outline_schema(constraints):
    """构建大纲JSON Schema"""
    chapter_numbering = constraints.get('chapter_numbering_format', {})
    level_1 = chapter_numbering.get('level_1', {})
    pattern = level_1.get('pattern', '第{number}章 {title}')
    
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "chapters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "chapter_number": {
                            "oneOf": [
                                {"type": "null"},
                                {"type": "integer", "minimum": 1}
                            ]
                        },
                        "chapter_title": {
                            "type": "string",
                            "pattern": f"^{pattern.replace('{number}', '\\\\d+').replace('{title}', '.+')}$"  # 验证标题格式
                        },
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "section_number": {"type": "string"},
                                    "section_title": {"type": "string"},
                                    "content_outline": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["chapter_title"]
                }
            }
        }
    }
```

---

### 3.3 章节生成增强：格式模板约束

**文件**：`ai_generation_service.py` 的 `generate_chapter()` 方法

**改进**：
```python
async def generate_chapter(chapter_info, format_instructions):
    # 1. 从格式指令中提取章节格式
    chapter_format = extract_chapter_format(format_instructions, chapter_info)
    
    # 2. 构建格式模板
    format_template = build_format_template(chapter_format)
    
    # 3. AI生成章节内容（带格式模板）
    content = await ai_generate_with_template(
        prompt=build_chapter_prompt(chapter_info, chapter_format),
        format_template=format_template
    )
    
    return content

def build_format_template(chapter_format):
    """构建格式模板"""
    return f"""
## 格式要求（必须严格遵守）：

### 标题格式
- 字体：{chapter_format['heading']['font_name']}
- 字号：{chapter_format['heading']['font_size_pt']}磅
- 对齐：{chapter_format['heading']['alignment']}
- 加粗：{'是' if chapter_format['heading']['bold'] else '否'}

### 段落格式
- 字体：{chapter_format['paragraph']['font_name']}
- 字号：{chapter_format['paragraph']['font_size_pt']}磅
- 行距：{chapter_format['paragraph']['line_spacing']}倍
- 首行缩进：{chapter_format['paragraph']['first_line_indent_chars']}字符

**重要**：生成的内容必须严格按照以上格式要求。
"""
```

---

### 3.4 格式化简化：直接应用

**文件**：`format_service.py` 的 `format_thesis()` 方法

**改进**：
```python
async def format_thesis(thesis_id, format_instructions):
    # 1. 获取章节（已经符合格式要求）
    chapters = await get_chapters(thesis_id)
    
    # 2. 直接应用格式（无需转换）
    formatted_doc = apply_format(chapters, format_instructions)
    
    return formatted_doc
```

---

## 四、动态调整机制

### 4.1 指令验证和修正

**机制**：
- 提取后立即验证
- 自动修正异常值
- 确保指令准确

**实现**：
```python
def validate_and_fix_format_instructions(instructions):
    """动态验证和修正格式指令"""
    fixes = []
    
    # 验证字体大小
    if 'format_rules' in instructions:
        format_rules = instructions['format_rules']
        
        # 检查所有字体大小
        font_sizes = [
            ('default_font', 'size_pt'),
            ('headings.h1', 'font_size_pt'),
            ('headings.h2', 'font_size_pt'),
            ('headings.h3', 'font_size_pt'),
        ]
        
        for path, key in font_sizes:
            size = get_nested_value(format_rules, path, key)
            if size and (size < 8 or size > 30):
                # 修正为合理值
                fixed_size = 12 if 'default' in path else 14
                set_nested_value(format_rules, path, key, fixed_size)
                fixes.append(f"{path}.{key}: {size}磅 -> {fixed_size}磅")
    
    if fixes:
        logger.info(f"格式指令已修正: {', '.join(fixes)}")
    
    return instructions
```

---

### 4.2 大纲验证和纠正

**机制**：
- 生成后立即验证
- 自动纠正格式问题
- 确保大纲符合要求

**实现**：
```python
def validate_and_fix_outline(outline, format_instructions):
    """动态验证和纠正大纲"""
    # 1. 验证章节标题格式
    chapter_numbering = format_instructions.get('application_rules', {}).get('chapter_numbering_format', {})
    level_1 = chapter_numbering.get('level_1', {})
    
    if level_1:
        pattern = level_1.get('pattern', '第{number}章 {title}')
        number_style = level_1.get('number_style', 'chinese')
        
        for chapter in outline.get('chapters', []):
            if chapter.get('chapter_number'):
                # 检查并纠正标题格式
                if not matches_pattern(chapter['chapter_title'], pattern):
                    chapter['chapter_title'] = format_title(chapter['chapter_title'], chapter['chapter_number'], pattern, number_style)
    
    # 2. 验证特殊章节
    special_sections = format_instructions.get('application_rules', {}).get('special_section_format_rules', {})
    for chapter in outline.get('chapters', []):
        chapter_title = chapter.get('chapter_title', '')
        for section_type, section_config in special_sections.items():
            if section_config.get('title') in chapter_title:
                if not section_config.get('should_have_numbering', False):
                    chapter['chapter_number'] = None
    
    return outline
```

---

### 4.3 章节内容验证

**机制**：
- 生成后验证格式
- 确保符合要求

**实现**：
```python
def validate_chapter_content(content, format_instructions):
    """验证章节内容格式"""
    # 检查标题格式
    # 检查段落格式
    # 检查标点符号
    # ...
    return content
```

---

## 五、一次性生成流程

### 5.1 完整流程

```
1. 上传格式模板
   ↓
2. AI提取格式指令 + 立即验证修正
   ↓ 保存准确的指令
3. 用户创建论文
   ↓
4. 根据指令生成大纲 + 立即验证纠正
   ↓ 保存符合格式的大纲
5. 根据指令和大纲生成章节内容 + 立即验证
   ↓ 保存符合格式的章节内容
6. 格式化时直接应用指令
   ↓ 生成最终文档
```

---

### 5.2 关键保证

1. **指令准确性**：
   - 提取后立即验证
   - 自动修正异常值
   - 确保指令准确

2. **大纲准确性**：
   - 生成时严格约束
   - 生成后立即验证
   - 自动纠正格式问题

3. **章节准确性**：
   - 生成时严格约束
   - 生成后立即验证
   - 确保格式正确

4. **格式化简化**：
   - 直接应用格式
   - 无需转换
   - 确保正确

---

## 六、实现建议

### 6.1 指令提取增强

**修改位置**：`template_service.py` 的 `create_template()` 方法

**实现**：
```python
async def create_template(template_data):
    # 1. AI提取格式指令
    format_instructions = await read_word_document_with_ai(template_file)
    
    # 2. 立即验证和修正
    validated_instructions = validate_and_fix_format_instructions(format_instructions)
    
    # 3. 保存准确的指令
    template.format_data = validated_instructions
    await save_template(template)
```

---

### 6.2 大纲生成增强

**修改位置**：`ai_generation_service.py` 的 `generate_outline()` 方法

**实现**：
```python
async def generate_outline(thesis_info, template_id):
    # 1. 读取格式指令
    format_instructions = await get_format_instructions(template_id)
    
    # 2. 提取格式约束
    constraints = extract_outline_constraints(format_instructions)
    
    # 3. 生成大纲（带严格约束）
    outline = await ai_generate_with_constraints(thesis_info, constraints)
    
    # 4. 验证和纠正
    validated_outline = validate_and_fix_outline(outline, format_instructions)
    
    return validated_outline
```

---

### 6.3 章节生成增强

**修改位置**：`ai_generation_service.py` 的 `generate_chapter()` 方法

**实现**：
```python
async def generate_chapter(chapter_info, format_instructions):
    # 1. 提取章节格式
    chapter_format = extract_chapter_format(format_instructions, chapter_info)
    
    # 2. 生成章节内容（带格式约束）
    content = await ai_generate_with_format(chapter_info, chapter_format)
    
    # 3. 验证格式
    validated_content = validate_chapter_content(content, chapter_format)
    
    return validated_content
```

---

## 七、优势

### ✅ 1. 一次性准确

- 指令提取后立即验证修正
- 大纲生成后立即验证纠正
- 章节生成后立即验证
- 确保每一步都准确

### ✅ 2. 动态调整

- 自动检测异常值
- 自动修正错误
- 适应各种格式

### ✅ 3. 格式化简化

- 直接应用格式
- 无需转换
- 确保正确

### ✅ 4. 完全通用

- 适应所有学校格式
- 不依赖硬编码
- 动态调整

---

## 八、总结

### 🎯 核心思想

**"端到端、一次生成、直接应用、动态调整"**

### ✅ 实现要点

1. **指令提取**：提取后立即验证修正
2. **大纲生成**：生成时严格约束，生成后验证纠正
3. **章节生成**：生成时严格约束，生成后验证
4. **格式化**：直接应用，无需转换

### 📝 优势

- ✅ 一次性准确
- ✅ 动态调整
- ✅ 格式化简化
- ✅ 完全通用

**结论**：✅ **端到端动态格式化方案可以实现一次性生成准确的指令、大纲和章节内容，格式化时直接应用，适应所有格式！**
