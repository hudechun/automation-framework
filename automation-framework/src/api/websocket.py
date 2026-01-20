"""
WebSocket实时推送
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 所有活跃连接
        self.active_connections: List[WebSocket] = []
        # 按任务ID订阅的连接
        self.task_subscriptions: Dict[str, Set[WebSocket]] = {}
        # 心跳任务
        self.heartbeat_tasks: Dict[WebSocket, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        # 启动心跳
        task = asyncio.create_task(self._heartbeat(websocket))
        self.heartbeat_tasks[websocket] = task
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 取消心跳任务
        if websocket in self.heartbeat_tasks:
            self.heartbeat_tasks[websocket].cancel()
            del self.heartbeat_tasks[websocket]
        
        # 从所有订阅中移除
        for task_id, subscribers in self.task_subscriptions.items():
            if websocket in subscribers:
                subscribers.remove(websocket)
    
    async def _heartbeat(self, websocket: WebSocket):
        """心跳机制"""
        try:
            while True:
                await asyncio.sleep(30)  # 每30秒发送一次心跳
                await websocket.send_json({"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()})
        except Exception:
            pass
    
    def subscribe_task(self, websocket: WebSocket, task_id: str):
        """订阅任务状态"""
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = set()
        self.task_subscriptions[task_id].add(websocket)
    
    def unsubscribe_task(self, websocket: WebSocket, task_id: str):
        """取消订阅任务"""
        if task_id in self.task_subscriptions:
            self.task_subscriptions[task_id].discard(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_task_subscribers(self, task_id: str, message: dict):
        """发送消息给任务订阅者"""
        if task_id not in self.task_subscriptions:
            return
        
        disconnected = []
        for connection in self.task_subscriptions[task_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def push_task_status(self, task_id: str, status: str, data: dict = None):
        """推送任务状态变化"""
        message = {
            "type": "task_status",
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        await self.send_to_task_subscribers(task_id, message)
    
    async def push_log(self, task_id: str, level: str, message: str):
        """推送日志"""
        log_message = {
            "type": "log",
            "task_id": task_id,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_task_subscribers(task_id, log_message)
    
    async def push_system_event(self, event_type: str, data: dict):
        """推送系统事件"""
        message = {
            "type": "system_event",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)


# 全局连接管理器
manager = ConnectionManager()
