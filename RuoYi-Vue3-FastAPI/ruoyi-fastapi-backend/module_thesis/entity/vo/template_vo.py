"""
格式模板管理相关VO模型
"""
from datetime import datetime
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


# ==================== 格式模板相关VO ====================


class FormatTemplateModel(BaseModel):
    """
    格式模板信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    template_id: Optional[int] = Field(default=None, description='模板ID')
    template_name: Optional[str] = Field(default=None, description='模板名称')
    school_name: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    file_path: Optional[str] = Field(default=None, description='模板文件路径')
    file_name: Optional[str] = Field(default=None, description='原始文件名')
    file_size: Optional[int] = Field(default=None, description='文件大小')
    is_official: Optional[Literal['0', '1']] = Field(default=None, description='是否官方模板')
    usage_count: Optional[int] = Field(default=None, description='使用次数')
    status: Optional[Literal['0', '1']] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='template_name', message='模板名称不能为空')
    @Size(field_name='template_name', min_length=0, max_length=100, message='模板名称长度不能超过100个字符')
    def get_template_name(self) -> Union[str, None]:
        return self.template_name

    def validate_fields(self) -> None:
        self.get_template_name()


class TemplateUploadModel(BaseModel):
    """
    模板上传请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_name: str = Field(description='模板名称')
    school_name: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    is_official: str = Field(default='0', description='是否官方模板（0否 1是）')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='template_name', message='模板名称不能为空')
    @Size(field_name='template_name', min_length=1, max_length=100, message='模板名称长度为1-100个字符')
    def get_template_name(self) -> str:
        return self.template_name

    def validate_fields(self) -> None:
        self.get_template_name()


class TemplateUpdateModel(BaseModel):
    """
    更新模板请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_id: int = Field(description='模板ID')
    template_name: Optional[str] = Field(default=None, description='模板名称')
    school_name: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    status: Optional[str] = Field(default=None, description='状态')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='template_id', message='模板ID不能为空')
    def get_template_id(self) -> int:
        return self.template_id

    def validate_fields(self) -> None:
        self.get_template_id()


class TemplateQueryModel(BaseModel):
    """
    模板查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_name: Optional[str] = Field(default=None, description='模板名称')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    is_official: Optional[str] = Field(default=None, description='是否官方模板')
    status: Optional[str] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TemplatePageQueryModel(TemplateQueryModel):
    """
    模板分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTemplateModel(BaseModel):
    """
    删除模板模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_ids: str = Field(description='需要删除的模板ID（逗号分隔）')


# ==================== 模板格式规则相关VO ====================


class TemplateFormatRuleModel(BaseModel):
    """
    模板格式规则信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    rule_id: Optional[int] = Field(default=None, description='规则ID')
    template_id: Optional[int] = Field(default=None, description='模板ID')
    rule_type: Optional[str] = Field(default=None, description='规则类型')
    rule_content: Optional[dict[str, Any]] = Field(default=None, description='规则内容JSON')
    sort_order: Optional[int] = Field(default=None, description='排序')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AddFormatRuleModel(BaseModel):
    """
    添加格式规则请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_id: int = Field(description='模板ID')
    rule_type: str = Field(description='规则类型')
    rule_content: dict[str, Any] = Field(description='规则内容JSON')
    sort_order: Optional[int] = Field(default=0, description='排序')

    @NotBlank(field_name='template_id', message='模板ID不能为空')
    def get_template_id(self) -> int:
        return self.template_id

    @NotBlank(field_name='rule_type', message='规则类型不能为空')
    def get_rule_type(self) -> str:
        return self.rule_type

    @NotBlank(field_name='rule_content', message='规则内容不能为空')
    def get_rule_content(self) -> dict[str, Any]:
        return self.rule_content

    def validate_fields(self) -> None:
        self.get_template_id()
        self.get_rule_type()
        self.get_rule_content()


class UpdateFormatRuleModel(BaseModel):
    """
    更新格式规则请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    rule_id: int = Field(description='规则ID')
    rule_type: Optional[str] = Field(default=None, description='规则类型')
    rule_content: Optional[dict[str, Any]] = Field(default=None, description='规则内容JSON')
    sort_order: Optional[int] = Field(default=None, description='排序')

    @NotBlank(field_name='rule_id', message='规则ID不能为空')
    def get_rule_id(self) -> int:
        return self.rule_id

    def validate_fields(self) -> None:
        self.get_rule_id()


class BatchAddFormatRulesModel(BaseModel):
    """
    批量添加格式规则请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_id: int = Field(description='模板ID')
    rules: list[dict[str, Any]] = Field(description='规则列表')

    @NotBlank(field_name='template_id', message='模板ID不能为空')
    def get_template_id(self) -> int:
        return self.template_id

    @NotBlank(field_name='rules', message='规则列表不能为空')
    def get_rules(self) -> list[dict[str, Any]]:
        return self.rules

    def validate_fields(self) -> None:
        self.get_template_id()
        self.get_rules()


# ==================== 响应VO ====================


class TemplateDetailResponseModel(BaseModel):
    """
    模板详情响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_id: int = Field(description='模板ID')
    template_name: str = Field(description='模板名称')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    file_name: str = Field(description='文件名')
    file_size: int = Field(description='文件大小')
    is_official: str = Field(description='是否官方模板')
    usage_count: int = Field(description='使用次数')
    status: str = Field(description='状态')
    format_rules: Optional[list[dict[str, Any]]] = Field(default=None, description='格式规则列表')
    create_time: datetime = Field(description='创建时间')


class TemplateListItemModel(BaseModel):
    """
    模板列表项响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_id: int = Field(description='模板ID')
    template_name: str = Field(description='模板名称')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    is_official: str = Field(description='是否官方模板')
    usage_count: int = Field(description='使用次数')
    status: str = Field(description='状态')
    create_time: datetime = Field(description='创建时间')


class PopularTemplateModel(BaseModel):
    """
    热门模板响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    template_id: int = Field(description='模板ID')
    template_name: str = Field(description='模板名称')
    school: Optional[str] = Field(default=None, description='学校名称')
    usage_count: int = Field(description='使用次数')
