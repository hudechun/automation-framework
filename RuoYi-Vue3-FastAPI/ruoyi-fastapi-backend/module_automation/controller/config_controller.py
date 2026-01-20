from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_automation.entity.vo.config_vo import DeleteModelConfigModel, ModelConfigModel, ModelConfigPageQueryModel
from module_automation.service.config_service import ModelConfigService
from utils.log_util import logger
from utils.response_util import ResponseUtil

config_controller = APIRouterPro(
    prefix='/automation/config', order_num=103, tags=['自动化管理-模型配置'], dependencies=[PreAuthDependency()]
)


@config_controller.get(
    '/list',
    summary='获取模型配置分页列表接口',
    response_model=PageResponseModel[ModelConfigModel],
    dependencies=[UserInterfaceAuthDependency('automation:config:list')],
)
async def get_automation_config_list(
    request: Request,
    config_page_query: Annotated[ModelConfigPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    config_page_query_result = await ModelConfigService.get_model_config_list_services(
        query_db, config_page_query, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=config_page_query_result)


@config_controller.get(
    '/{config_id}',
    summary='获取模型配置详细信息接口',
    response_model=DataResponseModel[ModelConfigModel],
    dependencies=[UserInterfaceAuthDependency('automation:config:query')],
)
async def get_automation_config_detail(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    config_detail_result = await ModelConfigService.model_config_detail_services(query_db, config_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=config_detail_result)


@config_controller.post(
    '',
    summary='新增模型配置接口',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:config:add')],
)
@ValidateFields(validate_model='add_config')
@Log(title='模型配置管理', business_type=BusinessType.INSERT)
async def add_automation_config(
    request: Request,
    add_config: ModelConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_config.created_at = datetime.now()
    add_config.updated_at = datetime.now()
    add_config_result = await ModelConfigService.add_model_config_services(query_db, add_config)
    logger.info(add_config_result.message)
    return ResponseUtil.success(msg=add_config_result.message)


@config_controller.put(
    '',
    summary='编辑模型配置接口',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:config:edit')],
)
@ValidateFields(validate_model='edit_config')
@Log(title='模型配置管理', business_type=BusinessType.UPDATE)
async def edit_automation_config(
    request: Request,
    edit_config: ModelConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_config.updated_at = datetime.now()
    edit_config_result = await ModelConfigService.edit_model_config_services(query_db, edit_config)
    logger.info(edit_config_result.message)
    return ResponseUtil.success(msg=edit_config_result.message)


@config_controller.delete(
    '/{config_ids}',
    summary='删除模型配置接口',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:config:remove')],
)
@Log(title='模型配置管理', business_type=BusinessType.DELETE)
async def delete_automation_config(
    request: Request,
    config_ids: Annotated[str, Path(description='需要删除的配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_config_result = await ModelConfigService.delete_model_config_services(
        query_db, DeleteModelConfigModel(configIds=config_ids)
    )
    logger.info(delete_config_result.message)
    return ResponseUtil.success(msg=delete_config_result.message)
