# 论文生成流程补充说明

## 补充内容概述

本文档补充了AI论文写作系统的完整生成流程，特别是以下关键环节：

1. **格式模板解析** - 如何读取和解析用户上传的Word格式模板
2. **格式提示词生成** - 如何将格式要求转换为AI可理解的提示词
3. **AI内容生成** - 如何组合多种信息生成高质量论文内容
4. **Word文档生成** - 如何用Python根据格式和内容生成最终论文

## 核心流程

### 完整的10步流程

```
1. 用户上传格式模板（Word文档）
   ↓
2. Python解析格式模板（python-docx）
   ↓
3. 生成格式要求提示词
   ↓
4. 用户输入论文基本信息（标题、专业、学历等）
   ↓
5. AI生成论文大纲
   ↓
6. 用户确认/调整大纲
   ↓
7. AI逐章节生成论文内容
   ↓
8. 用户审阅/编辑内容
   ↓
9. Python生成符合格式的Word文档
   ↓
10. 用户下载论文
```

## 关键技术实现

### 1. 格式模板解析（DocxParser）

**功能**：读取用户上传的Word模板，提取所有格式信息

**实现文件**：`module_thesis/utils/docx_parser.py`

**提取内容**：
- 页面设置（页边距、纸张大小）
- 样式信息（字体、字号、行距、对齐方式）
- 章节结构和编号格式
- 页眉页脚格式

**核心代码**：
```python
from docx import Document

class DocxParser:
    def parse_document(self, file_path: str) -> dict:
        """解析Word文档，提取格式信息"""
        doc = Document(file_path)
        
        return {
            'page_settings': self.parse_page_settings(doc),
            'styles': self.parse_styles(doc),
            'chapter_structure': self.parse_chapter_structure(doc),
            'header_footer': self.parse_header_footer(doc)
        }
```

### 2. 格式提示词生成（FormatPromptGenerator）

**功能**：将格式信息转换为AI可理解的自然语言描述

**实现文件**：`module_thesis/utils/format_prompt_generator.py`

**转换示例**：
```
输入（格式数据）：
{
  'page_width': 21.0,
  'page_height': 29.7,
  'top_margin': 2.54,
  'styles': {
    'Heading 1': {
      'font_name': '黑体',
      'font_size': 16,
      'bold': True,
      'alignment': 'center'
    }
  }
}

输出（提示词）：
"论文格式要求：
- 纸张大小：21.0cm × 29.7cm（A4）
- 页边距：上2.54cm，下2.54cm，左3.17cm，右3.17cm
- 一级标题：黑体，三号（16pt），加粗，居中
- 正文：宋体，小四（12pt），首行缩进2字符，1.5倍行距
..."
```

### 3. AI内容生成（AIService）

**功能**：组合格式提示词、论文信息、上下文，调用AI生成内容

**实现文件**：`module_thesis/service/ai_service.py`

**生成大纲**：
```python
async def generate_outline(
    self,
    title: str,
    major: str,
    degree_level: str,
    keywords: list,
    format_prompt: str
) -> dict:
    """生成论文大纲"""
    
    prompt = f"""
    论文标题：{title}
    专业：{major}
    学历：{degree_level}
    关键词：{', '.join(keywords)}
    
    {format_prompt}
    
    请生成论文大纲...
    """
    
    response = await self.qwen_client.generate(prompt)
    return json.loads(response)
```

**生成章节内容**：
```python
async def generate_chapter_content(
    self,
    thesis_info: dict,
    chapter_info: dict,
    previous_chapters: list,
    format_prompt: str,
    target_words: int = 2000
) -> str:
    """生成章节内容"""
    
    # 构建上下文（前面章节的摘要）
    context = self._build_context(previous_chapters)
    
    prompt = f"""
    【论文基本信息】
    论文标题：{thesis_info['title']}
    专业：{thesis_info['major']}
    关键词：{', '.join(thesis_info['keywords'])}
    
    【当前章节】
    章节标题：{chapter_info['title']}
    章节描述：{chapter_info['description']}
    目标字数：约{target_words}字
    
    【前文内容】
    {context}
    
    {format_prompt}
    
    请生成该章节的完整内容...
    """
    
    content = await self.qwen_client.generate(prompt)
    return content
```

### 4. Word文档生成（DocxFormatter）

**功能**：根据格式数据和论文内容，生成符合格式要求的Word文档

**实现文件**：`module_thesis/utils/docx_formatter.py`

**核心流程**：
```python
from docx import Document
from docx.shared import Pt, Cm

class DocxFormatter:
    def generate_thesis_document(
        self,
        thesis: dict,
        chapters: list,
        format_data: dict
    ) -> Document:
        """生成完整的论文Word文档"""
        
        doc = Document()
        
        # 1. 应用页面设置
        self._apply_page_settings(doc, format_data)
        
        # 2. 添加封面
        self._add_cover_page(doc, thesis)
        
        # 3. 添加目录
        self._add_table_of_contents(doc)
        
        # 4. 逐章节添加内容
        for chapter in chapters:
            self._add_chapter(doc, chapter, format_data)
        
        # 5. 应用页眉页脚
        self._apply_header_footer(doc, thesis, format_data)
        
        return doc
    
    def _add_chapter(self, doc: Document, chapter: dict, format_data: dict):
        """添加章节"""
        # 添加标题（应用对应级别的样式）
        heading = doc.add_heading(chapter['title'], level=chapter['level'])
        self._apply_heading_style(heading, chapter['level'], format_data)
        
        # 添加内容（应用正文样式）
        paragraphs = chapter['content'].split('\n\n')
        for para_text in paragraphs:
            para = doc.add_paragraph(para_text.strip())
            self._apply_paragraph_style(para, format_data)
    
    def _apply_heading_style(self, heading, level: int, format_data: dict):
        """应用标题样式"""
        style_name = f'Heading {level}'
        style_info = format_data['styles'][style_name]
        
        # 设置字体
        run = heading.runs[0]
        run.font.name = style_info['font_name']
        run.font.size = Pt(style_info['font_size'])
        run.font.bold = style_info['bold']
        
        # 设置段落格式
        heading.paragraph_format.alignment = style_info['alignment']
        heading.paragraph_format.space_before = Pt(style_info['space_before'])
        heading.paragraph_format.space_after = Pt(style_info['space_after'])
```

## 数据流转图

```
┌──────────────────┐
│ 用户上传模板.docx │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│ DocxParser.parse_document()  │
│ 提取格式信息                  │
└────────┬─────────────────────┘
         │
         ▼ format_data (JSON)
┌──────────────────────────────────────┐
│ FormatPromptGenerator.generate()     │
│ 转换为AI提示词                        │
└────────┬─────────────────────────────┘
         │
         ▼ format_prompt (文本)
┌──────────────────────────────────────┐
│ 用户输入：标题、专业、学历、关键词    │
└────────┬─────────────────────────────┘
         │
         ▼ thesis_info + format_prompt
┌──────────────────────────────────────┐
│ AIService.generate_outline()         │
│ 生成论文大纲                          │
└────────┬─────────────────────────────┘
         │
         ▼ outline (JSON)
┌──────────────────────────────────────┐
│ 用户确认/调整大纲                     │
└────────┬─────────────────────────────┘
         │
         ▼ confirmed_outline
┌──────────────────────────────────────┐
│ AIService.generate_chapter_content() │
│ 逐章节生成内容                        │
│ （循环处理每个章节）                  │
└────────┬─────────────────────────────┘
         │
         ▼ chapters (list)
┌──────────────────────────────────────┐
│ 用户审阅/编辑内容                     │
└────────┬─────────────────────────────┘
         │
         ▼ final_chapters + format_data
┌──────────────────────────────────────┐
│ DocxFormatter.generate_document()    │
│ 生成Word文档                          │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────┐
│ 用户下载论文.docx │
└──────────────────┘
```

## 需要创建的工具类

### 1. DocxParser（格式解析器）
**文件**：`module_thesis/utils/docx_parser.py`

**主要方法**：
- `parse_document(file_path)` - 解析整个文档
- `parse_page_settings(doc)` - 解析页面设置
- `parse_styles(doc)` - 解析样式信息
- `parse_chapter_structure(doc)` - 解析章节结构
- `parse_header_footer(doc)` - 解析页眉页脚

### 2. FormatPromptGenerator（格式提示词生成器）
**文件**：`module_thesis/utils/format_prompt_generator.py`

**主要方法**：
- `generate_format_prompt(format_data)` - 生成完整的格式提示词
- `_format_page_settings(data)` - 格式化页面设置描述
- `_format_styles(data)` - 格式化样式描述
- `_get_alignment_text(alignment)` - 转换对齐方式为文本

### 3. DocxFormatter（Word文档生成器）
**文件**：`module_thesis/utils/docx_formatter.py`

**主要方法**：
- `generate_thesis_document(thesis, chapters, format_data)` - 生成完整文档
- `_apply_page_settings(doc, format_data)` - 应用页面设置
- `_add_cover_page(doc, thesis)` - 添加封面
- `_add_table_of_contents(doc)` - 添加目录
- `_add_chapter(doc, chapter, format_data)` - 添加章节
- `_apply_heading_style(heading, level, format_data)` - 应用标题样式
- `_apply_paragraph_style(para, format_data)` - 应用正文样式
- `_apply_header_footer(doc, thesis, format_data)` - 应用页眉页脚

### 4. AIService（AI服务）
**文件**：`module_thesis/service/ai_service.py`

**主要方法**：
- `generate_outline(...)` - 生成论文大纲
- `generate_chapter_content(...)` - 生成章节内容
- `_build_context(previous_chapters)` - 构建上下文
- `_build_outline_prompt(...)` - 构建大纲生成提示词
- `_build_chapter_prompt(...)` - 构建章节生成提示词

## 依赖库

### python-docx
用于Word文档的读取和生成

```bash
pip install python-docx
```

**主要功能**：
- 读取.docx文件
- 提取样式、格式信息
- 创建新的Word文档
- 设置字体、段落格式
- 添加页眉页脚

### 通义千问SDK
用于AI内容生成

```bash
pip install dashscope
```

**主要功能**：
- 调用通义千问API
- 生成论文大纲
- 生成章节内容

## 配置要求

### 1. 通义千问API配置
```python
# config/ai_config.py
QWEN_API_KEY = "your-api-key"
QWEN_MODEL = "qwen-max"  # 或 qwen-plus
```

### 2. 文件存储配置
```python
# config/storage_config.py
TEMPLATE_UPLOAD_PATH = "/path/to/templates"
THESIS_EXPORT_PATH = "/path/to/exports"
MAX_TEMPLATE_SIZE = 10 * 1024 * 1024  # 10MB
```

## 性能优化

### 1. 格式模板缓存
解析后的格式数据缓存到Redis，避免重复解析

### 2. AI生成异步处理
章节内容生成使用异步任务，支持并发生成多个章节

### 3. 文档生成队列
Word文档生成放入队列，避免阻塞主线程

## 错误处理

### 1. 格式模板解析失败
- 检查文件格式是否正确
- 提供默认格式模板
- 记录错误日志

### 2. AI生成失败
- 重试机制（最多3次）
- 降级到备用模型
- 提供手动编辑选项

### 3. Word文档生成失败
- 检查格式数据完整性
- 提供纯文本导出选项
- 记录错误详情

## 相关文档

- [完整流程详解](./THESIS_GENERATION_WORKFLOW.md)
- [数据库设计](./DATABASE_SCHEMA_COMPLETE.md)
- [实体类文档](./ENTITY_CLASSES_COMPLETE.md)
- [设计文档](./design.md)

---

**创建时间**: 2026-01-25  
**最后更新**: 2026-01-25
