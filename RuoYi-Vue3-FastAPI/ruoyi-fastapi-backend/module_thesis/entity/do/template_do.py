"""
格式模板相关实体类
"""
from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, JSON

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AiWriteFormatTemplate(Base):
    """
    格式模板表
    """

    __tablename__ = 'ai_write_format_template'
    __table_args__ = {'comment': '格式模板表'}

    template_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='模板ID')
    template_name = Column(String(100), nullable=False, comment='模板名称')
    school_name = Column(String(100), nullable=False, comment='学校名称')
    major = Column(String(100), nullable=True, server_default="''", comment='专业')
    degree_level = Column(String(20), nullable=False, comment='学位级别（本科/硕士/博士）')
    
    file_path = Column(String(500), nullable=False, comment='模板文件路径')
    file_name = Column(String(200), nullable=False, comment='原始文件名')
    file_size = Column(BigInteger, nullable=True, server_default='0', comment='文件大小（字节）')
    
    format_data = Column(
        JSON,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='格式数据（JSON格式，解析后的格式规则）',
    )
    
    is_official = Column(CHAR(1), nullable=True, server_default='0', comment='是否官方模板（0否 1是）')
    usage_count = Column(Integer, nullable=True, server_default='0', comment='使用次数')
    
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


class AiWriteTemplateFormatRule(Base):
    """
    模板格式规则表
    """

    __tablename__ = 'ai_write_template_format_rule'
    __table_args__ = {'comment': '模板格式规则表'}

    rule_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='规则ID')
    template_id = Column(BigInteger, nullable=False, comment='模板ID')
    
    rule_type = Column(String(50), nullable=False, comment='规则类型（page_margin/font/line_spacing/numbering）')
    rule_name = Column(String(100), nullable=False, comment='规则名称')
    rule_value = Column(JSON, nullable=False, comment='规则值（JSON格式）')
    
    sort_order = Column(Integer, nullable=True, server_default='0', comment='显示顺序')
    
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
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


class UniversalInstructionSystem(Base):
    """
    通用格式指令系统表
    """

    __tablename__ = 'universal_instruction_system'
    __table_args__ = {'comment': '通用格式指令系统表'}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='ID')
    version = Column(String(50), nullable=False, comment='版本号')
    description = Column(String(500), nullable=True, comment='描述')
    instruction_data = Column(
        JSON,
        nullable=False,
        comment='指令数据（JSON格式，完整指令系统）',
    )
    is_active = Column(CHAR(1), nullable=True, server_default='1', comment='是否激活（0否 1是）')
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
