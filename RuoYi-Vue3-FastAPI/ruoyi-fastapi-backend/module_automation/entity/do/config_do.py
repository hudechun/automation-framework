from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String

from config.database import Base


class ModelConfigDO(Base):
    """
    模型配置数据对象
    """

    __tablename__ = 'model_configs'
    __table_args__ = {'comment': '模型配置表'}

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='配置ID')
    name = Column(String(255), unique=True, nullable=False, comment='配置名称')
    provider = Column(String(50), nullable=False, comment='提供商')
    model = Column(String(100), nullable=False, comment='模型名称')
    api_key = Column(String(255), nullable=True, comment='API密钥')
    params = Column(JSON, nullable=True, comment='模型参数')
    enabled = Column(Boolean, nullable=False, server_default='1', comment='是否启用')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
