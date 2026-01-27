# 大纲和格式指令校验报告

## 一、大纲数据校验

### ✅ 1. 特殊章节编号处理

**校验结果**：✅ **正确**

- **摘要**：`chapter_number: null` ✅ 正确（特殊章节，无编号）
- **结论**：`chapter_number: null` ✅ 正确（特殊章节，无编号）
- **参考文献**：`chapter_number: null` ✅ 正确（特殊章节，无编号）

**符合格式指令要求**：
```json
"special_section_format_rules": {
  "abstract": {"should_have_numbering": false},
  "conclusion": {"should_have_numbering": false},
  "references": {"should_have_numbering": false}
}
```

---

### ❌ 2. 章节编号格式问题

**问题**：
- 大纲中使用数字编号：`chapter_number: 1, 2, 3, 4, 5`
- 格式指令要求中文格式：`第一章、第二章、第三章...`

**格式指令要求**：
```json
"chapter_numbering_format": {
  "level_1": {
    "pattern": "第{number}章 {title}",
    "examples": ["第一章 引言"],
    "format_type": "chinese_chapter",
    "number_style": "chinese"
  }
}
```

**当前大纲**：
```json
{"chapter_title": "引言", "chapter_number": 1}  // ❌ 应该是 "第一章 引言"
{"chapter_title": "文献综述", "chapter_number": 2}  // ❌ 应该是 "第二章 文献综述"
```

**应该生成**：
```json
{"chapter_title": "第一章 引言", "chapter_number": 1}
{"chapter_title": "第二章 文献综述", "chapter_number": 2}
```

---

### ⚠️ 3. 摘要章节结构问题

**问题**：
- 摘要章节包含 `sections`（小节）
- 摘要通常不应该有小节结构

**当前大纲**：
```json
{
  "chapter_title": "摘要",
  "chapter_number": null,
  "sections": [
    {"section_title": "研究背景与意义", "section_number": "1.1"},
    {"section_title": "研究内容与方法概述", "section_number": "1.2"}
  ]
}
```

**建议**：
- 摘要应该是一个整体，不需要小节
- 或者，如果摘要需要结构化，应该使用不同的格式

---

### ✅ 4. 章节顺序

**校验结果**：✅ **基本正确**

大纲章节顺序：
1. 摘要（无编号）
2. 引言（第1章）
3. 文献综述（第2章）
4. 研究方法（第3章）
5. 研究结果（第4章）
6. 讨论（第5章）
7. 结论（无编号）
8. 参考文献（无编号）

**符合格式指令要求**：
```json
"section_order": ["摘要", "正文", "结论", "参考文献"]
```

---

## 二、格式指令校验

### ❌ 1. 字体大小异常

**问题**：
- 所有字体大小都是 `45.72` 磅，这明显不正常
- 正常论文格式应该是：
  - 标题：14-18磅
  - 正文：12磅
  - 小标题：12-14磅

**当前指令**：
```json
"default_font": {"size_pt": 45.72},  // ❌ 异常大
"headings": {
  "h1": {"font_size_pt": 45.72},  // ❌ 异常大
  "h2": {"font_size_pt": 45.72},  // ❌ 异常大
  "h3": {"font_size_pt": 45.72}   // ❌ 异常大
}
```

**可能原因**：
- AI提取格式时，可能误将某些尺寸单位转换错误
- 或者从模板中提取的数据有问题

**建议**：
- 需要验证和修正字体大小
- 应该使用合理的默认值（如12-18磅）

---

### ✅ 2. 特殊章节格式规则

**校验结果**：✅ **正确**

```json
"special_section_format_rules": {
  "abstract": {
    "title": "摘要",
    "should_have_numbering": false,  // ✅ 正确
    "position": "after_toc"
  },
  "keywords": {
    "title": "关键词",
    "should_have_numbering": false,  // ✅ 正确
    "position": "after_abstract"
  },
  "conclusion": {
    "title": "结论",
    "should_have_numbering": false,  // ✅ 正确
    "position": "before_references"
  },
  "references": {
    "title": "参考文献",
    "should_have_numbering": false,  // ✅ 正确
    "position": "before_appendix"
  }
}
```

---

### ✅ 3. 章节编号格式规则

**校验结果**：✅ **配置正确**

```json
"chapter_numbering_format": {
  "level_1": {
    "pattern": "第{number}章 {title}",
    "examples": ["第一章 引言"],
    "format_type": "chinese_chapter",
    "number_style": "chinese"
  }
}
```

**问题**：虽然配置正确，但AI生成的大纲没有遵循这个格式。

---

## 三、问题总结

### ❌ 主要问题

1. **章节编号格式不符合要求**
   - 大纲使用数字编号（1, 2, 3...）
   - 应该使用中文格式（第一章、第二章...）
   - **原因**：AI生成时没有严格按照格式指令要求

2. **字体大小异常**
   - 所有字体都是45.72磅，明显不正常
   - **原因**：格式提取时可能出错

3. **摘要章节结构**
   - 摘要包含小节，可能不符合要求
   - **建议**：根据实际需求决定

---

## 四、改进建议

### 1. 增强提示词：明确章节标题格式

**当前问题**：
- AI生成的大纲中，章节标题只包含标题文本，不包含编号格式

**改进方案**：
在提示词中明确要求：
```
章节标题必须包含完整的编号格式，例如：
- "第一章 引言"（不是只有"引言"）
- "第二章 文献综述"（不是只有"文献综述"）
```

---

### 2. 增强大纲验证：纠正章节标题格式

**改进方案**：
在 `_validate_outline_format()` 中，如果检测到章节标题不符合格式要求，自动纠正：

```python
# 检查章节标题格式
if chapter_number is not None:
    # 检查标题是否包含编号格式
    expected_format = f"第{_number_to_chinese(chapter_number)}章"
    if expected_format not in chapter_title:
        # 自动添加编号格式
        chapter_title = f"{expected_format} {chapter_title}"
        validated_chapter['chapter_title'] = chapter_title
```

---

### 3. 格式指令验证：修正异常值

**改进方案**：
在格式指令保存或使用时，验证字体大小是否合理：

```python
def validate_font_size(size_pt):
    """验证字体大小是否合理"""
    if size_pt < 8 or size_pt > 30:
        # 异常值，使用默认值
        return 12  # 默认12磅
    return size_pt
```

---

## 五、校验结论

### ✅ 正确的部分

1. ✅ 特殊章节编号处理正确（摘要、结论、参考文献无编号）
2. ✅ 格式指令配置结构正确
3. ✅ 章节顺序基本正确

### ❌ 需要改进的部分

1. ❌ **章节标题格式不符合要求**（最重要）
   - 应该使用"第一章 引言"格式，而不是只有"引言"
   
2. ❌ **字体大小异常**
   - 45.72磅明显不正常，需要修正

3. ⚠️ **摘要章节结构**
   - 摘要包含小节，需要确认是否符合要求

---

## 六、建议

1. **立即修复**：章节标题格式问题（影响最大）
2. **验证修复**：字体大小异常问题
3. **确认需求**：摘要章节结构是否符合要求

**总体评价**：大纲结构基本正确，但章节标题格式不符合要求，需要改进。
