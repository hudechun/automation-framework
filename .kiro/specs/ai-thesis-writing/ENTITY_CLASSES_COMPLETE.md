# AI论文写作系统 - 实体类创建完成

## 完成时间
2026-01-25

## 创建的实体类（13个）

### 1. 会员管理相关（4个实体类）

#### member_do.py
- ✅ `AiWriteMemberPackage` - 会员套餐表
- ✅ `AiWriteUserMembership` - 用户会员表
- ✅ `AiWriteUserFeatureQuota` - 用户功能配额表
- ✅ `AiWriteQuotaRecord` - 配额使用记录表

### 2. 论文管理相关（4个实体类）

#### thesis_do.py
- ✅ `AiWriteThesis` - 论文表
- ✅ `AiWriteThesisOutline` - 论文大纲表
- ✅ `AiWriteThesisChapter` - 论文章节表
- ✅ `AiWriteThesisVersion` - 论文版本历史表

### 3. 格式模板相关（2个实体类）

#### template_do.py
- ✅ `AiWriteFormatTemplate` - 格式模板表
- ✅ `AiWriteTemplateFormatRule` - 模板格式规则表

### 4. 订单支付相关（3个实体类）

#### order_do.py
- ✅ `AiWriteOrder` - 订单表
- ✅ `AiWriteFeatureService` - 功能服务表
- ✅ `AiWriteExportRecord` - 导出记录表

## 技术规范

### 1. 完全符合RuoYi规范
- ✅ 使用SQLAlchemy ORM
- ✅ 继承自 `Base` 类
- ✅ 使用 `__tablename__` 指定表名
- ✅ 使用 `__table_args__` 添加表注释
- ✅ 所有字段都有详细的中文注释

### 2. 字段类型映射

| SQL类型 | SQLAlchemy类型 | 说明 |
|---------|---------------|------|
| bigint(20) | BigInteger | 主键、外键 |
| varchar(n) | String(n) | 字符串 |
| char(1) | CHAR(1) | 状态、标志 |
| int(11) | Integer | 整数 |
| decimal(10,2) | Numeric(10,2) | 金额 |
| datetime | DateTime | 日期时间 |
| text | Text | 长文本 |
| longtext | Text | 超长文本 |
| json | JSON | JSON数据 |

### 3. 标准字段处理

所有表都包含RuoYi标准字段：
```python
create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='备注')
```

部分表包含：
```python
status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
del_flag = Column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0代表存在 2代表删除）')
sort_order = Column(Integer, nullable=True, server_default='0', comment='显示顺序')
```

### 4. 特殊字段处理

#### NULL值处理
使用 `SqlalchemyUtil.get_server_default_null()` 处理可为NULL的字段：
```python
template_id = Column(
    BigInteger,
    nullable=True,
    server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
    comment='模板ID',
)
```

#### JSON字段
```python
features = Column(JSON, nullable=False, comment='功能权限配置（JSON格式）')
keywords = Column(JSON, nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='关键词（JSON数组）')
```

#### 自动更新时间
```python
update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
```

#### 唯一约束
```python
thesis_id = Column(BigInteger, nullable=False, unique=True, comment='论文ID')
order_no = Column(String(64), nullable=False, unique=True, comment='订单号')
```

## 文件结构

```
module_thesis/
└── entity/
    ├── __init__.py                    ✅ 已创建
    ├── do/                            ✅ 数据库实体类
    │   ├── __init__.py                ✅ 导入所有实体
    │   ├── member_do.py               ✅ 会员管理实体（4个类）
    │   ├── thesis_do.py               ✅ 论文管理实体（4个类）
    │   ├── template_do.py             ✅ 格式模板实体（2个类）
    │   └── order_do.py                ✅ 订单支付实体（3个类）
    └── vo/                            ⏳ 待创建（视图对象）
```

## 使用示例

### 导入实体类
```python
# 方式1：导入所有实体
from module_thesis.entity.do import *

# 方式2：导入特定实体
from module_thesis.entity.do import AiWriteMemberPackage, AiWriteUserMembership

# 方式3：从具体文件导入
from module_thesis.entity.do.member_do import AiWriteMemberPackage
```

### 创建实例
```python
from datetime import datetime, timedelta
from module_thesis.entity.do import AiWriteMemberPackage

# 创建会员套餐
package = AiWriteMemberPackage(
    package_name='专业版',
    package_desc='适合毕业论文写作',
    price=199.00,
    duration_days=30,
    word_quota=100000,
    usage_quota=30,
    features={
        'basic_generation': True,
        'de_ai': {'enabled': True, 'quota': 50000},
        'polish': {'enabled': True, 'quota': 30000}
    },
    is_recommended='1',
    badge='最受欢迎',
    sort_order=2,
    status='0',
    del_flag='0',
    create_by='admin',
    create_time=datetime.now()
)
```

### 查询示例
```python
from sqlalchemy import select
from module_thesis.entity.do import AiWriteUserMembership

# 查询用户当前会员
stmt = select(AiWriteUserMembership).where(
    AiWriteUserMembership.user_id == user_id,
    AiWriteUserMembership.status == '0',
    AiWriteUserMembership.del_flag == '0',
    AiWriteUserMembership.end_date > datetime.now()
).order_by(AiWriteUserMembership.end_date.desc())
```

## 与数据库表的对应关系

| 实体类 | 数据库表 | 文件 |
|--------|---------|------|
| AiWriteMemberPackage | ai_write_member_package | member_do.py |
| AiWriteUserMembership | ai_write_user_membership | member_do.py |
| AiWriteUserFeatureQuota | ai_write_user_feature_quota | member_do.py |
| AiWriteQuotaRecord | ai_write_quota_record | member_do.py |
| AiWriteThesis | ai_write_thesis | thesis_do.py |
| AiWriteThesisOutline | ai_write_thesis_outline | thesis_do.py |
| AiWriteThesisChapter | ai_write_thesis_chapter | thesis_do.py |
| AiWriteThesisVersion | ai_write_thesis_version | thesis_do.py |
| AiWriteFormatTemplate | ai_write_format_template | template_do.py |
| AiWriteTemplateFormatRule | ai_write_template_format_rule | template_do.py |
| AiWriteOrder | ai_write_order | order_do.py |
| AiWriteFeatureService | ai_write_feature_service | order_do.py |
| AiWriteExportRecord | ai_write_export_record | order_do.py |

## 下一步工作

### 任务2.2：创建DAO层（数据访问层）

在 `module_thesis/dao/` 目录下创建：
- `member_dao.py` - 会员相关DAO
- `thesis_dao.py` - 论文相关DAO
- `template_dao.py` - 模板相关DAO
- `order_dao.py` - 订单相关DAO

**预计工时**: 4小时

## 验证实体类

可以通过以下方式验证实体类是否正确：

```python
# 测试导入
from module_thesis.entity.do import *

# 打印所有实体类
print(__all__)

# 检查表名
print(AiWriteMemberPackage.__tablename__)  # 应输出: ai_write_member_package

# 检查字段
print(AiWriteMemberPackage.__table__.columns.keys())
```

## 注意事项

1. ✅ 所有实体类都继承自 `Base`
2. ✅ 使用 `datetime.now` 而不是 `datetime.now()`（不带括号）
3. ✅ JSON字段需要特殊处理NULL值
4. ✅ 金额字段使用 `Numeric(10, 2)`
5. ✅ 主键都设置了 `autoincrement=True`
6. ✅ 外键字段可为NULL时需要特殊处理
7. ✅ 唯一约束使用 `unique=True`

## 相关文档

- [数据库表设计](./DATABASE_SCHEMA_COMPLETE.md)
- [数据库快速参考](./DATABASE_QUICK_REFERENCE.md)
- [开发进度](./PROGRESS.md)
- [任务列表](./tasks.md)

---

**完成时间**: 2026-01-25  
**下一步**: 创建DAO层
