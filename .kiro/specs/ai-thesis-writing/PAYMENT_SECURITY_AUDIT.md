# 支付系统安全审查报告

## 审查时间
2026-01-25

## 审查范围
- 数据库设计
- 配置管理
- 支付提供商实现
- Service层
- Controller层
- 整体支付流程

---

## 🔴 发现的严重问题

### 1. 配置安全问题

#### 问题1.1：敏感信息明文存储 ⚠️ **严重**
**位置**：`sql/payment_schema.sql`
**问题**：API Key、私钥等敏感信息直接存储在JSON字段中，没有加密

**风险**：
- 数据库泄露导致支付密钥泄露
- 内部人员可直接查看密钥
- 日志可能记录敏感信息

**修复方案**：
1. 使用环境变量存储敏感信息
2. 数据库只存储加密后的配置
3. 使用密钥管理服务（KMS）

#### 问题1.2：配置验证不足 ⚠️ **中等**
**位置**：所有Provider的`__init__`方法
**问题**：没有验证配置的完整性和有效性

**风险**：
- 配置错误导致支付失败
- 缺少必需字段导致运行时错误

**修复方案**：
```python
def __init__(self, config: dict):
    # 验证必需字段
    required_fields = ['api_key', 'app_id']
    missing_fields = [f for f in required_fields if f not in config]
    if missing_fields:
        raise ServiceException(message=f'配置缺少必需字段: {missing_fields}')
    
    # 验证字段格式
    if not config['api_key'].startswith('sk_'):
        raise ServiceException(message='API Key格式错误')
```

### 2. Webhook安全问题

#### 问题2.1：签名验证可能被绕过 ⚠️ **严重**
**位置**：`pingpp_provider.py` line 107
**问题**：当没有配置公钥时，直接返回True跳过验证

```python
if not pub_key_path:
    return True  # 危险！测试环境可以，生产环境不行
```

**风险**：
- 攻击者可以伪造支付回调
- 导致订单被恶意激活

**修复方案**：
```python
if not pub_key_path:
    # 生产环境必须配置公钥
    if not self.config.get('is_test_mode', False):
        raise ServiceException(message='生产环境必须配置Webhook公钥')
    logger.warning('测试环境：跳过Webhook签名验证')
    return True
```

#### 问题2.2：支付宝签名验证修改了原始数据 ⚠️ **严重**
**位置**：`alipay_provider.py` line 117
**问题**：使用`data.pop()`修改了原始数据

```python
sign = data.pop('sign', None)  # 危险！修改了原始数据
```

**风险**：
- 如果验证失败需要重试，数据已被破坏
- 日志记录的数据不完整

**修复方案**：
```python
# 复制数据，不修改原始数据
data_copy = data.copy()
sign = data_copy.pop('sign', None)
sign_type = data_copy.pop('sign_type', 'RSA2')
```

### 3. 金额处理问题

#### 问题3.1：金额精度丢失 ⚠️ **中等**
**位置**：多处使用`float(amount)`
**问题**：浮点数精度问题可能导致金额不准确

**风险**：
- 0.1 + 0.2 != 0.3
- 累计误差

**修复方案**：
```python
# 始终使用Decimal处理金额
from decimal import Decimal

# 错误
amount = float(response.get('total_amount', 0))

# 正确
amount = Decimal(str(response.get('total_amount', '0')))
```

#### 问题3.2：金额转换没有四舍五入 ⚠️ **中等**
**位置**：`pingpp_provider.py` line 48
**问题**：`int(amount * 100)` 可能丢失精度

**修复方案**：
```python
# 使用Decimal的quantize方法
from decimal import Decimal, ROUND_HALF_UP

amount_fen = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
```

### 4. 异常处理问题

#### 问题4.1：异常信息泄露 ⚠️ **中等**
**位置**：所有Provider的异常处理
**问题**：直接返回原始异常信息

```python
except Exception as e:
    raise ServiceException(message=f'Ping++创建支付失败: {str(e)}')
```

**风险**：
- 泄露内部实现细节
- 泄露配置信息
- 泄露系统路径

**修复方案**：
```python
except Exception as e:
    logger.error(f'Ping++创建支付失败: {str(e)}', exc_info=True)
    # 返回通用错误信息
    raise ServiceException(message='支付创建失败，请稍后重试')
```

### 5. 并发安全问题

#### 问题5.1：支付流水可能重复创建 ⚠️ **严重**
**位置**：`payment_gateway_service.py` line 90
**问题**：没有检查支付流水是否已存在

**风险**：
- 重复提交导致多次扣款
- 订单状态混乱

**修复方案**：
```python
# 检查是否已存在支付流水
existing = await PaymentTransactionDao.get_transaction_by_order_no(query_db, order_no)
if existing and existing.status == 'pending':
    # 返回已存在的支付信息
    return {
        'payment_id': existing.payment_id,
        'order_no': existing.order_no,
        ...
    }
```

#### 问题5.2：订单状态没有加锁 ⚠️ **严重**
**位置**：`payment_controller.py` line 50
**问题**：检查订单状态和创建支付之间没有加锁

**风险**：
- 并发请求可能创建多个支付
- 订单状态竞争条件

**修复方案**：
```python
# 使用数据库行锁
from sqlalchemy import select
from module_thesis.entity.do.order_do import Order

# 加锁查询订单
result = await query_db.execute(
    select(Order)
    .where(Order.order_id == order_id)
    .with_for_update()  # 行锁
)
order = result.scalar_one_or_none()
```

### 6. 日志安全问题

#### 问题6.1：日志可能记录敏感信息 ⚠️ **中等**
**位置**：多处日志记录
**问题**：可能记录支付凭证、密钥等敏感信息

**修复方案**：
```python
# 创建日志过滤器
def mask_sensitive_data(data: dict) -> dict:
    """脱敏敏感数据"""
    sensitive_keys = ['api_key', 'private_key', 'credential', 'password']
    masked = data.copy()
    for key in sensitive_keys:
        if key in masked:
            masked[key] = '***MASKED***'
    return masked

# 使用
logger.info(f'创建支付成功: {mask_sensitive_data(result)}')
```

---

## 🟡 发现的中等问题

### 7. 配置管理问题

#### 问题7.1：缺少配置版本控制
**建议**：添加配置版本字段，支持配置回滚

#### 问题7.2：缺少配置变更审计
**建议**：记录配置变更历史

### 8. 错误处理问题

#### 问题8.1：缺少重试机制
**建议**：网络请求失败时自动重试

#### 问题8.2：缺少熔断机制
**建议**：提供商连续失败时自动切换

### 9. 监控问题

#### 问题9.1：缺少支付成功率监控
**建议**：记录支付成功率、失败率

#### 问题9.2：缺少异常告警
**建议**：支付失败时发送告警

---

## ✅ 做得好的地方

1. ✅ 使用抽象基类统一接口
2. ✅ SDK延迟加载，容错性好
3. ✅ 支持多提供商，灵活切换
4. ✅ 完整的流水记录
5. ✅ 详细的文档注释

---

## 🔧 修复优先级

### P0（立即修复）
1. ✅ 配置加密存储
2. ✅ Webhook签名验证不能跳过（生产环境）
3. ✅ 支付宝签名验证不修改原始数据
4. ✅ 支付流水防重复
5. ✅ 订单状态加锁

### P1（尽快修复）
1. ✅ 金额使用Decimal处理
2. ✅ 配置验证
3. ✅ 异常信息脱敏
4. ✅ 日志脱敏

### P2（后续优化）
1. 配置版本控制
2. 重试机制
3. 熔断机制
4. 监控告警

---

## 📋 修复清单

### 立即修复（P0）

- [ ] 1. 实现配置加密存储
- [ ] 2. 修复Webhook签名验证逻辑
- [ ] 3. 修复支付宝签名验证
- [ ] 4. 添加支付流水防重复
- [ ] 5. 添加订单状态锁

### 尽快修复（P1）

- [ ] 6. 统一使用Decimal处理金额
- [ ] 7. 添加配置验证
- [ ] 8. 异常信息脱敏
- [ ] 9. 日志脱敏

### 后续优化（P2）

- [ ] 10. 配置版本控制
- [ ] 11. 重试机制
- [ ] 12. 熔断机制
- [ ] 13. 监控告警

---

## 🔒 安全建议

### 1. 配置安全
- ✅ 使用环境变量存储敏感信息
- ✅ 数据库配置加密存储
- ✅ 定期轮换密钥
- ✅ 限制配置访问权限

### 2. 通信安全
- ✅ 所有回调地址使用HTTPS
- ✅ 验证Webhook签名
- ✅ 使用TLS 1.2+
- ✅ 证书有效期检查

### 3. 数据安全
- ✅ 敏感数据加密存储
- ✅ 日志脱敏
- ✅ 定期备份
- ✅ 访问控制

### 4. 业务安全
- ✅ 订单防重复提交
- ✅ 金额验证
- ✅ 状态机验证
- ✅ 限流防刷

### 5. 运维安全
- ✅ 监控告警
- ✅ 异常追踪
- ✅ 审计日志
- ✅ 应急预案

---

## 📝 总结

### 发现的问题统计
- 🔴 严重问题：6个
- 🟡 中等问题：6个
- 🟢 轻微问题：0个

### 修复建议
1. **立即修复P0问题**（预计2小时）
2. **尽快修复P1问题**（预计3小时）
3. **后续优化P2问题**（预计5小时）

### 安全评分
- 修复前：⭐⭐⭐☆☆ (3/5)
- 修复后：⭐⭐⭐⭐⭐ (5/5)

---

**审查人**: Kiro AI Assistant  
**审查时间**: 2026-01-25  
**下次审查**: 修复完成后
