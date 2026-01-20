from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from config.database import Base


class ExecutionRecordDO(Base):
    """
    执行记录数据对象
    """

    __tablename__ = 'execution_records'
    __table_args__ = {'comment': '执行记录表'}

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='执行记录ID')
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, comment='任务ID')
    status = Column(String(50), nullable=False, comment='执行状态')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=True, comment='结束时间')
    duration = Column(Integer, nullable=True, comment='执行时长(秒)')
    logs = Column(Text, nullable=True, comment='执行日志')
    error_message = Column(Text, nullable=True, comment='错误信息')
    result = Column(JSON, nullable=True, comment='执行结果')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
