# 支付系统设计方案

## 概述

当前系统缺少支付SDK集成和支付配置管理，本文档提供完整的支付系统设计方案。

---

## 一、支付配置表设计

### 1. 支付配置表（ai_write_payment_config）

```sql
-- ----------------------------
-- 支付配置表
-- ----------------------------
drop table if exists ai_write_payment_config;
create table ai_write_payment_config (
  config_id         bigint(20)      not null auto_increment    comment '配置ID',
  payment_type      varchar(20)     not null                   comment '支付类型（alipay/wechat）',
  config_name       varchar(50)     not null                   comment '配置名称',
  
  -- 支付宝配置
  app_id            varchar(100)    default ''                 comment '应用ID',
  private_key       text            default null               comment '应用私钥',
  public_key        text            default null               comment '支付宝公钥',
  alipay_public_key text            default null               comment '支付宝公钥证书',
  
  -- 微信配置
  mch_id            varchar(50)     default ''                 comment '商户号',
  api_key           varchar(100)    default ''                 comment 'API密钥',
  api_v3_key        varchar(100)    default ''                 comment 'APIv3密钥',
  cert_serial_no    varchar(100)    default ''                 comment '证书序列号',
  private_cert_path varchar(200)    default ''                 comment '商户私钥证书路径',
  
  -- 通用配置
  notify_url        varchar(200)    not null                   comment '异步通知地址',
  return_url        varchar(200)    default ''                 comment '同步返回地址',
  
  is_sandbox        char(1)         default '0'                comment '是否沙箱环境（0否 1是）',
  is_default        char(1)         default '0'                comment '是否默认配置（0否 1是）',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (config_id),
  unique key uk_payment_type (payment_type, is_default)
) engine=innodb auto_increment=100 comment = '支付配置表';
```


### 2. 支付流水表（ai_write_payment_transaction）

```sql
-- ----------------------------
-- 支付流水表
-- ----------------------------
drop table if exists ai_write_payment_transaction;
create table ai_write_payment_transaction (
  transaction_id    bigint(20)      not null auto_increment    comment '流水ID',
  order_no          varchar(50)     not null                   comment '订单号',
  payment_type      varchar(20)     not null                   comment '支付类型（alipay/wechat）',
  
  trade_no          varchar(100)    default ''                 comment '第三方交易号',
  buyer_id          varchar(100)    default ''                 comment '买家ID',
  buyer_account     varchar(100)    default ''                 comment '买家账号',
  
  total_amount      decimal(10,2)   not null                   comment '订单金额',
  receipt_amount    decimal(10,2)   default 0.00               comment '实收金额',
  
  payment_time      datetime        default null               comment '支付时间',
  notify_time       datetime        default null               comment '通知时间',
  
  trade_status      varchar(20)     not null                   comment '交易状态（WAIT_BUYER_PAY/TRADE_SUCCESS/TRADE_CLOSED）',
  
  notify_data       text            default null               comment '通知原始数据',
  
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (transaction_id),
  unique key uk_order_no (order_no),
  index idx_trade_no (trade_no),
  index idx_trade_status (trade_status, create_time)
) engine=innodb auto_increment=100 comment = '支付流水表';
```

---

## 二、Python SDK集成

### 1. 依赖安装

```txt
# requirements.txt 添加
alipay-sdk-python==3.7.4
wechatpayv3==1.2.8
```

### 2. 支付宝SDK封装

创建 `module_thesis/payment/alipay_client.py`:

```python
"""
支付宝支付客户端
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel

from exceptions.exception import ServiceException


class AlipayClient:
    """支付宝支付客户端"""
    
    def __init__(
        self,
        app_id: str,
        private_key: str,
        alipay_public_key: str,
        notify_url: str,
        return_url: str = '',
        is_sandbox: bool = False
    ):
        """
        初始化支付宝客户端
        
        :param app_id: 应用ID
        :param private_key: 应用私钥
        :param alipay_public_key: 支付宝公钥
        :param notify_url: 异步通知地址
        :param return_url: 同步返回地址
        :param is_sandbox: 是否沙箱环境
        """
        # 配置
        config = AlipayClientConfig()
        config.app_id = app_id
        config.app_private_key = private_key
        config.alipay_public_key = alipay_public_key
        
        # 设置网关
        if is_sandbox:
            config.server_url = 'https://openapi.alipaydev.com/gateway.do'
        else:
            config.server_url = 'https://openapi.alipay.com/gateway.do'
        
        self.client = DefaultAlipayClient(alipay_client_config=config)
        self.notify_url = notify_url
        self.return_url = return_url
    
    def create_pc_pay(
        self,
        order_no: str,
        subject: str,
        total_amount: Decimal,
        body: str = ''
    ) -> str:
        """
        创建PC网站支付
        
        :param order_no: 订单号
        :param subject: 订单标题
        :param total_amount: 订单金额
        :param body: 订单描述
        :return: 支付表单HTML
        """
        try:
            model = AlipayTradePagePayModel()
            model.out_trade_no = order_no
            model.subject = subject
            model.total_amount = str(total_amount)
            model.body = body
            model.product_code = 'FAST_INSTANT_TRADE_PAY'
            
            request = AlipayTradePagePayRequest(biz_model=model)
            request.notify_url = self.notify_url
            request.return_url = self.return_url
            
            response = self.client.page_execute(request, http_method='GET')
            return response
        except Exception as e:
            raise ServiceException(message=f'创建支付宝支付失败: {str(e)}')
    
    def create_wap_pay(
        self,
        order_no: str,
        subject: str,
        total_amount: Decimal,
        body: str = ''
    ) -> str:
        """
        创建手机网站支付
        
        :param order_no: 订单号
        :param subject: 订单标题
        :param total_amount: 订单金额
        :param body: 订单描述
        :return: 支付表单HTML
        """
        try:
            model = AlipayTradeWapPayModel()
            model.out_trade_no = order_no
            model.subject = subject
            model.total_amount = str(total_amount)
            model.body = body
            model.product_code = 'QUICK_WAP_WAY'
            
            request = AlipayTradeWapPayRequest(biz_model=model)
            request.notify_url = self.notify_url
            request.return_url = self.return_url
            
            response = self.client.page_execute(request, http_method='GET')
            return response
        except Exception as e:
            raise ServiceException(message=f'创建支付宝WAP支付失败: {str(e)}')
    
    def query_order(self, order_no: str) -> dict:
        """
        查询订单
        
        :param order_no: 订单号
        :return: 订单信息
        """
        try:
            model = AlipayTradeQueryModel()
            model.out_trade_no = order_no
            
            request = AlipayTradeQueryRequest(biz_model=model)
            response = self.client.execute(request)
            
            if response.code == '10000':
                return {
                    'trade_no': response.trade_no,
                    'trade_status': response.trade_status,
                    'total_amount': response.total_amount,
                    'buyer_user_id': response.buyer_user_id,
                    'buyer_logon_id': response.buyer_logon_id
                }
            else:
                raise ServiceException(message=f'查询订单失败: {response.sub_msg}')
        except Exception as e:
            raise ServiceException(message=f'查询订单失败: {str(e)}')
    
    def refund(
        self,
        order_no: str,
        refund_amount: Decimal,
        refund_reason: str = ''
    ) -> dict:
        """
        退款
        
        :param order_no: 订单号
        :param refund_amount: 退款金额
        :param refund_reason: 退款原因
        :return: 退款结果
        """
        try:
            model = AlipayTradeRefundModel()
            model.out_trade_no = order_no
            model.refund_amount = str(refund_amount)
            model.refund_reason = refund_reason
            
            request = AlipayTradeRefundRequest(biz_model=model)
            response = self.client.execute(request)
            
            if response.code == '10000':
                return {
                    'trade_no': response.trade_no,
                    'refund_fee': response.refund_fee,
                    'gmt_refund_pay': response.gmt_refund_pay
                }
            else:
                raise ServiceException(message=f'退款失败: {response.sub_msg}')
        except Exception as e:
            raise ServiceException(message=f'退款失败: {str(e)}')
    
    def verify_notify(self, params: dict) -> bool:
        """
        验证异步通知签名
        
        :param params: 通知参数
        :return: 是否验证通过
        """
        try:
            return self.client.verify(params)
        except Exception:
            return False
```


### 3. 微信支付SDK封装

创建 `module_thesis/payment/wechat_client.py`:

```python
"""
微信支付客户端
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime
import time

from wechatpayv3 import WeChatPay, WeChatPayType

from exceptions.exception import ServiceException


class WechatPayClient:
    """微信支付客户端"""
    
    def __init__(
        self,
        app_id: str,
        mch_id: str,
        api_v3_key: str,
        cert_serial_no: str,
        private_key_path: str,
        notify_url: str,
        is_sandbox: bool = False
    ):
        """
        初始化微信支付客户端
        
        :param app_id: 应用ID
        :param mch_id: 商户号
        :param api_v3_key: APIv3密钥
        :param cert_serial_no: 证书序列号
        :param private_key_path: 商户私钥证书路径
        :param notify_url: 异步通知地址
        :param is_sandbox: 是否沙箱环境
        """
        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE if not is_sandbox else WeChatPayType.SANDBOX,
            mchid=mch_id,
            private_key=self._load_private_key(private_key_path),
            cert_serial_no=cert_serial_no,
            apiv3_key=api_v3_key,
            appid=app_id,
            notify_url=notify_url
        )
        self.app_id = app_id
        self.mch_id = mch_id
    
    def _load_private_key(self, path: str) -> str:
        """加载私钥"""
        with open(path, 'r') as f:
            return f.read()
    
    def create_native_pay(
        self,
        order_no: str,
        description: str,
        total_amount: Decimal
    ) -> str:
        """
        创建Native支付（扫码支付）
        
        :param order_no: 订单号
        :param description: 商品描述
        :param total_amount: 订单金额（元）
        :return: 二维码链接
        """
        try:
            # 金额转换为分
            amount_fen = int(total_amount * 100)
            
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=order_no,
                amount={'total': amount_fen, 'currency': 'CNY'}
            )
            
            if code == 200:
                return message.get('code_url')
            else:
                raise ServiceException(message=f'创建微信支付失败: {message}')
        except Exception as e:
            raise ServiceException(message=f'创建微信支付失败: {str(e)}')
    
    def create_jsapi_pay(
        self,
        order_no: str,
        description: str,
        total_amount: Decimal,
        openid: str
    ) -> dict:
        """
        创建JSAPI支付（公众号/小程序支付）
        
        :param order_no: 订单号
        :param description: 商品描述
        :param total_amount: 订单金额（元）
        :param openid: 用户openid
        :return: 支付参数
        """
        try:
            # 金额转换为分
            amount_fen = int(total_amount * 100)
            
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=order_no,
                amount={'total': amount_fen, 'currency': 'CNY'},
                payer={'openid': openid},
                pay_type=WeChatPayType.JSAPI
            )
            
            if code == 200:
                prepay_id = message.get('prepay_id')
                # 生成JSAPI支付参数
                timestamp = str(int(time.time()))
                nonce_str = self.wxpay._core.nonce_str()
                package = f'prepay_id={prepay_id}'
                
                pay_sign = self.wxpay._core.sign([
                    self.app_id,
                    timestamp,
                    nonce_str,
                    package
                ])
                
                return {
                    'appId': self.app_id,
                    'timeStamp': timestamp,
                    'nonceStr': nonce_str,
                    'package': package,
                    'signType': 'RSA',
                    'paySign': pay_sign
                }
            else:
                raise ServiceException(message=f'创建微信JSAPI支付失败: {message}')
        except Exception as e:
            raise ServiceException(message=f'创建微信JSAPI支付失败: {str(e)}')
    
    def query_order(self, order_no: str) -> dict:
        """
        查询订单
        
        :param order_no: 订单号
        :return: 订单信息
        """
        try:
            code, message = self.wxpay.query(out_trade_no=order_no)
            
            if code == 200:
                return {
                    'transaction_id': message.get('transaction_id'),
                    'trade_state': message.get('trade_state'),
                    'trade_state_desc': message.get('trade_state_desc'),
                    'success_time': message.get('success_time'),
                    'payer': message.get('payer', {})
                }
            else:
                raise ServiceException(message=f'查询订单失败: {message}')
        except Exception as e:
            raise ServiceException(message=f'查询订单失败: {str(e)}')
    
    def refund(
        self,
        order_no: str,
        refund_no: str,
        total_amount: Decimal,
        refund_amount: Decimal,
        reason: str = ''
    ) -> dict:
        """
        退款
        
        :param order_no: 订单号
        :param refund_no: 退款单号
        :param total_amount: 订单金额（元）
        :param refund_amount: 退款金额（元）
        :param reason: 退款原因
        :return: 退款结果
        """
        try:
            # 金额转换为分
            total_fen = int(total_amount * 100)
            refund_fen = int(refund_amount * 100)
            
            code, message = self.wxpay.refund(
                out_trade_no=order_no,
                out_refund_no=refund_no,
                amount={
                    'refund': refund_fen,
                    'total': total_fen,
                    'currency': 'CNY'
                },
                reason=reason
            )
            
            if code == 200:
                return {
                    'refund_id': message.get('refund_id'),
                    'status': message.get('status'),
                    'success_time': message.get('success_time')
                }
            else:
                raise ServiceException(message=f'退款失败: {message}')
        except Exception as e:
            raise ServiceException(message=f'退款失败: {str(e)}')
    
    def verify_notify(self, headers: dict, body: str) -> dict:
        """
        验证异步通知签名
        
        :param headers: 请求头
        :param body: 请求体
        :return: 通知数据
        """
        try:
            result = self.wxpay.callback(headers, body)
            return result
        except Exception as e:
            raise ServiceException(message=f'验证签名失败: {str(e)}')
```

---

## 三、支付服务层

创建 `module_thesis/service/payment_service.py`:

```python
"""
支付服务层
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from exceptions.exception import ServiceException
from module_thesis.dao import PaymentConfigDao, PaymentTransactionDao
from module_thesis.payment.alipay_client import AlipayClient
from module_thesis.payment.wechat_client import WechatPayClient


class PaymentService:
    """支付服务类"""
    
    @classmethod
    async def get_alipay_client(cls, query_db: AsyncSession) -> AlipayClient:
        """获取支付宝客户端"""
        config = await PaymentConfigDao.get_default_config(query_db, 'alipay')
        if not config:
            raise ServiceException(message='支付宝配置不存在')
        
        return AlipayClient(
            app_id=config.app_id,
            private_key=config.private_key,
            alipay_public_key=config.alipay_public_key,
            notify_url=config.notify_url,
            return_url=config.return_url,
            is_sandbox=config.is_sandbox == '1'
        )
    
    @classmethod
    async def get_wechat_client(cls, query_db: AsyncSession) -> WechatPayClient:
        """获取微信支付客户端"""
        config = await PaymentConfigDao.get_default_config(query_db, 'wechat')
        if not config:
            raise ServiceException(message='微信支付配置不存在')
        
        return WechatPayClient(
            app_id=config.app_id,
            mch_id=config.mch_id,
            api_v3_key=config.api_v3_key,
            cert_serial_no=config.cert_serial_no,
            private_key_path=config.private_cert_path,
            notify_url=config.notify_url,
            is_sandbox=config.is_sandbox == '1'
        )
    
    @classmethod
    async def create_payment(
        cls,
        query_db: AsyncSession,
        order_no: str,
        payment_type: str,
        subject: str,
        total_amount: Decimal,
        pay_method: str = 'pc',
        openid: str = None
    ) -> dict:
        """
        创建支付
        
        :param query_db: 数据库会话
        :param order_no: 订单号
        :param payment_type: 支付类型（alipay/wechat）
        :param subject: 订单标题
        :param total_amount: 订单金额
        :param pay_method: 支付方式（pc/wap/native/jsapi）
        :param openid: 微信openid（JSAPI支付必填）
        :return: 支付信息
        """
        try:
            if payment_type == 'alipay':
                client = await cls.get_alipay_client(query_db)
                
                if pay_method == 'pc':
                    pay_url = client.create_pc_pay(order_no, subject, total_amount)
                elif pay_method == 'wap':
                    pay_url = client.create_wap_pay(order_no, subject, total_amount)
                else:
                    raise ServiceException(message='不支持的支付方式')
                
                return {
                    'payment_type': 'alipay',
                    'pay_method': pay_method,
                    'pay_url': pay_url
                }
            
            elif payment_type == 'wechat':
                client = await cls.get_wechat_client(query_db)
                
                if pay_method == 'native':
                    code_url = client.create_native_pay(order_no, subject, total_amount)
                    return {
                        'payment_type': 'wechat',
                        'pay_method': 'native',
                        'code_url': code_url
                    }
                elif pay_method == 'jsapi':
                    if not openid:
                        raise ServiceException(message='JSAPI支付需要提供openid')
                    pay_params = client.create_jsapi_pay(order_no, subject, total_amount, openid)
                    return {
                        'payment_type': 'wechat',
                        'pay_method': 'jsapi',
                        'pay_params': pay_params
                    }
                else:
                    raise ServiceException(message='不支持的支付方式')
            
            else:
                raise ServiceException(message='不支持的支付类型')
        
        except ServiceException:
            raise
        except Exception as e:
            raise ServiceException(message=f'创建支付失败: {str(e)}')
```

---

## 四、支付回调处理

在 `order_controller.py` 中添加支付回调接口：

```python
@order_controller.post(
    '/payment/alipay/notify',
    summary='支付宝支付回调',
    description='支付宝异步通知接口',
    include_in_schema=False
)
async def alipay_notify(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> str:
    """支付宝支付回调"""
    try:
        # 获取通知参数
        form_data = await request.form()
        params = dict(form_data)
        
        # 验证签名
        client = await PaymentService.get_alipay_client(query_db)
        if not client.verify_notify(params):
            return 'fail'
        
        # 获取订单号和交易状态
        order_no = params.get('out_trade_no')
        trade_status = params.get('trade_status')
        trade_no = params.get('trade_no')
        
        # 只处理支付成功的通知
        if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            # 处理支付
            await OrderService.process_payment(
                query_db,
                order_no,
                trade_no,
                datetime.now()
            )
        
        return 'success'
    except Exception as e:
        logger.error(f'支付宝回调处理失败: {str(e)}')
        return 'fail'


@order_controller.post(
    '/payment/wechat/notify',
    summary='微信支付回调',
    description='微信支付异步通知接口',
    include_in_schema=False
)
async def wechat_notify(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> dict:
    """微信支付回调"""
    try:
        # 获取请求头和请求体
        headers = dict(request.headers)
        body = await request.body()
        
        # 验证签名并解密
        client = await PaymentService.get_wechat_client(query_db)
        result = client.verify_notify(headers, body.decode('utf-8'))
        
        # 获取订单号和交易状态
        order_no = result.get('out_trade_no')
        trade_state = result.get('trade_state')
        transaction_id = result.get('transaction_id')
        
        # 只处理支付成功的通知
        if trade_state == 'SUCCESS':
            # 处理支付
            await OrderService.process_payment(
                query_db,
                order_no,
                transaction_id,
                datetime.now()
            )
        
        return {'code': 'SUCCESS', 'message': '成功'}
    except Exception as e:
        logger.error(f'微信回调处理失败: {str(e)}')
        return {'code': 'FAIL', 'message': str(e)}
```

---

## 五、实施步骤

### 1. 数据库（立即）
- [ ] 创建支付配置表
- [ ] 创建支付流水表
- [ ] 添加初始配置数据

### 2. SDK集成（1-2天）
- [ ] 安装Python SDK
- [ ] 封装支付宝客户端
- [ ] 封装微信支付客户端
- [ ] 编写单元测试

### 3. Service层（1天）
- [ ] 创建PaymentService
- [ ] 实现支付创建方法
- [ ] 实现支付查询方法
- [ ] 实现退款方法

### 4. Controller层（1天）
- [ ] 添加支付创建接口
- [ ] 添加支付回调接口
- [ ] 添加支付查询接口
- [ ] 添加退款接口

### 5. 测试（1-2天）
- [ ] 沙箱环境测试
- [ ] 支付流程测试
- [ ] 回调处理测试
- [ ] 退款流程测试

---

## 六、配置示例

### 支付宝配置
```python
{
    "app_id": "2021001234567890",
    "private_key": "MIIEvQIBADANBgkqhkiG9w0BAQE...",
    "alipay_public_key": "MIIBIjANBgkqhkiG9w0BAQE...",
    "notify_url": "https://yourdomain.com/api/thesis/order/payment/alipay/notify",
    "return_url": "https://yourdomain.com/payment/success",
    "is_sandbox": false
}
```

### 微信支付配置
```python
{
    "app_id": "wx1234567890abcdef",
    "mch_id": "1234567890",
    "api_v3_key": "your_api_v3_key_32_characters",
    "cert_serial_no": "1234567890ABCDEF",
    "private_cert_path": "/path/to/apiclient_key.pem",
    "notify_url": "https://yourdomain.com/api/thesis/order/payment/wechat/notify",
    "is_sandbox": false
}
```

---

## 七、注意事项

### 安全性
1. ✅ 私钥和密钥必须加密存储
2. ✅ 回调接口必须验证签名
3. ✅ 使用HTTPS协议
4. ✅ 防止重复通知处理

### 稳定性
1. ✅ 支付回调要幂等处理
2. ✅ 记录完整的支付流水
3. ✅ 异常情况要有补偿机制
4. ✅ 定时对账

### 用户体验
1. ✅ 支付超时提醒
2. ✅ 支付状态实时查询
3. ✅ 多种支付方式选择
4. ✅ 支付失败友好提示
