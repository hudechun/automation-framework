# 格式化指令系统设计理念

## 一、设计原则

### 1.1 超集设计（Superset Design）

**核心思想**：指令系统是一个**完整的超集**，包含所有可能的格式要求，而不是针对某个特定学校的设计。

- ✅ **通用性**：能够覆盖各个学校的格式要求
- ✅ **可扩展性**：可以轻松添加新的格式属性
- ✅ **灵活性**：每个学校只使用其中的一部分（子集）

### 1.2 子集使用（Subset Usage）

**实际应用**：每个学校上传格式模板时，AI会：
1. 分析该学校的格式要求
2. 从指令系统的超集中提取**相关的部分**
3. 生成该学校的**专用指令**（子集）
4. 保存到模板表的`format_data`字段

**示例**：
- 学校A：只需要中文摘要、关键词、正文、结论、参考文献
- 学校B：需要中文摘要、英文摘要、关键词、正文、结论、参考文献、致谢、附录
- 学校C：需要目录、摘要、关键词、正文、结论、参考文献、附录

每个学校都使用指令系统的不同子集。

## 二、指令系统结构

### 2.1 完整指令结构（超集）

```json
{
  "version": "1.0",
  "description": "学校名称+学位级别+专业格式化指令",
  "instruction_type": "format_application",
  "format_rules": {
    // 基础格式
    "default_font": {...},
    "english_font": {...},
    "page": {...},
    
    // 标题格式（可能只有部分学校使用h3）
    "headings": {
      "h1": {...},
      "h2": {...},
      "h3": {...}
    },
    
    // 段落格式
    "paragraph": {...},
    
    // 特殊章节（不同学校使用不同的组合）
    "special_sections": {
      "title": {...},                    // 大多数学校需要
      "title_english": {...},            // 部分学校需要
      "author_info": {...},              // 部分学校需要
      "abstract": {...},                 // 大多数学校需要
      "abstract_english": {...},         // 部分学校需要
      "keywords": {...},                 // 大多数学校需要
      "keywords_english": {...},         // 部分学校需要
      "table_of_contents": {...},        // 部分学校需要
      "conclusion": {...},                // 大多数学校需要
      "references": {...},               // 所有学校需要
      "appendix": {...},                 // 部分学校需要
      "acknowledgement": {...}           // 部分学校需要
    },
    
    // 应用规则
    "application_rules": {
      "heading_detection": {...},
      "special_section_detection": [...],
      "auto_generate_toc": true/false,
      "toc_generation_rules": {...},
      "document_structure": {...},
      "font_fallback": {...}
    }
  }
}
```

### 2.2 学校专用指令（子集示例）

**学校A的指令**（简单格式）：
```json
{
  "format_rules": {
    "default_font": {"name": "宋体", "size_pt": 12},
    "page": {"size": "A4", "margins": {...}},
    "headings": {
      "h1": {...},
      "h2": {...}
    },
    "paragraph": {...},
    "special_sections": {
      "abstract": {...},
      "keywords": {...},
      "conclusion": {...},
      "references": {...}
    }
  }
}
```

**学校B的指令**（完整格式）：
```json
{
  "format_rules": {
    "default_font": {"name": "宋体", "size_pt": 14},
    "english_font": {"name": "Times New Roman", "size_pt": 14},
    "page": {...},
    "headings": {
      "h1": {...},
      "h2": {...},
      "h3": {...}
    },
    "paragraph": {...},
    "special_sections": {
      "title": {...},
      "title_english": {...},
      "author_info": {...},
      "abstract": {...},
      "abstract_english": {...},
      "keywords": {...},
      "keywords_english": {...},
      "table_of_contents": {...},
      "conclusion": {...},
      "references": {...},
      "appendix": {...},
      "acknowledgement": {...}
    },
    "application_rules": {
      "auto_generate_toc": true,
      "document_structure": {...}
    }
  }
}
```

## 三、验证方法

### 3.1 通过实际使用验证

**方法**：生成各种学校的格式提示词，检验指令系统是否满足需求。

**步骤**：
1. **收集学校格式要求**：收集不同学校的论文格式要求文档
2. **生成提示词**：为每个学校生成格式分析提示词
3. **测试AI提取**：使用AI分析格式模板，生成指令
4. **验证完整性**：检查生成的指令是否包含所有必要的格式信息
5. **识别缺失**：如果发现缺失的格式属性，补充到指令系统中

### 3.2 验证清单

在测试每个学校时，检查以下方面：

#### ✅ 基础格式
- [ ] 中文字体（default_font）
- [ ] 英文字体（english_font）
- [ ] 页面设置（page）
- [ ] 段落格式（paragraph）

#### ✅ 标题格式
- [ ] 一级标题（h1）
- [ ] 二级标题（h2）
- [ ] 三级标题（h3，如果学校使用）

#### ✅ 特殊章节
- [ ] 论文标题（title）
- [ ] 英文标题（title_english，如果学校使用）
- [ ] 作者信息（author_info，如果学校使用）
- [ ] 中文摘要（abstract）
- [ ] 英文摘要（abstract_english，如果学校使用）
- [ ] 中文关键词（keywords）
- [ ] 英文关键词（keywords_english，如果学校使用）
- [ ] 目录（table_of_contents，如果学校使用）
- [ ] 结论（conclusion）
- [ ] 参考文献（references）
- [ ] 附录（appendix，如果学校使用）
- [ ] 致谢（acknowledgement，如果学校使用）

#### ✅ 应用规则
- [ ] 标题识别规则（heading_detection）
- [ ] 特殊章节识别（special_section_detection）
- [ ] 目录生成规则（toc_generation_rules，如果学校使用）
- [ ] 文档结构顺序（document_structure）

### 3.3 缺失处理

如果在测试中发现缺失的格式属性：

1. **记录缺失项**：记录哪个学校的哪个格式要求无法满足
2. **分析原因**：分析是指令系统设计问题还是AI提取问题
3. **补充指令**：如果是设计问题，补充到指令系统中
4. **更新提示词**：如果是提取问题，优化AI提示词
5. **重新测试**：重新测试验证

## 四、指令系统扩展指南

### 4.1 何时扩展指令系统

当遇到以下情况时，需要扩展指令系统：

1. **新的格式属性**：某个学校有新的格式要求，当前指令系统无法表达
2. **新的特殊章节**：某个学校有新的特殊章节类型
3. **新的应用规则**：某个学校有特殊的格式应用规则

### 4.2 如何扩展指令系统

**步骤**：
1. 在`special_sections`中添加新的章节类型
2. 在`application_rules.special_section_detection`中添加识别规则
3. 在AI提示词中添加新格式的说明
4. 在格式化代码中添加新格式的处理逻辑
5. 更新文档说明

**示例**：添加"前言"章节
```json
{
  "special_sections": {
    "preface": {
      "title_text": "前言标题文本",
      "title_font": "字体",
      "title_size_pt": 字号,
      "content_font": "内容字体",
      "content_size_pt": 内容字号
    }
  },
  "application_rules": {
    "special_section_detection": [
      {"marker": "前言", "type": "preface"}
    ]
  }
}
```

## 五、最佳实践

### 5.1 指令系统维护

1. **保持超集完整性**：确保指令系统包含所有可能的格式要求
2. **向后兼容**：新增格式属性时，确保不影响已有功能
3. **文档同步**：更新指令系统时，同步更新文档

### 5.2 AI提示词优化

1. **明确说明**：在提示词中明确说明哪些格式是必需的，哪些是可选的
2. **示例引导**：提供格式示例，帮助AI理解格式要求
3. **提取规则**：明确说明如何从文档中提取格式信息

### 5.3 测试策略

1. **多样性测试**：测试不同学校、不同学位级别、不同专业的格式
2. **边界测试**：测试极端情况（如只有基础格式的学校）
3. **完整性测试**：测试包含所有格式要求的复杂学校

## 六、总结

- ✅ **指令系统是超集**：包含所有可能的格式要求
- ✅ **每个学校使用子集**：只使用其中的一部分
- ✅ **通过实际使用验证**：生成各种学校的提示词来检验完整性
- ✅ **持续扩展**：根据实际需求不断补充和完善

**当前指令系统已经包含了常见的格式要求，可以通过实际使用来验证和完善。**
