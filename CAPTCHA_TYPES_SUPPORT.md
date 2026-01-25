# 验证码类型支持说明

## 📋 支持的验证码类型

系统现在支持以下验证码类型的**自动检测和处理**：

### ✅ 已实现基础支持

| 验证码类型 | 检测 | 自动处理 | 人工介入 | 说明 |
|-----------|------|----------|----------|------|
| **图形验证码** | ✅ | ⚠️ OCR需配置 | ✅ | 图片验证码，支持OCR识别 |
| **滑动验证码** | ✅ | ✅ | ❌ | 滑块验证，自动计算滑动距离 |
| **点选验证码** | ✅ | ⚠️ 需指定目标 | ✅ | 点击图片中的文字/物体 |
| **拼图验证码** | ✅ | ⚠️ 需图像识别 | ✅ | 拼图验证，需要识别缺口位置 |
| **短信验证码** | ✅ | ⚠️ 需接码平台 | ✅ | 短信验证码，需要接码服务 |
| **邮箱验证码** | ✅ | ⚠️ 需邮箱服务 | ✅ | 邮箱验证码，需要邮箱接收 |
| **reCAPTCHA** | ✅ | ⚠️ 需第三方服务 | ✅ | Google reCAPTCHA |
| **hCaptcha** | ✅ | ⚠️ 需第三方服务 | ✅ | hCaptcha |
| **Cloudflare Turnstile** | ✅ | ⚠️ 需第三方服务 | ✅ | Cloudflare验证 |

---

## 🔍 详细说明

### 1. 图形验证码（Image Captcha）

**检测方式**：
- 自动扫描页面查找验证码图片
- 选择器：`img[alt*='验证码']`, `img[alt*='captcha']`, `.captcha img` 等

**处理方式**：
- ✅ **OCR识别**：需要配置OCR服务（Tesseract、百度OCR、阿里云OCR等）
- ✅ **人工输入**：`manual_input=True` 时等待用户输入

**使用示例**：
```python
HandleCaptcha(
    selector="img.captcha",  # 可选，自动检测
    ocr_provider="baidu",  # OCR服务提供商
    manual_input=True,  # 支持人工输入
    timeout=60000
)
```

---

### 2. 滑动验证码（Slider Captcha）

**检测方式**：
- 自动检测滑块元素：`.slider-verify`, `.slider-captcha`, `.geetest_slider` 等

**处理方式**：
- ✅ **自动滑动**：自动计算滑动距离并执行滑动
- ⚠️ **限制**：需要识别缺口位置（当前简化处理，可能需要图像识别优化）

**使用示例**：
```python
HandleCaptcha()  # 自动检测和处理
```

**工作原理**：
1. 查找滑块和轨道元素
2. 计算滑动距离（需要识别缺口位置）
3. 执行滑动操作

---

### 3. 点选验证码（Click Captcha）

**检测方式**：
- 自动检测：`.click-captcha`, `.point-captcha` 等

**处理方式**：
- ⚠️ **需要指定目标**：需要知道要点击的文字或物体
- ✅ **人工介入**：`manual_input=True` 时等待用户点击

**使用示例**：
```python
HandleCaptcha(
    selector=".click-captcha",
    manual_input=True  # 通常需要人工介入
)
```

**扩展建议**：
- 集成图像识别（识别需要点击的文字）
- 或使用OCR识别提示文字

---

### 4. 拼图验证码（Puzzle Captcha）

**检测方式**：
- 自动检测：`.puzzle-captcha`, `.jigsaw-captcha` 等

**处理方式**：
- ⚠️ **需要图像识别**：需要识别缺口位置
- ✅ **人工介入**：`manual_input=True` 时等待用户操作

**使用示例**：
```python
HandleCaptcha(
    selector=".puzzle-captcha",
    manual_input=True
)
```

**扩展建议**：
- 集成图像识别算法（识别拼图缺口位置）
- 或使用模板匹配

---

### 5. 短信验证码（SMS Captcha）

**检测方式**：
- 自动检测验证码输入框：`input[placeholder*='验证码']`, `input[name*='sms']` 等

**处理方式**：
- ⚠️ **需要接码平台**：集成接码服务（如接码平台API）
- ✅ **人工输入**：`manual_input=True` 时等待用户输入

**使用示例**：
```python
HandleCaptcha(
    selector="input[name='sms_code']",
    manual_input=True
)
```

**扩展建议**：
- 集成接码平台API（自动获取验证码）
- 或等待人工输入

---

### 6. 邮箱验证码（Email Captcha）

**检测方式**：
- 自动检测验证码输入框：`input[placeholder*='邮箱验证码']`, `input[name*='email_code']` 等

**处理方式**：
- ⚠️ **需要邮箱服务**：集成邮箱接收服务
- ✅ **人工输入**：`manual_input=True` 时等待用户输入

**使用示例**：
```python
HandleCaptcha(
    selector="input[name='email_code']",
    manual_input=True
)
```

**扩展建议**：
- 集成邮箱接收服务（IMAP/POP3）
- 或等待人工输入

---

### 7. Google reCAPTCHA

**检测方式**：
- 自动检测：`.g-recaptcha`, `iframe[src*='recaptcha']` 等

**处理方式**：
- ⚠️ **需要第三方服务**：集成2captcha、anti-captcha等服务
- ✅ **人工介入**：`manual_input=True` 时等待用户解决

**使用示例**：
```python
HandleCaptcha(
    selector=".g-recaptcha",
    manual_input=True
)
```

**扩展建议**：
- 集成2captcha API
- 或集成anti-captcha API
- 或等待人工解决

---

### 8. hCaptcha

**检测方式**：
- 自动检测：`.h-captcha`, `iframe[src*='hcaptcha']` 等

**处理方式**：
- ⚠️ **需要第三方服务**：类似reCAPTCHA
- ✅ **人工介入**：`manual_input=True` 时等待用户解决

---

### 9. Cloudflare Turnstile

**检测方式**：
- 自动检测：`.cf-turnstile`, `iframe[src*='challenges.cloudflare.com']` 等

**处理方式**：
- ⚠️ **需要第三方服务**：类似reCAPTCHA
- ✅ **人工介入**：`manual_input=True` 时等待用户解决

---

## 🎯 处理能力总结

### 完全自动处理 ✅
- **滑动验证码**：可以自动计算并执行滑动

### 需要配置服务 ⚠️
- **图形验证码**：需要配置OCR服务
- **短信验证码**：需要集成接码平台
- **邮箱验证码**：需要集成邮箱接收服务
- **reCAPTCHA/hCaptcha**：需要集成第三方服务（2captcha等）

### 需要人工介入 👤
- **点选验证码**：通常需要人工点击
- **拼图验证码**：通常需要人工操作
- **复杂验证码**：reCAPTCHA、hCaptcha等

---

## 🚀 使用方式

### 自动检测和处理

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

# 自动检测验证码类型并处理
actions = [
    Click(selector="button[type='submit']"),
    HandleCaptcha(
        selector=None,  # 自动检测
        manual_input=True,  # 支持人工介入
        timeout=60000
    ),
]
```

### 指定验证码类型（高级用法）

```python
from automation_framework.src.core.captcha_types import CaptchaType

# 如果知道验证码类型，可以指定
# 当前版本自动检测，未来版本可能支持指定类型
```

---

## 📊 检测优先级

系统按以下优先级检测验证码类型：

1. **reCAPTCHA** - 优先检测（最常见）
2. **hCaptcha** - 次优先
3. **Turnstile** - Cloudflare验证
4. **滑动验证码** - 滑块验证
5. **点选验证码** - 点击验证
6. **拼图验证码** - 拼图验证
7. **图形验证码** - 最后检测（通用）

---

## 🔧 扩展建议

### 1. OCR服务集成
```python
# 集成百度OCR
from baidu_ocr import BaiduOCR

ocr = BaiduOCR(api_key="your_key")
captcha_text = await ocr.recognize(image)
```

### 2. 接码平台集成
```python
# 集成接码平台
from sms_service import SMSService

sms = SMSService(api_key="your_key")
code = await sms.get_code(phone_number)
```

### 3. 第三方验证码服务
```python
# 集成2captcha
from twocaptcha import TwoCaptcha

solver = TwoCaptcha(api_key="your_key")
result = await solver.recaptcha(site_key, page_url)
```

---

## ✅ 总结

**系统现在可以：**

1. ✅ **自动检测** 9种常见验证码类型
2. ✅ **自动处理** 滑动验证码
3. ✅ **支持人工介入** 所有验证码类型
4. ⚠️ **需要配置** OCR、接码平台、第三方服务等

**对于无法自动处理的验证码，系统会：**
- 自动检测验证码类型
- 返回验证码信息
- 等待人工介入（如果启用）
- 提供扩展接口（集成第三方服务）

**系统设计灵活，可以轻松扩展支持新的验证码类型！** 🎊
