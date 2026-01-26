"""
AI模型配置相关VO模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class AiModelConfigModel(BaseModel):
    """
    AI模型配置信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    config_id: Optional[int] = Field(default=None, description='配置ID')
    model_name: Optional[str] = Field(default=None, description='模型名称')
    model_code: Optional[str] = Field(default=None, description='模型代码')
    model_version: Optional[str] = Field(default=None, description='模型版本')
    api_key: Optional[str] = Field(default=None, description='API密钥')
    api_base_url: Optional[str] = Field(default=None, description='API基础URL')
    api_endpoint: Optional[str] = Field(default=None, description='API端点')
    max_tokens: Optional[int] = Field(default=4096, description='最大token数')
    temperature: Optional[Decimal] = Field(default=Decimal('0.70'), description='温度参数')
    top_p: Optional[Decimal] = Field(default=Decimal('0.90'), description='Top P参数')
    is_enabled: Optional[str] = Field(default='0', description='是否启用（0否 1是）')
    is_default: Optional[str] = Field(default='0', description='是否默认（0否 1是）')
    is_preset: Optional[str] = Field(default='1', description='是否预设（0否 1是）')
    priority: Optional[int] = Field(default=0, description='优先级')
    status: Optional[Literal['0', '1']] = Field(default='0', description='状态（0正常 1停用）')
    del_flag: Optional[str] = Field(default='0', description='删除标志（0存在 2删除）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='model_name', message='模型名称不能为空')
    @Size(field_name='model_name', min_length=0, max_length=100, message='模型名称长度不能超过100个字符')
    def get_model_name(self) -> Union[str, None]:
        return self.model_name

    @NotBlank(field_name='model_code', message='模型代码不能为空')
    @Size(field_name='model_code', min_length=0, max_length=50, message='模型代码长度不能超过50个字符')
    def get_model_code(self) -> Union[str, None]:
        return self.model_code

    @NotBlank(field_name='model_version', message='模型版本不能为空')
    @Size(field_name='model_version', min_length=0, max_length=50, message='模型版本长度不能超过50个字符')
    def get_model_version(self) -> Union[str, None]:
        return self.model_version

    @NotBlank(field_name='api_base_url', message='API基础URL不能为空')
    @Size(field_name='api_base_url', min_length=0, max_length=200, message='API基础URL长度不能超过200个字符')
    def get_api_base_url(self) -> Union[str, None]:
        return self.api_base_url

    def validate_fields(self) -> None:
        self.get_model_name()
        self.get_model_code()
        self.get_model_version()
        self.get_api_base_url()


class AiModelConfigQueryModel(BaseModel):
    """
    AI模型配置查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    model_name: Optional[str] = Field(default=None, description='模型名称')
    model_code: Optional[str] = Field(default=None, description='模型代码')
    is_enabled: Optional[str] = Field(default=None, description='是否启用')
    is_default: Optional[str] = Field(default=None, description='是否默认')
    status: Optional[str] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AiModelConfigPageQueryModel(AiModelConfigQueryModel):
    """
    AI模型配置分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class AiModelTestRequestModel(BaseModel):
    """
    AI模型测试请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    config_id: int = Field(description='配置ID')
    test_prompt: Optional[str] = Field(default='你好', description='测试提示词')


class AiModelTestResponseModel(BaseModel):
    """
    AI模型测试响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    success: bool = Field(description='是否成功')
    response_text: Optional[str] = Field(default=None, description='响应文本')
    response_time: Optional[float] = Field(default=None, description='响应时间（秒）')
    error_message: Optional[str] = Field(default=None, description='错误信息')
