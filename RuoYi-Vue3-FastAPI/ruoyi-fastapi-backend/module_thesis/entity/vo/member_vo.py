"""
会员权益管理相关VO模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


# ==================== 会员套餐相关VO ====================


class MemberPackageModel(BaseModel):
    """
    会员套餐信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    package_id: Optional[int] = Field(default=None, description='套餐ID')
    package_name: Optional[str] = Field(default=None, description='套餐名称')
    package_type: Optional[str] = Field(default=None, description='套餐类型')
    price: Optional[Decimal] = Field(default=None, description='套餐价格')
    original_price: Optional[Decimal] = Field(default=None, description='原价')
    duration_days: Optional[int] = Field(default=None, description='有效期（天）')
    features: Optional[dict[str, Any]] = Field(default=None, description='功能配额JSON')
    description: Optional[str] = Field(default=None, description='套餐描述')
    sort_order: Optional[int] = Field(default=None, description='显示顺序')
    is_recommended: Optional[str] = Field(default=None, description='是否推荐')
    status: Optional[Literal['0', '1']] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='package_name', message='套餐名称不能为空')
    @Size(field_name='package_name', min_length=0, max_length=50, message='套餐名称长度不能超过50个字符')
    def get_package_name(self) -> Union[str, None]:
        return self.package_name

    @NotBlank(field_name='package_type', message='套餐类型不能为空')
    def get_package_type(self) -> Union[str, None]:
        return self.package_type

    @NotBlank(field_name='price', message='套餐价格不能为空')
    def get_price(self) -> Union[Decimal, None]:
        return self.price

    @NotBlank(field_name='duration_days', message='有效期不能为空')
    def get_duration_days(self) -> Union[int, None]:
        return self.duration_days

    def validate_fields(self) -> None:
        self.get_package_name()
        self.get_package_type()
        self.get_price()
        self.get_duration_days()


class MemberPackageQueryModel(BaseModel):
    """
    会员套餐查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    package_name: Optional[str] = Field(default=None, description='套餐名称')
    package_type: Optional[str] = Field(default=None, description='套餐类型')
    status: Optional[str] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class MemberPackagePageQueryModel(MemberPackageQueryModel):
    """
    会员套餐分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


# ==================== 用户会员相关VO ====================


class UserMembershipModel(BaseModel):
    """
    用户会员信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    membership_id: Optional[int] = Field(default=None, description='会员ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    package_id: Optional[int] = Field(default=None, description='套餐ID')
    package_name: Optional[str] = Field(default=None, description='套餐名称')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    status: Optional[Literal['active', 'expired', 'cancelled']] = Field(default=None, description='会员状态')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class UserMembershipQueryModel(BaseModel):
    """
    用户会员查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: Optional[int] = Field(default=None, description='用户ID')
    package_id: Optional[int] = Field(default=None, description='套餐ID')
    status: Optional[str] = Field(default=None, description='会员状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class UserMembershipPageQueryModel(UserMembershipQueryModel):
    """
    用户会员分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


# ==================== 用户功能配额相关VO ====================


class UserFeatureQuotaModel(BaseModel):
    """
    用户功能配额信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    quota_id: Optional[int] = Field(default=None, description='配额ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    feature_type: Optional[str] = Field(default=None, description='功能类型')
    total_quota: Optional[int] = Field(default=None, description='总配额')
    used_quota: Optional[int] = Field(default=None, description='已使用配额')
    remaining_quota: Optional[int] = Field(default=None, description='剩余配额')
    expire_time: Optional[datetime] = Field(default=None, description='过期时间')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class UserFeatureQuotaQueryModel(BaseModel):
    """
    用户功能配额查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: Optional[int] = Field(default=None, description='用户ID')
    feature_type: Optional[str] = Field(default=None, description='功能类型')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class UserFeatureQuotaPageQueryModel(UserFeatureQuotaQueryModel):
    """
    用户功能配额分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeductQuotaModel(BaseModel):
    """
    扣减配额请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: int = Field(description='用户ID')
    feature_type: str = Field(description='功能类型')
    amount: int = Field(description='扣减数量')
    business_id: Optional[int] = Field(default=None, description='业务ID')
    business_type: Optional[str] = Field(default=None, description='业务类型')

    @NotBlank(field_name='user_id', message='用户ID不能为空')
    def get_user_id(self) -> int:
        return self.user_id

    @NotBlank(field_name='feature_type', message='功能类型不能为空')
    def get_feature_type(self) -> str:
        return self.feature_type

    @NotBlank(field_name='amount', message='扣减数量不能为空')
    def get_amount(self) -> int:
        return self.amount

    def validate_fields(self) -> None:
        self.get_user_id()
        self.get_feature_type()
        self.get_amount()


# ==================== 配额使用记录相关VO ====================


class QuotaRecordModel(BaseModel):
    """
    配额使用记录信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    record_id: Optional[int] = Field(default=None, description='记录ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    feature_type: Optional[str] = Field(default=None, description='功能类型')
    amount: Optional[int] = Field(default=None, description='使用数量')
    business_id: Optional[int] = Field(default=None, description='业务ID')
    business_type: Optional[str] = Field(default=None, description='业务类型')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class QuotaRecordQueryModel(BaseModel):
    """
    配额使用记录查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: Optional[int] = Field(default=None, description='用户ID')
    feature_type: Optional[str] = Field(default=None, description='功能类型')
    business_type: Optional[str] = Field(default=None, description='业务类型')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class QuotaRecordPageQueryModel(QuotaRecordQueryModel):
    """
    配额使用记录分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


# ==================== 响应VO ====================


class MemberPackageResponseModel(BaseModel):
    """
    会员套餐响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    package_id: int = Field(description='套餐ID')
    package_name: str = Field(description='套餐名称')
    package_type: str = Field(description='套餐类型')
    price: Decimal = Field(description='套餐价格')
    original_price: Optional[Decimal] = Field(default=None, description='原价')
    duration_days: int = Field(description='有效期（天）')
    features: dict[str, Any] = Field(description='功能配额')
    description: Optional[str] = Field(default=None, description='套餐描述')
    is_recommended: str = Field(description='是否推荐')
    status: str = Field(description='状态')


class UserQuotaInfoModel(BaseModel):
    """
    用户配额信息响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: int = Field(description='用户ID')
    membership_status: str = Field(description='会员状态')
    membership_end_time: Optional[datetime] = Field(default=None, description='会员到期时间')
    quotas: list[dict[str, Any]] = Field(description='配额列表')
