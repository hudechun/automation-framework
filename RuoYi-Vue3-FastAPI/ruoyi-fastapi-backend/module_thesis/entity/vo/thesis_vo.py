"""
论文管理相关VO模型
"""
from datetime import datetime
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


# ==================== 论文相关VO ====================


class ThesisModel(BaseModel):
    """
    论文信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    title: Optional[str] = Field(default=None, description='论文标题')
    subject: Optional[str] = Field(default=None, description='论文主题')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    template_id: Optional[int] = Field(default=None, description='格式模板ID')
    status: Optional[Literal['draft', 'generating', 'completed', 'exported', 'formatted']] = Field(
        default=None, description='论文状态'
    )
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """去除状态值的首尾空格"""
        if isinstance(v, str):
            v = v.strip()
        return v
    
    word_count: Optional[int] = Field(default=None, description='字数统计')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='title', message='论文标题不能为空')
    @Size(field_name='title', min_length=0, max_length=200, message='论文标题长度不能超过200个字符')
    def get_title(self) -> Union[str, None]:
        return self.title

    @NotBlank(field_name='subject', message='论文主题不能为空')
    def get_subject(self) -> Union[str, None]:
        return self.subject

    def validate_fields(self) -> None:
        self.get_title()
        self.get_subject()


class ThesisCreateModel(BaseModel):
    """
    创建论文请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    title: str = Field(description='论文标题')
    subject: str = Field(description='论文主题')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    template_id: Optional[int] = Field(default=None, description='格式模板ID')
    chapter_word_count_requirement: Optional[str] = Field(default=None, description='每章节字数要求（格式：最小值-最大值，如：2000-3000）')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='title', message='论文标题不能为空')
    @Size(field_name='title', min_length=1, max_length=200, message='论文标题长度为1-200个字符')
    def get_title(self) -> str:
        return self.title

    @NotBlank(field_name='subject', message='论文主题不能为空')
    @Size(field_name='subject', min_length=1, max_length=500, message='论文主题长度为1-500个字符')
    def get_subject(self) -> str:
        return self.subject

    def validate_fields(self) -> None:
        self.get_title()
        self.get_subject()


class ThesisUpdateModel(BaseModel):
    """
    更新论文请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_id: int = Field(description='论文ID')
    title: Optional[str] = Field(default=None, description='论文标题')
    subject: Optional[str] = Field(default=None, description='论文主题')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    template_id: Optional[int] = Field(default=None, description='格式模板ID')
    status: Optional[str] = Field(default=None, description='论文状态')
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """去除状态值的首尾空格"""
        if isinstance(v, str):
            v = v.strip()
        return v
    
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='thesis_id', message='论文ID不能为空')
    def get_thesis_id(self) -> int:
        return self.thesis_id

    def validate_fields(self) -> None:
        self.get_thesis_id()


class ThesisQueryModel(BaseModel):
    """
    论文查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: Optional[int] = Field(default=None, description='用户ID')
    title: Optional[str] = Field(default=None, description='论文标题')
    status: Optional[str] = Field(default=None, description='论文状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class ThesisPageQueryModel(ThesisQueryModel):
    """
    论文分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteThesisModel(BaseModel):
    """
    删除论文模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_ids: str = Field(description='需要删除的论文ID（逗号分隔）')


# ==================== 论文大纲相关VO ====================


class ThesisOutlineModel(BaseModel):
    """
    论文大纲信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    outline_id: Optional[int] = Field(default=None, description='大纲ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    outline_structure: Optional[dict[str, Any]] = Field(default=None, alias='outline_data', description='大纲结构JSON')
    outline_data: Optional[dict[str, Any]] = Field(default=None, description='大纲数据（数据库字段）')
    version: Optional[int] = Field(default=None, description='版本号')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
    
    def model_post_init(self, __context):
        """后处理：确保outline_structure和outline_data同步"""
        if self.outline_data and not self.outline_structure:
            self.outline_structure = self.outline_data
        elif self.outline_structure and not self.outline_data:
            self.outline_data = self.outline_structure


class GenerateOutlineModel(BaseModel):
    """
    生成大纲请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_id: int = Field(description='论文ID')
    requirements: Optional[str] = Field(default=None, description='特殊要求')

    @NotBlank(field_name='thesis_id', message='论文ID不能为空')
    def get_thesis_id(self) -> int:
        return self.thesis_id

    def validate_fields(self) -> None:
        self.get_thesis_id()


class UpdateOutlineModel(BaseModel):
    """
    更新大纲请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    outline_id: int = Field(description='大纲ID')
    outline_structure: dict[str, Any] = Field(description='大纲结构JSON')

    @NotBlank(field_name='outline_id', message='大纲ID不能为空')
    def get_outline_id(self) -> int:
        return self.outline_id

    @NotBlank(field_name='outline_structure', message='大纲结构不能为空')
    def get_outline_structure(self) -> dict[str, Any]:
        return self.outline_structure

    def validate_fields(self) -> None:
        self.get_outline_id()
        self.get_outline_structure()


# ==================== 论文章节相关VO ====================


class ThesisChapterModel(BaseModel):
    """
    论文章节信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    chapter_id: Optional[int] = Field(default=None, description='章节ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    chapter_number: Optional[str] = Field(default=None, description='章节号')
    chapter_title: Optional[str] = Field(default=None, description='章节标题')
    content: Optional[str] = Field(default=None, description='章节内容')
    word_count: Optional[int] = Field(default=None, description='字数')
    sort_order: Optional[int] = Field(default=None, description='排序')
    status: Optional[Literal['pending', 'generating', 'completed']] = Field(default=None, description='章节状态')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class GenerateChapterModel(BaseModel):
    """
    生成章节内容请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    chapter_id: int = Field(description='章节ID')
    requirements: Optional[str] = Field(default=None, description='特殊要求')

    @NotBlank(field_name='chapter_id', message='章节ID不能为空')
    def get_chapter_id(self) -> int:
        return self.chapter_id

    def validate_fields(self) -> None:
        self.get_chapter_id()


class UpdateChapterModel(BaseModel):
    """
    更新章节请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    chapter_id: int = Field(description='章节ID')
    chapter_title: Optional[str] = Field(default=None, description='章节标题')
    content: Optional[str] = Field(default=None, description='章节内容')
    sort_order: Optional[int] = Field(default=None, description='排序')

    @NotBlank(field_name='chapter_id', message='章节ID不能为空')
    def get_chapter_id(self) -> int:
        return self.chapter_id

    def validate_fields(self) -> None:
        self.get_chapter_id()


# ==================== 论文版本相关VO ====================


class ThesisVersionModel(BaseModel):
    """
    论文版本信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    version_id: Optional[int] = Field(default=None, description='版本ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    version_number: Optional[int] = Field(default=None, description='版本号')
    content_snapshot: Optional[str] = Field(default=None, description='内容快照')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class CreateVersionModel(BaseModel):
    """
    创建版本请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_id: int = Field(description='论文ID')
    remark: Optional[str] = Field(default=None, description='版本说明')

    @NotBlank(field_name='thesis_id', message='论文ID不能为空')
    def get_thesis_id(self) -> int:
        return self.thesis_id

    def validate_fields(self) -> None:
        self.get_thesis_id()


class RestoreVersionModel(BaseModel):
    """
    恢复版本请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    version_id: int = Field(description='版本ID')

    @NotBlank(field_name='version_id', message='版本ID不能为空')
    def get_version_id(self) -> int:
        return self.version_id

    def validate_fields(self) -> None:
        self.get_version_id()


# ==================== 响应VO ====================


class ThesisDetailResponseModel(BaseModel):
    """
    论文详情响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_id: int = Field(description='论文ID')
    title: str = Field(description='论文标题')
    subject: str = Field(description='论文主题')
    school: Optional[str] = Field(default=None, description='学校名称')
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')
    status: str = Field(description='论文状态')
    word_count: int = Field(description='字数统计')
    outline: Optional[dict[str, Any]] = Field(default=None, description='大纲结构')
    chapters: Optional[list[dict[str, Any]]] = Field(default=None, description='章节列表')
    create_time: datetime = Field(description='创建时间')
    update_time: datetime = Field(description='更新时间')


class ThesisListItemModel(BaseModel):
    """
    论文列表项响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_id: int = Field(description='论文ID')
    title: str = Field(description='论文标题')
    status: str = Field(description='论文状态')
    word_count: int = Field(description='字数统计')
    create_time: datetime = Field(description='创建时间')
    update_time: datetime = Field(description='更新时间')
