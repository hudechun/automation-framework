-- ============================================================
-- AI模型配置表
-- ============================================================

DROP TABLE IF EXISTS ai_write_ai_model_config;
CREATE TABLE ai_write_ai_model_config (
  config_id         BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '配置ID',
  model_name        VARCHAR(100)    NOT NULL                   COMMENT '模型名称',
  model_code        VARCHAR(50)     NOT NULL                   COMMENT '模型代码（openai/claude/qwen等）',
  model_version     VARCHAR(50)     NOT NULL                   COMMENT '模型版本（gpt-4/claude-3等）',
  
  api_key           VARCHAR(500)    DEFAULT ''                 COMMENT 'API密钥（加密存储）',
  api_base_url      VARCHAR(200)    DEFAULT ''                 COMMENT 'API基础URL',
  api_endpoint      VARCHAR(200)    DEFAULT ''                 COMMENT 'API端点',
  
  max_tokens        INT(11)         DEFAULT 4096               COMMENT '最大token数',
  temperature       DECIMAL(3,2)    DEFAULT 0.70               COMMENT '温度参数',
  top_p             DECIMAL(3,2)    DEFAULT 0.90               COMMENT 'Top P参数',
  
  is_enabled        CHAR(1)         DEFAULT '0'                COMMENT '是否启用（0否 1是）',
  is_default        CHAR(1)         DEFAULT '0'                COMMENT '是否默认（0否 1是）',
  is_preset         CHAR(1)         DEFAULT '1'                COMMENT '是否预设（0否 1是）',
  
  priority          INT(4)          DEFAULT 0                  COMMENT '优先级（数字越大越优先）',
  
  status            CHAR(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志（0存在 2删除）',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  
  PRIMARY KEY (config_id),
  UNIQUE KEY uk_model_version (model_code, model_version),
  INDEX idx_enabled (is_enabled, is_default),
  INDEX idx_status (status, del_flag)
) ENGINE=InnoDB AUTO_INCREMENT=100 COMMENT='AI模型配置表';

-- ============================================================
-- 初始化预设模型数据
-- ============================================================

-- OpenAI GPT-4
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint, 
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('OpenAI GPT-4', 'openai', 'gpt-4', 'https://api.openai.com/v1', '/chat/completions',
 8192, 0.70, 0.90, '1', 100, '0', 'system', NOW(), '最强大的GPT模型，适合复杂任务');

-- OpenAI GPT-3.5 Turbo
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('OpenAI GPT-3.5 Turbo', 'openai', 'gpt-3.5-turbo', 'https://api.openai.com/v1', '/chat/completions',
 4096, 0.70, 0.90, '1', 90, '0', 'system', NOW(), '性价比高，响应快速');

-- Claude 3 Opus
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('Claude 3 Opus', 'claude', 'claude-3-opus-20240229', 'https://api.anthropic.com/v1', '/messages',
 4096, 0.70, 0.90, '1', 95, '0', 'system', NOW(), 'Anthropic最强模型，擅长长文本');

-- 通义千问
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('通义千问 Turbo', 'qwen', 'qwen-turbo', 'https://dashscope.aliyuncs.com/api/v1', '/services/aigc/text-generation/generation',
 6000, 0.70, 0.90, '1', 85, '0', 'system', NOW(), '阿里云大模型，中文优化');

-- DeepSeek
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('DeepSeek Chat', 'deepseek', 'deepseek-chat', 'https://api.deepseek.com/v1', '/chat/completions',
 4096, 0.70, 0.90, '1', 80, '0', 'system', NOW(), '国产开源模型，性价比极高');

-- 文心一言
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('文心一言 4.0', 'ernie', 'ernie-4.0', 'https://aip.baidubce.com/rpc/2.0', '/ai_custom/v1/wenxinworkshop/chat/completions_pro',
 2048, 0.70, 0.90, '1', 75, '0', 'system', NOW(), '百度大模型，中文理解强');

-- 智谱AI
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('智谱 GLM-4', 'zhipu', 'glm-4', 'https://open.bigmodel.cn/api/paas/v4', '/chat/completions',
 4096, 0.70, 0.90, '1', 70, '0', 'system', NOW(), '清华大模型，学术场景优化');

-- Moonshot AI (Kimi)
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time, remark)
VALUES 
('Moonshot AI', 'moonshot', 'moonshot-v1-8k', 'https://api.moonshot.cn/v1', '/chat/completions',
 8192, 0.70, 0.90, '1', 65, '0', 'system', NOW(), '超长上下文，适合长文档');
