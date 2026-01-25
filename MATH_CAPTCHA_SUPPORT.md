# 数学计算题验证码支持

## 概述

系统现在支持自动识别和计算数学计算题验证码，如 "6-9=?"、"3+5=?" 等。当视觉模型识别出这类验证码时，系统会自动计算结果并填写答案。

## 支持的格式

### 基本格式

- `6-9=?` → 计算结果: `-3`
- `3+5=?` → 计算结果: `8`
- `2*4=?` → 计算结果: `8`
- `10/2=?` → 计算结果: `5`

### 支持的变体

- **中文问号**: `6-9=？` → `-3`
- **带空格**: `6 - 9 = ?` → `-3`
- **中文运算符**: 
  - `8×3=？` → `24` (中文乘号)
  - `15÷3=？` → `5` (中文除号)

### 支持的运算符

- `+` (加法)
- `-` (减法)
- `*` (乘法)
- `/` (除法)
- `×` (中文乘号)
- `÷` (中文除号)

## 工作原理

### 处理流程

```
1. 视觉模型识别验证码文本
   ↓
2. 检测是否是数学计算题（MathCaptchaSolver.is_math_captcha()）
   ↓
3. 如果是，提取数学表达式并计算结果（MathCaptchaSolver.extract_and_solve()）
   ↓
4. 填写计算结果到输入框（而不是原始文本）
```

### 示例

**输入**: 视觉模型识别出 `"6-9=?"`

**处理过程**:
1. 检测到是数学计算题 ✓
2. 提取表达式: `6-9`
3. 计算结果: `-3`
4. 填写到输入框: `-3` ✓

## 代码实现

### 核心类

**MathCaptchaSolver** (`automation-framework/src/core/math_captcha_solver.py`)

主要方法：
- `is_math_captcha(text)`: 判断文本是否是数学计算题
- `solve(text)`: 求解数学表达式，返回 `(结果, 原始表达式)`
- `extract_and_solve(text)`: 从文本中提取数学表达式并求解，返回结果字符串

### 集成点

**HandleCaptcha._solve_image_captcha_with_data()**

在填写验证码之前，会先检查是否是数学计算题：

```python
# 检查是否是数学计算题验证码
if MathCaptchaSolver.is_math_captcha(captcha_text):
    result = MathCaptchaSolver.extract_and_solve(captcha_text)
    if result:
        final_text = result  # 使用计算结果
        is_math_captcha = True
```

## 使用示例

### 基本使用

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

# 创建验证码处理操作
captcha_action = HandleCaptcha(
    selector=None,
    vision_model_provider="qwen",
    manual_input=False
)

# 执行验证码处理
# 如果验证码是 "6-9=?"，系统会自动：
# 1. 识别出文本 "6-9=?"
# 2. 检测到是数学计算题
# 3. 计算结果 "-3"
# 4. 填写 "-3" 到输入框
result = await captcha_action.execute(driver)
```

### 测试示例

运行测试示例：

```bash
cd automation-framework
python examples/math_captcha_example.py
```

## 测试结果

测试用例及结果：

| 输入 | 是否为数学计算题 | 计算结果 |
|------|----------------|---------|
| `6-9=?` | ✓ | `-3` |
| `6-9=？` | ✓ | `-3` |
| `6 - 9 = ?` | ✓ | `-3` |
| `3+5=?` | ✓ | `8` |
| `2*4=?` | ✓ | `8` |
| `10/2=?` | ✓ | `5` |
| `8×3=？` | ✓ | `24` |
| `15÷3=？` | ✓ | `5` |
| `ABC123` | ✗ | - |
| `验证码` | ✗ | - |

## 返回结果格式

当处理数学计算题验证码时，返回结果会包含额外字段：

```python
{
    "success": True,
    "captcha_type": "image",
    "captcha_solved": True,
    "method": "vision_model",
    "captcha_text": "-3",  # 计算结果
    "is_math_captcha": True,
    "original_expression": "6-9=?"  # 原始表达式
}
```

## 注意事项

1. **识别依赖**: 数学计算题的识别依赖于视觉模型能够正确识别出数学表达式文本
2. **格式要求**: 表达式必须是 `数字 运算符 数字` 的格式
3. **除零处理**: 如果遇到除零情况（如 `10/0`），会返回 `None` 并记录警告
4. **回退机制**: 如果无法识别为数学计算题或计算失败，会使用原始文本填写

## 未来扩展

1. **支持更复杂的表达式**: 如 `(6+3)*2=?`
2. **支持小数运算**: 如 `3.5+2.5=?`
3. **支持负数**: 如 `-5+3=?`
4. **支持更多运算符**: 如 `%` (取模)、`^` (幂运算)
