# 动态识别特殊章节改进

## 一、问题分析

**用户提出的问题**：当前实现中硬编码了特殊章节的识别逻辑，应该根据格式指令动态识别。

**原有问题**：
- 在 `_validate_outline_format()` 方法中硬编码了特殊章节列表
- 无法适应不同学校的格式要求
- 不符合"指令系统描述格式要求"的设计原则

---

## 二、改进方案

### ✅ 1. 从格式指令动态读取特殊章节配置

**改进前**（硬编码）：
```python
# 识别特殊章节（根据标题）
special_chapter_keywords = ['摘要', '关键词', '结论', '结语', '参考文献', '致谢', 'Abstract', 'Key words', 'References', 'Acknowledgement', '目录', '目　录']
```

**改进后**（动态读取）：
```python
# 从格式指令中动态识别特殊章节（无编号的章节）
special_chapter_titles = []
if format_instructions:
    try:
        application_rules = format_instructions.get('application_rules', {})
        special_sections = application_rules.get('special_section_format_rules', {})
        
        for section_type, section_config in special_sections.items():
            title = section_config.get('title', '')
            has_numbering = section_config.get('should_have_numbering', False)
            if title and not has_numbering:
                special_chapter_titles.append(title)
                logger.debug(f"从格式指令识别特殊章节（无编号）：{title}")
    except Exception as e:
        logger.warning(f"从格式指令提取特殊章节配置失败: {str(e)}，将使用默认配置")

# 如果没有格式指令或提取失败，使用默认的特殊章节列表（向后兼容）
if not special_chapter_titles:
    special_chapter_titles = ['摘要', '关键词', '结论', '结语', '参考文献', '致谢', 'Abstract', 'Key words', 'References', 'Acknowledgement', '目录', '目　录']
    logger.debug("使用默认特殊章节列表（无格式指令或提取失败）")
```

---

### ✅ 2. 传递格式指令到验证方法

**改进前**：
```python
# 解析大纲内容
outline_data = cls._parse_outline_response(response)
logger.info(f"大纲解析完成，章节数: {len(outline_data.get('chapters', []))}")

return outline_data
```

**改进后**：
```python
# 解析大纲内容
outline_data = cls._parse_outline_response(response)
logger.info(f"大纲解析完成，章节数: {len(outline_data.get('chapters', []))}")

# 如果有格式指令，传递给验证方法用于动态识别特殊章节
format_instructions_for_validation = None
if template_id:
    try:
        from module_thesis.dao.template_dao import FormatTemplateDao
        template = await FormatTemplateDao.get_template_by_id(query_db, template_id)
        if template and template.format_data:
            import json
            format_instructions_for_validation = json.loads(template.format_data) if isinstance(template.format_data, str) else template.format_data
    except Exception as e:
        logger.debug(f"读取格式指令用于验证失败: {str(e)}")

# 验证和规范化大纲（传入格式指令用于动态识别特殊章节）
outline_data = cls._validate_outline_format(outline_data, format_instructions_for_validation)

return outline_data
```

---

### ✅ 3. 修改验证方法签名

**改进前**：
```python
@classmethod
def _validate_outline_format(cls, outline_data: Dict[str, Any]) -> Dict[str, Any]:
```

**改进后**：
```python
@classmethod
def _validate_outline_format(cls, outline_data: Dict[str, Any], format_instructions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    验证和规范化大纲格式
    
    :param outline_data: 解析后的大纲数据
    :param format_instructions: 格式指令（可选，用于动态识别特殊章节）
    :return: 验证和规范化后的大纲数据
    """
```

---

## 三、工作流程

### 3.1 改进后的流程

```
1. 生成大纲时，读取格式指令
   ↓
2. 从格式指令中提取特殊章节配置（special_section_format_rules）
   ↓
3. 在提示词中告诉AI哪些章节不应该有编号
   ↓
4. AI生成大纲
   ↓
5. 解析大纲
   ↓
6. 验证大纲时，再次读取格式指令
   ↓
7. 从格式指令中动态识别特殊章节（should_have_numbering: false）
   ↓
8. 根据动态识别的特殊章节列表，验证和规范化大纲
```

---

## 四、优势

### ✅ 1. 完全动态

- 不再硬编码特殊章节列表
- 根据格式指令动态识别
- 适应不同学校的格式要求

### ✅ 2. 向后兼容

- 如果没有格式指令，使用默认列表
- 如果格式指令提取失败，使用默认列表
- 不影响现有功能

### ✅ 3. 符合设计原则

- 指令系统描述格式要求
- 代码根据指令执行，不硬编码
- 完全通用，适应所有学校

---

## 五、格式指令配置示例

```json
{
  "application_rules": {
    "special_section_format_rules": {
      "abstract": {
        "title": "摘要",
        "should_have_numbering": false,
        "position": "after_toc"
      },
      "keywords": {
        "title": "关键词",
        "should_have_numbering": false,
        "position": "after_abstract"
      },
      "conclusion": {
        "title": "结语",
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

系统会自动识别：
- `title: "摘要"` + `should_have_numbering: false` → 特殊章节（无编号）
- `title: "结语"` + `should_have_numbering: false` → 特殊章节（无编号）
- `title: "参考文献"` + `should_have_numbering: false` → 特殊章节（无编号）

---

## 六、总结

### ✅ 改进完成

1. ✅ **移除硬编码**：不再硬编码特殊章节列表
2. ✅ **动态识别**：从格式指令中动态读取特殊章节配置
3. ✅ **向后兼容**：如果没有格式指令，使用默认列表
4. ✅ **符合设计原则**：指令系统描述格式要求，代码根据指令执行

### 🎯 核心改进

- **动态性**：根据格式指令动态识别特殊章节
- **通用性**：适应所有学校的格式要求
- **可维护性**：不需要修改代码，只需要更新格式指令

**结论**：✅ **已移除硬编码，改为根据格式指令动态识别特殊章节！**
