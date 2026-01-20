from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_automation.entity.do.execution_do import ExecutionRecordDO
from module_automation.entity.do.task_do import AutomationTask
from module_automation.entity.vo.execution_vo import ExecutionRecordPageQueryModel
from utils.page_util import PageUtil


class ExecutionRecordDao:
    """
    执行记录数据访问对象
    """

    @classmethod
    async def get_execution_record_list(
        cls, db: AsyncSession, query_object: ExecutionRecordPageQueryModel, is_page: bool = False
    ):
        """
        获取执行记录列表
        """
        query = (
            select(
                ExecutionRecordDO.id,
                ExecutionRecordDO.task_id,
                AutomationTask.name.label('task_name'),
                ExecutionRecordDO.status,
                ExecutionRecordDO.start_time,
                ExecutionRecordDO.end_time,
                ExecutionRecordDO.duration,
                ExecutionRecordDO.logs,
                ExecutionRecordDO.error_message,
                ExecutionRecordDO.result,
                ExecutionRecordDO.created_at,
            )
            .outerjoin(AutomationTask, ExecutionRecordDO.task_id == AutomationTask.id)
            .order_by(ExecutionRecordDO.created_at.desc())
        )

        # 任务ID筛选
        if query_object.task_id:
            query = query.where(ExecutionRecordDO.task_id == query_object.task_id)
        # 状态筛选
        if query_object.status:
            query = query.where(ExecutionRecordDO.status == query_object.status)
        # 时间范围筛选
        if query_object.begin_time and query_object.end_time:
            query = query.where(
                and_(
                    ExecutionRecordDO.start_time >= query_object.begin_time,
                    ExecutionRecordDO.start_time <= query_object.end_time,
                )
            )

        if is_page:
            execution_record_list = await PageUtil.paginate(
                db, query, query_object.page_num, query_object.page_size, is_page
            )
        else:
            result = await db.execute(query)
            execution_record_list = result.all()

        return execution_record_list

    @classmethod
    async def get_execution_record_detail_by_id(cls, db: AsyncSession, execution_id: int):
        """
        根据ID获取执行记录详情
        """
        query = (
            select(
                ExecutionRecordDO.id,
                ExecutionRecordDO.task_id,
                AutomationTask.name.label('task_name'),
                ExecutionRecordDO.status,
                ExecutionRecordDO.start_time,
                ExecutionRecordDO.end_time,
                ExecutionRecordDO.duration,
                ExecutionRecordDO.logs,
                ExecutionRecordDO.error_message,
                ExecutionRecordDO.result,
                ExecutionRecordDO.created_at,
            )
            .outerjoin(AutomationTask, ExecutionRecordDO.task_id == AutomationTask.id)
            .where(ExecutionRecordDO.id == execution_id)
        )
        result = await db.execute(query)
        execution_record = result.first()

        return execution_record

    @classmethod
    async def delete_execution_record_dao(cls, db: AsyncSession, execution_object: ExecutionRecordDO):
        """
        删除执行记录
        """
        await db.delete(execution_object)
        await db.flush()

    @classmethod
    async def get_execution_record_by_id(cls, db: AsyncSession, execution_id: int):
        """
        根据ID获取执行记录对象
        """
        query = select(ExecutionRecordDO).where(ExecutionRecordDO.id == execution_id)
        result = await db.execute(query)
        execution_record = result.scalars().first()

        return execution_record
