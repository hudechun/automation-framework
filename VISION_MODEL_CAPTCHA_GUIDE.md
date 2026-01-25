# 使用视觉模型识别验证码指南

## 📋 概述

系统现在支持使用**视觉模型（Vision Model）**代替传统OCR来识别验证码，**准确率更高，特别是对于复杂验证码**。

### 支持的视觉模型

- ✅ **Qwen Vision**（通义千问视觉模型）- 已集成
- ✅ **GPT-4 Vision** - 已集成
- ✅ **Claude Vision** - 待集成

---

## 🚀 使用方式

### 方式1：使用Qwen视觉模型（推荐）

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

actions = [
    Click(selector="button[type='submit']"),
    HandleCaptcha(
        selector=None,  # 自动检测验证码
        vision_model_provider="qwen",  # 使用Qwen视觉模型
        manual_input=True,  # 如果识别失败，支持人工输入
        timeout=60000
    ),
]
```

### 方式2：同时配置视觉模型和OCR（降级策略）

```python
HandleCaptcha(
    selector=None,
    vision_model_provider="qwen",  # 优先使用视觉模型
    ocr_provider="tesseract",  # 如果视觉模型失败，降级到OCR
    manual_input=True,  # 最后降级到人工输入
    timeout=60000
)
```

### 方式3：仅使用OCR（传统方式）

```python
HandleCaptcha(
    selector=None,
    ocr_provider="tesseract",  # 仅使用OCR
    manual_input=True,
    timeout=60000
)
```

---

## ⚙️ 配置

### 环境变量配置

#### Qwen视觉模型
```bash
# 设置Qwen API密钥
export QWEN_API_KEY="your_qwen_api_key"
# 或
export DASHSCOPE_API_KEY="your_dashscope_api_key"
```

#### GPT-4 Vision
```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your_openai_api_key"
```

### 代码配置

```python
from automation_framework.src.integrations.vision_model import QwenVisionClient

# 创建客户端时指定API密钥
client = QwenVisionClient(api_key="your_api_key")

# 或使用默认配置（从环境变量读取）
client = QwenVisionClient()
```

---

## 📊 处理优先级

系统按以下优先级处理验证码：

1. **视觉模型**（如果配置）
   - Qwen Vision
   - GPT-4 Vision
   - Claude Vision

2. **OCR服务**（如果视觉模型失败或未配置）
   - Tesseract
   - 百度OCR
   - 阿里云OCR

3. **人工输入**（如果自动识别失败且启用）

---

## 🎯 优势对比

### 视觉模型 vs OCR

| 特性 | 视觉模型 | OCR |
|------|---------|-----|
| **准确率** | ✅ 高（特别是复杂验证码） | ⚠️ 中等 |
| **中文支持** | ✅ 优秀 | ⚠️ 一般 |
| **扭曲文字** | ✅ 能识别 | ❌ 困难 |
| **背景干扰** | ✅ 抗干扰能力强 | ❌ 容易失败 |
| **速度** | ⚠️ 较慢（API调用） | ✅ 快（本地） |
| **成本** | ⚠️ 需要API费用 | ✅ 免费（本地） |

### 推荐使用场景

- ✅ **复杂验证码**：使用视觉模型
- ✅ **中文验证码**：使用视觉模型
- ✅ **扭曲/干扰验证码**：使用视觉模型
- ✅ **简单验证码**：可以使用OCR（更快更便宜）

---

## 💡 最佳实践

### 1. 优先使用视觉模型

```python
# ✅ 推荐：优先视觉模型，降级到OCR
HandleCaptcha(
    vision_model_provider="qwen",
    ocr_provider="tesseract",  # 备用
    manual_input=True  # 最后备用
)
```

### 2. 根据验证码类型选择

```python
# 复杂验证码：使用视觉模型
if captcha_type == "complex":
    HandleCaptcha(vision_model_provider="qwen")
# 简单验证码：使用OCR
else:
    HandleCaptcha(ocr_provider="tesseract")
```

### 3. 错误处理和重试

```python
# 视觉模型识别失败时，自动降级到OCR
HandleCaptcha(
    vision_model_provider="qwen",
    ocr_provider="tesseract",
    manual_input=True
)
```

---

## 🔧 集成示例

### 完整登录流程（使用视觉模型）

```python
from automation_framework.src.core.actions import GoToURL, Type, Click
from automation_framework.src.core.smart_wait import wait_for_network_idle, wait_for_element_visible
from automation_framework.src.core.captcha_action import HandleCaptcha

actions = [
    GoToURL(url="https://example.com/login"),
    wait_for_network_idle(timeout=30000),
    
    # 输入账号密码
    wait_for_element_visible("input[name='username']", timeout=10000),
    Type(selector="input[name='username']", text="abc"),
    Type(selector="input[name='password']", text="abc123"),
    
    # 点击登录
    Click(selector="button[type='submit']"),
    
    # 使用视觉模型识别验证码
    HandleCaptcha(
        selector=None,  # 自动检测
        vision_model_provider="qwen",  # 使用Qwen视觉模型
        ocr_provider="tesseract",  # 备用OCR
        manual_input=True,  # 最后备用人工输入
        timeout=60000
    ),
    
    # 等待登录成功
    wait_for_text("登录成功", timeout=10000),
]
```

---

## 📝 配置说明

### Qwen视觉模型配置

```python
# 方式1：环境变量
export QWEN_API_KEY="your_key"

# 方式2：代码中指定
HandleCaptcha(
    vision_model_provider="qwen",
    # API密钥从环境变量读取
)
```

### 自定义API端点

```python
from automation_framework.src.integrations.vision_model import QwenVisionClient

# 自定义API端点
client = QwenVisionClient(
    api_key="your_key",
    base_url="https://custom-endpoint.com/v1"
)
```

---

## ✅ 总结

**使用视觉模型识别验证码的优势：**

1. ✅ **准确率高**：特别是复杂验证码
2. ✅ **中文支持好**：能准确识别中文验证码
3. ✅ **抗干扰强**：能处理扭曲、干扰线等
4. ✅ **易于扩展**：支持多种视觉模型

**推荐配置：**
- 优先使用视觉模型（Qwen Vision）
- 降级到OCR（Tesseract）
- 最后人工输入

**系统现在可以更准确地识别各种验证码！** 🎊
