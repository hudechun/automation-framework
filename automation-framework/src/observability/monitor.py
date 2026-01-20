"""
实时监控系统
"""
import psutil
import time
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class TaskMetrics:
    """任务指标"""
    task_id: str
    start_time: str
    end_time: Optional[str]
    duration: Optional[float]
    status: str
    action_count: int
    error_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class MetricsCollector:
    """
    指标收集器
    """
    
    def __init__(self):
        self.system_metrics: List[SystemMetrics] = []
        self.task_metrics: Dict[str, TaskMetrics] = {}
        self._last_network = psutil.net_io_counters()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """
        收集系统指标
        
        Returns:
            系统指标
        """
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # 网络使用
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent / (1024 * 1024)
        network_recv_mb = network.bytes_recv / (1024 * 1024)
        
        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_percent=disk_percent,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb
        )
        
        self.system_metrics.append(metrics)
        return metrics
    
    def start_task_metrics(self, task_id: str) -> None:
        """
        开始收集任务指标
        
        Args:
            task_id: 任务ID
        """
        self.task_metrics[task_id] = TaskMetrics(
            task_id=task_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration=None,
            status="running",
            action_count=0,
            error_count=0
        )
    
    def update_task_metrics(
        self,
        task_id: str,
        action_count: Optional[int] = None,
        error_count: Optional[int] = None,
        status: Optional[str] = None
    ) -> None:
        """
        更新任务指标
        
        Args:
            task_id: 任务ID
            action_count: 操作数量
            error_count: 错误数量
            status: 状态
        """
        if task_id not in self.task_metrics:
            return
        
        metrics = self.task_metrics[task_id]
        
        if action_count is not None:
            metrics.action_count = action_count
        if error_count is not None:
            metrics.error_count = error_count
        if status is not None:
            metrics.status = status
    
    def end_task_metrics(self, task_id: str) -> None:
        """
        结束任务指标收集
        
        Args:
            task_id: 任务ID
        """
        if task_id not in self.task_metrics:
            return
        
        metrics = self.task_metrics[task_id]
        metrics.end_time = datetime.now().isoformat()
        
        # 计算持续时间
        start = datetime.fromisoformat(metrics.start_time)
        end = datetime.fromisoformat(metrics.end_time)
        metrics.duration = (end - start).total_seconds()
    
    def get_task_metrics(self, task_id: str) -> Optional[TaskMetrics]:
        """
        获取任务指标
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务指标
        """
        return self.task_metrics.get(task_id)
    
    def get_recent_system_metrics(self, count: int = 10) -> List[SystemMetrics]:
        """
        获取最近的系统指标
        
        Args:
            count: 数量
            
        Returns:
            系统指标列表
        """
        return self.system_metrics[-count:]


StatusCallback = Callable[[str, Dict[str, Any]], None]


class PerformanceMonitor:
    """
    性能监控器 - 实时监控和回调
    """
    
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.collector = MetricsCollector()
        self.callbacks: List[StatusCallback] = []
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    def register_callback(self, callback: StatusCallback) -> None:
        """
        注册状态回调
        
        Args:
            callback: 回调函数
        """
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: StatusCallback) -> None:
        """
        取消注册回调
        
        Args:
            callback: 回调函数
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, event: str, data: Dict[str, Any]) -> None:
        """
        通知所有回调
        
        Args:
            event: 事件名称
            data: 事件数据
        """
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def start(self) -> None:
        """启动监控"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self) -> None:
        """停止监控"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self) -> None:
        """监控循环"""
        while self.running:
            try:
                # 收集系统指标
                metrics = self.collector.collect_system_metrics()
                
                # 通知回调
                self._notify_callbacks("system_metrics", metrics.to_dict())
                
                # 检查告警条件
                self._check_alerts(metrics)
                
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(self.interval)
    
    def _check_alerts(self, metrics: SystemMetrics) -> None:
        """
        检查告警条件
        
        Args:
            metrics: 系统指标
        """
        # CPU告警
        if metrics.cpu_percent > 90:
            self._notify_callbacks("alert", {
                "type": "cpu_high",
                "value": metrics.cpu_percent,
                "threshold": 90
            })
        
        # 内存告警
        if metrics.memory_percent > 90:
            self._notify_callbacks("alert", {
                "type": "memory_high",
                "value": metrics.memory_percent,
                "threshold": 90
            })
        
        # 磁盘告警
        if metrics.disk_percent > 90:
            self._notify_callbacks("alert", {
                "type": "disk_high",
                "value": metrics.disk_percent,
                "threshold": 90
            })
    
    def on_task_start(self, task_id: str) -> None:
        """
        任务开始回调
        
        Args:
            task_id: 任务ID
        """
        self.collector.start_task_metrics(task_id)
        self._notify_callbacks("task_start", {"task_id": task_id})
    
    def on_task_end(self, task_id: str, status: str) -> None:
        """
        任务结束回调
        
        Args:
            task_id: 任务ID
            status: 任务状态
        """
        self.collector.update_task_metrics(task_id, status=status)
        self.collector.end_task_metrics(task_id)
        
        metrics = self.collector.get_task_metrics(task_id)
        if metrics:
            self._notify_callbacks("task_end", metrics.to_dict())
    
    def on_action_execute(
        self,
        task_id: str,
        action_type: str,
        duration: float
    ) -> None:
        """
        操作执行回调
        
        Args:
            task_id: 任务ID
            action_type: 操作类型
            duration: 执行时间
        """
        self._notify_callbacks("action_execute", {
            "task_id": task_id,
            "action_type": action_type,
            "duration": duration
        })
    
    def on_error(self, task_id: str, error: Exception) -> None:
        """
        错误回调
        
        Args:
            task_id: 任务ID
            error: 异常对象
        """
        if task_id in self.collector.task_metrics:
            metrics = self.collector.task_metrics[task_id]
            metrics.error_count += 1
        
        self._notify_callbacks("error", {
            "task_id": task_id,
            "error": str(error),
            "error_type": type(error).__name__
        })
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取当前状态
        
        Returns:
            状态字典
        """
        recent_metrics = self.collector.get_recent_system_metrics(1)
        current_metrics = recent_metrics[0] if recent_metrics else None
        
        return {
            "running": self.running,
            "current_metrics": current_metrics.to_dict() if current_metrics else None,
            "active_tasks": len([
                m for m in self.collector.task_metrics.values()
                if m.status == "running"
            ])
        }
