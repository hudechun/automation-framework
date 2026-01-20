"""
会话相关数据模型
"""
from tortoise import fields
from tortoise.models import Model


class Session(Model):
    """会话模型"""
    
    id = fields.IntField(pk=True)
    session_id = fields.CharField(max_length=255, unique=True, index=True)
    state = fields.CharField(max_length=50, default="created")  # created, running, paused, stopped, failed
    driver_type = fields.CharField(max_length=50)  # browser, desktop
    metadata = fields.JSONField(null=True)  # 会话元数据
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "sessions"
        indexes = [("session_id",), ("state",)]


class SessionCheckpoint(Model):
    """会话检查点模型"""
    
    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField("models.Session", related_name="checkpoints")
    checkpoint_name = fields.CharField(max_length=255)
    state_data = fields.JSONField()  # 状态数据
    actions_completed = fields.IntField(default=0)  # 已完成的操作数
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "session_checkpoints"
        indexes = [("session_id",), ("created_at",)]
