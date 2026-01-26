"""
统一支付网关服务（安全增强版）
"""
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_thesis.dao import PaymentConfigDao, PaymentTransactionDao
from module_thesis.payment.base_provider import PaymentProvider
from module_thesis.payment.pingpp_provider import PingppProvider
from module_thesis.payment.alipay_provider import AlipayProvider
from module_thesis.payment.wechat_provider import WechatProvider
from utils.log_util import logger
from utils.config_crypto import ConfigCrypto
from utils.sensitive_filter import mask_sensitive_data


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
    ) -> tuple[PaymentProvider, str]:
        """
        获取支付提供商
        
        :param query_db: 数据库会话
        :param provider_type: 指定提供商类型（可选）
        :param channel: 支付渠道（用于自动选择提供商）
        :return: (支付提供商实例, 提供商类型)
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
            configs = sorted(configs, key=lambda x: x.priority, reverse=True)
            config = configs[0]
            provider_type = config.provider_type
        
        # 解密配置
        try:
            decrypted_config = ConfigCrypto.decrypt_dict(config.config_data)
        except Exception as e:
            logger.error(f'解密支付配置失败: {str(e)}')
            # 如果解密失败，尝试使用原始配置（可能未加密）
            decrypted_config = config.config_data
        
        # 创建提供商实例
        provider_class = cls.PROVIDER_MAP.get(config.provider_type)
        if not provider_class:
            raise ServiceException(message=f'不支持的支付提供商: {config.provider_type}')
        
        try:
            provider = provider_class(decrypted_config)
            return provider, provider_type
        except ServiceException as e:
            raise e
        except Exception as e:
            logger.error(f'初始化支付提供商失败: {str(e)}')
            raise ServiceException(message='初始化支付提供商失败，请检查配置')
    
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
        """
        创建支付（统一入口，防重复）
        
        :param query_db: 数据库会话
        :param order_id: 订单ID
        :param order_no: 订单号
        :param amount: 金额（元）
        :param channel: 支付渠道
        :param subject: 订单标题
        :param body: 订单描述
        :param provider_type: 指定提供商（可选）
        :return: 支付信息
        """
        try:
            # 检查是否已存在待支付的流水（防重复）
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
                'fee_amount': Decimal('0.00'),  # 手续费后续计算
                'status': 'pending',
                'create_time': datetime.now()
            }
            await PaymentTransactionDao.add_transaction(query_db, transaction_data)
            await query_db.commit()
            
            logger.info(f'创建支付成功: order_no={order_no}, provider={actual_provider_type}, channel={channel}')
            
            return result
        except ServiceException:
            await query_db.rollback()
            raise
        except Exception as e:
            await query_db.rollback()
            logger.error(f'创建支付失败: order_no={order_no}, error={str(e)}', exc_info=True)
            raise ServiceException(message='支付创建失败，请稍后重试')
    
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
            provider, _ = await cls.get_provider(query_db, provider_type)
            result = provider.query_payment(payment_id)
            
            # 更新流水状态
            if result.get('paid'):
                await PaymentTransactionDao.update_transaction_status(
                    query_db,
                    payment_id,
                    'success',
                    result.get('transaction_no'),
                    datetime.now()
                )
                await query_db.commit()
            
            return result
        except Exception as e:
            logger.error(f'查询支付失败: {str(e)}')
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
            provider, _ = await cls.get_provider(query_db, provider_type)
            result = provider.create_refund(payment_id, amount, reason)
            
            # 更新流水状态
            if result.get('succeed'):
                await PaymentTransactionDao.update_transaction_status(
                    query_db,
                    payment_id,
                    'refunded',
                    refund_time=datetime.now()
                )
                await query_db.commit()
            
            logger.info(f'创建退款成功: payment_id={payment_id}, amount={amount}')
            
            return result
        except Exception as e:
            await query_db.rollback()
            logger.error(f'创建退款失败: {str(e)}')
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
            'wx_jsapi': {'name': '微信JSAPI支付', 'icon': 'wechat'},
            'wx_h5': {'name': '微信H5支付', 'icon': 'wechat'}
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
                        'provider_type': config.provider_type,
                        'fee_rate': float(config.fee_rate)
                    })
                    seen_channels.add(channel)
        
        return channels
    
    @classmethod
    async def get_payment_configs(cls, query_db: AsyncSession) -> List[Dict]:
        """
        获取所有支付配置
        
        :param query_db: 数据库会话
        :return: 配置列表
        """
        configs = await PaymentConfigDao.get_all_configs(query_db)
        
        result = []
        for config in configs:
            result.append({
                'config_id': config.config_id,
                'provider_type': config.provider_type,
                'provider_name': config.provider_name,
                'supported_channels': config.supported_channels,
                'is_enabled': config.is_enabled,
                'priority': config.priority,
                'fee_rate': float(config.fee_rate),
                'status': config.status
            })
        
        return result
    
    @classmethod
    async def update_config_status(
        cls,
        query_db: AsyncSession,
        config_id: int,
        is_enabled: str
    ):
        """
        更新配置状态
        
        :param query_db: 数据库会话
        :param config_id: 配置ID
        :param is_enabled: 是否启用
        """
        try:
            await PaymentConfigDao.update_status(query_db, config_id, is_enabled)
            await query_db.commit()
            logger.info(f'更新支付配置状态成功: config_id={config_id}, is_enabled={is_enabled}')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新配置状态失败: {str(e)}')
