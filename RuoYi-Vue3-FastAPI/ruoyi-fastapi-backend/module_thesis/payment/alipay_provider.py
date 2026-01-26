"""
支付宝支付提供商（安全增强版）
"""
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException
from utils.log_util import logger
from utils.sensitive_filter import mask_sensitive_data, get_safe_error_message


class AlipayProvider(PaymentProvider):
    """支付宝支付提供商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # 验证配置
        self._validate_config(config)
        
        # 延迟导入，避免未安装SDK时报错
        try:
            from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
            from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
            
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
        except ImportError:
            raise ServiceException(message='支付宝SDK未安装，请运行: pip install alipay-sdk-python')
    
    def _validate_config(self, config: dict):
        """验证支付宝配置"""
        required_fields = ['app_id', 'private_key', 'alipay_public_key', 'notify_url']
        missing_fields = [f for f in required_fields if not config.get(f)]
        
        if missing_fields:
            raise ServiceException(
                message=f'支付宝配置缺少必需字段: {", ".join(missing_fields)}'
            )
        
        # 验证App ID格式（16位数字）
        if not config['app_id'].isdigit() or len(config['app_id']) != 16:
            raise ServiceException(message='支付宝App ID格式错误，应为16位数字')
        
        # 验证回调地址必须是HTTPS
        if not config['notify_url'].startswith('https://'):
            is_test_mode = config.get('is_sandbox', False)
            if not is_test_mode:
                raise ServiceException(message='生产环境回调地址必须使用HTTPS')
    
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
            from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
            from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
            
            model = AlipayTradePagePayModel()
            model.out_trade_no = order_no
            model.total_amount = str(amount)  # 支付宝使用字符串
            model.subject = subject
            model.body = body
            model.product_code = 'FAST_INSTANT_TRADE_PAY'
            
            request = AlipayTradePagePayRequest(biz_model=model)
            request.notify_url = self.notify_url
            request.return_url = self.return_url
            
            response = self.client.page_execute(request, http_method='GET')
            
            result = {
                'provider': 'alipay',
                'payment_id': order_no,  # 支付宝使用订单号作为支付ID
                'order_no': order_no,
                'amount': amount,
                'credential': {'alipay_pc_direct': response},
                'channel': channel
            }
            
            # 记录日志（脱敏）
            logger.info(f'支付宝创建支付成功: {mask_sensitive_data(result)}')
            
            return result
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'支付宝创建支付失败: order_no={order_no}, error={str(e)}', exc_info=True)
            raise ServiceException(message=get_safe_error_message(e, '支付创建失败，请稍后重试'))
    
    def query_payment(self, payment_id: str) -> Dict:
        """查询支付"""
        try:
            from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
            from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
            
            model = AlipayTradeQueryModel()
            model.out_trade_no = payment_id
            
            request = AlipayTradeQueryRequest(biz_model=model)
            response = self.client.execute(request)
            
            if response.get('code') == '10000':
                return {
                    'payment_id': payment_id,
                    'order_no': response.get('out_trade_no'),
                    'amount': Decimal(str(response.get('total_amount', '0'))),
                    'paid': response.get('trade_status') in ['TRADE_SUCCESS', 'TRADE_FINISHED'],
                    'refunded': False,
                    'transaction_no': response.get('trade_no')
                }
            else:
                raise ServiceException(message=f'查询失败: {response.get("msg")}')
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'支付宝查询支付失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message=get_safe_error_message(e, '支付查询失败，请稍后重试'))
    
    def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Dict:
        """创建退款"""
        try:
            from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
            from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
            
            model = AlipayTradeRefundModel()
            model.out_trade_no = payment_id
            if amount:
                model.refund_amount = str(amount)
            model.refund_reason = reason
            
            request = AlipayTradeRefundRequest(biz_model=model)
            response = self.client.execute(request)
            
            if response.get('code') == '10000':
                return {
                    'refund_id': response.get('trade_no'),
                    'amount': Decimal(str(response.get('refund_fee', '0'))),
                    'succeed': True,
                    'status': 'success'
                }
            else:
                raise ServiceException(message=f'退款失败: {response.get("msg")}')
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'支付宝创建退款失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message=get_safe_error_message(e, '退款创建失败，请稍后重试'))
    
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
    
    def get_supported_channels(self) -> list:
        """获取支持的支付渠道"""
        return ['alipay_pc', 'alipay_wap', 'alipay_qr']
