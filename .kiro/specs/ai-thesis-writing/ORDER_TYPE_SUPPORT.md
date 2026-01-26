# 订单类型扩展 - 支持套餐和自选服务

## 概述
扩展订单系统，支持两种订单类型：
1. **套餐订单** (`package`) - 购买预设的会员套餐
2. **服务订单** (`service`) - 购买单个服务（降AI、润色、查重等）

## 数据库变更

### 1. 执行迁移脚本
```bash
mysql -u root -p ry-vue < RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/add_order_type_fields.sql
```

### 2. 新增字段
```sql
ALTER TABLE ai_write_order 
ADD COLUMN order_type VARCHAR(20) NOT NULL DEFAULT 'package' COMMENT '订单类型',
ADD COLUMN item_id BIGINT(20) NOT NULL DEFAULT 0 COMMENT '商品ID';
```

### 3. 表结构（更新后）
```sql
CREATE TABLE ai_write_order (
  order_id          BIGINT(20)      PRIMARY KEY AUTO_INCREMENT,
  order_no          VARCHAR(64)     NOT NULL UNIQUE,
  user_id           BIGINT(20)      NOT NULL,
  order_type        VARCHAR(20)     NOT NULL DEFAULT 'package',  -- 新增
  item_id           BIGINT(20)      NOT NULL DEFAULT 0,          -- 新增
  package_id        BIGINT(20)      NULL,                        -- 改为可空
  amount            DECIMAL(10,2)   NOT NULL,
  payment_method    VARCHAR(20)     NOT NULL,
  status            VARCHAR(20)     NOT NULL,
  expired_at        DATETIME        NOT NULL,
  ...
);
```

## 代码变更

### 1. 实体类更新 ✅
**文件**: `module_thesis/entity/do/order_do.py`

```python
class AiWriteOrder(Base):
    order_id = Column(BigInteger, primary_key=True)
    order_no = Column(String(64), nullable=False, unique=True)
    user_id = Column(BigInteger, nullable=False)
    order_type = Column(String(20), nullable=False, server_default='package')  # 新增
    item_id = Column(BigInteger, nullable=False, server_default='0')           # 新增
    package_id = Column(BigInteger, nullable=True)  # 改为可空
    ...
```

### 2. 创建订单方法更新 ✅
**文件**: `module_thesis/service/order_service.py`

```python
async def create_order(
    cls,
    query_db: AsyncSession,
    user_id: int,
    order_type: str,  # 'package' 或 'service'
    item_id: int,     # 套餐ID或服务ID
    amount: Decimal,
    payment_method: str = 'wechat'
) -> CrudResponseModel:
    order_data = {
        'order_no': cls._generate_order_no(),
        'user_id': user_id,
        'order_type': order_type,
        'item_id': item_id,
        'package_id': item_id if order_type == 'package' else None,
        'amount': amount,
        'payment_method': payment_method,
        'status': 'pending',
        'expired_at': datetime.now() + timedelta(minutes=30),
    }
    ...
```

### 3. 支付处理方法更新 ✅
**文件**: `module_thesis/service/order_service.py`

```python
async def process_payment(
    cls,
    query_db: AsyncSession,
    order_no: str,
    transaction_id: str,
    payment_time: datetime = None
) -> CrudResponseModel:
    order = await OrderDao.get_order_by_order_no(query_db, order_no)
    
    # 更新订单状态
    await OrderDao.update_order_status(...)
    
    # 根据订单类型处理
    if order.order_type == 'package':
        # 激活套餐
        await MemberService.activate_membership(
            query_db, order.user_id, order.item_id, auto_commit=False
        )
    elif order.order_type == 'service':
        # 处理服务订单
        service = await FeatureServiceDao.get_service_by_id(query_db, order.item_id)
        # 增加对应配额
        ...
    
    await query_db.commit()
```

## 前端调用示例

### 购买套餐
```javascript
import { createOrder } from '@/api/thesis/order'

// 购买套餐
const buyPackage = async (packageId, amount) => {
  const res = await createOrder({
    orderType: 'package',
    itemId: packageId,
    amount: amount,
    paymentMethod: 'mock'
  })
  console.log('订单创建成功:', res.data.order_no)
}
```

### 购买单个服务
```javascript
// 购买降AI服务
const buyService = async (serviceId, amount) => {
  const res = await createOrder({
    orderType: 'service',
    itemId: serviceId,
    amount: amount,
    paymentMethod: 'mock'
  })
  console.log('订单创建成功:', res.data.order_no)
}
```

## 服务订单处理逻辑

### 功能服务表
```sql
CREATE TABLE ai_write_feature_service (
  service_id        BIGINT(20)      PRIMARY KEY,
  service_name      VARCHAR(50)     NOT NULL,
  service_type      VARCHAR(30)     NOT NULL,  -- 'de_ai', 'polish', 'plagiarism_check'
  price             DECIMAL(10,2)   NOT NULL,
  billing_unit      VARCHAR(20)     NOT NULL,  -- 'per_word', 'per_paper'
  ...
);
```

### 服务类型映射
| 服务类型 | 说明 | 计费单位 |
|---------|------|---------|
| `de_ai` | 降AI检测 | 按字数 |
| `polish` | 论文润色 | 按字数 |
| `plagiarism_check` | 查重检测 | 按篇 |
| `aigc_detection` | AIGC检测 | 按篇 |
| `manual_review` | 人工审核 | 按篇 |

### 服务订单处理示例
```python
elif order.order_type == 'service':
    service = await FeatureServiceDao.get_service_by_id(query_db, order.item_id)
    if service:
        if service.billing_unit == 'per_word':
            # 按字数计费：增加字数配额
            word_quota = calculate_word_quota(service.price, order.amount)
            await MemberService.add_word_quota(
                query_db, order.user_id, word_quota, auto_commit=False
            )
        elif service.billing_unit == 'per_paper':
            # 按篇计费：增加使用次数
            usage_quota = calculate_usage_quota(service.price, order.amount)
            await MemberService.add_usage_quota(
                query_db, order.user_id, usage_quota, auto_commit=False
            )
```

## 测试步骤

### 1. 执行数据库迁移
```bash
mysql -u root -p ry-vue < add_order_type_fields.sql
```

### 2. 重启后端服务
```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

### 3. 测试套餐订单
1. 访问套餐页面
2. 选择套餐并购买
3. 使用模拟支付
4. 验证配额增加

### 4. 测试服务订单（待实现前端）
```bash
curl -X POST http://localhost:8000/thesis/order/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "order_type=service&item_id=1&amount=10.00&payment_method=mock"
```

## 后续开发任务

### 1. 服务列表页面
创建服务选购页面，展示所有可购买的单项服务：
- 降AI检测
- 论文润色
- 查重检测
- AIGC检测
- 人工审核

### 2. 服务订单处理完善
完善 `process_payment` 中的服务订单处理逻辑：
- 根据服务类型增加对应配额
- 记录服务购买历史
- 支持服务有效期

### 3. 订单详情页面
显示订单详细信息，区分套餐订单和服务订单：
- 套餐订单：显示套餐名称、配额信息
- 服务订单：显示服务名称、计费单位

### 4. 订单列表优化
在订单列表中显示订单类型标签：
- 套餐订单：蓝色标签
- 服务订单：绿色标签

## 兼容性说明

### 向后兼容
- `package_id` 字段保留，确保旧数据可读
- 新订单同时填充 `item_id` 和 `package_id`（套餐订单）
- 旧代码仍可使用 `package_id` 访问套餐订单

### 迁移策略
1. 执行迁移脚本，添加新字段
2. 更新现有数据，填充 `order_type` 和 `item_id`
3. 更新代码，使用新字段
4. 测试验证
5. 逐步废弃 `package_id` 字段

## 完成状态
✅ 数据库迁移脚本已创建
✅ 实体类已更新
✅ 创建订单方法已更新
✅ 支付处理方法已更新
⏳ 服务订单处理逻辑待完善
⏳ 服务选购页面待开发
⏳ 订单详情页面待优化
