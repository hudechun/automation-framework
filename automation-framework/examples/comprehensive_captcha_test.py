"""
全面的验证码类型测试用例
测试所有支持的验证码类型和场景
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.math_captcha_solver import MathCaptchaSolver
from src.core.captcha_types import CaptchaType


def test_math_captcha_variants():
    """测试数学计算题验证码的各种变体"""
    print("=" * 60)
    print("数学计算题验证码变体测试")
    print("=" * 60)
    
    test_cases = [
        # 基本格式
        ("6-9=?", "-3", "基本减法"),
        ("3+5=?", "8", "基本加法"),
        ("2*4=?", "8", "基本乘法"),
        ("10/2=?", "5", "基本除法"),
        
        # 中文问号
        ("6-9=？", "-3", "中文问号"),
        ("3+5=？", "8", "中文问号加法"),
        
        # 带空格
        ("6 - 9 = ?", "-3", "带空格"),
        ("3 + 5 = ?", "8", "带空格加法"),
        ("2 * 4 = ?", "8", "带空格乘法"),
        
        # 中文运算符
        ("8×3=？", "24", "中文乘号"),
        ("15÷3=？", "5", "中文除号"),
        ("6 - 9 = ？", "-3", "中文问号+空格"),
        
        # 边界情况
        ("0+0=?", "0", "零加法"),
        ("10-10=?", "0", "零结果"),
        ("1*1=?", "1", "单位乘法"),
        ("10/1=?", "10", "除以1"),
        
        # 负数结果
        ("5-10=?", "-5", "负数结果"),
        ("0-5=?", "-5", "零减数"),
        
        # 大数
        ("100+200=?", "300", "大数加法"),
        ("1000-500=?", "500", "大数减法"),
        
        # 非数学计算题（应该返回None）
        ("ABC123", None, "非数学计算题-字母数字"),
        ("验证码", None, "非数学计算题-中文"),
        ("123", None, "非数学计算题-纯数字"),
        ("6-9", None, "非数学计算题-无等号"),
    ]
    
    passed = 0
    failed = 0
    
    for test_input, expected, description in test_cases:
        result = MathCaptchaSolver.extract_and_solve(test_input)
        is_match = (result == expected) or (result is None and expected is None)
        
        status = "[通过]" if is_match else "[失败]"
        print(f"{status} {description}: {test_input}")
        print(f"  期望: {expected}, 实际: {result}")
        
        if is_match:
            passed += 1
        else:
            failed += 1
        print()
    
    print(f"总计: {passed} 通过, {failed} 失败")
    return passed, failed


def test_captcha_type_enum():
    """测试验证码类型枚举"""
    print("=" * 60)
    print("验证码类型枚举测试")
    print("=" * 60)
    
    captcha_types = [
        (CaptchaType.IMAGE, "图形验证码"),
        (CaptchaType.SLIDER, "滑动验证码"),
        (CaptchaType.CLICK, "点选验证码"),
        (CaptchaType.ROTATE, "旋转验证码"),
        (CaptchaType.PUZZLE, "拼图验证码"),
        (CaptchaType.SMS, "短信验证码"),
        (CaptchaType.EMAIL, "邮箱验证码"),
        (CaptchaType.VOICE, "语音验证码"),
        (CaptchaType.RECAPTCHA, "Google reCAPTCHA"),
        (CaptchaType.HCAPTCHA, "hCaptcha"),
        (CaptchaType.TURNSTILE, "Cloudflare Turnstile"),
        (CaptchaType.BEHAVIORAL, "行为验证码"),
        (CaptchaType.UNKNOWN, "未知类型"),
    ]
    
    print("支持的验证码类型:")
    for i, (captcha_type, description) in enumerate(captcha_types, 1):
        print(f"{i:2d}. {captcha_type.value:15s} - {description}")
    
    print(f"\n总计: {len(captcha_types)} 种验证码类型")


def test_image_captcha_variants():
    """测试图形验证码的各种变体"""
    print("=" * 60)
    print("图形验证码变体测试")
    print("=" * 60)
    
    variants = [
        # 数字验证码
        ("1234", "4位数字"),
        ("12345", "5位数字"),
        ("123456", "6位数字"),
        ("0000", "全零数字"),
        
        # 字母验证码
        ("ABCD", "大写字母"),
        ("abcd", "小写字母"),
        ("AbCd", "大小写混合"),
        
        # 数字+字母混合
        ("A1B2", "数字+大写字母"),
        ("a1b2", "数字+小写字母"),
        ("A1b2", "数字+大小写混合"),
        
        # 中文验证码
        ("验证码", "纯中文"),
        ("验证码123", "中文+数字"),
        ("验证码ABC", "中文+字母"),
        
        # 数学计算题
        ("6-9=?", "数学计算题-减法"),
        ("3+5=?", "数学计算题-加法"),
        ("2*4=?", "数学计算题-乘法"),
        ("10/2=?", "数学计算题-除法"),
        
        # 特殊字符
        ("!@#$", "特殊字符"),
        ("A1@B2", "混合+特殊字符"),
    ]
    
    print("图形验证码变体:")
    for i, (variant, description) in enumerate(variants, 1):
        is_math = MathCaptchaSolver.is_math_captcha(variant)
        math_label = " [数学计算题]" if is_math else ""
        print(f"{i:2d}. {variant:15s} - {description}{math_label}")
    
    print(f"\n总计: {len(variants)} 种变体")


def test_slider_captcha_scenarios():
    """测试滑动验证码的各种场景"""
    print("=" * 60)
    print("滑动验证码场景测试")
    print("=" * 60)
    
    scenarios = [
        ("缺口在右侧", "滑块在左侧，缺口在右侧"),
        ("缺口在左侧", "滑块在右侧，缺口在左侧"),
        ("缺口在中间", "缺口在轨道中间位置"),
        ("垂直滑动", "垂直方向的滑动验证码"),
        ("多段滑动", "需要滑动多段的验证码"),
        ("极验滑动", "极验（Geetest）滑动验证码"),
        ("网易易盾滑动", "网易易盾滑动验证码"),
        ("顶象滑动", "顶象滑动验证码"),
    ]
    
    print("滑动验证码场景:")
    for i, (scenario, description) in enumerate(scenarios, 1):
        print(f"{i:2d}. {scenario:15s} - {description}")
    
    print(f"\n总计: {len(scenarios)} 种场景")


def test_click_captcha_scenarios():
    """测试点选验证码的各种场景"""
    print("=" * 60)
    print("点选验证码场景测试")
    print("=" * 60)
    
    scenarios = [
        ("文字点选", "点击指定文字"),
        ("多文字点选", "点击多个文字"),
        ("顺序点选", "按顺序点击"),
        ("图片点选", "点击指定物体"),
        ("多物体点选", "点击多个物体"),
        ("中文提示", "中文提示的点选"),
        ("英文提示", "英文提示的点选"),
    ]
    
    print("点选验证码场景:")
    for i, (scenario, description) in enumerate(scenarios, 1):
        print(f"{i:2d}. {scenario:15s} - {description}")
    
    print(f"\n总计: {len(scenarios)} 种场景")


def test_special_scenarios():
    """测试特殊场景"""
    print("=" * 60)
    print("特殊场景测试")
    print("=" * 60)
    
    scenarios = [
        ("验证码刷新", "自动或手动刷新验证码"),
        ("验证码过期", "验证码过期处理"),
        ("验证码错误", "验证码错误处理"),
        ("弹窗验证码", "弹窗中的验证码"),
        ("iframe验证码", "iframe中的验证码"),
        ("移动端验证码", "移动设备上的验证码"),
        ("多层验证", "需要完成多层验证"),
        ("混合验证", "同时显示多种验证码"),
    ]
    
    print("特殊场景:")
    for i, (scenario, description) in enumerate(scenarios, 1):
        print(f"{i:2d}. {scenario:15s} - {description}")
    
    print(f"\n总计: {len(scenarios)} 种场景")


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("全面的验证码类型测试")
    print("=" * 60 + "\n")
    
    # 测试数学计算题变体
    math_passed, math_failed = test_math_captcha_variants()
    print("\n")
    
    # 测试验证码类型枚举
    test_captcha_type_enum()
    print("\n")
    
    # 测试图形验证码变体
    test_image_captcha_variants()
    print("\n")
    
    # 测试滑动验证码场景
    test_slider_captcha_scenarios()
    print("\n")
    
    # 测试点选验证码场景
    test_click_captcha_scenarios()
    print("\n")
    
    # 测试特殊场景
    test_special_scenarios()
    print("\n")
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"数学计算题测试: {math_passed} 通过, {math_failed} 失败")
    print(f"验证码类型: 13 种")
    print(f"图形验证码变体: 多种")
    print(f"滑动验证码场景: 8 种")
    print(f"点选验证码场景: 7 种")
    print(f"特殊场景: 8 种")
    print("\n[完成] 所有测试用例已列举")


if __name__ == "__main__":
    asyncio.run(main())
