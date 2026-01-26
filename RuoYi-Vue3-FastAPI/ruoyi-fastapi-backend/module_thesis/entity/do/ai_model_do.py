"""
AI模型配置数据库实体
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CHAR, DateTime, Integer, String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AiWriteAiModelConfig(Base):
    """
    AI模型配置表
    """

    __tablename__ = 'ai_write_ai_model_config'
    __table_args__ = {'comment': 'AI模型配置表'}

    config_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='配置ID'
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='模型名称')
    model_code: Mapped[str] = mapped_column(String(50), nullable=False, comment='模型代码')
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, comment='模型版本')

    api_key: Mapped[str] = mapped_column(String(500), nullable=True, server_default="''", comment='API密钥')
    api_base_url: Mapped[str] = mapped_column(String(200), nullable=True, server_default="''", comment='API基础URL')
    api_endpoint: Mapped[str] = mapped_column(String(200), nullable=True, server_default="''", comment='API端点')

    max_tokens: Mapped[int] = mapped_column(Integer, nullable=True, server_default='4096', comment='最大token数')
    temperature: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 2), nullable=True, server_default='0.70', comment='温度参数'
    )
    top_p: Mapped[Decimal] = mapped_column(DECIMAL(3, 2), nullable=True, server_default='0.90', comment='Top P参数')

    is_enabled: Mapped[str] = mapped_column(CHAR(1), nullable=True, server_default='0', comment='是否启用（0否 1是）')
    is_default: Mapped[str] = mapped_column(CHAR(1), nullable=True, server_default='0', comment='是否默认（0否 1是）')
    is_preset: Mapped[str] = mapped_column(CHAR(1), nullable=True, server_default='1', comment='是否预设（0否 1是）')

    priority: Mapped[int] = mapped_column(Integer, nullable=True, server_default='0', comment='优先级')

    status: Mapped[str] = mapped_column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
    del_flag: Mapped[str] = mapped_column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0存在 2删除）')
    create_by: Mapped[str] = mapped_column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by: Mapped[str] = mapped_column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间'
    )
    remark: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, True),
        comment='备注',
    )
