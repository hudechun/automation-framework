# 登录任务执行指南（包含验证码处理）

## 📋 任务描述

执行以下登录流程：
1. 打开Chrome浏览器
2. 访问登录页面 (XXXX.com/login)
3. 输入账号 (abc)
4. 输入密码 (abc123)
5. 点击登录按钮
6. 等待2秒（等待验证码出现）
7. 检测并处理图形验证码

---

## 🚀 执行方式

### 方式1：基础版本（固定等待）

```python
from automation_framework.src.core.actions import (
    GoToURL, Type, Click, Sleep
)
from automation_framework.src.core.smart_wait import (
    wait_for_network_idle,
    wait_for_element_visible,
    wait_for_text
)
from automation_framework.src.core.captcha_action import HandleCaptcha
from automation_framework.src.drivers.browser_driver import BrowserDriver, BrowserType

async def login_task():
    # 1. 创建并启动Chrome浏览器
    driver = BrowserDriver(browser_type=BrowserType.CHROMIUM)
    await driver.start(headless=False)  # 显示浏览器窗口
    
    # 2. 定义操作序列
    actions = [
        # 访问登录页面
        GoToURL(url="https://XXXX.com/login"),
        
        # 等待页面加载
        wait_for_network_idle(timeout=30000),
        
        # 等待并输入账号
        wait_for_element_visible("input[name='username']", timeout=10000),
        Type(selector="input[name='username']", text="abc"),
        
        # 等待并输入密码
        wait_for_element_visible("input[name='password']", timeout=10000),
        Type(selector="input[name='password']", text="abc123"),
        
        # 等待并点击登录按钮
        wait_for_element_visible("button[type='submit']", timeout=10000),
        Click(selector="button[type='submit']"),
        
        # 等待2秒（等待验证码出现）
        Sleep(duration=2000),
        
        # 检测并处理验证码
        HandleCaptcha(
            selector=None,  # 自动检测验证码
            manual_input=True,  # 支持人工输入
            timeout=60000  # 60秒超时
        ),
        
        # 等待登录成功
        wait_for_text("登录成功", timeout=10000),
    ]
    
    # 3. 执行操作
    for action in actions:
        await action.execute(driver)
    
    print("✅ 登录完成！")

# 运行
import asyncio
asyncio.run(login_task())
```

---

### 方式2：改进版本（智能等待验证码）

**优势**：不固定等待2秒，而是智能等待验证码出现

```python
from automation_framework.src.core.smart_wait import wait_for_custom
from automation_framework.src.core.captcha_action import CaptchaHandler

async def login_task_improved():
    driver = BrowserDriver(browser_type=BrowserType.CHROMIUM)
    await driver.start(headless=False)
    
    # 定义验证码检测函数
    async def check_captcha_appeared(driver):
        """检查验证码是否出现"""
        captcha_handler = CaptchaHandler()
        has_captcha = await captcha_handler.detect_captcha(driver._current_page)
        return has_captcha
    
    actions = [
        GoToURL(url="https://XXXX.com/login"),
        wait_for_network_idle(timeout=30000),
        
        Type(selector="input[name='username']", text="abc"),
        Type(selector="input[name='password']", text="abc123"),
        Click(selector="button[type='submit']"),
        
        # 智能等待验证码出现（而不是固定等待2秒）
        wait_for_custom(
            check_captcha_appeared,
            "等待验证码出现",
            timeout=10000  # 最多等待10秒
        ),
        
        # 处理验证码
        HandleCaptcha(manual_input=True, timeout=60000),
        
        wait_for_text("登录成功", timeout=10000),
    ]
    
    for action in actions:
        await action.execute(driver)
```

---

### 方式3：使用文本定位（最稳定）

**优势**：不依赖CSS类名，使用文本匹配，更稳定

```python
actions = [
    GoToURL(url="https://XXXX.com/login"),
    wait_for_network_idle(timeout=30000),
    
    # 使用多种定位策略（自动降级）
    Type(
        selector="input[name='username'], input[placeholder*='账号']",
        text="abc"
    ),
    Type(
        selector="input[name='password'], input[type='password']",
        text="abc123"
    ),
    
    # 使用文本定位登录按钮（更稳定）
    Click(
        selector="登录",  # 通过按钮文本定位
        locator_type="text"  # 使用文本匹配策略
    ),
    
    # 等待验证码出现
    wait_for_element_visible("img[alt*='验证码'], .captcha img", timeout=10000),
    
    # 处理验证码
    HandleCaptcha(
        selector="img[alt*='验证码'], .captcha img",  # 指定验证码图片
        manual_input=True,
        timeout=60000
    ),
    
    wait_for_text("登录成功", timeout=10000),
]
```

---

## 🔍 验证码处理详解

### HandleCaptcha 工作原理

1. **自动检测验证码**
   - 扫描页面查找验证码图片
   - 使用多种选择器：`img[alt*='验证码']`, `img[alt*='captcha']`, `.captcha`, `#captcha` 等

2. **处理方式**
   - **OCR识别**（如果配置了OCR服务）
   - **人工输入**（`manual_input=True`时）
   - 自动填写到验证码输入框

3. **执行流程**
   ```
   点击登录 → 等待验证码出现 → 检测验证码 → 处理验证码 → 继续执行
   ```

### 验证码处理配置

```python
HandleCaptcha(
    selector="img.captcha",  # 验证码图片选择器（可选，自动检测）
    manual_input=True,  # 是否支持人工输入
    timeout=60000  # 超时时间（毫秒）
)
```

---

## 📊 执行流程对比

### 基础版本（固定等待）
```
访问页面 → 输入账号 → 输入密码 → 点击登录 → 等待2秒 → 处理验证码 → 完成
```
- ✅ 简单直接
- ❌ 如果验证码在2秒内出现，浪费时间
- ❌ 如果验证码超过2秒才出现，可能失败

### 改进版本（智能等待）
```
访问页面 → 输入账号 → 输入密码 → 点击登录 → 智能等待验证码 → 处理验证码 → 完成
```
- ✅ 验证码出现立即处理（不浪费时间）
- ✅ 最多等待10秒（不会过早失败）
- ✅ 更高效、更可靠

---

## 🎯 最佳实践

### 1. 使用智能等待而非固定等待
```python
# ❌ 不推荐：固定等待
Sleep(duration=2000)

# ✅ 推荐：智能等待
wait_for_element_visible("img.captcha", timeout=10000)
```

### 2. 使用多种定位策略
```python
# ❌ 不推荐：单一选择器
Click(selector=".login-btn")

# ✅ 推荐：多种选择器（自动降级）
Click(selector="button[type='submit'], button:has-text('登录'), .login-btn")
```

### 3. 使用文本定位（更稳定）
```python
# ✅ 推荐：文本定位（不依赖CSS类名）
Click(selector="登录", locator_type="text")
```

### 4. 配置验证码处理
```python
# ✅ 推荐：自动检测 + 人工输入
HandleCaptcha(
    selector=None,  # 自动检测
    manual_input=True,  # 支持人工输入
    timeout=60000
)
```

---

## 🛠️ 完整示例代码

完整示例代码请参考：
- `automation-framework/examples/login_with_captcha_example.py`

该文件包含3个版本：
1. **基础版本**：固定等待2秒
2. **改进版本**：智能等待验证码
3. **文本定位版本**：使用文本定位（最稳定）

---

## ✅ 执行结果

### 成功场景
```
[1/9] 执行操作: GoToURL
✓ 操作完成: GoToURL

[2/9] 执行操作: SmartWait
✓ 操作完成: SmartWait

...

[7/9] 执行操作: Sleep
✓ 操作完成: Sleep

[8/9] 执行操作: HandleCaptcha
⏳ 等待人工输入验证码...
✓ 验证码已处理
✓ 操作完成: HandleCaptcha

[9/9] 执行操作: SmartWait
✓ 操作完成: SmartWait

✅ 登录任务执行完成！
```

### 验证码处理流程
1. 点击登录按钮
2. 等待验证码出现（智能等待或固定等待）
3. 检测到验证码图片
4. 如果配置了OCR，尝试自动识别
5. 如果需要人工输入，等待用户输入
6. 填写验证码到输入框
7. 继续后续操作

---

## 🎉 总结

**使用改进后的功能，可以更稳定、高效地执行登录任务：**

1. ✅ **智能等待**：不浪费时间，条件满足立即继续
2. ✅ **多种定位策略**：提高成功率，自动降级
3. ✅ **验证码处理**：自动检测和处理验证码
4. ✅ **文本定位**：更稳定，不依赖CSS类名

**系统现在可以完美处理包含验证码的登录流程！** 🎊
