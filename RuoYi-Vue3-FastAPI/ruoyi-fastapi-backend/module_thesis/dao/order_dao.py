"""
订单和支付相关DAO层
"""
from datetime import datetime
from typing import Any, Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_thesis.entity.do.order_do import AiWriteExportRecord, AiWriteFeatureService, AiWriteOrder
from utils.page_util import PageUtil


class OrderDao:
    """
    订单数据访问层
    """

    @classmethod
    async def add_order(cls, db: AsyncSession, order_data: dict) -> AiWriteOrder:
        """
        创建订单

        :param db: orm对象
        :param order_data: 订单数据字典
        :return: 订单对象
        """
        db_order = AiWriteOrder(**order_data)
        db.add(db_order)
        await db.flush()
        return db_order

    @classmethod
    async def get_order_by_id(cls, db: AsyncSession, order_id: int) -> Union[AiWriteOrder, None]:
        """
        根据订单ID获取订单信息

        :param db: orm对象
        :param order_id: 订单ID
        :return: 订单对象
        """
        order = (await db.execute(select(AiWriteOrder).where(AiWriteOrder.order_id == order_id))).scalars().first()
        return order

    @classmethod
    async def get_order_by_order_no(cls, db: AsyncSession, order_no: str) -> Union[AiWriteOrder, None]:
        """
        根据订单号获取订单信息

        :param db: orm对象
        :param order_no: 订单号
        :return: 订单对象
        """
        order = (await db.execute(select(AiWriteOrder).where(AiWriteOrder.order_no == order_no))).scalars().first()
        return order

    @classmethod
    async def get_order_list(
        cls,
        db: AsyncSession,
        user_id: int = None,
        status: str = None,
        page_num: int = 1,
        page_size: int = 10,
        is_page: bool = True,
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取订单列表（支持分页）

        :param db: orm对象
        :param user_id: 用户ID（可选）
        :param status: 订单状态（可选）
        :param page_num: 页码
        :param page_size: 每页数量
        :param is_page: 是否分页
        :return: 订单列表
        """
        query = (
            select(AiWriteOrder)
            .where(
                AiWriteOrder.user_id == user_id if user_id else True,
                AiWriteOrder.status == status if status else True,
            )
            .order_by(AiWriteOrder.create_time.desc())
        )

        order_list = await PageUtil.paginate(db, query, page_num, page_size, is_page)
        return order_list

    @classmethod
    async def update_order(cls, db: AsyncSession, order_data: dict) -> None:
        """
        更新订单信息

        :param db: orm对象
        :param order_data: 订单数据字典（必须包含order_id）
        :return:
        """
        await db.execute(update(AiWriteOrder), [order_data])

    @classmethod
    async def update_order_status(
        cls, db: AsyncSession, order_id: int, status: str, payment_time: datetime = None, transaction_id: str = None
    ) -> None:
        """
        更新订单状态

        :param db: orm对象
        :param order_id: 订单ID
        :param status: 订单状态
        :param payment_time: 支付时间（可选）
        :param transaction_id: 第三方交易号（可选）
        :return:
        """
        update_data = {'order_id': order_id, 'status': status, 'update_time': datetime.now()}
        if payment_time:
            update_data['payment_time'] = payment_time
        if transaction_id:
            update_data['transaction_id'] = transaction_id

        await db.execute(update(AiWriteOrder), [update_data])

    @classmethod
    async def get_order_statistics(
        cls, db: AsyncSession, user_id: int = None, start_date: datetime = None, end_date: datetime = None
    ) -> dict:
        """
        获取订单统计信息

        :param db: orm对象
        :param user_id: 用户ID（可选）
        :param start_date: 开始日期（可选）
        :param end_date: 结束日期（可选）
        :return: 统计信息字典
        """
        query = select(
            func.count(AiWriteOrder.order_id).label('total_count'),
            func.sum(AiWriteOrder.amount).label('total_amount'),
        ).where(
            AiWriteOrder.user_id == user_id if user_id else True,
            AiWriteOrder.create_time >= start_date if start_date else True,
            AiWriteOrder.create_time <= end_date if end_date else True,
        )

        result = (await db.execute(query)).first()
        return {'total_count': result.total_count or 0, 'total_amount': float(result.total_amount or 0)}


class FeatureServiceDao:
    """
    功能服务数据访问层
    """

    @classmethod
    async def add_service(cls, db: AsyncSession, service_data: dict) -> AiWriteFeatureService:
        """
        创建功能服务

        :param db: orm对象
        :param service_data: 服务数据字典
        :return: 服务对象
        """
        db_service = AiWriteFeatureService(**service_data)
        db.add(db_service)
        await db.flush()
        return db_service

    @classmethod
    async def get_service_by_id(cls, db: AsyncSession, service_id: int) -> Union[AiWriteFeatureService, None]:
        """
        根据服务ID获取服务信息

        :param db: orm对象
        :param service_id: 服务ID
        :return: 服务对象
        """
        service = (
            (
                await db.execute(
                    select(AiWriteFeatureService).where(
                        AiWriteFeatureService.service_id == service_id, AiWriteFeatureService.del_flag == '0'
                    )
                )
            )
            .scalars()
            .first()
        )
        return service

    @classmethod
    async def get_service_by_type(cls, db: AsyncSession, service_type: str) -> Union[AiWriteFeatureService, None]:
        """
        根据服务类型获取服务信息

        :param db: orm对象
        :param service_type: 服务类型
        :return: 服务对象
        """
        service = (
            (
                await db.execute(
                    select(AiWriteFeatureService).where(
                        AiWriteFeatureService.service_type == service_type,
                        AiWriteFeatureService.status == '0',
                        AiWriteFeatureService.del_flag == '0',
                    )
                )
            )
            .scalars()
            .first()
        )
        return service

    @classmethod
    async def get_service_list(
        cls,
        db: AsyncSession,
        status: str = None,
        page_num: int = 1,
        page_size: int = 10,
        is_page: bool = True,
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取功能服务列表（支持分页）

        :param db: orm对象
        :param status: 服务状态（可选）
        :param page_num: 页码
        :param page_size: 每页数量
        :param is_page: 是否分页
        :return: 服务列表
        """
        query = (
            select(AiWriteFeatureService)
            .where(
                AiWriteFeatureService.status == status if status else True,
                AiWriteFeatureService.del_flag == '0',
            )
            .order_by(AiWriteFeatureService.sort_order)
        )

        service_list = await PageUtil.paginate(db, query, page_num, page_size, is_page)
        return service_list

    @classmethod
    async def update_service(cls, db: AsyncSession, service_data: dict) -> None:
        """
        更新功能服务信息

        :param db: orm对象
        :param service_data: 服务数据字典（必须包含service_id）
        :return:
        """
        await db.execute(update(AiWriteFeatureService), [service_data])

    @classmethod
    async def delete_service(cls, db: AsyncSession, service_id: int) -> None:
        """
        删除功能服务（软删除）

        :param db: orm对象
        :param service_id: 服务ID
        :return:
        """
        await db.execute(
            update(AiWriteFeatureService).where(AiWriteFeatureService.service_id == service_id),
            [{'service_id': service_id, 'del_flag': '2', 'update_time': datetime.now()}],
        )


class ExportRecordDao:
    """
    导出记录数据访问层
    """

    @classmethod
    async def add_record(cls, db: AsyncSession, record_data: dict) -> AiWriteExportRecord:
        """
        创建导出记录

        :param db: orm对象
        :param record_data: 记录数据字典
        :return: 记录对象
        """
        db_record = AiWriteExportRecord(**record_data)
        db.add(db_record)
        await db.flush()
        return db_record

    @classmethod
    async def get_record_by_id(cls, db: AsyncSession, record_id: int) -> Union[AiWriteExportRecord, None]:
        """
        根据记录ID获取导出记录

        :param db: orm对象
        :param record_id: 记录ID
        :return: 记录对象
        """
        record = (
            (
                await db.execute(
                    select(AiWriteExportRecord).where(
                        AiWriteExportRecord.record_id == record_id, AiWriteExportRecord.del_flag == '0'
                    )
                )
            )
            .scalars()
            .first()
        )
        return record

    @classmethod
    async def get_record_list(
        cls,
        db: AsyncSession,
        user_id: int = None,
        thesis_id: int = None,
        page_num: int = 1,
        page_size: int = 10,
        is_page: bool = True,
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取导出记录列表（支持分页）

        :param db: orm对象
        :param user_id: 用户ID（可选）
        :param thesis_id: 论文ID（可选）
        :param page_num: 页码
        :param page_size: 每页数量
        :param is_page: 是否分页
        :return: 记录列表
        """
        query = (
            select(AiWriteExportRecord)
            .where(
                AiWriteExportRecord.user_id == user_id if user_id else True,
                AiWriteExportRecord.thesis_id == thesis_id if thesis_id else True,
                AiWriteExportRecord.del_flag == '0',
            )
            .order_by(AiWriteExportRecord.create_time.desc())
        )

        record_list = await PageUtil.paginate(db, query, page_num, page_size, is_page)
        return record_list

    @classmethod
    async def delete_record(cls, db: AsyncSession, record_id: int) -> None:
        """
        删除导出记录（软删除）

        :param db: orm对象
        :param record_id: 记录ID
        :return:
        """
        await db.execute(
            update(AiWriteExportRecord).where(AiWriteExportRecord.record_id == record_id),
            [{'record_id': record_id, 'del_flag': '2'}],
        )

    @classmethod
    async def get_user_export_count(cls, db: AsyncSession, user_id: int, thesis_id: int = None) -> int:
        """
        获取用户导出次数

        :param db: orm对象
        :param user_id: 用户ID
        :param thesis_id: 论文ID（可选）
        :return: 导出次数
        """
        query = select(func.count(AiWriteExportRecord.record_id)).where(
            AiWriteExportRecord.user_id == user_id,
            AiWriteExportRecord.thesis_id == thesis_id if thesis_id else True,
            AiWriteExportRecord.del_flag == '0',
        )

        count = (await db.execute(query)).scalar()
        return count or 0
