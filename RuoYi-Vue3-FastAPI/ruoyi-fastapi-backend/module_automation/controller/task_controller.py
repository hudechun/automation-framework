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
from module_automation.entity.vo.task_vo import DeleteTaskModel, TaskModel, TaskPageQueryModel
from module_automation.service.task_service import TaskService
from utils.log_util import logger
from utils.response_util import ResponseUtil

task_controller = APIRouterPro(
    prefix='/automation/task', order_num=100, tags=['自动化管理-任务管理'], dependencies=[PreAuthDependency()]
)


@task_controller.get(
    '/list',
    summary='获取任务分页列表接口',
    description='用于获取任务分页列表',
    response_model=PageResponseModel[TaskModel],
    dependencies=[UserInterfaceAuthDependency('automation:task:list')],
)
async def get_automation_task_list(
    request: Request,
    task_page_query: Annotated[TaskPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    # 获取分页数据
    task_page_query_result = await TaskService.get_task_list_services(query_db, task_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=task_page_query_result)


@task_controller.get(
    '/{task_id}',
    summary='获取任务详细信息接口',
    description='用于获取任务详细信息',
    response_model=DataResponseModel[TaskModel],
    dependencies=[UserInterfaceAuthDependency('automation:task:query')],
)
async def get_automation_task_detail(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    task_detail_result = await TaskService.task_detail_services(query_db, task_id)
    logger.info('获取成功')

    return ResponseUtil.success(data=task_detail_result)


@task_controller.post(
    '',
    summary='新增任务接口',
    description='用于新增任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:add')],
)
@ValidateFields(validate_model='add_task')
@Log(title='任务管理', business_type=BusinessType.INSERT)
async def add_automation_task(
    request: Request,
    add_task: TaskModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_task.created_at = datetime.now()
    add_task.updated_at = datetime.now()
    add_task_result = await TaskService.add_task_services(query_db, add_task)
    logger.info(add_task_result.message)

    return ResponseUtil.success(msg=add_task_result.message)


@task_controller.put(
    '',
    summary='编辑任务接口',
    description='用于编辑任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:edit')],
)
@ValidateFields(validate_model='edit_task')
@Log(title='任务管理', business_type=BusinessType.UPDATE)
async def edit_automation_task(
    request: Request,
    edit_task: TaskModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_task.updated_at = datetime.now()
    edit_task_result = await TaskService.edit_task_services(query_db, edit_task)
    logger.info(edit_task_result.message)

    return ResponseUtil.success(msg=edit_task_result.message)


@task_controller.delete(
    '/{task_ids}',
    summary='删除任务接口',
    description='用于删除任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:remove')],
)
@Log(title='任务管理', business_type=BusinessType.DELETE)
async def delete_automation_task(
    request: Request,
    task_ids: Annotated[str, Path(description='需要删除的任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_task_result = await TaskService.delete_task_services(query_db, DeleteTaskModel(taskIds=task_ids))
    logger.info(delete_task_result.message)

    return ResponseUtil.success(msg=delete_task_result.message)


@task_controller.post(
    '/{task_id}/execute',
    summary='执行任务接口',
    description='用于执行任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:execute')],
)
@Log(title='任务管理', business_type=BusinessType.OTHER)
async def execute_automation_task(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    execute_task_result = await TaskService.execute_task_services(query_db, task_id)
    logger.info(execute_task_result.message)

    return ResponseUtil.success(msg=execute_task_result.message)
