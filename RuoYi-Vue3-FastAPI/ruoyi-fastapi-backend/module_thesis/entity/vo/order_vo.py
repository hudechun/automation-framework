"""
订单和支付相关VO模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


# ==================== 订单相关VO ====================


class OrderModel(BaseModel):
    """
    订单信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    order_id: Optional[int] = Field(default=None, description='订单ID')
    order_no: Optional[str] = Field(default=None, description='订单号')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    package_id: Optional[int] = Field(default=None, description='套餐ID')
    amount: Optional[Decimal] = Field(default=None, description='订单金额')
    payment_method: Optional[str] = Field(default=None, description='支付方式')
    payment_time: Optional[datetime] = Field(default=None, description='支付时间')
    transaction_id: Optional[str] = Field(default=None, description='第三方交易号')
    status: Optional[Literal['pending', 'paid', 'refunded', 'cancelled']] = Field(default=None, description='订单状态')
    expired_at: Optional[datetime] = Field(default=None, description='订单过期时间')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class CreateOrderModel(BaseModel):
    """
    创建订单请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    package_id: int = Field(description='套餐ID')
    payment_method: str = Field(description='支付方式（wechat/alipay）')

    @NotBlank(field_name='package_id', message='套餐ID不能为空')
    def get_package_id(self) -> int:
        return self.package_id

    @NotBlank(field_name='payment_method', message='支付方式不能为空')
    def get_payment_method(self) -> str:
        return self.payment_method

    def validate_fields(self) -> None:
        self.get_package_id()
        self.get_payment_method()


class OrderQueryModel(BaseModel):
    """
    订单查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: Optional[int] = Field(default=None, description='用户ID')
    order_no: Optional[str] = Field(default=None, description='订单号')
    status: Optional[str] = Field(default=None, description='订单状态')
    payment_method: Optional[str] = Field(default=None, description='支付方式')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class OrderPageQueryModel(OrderQueryModel):
    """
    订单分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class PaymentCallbackModel(BaseModel):
    """
    支付回调模型（通用）
    """

    model_config = ConfigDict(alias_generator=to_camel)

    order_no: str = Field(description='订单号')
    transaction_id: str = Field(description='第三方交易号')
    payment_time: datetime = Field(description='支付时间')
    amount: Decimal = Field(description='支付金额')
    sign: str = Field(description='签名')


class RefundOrderModel(BaseModel):
    """
    退款请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    order_id: int = Field(description='订单ID')
    refund_reason: Optional[str] = Field(default=None, description='退款原因')

    @NotBlank(field_name='order_id', message='订单ID不能为空')
    def get_order_id(self) -> int:
        return self.order_id

    def validate_fields(self) -> None:
        self.get_order_id()


# ==================== 功能服务相关VO ====================


class FeatureServiceModel(BaseModel):
    """
    功能服务信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    service_id: Optional[int] = Field(default=None, description='服务ID')
    service_name: Optional[str] = Field(default=None, description='服务名称')
    service_type: Optional[str] = Field(default=None, description='服务类型')
    price: Optional[Decimal] = Field(default=None, description='服务价格')
    billing_unit: Optional[str] = Field(default=None, description='计费单位')
    service_desc: Optional[str] = Field(default=None, description='服务描述')
    sort_order: Optional[int] = Field(default=None, description='显示顺序')
    status: Optional[Literal['0', '1']] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='service_name', message='服务名称不能为空')
    @Size(field_name='service_name', min_length=0, max_length=50, message='服务名称长度不能超过50个字符')
    def get_service_name(self) -> Union[str, None]:
        return self.service_name

    @NotBlank(field_name='service_type', message='服务类型不能为空')
    def get_service_type(self) -> Union[str, None]:
        return self.service_type

    @NotBlank(field_name='price', message='服务价格不能为空')
    def get_price(self) -> Union[Decimal, None]:
        return self.price

    def validate_fields(self) -> None:
        self.get_service_name()
        self.get_service_type()
        self.get_price()


class FeatureServiceQueryModel(BaseModel):
    """
    功能服务查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    service_name: Optional[str] = Field(default=None, description='服务名称')
    service_type: Optional[str] = Field(default=None, description='服务类型')
    status: Optional[str] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class FeatureServicePageQueryModel(FeatureServiceQueryModel):
    """
    功能服务分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class PurchaseFeatureServiceModel(BaseModel):
    """
    购买功能服务请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    service_id: int = Field(description='服务ID')
    quantity: int = Field(description='购买数量')
    payment_method: str = Field(description='支付方式（wechat/alipay）')

    @NotBlank(field_name='service_id', message='服务ID不能为空')
    def get_service_id(self) -> int:
        return self.service_id

    @NotBlank(field_name='quantity', message='购买数量不能为空')
    def get_quantity(self) -> int:
        return self.quantity

    @NotBlank(field_name='payment_method', message='支付方式不能为空')
    def get_payment_method(self) -> str:
        return self.payment_method

    def validate_fields(self) -> None:
        self.get_service_id()
        self.get_quantity()
        self.get_payment_method()


# ==================== 导出记录相关VO ====================


class ExportRecordModel(BaseModel):
    """
    导出记录信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    record_id: Optional[int] = Field(default=None, description='记录ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    file_name: Optional[str] = Field(default=None, description='文件名')
    file_path: Optional[str] = Field(default=None, description='文件路径')
    file_size: Optional[int] = Field(default=None, description='文件大小')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class ExportThesisModel(BaseModel):
    """
    导出论文请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    thesis_id: int = Field(description='论文ID')
    export_format: str = Field(default='docx', description='导出格式（docx/pdf）')

    @NotBlank(field_name='thesis_id', message='论文ID不能为空')
    def get_thesis_id(self) -> int:
        return self.thesis_id

    def validate_fields(self) -> None:
        self.get_thesis_id()


class ExportRecordQueryModel(BaseModel):
    """
    导出记录查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: Optional[int] = Field(default=None, description='用户ID')
    thesis_id: Optional[int] = Field(default=None, description='论文ID')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class ExportRecordPageQueryModel(ExportRecordQueryModel):
    """
    导出记录分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


# ==================== 响应VO ====================


class OrderDetailResponseModel(BaseModel):
    """
    订单详情响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    order_id: int = Field(description='订单ID')
    order_no: str = Field(description='订单号')
    package_name: str = Field(description='套餐名称')
    amount: Decimal = Field(description='订单金额')
    payment_method: str = Field(description='支付方式')
    payment_time: Optional[datetime] = Field(default=None, description='支付时间')
    status: str = Field(description='订单状态')
    expired_at: datetime = Field(description='订单过期时间')
    create_time: datetime = Field(description='创建时间')


class PaymentResultModel(BaseModel):
    """
    支付结果响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    success: bool = Field(description='支付是否成功')
    order_no: str = Field(description='订单号')
    transaction_id: Optional[str] = Field(default=None, description='第三方交易号')
    message: str = Field(description='结果消息')


class OrderStatisticsModel(BaseModel):
    """
    订单统计响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    total_count: int = Field(description='订单总数')
    total_amount: Decimal = Field(description='订单总金额')
    paid_count: int = Field(default=0, description='已支付订单数')
    paid_amount: Decimal = Field(default=Decimal('0'), description='已支付金额')


class ExportRecordDetailModel(BaseModel):
    """
    导出记录详情响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    record_id: int = Field(description='记录ID')
    thesis_title: str = Field(description='论文标题')
    file_name: str = Field(description='文件名')
    file_size: int = Field(description='文件大小')
    download_url: str = Field(description='下载链接')
    create_time: datetime = Field(description='创建时间')
