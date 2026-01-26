-- ============================================================
-- 为管理员账号添加论文生成配额
-- ============================================================

-- 1. 查看admin用户的user_id
SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';

-- 2. 检查当前配额状态（将下面的1替换为上面查询到的user_id）
SELECT * FROM thesis_user_feature_quota WHERE user_id = 1 AND feature_type = 'thesis_generation';

-- 3. 如果上面查询有结果，执行UPDATE（更新配额）
UPDATE thesis_user_feature_quota 
SET total_quota = 1000, 
    remaining_quota = 1000 - used_quota,
    update_time = NOW()
WHERE user_id = 1 AND feature_type = 'thesis_generation';

-- 4. 如果上面查询没有结果，执行INSERT（创建新配额记录）
INSERT INTO thesis_user_feature_quota 
(user_id, feature_type, total_quota, used_quota, remaining_quota, 
 expire_time, status, create_time, update_time)
VALUES 
(1, 'thesis_generation', 1000, 0, 1000, 
 DATE_ADD(NOW(), INTERVAL 1 YEAR), '0', NOW(), NOW());

-- 5. 验证配额已添加
SELECT * FROM thesis_user_feature_quota WHERE user_id = 1 AND feature_type = 'thesis_generation';
