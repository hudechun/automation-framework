"""
大纲提示词模板 VO 模型
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class OutlinePromptTemplateModel(BaseModel):
    """大纲提示词模板信息模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    prompt_template_id: Optional[int] = Field(default=None, description='主键ID')
    format_template_id: Optional[int] = Field(default=None, description='关联格式模板ID')
    format_template_name: Optional[str] = Field(default=None, description='关联格式模板名称（联表带出）')
    name: Optional[str] = Field(default=None, description='模板名称')
    template_content: Optional[str] = Field(default=None, description='提示词全文')
    remark: Optional[str] = Field(default=None, description='备注（说明变量）')
    is_default: Optional[Literal['0', '1']] = Field(default='0', description='是否默认')
    sort_order: Optional[int] = Field(default=0, description='排序')
    status: Optional[Literal['0', '1']] = Field(default='0', description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')


class OutlinePromptTemplatePageQueryModel(BaseModel):
    """大纲提示词模板分页查询模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_num: int = Field(1, description='页码', ge=1)
    page_size: int = Field(10, description='每页数量', ge=1, le=100)
    name: Optional[str] = Field(None, description='模板名称（模糊）')
    format_template_id: Optional[int] = Field(None, description='关联格式模板ID')
    status: Optional[str] = Field(None, description='状态')


class OutlinePromptTemplateAddModel(BaseModel):
    """新增大纲提示词模板模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    format_template_id: Optional[int] = Field(None, description='关联格式模板ID')
    name: str = Field(..., description='模板名称', max_length=100)
    template_content: str = Field(..., description='提示词全文')
    remark: Optional[str] = Field(None, description='备注', max_length=500)
    is_default: Optional[Literal['0', '1']] = Field('0', description='是否默认')
    sort_order: Optional[int] = Field(0, description='排序')
    status: Optional[Literal['0', '1']] = Field('0', description='状态')


class OutlinePromptTemplateUpdateModel(BaseModel):
    """更新大纲提示词模板模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    prompt_template_id: int = Field(..., description='主键ID')
    format_template_id: Optional[int] = Field(None, description='关联格式模板ID')
    name: Optional[str] = Field(None, description='模板名称', max_length=100)
    template_content: Optional[str] = Field(None, description='提示词全文')
    remark: Optional[str] = Field(None, description='备注', max_length=500)
    is_default: Optional[Literal['0', '1']] = Field(None, description='是否默认')
    sort_order: Optional[int] = Field(None, description='排序')
    status: Optional[Literal['0', '1']] = Field(None, description='状态')
