# 表结构分析

## 1. ai_write_thesis（论文表）

### 主要字段：
- `thesis_id`: 论文ID（主键）
- `user_id`: 用户ID
- `template_id`: **模板ID（外键，关联到 ai_write_format_template）**
- `title`: 论文标题
- `attachment_path`: 附件路径（Word文档路径）- **注意：实际使用中，附件通过 template_id 关联到模板表的 file_path**
- `format_progress`: 格式化进度（0-100）
- `format_instructions`: 格式化指令（AI提取的格式要求）
- `status`: 状态（draft/generating/completed/exported/formatted）

### 关键关系：
- **论文 → 模板**：通过 `template_id` 关联到 `ai_write_format_template.template_id`
- **论文的附件**：实际上是通过 `template_id` 获取模板的 `file_path`，而不是直接使用 `attachment_path`

## 2. ai_write_format_template（格式模板表）

### 主要字段：
- `template_id`: 模板ID（主键）
- `template_name`: 模板名称
- `school_name`: 学校名称
- `major`: 专业
- `degree_level`: 学位级别（本科/硕士/博士）
- **`file_path`: 模板文件路径（Word文档路径）** - **这是实际存储模板Word文档的地方**
- `file_name`: 原始文件名
- `file_size`: 文件大小（字节）
- `format_data`: 格式数据（JSON格式，解析后的格式规则）
- `is_official`: 是否官方模板（0否 1是）
- `usage_count`: 使用次数

### 关键信息：
- **模板文件存储**：`file_path` 字段存储实际的Word文档路径
- **格式规则**：可以通过 `format_data` 字段获取已解析的格式规则（JSON格式）

## 3. 表关系图

```
ai_write_thesis (论文表)
    │
    │ template_id (外键)
    ↓
ai_write_format_template (格式模板表)
    │
    │ file_path (Word文档路径)
    ↓
实际的Word文档文件
```

## 4. 数据流程

### 格式化流程：
1. 用户创建论文时选择格式模板（设置 `thesis.template_id`）
2. 格式化时：
   - 从论文的 `template_id` 获取模板记录
   - 从模板的 `file_path` 获取Word文档路径
   - 读取Word文档并提取格式指令
   - 应用格式到论文内容

### 关键代码逻辑：
```python
# 1. 获取论文
thesis = await ThesisDao.get_thesis_by_id(query_db, thesis_id)

# 2. 通过 template_id 获取模板
template = await FormatTemplateDao.get_template_by_id(query_db, thesis.template_id)

# 3. 从模板获取Word文档路径
word_file_path = template.file_path

# 4. 使用该路径进行格式化
format_result = await FormatService.read_word_document_with_ai(query_db, word_file_path)
```

## 5. 注意事项

1. **attachment_path vs file_path**：
   - `thesis.attachment_path`：论文表的附件路径字段（存在但可能未使用）
   - `template.file_path`：模板表的文件路径字段（实际使用的路径）

2. **模板选择**：
   - 论文必须关联模板（`template_id` 不能为空）
   - 模板必须存在且 `file_path` 不能为空

3. **文件路径**：
   - 模板的 `file_path` 是相对路径或绝对路径
   - 需要确保路径指向有效的Word文档

## 6. 当前代码实现检查

### ✅ 正确的实现：
- `thesis_service.py` 中的 `format_thesis` 方法：
  - 从 `thesis.template_id` 获取模板 ✅
  - 从 `template.file_path` 获取Word文档路径 ✅
  - 使用该路径进行格式化 ✅

### ⚠️ 需要注意：
- 确保模板存在且 `file_path` 有效
- 处理文件路径不存在的情况
- 考虑使用 `format_data` 字段（如果已解析过格式规则，可以避免重复AI分析）
