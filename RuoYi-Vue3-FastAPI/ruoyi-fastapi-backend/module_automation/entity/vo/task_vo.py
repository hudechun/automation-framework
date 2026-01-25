from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class TaskModel(BaseModel):
    """
    自动化任务表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='任务ID')
    name: Optional[str] = Field(default=None, description='任务名称')
    description: Optional[str] = Field(default=None, description='任务描述')
    task_type: Optional[str] = Field(default=None, description='任务类型')
    actions: Optional[Union[List[Dict[str, Any]], str]] = Field(default=None, description='任务动作')
    config: Optional[Union[Dict[str, Any], str]] = Field(default=None, description='任务配置')
    status: Optional[Literal['pending', 'running', 'completed', 'failed', 'cancelled']] = Field(
        default='pending', description='任务状态'
    )
    created_at: Optional[datetime] = Field(default=None, description='创建时间')
    updated_at: Optional[datetime] = Field(default=None, description='更新时间')

    @NotBlank(field_name='name', message='任务名称不能为空')
    @Size(field_name='name', min_length=0, max_length=255, message='任务名称长度不能超过255个字符')
    def get_name(self) -> Union[str, None]:
        return self.name

    @NotBlank(field_name='task_type', message='任务类型不能为空')
    @Size(field_name='task_type', min_length=0, max_length=50, message='任务类型长度不能超过50个字符')
    def get_task_type(self) -> Union[str, None]:
        return self.task_type

    def validate_fields(self) -> None:
        self.get_name()
        self.get_task_type()


class TaskQueryModel(TaskModel):
    """
    自动化任务不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TaskPageQueryModel(TaskQueryModel):
    """
    自动化任务分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTaskModel(BaseModel):
    """
    删除自动化任务模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    task_ids: str = Field(description='需要删除的任务ID')


class ExecuteTaskModel(BaseModel):
    """
    执行任务模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    task_id: int = Field(description='任务ID')


class ParseTaskModel(BaseModel):
    """
    解析自然语言任务模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    description: str = Field(description='自然语言任务描述')
