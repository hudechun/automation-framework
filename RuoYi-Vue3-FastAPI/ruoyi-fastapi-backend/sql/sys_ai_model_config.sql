-- ============================================================
-- 系统AI模型配置表（全局配置，支持语言模型和视觉模型）
-- ============================================================

DROP TABLE IF EXISTS sys_ai_model_config;
CREATE TABLE sys_ai_model_config (
  config_id         BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '配置ID',
  model_name        VARCHAR(100)    NOT NULL                   COMMENT '模型名称',
  model_code        VARCHAR(100)    NOT NULL                   COMMENT '模型代码',
  model_type        VARCHAR(20)     NOT NULL DEFAULT 'language' COMMENT '模型类型（language/vision）',
  provider          VARCHAR(50)     NOT NULL                   COMMENT '提供商（openai/anthropic/qwen等）',
  
  api_key           VARCHAR(500)    DEFAULT NULL               COMMENT 'API密钥',
  api_endpoint      VARCHAR(500)    DEFAULT NULL               COMMENT 'API端点',
  model_version     VARCHAR(50)     DEFAULT NULL               COMMENT '模型版本',
  
  params            JSON            DEFAULT NULL               COMMENT '模型参数（JSON）',
  capabilities      JSON            DEFAULT NULL               COMMENT '模型能力（JSON）',
  
  priority          INT(4)          DEFAULT 0                  COMMENT '优先级（数字越大越优先）',
  is_enabled        CHAR(1)         DEFAULT '0'                COMMENT '是否启用（0否 1是）',
  is_default        CHAR(1)         DEFAULT '0'                COMMENT '是否默认（0否 1是）',
  is_preset         CHAR(1)         DEFAULT '0'                COMMENT '是否预设（0否 1是）',
  
  status            CHAR(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志（0存在 2删除）',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME        DEFAULT NULL               COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME        DEFAULT NULL               COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  
  PRIMARY KEY (config_id),
  UNIQUE KEY uk_model_code (model_code, model_type),
  KEY idx_provider (provider),
  KEY idx_model_type (model_type),
  KEY idx_is_enabled (is_enabled),
  KEY idx_is_default (is_default)
) ENGINE=InnoDB AUTO_INCREMENT=100 COMMENT='系统AI模型配置表';

-- ============================================================
-- 插入预设模型数据
-- ============================================================

-- OpenAI 语言模型
INSERT INTO sys_ai_model_config VALUES
(1, 'GPT-4o', 'gpt-4o', 'language', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4o-2024-11-20', 
 '{"temperature": 0.7, "max_tokens": 16384}', 
 '{"text_generation": true, "code_generation": true, "reasoning": true, "multimodal": true}', 
 100, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4o 最新多模态模型'),
(2, 'GPT-4o Mini', 'gpt-4o-mini', 'language', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4o-mini-2024-07-18', 
 '{"temperature": 0.7, "max_tokens": 16384}', 
 '{"text_generation": true, "code_generation": true, "fast_response": true}', 
 95, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4o Mini 快速高性价比'),
(3, 'GPT-4 Turbo', 'gpt-4-turbo', 'language', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4-turbo-2024-04-09', 
 '{"temperature": 0.7, "max_tokens": 4096}', 
 '{"text_generation": true, "code_generation": true, "reasoning": true}', 
 90, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4 Turbo 视觉支持');

-- Anthropic 语言模型
INSERT INTO sys_ai_model_config VALUES
(4, 'Claude 3.5 Sonnet', 'claude-3-5-sonnet-20241022', 'language', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-5-sonnet-20241022', 
 '{"temperature": 0.7, "max_tokens": 8192}', 
 '{"text_generation": true, "code_generation": true, "reasoning": true, "long_context": true}', 
 98, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3.5 Sonnet 最新最强版本'),
(5, 'Claude 3.5 Haiku', 'claude-3-5-haiku-20241022', 'language', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-5-haiku-20241022', 
 '{"temperature": 0.7, "max_tokens": 8192}', 
 '{"text_generation": true, "code_generation": true, "fast_response": true}', 
 92, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3.5 Haiku 快速版本'),
(6, 'Claude 3 Opus', 'claude-3-opus-20240229', 'language', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-opus-20240229', 
 '{"temperature": 0.7, "max_tokens": 4096}', 
 '{"text_generation": true, "code_generation": true, "reasoning": true, "long_context": true}', 
 90, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3 Opus 强大推理能力');

-- Qwen 语言模型
INSERT INTO sys_ai_model_config VALUES
(7, '通义千问Max', 'qwen3-max', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-max-latest', 
 '{"temperature": 0.7}', 
 '{"text_generation": true, "chinese_optimized": true}', 
 92, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Max 最强版本'),
(8, '通义千问Plus', 'qwen3-plus', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-plus-latest', 
 '{"temperature": 0.7}', 
 '{"text_generation": true, "chinese_optimized": true}', 
 88, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Plus 平衡版本'),
(9, '通义千问Turbo', 'qwen-flash', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-turbo-latest', 
 '{"temperature": 0.7}', 
 '{"text_generation": true, "fast_response": true, "chinese_optimized": true}', 
 82, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Turbo 快速版本'),
(10, '通义千问Long', 'qwen3-long', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-long', 
 '{"temperature": 0.7}', 
 '{"text_generation": true, "long_context": true, "chinese_optimized": true}', 
 86, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Long 超长上下文');

-- OpenAI 视觉模型
INSERT INTO sys_ai_model_config VALUES
(11, 'GPT-4o Vision', 'gpt-4o', 'vision', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4o-2024-11-20', 
 '{"temperature": 0.7, "max_tokens": 16384}', 
 '{"image_understanding": true, "ocr": true, "visual_reasoning": true, "multimodal": true}', 
 98, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4o 多模态视觉理解'),
(12, 'GPT-4o Mini Vision', 'gpt-4o-mini', 'vision', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4o-mini-2024-07-18', 
 '{"temperature": 0.7, "max_tokens": 16384}', 
 '{"image_understanding": true, "ocr": true, "visual_reasoning": true}', 
 92, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4o Mini 视觉理解高性价比');

-- Anthropic 视觉模型
INSERT INTO sys_ai_model_config VALUES
(13, 'Claude 3.5 Sonnet Vision', 'claude-3-5-sonnet-20241022', 'vision', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-5-sonnet-20241022', 
 '{"temperature": 0.7, "max_tokens": 8192}', 
 '{"image_understanding": true, "ocr": true, "visual_reasoning": true, "document_analysis": true}', 
 98, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3.5 Sonnet 视觉理解'),
(14, 'Claude 3 Opus Vision', 'claude-3-opus-20240229', 'vision', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-opus-20240229', 
 '{"temperature": 0.7, "max_tokens": 4096}', 
 '{"image_understanding": true, "ocr": true, "visual_reasoning": true, "document_analysis": true}', 
 90, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3 Opus 视觉理解');

-- Qwen 视觉模型
INSERT INTO sys_ai_model_config VALUES
(15, '通义千问VL Max', 'qwen-vl-max', 'vision', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-vl-max', 
 '{"temperature": 0.7, "max_tokens": 8000}', 
 '{"image_understanding": true, "ocr": true, "chinese_optimized": true, "video_understanding": true}', 
 90, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问VL Max 视觉理解'),
(16, 'Qwen2-VL', 'qwen2-vl-72b-instruct', 'vision', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen2-vl-72b-instruct', 
 '{"temperature": 0.7, "max_tokens": 8000}', 
 '{"image_understanding": true, "ocr": true, "chinese_optimized": true}', 
 85, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Qwen2-VL 72B 视觉理解');

-- ============================================================
-- 数据迁移（从旧表迁移到新表）
-- ============================================================

-- 如果旧表存在，迁移数据
INSERT INTO sys_ai_model_config (
  model_name, model_code, model_type, provider, api_key, api_endpoint,
  model_version, params, priority, is_enabled, is_default, is_preset,
  status, del_flag, create_by, create_time, update_by, update_time, remark
)
SELECT 
  model_name, 
  model_code, 
  'language' as model_type,
  CASE 
    WHEN model_code LIKE 'gpt%' THEN 'openai'
    WHEN model_code LIKE 'claude%' THEN 'anthropic'
    WHEN model_code LIKE 'qwen%' THEN 'qwen'
    ELSE model_code
  END as provider,
  api_key, 
  COALESCE(api_endpoint, api_base_url) as api_endpoint,
  model_version, 
  JSON_OBJECT(
    'temperature', COALESCE(temperature, 0.7),
    'max_tokens', COALESCE(max_tokens, 4096),
    'top_p', COALESCE(top_p, 0.9)
  ) as params,
  priority, 
  is_enabled, 
  is_default, 
  is_preset,
  status, 
  del_flag, 
  create_by, 
  create_time, 
  update_by, 
  update_time, 
  remark
FROM ai_write_ai_model_config
WHERE del_flag = '0'
  AND NOT EXISTS (
    SELECT 1 FROM sys_ai_model_config 
    WHERE sys_ai_model_config.model_code = ai_write_ai_model_config.model_code
  );
