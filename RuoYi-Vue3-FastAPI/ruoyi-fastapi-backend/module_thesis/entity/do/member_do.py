"""
会员管理相关实体类
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, Numeric, String, JSON

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AiWriteMemberPackage(Base):
    """
    会员套餐表
    """

    __tablename__ = 'ai_write_member_package'
    __table_args__ = {'comment': '会员套餐表'}

    package_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='套餐ID')
    package_name = Column(String(50), nullable=False, comment='套餐名称')
    package_desc = Column(String(200), nullable=True, server_default="''", comment='套餐描述')
    price = Column(Numeric(10, 2), nullable=False, comment='套餐价格')
    duration_days = Column(Integer, nullable=False, comment='套餐时长（天）')
    
    word_quota = Column(Integer, nullable=False, comment='字数配额（-1表示无限）')
    usage_quota = Column(Integer, nullable=False, comment='使用次数配额（-1表示无限）')
    
    features = Column(JSON, nullable=False, comment='功能权限配置（JSON格式）')
    
    is_recommended = Column(CHAR(1), nullable=True, server_default='0', comment='是否推荐（0否 1是）')
    badge = Column(String(20), nullable=True, server_default="''", comment='徽章文字')
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


class AiWriteUserMembership(Base):
    """
    用户会员表
    """

    __tablename__ = 'ai_write_user_membership'
    __table_args__ = {'comment': '用户会员表'}

    membership_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='会员ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    package_id = Column(BigInteger, nullable=False, comment='套餐ID')
    
    total_word_quota = Column(Integer, nullable=False, comment='总字数配额')
    used_word_quota = Column(Integer, nullable=True, server_default='0', comment='已使用字数')
    
    total_usage_quota = Column(Integer, nullable=False, comment='总使用次数')
    used_usage_quota = Column(Integer, nullable=True, server_default='0', comment='已使用次数')
    
    start_date = Column(DateTime, nullable=False, comment='开始时间')
    end_date = Column(DateTime, nullable=False, comment='结束时间')
    
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用 2过期）')
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


class AiWriteUserFeatureQuota(Base):
    """
    用户功能配额表
    """

    __tablename__ = 'ai_write_user_feature_quota'
    __table_args__ = {'comment': '用户功能配额表'}

    quota_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='配额ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    service_type = Column(String(30), nullable=False, comment='服务类型（de_ai/polish/aigc_detection/plagiarism_check）')
    
    total_quota = Column(Integer, nullable=False, comment='总配额（字数）')
    used_quota = Column(Integer, nullable=True, server_default='0', comment='已使用配额')
    
    start_date = Column(DateTime, nullable=False, comment='开始时间')
    end_date = Column(DateTime, nullable=False, comment='结束时间')
    
    source = Column(String(20), nullable=False, comment='来源（package/purchase）')
    source_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='来源ID（套餐ID或订单ID）',
    )
    
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用 2过期）')
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


class AiWriteQuotaRecord(Base):
    """
    配额使用记录表
    """

    __tablename__ = 'ai_write_quota_record'
    __table_args__ = {'comment': '配额使用记录表'}

    record_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='记录ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    thesis_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='论文ID',
    )
    
    word_count = Column(Integer, nullable=False, comment='字数变动（正数为扣减，负数为退还）')
    usage_count = Column(Integer, nullable=False, comment='次数变动')
    
    operation_type = Column(String(20), nullable=False, comment='操作类型（generate/refund）')
    
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )
