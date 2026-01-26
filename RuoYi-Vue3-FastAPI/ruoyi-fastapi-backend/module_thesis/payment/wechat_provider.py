"""
微信支付提供商（安全增强版）
"""
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

from module_thesis.payment.base_provider import PaymentProvider
from exceptions.exception import ServiceException
from utils.log_util import logger
from utils.sensitive_filter import mask_sensitive_data, get_safe_error_message


class WechatProvider(PaymentProvider):
    """微信支付提供商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # 验证配置
        self._validate_config(config)
        
        # 延迟导入，避免未安装SDK时报错
        try:
            from wechatpayv3 import WeChatPay, WeChatPayType
            
            # 读取私钥
            with open(config['private_cert_path'], 'r') as f:
                private_key = f.read()
            
            self.wxpay = WeChatPay(
                wechatpay_type=WeChatPayType.NATIVE,
                mchid=config['mch_id'],
                private_key=private_key,
                cert_serial_no=config['cert_serial_no'],
                apiv3_key=config['api_v3_key'],
                appid=config['app_id'],
                notify_url=config['notify_url']
            )
            self.app_id = config['app_id']
            self.mch_id = config['mch_id']
        except ImportError:
            raise ServiceException(message='微信支付SDK未安装，请运行: pip install wechatpayv3')
        except FileNotFoundError:
            raise ServiceException(message='微信支付证书文件不存在')
    
    def _validate_config(self, config: dict):
        """验证微信支付配置"""
        required_fields = ['app_id', 'mch_id', 'api_v3_key', 'cert_serial_no', 'private_cert_path', 'notify_url']
        missing_fields = [f for f in required_fields if not config.get(f)]
        
        if missing_fields:
            raise ServiceException(
                message=f'微信支付配置缺少必需字段: {", ".join(missing_fields)}'
            )
        
        # 验证回调地址必须是HTTPS
        if not config['notify_url'].startswith('https://'):
            is_test_mode = config.get('is_test_mode', False)
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
            # 使用Decimal处理金额
            amount_fen = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            # 根据渠道选择支付方式
            if channel == 'wx_native':
                # Native支付（扫码）
                code, message = self.wxpay.pay(
                    description=subject,
                    out_trade_no=order_no,
                    amount={'total': amount_fen},
                    pay_type=self.wxpay.WeChatPayType.NATIVE
                )
            elif channel == 'wx_jsapi':
                # JSAPI支付（公众号/小程序）
                openid = kwargs.get('openid')
                if not openid:
                    raise ServiceException(message='JSAPI支付需要提供openid')
                
                code, message = self.wxpay.pay(
                    description=subject,
                    out_trade_no=order_no,
                    amount={'total': amount_fen},
                    pay_type=self.wxpay.WeChatPayType.JSAPI,
                    payer={'openid': openid}
                )
            elif channel == 'wx_h5':
                # H5支付
                code, message = self.wxpay.pay(
                    description=subject,
                    out_trade_no=order_no,
                    amount={'total': amount_fen},
                    pay_type=self.wxpay.WeChatPayType.H5,
                    scene_info={
                        'payer_client_ip': kwargs.get('client_ip', '127.0.0.1'),
                        'h5_info': {'type': 'Wap'}
                    }
                )
            else:
                raise ServiceException(message=f'不支持的微信支付渠道: {channel}')
            
            if code == 200:
                result = {
                    'provider': 'wechat',
                    'payment_id': order_no,
                    'order_no': order_no,
                    'amount': amount,
                    'credential': {channel: message.get('code_url') or message.get('h5_url') or message},
                    'channel': channel
                }
                
                # 记录日志（脱敏）
                logger.info(f'微信创建支付成功: {mask_sensitive_data(result)}')
                
                return result
            else:
                raise ServiceException(message=f'微信支付创建失败: {message}')
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'微信创建支付失败: order_no={order_no}, error={str(e)}', exc_info=True)
            raise ServiceException(message=get_safe_error_message(e, '支付创建失败，请稍后重试'))
    
    def query_payment(self, payment_id: str) -> Dict:
        """查询支付"""
        try:
            code, message = self.wxpay.query(out_trade_no=payment_id)
            
            if code == 200:
                trade_state = message.get('trade_state')
                return {
                    'payment_id': payment_id,
                    'order_no': message.get('out_trade_no'),
                    'amount': Decimal(str(message.get('amount', {}).get('total', 0))) / 100,
                    'paid': trade_state == 'SUCCESS',
                    'refunded': trade_state == 'REFUND',
                    'transaction_no': message.get('transaction_id')
                }
            else:
                raise ServiceException(message=f'查询失败: {message}')
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'微信查询支付失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message=get_safe_error_message(e, '支付查询失败，请稍后重试'))
    
    def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Dict:
        """创建退款"""
        try:
            # 先查询订单获取总金额
            query_result = self.query_payment(payment_id)
            total_amount = int((query_result['amount'] * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            refund_amount = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) if amount else total_amount
            
            code, message = self.wxpay.refund(
                out_trade_no=payment_id,
                out_refund_no=f'REFUND_{payment_id}',
                amount={
                    'refund': refund_amount,
                    'total': total_amount,
                    'currency': 'CNY'
                },
                reason=reason
            )
            
            if code == 200:
                return {
                    'refund_id': message.get('refund_id'),
                    'amount': Decimal(str(message.get('amount', {}).get('refund', 0))) / 100,
                    'succeed': message.get('status') == 'SUCCESS',
                    'status': message.get('status')
                }
            else:
                raise ServiceException(message=f'退款失败: {message}')
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f'微信创建退款失败: payment_id={payment_id}, error={str(e)}')
            raise ServiceException(message=get_safe_error_message(e, '退款创建失败，请稍后重试'))
    
    def verify_webhook(self, data: dict, signature: str = None) -> bool:
        """验证Webhook签名"""
        try:
            # 微信支付V3的签名验证
            # 需要从headers中获取签名信息
            headers = data.get('headers', {})
            body = data.get('body', '')
            
            result = self.wxpay.verify(
                headers=headers,
                body=body
            )
            
            if not result:
                logger.warning('微信Webhook签名验证失败')
            
            return result
        except Exception as e:
            logger.error(f'微信Webhook签名验证异常: {str(e)}')
            return False
    
    def get_supported_channels(self) -> list:
        """获取支持的支付渠道"""
        return ['wx_native', 'wx_jsapi', 'wx_h5']
