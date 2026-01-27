# 格式化指令规范（Format Instruction Specification）

## 一、指令结构

格式化指令是一个结构化的JSON对象，描述如何将格式应用到论文文档中。指令包含格式信息和应用规则。

## 二、完整指令结构

```json
{
  "instruction_type": "format_application",
  "version": "1.0",
  "description": "文档格式化指令，描述如何将格式应用到论文文档中",
  
  "format_rules": {
    // 格式信息（见下文详细说明）
  },
  
  "layout_rules": {
    // 布局规则（空行、间距等）
  },
  
  "application_rules": {
    // 格式应用规则
  }
}
```

## 三、format_rules 详细结构

### 3.1 默认字体格式（font）
```json
{
  "font": {
    "name": "字体名称（如：宋体、楷体_GB2312、Times New Roman）",
    "size": 字体大小（数字，单位：磅，如：12）,
    "color": "颜色（RGB值，如：000000表示黑色）"
  }
}
```

### 3.2 段落格式（paragraph）
```json
{
  "paragraph": {
    "alignment": "对齐方式（left/center/right/justify）",
    "line_spacing": 行距倍数（数字，如：1.5）,
    "spacing_before": 段前间距（数字，单位：磅，如：0）,
    "spacing_after": 段后间距（数字，单位：磅，如：0）,
    "first_line_indent": 首行缩进（数字，单位：磅，如：24表示2字符）,
    "left_indent": 左缩进（数字，单位：磅，如：0）,
    "right_indent": 右缩进（数字，单位：磅，如：0）
  }
}
```

### 3.3 标题格式（headings）
```json
{
  "headings": {
    "h1": {
      "font_name": "字体名称",
      "font_size": 字体大小（数字，单位：磅）,
      "bold": true/false,
      "alignment": "对齐方式（left/center/right）",
      "spacing_before": 段前距（数字，单位：磅）,
      "spacing_after": 段后距（数字，单位：磅）
    },
    "h2": { /* 同h1 */ },
    "h3": { /* 同h1 */ }
  }
}
```

### 3.4 页面设置（page）
```json
{
  "page": {
    "margins": {
      "top": 上边距（数字，单位：磅）,
      "bottom": 下边距（数字，单位：磅）,
      "left": 左边距（数字，单位：磅）,
      "right": 右边距（数字，单位：磅）
    },
    "size": "纸张大小（A4/Letter等）"
  }
}
```

### 3.5 特殊格式（special_formats）
```json
{
  "special_formats": {
    "table_of_contents": {
      "title_format": { /* 同标题格式 */ },
      "entry_format": { /* 同段落格式，但可能包含特殊对齐方式 */ }
    },
    "abstract": {
      "title_format": { /* 同标题格式 */ },
      "content_format": { /* 同段落格式 */ }
    },
    "keywords": { /* 同段落格式 */ },
    "conclusion": {
      "title_format": { /* 同标题格式 */ },
      "content_format": { /* 同段落格式 */ }
    }
  }
}
```

## 四、layout_rules 详细结构（新增）

布局规则描述文档结构中的空行、间距等布局要求。

```json
{
  "layout_rules": {
    "title_spacing": {
      "after_title": 标题后的空行数（数字，如：1表示空1行，2表示空2行）,
      "before_title": 标题前的空行数（数字，如：0表示不空行）
    },
    "heading_spacing": {
      "h1": {
        "before": 一级标题前的空行数（数字）,
        "after": 一级标题后的空行数（数字）
      },
      "h2": {
        "before": 二级标题前的空行数（数字）,
        "after": 二级标题后的空行数（数字）
      },
      "h3": {
        "before": 三级标题前的空行数（数字）,
        "after": 三级标题后的空行数（数字）
      }
    },
    "chapter_spacing": {
      "between_chapters": 章节之间的空行数或分页要求（数字或"page_break"）,
      "before_chapter": 章节开始前的空行数（数字）,
      "after_chapter": 章节结束后的空行数（数字）
    },
    "section_spacing": {
      "abstract": {
        "before": 摘要前的空行数（数字）,
        "after": 摘要后的空行数（数字）
      },
      "keywords": {
        "before": 关键词前的空行数（数字）,
        "after": 关键词后的空行数（数字）
      },
      "conclusion": {
        "before": 结论前的空行数（数字）,
        "after": 结论后的空行数（数字）
      },
      "table_of_contents": {
        "before": 目录前的空行数（数字）,
        "after": 目录后的空行数（数字）
      }
    },
    "paragraph_spacing": {
      "between_paragraphs": 段落之间的空行数（数字，通常为0或1）,
      "first_paragraph_indent": 首段是否需要首行缩进（true/false）
    }
  }
}
```

## 五、application_rules 详细结构

格式应用规则描述如何应用格式。

```json
{
  "application_rules": {
    "default_font_application": "将默认字体格式应用到所有正文段落",
    "heading_application": "根据标题级别（h1/h2/h3）应用对应的标题格式",
    "paragraph_application": "将段落格式应用到所有正文段落",
    "special_section_application": "识别特殊章节（目录、摘要、关键词、结论）并应用对应格式",
    "layout_application": "按照layout_rules中的规则应用布局（空行、间距等）"
  }
}
```

## 六、指令执行规则

### 6.1 执行顺序
1. 应用页面设置（page）
2. 应用默认字体格式（font）
3. 应用段落格式（paragraph）
4. 应用标题格式（headings）
5. 应用特殊格式（special_formats）
6. 应用布局规则（layout_rules）

### 6.2 布局规则执行
- `title_spacing.after_title`: 在论文标题后添加指定数量的空行
- `heading_spacing.h1.after`: 在一级标题后添加指定数量的空行
- `chapter_spacing.between_chapters`: 在章节之间添加空行或分页符
- `section_spacing.abstract.after`: 在摘要后添加指定数量的空行
- 等等

### 6.3 兼容性
- 如果指令中缺少某个字段，使用合理的默认值
- 如果指令是旧格式（直接是format_rules），自动兼容处理

## 七、示例

### 7.1 完整指令示例
```json
{
  "instruction_type": "format_application",
  "version": "1.0",
  "description": "中南林业科技大学论文格式指令",
  
  "format_rules": {
    "font": {
      "name": "宋体",
      "size": 12,
      "color": "000000"
    },
    "paragraph": {
      "alignment": "left",
      "line_spacing": 1.5,
      "spacing_before": 0,
      "spacing_after": 0,
      "first_line_indent": 24,
      "left_indent": 0,
      "right_indent": 0
    },
    "headings": {
      "h1": {
        "font_name": "黑体",
        "font_size": 15,
        "bold": true,
        "alignment": "left",
        "spacing_before": 0,
        "spacing_after": 0
      }
    },
    "page": {
      "margins": {
        "top": 72,
        "bottom": 72,
        "left": 73.71,
        "right": 73.71
      },
      "size": "A4"
    }
  },
  
  "layout_rules": {
    "title_spacing": {
      "after_title": 1
    },
    "heading_spacing": {
      "h1": {
        "before": 0,
        "after": 1
      },
      "h2": {
        "before": 0,
        "after": 1
      },
      "h3": {
        "before": 0,
        "after": 0
      }
    },
    "chapter_spacing": {
      "between_chapters": "page_break",
      "before_chapter": 0,
      "after_chapter": 0
    },
    "section_spacing": {
      "abstract": {
        "before": 0,
        "after": 1
      },
      "keywords": {
        "before": 0,
        "after": 1
      }
    },
    "paragraph_spacing": {
      "between_paragraphs": 0,
      "first_paragraph_indent": true
    }
  },
  
  "application_rules": {
    "default_font_application": "将默认字体格式应用到所有正文段落",
    "heading_application": "根据标题级别应用对应的标题格式",
    "paragraph_application": "将段落格式应用到所有正文段落",
    "layout_application": "按照layout_rules中的规则应用布局"
  }
}
```

## 八、指令解析和执行

格式化代码需要：
1. 解析指令JSON
2. 提取format_rules、layout_rules、application_rules
3. 按照执行顺序应用格式
4. 根据layout_rules应用布局（空行、间距等）
