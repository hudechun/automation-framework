# 标题前后换行配置说明

## 一、当前指令系统中的配置

### 1.1 标题格式中的配置

在指令系统的 `headings` 部分，已经包含了标题前后换行的配置：

```json
{
  "headings": {
    "h1": {
      "font_name": "字体名称",
      "font_size_pt": 字体大小,
      "bold": true/false,
      "alignment": "对齐方式",
      "spacing_before_pt": 段前距（数字，单位：磅）,  // ✅ 标题前换行
      "spacing_after_pt": 段后距（数字，单位：磅）,   // ✅ 标题后换行
      "keep_with_next": true/false
    },
    "h2": {
      "spacing_before_pt": 段前距,
      "spacing_after_pt": 段后距
    },
    "h3": {
      "spacing_before_pt": 段前距,
      "spacing_after_pt": 段后距
    }
  }
}
```

---

### 1.2 特殊章节格式中的配置

在指令系统的 `special_sections` 部分，也包含了标题前后换行的配置：

```json
{
  "special_sections": {
    "conclusion": {
      "title_spacing_before_pt": 标题前间距（数字，单位：磅）,  // ✅ 结论标题前换行
      "title_spacing_after_pt": 标题后间距（数字，单位：磅）    // ✅ 结论标题后换行
    },
    "acknowledgement": {
      "title_spacing_before_pt": 标题前间距,
      "title_spacing_after_pt": 标题后间距
    },
    "table_of_contents": {
      "title_spacing_before_pt": 标题前间距,
      "title_spacing_after_pt": 标题后间距
    }
  }
}
```

---

## 二、提取逻辑

### 2.1 从Word文档提取

在 `_extract_document_content()` 方法中，已经实现了段前距和段后距的提取：

```python
# 提取标题格式信息
if para.paragraph_format:
    if para.paragraph_format.space_before:
        heading_info['spacing_before'] = str(para.paragraph_format.space_before)
    if para.paragraph_format.space_after:
        heading_info['spacing_after'] = str(para.paragraph_format.space_after)
```

---

## 三、在完整指令系统中的设计

### 3.1 建议的完整指令系统结构

在完整指令系统中，应该明确包含标题前后换行的配置：

```json
{
  "format_rules": {
    "headings": {
      "h1": {
        "spacing_before_pt": {
          "type": "number",
          "range": [0, 100],
          "default": 12,
          "description": "标题前间距（磅），控制标题前的换行/空行"
        },
        "spacing_after_pt": {
          "type": "number",
          "range": [0, 100],
          "default": 6,
          "description": "标题后间距（磅），控制标题后的换行/空行"
        }
      }
    }
  }
}
```

---

## 四、应用逻辑

### 4.1 格式化时应用

在格式化Word文档时，应该应用这些间距设置：

```python
# 应用标题格式
heading_para = doc.add_paragraph(chapter_title)
heading_para.style = 'Heading 1'

# 设置段前距（标题前换行）
if 'spacing_before_pt' in heading_format:
    heading_para.paragraph_format.space_before = Pt(heading_format['spacing_before_pt'])

# 设置段后距（标题后换行）
if 'spacing_after_pt' in heading_format:
    heading_para.paragraph_format.space_after = Pt(heading_format['spacing_after_pt'])
```

---

## 五、总结

### ✅ 当前状态

1. **指令系统中已有配置**：
   - ✅ `spacing_before_pt`: 段前距（标题前换行）
   - ✅ `spacing_after_pt`: 段后距（标题后换行）

2. **提取逻辑已实现**：
   - ✅ 从Word文档中提取段前距和段后距

3. **提示词中已包含**：
   - ✅ 在AI提示词中明确要求提取段前距和段后距

### ⚠️ 需要确认

1. **完整指令系统中是否需要更详细的定义**：
   - 是否需要定义默认值？
   - 是否需要定义范围（如0-100磅）？
   - 是否需要更明确的描述？

2. **格式化时是否正确应用**：
   - 需要检查格式化代码是否正确应用了这些间距设置

---

## 六、建议

### ✅ 建议1：在完整指令系统中明确定义

在完整指令系统中，应该明确包含标题前后换行的配置，包括：
- 类型：数字
- 范围：0-100磅
- 默认值：段前距12磅，段后距6磅
- 描述：控制标题前后的换行/空行

### ✅ 建议2：确保格式化时正确应用

需要检查格式化代码，确保在生成Word文档时正确应用了这些间距设置。
