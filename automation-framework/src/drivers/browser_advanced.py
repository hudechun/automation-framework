"""
浏览器高级功能实现
"""
from typing import Dict, Any, List, Optional
import json
import asyncio
from playwright.async_api import Page, BrowserContext


class FormFiller:
    """表单自动填充器"""
    
    def __init__(self, page: Page):
        """
        初始化表单填充器
        
        Args:
            page: Playwright页面对象
        """
        self.page = page
    
    async def fill_form(
        self,
        form_data: Dict[str, Any],
        validate: bool = True
    ) -> Dict[str, bool]:
        """
        批量填充表单
        
        Args:
            form_data: 表单数据字典 {selector: value}
            validate: 是否验证必填字段
            
        Returns:
            填充结果 {selector: success}
        """
        results = {}
        
        for selector, value in form_data.items():
            try:
                element = await self.page.query_selector(selector)
                if not element:
                    results[selector] = False
                    continue
                
                # 获取元素类型
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                input_type = await element.get_attribute("type")
                
                # 根据元素类型填充
                if tag_name == "input":
                    if input_type in ["text", "email", "password", "tel", "url"]:
                        await element.fill(str(value))
                    elif input_type == "checkbox":
                        if value:
                            await element.check()
                        else:
                            await element.uncheck()
                    elif input_type == "radio":
                        if value:
                            await element.check()
                elif tag_name == "select":
                    await element.select_option(str(value))
                elif tag_name == "textarea":
                    await element.fill(str(value))
                
                results[selector] = True
            except Exception as e:
                results[selector] = False
        
        if validate:
            validation_results = await self.validate_form()
            results["validation"] = validation_results
        
        return results
    
    async def validate_form(self) -> Dict[str, Any]:
        """
        验证表单（检查必填字段）
        
        Returns:
            验证结果
        """
        # 查找所有必填字段
        required_fields = await self.page.query_selector_all("[required]")
        
        validation = {
            "valid": True,
            "missing_fields": []
        }
        
        for field in required_fields:
            value = await field.input_value()
            if not value:
                selector = await field.evaluate(
                    "el => el.id || el.name || el.className"
                )
                validation["missing_fields"].append(selector)
                validation["valid"] = False
        
        return validation


class DynamicContentHandler:
    """动态内容处理器"""
    
    def __init__(self, page: Page):
        """
        初始化动态内容处理器
        
        Args:
            page: Playwright页面对象
        """
        self.page = page
    
    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 30000,
        state: str = "visible"
    ) -> bool:
        """
        等待元素出现
        
        Args:
            selector: 选择器
            timeout: 超时时间（毫秒）
            state: 元素状态（visible, hidden, attached, detached）
            
        Returns:
            是否成功
        """
        try:
            await self.page.wait_for_selector(
                selector,
                timeout=timeout,
                state=state
            )
            return True
        except:
            return False
    
    async def wait_for_network_idle(
        self,
        timeout: int = 30000,
        idle_time: int = 500
    ) -> bool:
        """
        等待网络请求完成
        
        Args:
            timeout: 超时时间（毫秒）
            idle_time: 空闲时间（毫秒）
            
        Returns:
            是否成功
        """
        try:
            await self.page.wait_for_load_state(
                "networkidle",
                timeout=timeout
            )
            return True
        except:
            return False
    
    async def handle_ajax(
        self,
        trigger_selector: str,
        wait_selector: str,
        timeout: int = 30000
    ) -> bool:
        """
        处理AJAX请求
        
        Args:
            trigger_selector: 触发AJAX的元素选择器
            wait_selector: 等待出现的元素选择器
            timeout: 超时时间
            
        Returns:
            是否成功
        """
        try:
            # 点击触发元素
            await self.page.click(trigger_selector)
            
            # 等待响应元素出现
            await self.page.wait_for_selector(
                wait_selector,
                timeout=timeout
            )
            return True
        except:
            return False
    
    async def wait_for_spa_navigation(
        self,
        url_pattern: str,
        timeout: int = 30000
    ) -> bool:
        """
        等待SPA页面导航
        
        Args:
            url_pattern: URL模式
            timeout: 超时时间
            
        Returns:
            是否成功
        """
        try:
            await self.page.wait_for_url(
                url_pattern,
                timeout=timeout
            )
            return True
        except:
            return False


class TabWindowManager:
    """标签页和窗口管理器"""
    
    def __init__(self, context: BrowserContext):
        """
        初始化管理器
        
        Args:
            context: 浏览器上下文
        """
        self.context = context
        self.pages: List[Page] = []
    
    async def new_tab(self, url: Optional[str] = None) -> Page:
        """
        打开新标签页
        
        Args:
            url: 要打开的URL（可选）
            
        Returns:
            新页面对象
        """
        page = await self.context.new_page()
        self.pages.append(page)
        
        if url:
            await page.goto(url)
        
        return page
    
    async def switch_tab(self, index: int) -> Optional[Page]:
        """
        切换到指定标签页
        
        Args:
            index: 标签页索引
            
        Returns:
            页面对象
        """
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None
    
    async def close_tab(self, index: int) -> bool:
        """
        关闭标签页
        
        Args:
            index: 标签页索引
            
        Returns:
            是否成功
        """
        if 0 <= index < len(self.pages):
            page = self.pages[index]
            await page.close()
            self.pages.remove(page)
            return True
        return False
    
    async def handle_popup(
        self,
        trigger_action: callable,
        timeout: int = 30000
    ) -> Optional[Page]:
        """
        处理弹出窗口
        
        Args:
            trigger_action: 触发弹窗的操作（async函数）
            timeout: 超时时间
            
        Returns:
            弹出窗口的页面对象
        """
        try:
            async with self.context.expect_page(timeout=timeout) as page_info:
                await trigger_action()
            
            popup = await page_info.value
            self.pages.append(popup)
            return popup
        except:
            return None
    
    def list_tabs(self) -> List[Page]:
        """
        列出所有标签页
        
        Returns:
            页面列表
        """
        return self.pages.copy()


class SessionManager:
    """会话和Cookie管理器"""
    
    def __init__(self, context: BrowserContext):
        """
        初始化会话管理器
        
        Args:
            context: 浏览器上下文
        """
        self.context = context
    
    async def get_cookies(
        self,
        urls: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取Cookies
        
        Args:
            urls: URL列表（可选，获取特定URL的cookies）
            
        Returns:
            Cookie列表
        """
        if urls:
            return await self.context.cookies(urls)
        return await self.context.cookies()
    
    async def set_cookies(
        self,
        cookies: List[Dict[str, Any]]
    ) -> None:
        """
        设置Cookies
        
        Args:
            cookies: Cookie列表
        """
        await self.context.add_cookies(cookies)
    
    async def clear_cookies(self) -> None:
        """清除所有Cookies"""
        await self.context.clear_cookies()
    
    async def save_session(self, file_path: str) -> bool:
        """
        保存会话到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            # 获取cookies和storage state
            state = await self.context.storage_state()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            return True
        except Exception as e:
            return False
    
    async def load_session(self, file_path: str) -> bool:
        """
        从文件加载会话
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 设置cookies
            if 'cookies' in state:
                await self.context.add_cookies(state['cookies'])
            
            # 设置localStorage
            if 'origins' in state:
                for origin in state['origins']:
                    if 'localStorage' in origin:
                        # 注意：需要在对应的页面上下文中设置
                        pass
            
            return True
        except Exception as e:
            return False
    
    async def get_local_storage(
        self,
        page: Page
    ) -> Dict[str, str]:
        """
        获取LocalStorage
        
        Args:
            page: 页面对象
            
        Returns:
            LocalStorage数据
        """
        return await page.evaluate("() => Object.assign({}, window.localStorage)")
    
    async def set_local_storage(
        self,
        page: Page,
        data: Dict[str, str]
    ) -> None:
        """
        设置LocalStorage
        
        Args:
            page: 页面对象
            data: 数据字典
        """
        for key, value in data.items():
            await page.evaluate(
                f"() => window.localStorage.setItem('{key}', '{value}')"
            )
