"""
Ping++支付提供商（安全增强版）
"""
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException
from utils.log_util import logger
from utils.sensitive_filter import mask_sensitive_data, get_safe_error_message


class PingppProvider(PaymentProvider):
    """Ping++支付提供商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # 验证配置
        self._validate_config(config)
        
        # 延迟导入，避免未安装SDK时报错
        try:
            import pingpp
            pingpp.api_key = config['api_key']
            self.pingpp = pingpp
            self.app_id = config['app_id']
            
            if config.get('private_key_path'):
                pingpp.private_key_path = config['private_key_path']
        except ImportError:
            raise ServiceException(message='Ping++ SDK未安装，请运行: pip install pingpp')
    
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
            raise ServiceException(message='Ping++ API Key格式错误，应以sk_test_或sk_live_开头')
        
        # 验证App ID格式
        if not config['app_id'].startswith('app_'):
            raise ServiceException(message='Ping++ App ID格式错误，应以app_开头')
    
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
            
            # 使用Decimal处理金额，避免精度丢失
            amount_fen = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            charge = self.pingpp.Charge.create(
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
            
            result = {
                'provider': 'pingpp',
                'payment_id': charge.id,
                'order_no': charge.order_no,
                'amount': Decimal(str(charge.amount)) / 100,
                'credential': charge.credential,
                'channel': channel
            }
            
            # 记录日志（脱敏）
            logger.info(f'Ping++创建支付成功: {mask_sensitive_data(result)}')
            
            return result
        except ServiceException:
            raise
        except Exception as e:
            # 记录详细错误（包含敏感信息）
            logger.error(f'Ping++创建支付失败: order_no={order_no}, error={str(e)}', exc_info=True)
            # 返回通用错误信息（不包含敏感信息）
            raise ServiceException(message=get_safe_error_message(e, '支付创建失败，请稍后重试'))
    
    def query_payment(self, payment_id: str) -> Dict:
        """查询支付"""
        try:
            charge = self.pingpp.Charge.retrieve(payment_id)
            return {
                'payment_id': charge.id,
                'order_no': charge.order_no,
                'amount': Decimal(str(charge.amount)) / 100,
                'paid': charge.paid,
                'refunded': charge.refunded,
                'transaction_no': charge.transaction_no
            }
        except Exception as e:
            logger.error(f'Ping++查询支付失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message=get_safe_error_message(e, '支付查询失败，请稍后重试'))
    
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
                # 使用Decimal处理金额
                refund_data['amount'] = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            refund = self.pingpp.Refund.create(payment_id, **refund_data)
            return {
                'refund_id': refund.id,
                'amount': Decimal(str(refund.amount)) / 100,
                'succeed': refund.succeed,
                'status': refund.status
            }
        except Exception as e:
            logger.error(f'Ping++创建退款失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message=get_safe_error_message(e, '退款创建失败，请稍后重试'))
    
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
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'Ping++ Webhook签名验证异常: {str(e)}')
            return False
    
    def get_supported_channels(self) -> list:
        """获取支持的支付渠道"""
        return [
            'alipay_pc', 'alipay_wap', 'alipay_qr',
            'wx_pub', 'wx_lite', 'wx_wap', 'wx_pub_qr'
        ]
