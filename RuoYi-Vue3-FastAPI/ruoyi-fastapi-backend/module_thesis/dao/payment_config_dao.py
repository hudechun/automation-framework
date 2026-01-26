"""
支付配置DAO
"""
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from module_thesis.entity.do.payment_do import PaymentConfig


class PaymentConfigDao:
    """支付配置数据访问类"""

    @classmethod
    async def get_config_by_id(cls, db: AsyncSession, config_id: int) -> Optional[PaymentConfig]:
        """
        根据ID获取配置

        :param db: 数据库会话
        :param config_id: 配置ID
        :return: 配置对象
        """
        result = await db.execute(
            select(PaymentConfig).where(
                PaymentConfig.config_id == config_id,
                PaymentConfig.del_flag == '0'
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_config_by_type(cls, db: AsyncSession, provider_type: str) -> Optional[PaymentConfig]:
        """
        根据提供商类型获取配置

        :param db: 数据库会话
        :param provider_type: 提供商类型
        :return: 配置对象
        """
        result = await db.execute(
            select(PaymentConfig).where(
                PaymentConfig.provider_type == provider_type,
                PaymentConfig.del_flag == '0'
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_enabled_configs(cls, db: AsyncSession) -> List[PaymentConfig]:
        """
        获取所有启用的配置

        :param db: 数据库会话
        :return: 配置列表
        """
        result = await db.execute(
            select(PaymentConfig).where(
                PaymentConfig.is_enabled == '1',
                PaymentConfig.status == '0',
                PaymentConfig.del_flag == '0'
            ).order_by(PaymentConfig.priority.desc())
        )
        return result.scalars().all()

    @classmethod
    async def get_all_configs(cls, db: AsyncSession) -> List[PaymentConfig]:
        """
        获取所有配置

        :param db: 数据库会话
        :return: 配置列表
        """
        result = await db.execute(
            select(PaymentConfig).where(
                PaymentConfig.del_flag == '0'
            ).order_by(PaymentConfig.priority.desc())
        )
        return result.scalars().all()

    @classmethod
    async def add_config(cls, db: AsyncSession, config_data: dict) -> PaymentConfig:
        """
        添加配置

        :param db: 数据库会话
        :param config_data: 配置数据
        :return: 新配置对象
        """
        new_config = PaymentConfig(**config_data)
        db.add(new_config)
        await db.flush()
        await db.refresh(new_config)
        return new_config

    @classmethod
    async def update_config(cls, db: AsyncSession, config_id: int, config_data: dict):
        """
        更新配置

        :param db: 数据库会话
        :param config_id: 配置ID
        :param config_data: 配置数据
        """
        await db.execute(
            update(PaymentConfig)
            .where(PaymentConfig.config_id == config_id)
            .values(**config_data)
        )
        await db.flush()

    @classmethod
    async def update_status(cls, db: AsyncSession, config_id: int, is_enabled: str):
        """
        更新启用状态

        :param db: 数据库会话
        :param config_id: 配置ID
        :param is_enabled: 是否启用
        """
        await db.execute(
            update(PaymentConfig)
            .where(PaymentConfig.config_id == config_id)
            .values(is_enabled=is_enabled)
        )
        await db.flush()

    @classmethod
    async def delete_config(cls, db: AsyncSession, config_id: int):
        """
        删除配置（软删除）

        :param db: 数据库会话
        :param config_id: 配置ID
        """
        await db.execute(
            update(PaymentConfig)
            .where(PaymentConfig.config_id == config_id)
            .values(del_flag='2')
        )
        await db.flush()
