# 自适应验证码处理策略

## 概述

自适应验证码处理系统能够根据不同的验证码场景自动调整处理方法和参数，通过历史学习优化策略选择，提高验证码处理的成功率和效率。

## 核心特性

### 1. 多策略自动切换

系统会根据验证码类型和识别结果，自动选择最佳处理策略：

- **视觉模型优先**：置信度高时优先使用视觉模型识别
- **数学计算题自动识别**：自动检测并计算数学表达式
- **OCR备用**：视觉模型失败时自动切换到OCR
- **回退机制**：所有方法失败时使用通用回退策略

### 2. 置信度评估

根据视觉模型返回的置信度动态调整策略：

- **高置信度 (>0.7)**：直接使用视觉模型结果
- **中等置信度 (0.5-0.7)**：使用视觉模型，但增加验证步骤
- **低置信度 (<0.5)**：尝试多种方法，选择最佳结果

### 3. 历史学习机制

系统会记录每种验证码类型和处理方法的成功率，优先使用成功率高的方法：

- **成功率统计**：记录每种方法的成功/失败次数
- **置信度统计**：记录平均置信度
- **时效性权重**：最近成功的方法获得更高权重
- **自动排序**：根据综合得分自动排序策略

### 4. 动态参数调整

根据验证码复杂度和历史成功率自动调整参数：

- **重试次数**：成功率低时增加重试次数
- **超时时间**：根据复杂度调整超时时间
- **校准测试**：置信度低时增加校准测试次数
- **滑动速度**：根据历史数据调整滑动速度

### 5. 自适应重试

根据错误类型自动调整重试策略：

- **网络错误**：快速重试
- **识别错误**：切换方法后重试
- **超时错误**：增加超时时间后重试
- **元素未找到**：等待后重试

## 策略得分计算

策略得分公式：

```
得分 = 成功率 × 0.6 + 平均置信度 × 0.3 + 时效性 × 0.1
```

其中：
- **成功率**：成功次数 / 总尝试次数
- **平均置信度**：所有成功尝试的平均置信度
- **时效性**：基于最近成功时间的权重（24小时内为1.0，随时间递减）

## 使用示例

### 基本使用

```python
from automation_framework.src.core.captcha_action import HandleCaptcha

# 创建验证码处理操作（自动启用自适应策略）
captcha_action = HandleCaptcha(
    selector=None,
    vision_model_provider="qwen",
    manual_input=False
)

# 执行验证码处理
# 系统会自动：
# 1. 识别验证码类型
# 2. 评估置信度
# 3. 选择最佳策略
# 4. 如果失败，自动尝试其他策略
# 5. 记录结果用于学习
result = await captcha_action.execute(driver)
```

### 自定义配置

```python
from automation_framework.src.core.captcha_adaptive_strategy import (
    AdaptiveCaptchaStrategy, StrategyConfig
)

# 自定义策略配置
config = StrategyConfig(
    max_attempts=5,              # 最大尝试次数
    confidence_threshold=0.6,     # 置信度阈值
    enable_fallback=True,        # 启用回退
    enable_learning=True,        # 启用学习
    adaptive_params=True         # 启用参数自适应
)

captcha_action = HandleCaptcha(
    selector=None,
    vision_model_provider="qwen"
)
# 策略配置会自动应用
```

### 查看策略统计

```python
# 获取策略统计信息
statistics = captcha_action.adaptive_strategy.get_strategy_statistics()

# 查看特定类型的统计
image_stats = captcha_action.adaptive_strategy.get_strategy_statistics("image")

# 重置统计信息
captcha_action.adaptive_strategy.reset_statistics("image")
```

## 自适应场景示例

### 场景1: 清晰图形验证码

```
1. 视觉模型识别: confidence=0.95
2. 策略选择: vision_model (得分最高)
3. 执行: 直接使用视觉模型结果
4. 结果: 成功，记录到历史
```

### 场景2: 模糊图形验证码

```
1. 视觉模型识别: confidence=0.45 (低)
2. 策略选择: 
   - 尝试 vision_model (虽然置信度低，但历史成功率高)
   - 如果失败，自动切换到 OCR
3. 执行: 多策略尝试
4. 结果: OCR成功，更新历史（OCR成功率提高）
```

### 场景3: 数学计算题验证码

```
1. 视觉模型识别: "6-9=?"，confidence=0.92
2. 策略选择: math_calculator (自动检测到数学表达式)
3. 执行: 计算结果 "-3"，填写到输入框
4. 结果: 成功，记录到历史
```

### 场景4: 滑动验证码（首次遇到）

```
1. 视觉模型识别: slider，confidence=0.88
2. 策略选择: vision_model (默认高优先级)
3. 执行: 识别缺口位置，分段滑动
4. 结果: 成功，记录到历史
```

### 场景5: 滑动验证码（历史学习后）

```
1. 视觉模型识别: slider，confidence=0.75
2. 策略选择: 
   - 根据历史，vision_model 成功率 95%，优先使用
   - 如果失败，自动调整参数（增加校准测试）
3. 执行: 使用优化后的参数
4. 结果: 成功，更新历史
```

## 自适应参数调整示例

### 滑动验证码参数调整

**初始参数**：
```python
{
    "calibration_tests": 5,
    "segments": 20,
    "fast_ratio": 0.85
}
```

**如果成功率 < 50%**：
```python
{
    "calibration_tests": 7,      # 增加校准测试
    "segments": 25,              # 增加分段数
    "fast_ratio": 0.80           # 调整速度比例
}
```

**如果置信度 < 0.6**：
```python
{
    "calibration_tests": 8,      # 进一步增加校准
    "segments": 30,              # 更多分段（更平滑）
    "fast_ratio": 0.75           # 更慢的速度
}
```

## 策略历史学习示例

### 学习过程

**第1次尝试**：
- 方法: `vision_model`
- 结果: 成功
- 记录: `{success_count: 1, failure_count: 0, avg_confidence: 0.92}`

**第2次尝试**：
- 方法: `vision_model`
- 结果: 失败
- 记录: `{success_count: 1, failure_count: 1, avg_confidence: 0.92}`
- 得分: `0.5 * 0.6 + 0.92 * 0.3 + 1.0 * 0.1 = 0.676`

**第3次尝试**：
- 方法: `ocr` (备用)
- 结果: 成功
- 记录: `{success_count: 1, failure_count: 0, avg_confidence: 0.85}`
- 得分: `1.0 * 0.6 + 0.85 * 0.3 + 1.0 * 0.1 = 0.955`

**第4次尝试**：
- 系统选择: `ocr` (得分更高)
- 结果: 成功
- 更新: OCR得分进一步提高

## 配置选项

### StrategyConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_attempts` | int | 3 | 最大尝试次数 |
| `confidence_threshold` | float | 0.5 | 置信度阈值 |
| `enable_fallback` | bool | True | 是否启用回退 |
| `enable_learning` | bool | True | 是否启用学习 |
| `adaptive_params` | bool | True | 是否自适应调整参数 |

## 性能优化

### 1. 策略缓存

系统会缓存策略得分，避免重复计算：

```python
# 首次计算
score = calculate_strategy_score("image", "vision_model")  # 计算

# 后续使用缓存
score = get_cached_score("image", "vision_model")  # 从缓存读取
```

### 2. 并行尝试

对于低置信度的情况，可以并行尝试多种方法：

```python
# 并行执行多个策略
results = await asyncio.gather(
    try_vision_model(),
    try_ocr(),
    try_fallback()
)
# 选择最佳结果
best_result = max(results, key=lambda r: r.confidence)
```

### 3. 预加载策略

系统启动时预加载常用策略：

```python
# 预加载常用验证码类型的策略
preload_strategies(["image", "slider", "click"])
```

## 监控和调试

### 查看策略执行日志

```python
# 启用详细日志
import logging
logging.getLogger("automation_framework.src.core.captcha_adaptive_strategy").setLevel(logging.DEBUG)
```

### 获取策略统计

```python
# 获取所有类型的统计
stats = adaptive_strategy.get_strategy_statistics()

# 输出示例
{
    "image": {
        "vision_model": {
            "success_rate": 0.95,
            "avg_confidence": 0.92,
            "avg_time": 1.2,
            "total_attempts": 100
        },
        "ocr": {
            "success_rate": 0.85,
            "avg_confidence": 0.78,
            "avg_time": 0.8,
            "total_attempts": 50
        }
    }
}
```

## 最佳实践

### 1. 启用学习机制

```python
config = StrategyConfig(enable_learning=True)
```

### 2. 定期查看统计

```python
# 每周查看一次统计，了解各方法的性能
weekly_stats = adaptive_strategy.get_strategy_statistics()
```

### 3. 根据统计调整配置

```python
# 如果某种方法成功率持续低，可以降低其优先级
if stats["image"]["ocr"]["success_rate"] < 0.5:
    # 调整OCR优先级
    adaptive_strategy._strategy_priority["ocr"] = StrategyPriority.LOW
```

### 4. 重置统计（如果需要）

```python
# 如果系统更新后，重置统计以重新学习
adaptive_strategy.reset_statistics()
```

## 优势总结

1. **自动优化**：无需手动调整，系统自动学习最优策略
2. **高成功率**：多策略尝试，选择最佳方法
3. **自适应参数**：根据场景自动调整参数
4. **历史学习**：基于历史数据优化策略选择
5. **灵活扩展**：易于添加新的处理策略

## 未来扩展

1. **多模型融合**：同时使用多个视觉模型，综合结果
2. **实时调整**：根据实时反馈动态调整策略
3. **A/B测试**：对比不同策略的效果
4. **机器学习**：使用ML模型预测最佳策略
5. **分布式学习**：多个实例共享学习结果
