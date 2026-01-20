"""
文件和插件相关数据模型
"""
from tortoise import fields
from tortoise.models import Model


class FileStorage(Model):
    """文件存储"""
    
    id = fields.IntField(pk=True)
    file_name = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=512)
    file_type = fields.CharField(max_length=50)  # screenshot, log, video, export
    file_size = fields.IntField()  # 文件大小（字节）
    mime_type = fields.CharField(max_length=100, null=True)
    related_type = fields.CharField(max_length=50, null=True)  # task, execution, session
    related_id = fields.IntField(null=True)
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "file_storage"
        indexes = [("file_type",), ("related_type", "related_id"), ("created_at",)]


class Plugin(Model):
    """插件"""
    
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True, index=True)
    version = fields.CharField(max_length=50)
    description = fields.TextField(null=True)
    plugin_type = fields.CharField(max_length=50)  # action, driver, agent, integration
    manifest = fields.JSONField()  # 插件清单
    config = fields.JSONField(null=True)  # 插件配置
    enabled = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "plugins"


class PerformanceMetrics(Model):
    """性能指标"""
    
    id = fields.IntField(pk=True)
    metric_type = fields.CharField(max_length=50)  # cpu, memory, disk, network, task
    metric_name = fields.CharField(max_length=100)
    value = fields.FloatField()
    unit = fields.CharField(max_length=20, null=True)
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "performance_metrics"
        indexes = [("metric_type",), ("metric_name",), ("created_at",)]
