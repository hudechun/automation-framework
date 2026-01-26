"""
订单和支付相关实体类
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, Numeric, String, Text

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AiWriteOrder(Base):
    """
    订单表
    """

    __tablename__ = 'ai_write_order'
    __table_args__ = {'comment': '订单表'}

    order_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='订单ID')
    order_no = Column(String(64), nullable=False, unique=True, comment='订单号')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    order_type = Column(String(20), nullable=False, server_default='package', comment='订单类型（package-套餐, service-服务）')
    item_id = Column(BigInteger, nullable=False, server_default='0', comment='商品ID（套餐ID或服务ID）')
    package_id = Column(BigInteger, nullable=True, comment='套餐ID（兼容字段）')
    
    amount = Column(Numeric(10, 2), nullable=False, comment='订单金额')
    
    payment_method = Column(String(20), nullable=False, comment='支付方式（wechat/alipay）')
    payment_time = Column(
        DateTime,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='支付时间',
    )
    transaction_id = Column(String(64), nullable=True, server_default="''", comment='第三方交易号')
    
    status = Column(String(20), nullable=False, comment='订单状态（pending/paid/refunded/cancelled）')
    
    expired_at = Column(DateTime, nullable=False, comment='订单过期时间')
    
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class AiWriteFeatureService(Base):
    """
    功能服务表
    """

    __tablename__ = 'ai_write_feature_service'
    __table_args__ = {'comment': '功能服务表'}

    service_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='服务ID')
    service_name = Column(String(50), nullable=False, comment='服务名称')
    service_type = Column(String(30), nullable=False, comment='服务类型（de_ai/polish/aigc_detection/plagiarism_check/manual_review）')
    
    price = Column(Numeric(10, 2), nullable=False, comment='服务价格')
    billing_unit = Column(String(20), nullable=False, comment='计费单位（per_word/per_thousand_words/per_paper）')
    
    service_desc = Column(
        Text,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='服务描述',
    )
    
    sort_order = Column(Integer, nullable=True, server_default='0', comment='显示顺序')
    
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
    del_flag = Column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class AiWriteExportRecord(Base):
    """
    导出记录表
    """

    __tablename__ = 'ai_write_export_record'
    __table_args__ = {'comment': '导出记录表'}

    record_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='记录ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    thesis_id = Column(BigInteger, nullable=False, comment='论文ID')
    
    file_name = Column(String(200), nullable=False, comment='文件名')
    file_path = Column(String(500), nullable=False, comment='文件路径')
    file_size = Column(BigInteger, nullable=False, comment='文件大小（字节）')
    
    del_flag = Column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )
