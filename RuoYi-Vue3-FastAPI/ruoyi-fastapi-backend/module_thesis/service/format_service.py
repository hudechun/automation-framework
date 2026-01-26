"""
论文格式化服务 - 使用AI读取Word文档并生成格式化指令，然后进行格式化
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_thesis.service.ai_generation_service import AiGenerationService
from utils.log_util import logger

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    DOCX_AVAILABLE = True
except ImportError as e:
    DOCX_AVAILABLE = False
    # 为了类型注解，定义一个占位符类型
    if TYPE_CHECKING:
        from docx import Document
    else:
        Document = None  # type: ignore
    logger.warning(f"python-docx 未安装，Word文档处理功能将不可用。请运行: pip install python-docx。错误详情: {str(e)}")


class FormatService:
    """
    论文格式化服务类
    """
    
    @classmethod
    async def read_word_document_with_ai(
        cls,
        query_db: AsyncSession,
        word_file_path: str,
        config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        使用AI读取Word文档并提取格式指令
        
        :param query_db: 数据库会话
        :param word_file_path: Word文档路径
        :param config_id: AI模型配置ID（可选）
        :return: 格式指令和文档分析结果
        """
        if not DOCX_AVAILABLE:
            raise ServiceException(message='python-docx 未安装，无法处理Word文档。请运行: pip install python-docx')
        
        if not os.path.exists(word_file_path):
            raise ServiceException(message=f'Word文档不存在: {word_file_path}')
        
        # 检查文件格式：python-docx 只能处理 .docx 格式，不能处理 .doc 格式
        file_ext = os.path.splitext(word_file_path)[1].lower()
        if file_ext == '.doc':
            raise ServiceException(
                message=f'模板文件是 .doc 格式，无法直接处理。python-docx 只能处理 .docx 格式。'
                f'请将模板文件转换为 .docx 格式后重新上传。文件路径: {word_file_path}'
            )
        elif file_ext != '.docx':
            raise ServiceException(
                message=f'模板文件格式不支持（当前格式: {file_ext}）。请使用 .docx 格式的Word文档。文件路径: {word_file_path}'
            )
        
        try:
            # 读取Word文档
            doc = Document(word_file_path)
            
            # 提取文档内容（文本、格式信息）
            document_content = cls._extract_document_content(doc)
            
            # 使用AI分析文档格式并生成格式化指令
            format_instructions = await cls._analyze_format_with_ai(
                query_db,
                document_content,
                config_id
            )
            
            logger.info(f"AI读取Word文档完成 - 文件: {word_file_path}, 格式指令长度: {len(format_instructions)}")
            
            return {
                'format_instructions': format_instructions,
                'document_analysis': document_content,
                'file_path': word_file_path
            }
            
        except Exception as e:
            logger.error(f"读取Word文档失败: {str(e)}", exc_info=True)
            raise ServiceException(message=f'读取Word文档失败: {str(e)}')
    
    @classmethod
    def _extract_document_content(cls, doc: Any) -> Dict[str, Any]:
        """
        提取Word文档的内容和格式信息
        
        识别以下格式要求：
        1. 字体格式：字体名称、大小、颜色、粗体、斜体、下划线
        2. 段落格式：对齐方式、行距、段前距、段后距、首行缩进、左右缩进
        3. 标题格式：各级标题的样式（字体、大小、对齐等）
        4. 页面设置：页边距、纸张大小、页眉页脚
        5. 样式信息：文档中使用的样式名称和属性
        
        :param doc: python-docx Document对象
        :return: 文档内容字典
        """
        content = {
            'paragraphs': [],
            'styles': {},
            'headings': {},  # 识别标题格式
            'format_info': {
                'font_name': None,
                'font_size': None,
                'line_spacing': None,
                'paragraph_spacing': None,
                'margins': None,
                'page_size': None,
            }
        }
        
        # 提取段落内容和格式
        for para in doc.paragraphs:
            para_info = {
                'text': para.text,
                'style': para.style.name if para.style else None,
                'alignment': str(para.alignment) if para.alignment else None,
            }
            
            # 提取段落格式信息
            if para.paragraph_format:
                para_info['paragraph_format'] = {
                    'alignment': str(para.alignment) if para.alignment else None,
                    'line_spacing': str(para.paragraph_format.line_spacing) if para.paragraph_format.line_spacing else None,
                    'line_spacing_rule': str(para.paragraph_format.line_spacing_rule) if para.paragraph_format.line_spacing_rule else None,
                    'space_before': str(para.paragraph_format.space_before) if para.paragraph_format.space_before else None,
                    'space_after': str(para.paragraph_format.space_after) if para.paragraph_format.space_after else None,
                    'first_line_indent': str(para.paragraph_format.first_line_indent) if para.paragraph_format.first_line_indent else None,
                    'left_indent': str(para.paragraph_format.left_indent) if para.paragraph_format.left_indent else None,
                    'right_indent': str(para.paragraph_format.right_indent) if para.paragraph_format.right_indent else None,
                }
            
            # 提取段落中的文本运行格式信息
            runs_info = []
            for run in para.runs:
                run_info = {
                    'text': run.text,
                    'bold': run.bold,
                    'italic': run.italic,
                    'underline': run.underline,
                    'font_name': run.font.name if run.font.name else None,
                    'font_size': str(run.font.size) if run.font.size else None,
                    'font_color': str(run.font.color.rgb) if run.font.color and run.font.color.rgb else None,
                }
                runs_info.append(run_info)
            para_info['runs'] = runs_info
            content['paragraphs'].append(para_info)
            
            # 识别标题格式（通过样式名称或格式特征）
            if para.style and para.style.name:
                style_name = para.style.name.lower()
                if 'heading' in style_name or 'title' in style_name or '标题' in style_name:
                    # 提取标题级别和格式
                    heading_level = None
                    if 'heading 1' in style_name or '标题 1' in style_name or 'h1' in style_name:
                        heading_level = 1
                    elif 'heading 2' in style_name or '标题 2' in style_name or 'h2' in style_name:
                        heading_level = 2
                    elif 'heading 3' in style_name or '标题 3' in style_name or 'h3' in style_name:
                        heading_level = 3
                    
                    if heading_level:
                        if heading_level not in content['headings']:
                            content['headings'][f'h{heading_level}'] = {
                                'style_name': para.style.name,
                                'font_name': runs_info[0]['font_name'] if runs_info else None,
                                'font_size': runs_info[0]['font_size'] if runs_info else None,
                                'bold': runs_info[0]['bold'] if runs_info else None,
                                'alignment': para_info['alignment'],
                            }
        
        # 提取默认样式信息（从正文段落）
        body_paragraphs = [p for p in doc.paragraphs if p.style and 'heading' not in p.style.name.lower() and 'title' not in p.style.name.lower()]
        if body_paragraphs:
            first_body_para = body_paragraphs[0]
            if first_body_para.runs:
                first_run = first_body_para.runs[0]
                if first_run.font.name:
                    content['format_info']['font_name'] = first_run.font.name
                if first_run.font.size:
                    content['format_info']['font_size'] = str(first_run.font.size)
            
            # 提取段落格式（从第一个正文段落）
            if first_body_para.paragraph_format:
                if first_body_para.paragraph_format.line_spacing:
                    content['format_info']['line_spacing'] = str(first_body_para.paragraph_format.line_spacing)
                if first_body_para.paragraph_format.space_before:
                    content['format_info']['paragraph_spacing_before'] = str(first_body_para.paragraph_format.space_before)
                if first_body_para.paragraph_format.space_after:
                    content['format_info']['paragraph_spacing_after'] = str(first_body_para.paragraph_format.space_after)
        
        # 提取节信息（页边距、纸张大小等）
        if doc.sections:
            section = doc.sections[0]
            content['format_info']['margins'] = {
                'top': str(section.top_margin),
                'bottom': str(section.bottom_margin),
                'left': str(section.left_margin),
                'right': str(section.right_margin),
            }
            
            # 提取纸张大小
            if section.page_width and section.page_height:
                content['format_info']['page_size'] = {
                    'width': str(section.page_width),
                    'height': str(section.page_height),
                }
        
        # 提取文档样式信息
        if hasattr(doc.styles, 'styles'):
            for style in doc.styles.styles:
                if style.name and style.name not in ['Normal', 'Default Paragraph Font']:
                    content['styles'][style.name] = {
                        'type': str(style.type) if hasattr(style, 'type') else None,
                    }
        
        return content
    
    @classmethod
    async def _analyze_format_with_ai(
        cls,
        query_db: AsyncSession,
        document_content: Dict[str, Any],
        config_id: Optional[int] = None
    ) -> str:
        """
        使用AI分析文档格式并生成格式化指令
        
        :param query_db: 数据库会话
        :param document_content: 文档内容
        :param config_id: AI模型配置ID（可选）
        :return: 格式化指令（JSON字符串）
        """
        # 构建提示词
        prompt = cls._build_format_analysis_prompt(document_content)
        
        # 获取AI提供商（使用私有方法，需要直接调用）
        # 由于_get_ai_provider是类方法，可以直接调用
        llm_provider, _ = await AiGenerationService._get_ai_provider(query_db, config_id)
        
        # 调用AI分析
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的文档格式分析专家，擅长分析Word文档的格式要求并生成详细的格式化指令。"
            },
            {"role": "user", "content": prompt}
        ]
        
        logger.info("开始使用AI分析Word文档格式...")
        response = await llm_provider.chat(messages, temperature=0.3, max_tokens=2000)
        logger.info(f"AI格式分析完成，响应长度: {len(response) if response else 0}")
        
        # 打印AI生成的格式化内容（按用户要求）
        print("=" * 80)
        print("AI读取Word文档，生成的格式化内容：")
        print("=" * 80)
        print(response)
        print("=" * 80)
        
        return response
    
    @classmethod
    def _build_format_analysis_prompt(cls, document_content: Dict[str, Any]) -> str:
        """构建格式分析提示词"""
        # 将文档内容转换为JSON字符串（用于AI分析）
        # 限制长度，避免超出token限制，但保留关键格式信息
        content_json = json.dumps(document_content, ensure_ascii=False, indent=2)
        if len(content_json) > 3000:
            # 如果内容太长，只保留格式信息部分
            content_dict = document_content.copy()
            # 保留段落格式信息，但截断文本内容
            if 'paragraphs' in content_dict:
                for para in content_dict['paragraphs']:
                    if 'text' in para and len(para['text']) > 100:
                        para['text'] = para['text'][:100] + '...'
            content_json = json.dumps(content_dict, ensure_ascii=False, indent=2)[:3000]
        
        prompt = f"""你是一位专业的文档格式分析专家。请分析以下Word文档的格式要求，并生成标准化的JSON格式指令。

## 文档格式信息：
{content_json}

## 分析要求：

### 1. 字体格式识别
- 从文档的正文段落中识别默认字体名称（如：宋体、Times New Roman、Arial）
- 识别默认字体大小（通常为12磅）
- 识别字体颜色（如果有特殊颜色，否则使用默认黑色）

### 2. 段落格式识别
- **对齐方式**：识别正文段落的对齐方式（left=左对齐，center=居中，right=右对齐，justify=两端对齐）
- **行距**：识别行距倍数（如：1.5表示1.5倍行距，2.0表示2倍行距）
- **段间距**：识别段前距（spacing_before）和段后距（spacing_after），单位为磅
- **首行缩进**：识别首行缩进值（通常为24磅，表示2字符缩进）

### 3. 标题格式识别
- 识别各级标题（h1, h2, h3等）的格式
- 包括：字体大小、是否加粗、对齐方式、段前距、段后距
- 如果文档中有多个级别的标题，都要识别

### 4. 页面设置识别
- **页边距**：识别上下左右页边距（单位为磅，1英寸=72磅）
  - 常见值：上下72磅（1英寸），左右90磅（1.25英寸）
- **纸张大小**：识别纸张大小（A4、Letter等）

## 输出要求：

请严格按照以下JSON格式返回，**只返回JSON，不要包含任何其他文字说明**：

{{
  "font": {{
    "name": "字体名称（如：宋体、Times New Roman）",
    "size": 字体大小（数字，单位：磅，如：12）,
    "color": "颜色（可选，如：000000表示黑色）"
  }},
  "paragraph": {{
    "alignment": "对齐方式（left/center/right/justify）",
    "line_spacing": 行距倍数（数字，如：1.5）,
    "spacing_before": 段前间距（数字，单位：磅，如：0）,
    "spacing_after": 段后间距（数字，单位：磅，如：0）,
    "first_line_indent": 首行缩进（数字，单位：磅，如：24表示2字符）,
    "left_indent": 左缩进（数字，单位：磅，如：0）,
    "right_indent": 右缩进（数字，单位：磅，如：0）
  }},
  "headings": {{
    "h1": {{
      "font_name": "字体名称",
      "font_size": 字体大小（数字，单位：磅）,
      "bold": true/false,
      "alignment": "对齐方式（通常为center）",
      "spacing_before": 段前距（数字，单位：磅）,
      "spacing_after": 段后距（数字，单位：磅）
    }},
    "h2": {{
      "font_name": "字体名称",
      "font_size": 字体大小（数字，单位：磅）,
      "bold": true/false,
      "alignment": "对齐方式",
      "spacing_before": 段前距（数字，单位：磅）,
      "spacing_after": 段后距（数字，单位：磅）
    }},
    "h3": {{
      "font_name": "字体名称",
      "font_size": 字体大小（数字，单位：磅）,
      "bold": true/false,
      "alignment": "对齐方式",
      "spacing_before": 段前距（数字，单位：磅）,
      "spacing_after": 段后距（数字，单位：磅）
    }}
  }},
  "page": {{
    "margins": {{
      "top": 上边距（数字，单位：磅，如：72）,
      "bottom": 下边距（数字，单位：磅，如：72）,
      "left": 左边距（数字，单位：磅，如：90）,
      "right": 右边距（数字，单位：磅，如：90）
    }},
    "size": "纸张大小（如：A4、Letter）"
  }}
}}

## 重要提示：
1. **必须返回有效的JSON格式**，可以直接被json.loads()解析
2. 如果某个格式信息无法确定，使用合理的默认值：
   - 字体：宋体（中文）或Times New Roman（英文）
   - 字体大小：12磅
   - 行距：1.5倍
   - 首行缩进：24磅（2字符）
   - 页边距：上下72磅，左右90磅
3. **只返回JSON对象，不要包含markdown代码块标记（```json）**
4. 确保所有数字都是数字类型，不是字符串

现在请分析文档格式并返回JSON格式指令："""
        
        return prompt
    
    @classmethod
    async def format_thesis(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        word_file_path: Optional[str] = None,
        format_instructions: Optional[str] = None,
        config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        格式化论文（根据AI提取的格式指令）
        
        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param word_file_path: Word文档路径（如果提供，会先读取并提取格式指令）
        :param format_instructions: 格式化指令（JSON字符串，如果提供则直接使用）
        :param config_id: AI模型配置ID（可选）
        :return: 格式化结果
        """
        if not DOCX_AVAILABLE:
            raise ServiceException(message='python-docx 未安装，无法格式化Word文档。请运行: pip install python-docx')
        
        try:
            # 如果没有提供格式指令，需要先读取Word文档并提取
            if not format_instructions and word_file_path:
                logger.info(f"开始读取Word文档并提取格式指令 - 文件: {word_file_path}")
                read_result = await cls.read_word_document_with_ai(query_db, word_file_path, config_id)
                format_instructions = read_result['format_instructions']
            
            if not format_instructions:
                raise ServiceException(message='未提供格式化指令，无法进行格式化')
            
            # 解析格式指令
            try:
                format_config = json.loads(format_instructions) if isinstance(format_instructions, str) else format_instructions
            except json.JSONDecodeError:
                # 如果AI返回的不是纯JSON，尝试提取JSON部分
                format_config = cls._extract_json_from_text(format_instructions)
            
            # 获取论文的所有章节（只包含已完成的章节）
            from module_thesis.dao.thesis_dao import ThesisChapterDao
            all_chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
            
            # 只格式化已完成的章节
            chapters = [c for c in all_chapters if c.status == 'completed']
            
            if not chapters:
                raise ServiceException(message='论文没有已完成的章节内容，无法格式化')
            
            # 获取论文基本信息（用于文档头部）
            from module_thesis.dao.thesis_dao import ThesisDao
            thesis = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
            
            # 创建格式化的Word文档
            output_path = cls._create_formatted_document(chapters, format_config, thesis_id, thesis)
            
            logger.info(f"论文格式化完成 - 论文ID: {thesis_id}, 输出文件: {output_path}")
            
            return {
                'formatted_file_path': output_path,
                'format_instructions': format_instructions,
                'format_config': format_config
            }
            
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f"格式化论文失败: {str(e)}", exc_info=True)
            raise ServiceException(message=f'格式化论文失败: {str(e)}')
    
    @classmethod
    def _extract_json_from_text(cls, text: str) -> Dict[str, Any]:
        """从文本中提取JSON内容"""
        import re
        
        # 尝试提取JSON代码块
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 尝试提取大括号内容
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 如果都失败，返回默认配置
        logger.warning("无法从AI响应中提取JSON，使用默认格式配置")
        return {
            'font': {'name': '宋体', 'size': 12},
            'paragraph': {'alignment': 'left', 'line_spacing': 1.5},
            'page': {'margins': {'top': 72, 'bottom': 72, 'left': 90, 'right': 90}}
        }
    
    @classmethod
    def _create_formatted_document(
        cls,
        chapters: list,
        format_config: Dict[str, Any],
        thesis_id: int,
        thesis = None
    ) -> str:
        """
        创建格式化的Word文档
        
        :param chapters: 章节列表（已完成状态）
        :param format_config: 格式配置
        :param thesis_id: 论文ID
        :param thesis: 论文对象（可选，用于添加标题等信息）
        :return: 输出文件路径
        """
        if not DOCX_AVAILABLE:
            raise ServiceException(message='python-docx 未安装，无法创建Word文档。请运行: pip install python-docx')
        
        # 创建新文档
        doc = Document()
        
        # 应用页面设置
        if 'page' in format_config:
            page_config = format_config['page']
            if 'margins' in page_config:
                margins = page_config['margins']
                section = doc.sections[0]
                section.top_margin = Inches(float(margins.get('top', 72)) / 72)
                section.bottom_margin = Inches(float(margins.get('bottom', 72)) / 72)
                section.left_margin = Inches(float(margins.get('left', 90)) / 72)
                section.right_margin = Inches(float(margins.get('right', 90)) / 72)
        
        # 获取格式配置
        font_config = format_config.get('font', {})
        para_config = format_config.get('paragraph', {})
        headings_config = format_config.get('headings', {})
        
        # 设置默认字体
        default_font_name = font_config.get('name', '宋体')
        default_font_size = Pt(font_config.get('size', 12))
        
        # 添加论文标题（如果有）
        if thesis and thesis.title:
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(thesis.title)
            title_run.font.name = default_font_name
            title_run.font.size = Pt(18)  # 标题字体稍大
            title_run.font.bold = True
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()  # 空行
        
        # 按章节顺序排序（确保与大纲顺序一致）
        chapters = sorted(chapters, key=lambda x: getattr(x, 'order_num', 0) if hasattr(x, 'order_num') else 0)
        
        # 遍历章节，添加内容
        for idx, chapter in enumerate(chapters):
            if not chapter.content:
                continue
            
            # 添加章节标题
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(chapter.title)
            title_run.bold = True
            
            # 应用标题格式
            if headings_config:
                level_key = f'h{chapter.level}' if hasattr(chapter, 'level') else 'h1'
                if level_key in headings_config:
                    heading_style = headings_config[level_key]
                    title_run.font.size = Pt(heading_style.get('font_size', 16))
                    title_run.font.name = heading_style.get('font_name', default_font_name)
                    title_run.font.bold = heading_style.get('bold', True)
                else:
                    # 如果没有对应级别的标题格式，使用默认值
                    title_run.font.size = Pt(16)
                    title_run.font.name = default_font_name
                    title_run.font.bold = True
            else:
                # 如果没有标题配置，使用默认格式
                title_run.font.size = Pt(16)
                title_run.font.name = default_font_name
                title_run.font.bold = True
            
            # 设置标题对齐（通常标题居中）
            title_alignment = headings_config.get(f'h{chapter.level if hasattr(chapter, "level") else 1}', {}).get('alignment', 'center')
            if title_alignment == 'center':
                title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif title_alignment == 'right':
                title_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER  # 默认居中
            
            # 设置标题段间距
            if headings_config:
                level_key = f'h{chapter.level}' if hasattr(chapter, 'level') else 'h1'
                if level_key in headings_config:
                    heading_style = headings_config[level_key]
                    if 'spacing_before' in heading_style:
                        title_para.paragraph_format.space_before = Pt(heading_style['spacing_before'])
                    if 'spacing_after' in heading_style:
                        title_para.paragraph_format.space_after = Pt(heading_style['spacing_after'])
            
            # 添加空行（标题后）
            doc.add_paragraph()
            
            # 处理章节内容（支持Markdown格式）
            content_lines = chapter.content.split('\n')
            current_heading_level = None
            
            for line in content_lines:
                line = line.strip()
                if not line:
                    # 空行
                    doc.add_paragraph()
                    continue
                
                # 检测Markdown标题（## 或 ###）
                if line.startswith('##'):
                    # 二级标题
                    heading_text = line.lstrip('#').strip()
                    heading_para = doc.add_paragraph()
                    heading_run = heading_para.add_run(heading_text)
                    heading_run.font.size = Pt(14)  # 比一级标题小
                    heading_run.font.name = default_font_name
                    heading_run.font.bold = True
                    heading_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    heading_para.paragraph_format.space_before = Pt(12)
                    heading_para.paragraph_format.space_after = Pt(6)
                    continue
                elif line.startswith('###'):
                    # 三级标题
                    heading_text = line.lstrip('#').strip()
                    heading_para = doc.add_paragraph()
                    heading_run = heading_para.add_run(heading_text)
                    heading_run.font.size = Pt(13)
                    heading_run.font.name = default_font_name
                    heading_run.font.bold = True
                    heading_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    heading_para.paragraph_format.space_before = Pt(10)
                    heading_para.paragraph_format.space_after = Pt(4)
                    continue
                
                # 处理普通段落（支持Markdown加粗）
                para = doc.add_paragraph()
                
                # 处理Markdown加粗（**文本**）
                import re
                parts = re.split(r'(\*\*.*?\*\*)', line)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        # 加粗文本
                        bold_text = part.strip('*')
                        run = para.add_run(bold_text)
                        run.font.name = default_font_name
                        run.font.size = default_font_size
                        run.font.bold = True
                    elif part.strip():
                        # 普通文本
                        run = para.add_run(part)
                        run.font.name = default_font_name
                        run.font.size = default_font_size
                
                # 应用段落格式
                alignment = para_config.get('alignment', 'left')
                if alignment == 'center':
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif alignment == 'right':
                    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                elif alignment == 'justify':
                    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                else:
                    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # 设置行距
                if 'line_spacing' in para_config:
                    line_spacing_value = para_config['line_spacing']
                    if isinstance(line_spacing_value, (int, float)):
                        para.paragraph_format.line_spacing = line_spacing_value
                    elif isinstance(line_spacing_value, str):
                        try:
                            para.paragraph_format.line_spacing = float(line_spacing_value)
                        except ValueError:
                            para.paragraph_format.line_spacing = 1.5
                
                # 设置段间距
                if 'spacing_before' in para_config:
                    para.paragraph_format.space_before = Pt(para_config['spacing_before'])
                if 'spacing_after' in para_config:
                    para.paragraph_format.space_after = Pt(para_config['spacing_after'])
                
                # 设置首行缩进（只有段落的第一行需要缩进）
                if 'first_line_indent' in para_config:
                    para.paragraph_format.first_line_indent = Pt(para_config['first_line_indent'])
            
            # 章节之间添加分页符（最后一章不添加）
            if idx < len(chapters) - 1:
                doc.add_page_break()
        
        # 保存文档
        output_dir = Path('uploads/thesis/formatted')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'thesis_{thesis_id}_formatted.docx'
        
        # 确保路径是绝对路径
        output_path = output_path.resolve()
        
        doc.save(str(output_path))
        
        logger.info(f"格式化文档已保存: {output_path}")
        
        return str(output_path)
