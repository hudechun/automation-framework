"""
自适应验证码处理示例
演示自适应策略如何根据场景自动调整
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.captcha_adaptive_strategy import AdaptiveCaptchaStrategy, StrategyConfig, StrategyResult


async def simulate_adaptive_strategy():
    """模拟自适应策略的执行过程"""
    print("=" * 60)
    print("自适应验证码处理策略演示")
    print("=" * 60)
    
    # 创建自适应策略管理器
    strategy = AdaptiveCaptchaStrategy(
        vision_model_provider="qwen",
        config=StrategyConfig(
            max_attempts=3,
            confidence_threshold=0.5,
            enable_learning=True,
            adaptive_params=True
        )
    )
    
    # 模拟场景1: 清晰图形验证码（高置信度）
    print("\n场景1: 清晰图形验证码")
    print("-" * 60)
    recognition_data_1 = {
        "type": "image",
        "data": {"text": "ABC123"},
        "confidence": 0.95,
        "description": "清晰的图形验证码"
    }
    
    # 模拟处理函数
    async def handler_1(method: str, params: dict) -> dict:
        if method == "vision_model":
            return {"success": True, "confidence": 0.95}
        return {"success": False}
    
    result_1 = await strategy.execute_adaptive_strategy(
        captcha_type="image",
        recognition_data=recognition_data_1,
        handler_func=handler_1
    )
    print(f"结果: {result_1.success}, 方法: {result_1.method}, 置信度: {result_1.confidence:.2f}")
    
    # 模拟场景2: 模糊图形验证码（低置信度）
    print("\n场景2: 模糊图形验证码")
    print("-" * 60)
    recognition_data_2 = {
        "type": "image",
        "data": {"text": "XY7Z"},
        "confidence": 0.45,
        "description": "模糊的图形验证码"
    }
    
    attempt_count = 0
    async def handler_2(method: str, params: dict) -> dict:
        nonlocal attempt_count
        attempt_count += 1
        if method == "vision_model" and attempt_count == 1:
            return {"success": False, "confidence": 0.45, "error": "识别失败"}
        elif method == "ocr":
            return {"success": True, "confidence": 0.78}
        return {"success": False}
    
    result_2 = await strategy.execute_adaptive_strategy(
        captcha_type="image",
        recognition_data=recognition_data_2,
        handler_func=handler_2
    )
    print(f"结果: {result_2.success}, 方法: {result_2.method}, 置信度: {result_2.confidence:.2f}")
    print(f"尝试次数: {attempt_count}")
    
    # 模拟场景3: 数学计算题验证码
    print("\n场景3: 数学计算题验证码")
    print("-" * 60)
    recognition_data_3 = {
        "type": "image",
        "data": {"text": "6-9=?"},
        "confidence": 0.92,
        "description": "数学计算题验证码"
    }
    
    async def handler_3(method: str, params: dict) -> dict:
        if method == "math_calculator":
            return {"success": True, "confidence": 0.99}
        return {"success": False}
    
    result_3 = await strategy.execute_adaptive_strategy(
        captcha_type="image",
        recognition_data=recognition_data_3,
        handler_func=handler_3
    )
    print(f"结果: {result_3.success}, 方法: {result_3.method}, 置信度: {result_3.confidence:.2f}")
    
    # 查看策略统计
    print("\n策略统计信息:")
    print("-" * 60)
    stats = strategy.get_strategy_statistics("image")
    for method, data in stats.get("image", {}).items():
        print(f"{method}:")
        print(f"  成功率: {data['success_rate']:.2%}")
        print(f"  平均置信度: {data['avg_confidence']:.2f}")
        print(f"  平均耗时: {data.get('avg_time', 0):.2f}s")
        print(f"  总尝试次数: {data['total_attempts']}")
    
    # 模拟场景4: 滑动验证码（自适应参数调整）
    print("\n场景4: 滑动验证码（自适应参数）")
    print("-" * 60)
    recognition_data_4 = {
        "type": "slider",
        "data": {"gap_x": 150.5, "gap_width": 50.0},
        "confidence": 0.65,
        "description": "滑动验证码"
    }
    
    async def handler_4(method: str, params: dict) -> dict:
        # 检查参数是否被自适应调整
        if "calibration_tests" in params:
            print(f"  自适应参数: calibration_tests={params['calibration_tests']}")
        return {"success": True, "confidence": 0.65}
    
    result_4 = await strategy.execute_adaptive_strategy(
        captcha_type="slider",
        recognition_data=recognition_data_4,
        handler_func=handler_4
    )
    print(f"结果: {result_4.success}, 方法: {result_4.method}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


async def demonstrate_learning_process():
    """演示学习过程"""
    print("\n" + "=" * 60)
    print("策略学习过程演示")
    print("=" * 60)
    
    strategy = AdaptiveCaptchaStrategy(
        config=StrategyConfig(enable_learning=True)
    )
    
    # 模拟多次尝试，观察策略选择的变化
    scenarios = [
        ("vision_model", True, 0.92),
        ("vision_model", False, 0.45),
        ("ocr", True, 0.78),
        ("ocr", True, 0.82),
        ("vision_model", True, 0.88),
    ]
    
    print("\n模拟5次验证码处理:")
    for i, (method, success, confidence) in enumerate(scenarios, 1):
        # 记录结果
        result = StrategyResult(
            success=success,
            method=method,
            confidence=confidence,
            execution_time=1.0
        )
        strategy._record_strategy_result("image", method, result)
        
        # 计算当前得分
        score = strategy._calculate_strategy_score("image", method)
        print(f"{i}. 方法: {method}, 成功: {success}, 置信度: {confidence:.2f}, 得分: {score:.3f}")
    
    # 查看最终统计
    print("\n最终统计:")
    stats = strategy.get_strategy_statistics("image")
    for method, data in stats.get("image", {}).items():
        print(f"{method}: 成功率={data['success_rate']:.2%}, 得分={strategy._calculate_strategy_score('image', method):.3f}")


if __name__ == "__main__":
    asyncio.run(simulate_adaptive_strategy())
    asyncio.run(demonstrate_learning_process())
