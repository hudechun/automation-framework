"""
大纲提示词模板相关实体类
"""
from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, Text

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AiWriteOutlinePromptTemplate(Base):
    """
    大纲提示词模板表
    """

    __tablename__ = 'ai_write_outline_prompt_template'
    __table_args__ = {'comment': '大纲提示词模板表'}

    prompt_template_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    format_template_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='关联格式模板ID（NULL表示全局默认）',
    )
    name = Column(String(100), nullable=True, server_default="''", comment='模板名称')
    template_content = Column(Text, nullable=True, comment='提示词全文')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注（说明变量）',
    )
    is_default = Column(CHAR(1), nullable=True, server_default='0', comment='同一format_template_id下是否默认（0否 1是）')
    sort_order = Column(Integer, nullable=True, server_default='0', comment='排序')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
    del_flag = Column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
