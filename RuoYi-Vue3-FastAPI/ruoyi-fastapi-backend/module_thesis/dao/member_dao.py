"""
会员管理模块数据库操作层
"""
from typing import Any, Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_thesis.entity.do.member_do import (
    AiWriteMemberPackage,
    AiWriteQuotaRecord,
    AiWriteUserFeatureQuota,
    AiWriteUserMembership,
)
from utils.page_util import PageUtil


class MemberPackageDao:
    """
    会员套餐数据访问对象
    """

    @classmethod
    async def get_package_by_id(cls, db: AsyncSession, package_id: int) -> Union[AiWriteMemberPackage, None]:
        """
        根据套餐ID获取套餐详情

        :param db: orm对象
        :param package_id: 套餐ID
        :return: 套餐信息对象
        """
        package_info = (
            await db.execute(
                select(AiWriteMemberPackage).where(
                    AiWriteMemberPackage.package_id == package_id, AiWriteMemberPackage.del_flag == '0'
                )
            )
        ).scalars().first()

        return package_info

    @classmethod
    async def get_package_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取套餐列表

        :param db: orm对象
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 套餐列表
        """
        query_object = query_object or {}
        query = (
            select(AiWriteMemberPackage)
            .where(
                AiWriteMemberPackage.status == query_object.get('status') if query_object.get('status') else True,
                AiWriteMemberPackage.del_flag == '0',
            )
            .order_by(AiWriteMemberPackage.sort_order, AiWriteMemberPackage.price)
        )

        package_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
        )

        return package_list

    @classmethod
    async def add_package(cls, db: AsyncSession, package_data: dict) -> AiWriteMemberPackage:
        """
        新增套餐

        :param db: orm对象
        :param package_data: 套餐数据
        :return: 套餐对象
        """
        db_package = AiWriteMemberPackage(**package_data)
        db.add(db_package)
        await db.flush()

        return db_package

    @classmethod
    async def update_package(cls, db: AsyncSession, package_data: dict) -> None:
        """
        更新套餐

        :param db: orm对象
        :param package_data: 套餐数据
        :return:
        """
        await db.execute(update(AiWriteMemberPackage), [package_data])

    @classmethod
    async def delete_package(cls, db: AsyncSession, package_id: int) -> None:
        """
        删除套餐（软删除）

        :param db: orm对象
        :param package_id: 套餐ID
        :return:
        """
        await db.execute(
            update(AiWriteMemberPackage)
            .where(AiWriteMemberPackage.package_id == package_id)
            .values(del_flag='2')
        )


class UserMembershipDao:
    """
    用户会员数据访问对象
    """

    @classmethod
    async def get_membership_by_user_id(cls, db: AsyncSession, user_id: int) -> Union[AiWriteUserMembership, None]:
        """
        根据用户ID获取有效会员信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 会员信息对象
        """
        membership_info = (
            await db.execute(
                select(AiWriteUserMembership).where(
                    AiWriteUserMembership.user_id == user_id,
                    AiWriteUserMembership.status == '0',
                    AiWriteUserMembership.del_flag == '0',
                )
            )
        ).scalars().first()

        return membership_info

    @classmethod
    async def get_membership_by_id(cls, db: AsyncSession, membership_id: int) -> Union[AiWriteUserMembership, None]:
        """
        根据会员ID获取会员详情

        :param db: orm对象
        :param membership_id: 会员ID
        :return: 会员信息对象
        """
        membership_info = (
            await db.execute(
                select(AiWriteUserMembership).where(
                    AiWriteUserMembership.membership_id == membership_id, AiWriteUserMembership.del_flag == '0'
                )
            )
        ).scalars().first()

        return membership_info

    @classmethod
    async def add_membership(cls, db: AsyncSession, membership_data: dict) -> AiWriteUserMembership:
        """
        新增用户会员

        :param db: orm对象
        :param membership_data: 会员数据
        :return: 会员对象
        """
        db_membership = AiWriteUserMembership(**membership_data)
        db.add(db_membership)
        await db.flush()

        return db_membership

    @classmethod
    async def update_membership(cls, db: AsyncSession, membership_data: dict) -> None:
        """
        更新用户会员

        :param db: orm对象
        :param membership_data: 会员数据
        :return:
        """
        await db.execute(update(AiWriteUserMembership), [membership_data])

    @classmethod
    async def update_quota_usage(
        cls, db: AsyncSession, membership_id: int, word_count: int, usage_count: int = 1
    ) -> None:
        """
        更新配额使用量

        :param db: orm对象
        :param membership_id: 会员ID
        :param word_count: 字数变动
        :param usage_count: 次数变动
        :return:
        """
        await db.execute(
            update(AiWriteUserMembership)
            .where(AiWriteUserMembership.membership_id == membership_id)
            .values(
                used_word_quota=AiWriteUserMembership.used_word_quota + word_count,
                used_usage_quota=AiWriteUserMembership.used_usage_quota + usage_count,
            )
        )


class UserFeatureQuotaDao:
    """
    用户功能配额数据访问对象
    """

    @classmethod
    async def get_quota_by_user_and_service(
        cls, db: AsyncSession, user_id: int, service_type: str
    ) -> Union[AiWriteUserFeatureQuota, None]:
        """
        根据用户ID和服务类型获取配额

        :param db: orm对象
        :param user_id: 用户ID
        :param service_type: 服务类型
        :return: 配额信息对象
        """
        quota_info = (
            await db.execute(
                select(AiWriteUserFeatureQuota).where(
                    AiWriteUserFeatureQuota.user_id == user_id,
                    AiWriteUserFeatureQuota.service_type == service_type,
                    AiWriteUserFeatureQuota.status == '0',
                    AiWriteUserFeatureQuota.del_flag == '0',
                )
            )
        ).scalars().first()

        return quota_info

    @classmethod
    async def get_quota_by_user_and_feature(
        cls, db: AsyncSession, user_id: int, feature_type: str
    ) -> Union[AiWriteUserFeatureQuota, None]:
        """
        根据用户ID和功能类型获取配额（别名方法）

        :param db: orm对象
        :param user_id: 用户ID
        :param feature_type: 功能类型（实际对应service_type字段）
        :return: 配额信息对象
        """
        return await cls.get_quota_by_user_and_service(db, user_id, feature_type)

    @classmethod
    async def get_quota_list_by_user(cls, db: AsyncSession, user_id: int) -> list[AiWriteUserFeatureQuota]:
        """
        获取用户所有功能配额

        :param db: orm对象
        :param user_id: 用户ID
        :return: 配额列表
        """
        quota_list = (
            await db.execute(
                select(AiWriteUserFeatureQuota).where(
                    AiWriteUserFeatureQuota.user_id == user_id, AiWriteUserFeatureQuota.del_flag == '0'
                )
            )
        ).scalars().all()

        return list(quota_list)

    @classmethod
    async def add_quota(cls, db: AsyncSession, quota_data: dict) -> AiWriteUserFeatureQuota:
        """
        新增功能配额

        :param db: orm对象
        :param quota_data: 配额数据
        :return: 配额对象
        """
        db_quota = AiWriteUserFeatureQuota(**quota_data)
        db.add(db_quota)
        await db.flush()

        return db_quota

    @classmethod
    async def update_quota(cls, db: AsyncSession, quota_data: dict) -> None:
        """
        更新功能配额

        :param db: orm对象
        :param quota_data: 配额数据
        :return:
        """
        await db.execute(update(AiWriteUserFeatureQuota), [quota_data])

    @classmethod
    async def update_quota_usage(cls, db: AsyncSession, quota_id: int, used_amount: int) -> None:
        """
        更新配额使用量

        :param db: orm对象
        :param quota_id: 配额ID
        :param used_amount: 使用量
        :return:
        """
        await db.execute(
            update(AiWriteUserFeatureQuota)
            .where(AiWriteUserFeatureQuota.quota_id == quota_id)
            .values(used_quota=AiWriteUserFeatureQuota.used_quota + used_amount)
        )

    @classmethod
    async def add_quota_amount(
        cls, db: AsyncSession, user_id: int, feature_type: str, amount: int
    ) -> None:
        """
        增加配额数量

        :param db: orm对象
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :param amount: 增加的配额数量
        :return:
        """
        await db.execute(
            update(AiWriteUserFeatureQuota)
            .where(
                AiWriteUserFeatureQuota.user_id == user_id,
                AiWriteUserFeatureQuota.service_type == feature_type,
            )
            .values(total_quota=AiWriteUserFeatureQuota.total_quota + amount)
        )

    @classmethod
    async def deduct_quota(
        cls, db: AsyncSession, user_id: int, feature_type: str, amount: int
    ) -> None:
        """
        扣减配额

        :param db: orm对象
        :param user_id: 用户ID
        :param feature_type: 功能类型
        :param amount: 扣减的配额数量
        :return:
        """
        await db.execute(
            update(AiWriteUserFeatureQuota)
            .where(
                AiWriteUserFeatureQuota.user_id == user_id,
                AiWriteUserFeatureQuota.service_type == feature_type,
            )
            .values(used_quota=AiWriteUserFeatureQuota.used_quota + amount)
        )

    @classmethod
    async def get_quota_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取配额列表

        :param db: orm对象
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 配额列表
        """
        query_object = query_object or {}
        query = select(AiWriteUserFeatureQuota).where(
            AiWriteUserFeatureQuota.user_id == query_object.get('user_id') if query_object.get('user_id') else True,
            AiWriteUserFeatureQuota.service_type == query_object.get('service_type')
            if query_object.get('service_type')
            else True,
            AiWriteUserFeatureQuota.status == query_object.get('status') if query_object.get('status') else True,
            AiWriteUserFeatureQuota.del_flag == '0',
        ).order_by(AiWriteUserFeatureQuota.create_time.desc())

        quota_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
        )

        return quota_list


class QuotaRecordDao:
    """
    配额使用记录数据访问对象
    """

    @classmethod
    async def add_record(cls, db: AsyncSession, record_data: dict) -> AiWriteQuotaRecord:
        """
        新增配额使用记录

        :param db: orm对象
        :param record_data: 记录数据
        :return: 记录对象
        """
        db_record = AiWriteQuotaRecord(**record_data)
        db.add(db_record)
        await db.flush()

        return db_record

    @classmethod
    async def get_record_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取配额使用记录列表

        :param db: orm对象
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 记录列表
        """
        query_object = query_object or {}
        query = select(AiWriteQuotaRecord).where(
            AiWriteQuotaRecord.user_id == query_object.get('user_id') if query_object.get('user_id') else True,
            AiWriteQuotaRecord.thesis_id == query_object.get('thesis_id') if query_object.get('thesis_id') else True,
            AiWriteQuotaRecord.operation_type == query_object.get('operation_type')
            if query_object.get('operation_type')
            else True,
        ).order_by(AiWriteQuotaRecord.create_time.desc())

        record_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
        )

        return record_list

    @classmethod
    async def get_user_total_usage(cls, db: AsyncSession, user_id: int) -> dict:
        """
        获取用户总使用量统计

        :param db: orm对象
        :param user_id: 用户ID
        :return: 统计数据
        """
        result = (
            await db.execute(
                select(
                    func.sum(AiWriteQuotaRecord.word_count).label('total_words'),
                    func.sum(AiWriteQuotaRecord.usage_count).label('total_usage'),
                ).where(AiWriteQuotaRecord.user_id == user_id, AiWriteQuotaRecord.operation_type == 'generate')
            )
        ).first()

        return {'total_words': result.total_words or 0, 'total_usage': result.total_usage or 0}
