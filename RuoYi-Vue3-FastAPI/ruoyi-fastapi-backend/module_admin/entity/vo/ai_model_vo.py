"""
系统AI模型配置VO
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AiModelConfigModel(BaseModel):
    """AI模型配置模型"""

    model_config = ConfigDict(from_attributes=True)

    config_id: Optional[int] = Field(default=None, description='配置ID')
    model_name: str = Field(description='模型名称')
    model_code: str = Field(description='模型代码')
    model_type: str = Field(default='language', description='模型类型（language/vision）')
    provider: str = Field(description='提供商（openai/anthropic/qwen等）')
    
    api_key: Optional[str] = Field(default=None, description='API密钥')
    api_base_url: Optional[str] = Field(default=None, description='API基础URL')
    api_endpoint: Optional[str] = Field(default=None, description='API端点')
    model_version: Optional[str] = Field(default=None, description='模型版本')
    
    params: Optional[dict[str, Any]] = Field(default=None, description='模型参数（JSON）')
    capabilities: Optional[dict[str, Any]] = Field(default=None, description='模型能力（JSON）')
    
    priority: Optional[int] = Field(default=0, description='优先级')
    is_enabled: Optional[str] = Field(default='0', description='是否启用（0否 1是）')
    is_default: Optional[str] = Field(default='0', description='是否默认（0否 1是）')
    is_preset: Optional[str] = Field(default='0', description='是否预设（0否 1是）')
    
    status: Optional[str] = Field(default='0', description='状态（0正常 1停用）')
    del_flag: Optional[str] = Field(default='0', description='删除标志（0存在 2删除）')
    create_by: Optional[str] = Field(default='', description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default='', description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AiModelConfigPageQueryModel(BaseModel):
    """AI模型配置分页查询模型"""

    model_config = ConfigDict(from_attributes=True)

    model_name: Optional[str] = Field(default=None, description='模型名称')
    model_type: Optional[str] = Field(default=None, description='模型类型')
    provider: Optional[str] = Field(default=None, description='提供商')
    is_enabled: Optional[str] = Field(default=None, description='是否启用')
    status: Optional[str] = Field(default=None, description='状态')
    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')


class AiModelTestResponseModel(BaseModel):
    """AI模型测试响应模型"""

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel)

    success: bool = Field(default=False, description='是否成功')
    response_text: Optional[str] = Field(default=None, description='响应文本')
    error_message: Optional[str] = Field(default=None, description='错误信息')
    response_time: float = Field(default=0.0, description='响应时间（秒）')


class PresetModelModel(BaseModel):
    """预设模型模型（用于下拉选择）"""

    model_config = ConfigDict(from_attributes=True)

    model_code: str = Field(description='模型代码')
    model_name: str = Field(description='模型名称')
    model_type: str = Field(description='模型类型')
    provider: str = Field(description='提供商')
    api_endpoint: Optional[str] = Field(default=None, description='API端点')
    model_version: Optional[str] = Field(default=None, description='模型版本')
    params: Optional[dict[str, Any]] = Field(default=None, description='模型参数')
    capabilities: Optional[dict[str, Any]] = Field(default=None, description='模型能力')
    remark: Optional[str] = Field(default=None, description='备注')
