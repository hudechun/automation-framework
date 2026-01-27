# 完整指令系统完善方案

## 一、当前指令系统分析

### 1.1 已有部分

✅ **基础格式**：
- 字体格式（default_font, english_font）
- 段落格式（paragraph）
- 标题格式（headings: h1, h2, h3）
- 页面设置（page）

✅ **特殊章节**：
- 标题（title）
- 摘要（abstract）
- 关键词（keywords）
- 英文摘要（abstract_english）
- 英文关键词（keywords_english）
- 英文题目（title_english）
- 作者信息（author_info）
- 附录（appendix）
- 结论（conclusion）
- 参考文献（references）
- 致谢（acknowledgement）
- 目录（table_of_contents）

✅ **应用规则**：
- 标题识别规则（heading_detection）
- 特殊章节检测（special_section_detection）
- 文档结构（document_structure）
- 目录生成规则（toc_generation_rules）
- 章节编号格式（chapter_numbering_format）
- 特殊章节格式规则（special_section_format_rules）

---

## 二、缺失部分分析

### ❌ 2.1 表格格式

**缺失**：
- 表格标题格式
- 表格边框样式
- 表格对齐方式
- 表格字体格式
- 表格行高、列宽规则

**需要添加**：
```json
{
  "format_rules": {
    "table": {
      "caption": {
        "font_name": "表格标题字体",
        "font_size_pt": "表格标题字号",
        "alignment": "对齐方式（above/below）",
        "format": "格式模板（如：表{number} {title}）"
      },
      "border": {
        "style": "边框样式（solid/dashed/dotted）",
        "width_pt": "边框宽度（磅）",
        "color": "边框颜色"
      },
      "cell": {
        "font_name": "单元格字体",
        "font_size_pt": "单元格字号",
        "alignment": "单元格对齐方式",
        "padding_pt": "单元格内边距（磅）"
      },
      "header_row": {
        "font_name": "表头字体",
        "font_size_pt": "表头字号",
        "bold": "是否加粗",
        "background_color": "背景颜色"
      }
    }
  }
}
```

---

### ❌ 2.2 图片格式

**缺失**：
- 图片标题格式
- 图片对齐方式
- 图片大小规则
- 图片位置规则

**需要添加**：
```json
{
  "format_rules": {
    "figure": {
      "caption": {
        "font_name": "图片标题字体",
        "font_size_pt": "图片标题字号",
        "alignment": "对齐方式（center/left）",
        "format": "格式模板（如：图{number} {title}）"
      },
      "alignment": "图片对齐方式（center/left/right）",
      "max_width_cm": "最大宽度（厘米）",
      "max_height_cm": "最大高度（厘米）",
      "position": "位置规则（inline/float）"
    }
  }
}
```

---

### ❌ 2.3 页眉页脚

**缺失**：
- 页眉格式
- 页脚格式
- 页码格式
- 奇偶页不同设置

**需要添加**：
```json
{
  "format_rules": {
    "header_footer": {
      "header": {
        "enabled": "是否启用页眉",
        "font_name": "页眉字体",
        "font_size_pt": "页眉字号",
        "alignment": "对齐方式",
        "content": "页眉内容模板（如：{thesis_title}）",
        "different_odd_even": "奇偶页是否不同"
      },
      "footer": {
        "enabled": "是否启用页脚",
        "font_name": "页脚字体",
        "font_size_pt": "页脚字号",
        "alignment": "对齐方式",
        "page_number": {
          "enabled": "是否显示页码",
          "format": "页码格式（如：第{page}页、{page}/{total}）",
          "position": "页码位置（left/center/right）",
          "start_from": "起始页码（如：1、3）"
        },
        "different_odd_even": "奇偶页是否不同"
      }
    }
  }
}
```

---

### ❌ 2.4 列表格式

**缺失**：
- 有序列表格式
- 无序列表格式
- 列表缩进规则
- 列表项格式

**需要添加**：
```json
{
  "format_rules": {
    "list": {
      "ordered": {
        "numbering_style": "编号样式（1,2,3 / a,b,c / i,ii,iii）",
        "font_name": "列表项字体",
        "font_size_pt": "列表项字号",
        "indent_pt": "缩进值（磅）",
        "spacing_pt": "列表项间距（磅）"
      },
      "unordered": {
        "bullet_style": "项目符号样式（• / - / *）",
        "font_name": "列表项字体",
        "font_size_pt": "列表项字号",
        "indent_pt": "缩进值（磅）",
        "spacing_pt": "列表项间距（磅）"
      }
    }
  }
}
```

---

### ❌ 2.5 分页规则

**缺失**：
- 章节分页规则
- 特殊章节分页规则
- 避免孤行/寡行规则

**需要添加**：
```json
{
  "application_rules": {
    "page_break_rules": {
      "chapter_start": {
        "new_page": "章节是否从新页开始（true/false）",
        "page_break_before": "章节前是否分页"
      },
      "special_sections": {
        "abstract": {
          "new_page": "摘要是否从新页开始"
        },
        "references": {
          "new_page": "参考文献是否从新页开始"
        }
      },
      "orphan_widow_control": {
        "enabled": "是否启用孤行/寡行控制",
        "orphan_lines": "孤行最少行数（如：2）",
        "widow_lines": "寡行最少行数（如：2）"
      }
    }
  }
}
```

---

### ❌ 2.6 公式格式

**缺失**：
- 公式编号格式
- 公式对齐方式
- 公式字体格式

**需要添加**：
```json
{
  "format_rules": {
    "equation": {
      "caption": {
        "font_name": "公式编号字体",
        "font_size_pt": "公式编号字号",
        "alignment": "对齐方式（right）",
        "format": "格式模板（如：({number})）"
      },
      "alignment": "公式对齐方式（center/left）",
      "font_name": "公式字体（通常为Times New Roman）",
      "font_size_pt": "公式字号"
    }
  }
}
```

---

### ❌ 2.7 脚注格式

**缺失**：
- 脚注编号格式
- 脚注字体格式
- 脚注位置规则

**需要添加**：
```json
{
  "format_rules": {
    "footnote": {
      "numbering_style": "编号样式（1,2,3 / *,**,***）",
      "font_name": "脚注字体",
      "font_size_pt": "脚注字号",
      "line_spacing": "脚注行距",
      "separator": "分隔符（如：——）"
    }
  }
}
```

---

### ❌ 2.8 封面格式

**缺失**：
- 封面布局规则
- 封面字体格式
- 封面信息位置

**需要添加**：
```json
{
  "format_rules": {
    "cover": {
      "title": {
        "font_name": "封面标题字体",
        "font_size_pt": "封面标题字号",
        "alignment": "对齐方式",
        "position": "位置（top/center）"
      },
      "author_info": {
        "font_name": "作者信息字体",
        "font_size_pt": "作者信息字号",
        "alignment": "对齐方式",
        "position": "位置（bottom/center）"
      },
      "layout": {
        "spacing_pt": "各元素间距（磅）",
        "margins": "封面边距"
      }
    }
  }
}
```

---

### ❌ 2.9 段落间距规则

**缺失**：
- 段落之间的间距规则
- 不同级别段落的间距规则

**需要添加**：
```json
{
  "format_rules": {
    "paragraph": {
      "spacing_between_paragraphs_pt": "段落之间间距（磅）",
      "spacing_after_heading_pt": "标题后段落间距（磅）",
      "spacing_before_heading_pt": "标题前段落间距（磅）"
    }
  }
}
```

---

### ❌ 2.10 完整指令系统的元数据

**缺失**：
- 版本信息
- 更新日期
- 适用范围
- 字段类型定义
- 字段取值范围
- 字段默认值

**需要添加**：
```json
{
  "version": "1.0",
  "description": "通用格式指令系统（所有可能的格式要求）",
  "instruction_type": "universal_format",
  "last_updated": "2024-01-01",
  "applicable_scopes": ["本科论文", "硕士论文", "博士论文"],
  "field_definitions": {
    "font_name": {
      "type": "string",
      "allowed_values": ["宋体", "楷体_GB2312", "黑体", "Times New Roman", "Arial"],
      "description": "字体名称"
    },
    "font_size_pt": {
      "type": "number",
      "range": [8, 30],
      "default": 12,
      "description": "字体大小（磅）"
    }
  }
}
```

---

## 三、完整指令系统结构设计

### 3.1 完整结构

```json
{
  "version": "1.0",
  "description": "通用格式指令系统（所有可能的格式要求）",
  "instruction_type": "universal_format",
  "last_updated": "2024-01-01",
  "applicable_scopes": ["本科论文", "硕士论文", "博士论文"],
  
  "format_rules": {
    "default_font": {
      "name": {
        "type": "string",
        "allowed_values": ["宋体", "楷体_GB2312", "黑体", "Times New Roman", "Arial"],
        "default": "宋体",
        "description": "默认中文字体"
      },
      "size_pt": {
        "type": "number",
        "range": [8, 30],
        "default": 12,
        "description": "默认字体大小（磅）"
      },
      "color": {
        "type": "string",
        "pattern": "^[0-9A-Fa-f]{6}$",
        "default": "000000",
        "description": "字体颜色（RGB值）"
      }
    },
    
    "english_font": {
      "name": {
        "type": "string",
        "allowed_values": ["Times New Roman", "Arial", "Calibri"],
        "default": "Times New Roman",
        "description": "英文字体"
      },
      "size_pt": {
        "type": "number",
        "range": [8, 30],
        "default": 12,
        "description": "英文字体大小（磅）"
      }
    },
    
    "page": {
      "size": {
        "type": "string",
        "allowed_values": ["A4", "Letter", "A3"],
        "default": "A4",
        "description": "纸张大小"
      },
      "margins": {
        "top_cm": {
          "type": "number",
          "range": [1.0, 5.0],
          "default": 2.54,
          "description": "上边距（厘米）"
        },
        "bottom_cm": {
          "type": "number",
          "range": [1.0, 5.0],
          "default": 2.54,
          "description": "下边距（厘米）"
        },
        "left_cm": {
          "type": "number",
          "range": [1.0, 5.0],
          "default": 3.17,
          "description": "左边距（厘米）"
        },
        "right_cm": {
          "type": "number",
          "range": [1.0, 5.0],
          "default": 3.17,
          "description": "右边距（厘米）"
        }
      }
    },
    
    "headings": {
      "h1": {
        "font_name": {
          "type": "string",
          "allowed_values": ["黑体", "楷体_GB2312", "宋体", "Times New Roman"],
          "default": "黑体",
          "description": "一级标题字体"
        },
        "font_size_pt": {
          "type": "number",
          "range": [8, 30],
          "default": 14,
          "description": "一级标题字号（磅）"
        },
        "bold": {
          "type": "boolean",
          "default": true,
          "description": "是否加粗"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["left", "center", "right"],
          "default": "left",
          "description": "对齐方式"
        },
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
        },
        "keep_with_next": {
          "type": "boolean",
          "default": false,
          "description": "标题是否与下一段同页"
        }
      },
      "h2": { /* 类似h1 */ },
      "h3": { /* 类似h1 */ }
    },
    
    "paragraph": {
      "alignment": {
        "type": "string",
        "allowed_values": ["left", "center", "right", "justify"],
        "default": "left",
        "description": "段落对齐方式"
      },
      "line_spacing": {
        "type": "number",
        "range": [0.5, 3.0],
        "default": 1.5,
        "description": "行距倍数"
      },
      "first_line_indent_chars": {
        "type": "number",
        "range": [0, 10],
        "default": 2,
        "description": "首行缩进字符数"
      },
      "spacing_between_paragraphs_pt": {
        "type": "number",
        "range": [0, 50],
        "default": 0,
        "description": "段落之间间距（磅）"
      }
    },
    
    "table": {
      "caption": {
        "font_name": {
          "type": "string",
          "allowed_values": ["宋体", "黑体", "Times New Roman"],
          "default": "宋体",
          "description": "表格标题字体"
        },
        "font_size_pt": {
          "type": "number",
          "range": [8, 30],
          "default": 12,
          "description": "表格标题字号（磅）"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["above", "below"],
          "default": "above",
          "description": "标题位置（表格上方/下方）"
        },
        "format": {
          "type": "string",
          "pattern": "表\\{number\\} .+",
          "default": "表{number} {title}",
          "description": "表格标题格式模板"
        }
      },
      "border": {
        "style": {
          "type": "string",
          "allowed_values": ["solid", "dashed", "dotted", "none"],
          "default": "solid",
          "description": "边框样式"
        },
        "width_pt": {
          "type": "number",
          "range": [0.5, 5.0],
          "default": 0.5,
          "description": "边框宽度（磅）"
        }
      },
      "cell": {
        "font_name": {
          "type": "string",
          "allowed_values": ["宋体", "Times New Roman"],
          "default": "宋体",
          "description": "单元格字体"
        },
        "font_size_pt": {
          "type": "number",
          "range": [8, 30],
          "default": 12,
          "description": "单元格字号（磅）"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["left", "center", "right"],
          "default": "center",
          "description": "单元格对齐方式"
        }
      }
    },
    
    "figure": {
      "caption": {
        "font_name": {
          "type": "string",
          "allowed_values": ["宋体", "Times New Roman"],
          "default": "宋体",
          "description": "图片标题字体"
        },
        "font_size_pt": {
          "type": "number",
          "range": [8, 30],
          "default": 12,
          "description": "图片标题字号（磅）"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["center", "left"],
          "default": "center",
          "description": "图片标题对齐方式"
        },
        "format": {
          "type": "string",
          "pattern": "图\\{number\\} .+",
          "default": "图{number} {title}",
          "description": "图片标题格式模板"
        }
      },
      "alignment": {
        "type": "string",
        "allowed_values": ["center", "left", "right"],
        "default": "center",
        "description": "图片对齐方式"
      }
    },
    
    "header_footer": {
      "header": {
        "enabled": {
          "type": "boolean",
          "default": false,
          "description": "是否启用页眉"
        },
        "font_name": {
          "type": "string",
          "allowed_values": ["宋体", "Times New Roman"],
          "default": "宋体",
          "description": "页眉字体"
        },
        "font_size_pt": {
          "type": "number",
          "range": [8, 30],
          "default": 10,
          "description": "页眉字号（磅）"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["left", "center", "right"],
          "default": "center",
          "description": "页眉对齐方式"
        }
      },
      "footer": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "是否启用页脚"
        },
        "page_number": {
          "enabled": {
            "type": "boolean",
            "default": true,
            "description": "是否显示页码"
          },
          "format": {
            "type": "string",
            "allowed_values": ["{page}", "第{page}页", "{page}/{total}"],
            "default": "{page}",
            "description": "页码格式"
          },
          "position": {
            "type": "string",
            "allowed_values": ["left", "center", "right"],
            "default": "center",
            "description": "页码位置"
          }
        }
      }
    },
    
    "list": {
      "ordered": {
        "numbering_style": {
          "type": "string",
          "allowed_values": ["1,2,3", "a,b,c", "i,ii,iii", "A,B,C"],
          "default": "1,2,3",
          "description": "有序列表编号样式"
        },
        "font_name": {
          "type": "string",
          "allowed_values": ["宋体", "Times New Roman"],
          "default": "宋体",
          "description": "列表项字体"
        },
        "indent_pt": {
          "type": "number",
          "range": [0, 200],
          "default": 36,
          "description": "列表缩进值（磅）"
        }
      },
      "unordered": {
        "bullet_style": {
          "type": "string",
          "allowed_values": ["•", "-", "*", "○"],
          "default": "•",
          "description": "无序列表项目符号"
        },
        "font_name": {
          "type": "string",
          "allowed_values": ["宋体", "Times New Roman"],
          "default": "宋体",
          "description": "列表项字体"
        },
        "indent_pt": {
          "type": "number",
          "range": [0, 200],
          "default": 36,
          "description": "列表缩进值（磅）"
        }
      }
    },
    
    "equation": {
      "caption": {
        "font_name": {
          "type": "string",
          "allowed_values": ["Times New Roman", "宋体"],
          "default": "Times New Roman",
          "description": "公式编号字体"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["right", "center"],
          "default": "right",
          "description": "公式编号对齐方式"
        },
        "format": {
          "type": "string",
          "pattern": "\\(\\{number\\}\\)",
          "default": "({number})",
          "description": "公式编号格式模板"
        }
      }
    },
    
    "footnote": {
      "numbering_style": {
        "type": "string",
        "allowed_values": ["1,2,3", "*,**,***"],
        "default": "1,2,3",
        "description": "脚注编号样式"
      },
      "font_name": {
        "type": "string",
        "allowed_values": ["宋体", "Times New Roman"],
        "default": "宋体",
        "description": "脚注字体"
      },
      "font_size_pt": {
        "type": "number",
        "range": [8, 30],
        "default": 10,
        "description": "脚注字号（磅）"
      }
    },
    
    "cover": {
      "title": {
        "font_name": {
          "type": "string",
          "allowed_values": ["黑体", "楷体_GB2312", "宋体"],
          "default": "黑体",
          "description": "封面标题字体"
        },
        "font_size_pt": {
          "type": "number",
          "range": [16, 30],
          "default": 22,
          "description": "封面标题字号（磅）"
        },
        "alignment": {
          "type": "string",
          "allowed_values": ["center", "left"],
          "default": "center",
          "description": "封面标题对齐方式"
        }
      }
    },
    
    "special_sections": {
      /* 保持现有的特殊章节配置 */
    }
  },
  
  "application_rules": {
    "page_break_rules": {
      "chapter_start": {
        "new_page": {
          "type": "boolean",
          "default": false,
          "description": "章节是否从新页开始"
        }
      },
      "special_sections": {
        "abstract": {
          "new_page": {
            "type": "boolean",
            "default": false,
            "description": "摘要是否从新页开始"
          }
        },
        "references": {
          "new_page": {
            "type": "boolean",
            "default": true,
            "description": "参考文献是否从新页开始"
          }
        }
      },
      "orphan_widow_control": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "是否启用孤行/寡行控制"
        },
        "orphan_lines": {
          "type": "number",
          "range": [1, 5],
          "default": 2,
          "description": "孤行最少行数"
        },
        "widow_lines": {
          "type": "number",
          "range": [1, 5],
          "default": 2,
          "description": "寡行最少行数"
        }
      }
    },
    
    /* 保持现有的其他应用规则 */
  }
}
```

---

## 四、完善建议

### ✅ 建议1：添加缺失的格式规则

1. **表格格式**（table）
2. **图片格式**（figure）
3. **页眉页脚**（header_footer）
4. **列表格式**（list）
5. **公式格式**（equation）
6. **脚注格式**（footnote）
7. **封面格式**（cover）
8. **段落间距规则**（paragraph spacing）

### ✅ 建议2：添加分页规则

1. **章节分页规则**（chapter_start）
2. **特殊章节分页规则**（special_sections）
3. **孤行/寡行控制**（orphan_widow_control）

### ✅ 建议3：完善元数据

1. **版本信息**（version）
2. **更新日期**（last_updated）
3. **适用范围**（applicable_scopes）
4. **字段类型定义**（field_definitions）
5. **字段取值范围**（range）
6. **字段默认值**（default）

### ✅ 建议4：统一字段定义格式

每个字段应该包含：
- `type`: 字段类型（string/number/boolean）
- `allowed_values`: 允许的值列表（如果是枚举）
- `range`: 取值范围（如果是数字）
- `default`: 默认值
- `description`: 字段描述

---

## 五、实施步骤

### 步骤1：设计完整指令系统JSON文件

创建 `module_thesis/config/universal_instruction_system.json`，包含所有格式规则。

### 步骤2：创建数据库表

创建 `universal_instruction_system` 表，存储完整指令系统。

### 步骤3：初始化数据

创建初始化脚本，将JSON文件中的数据插入数据库。

### 步骤4：更新提取逻辑

更新 `_extract_document_content()` 方法，提取表格、图片等格式信息。

### 步骤5：更新AI提示词

更新 `_build_format_analysis_prompt()` 方法，包含新增的格式要求。

---

## 六、总结

**需要完善的部分**：
1. ✅ 表格格式
2. ✅ 图片格式
3. ✅ 页眉页脚
4. ✅ 列表格式
5. ✅ 公式格式
6. ✅ 脚注格式
7. ✅ 封面格式
8. ✅ 分页规则
9. ✅ 段落间距规则
10. ✅ 元数据和字段定义

**完善后的优势**：
- ✅ 覆盖所有可能的格式要求
- ✅ 每个字段都有明确的类型、范围、默认值
- ✅ 更容易生成准确的子集指令系统
- ✅ 更容易校验子集指令系统
