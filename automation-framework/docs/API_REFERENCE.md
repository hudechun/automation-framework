# API参考文档

## 核心API

### AutomationClient

主客户端类，用于与自动化框架交互。

```python
from src.sdk import AutomationClient

async with AutomationClient(base_url="http://localhost:8000") as client:
    # 使用client
    pass
```

### TaskAPI

任务管理API。

```python
# 创建任务
task = await client.tasks.create(
    name="Task Name",
    description="Task Description",
    actions=[...]
)

# 列出任务
tasks = await client.tasks.list(limit=10)

# 获取任务
task = await client.tasks.get(task_id)

# 更新任务
task = await client.tasks.update(task_id, name="New Name")

# 删除任务
await client.tasks.delete(task_id)

# 执行任务
await client.tasks.execute(task_id)

# 执行并等待完成
result = await client.tasks.execute_and_wait(task_id)
```

### SessionAPI

会话管理API。

```python
# 创建会话
session = await client.sessions.create(driver_type="browser")

# 列出会话
sessions = await client.sessions.list()

# 获取会话
session = await client.sessions.get(session_id)

# 暂停会话
await client.sessions.pause(session_id)

# 恢复会话
await client.sessions.resume(session_id)

# 停止会话
await client.sessions.stop(session_id)
```

### HistoryAPI

历史记录API。

```python
# 列出执行记录
records = await client.history.list(limit=10)

# 获取执行记录
record = await client.history.get(execution_id)

# 导出记录
await client.history.export(format="json")
```

## REST API端点

### 任务管理

- `POST /api/tasks` - 创建任务
- `GET /api/tasks` - 列出任务
- `GET /api/tasks/{id}` - 获取任务详情
- `PUT /api/tasks/{id}` - 更新任务
- `DELETE /api/tasks/{id}` - 删除任务
- `POST /api/tasks/{id}/execute` - 执行任务
- `POST /api/tasks/{id}/pause` - 暂停任务
- `POST /api/tasks/{id}/resume` - 恢复任务
- `POST /api/tasks/{id}/stop` - 停止任务

### 会话管理

- `POST /api/sessions` - 创建会话
- `GET /api/sessions` - 列出会话
- `GET /api/sessions/{id}` - 获取会话详情
- `POST /api/sessions/{id}/pause` - 暂停会话
- `POST /api/sessions/{id}/resume` - 恢复会话
- `POST /api/sessions/{id}/stop` - 停止会话

### 历史记录

- `GET /api/executions` - 列出执行记录
- `GET /api/executions/{id}` - 获取执行详情
- `POST /api/executions/export` - 导出记录

### 监控

- `GET /api/monitor/system` - 系统状态
- `GET /api/monitor/metrics` - 性能指标
- `GET /api/monitor/health` - 健康检查

## 数据模型

### Task

```python
{
    "id": "task_123",
    "name": "Task Name",
    "description": "Task Description",
    "actions": [...],
    "config": {...},
    "status": "pending",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### Session

```python
{
    "id": "session_123",
    "driver_type": "browser",
    "state": "running",
    "created_at": "2024-01-01T00:00:00",
    "metadata": {...}
}
```

### ExecutionRecord

```python
{
    "id": "exec_123",
    "task_id": "task_123",
    "status": "completed",
    "started_at": "2024-01-01T00:00:00",
    "completed_at": "2024-01-01T00:01:00",
    "duration": 60.0,
    "logs": [...],
    "screenshots": [...]
}
```

## 错误处理

所有API调用可能抛出以下异常：

- `APIError` - 通用API错误
- `AuthenticationError` - 认证失败
- `ValidationError` - 参数验证失败
- `NotFoundError` - 资源不存在
- `RateLimitError` - 超过速率限制

```python
from src.sdk.exceptions import APIError

try:
    task = await client.tasks.get("invalid_id")
except APIError as e:
    print(f"Error: {e}")
```
