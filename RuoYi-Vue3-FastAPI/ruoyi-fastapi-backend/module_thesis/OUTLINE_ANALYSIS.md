# 大纲生成结果分析

## 一、生成的大纲内容

```json
{
  "title": "人工智能",
  "chapters": [
    {
      "chapter_title": "摘要",
      "chapter_number": 1,
      "sections": [...]
    },
    {
      "chapter_title": "引言",
      "chapter_number": 2,
      "sections": [...]
    },
    ...
    {
      "chapter_title": "结论",
      "chapter_number": 7,
      "sections": [...]
    },
    {
      "chapter_title": "参考文献",
      "chapter_number": 8,
      "sections": [...]
    }
  ]
}
```

---

## 二、问题分析

### ❌ 问题1：特殊章节不应该有章节编号

**问题**：
- "摘要"作为第1章，有 `chapter_number: 1`
- "参考文献"作为第8章，有 `chapter_number: 8`

**设计要求**：
- 摘要、关键词、结论、参考文献等特殊章节不应该有章节编号
- 应该使用 `should_have_numbering: false` 标识

**影响**：
- 格式化时，这些章节会被当作普通章节处理
- 不符合格式要求

---

### ❌ 问题2：章节编号格式不正确

**问题**：
- 使用数字编号：`chapter_number: 1, 2, 3...`

**设计要求**：
- 应该使用中文章节格式：`第一章`、`第二章`等
- 或者根据格式指令中的 `chapter_numbering_format` 要求

**影响**：
- 格式化时，章节标题可能不符合要求

---

### ❌ 问题3：章节顺序可能不符合section_order

**问题**：
- 大纲中的章节顺序：摘要、引言、文献综述、研究方法、研究结果、讨论、结论、参考文献

**需要检查**：
- 格式指令中的 `section_order` 是什么？
- 是否与生成的大纲顺序一致？

---

### ✅ 正确的地方

1. **章节结构完整**：每个章节都有 `sections`，包含小节信息
2. **小节编号格式正确**：使用 `1.1`、`1.2` 等格式
3. **内容概要完整**：每个小节都有 `content_outline`

---

## 三、改进建议

### 1. 增强提示词：明确特殊章节处理

**当前问题**：
- AI可能不理解哪些章节不应该有编号
- AI可能不理解章节编号格式要求

**改进方案**：
- 在提示词中明确列出特殊章节（摘要、关键词、结论、参考文献等）
- 明确要求这些章节不使用 `chapter_number`，或者使用特殊标识
- 明确要求章节编号格式（如：第一章、第二章）

---

### 2. 增强大纲验证：纠正特殊章节

**当前问题**：
- 大纲解析时，没有检查特殊章节的编号

**改进方案**：
- 在 `_validate_outline_format()` 中，识别特殊章节
- 移除特殊章节的 `chapter_number`，或者设置为特殊值（如：-1）
- 重新规范化其他章节的 `chapter_number`

---

### 3. 增强格式要求提取：明确特殊章节规则

**当前问题**：
- 格式要求中可能没有明确特殊章节的处理方式

**改进方案**：
- 在提取格式要求时，明确列出特殊章节
- 明确要求这些章节不使用章节编号
- 明确要求章节编号格式

---

## 四、具体改进实现

### 改进1：增强提示词

在 `_build_outline_prompt()` 中，添加特殊章节的明确说明：

```python
# 如果有特殊章节格式规则，明确说明
if special_sections:
    special_chapters_instruction = "\n\n**特殊章节处理规则**（必须严格遵守）：\n"
    for section_type, section_config in special_sections.items():
        title = section_config.get('title', '')
        has_numbering = section_config.get('should_have_numbering', False)
        if title and not has_numbering:
            section_name_map = {
                'abstract': '摘要',
                'keywords': '关键词',
                'conclusion': '结论',
                'references': '参考文献',
                'acknowledgement': '致谢'
            }
            section_name = section_name_map.get(section_type, section_type)
            special_chapters_instruction += f"- {section_name}（标题：{title}）**不应该有章节编号**，在JSON中不设置chapter_number或设置为null\n"
    
    format_requirements += special_chapters_instruction
```

---

### 改进2：增强大纲验证

在 `_validate_outline_format()` 中，处理特殊章节：

```python
# 识别特殊章节（根据标题）
special_chapter_titles = ['摘要', '关键词', '结论', '结语', '参考文献', '致谢', 'Abstract', 'Key words', 'References', 'Acknowledgement']

validated_chapters = []
numbered_chapters = []  # 有编号的章节
special_chapters = []   # 特殊章节（无编号）

for idx, chapter in enumerate(outline_data['chapters']):
    chapter_title = chapter.get('chapter_title', '')
    
    # 判断是否为特殊章节
    is_special = any(title in chapter_title for title in special_chapter_titles)
    
    if is_special:
        # 特殊章节：移除chapter_number或设置为null
        validated_chapter = {
            'chapter_number': None,  # 或使用特殊值 -1
            'chapter_title': chapter_title,
            'sections': []
        }
        special_chapters.append(validated_chapter)
    else:
        # 普通章节：保留chapter_number
        validated_chapter = {
            'chapter_number': chapter.get('chapter_number', idx + 1),
            'chapter_title': chapter_title,
            'sections': []
        }
        numbered_chapters.append(validated_chapter)

# 重新规范化numbered_chapters的chapter_number
for idx, chapter in enumerate(numbered_chapters):
    chapter['chapter_number'] = idx + 1

# 合并章节（按照原始顺序，但特殊章节无编号）
# 这里需要根据section_order来确定最终顺序
```

---

### 改进3：明确章节编号格式要求

在格式要求中，明确章节编号格式：

```python
# 章节编号格式
if chapter_numbering:
    level_1 = chapter_numbering.get('level_1', {})
    if level_1:
        pattern = level_1.get('pattern', '第X章 标题')
        examples = level_1.get('examples', [])
        format_requirements_parts.append(f"\n**章节编号格式要求**：")
        format_requirements_parts.append(f"- 一级标题格式：{pattern}")
        format_requirements_parts.append(f"- 示例：{', '.join(examples[:3])}")
        format_requirements_parts.append(f"- **重要**：章节标题必须包含完整的编号格式（如：第一章 引言），而不仅仅是标题文本")
```

---

## 五、总结

### ❌ 当前问题

1. **特殊章节有编号**：摘要、参考文献等不应该有章节编号
2. **章节编号格式不正确**：使用数字而不是中文格式
3. **章节顺序可能不符合要求**：需要检查是否与section_order一致

### ✅ 改进方向

1. **增强提示词**：明确特殊章节处理规则和章节编号格式
2. **增强验证**：在大纲解析时纠正特殊章节的编号
3. **明确格式要求**：在格式要求中明确章节编号格式

**结论**：当前生成的大纲**不符合设计要求**，需要进行改进。
