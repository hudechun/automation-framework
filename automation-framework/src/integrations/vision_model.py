"""
视觉模型集成 - 用于验证码识别等图像理解任务
"""
from typing import Optional, Dict, Any
import logging
import base64
import io

logger = logging.getLogger(__name__)


class VisionModelClient:
    """视觉模型客户端基类"""
    
    async def recognize_captcha(self, image_bytes: bytes, prompt: Optional[str] = None) -> Optional[str]:
        """
        识别验证码
        
        Args:
            image_bytes: 验证码图片的字节数据
            prompt: 提示词
            
        Returns:
            验证码文本
        """
        raise NotImplementedError
    
    def _image_to_base64(self, image_bytes: bytes) -> str:
        """将图片字节转换为base64编码"""
        return base64.b64encode(image_bytes).decode('utf-8')


class QwenVisionClient(VisionModelClient):
    """Qwen视觉模型客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化Qwen视觉模型客户端
        
        Args:
            api_key: API密钥（如果为None，从环境变量或配置读取）
            base_url: API基础URL（如果为None，使用默认值）
        """
        self.api_key = api_key
        self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    async def recognize_captcha(self, image_bytes: bytes, prompt: Optional[str] = None) -> Optional[str]:
        """
        使用Qwen视觉模型识别验证码
        
        Args:
            image_bytes: 验证码图片的字节数据
            prompt: 提示词
            
        Returns:
            验证码文本
        """
        try:
            import aiohttp
            
            # 构建提示词
            if not prompt:
                prompt = """请识别这张验证码图片中的文字或数字，只返回验证码内容，不要包含其他说明文字。
例如，如果验证码是"ABC123"，只返回"ABC123"。
如果验证码是"验证码：1234"，只返回"1234"。
如果验证码包含中文字符，请准确识别并返回。"""
            
            # 将图片转换为base64
            image_base64 = self._image_to_base64(image_bytes)
            
            # 构建请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "qwen-vl-max",  # 或 "qwen-vl-plus"
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 50  # 验证码通常很短
            }
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # 提取验证码文本
                        captcha_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        return captcha_text
                    else:
                        error_text = await response.text()
                        logger.error(f"Qwen API请求失败: {response.status}, {error_text}")
                        return None
                        
        except ImportError:
            logger.error("aiohttp未安装，无法使用Qwen视觉模型")
            return None
        except Exception as e:
            logger.error(f"Qwen视觉模型识别失败: {e}")
            return None


class GPT4VisionClient(VisionModelClient):
    """GPT-4 Vision客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化GPT-4 Vision客户端
        
        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL（如果为None，使用OpenAI默认值）
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
    
    async def recognize_captcha(self, image_bytes: bytes, prompt: Optional[str] = None) -> Optional[str]:
        """使用GPT-4 Vision识别验证码"""
        try:
            import aiohttp
            
            if not prompt:
                prompt = "识别这张验证码图片中的文字或数字，只返回验证码内容。"
            
            image_base64 = self._image_to_base64(image_bytes)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        captcha_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        return captcha_text
                    else:
                        error_text = await response.text()
                        logger.error(f"GPT-4 Vision API请求失败: {response.status}, {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"GPT-4 Vision识别失败: {e}")
            return None
