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
from module_automation.entity.vo.task_vo import DeleteTaskModel, TaskModel, TaskPageQueryModel, ParseTaskModel
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


@task_controller.post(
    '/{task_id}/pause',
    summary='暂停任务接口',
    description='用于暂停正在执行的任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:execute')],
)
@Log(title='任务管理', business_type=BusinessType.OTHER)
async def pause_automation_task(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    pause_task_result = await TaskService.pause_task_services(query_db, task_id)
    logger.info(pause_task_result.message)
    return ResponseUtil.success(msg=pause_task_result.message)


@task_controller.post(
    '/{task_id}/resume',
    summary='恢复任务接口',
    description='用于恢复已暂停的任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:execute')],
)
@Log(title='任务管理', business_type=BusinessType.OTHER)
async def resume_automation_task(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    resume_task_result = await TaskService.resume_task_services(query_db, task_id)
    logger.info(resume_task_result.message)
    return ResponseUtil.success(msg=resume_task_result.message)


@task_controller.post(
    '/{task_id}/stop',
    summary='停止任务接口',
    description='用于停止正在执行的任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:execute')],
)
@Log(title='任务管理', business_type=BusinessType.OTHER)
async def stop_automation_task(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    stop_task_result = await TaskService.stop_task_services(query_db, task_id)
    logger.info(stop_task_result.message)
    return ResponseUtil.success(msg=stop_task_result.message)


@task_controller.get(
    '/{task_id}/execution/status',
    summary='获取任务执行状态接口',
    description='用于获取任务的实时执行状态',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:query')],
)
async def get_task_execution_status(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    status_result = await TaskService.get_task_execution_status_services(query_db, task_id)
    return ResponseUtil.success(data=status_result)


@task_controller.get(
    '/{task_id}/execution/progress',
    summary='获取任务执行进度接口',
    description='用于获取任务的实时执行进度',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:query')],
)
async def get_task_execution_progress(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    progress_result = await TaskService.get_task_execution_progress_services(query_db, task_id)
    return ResponseUtil.success(data=progress_result)


@task_controller.get(
    '/{task_id}/execution/logs',
    summary='获取任务执行日志接口',
    description='用于获取任务的执行日志',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:query')],
)
async def get_task_execution_logs(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    skip: Annotated[int, Query(ge=0, description='跳过条数')] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description='返回条数')] = 100,
) -> Response:
    logs_result = await TaskService.get_task_execution_logs_services(query_db, task_id, skip, limit)
    return ResponseUtil.success(data=logs_result)


@task_controller.post(
    '/parse',
    summary='解析自然语言任务接口',
    description='用于将自然语言描述解析为任务操作序列',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('automation:task:add')],
)
async def parse_natural_language_task(
    request: Request,
    parse_data: ParseTaskModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    parse_result = await TaskService.parse_natural_language_task_services(query_db, parse_data.model_dump())
    return ResponseUtil.success(data=parse_result)
