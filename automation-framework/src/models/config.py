"""
配置和日志相关数据模型
"""
from tortoise import fields
from tortoise.models import Model


class ModelConfig(Model):
    """模型配置"""
    
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True, index=True)
    provider = fields.CharField(max_length=50)  # openai, anthropic, ollama
    model = fields.CharField(max_length=100)
    api_key = fields.CharField(max_length=255, null=True)
    params = fields.JSONField(null=True)  # 模型参数
    enabled = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "model_configs"


class ModelMetrics(Model):
    """模型性能指标"""
    
    id = fields.IntField(pk=True)
    model_config = fields.ForeignKeyField("models.ModelConfig", related_name="metrics")
    latency = fields.FloatField()  # 延迟（秒）
    cost = fields.FloatField(null=True)  # 成本
    tokens = fields.IntField(null=True)  # token数
    success = fields.BooleanField(default=True)
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "model_metrics"
        indexes = [("model_config_id",), ("created_at",)]


class SystemLog(Model):
    """系统日志"""
    
    id = fields.IntField(pk=True)
    level = fields.CharField(max_length=20)  # debug, info, warning, error, critical
    message = fields.TextField()
    module = fields.CharField(max_length=255, null=True)
    function = fields.CharField(max_length=255, null=True)
    line_number = fields.IntField(null=True)
    extra_data = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "system_logs"
        indexes = [("level",), ("created_at",)]


class NotificationConfig(Model):
    """通知配置"""
    
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    notification_type = fields.CharField(max_length=50)  # email, webhook, slack, dingtalk, wechat_work
    config = fields.JSONField()  # 通知配置
    enabled = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "notification_configs"
