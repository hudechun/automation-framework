"""
浏览器自动化示例
"""
import asyncio
from src.sdk import AutomationClient


async def example_web_scraping():
    """示例1：网页数据抓取"""
    async with AutomationClient() as client:
        task = await client.tasks.create(
            name="Web Scraping Example",
            description="Scrape data from example.com",
            actions=[
                {"type": "goto", "url": "https://example.com"},
                {"type": "wait_for_selector", "selector": "h1"},
                {"type": "get_text", "selector": "h1"},
                {"type": "screenshot", "path": "example.png"}
            ]
        )
        
        result = await client.tasks.execute_and_wait(task["id"])
        print(f"Scraping completed: {result['status']}")


async def example_form_filling():
    """示例2：表单自动填充"""
    async with AutomationClient() as client:
        task = await client.tasks.create(
            name="Form Filling Example",
            description="Fill and submit a form",
            actions=[
                {"type": "goto", "url": "https://example.com/form"},
                {"type": "type", "selector": "#name", "text": "John Doe"},
                {"type": "type", "selector": "#email", "text": "john@example.com"},
                {"type": "click", "selector": "#submit"},
                {"type": "wait_for_navigation"},
                {"type": "screenshot", "path": "form_submitted.png"}
            ]
        )
        
        result = await client.tasks.execute_and_wait(task["id"])
        print(f"Form submission completed: {result['status']}")


async def example_multi_page_navigation():
    """示例3：多页面导航"""
    async with AutomationClient() as client:
        task = await client.tasks.create(
            name="Multi-Page Navigation",
            description="Navigate through multiple pages",
            actions=[
                {"type": "goto", "url": "https://example.com/page1"},
                {"type": "click", "selector": "a[href='/page2']"},
                {"type": "wait_for_load"},
                {"type": "click", "selector": "a[href='/page3']"},
                {"type": "wait_for_load"},
                {"type": "screenshot", "path": "final_page.png"}
            ]
        )
        
        result = await client.tasks.execute_and_wait(task["id"])
        print(f"Navigation completed: {result['status']}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_web_scraping())
    # asyncio.run(example_form_filling())
    # asyncio.run(example_multi_page_navigation())
