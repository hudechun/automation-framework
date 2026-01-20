from typing import Any, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_automation.dao.task_dao import TaskDao
from module_automation.entity.vo.task_vo import DeleteTaskModel, TaskModel, TaskPageQueryModel
from utils.common_util import CamelCaseUtil


class TaskService:
    """
    自动化任务管理模块服务层
    """

    @classmethod
    async def get_task_list_services(
        cls, query_db: AsyncSession, query_object: TaskPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取任务列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 任务列表信息对象
        """
        task_list_result = await TaskDao.get_task_list(query_db, query_object, is_page)

        return task_list_result

    @classmethod
    async def task_detail_services(cls, query_db: AsyncSession, task_id: int) -> TaskModel:
        """
        获取任务详细信息service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 任务信息对象
        """
        task_info = await TaskDao.get_task_detail_by_id(query_db, task_id)
        if task_info:
            result = TaskModel(**CamelCaseUtil.transform_result(task_info))
        else:
            result = TaskModel(**dict())

        return result

    @classmethod
    async def add_task_services(cls, query_db: AsyncSession, page_object: TaskModel) -> CrudResponseModel:
        """
        新增任务信息service

        :param query_db: orm对象
        :param page_object: 新增任务对象
        :return: 新增任务校验结果
        """
        try:
            await TaskDao.add_task_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_task_services(cls, query_db: AsyncSession, page_object: TaskModel) -> CrudResponseModel:
        """
        编辑任务信息service

        :param query_db: orm对象
        :param page_object: 编辑任务对象
        :return: 编辑任务校验结果
        """
        task_info = await cls.task_detail_services(query_db, page_object.id)
        if task_info.id:
            try:
                await TaskDao.edit_task_dao(query_db, page_object)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='任务不存在')

    @classmethod
    async def delete_task_services(cls, query_db: AsyncSession, page_object: DeleteTaskModel) -> CrudResponseModel:
        """
        删除任务信息service

        :param query_db: orm对象
        :param page_object: 删除任务对象
        :return: 删除任务校验结果
        """
        if page_object.task_ids:
            task_id_list = page_object.task_ids.split(',')
            try:
                await TaskDao.delete_task_dao(query_db, task_id_list)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入任务ID为空')

    @classmethod
    async def execute_task_services(cls, query_db: AsyncSession, task_id: int) -> CrudResponseModel:
        """
        执行任务service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 执行结果
        """
        from module_automation.executor import TaskExecutor, BackgroundWorker
        from module_automation.executor.task_executor import get_task_executor
        from module_automation.executor.background_worker import get_background_worker
        
        task_info = await cls.task_detail_services(query_db, task_id)
        if not task_info.id:
            raise ServiceException(message='任务不存在')

        # 检查任务状态
        if task_info.status == 'running':
            raise ServiceException(message='任务正在执行中')

        try:
            # 更新任务状态为执行中
            await TaskDao.edit_task_dao(query_db, TaskModel(id=task_id, status='running'))
            await query_db.commit()

            # 获取执行器和后台工作线程
            executor = get_task_executor()
            worker = get_background_worker()
            
            # 定义执行完成回调
            async def on_complete(task_id: int, result: dict, error: Exception):
                """任务执行完成回调"""
                try:
                    if error:
                        # 执行失败
                        await TaskDao.edit_task_dao(query_db, TaskModel(id=task_id, status='failed'))
                    else:
                        # 执行成功
                        await TaskDao.edit_task_dao(query_db, TaskModel(id=task_id, status='completed'))
                    await query_db.commit()
                except Exception as e:
                    print(f"更新任务状态失败: {str(e)}")
            
            # 提交任务到后台执行
            coroutine = executor.execute_task(
                task_id=task_id,
                task_name=task_info.name,
                task_type=task_info.task_type,
                actions=task_info.actions,
                config=task_info.config
            )
            worker.submit_task(task_id, coroutine, on_complete)

            return CrudResponseModel(is_success=True, message='任务已开始执行')
        except Exception as e:
            await query_db.rollback()
            # 执行失败，更新状态为失败
            await TaskDao.edit_task_dao(query_db, TaskModel(id=task_id, status='failed'))
            await query_db.commit()
            raise e
