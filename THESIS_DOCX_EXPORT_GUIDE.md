# 论文Word文档导出功能实现指南

## 概述

本指南说明如何使用 `docx` skill 实现论文按格式导出为 Word 文档的功能。

## 方案架构

```
论文数据（数据库）
    ↓
后端服务（Python/FastAPI）
    ↓
Node.js 导出服务（使用 docx-js）
    ↓
格式化的 Word 文档（.docx）
```

## 实现步骤

### 步骤1：安装依赖

```bash
# 安装 docx 库（全局安装）
npm install -g docx

# 或在项目中安装
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
npm install docx
```

### 步骤2：创建 Word 导出服务

创建 `module_thesis/service/docx_export_service.py`:

```python
"""
Word文档导出服务
"""
import json
import subprocess
import tempfile
import os
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_thesis.dao.thesis_dao import ThesisDao, ThesisChapterDao, ThesisOutlineDao
from utils.log_util import logger


class DocxExportService:
    """Word文档导出服务"""
    
    @classmethod
    async def export_thesis_to_docx(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        template_config: Dict[str, Any] = None
    ) -> bytes:
        """
        导出论文为Word文档
        
        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param template_config: 模板配置（字体、间距、页边距等）
        :return: Word文档二进制数据
        """
        try:
            # 1. 获取论文数据
            thesis_data = await cls._get_thesis_data(query_db, thesis_id)
            
            # 2. 准备导出配置
            export_config = cls._prepare_export_config(thesis_data, template_config)
            
            # 3. 调用 Node.js 脚本生成 Word 文档
            docx_buffer = await cls._generate_docx(export_config)
            
            return docx_buffer
            
        except Exception as e:
            logger.error(f"导出Word文档失败: {str(e)}")
            raise ServiceException(message=f'导出Word文档失败: {str(e)}')
    
    @classmethod
    async def _get_thesis_data(cls, query_db: AsyncSession, thesis_id: int) -> Dict[str, Any]:
        """获取论文完整数据"""
        # 获取论文基本信息
        thesis = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
        if not thesis:
            raise ServiceException(message='论文不存在')
        
        # 获取大纲
        outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, thesis_id)
        
        # 获取所有章节
        chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
        
        return {
            'thesis': {
                'title': thesis.title,
                'major': getattr(thesis, 'major', ''),
                'degree_level': getattr(thesis, 'degree_level', ''),
                'research_direction': getattr(thesis, 'research_direction', ''),
                'keywords': getattr(thesis, 'keywords', ''),
            },
            'outline': json.loads(outline.outline_data) if outline and outline.outline_data else None,
            'chapters': [
                {
                    'title': chapter.title,
                    'level': chapter.level,
                    'order_num': chapter.order_num,
                    'content': chapter.content,
                    'word_count': chapter.word_count
                }
                for chapter in sorted(chapters, key=lambda x: x.order_num)
            ]
        }
    
    @classmethod
    def _prepare_export_config(
        cls,
        thesis_data: Dict[str, Any],
        template_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """准备导出配置"""
        # 默认模板配置
        default_config = {
            'font': {
                'title': 'SimHei',  # 黑体
                'heading': 'SimHei',  # 黑体
                'body': 'SimSun',  # 宋体
                'english': 'Times New Roman'
            },
            'fontSize': {
                'title': 36,  # 18pt
                'heading1': 32,  # 16pt
                'heading2': 28,  # 14pt
                'heading3': 26,  # 13pt
                'body': 24  # 12pt
            },
            'spacing': {
                'lineSpacing': 360,  # 1.5倍行距
                'beforeParagraph': 0,
                'afterParagraph': 0
            },
            'margin': {
                'top': 1440,  # 1英寸 = 1440 twips
                'right': 1440,
                'bottom': 1440,
                'left': 1440
            },
            'pageSize': {
                'width': 11906,  # A4宽度
                'height': 16838  # A4高度
            }
        }
        
        # 合并用户配置
        if template_config:
            default_config.update(template_config)
        
        return {
            'thesis': thesis_data,
            'template': default_config
        }
    
    @classmethod
    async def _generate_docx(cls, export_config: Dict[str, Any]) -> bytes:
        """调用 Node.js 脚本生成 Word 文档"""
        # 创建临时文件保存配置
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as config_file:
            json.dump(export_config, config_file, ensure_ascii=False, indent=2)
            config_path = config_file.name
        
        # 创建临时输出文件
        output_path = tempfile.mktemp(suffix='.docx')
        
        try:
            # 调用 Node.js 脚本
            script_path = os.path.join(
                os.path.dirname(__file__),
                '../scripts/generate_docx.js'
            )
            
            result = subprocess.run(
                ['node', script_path, config_path, output_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise Exception(f"Node.js脚本执行失败: {result.stderr}")
            
            # 读取生成的文档
            with open(output_path, 'rb') as f:
                docx_buffer = f.read()
            
            return docx_buffer
            
        finally:
            # 清理临时文件
            if os.path.exists(config_path):
                os.remove(config_path)
            if os.path.exists(output_path):
                os.remove(output_path)
```

### 步骤3：创建 Node.js 导出脚本

创建 `module_thesis/scripts/generate_docx.js`:

```javascript
#!/usr/bin/env node

const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak } = require('docx');

// 读取配置
const configPath = process.argv[2];
const outputPath = process.argv[3];

if (!configPath || !outputPath) {
    console.error('Usage: node generate_docx.js <config.json> <output.docx>');
    process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const { thesis, template } = config;

// 创建文档
const doc = new Document({
    styles: {
        default: {
            document: {
                run: { font: template.font.body, size: template.fontSize.body }
            }
        },
        paragraphStyles: [
            {
                id: "Title",
                name: "Title",
                basedOn: "Normal",
                run: { size: template.fontSize.title, bold: true, font: template.font.title },
                paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER }
            },
            {
                id: "Heading1",
                name: "Heading 1",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: template.fontSize.heading1, bold: true, font: template.font.heading },
                paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
            },
            {
                id: "Heading2",
                name: "Heading 2",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: template.fontSize.heading2, bold: true, font: template.font.heading },
                paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 }
            },
            {
                id: "Heading3",
                name: "Heading 3",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: template.fontSize.heading3, bold: true, font: template.font.heading },
                paragraph: { spacing: { before: 120, after: 120 }, outlineLevel: 2 }
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: template.margin,
                size: template.pageSize
            }
        },
        children: generateContent(thesis, template)
    }]
});

// 生成文档内容
function generateContent(thesis, template) {
    const content = [];
    
    // 标题页
    content.push(
        new Paragraph({
            heading: HeadingLevel.TITLE,
            children: [new TextRun(thesis.thesis.title)]
        }),
        new Paragraph({ text: "" }), // 空行
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: `专业：${thesis.thesis.major}`, size: 28 })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: `学位级别：${thesis.thesis.degree_level}`, size: 28 })]
        }),
        new Paragraph({ text: "" }),
        new PageBreak()
    );
    
    // 摘要（如果有）
    if (thesis.outline && thesis.outline.abstract) {
        content.push(
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("摘要")]
            }),
            new Paragraph({ text: thesis.outline.abstract }),
            new Paragraph({ text: "" }),
            new Paragraph({
                children: [
                    new TextRun({ text: "关键词：", bold: true }),
                    new TextRun(thesis.thesis.keywords || "")
                ]
            }),
            new PageBreak()
        );
    }
    
    // 章节内容
    if (thesis.chapters && thesis.chapters.length > 0) {
        thesis.chapters.forEach((chapter, index) => {
            // 章节标题
            const headingLevel = chapter.level === 1 ? HeadingLevel.HEADING_1 :
                                chapter.level === 2 ? HeadingLevel.HEADING_2 :
                                HeadingLevel.HEADING_3;
            
            content.push(
                new Paragraph({
                    heading: headingLevel,
                    children: [new TextRun(chapter.title)]
                })
            );
            
            // 章节内容（Markdown转换为段落）
            if (chapter.content) {
                const paragraphs = parseMarkdownContent(chapter.content, template);
                content.push(...paragraphs);
            }
            
            // 章节之间添加分页（除了最后一章）
            if (index < thesis.chapters.length - 1) {
                content.push(new PageBreak());
            }
        });
    }
    
    return content;
}

// 解析Markdown内容为段落
function parseMarkdownContent(markdown, template) {
    const paragraphs = [];
    const lines = markdown.split('\n');
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        if (!trimmed) {
            // 空行
            paragraphs.push(new Paragraph({ text: "" }));
            continue;
        }
        
        // 标题
        if (trimmed.startsWith('###')) {
            paragraphs.push(
                new Paragraph({
                    heading: HeadingLevel.HEADING_3,
                    children: [new TextRun(trimmed.replace(/^###\s*/, ''))]
                })
            );
        } else if (trimmed.startsWith('##')) {
            paragraphs.push(
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun(trimmed.replace(/^##\s*/, ''))]
                })
            );
        } else if (trimmed.startsWith('#')) {
            paragraphs.push(
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [new TextRun(trimmed.replace(/^#\s*/, ''))]
                })
            );
        } else {
            // 普通段落
            paragraphs.push(
                new Paragraph({
                    spacing: {
                        line: template.spacing.lineSpacing,
                        before: template.spacing.beforeParagraph,
                        after: template.spacing.afterParagraph
                    },
                    children: [new TextRun(trimmed)]
                })
            );
        }
    }
    
    return paragraphs;
}

// 生成并保存文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`Document generated successfully: ${outputPath}`);
    process.exit(0);
}).catch(error => {
    console.error('Error generating document:', error);
    process.exit(1);
});
```

### 步骤4：添加导出控制器

在 `module_thesis/controller/thesis_controller.py` 中添加导出接口：

```python
@router.get('/paper/{thesis_id}/export', summary='导出论文为Word文档')
async def export_thesis(
    thesis_id: int,
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(get_current_user)
):
    """导出论文为Word文档"""
    try:
        from module_thesis.service.docx_export_service import DocxExportService
        
        # 生成Word文档
        docx_buffer = await DocxExportService.export_thesis_to_docx(
            query_db,
            thesis_id
        )
        
        # 获取论文标题作为文件名
        from module_thesis.service.thesis_service import ThesisService
        thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
        filename = f"{thesis.title}.docx"
        
        # 返回文件
        from fastapi.responses import Response
        return Response(
            content=docx_buffer,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except ServiceException as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"导出论文失败: {str(e)}")
        return ResponseUtil.failure(msg=f'导出论文失败: {str(e)}')
```

### 步骤5：前端调用

在前端添加导出按钮：

```javascript
// src/api/thesis/paper.js
export function exportThesis(paperId) {
  return request({
    url: `/thesis/paper/${paperId}/export`,
    method: 'get',
    responseType: 'blob'
  })
}

// 在论文列表页面
const handleExport = (row) => {
  exportThesis(row.thesisId).then(response => {
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${row.title}.docx`;
    link.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success('导出成功');
  }).catch(() => {
    ElMessage.error('导出失败');
  });
};
```

## 高级功能

### 1. 自定义模板

支持用户上传自定义Word模板，提取样式并应用：

```python
@classmethod
async def export_with_template(
    cls,
    query_db: AsyncSession,
    thesis_id: int,
    template_id: int
) -> bytes:
    """使用自定义模板导出"""
    # 1. 获取模板配置
    template = await TemplateDao.get_template_by_id(query_db, template_id)
    template_config = json.loads(template.format_config)
    
    # 2. 导出
    return await cls.export_thesis_to_docx(query_db, thesis_id, template_config)
```

### 2. 支持更多格式元素

在 `generate_docx.js` 中添加：
- 表格支持
- 图片支持
- 公式支持
- 参考文献格式化
- 页眉页脚
- 页码
- 目录

### 3. 批量导出

```python
@classmethod
async def batch_export(
    cls,
    query_db: AsyncSession,
    thesis_ids: List[int]
) -> bytes:
    """批量导出为ZIP"""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for thesis_id in thesis_ids:
            docx_buffer = await cls.export_thesis_to_docx(query_db, thesis_id)
            thesis = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
            zip_file.writestr(f"{thesis.title}.docx", docx_buffer)
    
    return zip_buffer.getvalue()
```

## 测试清单

- [ ] 安装 docx 依赖
- [ ] 创建导出服务
- [ ] 创建 Node.js 脚本
- [ ] 添加导出接口
- [ ] 前端集成
- [ ] 测试基本导出
- [ ] 测试中文字体
- [ ] 测试格式保留
- [ ] 测试大文档性能
- [ ] 测试模板功能

## 注意事项

1. **中文字体**：确保使用支持中文的字体（SimSun, SimHei等）
2. **性能**：大文档可能需要较长时间，考虑异步处理
3. **内存**：Node.js 进程可能需要较大内存，注意配置
4. **错误处理**：完善的错误处理和日志记录
5. **安全性**：验证用户权限，防止未授权导出

## 完成状态

✅ 方案设计完成
✅ 代码示例提供
⏳ 等待实现和测试
