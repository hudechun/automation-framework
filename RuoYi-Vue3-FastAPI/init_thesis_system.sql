-- ============================================================
-- AI论文写作系统 - 完整初始化脚本
-- 执行顺序：
-- 1. 创建所有表结构
-- 2. 初始化基础数据
-- 3. 为admin用户添加配额
-- ============================================================

-- 使用数据库
USE `ruoyi-fastapi`;

-- ============================================================
-- 第一步：创建表结构（从thesis_schema.sql）
-- ============================================================

SOURCE RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql;

-- ============================================================
-- 第二步：为admin用户添加论文生成配额
-- ============================================================

-- 查看admin用户的user_id
SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';

-- 为admin用户添加配额（假设user_id=1，如果不是请修改）
INSERT INTO ai_write_user_feature_quota 
(user_id, service_type, total_quota, used_quota, 
 start_date, end_date, source, source_id, 
 status, del_flag, create_by, create_time, update_by, update_time, remark)
VALUES 
(1, 'thesis_generation', 1000, 0, 
 NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 'manual', NULL,
 '0', '0', 'admin', NOW(), '', NOW(), '管理员初始配额')
ON DUPLICATE KEY UPDATE
    total_quota = 1000,
    used_quota = 0,
    update_time = NOW();

-- 验证配额已添加
SELECT * FROM ai_write_user_feature_quota 
WHERE user_id = 1 AND service_type = 'thesis_generation';

-- ============================================================
-- 第三步：验证所有表是否创建成功
-- ============================================================

SHOW TABLES LIKE 'ai_write_%';

-- ============================================================
-- 完成！
-- ============================================================
