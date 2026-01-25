-- ============================================
-- 浏览器与桌面自动化框架 - 数据库表结构
-- ============================================
-- 数据库版本: MySQL 8.0+
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_unicode_ci
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS automation_framework 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE automation_framework;

-- ============================================
-- 1. 任务相关表
-- ============================================

-- 任务表
CREATE TABLE IF NOT EXISTS `tasks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL COMMENT '任务名称',
    `description` TEXT COMMENT '任务描述',
    `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型: browser, desktop, hybrid',
    `actions` JSON NOT NULL COMMENT '操作列表',
    `config` JSON COMMENT '任务配置',
    `status` VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '状态: pending, running, completed, failed',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_name` (`name`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';

-- 调度表
CREATE TABLE IF NOT EXISTS `schedules` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `task_id` INT NOT NULL COMMENT '关联任务ID',
    `schedule_type` VARCHAR(50) NOT NULL COMMENT '调度类型: once, interval, cron',
    `schedule_config` JSON NOT NULL COMMENT '调度配置',
    `enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    `next_run_time` DATETIME COMMENT '下次运行时间',
    `last_run_time` DATETIME COMMENT '上次运行时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_enabled` (`enabled`),
    INDEX `idx_next_run_time` (`next_run_time`),
    FOREIGN KEY (`task_id`) REFERENCES `tasks`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='调度表';

-- 执行记录表
CREATE TABLE IF NOT EXISTS `execution_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `task_id` INT NOT NULL COMMENT '关联任务ID',
    `status` VARCHAR(50) NOT NULL COMMENT '状态: running, completed, failed',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME COMMENT '结束时间',
    `duration` INT COMMENT '执行时长（秒）',
    `logs` TEXT COMMENT '执行日志',
    `screenshots` JSON COMMENT '截图路径列表',
    `error_message` TEXT COMMENT '错误信息',
    `error_stack` TEXT COMMENT '错误堆栈',
    `result` JSON COMMENT '执行结果',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_start_time` (`start_time`),
    FOREIGN KEY (`task_id`) REFERENCES `tasks`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行记录表';

-- ============================================
-- 2. 会话相关表
-- ============================================

-- 会话表
CREATE TABLE IF NOT EXISTS `sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` VARCHAR(255) NOT NULL UNIQUE COMMENT '会话ID',
    `state` VARCHAR(50) NOT NULL DEFAULT 'created' COMMENT '状态: created, running, paused, stopped, failed',
    `driver_type` VARCHAR(50) NOT NULL COMMENT '驱动类型: browser, desktop',
    `session_metadata` JSON COMMENT '会话元数据（包含user_id和task_id）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_session_id` (`session_id`),
    INDEX `idx_state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- 会话检查点表
CREATE TABLE IF NOT EXISTS `session_checkpoints` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` INT NOT NULL COMMENT '关联会话ID',
    `checkpoint_name` VARCHAR(255) NOT NULL COMMENT '检查点名称',
    `state_data` JSON NOT NULL COMMENT '状态数据',
    `actions_completed` INT NOT NULL DEFAULT 0 COMMENT '已完成的操作数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_session_id` (`session_id`),
    INDEX `idx_created_at` (`created_at`),
    FOREIGN KEY (`session_id`) REFERENCES `sessions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话检查点表';

-- ============================================
-- 3. 配置和日志表
-- ============================================

-- 模型配置表
CREATE TABLE IF NOT EXISTS `model_configs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT '配置名称',
    `provider` VARCHAR(50) NOT NULL COMMENT '提供商: openai, anthropic, qwen, ollama',
    `model` VARCHAR(100) NOT NULL COMMENT '模型名称',
    `api_key` VARCHAR(255) COMMENT 'API密钥',
    `params` JSON COMMENT '模型参数',
    `enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型配置表';

-- 模型性能指标表
CREATE TABLE IF NOT EXISTS `model_metrics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `model_config_id` INT NOT NULL COMMENT '关联模型配置ID',
    `latency` FLOAT NOT NULL COMMENT '延迟（秒）',
    `cost` FLOAT COMMENT '成本',
    `tokens` INT COMMENT 'Token数',
    `success` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否成功',
    `error_message` TEXT COMMENT '错误信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_model_config_id` (`model_config_id`),
    INDEX `idx_created_at` (`created_at`),
    FOREIGN KEY (`model_config_id`) REFERENCES `model_configs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型性能指标表';

-- 系统日志表
CREATE TABLE IF NOT EXISTS `system_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `level` VARCHAR(20) NOT NULL COMMENT '日志级别: debug, info, warning, error, critical',
    `message` TEXT NOT NULL COMMENT '日志消息',
    `module` VARCHAR(255) COMMENT '模块名称',
    `function` VARCHAR(255) COMMENT '函数名称',
    `line_number` INT COMMENT '行号',
    `extra_data` JSON COMMENT '额外数据',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_level` (`level`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- 通知配置表
CREATE TABLE IF NOT EXISTS `notification_configs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT '配置名称',
    `notification_type` VARCHAR(50) NOT NULL COMMENT '通知类型: email, webhook, slack, dingtalk, wechat_work',
    `config` JSON NOT NULL COMMENT '通知配置',
    `enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知配置表';

-- ============================================
-- 4. 文件和插件表
-- ============================================

-- 文件存储表
CREATE TABLE IF NOT EXISTS `file_storage` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
    `file_path` VARCHAR(512) NOT NULL COMMENT '文件路径',
    `file_type` VARCHAR(50) NOT NULL COMMENT '文件类型: screenshot, log, video, export',
    `file_size` INT NOT NULL COMMENT '文件大小（字节）',
    `mime_type` VARCHAR(100) COMMENT 'MIME类型',
    `related_type` VARCHAR(50) COMMENT '关联类型: task, execution, session',
    `related_id` INT COMMENT '关联ID',
    `metadata` JSON COMMENT '元数据',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_file_type` (`file_type`),
    INDEX `idx_related` (`related_type`, `related_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件存储表';

-- 插件表
CREATE TABLE IF NOT EXISTS `plugins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT '插件名称',
    `version` VARCHAR(50) NOT NULL COMMENT '版本号',
    `description` TEXT COMMENT '插件描述',
    `plugin_type` VARCHAR(50) NOT NULL COMMENT '插件类型: action, driver, agent, integration',
    `manifest` JSON NOT NULL COMMENT '插件清单',
    `config` JSON COMMENT '插件配置',
    `enabled` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件表';

-- 性能指标表
CREATE TABLE IF NOT EXISTS `performance_metrics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `metric_type` VARCHAR(50) NOT NULL COMMENT '指标类型: cpu, memory, disk, network, task',
    `metric_name` VARCHAR(100) NOT NULL COMMENT '指标名称',
    `value` FLOAT NOT NULL COMMENT '指标值',
    `unit` VARCHAR(20) COMMENT '单位',
    `metadata` JSON COMMENT '元数据',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_metric_type` (`metric_type`),
    INDEX `idx_metric_name` (`metric_name`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='性能指标表';

-- ============================================
-- 5. Aerich迁移表（Tortoise-ORM使用）
-- ============================================

-- Aerich迁移记录表
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `version` VARCHAR(255) NOT NULL COMMENT '版本号',
    `app` VARCHAR(100) NOT NULL COMMENT '应用名称',
    `content` JSON NOT NULL COMMENT '迁移内容',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库迁移记录表';

-- ============================================
-- 6. 初始数据
-- ============================================

-- 插入默认模型配置（示例）
INSERT INTO `model_configs` (`name`, `provider`, `model`, `enabled`, `params`) VALUES
('qwen_default', 'qwen', 'qwen-turbo', TRUE, '{"temperature": 0.7, "max_tokens": 2000}'),
('openai_default', 'openai', 'gpt-4', FALSE, '{"temperature": 0.7, "max_tokens": 2000}'),
('anthropic_default', 'anthropic', 'claude-3-opus-20240229', FALSE, '{"temperature": 0.7, "max_tokens": 4096}')
ON DUPLICATE KEY UPDATE `name`=`name`;

-- 插入默认通知配置（示例）
INSERT INTO `notification_configs` (`name`, `notification_type`, `config`, `enabled`) VALUES
('email_default', 'email', '{"smtp_host": "smtp.gmail.com", "smtp_port": 587}', FALSE),
('webhook_default', 'webhook', '{"url": "https://example.com/webhook"}', FALSE)
ON DUPLICATE KEY UPDATE `name`=`name`;

-- ============================================
-- 7. 视图（可选）
-- ============================================

-- 任务执行统计视图
CREATE OR REPLACE VIEW `v_task_statistics` AS
SELECT 
    t.id AS task_id,
    t.name AS task_name,
    COUNT(er.id) AS total_executions,
    SUM(CASE WHEN er.status = 'completed' THEN 1 ELSE 0 END) AS successful_executions,
    SUM(CASE WHEN er.status = 'failed' THEN 1 ELSE 0 END) AS failed_executions,
    ROUND(SUM(CASE WHEN er.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(er.id), 2) AS success_rate,
    AVG(er.duration) AS avg_duration,
    MAX(er.created_at) AS last_execution_time
FROM tasks t
LEFT JOIN execution_records er ON t.id = er.task_id
GROUP BY t.id, t.name;

-- 最近执行记录视图
CREATE OR REPLACE VIEW `v_recent_executions` AS
SELECT 
    er.id,
    t.name AS task_name,
    er.status,
    er.start_time,
    er.end_time,
    er.duration,
    er.error_message
FROM execution_records er
JOIN tasks t ON er.task_id = t.id
ORDER BY er.created_at DESC
LIMIT 100;

-- ============================================
-- 完成
-- ============================================

-- 显示所有表
SHOW TABLES;

-- 显示表结构统计
SELECT 
    TABLE_NAME AS '表名',
    TABLE_COMMENT AS '说明',
    TABLE_ROWS AS '行数',
    ROUND(DATA_LENGTH/1024/1024, 2) AS '数据大小(MB)',
    ROUND(INDEX_LENGTH/1024/1024, 2) AS '索引大小(MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'automation_framework'
ORDER BY TABLE_NAME;
