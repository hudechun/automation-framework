from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from config.database import Base


class AutomationTask(Base):
    """
    自动化任务表
    """

    __tablename__ = 'tasks'
    __table_args__ = {'comment': '自动化任务表'}

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='任务ID')
    name = Column(String(255), nullable=False, comment='任务名称')
    description = Column(Text, nullable=True, comment='任务描述')
    task_type = Column(String(50), nullable=False, comment='任务类型')
    actions = Column(JSON, nullable=False, comment='任务动作')
    config = Column(JSON, nullable=True, comment='任务配置')
    status = Column(String(50), nullable=False, server_default='pending', comment='任务状态')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
