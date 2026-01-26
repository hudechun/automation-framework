"""
订单和支付管理控制器
"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Path, Query, Request, Response
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_thesis.entity.vo import (
    OrderPageQueryModel,
    FeatureServicePageQueryModel,
    FeatureServiceModel,
    ExportRecordPageQueryModel,
)
from module_thesis.service import OrderService
from utils.log_util import logger
from utils.response_util import ResponseUtil

order_controller = APIRouterPro(
    prefix='/thesis/order',
    order_num=4,
    tags=['论文系统-订单管理'],
    dependencies=[PreAuthDependency()]
)


# ==================== 订单管理 ====================

@order_controller.get(
    '/list',
    summary='获取订单列表',
    description='获取订单分页列表',
    response_model=PageResponseModel,
)
async def get_order_list(
    request: Request,
    query: Annotated[OrderPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取订单列表"""
    # 普通用户只能查看自己的订单
    if not current_user.user.admin:
        query.user_id = current_user.user.user_id
    
    result = await OrderService.get_order_list(query_db, query, is_page=True)
    logger.info('获取订单列表成功')
    return ResponseUtil.success(model_content=result)


@order_controller.get(
    '/my',
    summary='获取我的订单',
    description='获取当前用户的订单列表',
    response_model=PageResponseModel,
)
async def get_my_orders(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    status: Annotated[str | None, Query(description='订单状态')] = None,
    page_num: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 10,
) -> Response:
    """获取我的订单"""
    query = OrderPageQueryModel(
        user_id=current_user.user.user_id,
        status=status,
        page_num=page_num,
        page_size=page_size
    )
    result = await OrderService.get_order_list(query_db, query, is_page=True)
    logger.info('获取我的订单成功')
    return ResponseUtil.success(model_content=result)


@order_controller.get(
    '/{order_id}',
    summary='获取订单详情',
    description='获取指定订单的详细信息',
    response_model=DataResponseModel,
)
async def get_order_detail(
    request: Request,
    order_id: Annotated[int, Path(description='订单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取订单详情"""
    result = await OrderService.get_order_detail(query_db, order_id)
    
    # 权限检查：只能查看自己的订单（管理员除外）
    if not current_user.user.admin and result.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此订单')
    
    logger.info(f'获取订单ID为{order_id}的信息成功')
    return ResponseUtil.success(data=result)


@order_controller.post(
    '/create',
    summary='创建订单',
    description='创建新订单',
    response_model=ResponseBaseModel,
)
@Log(title='订单管理', business_type=BusinessType.INSERT)
async def create_order(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    order_type: Annotated[str, Query(description='订单类型：package-套餐, service-服务')],
    item_id: Annotated[int, Query(description='商品ID')],
    amount: Annotated[Decimal, Query(description='订单金额')],
    payment_method: Annotated[str, Query(description='支付方式：wechat, alipay')] = 'wechat',
) -> Response:
    """创建订单"""
    result = await OrderService.create_order(
        query_db,
        current_user.user.user_id,
        order_type,
        item_id,
        amount,
        payment_method
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@order_controller.post(
    '/cancel/{order_id}',
    summary='取消订单',
    description='取消待支付的订单',
    response_model=ResponseBaseModel,
)
@Log(title='订单管理', business_type=BusinessType.UPDATE)
async def cancel_order(
    request: Request,
    order_id: Annotated[int, Path(description='订单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """取消订单"""
    result = await OrderService.cancel_order(
        query_db,
        order_id,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 支付处理 ====================

@order_controller.post(
    '/payment/callback',
    summary='支付回调',
    description='处理支付平台的回调通知',
    response_model=ResponseBaseModel,
)
@Log(title='支付处理', business_type=BusinessType.OTHER)
async def payment_callback(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    order_no: Annotated[str, Query(description='订单号')],
    transaction_id: Annotated[str, Query(description='第三方交易号')],
) -> Response:
    """支付回调"""
    result = await OrderService.process_payment(
        query_db,
        order_no,
        transaction_id,
        datetime.now()
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@order_controller.post(
    '/refund/{order_id}',
    summary='申请退款',
    description='申请订单退款',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:order:refund')],
)
@Log(title='订单退款', business_type=BusinessType.OTHER)
async def refund_order(
    request: Request,
    order_id: Annotated[int, Path(description='订单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    refund_reason: Annotated[str | None, Query(description='退款原因')] = None,
) -> Response:
    """申请退款"""
    result = await OrderService.process_refund(query_db, order_id, refund_reason)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@order_controller.get(
    '/statistics',
    summary='获取订单统计',
    description='获取订单统计信息',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('thesis:order:list')],
)
async def get_order_statistics(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    user_id: Annotated[int | None, Query(description='用户ID')] = None,
) -> Response:
    """获取订单统计"""
    result = await OrderService.get_order_statistics(query_db, user_id)
    return ResponseUtil.success(data=result)


# ==================== 功能服务管理 ====================

@order_controller.get(
    '/service/list',
    summary='获取功能服务列表',
    description='获取功能服务分页列表',
    response_model=PageResponseModel[FeatureServiceModel],
)
async def get_service_list(
    request: Request,
    query: Annotated[FeatureServicePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取功能服务列表"""
    result = await OrderService.get_service_list(query_db, query, is_page=True)
    logger.info('获取功能服务列表成功')
    return ResponseUtil.success(model_content=result)


@order_controller.get(
    '/service/{service_id}',
    summary='获取服务详情',
    description='获取指定服务的详细信息',
    response_model=DataResponseModel[FeatureServiceModel],
)
async def get_service_detail(
    request: Request,
    service_id: Annotated[int, Path(description='服务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取服务详情"""
    result = await OrderService.get_service_detail(query_db, service_id)
    logger.info(f'获取服务ID为{service_id}的信息成功')
    return ResponseUtil.success(data=result)


@order_controller.post(
    '/service',
    summary='创建功能服务',
    description='创建新的功能服务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:service:add')],
)
@ValidateFields(validate_model='add_service')
@Log(title='功能服务管理', business_type=BusinessType.INSERT)
async def create_service(
    request: Request,
    service_data: FeatureServiceModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建功能服务"""
    service_data.create_by = current_user.user.user_name
    service_data.create_time = datetime.now()
    
    result = await OrderService.create_service(query_db, service_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@order_controller.put(
    '/service',
    summary='更新功能服务',
    description='更新功能服务信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:service:edit')],
)
@ValidateFields(validate_model='edit_service')
@Log(title='功能服务管理', business_type=BusinessType.UPDATE)
async def update_service(
    request: Request,
    service_data: FeatureServiceModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新功能服务"""
    service_data.update_by = current_user.user.user_name
    service_data.update_time = datetime.now()
    
    result = await OrderService.update_service(query_db, service_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@order_controller.delete(
    '/service/{service_id}',
    summary='删除功能服务',
    description='删除指定功能服务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:service:remove')],
)
@Log(title='功能服务管理', business_type=BusinessType.DELETE)
async def delete_service(
    request: Request,
    service_id: Annotated[int, Path(description='服务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除功能服务"""
    result = await OrderService.delete_service(query_db, service_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 导出记录管理 ====================

@order_controller.get(
    '/export/list',
    summary='获取导出记录列表',
    description='获取导出记录分页列表',
    response_model=PageResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:export:list')],
)
async def get_export_record_list(
    request: Request,
    query: Annotated[ExportRecordPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取导出记录列表"""
    # 普通用户只能查看自己的记录
    if not current_user.user.admin:
        query.user_id = current_user.user.user_id
    
    result = await OrderService.get_export_record_list(query_db, query, is_page=True)
    logger.info('获取导出记录列表成功')
    return ResponseUtil.success(model_content=result)


@order_controller.get(
    '/export/my',
    summary='获取我的导出记录',
    description='获取当前用户的导出记录',
    response_model=PageResponseModel,
)
async def get_my_export_records(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    thesis_id: Annotated[int | None, Query(description='论文ID')] = None,
    page_num: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 10,
) -> Response:
    """获取我的导出记录"""
    query = ExportRecordPageQueryModel(
        user_id=current_user.user.user_id,
        thesis_id=thesis_id,
        page_num=page_num,
        page_size=page_size
    )
    result = await OrderService.get_export_record_list(query_db, query, is_page=True)
    logger.info('获取我的导出记录成功')
    return ResponseUtil.success(model_content=result)


@order_controller.post(
    '/export/create',
    summary='创建导出记录',
    description='创建论文导出记录（需要扣减配额）',
    response_model=ResponseBaseModel,
)
@Log(title='论文导出', business_type=BusinessType.EXPORT)
async def create_export_record(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    thesis_id: Annotated[int, Query(description='论文ID')],
    export_format: Annotated[str, Query(description='导出格式：docx, pdf')],
    file_path: Annotated[str, Query(description='文件路径')],
    file_size: Annotated[int, Query(description='文件大小（字节）')],
) -> Response:
    """创建导出记录"""
    result = await OrderService.create_export_record(
        query_db,
        current_user.user.user_id,
        thesis_id,
        export_format,
        file_path,
        file_size
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@order_controller.get(
    '/export/count',
    summary='获取导出次数',
    description='获取用户的导出次数统计',
    response_model=DataResponseModel[int],
)
async def get_export_count(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    thesis_id: Annotated[int | None, Query(description='论文ID')] = None,
) -> Response:
    """获取导出次数"""
    result = await OrderService.get_user_export_count(
        query_db,
        current_user.user.user_id,
        thesis_id
    )
    return ResponseUtil.success(data=result)
