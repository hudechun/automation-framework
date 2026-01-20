"""
Qwen模型使用示例

演示如何使用通义千问（Qwen）模型进行自动化任务
"""
import asyncio
import os
from dotenv import load_dotenv

from src.ai.config import ModelConfig, ModelProfile, ModelProvider, get_global_config_manager
from src.ai.llm import create_llm_provider
from src.ai.vision import create_vision_model
from src.ai.agent import Agent


async def example_basic_chat():
    """示例1：基础对话"""
    print("=" * 50)
    print("示例1：基础对话")
    print("=" * 50)
    
    # 创建Qwen配置
    config = ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-turbo",
        api_key=os.getenv("QWEN_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        params={
            "temperature": 0.7,
            "max_tokens": 2000
        }
    )
    
    # 创建LLM提供商
    llm = create_llm_provider(config)
    
    # 发送消息
    messages = [
        {"role": "system", "content": "你是一个专业的自动化助手，帮助用户完成浏览器和桌面自动化任务。"},
        {"role": "user", "content": "如何使用Python自动化填写网页表单？请给出详细步骤。"}
    ]
    
    print("\n发送消息...")
    response = await llm.chat(messages)
    print(f"\n模型响应:\n{response}")


async def example_stream_chat():
    """示例2：流式输出"""
    print("\n" + "=" * 50)
    print("示例2：流式输出")
    print("=" * 50)
    
    config = ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-plus",
        api_key=os.getenv("QWEN_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    llm = create_llm_provider(config)
    
    messages = [
        {"role": "system", "content": "你是一个自动化专家。"},
        {"role": "user", "content": "解释一下浏览器自动化的工作原理。"}
    ]
    
    print("\n流式输出:")
    async for chunk in llm.stream(messages):
        print(chunk, end="", flush=True)
    print("\n")


async def example_vision_analysis():
    """示例3：视觉分析（需要截图文件）"""
    print("\n" + "=" * 50)
    print("示例3：视觉分析")
    print("=" * 50)
    
    # 创建视觉模型配置
    config = ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-vl-plus",
        api_key=os.getenv("QWEN_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    vision = create_vision_model(config)
    
    # 注意：需要实际的截图文件
    screenshot_path = "screenshot.png"
    
    if os.path.exists(screenshot_path):
        print(f"\n分析截图: {screenshot_path}")
        result = await vision.analyze_screenshot(
            image_path=screenshot_path,
            prompt="详细描述这个页面的内容和布局"
        )
        print(f"\n分析结果:\n{result}")
        
        # 查找特定元素
        print("\n查找登录按钮...")
        element = await vision.find_element(
            image_path=screenshot_path,
            element_description="登录按钮"
        )
        print(f"\n元素位置: {element}")
    else:
        print(f"\n跳过视觉分析示例（未找到截图文件: {screenshot_path}）")


async def example_task_planning():
    """示例4：任务规划"""
    print("\n" + "=" * 50)
    print("示例4：任务规划")
    print("=" * 50)
    
    config = ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-max",
        api_key=os.getenv("QWEN_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        params={
            "temperature": 0.3,  # 降低随机性，提高规划准确性
            "max_tokens": 3000
        }
    )
    
    llm = create_llm_provider(config)
    
    # 任务规划提示词
    messages = [
        {"role": "system", "content": """你是一个自动化任务规划专家。
你需要将用户的自然语言任务分解为具体的操作步骤。

可用的操作类型：
- NAVIGATION: 导航操作（打开URL、前进、后退、刷新）
- INTERACTION: 交互操作（点击、双击、右键、悬停、拖拽）
- INPUT: 输入操作（输入文本、按键、上传文件）
- QUERY: 查询操作（获取文本、获取属性、截图）
- WAIT: 等待操作（等待元素、等待文本、延迟）

请以JSON格式返回操作步骤列表。"""},
        {"role": "user", "content": "任务：打开百度，搜索'Python自动化'，点击第一个搜索结果"}
    ]
    
    print("\n规划任务...")
    response = await llm.chat(messages)
    print(f"\n任务规划:\n{response}")


async def example_with_fallback():
    """示例5：使用降级链"""
    print("\n" + "=" * 50)
    print("示例5：使用降级链")
    print("=" * 50)
    
    # 创建主模型配置
    task_model = ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-max",
        api_key=os.getenv("QWEN_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 创建降级链
    fallback_chain = [
        ModelConfig(
            provider=ModelProvider.QWEN,
            model="qwen-plus",
            api_key=os.getenv("QWEN_API_KEY"),
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        ModelConfig(
            provider=ModelProvider.QWEN,
            model="qwen-turbo",
            api_key=os.getenv("QWEN_API_KEY"),
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    ]
    
    # 创建配置文件
    profile = ModelProfile(
        name="qwen_with_fallback",
        task_model=task_model,
        fallback_chain=fallback_chain,
        metadata={
            "description": "带降级链的Qwen配置",
            "strategy": "qwen-max -> qwen-plus -> qwen-turbo"
        }
    )
    
    # 添加到配置管理器
    config_manager = get_global_config_manager()
    config_manager.add_profile(profile)
    
    print("\n配置文件已创建:")
    print(f"- 主模型: {task_model.model}")
    print(f"- 降级链: {' -> '.join([m.model for m in fallback_chain])}")
    
    # 获取降级模型
    print("\n模拟降级场景:")
    print(f"当前模型: {task_model.model}")
    
    fallback1 = config_manager.get_fallback_model(current_index=-1)
    if fallback1:
        print(f"第一次降级: {fallback1.model}")
    
    fallback2 = config_manager.get_fallback_model(current_index=0)
    if fallback2:
        print(f"第二次降级: {fallback2.model}")


async def example_config_file():
    """示例6：使用配置文件"""
    print("\n" + "=" * 50)
    print("示例6：使用配置文件")
    print("=" * 50)
    
    config_manager = get_global_config_manager()
    
    # 创建配置文件
    config_path = "config/qwen_config.json"
    
    if not os.path.exists(config_path):
        print(f"\n创建配置文件: {config_path}")
        
        # 创建配置
        profile = ModelProfile(
            name="qwen_default",
            task_model=ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-turbo",
                api_key=os.getenv("QWEN_API_KEY"),
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                params={"temperature": 0.7, "max_tokens": 2000}
            ),
            vision_model=ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",
                api_key=os.getenv("QWEN_API_KEY"),
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                params={"temperature": 0.7, "max_tokens": 2000}
            )
        )
        
        config_manager.add_profile(profile)
        config_manager.save_config(config_path)
        print("配置文件已创建")
    else:
        print(f"\n加载配置文件: {config_path}")
        config_manager.load_config(config_path)
        print("配置文件已加载")
    
    # 列出所有配置
    profiles = config_manager.list_profiles()
    print(f"\n可用的配置文件: {profiles}")
    
    # 获取当前配置
    current_profile = config_manager.get_profile()
    if current_profile:
        print(f"\n当前配置: {current_profile.name}")
        print(f"- 任务模型: {current_profile.task_model.model}")
        if current_profile.vision_model:
            print(f"- 视觉模型: {current_profile.vision_model.model}")


async def example_multi_turn_conversation():
    """示例7：多轮对话"""
    print("\n" + "=" * 50)
    print("示例7：多轮对话")
    print("=" * 50)
    
    config = ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-plus",
        api_key=os.getenv("QWEN_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    llm = create_llm_provider(config)
    
    # 多轮对话
    messages = [
        {"role": "system", "content": "你是一个自动化助手。"}
    ]
    
    # 第一轮
    messages.append({"role": "user", "content": "什么是Playwright？"})
    print("\n用户: 什么是Playwright？")
    
    response1 = await llm.chat(messages)
    print(f"助手: {response1[:200]}...")
    messages.append({"role": "assistant", "content": response1})
    
    # 第二轮
    messages.append({"role": "user", "content": "它和Selenium有什么区别？"})
    print("\n用户: 它和Selenium有什么区别？")
    
    response2 = await llm.chat(messages)
    print(f"助手: {response2[:200]}...")
    messages.append({"role": "assistant", "content": response2})
    
    # 第三轮
    messages.append({"role": "user", "content": "给我一个简单的使用示例"})
    print("\n用户: 给我一个简单的使用示例")
    
    response3 = await llm.chat(messages)
    print(f"助手: {response3}")


async def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 检查API密钥
    if not os.getenv("QWEN_API_KEY"):
        print("错误: 未设置QWEN_API_KEY环境变量")
        print("请在.env文件中设置: QWEN_API_KEY=sk-your-api-key-here")
        return
    
    print("Qwen模型使用示例")
    print("=" * 50)
    
    try:
        # 运行示例
        await example_basic_chat()
        await example_stream_chat()
        await example_vision_analysis()
        await example_task_planning()
        await example_with_fallback()
        await example_config_file()
        await example_multi_turn_conversation()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
