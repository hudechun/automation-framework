# 格式化指令系统重新设计 - 实现总结

## 一、实现完成情况

### ✅ 1. 通用指令格式设计
- **状态**：已完成
- **说明**：设计了完整的通用指令格式，包含所有格式属性
- **位置**：`format_service.py` 中的 `_build_format_analysis_prompt()` 方法

### ✅ 2. 学校指令保存机制
- **状态**：已完成
- **说明**：每个学校上传格式文档时，AI生成指令并保存到模板表的`format_data`字段
- **位置**：`template_service.py` 中的 `create_template()` 方法

### ✅ 3. AI生成自然语言和指令
- **状态**：已完成（方案B）
- **说明**：上传格式文件时，AI同时生成自然语言描述和JSON格式指令
- **位置**：`format_service.py` 中的 `_analyze_format_with_ai()` 方法

### ✅ 4. 目录生成功能
- **状态**：已完成
- **说明**：实现了自动生成目录功能，支持自动生成和手动创建两种方式
- **位置**：`format_service.py` 中的 `_generate_table_of_contents()` 方法

## 二、目录生成功能详细说明

### 2.1 功能特点

1. **自动生成目录**
   - 当格式指令中 `application_rules.auto_generate_toc = true` 时自动触发
   - 自动扫描所有章节，提取标题和级别
   - 根据格式指令中的目录格式配置生成目录

2. **目录格式应用**
   - 从格式指令的 `special_sections.table_of_contents` 中读取格式
   - 支持目录标题格式（字体、字号、对齐、前后间距）
   - 支持多级目录条目格式（不同级别的缩进、字体、字号）

3. **目录生成规则**
   - 可配置包含的目录级别（`include_levels`）
   - 可配置排除的章节（`exclude_sections`）
   - 支持页码格式配置（`page_number_format`）

### 2.2 实现方法

#### 方法1：`_generate_table_of_contents()`
- **功能**：自动生成目录章节对象
- **参数**：
  - `chapters`: 章节列表
  - `format_config`: 格式配置
  - `layout_rules`: 布局规则
- **返回**：目录章节对象（包含标题和条目列表）

#### 方法2：在 `_create_formatted_document()` 中集成
- **位置**：在步骤5/6之前（第1602-1625行）
- **逻辑**：
  1. 检查是否需要生成目录
  2. 检查是否已有目录章节
  3. 如果需要且没有，则自动生成
  4. 将目录插入到第一个位置（摘要之前）

#### 方法3：目录内容生成
- **位置**：在章节内容处理逻辑中（第1719-1742行）
- **逻辑**：
  1. 识别为目录章节
  2. 如果是自动生成的目录，生成目录内容
  3. 根据级别添加缩进
  4. 生成格式化的目录行

### 2.3 使用方式

#### 方式1：自动生成目录（推荐）

在格式指令中设置：
```json
{
  "application_rules": {
    "auto_generate_toc": true,
    "toc_generation_rules": {
      "include_levels": [1, 2, 3],
      "exclude_sections": ["摘要", "关键词", "目录"],
      "page_number_format": "arabic"
    }
  }
}
```

格式化论文时，系统会自动：
1. 检测是否需要生成目录
2. 扫描所有章节
3. 生成目录章节
4. 插入到文档开头

#### 方式2：手动创建目录章节

1. 用户在论文大纲中手动创建"目录"章节
2. 系统识别该章节为目录章节
3. 应用目录格式（从格式指令中读取）
4. 用户可以在目录章节中手动填写目录内容

## 三、指令格式结构

### 3.1 完整结构

```json
{
  "version": "1.0",
  "description": "学校名称+学位级别+专业格式化指令",
  "instruction_type": "format_application",
  "format_rules": {
    "default_font": {...},
    "english_font": {...},
    "page": {...},
    "headings": {...},
    "paragraph": {...},
    "special_sections": {
      "title": {...},
      "abstract": {...},
      "keywords": {...},
      "conclusion": {...},
      "references": {...},
      "acknowledgement": {...},
      "table_of_contents": {
        "title_text": "目 录",
        "title_font": "黑体",
        "title_size_pt": 15,
        "title_alignment": "center",
        "title_spacing_before_pt": 24,
        "title_spacing_after_pt": 24,
        "entry_levels": [1, 2, 3]
      }
    },
    "application_rules": {
      "heading_detection": "...",
      "special_section_detection": [...],
      "auto_generate_toc": true/false,
      "toc_generation_rules": {
        "include_levels": [1, 2, 3],
        "exclude_sections": ["摘要", "关键词", "目录"],
        "page_number_format": "arabic"
      },
      "font_fallback": {...}
    }
  }
}
```

### 3.2 关键字段说明

- **`auto_generate_toc`**：是否自动生成目录
- **`toc_generation_rules.include_levels`**：包含的目录级别
- **`toc_generation_rules.exclude_sections`**：排除的章节
- **`table_of_contents.title_spacing_before_pt`**：目录标题前间距
- **`table_of_contents.title_spacing_after_pt`**：目录标题后间距

## 四、工作流程

### 4.1 上传格式文件流程

1. **上传格式文件**：学校管理员上传格式模板文档（.docx）
2. **AI分析格式**：调用AI分析文档格式，提取所有格式信息
3. **生成指令**：AI生成JSON格式指令和自然语言描述
4. **保存到数据库**：
   - `format_data`字段：保存完整的JSON格式指令
   - `remark`字段（可选）：保存自然语言描述
5. **模板关联**：每个模板（学校+专业+学位级别）有独立的指令

### 4.2 格式化论文流程

1. **读取格式指令**：从模板的`format_data`字段读取指令
2. **解析格式配置**：解析JSON格式指令，提取格式配置和布局规则
3. **检查目录生成**：
   - 检查格式指令中是否设置了`auto_generate_toc`
   - 检查文档中是否已有目录章节
   - 如果需要且没有，则自动生成目录
4. **应用格式**：根据格式指令应用所有格式
5. **生成文档**：生成格式化的Word文档

## 五、测试建议

### 5.1 测试场景

1. **自动生成目录**
   - 测试格式指令中`auto_generate_toc=true`的情况
   - 验证目录是否正确生成
   - 验证目录格式是否正确应用

2. **手动创建目录**
   - 测试用户手动创建目录章节的情况
   - 验证目录格式是否正确应用

3. **目录格式应用**
   - 测试不同学校的目录格式
   - 验证目录标题前后空行是否正确
   - 验证多级目录格式是否正确

4. **目录生成规则**
   - 测试不同的`include_levels`配置
   - 测试不同的`exclude_sections`配置
   - 验证目录条目是否正确过滤

### 5.2 测试数据

建议使用不同学校的格式模板进行测试：
- 中南林业科技大学
- 其他学校的格式模板

## 六、注意事项

1. **目录页码**：当前实现中，目录条目的页码为`None`，因为页码需要在文档生成后才能确定。如果需要页码，可以考虑：
   - 使用Word的TOC功能（需要额外的库支持）
   - 在文档生成后，再次扫描文档，更新目录页码

2. **目录格式**：确保格式指令中的目录格式配置完整，包括：
   - 目录标题格式
   - 目录条目格式（多级）
   - 目录前后空行

3. **性能优化**：如果章节数量很多，目录生成可能需要一些时间。可以考虑：
   - 异步生成目录
   - 缓存目录生成结果

## 七、后续优化建议

1. **目录页码支持**：实现目录页码的自动更新
2. **目录样式优化**：支持更多目录样式（点线、下划线等）
3. **目录级别限制**：支持配置最大目录级别
4. **目录生成性能**：优化大量章节时的目录生成性能
