# 验证码统一视觉模型处理

## 概述

本文档描述了验证码处理的统一视觉模型架构。该架构通过统一的视觉模型识别器（`CaptchaVisionRecognizer`）来识别验证码类型并提取处理所需的数据，然后根据类型分发到专门的处理方法。

## 架构设计

### 核心组件

1. **CaptchaVisionRecognizer** (`automation-framework/src/core/captcha_vision_recognizer.py`)
   - 统一的验证码视觉模型识别器
   - 负责识别验证码类型（image, slider, click, puzzle, rotate等）
   - 提取验证码处理所需的数据（如缺口位置、点击坐标、旋转角度、文字内容等）
   - 返回标准化的JSON格式结果

2. **HandleCaptcha** (`automation-framework/src/core/captcha_action.py`)
   - 验证码处理操作的主类
   - 集成统一的视觉模型识别流程
   - 根据识别结果分发到专门的处理方法

### 处理流程

```
1. 自动定位验证码元素（如果selector为None）
   ↓
2. 截图验证码
   ↓
3. 调用CaptchaVisionRecognizer识别类型和数据
   ↓
4. 根据类型分发到_solve_*_with_data方法
   ↓
5. 如果视觉模型识别失败，回退到原有的检测和处理流程
```

## 视觉模型返回的数据格式

### 标准JSON格式

```json
{
    "type": "image|slider|click|puzzle|rotate|unknown",
    "data": {
        // 根据类型不同，data字段不同
    },
    "confidence": 0.0-1.0,
    "description": "验证码描述"
}
```

### 各类型的数据格式

#### 1. Image（图形验证码）

```json
{
    "type": "image",
    "data": {
        "text": "验证码文字内容"
    },
    "confidence": 0.95,
    "description": "图形验证码，包含文字/数字"
}
```

#### 2. Slider（滑动验证码）

```json
{
    "type": "slider",
    "data": {
        "gap_x": 150.5,
        "gap_width": 50.0
    },
    "confidence": 0.92,
    "description": "滑动验证码，需要滑动滑块到缺口位置"
}
```

#### 3. Click（点选验证码）

```json
{
    "type": "click",
    "data": {
        "targets": [
            {"x": 100, "y": 200, "text": "登录"},
            {"x": 150, "y": 250, "text": "注册"}
        ]
    },
    "confidence": 0.88,
    "description": "点选验证码，需要点击指定的文字或物体"
}
```

#### 4. Puzzle（拼图验证码）

```json
{
    "type": "puzzle",
    "data": {
        "gap_x": 200.0,
        "gap_y": 100.0,
        "gap_width": 60.0,
        "gap_height": 60.0
    },
    "confidence": 0.90,
    "description": "拼图验证码，需要拖动拼图块到缺口位置"
}
```

#### 5. Rotate（旋转验证码）

```json
{
    "type": "rotate",
    "data": {
        "rotation_angle": 90,
        "direction": "clockwise"
    },
    "confidence": 0.85,
    "description": "旋转验证码，需要旋转图片到正确角度"
}
```

## 使用方法

### 基本使用

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

# 创建验证码处理操作
captcha_action = HandleCaptcha(
    selector=None,  # 自动检测验证码元素
    vision_model_provider="qwen",  # 使用Qwen视觉模型
    manual_input=False
)

# 执行验证码处理
result = await captcha_action.execute(driver)
```

### 配置视觉模型

视觉模型提供商可以通过以下方式配置：

1. **通过参数传递**：
   ```python
   HandleCaptcha(vision_model_provider="qwen")
   ```

2. **通过环境变量自动检测**：
   - `QWEN_API_KEY` 或 `DASHSCOPE_API_KEY` → 使用 Qwen
   - `OPENAI_API_KEY` → 使用 GPT-4 Vision
   - `ANTHROPIC_API_KEY` → 使用 Claude Vision

### 支持的视觉模型提供商

- **qwen**: 通义千问视觉模型（Qwen-VL）
- **gpt4v** / **gpt-4-vision** / **openai**: GPT-4 Vision
- **claude** / **claude-vision** / **anthropic**: Claude 3 Vision

## 处理方法的实现

### 使用视觉模型数据的方法

- `_solve_image_captcha_with_data()`: 使用视觉模型返回的文字内容填写验证码
- `_solve_slider_captcha_with_data()`: 使用视觉模型返回的缺口位置进行滑动
- `_solve_click_captcha_with_data()`: 使用视觉模型返回的点击坐标进行点击
- `_solve_puzzle_captcha_with_data()`: 使用视觉模型返回的缺口位置进行拖拽
- `_solve_rotate_captcha_with_data()`: 使用视觉模型返回的旋转角度进行旋转

### 回退方法

如果视觉模型识别失败（置信度 < 0.5 或返回 unknown），系统会自动回退到原有的检测和处理流程：

- `_solve_by_type()`: 使用 `CaptchaDetector` 检测类型，然后调用相应的处理方法
- `_solve_image_captcha()`: 使用 OCR 或视觉模型识别文字
- `_solve_slider_captcha()`: 使用视觉模型识别缺口位置
- 等等...

## 优势

1. **统一入口**: 所有验证码类型都通过统一的视觉模型识别器处理
2. **标准化数据格式**: 返回标准化的JSON格式，便于处理和扩展
3. **智能回退**: 如果视觉模型识别失败，自动回退到原有方法
4. **易于扩展**: 新增验证码类型只需在 `CaptchaVisionRecognizer` 中添加相应的提示词和数据格式
5. **统计支持**: 自动记录验证码识别统计信息

## 统计信息

系统会自动记录验证码识别统计信息：

- 验证码类型
- 识别成功率
- 使用的识别方法（vision_model, ocr, fallback等）

## 注意事项

1. **置信度阈值**: 只有当视觉模型返回的置信度 > 0.5 时，才会使用识别结果
2. **回退机制**: 如果视觉模型未配置或识别失败，会自动回退到原有方法
3. **坐标转换**: 对于点选和拼图验证码，需要将相对坐标转换为页面坐标
4. **临时文件**: 视觉模型识别过程中会创建临时文件，使用后会自动清理

## 示例场景

### 场景1: 图形验证码

```python
# 视觉模型识别返回：
{
    "type": "image",
    "data": {"text": "ABC123"},
    "confidence": 0.95
}

# 处理流程：
# 1. 提取文字 "ABC123"
# 2. 查找验证码输入框
# 3. 填写验证码
```

### 场景2: 滑动验证码

```python
# 视觉模型识别返回：
{
    "type": "slider",
    "data": {"gap_x": 150.5, "gap_width": 50.0},
    "confidence": 0.92
}

# 处理流程：
# 1. 提取缺口位置 gap_x = 150.5
# 2. 计算滑动距离
# 3. 通过5次校验计算校验因子
# 4. 分段滑动（20份，前85%快速，后15%慢速）
```

### 场景3: 点选验证码

```python
# 视觉模型识别返回：
{
    "type": "click",
    "data": {
        "targets": [
            {"x": 100, "y": 200, "text": "登录"},
            {"x": 150, "y": 250, "text": "注册"}
        ]
    },
    "confidence": 0.88
}

# 处理流程：
# 1. 提取点击目标坐标
# 2. 转换为页面坐标
# 3. 按顺序点击所有目标
```

## 未来扩展

1. **更多验证码类型**: 支持更多验证码类型（如行为验证码、语音验证码等）
2. **多模型融合**: 支持多个视觉模型的结果融合，提高识别准确率
3. **缓存机制**: 缓存识别结果，避免重复识别
4. **实时反馈**: 支持实时反馈识别结果给前端
5. **自定义提示词**: 允许用户自定义视觉模型的提示词
