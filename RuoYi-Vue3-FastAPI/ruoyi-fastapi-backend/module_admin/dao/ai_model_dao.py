"""
系统AI模型配置DAO
"""
from typing import Any, Optional

from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_admin.entity.do.ai_model_do import AiModelConfig
from utils.page_util import PageUtil


class AiModelConfigDao:
    """
    AI模型配置数据访问对象
    """

    @classmethod
    async def get_config_list(
        cls, query_db: AsyncSession, query_object: dict[str, Any], is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取AI模型配置列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 配置列表
        """
        query = select(AiModelConfig).where(AiModelConfig.del_flag == '0')

        # 条件过滤
        if query_object.get('model_name'):
            query = query.where(AiModelConfig.model_name.like(f"%{query_object['model_name']}%"))
        if query_object.get('model_type'):
            query = query.where(AiModelConfig.model_type == query_object['model_type'])
        if query_object.get('provider'):
            query = query.where(AiModelConfig.provider == query_object['provider'])
        if query_object.get('is_enabled'):
            query = query.where(AiModelConfig.is_enabled == query_object['is_enabled'])
        if query_object.get('status'):
            query = query.where(AiModelConfig.status == query_object['status'])

        # 排序
        query = query.order_by(desc(AiModelConfig.priority), desc(AiModelConfig.create_time))

        if is_page:
            return await PageUtil.paginate(
                query_db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
            )
        else:
            result = await query_db.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_config_by_id(cls, query_db: AsyncSession, config_id: int) -> Optional[AiModelConfig]:
        """
        根据ID获取配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :return: 配置对象
        """
        query = select(AiModelConfig).where(
            and_(AiModelConfig.config_id == config_id, AiModelConfig.del_flag == '0')
        )
        result = await query_db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_config_by_code(cls, query_db: AsyncSession, model_code: str, model_type: str = 'language') -> Optional[AiModelConfig]:
        """
        根据模型代码获取配置

        :param query_db: 数据库会话
        :param model_code: 模型代码
        :param model_type: 模型类型
        :return: 配置对象
        """
        query = select(AiModelConfig).where(
            and_(
                AiModelConfig.model_code == model_code,
                AiModelConfig.model_type == model_type,
                AiModelConfig.del_flag == '0'
            )
        )
        result = await query_db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_default_config(cls, query_db: AsyncSession, model_type: str = 'language') -> Optional[AiModelConfig]:
        """
        获取默认配置

        :param query_db: 数据库会话
        :param model_type: 模型类型
        :return: 默认配置对象
        """
        query = select(AiModelConfig).where(
            and_(
                AiModelConfig.is_default == '1',
                AiModelConfig.model_type == model_type,
                AiModelConfig.is_enabled == '1',
                AiModelConfig.del_flag == '0'
            )
        )
        result = await query_db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_enabled_configs(cls, query_db: AsyncSession, model_type: Optional[str] = None) -> list[AiModelConfig]:
        """
        获取所有启用的配置

        :param query_db: 数据库会话
        :param model_type: 模型类型（可选）
        :return: 配置列表
        """
        query = select(AiModelConfig).where(
            and_(AiModelConfig.is_enabled == '1', AiModelConfig.del_flag == '0')
        )
        
        if model_type:
            query = query.where(AiModelConfig.model_type == model_type)
        
        query = query.order_by(desc(AiModelConfig.priority))
        result = await query_db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_preset_models(
        cls, query_db: AsyncSession, model_type: Optional[str] = None, provider: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        获取预设模型列表（用于下拉选择）

        :param query_db: 数据库会话
        :param model_type: 模型类型
        :param provider: 提供商
        :return: 预设模型列表
        """
        query = select(AiModelConfig).where(
            and_(AiModelConfig.is_preset == '1', AiModelConfig.del_flag == '0')
        )

        if model_type:
            query = query.where(AiModelConfig.model_type == model_type)
        if provider:
            query = query.where(AiModelConfig.provider == provider)

        query = query.order_by(desc(AiModelConfig.priority))
        result = await query_db.execute(query)
        configs = result.scalars().all()

        # 转换为字典列表
        return [
            {
                'model_code': config.model_code,
                'model_name': config.model_name,
                'model_type': config.model_type,
                'provider': config.provider,
                'api_endpoint': config.api_endpoint,
                'model_version': config.model_version,
                'params': config.params,
                'capabilities': config.capabilities,
                'remark': config.remark,
            }
            for config in configs
        ]

    @classmethod
    async def add_config(cls, query_db: AsyncSession, config_data: dict[str, Any]) -> None:
        """
        新增配置

        :param query_db: 数据库会话
        :param config_data: 配置数据
        """
        new_config = AiModelConfig(**config_data)
        query_db.add(new_config)
        await query_db.flush()

    @classmethod
    async def update_config(cls, query_db: AsyncSession, config_id: int, config_data: dict[str, Any]) -> None:
        """
        更新配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :param config_data: 配置数据
        """
        # 确保只使用 DO 模型中存在的字段，避免 "Unconsumed column names" 错误
        do_model_fields = {field.name for field in AiModelConfig.__table__.columns}
        filtered_config_data = {k: v for k, v in config_data.items() if k in do_model_fields}
        
        if not filtered_config_data:
            return  # 没有需要更新的字段
        
        query = (
            update(AiModelConfig)
            .where(and_(AiModelConfig.config_id == config_id, AiModelConfig.del_flag == '0'))
            .values(**filtered_config_data)
        )
        await query_db.execute(query)

    @classmethod
    async def delete_config(cls, query_db: AsyncSession, config_id: int) -> None:
        """
        删除配置（软删除）

        :param query_db: 数据库会话
        :param config_id: 配置ID
        """
        query = (
            update(AiModelConfig)
            .where(AiModelConfig.config_id == config_id)
            .values(del_flag='2')
        )
        await query_db.execute(query)

    @classmethod
    async def enable_config(cls, query_db: AsyncSession, config_id: int) -> None:
        """
        启用配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        """
        query = (
            update(AiModelConfig)
            .where(and_(AiModelConfig.config_id == config_id, AiModelConfig.del_flag == '0'))
            .values(is_enabled='1')
        )
        await query_db.execute(query)

    @classmethod
    async def disable_config(cls, query_db: AsyncSession, config_id: int) -> None:
        """
        禁用配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        """
        query = (
            update(AiModelConfig)
            .where(and_(AiModelConfig.config_id == config_id, AiModelConfig.del_flag == '0'))
            .values(is_enabled='0')
        )
        await query_db.execute(query)

    @classmethod
    async def clear_default_config(cls, query_db: AsyncSession, model_type: str = 'language') -> None:
        """
        清除默认配置

        :param query_db: 数据库会话
        :param model_type: 模型类型
        """
        query = (
            update(AiModelConfig)
            .where(and_(AiModelConfig.model_type == model_type, AiModelConfig.del_flag == '0'))
            .values(is_default='0')
        )
        await query_db.execute(query)

    @classmethod
    async def set_default_config(cls, query_db: AsyncSession, config_id: int) -> None:
        """
        设置默认配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        """
        # 先获取配置的模型类型
        config = await cls.get_config_by_id(query_db, config_id)
        if config:
            # 清除同类型的默认配置
            await cls.clear_default_config(query_db, config.model_type)
            
            # 设置新的默认配置
            query = (
                update(AiModelConfig)
                .where(and_(AiModelConfig.config_id == config_id, AiModelConfig.del_flag == '0'))
                .values(is_default='1')
            )
            await query_db.execute(query)

    @classmethod
    async def get_models_by_type(cls, query_db: AsyncSession, model_type: str) -> list[AiModelConfig]:
        """
        根据类型获取模型列表

        :param query_db: 数据库会话
        :param model_type: 模型类型
        :return: 模型列表
        """
        query = select(AiModelConfig).where(
            and_(
                AiModelConfig.model_type == model_type,
                AiModelConfig.is_enabled == '1',
                AiModelConfig.del_flag == '0'
            )
        ).order_by(desc(AiModelConfig.priority))
        
        result = await query_db.execute(query)
        return result.scalars().all()
