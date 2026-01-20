"""
任务相关数据模型
"""
from tortoise import fields
from tortoise.models import Model
from datetime import datetime


class Task(Model):
    """任务模型"""
    
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, index=True)
    description = fields.TextField(null=True)
    task_type = fields.CharField(max_length=50)  # browser, desktop, hybrid
    actions = fields.JSONField()  # 操作列表
    config = fields.JSONField(null=True)  # 任务配置
    status = fields.CharField(max_length=50, default="pending")  # pending, running, completed, failed
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "tasks"
        indexes = [("name",), ("status",), ("created_at",)]


class Schedule(Model):
    """调度模型"""
    
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField("models.Task", related_name="schedules")
    schedule_type = fields.CharField(max_length=50)  # once, interval, cron
    schedule_config = fields.JSONField()  # 调度配置
    enabled = fields.BooleanField(default=True)
    next_run_time = fields.DatetimeField(null=True)
    last_run_time = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "schedules"
        indexes = [("enabled",), ("next_run_time",)]


class ExecutionRecord(Model):
    """执行记录模型"""
    
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField("models.Task", related_name="executions")
    status = fields.CharField(max_length=50)  # running, completed, failed
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField(null=True)
    duration = fields.IntField(null=True)  # 执行时长（秒）
    logs = fields.TextField(null=True)  # 执行日志
    screenshots = fields.JSONField(null=True)  # 截图路径列表
    error_message = fields.TextField(null=True)  # 错误信息
    error_stack = fields.TextField(null=True)  # 错误堆栈
    result = fields.JSONField(null=True)  # 执行结果
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "execution_records"
        indexes = [("task_id",), ("status",), ("start_time",)]
