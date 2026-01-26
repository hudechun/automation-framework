"""
支付相关实体类
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, BigInteger, String, DateTime, CHAR, Integer, JSON, DECIMAL
from sqlalchemy.orm import declarative_base

from config.database import Base


class PaymentConfig(Base):
    """支付配置表"""
    __tablename__ = 'ai_write_payment_config'

    config_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='配置ID')
    provider_type = Column(String(20), nullable=False, comment='支付提供商')
    provider_name = Column(String(50), nullable=False, comment='提供商名称')
    config_data = Column(JSON, nullable=False, comment='配置数据')
    supported_channels = Column(JSON, nullable=False, comment='支持的支付渠道')
    is_enabled = Column(CHAR(1), default='1', comment='是否启用')
    is_default = Column(CHAR(1), default='0', comment='是否默认')
    priority = Column(Integer, default=0, comment='优先级')
    fee_rate = Column(DECIMAL(5, 4), default=0.0060, comment='手续费率')
    status = Column(CHAR(1), default='0', comment='状态')
    del_flag = Column(CHAR(1), default='0', comment='删除标志')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), comment='备注')


class PaymentTransaction(Base):
    """支付流水表"""
    __tablename__ = 'ai_write_payment_transaction'

    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='流水ID')
    order_id = Column(BigInteger, nullable=False, comment='订单ID')
    order_no = Column(String(50), nullable=False, comment='订单号')
    provider_type = Column(String(20), nullable=False, comment='支付提供商')
    payment_id = Column(String(100), nullable=False, unique=True, comment='支付ID')
    payment_channel = Column(String(50), nullable=False, comment='支付渠道')
    amount = Column(DECIMAL(10, 2), nullable=False, comment='支付金额')
    fee_amount = Column(DECIMAL(10, 2), default=0.00, comment='手续费')
    status = Column(String(20), default='pending', comment='状态')
    transaction_no = Column(String(100), comment='第三方交易号')
    payment_time = Column(DateTime, comment='支付时间')
    refund_time = Column(DateTime, comment='退款时间')
    del_flag = Column(CHAR(1), default='0', comment='删除标志')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), comment='备注')
