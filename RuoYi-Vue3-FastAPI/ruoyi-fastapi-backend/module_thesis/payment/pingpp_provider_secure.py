"""
Ping++支付提供商（安全增强版）
"""
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException
from utils.log_util import logger


class PingppProvider(PaymentProvider):
    """Ping++支付提供商（安全增强版）"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # 验证必需配置
        self._validate_config(config)
        
        # 延迟导入，避免未安装SDK时报错
        try:
            import pingpp
            pingpp.api_key = config['api_key']
            self.pingpp = pingpp
            self.app_id = config['app_id']
            self.is_test_mode = config.get('is_test_mode', False)
            
            if config.get('private_key_path'):
                pingpp.private_key_path = config['private_key_path']
                
            logger.info(f'Ping++提供商初始化成功: app_id={self.app_id}, test_mode={self.is_test_mode}')
        except ImportError:
            raise ServiceException(message='Ping++ SDK未安装，请运行: pip install pingpp')
        except Exception as e:
            logger.error(f'Ping++提供商初始化失败: {str(e)}')
            raise ServiceException(message='Ping++提供商初始化失败')
    
    def _validate_config(self, config: dict):
        """验证配置完整性"""
        required_fields = ['api_key', 'app_id']
        missing_fields = [f for f in required_fields if not config.get(f)]
        
        if missing_fields:
            raise ServiceException(message=f'Ping++配置缺少必需字段: {", ".join(missing_fields)}')
        
        # 验证API Key格式
        api_key = config['api_key']
        if not (api_key.startswith('sk_test_') or api_key.startswith('sk_live_')):
            raise ServiceException(message='Ping++ API Key格式错误')
        
        # 验证App ID格式
        if not config['app_id'].startswith('app_'):
            raise ServiceException(message='Ping++ App ID格式错误')
    
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
            # 验证金额
            if amount <= 0:
                raise ServiceException(message='支付金额必须大于0')
            
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
            
            # 金额转换（使用四舍五入）
            amount_fen = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            # 创建支付
            charge = self.pingpp.Charge.create(
                order_no=order_no,
                amount=amount_fen,
                app=dict(id=self.app_id),
                channel=pingpp_channel,
                currency='cny',
                client_ip=kwargs.get('client_ip', '127.0.0.1'),
                subject=subject[:32],  # 限制长度
                body=body[:128] if body else '',  # 限制长度
                extra=kwargs.get('extra', {})
            )
            
            logger.info(f'Ping++创建支付成功: order_no={order_no}, payment_id={charge.id}, channel={channel}')
            
            return {
                'provider': 'pingpp',
                'payment_id': charge.id,
                'order_no': charge.order_no,
                'amount': Decimal(str(charge.amount)) / 100,
                'credential': charge.credential,
                'channel': channel
            }
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'Ping++创建支付失败: order_no={order_no}, error={str(e)}', exc_info=True)
            raise ServiceException(message='支付创建失败，请稍后重试')
    
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
            raise ServiceException(message='支付查询失败，请稍后重试')
    
    def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Dict:
        """创建退款"""
        try:
            refund_data = {'description': reason[:255] if reason else ''}  # 限制长度
            
            if amount:
                if amount <= 0:
                    raise ServiceException(message='退款金额必须大于0')
                refund_data['amount'] = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            refund = self.pingpp.Refund.create(payment_id, **refund_data)
            
            logger.info(f'Ping++创建退款成功: payment_id={payment_id}, refund_id={refund.id}')
            
            return {
                'refund_id': refund.id,
                'amount': Decimal(str(refund.amount)) / 100,
                'succeed': refund.succeed,
                'status': refund.status
            }
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'Ping++创建退款失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message='退款创建失败，请稍后重试')
    
    def verify_webhook(self, data: dict, signature: str = None) -> bool:
        """验证Webhook签名（安全增强）"""
        try:
            pub_key_path = self.config.get('pub_key_path')
            
            # 生产环境必须配置公钥
            if not pub_key_path:
                if not self.is_test_mode:
                    logger.error('生产环境未配置Webhook公钥')
                    raise ServiceException(message='生产环境必须配置Webhook公钥')
                
                logger.warning('测试环境：跳过Webhook签名验证')
                return True
            
            # 验证签名
            data_str = data if isinstance(data, str) else str(data)
            result = self.pingpp.Webhook.verify_signature(
                data_str.encode('utf-8'),
                signature,
                pub_key_path
            )
            
            if not result:
                logger.warning(f'Ping++ Webhook签名验证失败')
            
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
