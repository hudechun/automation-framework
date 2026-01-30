"""
大纲提示词模板管理控制器
"""
from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_thesis.entity.vo.outline_prompt_template_vo import (
    OutlinePromptTemplateModel,
    OutlinePromptTemplatePageQueryModel,
    OutlinePromptTemplateAddModel,
    OutlinePromptTemplateUpdateModel,
)
from module_thesis.service.outline_prompt_template_service import OutlinePromptTemplateService
from utils.log_util import logger
from utils.response_util import ResponseUtil

outline_prompt_template_controller = APIRouterPro(
    prefix='/thesis/outline-prompt-template',
    order_num=5,
    tags=['论文系统-大纲提示词模板管理'],
    dependencies=[PreAuthDependency()],
)


@outline_prompt_template_controller.get(
    '/list',
    summary='获取大纲提示词模板列表',
    description='获取大纲提示词模板分页列表',
    response_model=PageResponseModel[OutlinePromptTemplateModel],
)
async def get_outline_prompt_template_list(
    request: Request,
    query: Annotated[OutlinePromptTemplatePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取大纲提示词模板列表"""
    result = await OutlinePromptTemplateService.get_list(query_db, query, is_page=True)
    logger.info('获取大纲提示词模板列表成功')
    return ResponseUtil.success(model_content=result)


@outline_prompt_template_controller.get(
    '/{prompt_template_id}',
    summary='获取大纲提示词模板详情',
    description='获取指定大纲提示词模板的详细信息',
    response_model=DataResponseModel[OutlinePromptTemplateModel],
)
async def get_outline_prompt_template_detail(
    request: Request,
    prompt_template_id: Annotated[int, Path(description='提示词模板ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取大纲提示词模板详情"""
    result = await OutlinePromptTemplateService.get_by_id(query_db, prompt_template_id)
    if result is None:
        return ResponseUtil.failure(msg='大纲提示词模板不存在')
    logger.info(f'获取大纲提示词模板ID为{prompt_template_id}的信息成功')
    return ResponseUtil.success(data=result)


@outline_prompt_template_controller.post(
    '',
    summary='新增大纲提示词模板',
    description='创建新的大纲提示词模板',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:outline-prompt-template:add')],
)
@Log(title='大纲提示词模板管理', business_type=BusinessType.INSERT)
async def create_outline_prompt_template(
    request: Request,
    data: OutlinePromptTemplateAddModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增大纲提示词模板"""
    result = await OutlinePromptTemplateService.add(
        query_db, data, create_by=current_user.user.user_name or ''
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@outline_prompt_template_controller.put(
    '/{prompt_template_id}',
    summary='更新大纲提示词模板',
    description='更新大纲提示词模板信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:outline-prompt-template:edit')],
)
@Log(title='大纲提示词模板管理', business_type=BusinessType.UPDATE)
async def update_outline_prompt_template(
    request: Request,
    prompt_template_id: Annotated[int, Path(description='提示词模板ID')],
    data: OutlinePromptTemplateUpdateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新大纲提示词模板"""
    data.prompt_template_id = prompt_template_id
    result = await OutlinePromptTemplateService.update(
        query_db, data, update_by=current_user.user.user_name or ''
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@outline_prompt_template_controller.delete(
    '/{prompt_template_id}',
    summary='删除大纲提示词模板',
    description='删除指定的大纲提示词模板',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:outline-prompt-template:remove')],
)
@Log(title='大纲提示词模板管理', business_type=BusinessType.DELETE)
async def delete_outline_prompt_template(
    request: Request,
    prompt_template_id: Annotated[int, Path(description='提示词模板ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除大纲提示词模板"""
    result = await OutlinePromptTemplateService.delete_logic(query_db, prompt_template_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
