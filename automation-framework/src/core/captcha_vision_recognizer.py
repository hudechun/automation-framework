"""
统一的验证码视觉模型识别器
负责识别验证码类型和提取必要的数据
"""
from typing import Optional, Dict, Any
import logging
import json
import re
import os
import tempfile

from .captcha_types import CaptchaType

logger = logging.getLogger(__name__)


class CaptchaVisionRecognizer:
    """
    统一的验证码视觉模型识别器
    
    功能：
    1. 识别验证码类型（image, slider, click, puzzle, rotate等）
    2. 提取验证码处理所需的数据（如缺口位置、点击坐标、旋转角度、文字内容等）
    3. 返回标准化的JSON格式结果
    """
    
    def __init__(self, vision_model_provider: Optional[str] = None):
        """
        初始化识别器
        
        Args:
            vision_model_provider: 视觉模型提供商（如"qwen", "gpt4v", "claude"）
        """
        self.vision_model_provider = vision_model_provider or self._detect_provider()
        self.vision_model = None
        self._init_vision_model()
    
    def _detect_provider(self) -> Optional[str]:
        """从环境变量检测视觉模型提供商"""
        if os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"):
            return "qwen"
        elif os.getenv("OPENAI_API_KEY"):
            return "gpt4v"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "claude"
        return None
    
    def _init_vision_model(self):
        """初始化视觉模型"""
        if not self.vision_model_provider:
            return
        
        try:
            from ...ai.vision import create_vision_model
            from ...ai.config import ModelConfig, ModelProvider
        except ImportError:
            try:
                import sys
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                from automation_framework.src.ai.vision import create_vision_model
                from automation_framework.src.ai.config import ModelConfig, ModelProvider
            except ImportError:
                logger.warning("视觉模型模块未找到，将无法使用视觉识别")
                return
        
        try:
            provider_lower = self.vision_model_provider.lower()
            
            if provider_lower == "qwen":
                api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
                if not api_key:
                    logger.warning("未设置QWEN_API_KEY环境变量")
                    return
                config = ModelConfig(
                    provider=ModelProvider.QWEN,
                    model="qwen-vl-plus",
                    api_key=api_key,
                    api_base=os.getenv("QWEN_API_BASE") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
                self.vision_model = create_vision_model(config)
                
            elif provider_lower in ["gpt4v", "gpt-4-vision", "openai"]:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("未设置OPENAI_API_KEY环境变量")
                    return
                config = ModelConfig(
                    provider=ModelProvider.OPENAI,
                    model="gpt-4-vision-preview",
                    api_key=api_key
                )
                self.vision_model = create_vision_model(config)
                
            elif provider_lower in ["claude", "claude-vision", "anthropic"]:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning("未设置ANTHROPIC_API_KEY环境变量")
                    return
                config = ModelConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model="claude-3-opus-20240229",
                    api_key=api_key
                )
                self.vision_model = create_vision_model(config)
            else:
                logger.warning(f"不支持的视觉模型提供商: {self.vision_model_provider}")
                
        except Exception as e:
            logger.error(f"初始化视觉模型失败: {e}")
            self.vision_model = None
    
    async def recognize(
        self,
        image_bytes: bytes,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        识别验证码类型和数据
        
        Args:
            image_bytes: 验证码图片的字节数据
            image_path: 验证码图片路径（可选，如果提供则优先使用）
            
        Returns:
            识别结果字典，格式：
            {
                "type": "image|slider|click|puzzle|rotate|unknown",
                "data": {
                    # 根据类型不同，data字段不同：
                    # image: {"text": "验证码文字"}
                    # slider: {"gap_x": 缺口X坐标, "gap_width": 缺口宽度}
                    # click: {"targets": [{"x": x, "y": y, "text": "文字"}, ...]}
                    # puzzle: {"gap_x": X坐标, "gap_y": Y坐标, "gap_width": 宽度, "gap_height": 高度}
                    # rotate: {"rotation_angle": 角度, "direction": "clockwise|counterclockwise"}
                },
                "confidence": 0.0-1.0,
                "description": "验证码描述"
            }
        """
        if not self.vision_model:
            logger.warning("视觉模型未初始化，无法识别验证码")
            return {
                "type": "unknown",
                "data": {},
                "confidence": 0.0,
                "description": "视觉模型未配置"
            }
        
        # 保存图片到临时文件（如果提供了路径则使用，否则创建临时文件）
        temp_file_path = image_path
        should_delete = False
        
        if not temp_file_path:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                temp_file_path = tmp_file.name
                should_delete = True
        
        try:
            # 构建统一的识别提示词
            prompt = """分析这张验证码图片，识别验证码类型并提取处理所需的数据。

验证码类型包括：
1. image: 图形验证码（文字/数字图片），需要识别文字内容
2. slider: 滑动验证码（滑块验证，有缺口需要滑动），需要识别缺口位置
3. click: 点选验证码（需要点击图片中的文字或物体），需要识别点击坐标
4. puzzle: 拼图验证码（需要拖动拼图块），需要识别缺口位置
5. rotate: 旋转验证码（需要旋转图片），需要识别旋转角度

请以JSON格式返回结果，格式如下：

对于 image 类型：
{
    "type": "image",
    "data": {
        "text": "验证码文字内容"
    },
    "confidence": <识别置信度 0-1>,
    "description": "图形验证码，包含文字/数字"
}

对于 slider 类型：
{
    "type": "slider",
    "data": {
        "gap_x": <缺口左边缘相对于图片左边缘的X坐标（像素）>,
        "gap_width": <缺口宽度（像素）>
    },
    "confidence": <识别置信度 0-1>,
    "description": "滑动验证码，需要滑动滑块到缺口位置"
}

对于 click 类型：
{
    "type": "click",
    "data": {
        "targets": [
            {"x": <X坐标（像素）>, "y": <Y坐标（像素）>, "text": "<目标文字>"},
            ...
        ]
    },
    "confidence": <识别置信度 0-1>,
    "description": "点选验证码，需要点击指定的文字或物体"
}

对于 puzzle 类型：
{
    "type": "puzzle",
    "data": {
        "gap_x": <缺口左边缘相对于图片左边缘的X坐标（像素）>,
        "gap_y": <缺口上边缘相对于图片上边缘的Y坐标（像素）>,
        "gap_width": <缺口宽度（像素）>,
        "gap_height": <缺口高度（像素）>
    },
    "confidence": <识别置信度 0-1>,
    "description": "拼图验证码，需要拖动拼图块到缺口位置"
}

对于 rotate 类型：
{
    "type": "rotate",
    "data": {
        "rotation_angle": <需要旋转的角度（0-360度）>,
        "direction": "clockwise" 或 "counterclockwise"
    },
    "confidence": <识别置信度 0-1>,
    "description": "旋转验证码，需要旋转图片到正确角度"
}

只返回JSON，不要包含其他文字。"""
            
            # 调用视觉模型
            result_text = await self.vision_model.analyze_screenshot(temp_file_path, prompt)
            
            # 解析JSON结果
            recognition_result = self._parse_result(result_text)
            
            logger.info(f"视觉模型识别结果: type={recognition_result.get('type')}, confidence={recognition_result.get('confidence', 0):.2f}")
            
            return recognition_result
            
        except Exception as e:
            logger.error(f"视觉模型识别失败: {e}")
            return {
                "type": "unknown",
                "data": {},
                "confidence": 0.0,
                "description": f"识别失败: {str(e)}"
            }
        finally:
            # 清理临时文件
            if should_delete and temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    def _parse_result(self, result_text: str) -> Dict[str, Any]:
        """
        解析视觉模型返回的结果
        
        Args:
            result_text: 视觉模型返回的文本
            
        Returns:
            解析后的结果字典
        """
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', result_text, re.MULTILINE)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # 验证和标准化结果
                captcha_type = data.get("type", "unknown").lower()
                data_dict = data.get("data", {})
                confidence = float(data.get("confidence", 0.0))
                description = data.get("description", "")
                
                # 映射到CaptchaType枚举值
                type_mapping = {
                    "image": "image",
                    "slider": "slider",
                    "click": "click",
                    "puzzle": "puzzle",
                    "rotate": "rotate",
                }
                
                normalized_type = type_mapping.get(captcha_type, "unknown")
                
                return {
                    "type": normalized_type,
                    "data": data_dict,
                    "confidence": max(0.0, min(1.0, confidence)),  # 限制在0-1之间
                    "description": description
                }
            else:
                logger.warning(f"无法从结果中提取JSON: {result_text[:200]}")
                return {
                    "type": "unknown",
                    "data": {},
                    "confidence": 0.0,
                    "description": "无法解析识别结果"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始结果: {result_text[:200]}")
            return {
                "type": "unknown",
                "data": {},
                "confidence": 0.0,
                "description": f"JSON解析失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"解析结果失败: {e}")
            return {
                "type": "unknown",
                "data": {},
                "confidence": 0.0,
                "description": f"解析失败: {str(e)}"
            }
