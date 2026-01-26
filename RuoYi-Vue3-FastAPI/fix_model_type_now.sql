-- 快速修复：更新ai_write_ai_model_config表的model_type字段
-- 将所有现有记录设置为语言模型

-- 1. 更新model_type字段为'language'
UPDATE ai_write_ai_model_config 
SET model_type = 'language' 
WHERE model_type IS NULL OR model_type = '';

-- 2. 更新provider字段
UPDATE ai_write_ai_model_config 
SET provider = model_code 
WHERE provider IS NULL OR provider = '';

-- 3. 查看更新结果
SELECT 
    config_id,
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default,
    priority
FROM ai_write_ai_model_config
WHERE del_flag = '0'
ORDER BY priority DESC;

-- 4. 检查是否有默认的语言模型
SELECT 
    config_id,
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default
FROM ai_write_ai_model_config
WHERE model_type = 'language'
  AND is_default = '1'
  AND is_enabled = '1'
  AND del_flag = '0';
