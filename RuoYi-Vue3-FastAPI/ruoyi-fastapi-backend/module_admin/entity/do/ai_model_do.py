"""
系统AI模型配置DO
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class AiModelConfig(Base):
    """系统AI模型配置表"""

    __tablename__ = 'ai_write_ai_model_config'

    config_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment='配置ID')
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='模型名称')
    model_code: Mapped[str] = mapped_column(String(100), nullable=False, comment='模型代码')
    model_type: Mapped[str] = mapped_column(String(20), nullable=False, default='language', comment='模型类型（language/vision）')
    provider: Mapped[str] = mapped_column(String(50), nullable=False, comment='提供商（openai/anthropic/qwen等）')
    
    api_key: Mapped[Optional[str]] = mapped_column(String(500), comment='API密钥')
    api_base_url: Mapped[Optional[str]] = mapped_column(String(200), comment='API基础URL')
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), comment='API端点')
    model_version: Mapped[Optional[str]] = mapped_column(String(50), comment='模型版本')
    
    params: Mapped[Optional[dict]] = mapped_column(JSON, comment='模型参数（JSON）')
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON, comment='模型能力（JSON）')
    
    priority: Mapped[int] = mapped_column(default=0, comment='优先级')
    is_enabled: Mapped[str] = mapped_column(String(1), default='0', comment='是否启用（0否 1是）')
    is_default: Mapped[str] = mapped_column(String(1), default='0', comment='是否默认（0否 1是）')
    is_preset: Mapped[str] = mapped_column(String(1), default='0', comment='是否预设（0否 1是）')
    
    status: Mapped[str] = mapped_column(String(1), default='0', comment='状态（0正常 1停用）')
    del_flag: Mapped[str] = mapped_column(String(1), default='0', comment='删除标志（0存在 2删除）')
    create_by: Mapped[str] = mapped_column(String(64), default='', comment='创建者')
    create_time: Mapped[Optional[datetime]] = mapped_column(comment='创建时间')
    update_by: Mapped[str] = mapped_column(String(64), default='', comment='更新者')
    update_time: Mapped[Optional[datetime]] = mapped_column(comment='更新时间')
    remark: Mapped[Optional[str]] = mapped_column(String(500), comment='备注')
