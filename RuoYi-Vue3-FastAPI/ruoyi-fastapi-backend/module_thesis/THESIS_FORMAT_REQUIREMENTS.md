# 论文格式化系统 - 格式指令生成与识别要求

## 一、AI生成文档格式指令的要求

### 1.1 格式指令识别方式

系统使用 **python-docx** 库读取Word文档，提取格式信息，然后使用AI分析并生成标准化的格式指令。

#### Python识别格式的方式：

1. **字体格式识别**：
   - 字体名称：`run.font.name`
   - 字体大小：`run.font.size` (磅值)
   - 字体颜色：`run.font.color.rgb` (RGB值)
   - 粗体：`run.bold`
   - 斜体：`run.italic`
   - 下划线：`run.underline`

2. **段落格式识别**：
   - 对齐方式：`para.alignment` (left/center/right/justify)
   - 行距：`para.paragraph_format.line_spacing`
   - 段前距：`para.paragraph_format.space_before`
   - 段后距：`para.paragraph_format.space_after`
   - 首行缩进：`para.paragraph_format.first_line_indent`
   - 左右缩进：`para.paragraph_format.left_indent/right_indent`

3. **标题格式识别**：
   - 通过样式名称识别：`para.style.name` (如 "Heading 1", "标题 1")
   - 提取标题的字体、大小、对齐等格式

4. **页面设置识别**：
   - 页边距：`section.top_margin/bottom_margin/left_margin/right_margin`
   - 纸张大小：`section.page_width/page_height`

### 1.2 AI生成格式指令的要求

**提示词要求**：
- 系统角色：专业的文档格式分析专家
- 输入：Word文档的格式信息（JSON格式）
- 输出：标准化的JSON格式指令

**格式指令JSON结构**：
```json
{
  "font": {
    "name": "字体名称（如：宋体、Times New Roman）",
    "size": 字体大小（磅，如：12）,
    "color": "颜色（RGB或颜色名称，可选）"
  },
  "paragraph": {
    "alignment": "对齐方式（left/center/right/justify）",
    "line_spacing": 行距倍数（如：1.5）,
    "spacing_before": 段前间距（磅）,
    "spacing_after": 段后间距（磅）,
    "first_line_indent": 首行缩进（磅，如：24表示2字符）,
    "left_indent": 左缩进（磅）,
    "right_indent": 右缩进（磅）
  },
  "headings": {
    "h1": {
      "font_name": "字体名称",
      "font_size": 字体大小（磅）,
      "bold": true/false,
      "alignment": "对齐方式",
      "spacing_before": 段前距,
      "spacing_after": 段后距
    },
    "h2": { ... },
    "h3": { ... }
  },
  "page": {
    "margins": {
      "top": 上边距（磅，如：72）,
      "bottom": 下边距（磅）,
      "left": 左边距（磅，如：90）,
      "right": 右边距（磅）
    },
    "size": "纸张大小（A4/Letter等）"
  }
}
```

**AI分析要求**：
1. 必须返回纯JSON格式，不要包含其他说明文字
2. 如果无法确定某个格式，使用合理的默认值
3. 优先识别正文段落的格式作为默认格式
4. 识别所有级别的标题格式（h1-h6）
5. 识别页面设置（页边距、纸张大小）

---

## 二、生成章节内容的要求

### 2.1 章节生成输入信息

**必需信息**：
1. **论文基本信息**：
   - 论文标题
   - 专业
   - 学历层次（本科/硕士/博士）
   - 研究方向
   - 关键词

2. **章节信息**：
   - 章节号（如：1, 2, 3）
   - 章节标题（如：引言、文献综述、研究方法）
   - 章节小节（从大纲中提取，如果有）

3. **大纲上下文**（可选但推荐）：
   - 完整的大纲结构（JSON格式）
   - 帮助AI理解论文整体结构和章节关系

### 2.2 章节生成提示词要求

**系统角色**：专业的学术论文写作助手

**提示词结构**：
```
请为以下论文撰写章节内容：

论文信息：
- 标题：[论文标题]
- 专业：[专业]
- 学历层次：[学历层次]
- 研究方向：[研究方向]
- 关键词：[关键词列表]

章节信息：
- 章节号：[章节号]
- 章节标题：[章节标题]
- 章节小节：[小节列表，如果有]

大纲上下文：
[完整的大纲结构，帮助理解论文整体结构]

要求：
1. 内容要符合学术规范
2. 逻辑清晰，结构完整
3. 字数要充足（根据章节类型确定）
4. 使用学术语言
5. 如果有小节，要按照小节结构组织内容

请直接返回章节内容，不要包含其他说明文字。
```

### 2.3 章节内容质量要求

1. **学术规范性**：
   - 使用学术语言
   - 避免口语化表达
   - 逻辑清晰，论证充分

2. **结构完整性**：
   - 章节开头要有引言
   - 主体内容要分层次
   - 章节结尾要有小结（如适用）

3. **字数要求**：
   - **用户选择**：在新建论文时，用户可以选择每章节字数要求
   - **优先级**：论文中保存的字数要求 > 系统配置 > 默认值
   - **论文字段**：`ai_write_thesis.chapter_word_count_requirement`（格式：最小值-最大值，如：2000-3000）
   - **系统配置**：如果论文中没有配置，则从系统配置表（sys_config）读取
     * 配置键名格式：`thesis.word_count.{学位级别}`
     * `thesis.word_count.本科`：默认值 2000-3000
     * `thesis.word_count.硕士`：默认值 3000-5000
     * `thesis.word_count.博士`：默认值 5000-8000
   - **默认值**：如果论文和系统配置都没有，使用默认值
     * 本科：2000-3000
     * 硕士：3000-5000
     * 博士：5000-8000

4. **内容相关性**：
   - 与论文主题相关
   - 与大纲结构一致
   - 与前后章节呼应

---

## 三、格式化完整论文的要求

### 3.1 格式化流程

1. **准备阶段**：
   - 检查所有章节是否已完成（status='completed'）
   - 获取论文关联的格式模板
   - 获取格式指令（优先使用模板的format_data，如果没有则从Word文档解析）

2. **应用格式**：
   - 创建新的Word文档
   - 应用页面设置（页边距、纸张大小）
   - 添加论文标题（使用标题格式）
   - 遍历所有已完成的章节：
     * 添加章节标题（应用标题格式）
     * 添加章节内容（应用正文格式）
     * 章节之间添加适当间距

3. **保存文档**：
   - 保存到：`uploads/thesis/formatted/thesis_{thesis_id}_formatted.docx`
   - 更新论文状态为 `formatted`

### 3.2 格式化要求

#### 3.2.1 文档结构

```
[论文标题]（居中，大号字体，加粗）
[空行]

[第一章标题]（居中，标题格式）
[章节内容]（正文格式，首行缩进）

[第二章标题]（居中，标题格式）
[章节内容]（正文格式，首行缩进）

...
```

#### 3.2.2 格式应用规则

1. **论文标题**：
   - 字体：标题字体（通常比正文大）
   - 大小：18磅
   - 对齐：居中
   - 加粗：是

2. **章节标题**：
   - 根据章节级别应用对应的标题格式（h1/h2/h3）
   - 默认：居中，加粗，比正文大2-4磅

3. **正文内容**：
   - 字体：从格式指令中获取（默认：宋体）
   - 大小：从格式指令中获取（默认：12磅）
   - 对齐：从格式指令中获取（默认：左对齐）
   - 行距：从格式指令中获取（默认：1.5倍）
   - 首行缩进：从格式指令中获取（默认：2字符，24磅）

4. **段落间距**：
   - 段前距：从格式指令中获取
   - 段后距：从格式指令中获取

5. **页面设置**：
   - 页边距：从格式指令中获取（默认：上下72磅，左右90磅）
   - 纸张大小：从格式指令中获取（默认：A4）

### 3.3 格式化代码实现要点

#### 3.3.1 格式指令解析

```python
# 解析格式指令（JSON字符串）
format_config = json.loads(format_instructions)

# 获取各部分的格式配置
font_config = format_config.get('font', {})
para_config = format_config.get('paragraph', {})
headings_config = format_config.get('headings', {})
page_config = format_config.get('page', {})
```

#### 3.3.2 应用格式

```python
# 应用页面设置
section = doc.sections[0]
section.top_margin = Inches(margins['top'] / 72)
section.bottom_margin = Inches(margins['bottom'] / 72)
section.left_margin = Inches(margins['left'] / 72)
section.right_margin = Inches(margins['right'] / 72)

# 应用段落格式
para = doc.add_paragraph()
run = para.add_run(text)
run.font.name = font_config.get('name', '宋体')
run.font.size = Pt(font_config.get('size', 12))
para.alignment = get_alignment(para_config.get('alignment', 'left'))
para.paragraph_format.line_spacing = para_config.get('line_spacing', 1.5)
para.paragraph_format.first_line_indent = Pt(para_config.get('first_line_indent', 24))
```

#### 3.3.3 处理章节内容

```python
# 只处理已完成的章节
chapters = [c for c in all_chapters if c.status == 'completed']

# 按章节顺序排序
chapters.sort(key=lambda x: x.order_num)

# 遍历章节，应用格式
for chapter in chapters:
    # 添加章节标题
    title_para = doc.add_paragraph()
    title_run = title_para.add_run(chapter.title)
    # 应用标题格式
    apply_heading_format(title_run, chapter.level, headings_config)
    
    # 添加章节内容
    content_lines = chapter.content.split('\n')
    for line in content_lines:
        if line.strip():
            para = doc.add_paragraph()
            run = para.add_run(line.strip())
            # 应用正文格式
            apply_body_format(run, para, font_config, para_config)
```

---

## 四、完整流程总结

### 4.1 格式指令生成流程

```
1. 上传Word模板
   ↓
2. python-docx读取文档
   ↓
3. 提取格式信息（字体、段落、标题、页面）
   ↓
4. 构建AI提示词
   ↓
5. AI分析并生成JSON格式指令
   ↓
6. 保存到模板的format_data字段
```

### 4.2 章节生成流程

```
1. 获取论文信息和大纲
   ↓
2. 构建章节生成提示词
   ↓
3. AI生成章节内容
   ↓
4. 保存章节到数据库（status='completed'）
   ↓
5. 更新论文总字数
```

### 4.3 格式化流程

```
1. 检查章节是否都已完成
   ↓
2. 获取格式指令（从模板format_data或重新解析）
   ↓
3. 创建新Word文档
   ↓
4. 应用页面设置
   ↓
5. 添加论文标题
   ↓
6. 遍历章节，应用格式并添加内容
   ↓
7. 保存格式化后的文档
   ↓
8. 更新论文状态为formatted
```

---

## 五、关键代码位置

1. **格式提取**：`module_thesis/service/format_service.py:_extract_document_content()`
2. **AI格式分析**：`module_thesis/service/format_service.py:_analyze_format_with_ai()`
3. **章节生成**：`module_thesis/service/ai_generation_service.py:generate_chapter()`
4. **格式化文档**：`module_thesis/service/format_service.py:_create_formatted_document()`
5. **格式化流程**：`module_thesis/service/thesis_service.py:format_thesis()`

---

## 六、字数要求配置

### 6.1 用户选择（新建论文时）

在新建论文时，用户可以在表单中选择**每章节字数要求**：

- **字段名**：`chapterWordCountRequirement`
- **格式**：最小值-最大值（如：2000-3000）
- **存储位置**：`ai_write_thesis.chapter_word_count_requirement`
- **说明**：用户可以根据自己的需求选择每章节的字数要求

### 6.2 系统配置（默认值）

如果用户在创建论文时没有选择字数要求，系统会根据学位级别从系统配置表（`sys_config`）读取默认值：

1. **数据库直接配置**：
   ```sql
   -- 执行初始化SQL脚本
   source sql/thesis_word_count_config.sql
   ```

2. **通过系统管理界面配置**：
   - 进入：系统管理 -> 参数配置
   - 添加或修改以下配置项：
     * 配置名称：论文章节字数要求-本科
     * 参数键名：`thesis.word_count.本科`
     * 参数键值：`2000-3000`
     * 系统内置：是
   
   * 配置名称：论文章节字数要求-硕士
     * 参数键名：`thesis.word_count.硕士`
     * 参数键值：`3000-5000`
     * 系统内置：是
   
   * 配置名称：论文章节字数要求-博士
     * 参数键名：`thesis.word_count.博士`
     * 参数键值：`5000-8000`
     * 系统内置：是

### 6.3 字数要求读取优先级

在生成章节时，系统按以下优先级获取字数要求：

1. **论文中保存的字数要求**（`chapter_word_count_requirement`字段）
2. **系统配置**（根据学位级别从`sys_config`表读取）
3. **默认值**（如果配置不存在）：
   - 本科：2000-3000
   - 硕士：3000-5000
   - 博士：5000-8000

### 6.4 数据库字段

需要在论文表中添加字段（执行SQL脚本）：
```sql
-- 执行SQL脚本
source sql/thesis_add_chapter_word_count_requirement.sql
```

### 6.5 配置生效

- 系统配置修改后，需要清除Redis缓存或重启服务才能生效
- 系统启动时会自动加载配置到Redis缓存
- 论文中的字数要求立即生效，无需重启

---

## 七、注意事项

1. **格式指令必须是有效的JSON**：AI返回的格式指令需要能够被解析为JSON
2. **章节内容要完整**：只格式化status='completed'的章节
3. **路径处理**：格式化文件保存路径要使用绝对路径
4. **错误处理**：每个步骤都要有完善的错误处理和日志记录
5. **性能优化**：格式化大文档时要注意内存使用
6. **字数配置**：字数要求可以从系统配置中读取，支持动态调整
