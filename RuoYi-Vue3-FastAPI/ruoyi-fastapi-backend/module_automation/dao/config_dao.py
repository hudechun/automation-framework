from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_automation.entity.do.config_do import ModelConfigDO
from module_automation.entity.vo.config_vo import ModelConfigPageQueryModel
from utils.page_util import PageUtil


class ModelConfigDao:
    """
    模型配置数据访问对象
    """

    @classmethod
    async def get_model_config_list(
        cls, db: AsyncSession, query_object: ModelConfigPageQueryModel, is_page: bool = False
    ):
        """
        获取模型配置列表
        """
        query = select(ModelConfigDO).order_by(ModelConfigDO.created_at.desc())

        # 配置名称筛选
        if query_object.name:
            query = query.where(ModelConfigDO.name.like(f'%{query_object.name}%'))
        # 提供商筛选
        if query_object.provider:
            query = query.where(ModelConfigDO.provider == query_object.provider)
        # 启用状态筛选
        if query_object.enabled is not None:
            query = query.where(ModelConfigDO.enabled == query_object.enabled)

        if is_page:
            model_config_list = await PageUtil.paginate(
                db, query, query_object.page_num, query_object.page_size, is_page
            )
        else:
            result = await db.execute(query)
            model_config_list = result.scalars().all()

        return model_config_list

    @classmethod
    async def get_model_config_detail_by_id(cls, db: AsyncSession, config_id: int):
        """
        根据ID获取模型配置详情
        """
        query = select(ModelConfigDO).where(ModelConfigDO.id == config_id)
        result = await db.execute(query)
        model_config = result.scalars().first()

        return model_config

    @classmethod
    async def add_model_config_dao(cls, db: AsyncSession, config_object: ModelConfigDO):
        """
        新增模型配置
        """
        db.add(config_object)
        await db.flush()

    @classmethod
    async def edit_model_config_dao(cls, db: AsyncSession, config_object: dict):
        """
        编辑模型配置
        """
        await db.execute(update(ModelConfigDO).where(ModelConfigDO.id == config_object.get('id')).values(**config_object))
        await db.flush()

    @classmethod
    async def delete_model_config_dao(cls, db: AsyncSession, config_object: ModelConfigDO):
        """
        删除模型配置
        """
        await db.delete(config_object)
        await db.flush()

    @classmethod
    async def get_model_config_by_id(cls, db: AsyncSession, config_id: int):
        """
        根据ID获取模型配置对象
        """
        query = select(ModelConfigDO).where(ModelConfigDO.id == config_id)
        result = await db.execute(query)
        model_config = result.scalars().first()

        return model_config

    @classmethod
    async def get_model_config_by_name(cls, db: AsyncSession, name: str):
        """
        根据名称获取模型配置对象
        """
        query = select(ModelConfigDO).where(ModelConfigDO.name == name)
        result = await db.execute(query)
        model_config = result.scalars().first()

        return model_config
