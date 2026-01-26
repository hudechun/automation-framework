# AI生成功能字段名修复

## 问题

生成大纲时报错：`'ThesisModel' object has no attribute 'research_direction'`

## 原因分析

1. **ThesisModel VO** 中没有 `research_direction` 和 `keywords` 字段
2. **数据库表** (`ai_write_thesis`) 有这些字段
3. **字段名不匹配**：
   - 大纲表字段是 `outline_data` 而不是 `content`
   - 章节表字段是 `title`, `level`, `order_num` 而不是 `chapter_number`, `chapter_title`

## 修复方案

### 1. 修复大纲生成 - 使用数据库对象

**修改前：**
```python
thesis_info = {
    'title': thesis.title,
    'major': thesis.major,
    'degree_level': thesis.degree_level,
    'research_direction': thesis.research_direction,  # ❌ ThesisModel没有这个字段
    'keywords': thesis.keywords  # ❌ ThesisModel没有这个字段
}
```

**修改后：**
```python
# 从数据库对象获取论文信息
thesis_dict = await ThesisDao.get_thesis_by_id(query_db, outline_data.thesis_id)

thesis_info = {
    'title': thesis_dict.title if thesis_dict else thesis.title,
    'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
    'degree_level': getattr(thesis_dict, 'degree_level', '') if thesis_dict else '',
    'research_direction': getattr(thesis_dict, 'research_direction', '') if thesis_dict else '',
    'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else ''
}
```

### 2. 修复大纲存储字段名

**修改前：**
```python
outline_dict = {
    'thesis_id': outline_data.thesis_id,
    'content': outline_content  # ❌ 字段名错误
}
```

**修改后：**
```python
outline_dict = {
    'thesis_id': outline_data.thesis_id,
    'outline_data': outline_content  # ✅ 正确的字段名
}
```

### 3. 修复大纲读取字段名

**修改前：**
```python
outline_context = outline.content if outline else None  # ❌ 字段名错误
```

**修改后：**
```python
outline_context = outline.outline_data if outline else None  # ✅ 正确的字段名
```

### 4. 修复章节创建字段名

**修改前：**
```python
chapter_dict = {
    'thesis_id': chapter_data.thesis_id,
    'chapter_number': chapter_data.chapter_number,  # ❌ 字段名错误
    'chapter_title': chapter_data.chapter_title,    # ❌ 字段名错误
    'content': ai_content,
    'word_count': word_count,
    'status': 'completed'
}
```

**修改后：**
```python
chapter_dict = {
    'thesis_id': chapter_data.thesis_id,
    'title': chapter_data.chapter_title,  # ✅ 正确的字段名
    'level': 1,  # 默认一级章节
    'order_num': chapter_data.chapter_number if isinstance(chapter_data.chapter_number, int) else 1,
    'content': ai_content,
    'word_count': word_count,
    'status': 'completed'
}
```

## 数据库字段对照表

### ai_write_thesis 表
| 数据库字段 | VO字段 | 说明 |
|-----------|--------|------|
| title | title | 论文标题 |
| major | major | 专业 |
| degree_level | degree_level | 学位级别 |
| research_direction | ❌ 无 | 研究方向（VO中缺失） |
| keywords | ❌ 无 | 关键词（VO中缺失） |
| total_words | word_count | 总字数 |

### ai_write_thesis_outline 表
| 数据库字段 | VO字段 | 说明 |
|-----------|--------|------|
| outline_id | outline_id | 大纲ID |
| thesis_id | thesis_id | 论文ID |
| outline_data | ❌ content | 大纲数据（字段名不匹配） |
| structure_type | ❌ 无 | 结构类型 |

### ai_write_thesis_chapter 表
| 数据库字段 | VO字段 | 说明 |
|-----------|--------|------|
| chapter_id | chapter_id | 章节ID |
| thesis_id | thesis_id | 论文ID |
| title | chapter_title | 章节标题（字段名不匹配） |
| level | ❌ 无 | 章节级别 |
| order_num | ❌ chapter_number | 显示顺序（字段名不匹配） |
| content | content | 章节内容 |
| word_count | word_count | 字数统计 |
| status | status | 状态 |

## 修复结果

✅ 大纲生成现在可以正确获取论文的所有字段
✅ 大纲存储使用正确的字段名 `outline_data`
✅ 章节创建使用正确的字段名 `title`, `level`, `order_num`
✅ 所有字段名与数据库表结构匹配

## 后续建议

### 1. 统一VO模型和数据库字段

建议在 `ThesisModel` 中添加缺失的字段：

```python
class ThesisModel(BaseModel):
    # ... 现有字段 ...
    research_direction: Optional[str] = Field(default=None, description='研究方向')
    keywords: Optional[Union[str, list]] = Field(default=None, description='关键词')
```

### 2. 统一大纲字段名

建议修改 `ThesisOutlineModel` 的字段名：

```python
class ThesisOutlineModel(BaseModel):
    outline_id: Optional[int] = Field(default=None, description='大纲ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    outline_data: Optional[dict[str, Any]] = Field(default=None, description='大纲数据')  # 改为outline_data
    structure_type: Optional[str] = Field(default=None, description='结构类型')
```

### 3. 统一章节字段名

建议修改 `ThesisChapterModel` 的字段名：

```python
class ThesisChapterModel(BaseModel):
    chapter_id: Optional[int] = Field(default=None, description='章节ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    title: Optional[str] = Field(default=None, description='章节标题')  # 改为title
    level: Optional[int] = Field(default=None, description='章节级别')  # 添加level
    order_num: Optional[int] = Field(default=None, description='显示顺序')  # 改为order_num
    content: Optional[str] = Field(default=None, description='章节内容')
    word_count: Optional[int] = Field(default=None, description='字数')
    status: Optional[str] = Field(default=None, description='章节状态')
```

## 测试清单

- [x] 修复大纲生成字段获取
- [x] 修复大纲存储字段名
- [x] 修复大纲读取字段名
- [x] 修复章节创建字段名
- [ ] 测试大纲生成功能
- [ ] 测试章节生成功能
- [ ] 验证数据库存储正确

## 文件修改

- `module_thesis/service/thesis_service.py` - 修复字段名和数据获取逻辑

## 完成状态

✅ 字段名修复完成
✅ 代码诊断通过
⏳ 等待功能测试
