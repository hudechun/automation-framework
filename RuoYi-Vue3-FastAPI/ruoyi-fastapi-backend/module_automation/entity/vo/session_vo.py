from datetime import datetime
from typing import Any, Dict, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SessionModel(BaseModel):
    """
    自动化会话表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='会话ID')
    session_id: Optional[str] = Field(default=None, description='会话标识')
    state: Optional[Literal['created', 'running', 'paused', 'completed', 'failed']] = Field(
        default='created', description='会话状态'
    )
    driver_type: Optional[str] = Field(default=None, description='驱动类型')
    session_metadata: Optional[Union[Dict[str, Any], str]] = Field(default=None, description='元数据', alias='metadata')
    created_at: Optional[datetime] = Field(default=None, description='创建时间')
    updated_at: Optional[datetime] = Field(default=None, description='更新时间')


class SessionQueryModel(SessionModel):
    """
    自动化会话不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class SessionPageQueryModel(SessionQueryModel):
    """
    自动化会话分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteSessionModel(BaseModel):
    """
    删除自动化会话模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    session_ids: str = Field(description='需要删除的会话ID')
