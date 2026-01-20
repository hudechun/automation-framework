"""
性能告警
"""
from typing import Dict, List, Callable
from datetime import datetime


class AlertRule:
    """告警规则"""
    
    def __init__(
        self,
        name: str,
        metric: str,
        threshold: float,
        duration: int = 60,
        severity: str = "warning"
    ):
        self.name = name
        self.metric = metric
        self.threshold = threshold
        self.duration = duration  # 持续时间（秒）
        self.severity = severity
        self.triggered_at = None
        self.is_active = False


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alert_history: List[dict] = []
        self.handlers: List[Callable] = []
    
    def add_rule(
        self,
        name: str,
        metric: str,
        threshold: float,
        duration: int = 60,
        severity: str = "warning"
    ):
        """添加告警规则"""
        rule = AlertRule(name, metric, threshold, duration, severity)
        self.rules[name] = rule
    
    def remove_rule(self, name: str):
        """移除告警规则"""
        if name in self.rules:
            del self.rules[name]
    
    def register_handler(self, handler: Callable):
        """注册告警处理器"""
        self.handlers.append(handler)
    
    async def check_metrics(self, metrics: dict):
        """检查指标是否触发告警"""
        current_time = datetime.now()
        
        for rule_name, rule in self.rules.items():
            # 提取指标值
            metric_value = self._extract_metric(metrics, rule.metric)
            
            if metric_value is None:
                continue
            
            # 检查是否超过阈值
            if metric_value > rule.threshold:
                if not rule.is_active:
                    rule.triggered_at = current_time
                    rule.is_active = True
                
                # 检查持续时间
                if rule.triggered_at:
                    duration = (current_time - rule.triggered_at).total_seconds()
                    if duration >= rule.duration:
                        # 触发告警
                        await self._trigger_alert(rule, metric_value, metrics)
            else:
                # 恢复正常
                if rule.is_active:
                    rule.is_active = False
                    rule.triggered_at = None
    
    def _extract_metric(self, metrics: dict, metric_path: str):
        """提取指标值"""
        parts = metric_path.split(".")
        value = metrics
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    async def _trigger_alert(self, rule: AlertRule, value: float, metrics: dict):
        """触发告警"""
        alert = {
            "rule_name": rule.name,
            "metric": rule.metric,
            "value": value,
            "threshold": rule.threshold,
            "severity": rule.severity,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        self.alert_history.append(alert)
        
        # 调用所有处理器
        for handler in self.handlers:
            try:
                await handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    def get_alert_history(self, limit: int = 100) -> List[dict]:
        """获取告警历史"""
        return self.alert_history[-limit:]
    
    def get_active_alerts(self) -> List[dict]:
        """获取活跃的告警"""
        return [
            {
                "name": rule.name,
                "metric": rule.metric,
                "threshold": rule.threshold,
                "severity": rule.severity,
                "triggered_at": rule.triggered_at.isoformat() if rule.triggered_at else None
            }
            for rule in self.rules.values()
            if rule.is_active
        ]


# 全局告警管理器
alert_manager = AlertManager()

# 添加默认告警规则
alert_manager.add_rule("high_cpu", "system.cpu_usage", 80.0, duration=300, severity="warning")
alert_manager.add_rule("high_memory", "system.memory_usage", 85.0, duration=300, severity="warning")
alert_manager.add_rule("high_disk", "system.disk_usage", 90.0, duration=600, severity="critical")
