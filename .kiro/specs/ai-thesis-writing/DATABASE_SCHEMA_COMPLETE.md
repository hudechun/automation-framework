# AI论文写作系统 - 数据库表设计完成

## 完成时间
2026-01-25

## 设计规范
✅ 完全符合RuoYi-Vue3-FastAPI框架规范
✅ 表前缀统一使用 `ai_write_`
✅ 包含RuoYi标准字段：`create_by`, `create_time`, `update_by`, `update_time`, `remark`
✅ 使用 `del_flag` 实现软删除（0代表存在 2代表删除）
✅ 使用 `char(1)` 类型表示状态
✅ 遵循RuoYi的命名和注释风格

## 数据库表清单（共13张表）

### 1. 会员套餐管理（3张表）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `ai_write_member_package` | 会员套餐表 | package_id, package_name, price, duration_days, word_quota, usage_quota, features(JSON) |
| `ai_write_user_membership` | 用户会员表 | membership_id, user_id, package_id, total_word_quota, used_word_quota, start_date, end_date |
| `ai_write_user_feature_quota` | 用户功能配额表 | quota_id, user_id, service_type, total_quota, used_quota, source |

### 2. 配额管理（1张表）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `ai_write_quota_record` | 配额使用记录表 | record_id, user_id, thesis_id, word_count, usage_count, operation_type |

### 3. 论文管理（4张表）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `ai_write_thesis` | 论文表 | thesis_id, user_id, template_id, title, major, degree_level, status, total_words |
| `ai_write_thesis_outline` | 论文大纲表 | outline_id, thesis_id, structure_type, outline_data(JSON) |
| `ai_write_thesis_chapter` | 论文章节表 | chapter_id, thesis_id, title, level, order_num, content, word_count, status |
| `ai_write_thesis_version` | 论文版本历史表 | version_id, thesis_id, version_number, snapshot_data(JSON) |

### 4. 格式模板管理（2张表）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `ai_write_format_template` | 格式模板表 | template_id, school_name, major, degree_level, format_data(JSON) |
| `ai_write_template_format_rule` | 模板格式规则表 | rule_id, template_id, rule_type, rule_name, rule_value(JSON) |

### 5. 导出管理（1张表）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `ai_write_export_record` | 导出记录表 | record_id, user_id, thesis_id, file_name, file_path, file_size |

### 6. 订单支付（2张表）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `ai_write_order` | 订单表 | order_id, order_no, user_id, package_id, amount, payment_method, status |
| `ai_write_feature_service` | 功能服务表 | service_id, service_name, service_type, price, billing_unit |

## 核心设计特点

### 1. 灵活的会员套餐配置
- 使用JSON字段存储功能权限配置
- 支持管理后台自由创建和配置套餐
- 功能类型包括：boolean（开关）、quota（配额）、count（次数）

### 2. 完善的配额管理
- 基础配额：字数配额、使用次数配额
- 功能配额：去AI化、润色、检测、查重等独立配额
- 配额记录：完整的使用和退还记录

### 3. 论文创作流程
- 论文基本信息
- 大纲生成和管理
- 章节内容生成和编辑
- 版本历史管理

### 4. 格式模板系统
- 支持多学校、多专业、多学位级别
- JSON存储完整格式数据
- 独立的格式规则表

### 5. 支付订单系统
- 支持微信支付、支付宝
- 订单状态管理
- 单项功能购买

## 初始化数据

### 会员套餐（3个）
1. **免费体验版** - ¥0/月，5000字，1次
2. **专业版** - ¥199/月，10万字，30次（推荐）
3. **旗舰版** - ¥499/月，无限使用

### 功能服务（5个）
1. **去AI化处理** - ¥0.05/千字
2. **内容润色** - ¥0.08/千字
3. **AIGC检测预估** - ¥0.02/千字
4. **查重率预估** - ¥0.10/千字
5. **人工审核服务** - ¥50/篇

## 索引设计

所有表都包含合理的索引：
- 主键索引
- 用户ID索引（用于快速查询用户数据）
- 状态索引（用于筛选）
- 时间索引（用于排序和过期查询）
- 外键索引（用于关联查询）

## 下一步工作

1. ✅ 数据库表设计完成
2. ⏳ 创建实体类（Entity）
3. ⏳ 创建DAO层
4. ⏳ 创建Service层
5. ⏳ 创建Controller层
6. ⏳ 前端页面开发

## 文件位置

- SQL文件：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql`
- 模块目录：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/`

## 执行SQL

```bash
# 进入MySQL
mysql -u root -p

# 选择数据库
use ry-vue;

# 执行SQL文件
source RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql;
```

## 注意事项

1. 所有表都使用 `InnoDB` 引擎，支持事务
2. 字符集使用 `utf8mb4`，支持emoji和特殊字符
3. JSON字段用于存储复杂的配置和数据结构
4. 软删除机制保证数据安全
5. 完整的审计字段（创建人、创建时间、更新人、更新时间）
