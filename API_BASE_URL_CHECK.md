# API Base URL 检查与修复

## 检查结果

### 1. 数据流路径

```
数据库 (api_endpoint) 
  → AiModelConfig DO 
  → AiModelConfigModel VO (api_endpoint)
  → _get_ai_provider (config.api_endpoint)
  → llm_config['api_base']
  → create_llm_provider (config['api_base'])
  → Provider.__init__ (config.get('api_base'))
  → Client (base_url)
```

### 2. 发现的问题

1. **空值处理不完善**：如果 `api_endpoint` 为空字符串，会被直接传递，可能导致问题
2. **日志不够详细**：无法清楚看到 API base_url 的值
3. **缺少警告**：当 API endpoint 未配置时，没有明确的警告信息

### 3. 修复内容

#### 3.1 增强空值处理

在 `_get_ai_provider` 方法中：

```python
# 获取API端点，如果为空则使用None（让Provider使用默认值）
api_endpoint = config.api_endpoint.strip() if config.api_endpoint and config.api_endpoint.strip() else None

llm_config = {
    'provider': provider_value,
    'model': config.model_version,
    'api_key': config.api_key,
    'api_base': api_endpoint,  # 可能是None，Provider会使用默认值
    'params': params
}
```

#### 3.2 增强日志记录

```python
# 记录配置信息（用于诊断）
logger.info(
    f"创建AI提供商 - Provider: {provider_value}, "
    f"Model: {config.model_version}, "
    f"API Endpoint: {api_endpoint or '(使用默认)'}, "
    f"Config ID: {config.config_id}, "
    f"API Key: {'已配置' if config.api_key else '未配置'}"
)

# 额外检查：如果api_endpoint为空，记录警告
if not api_endpoint:
    logger.warning(
        f"API端点未配置 (Config ID: {config.config_id})，将使用Provider默认端点。"
        f"如需自定义端点，请在AI模型配置中设置API端点。"
    )
```

#### 3.3 Provider 初始化日志

在 `OpenAIProvider` 和 `AnthropicProvider` 的 `__init__` 方法中添加：

```python
api_base = config.get('api_base')
logger.debug(f"OpenAI Provider初始化 - base_url: {api_base or '(使用默认)'}")
self.client = openai.AsyncOpenAI(
    api_key=config['api_key'],
    base_url=api_base  # None时使用OpenAI默认端点
)
```

### 4. 测试脚本

创建了 `test_api_base_url.py` 用于验证：

1. 检查数据库中的 `api_endpoint` 值
2. 验证配置转换过程
3. 检查 Provider 初始化时的 `base_url`
4. 列出所有启用的配置及其 API endpoint

### 5. 使用说明

#### 运行测试脚本

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python test_api_base_url.py
```

#### 查看日志

在生成论文大纲时，日志会显示：

```
创建AI提供商 - Provider: qwen, Model: qwen-max, API Endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1, Config ID: 114, API Key: 已配置
```

如果 API endpoint 未配置：

```
⚠️  API端点未配置 (Config ID: 114)，将使用Provider默认端点。如需自定义端点，请在AI模型配置中设置API端点。
```

### 6. 默认行为

- **OpenAI**: 如果 `base_url` 为 `None`，使用 `https://api.openai.com/v1`
- **Anthropic**: 如果 `base_url` 为 `None`，使用 `https://api.anthropic.com`
- **Qwen**: 如果 `base_url` 为 `None`，使用 `https://dashscope.aliyuncs.com/compatible-mode/v1`

### 7. 相关文件

- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/ai_generation_service.py` - Service层配置传递
- `automation-framework/src/ai/llm.py` - LLM Provider实现
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/test_api_base_url.py` - 测试脚本

### 8. 验证步骤

1. **检查数据库配置**：
   ```sql
   SELECT config_id, provider, model_version, api_endpoint 
   FROM ai_write_ai_model_config 
   WHERE is_enabled = '1' AND model_type = 'language';
   ```

2. **查看日志**：生成论文大纲时，检查日志中的 "创建AI提供商" 信息

3. **运行测试脚本**：执行 `test_api_base_url.py` 验证配置传递

4. **检查连接错误**：如果仍然出现连接错误，检查：
   - API endpoint 是否正确
   - 网络连接是否正常
   - API Key 是否有效
