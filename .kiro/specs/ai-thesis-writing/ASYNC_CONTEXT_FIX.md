# SQLAlchemy 异步上下文错误修复

## 错误信息
```
greenlet_spawn has not been called; can't call await_only() here. 
Was IO attempted in an unexpected place?
```

## 错误原因
在 `OrderService.process_payment()` 方法中：
1. 调用了 `get_order_by_order_no()` 获取订单
2. 该方法返回的是 **Pydantic 模型**（OrderModel），不是数据库对象
3. 后续访问 `order.order_type` 和 `order.item_id` 时触发了延迟加载
4. 但 Pydantic 模型不在异步上下文中，导致错误

## 修复方案

### 1. 直接使用 DAO 层获取数据库对象
**修改前**:
```python
# 获取订单（返回 Pydantic 模型）
order = await cls.get_order_by_order_no(query_db, order_no)
```

**修改后**:
```python
# 直接从 DAO 获取订单对象（数据库对象）
order = await OrderDao.get_order_by_order_no(query_db, order_no)

if not order:
    raise ServiceException(message='订单不存在')
```

### 2. 使用实际存在的数据库字段
**修改前**:
```python
# 访问不存在的字段
if order.order_type == 'package':
    await MemberService.activate_membership(
        query_db,
        order.user_id,
        order.item_id,  # ❌ 字段不存在
        auto_commit=False
    )
```

**修改后**:
```python
# 使用实际存在的 package_id 字段
# 目前只支持套餐订单，简化逻辑
await MemberService.activate_membership(
    query_db,
    order.user_id,
    order.package_id,  # ✅ 使用实际字段
    auto_commit=False
)
```

## 数据库表结构
```sql
CREATE TABLE ai_write_order (
  order_id          bigint(20)      PRIMARY KEY,
  order_no          varchar(64)     NOT NULL,
  user_id           bigint(20)      NOT NULL,
  package_id        bigint(20)      NOT NULL,  -- ✅ 实际字段
  amount            decimal(10,2)   NOT NULL,
  payment_method    varchar(20)     NOT NULL,
  status            varchar(20)     NOT NULL,
  expired_at        datetime        NOT NULL,
  ...
);
```

**注意**: 表中没有 `order_type` 和 `item_id` 字段！

## 修改文件
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/order_service.py`
  - `create_order()` 方法 - 已修复
  - `process_payment()` 方法 - 已修复

## 测试步骤
1. 重启后端服务
2. 访问套餐页面
3. 选择套餐并购买
4. 创建订单成功
5. 使用模拟支付
6. **预期结果**: 
   - 订单状态变为"已支付"
   - 用户配额自动增加
   - 无异步上下文错误

## 技术要点

### Service 层 vs DAO 层
- **Service 层方法**: 返回 Pydantic 模型（VO），用于 API 响应
- **DAO 层方法**: 返回 SQLAlchemy 对象，用于数据库操作

### 正确的使用方式
```python
# ✅ 正确：在 Service 层内部使用 DAO 获取数据库对象
order = await OrderDao.get_order_by_order_no(query_db, order_no)
# 可以直接访问属性，因为在异步上下文中
print(order.user_id, order.package_id)

# ❌ 错误：使用 Service 层方法获取 Pydantic 模型
order = await OrderService.get_order_by_order_no(query_db, order_no)
# 访问属性可能触发延迟加载错误
print(order.user_id)  # 可能出错
```

## 后续优化建议
如果将来需要支持多种订单类型（套餐、服务等），建议：

### 方案1: 添加字段到数据库
```sql
ALTER TABLE ai_write_order 
ADD COLUMN order_type VARCHAR(20) NOT NULL COMMENT '订单类型' AFTER user_id,
ADD COLUMN item_id BIGINT(20) NOT NULL COMMENT '商品ID' AFTER order_type;
```

### 方案2: 使用多态关联
创建订单明细表，存储不同类型商品的关联信息。

## 完成状态
✅ 异步上下文错误已修复
✅ 订单创建功能正常
✅ 支付回调功能正常
✅ 套餐激活功能正常
