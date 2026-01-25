"""
LLM集成 - 统一的LLM接口
"""
from typing import Dict, Any, List, Optional, AsyncIterator
from abc import ABC, abstractmethod
import asyncio
import time

from .config import ModelConfig
from .rate_limiter import get_rate_limiter, RateLimitConfig


class LLMProvider(ABC):
    """LLM提供商抽象基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        聊天接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Returns:
            模型响应
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式输出接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Yields:
            模型响应片段
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API提供商"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.api_base
            )
        except ImportError:
            raise ImportError("openai package is not installed. Install it with: pip install openai")
        
        # 获取限流器（默认60次/分钟）
        self.rate_limiter = get_rate_limiter(
            RateLimitConfig(max_requests=60, window_seconds=60)
        )
        self.api_key = config.api_key or "default"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """OpenAI聊天接口（带限流和重试）"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # 限流控制
                await self.rate_limiter.acquire(self.api_key)
                
                params = {
                    "model": self.config.model,
                    "messages": messages,
                    **self.config.params,
                    **kwargs
                }
                
                response = await self.client.chat.completions.create(**params)
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e).lower()
                
                # 处理限流错误（429 Too Many Requests）
                if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
                    if attempt < max_retries - 1:
                        # 指数退避：1s, 2s, 4s
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit exceeded. Retrying after {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts. Please try again later.")
                
                # 其他错误直接抛出
                raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """OpenAI流式输出"""
        params = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
            **self.config.params,
            **kwargs
        }
        
        stream = await self.client.chat.completions.create(**params)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    """Anthropic API提供商"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=config.api_key,
                base_url=config.api_base
            )
        except ImportError:
            raise ImportError("anthropic package is not installed. Install it with: pip install anthropic")
        
        # 获取限流器（默认50次/分钟，Anthropic通常限制更严格）
        self.rate_limiter = get_rate_limiter(
            RateLimitConfig(max_requests=50, window_seconds=60)
        )
        self.api_key = config.api_key or "default"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Anthropic聊天接口（带限流和重试）"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # 限流控制
                await self.rate_limiter.acquire(self.api_key)
        # 转换消息格式
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        params = {
            "model": self.config.model,
            "messages": converted_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            **self.config.params,
        }
        
        if system_message:
            params["system"] = system_message
        
                response = await self.client.messages.create(**params)
                return response.content[0].text
                
            except Exception as e:
                error_str = str(e).lower()
                
                # 处理限流错误（429 Too Many Requests）
                if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
                    if attempt < max_retries - 1:
                        # 指数退避：1s, 2s, 4s
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit exceeded. Retrying after {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts. Please try again later.")
                
                # 其他错误直接抛出
                raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Anthropic流式输出"""
        # 转换消息格式
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        params = {
            "model": self.config.model,
            "messages": converted_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
            **self.config.params,
        }
        
        if system_message:
            params["system"] = system_message
        
        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text


class OllamaProvider(LLMProvider):
    """Ollama本地模型提供商"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_base = config.api_base or "http://localhost:11434"
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Ollama聊天接口"""
        import aiohttp
        
        url = f"{self.api_base}/api/chat"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            **self.config.params,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                return data["message"]["content"]
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Ollama流式输出"""
        import aiohttp
        import json
        
        url = f"{self.api_base}/api/chat"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
            **self.config.params,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                async for line in response.content:
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]


class QwenProvider(LLMProvider):
    """Qwen模型提供商（通过OpenAI兼容API）"""
    
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
            raise ImportError("openai package is not installed. Install it with: pip install openai")
        
        # 获取限流器（默认60次/分钟）
        self.rate_limiter = get_rate_limiter(
            RateLimitConfig(max_requests=60, window_seconds=60)
        )
        self.api_key = config.api_key or "default"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Qwen聊天接口（带限流和重试）"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # 限流控制
                await self.rate_limiter.acquire(self.api_key)
                
                params = {
                    "model": self.config.model,
                    "messages": messages,
                    **self.config.params,
                    **kwargs
                }
                
                response = await self.client.chat.completions.create(**params)
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e).lower()
                
                # 处理限流错误（429 Too Many Requests）
                if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str or "请求过于频繁" in error_str:
                    if attempt < max_retries - 1:
                        # 指数退避：1s, 2s, 4s
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit exceeded. Retrying after {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts. Please try again later.")
                
                # 其他错误直接抛出
                raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Qwen流式输出"""
        params = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
            **self.config.params,
            **kwargs
        }
        
        stream = await self.client.chat.completions.create(**params)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def create_llm_provider(config: ModelConfig) -> LLMProvider:
    """
    创建LLM提供商
    
    Args:
        config: 模型配置
        
    Returns:
        LLM提供商实例
    """
    from .config import ModelProvider
    
    if config.provider == ModelProvider.OPENAI:
        return OpenAIProvider(config)
    elif config.provider == ModelProvider.ANTHROPIC:
        return AnthropicProvider(config)
    elif config.provider == ModelProvider.OLLAMA:
        return OllamaProvider(config)
    elif config.provider == ModelProvider.QWEN:
        return QwenProvider(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
