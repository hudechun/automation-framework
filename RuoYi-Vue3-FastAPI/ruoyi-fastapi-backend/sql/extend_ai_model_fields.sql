ALTER TABLE ai_write_ai_model_config ADD COLUMN model_type VARCHAR(20) DEFAULT 'language' COMMENT '模型类型' AFTER model_version;

ALTER TABLE ai_write_ai_model_config ADD COLUMN provider VARCHAR(50) DEFAULT '' COMMENT '提供商' AFTER model_type;

ALTER TABLE ai_write_ai_model_config ADD COLUMN params TEXT DEFAULT NULL COMMENT '模型参数JSON' AFTER top_p;

ALTER TABLE ai_write_ai_model_config ADD COLUMN capabilities TEXT DEFAULT NULL COMMENT '模型能力JSON' AFTER params;

UPDATE ai_write_ai_model_config SET provider = model_code WHERE provider = '';

UPDATE ai_write_ai_model_config SET model_type = 'language' WHERE model_type IS NULL OR model_type = '';

CREATE INDEX idx_model_type ON ai_write_ai_model_config(model_type);

CREATE INDEX idx_provider ON ai_write_ai_model_config(provider);
