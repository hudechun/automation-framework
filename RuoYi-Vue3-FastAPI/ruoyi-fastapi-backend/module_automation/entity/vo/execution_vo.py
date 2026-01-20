from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ExecutionRecordModel(BaseModel):
    """
    执行记录模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, description='执行记录ID')
    task_id: Optional[int] = Field(default=None, description='任务ID')
    task_name: Optional[str] = Field(default=None, description='任务名称')
    status: Optional[str] = Field(default=None, description='执行状态')
    start_time: Optional[Union[datetime, str]] = Field(default=None, description='开始时间')
    end_time: Optional[Union[datetime, str]] = Field(default=None, description='结束时间')
    duration: Optional[int] = Field(default=None, description='执行时长(秒)')
    logs: Optional[str] = Field(default=None, description='执行日志')
    error_message: Optional[str] = Field(default=None, description='错误信息')
    result: Optional[dict] = Field(default=None, description='执行结果')
    created_at: Optional[Union[datetime, str]] = Field(default=None, description='创建时间')


class ExecutionRecordPageQueryModel(BaseModel):
    """
    执行记录分页查询模型
    """

    task_id: Optional[int] = Field(default=None, description='任务ID')
    status: Optional[str] = Field(default=None, description='执行状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间-起始')
    end_time: Optional[str] = Field(default=None, description='开始时间-结束')
    page_num: int = Field(default=1, alias='pageNum', description='当前页码')
    page_size: int = Field(default=10, alias='pageSize', description='每页记录数')


class DeleteExecutionRecordModel(BaseModel):
    """
    删除执行记录模型
    """

    execution_ids: str = Field(alias='executionIds', description='需要删除的执行记录ID')
