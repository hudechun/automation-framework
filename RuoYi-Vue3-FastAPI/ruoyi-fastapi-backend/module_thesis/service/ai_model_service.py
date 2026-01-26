"""
AI模型配置服务层
"""
import time
from typing import Any, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao.ai_model_dao import AiModelConfigDao
from module_thesis.entity.vo.ai_model_vo import (
    AiModelConfigModel,
    AiModelConfigPageQueryModel,
    AiModelTestResponseModel,
)
from utils.common_util import CamelCaseUtil


class AiModelService:
    """
    AI模型配置服务类
    """

    @classmethod
    async def get_config_list(
        cls, query_db: AsyncSession, query_object: AiModelConfigPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取AI模型配置列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 配置列表
        """
        return await AiModelConfigDao.get_config_list(query_db, query_object.model_dump(), is_page)

    @classmethod
    async def get_config_detail(cls, query_db: AsyncSession, config_id: int) -> AiModelConfigModel:
        """
        获取AI模型配置详情

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :return: 配置详情
        """
        config = await AiModelConfigDao.get_config_by_id(query_db, config_id)
        if not config:
            raise ServiceException(message='AI模型配置不存在')
        return AiModelConfigModel(**CamelCaseUtil.transform_result(config))

    @classmethod
    async def get_default_config(cls, query_db: AsyncSession, model_type: str = 'language') -> Union[AiModelConfigModel, None]:
        """
        获取默认AI模型配置

        :param query_db: 数据库会话
        :param model_type: 模型类型（language/vision）
        :return: 默认配置
        """
        config = await AiModelConfigDao.get_default_config(query_db, model_type)
        if config:
            return AiModelConfigModel(**CamelCaseUtil.transform_result(config))
        return None

    @classmethod
    async def get_enabled_configs(cls, query_db: AsyncSession) -> list[AiModelConfigModel]:
        """
        获取所有启用的AI模型配置

        :param query_db: 数据库会话
        :return: 启用的配置列表
        """
        configs = await AiModelConfigDao.get_enabled_configs(query_db)
        return [AiModelConfigModel(**CamelCaseUtil.transform_result(config)) for config in configs]

    @classmethod
    async def add_config(cls, query_db: AsyncSession, config_data: AiModelConfigModel) -> CrudResponseModel:
        """
        新增AI模型配置

        :param query_db: 数据库会话
        :param config_data: 配置数据
        :return: 操作结果
        """
        try:
            # 检查模型代码是否已存在
            existing_config = await AiModelConfigDao.get_config_by_code(query_db, config_data.model_code)
            if existing_config:
                raise ServiceException(message=f'模型代码 {config_data.model_code} 已存在')

            await AiModelConfigDao.add_config(query_db, config_data.model_dump(exclude_none=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except ServiceException:
            await query_db.rollback()
            raise
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_config(cls, query_db: AsyncSession, config_data: AiModelConfigModel) -> CrudResponseModel:
        """
        更新AI模型配置

        :param query_db: 数据库会话
        :param config_data: 配置数据
        :return: 操作结果
        """
        # 检查配置是否存在
        await cls.get_config_detail(query_db, config_data.config_id)

        try:
            # 使用 by_alias=False 获取原始字段名（snake_case），而不是 camelCase
            # 因为 DO 模型使用 snake_case 字段名
            update_data = config_data.model_dump(exclude_unset=True, exclude={'config_id'}, by_alias=False)
            
            # 获取DO模型的所有字段名，过滤掉不存在的字段
            # 使用 module_admin 的 DO 模型，与 DAO 层保持一致，避免重复定义表
            from module_admin.entity.do.ai_model_do import AiModelConfig
            do_model_fields = {field.name for field in AiModelConfig.__table__.columns}
            
            # 只保留 DO 模型中存在的字段
            filtered_data = {k: v for k, v in update_data.items() if k in do_model_fields}
            
            if filtered_data:
                await AiModelConfigDao.update_config(query_db, config_data.config_id, filtered_data)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            else:
                return CrudResponseModel(is_success=True, message='没有需要更新的字段')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_config(cls, query_db: AsyncSession, config_id: int) -> CrudResponseModel:
        """
        删除AI模型配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :return: 操作结果
        """
        # 检查配置是否存在
        config = await cls.get_config_detail(query_db, config_id)

        # 检查是否为预设模型
        if config.is_preset == '1':
            raise ServiceException(message='预设模型不能删除，只能禁用')

        try:
            await AiModelConfigDao.delete_config(query_db, config_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')

    @classmethod
    async def enable_config(cls, query_db: AsyncSession, config_id: int) -> CrudResponseModel:
        """
        启用AI模型配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :return: 操作结果
        """
        # 检查配置是否存在
        await cls.get_config_detail(query_db, config_id)

        try:
            await AiModelConfigDao.enable_config(query_db, config_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='启用成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'启用失败: {str(e)}')

    @classmethod
    async def disable_config(cls, query_db: AsyncSession, config_id: int) -> CrudResponseModel:
        """
        禁用AI模型配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :return: 操作结果
        """
        # 检查配置是否存在
        config = await cls.get_config_detail(query_db, config_id)

        # 如果是默认配置，先取消默认
        if config.is_default == '1':
            await AiModelConfigDao.clear_default_config(query_db)

        try:
            await AiModelConfigDao.disable_config(query_db, config_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='禁用成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'禁用失败: {str(e)}')

    @classmethod
    async def set_default_config(cls, query_db: AsyncSession, config_id: int) -> CrudResponseModel:
        """
        设置默认AI模型配置

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :return: 操作结果
        """
        # 检查配置是否存在
        config = await cls.get_config_detail(query_db, config_id)

        # 检查配置是否启用
        if config.is_enabled != '1':
            raise ServiceException(message='只能将启用的模型设为默认')

        try:
            await AiModelConfigDao.set_default_config(query_db, config_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='设置默认成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'设置默认失败: {str(e)}')

    @classmethod
    async def test_config(cls, query_db: AsyncSession, config_id: int, test_prompt: str = '你好') -> AiModelTestResponseModel:
        """
        测试AI模型配置连接
        
        注意：此方法已废弃，请使用 module_admin.service.ai_model_service.AiModelService.test_config

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :param test_prompt: 测试提示词
        :return: 测试结果
        """
        try:
            # 使用系统级AI模型服务进行测试
            from module_admin.service.ai_model_service import AiModelService as SystemAiModelService
            
            return await SystemAiModelService.test_config(query_db, config_id, test_prompt)
            
        except Exception as e:
            return AiModelTestResponseModel(
                success=False,
                error_message=f'测试失败: {str(e)}',
                response_time=0
            )

    @classmethod
    async def get_config_by_code(cls, query_db: AsyncSession, model_code: str) -> Union[AiModelConfigModel, None]:
        """
        根据模型代码获取配置

        :param query_db: 数据库会话
        :param model_code: 模型代码
        :return: 配置信息
        """
        config = await AiModelConfigDao.get_config_by_code(query_db, model_code)
        if config:
            return AiModelConfigModel(**CamelCaseUtil.transform_result(config))
        return None
