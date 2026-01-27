# 特殊页面永久保存策略

## 一、保存策略

### 1.1 文件永久保存

**是的，特殊页面文件会永久保存**，直到模板被删除。

**保存位置**：
```
uploads/templates/special_pages/
├── cover_template_{template_id}.docx          # 封面页面
├── declaration_template_{template_id}.docx    # 原创性声明页面
├── review_table_template_{template_id}.docx  # 评审表（可选）
└── defense_record_template_{template_id}.docx # 答辩记录表（可选）
```

**文件命名规则**：
- 使用 `template_id` 作为文件名的一部分
- 确保每个模板的特殊页面文件唯一
- 文件名包含页面类型，便于识别

### 1.2 生命周期管理

**与模板绑定**：
- 特殊页面文件的生命周期与模板绑定
- 模板创建时：提取并保存特殊页面
- 模板更新时：重新提取并覆盖旧文件（可选）
- 模板删除时：同时删除对应的特殊页面文件

## 二、实现方案

### 2.1 文件保存路径

```python
# 文件保存路径结构
special_pages_dir = Path('uploads/templates/special_pages')
special_pages_dir.mkdir(parents=True, exist_ok=True)

# 文件路径
cover_path = special_pages_dir / f'cover_template_{template_id}.docx'
declaration_path = special_pages_dir / f'declaration_template_{template_id}.docx'
```

### 2.2 文件持久化

**保存时机**：
1. **模板创建时**：上传格式文件后，立即提取并保存特殊页面
2. **模板更新时**（可选）：如果重新上传格式文件，可以选择是否重新提取

**保存位置**：
- 服务器本地文件系统
- 路径存储在 `format_data.special_pages` 中
- 文件永久保存，直到模板删除

### 2.3 文件清理策略

**自动清理**：
- 当模板被删除时，自动删除对应的特殊页面文件
- 防止磁盘空间浪费

**实现代码**：
```python
@classmethod
async def delete_template(cls, query_db: AsyncSession, template_id: int) -> CrudResponseModel:
    """
    删除模板（同时删除特殊页面文件）
    """
    # 1. 获取模板信息
    template = await cls.get_template_detail(query_db, template_id)
    
    # 2. 删除特殊页面文件
    if template.format_data:
        format_data = json.loads(template.format_data) if isinstance(template.format_data, str) else template.format_data
        special_pages = format_data.get('special_pages', {})
        
        for page_type, page_info in special_pages.items():
            file_path = page_info.get('file_path')
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"已删除特殊页面文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除特殊页面文件失败: {file_path}, 错误: {str(e)}")
    
    # 3. 删除模板记录
    await FormatTemplateDao.delete_template(query_db, template_id)
    
    return CrudResponseModel(is_success=True, message='删除成功')
```

## 三、使用场景

### 3.1 模板创建（首次上传）

```python
# 1. 上传格式文件
file_path = "uploads/templates/template_123.docx"

# 2. 提取格式指令
format_result = await FormatService.read_word_document_with_ai(query_db, file_path)

# 3. 提取特殊页面（永久保存）
special_pages = await FormatService.extract_special_pages(file_path, template_id=123)

# 4. 合并到 format_data
format_data = {
    "version": "1.0",
    "format_rules": format_result['format_instructions'],
    "special_pages": special_pages  # 包含文件路径
}

# 5. 保存模板
template.format_data = format_data
# 此时 special_pages 中的文件已经永久保存在服务器上
```

### 3.2 格式化论文（使用已保存的特殊页面）

```python
# 1. 读取模板
template = await FormatTemplateDao.get_template_by_id(query_db, template_id)

# 2. 解析 format_data
format_data = json.loads(template.format_data)
special_pages = format_data.get('special_pages', {})

# 3. 使用已保存的特殊页面文件
if 'cover_page' in special_pages:
    cover_path = special_pages['cover_page']['file_path']
    # 文件已经永久保存，直接使用
    cls._insert_page_from_template(doc, cover_path)
```

### 3.3 模板更新（重新上传格式文件）

**选项1：保留旧的特殊页面**（推荐）
```python
# 如果新上传的格式文件中没有特殊页面，保留旧的
if not new_special_pages:
    # 保留 format_data 中已有的 special_pages
    format_data['special_pages'] = existing_format_data.get('special_pages', {})
```

**选项2：重新提取特殊页面**
```python
# 重新提取并覆盖旧文件
new_special_pages = await FormatService.extract_special_pages(new_file_path, template_id)
# 旧文件会被新文件覆盖（因为文件名相同）
format_data['special_pages'] = new_special_pages
```

## 四、文件管理建议

### 4.1 文件组织

```
uploads/templates/
├── template_1.docx                    # 原始模板文件
├── template_2.docx
└── special_pages/                     # 特殊页面目录
    ├── cover_template_1.docx         # 模板1的封面
    ├── declaration_template_1.docx   # 模板1的声明
    ├── cover_template_2.docx         # 模板2的封面
    └── declaration_template_2.docx   # 模板2的声明
```

### 4.2 文件备份

**建议**：
- 定期备份 `uploads/templates/special_pages/` 目录
- 与模板文件一起备份
- 确保数据安全

### 4.3 文件验证

**在格式化时验证文件存在**：
```python
def _insert_page_from_template(cls, target_doc: Document, source_file_path: str) -> None:
    """插入页面，验证文件存在"""
    if not os.path.exists(source_file_path):
        logger.error(f"特殊页面文件不存在: {source_file_path}")
        raise ServiceException(message=f'特殊页面文件不存在: {source_file_path}')
    
    # 继续插入页面...
```

## 五、优势总结

### ✅ 永久保存的优势

1. **一次提取，永久使用**：
   - 模板创建时提取一次
   - 后续格式化直接使用，无需重新提取

2. **性能优化**：
   - 避免每次格式化都重新提取
   - 减少文件I/O操作

3. **数据一致性**：
   - 确保每次格式化使用相同的封面和声明
   - 避免因格式文件变化导致的不一致

4. **存储效率**：
   - 特殊页面文件通常很小（几KB到几十KB）
   - 与模板文件一起管理，便于备份和恢复

## 六、注意事项

### 6.1 文件路径

- 使用**绝对路径**或**相对项目根目录的路径**
- 确保路径在不同环境下都能正确访问

### 6.2 文件权限

- 确保 `uploads/templates/special_pages/` 目录有写入权限
- 确保文件有读取权限

### 6.3 磁盘空间

- 定期检查磁盘空间
- 删除模板时及时清理对应的特殊页面文件

### 6.4 文件迁移

- 如果服务器迁移，需要同时迁移 `uploads/templates/special_pages/` 目录
- 确保路径在 `format_data` 中的正确性

## 七、总结

**✅ 特殊页面文件会永久保存**，直到模板被删除。

**工作流程**：
1. **模板创建时**：提取并永久保存特殊页面文件
2. **格式化时**：直接使用已保存的特殊页面文件
3. **模板删除时**：自动清理对应的特殊页面文件

**优势**：
- 一次提取，永久使用
- 性能优化
- 数据一致性
- 存储效率高

**建议**：使用方案B（format_data JSON存储），文件永久保存在服务器上，路径存储在 `format_data.special_pages` 中。
