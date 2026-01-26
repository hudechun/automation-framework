# 大纲格式支持说明

## 一、支持的大纲格式

系统现在支持多种大纲数据格式，通过统一的大纲解析工具 `outline_parser.py` 处理。

### 格式1：直接格式（推荐）
```json
{
  "title": "人工智能",
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_title": "摘要",
      "sections": [...]
    },
    ...
  ]
}
```

### 格式2：包装格式（兼容）
```json
{
  "title": "论文大纲",
  "content": "{\"title\": \"人工智能\", \"chapters\": [...]}",
  "chapters": []
}
```

**说明**：如果 `content` 字段是JSON字符串，系统会自动解析并使用 `content` 中的数据。

### 格式3：JSON字符串格式（旧数据兼容）
```json
"{\"title\": \"人工智能\", \"chapters\": [...]}"
```

## 二、解析逻辑

### 2.1 解析优先级

1. **优先使用 `content` 字段**：如果存在 `content` 字段且是JSON字符串，解析后检查是否有 `chapters`
2. **使用外层 `chapters`**：如果外层直接有 `chapters` 字段，直接使用
3. **合并数据**：如果 `content` 解析后有数据但外层没有 `chapters`，尝试合并

### 2.2 代码实现

**位置**：`module_thesis/utils/outline_parser.py`

**主要方法**：
- `parse_outline_data()`: 解析大纲数据，返回字典和上下文字符串
- `extract_chapters_from_outline()`: 从解析后的大纲中提取章节列表

## 三、使用位置

### 3.1 章节生成

**位置**：`thesis_service.py`

- `generate_chapter()`: 单个章节生成
- `batch_generate_chapters()`: 批量章节生成
- `continue_generate_chapters()`: 继续生成未完成的章节

**处理流程**：
1. 从数据库获取大纲数据
2. 使用 `parse_outline_data()` 解析
3. 使用 `extract_chapters_from_outline()` 提取章节列表
4. 匹配章节号或章节标题，提取对应的小节信息
5. 传递给AI生成章节内容

### 3.2 字数计算

**位置**：`ai_generation_service.py`

- `_calculate_chapter_word_count_requirement()`: 计算每章节字数要求

**处理流程**：
1. 从大纲上下文中解析章节数量
2. 使用统一解析工具处理不同格式
3. 计算平均字数

### 3.3 格式化

**位置**：`format_service.py`

格式化时直接从数据库读取已生成的章节内容，不依赖大纲格式。

## 四、测试场景

### 场景1：直接格式
```json
{
  "chapters": [
    {"chapter_number": 1, "chapter_title": "摘要", "sections": [...]}
  ]
}
```
✅ **支持**：直接解析 `chapters` 字段

### 场景2：包装格式（content字段）
```json
{
  "title": "论文大纲",
  "content": "{\"chapters\": [...]}",
  "chapters": []
}
```
✅ **支持**：自动解析 `content` 字段中的JSON字符串

### 场景3：混合格式
```json
{
  "title": "论文大纲",
  "content": "{\"title\": \"人工智能\", \"chapters\": [...]}",
  "chapters": []
}
```
✅ **支持**：优先使用 `content` 中解析的数据

## 五、注意事项

1. **数据完整性**：确保大纲数据中包含 `chapters` 字段
2. **章节匹配**：章节生成时通过 `chapter_number` 或 `chapter_title` 匹配
3. **小节信息**：如果章节有 `sections` 字段，会自动提取并传递给AI
4. **错误处理**：如果解析失败，会记录日志但不影响整体流程

## 六、格式化支持

格式化功能**不依赖大纲格式**，因为：
1. 格式化时直接读取已生成的章节内容（`ai_write_thesis_chapter.content`）
2. 章节内容已经包含完整的文本，无需从大纲解析
3. 格式化只负责应用样式和布局

**格式化流程**：
1. 获取所有已完成的章节（`status='completed'`）
2. 按 `order_num` 排序
3. 应用格式配置（字体、段落、标题样式等）
4. 生成Word文档
