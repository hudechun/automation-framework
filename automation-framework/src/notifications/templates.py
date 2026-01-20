"""
通知模板管理
"""
from jinja2 import Template
from typing import Dict, Optional


class NotificationTemplate:
    """通知模板"""
    
    def __init__(self, name: str, template: str, description: str = ""):
        self.name = name
        self.template = template
        self.description = description
        self._jinja_template = Template(template)
    
    def render(self, **context) -> str:
        """渲染模板"""
        return self._jinja_template.render(**context)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        # 任务完成模板
        self.register_template(
            "task_completed",
            """
✅ **任务完成通知**

**任务名称**: {{ task_name }}
**任务ID**: {{ task_id }}
**执行状态**: {{ status }}
**执行时间**: {{ duration }}秒
**完成时间**: {{ completed_at }}

{% if result %}
**执行结果**: {{ result }}
{% endif %}
            """.strip(),
            "任务完成通知模板"
        )
        
        # 任务失败模板
        self.register_template(
            "task_failed",
            """
❌ **任务失败通知**

**任务名称**: {{ task_name }}
**任务ID**: {{ task_id }}
**失败原因**: {{ error_message }}
**失败时间**: {{ failed_at }}

{% if screenshot_url %}
**错误截图**: {{ screenshot_url }}
{% endif %}

{% if retry_count %}
**重试次数**: {{ retry_count }}
{% endif %}
            """.strip(),
            "任务失败通知模板"
        )
        
        # 系统告警模板
        self.register_template(
            "system_alert",
            """
⚠️ **系统告警**

**告警类型**: {{ alert_type }}
**告警级别**: {{ severity }}
**告警信息**: {{ message }}
**发生时间**: {{ timestamp }}

{% if metrics %}
**系统指标**:
- CPU使用率: {{ metrics.cpu_usage }}%
- 内存使用率: {{ metrics.memory_usage }}%
- 磁盘使用率: {{ metrics.disk_usage }}%
{% endif %}
            """.strip(),
            "系统告警通知模板"
        )
        
        # 定时任务提醒模板
        self.register_template(
            "scheduled_task_reminder",
            """
🔔 **定时任务提醒**

**任务名称**: {{ task_name }}
**任务ID**: {{ task_id }}
**计划执行时间**: {{ scheduled_time }}
**任务描述**: {{ description }}
            """.strip(),
            "定时任务提醒模板"
        )
    
    def register_template(self, name: str, template: str, description: str = ""):
        """注册模板"""
        self.templates[name] = NotificationTemplate(name, template, description)
    
    def get_template(self, name: str) -> Optional[NotificationTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def render_template(self, name: str, **context) -> str:
        """渲染模板"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        return template.render(**context)
    
    def list_templates(self) -> Dict[str, str]:
        """列出所有模板"""
        return {
            name: template.description
            for name, template in self.templates.items()
        }


# 全局模板管理器
template_manager = TemplateManager()
