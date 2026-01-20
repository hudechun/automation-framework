from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_automation.entity.vo.execution_vo import (
    DeleteExecutionRecordModel,
    ExecutionRecordModel,
    ExecutionRecordPageQueryModel,
)
from module_automation.service.execution_service import ExecutionRecordService
from utils.log_util import logger
from utils.response_util import ResponseUtil

execution_controller = APIRouterPro(
    prefix='/automation/execution', order_num=102, tags=['自动化管理-执行记录'], dependencies=[PreAuthDependency()]
)


@execution_controller.get(
    '/list',
    summary='获取执行记录分页列表接口',
    response_model=PageResponseModel[ExecutionRecordModel],
    dependencies=[UserInterfaceAuthDependency('automation:execution:list')],
)
async def get_automation_execution_list(
    request: Request,
    execution_page_query: Annotated[ExecutionRecordPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    execution_page_query_result = await ExecutionRecordService.get_execution_record_list_services(
        query_db, execution_page_query, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=execution_page_query_result)


@execution_controller.get(
    '/{execution_id}',
    summary='获取执行记录详细信息接口',
    response_model=DataResponseModel[ExecutionRecordModel],
    dependencies=[UserInterfaceAuthDependency('automation:execution:query')],
)
async def get_automation_execution_detail(
    request: Request,
    execution_id: Annotated[int, Path(description='执行记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    execution_detail_result = await ExecutionRecordService.execution_record_detail_services(query_db, execution_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=execution_detail_result)


@execution_controller.delete(
    '/{execution_ids}',
    summary='删除执行记录接口',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:execution:remove')],
)
@Log(title='执行记录管理', business_type=BusinessType.DELETE)
async def delete_automation_execution(
    request: Request,
    execution_ids: Annotated[str, Path(description='需要删除的执行记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_execution_result = await ExecutionRecordService.delete_execution_record_services(
        query_db, DeleteExecutionRecordModel(executionIds=execution_ids)
    )
    logger.info(delete_execution_result.message)
    return ResponseUtil.success(msg=delete_execution_result.message)
