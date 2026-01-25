"""
验证码类型和处理策略
"""
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
import logging
import asyncio
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class CaptchaType(str, Enum):
    """验证码类型枚举"""
    IMAGE = "image"  # 图形验证码（图片验证码）
    SLIDER = "slider"  # 滑动验证码（滑块验证）
    CLICK = "click"  # 点选验证码（点击图片中的文字/物体）
    ROTATE = "rotate"  # 旋转验证码
    PUZZLE = "puzzle"  # 拼图验证码
    SMS = "sms"  # 短信验证码
    EMAIL = "email"  # 邮箱验证码
    VOICE = "voice"  # 语音验证码
    RECAPTCHA = "recaptcha"  # Google reCAPTCHA
    HCAPTCHA = "hcaptcha"  # hCaptcha
    TURNSTILE = "turnstile"  # Cloudflare Turnstile
    BEHAVIORAL = "behavioral"  # 行为验证码
    UNKNOWN = "unknown"  # 未知类型


class CaptchaDetector:
    """验证码检测器 - 自动识别验证码类型（支持视觉模型识别）"""
    
    def __init__(self, vision_model_provider: Optional[str] = None):
        """
        初始化验证码检测器
        
        Args:
            vision_model_provider: 视觉模型提供商（如"qwen"），用于识别验证码类型
        """
        self.vision_model_provider = vision_model_provider
    
    # 各种验证码的识别特征
    CAPTCHA_SELECTORS = {
        CaptchaType.IMAGE: [
            "img[alt*='验证码']",
            "img[alt*='captcha']",
            ".captcha img",
            "#captcha img",
            "[class*='captcha'] img",
            "[id*='captcha'] img",
        ],
        CaptchaType.SLIDER: [
            ".slider-verify",
            ".slider-captcha",
            "[class*='slider']",
            "[id*='slider']",
            ".geetest_slider",
        ],
        CaptchaType.CLICK: [
            ".click-captcha",
            "[class*='click']",
            ".point-captcha",
        ],
        CaptchaType.PUZZLE: [
            ".puzzle-captcha",
            "[class*='puzzle']",
            ".jigsaw-captcha",
        ],
        CaptchaType.ROTATE: [
            ".rotate-captcha",
            "[class*='rotate']",
            ".rotation-captcha",
        ],
        CaptchaType.RECAPTCHA: [
            ".g-recaptcha",
            "#recaptcha",
            "iframe[src*='recaptcha']",
        ],
        CaptchaType.HCAPTCHA: [
            ".h-captcha",
            "iframe[src*='hcaptcha']",
        ],
        CaptchaType.TURNSTILE: [
            ".cf-turnstile",
            "iframe[src*='challenges.cloudflare.com']",
        ],
    }
    
    async def detect_captcha_type(self, page: Page) -> Tuple[Optional[CaptchaType], Optional[str]]:
        """
        检测页面上的验证码类型（支持视觉模型识别）
        
        流程：
        1. 先使用选择器检测（快速）
        2. 如果检测到验证码但类型不确定，使用视觉模型识别
        
        Args:
            page: Playwright Page对象
            
        Returns:
            (验证码类型, 选择器) 元组，如果未检测到返回 (None, None)
        """
        # 按优先级检测各种验证码类型（使用选择器）
        detection_order = [
            CaptchaType.RECAPTCHA,
            CaptchaType.HCAPTCHA,
            CaptchaType.TURNSTILE,
            CaptchaType.SLIDER,
            CaptchaType.CLICK,
            CaptchaType.PUZZLE,
            CaptchaType.ROTATE,
            CaptchaType.IMAGE,
        ]
        
        for captcha_type in detection_order:
            selectors = self.CAPTCHA_SELECTORS.get(captcha_type, [])
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            logger.info(f"检测到验证码类型: {captcha_type.value}, 选择器: {selector}")
                            return captcha_type, selector
                except:
                    continue
        
        # 如果选择器检测失败，尝试通用检测
        generic_selectors = [
            "img[alt*='验证码']",
            "img[alt*='captcha']",
            ".captcha",
            "#captcha",
        ]
        
        captcha_element = None
        captcha_selector = None
        
        for selector in generic_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    captcha_element = element
                    captcha_selector = selector
                    break
            except:
                continue
        
        # 如果检测到验证码元素但类型不确定，使用视觉模型识别
        if captcha_element and self.vision_model_provider:
            captcha_type = await self._identify_type_with_vision_model(page, captcha_element)
            if captcha_type:
                logger.info(f"视觉模型识别验证码类型: {captcha_type.value}")
                return captcha_type, captcha_selector
        
        if captcha_element:
            logger.info(f"检测到通用验证码，选择器: {captcha_selector}")
            return CaptchaType.IMAGE, captcha_selector
        
        return None, None
    
    async def _identify_type_with_vision_model(
        self,
        page: Page,
        captcha_element: Any
    ) -> Optional[CaptchaType]:
        """
        使用视觉模型识别验证码类型
        
        Args:
            page: Playwright Page对象
            captcha_element: 验证码元素
            
        Returns:
            验证码类型，如果识别失败返回None
        """
        try:
            # 截图验证码
            image_bytes = await captcha_element.screenshot()
            
            # 尝试导入视觉模型
            try:
                from ...ai.vision import create_vision_model
                from ...ai.config import ModelConfig, ModelProvider
            except ImportError:
                try:
                    import sys
                    import os
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)
                    from automation_framework.src.ai.vision import create_vision_model
                    from automation_framework.src.ai.config import ModelConfig, ModelProvider
                except ImportError:
                    return None
            
            import os
            api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return None
            
            config = ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",
                api_key=api_key
            )
            
            vision_model = create_vision_model(config)
            
            # 保存图片到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # 构建提示词，要求识别验证码类型
                prompt = """分析这张验证码图片，识别验证码类型。

验证码类型包括：
- image: 图形验证码（文字/数字图片）
- slider: 滑动验证码（滑块验证，有缺口需要滑动）
- click: 点选验证码（需要点击图片中的文字或物体）
- puzzle: 拼图验证码（需要拖动拼图块）
- rotate: 旋转验证码（需要旋转图片）

请以JSON格式返回结果：
{
    "type": "<验证码类型: image/slider/click/puzzle/rotate>",
    "confidence": <识别置信度 0-1>,
    "description": "<验证码描述>"
}

只返回JSON，不要包含其他文字。"""
                
                result = await vision_model.analyze_screenshot(tmp_file_path, prompt)
                
                # 解析JSON结果
                import json
                import re
                
                json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    captcha_type_str = data.get("type", "").lower()
                    confidence = data.get("confidence", 0.0)
                    
                    if confidence > 0.5:
                        # 映射到CaptchaType枚举
                        type_mapping = {
                            "image": CaptchaType.IMAGE,
                            "slider": CaptchaType.SLIDER,
                            "click": CaptchaType.CLICK,
                            "puzzle": CaptchaType.PUZZLE,
                            "rotate": CaptchaType.ROTATE,
                        }
                        
                        captcha_type = type_mapping.get(captcha_type_str)
                        if captcha_type:
                            logger.info(f"视觉模型识别验证码类型: {captcha_type.value}, 置信度: {confidence:.2f}")
                            return captcha_type
                
                return None
                
            finally:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"视觉模型识别验证码类型失败: {e}")
            return None
    
    @classmethod
    async def detect_captcha_type_static(cls, page: Page) -> Tuple[Optional[CaptchaType], Optional[str]]:
        """静态方法：使用选择器检测（向后兼容）"""
        detector = cls()
        return await detector.detect_captcha_type(page)
    
    @classmethod
    async def detect_sms_captcha(cls, page: Page) -> bool:
        """检测是否有短信验证码输入框"""
        sms_selectors = [
            "input[placeholder*='验证码']",
            "input[placeholder*='短信验证码']",
            "input[name*='sms']",
            "input[name*='code']",
            ".sms-code-input",
        ]
        
        for selector in sms_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    return True
            except:
                continue
        
        return False
    
    @classmethod
    async def detect_email_captcha(cls, page: Page) -> bool:
        """检测是否有邮箱验证码输入框"""
        email_selectors = [
            "input[placeholder*='邮箱验证码']",
            "input[name*='email_code']",
            ".email-code-input",
        ]
        
        for selector in email_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    return True
            except:
                continue
        
        return False


class ImageCaptchaHandler:
    """图形验证码处理器（支持视觉模型和OCR）"""
    
    def __init__(self, vision_model_provider: Optional[str] = None, ocr_provider: Optional[str] = None):
        """
        初始化图形验证码处理器
        
        Args:
            vision_model_provider: 视觉模型提供商（如"qwen", "gpt4v", "claude"等）
                                 如果为None，尝试从环境变量或配置读取
            ocr_provider: OCR服务提供商（如"tesseract", "baidu", "aliyun"等）
        """
        self.vision_model_provider = vision_model_provider
        self.ocr_provider = ocr_provider
        
        # 如果未指定视觉模型提供商，尝试从环境变量检测
        if not self.vision_model_provider:
            import os
            if os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"):
                self.vision_model_provider = "qwen"
            elif os.getenv("OPENAI_API_KEY"):
                self.vision_model_provider = "gpt4v"
    
    async def solve(self, page: Page, selector: str, ocr_provider: Optional[str] = None) -> Optional[str]:
        """
        使用视觉模型或OCR识别图形验证码
        
        优先级：视觉模型 > OCR服务
        
        Args:
            page: Playwright Page对象
            selector: 验证码图片选择器
            ocr_provider: OCR服务提供商（如果未在初始化时指定）
            
        Returns:
            验证码文本，如果识别失败返回None
        """
        # 优先使用视觉模型
        if self.vision_model_provider:
            result = await self._solve_with_vision_model(page, selector)
            if result:
                return result
        
        # 如果视觉模型失败或未配置，使用OCR
        ocr_provider = ocr_provider or self.ocr_provider
        if ocr_provider:
            result = await self._solve_with_ocr(page, selector, ocr_provider)
            if result:
                return result
        
        logger.warning("验证码识别失败：未配置视觉模型或OCR服务")
        return None
    
    async def _solve_with_vision_model_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """
        使用视觉模型识别验证码（从图片字节）
        
        Args:
            image_bytes: 验证码图片字节
            
        Returns:
            验证码文本
        """
        provider_lower = self.vision_model_provider.lower()
        if provider_lower == "qwen":
            return await self._solve_with_qwen(image_bytes)
        elif provider_lower in ["gpt4v", "gpt-4-vision", "openai"]:
            return await self._solve_with_gpt4v(image_bytes)
        elif provider_lower in ["claude", "claude-vision", "anthropic"]:
            return await self._solve_with_claude(image_bytes)
        else:
            logger.warning(f"不支持的视觉模型: {self.vision_model_provider}")
            return None
    
    async def _solve_with_qwen(self, image_bytes: bytes) -> Optional[str]:
        """
        使用Qwen视觉模型识别验证码（使用已有的QwenVisionProvider）
        
        Args:
            image_bytes: 验证码图片的字节数据
            
        Returns:
            验证码文本
        """
        try:
            # 尝试导入已有的视觉模型模块
            try:
                from ...ai.vision import create_vision_model
                from ...ai.config import ModelConfig, ModelProvider
            except ImportError:
                try:
                    import sys
                    import os
                    # 添加项目路径
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)
                    
                    from automation_framework.src.ai.vision import create_vision_model
                    from automation_framework.src.ai.config import ModelConfig, ModelProvider
                except ImportError:
                    logger.warning("Qwen视觉模型未集成，请检查集成配置")
                    return None
            
            # 创建Qwen视觉模型配置
            import os
            api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                logger.warning("未设置QWEN_API_KEY环境变量")
                return None
            
            config = ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",  # 或 "qwen-vl-max"
                api_key=api_key,
                api_base=os.getenv("QWEN_API_BASE") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            # 创建视觉模型实例
            vision_model = create_vision_model(config)
            
            # 将图片字节保存为临时文件（因为analyze_screenshot需要文件路径）
            import tempfile
            import os as os_module
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # 构建提示词
                prompt = """请识别这张验证码图片中的文字或数字，只返回验证码内容，不要包含其他说明文字。

例如，如果验证码是"ABC123"，只返回"ABC123"。
如果验证码是"验证码：1234"，只返回"1234"。
如果验证码包含中文字符，请准确识别并返回。"""
                
                # 调用视觉模型分析截图
                result = await vision_model.analyze_screenshot(
                    image_path=tmp_file_path,
                    prompt=prompt
                )
                
                if result:
                    # 清理结果（移除可能的说明文字）
                    captcha_text = self._clean_captcha_result(result)
                    logger.info(f"Qwen识别验证码成功: {captcha_text[:3]}***")
                    return captcha_text
                
                return None
            finally:
                # 清理临时文件
                try:
                    os_module.unlink(tmp_file_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Qwen视觉模型识别失败: {e}")
            return None
    
    async def _solve_with_gpt4v(self, image_bytes: bytes) -> Optional[str]:
        """使用GPT-4 Vision识别验证码"""
        try:
            from ...ai.vision import create_vision_model
            from ...ai.config import ModelConfig, ModelProvider
        except ImportError:
            try:
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                from automation_framework.src.ai.vision import create_vision_model
                from automation_framework.src.ai.config import ModelConfig, ModelProvider
            except ImportError:
                logger.warning("GPT-4 Vision未集成")
                return None
        
        import os
        import tempfile
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("未设置OPENAI_API_KEY环境变量")
            return None
        
        config = ModelConfig(
            provider=ModelProvider.OPENAI,
            model="gpt-4-vision-preview",
            api_key=api_key
        )
        
        vision_model = create_vision_model(config)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            prompt = """识别这张验证码图片中的文字或数字，只返回验证码内容。"""
            result = await vision_model.analyze_screenshot(tmp_file_path, prompt)
            if result:
                captcha_text = self._clean_captcha_result(result)
                logger.info(f"GPT-4 Vision识别验证码成功: {captcha_text[:3]}***")
                return captcha_text
            return None
        finally:
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    async def _solve_with_claude(self, image_bytes: bytes) -> Optional[str]:
        """使用Claude Vision识别验证码"""
        try:
            from ...ai.vision import create_vision_model
            from ...ai.config import ModelConfig, ModelProvider
        except ImportError:
            try:
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                from automation_framework.src.ai.vision import create_vision_model
                from automation_framework.src.ai.config import ModelConfig, ModelProvider
            except ImportError:
                logger.warning("Claude Vision未集成")
                return None
        
        import os
        import tempfile
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("未设置ANTHROPIC_API_KEY环境变量")
            return None
        
        config = ModelConfig(
            provider=ModelProvider.ANTHROPIC,
            model="claude-3-opus-20240229",  # 或 "claude-3-sonnet-20240229"
            api_key=api_key
        )
        
        vision_model = create_vision_model(config)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            prompt = """识别这张验证码图片中的文字或数字，只返回验证码内容。"""
            result = await vision_model.analyze_screenshot(tmp_file_path, prompt)
            if result:
                captcha_text = self._clean_captcha_result(result)
                logger.info(f"Claude Vision识别验证码成功: {captcha_text[:3]}***")
                return captcha_text
            return None
        finally:
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    async def _solve_with_ocr(self, page: Page, selector: str, ocr_provider: str) -> Optional[str]:
        """
        使用OCR服务识别验证码
        
        Args:
            page: Playwright Page对象
            selector: 验证码图片选择器
            ocr_provider: OCR服务提供商
            
        Returns:
            验证码文本
        """
        try:
            captcha_element = await page.query_selector(selector)
            if not captcha_element:
                return None
            
            image_bytes = await captcha_element.screenshot()
            
            if ocr_provider.lower() == "tesseract":
                # 使用本地Tesseract OCR
                from .local_ocr import get_local_ocr
                
                ocr = get_local_ocr(lang="eng+chi_sim")
                if not ocr.is_available():
                    logger.warning("Tesseract OCR不可用，请安装Tesseract")
                    return None
                
                # 异步识别
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果事件循环正在运行，使用同步方法
                        text = ocr.recognize_sync(image_bytes, preprocess=True)
                    else:
                        # 否则可以使用异步方法
                        text = loop.run_until_complete(
                            ocr.recognize(image_bytes, preprocess=True)
                        )
                    return text
                except Exception as e:
                    logger.error(f"Tesseract OCR识别失败: {e}")
                    return None
            
            elif ocr_provider.lower() == "baidu":
                # 使用百度OCR
                logger.warning("百度OCR集成待实现")
                return None
            
            elif ocr_provider.lower() == "aliyun":
                # 使用阿里云OCR
                logger.warning("阿里云OCR集成待实现")
                return None
            
            else:
                logger.warning(f"不支持的OCR服务: {ocr_provider}")
                return None
                
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return None
    
    def _clean_captcha_result(self, result: str) -> str:
        """
        清理验证码识别结果
        
        移除可能的说明文字，只保留验证码内容
        
        Args:
            result: 原始识别结果
            
        Returns:
            清理后的验证码文本
        """
        import re
        
        # 移除常见的说明文字
        patterns = [
            r"验证码[：:]\s*",
            r"验证码是[：:]\s*",
            r"captcha[：:]\s*",
            r"code[：:]\s*",
            r"图片中的[文字数字字符]+[是：:]\s*",
        ]
        
        cleaned = result.strip()
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        
        # 移除多余的空白字符
        cleaned = re.sub(r"\s+", "", cleaned)
        
        return cleaned.strip()


class SliderCaptchaHandler:
    """滑动验证码处理器（使用视觉模型识别缺口位置）"""
    
    def __init__(self, vision_model_provider: Optional[str] = None):
        """
        初始化滑动验证码处理器
        
        Args:
            vision_model_provider: 视觉模型提供商（如"qwen"）
        """
        self.vision_model_provider = vision_model_provider
    
    async def solve(self, page: Page, selector: str) -> bool:
        """
        解决滑动验证码
        
        算法：
        1. 使用视觉模型识别缺口位置
        2. 计算滑动距离
        3. 分割为20份，前85%快速，后15%慢速
        4. 通过5次校验计算校验因子
        5. 使用校验因子计算真实距离
        
        Args:
            page: Playwright Page对象
            selector: 滑块容器选择器
            
        Returns:
            是否成功
        """
        try:
            # 1. 查找滑块和轨道元素
            slider_track = await page.query_selector(f"{selector} .slider-track, {selector} .slider-bg, {selector} .geetest_slider_track")
            slider_button = await page.query_selector(f"{selector} .slider-button, {selector} .slider-btn, {selector} .geetest_slider_button")
            
            if not slider_track or not slider_button:
                logger.error("未找到滑块元素")
                return False
            
            # 2. 获取滑块和轨道的尺寸和位置
            track_box = await slider_track.bounding_box()
            button_box = await slider_button.bounding_box()
            
            if not track_box or not button_box:
                return False
            
            # 3. 截图验证码图片（包含缺口）
            captcha_image_bytes = await slider_track.screenshot()
            
            # 4. 使用视觉模型识别缺口位置
            gap_position = await self._detect_gap_with_vision_model(captcha_image_bytes, track_box)
            
            if gap_position is None:
                logger.error("无法识别缺口位置")
                return False
            
            # 5. 计算滑动距离（缺口位置 - 滑块当前位置）
            slide_distance = gap_position - (button_box['x'] - track_box['x'])
            
            # 6. 通过5次校验计算校验因子
            calibration_factor = await self._calibrate_slide_distance(
                page, slider_button, button_box, slide_distance
            )
            
            # 7. 使用校验因子计算真实距离
            real_distance = slide_distance * calibration_factor
            
            # 8. 执行分段滑动（20份，前85%快速，后15%慢速）
            success = await self._slide_with_segments(
                page, slider_button, button_box, real_distance
            )
            
            if success:
                logger.info(f"滑动验证码完成，距离: {real_distance:.2f}px (原始: {slide_distance:.2f}px, 校验因子: {calibration_factor:.3f})")
            
            return success
            
        except Exception as e:
            logger.error(f"滑动验证码处理失败: {e}")
            return False
    
    async def _detect_gap_with_vision_model(
        self,
        image_bytes: bytes,
        track_box: Dict[str, float]
    ) -> Optional[float]:
        """
        使用视觉模型识别缺口位置
        
        Args:
            image_bytes: 验证码图片字节
            track_box: 轨道边界框
            
        Returns:
            缺口位置（相对于轨道左边缘的X坐标），如果识别失败返回None
        """
        try:
            # 尝试导入视觉模型
            try:
                from ...ai.vision import create_vision_model
                from ...ai.config import ModelConfig, ModelProvider
            except ImportError:
                try:
                    import sys
                    import os
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)
                    from automation_framework.src.ai.vision import create_vision_model
                    from automation_framework.src.ai.config import ModelConfig, ModelProvider
                except ImportError:
                    logger.warning("视觉模型未集成")
                    return None
            
            # 创建视觉模型配置
            import os
            api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                logger.warning("未设置QWEN_API_KEY")
                return None
            
            config = ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",
                api_key=api_key,
                api_base=os.getenv("QWEN_API_BASE") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            vision_model = create_vision_model(config)
            
            # 保存图片到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # 构建提示词，要求返回JSON格式
                prompt = """分析这张滑块验证码图片，识别缺口（凹槽）的位置。

请以JSON格式返回结果：
{
    "gap_x": <缺口左边缘相对于图片左边缘的X坐标（像素）>,
    "gap_width": <缺口宽度（像素）>,
    "confidence": <识别置信度 0-1>
}

只返回JSON，不要包含其他文字。"""
                
                # 调用视觉模型
                result = await vision_model.analyze_screenshot(tmp_file_path, prompt)
                
                # 解析JSON结果
                import json
                import re
                
                # 提取JSON部分
                json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    gap_x = data.get("gap_x")
                    confidence = data.get("confidence", 1.0)
                    
                    if gap_x is not None and confidence > 0.5:
                        logger.info(f"视觉模型识别缺口位置: {gap_x}px, 置信度: {confidence:.2f}")
                        return float(gap_x)
                
                logger.warning(f"无法解析视觉模型返回结果: {result}")
                return None
                
            finally:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"视觉模型识别缺口失败: {e}")
            return None
    
    async def _calibrate_slide_distance(
        self,
        page: Page,
        slider_button: Any,
        button_box: Dict[str, float],
        initial_distance: float
    ) -> float:
        """
        通过5次校验计算校验因子
        
        Args:
            page: Playwright Page对象
            slider_button: 滑块按钮元素
            button_box: 滑块按钮边界框
            initial_distance: 初始计算的滑动距离
            
        Returns:
            校验因子
        """
        calibration_tests = 5
        calibration_results = []
        
        # 执行5次小距离滑动测试
        test_distance = initial_distance * 0.1  # 使用10%的距离进行测试
        
        for i in range(calibration_tests):
            try:
                # 记录滑动前位置
                start_box = await slider_button.bounding_box()
                if not start_box:
                    continue
                
                # 执行小距离滑动
                await slider_button.hover()
                await page.mouse.down()
                await page.mouse.move(
                    start_box['x'] + test_distance,
                    start_box['y'],
                    steps=10
                )
                await page.mouse.up()
                
                # 等待一小段时间
                await page.wait_for_timeout(100)
                
                # 记录滑动后位置
                end_box = await slider_button.bounding_box()
                if not end_box:
                    continue
                
                # 计算实际移动距离
                actual_distance = end_box['x'] - start_box['x']
                if actual_distance > 0:
                    # 计算校验因子（实际距离 / 目标距离）
                    factor = actual_distance / test_distance
                    calibration_results.append(factor)
                
                # 重置滑块位置（如果需要）
                # await self._reset_slider(page, slider_button)
                
            except Exception as e:
                logger.debug(f"校验测试 {i+1} 失败: {e}")
                continue
        
        # 计算平均校验因子
        if calibration_results:
            avg_factor = sum(calibration_results) / len(calibration_results)
            logger.info(f"校验因子: {avg_factor:.3f} (基于{len(calibration_results)}次测试)")
            return avg_factor
        else:
            logger.warning("无法计算校验因子，使用默认值1.0")
            return 1.0
    
    async def _slide_with_segments(
        self,
        page: Page,
        slider_button: Any,
        button_box: Dict[str, float],
        total_distance: float
    ) -> bool:
        """
        分段滑动：分割为20份，前85%快速，后15%慢速
        
        Args:
            page: Playwright Page对象
            slider_button: 滑块按钮元素
            button_box: 滑块按钮边界框
            total_distance: 总滑动距离
            
        Returns:
            是否成功
        """
        try:
            segments = 20
            segment_distance = total_distance / segments
            
            # 前85%的段数（快速）
            fast_segments = int(segments * 0.85)
            # 后15%的段数（慢速）
            slow_segments = segments - fast_segments
            
            start_x = button_box['x']
            start_y = button_box['y']
            
            await slider_button.hover()
            await page.mouse.down()
            
            current_x = start_x
            
            # 前85%：快速滑动（每段steps=5）
            for i in range(fast_segments):
                current_x += segment_distance
                await page.mouse.move(current_x, start_y, steps=5)
                await page.wait_for_timeout(10)  # 短暂延迟
            
            # 后15%：慢速滑动（每段steps=20）
            for i in range(slow_segments):
                current_x += segment_distance
                await page.mouse.move(current_x, start_y, steps=20)
                await page.wait_for_timeout(20)  # 稍长延迟
            
            await page.mouse.up()
            
            # 等待验证完成
            await page.wait_for_timeout(500)
            
            logger.info(f"分段滑动完成: {fast_segments}段快速 + {slow_segments}段慢速")
            return True
            
        except Exception as e:
            logger.error(f"分段滑动失败: {e}")
            return False


class ClickCaptchaHandler:
    """点选验证码处理器（使用视觉模型识别点击目标）"""
    
    def __init__(self, vision_model_provider: Optional[str] = None):
        """
        初始化点选验证码处理器
        
        Args:
            vision_model_provider: 视觉模型提供商
        """
        self.vision_model_provider = vision_model_provider
    
    async def solve(
        self,
        page: Page,
        selector: str,
        target_text: Optional[str] = None,
        prompt_text: Optional[str] = None
    ) -> bool:
        """
        解决点选验证码
        
        流程：
        1. 如果指定了target_text，直接查找并点击
        2. 如果未指定，使用视觉模型识别需要点击的文字/物体
        3. 获取点击坐标并执行点击
        
        Args:
            page: Playwright Page对象
            selector: 验证码容器选择器
            target_text: 需要点击的文字（如"点击图中的文字"）
            prompt_text: 提示文字（如"请点击图中的'登录'文字"）
            
        Returns:
            是否成功
        """
        try:
            # 1. 如果指定了目标文字，直接查找并点击
            if target_text:
                elements = await page.query_selector_all(f"{selector} *")
                for element in elements:
                    text = await element.text_content()
                    if text and target_text in text:
                        await element.click()
                        logger.info(f"点击了包含'{target_text}'的元素")
                        return True
            
            # 2. 使用视觉模型识别需要点击的目标
            if self.vision_model_provider:
                click_targets = await self._identify_click_targets_with_vision(
                    page, selector, prompt_text or target_text
                )
                
                if click_targets:
                    # 按顺序点击所有目标
                    for target in click_targets:
                        x = target.get("x")
                        y = target.get("y")
                        if x is not None and y is not None:
                            await page.mouse.click(x, y)
                            await page.wait_for_timeout(300)  # 点击间隔
                            logger.info(f"点击坐标: ({x}, {y})")
                    
                    return True
            
            # 3. 如果都失败，可能需要人工介入
            logger.warning("点选验证码需要指定目标文字或使用视觉模型识别")
            return False
            
        except Exception as e:
            logger.error(f"点选验证码处理失败: {e}")
            return False
    
    async def _identify_click_targets_with_vision(
        self,
        page: Page,
        selector: str,
        prompt: Optional[str]
    ) -> List[Dict[str, float]]:
        """
        使用视觉模型识别需要点击的目标坐标
        
        Args:
            page: Playwright Page对象
            selector: 验证码容器选择器
            prompt: 提示文字（如"点击图中的'登录'文字"）
            
        Returns:
            点击目标坐标列表 [{"x": x, "y": y}, ...]
        """
        try:
            # 截图验证码区域
            captcha_element = await page.query_selector(selector)
            if not captcha_element:
                return []
            
            image_bytes = await captcha_element.screenshot()
            element_box = await captcha_element.bounding_box()
            if not element_box:
                return []
            
            # 使用视觉模型识别
            try:
                from ...ai.vision import create_vision_model
                from ...ai.config import ModelConfig, ModelProvider
            except ImportError:
                try:
                    import sys
                    import os
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)
                    from automation_framework.src.ai.vision import create_vision_model
                    from automation_framework.src.ai.config import ModelConfig, ModelProvider
                except ImportError:
                    return []
            
            import os
            api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return []
            
            config = ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",
                api_key=api_key
            )
            
            vision_model = create_vision_model(config)
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # 构建提示词
                if prompt:
                    vision_prompt = f"""分析这张点选验证码图片，识别需要点击的目标。

提示：{prompt}

请以JSON格式返回需要点击的坐标（相对于图片）：
{{
    "targets": [
        {{"x": <X坐标（像素）>, "y": <Y坐标（像素）>, "text": "<目标文字>"}},
        ...
    ]
}}

只返回JSON，不要包含其他文字。"""
                else:
                    vision_prompt = """分析这张点选验证码图片，识别需要点击的文字或物体。

请以JSON格式返回需要点击的坐标（相对于图片）：
{
    "targets": [
        {"x": <X坐标（像素）>, "y": <Y坐标（像素）>, "text": "<目标文字>"},
        ...
    ]
}

只返回JSON，不要包含其他文字。"""
                
                result = await vision_model.analyze_screenshot(tmp_file_path, vision_prompt)
                
                # 解析JSON结果
                import json
                import re
                
                json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    targets = data.get("targets", [])
                    click_targets = []
                    
                    for target in targets:
                        x = target.get("x")
                        y = target.get("y")
                        if x is not None and y is not None:
                            # 转换为页面坐标（相对于验证码元素）
                            page_x = element_box['x'] + x
                            page_y = element_box['y'] + y
                            click_targets.append({"x": page_x, "y": page_y})
                    
                    logger.info(f"视觉模型识别到{len(click_targets)}个点击目标")
                    return click_targets
                
                return []
                
            finally:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"视觉模型识别点击目标失败: {e}")
            return []


class PuzzleCaptchaHandler:
    """拼图验证码处理器（使用视觉模型识别缺口位置）"""
    
    def __init__(self, vision_model_provider: Optional[str] = None):
        """
        初始化拼图验证码处理器
        
        Args:
            vision_model_provider: 视觉模型提供商
        """
        self.vision_model_provider = vision_model_provider
    
    async def solve(self, page: Page, selector: str) -> bool:
        """
        解决拼图验证码
        
        流程：
        1. 查找拼图块和背景图
        2. 使用视觉模型识别缺口位置
        3. 计算需要移动的距离
        4. 执行拖拽
        
        Args:
            page: Playwright Page对象
            selector: 验证码容器选择器
            
        Returns:
            是否成功
        """
        try:
            # 1. 查找拼图块和背景图
            puzzle_piece = await page.query_selector(f"{selector} .puzzle-piece, {selector} .jigsaw-piece")
            puzzle_bg = await page.query_selector(f"{selector} .puzzle-bg, {selector} .jigsaw-bg")
            
            if not puzzle_piece or not puzzle_bg:
                logger.error("未找到拼图元素")
                return False
            
            # 2. 获取拼图块和背景的位置
            piece_box = await puzzle_piece.bounding_box()
            bg_box = await puzzle_bg.bounding_box()
            
            if not piece_box or not bg_box:
                return False
            
            # 3. 截图背景图（包含缺口）
            bg_image_bytes = await puzzle_bg.screenshot()
            
            # 4. 使用视觉模型识别缺口位置
            gap_position = await self._detect_gap_with_vision_model(
                bg_image_bytes, bg_box, piece_box
            )
            
            if gap_position is None:
                logger.error("无法识别拼图缺口位置")
                return False
            
            # 5. 计算需要移动的距离
            target_x = gap_position
            target_y = bg_box['y'] + (bg_box['height'] / 2)  # 垂直居中
            
            # 6. 执行拖拽（分段移动，模拟人工操作）
            success = await self._drag_puzzle_piece(
                page, puzzle_piece, piece_box, target_x, target_y
            )
            
            if success:
                logger.info(f"拼图验证码完成，移动到: ({target_x:.2f}, {target_y:.2f})")
            
            return success
            
        except Exception as e:
            logger.error(f"拼图验证码处理失败: {e}")
            return False
    
    async def _detect_gap_with_vision_model(
        self,
        image_bytes: bytes,
        bg_box: Dict[str, float],
        piece_box: Dict[str, float]
    ) -> Optional[float]:
        """
        使用视觉模型识别拼图缺口位置
        
        Args:
            image_bytes: 背景图字节
            bg_box: 背景图边界框
            piece_box: 拼图块边界框
            
        Returns:
            缺口X坐标（页面坐标），如果识别失败返回None
        """
        try:
            # 导入视觉模型
            try:
                from ...ai.vision import create_vision_model
                from ...ai.config import ModelConfig, ModelProvider
            except ImportError:
                try:
                    import sys
                    import os
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)
                    from automation_framework.src.ai.vision import create_vision_model
                    from automation_framework.src.ai.config import ModelConfig, ModelProvider
                except ImportError:
                    return None
            
            import os
            api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return None
            
            config = ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",
                api_key=api_key
            )
            
            vision_model = create_vision_model(config)
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                prompt = """分析这张拼图验证码图片，识别缺口（凹槽）的位置。

请以JSON格式返回结果：
{
    "gap_x": <缺口左边缘相对于图片左边缘的X坐标（像素）>,
    "gap_y": <缺口上边缘相对于图片上边缘的Y坐标（像素）>,
    "gap_width": <缺口宽度（像素）>,
    "gap_height": <缺口高度（像素）>,
    "confidence": <识别置信度 0-1>
}

只返回JSON，不要包含其他文字。"""
                
                result = await vision_model.analyze_screenshot(tmp_file_path, prompt)
                
                import json
                import re
                
                json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    gap_x = data.get("gap_x")
                    confidence = data.get("confidence", 1.0)
                    
                    if gap_x is not None and confidence > 0.5:
                        # 转换为页面坐标
                        page_x = bg_box['x'] + gap_x
                        logger.info(f"视觉模型识别拼图缺口位置: {page_x}px, 置信度: {confidence:.2f}")
                        return page_x
                
                return None
                
            finally:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"视觉模型识别拼图缺口失败: {e}")
            return None
    
    async def _drag_puzzle_piece(
        self,
        page: Page,
        puzzle_piece: Any,
        piece_box: Dict[str, float],
        target_x: float,
        target_y: float
    ) -> bool:
        """
        拖拽拼图块到目标位置（分段移动，模拟人工操作）
        
        Args:
            page: Playwright Page对象
            puzzle_piece: 拼图块元素
            piece_box: 拼图块边界框
            target_x: 目标X坐标
            target_y: 目标Y坐标
            
        Returns:
            是否成功
        """
        try:
            start_x = piece_box['x'] + piece_box['width'] / 2
            start_y = piece_box['y'] + piece_box['height'] / 2
            
            # 分段移动（10段）
            segments = 10
            dx = (target_x - start_x) / segments
            dy = (target_y - start_y) / segments
            
            await puzzle_piece.hover()
            await page.mouse.down()
            
            current_x = start_x
            current_y = start_y
            
            for i in range(segments):
                current_x += dx
                current_y += dy
                await page.mouse.move(current_x, current_y, steps=15)
                await page.wait_for_timeout(30)  # 每段延迟
            
            await page.mouse.up()
            
            # 等待验证完成
            await page.wait_for_timeout(500)
            
            return True
            
        except Exception as e:
            logger.error(f"拖拽拼图块失败: {e}")
            return False


class RecaptchaHandler:
    """Google reCAPTCHA处理器"""
    
    async def solve(self, page: Page, selector: str) -> bool:
        """
        解决reCAPTCHA
        
        注意：reCAPTCHA通常需要：
        1. 使用第三方服务（如2captcha、anti-captcha）
        2. 或等待人工解决
        
        Args:
            page: Playwright Page对象
            selector: reCAPTCHA容器选择器
            
        Returns:
            是否成功
        """
        try:
            # 查找reCAPTCHA iframe
            iframe = await page.query_selector("iframe[src*='recaptcha']")
            if not iframe:
                logger.error("未找到reCAPTCHA iframe")
                return False
            
            # reCAPTCHA通常需要第三方服务或人工解决
            logger.warning("reCAPTCHA需要第三方服务（如2captcha）或人工解决")
            
            # 可以集成第三方服务API
            # 例如：2captcha API
            # result = await self._solve_with_2captcha(page, iframe)
            
            return False
            
        except Exception as e:
            logger.error(f"reCAPTCHA处理失败: {e}")
            return False


class SMSCaptchaHandler:
    """短信验证码处理器"""
    
    async def solve(self, page: Page, input_selector: str, phone_number: Optional[str] = None) -> Optional[str]:
        """
        处理短信验证码
        
        Args:
            page: Playwright Page对象
            input_selector: 验证码输入框选择器
            phone_number: 手机号（如果需要发送验证码）
            
        Returns:
            验证码文本（如果自动获取），否则返回None等待人工输入
        """
        try:
            # 如果需要发送验证码
            if phone_number:
                send_button = await page.query_selector("button:has-text('发送'), button:has-text('获取验证码')")
                if send_button:
                    await send_button.click()
                    logger.info("已点击发送验证码按钮")
            
            # 等待验证码输入
            # 实际实现需要：
            # 1. 集成短信接收服务（如接码平台）
            # 2. 或等待人工输入
            
            logger.warning("短信验证码需要集成接码平台或等待人工输入")
            return None
            
        except Exception as e:
            logger.error(f"短信验证码处理失败: {e}")
            return None


class RotateCaptchaHandler:
    """旋转验证码处理器（使用视觉模型识别旋转角度）"""
    
    def __init__(self, vision_model_provider: Optional[str] = None):
        """
        初始化旋转验证码处理器
        
        Args:
            vision_model_provider: 视觉模型提供商
        """
        self.vision_model_provider = vision_model_provider
    
    async def solve(self, page: Page, selector: str) -> bool:
        """
        解决旋转验证码
        
        流程：
        1. 截图验证码图片
        2. 使用视觉模型识别需要旋转的角度
        3. 执行旋转操作
        
        Args:
            page: Playwright Page对象
            selector: 验证码容器选择器
            
        Returns:
            是否成功
        """
        try:
            # 查找验证码图片和旋转按钮
            captcha_image = await page.query_selector(f"{selector} img, {selector} .captcha-image")
            rotate_button = await page.query_selector(f"{selector} .rotate-btn, {selector} button[title*='旋转']")
            
            if not captcha_image:
                logger.error("未找到验证码图片")
                return False
            
            # 截图验证码
            image_bytes = await captcha_image.screenshot()
            image_box = await captcha_image.bounding_box()
            if not image_box:
                return False
            
            # 使用视觉模型识别旋转角度
            rotation_angle = await self._detect_rotation_angle_with_vision(image_bytes)
            
            if rotation_angle is None:
                logger.error("无法识别旋转角度")
                return False
            
            # 执行旋转操作
            if rotate_button:
                # 如果有旋转按钮，点击旋转按钮
                clicks_needed = int(rotation_angle / 90)  # 每次旋转90度
                for _ in range(clicks_needed):
                    await rotate_button.click()
                    await page.wait_for_timeout(300)
            else:
                # 如果没有旋转按钮，使用JavaScript旋转
                await page.evaluate(f"""
                    const img = document.querySelector('{selector} img');
                    if (img) {{
                        img.style.transform = 'rotate({rotation_angle}deg)';
                    }}
                """)
            
            logger.info(f"旋转验证码完成，角度: {rotation_angle}度")
            return True
            
        except Exception as e:
            logger.error(f"旋转验证码处理失败: {e}")
            return False
    
    async def _detect_rotation_angle_with_vision(self, image_bytes: bytes) -> Optional[float]:
        """
        使用视觉模型识别需要旋转的角度
        
        Args:
            image_bytes: 验证码图片字节
            
        Returns:
            旋转角度（0-360度），如果识别失败返回None
        """
        try:
            # 导入视觉模型
            try:
                from ...ai.vision import create_vision_model
                from ...ai.config import ModelConfig, ModelProvider
            except ImportError:
                try:
                    import sys
                    import os
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)
                    from automation_framework.src.ai.vision import create_vision_model
                    from automation_framework.src.ai.config import ModelConfig, ModelProvider
                except ImportError:
                    return None
            
            import os
            api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return None
            
            config = ModelConfig(
                provider=ModelProvider.QWEN,
                model="qwen-vl-plus",
                api_key=api_key
            )
            
            vision_model = create_vision_model(config)
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                prompt = """分析这张旋转验证码图片，识别需要旋转的角度。

请以JSON格式返回结果：
{
    "rotation_angle": <需要旋转的角度（0-360度）>,
    "direction": <旋转方向: "clockwise"或"counterclockwise">,
    "confidence": <识别置信度 0-1>
}

只返回JSON，不要包含其他文字。"""
                
                result = await vision_model.analyze_screenshot(tmp_file_path, prompt)
                
                import json
                import re
                
                json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    angle = data.get("rotation_angle")
                    confidence = data.get("confidence", 1.0)
                    
                    if angle is not None and confidence > 0.5:
                        logger.info(f"视觉模型识别旋转角度: {angle}度, 置信度: {confidence:.2f}")
                        return float(angle)
                
                return None
                
            finally:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"视觉模型识别旋转角度失败: {e}")
            return None


class EmailCaptchaHandler:
    """邮箱验证码处理器"""
    
    async def solve(self, page: Page, input_selector: str, email: Optional[str] = None) -> Optional[str]:
        """
        处理邮箱验证码
        
        Args:
            page: Playwright Page对象
            input_selector: 验证码输入框选择器
            email: 邮箱地址（如果需要发送验证码）
            
        Returns:
            验证码文本（如果自动获取），否则返回None等待人工输入
        """
        try:
            # 如果需要发送验证码
            if email:
                send_button = await page.query_selector("button:has-text('发送'), button:has-text('获取验证码')")
                if send_button:
                    await send_button.click()
                    logger.info("已点击发送验证码按钮")
            
            # 等待验证码输入
            # 实际实现需要：
            # 1. 集成邮箱接收服务
            # 2. 或等待人工输入
            
            logger.warning("邮箱验证码需要集成邮箱接收服务或等待人工输入")
            return None
            
        except Exception as e:
            logger.error(f"邮箱验证码处理失败: {e}")
            return None
