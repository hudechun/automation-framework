# Qwen模型配置指南

本指南介绍如何配置和使用阿里云通义千问（Qwen）模型。

## 前置条件

1. **获取API密钥**
   - 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
   - 注册并登录账号
   - 在"API-KEY管理"页面创建API密钥
   - 保存你的API密钥（格式：`sk-xxxxxxxxxxxxxx`）

2. **安装依赖**
   ```bash
   pip install openai  # Qwen使用OpenAI兼容API
   ```

## 支持的Qwen模型

### 文本模型
- **qwen-turbo**: 快速响应，适合日常任务
- **qwen-plus**: 平衡性能和成本
- **qwen-max**: 最强大的模型，适合复杂任务
- **qwen-long**: 超长上下文支持

### 视觉模型
- **qwen-vl-plus**: 视觉理解模型
- **qwen-vl-max**: 高性能视觉模型

## 配置方法

### 方法1：使用配置文件

1. **复制示例配置**
   ```bash
   cp config/qwen_config.example.json config/qwen_config.json
   ```

2. **编辑配置文件**
   ```json
   {
     "current_profile": "qwen_default",
     "profiles": [
       {
         "name": "qwen_default",
         "task_model": {
           "provider": "qwen",
           "model": "qwen-turbo",
           "api_key": "sk-your-api-key-here",
           "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
           "params": {
             "temperature": 0.7,
             "max_tokens": 2000
           }
         },
         "vision_model": {
           "provider": "qwen",
           "model": "qwen-vl-plus",
           "api_key": "sk-your-api-key-here",
           "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
           "params": {
             "temperature": 0.7,
             "max_tokens": 2000
           }
         }
       }
     ]
   }
   ```

3. **加载配置**
   ```python
   from src.ai.config import get_global_config_manager
   
   config_manager = get_global_config_manager()
   config_manager.load_config("config/qwen_config.json")
   ```

### 方法2：使用Python代码

```python
from src.ai.config import ModelConfig, ModelProfile, ModelProvider, get_global_config_manager

# 创建Qwen任务模型配置
task_model = ModelConfig(
    provider=ModelProvider.QWEN,
    model="qwen-turbo",
    api_key="sk-your-api-key-here",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    params={
        "temperature": 0.7,
        "max_tokens": 2000
    }
)

# 创建Qwen视觉模型配置
vision_model = ModelConfig(
    provider=ModelProvider.QWEN,
    model="qwen-vl-plus",
    api_key="sk-your-api-key-here",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    params={
        "temperature": 0.7,
        "max_tokens": 2000
    }
)

# 创建配置文件
profile = ModelProfile(
    name="qwen_default",
    task_model=task_model,
    vision_model=vision_model
)

# 添加到配置管理器
config_manager = get_global_config_manager()
config_manager.add_profile(profile)
```

### 方法3：使用环境变量

在 `.env` 文件中配置：

```bash
# Qwen API配置
QWEN_API_KEY=sk-your-api-key-here
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo
QWEN_VISION_MODEL=qwen-vl-plus
```

然后在代码中读取：

```python
import os
from dotenv import load_dotenv
from src.ai.config import ModelConfig, ModelProvider

load_dotenv()

task_model = ModelConfig(
    provider=ModelProvider.QWEN,
    model=os.getenv("QWEN_MODEL", "qwen-turbo"),
    api_key=os.getenv("QWEN_API_KEY"),
    api_base=os.getenv("QWEN_API_BASE"),
    params={"temperature": 0.7, "max_tokens": 2000}
)
```

## 使用示例

### 基础文本生成

```python
from src.ai.llm import create_llm_provider
from src.ai.config import ModelConfig, ModelProvider

# 创建配置
config = ModelConfig(
    provider=ModelProvider.QWEN,
    model="qwen-turbo",
    api_key="sk-your-api-key-here",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 创建LLM提供商
llm = create_llm_provider(config)

# 发送消息
messages = [
    {"role": "system", "content": "你是一个自动化助手"},
    {"role": "user", "content": "如何自动化填写网页表单？"}
]

response = await llm.chat(messages)
print(response)
```

### 流式输出

```python
# 流式生成
async for chunk in llm.stream(messages):
    print(chunk, end="", flush=True)
```

### 视觉理解

```python
from src.ai.vision import create_vision_model
from src.ai.config import ModelConfig, ModelProvider

# 创建视觉模型配置
config = ModelConfig(
    provider=ModelProvider.QWEN,
    model="qwen-vl-plus",
    api_key="sk-your-api-key-here",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 创建视觉模型
vision = create_vision_model(config)

# 分析截图
result = await vision.analyze_screenshot(
    image_path="screenshot.png",
    prompt="描述这个页面的内容"
)
print(result)

# 查找UI元素
element = await vision.find_element(
    image_path="screenshot.png",
    element_description="登录按钮"
)
print(element)
```

### 在AI Agent中使用

```python
from src.ai.agent import Agent
from src.ai.config import get_global_config_manager

# 加载Qwen配置
config_manager = get_global_config_manager()
config_manager.load_config("config/qwen_config.json")

# 创建Agent
agent = Agent()

# 执行任务
result = await agent.execute_task(
    "打开百度并搜索'Python自动化'"
)
```

## 模型选择建议

### qwen-turbo
- **适用场景**: 日常任务、快速响应
- **优点**: 速度快、成本低
- **缺点**: 能力相对较弱
- **推荐用途**: 简单的网页操作、表单填写

### qwen-plus
- **适用场景**: 中等复杂度任务
- **优点**: 性能和成本平衡
- **缺点**: 无明显缺点
- **推荐用途**: 大多数自动化任务

### qwen-max
- **适用场景**: 复杂任务、需要深度理解
- **优点**: 能力最强、理解最准确
- **缺点**: 成本较高、速度较慢
- **推荐用途**: 复杂的任务规划、多步骤操作

### qwen-vl-plus/max
- **适用场景**: 需要视觉理解的任务
- **优点**: 强大的图像理解能力
- **缺点**: 成本较高
- **推荐用途**: 元素定位失败时的降级方案

## 降级链配置

配置模型降级链，在主模型失败时自动切换：

```python
from src.ai.config import ModelConfig, ModelProvider, get_global_config_manager

# 配置降级链：qwen-max -> qwen-plus -> qwen-turbo
fallback_chain = [
    ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-plus",
        api_key="sk-your-api-key-here",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    ),
    ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-turbo",
        api_key="sk-your-api-key-here",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
]

config_manager = get_global_config_manager()
config_manager.configure_fallback_chain(fallback_chain)
```

## 成本优化建议

1. **使用合适的模型**
   - 简单任务使用 qwen-turbo
   - 复杂任务使用 qwen-plus
   - 仅在必要时使用 qwen-max

2. **控制token使用**
   ```python
   params = {
       "max_tokens": 1000,  # 限制输出长度
       "temperature": 0.7   # 降低随机性
   }
   ```

3. **使用降级链**
   - 先尝试低成本模型
   - 失败时再使用高性能模型

4. **缓存结果**
   - 对相同的任务缓存模型响应
   - 避免重复调用

## 常见问题

### Q: API密钥在哪里获取？
A: 访问 [DashScope控制台](https://dashscope.console.aliyun.com/) 创建API密钥。

### Q: 支持哪些Qwen模型？
A: 支持所有通过OpenAI兼容API提供的Qwen模型，包括文本和视觉模型。

### Q: 如何切换模型？
A: 使用 `config_manager.switch_profile()` 或 `config_manager.switch_model()` 方法。

### Q: 视觉模型如何使用？
A: 使用 `create_vision_model()` 创建视觉模型实例，然后调用 `analyze_screenshot()` 或 `find_element()` 方法。

### Q: 如何监控API使用量？
A: 在DashScope控制台查看API调用统计和费用。

### Q: 遇到API错误怎么办？
A: 检查API密钥是否正确、网络连接是否正常、配置的api_base是否正确。

## 相关链接

- [阿里云DashScope文档](https://help.aliyun.com/zh/dashscope/)
- [Qwen模型介绍](https://qwenlm.github.io/)
- [API定价](https://dashscope.console.aliyun.com/billing)
- [OpenAI兼容API文档](https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope/)

## 更新日志

- **2026-01-19**: 添加Qwen模型支持
  - 支持qwen-turbo、qwen-plus、qwen-max文本模型
  - 支持qwen-vl-plus、qwen-vl-max视觉模型
  - 通过OpenAI兼容API实现
  - 支持流式输出
  - 支持降级链配置
