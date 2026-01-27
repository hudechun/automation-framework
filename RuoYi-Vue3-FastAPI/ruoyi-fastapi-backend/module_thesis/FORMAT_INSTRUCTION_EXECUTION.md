# 格式化指令执行说明（Format Instruction Execution Guide）

## 一、指令识别和执行流程

### 1.1 指令解析

格式化代码会按照以下步骤解析和执行格式化指令：

1. **解析指令JSON**
   ```python
   format_instruction_data = json.loads(format_instructions)
   ```

2. **提取格式配置和布局规则**
   ```python
   if 'format_rules' in format_instruction_data:
       format_config = format_instruction_data['format_rules']
       layout_rules = format_instruction_data.get('layout_rules', {})
   else:
       # 兼容旧格式
       format_config = format_instruction_data
   ```

3. **验证和修正格式数据**
   ```python
   format_config = cls._validate_and_fix_format_config(format_config)
   ```

### 1.2 指令执行顺序

格式化代码按照以下顺序执行指令：

1. **应用页面设置**（page）
2. **应用默认字体格式**（font）
3. **应用段落格式**（paragraph）
4. **应用标题格式**（headings）
5. **应用特殊格式**（special_formats）
6. **应用布局规则**（layout_rules）

## 二、章节内容与格式指令的对应关系

### 2.1 章节级别识别

章节的格式通过 `chapter.level` 字段确定：

- **level = 1** → 使用 `headings.h1` 格式
- **level = 2** → 使用 `headings.h2` 格式
- **level = 3** → 使用 `headings.h3` 格式

**代码实现**：
```python
level_key = f'h{chapter.level}' if hasattr(chapter, 'level') else 'h1'
if level_key in headings_config:
    heading_style = headings_config[level_key]
    # 应用标题格式
```

### 2.2 章节标题格式应用

章节标题会应用对应级别的格式：

```python
# 应用标题格式
title_run.font.size = Pt(heading_style.get('font_size', 16))
title_run.font.name = heading_style.get('font_name', default_font_name)
title_run.font.bold = heading_style.get('bold', True)

# 应用标题对齐
title_alignment = heading_style.get('alignment', 'center')
if title_alignment == 'center':
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### 2.3 章节内容格式应用

章节内容会应用：

1. **普通段落格式**（paragraph）：
   - 字体、字号、行距、首行缩进等

2. **特殊章节格式**（如果是目录、摘要、关键词、结论）：
   - 应用对应的 `special_formats` 格式

3. **Markdown标题格式**（章节内容中的 ## 或 ###）：
   - 使用对应的 h2 或 h3 格式

## 三、目录格式指令识别和应用

### 3.1 目录章节识别

系统通过章节标题识别目录章节：

```python
if '目录' in chapter.title or 'table of contents' in chapter_title_lower:
    is_special_section = True
    special_type = 'table_of_contents'
```

### 3.2 目录格式应用

目录格式按照以下优先级应用：

1. **多级目录格式**（level_formats）：
   - 如果指令中包含 `level_formats`，根据目录条目级别应用对应格式
   - `level1` → 一级目录格式
   - `level2` → 二级目录格式
   - `level3` → 三级目录格式

2. **通用目录格式**（entry_format）：
   - 如果没有 `level_formats`，使用 `entry_format`

**代码实现**：
```python
if special_type == 'table_of_contents':
    level_formats = special_format.get('level_formats', {})
    
    # 判断目录级别
    toc_level = 1  # 通过内容特征判断
    
    if level_formats and f'level{toc_level}' in level_formats:
        # 使用对应级别的格式
        level_format = level_formats[f'level{toc_level}']
    elif 'entry_format' in special_format:
        # 使用通用格式
        entry_format = special_format['entry_format']
```

### 3.3 目录级别识别

系统通过内容特征识别目录级别：

- **一级目录**：`一、绪论`、`1 绪论`（中文编号或数字编号开头）
- **二级目录**：`（一）`、`1.1`（括号编号或二级编号）
- **三级目录**：`1.1.1`（三级编号）

## 四、指令对应关系表

### 4.1 章节标题与格式指令对应

| 章节级别 | 格式指令字段 | 应用位置 |
|---------|------------|---------|
| level=1 | `headings.h1` | 章节标题 |
| level=2 | `headings.h2` | 章节标题 |
| level=3 | `headings.h3` | 章节标题 |

### 4.2 章节内容与格式指令对应

| 内容类型 | 格式指令字段 | 应用位置 |
|---------|------------|---------|
| 普通段落 | `paragraph` | 章节内容段落 |
| Markdown ## | `headings.h2` | 章节内容中的二级标题 |
| Markdown ### | `headings.h3` | 章节内容中的三级标题 |
| 目录条目 | `special_formats.table_of_contents.entry_format` 或 `level_formats` | 目录章节内容 |
| 摘要内容 | `special_formats.abstract.content_format` | 摘要章节内容 |
| 关键词 | `special_formats.keywords` | 关键词章节内容 |
| 结论内容 | `special_formats.conclusion.content_format` | 结论章节内容 |

### 4.3 布局规则对应

| 布局规则 | 指令字段 | 应用位置 |
|---------|---------|---------|
| 标题后空行 | `layout_rules.heading_spacing.h1.after` | 章节标题后 |
| 章节间距 | `layout_rules.chapter_spacing.between_chapters` | 章节之间 |
| 特殊章节间距 | `layout_rules.section_spacing.abstract.after` | 特殊章节后 |

## 五、指令执行验证

### 5.1 验证点

格式化代码会验证：

1. **指令格式**：确保指令是有效的JSON
2. **格式配置**：验证格式数据（修正明显错误）
3. **章节级别**：确保章节有 `level` 字段
4. **格式应用**：确保格式正确应用到对应位置

### 5.2 兼容性处理

系统支持：

1. **新格式指令**（包含 `format_rules` 和 `layout_rules`）
2. **旧格式指令**（直接是格式配置）
3. **缺失字段**：使用合理的默认值

## 六、示例：指令执行流程

### 6.1 示例指令

```json
{
  "format_rules": {
    "headings": {
      "h1": {
        "font_name": "黑体",
        "font_size": 15,
        "bold": true,
        "alignment": "left"
      }
    },
    "special_formats": {
      "table_of_contents": {
        "entry_format": {
          "font_name": "宋体",
          "font_size": 12,
          "alignment": "justify"
        },
        "level_formats": {
          "level1": {
            "font_name": "宋体",
            "font_size": 14,
            "indent": 0
          }
        }
      }
    }
  },
  "layout_rules": {
    "heading_spacing": {
      "h1": {
        "after": 1
      }
    }
  }
}
```

### 6.2 执行流程

1. **解析指令**：提取 `format_rules` 和 `layout_rules`
2. **应用页面设置**：设置页边距
3. **遍历章节**：
   - 章节1（level=1，标题="一、绪论"）：
     - 应用 `headings.h1` 格式（黑体15磅加粗左对齐）
     - 标题后空1行（`layout_rules.heading_spacing.h1.after`）
     - 应用 `paragraph` 格式到内容段落
   - 目录章节（标题="目录"）：
     - 识别为 `table_of_contents`
     - 内容中的"一、绪论"识别为一级目录
     - 应用 `level_formats.level1` 格式（宋体14磅，无缩进）
4. **完成格式化**

## 七、常见问题

### 7.1 章节级别不匹配

**问题**：章节的 `level` 字段与格式指令不匹配

**解决**：
- 确保章节创建时正确设置 `level` 字段
- 格式化代码会使用 `chapter.level` 来确定格式

### 7.2 目录格式未应用

**问题**：目录格式指令未正确应用

**解决**：
- 确保章节标题包含"目录"关键字
- 确保指令中包含 `special_formats.table_of_contents`
- 检查目录条目的级别识别逻辑

### 7.3 布局规则未生效

**问题**：空行、间距等布局规则未生效

**解决**：
- 确保指令中包含 `layout_rules`
- 确保格式化代码正确解析 `layout_rules`
- 检查布局规则的应用逻辑

## 八、总结

格式化代码能够：

1. ✅ **正确识别指令**：解析新格式和旧格式指令
2. ✅ **正确应用格式**：根据章节级别和类型应用对应格式
3. ✅ **正确应用布局**：按照 `layout_rules` 应用空行、间距等
4. ✅ **支持多级目录**：识别目录级别并应用对应格式
5. ✅ **章节内容对应**：章节内容正确对应格式指令

**关键点**：
- 章节级别通过 `chapter.level` 确定
- 格式指令通过 `headings.h{level}` 对应
- 目录格式通过内容特征识别级别
- 布局规则通过 `layout_rules` 应用
