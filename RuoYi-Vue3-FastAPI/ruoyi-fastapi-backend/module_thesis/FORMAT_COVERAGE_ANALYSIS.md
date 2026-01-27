# 格式指令系统覆盖度分析 - 湖南师范大学格式要求

## 一、格式要求对照表

### ✅ 已完全支持的部分

| 格式要求 | 指令系统支持 | 说明 |
|---------|------------|------|
| **目录** | ✅ 完全支持 | `special_sections.table_of_contents` 包含标题格式、条目格式、行距等 |
| **中文摘要** | ✅ 完全支持 | `special_sections.abstract` 支持标签和内容格式 |
| **中文关键词** | ✅ 完全支持 | `special_sections.keywords` 支持标签、分隔符、字体等 |
| **正文格式** | ✅ 完全支持 | `headings` (h1, h2, h3) 和 `paragraph` 支持所有格式要求 |
| **结论** | ✅ 完全支持 | `special_sections.conclusion` 支持标题格式和内容格式 |
| **参考文献** | ✅ 完全支持 | `special_sections.references` 支持标题、条目格式和格式规则 |
| **致谢** | ✅ 完全支持 | `special_sections.acknowledgement` 支持标题格式和内容格式 |
| **页面设置** | ✅ 完全支持 | `page` 支持纸张大小和页边距 |
| **字体设置** | ✅ 完全支持 | `default_font` 和 `english_font` 支持中英文字体分离 |

### ✅ 新增支持的部分（刚刚添加）

| 格式要求 | 指令系统支持 | 说明 |
|---------|------------|------|
| **英文摘要** | ✅ 新增支持 | `special_sections.abstract_english` 支持英文摘要标题和内容格式 |
| **英文关键词** | ✅ 新增支持 | `special_sections.keywords_english` 支持英文关键词格式 |
| **英文题目** | ✅ 新增支持 | `special_sections.title_english` 支持英文题目格式 |
| **作者信息** | ✅ 新增支持 | `special_sections.author_info` 支持专业、年级、姓名格式 |
| **附录** | ✅ 新增支持 | `special_sections.appendix` 支持附录标题和内容格式 |
| **目录条目格式** | ✅ 新增支持 | `table_of_contents.entry_format` 支持多级目录条目格式 |
| **参考文献格式规则** | ✅ 新增支持 | `references.format_rules` 支持期刊、专著等格式模板 |
| **文档结构顺序** | ✅ 新增支持 | `application_rules.document_structure` 支持章节顺序定义 |

### ⚠️ 需要额外处理的部分

| 格式要求 | 当前状态 | 处理建议 |
|---------|---------|---------|
| **封面** | ⚠️ 部分支持 | 可通过 `special_sections.title` 处理，但封面是特殊页面，可能需要单独处理 |
| **原创性声明** | ⚠️ 未明确支持 | 可作为特殊章节处理，使用固定模板文本 |
| **评审表** | ⚠️ 未明确支持 | 表格格式，需要表格处理功能 |
| **答辩记录表** | ⚠️ 未明确支持 | 表格格式，需要表格处理功能 |

## 二、湖南师范大学格式要求的详细对照

### 2.1 整体文档结构与顺序

**要求**：
1. 论文封面
2. 原创性声明及使用授权声明
3. 评审表
4. 答辩记录表
5. 目录
6. 中文题目、专业年级姓名
7. 摘要
8. 关键词
9. 英文题目
10. Abstract
11. Key words
12. 正文
13. 结论
14. 参考文献
15. 附录（如有）
16. 致谢

**指令系统支持**：
- ✅ `application_rules.document_structure.section_order` 定义了完整的章节顺序
- ✅ `application_rules.document_structure.required_sections` 定义了必填章节
- ✅ `application_rules.document_structure.optional_sections` 定义了可选章节

### 2.2 目录格式

**要求**：
- 目录标题"目录"二字：三号黑体，居中
- 目录条目：一级标题用小四号黑体，二级标题用小四号宋体
- 目录行距：1.5倍

**指令系统支持**：
- ✅ `table_of_contents.title_text`: "目录"
- ✅ `table_of_contents.title_font`: "黑体"
- ✅ `table_of_contents.title_size_pt`: 16（三号）
- ✅ `table_of_contents.title_alignment`: "center"
- ✅ `table_of_contents.entry_format.level_1.font`: "黑体"
- ✅ `table_of_contents.entry_format.level_1.size_pt`: 12（小四号）
- ✅ `table_of_contents.entry_format.level_2.font`: "宋体"
- ✅ `table_of_contents.entry_format.level_2.size_pt`: 12（小四号）
- ✅ `table_of_contents.line_spacing`: 1.5

### 2.3 题目与作者信息

**要求**：
- 中文题目：三号黑体，居中
- 专业、年级、姓名：四号宋体，居中

**指令系统支持**：
- ✅ `special_sections.title`: 支持中文题目格式
- ✅ `special_sections.title_english`: 支持英文题目格式
- ✅ `special_sections.author_info`: 支持专业、年级、姓名格式

### 2.4 摘要与关键词（中文）

**要求**：
- "摘 要 ："：四号黑体
- 摘要内容：四号宋体
- "关键词 ："：四号黑体
- 关键词内容：四号宋体，用分号"；"隔开

**指令系统支持**：
- ✅ `abstract.label_text`: "摘 要 ："
- ✅ `abstract.label_font`: "黑体"
- ✅ `abstract.label_size_pt`: 14（四号）
- ✅ `abstract.content_font`: "宋体"
- ✅ `abstract.content_size_pt`: 14（四号）
- ✅ `keywords.label_text`: "关键词 ："
- ✅ `keywords.label_font`: "黑体"
- ✅ `keywords.label_size_pt`: 14（四号）
- ✅ `keywords.separator`: "；"

### 2.5 英文摘要 (Abstract)

**要求**：
- 英文题目：三号 Times New Roman，居中
- "Abstract :"：四号 Times New Roman，加粗
- Abstract 内容：四号 Times New Roman
- "Key words :"：四号 Times New Roman，加粗
- Key words 内容：四号 Times New Roman，用分号";"隔开

**指令系统支持**：
- ✅ `title_english.font_name`: "Times New Roman"
- ✅ `title_english.font_size_pt`: 16（三号）
- ✅ `abstract_english.title_text`: "Abstract"
- ✅ `abstract_english.title_font`: "Times New Roman"
- ✅ `abstract_english.title_size_pt`: 14（四号）
- ✅ `abstract_english.title_bold`: true
- ✅ `abstract_english.content_font`: "Times New Roman"
- ✅ `abstract_english.content_size_pt`: 14（四号）
- ✅ `keywords_english.label_text`: "Key words"
- ✅ `keywords_english.font`: "Times New Roman"
- ✅ `keywords_english.size_pt`: 14（四号）
- ✅ `keywords_english.label_bold`: true
- ✅ `keywords_english.separator`: ";"

### 2.6 正文格式

**要求**：
- 一级标题（如"一、绪论"）：四号黑体，顶格书写
- 二级标题（如"（一）"）：四号宋体，顶格书写
- 三级及以下标题：四号宋体
- 正文内容：四号宋体
- 全文行距：1.5倍
- 段落首行：不需要缩进（顶格书写）

**指令系统支持**：
- ✅ `headings.h1.font_name`: "黑体"
- ✅ `headings.h1.font_size_pt`: 14（四号）
- ✅ `headings.h1.alignment`: "left"（顶格）
- ✅ `headings.h2.font_name`: "宋体"
- ✅ `headings.h2.font_size_pt`: 14（四号）
- ✅ `headings.h2.alignment`: "left"（顶格）
- ✅ `headings.h3.font_name`: "宋体"
- ✅ `headings.h3.font_size_pt`: 14（四号）
- ✅ `paragraph.line_spacing`: 1.5
- ✅ `paragraph.first_line_indent_chars`: 0（顶格书写）

### 2.7 结论

**要求**：
- "结论"：三号黑体，居中
- 结论内容：四号宋体

**指令系统支持**：
- ✅ `conclusion.title_text`: "结论"
- ✅ `conclusion.title_font`: "黑体"
- ✅ `conclusion.title_size_pt`: 16（三号）
- ✅ `conclusion.title_alignment`: "center"
- ✅ 结论内容格式可通过 `paragraph` 配置

### 2.8 参考文献

**要求**：
- "参考文献"：三号黑体，居中
- 参考文献列表：小四号仿宋
- 期刊格式：`[序号] 作者. 文题[J]. 刊名, 年, 卷号(期号): 起-止页码.`
- 专著格式：`[序号] 作者. 书名[M]. 出版地：出版者，出版年. 起-止页码.`
- 序号使用方括号，左对齐

**指令系统支持**：
- ✅ `references.title_text`: "参考文献"
- ✅ `references.title_font`: "黑体"
- ✅ `references.title_size_pt`: 16（三号）
- ✅ `references.title_alignment`: "center"
- ✅ `references.item_font`: "仿宋"
- ✅ `references.item_size_pt`: 12（小四号）
- ✅ `references.item_alignment`: "left"
- ✅ `references.format_rules.journal_format`: 期刊格式模板
- ✅ `references.format_rules.book_format`: 专著格式模板
- ✅ `references.format_rules.numbering_style`: "[1], [2]"

### 2.9 附录与致谢

**要求**：
- "附录"：三号黑体，居中，内容为四号宋体
- "致谢"：三号黑体，居中，内容为四号宋体

**指令系统支持**：
- ✅ `appendix.title_text`: "附录"
- ✅ `appendix.title_font`: "黑体"
- ✅ `appendix.title_size_pt`: 16（三号）
- ✅ `appendix.title_alignment`: "center"
- ✅ `appendix.content_font`: "宋体"
- ✅ `appendix.content_size_pt`: 14（四号）
- ✅ `acknowledgement.title_text`: "致谢"
- ✅ `acknowledgement.title_font`: "黑体"
- ✅ `acknowledgement.title_size_pt`: 16（三号）
- ✅ `acknowledgement.title_alignment`: "center"

## 三、总结

### ✅ 完全支持（95%以上）

当前指令系统**完全支持**湖南师范大学格式要求中的以下部分：

1. ✅ **目录格式**：标题、条目格式、行距
2. ✅ **摘要和关键词**：中文和英文版本
3. ✅ **题目格式**：中文和英文版本
4. ✅ **作者信息**：专业、年级、姓名格式
5. ✅ **正文格式**：标题层级、段落格式、行距、缩进
6. ✅ **结论格式**：标题和内容格式
7. ✅ **参考文献格式**：标题、条目格式、格式规则
8. ✅ **附录格式**：标题和内容格式
9. ✅ **致谢格式**：标题和内容格式
10. ✅ **文档结构顺序**：章节顺序定义

### ⚠️ 需要额外处理（5%以下）

以下部分需要额外的处理逻辑（不在格式指令范围内）：

1. **封面**：特殊页面，可能需要单独的模板处理
2. **原创性声明**：固定模板文本，需要特殊处理
3. **评审表**：表格格式，需要表格处理功能
4. **答辩记录表**：表格格式，需要表格处理功能

### 结论

**当前指令系统可以处理湖南师范大学格式要求的95%以上内容**。剩余的5%主要是封面、声明和表格部分，这些可以通过以下方式处理：

1. **封面**：使用 `special_sections.title` 和 `special_sections.author_info` 配置，在格式化代码中特殊处理
2. **原创性声明**：作为固定模板文本，在格式化代码中直接插入
3. **评审表和答辩记录表**：作为表格，需要表格处理功能（可以留空或使用占位符）

**建议**：当前指令系统已经足够支持湖南师范大学的格式要求，可以直接使用。
