"""
支付模块
"""
from module_thesis.payment.base_provider import PaymentProvider
from module_thesis.payment.pingpp_provider import PingppProvider
from module_thesis.payment.alipay_provider import AlipayProvider
from module_thesis.payment.wechat_provider import WechatProvider

__all__ = [
    'PaymentProvider',
    'PingppProvider',
    'AlipayProvider',
    'WechatProvider',
]
