from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from module_automation.dao.execution_dao import ExecutionRecordDao
from module_automation.entity.vo.execution_vo import DeleteExecutionRecordModel, ExecutionRecordPageQueryModel


class ExecutionRecordService:
    """
    执行记录服务类
    """

    @classmethod
    async def get_execution_record_list_services(
        cls, query_db: AsyncSession, query_object: ExecutionRecordPageQueryModel, is_page: bool = False
    ):
        """
        获取执行记录列表
        """
        execution_record_list_result = await ExecutionRecordDao.get_execution_record_list(
            query_db, query_object, is_page
        )

        return execution_record_list_result

    @classmethod
    async def execution_record_detail_services(cls, query_db: AsyncSession, execution_id: int):
        """
        获取执行记录详情
        """
        execution_record = await ExecutionRecordDao.get_execution_record_detail_by_id(query_db, execution_id)
        if execution_record:
            result = execution_record._asdict()
        else:
            result = {}

        return result

    @classmethod
    async def delete_execution_record_services(cls, query_db: AsyncSession, delete_object: DeleteExecutionRecordModel):
        """
        删除执行记录
        """
        if delete_object.execution_ids:
            execution_id_list = delete_object.execution_ids.split(',')
            for execution_id in execution_id_list:
                execution_record = await ExecutionRecordDao.get_execution_record_by_id(query_db, int(execution_id))
                if execution_record:
                    await ExecutionRecordDao.delete_execution_record_dao(query_db, execution_record)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')

        return CrudResponseModel(is_success=False, message='传入执行记录ID为空')
