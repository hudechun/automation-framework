"""
登录任务示例 - 包含验证码处理
任务：打开Chrome，访问登录页面，输入账号密码，点击登录，处理验证码
"""
from automation_framework.src.core.actions import (
    GoToURL, Type, Click, Sleep
)
from automation_framework.src.core.smart_wait import (
    wait_for_network_idle,
    wait_for_element_visible,
    wait_for_text
)
from automation_framework.src.core.captcha_action import HandleCaptcha
from automation_framework.src.core.anti_detection import AntiDetectionConfig
from automation_framework.src.drivers.browser_driver import BrowserDriver, BrowserType


async def login_with_captcha_example():
    """
    执行登录任务（包含验证码处理）
    
    步骤：
    1. 打开Chrome浏览器
    2. 访问登录页面 (XXXX.com/login)
    3. 输入账号 (abc)
    4. 输入密码 (abc123)
    5. 点击登录按钮
    6. 等待2秒（等待验证码出现）
    7. 检测并处理图形验证码
    """
    
    # ==================== 步骤1：配置浏览器和反检测 ====================
    
    # 创建反检测配置（可选，提高成功率）
    anti_detection = AntiDetectionConfig(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        timezone="Asia/Shanghai"
    )
    
    # 创建浏览器驱动（Chrome）
    driver = BrowserDriver(browser_type=BrowserType.CHROMIUM)
    
    # 启动浏览器（应用反检测配置）
    await driver.start(
        headless=False,  # 显示浏览器窗口（方便调试）
        anti_detection=anti_detection
    )
    
    # ==================== 步骤2：定义操作序列 ====================
    
    actions = [
        # 1. 访问登录页面
        GoToURL(url="https://XXXX.com/login"),
        
        # 2. 等待页面加载完成（智能等待：网络空闲）
        wait_for_network_idle(timeout=30000),
        
        # 3. 等待账号输入框出现（智能等待：元素可见）
        wait_for_element_visible("input[name='username'], input[type='text'][placeholder*='账号'], input[type='text'][placeholder*='用户名']", timeout=10000),
        
        # 4. 输入账号
        Type(
            selector="input[name='username'], input[type='text'][placeholder*='账号'], input[type='text'][placeholder*='用户名']",
            text="abc"
        ),
        
        # 5. 等待密码输入框出现
        wait_for_element_visible("input[name='password'], input[type='password']", timeout=10000),
        
        # 6. 输入密码
        Type(
            selector="input[name='password'], input[type='password']",
            text="abc123"
        ),
        
        # 7. 等待登录按钮出现
        wait_for_element_visible("button[type='submit'], button:has-text('登录'), .login-btn, #login-btn", timeout=10000),
        
        # 8. 点击登录按钮（使用多种定位策略）
        Click(
            selector="button[type='submit'], button:has-text('登录'), .login-btn, #login-btn",
            locator_type="css"  # 可以尝试多种策略
        ),
        
        # 9. 等待2秒（等待验证码弹出）
        # 注意：这里使用固定等待，因为验证码可能在点击后延迟出现
        # 更好的方式是使用智能等待（见下面的改进版本）
        Sleep(duration=2000),
        
        # 10. 检测并处理验证码
        # HandleCaptcha会自动检测验证码，如果检测到则处理
        HandleCaptcha(
            selector=None,  # 自动检测验证码图片（如果为None）
            manual_input=True,  # 支持人工输入验证码
            timeout=60000  # 验证码处理超时时间（60秒）
        ),
        
        # 11. 等待登录成功（智能等待：文本出现）
        wait_for_text("登录成功,欢迎", timeout=10000),
    ]
    
    # ==================== 步骤3：执行操作序列 ====================
    
    try:
        for i, action in enumerate(actions):
            print(f"[{i+1}/{len(actions)}] 执行操作: {action.__class__.__name__}")
            
            # 执行操作
            result = await action.execute(driver)
            
            # 如果是验证码处理，显示结果
            if isinstance(action, HandleCaptcha):
                if result.get("success"):
                    if result.get("captcha_detected"):
                        if result.get("captcha_solved"):
                            print("✓ 验证码已自动处理")
                        elif result.get("manual_input"):
                            print("⏳ 等待人工输入验证码...")
                            # 这里可以触发前端事件，通知用户输入验证码
                    else:
                        print("ℹ 未检测到验证码")
                else:
                    print(f"✗ 验证码处理失败: {result.get('error')}")
            
            print(f"✓ 操作完成: {action.__class__.__name__}\n")
        
        print("✅ 登录任务执行完成！")
        
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        raise
    
    finally:
        # 清理资源（可选，如果需要保持浏览器打开可以注释掉）
        # await driver.stop()
        pass


# ==================== 改进版本：使用智能等待验证码 ====================

async def login_with_captcha_improved():
    """
    改进版本：使用智能等待验证码出现，而不是固定等待2秒
    """
    from automation_framework.src.core.smart_wait import wait_for_custom
    
    driver = BrowserDriver(browser_type=BrowserType.CHROMIUM)
    await driver.start(headless=False)
    
    # 定义验证码检测函数
    async def check_captcha_appeared(driver):
        """检查验证码是否出现"""
        from automation_framework.src.core.captcha_action import CaptchaHandler
        captcha_handler = CaptchaHandler()
        has_captcha = await captcha_handler.detect_captcha(driver._current_page)
        return has_captcha
    
    actions = [
        GoToURL(url="https://XXXX.com/login"),
        wait_for_network_idle(timeout=30000),
        
        # 输入账号
        wait_for_element_visible("input[name='username']", timeout=10000),
        Type(selector="input[name='username']", text="abc"),
        
        # 输入密码
        wait_for_element_visible("input[name='password']", timeout=10000),
        Type(selector="input[name='password']", text="abc123"),
        
        # 点击登录
        wait_for_element_visible("button[type='submit']", timeout=10000),
        Click(selector="button[type='submit']"),
        
        # 智能等待验证码出现（而不是固定等待2秒）
        wait_for_custom(
            check_captcha_appeared,
            "等待验证码出现",
            timeout=10000  # 最多等待10秒
        ),
        
        # 处理验证码
        HandleCaptcha(manual_input=True, timeout=60000),
        
        # 等待登录成功
        wait_for_text("登录成功", timeout=10000),
    ]
    
    try:
        for action in actions:
            await action.execute(driver)
        print("✅ 登录任务执行完成！")
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        raise


# ==================== 使用文本定位的版本（更稳定） ====================

async def login_with_captcha_text_locator():
    """
    使用文本定位的版本（更稳定，不依赖CSS类名）
    """
    driver = BrowserDriver(browser_type=BrowserType.CHROMIUM)
    await driver.start(headless=False)
    
    actions = [
        GoToURL(url="https://XXXX.com/login"),
        wait_for_network_idle(timeout=30000),
        
        # 使用文本定位输入框（如果页面有标签）
        # 或者使用多种定位策略的组合
        Type(
            selector="input[name='username'], input[placeholder*='账号'], input[placeholder*='用户名']",
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
        
        # 等待验证码出现（智能等待）
        wait_for_element_visible("img[alt*='验证码'], img[alt*='captcha'], .captcha img", timeout=10000),
        
        # 处理验证码
        HandleCaptcha(
            selector="img[alt*='验证码'], img[alt*='captcha'], .captcha img",  # 指定验证码图片选择器
            manual_input=True,
            timeout=60000
        ),
        
        # 等待登录成功
        wait_for_text("登录成功,欢迎", timeout=10000),
    ]
    
    try:
        for action in actions:
            await action.execute(driver)
        print("✅ 登录任务执行完成！")
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        raise


# ==================== 主函数 ====================

if __name__ == "__main__":
    import asyncio
    
    # 执行示例
    print("=" * 60)
    print("登录任务示例 - 包含验证码处理")
    print("=" * 60)
    print()
    
    # 选择要执行的版本
    # 版本1：基础版本（固定等待2秒）
    # asyncio.run(login_with_captcha_example())
    
    # 版本2：改进版本（智能等待验证码）
    # asyncio.run(login_with_captcha_improved())
    
    # 版本3：使用文本定位（最稳定）
    # asyncio.run(login_with_captcha_text_locator())
    
    print("\n请取消注释上面的函数调用来执行相应的示例")
