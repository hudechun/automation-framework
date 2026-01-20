# -*- coding: utf-8 -*-
"""
任务执行器 - 对接automation-framework执行逻辑
"""
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import asyncio

# 添加automation-framework到Python路径
automation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../automation-framework'))
if automation_path not in sys.path:
    sys.path.insert(0, automation_path)


class TaskExecutor:
    """
    任务执行器 - 负责执行自动化任务
    """
    
    def __init__(self):
        """初始化执行器"""
        self._running_tasks: Dict[int, Dict[str, Any]] = {}
        
    async def execute_task(
        self,
        task_id: int,
        task_name: str,
        task_type: str,
        actions: list,
        config: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task_id: 任务ID
            task_name: 任务名称
            task_type: 任务类型（browser/desktop/hybrid）
            actions: 操作列表
            config: 任务配置
            
        Returns:
            执行结果
        """
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 创建执行记录
        execution_record = {
            'session_id': session_id,
            'task_id': task_id,
            'status': 'running',
            'start_time': datetime.now(),
            'actions': actions,
            'config': config or {}
        }
        
        # 记录运行中的任务
        self._running_tasks[task_id] = execution_record
        
        try:
            # TODO: 这里调用automation-framework的核心执行逻辑
            # 目前先返回模拟结果
            result = await self._execute_actions(task_type, actions, config)
            
            # 更新执行记录
            execution_record['status'] = 'completed'
            execution_record['end_time'] = datetime.now()
            execution_record['result'] = result
            
            return {
                'success': True,
                'session_id': session_id,
                'result': result,
                'message': '任务执行成功'
            }
            
        except Exception as e:
            # 执行失败
            execution_record['status'] = 'failed'
            execution_record['end_time'] = datetime.now()
            execution_record['error'] = str(e)
            
            return {
                'success': False,
                'session_id': session_id,
                'error': str(e),
                'message': '任务执行失败'
            }
        finally:
            # 清理运行记录
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
    
    async def _execute_actions(
        self,
        task_type: str,
        actions: list,
        config: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        执行操作列表
        
        Args:
            task_type: 任务类型
            actions: 操作列表
            config: 配置
            
        Returns:
            执行结果
        """
        # TODO: 集成automation-framework的实际执行逻辑
        # 这里先返回模拟结果
        
        # 模拟执行延迟
        await asyncio.sleep(2)
        
        return {
            'task_type': task_type,
            'actions_count': len(actions),
            'executed_at': datetime.now().isoformat(),
            'status': 'success'
        }
    
    def get_running_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        获取运行中的任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息，如果不存在返回None
        """
        return self._running_tasks.get(task_id)
    
    def is_task_running(self, task_id: int) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否正在运行
        """
        return task_id in self._running_tasks


# 全局执行器实例
_global_executor: Optional[TaskExecutor] = None


def get_task_executor() -> TaskExecutor:
    """获取全局任务执行器实例"""
    global _global_executor
    if _global_executor is None:
        _global_executor = TaskExecutor()
    return _global_executor
