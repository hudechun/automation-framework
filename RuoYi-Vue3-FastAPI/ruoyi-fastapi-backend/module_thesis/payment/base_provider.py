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
