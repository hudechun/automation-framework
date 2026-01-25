# 验证码算法改进说明

## ✅ 已实现的改进

### 1. 滑块验证码算法改进 ✅

#### 1.1 视觉模型识别缺口位置
- ✅ 使用视觉模型（Qwen Vision）识别滑块缺口位置
- ✅ 视觉模型返回JSON格式数据：`{"gap_x": x, "gap_width": w, "confidence": c}`

#### 1.2 分段滑动算法
- ✅ **分割为20份**：总距离分割为20段
- ✅ **前85%快速**：前17段（85%）快速滑动（steps=5）
- ✅ **后15%慢速**：后3段（15%）慢速滑动（steps=20）
- ✅ **模拟人工操作**：每段之间有延迟

#### 1.3 校验因子计算
- ✅ **5次校验测试**：执行5次小距离滑动测试
- ✅ **计算校验因子**：`校验因子 = 实际移动距离 / 目标距离`
- ✅ **应用校验因子**：`真实距离 = 原始距离 × 校验因子`

#### 算法流程
```
1. 截图验证码（包含缺口）
   ↓
2. 视觉模型识别缺口位置 → {"gap_x": 150, "confidence": 0.95}
   ↓
3. 计算滑动距离 = 缺口位置 - 滑块当前位置
   ↓
4. 5次校验测试 → 计算校验因子（如1.05）
   ↓
5. 真实距离 = 原始距离 × 1.05
   ↓
6. 分段滑动（20份）：
   - 前17段：快速（steps=5）
   - 后3段：慢速（steps=20）
   ↓
7. 完成验证
```

---

### 2. 验证码类型识别改进 ✅

#### 2.1 视觉模型识别验证码类型
- ✅ 使用视觉模型识别验证码类型
- ✅ 返回JSON格式：`{"type": "slider", "confidence": 0.9, "description": "..."}`
- ✅ 支持类型：image, slider, click, puzzle, rotate

#### 2.2 双重检测机制
1. **选择器检测**（快速）：使用CSS选择器快速检测
2. **视觉模型识别**（准确）：如果选择器检测失败，使用视觉模型

#### 检测流程
```
1. 使用选择器检测（快速）
   ↓ 失败
2. 截图验证码
   ↓
3. 视觉模型识别类型 → {"type": "slider", "confidence": 0.9}
   ↓
4. 返回验证码类型
```

---

### 3. 点选验证码处理完善 ✅

#### 3.1 视觉模型识别点击目标
- ✅ 使用视觉模型识别需要点击的文字/物体
- ✅ 返回点击坐标：`{"targets": [{"x": 100, "y": 200, "text": "登录"}, ...]}`

#### 3.2 处理流程
```
1. 如果指定了target_text，直接查找并点击
   ↓ 失败
2. 截图验证码区域
   ↓
3. 视觉模型识别点击目标 → [{"x": 100, "y": 200}, ...]
   ↓
4. 按顺序点击所有目标
   ↓
5. 完成验证
```

---

### 4. 拼图验证码处理完善 ✅

#### 4.1 视觉模型识别缺口位置
- ✅ 使用视觉模型识别拼图缺口位置
- ✅ 返回JSON格式：`{"gap_x": x, "gap_y": y, "gap_width": w, "gap_height": h}`

#### 4.2 分段拖拽
- ✅ **10段移动**：拖拽过程分为10段
- ✅ **模拟人工操作**：每段有延迟，移动速度逐渐变化

#### 处理流程
```
1. 查找拼图块和背景图
   ↓
2. 截图背景图（包含缺口）
   ↓
3. 视觉模型识别缺口位置 → {"gap_x": 150, "gap_y": 100}
   ↓
4. 计算目标位置
   ↓
5. 分段拖拽（10段，模拟人工操作）
   ↓
6. 完成验证
```

---

### 5. 验证码统计功能 ✅

#### 5.1 统计信息
- ✅ 验证码类型计数
- ✅ 成功/失败次数
- ✅ 处理方法分布（vision/ocr/manual）
- ✅ 成功率统计

#### 5.2 使用方式
```python
from automation_framework.src.core.captcha_statistics import get_global_statistics

# 获取统计信息
statistics = get_global_statistics()
stats = statistics.get_statistics()

# 查看统计结果
print(f"总验证码数: {stats['total']}")
print(f"类型分布: {stats['by_type']}")
print(f"成功率: {stats['success_rate']}")
```

---

## 📊 算法详细说明

### 滑块验证码算法

#### 步骤1：识别缺口位置
```python
# 视觉模型返回格式
{
    "gap_x": 150.5,  # 缺口左边缘X坐标（像素）
    "gap_width": 50.0,  # 缺口宽度
    "confidence": 0.95  # 置信度
}
```

#### 步骤2：计算滑动距离
```python
slide_distance = gap_x - (button_x - track_x)
```

#### 步骤3：校验因子计算
```python
# 执行5次小距离测试
test_distance = slide_distance * 0.1  # 10%距离

# 每次测试计算实际移动距离
actual_distance = end_x - start_x

# 计算校验因子
factor = actual_distance / test_distance

# 平均校验因子
avg_factor = sum(factors) / len(factors)
```

#### 步骤4：分段滑动
```python
segments = 20
segment_distance = real_distance / segments

# 前85%（17段）：快速
for i in range(17):
    move(segment_distance, steps=5)  # 快速

# 后15%（3段）：慢速
for i in range(3):
    move(segment_distance, steps=20)  # 慢速
```

---

## 🎯 使用示例

### 滑块验证码
```python
from automation_framework.src.core.captcha_action import HandleCaptcha

actions = [
    Click(selector="button[type='submit']"),
    HandleCaptcha(
        selector=".slider-verify",  # 滑块验证码容器
        vision_model_provider="qwen",  # 使用视觉模型
        manual_input=True,
        timeout=60000
    ),
]
```

### 点选验证码
```python
HandleCaptcha(
    selector=".click-captcha",
    vision_model_provider="qwen",  # 使用视觉模型识别点击目标
    manual_input=True
)
```

### 拼图验证码
```python
HandleCaptcha(
    selector=".puzzle-captcha",
    vision_model_provider="qwen",  # 使用视觉模型识别缺口
    manual_input=True
)
```

---

## 📈 性能优化

### 滑块验证码优化
- ✅ **校验因子**：通过5次测试计算，提高准确性
- ✅ **分段滑动**：前85%快速，后15%慢速，模拟人工操作
- ✅ **视觉识别**：准确识别缺口位置，避免盲目滑动

### 点选验证码优化
- ✅ **视觉识别**：自动识别需要点击的目标
- ✅ **坐标定位**：精确获取点击坐标
- ✅ **批量点击**：支持多个目标按顺序点击

### 拼图验证码优化
- ✅ **视觉识别**：准确识别缺口位置
- ✅ **分段拖拽**：模拟人工操作，提高成功率

---

## ✅ 总结

**已完成的改进：**

1. ✅ **滑块验证码算法**：
   - ✅ 视觉模型识别缺口位置（返回JSON格式：`{"gap_x": x, "gap_width": w, "confidence": c}`）
   - ✅ 20份分段滑动（前85%快速，后15%慢速）
   - ✅ 5次校验计算校验因子
   - ✅ 使用校验因子计算真实距离

2. ✅ **验证码类型识别**：
   - ✅ 视觉模型识别验证码类型（返回JSON格式：`{"type": "slider", "confidence": 0.9}`）
   - ✅ 双重检测机制（选择器 + 视觉模型）
   - ✅ 统计验证码类型分布

3. ✅ **点选验证码处理**：
   - ✅ 视觉模型识别点击目标（返回JSON格式：`{"targets": [{"x": x, "y": y}, ...]}`）
   - ✅ 自动获取点击坐标
   - ✅ 支持多个目标按顺序点击

4. ✅ **拼图验证码处理**：
   - ✅ 视觉模型识别缺口位置（返回JSON格式：`{"gap_x": x, "gap_y": y, ...}`）
   - ✅ 分段拖拽（10段，模拟人工操作）

5. ✅ **旋转验证码处理**：
   - ✅ 视觉模型识别旋转角度（返回JSON格式：`{"rotation_angle": 90, "direction": "clockwise"}`）
   - ✅ 自动执行旋转操作

6. ✅ **验证码统计**：
   - ✅ 类型统计
   - ✅ 成功率统计
   - ✅ 方法分布统计（vision/ocr/manual）

**系统现在可以更准确地处理各种类型的验证码！** 🎊

---

## 📋 所有验证码类型处理总结

| 验证码类型 | 视觉模型识别 | 自动处理 | 人工介入 | 说明 |
|-----------|------------|---------|---------|------|
| **图形验证码** | ✅ JSON格式返回文字 | ✅ | ✅ | 视觉模型识别文字/数字 |
| **滑动验证码** | ✅ JSON格式返回缺口位置 | ✅ | ❌ | 20份分段滑动，5次校验 |
| **点选验证码** | ✅ JSON格式返回点击坐标 | ✅ | ✅ | 自动识别并点击目标 |
| **拼图验证码** | ✅ JSON格式返回缺口位置 | ✅ | ✅ | 分段拖拽模拟人工 |
| **旋转验证码** | ✅ JSON格式返回旋转角度 | ✅ | ✅ | 自动识别并旋转 |
| **短信验证码** | ❌ | ⚠️ 需接码平台 | ✅ | 需要接码服务 |
| **邮箱验证码** | ❌ | ⚠️ 需邮箱服务 | ✅ | 需要邮箱接收 |
| **reCAPTCHA** | ❌ | ⚠️ 需第三方服务 | ✅ | 需要2captcha等 |
| **hCaptcha** | ❌ | ⚠️ 需第三方服务 | ✅ | 需要第三方服务 |
| **Turnstile** | ❌ | ⚠️ 需第三方服务 | ✅ | 需要第三方服务 |
