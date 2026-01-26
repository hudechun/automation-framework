"""
AI模型配置控制器
"""
from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_thesis.entity.vo.ai_model_vo import (
    AiModelConfigModel,
    AiModelConfigPageQueryModel,
    AiModelTestResponseModel,
)
from module_thesis.service.ai_model_service import AiModelService
from utils.log_util import logger
from utils.response_util import ResponseUtil

ai_model_controller = APIRouterPro(
    prefix='/thesis/ai-model', order_num=1, tags=['论文系统-AI模型配置'], dependencies=[PreAuthDependency()]
)


# ==================== AI模型配置管理 ====================


@ai_model_controller.get(
    '/list',
    summary='获取AI模型配置列表',
    description='获取AI模型配置分页列表',
    response_model=PageResponseModel[AiModelConfigModel],
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:list')],
)
async def get_config_list(
    request: Request,
    query: Annotated[AiModelConfigPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取AI模型配置列表"""
    result = await AiModelService.get_config_list(query_db, query, is_page=True)
    logger.info('获取AI模型配置列表成功')
    return ResponseUtil.success(model_content=result)


@ai_model_controller.get(
    '/{config_id}',
    summary='获取AI模型配置详情',
    description='获取指定AI模型配置的详细信息',
    response_model=DataResponseModel[AiModelConfigModel],
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:query')],
)
async def get_config_detail(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取AI模型配置详情"""
    result = await AiModelService.get_config_detail(query_db, config_id)
    logger.info(f'获取AI模型配置ID为{config_id}的信息成功')
    return ResponseUtil.success(data=result)


@ai_model_controller.get(
    '/default/config',
    summary='获取默认AI模型配置',
    description='获取当前默认的AI模型配置',
    response_model=DataResponseModel[AiModelConfigModel],
)
async def get_default_config(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取默认AI模型配置"""
    result = await AiModelService.get_default_config(query_db)
    if not result:
        return ResponseUtil.error(msg='未设置默认AI模型')
    logger.info('获取默认AI模型配置成功')
    return ResponseUtil.success(data=result)


@ai_model_controller.get(
    '/enabled/list',
    summary='获取启用的AI模型配置列表',
    description='获取所有启用的AI模型配置',
    response_model=DataResponseModel[list[AiModelConfigModel]],
)
async def get_enabled_configs(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取启用的AI模型配置列表"""
    result = await AiModelService.get_enabled_configs(query_db)
    logger.info('获取启用的AI模型配置列表成功')
    return ResponseUtil.success(data=result)


@ai_model_controller.post(
    '',
    summary='新增AI模型配置',
    description='创建新的AI模型配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:add')],
)
@ValidateFields(validate_model='add_config')
@Log(title='AI模型配置管理', business_type=BusinessType.INSERT)
async def add_config(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    config_data: AiModelConfigModel = None,
) -> Response:
    """新增AI模型配置"""
    config_data.create_by = current_user.user.user_name
    config_data.create_time = datetime.now()
    config_data.update_by = current_user.user.user_name
    config_data.update_time = datetime.now()

    result = await AiModelService.add_config(query_db, config_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@ai_model_controller.put(
    '',
    summary='更新AI模型配置',
    description='更新AI模型配置信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:edit')],
)
@ValidateFields(validate_model='edit_config')
@Log(title='AI模型配置管理', business_type=BusinessType.UPDATE)
async def update_config(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    config_data: AiModelConfigModel = None,
) -> Response:
    """更新AI模型配置"""
    config_data.update_by = current_user.user.user_name
    config_data.update_time = datetime.now()

    result = await AiModelService.update_config(query_db, config_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@ai_model_controller.delete(
    '/{config_id}',
    summary='删除AI模型配置',
    description='删除指定的AI模型配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:remove')],
)
@Log(title='AI模型配置管理', business_type=BusinessType.DELETE)
async def delete_config(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除AI模型配置"""
    result = await AiModelService.delete_config(query_db, config_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@ai_model_controller.put(
    '/{config_id}/enable',
    summary='启用AI模型配置',
    description='启用指定的AI模型配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:edit')],
)
@Log(title='AI模型配置管理', business_type=BusinessType.UPDATE)
async def enable_config(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """启用AI模型配置"""
    result = await AiModelService.enable_config(query_db, config_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@ai_model_controller.put(
    '/{config_id}/disable',
    summary='禁用AI模型配置',
    description='禁用指定的AI模型配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:edit')],
)
@Log(title='AI模型配置管理', business_type=BusinessType.UPDATE)
async def disable_config(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """禁用AI模型配置"""
    result = await AiModelService.disable_config(query_db, config_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@ai_model_controller.put(
    '/{config_id}/default',
    summary='设置默认AI模型配置',
    description='将指定的AI模型配置设为默认',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:edit')],
)
@Log(title='AI模型配置管理', business_type=BusinessType.UPDATE)
async def set_default_config(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """设置默认AI模型配置"""
    result = await AiModelService.set_default_config(query_db, config_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@ai_model_controller.post(
    '/{config_id}/test',
    summary='测试AI模型配置',
    description='测试AI模型配置的连接',
    response_model=DataResponseModel[AiModelTestResponseModel],
    dependencies=[UserInterfaceAuthDependency('thesis:ai-model:test')],
)
@Log(title='AI模型配置测试', business_type=BusinessType.OTHER)
async def test_config(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    test_prompt: Annotated[str, Query(description='测试提示词')] = '你好',
) -> Response:
    """测试AI模型配置"""
    try:
        result = await AiModelService.test_config(query_db, config_id, test_prompt)
        logger.info(f'测试AI模型配置ID为{config_id}')
        
        # 使用 model_dump(by_alias=True) 确保字段名转换为 camelCase
        result_dict = result.model_dump(by_alias=True)
        
        if result.success:
            return ResponseUtil.success(data=result_dict, msg='测试成功')
        else:
            # 确保有错误信息
            error_msg = result.error_message or '测试失败，未知错误'
            return ResponseUtil.error(data=result_dict, msg=error_msg)
    except Exception as e:
        logger.error(f'测试AI模型配置失败 (Config ID: {config_id}): {str(e)}', exc_info=True)
        error_result = AiModelTestResponseModel(
            success=False,
            error_message=f'测试失败: {str(e)}',
            response_time=0.0
        )
        error_dict = error_result.model_dump(by_alias=True)
        return ResponseUtil.error(data=error_dict, msg=f'测试失败: {str(e)}')
