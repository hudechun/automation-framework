"""
通知历史管理
"""
from typing import List, Optional
from datetime import datetime
import asyncio


class NotificationHistory:
    """通知历史记录"""
    
    def __init__(self):
        self.history: List[dict] = []
        self.retry_queue: List[dict] = []
    
    async def record(
        self,
        channel: str,
        message: str,
        status: str,
        recipient: Optional[str] = None,
        error: Optional[str] = None
    ):
        """记录通知历史"""
        record = {
            "id": f"notif_{len(self.history)}",
            "channel": channel,
            "message": message,
            "status": status,  # pending, sent, failed
            "recipient": recipient,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "retry_count": 0
        }
        self.history.append(record)
        
        # 如果失败，加入重试队列
        if status == "failed":
            self.retry_queue.append(record)
    
    async def retry_failed(self, max_retries: int = 3):
        """重试失败的通知"""
        from .base import notification_manager
        
        retry_list = self.retry_queue.copy()
        self.retry_queue.clear()
        
        for record in retry_list:
            if record["retry_count"] >= max_retries:
                continue
            
            # 指数退避
            wait_time = 2 ** record["retry_count"]
            await asyncio.sleep(wait_time)
            
            try:
                success = await notification_manager.send_notification(
                    record["channel"],
                    record["message"]
                )
                
                if success:
                    record["status"] = "sent"
                else:
                    record["retry_count"] += 1
                    if record["retry_count"] < max_retries:
                        self.retry_queue.append(record)
            except Exception as e:
                record["retry_count"] += 1
                record["error"] = str(e)
                if record["retry_count"] < max_retries:
                    self.retry_queue.append(record)
    
    def get_history(
        self,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """获取通知历史"""
        filtered = self.history
        
        if channel:
            filtered = [r for r in filtered if r["channel"] == channel]
        
        if status:
            filtered = [r for r in filtered if r["status"] == status]
        
        return filtered[-limit:]
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        total = len(self.history)
        sent = len([r for r in self.history if r["status"] == "sent"])
        failed = len([r for r in self.history if r["status"] == "failed"])
        pending = len([r for r in self.history if r["status"] == "pending"])
        
        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "pending": pending,
            "success_rate": (sent / total * 100) if total > 0 else 0
        }


# 全局历史管理器
notification_history = NotificationHistory()
