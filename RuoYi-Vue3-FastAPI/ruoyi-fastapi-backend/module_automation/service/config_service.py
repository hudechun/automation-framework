from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from module_automation.dao.config_dao import ModelConfigDao
from module_automation.entity.do.config_do import ModelConfigDO
from module_automation.entity.vo.config_vo import DeleteModelConfigModel, ModelConfigModel, ModelConfigPageQueryModel


class ModelConfigService:
    """
    模型配置服务类
    """

    @classmethod
    async def get_model_config_list_services(
        cls, query_db: AsyncSession, query_object: ModelConfigPageQueryModel, is_page: bool = False
    ):
        """
        获取模型配置列表
        """
        model_config_list_result = await ModelConfigDao.get_model_config_list(query_db, query_object, is_page)

        return model_config_list_result

    @classmethod
    async def model_config_detail_services(cls, query_db: AsyncSession, config_id: int):
        """
        获取模型配置详情
        """
        model_config = await ModelConfigDao.get_model_config_detail_by_id(query_db, config_id)
        if model_config:
            result = ModelConfigModel(**model_config.__dict__)
        else:
            result = ModelConfigModel()

        return result

    @classmethod
    async def add_model_config_services(cls, query_db: AsyncSession, add_object: ModelConfigModel):
        """
        新增模型配置
        """
        # 检查配置名称是否已存在
        existing_config = await ModelConfigDao.get_model_config_by_name(query_db, add_object.name)
        if existing_config:
            return CrudResponseModel(is_success=False, message='配置名称已存在')

        add_model_config = ModelConfigDO(**add_object.model_dump())
        await ModelConfigDao.add_model_config_dao(query_db, add_model_config)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_model_config_services(cls, query_db: AsyncSession, edit_object: ModelConfigModel):
        """
        编辑模型配置
        """
        edit_model_config = edit_object.model_dump(exclude_unset=True)
        await ModelConfigDao.edit_model_config_dao(query_db, edit_model_config)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='更新成功')

    @classmethod
    async def delete_model_config_services(cls, query_db: AsyncSession, delete_object: DeleteModelConfigModel):
        """
        删除模型配置
        """
        if delete_object.config_ids:
            config_id_list = delete_object.config_ids.split(',')
            for config_id in config_id_list:
                model_config = await ModelConfigDao.get_model_config_by_id(query_db, int(config_id))
                if model_config:
                    await ModelConfigDao.delete_model_config_dao(query_db, model_config)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')

        return CrudResponseModel(is_success=False, message='传入配置ID为空')
