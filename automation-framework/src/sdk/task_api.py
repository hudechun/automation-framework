"""
任务管理API
"""
from typing import Dict, Any, List, Optional


class TaskAPI:
    """任务管理API"""
    
    def __init__(self, client):
        self.client = client
    
    async def create(
        self,
        name: str,
        description: str,
        actions: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建任务
        
        Args:
            name: 任务名称
            description: 任务描述
            actions: 操作列表
            **kwargs: 其他参数
            
        Returns:
            任务数据
        """
        data = {
            "name": name,
            "description": description,
            "actions": actions,
            **kwargs
        }
        return await self.client.request("POST", "/api/tasks", json=data)
    
    async def get(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务数据
        """
        return await self.client.request("GET", f"/api/tasks/{task_id}")
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        列出任务
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            **filters: 过滤条件
            
        Returns:
            任务列表
        """
        params = {"skip": skip, "limit": limit, **filters}
        return await self.client.request("GET", "/api/tasks", params=params)
    
    async def update(
        self,
        task_id: str,
        **updates
    ) -> Dict[str, Any]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            **updates: 更新字段
            
        Returns:
            更新后的任务数据
        """
        return await self.client.request(
            "PUT",
            f"/api/tasks/{task_id}",
            json=updates
        )
    
    async def delete(self, task_id: str) -> Dict[str, Any]:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            删除结果
        """
        return await self.client.request("DELETE", f"/api/tasks/{task_id}")
    
    async def execute(self, task_id: str) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            执行结果
        """
        return await self.client.request(
            "POST",
            f"/api/tasks/{task_id}/execute"
        )
    
    async def pause(self, task_id: str) -> Dict[str, Any]:
        """暂停任务"""
        return await self.client.request(
            "POST",
            f"/api/tasks/{task_id}/pause"
        )
    
    async def resume(self, task_id: str) -> Dict[str, Any]:
        """恢复任务"""
        return await self.client.request(
            "POST",
            f"/api/tasks/{task_id}/resume"
        )
    
    async def stop(self, task_id: str) -> Dict[str, Any]:
        """停止任务"""
        return await self.client.request(
            "POST",
            f"/api/tasks/{task_id}/stop"
        )
    
    async def execute_and_wait(
        self,
        task_id: str,
        poll_interval: float = 1.0,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        执行任务并等待完成
        
        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔
            timeout: 超时时间
            
        Returns:
            执行结果
        """
        import asyncio
        import time
        
        # 开始执行
        await self.execute(task_id)
        
        start_time = time.time()
        
        # 轮询状态
        while True:
            task = await self.get(task_id)
            status = task.get("status")
            
            if status in ["completed", "failed"]:
                return task
            
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                from .exceptions import TimeoutError
                raise TimeoutError(f"Task execution timeout: {task_id}")
            
            await asyncio.sleep(poll_interval)
