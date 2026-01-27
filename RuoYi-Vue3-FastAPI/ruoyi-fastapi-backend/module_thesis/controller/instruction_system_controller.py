"""
指令系统管理控制器
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
from module_thesis.entity.vo.instruction_system_vo import (
    UniversalInstructionSystemModel,
    InstructionSystemPageQueryModel,
    InstructionSystemAddModel,
    InstructionSystemUpdateModel,
)
from module_thesis.service.instruction_system_service import InstructionSystemService
from utils.log_util import logger
from utils.response_util import ResponseUtil

instruction_system_controller = APIRouterPro(
    prefix='/thesis/instruction-system',
    order_num=4,
    tags=['论文系统-指令系统管理'],
    dependencies=[PreAuthDependency()]
)


# ==================== 指令系统管理 ====================

@instruction_system_controller.get(
    '/list',
    summary='获取指令系统列表',
    description='获取指令系统分页列表',
    response_model=PageResponseModel[UniversalInstructionSystemModel],
)
async def get_instruction_system_list(
    request: Request,
    query: Annotated[InstructionSystemPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取指令系统列表"""
    result = await InstructionSystemService.get_instruction_system_list(query_db, query, is_page=True)
    logger.info('获取指令系统列表成功')
    return ResponseUtil.success(model_content=result)


@instruction_system_controller.get(
    '/active',
    summary='获取激活的指令系统',
    description='获取当前激活的指令系统',
    response_model=DataResponseModel[UniversalInstructionSystemModel],
)
async def get_active_instruction_system(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取激活的指令系统"""
    result = await InstructionSystemService.get_active_instruction_system(query_db)
    if result:
        logger.info('获取激活的指令系统成功')
        return ResponseUtil.success(data=result)
    else:
        return ResponseUtil.success(data=None, msg='未找到激活的指令系统')


@instruction_system_controller.get(
    '/{system_id}',
    summary='获取指令系统详情',
    description='获取指定指令系统的详细信息',
    response_model=DataResponseModel[UniversalInstructionSystemModel],
)
async def get_instruction_system_detail(
    request: Request,
    system_id: Annotated[int, Path(description='指令系统ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取指令系统详情"""
    result = await InstructionSystemService.get_instruction_system_detail(query_db, system_id)
    logger.info(f'获取指令系统ID为{system_id}的信息成功')
    return ResponseUtil.success(data=result)


@instruction_system_controller.post(
    '',
    summary='创建指令系统',
    description='创建新的指令系统',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:instruction-system:add')],
)
@ValidateFields(validate_model='add_instruction_system')
@Log(title='指令系统管理', business_type=BusinessType.INSERT)
async def create_instruction_system(
    request: Request,
    system_data: InstructionSystemAddModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建指令系统"""
    system_data.create_by = current_user.user.user_name
    system_data.create_time = datetime.now()
    
    result = await InstructionSystemService.create_instruction_system(
        query_db,
        system_data,
        current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@instruction_system_controller.put(
    '/{system_id}',
    summary='更新指令系统',
    description='更新指令系统信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:instruction-system:edit')],
)
@ValidateFields(validate_model='update_instruction_system')
@Log(title='指令系统管理', business_type=BusinessType.UPDATE)
async def update_instruction_system(
    request: Request,
    system_id: Annotated[int, Path(description='指令系统ID')],
    system_data: InstructionSystemUpdateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新指令系统"""
    system_data.update_by = current_user.user.user_name
    system_data.update_time = datetime.now()
    
    result = await InstructionSystemService.update_instruction_system(
        query_db,
        system_id,
        system_data,
        current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@instruction_system_controller.delete(
    '/{system_id}',
    summary='删除指令系统',
    description='删除指定的指令系统',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:instruction-system:remove')],
)
@Log(title='指令系统管理', business_type=BusinessType.DELETE)
async def delete_instruction_system(
    request: Request,
    system_id: Annotated[int, Path(description='指令系统ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除指令系统"""
    result = await InstructionSystemService.delete_instruction_system(query_db, system_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@instruction_system_controller.put(
    '/{system_id}/activate',
    summary='激活指令系统',
    description='激活指定的指令系统（会自动停用其他指令系统）',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:instruction-system:edit')],
)
@Log(title='指令系统管理', business_type=BusinessType.UPDATE)
async def activate_instruction_system(
    request: Request,
    system_id: Annotated[int, Path(description='指令系统ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """激活指令系统"""
    result = await InstructionSystemService.activate_instruction_system(
        query_db,
        system_id,
        current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
