# 本地OCR使用指南

## 概述

系统现在支持**本地OCR**（基于Tesseract），可以在本地运行，无需依赖外部API服务。

## 优势

1. **完全本地运行**：无需网络连接，无需API密钥
2. **隐私保护**：图像数据不会上传到外部服务
3. **免费使用**：无需支付API费用
4. **快速响应**：本地处理，延迟低
5. **离线可用**：完全离线工作

## 安装Tesseract OCR

### Windows

1. **下载安装包**
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载最新版本的Windows安装包

2. **安装**
   - 运行安装程序
   - 记住安装路径（默认：`C:\Program Files\Tesseract-OCR`）

3. **配置环境变量（可选）**
   - 将 `C:\Program Files\Tesseract-OCR` 添加到系统PATH
   - 或者在使用时指定路径

4. **安装中文语言包（可选）**
   - 安装程序会提示安装语言包
   - 选择 `chi_sim`（简体中文）和 `chi_tra`（繁体中文）

### macOS

```bash
# 使用Homebrew安装
brew install tesseract

# 安装中文语言包
brew install tesseract-lang
```

### Linux (Ubuntu/Debian)

```bash
# 安装Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr

# 安装中文语言包
sudo apt-get install tesseract-ocr-chi-sim  # 简体中文
sudo apt-get install tesseract-ocr-chi-tra  # 繁体中文
```

### Linux (CentOS/RHEL)

```bash
# 安装Tesseract
sudo yum install tesseract

# 安装中文语言包
sudo yum install tesseract-langpack-chi_sim
```

## Python依赖

系统已自动包含以下依赖：

```txt
pillow==10.1.0        # 图像处理
pytesseract==0.3.10  # Tesseract Python绑定
```

安装Python依赖：

```bash
cd automation-framework
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

# 使用本地OCR
captcha_action = HandleCaptcha(
    selector=".captcha-img",
    ocr_provider="tesseract"  # 指定使用Tesseract
)

# 执行验证码处理
result = await captcha_action.execute(driver)
```

### 自定义配置

```python
from automation_framework.src.core.local_ocr import LocalOCR

# 创建自定义OCR实例
ocr = LocalOCR(
    tesseract_cmd="C:\\Program Files\\Tesseract-OCR\\tesseract.exe",  # Windows路径
    lang="eng+chi_sim",  # 英文+简体中文
    config="--psm 7"  # Tesseract配置
)

# 识别图像
text = await ocr.recognize(image_bytes, preprocess=True)
```

### 在验证码处理中使用

```python
# 自适应策略会自动使用本地OCR作为备用方案
captcha_action = HandleCaptcha(
    selector=None,
    ocr_provider="tesseract",  # 本地OCR
    vision_model_provider="qwen"  # 视觉模型（优先）
)

# 系统会：
# 1. 优先使用视觉模型
# 2. 如果失败，自动切换到本地OCR
# 3. 如果还失败，使用其他备用方案
result = await captcha_action.execute(driver)
```

## 语言支持

### 常用语言代码

| 语言 | 代码 | 说明 |
|------|------|------|
| 英文 | `eng` | 默认支持 |
| 简体中文 | `chi_sim` | 需要安装语言包 |
| 繁体中文 | `chi_tra` | 需要安装语言包 |
| 多语言 | `eng+chi_sim` | 同时识别英文和中文 |

### 查看支持的语言

```python
from automation_framework.src.core.local_ocr import get_local_ocr

ocr = get_local_ocr()
languages = ocr.get_supported_languages()
print(f"支持的语言: {languages}")
```

## 图像预处理

系统会自动对图像进行预处理，提高识别率：

1. **灰度转换**：转换为灰度图
2. **对比度增强**：提高对比度
3. **锐化处理**：增强边缘
4. **去噪处理**：移除噪点

### 禁用预处理

```python
ocr = LocalOCR()
text = await ocr.recognize(image_bytes, preprocess=False)
```

## Tesseract配置参数

### PSM模式（页面分割模式）

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `--psm 7` | 单行文本 | 验证码（默认） |
| `--psm 8` | 单个单词 | 单个单词验证码 |
| `--psm 6` | 单个统一文本块 | 多行文本 |
| `--psm 13` | 原始行，无特定块 | 原始文本行 |

### 使用自定义配置

```python
ocr = LocalOCR(
    config="--psm 8 -c tessedit_char_whitelist=0123456789"  # 只识别数字
)
```

## 性能优化

### 1. 图像预处理

预处理可以显著提高识别率，但会增加处理时间：

```python
# 启用预处理（推荐）
text = await ocr.recognize(image_bytes, preprocess=True)

# 禁用预处理（更快，但识别率可能降低）
text = await ocr.recognize(image_bytes, preprocess=False)
```

### 2. 语言选择

只选择需要的语言可以提高速度：

```python
# 只识别英文（更快）
ocr = LocalOCR(lang="eng")

# 只识别中文（更快）
ocr = LocalOCR(lang="chi_sim")

# 多语言（较慢）
ocr = LocalOCR(lang="eng+chi_sim")
```

### 3. 字符白名单

限制识别字符可以提高准确率：

```python
ocr = LocalOCR(
    config="--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
```

## 常见问题

### 1. Tesseract未找到

**错误信息**：
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**解决方案**：
- Windows：指定Tesseract路径
  ```python
  ocr = LocalOCR(tesseract_cmd="C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
  ```
- Linux/macOS：确保Tesseract已安装并在PATH中

### 2. 语言包未找到

**错误信息**：
```
Error opening data file chi_sim.traineddata
```

**解决方案**：
- 安装对应的语言包（见"安装Tesseract OCR"部分）
- 或使用英文：`lang="eng"`

### 3. 识别率低

**解决方案**：
1. **启用预处理**：`preprocess=True`
2. **使用合适的PSM模式**：根据验证码类型选择
3. **限制字符集**：使用白名单
4. **提高图像质量**：确保图像清晰

### 4. 识别速度慢

**解决方案**：
1. **禁用预处理**：`preprocess=False`（如果图像质量好）
2. **限制语言**：只使用需要的语言
3. **使用字符白名单**：减少识别范围

## 与视觉模型对比

| 特性 | 本地OCR (Tesseract) | 视觉模型 (Qwen/GPT-4V) |
|------|---------------------|----------------------|
| **运行方式** | 本地 | 云端API |
| **网络要求** | 不需要 | 需要 |
| **API密钥** | 不需要 | 需要 |
| **费用** | 免费 | 按使用量收费 |
| **隐私** | 完全本地 | 数据上传云端 |
| **识别率** | 中等（取决于图像质量） | 高 |
| **速度** | 快（本地处理） | 中等（网络延迟） |
| **离线可用** | ✅ 是 | ❌ 否 |

## 最佳实践

### 1. 混合使用策略

```python
# 优先使用视觉模型，失败时使用本地OCR
captcha_action = HandleCaptcha(
    ocr_provider="tesseract",  # 本地OCR作为备用
    vision_model_provider="qwen"  # 视觉模型优先
)
```

### 2. 根据场景选择

- **高精度要求**：使用视觉模型
- **隐私敏感**：使用本地OCR
- **离线环境**：使用本地OCR
- **成本考虑**：优先使用本地OCR

### 3. 图像质量优化

- 确保验证码图像清晰
- 避免模糊、扭曲的图像
- 使用合适的图像尺寸

## 示例代码

### 完整示例

```python
import asyncio
from automation_framework.src.core.local_ocr import LocalOCR
from automation_framework.src.core.captcha_action import HandleCaptcha

async def main():
    # 方式1：直接使用本地OCR
    ocr = LocalOCR(lang="eng+chi_sim")
    
    # 读取图像
    with open("captcha.png", "rb") as f:
        image_bytes = f.read()
    
    # 识别
    text = await ocr.recognize(image_bytes, preprocess=True)
    print(f"识别结果: {text}")
    
    # 方式2：在验证码处理中使用
    captcha_action = HandleCaptcha(
        selector=".captcha-img",
        ocr_provider="tesseract"
    )
    
    # 执行（需要driver对象）
    # result = await captcha_action.execute(driver)

if __name__ == "__main__":
    asyncio.run(main())
```

## 总结

本地OCR（Tesseract）提供了：
- ✅ 完全本地运行
- ✅ 免费使用
- ✅ 隐私保护
- ✅ 离线可用

适合：
- 隐私敏感场景
- 离线环境
- 成本控制
- 作为视觉模型的备用方案

与视觉模型结合使用，可以获得最佳效果！🎯
