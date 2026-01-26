-- 更新现有AI模型记录的model_type字段
-- 将所有现有记录设置为语言模型

UPDATE ai_write_ai_model_config 
SET model_type = 'language' 
WHERE model_type IS NULL OR model_type = '';

UPDATE ai_write_ai_model_config 
SET provider = model_code 
WHERE provider IS NULL OR provider = '';

-- 验证更新结果
SELECT 
    config_id,
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default
FROM ai_write_ai_model_config
WHERE del_flag = '0'
ORDER BY priority DESC;
