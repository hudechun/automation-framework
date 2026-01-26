# AI模型类型使用说明

## 模型类型

系统支持两种模型类型：

1. **语言模型（language）**：用于文本生成、对话、论文写作等
2. **视觉模型（vision）**：用于图像识别、OCR、验证码识别等

## 前端显示

在AI模型配置页面（`/thesis/ai-model`），每个模型卡片会显示：

- **模型类型**：蓝色标签显示"语言模型"，橙色标签显示"视觉模型"
- **提供商**：显示模型的提供商（OpenAI/Anthropic/Qwen等）
- **模型版本**：显示具体的模型版本号

## 代码中使用

### 1. 论文系统中使用语言模型

```python
from module_thesis.service.ai_generation_service import AiGenerationService

# 生成论文大纲（自动使用默认的语言模型）
outline = await AiGenerationService.generate_outline(
    query_db=db,
    thesis_info={
        'title': '人工智能在教育中的应用研究',
        'major': '计算机科学',
        'degree_level': '硕士'
    }
)

# 或者指定特定的模型配置ID
outline = await AiGenerationService.generate_outline(
    query_db=db,
    thesis_info=thesis_info,
    config_id=123  # 指定模型配置ID
)
```

### 2. 自动化项目中使用视觉模型

```python
from module_admin.service.ai_model_service import AiModelService

# 获取默认的视觉模型
vision_model = await AiModelService.get_default_config(
    query_db=db,
    model_type='vision'
)

# 获取所有启用的视觉模型
vision_models = await AiModelService.get_enabled_configs(
    query_db=db,
    model_type='vision'
)

# 根据类型获取模型列表
language_models = await AiModelService.get_models_by_type(
    query_db=db,
    model_type='language'
)
```

### 3. 在AI生成服务中指定模型类型

```python
# 使用语言模型生成内容
llm_provider = await AiGenerationService._get_ai_provider(
    query_db=db,
    model_type='language'
)

# 使用视觉模型进行图像识别
vision_provider = await AiGenerationService._get_ai_provider(
    query_db=db,
    model_type='vision'
)
```

## 数据库字段

`ai_write_ai_model_config` 表中的相关字段：

| 字段名 | 类型 | 说明 | 可选值 |
|--------|------|------|--------|
| model_type | VARCHAR(20) | 模型类型 | language, vision |
| provider | VARCHAR(50) | 提供商 | openai, anthropic, qwen, custom |
| model_code | VARCHAR(50) | 模型代码 | 如：openai, claude, qwen |
| model_version | VARCHAR(50) | 模型版本 | 如：gpt-4o, claude-3-5-sonnet-20241022 |

## 常见模型配置示例

### 语言模型

```sql
-- OpenAI GPT-4o（语言模型）
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, model_type, provider, api_endpoint, is_enabled, priority)
VALUES 
('GPT-4o', 'openai', 'gpt-4o', 'language', 'openai', 'https://api.openai.com/v1/chat/completions', '1', 100);

-- Claude 3.5 Sonnet（语言模型）
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, model_type, provider, api_endpoint, is_enabled, priority)
VALUES 
('Claude 3.5 Sonnet', 'claude', 'claude-3-5-sonnet-20241022', 'language', 'anthropic', 'https://api.anthropic.com/v1/messages', '1', 95);
```

### 视觉模型

```sql
-- GPT-4 Vision（视觉模型）
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, model_type, provider, api_endpoint, is_enabled, priority)
VALUES 
('GPT-4 Vision', 'openai', 'gpt-4-vision-preview', 'vision', 'openai', 'https://api.openai.com/v1/chat/completions', '1', 90);

-- Claude 3.5 Sonnet Vision（视觉模型）
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, model_type, provider, api_endpoint, is_enabled, priority)
VALUES 
('Claude 3.5 Vision', 'claude', 'claude-3-5-sonnet-20241022', 'vision', 'anthropic', 'https://api.anthropic.com/v1/messages', '1', 85);
```

## 注意事项

1. **默认模型**：每种类型（language/vision）只能有一个默认模型
2. **优先级**：数字越大优先级越高，系统会优先使用高优先级的模型
3. **启用状态**：只有启用的模型才能被使用
4. **API密钥**：必须配置API密钥才能使用模型

## 扩展字段完成后的步骤

1. 运行 `extend_ai_model_table.bat` 扩展数据库表
2. 重启后端服务
3. 在前端页面配置模型类型
4. 在代码中根据需要选择合适的模型类型
