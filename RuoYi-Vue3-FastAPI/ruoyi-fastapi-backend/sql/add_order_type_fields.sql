-- 为订单表添加订单类型和商品ID字段
-- 支持套餐订单和自选服务订单

-- 注意：请根据实际数据库名修改或删除 USE 语句
-- USE `ry-vue`;  -- 如果数据库名包含特殊字符，需要用反引号包裹

-- 1. 添加 order_type 字段
ALTER TABLE ai_write_order 
ADD COLUMN order_type VARCHAR(20) NOT NULL DEFAULT 'package' COMMENT '订单类型（package-套餐, service-服务）' AFTER user_id;

-- 2. 添加 item_id 字段
ALTER TABLE ai_write_order 
ADD COLUMN item_id BIGINT(20) NOT NULL DEFAULT 0 COMMENT '商品ID（套餐ID或服务ID）' AFTER order_type;

-- 3. 更新现有数据：将 package_id 的值复制到 item_id
UPDATE ai_write_order 
SET item_id = package_id, 
    order_type = 'package'
WHERE item_id = 0;

-- 4. 添加索引
ALTER TABLE ai_write_order 
ADD INDEX idx_order_type (order_type),
ADD INDEX idx_item_id (item_id);

-- 5. package_id 字段保留用于兼容性，但可以设置为可空
ALTER TABLE ai_write_order 
MODIFY COLUMN package_id BIGINT(20) NULL COMMENT '套餐ID（兼容字段，建议使用item_id）';

-- 查看修改后的表结构
DESCRIBE ai_write_order;

-- 验证数据
SELECT order_id, order_no, order_type, item_id, package_id, amount, status 
FROM ai_write_order 
LIMIT 5;
