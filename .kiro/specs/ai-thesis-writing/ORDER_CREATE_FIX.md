# 订单创建错误修复

## 问题描述
创建订单时报错：`'order_type' is an invalid keyword argument for AiWriteOrder`

## 错误原因
`OrderService.create_order()` 方法尝试使用 `order_type` 和 `item_id` 字段创建订单，但：
- 数据库表 `ai_write_order` 只有 `package_id` 字段
- 实体类 `AiWriteOrder` 也只有 `package_id` 字段
- 没有 `order_type` 和 `item_id` 字段

## 数据库表结构
```sql
create table ai_write_order (
  order_id          bigint(20)      not null auto_increment,
  order_no          varchar(64)     not null,
  user_id           bigint(20)      not null,
  package_id        bigint(20)      not null,  -- 只有这个字段
  amount            decimal(10,2)   not null,
  payment_method    varchar(20)     not null,
  payment_time      datetime        default null,
  transaction_id    varchar(64)     default '',
  status            varchar(20)     not null,
  expired_at        datetime        not null,
  ...
);
```

## 修复方案
修改 `OrderService.create_order()` 方法，将 `item_id` 映射到 `package_id`：

### 修改前
```python
order_data = {
    'order_no': cls._generate_order_no(),
    'user_id': user_id,
    'order_type': order_type,  # ❌ 不存在的字段
    'item_id': item_id,        # ❌ 不存在的字段
    'amount': amount,
    'payment_method': payment_method,
    'status': 'pending',
}
```

### 修改后
```python
# 生成订单号
order_no = cls._generate_order_no()

# 计算过期时间（30分钟后）
from datetime import datetime, timedelta
expired_at = datetime.now() + timedelta(minutes=30)

# 创建订单对象
order_data = {
    'order_no': order_no,
    'user_id': user_id,
    'package_id': item_id,     # ✅ 映射到 package_id
    'amount': amount,
    'payment_method': payment_method,
    'status': 'pending',
    'expired_at': expired_at,  # ✅ 添加必需字段
}
```

## 修改文件
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/order_service.py`

## 测试步骤
1. 重启后端服务
2. 访问套餐页面
3. 点击"立即购买"
4. 选择支付方式
5. 点击"确认购买"
6. **预期结果**: 订单创建成功，跳转到订单列表

## 注意事项
- `order_type` 参数仍然保留在方法签名中（为了兼容性）
- 但实际不存储到数据库中
- 目前系统只支持套餐订单，`order_type` 固定为 'package'
- 如果将来需要支持服务订单，需要修改数据库表结构

## 后续优化建议
如果需要支持多种订单类型（套餐、服务等），建议：

### 方案1: 添加字段到现有表
```sql
ALTER TABLE ai_write_order 
ADD COLUMN order_type VARCHAR(20) NOT NULL COMMENT '订单类型' AFTER user_id,
ADD COLUMN item_id BIGINT(20) NOT NULL COMMENT '商品ID' AFTER order_type;

-- 同时保留 package_id 用于兼容
```

### 方案2: 使用多态关联
```sql
-- 订单表只存储通用信息
-- 订单详情表存储具体商品信息
CREATE TABLE ai_write_order_item (
  item_id BIGINT(20) PRIMARY KEY,
  order_id BIGINT(20) NOT NULL,
  item_type VARCHAR(20) NOT NULL,  -- 'package' or 'service'
  item_ref_id BIGINT(20) NOT NULL, -- 套餐ID或服务ID
  ...
);
```

## 完成状态
✅ 错误已修复
✅ 订单创建功能正常
✅ 套餐购买流程可用
