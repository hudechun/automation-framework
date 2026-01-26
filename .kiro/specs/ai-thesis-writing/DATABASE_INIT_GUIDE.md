# 数据库初始化指南

## 问题描述
错误信息：`thesis_user_feature_quota不存在`

实际情况：
- 代码中使用的表名是：`ai_write_user_feature_quota`
- 字段名是：`service_type`（不是 `feature_type`）
- 需要先创建表结构，然后添加配额数据

---

## 解决方案

### 方法1: 使用MySQL客户端工具（推荐）

#### 步骤1: 连接数据库
使用Navicat、DBeaver或其他MySQL客户端工具连接到数据库：
- 主机：106.53.217.96
- 端口：3306
- 用户名：root
- 密码：gyswxgyb7418!
- 数据库：ruoyi-fastapi

#### 步骤2: 执行表结构创建脚本
打开并执行文件：
```
RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql
```

这将创建以下表：
- ai_write_member_package（会员套餐表）
- ai_write_user_membership（用户会员表）
- ai_write_user_feature_quota（用户功能配额表）⭐
- ai_write_quota_record（配额使用记录表）
- ai_write_thesis（论文表）
- ai_write_thesis_outline（论文大纲表）
- ai_write_thesis_chapter（论文章节表）
- ai_write_format_template（格式模板表）
- ai_write_template_format_rule（模板格式规则表）
- ai_write_export_record（导出记录表）
- ai_write_order（订单表）
- ai_write_feature_service（功能服务表）
- ai_write_thesis_version（论文版本历史表）

#### 步骤3: 为admin用户添加配额
执行文件：
```
RuoYi-Vue3-FastAPI/quick_add_admin_quota.sql
```

或者直接执行以下SQL：
```sql
-- 1. 查看admin用户的user_id
SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';

-- 2. 添加配额（将1替换为实际的user_id）
INSERT INTO ai_write_user_feature_quota 
(user_id, service_type, total_quota, used_quota, 
 start_date, end_date, source, source_id, 
 status, del_flag, create_by, create_time, update_by, update_time, remark)
VALUES 
(1, 'thesis_generation', 1000, 0, 
 NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 'manual', NULL,
 '0', '0', 'admin', NOW(), '', NOW(), '管理员初始配额');

-- 3. 验证
SELECT * FROM ai_write_user_feature_quota 
WHERE user_id = 1 AND service_type = 'thesis_generation';
```

---

### 方法2: 使用命令行

```bash
# 连接到数据库
mysql -h 106.53.217.96 -u root -p ruoyi-fastapi

# 输入密码：gyswxgyb7418!

# 执行表结构创建
source RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql;

# 添加admin配额
INSERT INTO ai_write_user_feature_quota 
(user_id, service_type, total_quota, used_quota, 
 start_date, end_date, source, source_id, 
 status, del_flag, create_by, create_time, update_by, update_time, remark)
VALUES 
(1, 'thesis_generation', 1000, 0, 
 NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 'manual', NULL,
 '0', '0', 'admin', NOW(), '', NOW(), '管理员初始配额');

# 验证
SELECT * FROM ai_write_user_feature_quota WHERE user_id = 1;

# 退出
exit;
```

---

## 重要说明

### 表名对应关系
| 代码中的模型名 | 数据库表名 |
|--------------|-----------|
| AiWriteMemberPackage | ai_write_member_package |
| AiWriteUserMembership | ai_write_user_membership |
| AiWriteUserFeatureQuota | ai_write_user_feature_quota ⭐ |
| AiWriteQuotaRecord | ai_write_quota_record |
| AiWriteThesis | ai_write_thesis |
| AiWriteThesisOutline | ai_write_thesis_outline |
| AiWriteThesisChapter | ai_write_thesis_chapter |
| AiWriteFormatTemplate | ai_write_format_template |
| AiWriteTemplateFormatRule | ai_write_template_format_rule |
| AiWriteExportRecord | ai_write_export_record |
| AiWriteOrder | ai_write_order |
| AiWriteFeatureService | ai_write_feature_service |
| AiWriteThesisVersion | ai_write_thesis_version |

### 配额字段说明
| 字段名 | 类型 | 说明 |
|-------|------|------|
| quota_id | BIGINT | 配额ID（主键） |
| user_id | BIGINT | 用户ID |
| service_type | VARCHAR(30) | 服务类型 ⭐ |
| total_quota | INT | 总配额（字数或次数） |
| used_quota | INT | 已使用配额 |
| start_date | DATETIME | 开始时间 |
| end_date | DATETIME | 结束时间 |
| source | VARCHAR(20) | 来源（package/purchase/manual） |
| source_id | BIGINT | 来源ID |
| status | CHAR(1) | 状态（0正常 1停用 2过期） |
| del_flag | CHAR(1) | 删除标志（0存在 2删除） |

### 服务类型 (service_type)
- `thesis_generation`: 论文生成
- `de_ai`: 去AI化处理
- `polish`: 内容润色
- `aigc_detection`: AIGC检测
- `plagiarism_check`: 查重率预估
- `manual_review`: 人工审核

---

## 验证步骤

### 1. 验证表是否创建成功
```sql
SHOW TABLES LIKE 'ai_write_%';
```

应该显示13个表。

### 2. 验证配额是否添加成功
```sql
SELECT 
    quota_id,
    user_id,
    service_type,
    total_quota,
    used_quota,
    total_quota - used_quota AS remaining_quota,
    DATE_FORMAT(start_date, '%Y-%m-%d') AS start_date,
    DATE_FORMAT(end_date, '%Y-%m-%d') AS end_date,
    status,
    remark
FROM ai_write_user_feature_quota 
WHERE user_id = 1 AND service_type = 'thesis_generation';
```

应该显示一条记录，total_quota=1000，used_quota=0。

### 3. 在前端测试
1. 刷新浏览器页面（Ctrl+F5）
2. 进入"论文管理" → "论文列表"
3. 点击"新增"按钮
4. 填写论文信息并提交
5. 不应该再出现"配额不足"错误

---

## 常见问题

### Q1: 执行thesis_schema.sql时报错"表已存在"
A: 说明表已经创建过了，可以跳过步骤2，直接执行步骤3添加配额。

### Q2: 添加配额时报错"Duplicate entry"
A: 说明配额记录已存在，使用UPDATE语句更新：
```sql
UPDATE ai_write_user_feature_quota 
SET total_quota = 1000,
    used_quota = 0,
    update_time = NOW()
WHERE user_id = 1 AND service_type = 'thesis_generation';
```

### Q3: 如何查看当前用户的所有配额？
A: 
```sql
SELECT 
    service_type,
    total_quota,
    used_quota,
    total_quota - used_quota AS remaining_quota,
    status
FROM ai_write_user_feature_quota 
WHERE user_id = 1 AND del_flag = '0';
```

### Q4: 如何给其他用户添加配额？
A: 将SQL中的user_id=1替换为目标用户的ID即可。

### Q5: 配额用完了怎么办？
A: 
```sql
-- 增加配额
UPDATE ai_write_user_feature_quota 
SET total_quota = total_quota + 1000,
    update_time = NOW()
WHERE user_id = 1 AND service_type = 'thesis_generation';

-- 或者重置已使用配额
UPDATE ai_write_user_feature_quota 
SET used_quota = 0,
    update_time = NOW()
WHERE user_id = 1 AND service_type = 'thesis_generation';
```

---

## 相关文件
- 表结构SQL：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql`
- 快速添加配额SQL：`RuoYi-Vue3-FastAPI/quick_add_admin_quota.sql`
- 完整初始化SQL：`RuoYi-Vue3-FastAPI/init_thesis_system.sql`
- 数据模型定义：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/entity/do/member_do.py`
- DAO层实现：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/dao/member_dao.py`
