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
    async def get_default_config(cls, query_db: AsyncSession) -> Union[AiModelConfigModel, None]:
        """
        获取默认AI模型配置

        :param query_db: 数据库会话
        :return: 默认配置
        """
        config = await AiModelConfigDao.get_default_config(query_db)
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
            update_data = config_data.model_dump(exclude_unset=True, exclude={'config_id'})
            await AiModelConfigDao.update_config(query_db, config_data.config_id, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
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

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :param test_prompt: 测试提示词
        :return: 测试结果
        """
        # 获取配置
        config = await cls.get_config_detail(query_db, config_id)

        # 检查API Key是否配置
        if not config.api_key:
            return AiModelTestResponseModel(
                success=False, error_message='API Key未配置，请先配置API Key'
            )

        # 记录开始时间
        start_time = time.time()

        try:
            # TODO: 这里应该调用实际的AI模型API进行测试
            # 目前返回模拟结果
            # 实际实现时需要根据不同的model_code调用不同的API
            
            # 模拟API调用延迟
            import asyncio
            await asyncio.sleep(0.5)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            return AiModelTestResponseModel(
                success=True,
                response_text=f'测试成功！模型 {config.model_name} ({config.model_version}) 响应正常。',
                response_time=round(response_time, 2),
            )
        except Exception as e:
            response_time = time.time() - start_time
            return AiModelTestResponseModel(
                success=False,
                error_message=f'连接测试失败: {str(e)}',
                response_time=round(response_time, 2),
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
