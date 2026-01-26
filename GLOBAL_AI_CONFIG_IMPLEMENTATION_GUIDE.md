# 全局AI配置系统实施指南

## 概述

全局AI配置系统已完成开发，支持语言模型和视觉模型的统一管理，提供预设模型下拉选择，支持多模型配置和智能选择。

## 模型选择策略

### 1. 默认选择机制

系统提供三种模型选择方式：

#### 方式1：使用默认模型（推荐）
```python
# 自动选择默认的语言模型
config = await AiModelService.get_default_config(query_db, model_type='language')

# 自动选择默认的视觉模型
config = await AiModelService.get_default_config(query_db, model_type='vision')
```

**选择规则**：
- 查找 `is_default = '1'` 且 `is_enabled = '1'` 的模型
- 同一类型只能有一个默认模型
- 如果没有默认模型，返回 None

#### 方式2：指定配置ID
```python
# 使用特定的模型配置
config = await AiModelService.get_config_detail(query_db, config_id=1)
```

**使用场景**：
- 用户在前端选择特定模型
- 不同任务需要使用不同模型
- 测试特定模型性能

#### 方式3：按优先级自动选择
```python
# 获取所有启用的语言模型，按优先级排序
models = await AiModelService.get_enabled_configs(query_db, model_type='language')
if models:
    config = models[0]  # 使用优先级最高的模型
```

**选择规则**：
- 返回所有 `is_enabled = '1'` 的模型
- 按 `priority` 降序排序
- 优先级相同时按创建时间排序

### 2. 智能选择策略（推荐实现）

为了更灵活地选择模型，建议实现以下策略：

#### 策略1：按任务类型选择
```python
# 在论文生成服务中
async def _select_model_for_task(
    cls,
    query_db: AsyncSession,
    task_type: str,  # 'outline', 'chapter', 'summary'
    model_type: str = 'language'
) -> AiModelConfigModel:
    """根据任务类型智能选择模型"""
    
    # 获取所有启用的模型
    models = await AiModelService.get_enabled_configs(query_db, model_type)
    
    if not models:
        raise ServiceException(message=f'没有可用的{model_type}模型')
    
    # 根据任务类型选择最合适的模型
    if task_type == 'outline':
        # 大纲生成：优先选择推理能力强的模型
        for model in models:
            if model.capabilities and model.capabilities.get('reasoning'):
                return model
    
    elif task_type == 'chapter':
        # 章节生成：优先选择长文本生成能力强的模型
        for model in models:
            if model.capabilities and model.capabilities.get('long_context'):
                return model
    
    elif task_type == 'summary':
        # 摘要生成：优先选择快速响应的模型
        for model in models:
            if model.capabilities and model.capabilities.get('fast_response'):
                return model
    
    # 如果没有匹配的特殊能力，使用默认模型或优先级最高的模型
    default_model = await AiModelService.get_default_config(query_db, model_type)
    return default_model if default_model else models[0]
```

#### 策略2：按成本优化选择
```python
async def _select_model_by_cost(
    cls,
    query_db: AsyncSession,
    max_cost_level: int = 2  # 1=低成本, 2=中等, 3=高成本
) -> AiModelConfigModel:
    """按成本选择模型"""
    
    models = await AiModelService.get_enabled_configs(query_db, 'language')
    
    # 定义成本等级（根据提供商和模型）
    cost_map = {
        'gpt-4o': 3,
        'gpt-4-turbo': 3,
        'claude-3-5-sonnet': 3,
        'claude-3-opus': 3,
        'gpt-4o-mini': 2,
        'claude-3-5-haiku': 2,
        'qwen-max': 2,
        'qwen-plus': 1,
        'qwen-turbo': 1,
        'qwen-flash': 1,
    }
    
    # 筛选符合成本要求的模型
    suitable_models = [
        m for m in models 
        if cost_map.get(m.model_code, 2) <= max_cost_level
    ]
    
    # 返回优先级最高的符合成本要求的模型
    return suitable_models[0] if suitable_models else models[0]
```

#### 策略3：负载均衡选择
```python
import random

async def _select_model_with_load_balance(
    cls,
    query_db: AsyncSession,
    model_type: str = 'language'
) -> AiModelConfigModel:
    """负载均衡选择模型"""
    
    models = await AiModelService.get_enabled_configs(query_db, model_type)
    
    if not models:
        raise ServiceException(message=f'没有可用的{model_type}模型')
    
    # 获取相同优先级的模型
    max_priority = max(m.priority for m in models)
    top_models = [m for m in models if m.priority == max_priority]
    
    # 在相同优先级的模型中随机选择（负载均衡）
    return random.choice(top_models)
```

#### 策略4：故障转移选择
```python
async def _select_model_with_fallback(
    cls,
    query_db: AsyncSession,
    preferred_provider: str = 'openai',
    model_type: str = 'language'
) -> AiModelConfigModel:
    """带故障转移的模型选择"""
    
    models = await AiModelService.get_enabled_configs(query_db, model_type)
    
    # 优先选择指定提供商的模型
    preferred_models = [m for m in models if m.provider == preferred_provider]
    if preferred_models:
        return preferred_models[0]
    
    # 如果指定提供商不可用，选择其他提供商
    # 按优先级：anthropic > qwen > 其他
    fallback_order = ['anthropic', 'qwen', 'openai']
    for provider in fallback_order:
        provider_models = [m for m in models if m.provider == provider]
        if provider_models:
            return provider_models[0]
    
    # 最后返回任意可用模型
    return models[0] if models else None
```

### 3. 用户自定义选择

在前端页面中，用户可以：

1. **设置默认模型**：点击"设为默认"按钮
2. **选择特定模型**：在生成论文时选择使用哪个模型
3. **配置优先级**：调整模型的优先级顺序

## 实施步骤

### 步骤1：部署数据库

```bash
# Windows
cd RuoYi-Vue3-FastAPI
deploy_global_ai_config.bat

# Linux/Mac
cd RuoYi-Vue3-FastAPI
python deploy_global_ai_config.py
```

这将：
- 创建 `sys_ai_model_config` 表
- 插入16个预设模型（10个语言模型 + 6个视觉模型）
- 创建系统管理菜单

### 步骤2：配置API密钥

1. 登录系统管理后台
2. 进入 **系统管理 > AI模型配置**
3. 找到需要使用的模型
4. 点击"修改"，填入API密钥
5. 点击"启用"开关
6. 点击"设为默认"（可选）

### 步骤3：测试模型连接

1. 在AI模型配置列表中
2. 点击"测试"按钮
3. 输入测试提示词
4. 查看测试结果

### 步骤4：更新论文模块引用

论文模块已自动更新为使用系统级AI配置：

```python
# 旧代码（论文模块独立配置）
from module_thesis.service.ai_model_service import AiModelService

# 新代码（使用系统级配置）
from module_admin.service.ai_model_service import AiModelService
```

## 预设模型列表

### 语言模型（10个）

| 模型名称 | 模型代码 | 提供商 | 优先级 | 特点 |
|---------|---------|--------|--------|------|
| GPT-4o | gpt-4o | OpenAI | 100 | 最新多模态模型 |
| Claude 3.5 Sonnet | claude-3-5-sonnet-20241022 | Anthropic | 98 | 最强推理能力 |
| GPT-4o Mini | gpt-4o-mini | OpenAI | 95 | 高性价比 |
| 通义千问Max | qwen-max | Qwen | 92 | 中文优化 |
| Claude 3.5 Haiku | claude-3-5-haiku-20241022 | Anthropic | 92 | 快速响应 |
| GPT-4 Turbo | gpt-4-turbo | OpenAI | 90 | 视觉支持 |
| Claude 3 Opus | claude-3-opus-20240229 | Anthropic | 90 | 长上下文 |
| 通义千问Plus | qwen-plus | Qwen | 88 | 平衡版本 |
| 通义千问Long | qwen-long | Qwen | 86 | 超长上下文 |
| 通义千问Turbo | qwen-flash | Qwen | 82 | 快速响应 |

### 视觉模型（6个）

| 模型名称 | 模型代码 | 提供商 | 优先级 | 特点 |
|---------|---------|--------|--------|------|
| GPT-4o Vision | gpt-4o | OpenAI | 98 | 多模态视觉 |
| Claude 3.5 Sonnet Vision | claude-3-5-sonnet-20241022 | Anthropic | 98 | 文档分析 |
| GPT-4o Mini Vision | gpt-4o-mini | OpenAI | 92 | 高性价比 |
| Claude 3 Opus Vision | claude-3-opus-20240229 | Anthropic | 90 | 强大视觉理解 |
| 通义千问VL Max | qwen-vl-max | Qwen | 90 | 中文OCR |
| Qwen2-VL | qwen2-vl-72b-instruct | Qwen | 85 | 视频理解 |

## 使用示例

### 示例1：论文大纲生成

```python
# 在 thesis_service.py 中
async def generate_outline(self, query_db: AsyncSession, thesis_id: int):
    """生成论文大纲"""
    
    # 方式1：使用默认语言模型
    config = await AiModelService.get_default_config(query_db, 'language')
    
    # 方式2：智能选择（推荐）
    config = await self._select_model_for_task(query_db, 'outline', 'language')
    
    # 调用AI生成服务
    outline = await AiGenerationService.generate_outline(
        query_db,
        thesis_info,
        config_id=config.config_id
    )
    
    return outline
```

### 示例2：验证码识别

```python
# 在自动化框架中
async def recognize_captcha(self, query_db: AsyncSession, image_path: str):
    """识别验证码"""
    
    # 使用默认视觉模型
    config = await AiModelService.get_default_config(query_db, 'vision')
    
    if not config:
        raise ServiceException(message='未配置视觉模型')
    
    # 调用视觉识别服务
    result = await VisionService.recognize_image(
        query_db,
        image_path,
        config_id=config.config_id
    )
    
    return result
```

### 示例3：用户选择模型

```python
# 在论文控制器中
@router.post('/generate-outline')
async def generate_outline(
    thesis_id: int,
    model_id: Optional[int] = None,  # 用户可选择模型
    query_db: AsyncSession = Depends(get_db)
):
    """生成论文大纲"""
    
    # 如果用户指定了模型，使用指定的模型
    if model_id:
        config = await AiModelService.get_config_detail(query_db, model_id)
    else:
        # 否则使用默认模型
        config = await AiModelService.get_default_config(query_db, 'language')
    
    # 生成大纲
    outline = await ThesisService.generate_outline(
        query_db,
        thesis_id,
        config_id=config.config_id
    )
    
    return ResponseUtil.success(data=outline)
```

## 最佳实践

### 1. 模型配置建议

- **至少配置2个语言模型**：一个高性能（GPT-4o/Claude 3.5），一个高性价比（GPT-4o Mini/Qwen Plus）
- **至少配置1个视觉模型**：用于验证码识别等场景
- **设置默认模型**：为每种类型设置一个默认模型
- **合理设置优先级**：根据模型性能和成本设置优先级

### 2. 成本优化建议

- **开发环境**：使用 Qwen Plus/Turbo 或 GPT-4o Mini
- **生产环境**：根据任务重要性选择模型
  - 重要任务：GPT-4o、Claude 3.5 Sonnet
  - 一般任务：GPT-4o Mini、Qwen Plus
  - 批量任务：Qwen Turbo、Qwen Flash

### 3. 性能优化建议

- **启用多个模型**：实现负载均衡
- **配置故障转移**：主模型不可用时自动切换
- **监控模型性能**：记录响应时间和成功率
- **定期测试模型**：确保API密钥有效

### 4. 安全建议

- **API密钥加密存储**：数据库中的API密钥应加密
- **权限控制**：只有管理员可以配置AI模型
- **日志记录**：记录所有AI调用日志
- **配额管理**：设置每个模型的调用配额

## 故障排查

### 问题1：没有可用的模型

**症状**：调用时提示"未配置AI模型"

**解决方案**：
1. 检查是否有启用的模型：`is_enabled = '1'`
2. 检查API密钥是否配置
3. 检查模型类型是否匹配（language/vision）

### 问题2：模型调用失败

**症状**：测试时返回错误

**解决方案**：
1. 检查API密钥是否正确
2. 检查API端点是否正确
3. 检查网络连接
4. 检查模型代码是否正确（使用最新版本）

### 问题3：响应速度慢

**症状**：生成内容耗时过长

**解决方案**：
1. 使用快速响应的模型（Haiku、Mini、Turbo）
2. 减少 max_tokens 参数
3. 启用多个模型实现负载均衡
4. 考虑使用异步生成

## 后续扩展

### 1. 模型性能监控

```python
# 记录每次调用的性能指标
class ModelPerformanceLog(Base):
    __tablename__ = 'sys_ai_model_performance'
    
    log_id: Mapped[int] = mapped_column(primary_key=True)
    config_id: Mapped[int] = mapped_column(comment='模型配置ID')
    task_type: Mapped[str] = mapped_column(comment='任务类型')
    response_time: Mapped[float] = mapped_column(comment='响应时间（秒）')
    token_count: Mapped[int] = mapped_column(comment='Token数量')
    success: Mapped[bool] = mapped_column(comment='是否成功')
    error_message: Mapped[Optional[str]] = mapped_column(comment='错误信息')
    create_time: Mapped[datetime] = mapped_column(comment='创建时间')
```

### 2. 智能模型推荐

根据历史性能数据，自动推荐最适合的模型。

### 3. 成本统计

统计每个模型的调用次数和成本，帮助优化模型选择。

### 4. A/B测试

对比不同模型的生成质量，选择最优模型。

## 总结

全局AI配置系统提供了灵活的模型管理和选择机制：

1. **统一管理**：所有AI模型集中配置
2. **灵活选择**：支持默认、指定、智能选择
3. **易于扩展**：可添加自定义模型和选择策略
4. **跨模块复用**：论文、自动化等模块共享配置

建议根据实际业务需求，实现合适的模型选择策略，平衡性能、成本和用户体验。
