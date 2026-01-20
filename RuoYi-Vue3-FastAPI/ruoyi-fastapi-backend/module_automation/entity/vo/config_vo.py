from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ModelConfigModel(BaseModel):
    """
    模型配置模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, description='配置ID')
    name: Optional[str] = Field(default=None, description='配置名称')
    provider: Optional[str] = Field(default=None, description='提供商')
    model: Optional[str] = Field(default=None, description='模型名称')
    api_key: Optional[str] = Field(default=None, description='API密钥')
    params: Optional[dict] = Field(default=None, description='模型参数')
    enabled: Optional[bool] = Field(default=True, description='是否启用')
    created_at: Optional[Union[datetime, str]] = Field(default=None, description='创建时间')
    updated_at: Optional[Union[datetime, str]] = Field(default=None, description='更新时间')


class ModelConfigPageQueryModel(BaseModel):
    """
    模型配置分页查询模型
    """

    name: Optional[str] = Field(default=None, description='配置名称')
    provider: Optional[str] = Field(default=None, description='提供商')
    enabled: Optional[bool] = Field(default=None, description='是否启用')
    page_num: int = Field(default=1, alias='pageNum', description='当前页码')
    page_size: int = Field(default=10, alias='pageSize', description='每页记录数')


class DeleteModelConfigModel(BaseModel):
    """
    删除模型配置模型
    """

    config_ids: str = Field(alias='configIds', description='需要删除的配置ID')
