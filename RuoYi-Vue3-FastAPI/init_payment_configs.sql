-- 初始化支付配置
-- 插入四种支付方式的默认配置（包括模拟支付）
-- 创建人和更新人都设置为管理员（user_id=1, username='admin'）

-- 支付宝配置
INSERT INTO ai_write_payment_config (
    provider_type,
    provider_name,
    config_data,
    supported_channels,
    is_enabled,
    is_default,
    priority,
    fee_rate,
    status,
    del_flag,
    create_by,
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    'alipay',
    '支付宝直连',
    '{"app_id": "", "private_key": "", "alipay_public_key": "", "notify_url": "", "return_url": "", "is_sandbox": false}',
    '["alipay_pc", "alipay_wap", "alipay_qr"]',
    '0',  -- 默认禁用
    '0',  -- 非默认
    90,   -- 优先级
    0.0060,
    '0',  -- 正常状态
    '0',  -- 未删除
    'admin',  -- 创建人：管理员
    NOW(),
    'admin',  -- 更新人：管理员
    NOW(),
    '支付宝支付配置，需要填写app_id、private_key、alipay_public_key等信息'
) ON DUPLICATE KEY UPDATE 
    update_by = 'admin',
    update_time = NOW();

-- 微信支付配置
INSERT INTO ai_write_payment_config (
    provider_type,
    provider_name,
    config_data,
    supported_channels,
    is_enabled,
    is_default,
    priority,
    fee_rate,
    status,
    del_flag,
    create_by,
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    'wechat',
    '微信支付直连',
    '{"app_id": "", "mch_id": "", "api_v3_key": "", "cert_serial_no": "", "private_cert_path": "", "notify_url": "", "is_sandbox": false}',
    '["wx_native", "wx_jsapi", "wx_h5"]',
    '0',  -- 默认禁用
    '0',  -- 非默认
    80,   -- 优先级
    0.0060,
    '0',  -- 正常状态
    '0',  -- 未删除
    'admin',  -- 创建人：管理员
    NOW(),
    'admin',  -- 更新人：管理员
    NOW(),
    '微信支付配置，需要填写app_id、mch_id、api_v3_key等信息'
) ON DUPLICATE KEY UPDATE 
    update_by = 'admin',
    update_time = NOW();

-- Ping++配置
INSERT INTO ai_write_payment_config (
    provider_type,
    provider_name,
    config_data,
    supported_channels,
    is_enabled,
    is_default,
    priority,
    fee_rate,
    status,
    del_flag,
    create_by,
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    'pingpp',
    'Ping++聚合支付',
    '{"api_key": "", "app_id": "", "private_key_path": "", "pub_key_path": "", "webhook_url": ""}',
    '["alipay_pc", "alipay_wap", "alipay_qr", "wx_pub", "wx_lite", "wx_wap", "wx_pub_qr"]',
    '0',  -- 默认禁用
    '0',  -- 非默认
    100,  -- 优先级最高
    0.0100,
    '0',  -- 正常状态
    '0',  -- 未删除
    'admin',  -- 创建人：管理员
    NOW(),
    'admin',  -- 更新人：管理员
    NOW(),
    'Ping++聚合支付配置，支持多种支付渠道，需要填写api_key、app_id等信息'
) ON DUPLICATE KEY UPDATE 
    update_by = 'admin',
    update_time = NOW();

-- 模拟支付配置（开发调试用）
INSERT INTO ai_write_payment_config (
    provider_type,
    provider_name,
    config_data,
    supported_channels,
    is_enabled,
    is_default,
    priority,
    fee_rate,
    status,
    del_flag,
    create_by,
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    'mock',
    '模拟支付（开发调试）',
    '{"mode": "mock", "auto_success": true, "delay_seconds": 0}',
    '["mock"]',
    '1',  -- 默认启用，方便开发调试
    '0',  -- 非默认
    999,  -- 最高优先级
    0.0000,  -- 无手续费
    '0',  -- 正常状态
    '0',  -- 未删除
    'admin',  -- 创建人：管理员
    NOW(),
    'admin',  -- 更新人：管理员
    NOW(),
    '⚠️ 模拟支付配置，仅用于开发调试，直接模拟支付成功，生产环境请禁用'
) ON DUPLICATE KEY UPDATE 
    update_by = 'admin',
    update_time = NOW();
