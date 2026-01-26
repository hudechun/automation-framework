# AI模型配置更新问题修复

## 问题描述

编辑AI模型配置时保存失败，错误信息：
```
Uncaught (in promise) Error: 更新失败: Unconsumed column names: top_p, max_tokens, temperature, api_base_url
```

## 问题分析

### 根本原因

前端发送的更新数据包含以下字段：
- `top_p` - Top P参数
- `max_tokens` - 最大token数
- `temperature` - 温度参数
- `api_base_url` - API基础URL

但是 `module_admin` 的 DO 模型（`AiModelConfig`）中没有这些字段：
- DO 模型只有 `params`（JSON字段）用于存储模型参数
- DO 模型只有 `api_endpoint`，没有 `api_base_url`

当使用 SQLAlchemy 的 `update().values(**config_data)` 时，如果字典中包含模型不存在的字段，会抛出 "Unconsumed column names" 错误。

### 字段映射关系

| 前端字段 | DO模型字段 | 处理方式 |
|---------|-----------|---------|
| `top_p` | `params.top_p` | 合并到 `params` JSON字段 |
| `max_tokens` | `params.max_tokens` | 合并到 `params` JSON字段 |
| `temperature` | `params.temperature` | 合并到 `params` JSON字段 |
| `api_base_url` | `api_endpoint` | 映射到 `api_endpoint` 字段 |

## 修复方案

### 修复内容

在 `module_admin/service/ai_model_service.py` 的 `update_config` 方法中：

1. **过滤不存在的字段**：只保留 DO 模型中存在的字段
2. **特殊字段处理**：
   - `top_p`, `max_tokens`, `temperature` → 合并到 `params` JSON 字段
   - `api_base_url` → 映射到 `api_endpoint` 字段
3. **合并 params**：将新参数与现有 params 合并，避免覆盖

### 代码变更

```python
# 获取DO模型的所有字段名
do_model_fields = {field.name for field in AiModelConfig.__table__.columns}

# 分离普通字段和特殊字段
special_fields = {'top_p', 'max_tokens', 'temperature', 'api_base_url'}

# 处理特殊字段
for key, value in update_data.items():
    if key in special_fields:
        if key == 'api_base_url':
            filtered_data['api_endpoint'] = value
        elif key in ('top_p', 'temperature', 'max_tokens'):
            params_to_merge[key] = value
    
# 合并 params
if params_to_merge:
    existing_params = existing_config.params or {}
    merged_params = {**existing_params, **params_to_merge}
    filtered_data['params'] = merged_params
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
   - 更新时 params 为空或不存在

## 相关文件

- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/service/ai_model_service.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/entity/do/ai_model_do.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_admin/entity/vo/ai_model_vo.py`

## 总结

✅ **问题已修复** - 更新逻辑现在能正确处理前端发送的特殊字段
✅ **字段映射** - `top_p`, `max_tokens`, `temperature` 合并到 `params`，`api_base_url` 映射到 `api_endpoint`
✅ **数据完整性** - 新参数与现有 params 合并，不会覆盖其他参数
