"""
支付流水DAO
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from module_thesis.entity.do.payment_do import PaymentTransaction


class PaymentTransactionDao:
    """支付流水数据访问类"""

    @classmethod
    async def get_transaction_by_id(cls, db: AsyncSession, transaction_id: int) -> Optional[PaymentTransaction]:
        """
        根据ID获取流水

        :param db: 数据库会话
        :param transaction_id: 流水ID
        :return: 流水对象
        """
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.transaction_id == transaction_id,
                PaymentTransaction.del_flag == '0'
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_transaction_by_payment_id(cls, db: AsyncSession, payment_id: str) -> Optional[PaymentTransaction]:
        """
        根据支付ID获取流水

        :param db: 数据库会话
        :param payment_id: 支付ID
        :return: 流水对象
        """
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.payment_id == payment_id,
                PaymentTransaction.del_flag == '0'
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_transaction_by_order_no(cls, db: AsyncSession, order_no: str) -> Optional[PaymentTransaction]:
        """
        根据订单号获取流水

        :param db: 数据库会话
        :param order_no: 订单号
        :return: 流水对象
        """
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.order_no == order_no,
                PaymentTransaction.del_flag == '0'
            ).order_by(PaymentTransaction.create_time.desc())
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_transactions_by_order_id(cls, db: AsyncSession, order_id: int) -> List[PaymentTransaction]:
        """
        根据订单ID获取所有流水

        :param db: 数据库会话
        :param order_id: 订单ID
        :return: 流水列表
        """
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.order_id == order_id,
                PaymentTransaction.del_flag == '0'
            ).order_by(PaymentTransaction.create_time.desc())
        )
        return result.scalars().all()

    @classmethod
    async def add_transaction(cls, db: AsyncSession, transaction_data: dict) -> PaymentTransaction:
        """
        添加流水记录

        :param db: 数据库会话
        :param transaction_data: 流水数据
        :return: 新流水对象
        """
        new_transaction = PaymentTransaction(**transaction_data)
        db.add(new_transaction)
        await db.flush()
        await db.refresh(new_transaction)
        return new_transaction

    @classmethod
    async def update_transaction(cls, db: AsyncSession, transaction_id: int, transaction_data: dict):
        """
        更新流水记录

        :param db: 数据库会话
        :param transaction_id: 流水ID
        :param transaction_data: 流水数据
        """
        await db.execute(
            update(PaymentTransaction)
            .where(PaymentTransaction.transaction_id == transaction_id)
            .values(**transaction_data)
        )
        await db.flush()

    @classmethod
    async def update_transaction_status(
        cls,
        db: AsyncSession,
        payment_id: str,
        status: str,
        transaction_no: str = None,
        payment_time: datetime = None
    ):
        """
        更新流水状态

        :param db: 数据库会话
        :param payment_id: 支付ID
        :param status: 状态
        :param transaction_no: 第三方交易号
        :param payment_time: 支付时间
        """
        update_data = {'status': status, 'update_time': datetime.now()}
        if transaction_no:
            update_data['transaction_no'] = transaction_no
        if payment_time:
            update_data['payment_time'] = payment_time

        await db.execute(
            update(PaymentTransaction)
            .where(PaymentTransaction.payment_id == payment_id)
            .values(**update_data)
        )
        await db.flush()

    @classmethod
    async def get_transaction_list(
        cls,
        db: AsyncSession,
        order_id: int = None,
        status: str = None,
        provider_type: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> tuple:
        """
        获取流水列表（分页）

        :param db: 数据库会话
        :param order_id: 订单ID
        :param status: 状态
        :param provider_type: 提供商类型
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param page_num: 页码
        :param page_size: 每页数量
        :return: (流水列表, 总数)
        """
        query = select(PaymentTransaction).where(PaymentTransaction.del_flag == '0')

        if order_id:
            query = query.where(PaymentTransaction.order_id == order_id)
        if status:
            query = query.where(PaymentTransaction.status == status)
        if provider_type:
            query = query.where(PaymentTransaction.provider_type == provider_type)
        if start_time:
            query = query.where(PaymentTransaction.create_time >= start_time)
        if end_time:
            query = query.where(PaymentTransaction.create_time <= end_time)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        # 分页查询
        query = query.order_by(PaymentTransaction.create_time.desc())
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        result = await db.execute(query)

        return result.scalars().all(), total

    @classmethod
    async def get_transaction_statistics(
        cls,
        db: AsyncSession,
        start_time: datetime = None,
        end_time: datetime = None,
        provider_type: str = None
    ) -> dict:
        """
        获取流水统计

        :param db: 数据库会话
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param provider_type: 提供商类型
        :return: 统计信息
        """
        query = select(
            func.count(PaymentTransaction.transaction_id).label('total_count'),
            func.sum(PaymentTransaction.amount).label('total_amount'),
            func.sum(PaymentTransaction.fee_amount).label('total_fee')
        ).where(
            PaymentTransaction.del_flag == '0',
            PaymentTransaction.status == 'success'
        )

        if start_time:
            query = query.where(PaymentTransaction.payment_time >= start_time)
        if end_time:
            query = query.where(PaymentTransaction.payment_time <= end_time)
        if provider_type:
            query = query.where(PaymentTransaction.provider_type == provider_type)

        result = await db.execute(query)
        row = result.first()

        return {
            'total_count': row.total_count or 0,
            'total_amount': float(row.total_amount or 0),
            'total_fee': float(row.total_fee or 0)
        }

    @classmethod
    async def delete_transaction(cls, db: AsyncSession, transaction_id: int):
        """
        删除流水（软删除）

        :param db: 数据库会话
        :param transaction_id: 流水ID
        """
        await db.execute(
            update(PaymentTransaction)
            .where(PaymentTransaction.transaction_id == transaction_id)
            .values(del_flag='2')
        )
        await db.flush()
