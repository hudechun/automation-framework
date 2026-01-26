-- =============================================
-- AI论文写作系统 - 支付系统数据库表
-- =============================================

-- 支付配置表（支持多种支付方式）
CREATE TABLE IF NOT EXISTS ai_write_payment_config (
  config_id         BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '配置ID',
  provider_type     VARCHAR(20)     NOT NULL                   COMMENT '支付提供商（alipay/wechat/pingpp）',
  provider_name     VARCHAR(50)     NOT NULL                   COMMENT '提供商名称',
  
  -- 通用配置
  config_data       JSON            NOT NULL                   COMMENT '配置数据（JSON格式）',
  
  -- 支持的支付渠道
  supported_channels JSON           NOT NULL                   COMMENT '支持的支付渠道',
  
  -- 状态控制
  is_enabled        CHAR(1)         DEFAULT '1'                COMMENT '是否启用（0否 1是）',
  is_default        CHAR(1)         DEFAULT '0'                COMMENT '是否默认（0否 1是）',
  priority          INT(4)          DEFAULT 0                  COMMENT '优先级（数字越大优先级越高）',
  
  -- 费率配置
  fee_rate          DECIMAL(5,4)    DEFAULT 0.0060             COMMENT '手续费率',
  
  -- 标准字段
  status            CHAR(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志（0存在 2删除）',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (config_id),
  INDEX idx_provider (provider_type, is_enabled),
  INDEX idx_priority (priority DESC, is_enabled)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4 COMMENT = '支付配置表';

-- 支付流水表
CREATE TABLE IF NOT EXISTS ai_write_payment_transaction (
  transaction_id    BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '流水ID',
  order_id          BIGINT(20)      NOT NULL                   COMMENT '订单ID',
  order_no          VARCHAR(50)     NOT NULL                   COMMENT '订单号',
  
  -- 支付信息
  provider_type     VARCHAR(20)     NOT NULL                   COMMENT '支付提供商',
  payment_id        VARCHAR(100)    NOT NULL                   COMMENT '支付ID（第三方）',
  payment_channel   VARCHAR(50)     NOT NULL                   COMMENT '支付渠道',
  
  -- 金额信息
  amount            DECIMAL(10,2)   NOT NULL                   COMMENT '支付金额',
  fee_amount        DECIMAL(10,2)   DEFAULT 0.00               COMMENT '手续费',
  
  -- 状态信息
  status            VARCHAR(20)     DEFAULT 'pending'          COMMENT '状态（pending/success/failed/refunded）',
  transaction_no    VARCHAR(100)                               COMMENT '第三方交易号',
  
  -- 时间信息
  payment_time      DATETIME                                   COMMENT '支付时间',
  refund_time       DATETIME                                   COMMENT '退款时间',
  
  -- 标准字段
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志（0存在 2删除）',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (transaction_id),
  UNIQUE KEY uk_payment_id (payment_id),
  INDEX idx_order_no (order_no),
  INDEX idx_status (status),
  INDEX idx_create_time (create_time)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4 COMMENT = '支付流水表';

-- =============================================
-- 初始化配置数据
-- =============================================

-- Ping++配置（优先级最高）
INSERT INTO ai_write_payment_config (provider_type, provider_name, config_data, supported_channels, is_enabled, priority, fee_rate, status, create_by, create_time) VALUES
('pingpp', 'Ping++聚合支付', 
  '{"api_key": "sk_test_xxxxxx", "app_id": "app_xxxxxx", "private_key_path": "/path/to/key.pem", "pub_key_path": "/path/to/pub_key.pem", "webhook_url": "https://yourdomain.com/api/payment/webhook/pingpp"}',
  '["alipay_pc", "alipay_wap", "alipay_qr", "wx_pub", "wx_lite", "wx_wap", "wx_pub_qr"]',
  '0', 100, 0.0100, '0', 'admin', NOW());

-- 支付宝SDK配置
INSERT INTO ai_write_payment_config (provider_type, provider_name, config_data, supported_channels, is_enabled, priority, fee_rate, status, create_by, create_time) VALUES
('alipay', '支付宝直连', 
  '{"app_id": "2021001234567890", "private_key": "MIIEvQIBADANBgkqhkiG9w0...", "alipay_public_key": "MIIBIjANBgkqhkiG9w0...", "notify_url": "https://yourdomain.com/api/payment/webhook/alipay", "return_url": "https://yourdomain.com/payment/success", "is_sandbox": false}',
  '["alipay_pc", "alipay_wap", "alipay_qr"]',
  '0', 90, 0.0060, '0', 'admin', NOW());

-- 微信SDK配置
INSERT INTO ai_write_payment_config (provider_type, provider_name, config_data, supported_channels, is_enabled, priority, fee_rate, status, create_by, create_time) VALUES
('wechat', '微信支付直连', 
  '{"app_id": "wx1234567890abcdef", "mch_id": "1234567890", "api_v3_key": "your_api_v3_key_32_characters", "cert_serial_no": "1234567890ABCDEF", "private_cert_path": "/path/to/apiclient_key.pem", "notify_url": "https://yourdomain.com/api/payment/webhook/wechat", "is_sandbox": false}',
  '["wx_native", "wx_jsapi", "wx_h5"]',
  '0', 80, 0.0060, '0', 'admin', NOW());
