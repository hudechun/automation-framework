from typing import Any, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_automation.dao.session_dao import SessionDao
from module_automation.entity.vo.session_vo import DeleteSessionModel, SessionModel, SessionPageQueryModel
from utils.common_util import CamelCaseUtil


class SessionService:
    """
    自动化会话管理模块服务层
    """

    @classmethod
    async def get_session_list_services(
        cls, query_db: AsyncSession, query_object: SessionPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """获取会话列表信息service"""
        session_list_result = await SessionDao.get_session_list(query_db, query_object, is_page)
        return session_list_result

    @classmethod
    async def session_detail_services(cls, query_db: AsyncSession, session_id: int) -> SessionModel:
        """获取会话详细信息service"""
        session_info = await SessionDao.get_session_detail_by_id(query_db, session_id)
        if session_info:
            result = SessionModel(**CamelCaseUtil.transform_result(session_info))
        else:
            result = SessionModel(**dict())
        return result

    @classmethod
    async def delete_session_services(cls, query_db: AsyncSession, page_object: DeleteSessionModel) -> CrudResponseModel:
        """删除会话信息service"""
        if page_object.session_ids:
            session_id_list = page_object.session_ids.split(',')
            try:
                await SessionDao.delete_session_dao(query_db, session_id_list)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入会话ID为空')
