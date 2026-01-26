-- ============================================================
-- 快速为admin用户添加论文生成配额
-- 前提：thesis_schema.sql已经执行，所有表已创建
-- ============================================================

-- 1. 查看admin用户的user_id
SELECT '步骤1: 查找admin用户' AS step;
SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';

-- 2. 为admin用户添加论文生成配额
-- 注意：请将下面的user_id=1替换为上面查询到的实际user_id
SELECT '步骤2: 添加论文生成配额' AS step;
INSERT INTO ai_write_user_feature_quota 
(user_id, service_type, total_quota, used_quota, 
 start_date, end_date, source, source_id, 
 status, del_flag, create_by, create_time, update_by, update_time, remark)
VALUES 
(1, 'thesis_generation', 1000, 0, 
 NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 'manual', NULL,
 '0', '0', 'admin', NOW(), '', NOW(), '管理员初始配额');

-- 3. 验证配额已添加
SELECT '步骤3: 验证配额' AS step;
SELECT 
    quota_id,
    user_id,
    service_type,
    total_quota,
    used_quota,
    total_quota - used_quota AS remaining_quota,
    start_date,
    end_date,
    status,
    remark
FROM ai_write_user_feature_quota 
WHERE user_id = 1 AND service_type = 'thesis_generation';

-- 4. 如果配额已存在，使用UPDATE更新
-- UPDATE ai_write_user_feature_quota 
-- SET total_quota = 1000,
--     used_quota = 0,
--     update_time = NOW(),
--     remark = '管理员配额更新'
-- WHERE user_id = 1 AND service_type = 'thesis_generation';

SELECT '完成！admin用户现在有1000次论文生成配额' AS result;
