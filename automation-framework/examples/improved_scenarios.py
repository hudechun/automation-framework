"""
改进后的场景示例 - 使用新功能
"""
from automation_framework.src.core.actions import (
    GoToURL, WaitForLoad, Type, Click, GetText, GetAttribute, Screenshot
)
from automation_framework.src.core.smart_wait import (
    wait_for_element_visible,
    wait_for_text,
    wait_for_network_idle
)
from automation_framework.src.core.control_flow import Loop, If
from automation_framework.src.core.element_locator import ElementLocator, LocatorType
from automation_framework.src.core.captcha_action import HandleCaptcha
from automation_framework.src.core.anti_detection import AntiDetectionConfig, ProxyConfig


# ==================== 场景1：改进的价格监控（使用智能等待） ====================

def scenario_1_improved():
    """电商价格监控 - 使用智能等待"""
    actions = [
        GoToURL(url="https://www.jd.com"),
        wait_for_network_idle(timeout=30000),  # 智能等待：网络空闲
        Type(selector="input#key", text="iPhone 15"),
        Click(selector="button.search-btn"),
        wait_for_network_idle(timeout=30000),  # 智能等待：搜索结果加载完成
        wait_for_element_visible(".goods-item:first-child", timeout=10000),  # 智能等待：商品出现
        GetText(selector=".goods-item:first-child .price"),
        Screenshot(path="screenshot_price.png")
    ]
    return actions


# ==================== 场景2：改进的数据采集（使用循环） ====================

def scenario_2_improved():
    """数据采集 - 使用循环操作"""
    # 采集前10条新闻
    loop_actions = []
    for i in range(1, 11):
        loop_actions.extend([
            GetText(selector=f".news-item:nth-child({i}) .title"),
            GetAttribute(selector=f".news-item:nth-child({i}) a", attribute="href"),
        ])
    
    actions = [
        GoToURL(url="https://news.example.com"),
        wait_for_network_idle(timeout=30000),
        wait_for_element_visible(".news-list", timeout=10000),
        *loop_actions,  # 展开循环操作
        Screenshot(path="news_list.png")
    ]
    return actions


# ==================== 场景3：改进的登录（使用条件分支和验证码） ====================

def scenario_3_improved():
    """登录操作 - 使用条件分支和验证码处理"""
    
    # 定义条件函数（检查是否需要验证码）
    def needs_captcha(context):
        # 实际实现需要检查页面是否有验证码
        return context.get("has_captcha", False)
    
    actions = [
        GoToURL(url="https://example.com/login"),
        wait_for_network_idle(timeout=30000),
        wait_for_element_visible("input[name='username']", timeout=10000),
        Type(selector="input[name='username']", text="user123"),
        Type(selector="input[name='password']", text="password123"),
        # 条件分支：如果需要验证码，先处理验证码
        If(
            condition=needs_captcha,
            then_actions=[
                HandleCaptcha(manual_input=True),  # 处理验证码
            ],
            else_actions=[]
        ),
        Click(selector="button[type='submit']"),
        wait_for_network_idle(timeout=30000),
        wait_for_element_visible(".user-menu", timeout=10000),
        GetText(selector=".user-menu .username"),
    ]
    return actions


# ==================== 场景4：改进的元素定位（使用多种定位策略） ====================

def scenario_4_improved():
    """使用多种定位策略提高成功率"""
    
    # 使用文本匹配定位（更稳定）
    actions = [
        GoToURL(url="https://example.com"),
        wait_for_network_idle(timeout=30000),
        # 使用文本匹配而不是CSS选择器
        Click(selector="提交", locator_type="text"),  # 通过文本"提交"定位按钮
        wait_for_text("操作成功", timeout=10000),  # 等待成功文本出现
        GetText(selector=".result"),
    ]
    return actions


# ==================== 场景5：反检测配置 ====================

def scenario_5_anti_detection():
    """使用反检测配置"""
    
    # 创建反检测配置
    anti_detection = AntiDetectionConfig(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        timezone="Asia/Shanghai",
        extra_http_headers={
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
    )
    
    # 创建代理配置（可选）
    proxy = ProxyConfig(
        server="http://proxy.example.com:8080",
        username="user",
        password="pass"
    )
    
    # 在启动浏览器时使用
    # driver = BrowserDriver()
    # await driver.start(anti_detection=anti_detection, proxy=proxy)
    
    actions = [
        GoToURL(url="https://example.com"),
        wait_for_network_idle(timeout=30000),
        GetText(selector=".content"),
    ]
    return actions


# ==================== 场景6：综合使用所有改进 ====================

def scenario_6_comprehensive():
    """综合使用所有改进功能"""
    
    # 定义条件：检查是否已登录
    def is_logged_in(context):
        return context.get("user_id") is not None
    
    # 定义条件：检查是否有更多数据
    def has_more_data(context):
        return context.get("has_more", True)
    
    actions = [
        GoToURL(url="https://example.com/shop"),
        wait_for_network_idle(timeout=30000),
        
        # 条件分支：如果未登录，先登录
        If(
            condition=lambda ctx: not is_logged_in(ctx),
            then_actions=[
                Click(selector="登录", locator_type="text"),  # 使用文本定位
                wait_for_element_visible("input[name='username']", timeout=10000),
                Type(selector="input[name='username']", text="user"),
                Type(selector="input[name='password']", text="pass"),
                HandleCaptcha(manual_input=True),  # 处理验证码
                Click(selector="button[type='submit']"),
                wait_for_text("登录成功", timeout=10000),  # 智能等待文本
            ],
            else_actions=[]
        ),
        
        # 循环采集商品数据
        # 注意：实际实现中，Loop需要从JavaScript或页面状态动态获取数据
        # 这里简化示例
        wait_for_element_visible(".product-list", timeout=10000),
        
        # 采集前20个商品
        *[GetText(selector=f".product-item:nth-child({i}) .name") for i in range(1, 21)],
        *[GetAttribute(selector=f".product-item:nth-child({i}) .price", attribute="textContent") for i in range(1, 21)],
        
        Screenshot(path="products.png"),
    ]
    return actions
