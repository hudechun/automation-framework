"""
会员管理服务层
"""
from typing import Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from common.constant import CommonConstant
from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao import (
    MemberPackageDao,
    UserMembershipDao,
    UserFeatureQuotaDao,
    QuotaRecordDao,
)
from module_thesis.entity.vo import (
    MemberPackageModel,
    UserMembershipModel,
    UserFeatureQuotaModel,
    DeductQuotaModel,
    MemberPackagePageQueryModel,
    UserMembershipPageQueryModel,
    UserFeatureQuotaPageQueryModel,
    QuotaRecordPageQueryModel,
)
from utils.common_util import CamelCaseUtil


@dataclass
class QuotaCheckResult:
    """配额检查结果"""
    is_sufficient: bool  # 配额是否充足
    remaining_quota: int  # 剩余配额
    required_quota: int  # 需要的配额
    error_code: str  # 错误代码
    error_message: str  # 错误信息
    suggestion: str  # 建议操作


class MemberService:
    """
    会员管理服务类
    """

    # ==================== 会员套餐管理 ====================

    @classmethod
    async def get_package_list(
        cls,
        query_db: AsyncSession,
        query_object: MemberPackagePageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取会员套餐列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 套餐列表
        """
        # 将 Pydantic 模型转换为字典
        query_dict = query_object.model_dump(exclude_none=True) if query_object else {}
        return await MemberPackageDao.get_package_list(query_db, query_dict, is_page)

    @classmethod
    async def get_package_detail(cls, query_db: AsyncSession, package_id: int) -> MemberPackageModel:
        """
        获取套餐详情

        :param query_db: 数据库会话
        :param package_id: 套餐ID
        :return: 套餐详情
        """
        package = await MemberPackageDao.get_package_by_id(query_db, package_id)
        if not package:
            raise ServiceException(message='套餐不存在')
        return MemberPackageModel(**CamelCaseUtil.transform_result(package))

    @classmethod
    async def add_package(cls, query_db: AsyncSession, package_data: MemberPackageModel) -> CrudResponseModel:
        """
        新增会员套餐

        :param query_db: 数据库会话
        :param package_data: 套餐数据
        :return: 操作结果
        """
        try:
            await MemberPackageDao.add_package(query_db, package_data.model_dump(exclude_none=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def update_package(cls, query_db: AsyncSession, package_data: MemberPackageModel) -> CrudResponseModel:
        """
        更新会员套餐

        :param query_db: 数据库会话
        :param package_data: 套餐数据
        :return: 操作结果
        """
        # 检查套餐是否存在
        await cls.get_package_detail(query_db, package_data.package_id)

        try:
            update_data = package_data.model_dump(exclude_unset=True)
            await MemberPackageDao.update_package(query_db, package_data.package_id, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_package(cls, query_db: AsyncSession, package_id: int) -> CrudResponseModel:
        """
        删除会员套餐

        :param query_db: 数据库会话
        :param package_id: 套餐ID
        :return: 操作结果
        """
        # 检查套餐是否存在
        await cls.get_package_detail(query_db, package_id)

        try:
            await MemberPackageDao.delete_package(query_db, package_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    # ==================== 用户会员管理 ====================

    @classmethod
    async def get_membership_list(
        cls,
        query_db: AsyncSession,
        query_object: UserMembershipPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取用户会员列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 会员列表
        """
        return await UserMembershipDao.get_membership_list(query_db, query_object, is_page)

    @classmethod
    async def get_user_membership(cls, query_db: AsyncSession, user_id: int) -> Union[UserMembershipModel, None]:
        """
        获取用户会员信息

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :return: 会员信息
        """
        membership = await UserMembershipDao.get_membership_by_user_id(query_db, user_id)
        if membership:
            return UserMembershipModel(**CamelCaseUtil.transform_result(membership))
        return None

    @classmethod
    async def activate_membership(
        cls,
        query_db: AsyncSession,
        user_id: int,
        package_id: int,
        auto_commit: bool = False
    ) -> CrudResponseModel:
        """
        激活用户会员（不自动提交事务，由调用方控制）

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param package_id: 套餐ID
        :param auto_commit: 是否自动提交（默认False，由调用方控制事务）
        :return: 操作结果
        """
        # 获取套餐信息
        package = await cls.get_package_detail(query_db, package_id)

        # 检查用户是否已有会员
        existing_membership = await cls.get_user_membership(query_db, user_id)

        try:
            if existing_membership:
                # 续费会员 - 延长结束时间
                new_end_date = max(
                    existing_membership.end_date or datetime.now(),
                    datetime.now()
                ) + timedelta(days=package.duration_days)

                await UserMembershipDao.update_membership(
                    query_db,
                    {
                        'membership_id': existing_membership.membership_id,
                        'end_date': new_end_date,
                        'status': '0',  # 激活状态
                    }
                )
            else:
                # 新开通会员
                membership_data = {
                    'user_id': user_id,
                    'package_id': package_id,
                    'total_word_quota': package.word_quota,
                    'used_word_quota': 0,
                    'total_usage_quota': package.usage_quota,
                    'used_usage_quota': 0,
                    'start_date': datetime.now(),
                    'end_date': datetime.now() + timedelta(days=package.duration_days),
                    'status': '0',
                }
                await UserMembershipDao.add_membership(query_db, membership_data)

            # 配额已经在会员表中管理，不需要单独初始化
            # await cls._init_user_quotas(query_db, user_id, package.features)

            # 只有明确要求才自动提交
            if auto_commit:
                await query_db.commit()
            
            return CrudResponseModel(is_success=True, message='会员激活成功')
        except Exception as e:
            if auto_commit:
                await query_db.rollback()
            raise e

    @classmethod
    async def _init_user_quotas(cls, query_db: AsyncSession, user_id: int, features: dict):
        """
        初始化用户功能配额

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param features: 功能配额字典
        """
        for feature_type, quota_amount in features.items():
            # 检查配额是否已存在
            existing_quota = await UserFeatureQuotaDao.get_quota_by_user_and_feature(
                query_db, user_id, feature_type
            )

            if existing_quota:
                # 增加配额
                await UserFeatureQuotaDao.add_quota_amount(
                    query_db,
                    user_id,
                    feature_type,
                    quota_amount
                )
            else:
                # 创建新配额
                quota_data = {
                    'user_id': user_id,
                    'feature_type': feature_type,
                    'total_quota': quota_amount,
                    'used_quota': 0,
                    'remaining_quota': quota_amount,
                }
                await UserFeatureQuotaDao.add_quota(query_db, quota_data)

    # ==================== 配额管理 ====================

    @classmethod
    async def get_user_quota_list(
        cls,
        query_db: AsyncSession,
        query_object: UserFeatureQuotaPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取用户配额列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 配额列表
        """
        return await UserFeatureQuotaDao.get_quota_list(query_db, query_object, is_page)

    @classmethod
    async def get_user_quota(
        cls,
        query_db: AsyncSession,
        user_id: int,
        feature_type: str
    ) -> Union[UserFeatureQuotaModel, None]:
        """
        获取用户特定功能配额

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :return: 配额信息
        """
        quota = await UserFeatureQuotaDao.get_quota_by_user_and_feature(query_db, user_id, feature_type)
        if quota:
            return UserFeatureQuotaModel(**CamelCaseUtil.transform_result(quota))
        return None

    @classmethod
    async def check_quota(cls, query_db: AsyncSession, user_id: int, feature_type: str, amount: int) -> bool:
        """
        检查用户配额是否充足（简单版本，向后兼容）
        
        现在直接检查会员表中的配额，不再依赖单独的配额表

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型（暂时忽略，统一检查使用次数）
        :param amount: 需要的配额数量
        :return: 是否充足
        """
        # 获取用户会员信息
        membership = await cls.get_user_membership(query_db, user_id)
        if not membership:
            return False
        
        # 检查会员是否过期
        if membership.end_date and membership.end_date < datetime.now():
            return False
        
        # 检查使用次数配额
        remaining_usage = membership.total_usage_quota - (membership.used_usage_quota or 0)
        return remaining_usage >= amount

    @classmethod
    async def check_quota_detailed(
        cls,
        query_db: AsyncSession,
        user_id: int,
        feature_type: str,
        amount: int
    ) -> QuotaCheckResult:
        """
        详细检查用户配额（返回详细的检查结果）

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :param amount: 需要的配额数量
        :return: 详细的检查结果
        """
        # 1. 检查会员状态
        membership = await cls.get_user_membership(query_db, user_id)
        
        if not membership:
            return QuotaCheckResult(
                is_sufficient=False,
                remaining_quota=0,
                required_quota=amount,
                error_code='MEMBERSHIP_NOT_FOUND',
                error_message='您还未开通会员',
                suggestion='请先购买会员套餐以使用此功能'
            )
        
        # 2. 检查会员是否过期
        if membership.expire_time and membership.expire_time < datetime.now():
            return QuotaCheckResult(
                is_sufficient=False,
                remaining_quota=0,
                required_quota=amount,
                error_code='MEMBERSHIP_EXPIRED',
                error_message=f'您的会员已于 {membership.expire_time.strftime("%Y-%m-%d")} 过期',
                suggestion='请续费会员以继续使用'
            )
        
        # 3. 检查配额记录
        quota = await cls.get_user_quota(query_db, user_id, feature_type)
        
        if not quota:
            return QuotaCheckResult(
                is_sufficient=False,
                remaining_quota=0,
                required_quota=amount,
                error_code='QUOTA_NOT_INITIALIZED',
                error_message='配额未初始化',
                suggestion='请联系客服处理'
            )
        
        # 4. 检查配额是否充足
        if quota.remaining_quota < amount:
            # 获取功能类型的中文名称
            feature_names = {
                'thesis_generation': '论文生成',
                'outline_generation': '大纲生成',
                'chapter_generation': '章节生成',
                'export': '导出'
            }
            feature_name = feature_names.get(feature_type, feature_type)
            
            return QuotaCheckResult(
                is_sufficient=False,
                remaining_quota=quota.remaining_quota,
                required_quota=amount,
                error_code='QUOTA_INSUFFICIENT',
                error_message=f'{feature_name}配额不足，当前剩余 {quota.remaining_quota} 次，需要 {amount} 次',
                suggestion='请购买配额包或升级会员套餐'
            )
        
        # 5. 配额充足
        return QuotaCheckResult(
            is_sufficient=True,
            remaining_quota=quota.remaining_quota,
            required_quota=amount,
            error_code='SUCCESS',
            error_message='配额充足',
            suggestion=''
        )

    @classmethod
    async def check_quota_warning(
        cls,
        query_db: AsyncSession,
        user_id: int,
        feature_type: str
    ) -> dict:
        """
        检查配额预警

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :return: 预警信息
        """
        quota = await cls.get_user_quota(query_db, user_id, feature_type)
        
        if not quota:
            return {
                'has_warning': True,
                'warning_level': 'critical',
                'message': '您还未开通此功能',
                'suggestion': '请购买会员套餐'
            }
        
        # 计算使用率
        usage_rate = quota.used_quota / quota.total_quota if quota.total_quota > 0 else 0
        
        # 配额用完
        if quota.remaining_quota == 0:
            return {
                'has_warning': True,
                'warning_level': 'critical',
                'message': '配额已用完',
                'suggestion': '请购买配额包或升级套餐',
                'remaining_quota': 0,
                'total_quota': quota.total_quota
            }
        
        # 配额不足10%
        elif usage_rate >= 0.9:
            return {
                'has_warning': True,
                'warning_level': 'high',
                'message': f'配额即将用完，仅剩 {quota.remaining_quota} 次',
                'suggestion': '建议尽快购买配额包',
                'remaining_quota': quota.remaining_quota,
                'total_quota': quota.total_quota
            }
        
        # 配额不足30%
        elif usage_rate >= 0.7:
            return {
                'has_warning': True,
                'warning_level': 'medium',
                'message': f'配额剩余 {quota.remaining_quota} 次',
                'suggestion': '建议提前购买配额包',
                'remaining_quota': quota.remaining_quota,
                'total_quota': quota.total_quota
            }
        
        # 配额充足
        else:
            return {
                'has_warning': False,
                'warning_level': 'normal',
                'message': f'配额充足，剩余 {quota.remaining_quota} 次',
                'suggestion': '',
                'remaining_quota': quota.remaining_quota,
                'total_quota': quota.total_quota
            }

    @classmethod
    async def deduct_quota(
        cls,
        query_db: AsyncSession,
        deduct_data: DeductQuotaModel,
        auto_commit: bool = False
    ) -> CrudResponseModel:
        """
        扣减用户配额（不自动提交事务，由调用方控制）
        
        现在直接从会员表扣减配额，不再使用单独的配额表

        :param query_db: 数据库会话
        :param deduct_data: 扣减数据
        :param auto_commit: 是否自动提交（默认False，由调用方控制事务）
        :return: 操作结果
        """
        # 获取用户会员信息
        membership = await cls.get_user_membership(query_db, deduct_data.user_id)
        
        if not membership:
            raise ServiceException(
                message='您还未开通会员，请先购买会员套餐',
                code='MEMBERSHIP_NOT_FOUND'
            )
        
        # 检查会员是否过期
        if membership.end_date and membership.end_date < datetime.now():
            raise ServiceException(
                message=f'您的会员已于 {membership.end_date.strftime("%Y-%m-%d")} 过期，请续费',
                code='MEMBERSHIP_EXPIRED'
            )
        
        # 检查使用次数配额
        remaining_usage = membership.total_usage_quota - (membership.used_usage_quota or 0)
        if remaining_usage < deduct_data.amount:
            raise ServiceException(
                message=f'使用次数不足，当前剩余 {remaining_usage} 次，需要 {deduct_data.amount} 次',
                code='QUOTA_INSUFFICIENT'
            )

        try:
            # 扣减会员表中的使用次数
            await UserMembershipDao.update_quota_usage(
                query_db,
                membership.membership_id,
                word_count=0,  # 暂时不扣减字数
                usage_count=deduct_data.amount
            )

            # 记录使用记录（使用正确的字段名）
            record_data = {
                'user_id': deduct_data.user_id,
                'thesis_id': deduct_data.business_id if deduct_data.business_type in ['thesis_create', 'outline_generate', 'chapter_generate', 'chapter_batch_generate'] else None,
                'word_count': 0,  # 暂时不记录字数
                'usage_count': deduct_data.amount,
                'operation_type': 'generate',  # 生成操作
                'remark': f'{deduct_data.feature_type} - {deduct_data.business_type}'
            }
            await QuotaRecordDao.add_record(query_db, record_data)

            # 只有明确要求才自动提交
            if auto_commit:
                await query_db.commit()
            
            return CrudResponseModel(
                is_success=True,
                message='配额扣减成功',
                data={
                    'remaining_quota': remaining_usage - deduct_data.amount
                }
            )
        except ServiceException:
            # 重新抛出ServiceException
            if auto_commit:
                await query_db.rollback()
            raise
        except Exception as e:
            if auto_commit:
                await query_db.rollback()
            raise ServiceException(
                message='配额扣减失败，请稍后重试',
                code='DEDUCT_FAILED'
            )

    @classmethod
    async def add_quota(
        cls,
        query_db: AsyncSession,
        user_id: int,
        feature_type: str,
        amount: int,
        auto_commit: bool = False
    ) -> CrudResponseModel:
        """
        增加用户配额（不自动提交事务，由调用方控制）

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :param amount: 增加数量
        :param auto_commit: 是否自动提交（默认False，由调用方控制事务）
        :return: 操作结果
        """
        try:
            await UserFeatureQuotaDao.add_quota_amount(query_db, user_id, feature_type, amount)
            
            # 只有明确要求才自动提交
            if auto_commit:
                await query_db.commit()
            
            return CrudResponseModel(is_success=True, message='配额增加成功')
        except Exception as e:
            if auto_commit:
                await query_db.rollback()
            raise e

    @classmethod
    async def compensate_quota(
        cls,
        query_db: AsyncSession,
        user_id: int,
        feature_type: str,
        amount: int,
        reason: str,
        business_id: int = 0
    ) -> CrudResponseModel:
        """
        配额补偿（用于异常情况的补偿）

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :param amount: 补偿数量
        :param reason: 补偿原因
        :param business_id: 业务ID
        :return: 操作结果
        """
        try:
            # 增加配额
            await UserFeatureQuotaDao.add_quota_amount(
                query_db, user_id, feature_type, amount
            )
            
            # 记录补偿记录（使用负数表示补偿）
            record_data = {
                'user_id': user_id,
                'feature_type': feature_type,
                'quota_amount': -amount,  # 负数表示补偿
                'business_type': 'quota_compensation',
                'business_id': business_id,
                'use_time': datetime.now(),
                'remark': reason
            }
            await QuotaRecordDao.add_record(query_db, record_data)
            
            await query_db.commit()
            
            return CrudResponseModel(
                is_success=True,
                message=f'配额补偿成功，已返还 {amount} 次配额'
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'配额补偿失败: {str(e)}')

    # ==================== 配额使用记录 ====================

    @classmethod
    async def get_quota_record_list(
        cls,
        query_db: AsyncSession,
        query_object: QuotaRecordPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取配额使用记录列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 记录列表
        """
        return await QuotaRecordDao.get_record_list(query_db, query_object, is_page)

    @classmethod
    async def get_quota_statistics(
        cls,
        query_db: AsyncSession,
        user_id: int,
        feature_type: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> int:
        """
        获取配额使用统计

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 使用总量
        """
        return await QuotaRecordDao.get_usage_statistics(
            query_db, user_id, feature_type, start_time, end_time
        )


    # ==================== 用户会员详细管理 ====================

    @classmethod
    async def get_membership_detail(cls, query_db: AsyncSession, membership_id: int) -> UserMembershipModel:
        """
        获取用户会员详情

        :param query_db: 数据库会话
        :param membership_id: 会员ID
        :return: 会员详情
        """
        membership = await UserMembershipDao.get_membership_by_id(query_db, membership_id)
        if not membership:
            raise ServiceException(message='会员记录不存在')
        return UserMembershipModel(**CamelCaseUtil.transform_result(membership))

    @classmethod
    async def update_membership(
        cls,
        query_db: AsyncSession,
        membership_id: int,
        package_id: int
    ) -> CrudResponseModel:
        """
        更新用户会员

        :param query_db: 数据库会话
        :param membership_id: 会员ID
        :param package_id: 新套餐ID
        :return: 操作结果
        """
        try:
            # 获取现有会员记录
            membership = await UserMembershipDao.get_membership_by_id(query_db, membership_id)
            if not membership:
                raise ServiceException(message='会员记录不存在')
            
            # 获取新套餐信息
            package = await MemberPackageDao.get_package_by_id(query_db, package_id)
            if not package:
                raise ServiceException(message='套餐不存在')
            
            # 更新会员信息
            membership.package_id = package_id
            membership.update_time = datetime.now()
            
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_membership(cls, query_db: AsyncSession, membership_id: int) -> CrudResponseModel:
        """
        删除用户会员

        :param query_db: 数据库会话
        :param membership_id: 会员ID
        :return: 操作结果
        """
        try:
            membership = await UserMembershipDao.get_membership_by_id(query_db, membership_id)
            if not membership:
                raise ServiceException(message='会员记录不存在')
            
            # 软删除
            membership.del_flag = CommonConstant.DEL_FLAG_DELETED
            membership.update_time = datetime.now()
            
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def renew_membership(
        cls,
        query_db: AsyncSession,
        membership_id: int,
        duration: int
    ) -> CrudResponseModel:
        """
        续费会员

        :param query_db: 数据库会话
        :param membership_id: 会员ID
        :param duration: 续费天数
        :return: 操作结果
        """
        try:
            membership = await UserMembershipDao.get_membership_by_id(query_db, membership_id)
            if not membership:
                raise ServiceException(message='会员记录不存在')
            
            # 计算新的到期时间
            if membership.end_time and membership.end_time > datetime.now():
                # 如果还未过期，从当前到期时间延长
                new_end_time = membership.end_time + timedelta(days=duration)
            else:
                # 如果已过期，从现在开始计算
                new_end_time = datetime.now() + timedelta(days=duration)
            
            membership.end_time = new_end_time
            membership.update_time = datetime.now()
            
            await query_db.commit()
            return CrudResponseModel(is_success=True, message=f'续费成功，新到期时间：{new_end_time}')
        except Exception as e:
            await query_db.rollback()
            raise e
