@echo off
chcp 65001 >nul
echo ============================================================
echo 为管理员添加论文生成配额
echo ============================================================
echo.
echo 请在 MySQL 客户端中执行以下 SQL 语句：
echo.
echo -- 1. 查看 admin 用户的 user_id
echo SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';
echo.
echo -- 2. 检查当前配额状态（将下面的 1 替换为上面查询到的 user_id）
echo SELECT * FROM thesis_user_feature_quota WHERE user_id = 1 AND feature_type = 'thesis_generation';
echo.
echo -- 3. 如果上面查询有结果，执行 UPDATE（更新配额）
echo UPDATE thesis_user_feature_quota 
echo SET total_quota = 1000, 
echo     remaining_quota = 1000 - used_quota,
echo     update_time = NOW()
echo WHERE user_id = 1 AND feature_type = 'thesis_generation';
echo.
echo -- 4. 如果上面查询没有结果，执行 INSERT（创建新配额记录）
echo INSERT INTO thesis_user_feature_quota 
echo (user_id, feature_type, total_quota, used_quota, remaining_quota, 
echo  expire_time, status, create_time, update_time)
echo VALUES 
echo (1, 'thesis_generation', 1000, 0, 1000, 
echo  DATE_ADD(NOW(), INTERVAL 1 YEAR), '0', NOW(), NOW());
echo.
echo -- 5. 验证配额已添加
echo SELECT * FROM thesis_user_feature_quota WHERE user_id = 1 AND feature_type = 'thesis_generation';
echo.
echo ============================================================
echo 或者，复制 add_admin_quota.sql 文件的内容到 MySQL 客户端执行
echo ============================================================
pause
