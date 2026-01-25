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
        执行任务service - 使用Automation Framework的执行器

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 执行结果
        """
        import sys
        import os
        from common.context import RequestContext
        
        # 添加automation-framework到Python路径
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.task.executor import get_global_executor
            from src.task.task_manager import get_global_task_manager
            from src.core.types import TaskStatus
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        task_info = await cls.task_detail_services(query_db, task_id)
        if not task_info.id:
            raise ServiceException(message='任务不存在')

        # 检查任务状态
        if task_info.status == 'running':
            raise ServiceException(message='任务正在执行中')

        try:
            # 获取当前用户ID（如果可用）
            user_id = None
            try:
                current_user = RequestContext.get_current_user()
                user_id = current_user.user_id
            except:
                pass  # 如果无法获取用户，继续执行
            
            # 使用Automation Framework的执行器
            executor = get_global_executor(db_session=query_db)
            
            # 执行任务（task_id需要转换为字符串）
            result = await executor.execute_task(
                task_id=str(task_id),
                user_id=user_id,
                db_session=query_db
            )
            
            if not result.get("success"):
                raise ServiceException(message=result.get("message", "任务执行失败"))
            
            return CrudResponseModel(is_success=True, message='任务已开始执行')
        except ServiceException:
            raise
        except Exception as e:
            await query_db.rollback()
            # 执行失败，更新状态为失败
            try:
                await TaskDao.edit_task_dao(query_db, TaskModel(id=task_id, status='failed'))
                await query_db.commit()
            except:
                pass
            raise ServiceException(message=f'任务执行失败: {str(e)}')
    
    @classmethod
    async def pause_task_services(cls, query_db: AsyncSession, task_id: int) -> CrudResponseModel:
        """
        暂停任务service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 操作结果
        """
        import sys
        import os
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.task.executor import get_global_executor
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        executor = get_global_executor(db_session=query_db)
        result = await executor.pause_task(str(task_id), db_session=query_db)
        
        if not result.get("success"):
            raise ServiceException(message=result.get("message", "暂停任务失败"))
        
        return CrudResponseModel(is_success=True, message='任务已暂停')
    
    @classmethod
    async def resume_task_services(cls, query_db: AsyncSession, task_id: int) -> CrudResponseModel:
        """
        恢复任务service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 操作结果
        """
        import sys
        import os
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.task.executor import get_global_executor
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        executor = get_global_executor(db_session=query_db)
        result = await executor.resume_task(str(task_id), db_session=query_db)
        
        if not result.get("success"):
            raise ServiceException(message=result.get("message", "恢复任务失败"))
        
        return CrudResponseModel(is_success=True, message='任务已恢复')
    
    @classmethod
    async def stop_task_services(cls, query_db: AsyncSession, task_id: int) -> CrudResponseModel:
        """
        停止任务service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 操作结果
        """
        import sys
        import os
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.task.executor import get_global_executor
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        executor = get_global_executor(db_session=query_db)
        result = await executor.stop_task(str(task_id), db_session=query_db)
        
        if not result.get("success"):
            raise ServiceException(message=result.get("message", "停止任务失败"))
        
        return CrudResponseModel(is_success=True, message='任务已停止')
    
    @classmethod
    async def get_task_execution_status_services(cls, query_db: AsyncSession, task_id: int) -> dict:
        """
        获取任务执行状态service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 执行状态
        """
        import sys
        import os
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.task.executor import get_global_executor
            from src.task.task_manager import get_global_task_manager
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        executor = get_global_executor(db_session=query_db)
        task_manager = get_global_task_manager(db_session=query_db)
        
        # 获取执行状态
        state = executor.get_execution_state(str(task_id))
        
        # 获取任务信息
        task = await task_manager.get_task(str(task_id), db_session=query_db)
        
        return {
            "task_id": task_id,
            "task_name": task.name if task else None,
            "state": state.value if state else None,
            "is_running": executor.is_task_running(str(task_id))
        }
    
    @classmethod
    async def get_task_execution_progress_services(cls, query_db: AsyncSession, task_id: int) -> dict:
        """
        获取任务执行进度service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 执行进度
        """
        import sys
        import os
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.task.executor import get_global_executor
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        executor = get_global_executor(db_session=query_db)
        progress = executor.get_execution_progress(str(task_id))
        
        if progress:
            return progress.to_dict()
        else:
            # 如果没有进度信息，返回默认值
            return {
                "total_actions": 0,
                "current_action_index": 0,
                "completed_actions": 0,
                "failed_actions": 0,
                "remaining_actions": 0,
                "progress_percentage": 0.0,
                "elapsed_time": 0.0,
                "estimated_remaining_time": None,
                "average_action_time": 0.0
            }
    
    @classmethod
    async def get_task_execution_logs_services(cls, query_db: AsyncSession, task_id: int, skip: int = 0, limit: int = 100) -> dict:
        """
        获取任务执行日志service

        :param query_db: orm对象
        :param task_id: 任务ID
        :param skip: 跳过条数
        :param limit: 返回条数
        :return: 执行日志
        """
        import sys
        import os
        from sqlalchemy import select, desc
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        try:
            from src.models.sqlalchemy_models import ExecutionRecord as ExecutionRecordModel
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        # 获取最新的执行记录
        result = await query_db.execute(
            select(ExecutionRecordModel)
            .where(ExecutionRecordModel.task_id == task_id)
            .order_by(desc(ExecutionRecordModel.start_time))
            .limit(1)
        )
        execution_record = result.scalar_one_or_none()
        
        if not execution_record:
            return {"logs": [], "total": 0}
        
        # 从执行记录的logs字段解析日志
        logs = []
        if execution_record.logs:
            import json
            try:
                log_data = json.loads(execution_record.logs) if isinstance(execution_record.logs, str) else execution_record.logs
                if isinstance(log_data, list):
                    logs = log_data[skip:skip+limit]
            except:
                # 如果解析失败，返回原始日志文本
                logs = [{"level": "info", "message": execution_record.logs, "timestamp": execution_record.start_time.isoformat()}]
        
        return {
            "logs": logs,
            "total": len(logs),
            "execution_id": execution_record.id
        }
    
    @classmethod
    async def parse_natural_language_task_services(cls, query_db: AsyncSession, parse_data: dict) -> dict:
        """
        解析自然语言任务service

        :param query_db: orm对象
        :param parse_data: 解析数据，包含description字段
        :return: 解析结果
        """
        import sys
        import os
        
        automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
        if automation_path not in sys.path:
            sys.path.insert(0, automation_path)
        
        description = parse_data.get("description", "")
        if not description:
            raise ServiceException(message='描述不能为空')
        
        try:
            from src.ai.agent import TaskPlanner
            from src.ai.llm import create_llm_provider
            from src.models.sqlalchemy_models import ModelConfig as ModelConfigModel
            from sqlalchemy import select
        except ImportError as e:
            raise ServiceException(message=f'无法导入Automation Framework模块: {str(e)}')
        
        # 获取默认的LLM配置
        result = await query_db.execute(
            select(ModelConfigModel)
            .where(ModelConfigModel.enabled == True)
            .limit(1)
        )
        model_config = result.scalar_one_or_none()
        
        if not model_config:
            raise ServiceException(message='未配置LLM模型，请先配置模型')
        
        # 创建LLM提供者和TaskPlanner
        llm = create_llm_provider(model_config)
        planner = TaskPlanner(llm)
        
        # 解析任务
        task_desc = await planner.parse_task(description)
        
        # 生成计划
        plan = await planner.plan(task_desc)
        
        # 转换为Action对象
        actions = []
        for step in plan:
            actions.append(step)
        
        return {
            "success": True,
            "task_description": {
                "goal": task_desc.goal,
                "constraints": task_desc.constraints,
                "parameters": task_desc.parameters,
                "context": task_desc.context
            },
            "actions": actions,
            "total_actions": len(actions)
        }
