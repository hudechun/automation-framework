"""
指令系统VO模型
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


class UniversalInstructionSystemModel(BaseModel):
    """通用格式指令系统模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: Optional[int] = Field(None, description='ID')
    version: str = Field(..., description='版本号', max_length=50)
    description: Optional[str] = Field(None, description='描述', max_length=500)
    instruction_data: dict[str, Any] = Field(..., description='指令数据（JSON格式）')
    is_active: Optional[str] = Field('1', description='是否激活（0否 1是）')
    create_by: Optional[str] = Field(None, description='创建者', max_length=64)
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者', max_length=64)
    update_time: Optional[datetime] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注', max_length=500)
    
    @field_validator('is_active')
    @classmethod
    def validate_is_active(cls, v: str) -> str:
        if v not in ['0', '1']:
            raise ValueError('is_active必须是0或1')
        return v


class InstructionSystemPageQueryModel(BaseModel):
    """指令系统分页查询模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_num: int = Field(1, description='页码', ge=1)
    page_size: int = Field(10, description='每页数量', ge=1, le=100)
    version: Optional[str] = Field(None, description='版本号')
    is_active: Optional[str] = Field(None, description='是否激活（0否 1是）')
    description: Optional[str] = Field(None, description='描述（模糊查询）')


class InstructionSystemAddModel(BaseModel):
    """添加指令系统模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    version: str = Field(..., description='版本号', max_length=50)
    description: Optional[str] = Field(None, description='描述', max_length=500)
    instruction_data: dict[str, Any] = Field(..., description='指令数据（JSON格式）')
    is_active: Optional[str] = Field('1', description='是否激活（0否 1是）')
    remark: Optional[str] = Field(None, description='备注', max_length=500)
    
    @field_validator('is_active')
    @classmethod
    def validate_is_active(cls, v: str) -> str:
        if v not in ['0', '1']:
            raise ValueError('is_active必须是0或1')
        return v


class InstructionSystemUpdateModel(BaseModel):
    """更新指令系统模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    version: Optional[str] = Field(None, description='版本号', max_length=50)
    description: Optional[str] = Field(None, description='描述', max_length=500)
    instruction_data: Optional[dict[str, Any]] = Field(None, description='指令数据（JSON格式）')
    is_active: Optional[str] = Field(None, description='是否激活（0否 1是）')
    remark: Optional[str] = Field(None, description='备注', max_length=500)
    update_by: Optional[str] = Field(None, description='更新者', max_length=64)
    update_time: Optional[datetime] = Field(None, description='更新时间')
    
    @field_validator('is_active')
    @classmethod
    def validate_is_active(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ['0', '1']:
            raise ValueError('is_active必须是0或1')
        return v
