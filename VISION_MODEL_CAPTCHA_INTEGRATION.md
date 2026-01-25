# 视觉模型验证码识别集成说明

## ✅ 已集成视觉模型

系统已经集成了**Qwen视觉模型**（通义千问），现在可以**代替OCR**来识别验证码，**准确率更高**！

---

## 🎯 使用方式

### 方式1：自动使用视觉模型（推荐）

如果已配置Qwen API密钥，系统会**自动使用视觉模型**：

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

actions = [
    Click(selector="button[type='submit']"),
    HandleCaptcha(
        selector=None,  # 自动检测验证码
        # vision_model_provider="qwen",  # 可选：显式指定，如果不指定会自动检测
        manual_input=True,  # 如果识别失败，支持人工输入
        timeout=60000
    ),
]
```

**系统会自动：**
1. 检测是否配置了Qwen API密钥（环境变量 `QWEN_API_KEY`）
2. 如果已配置，自动使用Qwen视觉模型识别验证码
3. 如果未配置或识别失败，降级到OCR或人工输入

### 方式2：显式指定视觉模型

```python
HandleCaptcha(
    selector=None,
    vision_model_provider="qwen",  # 显式指定使用Qwen
    ocr_provider="tesseract",  # 备用OCR
    manual_input=True,  # 最后备用人工输入
    timeout=60000
)
```

### 方式3：使用其他视觉模型

```python
# 使用GPT-4 Vision
HandleCaptcha(
    vision_model_provider="gpt4v",  # 或 "openai"
    # 需要设置 OPENAI_API_KEY 环境变量
)

# 使用Claude Vision
HandleCaptcha(
    vision_model_provider="claude",  # 或 "anthropic"
    # 需要设置 ANTHROPIC_API_KEY 环境变量
)
```

---

## ⚙️ 配置

### Qwen视觉模型配置

```bash
# 设置Qwen API密钥（必需）
export QWEN_API_KEY="sk-your-qwen-api-key"

# 可选：设置API基础URL（默认使用DashScope）
export QWEN_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

### 自动检测逻辑

系统会按以下顺序自动检测可用的视觉模型：

1. **Qwen** - 如果设置了 `QWEN_API_KEY` 或 `DASHSCOPE_API_KEY`
2. **GPT-4 Vision** - 如果设置了 `OPENAI_API_KEY`
3. **Claude Vision** - 如果设置了 `ANTHROPIC_API_KEY`

如果都未配置，则使用OCR或人工输入。

---

## 📊 视觉模型 vs OCR 对比

| 特性 | 视觉模型（Qwen） | OCR（Tesseract） |
|------|-----------------|------------------|
| **准确率** | ✅ 高（90%+） | ⚠️ 中等（60-70%） |
| **中文支持** | ✅ 优秀 | ⚠️ 一般 |
| **扭曲文字** | ✅ 能识别 | ❌ 困难 |
| **背景干扰** | ✅ 抗干扰强 | ❌ 容易失败 |
| **复杂验证码** | ✅ 能处理 | ❌ 困难 |
| **速度** | ⚠️ 较慢（1-3秒） | ✅ 快（<1秒） |
| **成本** | ⚠️ 需要API费用 | ✅ 免费 |
| **网络要求** | ⚠️ 需要网络 | ✅ 本地 |

---

## 🚀 完整示例

### 登录任务（使用视觉模型识别验证码）

```python
from automation_framework.src.core.actions import GoToURL, Type, Click
from automation_framework.src.core.smart_wait import wait_for_network_idle, wait_for_element_visible
from automation_framework.src.core.captcha_action import HandleCaptcha

actions = [
    GoToURL(url="https://XXXX.com/login"),
    wait_for_network_idle(timeout=30000),
    
    # 输入账号密码
    wait_for_element_visible("input[name='username']", timeout=10000),
    Type(selector="input[name='username']", text="abc"),
    Type(selector="input[name='password']", text="abc123"),
    
    # 点击登录
    Click(selector="button[type='submit']"),
    
    # 使用视觉模型识别验证码（自动使用Qwen）
    HandleCaptcha(
        selector=None,  # 自动检测验证码
        vision_model_provider="qwen",  # 使用Qwen视觉模型（可选，会自动检测）
        ocr_provider="tesseract",  # 备用OCR
        manual_input=True,  # 最后备用人工输入
        timeout=60000
    ),
    
    # 等待登录成功
    wait_for_text("登录成功", timeout=10000),
]
```

---

## 🔧 技术实现

### 集成方式

系统使用已有的 `QwenVisionProvider`（在 `automation-framework/src/ai/vision.py` 中）：

```python
# 自动创建Qwen视觉模型配置
config = ModelConfig(
    provider=ModelProvider.QWEN,
    model="qwen-vl-plus",  # 视觉模型
    api_key=os.getenv("QWEN_API_KEY")
)

# 创建视觉模型实例
vision_model = create_vision_model(config)

# 识别验证码
result = await vision_model.analyze_screenshot(
    image_path="captcha.png",
    prompt="识别验证码内容"
)
```

### 处理流程

```
1. 检测验证码图片
   ↓
2. 截图验证码图片
   ↓
3. 调用视觉模型识别（Qwen Vision）
   ↓
4. 清理识别结果（移除说明文字）
   ↓
5. 填写验证码到输入框
   ↓
6. 如果失败，降级到OCR或人工输入
```

---

## ✅ 优势

### 使用视觉模型的优势

1. ✅ **准确率高**：特别是复杂验证码、中文验证码
2. ✅ **抗干扰强**：能处理扭曲、干扰线、背景复杂等情况
3. ✅ **易于扩展**：支持多种视觉模型（Qwen、GPT-4、Claude）
4. ✅ **自动降级**：识别失败自动降级到OCR或人工输入

### 推荐配置

```python
# ✅ 最佳实践：视觉模型 + OCR + 人工输入（三层降级）
HandleCaptcha(
    vision_model_provider="qwen",  # 优先：视觉模型（准确率高）
    ocr_provider="tesseract",  # 备用：OCR（速度快）
    manual_input=True  # 最后：人工输入（100%准确）
)
```

---

## 📝 注意事项

1. **API密钥**：需要配置Qwen API密钥（`QWEN_API_KEY`）
2. **网络要求**：需要能访问阿里云DashScope服务
3. **成本**：按API调用计费，注意控制使用量
4. **速度**：视觉模型识别需要1-3秒（比OCR慢）
5. **降级策略**：建议配置OCR和人工输入作为备用

---

## 🎉 总结

**系统现在可以：**

1. ✅ **自动使用视觉模型**（如果已配置Qwen API密钥）
2. ✅ **准确识别验证码**（特别是复杂验证码）
3. ✅ **自动降级**（视觉模型 → OCR → 人工输入）
4. ✅ **支持多种视觉模型**（Qwen、GPT-4、Claude）

**使用视觉模型代替OCR，验证码识别准确率大幅提升！** 🎊
