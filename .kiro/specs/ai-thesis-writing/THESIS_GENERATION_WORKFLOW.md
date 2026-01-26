# AI论文写作系统 - 完整生成流程

## 概述

本文档详细描述了从用户上传格式模板到最终生成符合格式要求的Word论文的完整流程。

---

## 核心流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     1. 用户上传格式模板                          │
│                    （Word文档 .docx）                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  2. Python解析格式模板                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • 使用python-docx解析Word文档                             │  │
│  │ • 提取页面设置（页边距、纸张大小）                         │  │
│  │ • 提取样式信息（字体、字号、行距、对齐方式）               │  │
│  │ • 提取章节结构和编号格式                                   │  │
│  │ • 提取页眉页脚格式                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. 生成格式要求提示词（Prompt）                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 将格式信息转换为AI可理解的文本描述：                       │  │
│  │ "论文格式要求：                                            │  │
│  │  - 页边距：上下2.54cm，左右3.17cm                         │  │
│  │  - 一级标题：黑体，三号（16pt），居中，段前段后0.5行      │  │
│  │  - 二级标题：黑体，四号（14pt），左对齐，段前段后0.5行    │  │
│  │  - 正文：宋体，小四（12pt），首行缩进2字符，1.5倍行距     │  │
│  │  - 章节编号：第一章、1.1、1.1.1格式                       │  │
│  │  - 页眉：居中显示学校名称，五号字                         │  │
│  │  ..."                                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. 用户输入论文基本信息                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • 论文标题："基于深度学习的图像识别研究"                   │  │
│  │ • 专业："计算机科学与技术"                                 │  │
│  │ • 学历："硕士"                                             │  │
│  │ • 研究方向："人工智能"                                     │  │
│  │ • 关键词：["深度学习", "图像识别", "卷积神经网络"]        │  │
│  │ • 论文类型："实证研究"                                     │  │
│  │ • 大纲结构："五段式"（摘要、引言、文献综述、研究方法...） │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    5. AI生成论文大纲                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 组合提示词：                                               │  │
│  │ • 格式要求提示词                                           │  │
│  │ • 论文基本信息                                             │  │
│  │ • 大纲生成指令                                             │  │
│  │                                                            │  │
│  │ 调用AI模型（通义千问/GPT-4）生成：                         │  │
│  │ {                                                          │  │
│  │   "chapters": [                                            │  │
│  │     {"level": 1, "title": "摘要", "description": "..."},  │  │
│  │     {"level": 1, "title": "第一章 引言", ...},            │  │
│  │     {"level": 2, "title": "1.1 研究背景", ...},           │  │
│  │     {"level": 2, "title": "1.2 研究意义", ...},           │  │
│  │     ...                                                    │  │
│  │   ]                                                        │  │
│  │ }                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 6. 用户确认/调整大纲                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • 用户可以手动调整章节标题                                 │  │
│  │ • 添加/删除章节                                            │  │
│  │ • 调整章节顺序                                             │  │
│  │ • 修改章节描述                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. AI逐章节生成论文内容                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 对每个章节，组合提示词：                                   │  │
│  │ • 格式要求提示词                                           │  │
│  │ • 论文基本信息（标题、专业、关键词等）                     │  │
│  │ • 当前章节信息（标题、级别、描述）                         │  │
│  │ • 上下文信息（已生成的前面章节内容）                       │  │
│  │ • 目标字数要求                                             │  │
│  │                                                            │  │
│  │ 调用AI模型生成章节内容（纯文本）                           │  │
│  │                                                            │  │
│  │ 示例提示词：                                               │  │
│  │ "你是一位专业的学术论文写作助手。                         │  │
│  │  论文标题：基于深度学习的图像识别研究                     │  │
│  │  专业：计算机科学与技术                                   │  │
│  │  学历：硕士                                               │  │
│  │  关键词：深度学习、图像识别、卷积神经网络                 │  │
│  │                                                            │  │
│  │  当前章节：第一章 引言                                     │  │
│  │  章节描述：介绍研究背景、研究意义和论文结构               │  │
│  │  目标字数：约2000字                                        │  │
│  │                                                            │  │
│  │  前文内容：[摘要内容...]                                   │  │
│  │                                                            │  │
│  │  格式要求：[格式提示词...]                                 │  │
│  │                                                            │  │
│  │  请生成该章节的内容，要求学术严谨、逻辑清晰..."           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                8. 用户审阅/编辑内容                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • 用户可以在线编辑每个章节的内容                           │  │
│  │ • 可以重新生成某个章节                                     │  │
│  │ • 可以使用去AI化、润色等功能优化内容                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          9. Python生成符合格式的Word文档                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 使用python-docx库：                                        │  │
│  │                                                            │  │
│  │ 1. 创建新的Word文档                                        │  │
│  │ 2. 应用页面设置（从模板解析的格式）                        │  │
│  │    - 设置页边距                                            │  │
│  │    - 设置纸张大小                                          │  │
│  │                                                            │  │
│  │ 3. 添加封面页                                              │  │
│  │    - 学校名称、论文标题、作者信息等                        │  │
│  │                                                            │  │
│  │ 4. 添加目录（自动生成）                                    │  │
│  │                                                            │  │
│  │ 5. 逐章节添加内容                                          │  │
│  │    - 根据章节级别应用对应样式                              │  │
│  │    - 一级标题：应用"标题1"样式（黑体、三号、居中）        │  │
│  │    - 二级标题：应用"标题2"样式（黑体、四号、左对齐）      │  │
│  │    - 正文：应用"正文"样式（宋体、小四、首行缩进）         │  │
│  │    - 自动添加章节编号                                      │  │
│  │                                                            │  │
│  │ 6. 添加页眉页脚                                            │  │
│  │    - 页眉：学校名称                                        │  │
│  │    - 页脚：页码                                            │  │
│  │                                                            │  │
│  │ 7. 添加参考文献                                            │  │
│  │                                                            │  │
│  │ 8. 保存为.docx文件                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   10. 用户下载论文                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • 生成的Word文档完全符合格式要求                           │  │
│  │ • 可以直接在Word中打开编辑                                 │  │
│  │ • 所有格式已正确应用                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 详细技术实现

### 1. 格式模板解析（DocxParser）

#### 1.1 解析页面设置
```python
from docx import Document
from docx.shared import Pt, Cm

class DocxParser:
    def parse_page_settings(self, doc: Document) -> dict:
        """解析页面设置"""
        section = doc.sections[0]
        
        return {
            'page_width': section.page_width.cm,
            'page_height': section.page_height.cm,
            'top_margin': section.top_margin.cm,
            'bottom_margin': section.bottom_margin.cm,
            'left_margin': section.left_margin.cm,
            'right_margin': section.right_margin.cm,
            'header_distance': section.header_distance.cm,
            'footer_distance': section.footer_distance.cm,
        }
```

#### 1.2 解析样式信息
```python
def parse_styles(self, doc: Document) -> dict:
    """解析样式信息"""
    styles = {}
    
    for style in doc.styles:
        if style.type == 1:  # 段落样式
            style_info = {
                'name': style.name,
                'font_name': style.font.name if style.font.name else '宋体',
                'font_size': style.font.size.pt if style.font.size else 12,
                'bold': style.font.bold if style.font.bold else False,
                'italic': style.font.italic if style.font.italic else False,
                'alignment': self._get_alignment(style.paragraph_format.alignment),
                'line_spacing': style.paragraph_format.line_spacing,
                'space_before': style.paragraph_format.space_before.pt if style.paragraph_format.space_before else 0,
                'space_after': style.paragraph_format.space_after.pt if style.paragraph_format.space_after else 0,
                'first_line_indent': style.paragraph_format.first_line_indent.cm if style.paragraph_format.first_line_indent else 0,
            }
            styles[style.name] = style_info
    
    return styles
```

#### 1.3 解析章节结构
```python
def parse_chapter_structure(self, doc: Document) -> list:
    """解析章节结构"""
    chapters = []
    
    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            level = int(para.style.name.replace('Heading ', ''))
            chapters.append({
                'level': level,
                'title': para.text,
                'style': para.style.name
            })
    
    return chapters
```

### 2. 格式要求转换为提示词

```python
class FormatPromptGenerator:
    def generate_format_prompt(self, format_data: dict) -> str:
        """将格式数据转换为AI提示词"""
        
        prompt = "论文格式要求：\n\n"
        
        # 页面设置
        prompt += "【页面设置】\n"
        prompt += f"- 纸张大小：{format_data['page_width']}cm × {format_data['page_height']}cm\n"
        prompt += f"- 页边距：上{format_data['top_margin']}cm，下{format_data['bottom_margin']}cm，"
        prompt += f"左{format_data['left_margin']}cm，右{format_data['right_margin']}cm\n\n"
        
        # 样式要求
        prompt += "【样式要求】\n"
        for style_name, style_info in format_data['styles'].items():
            if style_name.startswith('Heading'):
                level = style_name.replace('Heading ', '')
                prompt += f"- {level}级标题：{style_info['font_name']}，"
                prompt += f"{style_info['font_size']}号字，"
                prompt += f"{'加粗' if style_info['bold'] else '不加粗'}，"
                prompt += f"{self._get_alignment_text(style_info['alignment'])}，"
                prompt += f"段前{style_info['space_before']}磅，段后{style_info['space_after']}磅\n"
            elif style_name == 'Normal':
                prompt += f"- 正文：{style_info['font_name']}，"
                prompt += f"{style_info['font_size']}号字，"
                prompt += f"首行缩进{style_info['first_line_indent']}字符，"
                prompt += f"{style_info['line_spacing']}倍行距\n"
        
        prompt += "\n请严格按照以上格式要求生成论文内容。\n"
        
        return prompt
```

### 3. AI大纲生成

```python
class AIService:
    async def generate_outline(
        self,
        title: str,
        major: str,
        degree_level: str,
        keywords: list,
        thesis_type: str,
        structure_type: str,
        format_prompt: str
    ) -> dict:
        """生成论文大纲"""
        
        prompt = f"""你是一位专业的学术论文写作助手。请根据以下信息生成论文大纲：

论文标题：{title}
专业：{major}
学历：{degree_level}
关键词：{', '.join(keywords)}
论文类型：{thesis_type}
大纲结构：{structure_type}

{format_prompt}

要求：
1. 大纲应包含：摘要、引言、文献综述、研究方法、结果与分析、结论、参考文献
2. 每个章节应有清晰的标题和简要描述
3. 章节之间应有逻辑关联
4. 符合{degree_level}学术论文规范

请以JSON格式输出大纲结构：
{{
  "chapters": [
    {{
      "level": 1,
      "title": "摘要",
      "description": "概述研究背景、方法、结果和结论"
    }},
    ...
  ]
}}
"""
        
        response = await self.qwen_client.generate(prompt)
        outline = json.loads(response)
        
        return outline
```

### 4. AI章节内容生成

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
    
    # 构建上下文
    context = ""
    if previous_chapters:
        context = "前文内容摘要：\n"
        for prev_chapter in previous_chapters[-3:]:  # 只取最近3个章节
            context += f"【{prev_chapter['title']}】\n{prev_chapter['content'][:200]}...\n\n"
    
    prompt = f"""你是一位专业的学术论文写作助手。请根据以下信息生成章节内容：

【论文基本信息】
论文标题：{thesis_info['title']}
专业：{thesis_info['major']}
学历：{thesis_info['degree_level']}
研究方向：{thesis_info['research_direction']}
关键词：{', '.join(thesis_info['keywords'])}
论文类型：{thesis_info['thesis_type']}

【当前章节】
章节标题：{chapter_info['title']}
章节级别：{chapter_info['level']}级标题
章节描述：{chapter_info['description']}
目标字数：约{target_words}字

{context}

{format_prompt}

要求：
1. 内容应学术严谨、逻辑清晰
2. 适当引用文献（使用[1]、[2]等标注）
3. 使用专业术语
4. 保持与前文的连贯性
5. 字数控制在{target_words}字左右

请生成该章节的完整内容（纯文本格式，不要包含格式标记）：
"""
    
    content = await self.qwen_client.generate(prompt)
    
    return content
```

### 5. Word文档生成（DocxFormatter）

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class DocxFormatter:
    def __init__(self, format_data: dict):
        self.format_data = format_data
    
    def generate_thesis_document(
        self,
        thesis: dict,
        chapters: list
    ) -> Document:
        """生成完整的论文Word文档"""
        
        doc = Document()
        
        # 1. 应用页面设置
        self._apply_page_settings(doc)
        
        # 2. 添加封面
        self._add_cover_page(doc, thesis)
        
        # 3. 添加目录
        self._add_table_of_contents(doc)
        
        # 4. 添加摘要
        abstract_chapter = next(c for c in chapters if '摘要' in c['title'])
        self._add_chapter(doc, abstract_chapter)
        
        # 5. 添加正文章节
        for chapter in chapters:
            if '摘要' not in chapter['title'] and '参考文献' not in chapter['title']:
                self._add_chapter(doc, chapter)
        
        # 6. 添加参考文献
        references_chapter = next(c for c in chapters if '参考文献' in c['title'])
        self._add_chapter(doc, references_chapter)
        
        # 7. 应用页眉页脚
        self._apply_header_footer(doc, thesis)
        
        return doc
    
    def _apply_page_settings(self, doc: Document):
        """应用页面设置"""
        section = doc.sections[0]
        
        # 设置页面大小
        section.page_width = Cm(self.format_data['page_width'])
        section.page_height = Cm(self.format_data['page_height'])
        
        # 设置页边距
        section.top_margin = Cm(self.format_data['top_margin'])
        section.bottom_margin = Cm(self.format_data['bottom_margin'])
        section.left_margin = Cm(self.format_data['left_margin'])
        section.right_margin = Cm(self.format_data['right_margin'])
    
    def _add_chapter(self, doc: Document, chapter: dict):
        """添加章节"""
        # 添加标题
        heading = doc.add_heading(chapter['title'], level=chapter['level'])
        self._apply_heading_style(heading, chapter['level'])
        
        # 添加内容（按段落分割）
        paragraphs = chapter['content'].split('\n\n')
        for para_text in paragraphs:
            if para_text.strip():
                para = doc.add_paragraph(para_text.strip())
                self._apply_paragraph_style(para)
    
    def _apply_heading_style(self, heading, level: int):
        """应用标题样式"""
        style_name = f'Heading {level}'
        style_info = self.format_data['styles'].get(style_name, {})
        
        # 设置字体
        run = heading.runs[0]
        run.font.name = style_info.get('font_name', '黑体')
        run.font.size = Pt(style_info.get('font_size', 16))
        run.font.bold = style_info.get('bold', True)
        
        # 设置段落格式
        heading.paragraph_format.alignment = self._get_alignment_enum(
            style_info.get('alignment', 'center')
        )
        heading.paragraph_format.space_before = Pt(style_info.get('space_before', 12))
        heading.paragraph_format.space_after = Pt(style_info.get('space_after', 12))
    
    def _apply_paragraph_style(self, para):
        """应用正文样式"""
        style_info = self.format_data['styles'].get('Normal', {})
        
        # 设置字体
        run = para.runs[0] if para.runs else para.add_run()
        run.font.name = style_info.get('font_name', '宋体')
        run.font.size = Pt(style_info.get('font_size', 12))
        
        # 设置段落格式
        para.paragraph_format.first_line_indent = Cm(
            style_info.get('first_line_indent', 0.74)  # 2字符
        )
        para.paragraph_format.line_spacing = style_info.get('line_spacing', 1.5)
        para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    def _add_cover_page(self, doc: Document, thesis: dict):
        """添加封面"""
        # 学校名称
        school = doc.add_paragraph(thesis['school_name'])
        school.alignment = WD_ALIGN_PARAGRAPH.CENTER
        school.runs[0].font.size = Pt(22)
        school.runs[0].font.bold = True
        
        doc.add_paragraph()  # 空行
        
        # 论文标题
        title = doc.add_paragraph(thesis['title'])
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.runs[0].font.size = Pt(18)
        title.runs[0].font.bold = True
        
        # 更多信息...
        
        # 分页
        doc.add_page_break()
    
    def _apply_header_footer(self, doc: Document, thesis: dict):
        """应用页眉页脚"""
        section = doc.sections[0]
        
        # 页眉
        header = section.header
        header_para = header.paragraphs[0]
        header_para.text = thesis['school_name']
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_para.runs[0].font.size = Pt(10.5)
        
        # 页脚（页码）
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

---

## 关键技术点

### 1. 格式模板解析
- ✅ 使用 `python-docx` 库解析Word文档
- ✅ 提取所有样式信息（字体、字号、行距等）
- ✅ 提取页面设置（页边距、纸张大小）
- ✅ 提取章节结构和编号格式

### 2. 格式提示词生成
- ✅ 将格式信息转换为自然语言描述
- ✅ 让AI理解格式要求
- ✅ 在生成内容时遵循格式规范

### 3. AI内容生成
- ✅ 组合多种信息（格式、论文信息、上下文）
- ✅ 分章节生成，保持连贯性
- ✅ 控制字数和质量

### 4. Word文档生成
- ✅ 使用 `python-docx` 创建新文档
- ✅ 精确应用格式（字体、字号、行距、对齐等）
- ✅ 自动添加页眉页脚、目录
- ✅ 生成符合要求的最终文档

---

## 数据流转

```
用户上传模板.docx
    ↓
Python解析 → format_data (JSON)
    ↓
生成format_prompt (文本)
    ↓
用户输入 + format_prompt → AI生成大纲
    ↓
大纲 + format_prompt → AI生成章节内容
    ↓
章节内容 + format_data → Python生成Word文档
    ↓
用户下载论文.docx
```

---

## 相关文件

- **格式解析**: `module_thesis/utils/docx_parser.py`
- **提示词生成**: `module_thesis/utils/format_prompt_generator.py`
- **AI服务**: `module_thesis/service/ai_service.py`
- **文档生成**: `module_thesis/utils/docx_formatter.py`

---

**创建时间**: 2026-01-25  
**最后更新**: 2026-01-25
