# 论文章节字数要求计算流程

## 一、核心逻辑

### 1.1 数据来源
- **目标总字数**：用户在创建论文时输入的 `targetWordCount`（存储在 `ai_write_thesis.total_words`）
- **学历**：从用户选择的模板中获取（`ai_write_format_template.degree_level`）
- **章节数量**：从论文大纲中计算（`ai_write_thesis_outline.outline_data.chapters`）

### 1.2 计算方式

#### 方式一：有目标总字数
```
平均字数 = 目标总字数 / 章节数量
字数范围 = 平均字数 ± 20%
最小字数 = max(1000, 平均字数 - 20%)
最大字数 = 平均字数 + 20%
```

**示例**：
- 目标总字数：10000字
- 章节数量：5章
- 平均字数：2000字
- 字数范围：1600-2400字

#### 方式二：无目标总字数
根据学历使用默认范围：
- 本科：2000-3000字
- 硕士：3000-5000字
- 博士：5000-8000字

## 二、代码实现

### 2.1 关键方法

**位置**：`module_thesis/service/ai_generation_service.py`

**方法**：`_calculate_chapter_word_count_requirement`
```python
async def _calculate_chapter_word_count_requirement(
    query_db: AsyncSession,
    thesis_info: Dict[str, Any],
    chapter_info: Dict[str, Any],
    outline_context: Optional[Union[str, dict]] = None
) -> str
```

**流程**：
1. 从 `thesis_info` 获取 `total_words`（目标总字数）
2. 从 `thesis_info` 获取 `template_id`（模板ID）
3. 通过 `template_id` 从模板表获取 `degree_level`（学历）
4. 从 `outline_context` 解析章节数量
5. 根据是否有目标总字数，选择计算方式
6. 返回字数要求字符串（格式：`"最小值-最大值"`）

### 2.2 调用位置

1. **生成章节时**：`generate_chapter` 方法
   - 如果未提供 `word_count_requirement` 参数，自动计算

2. **构建提示词时**：`_build_chapter_prompt` 方法
   - 如果仍未提供，再次计算（双重保险）

## 三、数据流

### 3.1 论文创建流程

```
用户创建论文
  ↓
输入：论文标题、专业、研究方向、关键词、目标字数
  ↓
选择：格式模板（包含学历信息）
  ↓
保存到数据库：
  - ai_write_thesis.title
  - ai_write_thesis.major
  - ai_write_thesis.research_direction
  - ai_write_thesis.keywords
  - ai_write_thesis.total_words（目标总字数）
  - ai_write_thesis.template_id（模板ID）
```

### 3.2 章节生成流程

```
生成章节
  ↓
获取论文信息（包含 total_words 和 template_id）
  ↓
从模板表获取学历（degree_level）
  ↓
从大纲获取章节数量
  ↓
计算每章节字数要求
  ↓
构建AI提示词（包含字数要求）
  ↓
调用AI生成章节内容
```

## 四、关键代码位置

1. **字数计算**：`module_thesis/service/ai_generation_service.py:_calculate_chapter_word_count_requirement()`
2. **章节生成**：`module_thesis/service/ai_generation_service.py:generate_chapter()`
3. **提示词构建**：`module_thesis/service/ai_generation_service.py:_build_chapter_prompt()`
4. **论文信息构建**：`module_thesis/service/thesis_service.py`（多个方法中）

## 五、注意事项

1. **模板必须存在**：如果论文没有关联模板（`template_id` 为空），学历将使用默认值"本科"
2. **章节数量默认值**：如果无法从大纲解析章节数量，默认使用5章
3. **最小字数限制**：即使计算出的最小字数小于1000，也会强制设为1000字
4. **兼容性**：如果模板中没有学历信息，会尝试从论文信息中获取（兼容旧数据）

## 六、测试场景

1. **有目标总字数 + 有模板 + 有大纲**：正常计算
2. **有目标总字数 + 无模板**：使用默认学历（本科）
3. **无目标总字数 + 有模板**：使用学历对应的默认范围
4. **无目标总字数 + 无模板**：使用本科默认范围（2000-3000）
