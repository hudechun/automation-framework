# 统一支付网关设计

## 概述

设计一个统一的支付网关，支持多种支付方式（支付宝SDK、微信SDK、Ping++聚合支付等），根据数据库配置动态选择支付渠道。

---

## 一、架构设计

### 1. 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端应用                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 支付宝   │  │  微信    │  │  其他    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                  统一支付网关 API                        │
│              /api/payment/create                         │
│              /api/payment/query                          │
│              /api/payment/refund                         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                  支付网关服务层                          │
│              PaymentGatewayService                       │
│         (根据配置动态选择支付提供商)                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌──────────────┬──────────────┬──────────────┬───────────┐
│ 支付宝SDK    │  微信SDK     │  Ping++      │  其他     │
│ AlipayClient │ WechatClient │ PingppClient │  ...      │
└──────────────┴──────────────┴──────────────┴───────────┘
                        ↓
┌──────────────┬──────────────┬──────────────┬───────────┐
│ 支付宝平台   │  微信平台    │  Ping++平台  │  其他     │
└──────────────┴──────────────┴──────────────┴───────────┘
```

### 2. 数据库设计

```sql
-- 支付配置表（支持多种支付方式）
CREATE TABLE ai_write_payment_config (
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
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (config_id),
  INDEX idx_provider (provider_type, is_enabled),
  INDEX idx_priority (priority DESC, is_enabled)
) ENGINE=INNODB COMMENT = '支付配置表';

-- 初始化配置数据
INSERT INTO ai_write_payment_config (provider_type, provider_name, config_data, supported_channels, is_enabled, priority, fee_rate, status, create_by, create_time) VALUES
-- Ping++配置（优先级最高）
('pingpp', 'Ping++聚合支付', 
  '{"api_key": "sk_test_xxxxxx", "app_id": "app_xxxxxx", "private_key_path": "/path/to/key.pem", "webhook_url": "https://yourdomain.com/api/payment/webhook/pingpp"}',
  '["alipay_pc", "alipay_wap", "alipay_qr", "wx_pub", "wx_lite", "wx_wap", "wx_pub_qr"]',
  '1', 100, 0.0100, '0', 'admin', NOW()),

-- 支付宝SDK配置
('alipay', '支付宝直连', 
  '{"app_id": "2021001234567890", "private_key": "MIIEvQIBADANBgkqhkiG9w0...", "alipay_public_key": "MIIBIjANBgkqhkiG9w0...", "notify_url": "https://yourdomain.com/api/payment/webhook/alipay", "return_url": "https://yourdomain.com/payment/success", "is_sandbox": false}',
  '["alipay_pc", "alipay_wap", "alipay_qr"]',
  '1', 90, 0.0060, '0', 'admin', NOW()),

-- 微信SDK配置
('wechat', '微信支付直连', 
  '{"app_id": "wx1234567890abcdef", "mch_id": "1234567890", "api_v3_key": "your_api_v3_key", "cert_serial_no": "1234567890ABCDEF", "private_cert_path": "/path/to/cert.pem", "notify_url": "https://yourdomain.com/api/payment/webhook/wechat", "is_sandbox": false}',
  '["wx_native", "wx_jsapi", "wx_h5"]',
  '1', 80, 0.0060, '0', 'admin', NOW());
```

---

## 二、代码实现

### 1. 支付提供商接口（抽象基类）

创建 `module_thesis/payment/base_provider.py`:

```python
"""
支付提供商基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from decimal import Decimal


class PaymentProvider(ABC):
    """支付提供商抽象基类"""
    
    def __init__(self, config: dict):
        """
        初始化支付提供商
        
        :param config: 配置数据
        """
        self.config = config
    
    @abstractmethod
    def create_payment(
        self,
        order_no: str,
        amount: Decimal,
        channel: str,
        subject: str,
        body: str = '',
        **kwargs
    ) -> Dict:
        """
        创建支付
        
        :param order_no: 订单号
        :param amount: 金额（元）
        :param channel: 支付渠道
        :param subject: 订单标题
        :param body: 订单描述
        :return: 支付信息
        """
        pass
    
    @abstractmethod
    def query_payment(self, payment_id: str) -> Dict:
        """
        查询支付
        
        :param payment_id: 支付ID
        :return: 支付信息
        """
        pass
    
    @abstractmethod
    def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Dict:
        """
        创建退款
        
        :param payment_id: 支付ID
        :param amount: 退款金额（元），不填则全额退款
        :param reason: 退款原因
        :return: 退款信息
        """
        pass
    
    @abstractmethod
    def verify_webhook(self, data: dict, signature: str = None) -> bool:
        """
        验证Webhook签名
        
        :param data: 通知数据
        :param signature: 签名
        :return: 是否验证通过
        """
        pass
    
    @abstractmethod
    def get_supported_channels(self) -> list:
        """
        获取支持的支付渠道
        
        :return: 支付渠道列表
        """
        pass
```

### 2. Ping++提供商实现

创建 `module_thesis/payment/pingpp_provider.py`:

```python
"""
Ping++支付提供商
"""
import pingpp
from typing import Dict, Optional
from decimal import Decimal

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException


class PingppProvider(PaymentProvider):
    """Ping++支付提供商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        pingpp.api_key = config['api_key']
        self.app_id = config['app_id']
        
        if config.get('private_key_path'):
            pingpp.private_key_path = config['private_key_path']
    
    def create_payment(
        self,
        order_no: str,
        amount: Decimal,
        channel: str,
        subject: str,
        body: str = '',
        **kwargs
    ) -> Dict:
        """创建支付"""
        try:
            # 渠道映射
            channel_map = {
                'alipay_pc': 'alipay_pc_direct',
                'alipay_wap': 'alipay_wap',
                'alipay_qr': 'alipay_qr',
                'wx_pub': 'wx_pub',
                'wx_lite': 'wx_lite',
                'wx_wap': 'wx_wap',
                'wx_pub_qr': 'wx_pub_qr'
            }
            
            pingpp_channel = channel_map.get(channel, channel)
            amount_fen = int(amount * 100)
            
            charge = pingpp.Charge.create(
                order_no=order_no,
                amount=amount_fen,
                app=dict(id=self.app_id),
                channel=pingpp_channel,
                currency='cny',
                client_ip=kwargs.get('client_ip', '127.0.0.1'),
                subject=subject,
                body=body,
                extra=kwargs.get('extra', {})
            )
            
            return {
                'provider': 'pingpp',
                'payment_id': charge.id,
                'order_no': charge.order_no,
                'amount': charge.amount / 100,
                'credential': charge.credential,
                'channel': channel
            }
        except Exception as e:
            raise ServiceException(message=f'Ping++创建支付失败: {str(e)}')
    
    def query_payment(self, payment_id: str) -> Dict:
        """查询支付"""
        try:
            charge = pingpp.Charge.retrieve(payment_id)
            return {
                'payment_id': charge.id,
                'order_no': charge.order_no,
                'amount': charge.amount / 100,
                'paid': charge.paid,
                'refunded': charge.refunded,
                'transaction_no': charge.transaction_no
            }
        except Exception as e:
            raise ServiceException(message=f'Ping++查询支付失败: {str(e)}')
    
    def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Dict:
        """创建退款"""
        try:
            refund_data = {'description': reason}
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = pingpp.Refund.create(payment_id, **refund_data)
            return {
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'succeed': refund.succeed,
                'status': refund.status
            }
        except Exception as e:
            raise ServiceException(message=f'Ping++创建退款失败: {str(e)}')
    
    def verify_webhook(self, data: dict, signature: str = None) -> bool:
        """验证Webhook签名"""
        try:
            pub_key_path = self.config.get('pub_key_path')
            if not pub_key_path:
                return True  # 如果没有配置公钥，跳过验证
            
            return pingpp.Webhook.verify_signature(
                data.encode('utf-8'),
                signature,
                pub_key_path
            )
        except Exception:
            return False
    
    def get_supported_channels(self) -> list:
        """获取支持的支付渠道"""
        return [
            'alipay_pc', 'alipay_wap', 'alipay_qr',
            'wx_pub', 'wx_lite', 'wx_wap', 'wx_pub_qr'
        ]
```

### 3. 支付宝提供商实现

创建 `module_thesis/payment/alipay_provider.py`:

```python
"""
支付宝支付提供商
"""
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
# ... 其他导入

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException


class AlipayProvider(PaymentProvider):
    """支付宝支付提供商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        alipay_config = AlipayClientConfig()
        alipay_config.app_id = config['app_id']
        alipay_config.app_private_key = config['private_key']
        alipay_config.alipay_public_key = config['alipay_public_key']
        
        if config.get('is_sandbox'):
            alipay_config.server_url = 'https://openapi.alipaydev.com/gateway.do'
        else:
            alipay_config.server_url = 'https://openapi.alipay.com/gateway.do'
        
        self.client = DefaultAlipayClient(alipay_client_config=alipay_config)
        self.notify_url = config['notify_url']
        self.return_url = config.get('return_url', '')
    
    def create_payment(self, order_no: str, amount: Decimal, channel: str, subject: str, body: str = '', **kwargs) -> Dict:
        """创建支付"""
        # 实现支付宝支付创建逻辑
        # ...
        pass
    
    # ... 其他方法实现
```

### 4. 微信提供商实现

创建 `module_thesis/payment/wechat_provider.py`:

```python
"""
微信支付提供商
"""
from wechatpayv3 import WeChatPay, WeChatPayType

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException


class WechatProvider(PaymentProvider):
    """微信支付提供商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=config['mch_id'],
            private_key=self._load_private_key(config['private_cert_path']),
            cert_serial_no=config['cert_serial_no'],
            apiv3_key=config['api_v3_key'],
            appid=config['app_id'],
            notify_url=config['notify_url']
        )
    
    def create_payment(self, order_no: str, amount: Decimal, channel: str, subject: str, body: str = '', **kwargs) -> Dict:
        """创建支付"""
        # 实现微信支付创建逻辑
        # ...
        pass
    
    # ... 其他方法实现
```


### 5. 支付网关服务（核心）

创建 `module_thesis/service/payment_gateway_service.py`:

```python
"""
统一支付网关服务
"""
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from exceptions.exception import ServiceException
from module_thesis.dao import PaymentConfigDao
from module_thesis.payment.base_provider import PaymentProvider
from module_thesis.payment.pingpp_provider import PingppProvider
from module_thesis.payment.alipay_provider import AlipayProvider
from module_thesis.payment.wechat_provider import WechatProvider


class PaymentGatewayService:
    """统一支付网关服务"""
    
    # 提供商映射
    PROVIDER_MAP = {
        'pingpp': PingppProvider,
        'alipay': AlipayProvider,
        'wechat': WechatProvider
    }
    
    @classmethod
    async def get_provider(
        cls,
        query_db: AsyncSession,
        provider_type: str = None,
        channel: str = None
    ) -> PaymentProvider:
        """
        获取支付提供商
        
        :param query_db: 数据库会话
        :param provider_type: 指定提供商类型（可选）
        :param channel: 支付渠道（用于自动选择提供商）
        :return: 支付提供商实例
        """
        if provider_type:
            # 指定提供商
            config = await PaymentConfigDao.get_config_by_type(query_db, provider_type)
            if not config or config.is_enabled != '1':
                raise ServiceException(message=f'支付提供商{provider_type}未启用')
        else:
            # 自动选择：根据渠道和优先级
            configs = await PaymentConfigDao.get_enabled_configs(query_db)
            
            if not configs:
                raise ServiceException(message='没有可用的支付提供商')
            
            # 如果指定了渠道，筛选支持该渠道的提供商
            if channel:
                configs = [c for c in configs if channel in c.supported_channels]
                if not configs:
                    raise ServiceException(message=f'没有支持{channel}渠道的支付提供商')
            
            # 按优先级排序，选择第一个
            configs.sort(key=lambda x: x.priority, reverse=True)
            config = configs[0]
        
        # 创建提供商实例
        provider_class = cls.PROVIDER_MAP.get(config.provider_type)
        if not provider_class:
            raise ServiceException(message=f'不支持的支付提供商: {config.provider_type}')
        
        return provider_class(config.config_data)
    
    @classmethod
    async def create_payment(
        cls,
        query_db: AsyncSession,
        order_no: str,
        amount: Decimal,
        channel: str,
        subject: str,
        body: str = '',
        provider_type: str = None,
        **kwargs
    ) -> Dict:
        """
        创建支付（统一入口）
        
        :param query_db: 数据库会话
        :param order_no: 订单号
        :param amount: 金额（元）
        :param channel: 支付渠道
        :param subject: 订单标题
        :param body: 订单描述
        :param provider_type: 指定提供商（可选）
        :return: 支付信息
        """
        try:
            # 获取支付提供商
            provider = await cls.get_provider(query_db, provider_type, channel)
            
            # 创建支付
            result = provider.create_payment(
                order_no=order_no,
                amount=amount,
                channel=channel,
                subject=subject,
                body=body,
                **kwargs
            )
            
            return result
        except ServiceException:
            raise
        except Exception as e:
            raise ServiceException(message=f'创建支付失败: {str(e)}')
    
    @classmethod
    async def query_payment(
        cls,
        query_db: AsyncSession,
        payment_id: str,
        provider_type: str
    ) -> Dict:
        """
        查询支付
        
        :param query_db: 数据库会话
        :param payment_id: 支付ID
        :param provider_type: 提供商类型
        :return: 支付信息
        """
        try:
            provider = await cls.get_provider(query_db, provider_type)
            return provider.query_payment(payment_id)
        except Exception as e:
            raise ServiceException(message=f'查询支付失败: {str(e)}')
    
    @classmethod
    async def create_refund(
        cls,
        query_db: AsyncSession,
        payment_id: str,
        provider_type: str,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Dict:
        """
        创建退款
        
        :param query_db: 数据库会话
        :param payment_id: 支付ID
        :param provider_type: 提供商类型
        :param amount: 退款金额（可选）
        :param reason: 退款原因
        :return: 退款信息
        """
        try:
            provider = await cls.get_provider(query_db, provider_type)
            return provider.create_refund(payment_id, amount, reason)
        except Exception as e:
            raise ServiceException(message=f'创建退款失败: {str(e)}')
    
    @classmethod
    async def get_available_channels(cls, query_db: AsyncSession) -> List[Dict]:
        """
        获取所有可用的支付渠道
        
        :param query_db: 数据库会话
        :return: 支付渠道列表
        """
        configs = await PaymentConfigDao.get_enabled_configs(query_db)
        
        channels = []
        channel_map = {
            'alipay_pc': {'name': '支付宝PC支付', 'icon': 'alipay'},
            'alipay_wap': {'name': '支付宝手机支付', 'icon': 'alipay'},
            'alipay_qr': {'name': '支付宝扫码支付', 'icon': 'alipay'},
            'wx_pub': {'name': '微信公众号支付', 'icon': 'wechat'},
            'wx_lite': {'name': '微信小程序支付', 'icon': 'wechat'},
            'wx_wap': {'name': '微信H5支付', 'icon': 'wechat'},
            'wx_pub_qr': {'name': '微信扫码支付', 'icon': 'wechat'},
            'wx_native': {'name': '微信Native支付', 'icon': 'wechat'},
            'wx_jsapi': {'name': '微信JSAPI支付', 'icon': 'wechat'}
        }
        
        seen_channels = set()
        for config in configs:
            for channel in config.supported_channels:
                if channel not in seen_channels:
                    channel_info = channel_map.get(channel, {'name': channel, 'icon': 'payment'})
                    channels.append({
                        'channel': channel,
                        'name': channel_info['name'],
                        'icon': channel_info['icon'],
                        'provider': config.provider_name,
                        'fee_rate': float(config.fee_rate)
                    })
                    seen_channels.add(channel)
        
        return channels
```

### 6. Controller接口（统一入口）

在 `module_thesis/controller/payment_controller.py` 中创建：

```python
"""
统一支付控制器
"""
from typing import Annotated
from fastapi import APIRouter, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import DataResponseModel, CrudResponseModel
from common.router import APIRouter as CustomAPIRouter
from config.get_db import DBSessionDependency
from module_admin.aspect.interface_auth import UserInterfaceAuthDependency
from module_admin.aspect.data_scope import GetCurrentUserDependency
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_thesis.service.payment_gateway_service import PaymentGatewayService
from utils.response_util import ResponseUtil
from utils.log_util import logger


payment_controller = CustomAPIRouter(prefix='/payment', tags=['支付管理'])


@payment_controller.get(
    '/channels',
    summary='获取可用支付渠道',
    description='获取所有可用的支付渠道列表',
    response_model=DataResponseModel
)
async def get_available_channels(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取可用支付渠道"""
    channels = await PaymentGatewayService.get_available_channels(query_db)
    return ResponseUtil.success(data=channels)


@payment_controller.post(
    '/create',
    summary='创建支付',
    description='创建支付订单（统一入口）',
    response_model=DataResponseModel
)
async def create_payment(
    request: Request,
    order_id: Annotated[int, Query(description='订单ID')],
    channel: Annotated[str, Query(description='支付渠道')],
    provider: Annotated[str | None, Query(description='指定支付提供商')] = None,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, GetCurrentUserDependency()],
) -> Response:
    """创建支付"""
    from module_thesis.service.order_service import OrderService
    
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
    result = await PaymentGatewayService.create_payment(
        query_db,
        order_no=order.order_no,
        amount=order.amount,
        channel=channel,
        subject=f'购买{order.order_type}',
        body=f'订单号：{order.order_no}',
        provider_type=provider,
        client_ip=client_ip
    )
    
    logger.info(f'创建支付成功: {order.order_no}, 渠道: {channel}, 提供商: {result.get("provider")}')
    return ResponseUtil.success(data=result)


@payment_controller.get(
    '/query',
    summary='查询支付',
    description='查询支付状态',
    response_model=DataResponseModel
)
async def query_payment(
    request: Request,
    payment_id: Annotated[str, Query(description='支付ID')],
    provider: Annotated[str, Query(description='支付提供商')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """查询支付"""
    result = await PaymentGatewayService.query_payment(query_db, payment_id, provider)
    return ResponseUtil.success(data=result)


@payment_controller.post(
    '/refund',
    summary='创建退款',
    description='创建退款申请',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:payment:refund')]
)
async def create_refund(
    request: Request,
    payment_id: Annotated[str, Query(description='支付ID')],
    provider: Annotated[str, Query(description='支付提供商')],
    amount: Annotated[float | None, Query(description='退款金额')] = None,
    reason: Annotated[str, Query(description='退款原因')] = '',
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """创建退款"""
    from decimal import Decimal
    
    refund_amount = Decimal(str(amount)) if amount else None
    result = await PaymentGatewayService.create_refund(
        query_db,
        payment_id,
        provider,
        refund_amount,
        reason
    )
    
    logger.info(f'创建退款成功: {payment_id}, 金额: {amount}')
    return ResponseUtil.success(data=result)


# Webhook回调（支持多个提供商）
@payment_controller.post(
    '/webhook/{provider}',
    summary='支付回调',
    description='支付提供商回调接口',
    include_in_schema=False
)
async def payment_webhook(
    request: Request,
    provider: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> dict:
    """支付回调（统一入口）"""
    try:
        # 获取提供商实例
        provider_instance = await PaymentGatewayService.get_provider(query_db, provider)
        
        # 获取原始数据
        if provider == 'pingpp':
            raw_data = await request.body()
            signature = request.headers.get('x-pingplusplus-signature')
            
            # 验证签名
            if not provider_instance.verify_webhook(raw_data.decode('utf-8'), signature):
                return {'status': 'fail', 'message': '签名验证失败'}
            
            # 解析数据
            import json
            event = json.loads(raw_data.decode('utf-8'))
            
            if event['type'] == 'charge.succeeded':
                charge = event['data']['object']
                order_no = charge['order_no']
                transaction_no = charge['transaction_no']
                
                # 处理支付
                from module_thesis.service.order_service import OrderService
                await OrderService.process_payment(query_db, order_no, transaction_no)
        
        elif provider == 'alipay':
            form_data = await request.form()
            params = dict(form_data)
            
            # 验证签名
            if not provider_instance.verify_webhook(params):
                return 'fail'
            
            # 处理支付
            order_no = params.get('out_trade_no')
            trade_status = params.get('trade_status')
            trade_no = params.get('trade_no')
            
            if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                from module_thesis.service.order_service import OrderService
                await OrderService.process_payment(query_db, order_no, trade_no)
            
            return 'success'
        
        elif provider == 'wechat':
            headers = dict(request.headers)
            body = await request.body()
            
            # 验证签名并解密
            result = provider_instance.verify_webhook(headers, body.decode('utf-8'))
            
            # 处理支付
            order_no = result.get('out_trade_no')
            trade_state = result.get('trade_state')
            transaction_id = result.get('transaction_id')
            
            if trade_state == 'SUCCESS':
                from module_thesis.service.order_service import OrderService
                await OrderService.process_payment(query_db, order_no, transaction_id)
            
            return {'code': 'SUCCESS', 'message': '成功'}
        
        return {'status': 'success'}
    except Exception as e:
        logger.error(f'{provider}支付回调处理失败: {str(e)}')
        return {'status': 'fail', 'message': str(e)}
```

---

## 三、前端集成

### 1. 支付渠道选择组件

```vue
<template>
  <div class="payment-selector">
    <h3>选择支付方式</h3>
    
    <el-radio-group v-model="selectedChannel" class="channel-list">
      <el-radio
        v-for="channel in availableChannels"
        :key="channel.channel"
        :label="channel.channel"
        class="channel-item"
      >
        <div class="channel-content">
          <img :src="`/icons/${channel.icon}.png`" :alt="channel.name" />
          <div class="channel-info">
            <span class="channel-name">{{ channel.name }}</span>
            <span class="channel-provider">{{ channel.provider }}</span>
          </div>
          <span class="channel-fee">手续费: {{ (channel.fee_rate * 100).toFixed(2) }}%</span>
        </div>
      </el-radio>
    </el-radio-group>
    
    <div class="order-summary">
      <p>订单金额：<span class="amount">¥{{ orderAmount }}</span></p>
      <p>手续费：<span class="fee">¥{{ feeAmount }}</span></p>
      <p>实付金额：<span class="total">¥{{ totalAmount }}</span></p>
    </div>
    
    <el-button
      type="primary"
      size="large"
      @click="handlePay"
      :loading="paying"
      :disabled="!selectedChannel"
    >
      立即支付
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAvailableChannels, createPayment } from '@/api/payment'

const props = defineProps({
  orderId: Number,
  orderAmount: Number
})

const availableChannels = ref([])
const selectedChannel = ref('')
const paying = ref(false)

// 计算手续费
const feeAmount = computed(() => {
  if (!selectedChannel.value) return 0
  const channel = availableChannels.value.find(c => c.channel === selectedChannel.value)
  return channel ? (props.orderAmount * channel.fee_rate).toFixed(2) : 0
})

// 计算总金额
const totalAmount = computed(() => {
  return (parseFloat(props.orderAmount) + parseFloat(feeAmount.value)).toFixed(2)
})

// 加载可用支付渠道
onMounted(async () => {
  try {
    const res = await getAvailableChannels()
    availableChannels.value = res.data
    
    // 默认选择第一个
    if (availableChannels.value.length > 0) {
      selectedChannel.value = availableChannels.value[0].channel
    }
  } catch (error) {
    ElMessage.error('加载支付渠道失败')
  }
})

// 处理支付
async function handlePay() {
  if (!selectedChannel.value) {
    ElMessage.warning('请选择支付方式')
    return
  }
  
  paying.value = true
  
  try {
    const res = await createPayment({
      order_id: props.orderId,
      channel: selectedChannel.value
    })
    
    // 根据不同渠道处理支付
    handlePaymentResult(res.data)
  } catch (error) {
    ElMessage.error('创建支付失败')
  } finally {
    paying.value = false
  }
}

// 处理支付结果
function handlePaymentResult(data) {
  const { channel, credential } = data
  
  if (channel.startsWith('alipay')) {
    // 支付宝支付：跳转
    const payUrl = credential[`alipay_${channel.split('_')[1]}_direct`] || credential.alipay_pc_direct
    window.location.href = payUrl
  } else if (channel.startsWith('wx')) {
    // 微信支付：显示二维码或调起支付
    if (channel.includes('qr') || channel === 'wx_native') {
      showWechatQRCode(credential.wx_pub_qr || credential.wx_native)
    } else if (channel === 'wx_jsapi') {
      callWechatPay(credential.wx_jsapi)
    }
  }
}
</script>
```

---

## 四、配置管理界面

### 1. 支付配置管理页面

```vue
<template>
  <div class="payment-config-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>支付配置管理</span>
          <el-button type="primary" @click="handleAdd">添加配置</el-button>
        </div>
      </template>
      
      <el-table :data="configList" border>
        <el-table-column prop="provider_name" label="提供商" width="150" />
        <el-table-column prop="provider_type" label="类型" width="100" />
        <el-table-column label="支持渠道" width="300">
          <template #default="{ row }">
            <el-tag
              v-for="channel in row.supported_channels"
              :key="channel"
              size="small"
              style="margin: 2px"
            >
              {{ channel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fee_rate" label="费率" width="100">
          <template #default="{ row }">
            {{ (row.fee_rate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_enabled"
              active-value="1"
              inactive-value="0"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
```

---

## 五、使用示例

### 场景1：用户支付（自动选择最优提供商）

```python
# 创建支付，系统自动选择优先级最高的提供商
result = await PaymentGatewayService.create_payment(
    query_db,
    order_no='ORDER20240125001',
    amount=Decimal('199.00'),
    channel='alipay_pc',  # 只指定渠道
    subject='购买专业版会员'
)
# 系统会自动选择：Ping++ > 支付宝SDK（根据优先级）
```

### 场景2：指定使用某个提供商

```python
# 强制使用支付宝SDK
result = await PaymentGatewayService.create_payment(
    query_db,
    order_no='ORDER20240125001',
    amount=Decimal('199.00'),
    channel='alipay_pc',
    subject='购买专业版会员',
    provider_type='alipay'  # 指定使用支付宝SDK
)
```

### 场景3：动态切换提供商

```python
# 在数据库中修改配置，无需改代码
# 1. 禁用Ping++
UPDATE ai_write_payment_config SET is_enabled='0' WHERE provider_type='pingpp';

# 2. 启用支付宝SDK
UPDATE ai_write_payment_config SET is_enabled='1', priority=100 WHERE provider_type='alipay';

# 系统会自动使用支付宝SDK
```

---

## 六、优势总结

### 1. 灵活性
- ✅ 支持多种支付方式
- ✅ 可动态切换提供商
- ✅ 可同时启用多个提供商

### 2. 可维护性
- ✅ 统一的接口设计
- ✅ 配置化管理
- ✅ 易于扩展新提供商

### 3. 成本优化
- ✅ 可根据费率选择提供商
- ✅ 可设置优先级
- ✅ 支持A/B测试

### 4. 风险控制
- ✅ 多个提供商互为备份
- ✅ 单个提供商故障不影响业务
- ✅ 可快速切换

---

## 七、实施步骤

1. ✅ 创建数据库表和配置
2. ✅ 实现支付提供商基类
3. ✅ 实现各个提供商（Ping++、支付宝、微信）
4. ✅ 实现统一网关服务
5. ✅ 实现Controller接口
6. ✅ 前端集成
7. ✅ 测试和上线

**预计时间**：2-3天

需要我帮您实现具体的代码吗？
