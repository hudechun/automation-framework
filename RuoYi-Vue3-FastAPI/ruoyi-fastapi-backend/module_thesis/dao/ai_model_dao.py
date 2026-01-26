"""
AI模型配置数据库操作层
"""
from typing import Any, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
# 使用 module_admin 中的 AiModelConfig，避免重复定义
from module_admin.entity.do.ai_model_do import AiModelConfig as AiWriteAiModelConfig
from utils.page_util import PageUtil


class AiModelConfigDao:
    """
    AI模型配置数据访问对象
    """

    @classmethod
    async def get_config_by_id(cls, db: AsyncSession, config_id: int) -> Union[AiWriteAiModelConfig, None]:
        """
        根据配置ID获取模型配置详情

        :param db: orm对象
        :param config_id: 配置ID
        :return: 模型配置信息对象
        """
        config_info = (
            await db.execute(
                select(AiWriteAiModelConfig).where(
                    AiWriteAiModelConfig.config_id == config_id, AiWriteAiModelConfig.del_flag == '0'
                )
            )
        ).scalars().first()

        return config_info

    @classmethod
    async def get_config_by_code(cls, db: AsyncSession, model_code: str) -> Union[AiWriteAiModelConfig, None]:
        """
        根据模型代码获取模型配置

        :param db: orm对象
        :param model_code: 模型代码
        :return: 模型配置信息对象
        """
        config_info = (
            await db.execute(
                select(AiWriteAiModelConfig).where(
                    AiWriteAiModelConfig.model_code == model_code,
                    AiWriteAiModelConfig.is_enabled == '1',
                    AiWriteAiModelConfig.status == '0',
                    AiWriteAiModelConfig.del_flag == '0',
                )
            )
        ).scalars().first()

        return config_info

    @classmethod
    async def get_default_config(cls, db: AsyncSession, model_type: str = 'language') -> Union[AiWriteAiModelConfig, None]:
        """
        获取默认模型配置

        :param db: orm对象
        :param model_type: 模型类型（language/vision）
        :return: 默认模型配置信息对象
        """
        config_info = (
            await db.execute(
                select(AiWriteAiModelConfig)
                .where(
                    AiWriteAiModelConfig.model_type == model_type,
                    AiWriteAiModelConfig.is_default == '1',
                    AiWriteAiModelConfig.is_enabled == '1',
                    AiWriteAiModelConfig.status == '0',
                    AiWriteAiModelConfig.del_flag == '0',
                )
                .order_by(AiWriteAiModelConfig.priority.desc())
            )
        ).scalars().first()

        return config_info

    @classmethod
    async def get_enabled_configs(cls, db: AsyncSession) -> list[AiWriteAiModelConfig]:
        """
        获取所有启用的模型配置

        :param db: orm对象
        :return: 模型配置列表
        """
        configs = (
            await db.execute(
                select(AiWriteAiModelConfig)
                .where(
                    AiWriteAiModelConfig.is_enabled == '1',
                    AiWriteAiModelConfig.status == '0',
                    AiWriteAiModelConfig.del_flag == '0',
                )
                .order_by(AiWriteAiModelConfig.priority.desc(), AiWriteAiModelConfig.config_id)
            )
        ).scalars().all()

        return list(configs)

    @classmethod
    async def get_config_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取模型配置列表

        :param db: orm对象
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 模型配置列表
        """
        query_object = query_object or {}
        query = (
            select(AiWriteAiModelConfig)
            .where(
                AiWriteAiModelConfig.model_name.like(f'%{query_object.get("model_name")}%')
                if query_object.get('model_name')
                else True,
                AiWriteAiModelConfig.model_code == query_object.get('model_code')
                if query_object.get('model_code')
                else True,
                AiWriteAiModelConfig.is_enabled == query_object.get('is_enabled')
                if query_object.get('is_enabled')
                else True,
                AiWriteAiModelConfig.is_default == query_object.get('is_default')
                if query_object.get('is_default')
                else True,
                AiWriteAiModelConfig.status == query_object.get('status') if query_object.get('status') else True,
                AiWriteAiModelConfig.del_flag == '0',
            )
            .order_by(
                AiWriteAiModelConfig.is_default.desc(),
                AiWriteAiModelConfig.priority.desc(),
                AiWriteAiModelConfig.config_id,
            )
        )

        config_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
        )

        return config_list

    @classmethod
    async def add_config(cls, db: AsyncSession, config_data: dict) -> AiWriteAiModelConfig:
        """
        新增模型配置

        :param db: orm对象
        :param config_data: 模型配置数据
        :return: 模型配置对象
        """
        db_config = AiWriteAiModelConfig(**config_data)
        db.add(db_config)
        await db.flush()

        return db_config

    @classmethod
    async def update_config(cls, db: AsyncSession, config_id: int, config_data: dict) -> None:
        """
        更新模型配置

        :param db: orm对象
        :param config_id: 配置ID
        :param config_data: 模型配置数据
        :return:
        """
        # 确保只使用 DO 模型中存在的字段，避免 "Unconsumed column names" 错误
        do_model_fields = {field.name for field in AiWriteAiModelConfig.__table__.columns}
        filtered_config_data = {k: v for k, v in config_data.items() if k in do_model_fields}
        
        if not filtered_config_data:
            return  # 没有需要更新的字段
        
        await db.execute(
            update(AiWriteAiModelConfig).where(AiWriteAiModelConfig.config_id == config_id).values(**filtered_config_data)
        )

    @classmethod
    async def delete_config(cls, db: AsyncSession, config_id: int) -> None:
        """
        删除模型配置（软删除）

        :param db: orm对象
        :param config_id: 配置ID
        :return:
        """
        await db.execute(
            update(AiWriteAiModelConfig).where(AiWriteAiModelConfig.config_id == config_id).values(del_flag='2')
        )

    @classmethod
    async def enable_config(cls, db: AsyncSession, config_id: int) -> None:
        """
        启用模型配置

        :param db: orm对象
        :param config_id: 配置ID
        :return:
        """
        await db.execute(
            update(AiWriteAiModelConfig).where(AiWriteAiModelConfig.config_id == config_id).values(is_enabled='1')
        )

    @classmethod
    async def disable_config(cls, db: AsyncSession, config_id: int) -> None:
        """
        禁用模型配置

        :param db: orm对象
        :param config_id: 配置ID
        :return:
        """
        await db.execute(
            update(AiWriteAiModelConfig).where(AiWriteAiModelConfig.config_id == config_id).values(is_enabled='0')
        )

    @classmethod
    async def set_default_config(cls, db: AsyncSession, config_id: int) -> None:
        """
        设置默认模型配置

        :param db: orm对象
        :param config_id: 配置ID
        :return:
        """
        # 先取消所有默认配置
        await db.execute(update(AiWriteAiModelConfig).values(is_default='0'))

        # 设置指定配置为默认
        await db.execute(
            update(AiWriteAiModelConfig).where(AiWriteAiModelConfig.config_id == config_id).values(is_default='1')
        )

    @classmethod
    async def clear_default_config(cls, db: AsyncSession) -> None:
        """
        清除所有默认配置

        :param db: orm对象
        :return:
        """
        await db.execute(update(AiWriteAiModelConfig).values(is_default='0'))
