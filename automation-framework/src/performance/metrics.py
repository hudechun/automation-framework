"""
性能指标收集
"""
import psutil
import asyncio
from typing import Dict, List
from datetime import datetime


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics_history: List[dict] = []
        self.collection_task = None
    
    async def collect_system_metrics(self) -> dict:
        """收集系统指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        except:
            network_stats = {"bytes_sent": 0, "bytes_recv": 0}
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_available": memory.available,
            "disk_usage": disk.percent,
            "disk_free": disk.free,
            "network": network_stats
        }
        
        return metrics
    
    async def collect_task_metrics(self) -> dict:
        """收集任务指标"""
        # TODO: 从任务管理器获取实际数据
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": 0,
            "running_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
        
        return metrics
    
    async def collect_model_metrics(self) -> dict:
        """收集模型指标"""
        # TODO: 从AI模块获取实际数据
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_calls": 0,
            "average_latency": 0.0,
            "total_cost": 0.0,
            "total_tokens": 0
        }
        
        return metrics
    
    async def collect_all_metrics(self) -> dict:
        """收集所有指标"""
        system_metrics = await self.collect_system_metrics()
        task_metrics = await self.collect_task_metrics()
        model_metrics = await self.collect_model_metrics()
        
        all_metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": system_metrics,
            "tasks": task_metrics,
            "models": model_metrics
        }
        
        self.metrics_history.append(all_metrics)
        
        # 保持最近1000条记录
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return all_metrics
    
    async def start_collection(self, interval: int = 60):
        """启动定期收集"""
        async def collect_loop():
            while True:
                try:
                    await self.collect_all_metrics()
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"Metrics collection error: {e}")
                    await asyncio.sleep(interval)
        
        self.collection_task = asyncio.create_task(collect_loop())
    
    async def stop_collection(self):
        """停止收集"""
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
    
    def get_recent_metrics(self, limit: int = 100) -> List[dict]:
        """获取最近的指标"""
        return self.metrics_history[-limit:]
    
    def get_metrics_summary(self) -> dict:
        """获取指标摘要"""
        if not self.metrics_history:
            return {}
        
        recent = self.metrics_history[-10:]
        
        avg_cpu = sum(m["system"]["cpu_usage"] for m in recent) / len(recent)
        avg_memory = sum(m["system"]["memory_usage"] for m in recent) / len(recent)
        avg_disk = sum(m["system"]["disk_usage"] for m in recent) / len(recent)
        
        return {
            "average_cpu_usage": round(avg_cpu, 2),
            "average_memory_usage": round(avg_memory, 2),
            "average_disk_usage": round(avg_disk, 2),
            "sample_count": len(recent)
        }


# 全局性能指标收集器
performance_metrics = PerformanceMetrics()
