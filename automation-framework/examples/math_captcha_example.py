"""
数学计算题验证码处理示例
演示如何处理 "6-9=?" 这类数学计算题验证码
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.math_captcha_solver import MathCaptchaSolver


def test_math_captcha_solver():
    """测试数学计算题求解器"""
    print("=" * 50)
    print("数学计算题验证码求解器测试")
    print("=" * 50)
    
    test_cases = [
        "6-9=?",
        "6-9=？",
        "6 - 9 = ?",
        "3+5=?",
        "2*4=?",
        "10/2=?",
        "8×3=？",
        "15÷3=？",
        "ABC123",  # 非数学计算题
        "验证码",  # 非数学计算题
    ]
    
    for test_case in test_cases:
        print(f"\n测试用例: {test_case}")
        print(f"  是否为数学计算题: {MathCaptchaSolver.is_math_captcha(test_case)}")
        
        result = MathCaptchaSolver.solve(test_case)
        if result:
            calc_result, expression = result
            print(f"  计算结果: {expression} -> {calc_result}")
        else:
            extracted = MathCaptchaSolver.extract_and_solve(test_case)
            if extracted:
                print(f"  提取并计算结果: {test_case} -> {extracted}")
            else:
                print(f"  无法计算（非数学计算题或格式不支持）")


async def example_math_captcha_handling():
    """
    示例：在验证码处理流程中使用数学计算题求解
    
    流程：
    1. 视觉模型识别验证码文本 "6-9=?"
    2. 检测到是数学计算题
    3. 计算结果 "-3"
    4. 填写 "-3" 到输入框
    """
    print("\n" + "=" * 50)
    print("数学计算题验证码处理流程示例")
    print("=" * 50)
    
    # 模拟视觉模型识别结果
    recognition_data = {
        "type": "image",
        "data": {
            "text": "6-9=?"
        },
        "confidence": 0.95,
        "description": "图形验证码，包含数学计算题"
    }
    
    print(f"\n1. 视觉模型识别结果:")
    print(f"   文本: {recognition_data['data']['text']}")
    
    captcha_text = recognition_data['data']['text']
    
    # 检测是否是数学计算题
    print(f"\n2. 检测是否为数学计算题:")
    is_math = MathCaptchaSolver.is_math_captcha(captcha_text)
    print(f"   结果: {is_math}")
    
    if is_math:
        # 求解
        print(f"\n3. 求解数学计算题:")
        result = MathCaptchaSolver.extract_and_solve(captcha_text)
        if result:
            print(f"   原始表达式: {captcha_text}")
            print(f"   计算结果: {result}")
            print(f"\n4. 填写验证码:")
            print(f"   填写到输入框的值: {result}")
            print(f"   [成功] 成功处理数学计算题验证码！")
        else:
            print(f"   ❌ 无法求解")
    else:
        print(f"   不是数学计算题，直接使用原始文本")


if __name__ == "__main__":
    # 测试数学计算题求解器
    test_math_captcha_solver()
    
    # 运行示例
    asyncio.run(example_math_captcha_handling())
