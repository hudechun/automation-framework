from datetime import datetime, time
from typing import Any, Union

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_automation.entity.do.session_do import AutomationSession
from module_automation.entity.vo.session_vo import SessionPageQueryModel
from utils.page_util import PageUtil


class SessionDao:
    """
    自动化会话管理模块数据库操作层
    """

    @classmethod
    async def get_session_detail_by_id(cls, db: AsyncSession, session_id: int) -> Union[AutomationSession, None]:
        """根据会话ID获取会话详细信息"""
        session_info = (await db.execute(select(AutomationSession).where(AutomationSession.id == session_id))).scalars().first()
        return session_info

    @classmethod
    async def get_session_list(
        cls, db: AsyncSession, query_object: SessionPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """根据查询参数获取会话列表信息"""
        query = (
            select(AutomationSession)
            .where(
                AutomationSession.session_id.like(f'%{query_object.session_id}%') if query_object.session_id else True,
                AutomationSession.state == query_object.state if query_object.state else True,
                AutomationSession.driver_type == query_object.driver_type if query_object.driver_type else True,
                AutomationSession.created_at.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(AutomationSession.id.desc())
            .distinct()
        )
        session_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return session_list

    @classmethod
    async def delete_session_dao(cls, db: AsyncSession, session_ids: list[int]) -> int:
        """删除会话数据库操作"""
        result = await db.execute(delete(AutomationSession).where(AutomationSession.id.in_(session_ids)))
        await db.flush()
        return result.rowcount
