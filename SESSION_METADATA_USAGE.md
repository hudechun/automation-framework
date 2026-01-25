# Session Metadata 使用说明

## 📋 概述

根据实际数据库结构，`sessions` 表只有 `metadata` 字段（JSON类型），因此 `user_id` 和 `task_id` 存储在 `metadata` JSON 中，而不是作为独立字段。

## 🔧 数据结构

### Session Metadata 格式

```json
{
    "task_id": "123",
    "user_id": 1,
    "其他元数据": "..."
}
```

## 📝 代码使用

### 1. 创建 Session 时设置 metadata

```python
from automation_framework.src.core.session import SessionManager

session_manager = get_global_session_manager(db_session=db)
session = await session_manager.create_session(
    driver_type=DriverType.BROWSER,
    metadata={
        "task_id": task_id,
        "user_id": user_id
    },
    db_session=db
)
```

### 2. 从 Session 中提取 user_id 和 task_id

```python
from automation_framework.src.core.session_utils import (
    get_user_id_from_metadata,
    get_task_id_from_metadata
)

# 从session metadata中提取
user_id = get_user_id_from_metadata(session.metadata)
task_id = get_task_id_from_metadata(session.metadata)
```

### 3. 查询 Session（使用 JSON_EXTRACT）

```python
from sqlalchemy import select, func
from automation_framework.src.models.sqlalchemy_models import Session as SessionModel

# 按task_id查询
result = await db.execute(
    select(SessionModel)
    .where(
        func.json_extract(SessionModel.metadata, '$.task_id') == task_id
    )
    .order_by(SessionModel.updated_at.desc())
    .limit(1)
)

# 按user_id查询
result = await db.execute(
    select(SessionModel)
    .where(
        func.json_extract(SessionModel.metadata, '$.user_id') == user_id
    )
)
```

## 🔍 工具函数

已创建 `automation-framework/src/core/session_utils.py` 提供便捷函数：

- `get_user_id_from_metadata(metadata)` - 从metadata中提取user_id
- `get_task_id_from_metadata(metadata)` - 从metadata中提取task_id
- `set_user_id_in_metadata(metadata, user_id)` - 在metadata中设置user_id
- `set_task_id_in_metadata(metadata, task_id)` - 在metadata中设置task_id

## ⚠️ 注意事项

1. **查询性能**：使用 JSON_EXTRACT 查询性能可能不如独立字段，如果数据量大，考虑添加独立字段和索引
2. **数据一致性**：确保创建 session 时总是设置 task_id 和 user_id
3. **向后兼容**：现有代码中从 metadata 读取 task_id 的方式保持不变

## 📊 数据库迁移

如果将来需要将 `user_id` 和 `task_id` 作为独立字段，可以：

1. 执行迁移脚本的方案A（添加独立字段）
2. 更新 SQLAlchemy 模型，取消注释 `user_id` 和 `task_id` 字段
3. 迁移现有数据：从 metadata 中提取并填充到新字段

---

## ✅ 已更新的代码

1. ✅ `executor.py` - 创建 session 时在 metadata 中设置 user_id 和 task_id
2. ✅ `executor.py` - resume_task 中使用 JSON_EXTRACT 查询 session
3. ✅ `session_utils.py` - 新增工具函数
4. ✅ `sqlalchemy_models.py` - 注释掉 user_id 和 task_id 字段（可选）
5. ✅ `add_user_fields.sql` - 更新迁移脚本，提供两种方案
