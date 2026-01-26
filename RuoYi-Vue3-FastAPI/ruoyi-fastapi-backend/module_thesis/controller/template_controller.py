"""
格式模板管理控制器
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
from module_thesis.entity.vo import (
    FormatTemplateModel,
    TemplateFormatRuleModel,
    TemplatePageQueryModel,
)
from module_thesis.service import TemplateService
from utils.log_util import logger
from utils.response_util import ResponseUtil

template_controller = APIRouterPro(
    prefix='/thesis/template',
    order_num=3,
    tags=['论文系统-模板管理'],
    dependencies=[PreAuthDependency()]
)


# ==================== 模板管理 ====================

@template_controller.get(
    '/list',
    summary='获取模板列表',
    description='获取格式模板分页列表',
    response_model=PageResponseModel[FormatTemplateModel],
)
async def get_template_list(
    request: Request,
    query: Annotated[TemplatePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取模板列表"""
    result = await TemplateService.get_template_list(query_db, query, is_page=True)
    logger.info('获取模板列表成功')
    return ResponseUtil.success(model_content=result)


@template_controller.get(
    '/popular',
    summary='获取热门模板',
    description='获取热门模板列表',
    response_model=DataResponseModel,
)
async def get_popular_templates(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    limit: Annotated[int, Query(description='返回数量', ge=1, le=50)] = 10,
) -> Response:
    """获取热门模板"""
    result = await TemplateService.get_popular_templates(query_db, limit)
    logger.info('获取热门模板成功')
    return ResponseUtil.success(data=result)


@template_controller.get(
    '/{template_id}',
    summary='获取模板详情',
    description='获取指定模板的详细信息',
    response_model=DataResponseModel[FormatTemplateModel],
)
async def get_template_detail(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取模板详情"""
    result = await TemplateService.get_template_detail(query_db, template_id)
    logger.info(f'获取模板ID为{template_id}的信息成功')
    return ResponseUtil.success(data=result)


@template_controller.post(
    '',
    summary='创建模板',
    description='创建新的格式模板',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:add')],
)
@ValidateFields(validate_model='add_template')
@Log(title='模板管理', business_type=BusinessType.INSERT)
async def create_template(
    request: Request,
    template_data: FormatTemplateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建模板"""
    template_data.create_by = current_user.user.user_name
    template_data.create_time = datetime.now()
    template_data.update_by = current_user.user.user_name
    template_data.update_time = datetime.now()
    
    # 管理员创建为官方模板，普通用户创建为用户模板
    user_id = None if current_user.user.admin else current_user.user.user_id
    
    result = await TemplateService.create_template(query_db, template_data, user_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@template_controller.put(
    '',
    summary='更新模板',
    description='更新模板信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:edit')],
)
@ValidateFields(validate_model='edit_template')
@Log(title='模板管理', business_type=BusinessType.UPDATE)
async def update_template(
    request: Request,
    template_data: FormatTemplateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新模板"""
    template_data.update_by = current_user.user.user_name
    template_data.update_time = datetime.now()
    
    result = await TemplateService.update_template(query_db, template_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@template_controller.delete(
    '/{template_id}',
    summary='删除模板',
    description='删除指定模板',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:remove')],
)
@Log(title='模板管理', business_type=BusinessType.DELETE)
async def delete_template(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除模板"""
    result = await TemplateService.delete_template(query_db, template_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 格式规则管理 ====================

@template_controller.get(
    '/{template_id}/rules',
    summary='获取模板规则',
    description='获取指定模板的所有格式规则',
    response_model=DataResponseModel,
)
async def get_template_rules(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取模板规则"""
    result = await TemplateService.get_template_rules(query_db, template_id)
    logger.info('获取模板规则成功')
    return ResponseUtil.success(data=result)


@template_controller.get(
    '/{template_id}/rules/{rule_type}',
    summary='获取指定类型规则',
    description='获取指定模板的特定类型格式规则',
    response_model=DataResponseModel,
)
async def get_rules_by_type(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    rule_type: Annotated[str, Path(description='规则类型')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取指定类型规则"""
    result = await TemplateService.get_rules_by_type(query_db, template_id, rule_type)
    logger.info(f'获取{rule_type}类型规则成功')
    return ResponseUtil.success(data=result)


@template_controller.post(
    '/{template_id}/rule',
    summary='创建格式规则',
    description='为模板创建新的格式规则',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:edit')],
)
@ValidateFields(validate_model='add_rule')
@Log(title='模板规则', business_type=BusinessType.INSERT)
async def create_rule(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    rule_data: TemplateFormatRuleModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建格式规则"""
    rule_data.template_id = template_id
    rule_data.create_by = current_user.user.user_name
    rule_data.create_time = datetime.now()
    
    result = await TemplateService.create_rule(query_db, rule_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@template_controller.post(
    '/{template_id}/rules/batch',
    summary='批量创建格式规则',
    description='为模板批量创建格式规则',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:edit')],
)
@Log(title='模板规则', business_type=BusinessType.INSERT)
async def batch_create_rules(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    rules_data: list[TemplateFormatRuleModel],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """批量创建格式规则"""
    for rule in rules_data:
        rule.create_by = current_user.user.user_name
        rule.create_time = datetime.now()
    
    result = await TemplateService.batch_create_rules(query_db, template_id, rules_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@template_controller.put(
    '/rule',
    summary='更新格式规则',
    description='更新格式规则信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:edit')],
)
@ValidateFields(validate_model='edit_rule')
@Log(title='模板规则', business_type=BusinessType.UPDATE)
async def update_rule(
    request: Request,
    rule_data: TemplateFormatRuleModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新格式规则"""
    rule_data.update_by = current_user.user.user_name
    rule_data.update_time = datetime.now()
    
    result = await TemplateService.update_rule(query_db, rule_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@template_controller.delete(
    '/rule/{rule_id}',
    summary='删除格式规则',
    description='删除指定格式规则',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:template:edit')],
)
@Log(title='模板规则', business_type=BusinessType.DELETE)
async def delete_rule(
    request: Request,
    rule_id: Annotated[int, Path(description='规则ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除格式规则"""
    result = await TemplateService.delete_rule(query_db, rule_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 模板应用 ====================

@template_controller.post(
    '/{template_id}/apply/{thesis_id}',
    summary='应用模板到论文',
    description='将指定模板应用到论文',
    response_model=ResponseBaseModel,
)
@Log(title='模板应用', business_type=BusinessType.OTHER)
async def apply_template(
    request: Request,
    template_id: Annotated[int, Path(description='模板ID')],
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """应用模板到论文"""
    result = await TemplateService.apply_template_to_thesis(
        query_db,
        template_id,
        thesis_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)
