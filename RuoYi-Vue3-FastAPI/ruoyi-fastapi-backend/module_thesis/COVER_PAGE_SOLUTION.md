# 封面和原创性声明页面处理方案

## 一、需求分析

**问题**：封面和原创性声明页面是固定模板，不需要格式指令处理，只需要原样输出。

**解决方案**：在上传格式文件时，将封面和原创性声明页面单独提取并保存，格式化时原样插入到文档开头。

## 二、方案对比

### 方案A：新增数据库字段（推荐用于需要独立管理的场景）

**优点**：
- 字段明确，易于查询和管理
- 可以单独更新封面或声明页面
- 数据库结构清晰

**缺点**：
- 需要修改数据库表结构
- 需要数据库迁移
- 字段可能为空（不是所有学校都有封面/声明）

**实现**：
```python
# 在 AiWriteFormatTemplate 表中新增字段
cover_page_path = Column(String(500), nullable=True, comment='封面页面文件路径')
declaration_page_path = Column(String(500), nullable=True, comment='原创性声明页面文件路径')
review_table_path = Column(String(500), nullable=True, comment='评审表文件路径')
defense_record_path = Column(String(500), nullable=True, comment='答辩记录表文件路径')
```

### 方案B：在 format_data JSON 中存储（推荐，更灵活）

**优点**：
- ✅ **不需要修改数据库表结构**
- ✅ **灵活扩展**：可以存储任意数量的特殊页面
- ✅ **向后兼容**：不影响现有数据
- ✅ **逻辑清晰**：这些页面路径属于格式配置的一部分

**缺点**：
- 需要从JSON中解析路径
- 查询时需要解析JSON

**实现**：
```json
{
  "version": "1.0",
  "description": "学校名称+学位级别+专业格式化指令",
  "instruction_type": "format_application",
  "format_rules": {
    // ... 格式规则
  },
  "special_pages": {
    "cover_page": {
      "file_path": "uploads/templates/cover_page_template_id.docx",
      "description": "封面页面"
    },
    "declaration_page": {
      "file_path": "uploads/templates/declaration_template_id.docx",
      "description": "原创性声明页面"
    },
    "review_table": {
      "file_path": "uploads/templates/review_table_template_id.docx",
      "description": "评审表（可选）"
    },
    "defense_record": {
      "file_path": "uploads/templates/defense_record_template_id.docx",
      "description": "答辩记录表（可选）"
    }
  }
}
```

## 三、推荐方案：方案B（format_data JSON存储）

### 3.1 理由

1. **不需要数据库迁移**：直接使用现有的 `format_data` 字段
2. **灵活扩展**：可以轻松添加新的特殊页面类型
3. **逻辑合理**：特殊页面路径是格式配置的一部分
4. **向后兼容**：不影响现有模板数据

### 3.2 实现步骤

#### 步骤1：上传格式文件时提取特殊页面

在 `template_service.py` 的 `create_template` 方法中：

```python
# 1. 上传格式文件
# 2. 解析格式文件，提取封面和声明页面
from module_thesis.service.format_service import FormatService

# 提取特殊页面
special_pages = await FormatService.extract_special_pages(file_path)

# special_pages 结构：
# {
#   "cover_page": "uploads/templates/cover_template_123.docx",
#   "declaration_page": "uploads/templates/declaration_template_123.docx",
#   "review_table": "uploads/templates/review_template_123.docx",  # 可选
#   "defense_record": "uploads/templates/defense_template_123.docx"  # 可选
# }
```

#### 步骤2：保存到 format_data

```python
# 在生成 format_data 时，添加 special_pages
format_data = {
    "version": "1.0",
    "format_rules": {...},
    "special_pages": special_pages  # 添加特殊页面路径
}
```

#### 步骤3：格式化时使用特殊页面

在 `format_service.py` 的 `_create_formatted_document` 方法中：

```python
# 1. 读取 format_data 中的 special_pages
special_pages = format_config.get('special_pages', {})

# 2. 如果有封面页面，插入到文档开头
if 'cover_page' in special_pages:
    cover_path = special_pages['cover_page']['file_path']
    # 从封面文档中复制页面到新文档
    cls._insert_page_from_template(doc, cover_path)

# 3. 如果有声明页面，插入到封面之后
if 'declaration_page' in special_pages:
    declaration_path = special_pages['declaration_page']['file_path']
    cls._insert_page_from_template(doc, declaration_path)

# 4. 继续处理其他内容（目录、摘要等）
```

## 四、实现代码

### 4.1 提取特殊页面的方法

在 `format_service.py` 中添加：

```python
@classmethod
async def extract_special_pages(
    cls,
    template_file_path: str,
    template_id: int
) -> Dict[str, Any]:
    """
    从格式模板文件中提取特殊页面（封面、声明等）
    
    :param template_file_path: 模板文件路径
    :param template_id: 模板ID
    :return: 特殊页面路径字典
    """
    from docx import Document
    from pathlib import Path
    import os
    
    if not DOCX_AVAILABLE:
        return {}
    
    try:
        # 打开模板文档
        template_doc = Document(template_file_path)
        
        special_pages = {}
        output_dir = Path('uploads/templates/special_pages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 提取封面页面（通常是第一页）
        if len(template_doc.paragraphs) > 0:
            # 检查第一页是否包含封面信息
            first_page_text = ' '.join([p.text for p in template_doc.paragraphs[:10]])
            if any(keyword in first_page_text for keyword in ['封面', '题目', '姓名', '学号', '专业']):
                cover_doc = Document()
                # 复制第一页内容到新文档
                cls._copy_page_content(template_doc, cover_doc, start_para=0, end_para=10)
                cover_path = output_dir / f'cover_template_{template_id}.docx'
                cover_doc.save(str(cover_path))
                special_pages['cover_page'] = {
                    'file_path': str(cover_path),
                    'description': '封面页面'
                }
        
        # 提取原创性声明页面
        # 查找包含"原创性声明"或"使用授权"的页面
        for i, para in enumerate(template_doc.paragraphs):
            if '原创性声明' in para.text or '使用授权' in para.text:
                declaration_doc = Document()
                # 复制声明页面内容
                cls._copy_page_content(template_doc, declaration_doc, start_para=i, end_para=i+20)
                declaration_path = output_dir / f'declaration_template_{template_id}.docx'
                declaration_doc.save(str(declaration_path))
                special_pages['declaration_page'] = {
                    'file_path': str(declaration_path),
                    'description': '原创性声明页面'
                }
                break
        
        return special_pages
        
    except Exception as e:
        logger.error(f"提取特殊页面失败: {str(e)}")
        return {}
```

### 4.2 插入页面的方法

```python
@classmethod
def _insert_page_from_template(
    cls,
    target_doc: Document,
    source_file_path: str
) -> None:
    """
    从模板文件中复制页面内容到目标文档
    
    :param target_doc: 目标文档
    :param source_file_path: 源文件路径
    """
    from docx import Document
    
    try:
        source_doc = Document(source_file_path)
        
        # 复制所有段落
        for para in source_doc.paragraphs:
            new_para = target_doc.add_paragraph()
            for run in para.runs:
                new_run = new_para.add_run(run.text)
                new_run.font.name = run.font.name
                new_run.font.size = run.font.size
                new_run.font.bold = run.font.bold
                # 复制其他格式属性...
            
            # 复制段落格式
            new_para.alignment = para.alignment
            new_para.paragraph_format.line_spacing = para.paragraph_format.line_spacing
            # 复制其他段落格式...
        
        # 添加分页符（如果需要）
        target_doc.add_page_break()
        
    except Exception as e:
        logger.error(f"插入页面失败: {str(e)}")
```

## 五、数据库字段方案（如果选择方案A）

如果需要独立管理，可以在 `template_do.py` 中添加：

```python
class AiWriteFormatTemplate(Base):
    # ... 现有字段 ...
    
    # 特殊页面路径（可选）
    cover_page_path = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='封面页面文件路径'
    )
    declaration_page_path = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='原创性声明页面文件路径'
    )
    review_table_path = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='评审表文件路径（可选）'
    )
    defense_record_path = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='答辩记录表文件路径（可选）'
    )
```

## 六、建议

**推荐使用方案B（format_data JSON存储）**，原因：

1. ✅ **不需要数据库迁移**：直接使用现有字段
2. ✅ **灵活扩展**：可以轻松添加新的特殊页面类型
3. ✅ **向后兼容**：不影响现有数据
4. ✅ **逻辑清晰**：特殊页面是格式配置的一部分

如果未来需要独立查询或管理这些页面，再考虑迁移到方案A。

## 七、使用示例

### 上传格式文件时

```python
# 1. 上传格式文件
# 2. 提取格式指令
format_instructions = await FormatService.read_word_document_with_ai(file_path)

# 3. 提取特殊页面
special_pages = await FormatService.extract_special_pages(file_path, template_id)

# 4. 合并到 format_data
format_data = {
    **format_instructions,
    "special_pages": special_pages
}

# 5. 保存到数据库
template.format_data = format_data
```

### 格式化论文时

```python
# 1. 读取 format_data
format_data = json.loads(template.format_data)

# 2. 获取特殊页面
special_pages = format_data.get('special_pages', {})

# 3. 创建文档时插入特殊页面
doc = Document()

# 插入封面
if 'cover_page' in special_pages:
    cls._insert_page_from_template(doc, special_pages['cover_page']['file_path'])

# 插入声明
if 'declaration_page' in special_pages:
    cls._insert_page_from_template(doc, special_pages['declaration_page']['file_path'])

# 继续处理其他内容...
```
