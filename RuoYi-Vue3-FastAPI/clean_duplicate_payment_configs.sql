-- 清理重复的支付配置记录
-- 保留每个 provider_type 的第一条记录，删除其他重复记录

-- 查看重复记录
SELECT provider_type, COUNT(*) as count 
FROM ai_write_payment_config 
WHERE del_flag = '0'
GROUP BY provider_type 
HAVING COUNT(*) > 1;

-- 删除重复的支付宝配置（保留 config_id 最小的）
DELETE FROM ai_write_payment_config 
WHERE provider_type = 'alipay' 
AND config_id NOT IN (
    SELECT * FROM (
        SELECT MIN(config_id) 
        FROM ai_write_payment_config 
        WHERE provider_type = 'alipay' AND del_flag = '0'
    ) AS temp
);

-- 删除重复的微信支付配置（保留 config_id 最小的）
DELETE FROM ai_write_payment_config 
WHERE provider_type = 'wechat' 
AND config_id NOT IN (
    SELECT * FROM (
        SELECT MIN(config_id) 
        FROM ai_write_payment_config 
        WHERE provider_type = 'wechat' AND del_flag = '0'
    ) AS temp
);

-- 删除重复的 Ping++ 配置（保留 config_id 最小的）
DELETE FROM ai_write_payment_config 
WHERE provider_type = 'pingpp' 
AND config_id NOT IN (
    SELECT * FROM (
        SELECT MIN(config_id) 
        FROM ai_write_payment_config 
        WHERE provider_type = 'pingpp' AND del_flag = '0'
    ) AS temp
);

-- 验证清理结果
SELECT config_id, provider_type, provider_name, is_enabled, create_time 
FROM ai_write_payment_config 
WHERE del_flag = '0'
ORDER BY provider_type;
