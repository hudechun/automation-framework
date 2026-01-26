# 全局AI配置系统 - 快速开始

## 5分钟快速部署

### 1. 部署数据库（1分钟）

```bash
# Windows
cd RuoYi-Vue3-FastAPI
deploy_global_ai_config.bat

# Linux/Mac
cd RuoYi-Vue3-FastAPI
python deploy_global_ai_config.py
```

**完成后会看到**：
```
✓ 系统AI模型配置表创建成功
✓ 预设模型数量: 16
✓ 语言模型数量: 10
✓ 视觉模型数量: 6
✓ 系统管理菜单插入成功
```

### 2. 重启后端服务（1分钟）

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

### 3. 配置API密钥（2分钟）

1. 登录系统：http://localhost:8000
2. 进入：**系统管理 > AI模型配置**
3. 选择要使用的模型，点击"修改"
4. 填入API密钥
5. 点击"启用"开关
6. 点击"设为默认"

### 4. 测试模型（1分钟）

1. 在模型列表中点击"测试"
2. 输入测试提示词：`你好，请简单介绍一下你自己`
3. 查看测试结果

## 模型选择策略

### 当前实现：默认模型

```python
# 使用默认语言模型
config = await AiModelService.get_default_config(query_db, 'language')

# 使用默认视觉模型
config = await AiModelService.get_default_config(query_db, 'vision')
```

### 推荐实现：智能选择

根据任务类型、成本、负载等因素智能选择模型。详见 `GLOBAL_AI_CONFIG_IMPLEMENTATION_GUIDE.md`

## 常见问题

### Q1: 如何选择使用哪个模型？

**A:** 系统提供三种方式：

1. **默认模型**（推荐）：设置一个模型为默认，系统自动使用
2. **指定模型**：用户在前端选择特定模型
3. **智能选择**：根据任务类型自动选择最合适的模型

### Q2: 配置了多个模型，系统会用哪个？

**A:** 选择优先级：

1. 如果指定了 `config_id`，使用指定的模型
2. 如果有默认模型（`is_default = '1'`），使用默认模型
3. 如果没有默认模型，使用优先级最高的模型（`priority` 最大）

### Q3: 如何实现负载均衡？

**A:** 启用多个相同优先级的模型，在代码中随机选择：

```python
models = await AiModelService.get_enabled_configs(query_db, 'language')
max_priority = max(m.priority for m in models)
top_models = [m for m in models if m.priority == max_priority]
selected = random.choice(top_models)  # 随机选择
```

### Q4: 如何实现故障转移？

**A:** 配置多个提供商的模型，主模型失败时自动切换：

```python
try:
    # 尝试使用OpenAI
    result = await generate_with_openai()
except Exception:
    # 失败时切换到Anthropic
    result = await generate_with_anthropic()
```

### Q5: 推荐配置哪些模型？

**A:** 最小配置：

- **语言模型**：GPT-4o Mini（高性价比）+ Qwen Plus（中文优化）
- **视觉模型**：GPT-4o Mini Vision（通用场景）

**推荐配置**：

- **语言模型**：GPT-4o（高质量）+ Claude 3.5 Sonnet（推理）+ Qwen Plus（成本优化）
- **视觉模型**：GPT-4o Vision（通用）+ Qwen VL Max（中文OCR）

## 下一步

- 阅读完整实施指南：`GLOBAL_AI_CONFIG_IMPLEMENTATION_GUIDE.md`
- 实现智能模型选择策略
- 配置模型性能监控
- 优化成本和性能

## 技术支持

如有问题，请查看：
- 实施指南中的"故障排查"章节
- 系统日志：`logs/` 目录
- API文档：http://localhost:8000/docs
