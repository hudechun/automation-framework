"""
本地OCR使用示例
演示如何使用Tesseract进行本地OCR识别
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.local_ocr import LocalOCR, get_local_ocr


async def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 创建OCR实例
    ocr = LocalOCR(lang="eng+chi_sim")
    
    # 检查是否可用
    if not ocr.is_available():
        print("❌ Tesseract OCR不可用，请先安装Tesseract")
        print("   安装指南: https://github.com/tesseract-ocr/tesseract")
        return
    
    print("✅ Tesseract OCR可用")
    
    # 查看支持的语言
    languages = ocr.get_supported_languages()
    print(f"支持的语言: {languages[:10]}...")  # 只显示前10个
    
    # 注意：这里需要实际的图像文件
    # 示例：如果有captcha.png文件
    image_path = "captcha.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # 识别
        text = await ocr.recognize(image_bytes, preprocess=True)
        print(f"识别结果: {text}")
    else:
        print(f"⚠️  图像文件不存在: {image_path}")
        print("   请准备一个验证码图像文件进行测试")


async def example_custom_config():
    """自定义配置示例"""
    print("\n" + "=" * 60)
    print("示例2: 自定义配置")
    print("=" * 60)
    
    # Windows用户可能需要指定Tesseract路径
    tesseract_cmd = None
    if sys.platform == "win32":
        # Windows默认路径
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                tesseract_cmd = path
                break
    
    # 创建自定义OCR实例
    ocr = LocalOCR(
        tesseract_cmd=tesseract_cmd,
        lang="eng",  # 只识别英文
        config="--psm 7"  # 单行文本模式
    )
    
    if ocr.is_available():
        print("✅ 自定义配置的OCR可用")
        if tesseract_cmd:
            print(f"   Tesseract路径: {tesseract_cmd}")
        print(f"   语言: {ocr.lang}")
        print(f"   配置: {ocr.config}")
    else:
        print("❌ OCR不可用")


async def example_global_instance():
    """全局实例示例"""
    print("\n" + "=" * 60)
    print("示例3: 使用全局实例")
    print("=" * 60)
    
    # 获取全局OCR实例（单例模式）
    ocr1 = get_local_ocr()
    ocr2 = get_local_ocr()
    
    # 两个实例是同一个对象
    print(f"ocr1 is ocr2: {ocr1 is ocr2}")  # True
    
    if ocr1.is_available():
        print("✅ 全局OCR实例可用")
    else:
        print("❌ 全局OCR实例不可用")


async def example_preprocess_comparison():
    """预处理对比示例"""
    print("\n" + "=" * 60)
    print("示例4: 预处理对比")
    print("=" * 60)
    
    ocr = LocalOCR(lang="eng+chi_sim")
    
    if not ocr.is_available():
        print("❌ OCR不可用")
        return
    
    image_path = "captcha.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # 不使用预处理
        text_no_preprocess = await ocr.recognize(
            image_bytes,
            preprocess=False
        )
        print(f"不使用预处理: {text_no_preprocess}")
        
        # 使用预处理
        text_with_preprocess = await ocr.recognize(
            image_bytes,
            preprocess=True
        )
        print(f"使用预处理: {text_with_preprocess}")
        
        # 对比结果
        if text_with_preprocess and text_no_preprocess:
            if text_with_preprocess != text_no_preprocess:
                print("✅ 预处理提高了识别率")
            else:
                print("ℹ️  预处理结果相同")
    else:
        print(f"⚠️  图像文件不存在: {image_path}")


async def example_language_selection():
    """语言选择示例"""
    print("\n" + "=" * 60)
    print("示例5: 语言选择")
    print("=" * 60)
    
    ocr = LocalOCR()
    
    if not ocr.is_available():
        print("❌ OCR不可用")
        return
    
    languages = ocr.get_supported_languages()
    print(f"支持的语言数量: {len(languages)}")
    
    # 测试不同语言配置
    test_languages = ["eng", "chi_sim", "eng+chi_sim"]
    
    for lang in test_languages:
        if lang in languages or any(l in languages for l in lang.split("+")):
            print(f"✅ {lang}: 支持")
        else:
            print(f"❌ {lang}: 不支持（需要安装语言包）")


async def example_sync_vs_async():
    """同步vs异步示例"""
    print("\n" + "=" * 60)
    print("示例6: 同步vs异步")
    print("=" * 60)
    
    ocr = LocalOCR(lang="eng+chi_sim")
    
    if not ocr.is_available():
        print("❌ OCR不可用")
        return
    
    image_path = "captcha.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # 异步方式（推荐）
        import time
        start = time.time()
        text_async = await ocr.recognize(image_bytes)
        async_time = time.time() - start
        print(f"异步方式: {text_async} (耗时: {async_time:.2f}s)")
        
        # 同步方式
        start = time.time()
        text_sync = ocr.recognize_sync(image_bytes)
        sync_time = time.time() - start
        print(f"同步方式: {text_sync} (耗时: {sync_time:.2f}s)")
        
        # 结果应该相同
        if text_async == text_sync:
            print("✅ 两种方式结果一致")
    else:
        print(f"⚠️  图像文件不存在: {image_path}")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("本地OCR (Tesseract) 使用示例")
    print("=" * 60)
    print("\n注意：")
    print("1. 需要先安装Tesseract OCR")
    print("2. 需要准备测试图像文件（captcha.png）")
    print("3. 安装Python依赖: pip install pytesseract pillow")
    print()
    
    # 运行所有示例
    await example_basic_usage()
    await example_custom_config()
    await example_global_instance()
    await example_preprocess_comparison()
    await example_language_selection()
    await example_sync_vs_async()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
    print("\n更多信息请查看: LOCAL_OCR_GUIDE.md")


if __name__ == "__main__":
    asyncio.run(main())
