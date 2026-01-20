"""
SQLAlchemy 数据模型 - 统一使用 SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    JSON, Float, ForeignKey, Index
)
from sqlalchemy.orm import relationship

# 导入 RuoYi 的 Base 类（统一使用）
import sys
import os

# 添加 RuoYi 后端路径
ruoyi_backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend')
)
if ruoyi_backend_path not in sys.path:
    sys.path.insert(0, ruoyi_backend_path)

try:
    from config.database import Base
except ImportError:
    # 如果无法导入，创建一个临时的 Base（用于独立运行）
    from sqlalchemy.ext.asyncio import AsyncAttrs
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(AsyncAttrs, DeclarativeBase):
        pass


class Task(Base):
    """任务模型"""
    
    __tablename__ = 'tasks'
    __table_args__ = (
        Index('idx_name', 'name'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
        {'comment': '自动化任务表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='任务ID')
    name = Column(String(255), nullable=False, index=True, comment='任务名称')
    description = Column(Text, nullable=True, comment='任务描述')
    task_type = Column(String(50), nullable=False, comment='任务类型：browser, desktop, hybrid')
    actions = Column(JSON, nullable=False, comment='操作列表')
    config = Column(JSON, nullable=True, comment='任务配置')
    status = Column(String(50), nullable=False, server_default='pending', comment='任务状态：pending, running, completed, failed')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    schedules = relationship("Schedule", back_populates="task", cascade="all, delete-orphan")
    executions = relationship("ExecutionRecord", back_populates="task", cascade="all, delete-orphan")


class Schedule(Base):
    """调度模型"""
    
    __tablename__ = 'schedules'
    __table_args__ = (
        Index('idx_enabled', 'enabled'),
        Index('idx_next_run_time', 'next_run_time'),
        {'comment': '任务调度表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='调度ID')
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, comment='任务ID')
    schedule_type = Column(String(50), nullable=False, comment='调度类型：once, interval, cron')
    schedule_config = Column(JSON, nullable=False, comment='调度配置')
    enabled = Column(Boolean, nullable=False, server_default='1', comment='是否启用')
    next_run_time = Column(DateTime, nullable=True, comment='下次运行时间')
    last_run_time = Column(DateTime, nullable=True, comment='上次运行时间')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    task = relationship("Task", back_populates="schedules")


class ExecutionRecord(Base):
    """执行记录模型"""
    
    __tablename__ = 'execution_records'
    __table_args__ = (
        Index('idx_task_id', 'task_id'),
        Index('idx_status', 'status'),
        Index('idx_start_time', 'start_time'),
        {'comment': '执行记录表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='记录ID')
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, comment='任务ID')
    status = Column(String(50), nullable=False, comment='执行状态：running, completed, failed')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=True, comment='结束时间')
    duration = Column(Integer, nullable=True, comment='执行时长（秒）')
    logs = Column(Text, nullable=True, comment='执行日志')
    screenshots = Column(JSON, nullable=True, comment='截图路径列表')
    error_message = Column(Text, nullable=True, comment='错误信息')
    error_stack = Column(Text, nullable=True, comment='错误堆栈')
    result = Column(JSON, nullable=True, comment='执行结果')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    
    # 关系
    task = relationship("Task", back_populates="executions")


class Session(Base):
    """会话模型"""
    
    __tablename__ = 'sessions'
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_state', 'state'),
        {'comment': '会话表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='会话ID')
    session_id = Column(String(255), nullable=False, unique=True, index=True, comment='会话标识')
    state = Column(String(50), nullable=False, server_default='created', comment='会话状态：created, running, paused, stopped, failed')
    driver_type = Column(String(50), nullable=False, comment='驱动类型：browser, desktop')
    metadata = Column(JSON, nullable=True, comment='会话元数据')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    checkpoints = relationship("SessionCheckpoint", back_populates="session", cascade="all, delete-orphan")


class SessionCheckpoint(Base):
    """会话检查点模型"""
    
    __tablename__ = 'session_checkpoints'
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_created_at', 'created_at'),
        {'comment': '会话检查点表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='检查点ID')
    session_id = Column(Integer, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, comment='会话ID')
    checkpoint_name = Column(String(255), nullable=False, comment='检查点名称')
    state_data = Column(JSON, nullable=False, comment='状态数据')
    actions_completed = Column(Integer, nullable=False, server_default='0', comment='已完成的操作数')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    
    # 关系
    session = relationship("Session", back_populates="checkpoints")


class ModelConfig(Base):
    """模型配置"""
    
    __tablename__ = 'model_configs'
    __table_args__ = {'comment': '模型配置表'}
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='配置ID')
    name = Column(String(255), nullable=False, unique=True, index=True, comment='配置名称')
    provider = Column(String(50), nullable=False, comment='提供商：openai, anthropic, ollama, qwen')
    model = Column(String(100), nullable=False, comment='模型名称')
    api_key = Column(String(255), nullable=True, comment='API密钥')
    params = Column(JSON, nullable=True, comment='模型参数')
    enabled = Column(Boolean, nullable=False, server_default='1', comment='是否启用')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    metrics = relationship("ModelMetrics", back_populates="model_config", cascade="all, delete-orphan")


class ModelMetrics(Base):
    """模型性能指标"""
    
    __tablename__ = 'model_metrics'
    __table_args__ = (
        Index('idx_model_config_id', 'model_config_id'),
        Index('idx_created_at', 'created_at'),
        {'comment': '模型性能指标表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='指标ID')
    model_config_id = Column(Integer, ForeignKey('model_configs.id', ondelete='CASCADE'), nullable=False, comment='模型配置ID')
    latency = Column(Float, nullable=False, comment='延迟（秒）')
    cost = Column(Float, nullable=True, comment='成本')
    tokens = Column(Integer, nullable=True, comment='token数')
    success = Column(Boolean, nullable=False, server_default='1', comment='是否成功')
    error_message = Column(Text, nullable=True, comment='错误信息')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    
    # 关系
    model_config = relationship("ModelConfig", back_populates="metrics")


class SystemLog(Base):
    """系统日志"""
    
    __tablename__ = 'system_logs'
    __table_args__ = (
        Index('idx_level', 'level'),
        Index('idx_created_at', 'created_at'),
        {'comment': '系统日志表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='日志ID')
    level = Column(String(20), nullable=False, comment='日志级别：debug, info, warning, error, critical')
    message = Column(Text, nullable=False, comment='日志消息')
    module = Column(String(255), nullable=True, comment='模块名')
    function = Column(String(255), nullable=True, comment='函数名')
    line_number = Column(Integer, nullable=True, comment='行号')
    extra_data = Column(JSON, nullable=True, comment='额外数据')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')


class NotificationConfig(Base):
    """通知配置"""
    
    __tablename__ = 'notification_configs'
    __table_args__ = {'comment': '通知配置表'}
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='配置ID')
    name = Column(String(255), nullable=False, unique=True, comment='配置名称')
    notification_type = Column(String(50), nullable=False, comment='通知类型：email, webhook, slack, dingtalk, wechat_work')
    config = Column(JSON, nullable=False, comment='通知配置')
    enabled = Column(Boolean, nullable=False, server_default='1', comment='是否启用')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class FileStorage(Base):
    """文件存储"""
    
    __tablename__ = 'file_storage'
    __table_args__ = (
        Index('idx_file_type', 'file_type'),
        Index('idx_related', 'related_type', 'related_id'),
        Index('idx_created_at', 'created_at'),
        {'comment': '文件存储表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='文件ID')
    file_name = Column(String(255), nullable=False, comment='文件名')
    file_path = Column(String(512), nullable=False, comment='文件路径')
    file_type = Column(String(50), nullable=False, comment='文件类型：screenshot, log, video, export')
    file_size = Column(Integer, nullable=False, comment='文件大小（字节）')
    mime_type = Column(String(100), nullable=True, comment='MIME类型')
    related_type = Column(String(50), nullable=True, comment='关联类型：task, execution, session')
    related_id = Column(Integer, nullable=True, comment='关联ID')
    metadata = Column(JSON, nullable=True, comment='元数据')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')


class Plugin(Base):
    """插件"""
    
    __tablename__ = 'plugins'
    __table_args__ = {'comment': '插件表'}
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='插件ID')
    name = Column(String(255), nullable=False, unique=True, index=True, comment='插件名称')
    version = Column(String(50), nullable=False, comment='版本号')
    description = Column(Text, nullable=True, comment='描述')
    plugin_type = Column(String(50), nullable=False, comment='插件类型：action, driver, agent, integration')
    manifest = Column(JSON, nullable=False, comment='插件清单')
    config = Column(JSON, nullable=True, comment='插件配置')
    enabled = Column(Boolean, nullable=False, server_default='0', comment='是否启用')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class PerformanceMetrics(Base):
    """性能指标"""
    
    __tablename__ = 'performance_metrics'
    __table_args__ = (
        Index('idx_metric_type', 'metric_type'),
        Index('idx_metric_name', 'metric_name'),
        Index('idx_created_at', 'created_at'),
        {'comment': '性能指标表'}
    )
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='指标ID')
    metric_type = Column(String(50), nullable=False, comment='指标类型：cpu, memory, disk, network, task')
    metric_name = Column(String(100), nullable=False, comment='指标名称')
    value = Column(Float, nullable=False, comment='指标值')
    unit = Column(String(20), nullable=True, comment='单位')
    metadata = Column(JSON, nullable=True, comment='元数据')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
