"""
会员管理控制器
"""
from datetime import datetime
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
    MemberPackageModel,
    MemberPackagePageQueryModel,
    UserMembershipPageQueryModel,
    UserFeatureQuotaPageQueryModel,
    QuotaRecordPageQueryModel,
)
from module_thesis.service import MemberService
from utils.log_util import logger
from utils.response_util import ResponseUtil

member_controller = APIRouterPro(
    prefix='/thesis/member',
    order_num=1,
    tags=['论文系统-会员管理'],
    dependencies=[PreAuthDependency()]
)


# ==================== 会员套餐管理 ====================

@member_controller.get(
    '/package/list',
    summary='获取会员套餐列表',
    description='获取会员套餐分页列表',
    response_model=PageResponseModel[MemberPackageModel],
    dependencies=[UserInterfaceAuthDependency('thesis:member:list')],
)
async def get_package_list(
    request: Request,
    query: Annotated[MemberPackagePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取会员套餐列表"""
    result = await MemberService.get_package_list(query_db, query, is_page=True)
    logger.info('获取会员套餐列表成功')
    return ResponseUtil.success(model_content=result)


@member_controller.get(
    '/package/{package_id}',
    summary='获取套餐详情',
    description='获取指定套餐的详细信息',
    response_model=DataResponseModel[MemberPackageModel],
    dependencies=[UserInterfaceAuthDependency('thesis:member:query')],
)
async def get_package_detail(
    request: Request,
    package_id: Annotated[int, Path(description='套餐ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取套餐详情"""
    result = await MemberService.get_package_detail(query_db, package_id)
    logger.info(f'获取套餐ID为{package_id}的信息成功')
    return ResponseUtil.success(data=result)


@member_controller.post(
    '/package',
    summary='新增会员套餐',
    description='创建新的会员套餐',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:add')],
)
@ValidateFields(validate_model='add_package')
@Log(title='会员套餐管理', business_type=BusinessType.INSERT)
async def add_package(
    request: Request,
    package_data: MemberPackageModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增会员套餐"""
    package_data.create_by = current_user.user.user_name
    package_data.create_time = datetime.now()
    package_data.update_by = current_user.user.user_name
    package_data.update_time = datetime.now()
    
    result = await MemberService.add_package(query_db, package_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@member_controller.put(
    '/package',
    summary='更新会员套餐',
    description='更新会员套餐信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:edit')],
)
@ValidateFields(validate_model='edit_package')
@Log(title='会员套餐管理', business_type=BusinessType.UPDATE)
async def update_package(
    request: Request,
    package_data: MemberPackageModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新会员套餐"""
    package_data.update_by = current_user.user.user_name
    package_data.update_time = datetime.now()
    
    result = await MemberService.update_package(query_db, package_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@member_controller.delete(
    '/package/{package_id}',
    summary='删除会员套餐',
    description='删除指定的会员套餐',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:remove')],
)
@Log(title='会员套餐管理', business_type=BusinessType.DELETE)
async def delete_package(
    request: Request,
    package_id: Annotated[int, Path(description='套餐ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除会员套餐"""
    result = await MemberService.delete_package(query_db, package_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 用户会员管理 ====================

@member_controller.get(
    '/membership/{membership_id}',
    summary='获取用户会员详情',
    description='获取指定用户会员的详细信息',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:query')],
)
async def get_membership_detail(
    request: Request,
    membership_id: Annotated[int, Path(description='会员ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取用户会员详情"""
    result = await MemberService.get_membership_detail(query_db, membership_id)
    logger.info(f'获取会员ID为{membership_id}的信息成功')
    return ResponseUtil.success(data=result)


@member_controller.post(
    '/membership',
    summary='新增用户会员',
    description='为用户开通会员',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:add')],
)
@Log(title='用户会员管理', business_type=BusinessType.INSERT)
async def add_membership(
    request: Request,
    user_id: Annotated[int, Query(description='用户ID')],
    package_id: Annotated[int, Query(description='套餐ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增用户会员"""
    result = await MemberService.activate_membership(query_db, user_id, package_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@member_controller.put(
    '/membership',
    summary='更新用户会员',
    description='更新用户会员信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:edit')],
)
@Log(title='用户会员管理', business_type=BusinessType.UPDATE)
async def update_membership(
    request: Request,
    membership_id: Annotated[int, Query(description='会员ID')],
    package_id: Annotated[int, Query(description='套餐ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新用户会员"""
    result = await MemberService.update_membership(query_db, membership_id, package_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@member_controller.delete(
    '/membership/{membership_id}',
    summary='删除用户会员',
    description='删除指定用户会员',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:remove')],
)
@Log(title='用户会员管理', business_type=BusinessType.DELETE)
async def delete_membership(
    request: Request,
    membership_id: Annotated[int, Path(description='会员ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除用户会员"""
    result = await MemberService.delete_membership(query_db, membership_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@member_controller.post(
    '/membership/renew',
    summary='续费会员',
    description='为用户会员续费',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:renew')],
)
@Log(title='会员续费', business_type=BusinessType.OTHER)
async def renew_membership(
    request: Request,
    membership_id: Annotated[int, Query(description='会员ID')],
    duration: Annotated[int, Query(description='续费天数', ge=1)],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """续费会员"""
    result = await MemberService.renew_membership(query_db, membership_id, duration)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@member_controller.get(
    '/membership/list',
    summary='获取用户会员列表',
    description='获取用户会员分页列表',
    response_model=PageResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:list')],
)
async def get_membership_list(
    request: Request,
    query: Annotated[UserMembershipPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取用户会员列表"""
    result = await MemberService.get_membership_list(query_db, query, is_page=True)
    logger.info('获取用户会员列表成功')
    return ResponseUtil.success(model_content=result)


@member_controller.get(
    '/membership/my',
    summary='获取我的会员信息',
    description='获取当前用户的会员信息',
    response_model=DataResponseModel,
)
async def get_my_membership(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取我的会员信息"""
    result = await MemberService.get_user_membership(query_db, current_user.user.user_id)
    logger.info('获取会员信息成功')
    return ResponseUtil.success(data=result)


@member_controller.post(
    '/membership/activate',
    summary='激活会员',
    description='激活用户会员（通过支付后调用）',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:member:activate')],
)
@Log(title='会员管理', business_type=BusinessType.OTHER)
async def activate_membership(
    request: Request,
    user_id: Annotated[int, Query(description='用户ID')],
    package_id: Annotated[int, Query(description='套餐ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """激活会员"""
    result = await MemberService.activate_membership(query_db, user_id, package_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 配额管理 ====================

@member_controller.get(
    '/quota/list',
    summary='获取用户配额列表',
    description='获取用户配额分页列表',
    response_model=PageResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:quota:list')],
)
async def get_quota_list(
    request: Request,
    query: Annotated[UserFeatureQuotaPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取用户配额列表"""
    result = await MemberService.get_user_quota_list(query_db, query, is_page=True)
    logger.info('获取用户配额列表成功')
    return ResponseUtil.success(model_content=result)


@member_controller.get(
    '/quota/my',
    summary='获取我的配额',
    description='获取当前用户的所有功能配额',
    response_model=DataResponseModel,
)
async def get_my_quota(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取我的配额"""
    query = UserFeatureQuotaPageQueryModel(user_id=current_user.user.user_id)
    result = await MemberService.get_user_quota_list(query_db, query, is_page=False)
    logger.info('获取配额信息成功')
    return ResponseUtil.success(data=result)


@member_controller.get(
    '/quota/check',
    summary='检查配额',
    description='检查用户指定功能的配额是否充足',
    response_model=DataResponseModel[bool],
)
async def check_quota(
    request: Request,
    feature_type: Annotated[str, Query(description='功能类型')],
    amount: Annotated[int, Query(description='需要的配额数量', ge=1)],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """检查配额"""
    result = await MemberService.check_quota(
        query_db,
        current_user.user.user_id,
        feature_type,
        amount
    )
    return ResponseUtil.success(data=result)


# ==================== 配额使用记录 ====================

@member_controller.get(
    '/quota/record/list',
    summary='获取配额使用记录',
    description='获取配额使用记录分页列表',
    response_model=PageResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:quota:list')],
)
async def get_quota_record_list(
    request: Request,
    query: Annotated[QuotaRecordPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取配额使用记录"""
    result = await MemberService.get_quota_record_list(query_db, query, is_page=True)
    logger.info('获取配额使用记录成功')
    return ResponseUtil.success(model_content=result)


@member_controller.get(
    '/quota/record/my',
    summary='获取我的配额使用记录',
    description='获取当前用户的配额使用记录',
    response_model=PageResponseModel,
)
async def get_my_quota_record(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    feature_type: Annotated[str | None, Query(description='功能类型')] = None,
    page_num: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 10,
) -> Response:
    """获取我的配额使用记录"""
    query = QuotaRecordPageQueryModel(
        user_id=current_user.user.user_id,
        feature_type=feature_type,
        page_num=page_num,
        page_size=page_size
    )
    result = await MemberService.get_quota_record_list(query_db, query, is_page=True)
    logger.info('获取配额使用记录成功')
    return ResponseUtil.success(model_content=result)


@member_controller.get(
    '/quota/statistics',
    summary='获取配额统计',
    description='获取用户配额使用统计',
    response_model=DataResponseModel[int],
)
async def get_quota_statistics(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    feature_type: Annotated[str | None, Query(description='功能类型')] = None,
) -> Response:
    """获取配额统计"""
    result = await MemberService.get_quota_statistics(
        query_db,
        current_user.user.user_id,
        feature_type
    )
    return ResponseUtil.success(data=result)


# ==================== 配额详细检查和预警 ====================

@member_controller.get(
    '/quota/check/detailed',
    summary='详细检查配额',
    description='详细检查用户指定功能的配额，返回详细信息',
    response_model=DataResponseModel,
)
async def check_quota_detailed(
    request: Request,
    feature_type: Annotated[str, Query(description='功能类型')],
    amount: Annotated[int, Query(description='需要的配额数量', ge=1)],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """详细检查配额"""
    from module_thesis.service.member_service import QuotaCheckResult
    
    result: QuotaCheckResult = await MemberService.check_quota_detailed(
        query_db,
        current_user.user.user_id,
        feature_type,
        amount
    )
    
    return ResponseUtil.success(data={
        'is_sufficient': result.is_sufficient,
        'remaining_quota': result.remaining_quota,
        'required_quota': result.required_quota,
        'error_code': result.error_code,
        'error_message': result.error_message,
        'suggestion': result.suggestion
    })


@member_controller.get(
    '/quota/warning',
    summary='配额预警检查',
    description='检查用户配额预警状态',
    response_model=DataResponseModel,
)
async def check_quota_warning(
    request: Request,
    feature_type: Annotated[str, Query(description='功能类型')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """配额预警检查"""
    result = await MemberService.check_quota_warning(
        query_db,
        current_user.user.user_id,
        feature_type
    )
    return ResponseUtil.success(data=result)


@member_controller.post(
    '/quota/compensate',
    summary='配额补偿',
    description='管理员补偿用户配额（用于异常情况）',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:quota:compensate')],
)
async def compensate_quota(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    user_id: Annotated[int, Query(description='用户ID')],
    feature_type: Annotated[str, Query(description='功能类型')],
    amount: Annotated[int, Query(description='补偿数量', ge=1)],
    reason: Annotated[str, Query(description='补偿原因')],
    business_id: Annotated[int, Query(description='业务ID')] = 0,
) -> Response:
    """配额补偿"""
    result = await MemberService.compensate_quota(
        query_db,
        user_id,
        feature_type,
        amount,
        reason,
        business_id
    )
    logger.info(f'配额补偿成功: 用户{user_id}, 功能{feature_type}, 数量{amount}')
    return ResponseUtil.success(model_content=result)
