# 支付系统安全修复指南

## 概述

本文档提供支付系统安全问题的详细修复方案和实施步骤。

---

## 🔴 P0级别修复（立即执行）

### 修复1：配置加密存储

#### 问题描述
敏感配置（API Key、私钥）明文存储在数据库中。

#### 修复方案

**步骤1：安装加密库**
```bash
pip install cryptography
```

**步骤2：创建配置加密工具**
```python
# utils/config_crypto.py
from cryptography.fernet import Fernet
import os
import base64

class ConfigCrypto:
    """配置加密工具"""
    
    @staticmethod
    def get_key():
        """获取加密密钥（从环境变量）"""
        key = os.getenv('CONFIG_ENCRYPTION_KEY')
        if not key:
            raise ValueError('未设置CONFIG_ENCRYPTION_KEY环境变量')
        return key.encode()
    
    @staticmethod
    def encrypt(data: str) -> str:
        """加密配置"""
        f = Fernet(ConfigCrypto.get_key())
        encrypted = f.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """解密配置"""
        f = Fernet(ConfigCrypto.get_key())
        decrypted = f.decrypt(base64.b64decode(encrypted_data))
        return decrypted.decode()
```

**步骤3：生成加密密钥**
```python
# scripts/generate_config_key.py
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f'请将以下密钥添加到.env文件：')
print(f'CONFIG_ENCRYPTION_KEY={key.decode()}')
```

**步骤4：修改配置存储**
```python
# 存储时加密
from utils.config_crypto import ConfigCrypto
import json

config_data = {
    'api_key': 'sk_live_xxxxxx',
    'app_id': 'app_xxxxxx'
}

# 加密敏感字段
sensitive_fields = ['api_key', 'private_key', 'api_v3_key']
for field in sensitive_fields:
    if field in config_data:
        config_data[field] = ConfigCrypto.encrypt(config_data[field])

# 存储到数据库
encrypted_config = json.dumps(config_data)
```

**步骤5：修改配置读取**
```python
# 读取时解密
config_data = json.loads(encrypted_config)

sensitive_fields = ['api_key', 'private_key', 'api_v3_key']
for field in sensitive_fields:
    if field in config_data:
        config_data[field] = ConfigCrypto.decrypt(config_data[field])
```

---

### 修复2：Webhook签名验证增强

#### 修复代码

**Ping++提供商**
```python
def verify_webhook(self, data: dict, signature: str = None) -> bool:
    """验证Webhook签名（安全增强）"""
    try:
        pub_key_path = self.config.get('pub_key_path')
        
        # 生产环境必须配置公钥
        if not pub_key_path:
            is_test_mode = self.config.get('is_test_mode', False)
            if not is_test_mode:
                logger.error('生产环境未配置Webhook公钥')
                raise ServiceException(message='生产环境必须配置Webhook公钥')
            
            logger.warning('测试环境：跳过Webhook签名验证')
            return True
        
        # 验证签名
        result = self.pingpp.Webhook.verify_signature(
            data.encode('utf-8') if isinstance(data, str) else data,
            signature,
            pub_key_path
        )
        
        if not result:
            logger.warning('Ping++ Webhook签名验证失败')
        
        return result
    except Exception as e:
        logger.error(f'Ping++ Webhook签名验证异常: {str(e)}')
        return False
```

**支付宝提供商**
```python
def verify_webhook(self, data: dict, signature: str = None) -> bool:
    """验证Webhook签名（不修改原始数据）"""
    try:
        from alipay.aop.api.util.SignatureUtils import verify_with_rsa
        
        # 复制数据，不修改原始数据
        data_copy = data.copy()
        sign = data_copy.pop('sign', None)
        sign_type = data_copy.pop('sign_type', 'RSA2')
        
        if not sign:
            logger.warning('支付宝Webhook缺少签名')
            return False
        
        # 构建待签名字符串
        sorted_items = sorted(data_copy.items())
        unsigned_string = '&'.join([f'{k}={v}' for k, v in sorted_items if v])
        
        # 验证签名
        result = verify_with_rsa(
            self.config['alipay_public_key'],
            unsigned_string,
            sign,
            sign_type
        )
        
        if not result:
            logger.warning('支付宝Webhook签名验证失败')
        
        return result
    except Exception as e:
        logger.error(f'支付宝Webhook签名验证异常: {str(e)}')
        return False
```

---

### 修复3：支付流水防重复

#### 修复代码

```python
# payment_gateway_service.py

@classmethod
async def create_payment(
    cls,
    query_db: AsyncSession,
    order_id: int,
    order_no: str,
    amount: Decimal,
    channel: str,
    subject: str,
    body: str = '',
    provider_type: str = None,
    **kwargs
) -> Dict:
    """创建支付（防重复）"""
    try:
        # 检查是否已存在待支付的流水
        existing = await PaymentTransactionDao.get_transaction_by_order_no(query_db, order_no)
        if existing and existing.status == 'pending':
            logger.info(f'订单{order_no}已存在待支付流水，返回已有支付信息')
            
            # 返回已存在的支付信息
            return {
                'provider': existing.provider_type,
                'payment_id': existing.payment_id,
                'order_no': existing.order_no,
                'amount': existing.amount,
                'channel': existing.payment_channel,
                'is_existing': True  # 标记为已存在
            }
        
        # 获取支付提供商
        provider, actual_provider_type = await cls.get_provider(query_db, provider_type, channel)
        
        # 创建支付
        result = provider.create_payment(
            order_no=order_no,
            amount=amount,
            channel=channel,
            subject=subject,
            body=body,
            **kwargs
        )
        
        # 记录支付流水
        transaction_data = {
            'order_id': order_id,
            'order_no': order_no,
            'provider_type': actual_provider_type,
            'payment_id': result['payment_id'],
            'payment_channel': channel,
            'amount': amount,
            'fee_amount': Decimal('0.00'),
            'status': 'pending',
            'create_time': datetime.now()
        }
        await PaymentTransactionDao.add_transaction(query_db, transaction_data)
        await query_db.commit()
        
        logger.info(f'创建支付成功: order_no={order_no}, provider={actual_provider_type}')
        
        return result
    except ServiceException:
        await query_db.rollback()
        raise
    except Exception as e:
        await query_db.rollback()
        logger.error(f'创建支付失败: {str(e)}')
        raise ServiceException(message='支付创建失败，请稍后重试')
```

---

### 修复4：订单状态加锁

#### 修复代码

```python
# payment_controller.py

@payment_controller.post('/create')
async def create_payment(
    request: Request,
    order_id: Annotated[int, Query(description='订单ID')],
    channel: Annotated[str, Query(description='支付渠道')],
    provider: Annotated[str | None, Query(description='指定支付提供商')] = None,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, GetCurrentUserDependency()],
):
    """创建支付（加锁）"""
    from sqlalchemy import select
    from module_thesis.entity.do.order_do import Order
    
    # 使用行锁查询订单
    result = await query_db.execute(
        select(Order)
        .where(Order.order_id == order_id)
        .with_for_update()  # 行锁，防止并发
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise ServiceException(message='订单不存在')
    
    # 验证订单所有权
    if order.user_id != current_user.user.user_id:
        raise ServiceException(message='无权操作此订单')
    
    # 验证订单状态
    if order.status != 'pending':
        raise ServiceException(message='订单状态异常')
    
    # 获取客户端IP
    client_ip = request.client.host
    
    # 创建支付
    result = await PaymentGatewayService.create_payment(
        query_db,
        order_id=order.order_id,
        order_no=order.order_no,
        amount=order.amount,
        channel=channel,
        subject=f'购买{order.order_type}',
        body=f'订单号：{order.order_no}',
        provider_type=provider,
        client_ip=client_ip
    )
    
    logger.info(f'创建支付成功: {order.order_no}, 渠道: {channel}')
    return ResponseUtil.success(data=result)
```

---

## 🟡 P1级别修复（尽快执行）

### 修复5：金额使用Decimal处理

#### 修复原则
```python
# ❌ 错误：使用float
amount = float(response.get('total_amount', 0))

# ✅ 正确：使用Decimal
from decimal import Decimal
amount = Decimal(str(response.get('total_amount', '0')))

# ❌ 错误：直接转换
amount_fen = int(amount * 100)

# ✅ 正确：四舍五入
from decimal import ROUND_HALF_UP
amount_fen = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
```

---

### 修复6：配置验证

#### 修复代码

```python
class PaymentProvider(ABC):
    """支付提供商抽象基类"""
    
    def __init__(self, config: dict):
        """初始化支付提供商"""
        self.config = config
        self._validate_config(config)
    
    def _validate_config(self, config: dict):
        """验证配置（子类实现）"""
        pass

class PingppProvider(PaymentProvider):
    """Ping++支付提供商"""
    
    def _validate_config(self, config: dict):
        """验证Ping++配置"""
        required_fields = ['api_key', 'app_id']
        missing_fields = [f for f in required_fields if not config.get(f)]
        
        if missing_fields:
            raise ServiceException(
                message=f'Ping++配置缺少必需字段: {", ".join(missing_fields)}'
            )
        
        # 验证API Key格式
        api_key = config['api_key']
        if not (api_key.startswith('sk_test_') or api_key.startswith('sk_live_')):
            raise ServiceException(message='Ping++ API Key格式错误')
        
        # 验证App ID格式
        if not config['app_id'].startswith('app_'):
            raise ServiceException(message='Ping++ App ID格式错误')
```

---

### 修复7：异常信息脱敏

#### 修复代码

```python
# utils/log_util.py

def mask_sensitive_data(data: any) -> any:
    """脱敏敏感数据"""
    if isinstance(data, dict):
        masked = {}
        sensitive_keys = [
            'api_key', 'private_key', 'alipay_public_key',
            'api_v3_key', 'password', 'secret', 'token',
            'credential', 'sign', 'signature'
        ]
        
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                masked[key] = '***MASKED***'
            elif isinstance(value, (dict, list)):
                masked[key] = mask_sensitive_data(value)
            else:
                masked[key] = value
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data

# 使用示例
logger.info(f'创建支付成功: {mask_sensitive_data(result)}')
```

---

### 修复8：日志脱敏

#### 修复代码

```python
# 创建日志过滤器
import logging

class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""
    
    def filter(self, record):
        # 脱敏日志消息
        if hasattr(record, 'msg'):
            record.msg = self._mask_sensitive(str(record.msg))
        return True
    
    def _mask_sensitive(self, text: str) -> str:
        """脱敏文本中的敏感信息"""
        import re
        
        # 脱敏API Key
        text = re.sub(r'sk_(test|live)_[a-zA-Z0-9]+', 'sk_***MASKED***', text)
        
        # 脱敏App ID
        text = re.sub(r'app_[a-zA-Z0-9]+', 'app_***MASKED***', text)
        
        # 脱敏手机号
        text = re.sub(r'1[3-9]\d{9}', '***MASKED***', text)
        
        # 脱敏身份证号
        text = re.sub(r'\d{17}[\dXx]', '***MASKED***', text)
        
        return text

# 添加过滤器到logger
logger.addFilter(SensitiveDataFilter())
```

---

## 📋 实施检查清单

### 配置安全
- [ ] 生成配置加密密钥
- [ ] 实现配置加密工具
- [ ] 加密现有敏感配置
- [ ] 更新配置读取逻辑
- [ ] 测试加密解密功能

### Webhook安全
- [ ] 修复Ping++签名验证
- [ ] 修复支付宝签名验证
- [ ] 修复微信签名验证
- [ ] 添加签名验证日志
- [ ] 测试签名验证功能

### 并发安全
- [ ] 添加支付流水防重复
- [ ] 添加订单状态锁
- [ ] 测试并发场景
- [ ] 压力测试

### 数据安全
- [ ] 统一使用Decimal处理金额
- [ ] 添加配置验证
- [ ] 实现异常信息脱敏
- [ ] 实现日志脱敏
- [ ] 测试数据处理

### 测试验证
- [ ] 单元测试
- [ ] 集成测试
- [ ] 安全测试
- [ ] 压力测试
- [ ] 渗透测试

---

## 🔒 安全配置示例

### .env文件配置
```bash
# 配置加密密钥（生产环境必须设置）
CONFIG_ENCRYPTION_KEY=your_32_character_encryption_key_here

# 支付环境
PAYMENT_ENV=production  # production/test

# 日志级别
LOG_LEVEL=INFO

# 是否启用日志脱敏
ENABLE_LOG_MASKING=true
```

### 数据库配置（加密后）
```json
{
  "api_key": "gAAAAABh...",  // 加密后的API Key
  "app_id": "app_xxxxxx",
  "is_test_mode": false,
  "webhook_url": "https://yourdomain.com/api/payment/webhook/pingpp"
}
```

---

## 📊 修复进度跟踪

### P0修复（5项）
- [ ] 配置加密存储
- [ ] Webhook签名验证
- [ ] 支付宝签名验证
- [ ] 支付流水防重复
- [ ] 订单状态加锁

### P1修复（4项）
- [ ] 金额Decimal处理
- [ ] 配置验证
- [ ] 异常信息脱敏
- [ ] 日志脱敏

### 完成度
- P0: 0/5 (0%)
- P1: 0/4 (0%)
- 总计: 0/9 (0%)

---

**文档版本**: 1.0  
**创建时间**: 2026-01-25  
**更新时间**: 2026-01-25  
**负责人**: Kiro AI Assistant
