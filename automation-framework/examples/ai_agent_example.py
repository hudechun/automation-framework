"""
AI Agent使用示例
"""
import asyncio
from src.ai.agent import Agent
from src.ai.llm import OpenAIProvider
from src.ai.vision import GPT4VisionProvider


async def example_natural_language_task():
    """示例1：自然语言任务"""
    # 创建Agent
    llm = OpenAIProvider(api_key="your-api-key", model="gpt-4")
    agent = Agent(llm=llm)
    
    # 执行自然语言任务
    result = await agent.execute_task(
        "Go to example.com and take a screenshot"
    )
    
    print(f"Task result: {result}")


async def example_vision_task():
    """示例2：视觉识别任务"""
    # 创建带视觉能力的Agent
    llm = OpenAIProvider(api_key="your-api-key", model="gpt-4")
    vision = GPT4VisionProvider(api_key="your-api-key")
    agent = Agent(llm=llm, vision_model=vision)
    
    # 执行需要视觉识别的任务
    result = await agent.execute_task(
        "Find the login button on the page and click it"
    )
    
    print(f"Task result: {result}")


async def example_complex_planning():
    """示例3：复杂任务规划"""
    llm = OpenAIProvider(api_key="your-api-key", model="gpt-4")
    agent = Agent(llm=llm)
    
    # 执行复杂任务
    result = await agent.execute_task(
        """
        1. Go to example.com
        2. Search for 'automation'
        3. Click on the first result
        4. Extract the main heading
        5. Take a screenshot
        """
    )
    
    print(f"Task result: {result}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_natural_language_task())
    # asyncio.run(example_vision_task())
    # asyncio.run(example_complex_planning())
