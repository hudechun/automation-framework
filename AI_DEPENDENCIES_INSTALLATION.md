# AI模型依赖安装指南

## 问题描述

生成论文大纲时出现错误：
```
创建AI模型提供商失败: openai package is not installed. Install it with: pip install openai
```

## 解决方案

### 已安装的依赖

已成功安装以下AI模型相关的Python包：

1. ✅ **openai** (>=1.0.0) - OpenAI API支持
2. ✅ **anthropic** (>=0.18.0) - Anthropic (Claude) API支持  
3. ✅ **aiohttp** (>=3.9.0) - 异步HTTP客户端（用于Qwen等）

### 安装命令

如果需要在其他环境安装，可以使用以下命令：

```bash
# 激活虚拟环境（如果使用）
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 安装AI模型依赖
pip install openai>=1.0.0 anthropic>=0.18.0 aiohttp>=3.9.0

# 或者从requirements.txt安装
pip install -r requirements.txt
```

### 支持的AI模型提供商

系统支持以下AI模型提供商：

1. **OpenAI** - GPT系列模型
   - 需要配置：`provider: "openai"`, `api_key`, `model_version` (如: gpt-4, gpt-3.5-turbo)
   - API端点：默认使用OpenAI官方端点，也可自定义

2. **Anthropic** - Claude系列模型
   - 需要配置：`provider: "anthropic"`, `api_key`, `model_version` (如: claude-3-opus-20240229)
   - API端点：默认使用Anthropic官方端点，也可自定义

3. **Qwen** - 通义千问模型
   - 需要配置：`provider: "qwen"`, `api_key`, `model_version` (如: qwen-turbo, qwen-plus)
   - API端点：默认使用 `https://dashscope.aliyuncs.com/compatible-mode/v1`

### 配置AI模型

在AI模型管理页面配置模型：

1. **创建模型配置**
   - 模型名称：自定义名称
   - 模型代码：唯一标识（如：openai-gpt4）
   - 模型类型：选择 `language`（用于文本生成）
   - 提供商：选择 `openai`、`anthropic` 或 `qwen`
   - 模型版本：填写具体模型名称（如：gpt-4, claude-3-opus-20240229）
   - API Key：填写对应提供商的API密钥
   - API端点：可选，使用默认或自定义

2. **启用配置**
   - 设置 `is_enabled = '1'` 启用配置

3. **设置为默认**
   - 设置 `is_default = '1'` 设为默认配置
   - 或者系统会自动使用第一个启用的配置作为fallback

### 验证安装

运行以下命令验证依赖是否安装成功：

```python
python -c "import openai; import anthropic; print('✅ All dependencies installed')"
```

### 常见问题

#### 1. 导入错误

如果仍然出现导入错误，检查：
- 是否在正确的虚拟环境中
- 是否安装了正确版本的包
- 是否需要重启服务器

#### 2. API Key错误

如果API调用失败，检查：
- API Key是否正确
- API Key是否有足够的权限
- API端点是否正确

#### 3. 模型版本错误

确保模型版本名称正确：
- OpenAI: `gpt-4`, `gpt-3.5-turbo` 等
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229` 等
- Qwen: `qwen-turbo`, `qwen-plus`, `qwen-max` 等

## 总结

✅ **依赖已安装** - openai, anthropic, aiohttp 已成功安装
✅ **可以正常使用** - 现在可以配置AI模型并生成论文大纲了

## 下一步

1. 在AI模型管理页面配置模型
2. 填写API Key和模型信息
3. 启用并设置为默认
4. 测试生成论文大纲功能
