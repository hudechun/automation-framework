# AI连接错误重试机制修复

## 问题描述

生成论文大纲时出现连接错误：
```
AI API调用失败: Connection error. (类型: APIConnectionError)
无法连接到AI服务: Connection error.。请检查: 1) 网络连接 2) API端点配置 3) 防火墙/代理设置
```

## 问题分析

### 根本原因

1. **网络连接问题**：可能是临时的网络波动或连接中断
2. **API端点配置错误**：API端点可能不正确或不可访问
3. **超时问题**：请求可能因为超时而被中断
4. **缺少重试机制**：连接错误没有被重试，导致临时网络问题无法自动恢复

## 修复方案

### 1. LLM Provider 层 - 添加连接错误重试

在所有 LLM Provider（OpenAIProvider, AnthropicProvider, QwenProvider）中添加连接错误的重试逻辑：

```python
# 检查是否是连接错误（可重试）
is_connection_error = (
    "connection" in error_str or
    "timeout" in error_str or
    "network" in error_str or
    "unreachable" in error_str or
    "refused" in error_str or
    error_type in ("APIConnectionError", "ConnectionError", "TimeoutError", "ConnectTimeout")
)

# 连接错误和限流错误都可以重试
if (is_connection_error or is_rate_limit) and attempt < max_retries - 1:
    delay = base_delay * (2 ** attempt)  # 指数退避：1s, 2s, 4s
    await asyncio.sleep(delay)
    continue
```

### 2. Service 层 - 增强错误诊断

在 `ai_generation_service.py` 中：

1. **记录配置信息**：在创建提供商时记录详细的配置信息
2. **增强错误信息**：提供更详细的错误诊断信息，包括 API 端点、模型等

```python
# 记录配置信息（用于诊断）
logger.info(
    f"创建AI提供商 - Provider: {provider_value}, "
    f"Model: {config.model_version}, "
    f"API Endpoint: {config.api_endpoint or '默认'}, "
    f"Config ID: {config.config_id}"
)
```

### 3. 错误处理优化

- **连接错误**：自动重试 3 次，使用指数退避（1s, 2s, 4s）
- **限流错误**：自动重试 3 次，使用指数退避
- **其他错误**：提供详细的错误信息，包括错误类型和上下文

## 重试策略

| 错误类型 | 是否重试 | 重试次数 | 退避策略 |
|---------|---------|---------|---------|
| 连接错误 | ✅ 是 | 3次 | 指数退避（1s, 2s, 4s） |
| 超时错误 | ✅ 是 | 3次 | 指数退避（1s, 2s, 4s） |
| 限流错误 | ✅ 是 | 3次 | 指数退避（1s, 2s, 4s） |
| 认证错误 | ❌ 否 | - | - |
| 其他错误 | ❌ 否 | - | - |

## 诊断信息

现在日志会记录：
- Provider 类型（openai/anthropic/qwen）
- 模型版本
- API 端点
- 配置 ID
- 错误类型和详细信息

## 相关文件

- `automation-framework/src/ai/llm.py` - LLM Provider 重试逻辑
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/ai_generation_service.py` - Service 层错误处理

## 测试建议

1. **测试网络波动场景**：
   - 临时断开网络连接
   - 验证系统是否自动重试并恢复

2. **测试API端点错误**：
   - 配置错误的API端点
   - 验证错误信息是否包含正确的诊断信息

3. **测试超时场景**：
   - 模拟慢速网络
   - 验证超时重试是否正常工作

## 总结

✅ **连接错误重试** - 所有 LLM Provider 都添加了连接错误的重试机制
✅ **错误诊断增强** - 记录详细的配置信息和错误上下文
✅ **用户体验改善** - 临时网络问题可以自动恢复，减少用户重试次数
