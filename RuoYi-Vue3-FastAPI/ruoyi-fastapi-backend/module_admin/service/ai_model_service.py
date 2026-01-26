"""
系统AI模型配置服务层
"""
from typing import Any, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_admin.dao.ai_model_dao import AiModelConfigDao
from module_admin.entity.vo.ai_model_vo import (
    AiModelConfigModel,
    AiModelConfigPageQueryModel,
    AiModelTestResponseModel,
    PresetModelModel,
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
        # 直接使用model_validate，利用from_attributes自动映射，避免字段名转换问题
        return AiModelConfigModel.model_validate(config)

    @classmethod
    async def get_default_config(
        cls, query_db: AsyncSession, model_type: str = 'language'
    ) -> Union[AiModelConfigModel, None]:
        """
        获取默认AI模型配置

        :param query_db: 数据库会话
        :param model_type: 模型类型
        :return: 默认配置
        """
        config = await AiModelConfigDao.get_default_config(query_db, model_type)
        if config:
            # 直接使用model_validate，利用from_attributes自动映射，避免字段名转换问题
            return AiModelConfigModel.model_validate(config)
        return None

    @classmethod
    async def get_enabled_configs(
        cls, query_db: AsyncSession, model_type: Optional[str] = None
    ) -> list[AiModelConfigModel]:
        """
        获取所有启用的AI模型配置

        :param query_db: 数据库会话
        :param model_type: 模型类型（可选）
        :return: 启用的配置列表
        """
        configs = await AiModelConfigDao.get_enabled_configs(query_db, model_type)
        # 直接使用model_validate，利用from_attributes自动映射，避免字段名转换问题
        return [AiModelConfigModel.model_validate(config) for config in configs]

    @classmethod
    async def get_preset_models(
        cls, query_db: AsyncSession, model_type: Optional[str] = None, provider: Optional[str] = None
    ) -> list[PresetModelModel]:
        """
        获取预设模型列表（用于下拉选择）

        :param query_db: 数据库会话
        :param model_type: 模型类型
        :param provider: 提供商
        :return: 预设模型列表
        """
        models = await AiModelConfigDao.get_preset_models(query_db, model_type, provider)
        # get_preset_models返回的是字典列表，直接使用字典创建模型
        return [PresetModelModel(**model) for model in models]

    @classmethod
    async def get_models_by_type(cls, query_db: AsyncSession, model_type: str) -> list[AiModelConfigModel]:
        """
        根据类型获取模型列表

        :param query_db: 数据库会话
        :param model_type: 模型类型
        :return: 模型列表
        """
        models = await AiModelConfigDao.get_models_by_type(query_db, model_type)
        # 直接使用model_validate，利用from_attributes自动映射，避免字段名转换问题
        return [AiModelConfigModel.model_validate(model) for model in models]

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
            existing_config = await AiModelConfigDao.get_config_by_code(
                query_db, config_data.model_code, config_data.model_type
            )
            if existing_config:
                raise ServiceException(
                    message=f'模型代码 {config_data.model_code} ({config_data.model_type}) 已存在'
                )

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
            # 获取所有字段，排除未设置的字段和config_id
            # 同时排除特殊字段，因为它们不在DO模型中
            special_fields = {'top_p', 'max_tokens', 'temperature', 'api_base_url'}
            exclude_fields = {'config_id'} | special_fields  # 合并要排除的字段
            update_data = config_data.model_dump(
                exclude_unset=True, 
                exclude=exclude_fields  # 在dump时就排除特殊字段
            )
            
            # 获取DO模型的所有字段名，过滤掉不存在的字段
            from module_admin.entity.do.ai_model_do import AiModelConfig
            do_model_fields = {field.name for field in AiModelConfig.__table__.columns}
            
            # 需要特殊处理的字段（这些字段不在DO模型中，需要合并到params或映射到其他字段）
            # 注意：这些字段已经在 model_dump 时被排除了，但我们需要单独处理它们
            
            # 处理特殊字段（这些字段在 model_dump 时被排除了，需要单独获取）
            params_to_merge = {}
            has_params_update = False
            
            # 单独处理特殊字段（从原始 config_data 获取）
            if hasattr(config_data, 'top_p') and config_data.top_p is not None:
                params_to_merge['top_p'] = float(config_data.top_p)
                has_params_update = True
            if hasattr(config_data, 'temperature') and config_data.temperature is not None:
                params_to_merge['temperature'] = float(config_data.temperature)
                has_params_update = True
            if hasattr(config_data, 'max_tokens') and config_data.max_tokens is not None:
                params_to_merge['max_tokens'] = int(config_data.max_tokens)
                has_params_update = True
            if hasattr(config_data, 'api_base_url') and config_data.api_base_url is not None:
                # 将 api_base_url 映射到 api_endpoint（如果 api_endpoint 不在更新数据中）
                if 'api_endpoint' not in update_data:
                    update_data['api_endpoint'] = config_data.api_base_url
            
            # 分离普通字段
            filtered_data = {}
            for key, value in update_data.items():
                if key in do_model_fields:
                    # 普通字段，直接使用（但排除 params，因为我们要合并特殊字段）
                    if key != 'params':
                        filtered_data[key] = value
                    else:
                        # 如果 params 也在更新数据中，需要合并
                        has_params_update = True
            
            # 合并 params（如果有特殊字段需要合并或 params 字段被更新）
            if has_params_update or params_to_merge:
                import json
                # 获取现有的 params
                existing_config = await cls.get_config_detail(query_db, config_data.config_id)
                existing_params = existing_config.params or {}
                
                # 如果 params 是字符串，解析为字典
                if isinstance(existing_params, str):
                    try:
                        existing_params = json.loads(existing_params) if existing_params else {}
                    except:
                        existing_params = {}
                elif existing_params is None:
                    existing_params = {}
                
                # 如果 update_data 中有 params，先合并它
                if 'params' in update_data:
                    update_params = update_data['params']
                    if isinstance(update_params, str):
                        try:
                            update_params = json.loads(update_params) if update_params else {}
                        except:
                            update_params = {}
                        existing_params = {**existing_params, **update_params}
                    elif isinstance(update_params, dict):
                        existing_params = {**existing_params, **update_params}
                
                # 合并特殊字段参数
                if params_to_merge:
                    existing_params = {**existing_params, **params_to_merge}
                
                # 过滤掉 None 值
                merged_params = {k: v for k, v in existing_params.items() if v is not None}
                filtered_data['params'] = merged_params
            
            # 确保 filtered_data 中不包含任何特殊字段和 DO 模型中不存在的字段
            # 双重检查：只保留 DO 模型中存在的字段，并且排除特殊字段
            final_filtered_data = {}
            for key, value in filtered_data.items():
                # 严格检查：字段必须在 DO 模型中，且不在特殊字段列表中
                if key in do_model_fields and key not in special_fields:
                    final_filtered_data[key] = value
                # 如果发现特殊字段仍然存在，记录警告（但不应该发生）
                elif key in special_fields:
                    # 这不应该发生，但如果发生了，我们跳过它
                    pass
            
            # 最终验证：确保没有任何特殊字段
            remaining_special = set(final_filtered_data.keys()) & special_fields
            if remaining_special:
                # 如果还有特殊字段，强制移除
                final_filtered_data = {k: v for k, v in final_filtered_data.items() if k not in special_fields}
            
            if final_filtered_data:
                await AiModelConfigDao.update_config(query_db, config_data.config_id, final_filtered_data)
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
            await AiModelConfigDao.clear_default_config(query_db, config.model_type)

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
    async def test_config(
        cls, query_db: AsyncSession, config_id: int, test_prompt: str = '你好'
    ) -> AiModelTestResponseModel:
        """
        测试AI模型配置连接

        :param query_db: 数据库会话
        :param config_id: 配置ID
        :param test_prompt: 测试提示词
        :return: 测试结果
        """
        try:
            # 使用AI生成服务进行真实测试
            from module_thesis.service.ai_generation_service import AiGenerationService

            result = await AiGenerationService.test_ai_connection(query_db, config_id, test_prompt)

            return AiModelTestResponseModel(
                success=result['success'],
                response_text=result.get('response_text'),
                error_message=result.get('error_message'),
                response_time=result['response_time'],
            )

        except Exception as e:
            return AiModelTestResponseModel(success=False, error_message=f'测试失败: {str(e)}', response_time=0)

    @classmethod
    async def get_config_by_code(
        cls, query_db: AsyncSession, model_code: str, model_type: str = 'language'
    ) -> Union[AiModelConfigModel, None]:
        """
        根据模型代码获取配置

        :param query_db: 数据库会话
        :param model_code: 模型代码
        :param model_type: 模型类型
        :return: 配置信息
        """
        config = await AiModelConfigDao.get_config_by_code(query_db, model_code, model_type)
        if config:
            # 直接使用model_validate，利用from_attributes自动映射，避免字段名转换问题
            return AiModelConfigModel.model_validate(config)
        return None
