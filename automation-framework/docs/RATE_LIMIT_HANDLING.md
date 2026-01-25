# LLM API限流处理指南

## 问题描述

在使用LLM API时，可能会遇到"请求过于频繁，每分钟最多 60 次请求"的错误。这是API提供商的限流保护机制。

## 解决方案

系统已实现以下机制来处理限流问题：

### 1. 请求限流器（Rate Limiter）

**位置**：`automation-framework/src/ai/rate_limiter.py`

**功能**：
- 自动控制请求频率
- 在达到限制前自动等待
- 支持不同API的独立限流

**默认配置**：
- 最大请求数：60次/分钟
- 时间窗口：60秒

### 2. 自动重试机制

**功能**：
- 检测429错误（Too Many Requests）
- 指数退避重试（1s, 2s, 4s）
- 最多重试3次

**错误检测**：
- HTTP 429状态码
- 错误信息包含"rate limit"
- 错误信息包含"too many requests"
- 错误信息包含"请求过于频繁"（中文）

### 3. 优化LLM调用次数

**优化策略**：
- 场景化规划时，合并任务解析和计划生成为一次LLM调用
- 避免重复调用相同的LLM接口
- 使用缓存减少不必要的调用

## 使用方法

### 自动处理（推荐）

系统会自动处理限流，无需手动配置：

```python
from automation_framework.src.ai.agent import Agent
from automation_framework.src.ai.config import ModelConfig

# 创建Agent（自动启用限流）
agent = Agent(llm_config, enable_scenario=True)

# 正常使用，系统会自动处理限流
result = await agent.execute_task("给张三发送消息：你好")
```

### 自定义限流配置

如果需要调整限流参数：

```python
from automation_framework.src.ai.rate_limiter import RateLimitConfig, set_rate_limiter, RateLimiter

# 自定义配置（例如：30次/分钟）
config = RateLimitConfig(
    max_requests=30,
    window_seconds=60
)

# 设置全局限流器
limiter = RateLimiter(config)
set_rate_limiter(limiter)
```

### 查看剩余请求数

```python
from automation_framework.src.ai.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
remaining = limiter.get_remaining_requests("your-api-key")
print(f"剩余请求数: {remaining}")
```

## 最佳实践

### 1. 减少LLM调用次数

**优化前**（2次调用）：
```python
# 第一次：解析任务
task_desc = await planner.parse_task(description)
# 第二次：生成计划
plan = await planner.plan(task_desc)
```

**优化后**（1次调用）：
```python
# 合并为一次调用
result = await scenario_planner.plan_with_scenario(description)
```

### 2. 批量处理任务

如果需要处理多个任务，建议：
- 使用队列批量处理
- 添加延迟避免突发请求
- 使用异步并发控制

### 3. 监控请求频率

```python
from automation_framework.src.ai.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()

# 在处理任务前检查
remaining = limiter.get_remaining_requests()
if remaining < 10:
    print("警告：剩余请求数较少，建议稍后再试")
```

## 错误处理

### 常见错误

1. **"请求过于频繁，每分钟最多 60 次请求"**
   - 原因：超过API限流
   - 处理：系统自动重试，等待后继续

2. **"Rate limit exceeded after 3 attempts"**
   - 原因：重试3次后仍然失败
   - 处理：等待更长时间后重试，或降低请求频率

### 错误恢复

系统会自动：
1. 检测限流错误
2. 计算等待时间
3. 指数退避重试
4. 如果仍然失败，抛出异常

## 配置建议

### 不同API提供商的限流

| 提供商 | 默认限流 | 建议配置 |
|--------|---------|---------|
| OpenAI | 60次/分钟 | 50次/分钟（留出余量） |
| Qwen | 60次/分钟 | 50次/分钟（留出余量） |
| Anthropic | 50次/分钟 | 45次/分钟（留出余量） |
| Ollama | 无限制 | 无需配置 |

### 生产环境配置

```python
# 生产环境建议配置
config = RateLimitConfig(
    max_requests=50,  # 留出10次余量
    window_seconds=60
)
```

## 故障排查

### 问题1：仍然遇到限流错误

**可能原因**：
1. 多个进程/线程同时使用
2. 限流配置不正确
3. API密钥共享导致限流

**解决方案**：
1. 使用单例模式确保只有一个限流器实例
2. 检查限流配置是否正确
3. 为每个API密钥使用独立的限流器

### 问题2：请求速度太慢

**可能原因**：
1. 限流配置过于保守
2. 等待时间过长

**解决方案**：
1. 根据实际API限制调整配置
2. 优化LLM调用次数

### 问题3：重试失败

**可能原因**：
1. API限流时间窗口较长
2. 请求频率过高

**解决方案**：
1. 增加重试延迟
2. 降低请求频率
3. 使用队列批量处理

## 监控和日志

系统会自动记录：
- 限流等待时间
- 重试次数
- 错误信息

查看日志：
```python
# 日志会显示：
# "Rate limit reached. Waiting X.XX seconds..."
# "Rate limit exceeded. Retrying after X.X seconds... (attempt X/3)"
```

## 更新日志

- 2026-01-24: 初始版本，支持自动限流和重试
