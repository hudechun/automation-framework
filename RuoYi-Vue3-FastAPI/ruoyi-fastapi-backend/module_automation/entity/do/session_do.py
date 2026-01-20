from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from config.database import Base


class AutomationSession(Base):
    """
    自动化会话表
    """

    __tablename__ = 'sessions'
    __table_args__ = {'comment': '自动化会话表'}

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='会话ID')
    session_id = Column(String(255), nullable=False, unique=True, comment='会话标识')
    state = Column(String(50), nullable=False, server_default='created', comment='会话状态')
    driver_type = Column(String(50), nullable=False, comment='驱动类型')
    session_metadata = Column(JSON, nullable=True, comment='元数据')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
