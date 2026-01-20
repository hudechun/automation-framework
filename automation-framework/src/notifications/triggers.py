"""
通知触发器
"""
from typing import Callable, Dict, List
from datetime import datetime
from .base import notification_manager
from .templates import template_manager


class NotificationTrigger:
    """通知触发器"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def trigger(self, event_type: str, **context):
        """触发事件"""
        if event_type not in self.handlers:
            return
        
        for handler in self.handlers[event_type]:
            try:
                await handler(**context)
            except Exception as e:
                print(f"Handler error for {event_type}: {e}")


# 全局触发器
trigger = NotificationTrigger()


# 预定义触发器处理器
async def on_task_completed(task_id: str, task_name: str, status: str, duration: float, **kwargs):
    """任务完成触发器"""
    message = template_manager.render_template(
        "task_completed",
        task_id=task_id,
        task_name=task_name,
        status=status,
        duration=duration,
        completed_at=datetime.now().isoformat(),
        **kwargs
    )
    
    # 发送通知到所有配置的渠道
    await notification_manager.broadcast(message)


async def on_task_failed(task_id: str, task_name: str, error_message: str, **kwargs):
    """任务失败触发器"""
    message = template_manager.render_template(
        "task_failed",
        task_id=task_id,
        task_name=task_name,
        error_message=error_message,
        failed_at=datetime.now().isoformat(),
        **kwargs
    )
    
    # 发送通知到所有配置的渠道
    await notification_manager.broadcast(message)


async def on_system_alert(alert_type: str, severity: str, message: str, **kwargs):
    """系统告警触发器"""
    alert_message = template_manager.render_template(
        "system_alert",
        alert_type=alert_type,
        severity=severity,
        message=message,
        timestamp=datetime.now().isoformat(),
        **kwargs
    )
    
    # 发送通知到所有配置的渠道
    await notification_manager.broadcast(alert_message)


# 注册默认处理器
trigger.register_handler("task_completed", on_task_completed)
trigger.register_handler("task_failed", on_task_failed)
trigger.register_handler("system_alert", on_system_alert)
