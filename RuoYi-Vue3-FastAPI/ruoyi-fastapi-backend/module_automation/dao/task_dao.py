from datetime import datetime, time
from typing import Any, Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_automation.entity.do.task_do import AutomationTask
from module_automation.entity.vo.task_vo import TaskModel, TaskPageQueryModel
from utils.page_util import PageUtil


class TaskDao:
    """
    自动化任务管理模块数据库操作层
    """

    @classmethod
    async def get_task_detail_by_id(cls, db: AsyncSession, task_id: int) -> Union[AutomationTask, None]:
        """
        根据任务ID获取任务详细信息

        :param db: orm对象
        :param task_id: 任务ID
        :return: 任务信息对象
        """
        task_info = (await db.execute(select(AutomationTask).where(AutomationTask.id == task_id))).scalars().first()

        return task_info

    @classmethod
    async def get_task_list(
        cls, db: AsyncSession, query_object: TaskPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        根据查询参数获取任务列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 任务列表信息对象
        """
        query = (
            select(AutomationTask)
            .where(
                AutomationTask.name.like(f'%{query_object.name}%') if query_object.name else True,
                AutomationTask.task_type == query_object.task_type if query_object.task_type else True,
                AutomationTask.status == query_object.status if query_object.status else True,
                AutomationTask.created_at.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(AutomationTask.id.desc())
            .distinct()
        )
        task_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return task_list

    @classmethod
    async def add_task_dao(cls, db: AsyncSession, task: TaskModel) -> AutomationTask:
        """
        新增任务数据库操作

        :param db: orm对象
        :param task: 任务对象
        :return: 任务对象
        """
        db_task = AutomationTask(**task.model_dump(exclude_none=True))
        db.add(db_task)
        await db.flush()

        return db_task

    @classmethod
    async def edit_task_dao(cls, db: AsyncSession, task: TaskModel) -> int:
        """
        编辑任务数据库操作

        :param db: orm对象
        :param task: 任务对象
        :return: 影响行数
        """
        result = await db.execute(
            update(AutomationTask)
            .where(AutomationTask.id == task.id)
            .values(**task.model_dump(exclude_unset=True, exclude={'id', 'created_at'}))
        )
        await db.flush()

        return result.rowcount

    @classmethod
    async def delete_task_dao(cls, db: AsyncSession, task_ids: list[int]) -> int:
        """
        删除任务数据库操作

        :param db: orm对象
        :param task_ids: 任务ID列表
        :return: 影响行数
        """
        result = await db.execute(delete(AutomationTask).where(AutomationTask.id.in_(task_ids)))
        await db.flush()

        return result.rowcount
