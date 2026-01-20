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
from module_automation.entity.vo.session_vo import DeleteSessionModel, SessionModel, SessionPageQueryModel
from module_automation.service.session_service import SessionService
from utils.log_util import logger
from utils.response_util import ResponseUtil

session_controller = APIRouterPro(
    prefix='/automation/session', order_num=101, tags=['自动化管理-会话管理'], dependencies=[PreAuthDependency()]
)


@session_controller.get(
    '/list',
    summary='获取会话分页列表接口',
    response_model=PageResponseModel[SessionModel],
    dependencies=[UserInterfaceAuthDependency('automation:session:list')],
)
async def get_automation_session_list(
    request: Request,
    session_page_query: Annotated[SessionPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    session_page_query_result = await SessionService.get_session_list_services(query_db, session_page_query, is_page=True)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=session_page_query_result)


@session_controller.get(
    '/{session_id}',
    summary='获取会话详细信息接口',
    response_model=DataResponseModel[SessionModel],
    dependencies=[UserInterfaceAuthDependency('automation:session:query')],
)
async def get_automation_session_detail(
    request: Request,
    session_id: Annotated[int, Path(description='会话ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    session_detail_result = await SessionService.session_detail_services(query_db, session_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=session_detail_result)


@session_controller.delete(
    '/{session_ids}',
    summary='删除会话接口',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('automation:session:remove')],
)
@Log(title='会话管理', business_type=BusinessType.DELETE)
async def delete_automation_session(
    request: Request,
    session_ids: Annotated[str, Path(description='需要删除的会话ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_session_result = await SessionService.delete_session_services(query_db, DeleteSessionModel(sessionIds=session_ids))
    logger.info(delete_session_result.message)
    return ResponseUtil.success(msg=delete_session_result.message)
