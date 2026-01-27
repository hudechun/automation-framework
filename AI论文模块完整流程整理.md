# AI论文模块完整流程整理

## 📋 目录

1. [系统概述](#系统概述)
2. [核心业务流程](#核心业务流程)
3. [技术架构](#技术架构)
4. [数据库设计](#数据库设计)
5. [关键功能实现](#关键功能实现)
6. [API接口清单](#api接口清单)

---

## 🎯 系统概述

### 系统定位
AI论文写作系统是一个基于RuoYi-FastAPI框架的智能论文生成平台，帮助学生快速生成符合学校格式要求的学术论文。

### 核心价值
- ✅ 自动化论文格式处理，节省排版时间
- ✅ AI辅助内容生成，提高写作效率
- ✅ 智能去AI化处理，降低AIGC检测率
- ✅ 多学校格式支持，适应不同需求

### 技术栈
**后端**: FastAPI + MySQL + Redis + python-docx + 通义千问/GPT-4  
**前端**: Vue 3 + Element Plus + TinyMCE + Tailwind CSS

---

## 🔄 核心业务流程

### 流程1: 用户注册与会员购买

```
用户注册 → 浏览套餐 → 选择套餐 → 支付（微信/支付宝）→ 开通会员 → 获得配额
```

**涉及表**:
- `ai_write_member_package` - 会员套餐表
- `ai_write_user_membership` - 用户会员表
- `ai_write_order` - 订单表

**关键服务**:
- `MemberService.activate_membership()` - 激活会员
- `PaymentService.create_order()` - 创建订单


### 流程2: 格式模板上传与解析

```
管理员上传Word模板 → Python解析格式 → 提取样式规则 → 保存模板配置 → 用户可选择使用
```

**核心步骤**:
1. **上传模板** - 上传学校的论文格式Word文档（.docx）
2. **解析格式** - 使用`python-docx`解析文档结构
3. **提取规则** - 提取字体、字号、行距、页边距、章节编号等
4. **保存配置** - 将格式规则保存为JSON格式

**涉及表**:
- `ai_write_format_template` - 格式模板表
- `ai_write_template_format_rule` - 模板格式规则表

**关键代码**:
```python
# 解析Word文档格式
DocxParser.parse_document(file_path)
  → extract_styles()      # 提取样式
  → extract_structure()   # 提取章节结构
  → extract_numbering()   # 提取编号格式
```

---

### 流程3: 论文创建与大纲生成 ⭐

```
用户创建论文 → 填写基本信息 → AI生成大纲 → 用户确认/调整大纲
```

**详细步骤**:

#### 3.1 创建论文
用户填写:
- 论文标题
- 专业名称
- 学历层次（本科/硕士/博士）
- 研究方向
- 关键词（3-5个）
- 论文类型（理论研究/实证研究/综述）

**API**: `POST /thesis/paper/create`  
**服务**: `ThesisService.create_thesis()`  
**配额扣减**: 扣减1次论文生成配额

#### 3.2 AI生成大纲
系统调用AI模型生成论文大纲:

**输入**:
- 论文基本信息（标题、专业、关键词等）
- 格式要求（从模板中提取）
- 大纲结构类型（三段式/五段式）

**AI Prompt构建**:
```python
prompt = f"""
请为以下论文生成详细的大纲：
论文标题：{title}
专业：{major}
关键词：{keywords}

格式要求：
- 一级标题：第X章 标题（黑体、三号、居中）
- 二级标题：X.Y 标题（黑体、四号、左对齐）
...

返回JSON格式：
{{
  "title": "论文标题",
  "chapters": [
    {{
      "chapter_number": 1,
      "chapter_title": "第一章 引言",
      "sections": [
        {{"section_number": "1.1", "section_title": "研究背景"}}
      ]
    }}
  ]
}}
"""
```

**API**: `POST /thesis/paper/outline/generate`  
**服务**: `AiGenerationService.generate_outline()`  
**配额扣减**: 扣减1次大纲生成配额

**涉及表**:
- `ai_write_thesis` - 论文表
- `ai_write_thesis_outline` - 论文大纲表

---

### 流程4: 章节内容生成 ⭐⭐

```
选择章节 → AI生成内容 → 保存章节 → 更新字数统计 → 扣减配额
```

**详细步骤**:

#### 4.1 单章节生成
**API**: `POST /thesis/paper/chapter/generate`  
**服务**: `ThesisService.generate_chapter()`

**AI生成逻辑**:
```python
# 1. 获取上下文
thesis_info = {
    'title': '论文标题',
    'major': '专业',
    'keywords': ['关键词1', '关键词2']
}

chapter_info = {
    'chapter_number': 1,
    'chapter_title': '第一章 引言',
    'sections': [
        {'section_number': '1.1', 'section_title': '研究背景'}
    ]
}

# 2. 构建Prompt
prompt = f"""
你是专业的学术论文写作助手。
论文标题：{thesis_info['title']}
当前章节：{chapter_info['chapter_title']}
目标字数：约2000字

前文内容摘要：[已生成章节的摘要]

请生成该章节的完整内容...
"""

# 3. 调用AI生成
content = await llm_provider.chat(messages)

# 4. 保存章节
chapter = {
    'thesis_id': thesis_id,
    'title': chapter_title,
    'content': content,
    'word_count': calculate_word_count(content),
    'status': 'completed'
}
```

#### 4.2 批量生成章节
**API**: `POST /thesis/paper/chapter/batch-generate`  
**服务**: `ThesisService.batch_generate_chapters()`

**特点**:
- ✅ 支持断点续传（已完成的章节跳过）
- ✅ 部分成功策略（单个失败不影响其他）
- ✅ 按大纲顺序生成（保持连贯性）

**配额扣减**: 只扣减成功生成的章节数量

**涉及表**:
- `ai_write_thesis_chapter` - 论文章节表
- `ai_write_quota_record` - 配额使用记录表

---

### 流程5: 内容编辑与优化

```
查看章节 → 在线编辑 → 保存修改 → （可选）AI优化
```

**功能**:
1. **富文本编辑** - 支持格式调整、插入图表
2. **去AI化处理** - 改写AI痕迹明显的句子
3. **内容润色** - 语法检查、逻辑优化
4. **AIGC检测** - 预估AI生成概率

**API**:
- `PUT /thesis/paper/chapter/update` - 更新章节
- `POST /thesis/paper/chapter/optimize` - AI优化

---

### 流程6: 格式应用与导出 ⭐

```
选择格式模板 → Python应用格式 → 生成Word文档 → 用户下载
```

**详细步骤**:

#### 6.1 应用格式模板
```python
# 1. 获取模板格式数据
template = await TemplateDao.get_template_by_id(template_id)
format_data = json.loads(template.format_data)

# 2. 创建Word文档
doc = Document()

# 3. 应用页面设置
section = doc.sections[0]
section.page_width = Cm(format_data['page_width'])
section.page_height = Cm(format_data['page_height'])
section.top_margin = Cm(format_data['top_margin'])
...

# 4. 添加章节内容
for chapter in chapters:
    # 添加标题（应用样式）
    heading = doc.add_heading(chapter.title, level=chapter.level)
    apply_style(heading, format_data['styles']['Heading 1'])
    
    # 添加正文（应用样式）
    for paragraph in chapter.content.split('\n\n'):
        para = doc.add_paragraph(paragraph)
        apply_style(para, format_data['styles']['Normal'])

# 5. 添加页眉页脚
header = section.header
header.paragraphs[0].text = school_name

# 6. 保存文档
doc.save(output_path)
```

**API**: `POST /thesis/paper/export`  
**服务**: `ThesisService.export_thesis()`

**涉及表**:
- `ai_write_export_record` - 导出记录表

---

## 🏗️ 技术架构

### 分层架构

```
┌─────────────────────────────────────┐
│   前端层 (Vue 3 + Element Plus)      │
└─────────────────────────────────────┘
              ↓ HTTP/WebSocket
┌─────────────────────────────────────┐
│   API网关层 (FastAPI Router)         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   业务逻辑层 (Service Layer)         │
│   - ThesisService                   │
│   - AiGenerationService             │
│   - MemberService                   │
│   - TemplateService                 │
│   - PaymentService                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   数据访问层 (DAO Layer)             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   数据存储层 (MySQL + Redis)         │
└─────────────────────────────────────┘
```

### 模块结构

```
module_thesis/
├── controller/           # 控制器层（API接口）
│   ├── thesis_controller.py
│   ├── template_controller.py
│   ├── member_controller.py
│   └── payment_controller.py
├── service/             # 业务逻辑层
│   ├── thesis_service.py
│   ├── ai_generation_service.py
│   ├── member_service.py
│   ├── template_service.py
│   └── payment_gateway_service.py
├── dao/                 # 数据访问层
│   ├── thesis_dao.py
│   ├── template_dao.py
│   └── member_dao.py
├── entity/              # 实体类
│   ├── do/             # 数据库实体
│   └── vo/             # 视图对象
└── utils/               # 工具类
    ├── docx_parser.py
    └── docx_formatter.py
```

---

## 💾 数据库设计

### 核心表（13张）

#### 1. 会员相关（3张）
- `ai_write_member_package` - 会员套餐表
- `ai_write_user_membership` - 用户会员表
- `ai_write_user_feature_quota` - 用户功能配额表

#### 2. 论文相关（5张）
- `ai_write_thesis` - 论文表
- `ai_write_thesis_outline` - 论文大纲表
- `ai_write_thesis_chapter` - 论文章节表
- `ai_write_thesis_version` - 论文版本历史表
- `ai_write_export_record` - 导出记录表

#### 3. 模板相关（2张）
- `ai_write_format_template` - 格式模板表
- `ai_write_template_format_rule` - 模板格式规则表

#### 4. 订单相关（2张）
- `ai_write_order` - 订单表
- `ai_write_feature_service` - 功能服务表

#### 5. 配额相关（1张）
- `ai_write_quota_record` - 配额使用记录表

### 关键字段说明

**论文状态** (`ai_write_thesis.status`):
- `draft` - 草稿
- `generating` - 生成中
- `formatted` - 已格式化（章节生成完成）
- `completed` - 已完成
- `exported` - 已导出

**章节状态** (`ai_write_thesis_chapter.status`):
- `pending` - 待生成
- `generating` - 生成中
- `completed` - 已完成
- `edited` - 已编辑

**订单状态** (`ai_write_order.status`):
- `pending` - 待支付
- `paid` - 已支付
- `refunded` - 已退款
- `cancelled` - 已取消

---

## 🔑 关键功能实现

### 1. 配额管理系统

**设计思路**: 配额直接存储在会员表中，简化查询逻辑

```python
# 检查配额
async def check_quota(user_id, feature_type, amount):
    membership = await get_user_membership(user_id)
    
    # 检查会员是否过期
    if membership.end_date < datetime.now():
        return False
    
    # 检查使用次数配额
    remaining = membership.total_usage_quota - membership.used_usage_quota
    return remaining >= amount

# 扣减配额
async def deduct_quota(user_id, amount):
    # 更新会员表
    await update_quota_usage(membership_id, usage_count=amount)
    
    # 记录使用记录
    await add_quota_record({
        'user_id': user_id,
        'usage_count': amount,
        'operation_type': 'generate'
    })
```

**事务控制**: 配额扣减不自动提交，由调用方统一控制事务

---

### 2. AI模型统一接口

**设计思路**: 使用`automation-framework`的统一AI接口

```python
# 获取AI提供商
async def _get_ai_provider(query_db, config_id=None):
    # 1. 获取AI模型配置
    config = await AiModelService.get_default_config(query_db, 'language')
    
    # 2. 转换为ModelConfig
    model_config = model_config_from_db_model(config)
    
    # 3. 创建LLM提供商
    provider = create_llm_provider(model_config)
    
    return provider

# 调用AI生成
async def generate_outline(thesis_info):
    provider, config = await _get_ai_provider(query_db)
    
    messages = [
        {"role": "system", "content": "你是专业的学术论文写作助手"},
        {"role": "user", "content": prompt}
    ]
    
    response = await provider.chat(messages, temperature=0.7)
    return parse_outline_response(response)
```

**支持的AI模型**:
- 通义千问（Qwen）
- GPT-4（OpenAI）
- 本地模型

---

### 3. 格式模板解析

**核心技术**: `python-docx`库

```python
class DocxParser:
    def parse_document(self, file_path):
        doc = Document(file_path)
        
        return {
            'page_settings': self.extract_page_settings(doc),
            'styles': self.extract_styles(doc),
            'structure': self.extract_structure(doc),
            'numbering': self.extract_numbering(doc)
        }
    
    def extract_styles(self, doc):
        styles = {}
        for style in doc.styles:
            if style.type == 1:  # 段落样式
                styles[style.name] = {
                    'font_name': style.font.name,
                    'font_size': style.font.size.pt,
                    'bold': style.font.bold,
                    'alignment': style.paragraph_format.alignment,
                    'line_spacing': style.paragraph_format.line_spacing
                }
        return styles
```

---

### 4. Word文档生成

**核心技术**: `python-docx`库

```python
class DocxFormatter:
    def generate_thesis_document(self, thesis, chapters, format_data):
        doc = Document()
        
        # 1. 应用页面设置
        self._apply_page_settings(doc, format_data)
        
        # 2. 添加封面
        self._add_cover_page(doc, thesis)
        
        # 3. 添加目录
        self._add_table_of_contents(doc)
        
        # 4. 添加章节
        for chapter in chapters:
            self._add_chapter(doc, chapter, format_data)
        
        # 5. 添加页眉页脚
        self._apply_header_footer(doc, thesis)
        
        return doc
    
    def _add_chapter(self, doc, chapter, format_data):
        # 添加标题
        heading = doc.add_heading(chapter.title, level=chapter.level)
        self._apply_heading_style(heading, chapter.level, format_data)
        
        # 添加内容
        for para_text in chapter.content.split('\n\n'):
            para = doc.add_paragraph(para_text)
            self._apply_paragraph_style(para, format_data)
```

---

## 📡 API接口清单

### 论文管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/paper/list` | GET | 获取论文列表 |
| `/thesis/paper/detail` | GET | 获取论文详情 |
| `/thesis/paper/create` | POST | 创建论文 |
| `/thesis/paper/update` | PUT | 更新论文 |
| `/thesis/paper/delete` | DELETE | 删除论文 |

### 大纲管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/paper/outline/generate` | POST | 生成大纲 |
| `/thesis/paper/outline/get` | GET | 获取大纲 |

### 章节管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/paper/chapter/generate` | POST | 生成单个章节 |
| `/thesis/paper/chapter/batch-generate` | POST | 批量生成章节 |
| `/thesis/paper/chapter/list` | GET | 获取章节列表 |
| `/thesis/paper/chapter/update` | PUT | 更新章节 |
| `/thesis/paper/chapter/progress` | GET | 获取生成进度 |

### 导出管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/paper/export` | POST | 导出Word文档 |
| `/thesis/paper/export/records` | GET | 导出记录列表 |

### 会员管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/member/package/list` | GET | 套餐列表 |
| `/thesis/member/info` | GET | 用户会员信息 |
| `/thesis/member/quota` | GET | 用户配额信息 |

### 模板管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/template/list` | GET | 模板列表 |
| `/thesis/template/upload` | POST | 上传模板 |
| `/thesis/template/detail` | GET | 模板详情 |

### 订单管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/thesis/order/create` | POST | 创建订单 |
| `/thesis/order/list` | GET | 订单列表 |
| `/thesis/order/status` | GET | 查询订单状态 |

---

## 🎯 核心流程总结

### 完整使用流程

```
1. 用户注册登录
   ↓
2. 购买会员套餐（获得配额）
   ↓
3. 创建论文（填写基本信息）
   ↓
4. AI生成大纲（可调整）
   ↓
5. AI生成章节内容（批量或单个）
   ↓
6. 在线编辑优化（可选）
   ↓
7. 选择格式模板
   ↓
8. 导出Word文档
   ↓
9. 下载使用
```

### 配额扣减规则

| 操作 | 扣减配额 | 说明 |
|------|----------|------|
| 创建论文 | 1次 | 论文生成配额 |
| 生成大纲 | 1次 | 大纲生成配额 |
| 生成章节 | 1次/章节 | 章节生成配额 |
| 批量生成 | N次 | N=成功生成的章节数 |
| 导出文档 | 0次 | 不扣减配额 |

### 事务控制原则

- ✅ 配额扣减不自动提交，由调用方统一控制
- ✅ 业务操作和配额扣减在同一事务中
- ✅ 失败时统一回滚，保证数据一致性

---

## 📚 相关文档

- [需求规范](./kiro/specs/ai-thesis-writing/requirements.md)
- [设计文档](./kiro/specs/ai-thesis-writing/design.md)
- [数据库快速参考](./kiro/specs/ai-thesis-writing/DATABASE_QUICK_REFERENCE.md)
- [论文生成工作流](./kiro/specs/ai-thesis-writing/THESIS_GENERATION_WORKFLOW.md)
- [快速开始](./kiro/specs/ai-thesis-writing/QUICK_START.md)

---

**创建时间**: 2026-01-28  
**最后更新**: 2026-01-28
