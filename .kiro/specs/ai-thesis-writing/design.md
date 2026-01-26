# AI论文写作系统 - 设计文档
全部用中文回答

## 1. 概述

本设计文档描述了AI论文写作系统的技术架构、组件设计和实现细节。系统基于RuoYi-FastAPI框架，提供论文格式模板管理、AI内容生成、去AI化处理、会员权益管理和支付集成等核心功能。

### 1.1 设计目标

- 提供可扩展的模块化架构
- 支持多种AI模型集成
- 确保高性能和高可用性
- 实现安全的支付和数据处理
- 支持灵活的会员权益管理

### 1.2 技术栈

**后端**:
- FastAPI (Python 3.9+)
- MySQL 8.0+
- Redis 6.0+
- python-docx (Word文档处理)
- 通义千问/GPT-4 (AI模型)

**前端**:
- Vue 3
- Element Plus
- TinyMCE/Quill (富文本编辑器)
- Docx-preview (文档预览)
- Tailwind CSS (样式框架)

**UI/UX设计**:
- 详细的UI设计规范请参考: `ui-design.md`
- 设计系统包含: 色彩、字体、间距、组件、布局、交互等完整规范
- 遵循学术专业、简洁高效的设计理念

---

## 2. 系统架构

### 2.1 整体架构

系统采用分层架构设计:

```
┌─────────────────────────────────────────────┐
│           前端层 (Vue 3 + Element Plus)      │
└─────────────────────────────────────────────┘
                    ↓ HTTP/WebSocket
┌─────────────────────────────────────────────┐
│         API网关层 (FastAPI Router)           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  业务逻辑层 (Service Layer)                  │
│  - TemplateService                          │
│  - ThesisService                            │
│  - AIService                                │
│  - MemberService                            │
│  - PaymentService                           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  数据访问层 (DAO Layer)                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  数据存储层 (MySQL + Redis + File Storage)   │
└─────────────────────────────────────────────┘
```


### 2.2 模块结构

```
module_thesis/
├── controller/                    # 控制器层
│   ├── template_controller.py    # 模板管理API
│   ├── thesis_controller.py      # 论文管理API
│   ├── payment_controller.py     # 支付API
│   └── member_controller.py      # 会员管理API
├── service/                       # 业务逻辑层
│   ├── template_service.py       # 模板业务逻辑
│   ├── thesis_service.py         # 论文业务逻辑
│   ├── ai_service.py             # AI生成服务
│   ├── format_service.py         # 格式处理服务
│   ├── payment_service.py        # 支付服务
│   └── member_service.py         # 会员服务
├── dao/                           # 数据访问层
│   ├── template_dao.py
│   ├── thesis_dao.py
│   ├── member_dao.py
│   └── payment_dao.py
├── entity/                        # 实体类
│   ├── do/                       # 数据库实体
│   │   ├── template_do.py
│   │   ├── thesis_do.py
│   │   ├── member_do.py
│   │   └── payment_do.py
│   └── vo/                       # 视图对象
│       ├── template_vo.py
│       ├── thesis_vo.py
│       └── member_vo.py
├── utils/                         # 工具类
│   ├── docx_parser.py            # Word文档解析
│   ├── docx_formatter.py         # Word文档格式化
│   ├── aigc_detector.py          # AIGC检测
│   └── ai_optimizer.py           # AI优化处理
└── middleware/                    # 中间件
    ├── quota_middleware.py       # 配额验证中间件
    └── member_middleware.py      # 会员权限中间件
```

---

## 3. 核心组件设计

### 3.1 格式模板管理

#### 3.1.1 模板解析器 (DocxParser)

**职责**: 解析Word文档，提取格式规则和章节结构

**核心方法**:
```python
class DocxParser:
    def parse_document(self, file_path: str) -> TemplateFormat:
        """解析Word文档，提取格式信息"""
        pass
    
    def extract_styles(self, document: Document) -> Dict[str, StyleInfo]:
        """提取样式信息（字体、字号、行距等）"""
        pass
    
    def extract_structure(self, document: Document) -> List[ChapterStructure]:
        """提取章节结构"""
        pass
    
    def extract_numbering(self, document: Document) -> NumberingFormat:
        """提取编号格式"""
        pass
```


**数据结构**:
```python
@dataclass
class TemplateFormat:
    """模板格式信息"""
    template_id: str
    school_name: str
    major: str
    degree_level: str  # 本科/硕士/博士
    
    # 页面设置
    page_margins: PageMargins
    page_size: PageSize
    
    # 样式信息
    styles: Dict[str, StyleInfo]  # 标题1-6、正文、引用等
    
    # 章节结构
    chapter_structure: List[ChapterStructure]
    
    # 编号格式
    numbering_format: NumberingFormat
    
    # 页眉页脚
    header_footer: HeaderFooterFormat

@dataclass
class StyleInfo:
    """样式信息"""
    font_name: str
    font_size: float
    bold: bool
    italic: bool
    line_spacing: float
    alignment: str  # left/center/right/justify
    first_line_indent: float
    space_before: float
    space_after: float
```

#### 3.1.2 模板服务 (TemplateService)

**职责**: 管理模板的CRUD操作和模板应用

**核心方法**:
```python
class TemplateService:
    async def upload_template(self, file: UploadFile, metadata: TemplateMetadata) -> Template:
        """上传并解析模板"""
        pass
    
    async def get_template(self, template_id: str) -> Template:
        """获取模板详情"""
        pass
    
    async def list_templates(self, filters: TemplateFilter) -> List[Template]:
        """查询模板列表"""
        pass
    
    async def update_template(self, template_id: str, updates: TemplateUpdate) -> Template:
        """更新模板"""
        pass
    
    async def delete_template(self, template_id: str) -> bool:
        """删除模板（软删除）"""
        pass
    
    async def apply_template(self, thesis_id: str, template_id: str) -> bool:
        """应用模板到论文"""
        pass
```

---

### 3.2 会员权益管理

#### 3.2.1 会员等级配置

**套餐设置说明**:

根据需求文档，系统提供4个会员等级，但考虑到实际运营，建议简化为3个主要套餐：

**方案一：三套餐体系（推荐）**

| 套餐 | 价格 | 字数配额 | 使用次数 | 核心功能 |
|------|------|----------|----------|----------|
| **免费体验版** | ¥0 | 5,000字 | 1次 | • 基础论文生成<br>• 简单大纲生成<br>• 基础格式应用<br>• 单次导出 |
| **专业版** | ¥199/月 | 100,000字 | 30次 | • 免费版所有功能<br>• 去AI化处理<br>• 内容润色<br>• AIGC检测预估<br>• 多次导出<br>• 版本历史（10个版本） |
| **旗舰版** | ¥499/月 | 无限 | 无限 | • 专业版所有功能<br>• 查重率预估<br>• 高级AI模型（GPT-4）<br>• 人工审核服务<br>• 无限版本历史<br>• 优先客服支持 |

**方案二：四套餐体系（原需求）**

| 套餐 | 价格 | 字数配额 | 使用次数 | 核心功能 |
|------|------|----------|----------|----------|
| **免费版** | ¥0 | 5,000字 | 1次 | • 基础生成 |
| **基础版** | ¥99/月 | 50,000字 | 10次 | • 免费版功能<br>• 去AI化 |
| **专业版** | ¥299/月 | 200,000字 | 50次 | • 基础版功能<br>• 高级润色<br>• 查重 |
| **旗舰版** | ¥599/月 | 无限 | 无限 | • 专业版功能<br>• 人工审核 |

**方案三：单项功能购买（灵活组合）**

除了套餐外，用户可以单独购买功能服务：

| 功能服务 | 单价 | 计费方式 | 说明 |
|---------|------|----------|------|
| **去AI化处理** | ¥0.05/千字 | 按字数计费 | 改写AI痕迹明显的句子，增加人性化表达 |
| **内容润色** | ¥0.08/千字 | 按字数计费 | 语法检查、逻辑优化、表达优化 |
| **AIGC检测预估** | ¥0.02/千字 | 按字数计费 | 预估AI生成概率，标注高风险句子 |
| **查重率预估** | ¥0.10/千字 | 按字数计费 | 与文献库对比，计算相似度 |
| **人工审核服务** | ¥50/篇 | 按篇计费 | 专业编辑审核，提供修改建议（3-5个工作日） |

**单项功能套餐包（更优惠）**:

| 套餐包 | 价格 | 包含内容 | 节省 |
|--------|------|----------|------|
| **去AI化套餐包** | ¥39 | 10万字去AI化额度 | 节省¥11（原价¥50） |
| **润色套餐包** | ¥59 | 10万字润色额度 | 节省¥21（原价¥80） |
| **检测套餐包** | ¥99 | 10万字AIGC检测 + 5万字查重 | 节省¥26（原价¥125） |
| **全能套餐包** | ¥199 | 5万字全功能（去AI化+润色+检测+查重） | 节省¥56（原价¥255） |

**组合购买优势**:
- 用户可以只购买基础套餐（字数配额），然后按需购买功能服务
- 适合偶尔使用高级功能的用户
- 更灵活的定价策略

**功能详细说明**:

1. **基础论文生成**
   - AI大纲生成（通义千问）
   - 按章节内容生成
   - 基础格式应用
   - Word文档导出

2. **去AI化处理**
   - 识别AI痕迹明显的句子
   - 改写句式结构
   - 增加人性化表达
   - 添加过渡词和连接词

3. **内容润色**
   - 语法检查和修正
   - 逻辑优化
   - 表达优化
   - 学术用语规范化

4. **AIGC检测预估**
   - 预估内容的AI生成概率
   - 标注高风险句子
   - 提供优化建议

5. **查重率预估**
   - 与已有文献对比
   - 计算相似度
   - 标注重复内容

6. **人工审核服务**
   - 专业编辑审核
   - 格式规范检查
   - 内容质量评估
   - 修改建议

**数据模型**:
```python
@dataclass
class MemberPackage:
    """会员套餐"""
    package_id: str
    name: str  # 套餐名称（可自定义）
    description: str  # 套餐描述
    price: Decimal
    duration_days: int  # 套餐时长（天）
    
    # 基础配额
    word_quota: int  # 字数配额（-1表示无限）
    usage_quota: int  # 使用次数（-1表示无限）
    
    # 功能权限（灵活配置）
    features: Dict[str, Any]  # 功能配置字典
    # 示例：
    # {
    #     'basic_generation': True,
    #     'de_ai': {'enabled': True, 'quota': 50000},  # 5万字去AI化配额
    #     'polish': {'enabled': True, 'quota': 30000},  # 3万字润色配额
    #     'aigc_detection': {'enabled': True, 'quota': -1},  # 无限AIGC检测
    #     'plagiarism_check': {'enabled': False},  # 不包含查重
    #     'manual_review': {'enabled': True, 'count': 2},  # 2次人工审核
    #     'advanced_ai': False,  # 不使用高级AI模型
    #     'version_limit': 10,  # 最多10个版本
    #     'priority_support': False  # 无优先支持
    # }
    
    # 显示设置
    is_recommended: bool  # 是否推荐
    badge: str  # 徽章文字（如"最受欢迎"、"性价比之选"）
    sort_order: int  # 排序
    
    # 状态
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class PackageFeatureConfig:
    """套餐功能配置（用于管理后台）"""
    feature_key: str  # 功能标识
    feature_name: str  # 功能名称
    feature_type: str  # boolean/quota/count  # 功能类型
    default_value: Any  # 默认值
    description: str  # 功能描述
    
    # 配额类型特有
    quota_unit: Optional[str]  # words/times  # 配额单位
    
    # 显示设置
    display_order: int
    is_visible: bool  # 是否在前端显示

# 预定义的功能配置
FEATURE_CONFIGS = [
    PackageFeatureConfig(
        feature_key='basic_generation',
        feature_name='基础论文生成',
        feature_type='boolean',
        default_value=True,
        description='AI大纲和内容生成',
        display_order=1,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='de_ai',
        feature_name='去AI化处理',
        feature_type='quota',
        default_value={'enabled': False, 'quota': 0},
        description='改写AI痕迹，增加人性化表达',
        quota_unit='words',
        display_order=2,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='polish',
        feature_name='内容润色',
        feature_type='quota',
        default_value={'enabled': False, 'quota': 0},
        description='语法检查、逻辑优化',
        quota_unit='words',
        display_order=3,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='aigc_detection',
        feature_name='AIGC检测预估',
        feature_type='quota',
        default_value={'enabled': False, 'quota': 0},
        description='预估AI生成概率',
        quota_unit='words',
        display_order=4,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='plagiarism_check',
        feature_name='查重率预估',
        feature_type='quota',
        default_value={'enabled': False, 'quota': 0},
        description='与文献库对比相似度',
        quota_unit='words',
        display_order=5,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='manual_review',
        feature_name='人工审核服务',
        feature_type='count',
        default_value={'enabled': False, 'count': 0},
        description='专业编辑审核',
        quota_unit='times',
        display_order=6,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='advanced_ai',
        feature_name='高级AI模型',
        feature_type='boolean',
        default_value=False,
        description='使用GPT-4等高级模型',
        display_order=7,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='version_limit',
        feature_name='版本历史数量',
        feature_type='count',
        default_value=5,
        description='可保存的历史版本数量',
        quota_unit='versions',
        display_order=8,
        is_visible=True
    ),
    PackageFeatureConfig(
        feature_key='priority_support',
        feature_name='优先客服支持',
        feature_type='boolean',
        default_value=False,
        description='优先响应客服请求',
        display_order=9,
        is_visible=False
    )
]

@dataclass
class FeatureService:
    """单项功能服务"""
    service_id: str
    name: str  # 去AI化/内容润色/AIGC检测/查重/人工审核
    service_type: str  # de_ai/polish/aigc_detection/plagiarism_check/manual_review
    
    # 定价
    price: Decimal
    billing_unit: str  # per_word/per_thousand_words/per_paper
    
    # 状态
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class UserFeatureQuota:
    """用户功能配额"""
    quota_id: str
    user_id: str
    service_type: str  # de_ai/polish/aigc_detection/plagiarism_check
    
    # 配额（按字数）
    total_quota: int  # 总配额（字数）
    used_quota: int   # 已使用（字数）
    remaining_quota: int  # 剩余（字数）
    
    # 有效期
    start_date: datetime
    end_date: datetime
    
    # 来源
    source: str  # package/purchase  # 来自套餐还是单独购买
    
    # 状态
    is_active: bool
```

**套餐配置灵活性说明**:

1. **管理后台可以自由创建套餐**
   - 自定义套餐名称、价格、时长
   - 灵活配置每个功能的开启/关闭
   - 为每个功能设置独立的配额

2. **功能配置类型**
   - Boolean类型：简单的开启/关闭（如高级AI模型）
   - Quota类型：带配额的功能（如去AI化5万字）
   - Count类型：按次数的功能（如人工审核2次）

3. **配置示例**
   ```python
   # 示例1：学生基础套餐
   {
       'name': '学生基础套餐',
       'price': 49,
       'word_quota': 30000,
       'features': {
           'basic_generation': True,
           'de_ai': {'enabled': True, 'quota': 10000},
           'polish': {'enabled': False},
           'aigc_detection': {'enabled': True, 'quota': 30000},
           'version_limit': 5
       }
   }
   
   # 示例2：毕业论文专属套餐
   {
       'name': '毕业论文专属',
       'price': 399,
       'word_quota': 100000,
       'features': {
           'basic_generation': True,
           'de_ai': {'enabled': True, 'quota': 100000},
           'polish': {'enabled': True, 'quota': 50000},
           'aigc_detection': {'enabled': True, 'quota': -1},  # 无限
           'plagiarism_check': {'enabled': True, 'quota': 100000},
           'manual_review': {'enabled': True, 'count': 1},
           'version_limit': 20
       }
   }
   ```

4. **前端展示**
   - 套餐对比表自动根据配置生成
   - 显示每个功能的配额或开启状态
   - 支持推荐标签和徽章

**功能权限标识**:
- `basic_generation`: 基础论文生成
- `de_ai`: 去AI化处理
- `polish`: 内容润色
- `aigc_detection`: AIGC检测预估
- `plagiarism_check`: 查重率预估
- `manual_review`: 人工审核服务
- `advanced_ai`: 高级AI模型（GPT-4）
- `unlimited_versions`: 无限版本历史
- `priority_support`: 优先客服支持


#### 3.2.2 配额管理

**数据模型**:
```python
@dataclass
class UserQuota:
    """用户配额"""
    user_id: str
    package_id: str
    
    # 配额信息
    total_word_quota: int
    used_word_quota: int
    remaining_word_quota: int
    
    total_usage_quota: int
    used_usage_quota: int
    remaining_usage_quota: int
    
    # 有效期
    start_date: datetime
    end_date: datetime
    
    # 状态
    is_active: bool
```

**配额服务**:
```python
class MemberService:
    async def check_quota(self, user_id: str, word_count: int) -> QuotaCheckResult:
        """检查用户配额是否充足"""
        pass
    
    async def deduct_quota(self, user_id: str, word_count: int) -> bool:
        """扣减配额"""
        pass
    
    async def get_user_quota(self, user_id: str) -> UserQuota:
        """获取用户配额信息"""
        pass
    
    async def upgrade_membership(self, user_id: str, package_id: str) -> bool:
        """升级会员"""
        pass
    
    async def check_feature_access(self, user_id: str, feature: str) -> bool:
        """检查功能访问权限"""
        pass
```

#### 3.2.3 权限中间件

**实现**:
```python
class MemberMiddleware:
    """会员权限验证中间件"""
    
    async def __call__(self, request: Request, call_next):
        # 获取用户信息
        user_id = request.state.user_id
        
        # 获取请求的功能
        feature = self._extract_feature(request)
        
        # 检查权限
        if not await self.member_service.check_feature_access(user_id, feature):
            raise HTTPException(
                status_code=403,
                detail="该功能需要升级会员"
            )
        
        return await call_next(request)
```

---

### 3.3 论文创作流程

#### 3.3.1 论文数据模型

```python
@dataclass
class Thesis:
    """论文实体"""
    thesis_id: str
    user_id: str
    template_id: str
    
    # 基本信息
    title: str
    major: str
    degree_level: str
    research_direction: str
    keywords: List[str]
    thesis_type: str  # 理论研究/实证研究/综述
    
    # 状态
    status: str  # draft/generating/completed/exported
    
    # 内容
    outline: ThesisOutline
    chapters: List[Chapter]
    
    # 统计
    total_words: int
    
    # 时间
    created_at: datetime
    updated_at: datetime
    last_generated_at: datetime

@dataclass
class ThesisOutline:
    """论文大纲"""
    outline_id: str
    thesis_id: str
    structure_type: str  # 三段式/五段式
    chapters: List[OutlineChapter]

@dataclass
class OutlineChapter:
    """大纲章节"""
    chapter_id: str
    title: str
    level: int  # 1-6
    order: int
    parent_id: Optional[str]
    description: str  # 章节描述

@dataclass
class Chapter:
    """论文章节"""
    chapter_id: str
    thesis_id: str
    outline_chapter_id: str
    
    title: str
    level: int
    order: int
    
    # 内容
    content: str  # 富文本内容
    word_count: int
    
    # 状态
    status: str  # pending/generating/completed/edited
    
    # AI生成信息
    generation_prompt: str
    generation_model: str
    
    # 时间
    created_at: datetime
    updated_at: datetime
```


#### 3.3.2 论文服务 (ThesisService)

```python
class ThesisService:
    async def create_thesis(self, user_id: str, thesis_info: ThesisCreateRequest) -> Thesis:
        """创建论文"""
        # 1. 验证用户配额
        # 2. 创建论文记录
        # 3. 保存为草稿
        pass
    
    async def generate_outline(self, thesis_id: str) -> ThesisOutline:
        """生成论文大纲"""
        # 1. 获取论文基本信息
        # 2. 调用AI服务生成大纲
        # 3. 保存大纲
        pass
    
    async def update_outline(self, thesis_id: str, outline: ThesisOutline) -> ThesisOutline:
        """更新大纲"""
        pass
    
    async def generate_chapter(self, thesis_id: str, chapter_id: str) -> Chapter:
        """生成章节内容"""
        # 1. 检查配额
        # 2. 获取上下文（大纲、已生成章节）
        # 3. 调用AI服务生成内容
        # 4. 扣减配额
        # 5. 保存章节
        pass
    
    async def regenerate_chapter(self, thesis_id: str, chapter_id: str) -> Chapter:
        """重新生成章节"""
        pass
    
    async def update_chapter(self, chapter_id: str, content: str) -> Chapter:
        """更新章节内容（用户编辑）"""
        pass
    
    async def get_thesis(self, thesis_id: str) -> Thesis:
        """获取论文详情"""
        pass
    
    async def list_user_theses(self, user_id: str, filters: ThesisFilter) -> List[Thesis]:
        """获取用户论文列表"""
        pass
    
    async def delete_thesis(self, thesis_id: str) -> bool:
        """删除论文（软删除）"""
        pass
```

---

### 3.4 AI服务

#### 3.4.1 AI服务接口

```python
class AIService:
    """AI服务统一接口"""
    
    def __init__(self):
        self.models = {
            'qwen': QwenModel(),      # 通义千问
            'gpt4': GPT4Model(),      # GPT-4
            'local': LocalModel()     # 本地模型
        }
    
    async def generate_outline(
        self, 
        title: str, 
        keywords: List[str], 
        thesis_type: str,
        structure_type: str
    ) -> ThesisOutline:
        """生成论文大纲"""
        prompt = self._build_outline_prompt(title, keywords, thesis_type, structure_type)
        response = await self.models['qwen'].generate(prompt)
        return self._parse_outline_response(response)
    
    async def generate_chapter_content(
        self,
        chapter_title: str,
        chapter_description: str,
        context: GenerationContext
    ) -> str:
        """生成章节内容"""
        prompt = self._build_chapter_prompt(chapter_title, chapter_description, context)
        response = await self.models['qwen'].generate(prompt)
        return response
    
    async def optimize_content(
        self,
        content: str,
        optimization_type: str  # de_ai/plagiarism_reduction/polish
    ) -> str:
        """优化内容"""
        if optimization_type == 'de_ai':
            return await self._de_ai_process(content)
        elif optimization_type == 'plagiarism_reduction':
            return await self._reduce_plagiarism(content)
        elif optimization_type == 'polish':
            return await self._polish_content(content)
    
    async def _de_ai_process(self, content: str) -> str:
        """去AI化处理"""
        # 1. 识别AI痕迹明显的句子
        # 2. 改写句式
        # 3. 增加人性化表达
        # 4. 添加过渡词
        pass
    
    async def _reduce_plagiarism(self, content: str) -> str:
        """降重处理"""
        # 1. 同义词替换
        # 2. 句式转换
        # 3. 段落重组
        pass
    
    async def _polish_content(self, content: str) -> str:
        """内容润色"""
        # 1. 语法检查
        # 2. 逻辑优化
        # 3. 表达优化
        pass
    
    async def estimate_aigc_rate(self, content: str) -> float:
        """预估AIGC检测率"""
        # 调用AIGC检测模型
        pass
```


#### 3.4.2 生成上下文

```python
@dataclass
class GenerationContext:
    """内容生成上下文"""
    thesis_title: str
    keywords: List[str]
    thesis_type: str
    
    # 大纲信息
    outline: ThesisOutline
    
    # 已生成的章节（用于保持连贯性）
    previous_chapters: List[Chapter]
    
    # 参考文献
    references: List[Reference]
    
    # 用户偏好
    writing_style: str  # 学术/通俗
    detail_level: str   # 简洁/详细
```

#### 3.4.3 Prompt模板

**大纲生成Prompt**:
```python
OUTLINE_PROMPT_TEMPLATE = """
你是一位专业的学术论文写作助手。请根据以下信息生成论文大纲：

论文标题：{title}
关键词：{keywords}
论文类型：{thesis_type}
大纲结构：{structure_type}

要求：
1. 大纲应包含：摘要、引言、文献综述、研究方法、结果与分析、结论、参考文献
2. 每个章节应有清晰的标题和简要描述
3. 章节之间应有逻辑关联
4. 符合学术论文规范

请以JSON格式输出大纲结构。
"""

CHAPTER_PROMPT_TEMPLATE = """
你是一位专业的学术论文写作助手。请根据以下信息生成章节内容：

论文标题：{thesis_title}
关键词：{keywords}
当前章节：{chapter_title}
章节描述：{chapter_description}

上下文信息：
{context}

要求：
1. 内容应学术严谨、逻辑清晰
2. 适当引用文献
3. 字数约{target_words}字
4. 使用专业术语
5. 保持与前文的连贯性

请生成章节内容。
"""
```

---

### 3.5 格式应用服务

#### 3.5.1 格式化器 (DocxFormatter)

```python
class DocxFormatter:
    """Word文档格式化器"""
    
    def __init__(self, template: TemplateFormat):
        self.template = template
    
    def format_thesis(self, thesis: Thesis) -> Document:
        """格式化论文为Word文档"""
        doc = Document()
        
        # 1. 应用页面设置
        self._apply_page_settings(doc)
        
        # 2. 添加封面
        self._add_cover_page(doc, thesis)
        
        # 3. 添加目录
        self._add_table_of_contents(doc)
        
        # 4. 添加摘要
        self._add_abstract(doc, thesis)
        
        # 5. 添加章节内容
        for chapter in thesis.chapters:
            self._add_chapter(doc, chapter)
        
        # 6. 添加参考文献
        self._add_references(doc, thesis)
        
        # 7. 应用页眉页脚
        self._apply_header_footer(doc)
        
        return doc
    
    def _apply_page_settings(self, doc: Document):
        """应用页面设置"""
        section = doc.sections[0]
        section.page_width = self.template.page_size.width
        section.page_height = self.template.page_size.height
        section.left_margin = self.template.page_margins.left
        section.right_margin = self.template.page_margins.right
        section.top_margin = self.template.page_margins.top
        section.bottom_margin = self.template.page_margins.bottom
    
    def _add_chapter(self, doc: Document, chapter: Chapter):
        """添加章节"""
        # 添加标题
        heading = doc.add_heading(chapter.title, level=chapter.level)
        self._apply_style(heading, f'Heading {chapter.level}')
        
        # 添加内容
        paragraphs = chapter.content.split('\n\n')
        for para_text in paragraphs:
            para = doc.add_paragraph(para_text)
            self._apply_style(para, 'Normal')
    
    def _apply_style(self, element, style_name: str):
        """应用样式"""
        style_info = self.template.styles.get(style_name)
        if style_info:
            # 应用字体、字号、行距等
            pass
```


---

### 3.6 支付系统

#### 3.6.1 支付服务 (PaymentService)

```python
class PaymentService:
    """支付服务"""
    
    def __init__(self):
        self.wechat_pay = WeChatPayClient()
        self.alipay = AlipayClient()
    
    async def create_order(
        self,
        user_id: str,
        package_id: str,
        payment_method: str  # wechat/alipay
    ) -> Order:
        """创建订单"""
        # 1. 获取套餐信息
        package = await self.member_service.get_package(package_id)
        
        # 2. 创建订单记录
        order = Order(
            order_id=self._generate_order_id(),
            user_id=user_id,
            package_id=package_id,
            amount=package.price,
            status='pending',
            payment_method=payment_method
        )
        await self.order_dao.create(order)
        
        # 3. 调用支付接口
        if payment_method == 'wechat':
            payment_info = await self._create_wechat_payment(order)
        else:
            payment_info = await self._create_alipay_payment(order)
        
        return order, payment_info
    
    async def _create_wechat_payment(self, order: Order) -> WeChatPaymentInfo:
        """创建微信支付"""
        result = await self.wechat_pay.create_native_pay(
            out_trade_no=order.order_id,
            description=f"会员套餐-{order.package_id}",
            amount=int(order.amount * 100),  # 转换为分
            notify_url=settings.WECHAT_NOTIFY_URL
        )
        return WeChatPaymentInfo(
            code_url=result['code_url'],
            order_id=order.order_id
        )
    
    async def handle_wechat_callback(self, callback_data: dict) -> bool:
        """处理微信支付回调"""
        # 1. 验证签名
        if not self.wechat_pay.verify_signature(callback_data):
            return False
        
        # 2. 更新订单状态
        order_id = callback_data['out_trade_no']
        await self.order_dao.update_status(order_id, 'paid')
        
        # 3. 开通会员
        order = await self.order_dao.get(order_id)
        await self.member_service.activate_membership(order.user_id, order.package_id)
        
        return True
    
    async def query_order_status(self, order_id: str) -> str:
        """查询订单状态"""
        order = await self.order_dao.get(order_id)
        
        # 如果订单状态为pending，主动查询支付状态
        if order.status == 'pending':
            if order.payment_method == 'wechat':
                result = await self.wechat_pay.query_order(order_id)
                if result['trade_state'] == 'SUCCESS':
                    await self.handle_payment_success(order_id)
        
        return order.status
    
    async def refund_order(self, order_id: str, reason: str) -> bool:
        """退款"""
        order = await self.order_dao.get(order_id)
        
        if order.payment_method == 'wechat':
            result = await self.wechat_pay.refund(
                out_trade_no=order_id,
                out_refund_no=self._generate_refund_id(),
                amount=int(order.amount * 100),
                reason=reason
            )
        else:
            result = await self.alipay.refund(
                out_trade_no=order_id,
                refund_amount=float(order.amount),
                refund_reason=reason
            )
        
        if result['success']:
            await self.order_dao.update_status(order_id, 'refunded')
            await self.member_service.deactivate_membership(order.user_id)
            return True
        
        return False
```

#### 3.6.2 订单数据模型

```python
@dataclass
class Order:
    """订单"""
    order_id: str
    user_id: str
    package_id: str
    
    # 金额
    amount: Decimal
    
    # 支付信息
    payment_method: str  # wechat/alipay
    payment_time: Optional[datetime]
    transaction_id: Optional[str]  # 第三方交易号
    
    # 状态
    status: str  # pending/paid/refunded/cancelled
    
    # 时间
    created_at: datetime
    updated_at: datetime
    expired_at: datetime  # 订单过期时间（30分钟）
```


---

### 3.7 历史记录管理

#### 3.7.1 版本控制

```python
@dataclass
class ThesisVersion:
    """论文版本"""
    version_id: str
    thesis_id: str
    version_number: int
    
    # 快照数据
    snapshot: dict  # 完整的论文数据快照
    
    # 变更信息
    change_description: str
    changed_by: str
    
    # 时间
    created_at: datetime

class VersionService:
    """版本管理服务"""
    
    async def create_version(self, thesis_id: str, description: str) -> ThesisVersion:
        """创建版本快照"""
        thesis = await self.thesis_dao.get(thesis_id)
        
        version = ThesisVersion(
            version_id=self._generate_version_id(),
            thesis_id=thesis_id,
            version_number=await self._get_next_version_number(thesis_id),
            snapshot=thesis.to_dict(),
            change_description=description,
            changed_by=thesis.user_id,
            created_at=datetime.now()
        )
        
        await self.version_dao.create(version)
        return version
    
    async def restore_version(self, thesis_id: str, version_id: str) -> Thesis:
        """恢复到指定版本"""
        version = await self.version_dao.get(version_id)
        thesis = Thesis.from_dict(version.snapshot)
        
        # 创建新版本（恢复操作也记录为版本）
        await self.create_version(thesis_id, f"恢复到版本{version.version_number}")
        
        # 更新当前论文
        await self.thesis_dao.update(thesis)
        return thesis
    
    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> VersionDiff:
        """对比两个版本"""
        v1 = await self.version_dao.get(version_id_1)
        v2 = await self.version_dao.get(version_id_2)
        
        return self._compute_diff(v1.snapshot, v2.snapshot)
```

#### 3.7.2 自动保存

```python
class AutoSaveService:
    """自动保存服务"""
    
    def __init__(self):
        self.save_interval = 30  # 30秒
        self.pending_saves = {}  # {thesis_id: pending_data}
    
    async def schedule_save(self, thesis_id: str, data: dict):
        """调度保存"""
        self.pending_saves[thesis_id] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def flush_pending_saves(self):
        """执行待保存的数据"""
        for thesis_id, save_info in self.pending_saves.items():
            await self.thesis_dao.update(thesis_id, save_info['data'])
        
        self.pending_saves.clear()
    
    async def start_auto_save_loop(self):
        """启动自动保存循环"""
        while True:
            await asyncio.sleep(self.save_interval)
            await self.flush_pending_saves()
```

---

## 4. 数据模型

### 4.1 数据库表设计

#### 4.1.1 thesis_template (格式模板表)

```sql
CREATE TABLE thesis_template (
    template_id VARCHAR(32) PRIMARY KEY,
    school_name VARCHAR(100) NOT NULL,
    major VARCHAR(100),
    degree_level VARCHAR(20) NOT NULL,  -- 本科/硕士/博士
    
    -- 格式数据（JSON）
    format_data JSON NOT NULL,
    
    -- 状态
    is_active TINYINT(1) DEFAULT 1,
    is_deleted TINYINT(1) DEFAULT 0,
    
    -- 统计
    usage_count INT DEFAULT 0,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    created_by VARCHAR(32),
    
    INDEX idx_school (school_name),
    INDEX idx_degree (degree_level),
    INDEX idx_active (is_active, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.2 thesis_paper (论文表)

```sql
CREATE TABLE thesis_paper (
    thesis_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    template_id VARCHAR(32),
    
    -- 基本信息
    title VARCHAR(200) NOT NULL,
    major VARCHAR(100),
    degree_level VARCHAR(20),
    research_direction VARCHAR(100),
    keywords JSON,  -- 数组
    thesis_type VARCHAR(50),
    
    -- 状态
    status VARCHAR(20) NOT NULL,  -- draft/generating/completed/exported
    
    -- 统计
    total_words INT DEFAULT 0,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_generated_at DATETIME,
    
    -- 软删除
    is_deleted TINYINT(1) DEFAULT 0,
    
    INDEX idx_user (user_id, is_deleted),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (template_id) REFERENCES thesis_template(template_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```


#### 4.1.3 thesis_outline (大纲表)

```sql
CREATE TABLE thesis_outline (
    outline_id VARCHAR(32) PRIMARY KEY,
    thesis_id VARCHAR(32) NOT NULL,
    structure_type VARCHAR(20),  -- 三段式/五段式
    
    -- 大纲数据（JSON）
    outline_data JSON NOT NULL,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (thesis_id) REFERENCES thesis_paper(thesis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.4 thesis_chapter (章节表)

```sql
CREATE TABLE thesis_chapter (
    chapter_id VARCHAR(32) PRIMARY KEY,
    thesis_id VARCHAR(32) NOT NULL,
    outline_chapter_id VARCHAR(32),
    
    -- 章节信息
    title VARCHAR(200) NOT NULL,
    level INT NOT NULL,  -- 1-6
    order_num INT NOT NULL,
    
    -- 内容
    content LONGTEXT,
    word_count INT DEFAULT 0,
    
    -- 状态
    status VARCHAR(20) NOT NULL,  -- pending/generating/completed/edited
    
    -- AI生成信息
    generation_prompt TEXT,
    generation_model VARCHAR(50),
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    INDEX idx_thesis (thesis_id, order_num),
    FOREIGN KEY (thesis_id) REFERENCES thesis_paper(thesis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.5 member_package (会员套餐表)

```sql
CREATE TABLE member_package (
    package_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    price DECIMAL(10, 2) NOT NULL,
    duration_days INT NOT NULL,
    
    -- 基础配额
    word_quota INT NOT NULL,  -- -1表示无限
    usage_quota INT NOT NULL,  -- -1表示无限
    
    -- 功能权限（JSON格式，灵活配置）
    features JSON NOT NULL,
    -- 示例：
    -- {
    --   "basic_generation": true,
    --   "de_ai": {"enabled": true, "quota": 50000},
    --   "polish": {"enabled": true, "quota": 30000},
    --   "aigc_detection": {"enabled": true, "quota": -1},
    --   "plagiarism_check": {"enabled": false},
    --   "manual_review": {"enabled": true, "count": 2},
    --   "advanced_ai": false,
    --   "version_limit": 10,
    --   "priority_support": false
    -- }
    
    -- 显示设置
    is_recommended TINYINT(1) DEFAULT 0,
    badge VARCHAR(20),  -- 徽章文字
    sort_order INT DEFAULT 0,
    
    -- 状态
    is_active TINYINT(1) DEFAULT 1,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    INDEX idx_active (is_active, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.6 user_membership (用户会员表)

```sql
CREATE TABLE user_membership (
    membership_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    package_id VARCHAR(32) NOT NULL,
    
    -- 配额
    total_word_quota INT NOT NULL,
    used_word_quota INT DEFAULT 0,
    
    total_usage_quota INT NOT NULL,
    used_usage_quota INT DEFAULT 0,
    
    -- 有效期
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    
    -- 状态
    is_active TINYINT(1) DEFAULT 1,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    INDEX idx_user (user_id, is_active),
    INDEX idx_expire (end_date, is_active),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (package_id) REFERENCES member_package(package_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.7 member_order (订单表)

```sql
CREATE TABLE member_order (
    order_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    package_id VARCHAR(32) NOT NULL,
    
    -- 金额
    amount DECIMAL(10, 2) NOT NULL,
    
    -- 支付信息
    payment_method VARCHAR(20) NOT NULL,  -- wechat/alipay
    payment_time DATETIME,
    transaction_id VARCHAR(64),  -- 第三方交易号
    
    -- 状态
    status VARCHAR(20) NOT NULL,  -- pending/paid/refunded/cancelled
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    expired_at DATETIME NOT NULL,
    
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_expire (expired_at, status),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (package_id) REFERENCES member_package(package_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.8 quota_record (配额记录表)

```sql
CREATE TABLE quota_record (
    record_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    thesis_id VARCHAR(32),
    
    -- 配额变动
    word_count INT NOT NULL,  -- 正数为扣减，负数为退还
    usage_count INT NOT NULL,
    
    -- 操作类型
    operation_type VARCHAR(20) NOT NULL,  -- generate/refund
    
    -- 时间
    created_at DATETIME NOT NULL,
    
    INDEX idx_user (user_id, created_at),
    INDEX idx_thesis (thesis_id),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.9 feature_service (功能服务表)

```sql
CREATE TABLE feature_service (
    service_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    service_type VARCHAR(30) NOT NULL,  -- de_ai/polish/aigc_detection/plagiarism_check/manual_review
    
    -- 定价
    price DECIMAL(10, 2) NOT NULL,
    billing_unit VARCHAR(20) NOT NULL,  -- per_word/per_thousand_words/per_paper
    
    -- 描述
    description TEXT,
    
    -- 状态
    is_active TINYINT(1) DEFAULT 1,
    
    -- 排序
    sort_order INT DEFAULT 0,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    INDEX idx_type (service_type),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.10 user_feature_quota (用户功能配额表)

```sql
CREATE TABLE user_feature_quota (
    quota_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    service_type VARCHAR(30) NOT NULL,
    
    -- 配额（按字数）
    total_quota INT NOT NULL,
    used_quota INT DEFAULT 0,
    
    -- 有效期
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    
    -- 来源
    source VARCHAR(20) NOT NULL,  -- package/purchase
    source_id VARCHAR(32),  -- 套餐ID或订单ID
    
    -- 状态
    is_active TINYINT(1) DEFAULT 1,
    
    -- 时间
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    INDEX idx_user (user_id, service_type, is_active),
    INDEX idx_expire (end_date, is_active),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```


#### 4.1.11 thesis_version (版本历史表)

```sql
CREATE TABLE thesis_version (
    version_id VARCHAR(32) PRIMARY KEY,
    thesis_id VARCHAR(32) NOT NULL,
    version_number INT NOT NULL,
    
    -- 快照数据（JSON）
    snapshot_data JSON NOT NULL,
    
    -- 变更信息
    change_description VARCHAR(200),
    changed_by VARCHAR(32),
    
    -- 时间
    created_at DATETIME NOT NULL,
    
    INDEX idx_thesis (thesis_id, version_number),
    FOREIGN KEY (thesis_id) REFERENCES thesis_paper(thesis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4.1.12 export_record (导出记录表)

```sql
CREATE TABLE export_record (
    record_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    thesis_id VARCHAR(32) NOT NULL,
    
    -- 文件信息
    file_name VARCHAR(200) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    
    -- 时间
    created_at DATETIME NOT NULL,
    
    -- 软删除
    is_deleted TINYINT(1) DEFAULT 0,
    
    INDEX idx_user (user_id, is_deleted),
    INDEX idx_thesis (thesis_id),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (thesis_id) REFERENCES thesis_paper(thesis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 5. API接口设计

### 5.1 模板管理接口

```python
# 上传模板
POST /api/thesis/template/upload
Request:
- file: UploadFile
- school_name: str
- major: str
- degree_level: str

Response:
{
    "code": 200,
    "msg": "success",
    "data": {
        "template_id": "xxx",
        "format_data": {...}
    }
}

# 获取模板列表
GET /api/thesis/template/list
Query:
- school_name: str (optional)
- degree_level: str (optional)
- page: int
- page_size: int

Response:
{
    "code": 200,
    "data": {
        "total": 100,
        "items": [...]
    }
}

# 获取模板详情
GET /api/thesis/template/{template_id}

# 更新模板
PUT /api/thesis/template/{template_id}

# 删除模板
DELETE /api/thesis/template/{template_id}
```

### 5.2 论文管理接口

```python
# 创建论文
POST /api/thesis/paper/create
Request:
{
    "template_id": "xxx",
    "title": "论文标题",
    "major": "计算机科学",
    "degree_level": "硕士",
    "research_direction": "人工智能",
    "keywords": ["AI", "机器学习"],
    "thesis_type": "理论研究"
}

# 生成大纲
POST /api/thesis/paper/{thesis_id}/outline/generate
Request:
{
    "structure_type": "五段式"
}

# 更新大纲
PUT /api/thesis/paper/{thesis_id}/outline
Request:
{
    "outline_data": {...}
}

# 生成章节内容
POST /api/thesis/paper/{thesis_id}/chapter/{chapter_id}/generate

# 重新生成章节
POST /api/thesis/paper/{thesis_id}/chapter/{chapter_id}/regenerate

# 更新章节内容
PUT /api/thesis/paper/{thesis_id}/chapter/{chapter_id}
Request:
{
    "content": "章节内容"
}

# 获取论文详情
GET /api/thesis/paper/{thesis_id}

# 获取用户论文列表
GET /api/thesis/paper/list
Query:
- status: str (optional)
- page: int
- page_size: int

# 删除论文
DELETE /api/thesis/paper/{thesis_id}
```

### 5.3 AI优化接口

```python
# 去AI化处理
POST /api/thesis/ai/de-ai
Request:
{
    "content": "原始内容"
}

Response:
{
    "code": 200,
    "data": {
        "optimized_content": "优化后的内容",
        "changes": [...]
    }
}

# 降重处理
POST /api/thesis/ai/reduce-plagiarism
Request:
{
    "content": "原始内容"
}

# 内容润色
POST /api/thesis/ai/polish
Request:
{
    "content": "原始内容"
}

# AIGC检测率预估
POST /api/thesis/ai/estimate-aigc
Request:
{
    "content": "内容"
}

Response:
{
    "code": 200,
    "data": {
        "aigc_rate": 0.35,  # 35%
        "confidence": 0.85
    }
}
```


### 5.4 会员管理接口

```python
# 获取套餐列表
GET /api/thesis/member/packages

Response:
{
    "code": 200,
    "data": [
        {
            "package_id": "free",
            "name": "免费版",
            "price": 0,
            "word_quota": 5000,
            "usage_quota": 1,
            "features": ["basic_generation"]
        },
        ...
    ]
}

# 获取用户配额
GET /api/thesis/member/quota

Response:
{
    "code": 200,
    "data": {
        "package_name": "专业版",
        "total_word_quota": 200000,
        "used_word_quota": 50000,
        "remaining_word_quota": 150000,
        "total_usage_quota": 50,
        "used_usage_quota": 10,
        "remaining_usage_quota": 40,
        "end_date": "2024-12-31 23:59:59"
    }
}

# 检查功能权限
GET /api/thesis/member/check-feature
Query:
- feature: str

Response:
{
    "code": 200,
    "data": {
        "has_access": true
    }
}
```

### 5.5 支付接口

```python
# 创建订单
POST /api/thesis/payment/order/create
Request:
{
    "package_id": "pro",
    "payment_method": "wechat"
}

Response:
{
    "code": 200,
    "data": {
        "order_id": "xxx",
        "code_url": "weixin://...",  # 微信支付二维码URL
        "amount": 299.00,
        "expired_at": "2024-01-01 12:30:00"
    }
}

# 查询订单状态
GET /api/thesis/payment/order/{order_id}/status

Response:
{
    "code": 200,
    "data": {
        "status": "paid",
        "payment_time": "2024-01-01 12:15:30"
    }
}

# 微信支付回调
POST /api/thesis/payment/wechat/callback
(由微信服务器调用)

# 支付宝支付回调
POST /api/thesis/payment/alipay/callback
(由支付宝服务器调用)

# 申请退款
POST /api/thesis/payment/order/{order_id}/refund
Request:
{
    "reason": "退款原因"
}

# 获取订单列表
GET /api/thesis/payment/order/list
Query:
- status: str (optional)
- page: int
- page_size: int
```

### 5.6 导出接口

```python
# 导出论文
POST /api/thesis/paper/{thesis_id}/export

Response:
{
    "code": 200,
    "data": {
        "file_url": "https://...",
        "file_name": "论文标题.docx",
        "file_size": 1024000
    }
}

# 获取导出记录
GET /api/thesis/export/list
Query:
- page: int
- page_size: int

# 重新下载
GET /api/thesis/export/{record_id}/download
```

### 5.7 版本管理接口

```python
# 创建版本
POST /api/thesis/paper/{thesis_id}/version/create
Request:
{
    "description": "版本描述"
}

# 获取版本列表
GET /api/thesis/paper/{thesis_id}/version/list

# 恢复版本
POST /api/thesis/paper/{thesis_id}/version/{version_id}/restore

# 对比版本
GET /api/thesis/paper/{thesis_id}/version/compare
Query:
- version_id_1: str
- version_id_2: str
```

---

## 6. 错误处理

### 6.1 错误码定义

```python
class ThesisErrorCode:
    # 配额相关
    QUOTA_INSUFFICIENT = 40001  # 配额不足
    QUOTA_EXPIRED = 40002       # 配额已过期
    
    # 权限相关
    FEATURE_NOT_ALLOWED = 40301  # 功能未授权
    MEMBERSHIP_REQUIRED = 40302  # 需要会员
    
    # 模板相关
    TEMPLATE_NOT_FOUND = 40401   # 模板不存在
    TEMPLATE_PARSE_ERROR = 40402 # 模板解析失败
    
    # 论文相关
    THESIS_NOT_FOUND = 40403     # 论文不存在
    CHAPTER_GENERATING = 40404   # 章节正在生成中
    
    # 支付相关
    ORDER_NOT_FOUND = 40405      # 订单不存在
    ORDER_EXPIRED = 40406        # 订单已过期
    PAYMENT_FAILED = 40407       # 支付失败
    
    # AI服务相关
    AI_SERVICE_ERROR = 50001     # AI服务错误
    AI_QUOTA_EXCEEDED = 50002    # AI配额超限
```

### 6.2 异常处理

```python
class ThesisException(Exception):
    """论文系统异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

class QuotaInsufficientException(ThesisException):
    """配额不足异常"""
    def __init__(self):
        super().__init__(
            ThesisErrorCode.QUOTA_INSUFFICIENT,
            "配额不足，请升级会员"
        )

class FeatureNotAllowedException(ThesisException):
    """功能未授权异常"""
    def __init__(self, feature: str):
        super().__init__(
            ThesisErrorCode.FEATURE_NOT_ALLOWED,
            f"该功能需要升级会员: {feature}"
        )

# 全局异常处理器
@app.exception_handler(ThesisException)
async def thesis_exception_handler(request: Request, exc: ThesisException):
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "msg": exc.message
        }
    )
```


---

## 7. 正确性属性 (Correctness Properties)

属性是一种特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。

### 7.1 模板管理属性

**Property 1: 模板解析往返一致性**
*对于任何*有效的Word文档格式模板，解析后保存再重新加载应该产生等价的格式信息
**验证需求: 2.1.1**

**Property 2: 模板软删除不可见性**
*对于任何*被软删除的模板，它不应该出现在活动模板列表中，但应该仍然存在于数据库中
**验证需求: 2.1.2**

**Property 3: 模板筛选正确性**
*对于任何*学校/专业/学历层次筛选条件，返回的所有模板都应该匹配该筛选条件
**验证需求: 2.1.3**

**Property 4: 模板搜索包含性**
*对于任何*关键词搜索，返回的所有模板的名称或描述都应该包含该关键词
**验证需求: 2.1.3**

### 7.2 会员权益属性

**Property 5: 配额扣减一致性**
*对于任何*配额扣减操作，剩余配额应该等于总配额减去已使用配额
**验证需求: 2.2.1**

**Property 6: 使用次数递增性**
*对于任何*论文生成操作，使用次数应该增加1
**验证需求: 2.2.1**

**Property 7: 会员过期自动降级**
*对于任何*过期的会员，系统应该自动将其降级为免费版
**验证需求: 2.2.1**

**Property 8: 权限访问控制**
*对于任何*用户和功能，如果用户的会员等级不包含该功能，访问应该被拒绝
**验证需求: 2.2.2**

**Property 9: 配额不足拒绝**
*对于任何*配额不足的用户，超出配额的操作应该被拒绝并提示升级
**验证需求: 2.2.2**

### 7.3 论文创作属性

**Property 10: 论文创建信息完整性**
*对于任何*有效的论文创建请求，创建的论文应该包含所有提供的基本信息字段
**验证需求: 2.3.1**

**Property 11: 表单验证拒绝无效输入**
*对于任何*无效的论文信息（如空标题、无效关键词），创建操作应该被拒绝
**验证需求: 2.3.1**

**Property 12: 大纲结构完整性**
*对于任何*生成的论文大纲，它应该包含所有必需的章节（摘要、引言、文献综述、研究方法、结果与分析、结论、参考文献）
**验证需求: 2.3.2**

**Property 13: 大纲结构类型匹配**
*对于任何*指定的大纲结构类型（三段式/五段式），生成的大纲应该符合该结构类型
**验证需求: 2.3.2**

**Property 14: 章节生成顺序性**
*对于任何*论文，章节应该按照大纲中定义的顺序生成
**验证需求: 2.3.3**

**Property 15: 字数统计准确性**
*对于任何*章节内容，统计的字数应该等于实际内容的字数
**验证需求: 2.3.3**

**Property 16: 自动保存时效性**
*对于任何*内容编辑，修改应该在30秒内被自动保存
**验证需求: 2.3.4**

**Property 17: 版本创建记录性**
*对于任何*保存操作，应该创建一个新的版本记录
**验证需求: 2.3.4**

**Property 18: 撤销重做往返性**
*对于任何*操作，执行撤销然后重做应该返回到原始状态
**验证需求: 2.3.4**

### 7.4 AI优化属性

**Property 19: 去AI化降低检测率**
*对于任何*内容，去AI化处理后的AIGC检测率应该低于处理前
**验证需求: 2.3.5**

**Property 20: 降重降低相似度**
*对于任何*内容，降重处理后的查重率应该低于处理前
**验证需求: 2.3.5**

**Property 21: AIGC检测率范围有效性**
*对于任何*内容，AIGC检测率预估应该返回0到1之间的值
**验证需求: 2.3.5**

**Property 22: 查重率范围有效性**
*对于任何*内容，查重率预估应该返回0到1之间的值
**验证需求: 2.3.5**

### 7.5 格式应用属性

**Property 23: 格式应用一致性**
*对于任何*论文和模板，应用模板后的文档格式应该符合模板定义的所有格式规则
**验证需求: 2.3.6**

**Property 24: 标题层级格式匹配**
*对于任何*标题层级（1-6），格式化后的标题样式应该匹配模板中对应层级的样式定义
**验证需求: 2.3.6**

**Property 25: 目录包含所有章节**
*对于任何*论文，自动生成的目录应该包含所有章节标题
**验证需求: 2.3.6**

**Property 26: 图表编号连续性**
*对于任何*论文中的图表，编号应该是连续的（1, 2, 3, ...）
**验证需求: 2.3.6**

### 7.6 导出属性

**Property 27: 导出格式有效性**
*对于任何*论文，导出的文件应该是有效的.docx格式
**验证需求: 2.3.7**

**Property 28: 导出格式保留性**
*对于任何*论文，导出后重新导入应该保留所有格式信息（往返一致性）
**验证需求: 2.3.7**

**Property 29: 导出文件命名规范**
*对于任何*论文，导出的文件名应该遵循命名规则（包含论文标题）
**验证需求: 2.3.7**

**Property 30: 导出记录创建**
*对于任何*导出操作，应该创建一条导出记录
**验证需求: 2.3.7**

### 7.7 支付属性

**Property 31: 订单创建完整性**
*对于任何*套餐和支付方式，创建的订单应该包含正确的金额和支付信息
**验证需求: 2.4.1**

**Property 32: 支付成功会员激活**
*对于任何*支付成功的订单，对应用户的会员应该被自动激活
**验证需求: 2.4.1**

**Property 33: 支付回调状态同步**
*对于任何*有效的支付回调，订单状态应该被更新为已支付
**验证需求: 2.4.2**

**Property 34: 退款会员停用**
*对于任何*退款请求，订单应该被标记为已退款且用户会员应该被停用
**验证需求: 2.4.2**

### 7.8 历史记录属性

**Property 35: 草稿自动保存间隔**
*对于任何*编辑操作，内容应该在30秒内被自动保存
**验证需求: 2.5.1**

**Property 36: 草稿软删除可恢复性**
*对于任何*被软删除的草稿，它应该可以被恢复到活动状态
**验证需求: 2.5.1**

**Property 37: 草稿搜索匹配性**
*对于任何*搜索关键词，返回的所有草稿都应该包含该关键词
**验证需求: 2.5.1**

**Property 38: 版本恢复状态一致性**
*对于任何*版本，恢复后的论文状态应该与该版本的快照一致
**验证需求: 2.5.2**

**Property 39: 版本列表顺序性**
*对于任何*论文，版本列表应该按照版本号或创建时间排序
**验证需求: 2.5.2**

### 7.9 管理功能属性

**Property 40: 用户配额调整生效性**
*对于任何*管理员的配额调整操作，用户的新配额应该立即生效
**验证需求: 2.6.1**

**Property 41: 账号冻结访问限制**
*对于任何*被冻结的账号，该用户应该无法访问系统功能
**验证需求: 2.6.1**

**Property 42: 订单列表筛选正确性**
*对于任何*订单状态筛选，返回的所有订单都应该匹配该状态
**验证需求: 2.6.2**

**Property 43: 内容审核状态更新**
*对于任何*审核决定（通过/拒绝），内容的审核状态应该被更新
**验证需求: 2.6.3**

**Property 44: 系统配置即时生效**
*对于任何*系统配置更改，新配置应该立即应用到后续操作
**验证需求: 2.6.4**


---

## 8. 错误处理策略

### 8.1 错误分类

**客户端错误 (4xx)**:
- 400: 请求参数错误
- 401: 未认证
- 403: 权限不足/配额不足
- 404: 资源不存在
- 409: 资源冲突（如重复创建）
- 429: 请求过于频繁

**服务端错误 (5xx)**:
- 500: 内部服务器错误
- 502: AI服务不可用
- 503: 服务暂时不可用
- 504: 请求超时

### 8.2 错误响应格式

```python
{
    "code": 40001,
    "msg": "配额不足，请升级会员",
    "data": {
        "current_quota": 0,
        "required_quota": 5000,
        "upgrade_url": "/member/packages"
    }
}
```

### 8.3 重试策略

**AI服务调用**:
- 最大重试次数: 3次
- 重试间隔: 指数退避 (1s, 2s, 4s)
- 重试条件: 网络错误、超时、5xx错误

**支付回调**:
- 最大重试次数: 5次
- 重试间隔: 固定间隔 (30s)
- 重试条件: 回调处理失败

**数据库操作**:
- 最大重试次数: 3次
- 重试间隔: 固定间隔 (100ms)
- 重试条件: 死锁、连接超时

### 8.4 降级策略

**AI服务降级**:
- 主模型不可用时，切换到备用模型
- 所有模型不可用时，返回错误提示用户稍后重试

**支付服务降级**:
- 支付接口不可用时，显示维护提示
- 保存订单信息，待服务恢复后处理

**文件存储降级**:
- 主存储不可用时，使用备用存储
- 所有存储不可用时，暂存到本地，异步上传

### 8.5 日志记录

**关键操作日志**:
- 用户登录/登出
- 会员购买/升级
- 配额扣减
- 论文生成
- 支付回调
- 管理员操作

**错误日志**:
- 所有异常堆栈
- 请求参数
- 用户信息
- 时间戳

**性能日志**:
- API响应时间
- AI生成耗时
- 数据库查询耗时

---

## 9. 测试策略

### 9.1 测试方法

系统采用**双重测试方法**：单元测试和基于属性的测试（Property-Based Testing）相结合，确保全面的代码覆盖和正确性验证。

**单元测试**:
- 验证特定示例和边界情况
- 测试错误条件和异常处理
- 测试组件之间的集成点
- 关注具体的输入输出对

**基于属性的测试**:
- 验证跨所有输入的通用属性
- 通过随机化实现全面的输入覆盖
- 每个测试最少运行100次迭代
- 关注系统应该始终保持的不变量

两种方法是互补的：单元测试捕获具体的错误，属性测试验证通用的正确性。

### 9.2 测试框架

**后端测试**:
- 测试框架: pytest
- 属性测试库: Hypothesis
- Mock库: pytest-mock
- 覆盖率工具: pytest-cov

**前端测试**:
- 测试框架: Vitest
- 组件测试: @vue/test-utils
- E2E测试: Playwright

### 9.3 属性测试配置

每个属性测试必须:
1. 最少运行100次迭代（由于随机化）
2. 使用注释引用设计文档中的属性
3. 标签格式: `# Feature: ai-thesis-writing, Property {number}: {property_text}`

**示例**:
```python
from hypothesis import given, strategies as st
import pytest

# Feature: ai-thesis-writing, Property 5: 配额扣减一致性
@given(
    total_quota=st.integers(min_value=1000, max_value=1000000),
    deduction=st.integers(min_value=1, max_value=10000)
)
@pytest.mark.property_test
def test_quota_deduction_consistency(total_quota, deduction):
    """
    对于任何配额扣减操作，剩余配额应该等于总配额减去已使用配额
    """
    user_quota = UserQuota(
        total_word_quota=total_quota,
        used_word_quota=0
    )
    
    # 执行扣减
    user_quota.deduct(deduction)
    
    # 验证一致性
    assert user_quota.remaining_word_quota == total_quota - deduction
    assert user_quota.used_word_quota == deduction

# Feature: ai-thesis-writing, Property 28: 导出格式保留性
@given(
    thesis=st.builds(Thesis)  # 生成随机论文
)
@pytest.mark.property_test
def test_export_format_preservation(thesis):
    """
    对于任何论文，导出后重新导入应该保留所有格式信息（往返一致性）
    """
    # 导出
    docx_file = export_service.export_thesis(thesis)
    
    # 重新导入
    imported_thesis = import_service.import_thesis(docx_file)
    
    # 验证格式保留
    assert imported_thesis.format_equals(thesis)
```

### 9.4 测试覆盖目标

**代码覆盖率**:
- 总体覆盖率: > 80%
- 核心业务逻辑: > 90%
- 工具类: > 70%

**功能覆盖**:
- P0功能: 100%测试覆盖
- P1功能: > 80%测试覆盖
- P2功能: > 60%测试覆盖

### 9.5 测试类型

**单元测试**:
- Service层业务逻辑测试
- DAO层数据访问测试
- 工具类功能测试
- 中间件测试

**集成测试**:
- API接口测试
- 数据库集成测试
- 第三方服务集成测试（Mock）

**属性测试**:
- 每个正确性属性对应一个属性测试
- 使用Hypothesis生成随机测试数据
- 验证系统不变量

**E2E测试**:
- 关键用户流程测试
- 论文创建到导出完整流程
- 支付流程测试

### 9.6 测试数据管理

**测试数据库**:
- 使用独立的测试数据库
- 每次测试前重置数据
- 使用工厂模式生成测试数据

**Mock数据**:
- AI服务响应Mock
- 支付接口Mock
- 文件存储Mock

### 9.7 性能测试

**负载测试**:
- 并发用户数: 1000
- 响应时间: < 2s (95th percentile)
- 错误率: < 0.1%

**压力测试**:
- 逐步增加负载直到系统崩溃
- 确定系统瓶颈
- 验证降级策略

**AI生成性能**:
- 大纲生成: < 10s
- 章节生成: < 30s/千字
- 优化处理: < 20s/千字

---

## 10. 安全考虑

### 10.1 数据安全

**敏感数据加密**:
- 用户密码: bcrypt加密
- 支付信息: AES-256加密
- API密钥: 环境变量存储

**数据传输**:
- 全站HTTPS
- API请求签名验证
- 防重放攻击

### 10.2 访问控制

**认证**:
- JWT Token认证
- Token过期时间: 2小时
- Refresh Token: 7天

**授权**:
- 基于角色的访问控制（RBAC）
- 会员等级权限控制
- 资源所有权验证

### 10.3 防护措施

**SQL注入防护**:
- 使用参数化查询
- ORM框架（SQLAlchemy）

**XSS防护**:
- 输入验证和过滤
- 输出编码
- CSP策略

**CSRF防护**:
- CSRF Token验证
- SameSite Cookie

**限流**:
- API限流: 100请求/分钟/用户
- AI生成限流: 10请求/分钟/用户
- 登录限流: 5次失败后锁定10分钟

### 10.4 内容安全

**敏感词过滤**:
- 政治敏感词
- 违法违规内容
- 学术不端内容

**内容审核**:
- 自动审核（关键词匹配）
- 人工审核（旗舰版）
- 违规内容标记和处理

---

## 11. 部署架构

### 11.1 服务器配置

**应用服务器**:
- 数量: 2台（主备）
- 配置: 8核16G
- 负载均衡: Nginx

**数据库服务器**:
- 主库: 1台 (8核32G)
- 从库: 1台 (8核32G)
- 读写分离

**缓存服务器**:
- Redis集群: 3节点
- 配置: 4核8G

**文件存储**:
- 对象存储（OSS/S3）
- CDN加速

### 11.2 监控告警

**系统监控**:
- CPU、内存、磁盘使用率
- 网络流量
- 进程状态

**应用监控**:
- API响应时间
- 错误率
- 请求量

**业务监控**:
- 用户注册量
- 订单量
- 论文生成量
- AI服务调用量

**告警策略**:
- 错误率 > 1%: 立即告警
- 响应时间 > 5s: 警告
- 服务不可用: 紧急告警

---

## 12. 总结

本设计文档详细描述了AI论文写作系统的技术架构、核心组件、数据模型、API接口、正确性属性和测试策略。系统采用模块化设计，支持灵活扩展，通过双重测试方法（单元测试+属性测试）确保系统的正确性和可靠性。

**关键设计决策**:
1. 分层架构确保关注点分离
2. 基于属性的测试验证系统不变量
3. 配额管理和权限控制保证商业模式
4. AI服务抽象支持多模型切换
5. 完善的错误处理和降级策略
6. 安全措施覆盖数据、访问和内容

**下一步**:
- 创建详细的实现任务列表
- 开始P0核心功能开发
- 建立CI/CD流程
- 准备测试环境
