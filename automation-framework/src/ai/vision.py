"""
视觉理解模块 - 集成视觉模型
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import base64
from pathlib import Path

from .config import ModelConfig


class VisionModel(ABC):
    """视觉模型抽象基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        
    @abstractmethod
    async def analyze_screenshot(
        self,
        image_path: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        分析截图
        
        Args:
            image_path: 图片路径
            prompt: 提示词
            **kwargs: 额外参数
            
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    async def find_element(
        self,
        image_path: str,
        element_description: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        查找UI元素
        
        Args:
            image_path: 图片路径
            element_description: 元素描述
            **kwargs: 额外参数
            
        Returns:
            元素位置信息
        """
        pass
    
    def encode_image(self, image_path: str) -> str:
        """
        编码图片为base64
        
        Args:
            image_path: 图片路径
            
        Returns:
            base64编码的图片
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


class GPT4VisionProvider(VisionModel):
    """GPT-4 Vision提供商"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.api_base
            )
        except ImportError:
            raise ImportError("openai package is not installed")
    
    async def analyze_screenshot(
        self,
        image_path: str,
        prompt: str,
        **kwargs
    ) -> str:
        """GPT-4V分析截图"""
        image_data = self.encode_image(image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            **self.config.params,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def find_element(
        self,
        image_path: str,
        element_description: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """GPT-4V查找元素"""
        prompt = f"""Analyze this screenshot and find the UI element: {element_description}
        
Return the element's location in JSON format:
{{
    "found": true/false,
    "x": <x coordinate>,
    "y": <y coordinate>,
    "width": <width>,
    "height": <height>,
    "description": "<what you found>"
}}"""
        
        result = await self.analyze_screenshot(image_path, prompt, **kwargs)
        
        # 解析JSON响应
        try:
            import json
            # 提取JSON部分
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0].strip()
            else:
                json_str = result
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse vision response: {e}")
            return None


class Claude3VisionProvider(VisionModel):
    """Claude 3 Vision提供商"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=config.api_key,
                base_url=config.api_base
            )
        except ImportError:
            raise ImportError("anthropic package is not installed")
    
    async def analyze_screenshot(
        self,
        image_path: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Claude 3分析截图"""
        image_data = self.encode_image(image_path)
        
        # 检测图片类型
        image_path_obj = Path(image_path)
        media_type = "image/png"
        if image_path_obj.suffix.lower() in [".jpg", ".jpeg"]:
            media_type = "image/jpeg"
        elif image_path_obj.suffix.lower() == ".webp":
            media_type = "image/webp"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        response = await self.client.messages.create(
            model=self.config.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            **self.config.params
        )
        
        return response.content[0].text
    
    async def find_element(
        self,
        image_path: str,
        element_description: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Claude 3查找元素"""
        prompt = f"""Analyze this screenshot and find the UI element: {element_description}
        
Return the element's location in JSON format:
{{
    "found": true/false,
    "x": <x coordinate>,
    "y": <y coordinate>,
    "width": <width>,
    "height": <height>,
    "description": "<what you found>"
}}"""
        
        result = await self.analyze_screenshot(image_path, prompt, **kwargs)
        
        # 解析JSON响应
        try:
            import json
            # 提取JSON部分
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0].strip()
            else:
                json_str = result
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse vision response: {e}")
            return None


class QwenVisionProvider(VisionModel):
    """Qwen Vision提供商（通过OpenAI兼容API）"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            import openai
            # Qwen使用OpenAI兼容的API
            self.client = openai.AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.api_base or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        except ImportError:
            raise ImportError("openai package is not installed")
    
    async def analyze_screenshot(
        self,
        image_path: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Qwen Vision分析截图"""
        image_data = self.encode_image(image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            **self.config.params,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def find_element(
        self,
        image_path: str,
        element_description: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Qwen Vision查找元素"""
        prompt = f"""分析这个截图并找到UI元素：{element_description}
        
以JSON格式返回元素位置：
{{
    "found": true/false,
    "x": <x坐标>,
    "y": <y坐标>,
    "width": <宽度>,
    "height": <高度>,
    "description": "<你找到的内容>"
}}"""
        
        result = await self.analyze_screenshot(image_path, prompt, **kwargs)
        
        # 解析JSON响应
        try:
            import json
            # 提取JSON部分
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0].strip()
            else:
                json_str = result
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse vision response: {e}")
            return None


def create_vision_model(config: ModelConfig) -> VisionModel:
    """
    创建视觉模型
    
    Args:
        config: 模型配置
        
    Returns:
        视觉模型实例
    """
    from .config import ModelProvider
    
    if config.provider == ModelProvider.OPENAI:
        return GPT4VisionProvider(config)
    elif config.provider == ModelProvider.ANTHROPIC:
        return Claude3VisionProvider(config)
    elif config.provider == ModelProvider.QWEN:
        return QwenVisionProvider(config)
    else:
        raise ValueError(f"Unsupported vision provider: {config.provider}")
