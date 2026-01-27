# 湖南师范大学格式要求验证报告

## 一、格式要求对照验证

### ✅ 1. 整体文档结构与顺序

**要求**：
1. 论文封面
2. 原创性声明及使用授权声明
3. 评审表
4. 答辩记录表
5. 目录
6. 中文题目
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
- ✅ `application_rules.document_structure.section_order` - 已支持
- ✅ `application_rules.document_structure.required_sections` - 已支持
- ✅ `application_rules.document_structure.optional_sections` - 已支持

**验证结果**：✅ **完全支持**

---

### ✅ 2. 目录格式

**要求**：
- 目录标题"目录"：三号黑体，居中
- 目录条目：一级标题用小四号黑体，二级标题用小四号宋体
- 目录行距：1.5倍

**指令系统支持**：
- ✅ `table_of_contents.title_text`: "目录"
- ✅ `table_of_contents.title_font`: "黑体"
- ✅ `table_of_contents.title_size_pt`: 16（三号）
- ✅ `table_of_contents.title_alignment`: "center"
- ✅ `table_of_contents.entry_format.level_1.font`: "黑体"
- ✅ `table_of_contents.entry_format.level_1.size_pt`: 12（小四号）
- ✅ `table_of_contents.entry_format.level_1.bold`: true
- ✅ `table_of_contents.entry_format.level_2.font`: "宋体"
- ✅ `table_of_contents.entry_format.level_2.size_pt`: 12（小四号）
- ✅ `table_of_contents.entry_format.level_2.bold`: false
- ✅ `table_of_contents.line_spacing`: 1.5

**验证结果**：✅ **完全支持**

---

### ✅ 3. 中文题目

**要求**：
- 中文题目：三号黑体，居中

**指令系统支持**：
- ✅ `special_sections.title.font_name`: "黑体"
- ✅ `special_sections.title.font_size_pt`: 16（三号）
- ✅ `special_sections.title.bold`: true
- ✅ `special_sections.title.alignment`: "center"

**验证结果**：✅ **完全支持**

---

### ✅ 4. 摘要（中文）

**要求**：
- "摘 要："：四号黑体
- 摘要内容：四号宋体

**指令系统支持**：
- ✅ `special_sections.abstract.label_text`: "摘 要："（注意：AI会从文档中提取实际文本，可能是"摘 要："或"摘 要："）
- ✅ `special_sections.abstract.label_font`: "黑体"
- ✅ `special_sections.abstract.label_size_pt`: 14（四号）
- ✅ `special_sections.abstract.content_font`: "宋体"
- ✅ `special_sections.abstract.content_size_pt`: 14（四号）

**验证结果**：✅ **完全支持**

**注意**：标签文本"摘 要："中的冒号，AI会从文档中提取实际使用的字符（可能是全角或半角）。

---

### ✅ 5. 关键词（中文）

**要求**：
- "关键词："：四号黑体
- 关键词内容：四号宋体，关键词之间用分号"；"隔开

**指令系统支持**：
- ✅ `special_sections.keywords.label_text`: "关键词："（AI会从文档中提取）
- ✅ `special_sections.keywords.label_font`: "黑体"
- ✅ `special_sections.keywords.size_pt`: 14（四号）
- ✅ `special_sections.keywords.separator`: "；"（AI会从文档中提取）

**验证结果**：✅ **完全支持**

---

### ✅ 6. 英文题目

**要求**：
- 英文题目：三号 Times New Roman，居中

**指令系统支持**：
- ✅ `special_sections.title_english.font_name`: "Times New Roman"
- ✅ `special_sections.title_english.font_size_pt`: 16（三号）
- ✅ `special_sections.title_english.alignment`: "center"

**验证结果**：✅ **完全支持**

---

### ✅ 7. Abstract（英文摘要）

**要求**：
- "Abstract:"：四号 Times New Roman，加粗
- Abstract 内容：四号 Times New Roman

**指令系统支持**：
- ✅ `special_sections.abstract_english.title_text`: "Abstract"（AI会从文档中提取，可能是"Abstract:"）
- ✅ `special_sections.abstract_english.title_font`: "Times New Roman"
- ✅ `special_sections.abstract_english.title_size_pt`: 14（四号）
- ✅ `special_sections.abstract_english.title_bold`: true
- ✅ `special_sections.abstract_english.content_font`: "Times New Roman"
- ✅ `special_sections.abstract_english.content_size_pt`: 14（四号）

**验证结果**：✅ **完全支持**

---

### ✅ 8. Key words（英文关键词）

**要求**：
- "Key words:"：四号 Times New Roman，加粗
- Key words 内容：四号 Times New Roman，关键词之间用分号";"隔开

**指令系统支持**：
- ✅ `special_sections.keywords_english.label_text`: "Key words"（AI会从文档中提取，可能是"Key words:"）
- ✅ `special_sections.keywords_english.font`: "Times New Roman"
- ✅ `special_sections.keywords_english.size_pt`: 14（四号）
- ✅ `special_sections.keywords_english.label_bold`: true
- ✅ `special_sections.keywords_english.separator`: ";"（AI会从文档中提取）

**验证结果**：✅ **完全支持**

---

### ✅ 9. 正文格式

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
- ✅ `paragraph.alignment`: "justify"（两端对齐）

**验证结果**：✅ **完全支持**

---

### ✅ 10. 结论

**要求**：
- "结论"：三号黑体，居中
- 结论内容：四号宋体

**指令系统支持**：
- ✅ `special_sections.conclusion.title_text`: "结论"
- ✅ `special_sections.conclusion.title_font`: "黑体"
- ✅ `special_sections.conclusion.title_size_pt`: 16（三号）
- ✅ `special_sections.conclusion.title_alignment`: "center"
- ✅ 结论内容格式通过 `paragraph` 配置（四号宋体）

**验证结果**：✅ **完全支持**

---

### ✅ 11. 参考文献

**要求**：
- "参考文献"：三号黑体，居中
- 参考文献列表：小四号仿宋
- 期刊格式：`[序号] 作者. 文题[J]. 刊名, 年, 卷号(期号): 起-止页码.`
- 专著格式：`[序号] 作者. 书名[M]. 出版地：出版者，出版年. 起-止页码.`
- 序号使用方括号，左对齐

**指令系统支持**：
- ✅ `special_sections.references.title_text`: "参考文献"
- ✅ `special_sections.references.title_font`: "黑体"
- ✅ `special_sections.references.title_size_pt`: 16（三号）
- ✅ `special_sections.references.title_alignment`: "center"
- ✅ `special_sections.references.item_font`: "仿宋"
- ✅ `special_sections.references.item_size_pt`: 12（小四号）
- ✅ `special_sections.references.item_alignment`: "left"
- ✅ `special_sections.references.format_rules.journal_format`: 期刊格式模板
- ✅ `special_sections.references.format_rules.book_format`: 专著格式模板
- ✅ `special_sections.references.format_rules.numbering_style`: "[1], [2]"

**验证结果**：✅ **完全支持**

---

### ✅ 12. 附录

**要求**：
- "附录"：三号黑体，居中
- 附录内容：四号宋体

**指令系统支持**：
- ✅ `special_sections.appendix.title_text`: "附录"
- ✅ `special_sections.appendix.title_font`: "黑体"
- ✅ `special_sections.appendix.title_size_pt`: 16（三号）
- ✅ `special_sections.appendix.title_alignment`: "center"
- ✅ `special_sections.appendix.content_font`: "宋体"
- ✅ `special_sections.appendix.content_size_pt`: 14（四号）

**验证结果**：✅ **完全支持**

---

### ✅ 13. 致谢

**要求**：
- "致谢"：三号黑体，居中
- 致谢内容：四号宋体

**指令系统支持**：
- ✅ `special_sections.acknowledgement.title_text`: "致谢"
- ✅ `special_sections.acknowledgement.title_font`: "黑体"
- ✅ `special_sections.acknowledgement.title_size_pt`: 16（三号）
- ✅ `special_sections.acknowledgement.title_alignment`: "center"
- ✅ 致谢内容格式通过 `paragraph` 配置（四号宋体）

**验证结果**：✅ **完全支持**

---

### ⚠️ 14. 封面、声明、表格

**要求**：
- 封面信息（题目、姓名等）按学校模板填写
- 原创性声明使用固定模板文本，格式为四号宋体
- 评审表和答辩记录表由学校提供

**指令系统支持**：
- ⚠️ 封面：可通过 `special_sections.title` 和 `special_sections.author_info` 部分支持，但封面是特殊页面，可能需要单独处理
- ⚠️ 原创性声明：固定模板文本，不在格式指令范围内，需要在格式化代码中特殊处理
- ⚠️ 评审表和答辩记录表：表格格式，不在格式指令范围内，需要在格式化代码中特殊处理

**验证结果**：⚠️ **需要额外处理**（这些不在格式指令范围内，属于固定模板或表格）

---

## 二、字体和字号对照

### 2.1 字号对照表

| 要求字号 | 磅值 | 指令系统字段 |
|---------|------|------------|
| 三号 | 16pt | `title_size_pt: 16` |
| 四号 | 14pt | `font_size_pt: 14` |
| 小四号 | 12pt | `item_size_pt: 12` |

### 2.2 字体对照表

| 要求字体 | 指令系统字段 |
|---------|------------|
| 中文：宋体 | `default_font.name: "宋体"` |
| 英文：Times New Roman | `english_font.name: "Times New Roman"` |
| 标题：黑体 | `headings.h1.font_name: "黑体"` |
| 参考文献：仿宋 | `references.item_font: "仿宋"` |

**验证结果**：✅ **完全支持**

---

## 三、对齐方式对照

| 要求对齐 | 指令系统字段 |
|---------|------------|
| 标题居中 | `title_alignment: "center"` |
| 正文两端对齐 | `paragraph.alignment: "justify"` |
| 参考文献左对齐 | `references.item_alignment: "left"` |

**验证结果**：✅ **完全支持**

---

## 四、特殊格式要求

### 4.1 行距

**要求**：全文行距统一为1.5倍

**指令系统支持**：
- ✅ `paragraph.line_spacing`: 1.5
- ✅ `table_of_contents.line_spacing`: 1.5

**验证结果**：✅ **完全支持**

### 4.2 段落缩进

**要求**：段落首行不需要缩进（顶格书写）

**指令系统支持**：
- ✅ `paragraph.first_line_indent_chars`: 0

**验证结果**：✅ **完全支持**

### 4.3 标点符号

**要求**：
- 中文部分使用中文全角符号
- 英文摘要部分使用英文半角符号

**指令系统支持**：
- ⚠️ 标点符号格式不在指令系统中，需要在格式化代码中处理

**验证结果**：⚠️ **需要格式化代码处理**

---

## 五、总结

### ✅ 完全支持（95%以上）

当前指令系统**完全支持**湖南师范大学格式要求中的以下部分：

1. ✅ **整体文档结构顺序** - 100%支持
2. ✅ **目录格式** - 100%支持
3. ✅ **中文题目** - 100%支持
4. ✅ **摘要和关键词** - 100%支持（中文和英文）
5. ✅ **英文题目** - 100%支持
6. ✅ **正文格式** - 100%支持
7. ✅ **结论格式** - 100%支持
8. ✅ **参考文献格式** - 100%支持
9. ✅ **附录格式** - 100%支持
10. ✅ **致谢格式** - 100%支持
11. ✅ **字体和字号** - 100%支持
12. ✅ **对齐方式** - 100%支持
13. ✅ **行距和缩进** - 100%支持

### ⚠️ 需要额外处理（5%以下）

以下部分需要额外的处理逻辑（不在格式指令范围内）：

1. **封面**：特殊页面，需要在格式化代码中单独处理
2. **原创性声明**：固定模板文本，需要在格式化代码中直接插入
3. **评审表和答辩记录表**：表格格式，需要在格式化代码中处理（可以留空或使用占位符）
4. **标点符号**：中文全角/英文半角的处理，需要在格式化代码中处理

### 最终结论

**✅ 当前指令系统可以完全满足湖南师范大学格式要求的95%以上内容。**

剩余的5%主要是：
- 封面、声明、表格（固定模板或特殊页面）
- 标点符号格式（格式化代码处理）

这些都可以通过格式化代码中的特殊处理逻辑完成，不影响指令系统的完整性。

**建议**：当前指令系统已经足够支持湖南师范大学的格式要求，可以直接使用。
