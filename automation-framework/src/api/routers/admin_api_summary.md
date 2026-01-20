# FastAPIAdmin 后台接口文档

## 接口分类

所有接口前缀：`/admin/api`

### 1. 任务管理 (Tasks)

- `GET /admin/api/tasks` - 获取任务列表（分页、搜索、过滤）
- `GET /admin/api/tasks/{task_id}` - 获取任务详情
- `POST /admin/api/tasks` - 创建任务
- `PUT /admin/api/tasks/{task_id}` - 更新任务
- `DELETE /admin/api/tasks/{task_id}` - 删除任务
- `POST /admin/api/tasks/{task_id}/execute` - 执行任务
- `POST /admin/api/tasks/{task_id}/pause` - 暂停任务
- `POST /admin/api/tasks/{task_id}/resume` - 恢复任务
- `POST /admin/api/tasks/{task_id}/stop` - 停止任务

### 2. 调度管理 (Schedules)

- `GET /admin/api/schedules` - 获取调度列表（分页、过滤）
- `GET /admin/api/schedules/{schedule_id}` - 获取调度详情
- `PUT /admin/api/schedules/{schedule_id}/enable` - 启用/禁用调度
- `DELETE /admin/api/schedules/{schedule_id}` - 删除调度

### 3. 执行记录 (ExecutionRecords)

- `GET /admin/api/executions` - 获取执行记录列表（分页、过滤）
- `GET /admin/api/executions/{execution_id}` - 获取执行记录详情
- `DELETE /admin/api/executions/{execution_id}` - 删除执行记录

### 4. 会话管理 (Sessions)

- `GET /admin/api/sessions` - 获取会话列表（分页、过滤）
- `GET /admin/api/sessions/{session_id}` - 获取会话详情
- `DELETE /admin/api/sessions/{session_id}` - 删除会话

### 5. 会话检查点 (SessionCheckpoints)

- `GET /admin/api/checkpoints` - 获取检查点列表（分页、过滤）
- `GET /admin/api/checkpoints/{checkpoint_id}` - 获取检查点详情

### 6. 模型配置 (ModelConfigs)

- `GET /admin/api/model-configs` - 获取模型配置列表（分页、搜索、过滤）
- `GET /admin/api/model-configs/{config_id}` - 获取模型配置详情
- `POST /admin/api/model-configs` - 创建模型配置
- `PUT /admin/api/model-configs/{config_id}` - 更新模型配置
- `DELETE /admin/api/model-configs/{config_id}` - 删除模型配置

### 7. 模型指标 (ModelMetrics)

- `GET /admin/api/model-metrics` - 获取模型指标列表（分页、过滤）

### 8. 系统日志 (SystemLogs)

- `GET /admin/api/system-logs` - 获取系统日志列表（分页、过滤）
- `DELETE /admin/api/system-logs` - 清理系统日志（保留最近N天）

### 9. 通知配置 (NotificationConfigs)

- `GET /admin/api/notification-configs` - 获取通知配置列表（分页、过滤）
- `POST /admin/api/notification-configs` - 创建通知配置
- `DELETE /admin/api/notification-configs/{config_id}` - 删除通知配置

### 10. 文件存储 (FileStorage)

- `GET /admin/api/files` - 获取文件列表（分页、过滤）
- `DELETE /admin/api/files/{file_id}` - 删除文件记录

### 11. 插件管理 (Plugins)

- `GET /admin/api/plugins` - 获取插件列表（分页、搜索、过滤）
- `PUT /admin/api/plugins/{plugin_id}/enable` - 启用/禁用插件

### 12. 性能指标 (PerformanceMetrics)

- `GET /admin/api/performance-metrics` - 获取性能指标列表（分页、过滤）

### 13. 仪表板统计 (Dashboard)

- `GET /admin/api/dashboard/stats` - 获取仪表板统计数据
- `GET /admin/api/dashboard/recent-executions` - 获取最近执行记录
- `GET /admin/api/dashboard/task-success-rate` - 获取任务成功率统计

## 通用响应格式

### 分页响应 (PaginatedResponse)
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 成功响应 (SuccessResponse)
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

### 错误响应
```json
{
  "detail": "Error message"
}
```

## 查询参数说明

### 通用分页参数
- `page`: 页码（从1开始）
- `page_size`: 每页数量（1-100）

### 通用过滤参数
- `search`: 搜索关键词（用于名称、描述等字段）
- `start_date`: 开始日期（ISO格式）
- `end_date`: 结束日期（ISO格式）

## 使用示例

### 获取任务列表
```bash
GET /admin/api/tasks?page=1&page_size=20&status=running&search=test
```

### 创建任务
```bash
POST /admin/api/tasks
Content-Type: application/json

{
  "name": "测试任务",
  "description": "任务描述",
  "task_type": "browser",
  "actions": [...],
  "config": {}
}
```

### 执行任务
```bash
POST /admin/api/tasks/1/execute
```

### 获取仪表板统计
```bash
GET /admin/api/dashboard/stats
```
