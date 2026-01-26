# Ping++ 快速集成示例

## 概述

本文档提供Ping++聚合支付的完整集成示例，从安装到上线只需1小时。

---

## 一、准备工作（10分钟）

### 1. 注册Ping++账号
- 访问：https://www.pingxx.com/
- 注册并完成企业认证（1-3个工作日）

### 2. 创建应用
- 登录控制台
- 创建应用，获取：
  - `API Key`：sk_test_xxxxxx（测试环境）
  - `App ID`：app_xxxxxx

### 3. 配置支付渠道
- 配置支付宝
- 配置微信支付

---

## 二、安装SDK（2分钟）

```bash
pip install pingpp
```

---

## 三、代码实现（30分钟）

### 1. 创建Ping++客户端

创建 `module_thesis/payment/pingpp_client.py`:

```python
"""
Ping++ 支付客户端
"""
import pingpp
from decimal import Decimal
from typing import Optional

from exceptions.exception import ServiceException


class PingppClient:
    """Ping++支付客户端"""
    
    def __init__(self, api_key: str, app_id: str, private_key_path: str = None):
        """
        初始化Ping++客户端
        
        :param api_key: API密钥
        :param app_id: 应用ID
        :param private_key_path: RSA私钥路径（可选）
        """
        pingpp.api_key = api_key
        self.app_id = app_id
        
        if private_key_path:
            pingpp.private_key_path = private_key_path
    
    def create_charge(
        self,
        order_no: str,
        amount: Decimal,
        channel: str,
        subject: str,
        body: str = '',
        client_ip: str = '127.0.0.1',
        extra: dict = None
    ) -> dict:
        """
        创建支付
        
        :param order_no: 订单号
        :param amount: 金额（元）
        :param channel: 支付渠道
        :param subject: 订单标题
        :param body: 订单描述
        :param client_ip: 客户端IP
        :param extra: 额外参数
        :return: 支付凭证
        """
        try:
            # 金额转换为分
            amount_fen = int(amount * 100)
            
            charge = pingpp.Charge.create(
                order_no=order_no,
                amount=amount_fen,
                app=dict(id=self.app_id),
                channel=channel,
                currency='cny',
                client_ip=client_ip,
                subject=subject,
                body=body,
                extra=extra or {}
            )
            
            return {
                'id': charge.id,
                'order_no': charge.order_no,
                'amount': charge.amount,
                'credential': charge.credential,
                'created': charge.created
            }
        except Exception as e:
            raise ServiceException(message=f'创建支付失败: {str(e)}')
    
    def query_charge(self, charge_id: str) -> dict:
        """
        查询支付
        
        :param charge_id: 支付ID
        :return: 支付信息
        """
        try:
            charge = pingpp.Charge.retrieve(charge_id)
            
            return {
                'id': charge.id,
                'order_no': charge.order_no,
                'amount': charge.amount,
                'paid': charge.paid,
                'refunded': charge.refunded,
                'time_paid': charge.time_paid,
                'transaction_no': charge.transaction_no
            }
        except Exception as e:
            raise ServiceException(message=f'查询支付失败: {str(e)}')
    
    def create_refund(
        self,
        charge_id: str,
        amount: Decimal = None,
        description: str = ''
    ) -> dict:
        """
        创建退款
        
        :param charge_id: 支付ID
        :param amount: 退款金额（元），不填则全额退款
        :param description: 退款描述
        :return: 退款信息
        """
        try:
            refund_data = {
                'description': description
            }
            
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = pingpp.Refund.create(charge_id, **refund_data)
            
            return {
                'id': refund.id,
                'amount': refund.amount,
                'succeed': refund.succeed,
                'status': refund.status,
                'time_succeed': refund.time_succeed
            }
        except Exception as e:
            raise ServiceException(message=f'创建退款失败: {str(e)}')
    
    @staticmethod
    def verify_signature(raw_data: bytes, signature: str, pub_key_path: str) -> bool:
        """
        验证Webhook签名
        
        :param raw_data: 原始数据
        :param signature: 签名
        :param pub_key_path: Ping++公钥路径
        :return: 是否验证通过
        """
        try:
            return pingpp.Webhook.verify_signature(raw_data, signature, pub_key_path)
        except Exception:
            return False


# 支付渠道常量
class PingppChannel:
    """Ping++支付渠道"""
    ALIPAY_PC = 'alipay_pc_direct'      # 支付宝PC网站支付
    ALIPAY_WAP = 'alipay_wap'           # 支付宝手机网站支付
    ALIPAY_QR = 'alipay_qr'             # 支付宝扫码支付
    
    WECHAT_PUB = 'wx_pub'               # 微信公众号支付
    WECHAT_LITE = 'wx_lite'             # 微信小程序支付
    WECHAT_WAP = 'wx_wap'               # 微信H5支付
    WECHAT_PUB_QR = 'wx_pub_qr'         # 微信扫码支付
```

### 2. 集成到PaymentService

修改 `module_thesis/service/payment_service.py`:

```python
"""
支付服务层（使用Ping++）
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from exceptions.exception import ServiceException
from module_thesis.dao import PaymentConfigDao
from module_thesis.payment.pingpp_client import PingppClient, PingppChannel


class PaymentService:
    """支付服务类"""
    
    @classmethod
    async def get_pingpp_client(cls, query_db: AsyncSession) -> PingppClient:
        """获取Ping++客户端"""
        config = await PaymentConfigDao.get_default_config(query_db, 'pingpp')
        if not config:
            raise ServiceException(message='Ping++配置不存在')
        
        return PingppClient(
            api_key=config.api_key,
            app_id=config.app_id,
            private_key_path=config.private_key_path
        )
    
    @classmethod
    async def create_payment(
        cls,
        query_db: AsyncSession,
        order_no: str,
        amount: Decimal,
        channel: str,
        subject: str,
        body: str = '',
        client_ip: str = '127.0.0.1',
        extra: dict = None
    ) -> dict:
        """
        创建支付
        
        :param query_db: 数据库会话
        :param order_no: 订单号
        :param amount: 金额（元）
        :param channel: 支付渠道
        :param subject: 订单标题
        :param body: 订单描述
        :param client_ip: 客户端IP
        :param extra: 额外参数
        :return: 支付信息
        """
        try:
            client = await cls.get_pingpp_client(query_db)
            
            result = client.create_charge(
                order_no=order_no,
                amount=amount,
                channel=channel,
                subject=subject,
                body=body,
                client_ip=client_ip,
                extra=extra
            )
            
            return result
        except ServiceException:
            raise
        except Exception as e:
            raise ServiceException(message=f'创建支付失败: {str(e)}')
    
    @classmethod
    async def query_payment(cls, query_db: AsyncSession, charge_id: str) -> dict:
        """查询支付"""
        try:
            client = await cls.get_pingpp_client(query_db)
            return client.query_charge(charge_id)
        except Exception as e:
            raise ServiceException(message=f'查询支付失败: {str(e)}')
    
    @classmethod
    async def create_refund(
        cls,
        query_db: AsyncSession,
        charge_id: str,
        amount: Decimal = None,
        description: str = ''
    ) -> dict:
        """创建退款"""
        try:
            client = await cls.get_pingpp_client(query_db)
            return client.create_refund(charge_id, amount, description)
        except Exception as e:
            raise ServiceException(message=f'创建退款失败: {str(e)}')
```

### 3. 添加Controller接口

在 `module_thesis/controller/order_controller.py` 中添加：

```python
from module_thesis.payment.pingpp_client import PingppChannel

@order_controller.post(
    '/payment/create',
    summary='创建支付',
    description='创建支付订单',
    response_model=DataResponseModel
)
async def create_payment(
    request: Request,
    order_id: Annotated[int, Query(description='订单ID')],
    channel: Annotated[str, Query(description='支付渠道')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建支付"""
    # 获取订单
    order = await OrderService.get_order_detail(query_db, order_id)
    
    # 验证订单所有权
    if order.user_id != current_user.user.user_id:
        raise ServiceException(message='无权操作此订单')
    
    # 验证订单状态
    if order.status != 'pending':
        raise ServiceException(message='订单状态异常')
    
    # 获取客户端IP
    client_ip = request.client.host
    
    # 创建支付
    result = await PaymentService.create_payment(
        query_db,
        order_no=order.order_no,
        amount=order.amount,
        channel=channel,
        subject=f'购买{order.order_type}',
        body=f'订单号：{order.order_no}',
        client_ip=client_ip
    )
    
    logger.info(f'创建支付成功: {order.order_no}')
    return ResponseUtil.success(data=result)


@order_controller.post(
    '/payment/webhook',
    summary='支付回调',
    description='Ping++支付回调接口',
    include_in_schema=False
)
async def payment_webhook(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> dict:
    """支付回调"""
    try:
        # 获取原始数据和签名
        raw_data = await request.body()
        signature = request.headers.get('x-pingplusplus-signature')
        
        # 验证签名
        pub_key_path = '/path/to/pingpp_public_key.pem'
        if not PingppClient.verify_signature(raw_data, signature, pub_key_path):
            return {'status': 'fail', 'message': '签名验证失败'}
        
        # 解析数据
        import json
        event = json.loads(raw_data.decode('utf-8'))
        
        # 处理不同类型的事件
        if event['type'] == 'charge.succeeded':
            # 支付成功
            charge = event['data']['object']
            order_no = charge['order_no']
            transaction_no = charge['transaction_no']
            
            # 处理支付
            await OrderService.process_payment(
                query_db,
                order_no,
                transaction_no,
                datetime.now()
            )
        
        elif event['type'] == 'refund.succeeded':
            # 退款成功
            refund = event['data']['object']
            # 处理退款逻辑
            pass
        
        return {'status': 'success'}
    except Exception as e:
        logger.error(f'支付回调处理失败: {str(e)}')
        return {'status': 'fail', 'message': str(e)}


@order_controller.get(
    '/payment/query/{charge_id}',
    summary='查询支付',
    description='查询支付状态',
    response_model=DataResponseModel
)
async def query_payment(
    request: Request,
    charge_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """查询支付"""
    result = await PaymentService.query_payment(query_db, charge_id)
    return ResponseUtil.success(data=result)
```

---

## 四、前端集成（20分钟）

### 1. 支付宝PC支付

```javascript
// 创建支付
async function createAlipayPayment(orderId) {
  try {
    const res = await request.post('/thesis/order/payment/create', {
      order_id: orderId,
      channel: 'alipay_pc_direct'
    })
    
    // 获取支付凭证
    const credential = res.data.credential.alipay_pc_direct
    
    // 跳转到支付页面
    window.location.href = credential
  } catch (error) {
    ElMessage.error('创建支付失败')
  }
}
```

### 2. 微信扫码支付

```javascript
// 创建支付
async function createWechatPayment(orderId) {
  try {
    const res = await request.post('/thesis/order/payment/create', {
      order_id: orderId,
      channel: 'wx_pub_qr'
    })
    
    // 获取二维码URL
    const qrCodeUrl = res.data.credential.wx_pub_qr
    
    // 显示二维码
    showQRCode(qrCodeUrl)
    
    // 轮询查询支付状态
    pollPaymentStatus(res.data.id)
  } catch (error) {
    ElMessage.error('创建支付失败')
  }
}

// 轮询支付状态
function pollPaymentStatus(chargeId) {
  const timer = setInterval(async () => {
    try {
      const res = await request.get(`/thesis/order/payment/query/${chargeId}`)
      
      if (res.data.paid) {
        clearInterval(timer)
        ElMessage.success('支付成功')
        router.push('/order/success')
      }
    } catch (error) {
      clearInterval(timer)
    }
  }, 2000)
}
```

### 3. 支付页面组件

```vue
<template>
  <div class="payment-page">
    <el-card>
      <h2>选择支付方式</h2>
      
      <el-radio-group v-model="paymentChannel">
        <el-radio label="alipay_pc_direct">
          <img src="/icons/alipay.png" alt="支付宝" />
          支付宝支付
        </el-radio>
        <el-radio label="wx_pub_qr">
          <img src="/icons/wechat.png" alt="微信" />
          微信支付
        </el-radio>
      </el-radio-group>
      
      <div class="order-info">
        <p>订单号：{{ orderNo }}</p>
        <p>金额：<span class="amount">¥{{ amount }}</span></p>
      </div>
      
      <el-button
        type="primary"
        size="large"
        @click="handlePay"
        :loading="paying"
      >
        立即支付
      </el-button>
    </el-card>
    
    <!-- 微信支付二维码弹窗 -->
    <el-dialog v-model="showQRCode" title="微信扫码支付">
      <div class="qrcode-container">
        <qrcode-vue :value="qrCodeUrl" :size="200" />
        <p>请使用微信扫码支付</p>
        <p class="amount">¥{{ amount }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import QrcodeVue from 'qrcode.vue'
import { createPayment, queryPayment } from '@/api/order'

const props = defineProps({
  orderId: Number,
  orderNo: String,
  amount: Number
})

const paymentChannel = ref('alipay_pc_direct')
const paying = ref(false)
const showQRCode = ref(false)
const qrCodeUrl = ref('')

async function handlePay() {
  paying.value = true
  
  try {
    const res = await createPayment({
      order_id: props.orderId,
      channel: paymentChannel.value
    })
    
    if (paymentChannel.value === 'alipay_pc_direct') {
      // 支付宝支付：跳转
      window.location.href = res.data.credential.alipay_pc_direct
    } else if (paymentChannel.value === 'wx_pub_qr') {
      // 微信支付：显示二维码
      qrCodeUrl.value = res.data.credential.wx_pub_qr
      showQRCode.value = true
      
      // 轮询支付状态
      pollPaymentStatus(res.data.id)
    }
  } catch (error) {
    ElMessage.error('创建支付失败')
  } finally {
    paying.value = false
  }
}

function pollPaymentStatus(chargeId) {
  const timer = setInterval(async () => {
    try {
      const res = await queryPayment(chargeId)
      
      if (res.data.paid) {
        clearInterval(timer)
        showQRCode.value = false
        ElMessage.success('支付成功')
        router.push('/order/success')
      }
    } catch (error) {
      clearInterval(timer)
    }
  }, 2000)
}
</script>
```

---

## 五、测试（10分钟）

### 1. 测试环境配置

```python
# 使用测试API Key
API_KEY = 'sk_test_xxxxxx'
APP_ID = 'app_xxxxxx'
```

### 2. 测试流程

1. 创建订单
2. 选择支付方式
3. 完成支付（测试环境无需真实支付）
4. 验证回调
5. 检查订单状态

### 3. 测试账号

Ping++提供测试账号，无需真实支付：
- 支付宝测试账号：https://docs.pingxx.com/guide/test-card
- 微信测试账号：https://docs.pingxx.com/guide/test-card

---

## 六、上线（10分钟）

### 1. 切换到生产环境

```python
# 使用生产API Key
API_KEY = 'sk_live_xxxxxx'
APP_ID = 'app_xxxxxx'
```

### 2. 配置Webhook

在Ping++控制台配置Webhook地址：
```
https://yourdomain.com/api/thesis/order/payment/webhook
```

### 3. 下载公钥

下载Ping++公钥用于验证签名：
```bash
wget https://www.pingxx.com/pingpp_public_key.pem
```

---

## 七、费用说明

### 测试环境
- ✅ 完全免费
- ✅ 无交易限制
- ✅ 功能完整

### 生产环境
- 手续费：0.6% - 1.2%（根据交易量）
- 无月费、年费
- T+1自动结算

### 示例计算

月交易额10万元：
- 手续费：100,000 × 1.0% = 1,000元
- 其他费用：0元
- **总成本**：1,000元/月

---

## 八、常见问题

### Q1: 如何获取测试API Key？
A: 注册后在控制台的"开发设置"中获取。

### Q2: 测试环境可以真实支付吗？
A: 不可以，测试环境不会真实扣款。

### Q3: 如何切换到生产环境？
A: 更换API Key为生产环境的Key即可。

### Q4: Webhook如何验证签名？
A: 使用Ping++提供的公钥验证签名。

### Q5: 支持哪些支付方式？
A: 支付宝、微信、银联、Apple Pay等。

---

## 九、总结

使用Ping++的优势：
- ✅ 1小时即可完成集成
- ✅ 代码简单，易于维护
- ✅ 支持多种支付方式
- ✅ 提供完善的测试环境
- ✅ 技术支持响应快

成本对比：
- 开发成本：1小时（vs 自己对接3天）
- 维护成本：0（vs 自己维护1天/月）
- 手续费：+0.4%（vs 自己对接0.6%）

**结论**：对于大多数项目，使用Ping++是最优选择！
