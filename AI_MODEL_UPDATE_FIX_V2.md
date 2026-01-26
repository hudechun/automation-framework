# AI模型配置更新问题修复（V2）

## 问题描述

编辑AI模型配置时保存失败，错误信息：
```
Uncaught (in promise) Error: 更新失败: Unconsumed column names: max_tokens, temperature, top_p, api_base_url
```

## 问题分析

### 根本原因

前端发送的更新数据包含以下字段，但这些字段在 `module_admin` 的 DO 模型（`AiModelConfig`）中不存在：
- `top_p` - Top P参数
- `max_tokens` - 最大token数
- `temperature` - 温度参数
- `api_base_url` - API基础URL

当 SQLAlchemy 的 `update().values(**config_data)` 接收到不存在的字段时，会抛出 "Unconsumed column names" 错误。

## 修复方案

### 双层保护机制

#### 1. Service 层保护（`ai_model_service.py`）

在 `update_config` 方法中：

1. **识别特殊字段**：`top_p`, `max_tokens`, `temperature`, `api_base_url`
2. **字段映射**：
   - `top_p`, `max_tokens`, `temperature` → 合并到 `params` JSON 字段
   - `api_base_url` → 映射到 `api_endpoint` 字段（如果 `api_endpoint` 不在更新数据中）
3. **过滤普通字段**：只保留 DO 模型中存在的字段
4. **双重检查**：确保 `filtered_data` 中不包含任何特殊字段

#### 2. DAO 层保护（`ai_model_dao.py`）

在 `update_config` 方法中添加最终过滤：

```python
# 确保只使用 DO 模型中存在的字段
do_model_fields = {field.name for field in AiModelConfig.__table__.columns}
filtered_config_data = {k: v for k, v in config_data.items() if k in do_model_fields}
```

这提供了**第二层保护**，即使 Service 层有遗漏，DAO 层也会过滤掉不存在的字段。

### 字段映射关系

| 前端字段 | DO模型字段 | 处理方式 |
|---------|-----------|---------|
| `top_p` | `params.top_p` | 合并到 `params` JSON字段 |
| `max_tokens` | `params.max_tokens` | 合并到 `params` JSON字段 |
| `temperature` | `params.temperature` | 合并到 `params` JSON字段 |
| `api_base_url` | `api_endpoint` | 映射到 `api_endpoint` 字段 |

### 代码变更

#### Service 层 (`ai_model_service.py`)

```python
# 1. 识别特殊字段
special_fields = {'top_p', 'max_tokens', 'temperature', 'api_base_url'}

# 2. 处理特殊字段
for key, value in update_data.items():
    if key in special_fields:
        if key == 'api_base_url':
            if 'api_endpoint' not in update_data:
                filtered_data['api_endpoint'] = value
        elif key in ('top_p', 'temperature', 'max_tokens'):
            params_to_merge[key] = value  # 合并到 params

# 3. 双重检查
final_filtered_data = {}
for key, value in filtered_data.items():
    if key in do_model_fields and key not in special_fields:
        final_filtered_data[key] = value
```

#### DAO 层 (`ai_model_dao.py`)

```python
# 最终过滤保护
do_model_fields = {field.name for field in AiModelConfig.__table__.columns}
filtered_config_data = {k: v for k, v in config_data.items() if k in do_model_fields}
```

## 测试建议

1. **测试更新包含特殊字段的配置**：
   - 编辑AI模型配置
   - 修改 `top_p`, `max_tokens`, `temperature`, `api_base_url`
   - 保存并验证是否成功

2. **验证数据正确性**：
   - 检查 `params` JSON 字段是否包含合并的参数
   - 检查 `api_endpoint` 是否正确更新

3. **测试边界情况**：
   - 只更新普通字段（不包含特殊字段）
   - 只更新特殊字段
   - 同时更新 `api_endpoint` 和 `api_base_url`（应该优先使用 `api_endpoint`）
   - 更新时 params 为空或不存在

## 相关文件

- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/service/ai_model_service.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/dao/ai_model_dao.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/entity/do/ai_model_do.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/entity/vo/ai_model_vo.py`

## 总结

✅ **双层保护** - Service 层和 DAO 层都进行了字段过滤
✅ **字段映射** - 特殊字段正确映射到 DO 模型字段
✅ **数据完整性** - 新参数与现有 params 合并，不会覆盖其他参数
✅ **健壮性** - 即使 Service 层有遗漏，DAO 层也会过滤掉不存在的字段
