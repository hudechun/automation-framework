"""
验证码处理操作 - 支持多种验证码类型
"""
from typing import Optional, Dict, Any
from playwright.async_api import Page
from .interfaces import Action, Driver
from .types import ActionType
from .anti_detection import CaptchaHandler
from .captcha_types import (
    CaptchaType, CaptchaDetector,
    ImageCaptchaHandler, SliderCaptchaHandler, ClickCaptchaHandler,
    PuzzleCaptchaHandler, RotateCaptchaHandler, RecaptchaHandler,
    SMSCaptchaHandler, EmailCaptchaHandler
)
from .captcha_vision_recognizer import CaptchaVisionRecognizer
from .captcha_statistics import get_global_statistics
from .math_captcha_solver import MathCaptchaSolver
from .captcha_adaptive_strategy import AdaptiveCaptchaStrategy, StrategyConfig, StrategyResult
import logging

logger = logging.getLogger(__name__)


class HandleCaptcha(Action):
    """
    处理验证码操作
    """
    
    # 常见验证码输入框选择器
    CAPTCHA_INPUT_SELECTORS = [
        "input[name*='captcha']",
        "input[name*='验证码']",
        "input[type='text'][placeholder*='captcha']",
        "input[type='text'][placeholder*='验证码']",
    ]
    
    def __init__(
        self,
        selector: Optional[str] = None,
        ocr_provider: Optional[str] = None,
        manual_input: bool = False,
        timeout: int = 60000,
        vision_model_provider: Optional[str] = None
    ):
        """
        初始化验证码处理
        
        Args:
            selector: 验证码图片选择器（如果为None，自动检测）
            ocr_provider: OCR服务提供商
            manual_input: 是否等待人工输入
            timeout: 超时时间（毫秒）
            vision_model_provider: 视觉模型提供商（如"qwen", "gpt4v", "claude"）
        """
        super().__init__(
            ActionType.INTERACTION,
            selector=selector,
            ocr_provider=ocr_provider,
            manual_input=manual_input,
            timeout=timeout
        )
        self.selector = selector
        self.ocr_provider = ocr_provider
        self.manual_input = manual_input
        self.timeout = timeout
        self.vision_model_provider = vision_model_provider
        self.captcha_handler = CaptchaHandler(
            ocr_provider=ocr_provider,
            manual_fallback=manual_input
        )
        # 初始化统一的视觉模型识别器
        self.vision_recognizer = CaptchaVisionRecognizer(vision_model_provider=vision_model_provider)
        # 初始化自适应策略管理器
        self.adaptive_strategy = AdaptiveCaptchaStrategy(
            vision_model_provider=vision_model_provider,
            config=StrategyConfig(
                max_attempts=3,
                confidence_threshold=0.5,
                enable_fallback=True,
                enable_learning=True,
                adaptive_params=True
            )
        )
    
    async def _fill_captcha_input(self, page: Page, value: str) -> bool:
        """
        在常见验证码输入框中填写文本
        
        Returns:
            True 表示填写成功，False 表示未找到可用输入框
        """
        for input_selector in self.CAPTCHA_INPUT_SELECTORS:
            try:
                input_element = await page.query_selector(input_selector)
                if input_element:
                    await input_element.fill(value)
                    logger.info(f"已在验证码输入框 {input_selector} 中填写值")
                    return True
            except Exception as e:
                logger.debug(f\"填写验证码输入框失败, selector={input_selector}, error={e}\")
                continue
        return False
    
    def validate(self) -> bool:
        """验证参数"""
        return isinstance(self.timeout, int) and self.timeout > 0
    
    async def execute(self, driver: Driver) -> Dict[str, Any]:
        """
        执行验证码处理（统一视觉模型处理流程）
        
        流程：
        1. 自动定位验证码元素（如果selector为None）
        2. 截图验证码
        3. 使用统一的视觉模型识别器识别类型和数据
        4. 根据类型分发到专门的处理方法
        5. 如果视觉模型识别失败，回退到原有的检测和处理流程
        """
        if not self.validate():
            raise ValueError("Invalid captcha handler parameters")
        
        if not hasattr(driver, '_current_page'):
            raise RuntimeError("Driver does not have a current page")
        
        page = driver._current_page
        
        # 1. 自动定位验证码元素（如果selector为None）
        captcha_element = None
        captcha_selector = self.selector
        
        if not captcha_selector:
            # 尝试自动检测验证码元素
            captcha_selectors = [
                "img[alt*='验证码']",
                "img[alt*='captcha']",
                ".captcha img",
                "#captcha img",
                "[class*='captcha'] img",
                "[id*='captcha'] img",
                ".slider-verify",
                ".slider-captcha",
                ".click-captcha",
                ".puzzle-captcha",
                ".rotate-captcha",
            ]
            
            for selector in captcha_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        captcha_element = element
                        captcha_selector = selector
                        logger.info(f"自动检测到验证码元素: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"自动检测验证码元素失败: {selector}, error={e}")
                    continue
        
        # 检查是否是短信或邮箱验证码（这些不需要截图）
        if await CaptchaDetector.detect_sms_captcha(page):
            return await self._solve_sms_captcha(page, captcha_selector)
        elif await CaptchaDetector.detect_email_captcha(page):
            return await self._solve_email_captcha(page, captcha_selector)
        
        # 如果没有找到验证码元素，尝试使用原有的检测方法
        if not captcha_element:
            detector = CaptchaDetector(vision_model_provider=self.vision_model_provider)
            captcha_type, detected_selector = await detector.detect_captcha_type(page)
            
            if not captcha_type:
                logger.info("No captcha detected")
                return {"success": True, "captcha_detected": False, "captcha_type": None}
            
            captcha_selector = detected_selector
            captcha_element = await page.query_selector(captcha_selector) if captcha_selector else None
        
        if not captcha_element:
            logger.warning("无法定位验证码元素")
            return {"success": False, "error": "无法定位验证码元素"}
        
        # 2. 截图验证码
        try:
            captcha_image_bytes = await captcha_element.screenshot()
        except Exception as e:
            logger.error(f"截图验证码失败: {e}")
            return {"success": False, "error": f"截图失败: {str(e)}"}
        
        # 3. 使用统一的视觉模型识别器识别类型和数据
        recognition_result = await self.vision_recognizer.recognize(captcha_image_bytes)
        
        captcha_type_str = recognition_result.get("type", "unknown")
        recognition_data = recognition_result.get("data", {})
        confidence = recognition_result.get("confidence", 0.0)
        
        logger.info(f"视觉模型识别结果: type={captcha_type_str}, confidence={confidence:.2f}")
        
        # 4. 使用自适应策略处理验证码
        async def adaptive_handler(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
            """自适应处理函数包装器"""
            params["page"] = page
            params["captcha_selector"] = captcha_selector
            params["recognition_data"] = recognition_result if confidence > 0.3 else None
            params["selector"] = self.selector
            return await self._adaptive_handler(method, params)
        
        strategy_result = await self.adaptive_strategy.execute_adaptive_strategy(
            captcha_type=captcha_type_str,
            recognition_data=recognition_result if confidence > 0.3 else None,
            handler_func=adaptive_handler
        )
        
        # 5. 如果自适应策略失败，回退到原有方法
        if not strategy_result.success:
            logger.info("自适应策略失败，回退到原有的验证码检测和处理流程")
            detector = CaptchaDetector(vision_model_provider=self.vision_model_provider)
            captcha_type, detected_selector = await detector.detect_captcha_type(page)
            
            if not captcha_type:
                return {
                    "success": False,
                    "error": "无法识别验证码类型",
                    "adaptive_strategy_failed": True
                }
            
            selector = captcha_selector or detected_selector
            result = await self._solve_by_type(page, captcha_type, selector)
            
            # 记录统计信息
            statistics = get_global_statistics()
            statistics.record_captcha(
                captcha_type=captcha_type,
                success=result.get("success", False),
                method=result.get("method", "fallback")
            )
            
            return result
        
        # 6. 记录统计信息
        statistics = get_global_statistics()
        try:
            captcha_type_enum = CaptchaType(captcha_type_str)
        except ValueError:
            captcha_type_enum = CaptchaType.UNKNOWN
        
        statistics.record_captcha(
            captcha_type=captcha_type_enum,
            success=strategy_result.success,
            method=strategy_result.method
        )
        
        # 返回结果
        return {
            "success": strategy_result.success,
            "captcha_type": captcha_type_str,
            "captcha_solved": strategy_result.success,
            "method": strategy_result.method,
            "confidence": strategy_result.confidence,
            "execution_time": strategy_result.execution_time,
            **strategy_result.metadata
        }
    
    async def _adaptive_handler(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        自适应策略处理函数
        
        Args:
            method: 处理方法名称
            params: 处理参数（包含page, captcha_selector等）
            
        Returns:
            处理结果
        """
        page = params.get("page")
        captcha_selector = params.get("captcha_selector")
        recognition_data = params.get("recognition_data")
        
        if not page:
            return {"success": False, "error": "Page not provided"}
        
        try:
            if method == "vision_model":
                # 使用视觉模型数据
                if recognition_data:
                    captcha_type_str = recognition_data.get("type", "unknown")
                    data = recognition_data.get("data", {})
                    return await self._solve_by_type_with_data(
                        page, captcha_type_str, data, captcha_selector
                    )
                else:
                    return {"success": False, "error": "No recognition data"}
            
            elif method == "math_calculator":
                # 数学计算题
                text = params.get("text", "")
                if text:
                    result = MathCaptchaSolver.extract_and_solve(text)
                    if result:
                        filled = await self._fill_captcha_input(page, result)
                        if filled:
                            return {
                                "success": True,
                                "captcha_type": "image",
                                "method": "math_calculator",
                                "confidence": 0.95
                            }
                return {"success": False, "error": "Math calculation failed"}
            
            elif method == "ocr":
                # OCR识别（支持本地Tesseract和云端OCR）
                # 优先使用本地OCR（如果配置了tesseract）
                if self.ocr_provider and self.ocr_provider.lower() == "tesseract":
                    from .local_ocr import get_local_ocr
                    ocr = get_local_ocr()
                    if ocr.is_available():
                        # 使用本地OCR
                        try:
                            captcha_element = await page.query_selector(captcha_selector or ".captcha img")
                            if captcha_element:
                                image_bytes = await captcha_element.screenshot()
                                text = await ocr.recognize(image_bytes, preprocess=True)
                                if text and await self._fill_captcha_input(page, text):
                                    return {
                                        "success": True,
                                        "captcha_type": "image",
                                        "method": "local_ocr",
                                        "confidence": 0.7
                                    }
                        except Exception as e:
                            logger.warning(f"本地OCR识别失败: {e}，回退到原有方法")
                # 回退到原有OCR方法
                return await self._solve_image_captcha(page, captcha_selector)
            
            elif method == "fallback":
                # 回退方法
                detector = CaptchaDetector(vision_model_provider=self.vision_model_provider)
                captcha_type, detected_selector = await detector.detect_captcha_type(page)
                if captcha_type:
                    selector = captcha_selector or detected_selector
                    return await self._solve_by_type(page, captcha_type, selector)
                return {"success": False, "error": "Fallback detection failed"}
            
            else:
                return {"success": False, "error": f"Unknown method: {method}"}
        
        except Exception as e:
            logger.error(f"自适应处理函数异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def _solve_by_type_with_data(
        self,
        page: Page,
        captcha_type_str: str,
        recognition_data: Dict[str, Any],
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """
        根据视觉模型返回的类型和数据解决验证码
        
        Args:
            page: Playwright Page对象
            captcha_type_str: 验证码类型字符串（"image", "slider", "click", "puzzle", "rotate"）
            recognition_data: 视觉模型返回的数据
            selector: 验证码选择器
            
        Returns:
            处理结果
        """
        if captcha_type_str == "image":
            return await self._solve_image_captcha_with_data(page, recognition_data, selector)
        elif captcha_type_str == "slider":
            return await self._solve_slider_captcha_with_data(page, recognition_data, selector)
        elif captcha_type_str == "click":
            return await self._solve_click_captcha_with_data(page, recognition_data, selector)
        elif captcha_type_str == "puzzle":
            return await self._solve_puzzle_captcha_with_data(page, recognition_data, selector)
        elif captcha_type_str == "rotate":
            return await self._solve_rotate_captcha_with_data(page, recognition_data, selector)
        else:
            logger.warning(f"未知验证码类型: {captcha_type_str}，使用通用处理")
            return await self._solve_generic_captcha(page, selector)
    
    async def _solve_by_type(
        self,
        page: Page,
        captcha_type: CaptchaType,
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """根据验证码类型解决验证码（原有方法，作为回退）"""
        
        if captcha_type == CaptchaType.IMAGE:
            # 图形验证码（OCR识别）
            return await self._solve_image_captcha(page, selector)
        
        elif captcha_type == CaptchaType.SLIDER:
            # 滑动验证码
            return await self._solve_slider_captcha(page, selector)
        
        elif captcha_type == CaptchaType.CLICK:
            # 点选验证码
            return await self._solve_click_captcha(page, selector)
        
        elif captcha_type == CaptchaType.PUZZLE:
            # 拼图验证码
            return await self._solve_puzzle_captcha(page, selector)
        
        elif captcha_type == CaptchaType.RECAPTCHA:
            # Google reCAPTCHA
            return await self._solve_recaptcha(page, selector)
        
        elif captcha_type == CaptchaType.HCAPTCHA:
            # hCaptcha
            return await self._solve_hcaptcha(page, selector)
        
        elif captcha_type == CaptchaType.SMS:
            # 短信验证码
            return await self._solve_sms_captcha(page, selector)
        
        elif captcha_type == CaptchaType.EMAIL:
            # 邮箱验证码
            return await self._solve_email_captcha(page, selector)
        
        elif captcha_type == CaptchaType.ROTATE:
            # 旋转验证码
            return await self._solve_rotate_captcha(page, selector)
        
        else:
            # 未知类型，使用通用处理
            logger.warning(f"未知验证码类型: {captcha_type.value}，使用通用处理")
            return await self._solve_generic_captcha(page, selector)
    
    async def _solve_image_captcha_with_data(
        self,
        page: Page,
        recognition_data: Dict[str, Any],
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """使用视觉模型返回的数据处理图形验证码（支持数学计算题）"""
        captcha_text = recognition_data.get("text", "").strip()
        
        if not captcha_text:
            logger.warning("视觉模型未返回验证码文字，回退到原有方法")
            return await self._solve_image_captcha(page, selector)
        
        # 检查是否是数学计算题验证码
        final_text = captcha_text
        is_math_captcha = False
        original_expression = None
        
        if MathCaptchaSolver.is_math_captcha(captcha_text):
            # 尝试求解数学计算题
            result = MathCaptchaSolver.extract_and_solve(captcha_text)
            if result:
                original_expression = captcha_text
                final_text = result
                is_math_captcha = True
                logger.info(f"检测到数学计算题验证码: {original_expression} -> {final_text}")
            else:
                logger.warning(f"无法求解数学计算题: {captcha_text}")
        
        # 填写验证码（如果是数学计算题，填写计算结果；否则填写原始文本）
        filled = await self._fill_captcha_input(page, final_text)
        if filled:
            log_msg = f"使用视觉模型识别结果填写验证码: {final_text}"
            if is_math_captcha:
                log_msg += f" (原始表达式: {original_expression})"
            logger.info(log_msg)
            return {
                "success": True,
                "captcha_type": CaptchaType.IMAGE.value,
                "captcha_solved": True,
                "method": "vision_model",
                "captcha_text": final_text,
                "is_math_captcha": is_math_captcha,
                "original_expression": original_expression if is_math_captcha else None
            }
        
        # 如果找不到输入框，返回成功但标记为未填写
        return {
            "success": True,
            "captcha_type": CaptchaType.IMAGE.value,
            "captcha_solved": False,
            "error": "未找到验证码输入框",
            "captcha_text": final_text,
            "is_math_captcha": is_math_captcha,
            "original_expression": original_expression if is_math_captcha else None
        }
    
    async def _solve_image_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理图形验证码（支持视觉模型和OCR，支持数学计算题）（原有方法，作为回退）"""
        handler = ImageCaptchaHandler(
            vision_model_provider=self.vision_model_provider,
            ocr_provider=self.ocr_provider
        )
        captcha_text = await handler.solve(page, selector or "", self.ocr_provider)
        
        if captcha_text:
            # 检查是否是数学计算题验证码
            final_text = captcha_text
            is_math_captcha = False
            original_expression = None
            
            if MathCaptchaSolver.is_math_captcha(captcha_text):
                # 尝试求解数学计算题
                result = MathCaptchaSolver.extract_and_solve(captcha_text)
                if result:
                    original_expression = captcha_text
                    final_text = result
                    is_math_captcha = True
                    logger.info(f"检测到数学计算题验证码: {original_expression} -> {final_text}")
            
            # 填写验证码
            if await self._fill_captcha_input(page, final_text):
                return {
                    "success": True,
                    "captcha_type": CaptchaType.IMAGE.value,
                    "captcha_solved": True,
                    "method": "vision" if self.vision_model_provider else "ocr",
                    "is_math_captcha": is_math_captcha,
                    "original_expression": original_expression if is_math_captcha else None
                }
        
        # OCR失败，等待人工输入
        if self.manual_input:
            return {
                "success": True,
                "captcha_type": CaptchaType.IMAGE.value,
                "captcha_solved": False,
                "manual_input": True
            }
        
        return {
            "success": False,
            "captcha_type": CaptchaType.IMAGE.value,
            "error": "OCR识别失败且未启用人工输入"
        }
    
    async def _solve_slider_captcha_with_data(
        self,
        page: Page,
        recognition_data: Dict[str, Any],
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """使用视觉模型返回的数据处理滑动验证码"""
        gap_x = recognition_data.get("gap_x")
        gap_width = recognition_data.get("gap_width", 0)
        
        if gap_x is None:
            logger.warning("视觉模型未返回缺口位置，回退到原有方法")
            return await self._solve_slider_captcha(page, selector)
        
        try:
            # 查找滑块和轨道元素
            selector_str = selector or ""
            slider_track = await page.query_selector(f"{selector_str} .slider-track, {selector_str} .slider-bg, {selector_str} .geetest_slider_track")
            slider_button = await page.query_selector(f"{selector_str} .slider-button, {selector_str} .slider-btn, {selector_str} .geetest_slider_button")
            
            if not slider_track or not slider_button:
                logger.error("未找到滑块元素")
                return await self._solve_slider_captcha(page, selector)
            
            # 获取滑块和轨道的尺寸和位置
            track_box = await slider_track.bounding_box()
            button_box = await slider_button.bounding_box()
            
            if not track_box or not button_box:
                return await self._solve_slider_captcha(page, selector)
            
            # 计算滑动距离（缺口位置 - 滑块当前位置）
            slide_distance = gap_x - (button_box['x'] - track_box['x'])
            
            # 使用SliderCaptchaHandler的校准和滑动逻辑
            handler = SliderCaptchaHandler(vision_model_provider=self.vision_model_provider)
            
            # 通过5次校验计算校验因子
            calibration_factor = await handler._calibrate_slide_distance(
                page, slider_button, button_box, slide_distance
            )
            
            # 使用校验因子计算真实距离
            real_distance = slide_distance * calibration_factor
            
            # 执行分段滑动（20份，前85%快速，后15%慢速）
            success = await handler._slide_with_segments(
                page, slider_button, button_box, real_distance
            )
            
            if success:
                logger.info(f"滑动验证码完成（使用视觉模型数据），距离: {real_distance:.2f}px")
            
            return {
                "success": success,
                "captcha_type": CaptchaType.SLIDER.value,
                "captcha_solved": success,
                "method": "vision_model"
            }
            
        except Exception as e:
            logger.error(f"使用视觉模型数据处理滑动验证码失败: {e}，回退到原有方法")
            return await self._solve_slider_captcha(page, selector)
    
    async def _solve_slider_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理滑动验证码（使用视觉模型识别缺口位置）（原有方法，作为回退）"""
        handler = SliderCaptchaHandler(vision_model_provider=self.vision_model_provider)
        success = await handler.solve(page, selector or "")
        
        return {
            "success": success,
            "captcha_type": CaptchaType.SLIDER.value,
            "captcha_solved": success
        }
    
    async def _solve_click_captcha_with_data(
        self,
        page: Page,
        recognition_data: Dict[str, Any],
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """使用视觉模型返回的数据处理点选验证码"""
        targets = recognition_data.get("targets", [])
        
        if not targets:
            logger.warning("视觉模型未返回点击目标，回退到原有方法")
            return await self._solve_click_captcha(page, selector)
        
        try:
            # 获取验证码容器元素（用于坐标转换）
            selector_str = selector or ""
            captcha_element = await page.query_selector(selector_str) if selector_str else None
            element_box = None
            
            if captcha_element:
                element_box = await captcha_element.bounding_box()
            
            # 按顺序点击所有目标
            for target in targets:
                x = target.get("x")
                y = target.get("y")
                text = target.get("text", "")
                
                if x is not None and y is not None:
                    # 如果坐标是相对于验证码元素的，需要转换为页面坐标
                    if element_box:
                        page_x = element_box['x'] + x
                        page_y = element_box['y'] + y
                    else:
                        page_x = x
                        page_y = y
                    
                    await page.mouse.click(page_x, page_y)
                    await page.wait_for_timeout(300)  # 点击间隔
                    logger.info(f"点击坐标: ({page_x}, {page_y}), 目标: {text}")
            
            logger.info(f"点选验证码完成（使用视觉模型数据），点击了{len(targets)}个目标")
            return {
                "success": True,
                "captcha_type": CaptchaType.CLICK.value,
                "captcha_solved": True,
                "method": "vision_model",
                "targets_count": len(targets)
            }
            
        except Exception as e:
            logger.error(f"使用视觉模型数据处理点选验证码失败: {e}，回退到原有方法")
            return await self._solve_click_captcha(page, selector)
    
    async def _solve_click_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理点选验证码（使用视觉模型识别点击目标）（原有方法，作为回退）"""
        handler = ClickCaptchaHandler(vision_model_provider=self.vision_model_provider)
        # 点选验证码通常需要指定目标文字或使用视觉模型识别
        success = await handler.solve(page, selector or "", target_text=None)
        
        if not success and self.manual_input:
            return {
                "success": True,
                "captcha_type": CaptchaType.CLICK.value,
                "captcha_solved": False,
                "manual_input": True
            }
        
        return {
            "success": success,
            "captcha_type": CaptchaType.CLICK.value,
            "captcha_solved": success
        }
    
    async def _solve_puzzle_captcha_with_data(
        self,
        page: Page,
        recognition_data: Dict[str, Any],
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """使用视觉模型返回的数据处理拼图验证码"""
        gap_x = recognition_data.get("gap_x")
        gap_y = recognition_data.get("gap_y")
        gap_width = recognition_data.get("gap_width", 0)
        gap_height = recognition_data.get("gap_height", 0)
        
        if gap_x is None or gap_y is None:
            logger.warning("视觉模型未返回拼图缺口位置，回退到原有方法")
            return await self._solve_puzzle_captcha(page, selector)
        
        try:
            # 查找拼图块和背景图
            selector_str = selector or ""
            puzzle_piece = await page.query_selector(f"{selector_str} .puzzle-piece, {selector_str} .jigsaw-piece")
            puzzle_bg = await page.query_selector(f"{selector_str} .puzzle-bg, {selector_str} .jigsaw-bg")
            
            if not puzzle_piece or not puzzle_bg:
                logger.error("未找到拼图元素")
                return await self._solve_puzzle_captcha(page, selector)
            
            # 获取拼图块和背景的位置
            piece_box = await puzzle_piece.bounding_box()
            bg_box = await puzzle_bg.bounding_box()
            
            if not piece_box or not bg_box:
                return await self._solve_puzzle_captcha(page, selector)
            
            # 转换为页面坐标
            target_x = bg_box['x'] + gap_x
            target_y = bg_box['y'] + gap_y
            
            # 使用PuzzleCaptchaHandler的拖拽逻辑
            handler = PuzzleCaptchaHandler(vision_model_provider=self.vision_model_provider)
            success = await handler._drag_puzzle_piece(
                page, puzzle_piece, piece_box, target_x, target_y
            )
            
            if success:
                logger.info(f"拼图验证码完成（使用视觉模型数据），移动到: ({target_x:.2f}, {target_y:.2f})")
            
            return {
                "success": success,
                "captcha_type": CaptchaType.PUZZLE.value,
                "captcha_solved": success,
                "method": "vision_model"
            }
            
        except Exception as e:
            logger.error(f"使用视觉模型数据处理拼图验证码失败: {e}，回退到原有方法")
            return await self._solve_puzzle_captcha(page, selector)
    
    async def _solve_puzzle_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理拼图验证码（原有方法，作为回退）"""
        handler = PuzzleCaptchaHandler(vision_model_provider=self.vision_model_provider)
        success = await handler.solve(page, selector or "")
        
        return {
            "success": success,
            "captcha_type": CaptchaType.PUZZLE.value,
            "captcha_solved": success
        }
    
    async def _solve_recaptcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理reCAPTCHA"""
        handler = RecaptchaHandler()
        success = await handler.solve(page, selector or "")
        
        if not success and self.manual_input:
            return {
                "success": True,
                "captcha_type": CaptchaType.RECAPTCHA.value,
                "captcha_solved": False,
                "manual_input": True,
                "note": "reCAPTCHA通常需要第三方服务或人工解决"
            }
        
        return {
            "success": success,
            "captcha_type": CaptchaType.RECAPTCHA.value,
            "captcha_solved": success
        }
    
    async def _solve_hcaptcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理hCaptcha"""
        # hCaptcha处理类似reCAPTCHA
        if self.manual_input:
            return {
                "success": True,
                "captcha_type": CaptchaType.HCAPTCHA.value,
                "captcha_solved": False,
                "manual_input": True,
                "note": "hCaptcha通常需要第三方服务或人工解决"
            }
        
        return {
            "success": False,
            "captcha_type": CaptchaType.HCAPTCHA.value,
            "error": "hCaptcha需要第三方服务或人工解决"
        }
    
    async def _solve_sms_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理短信验证码"""
        handler = SMSCaptchaHandler()
        input_selector = selector or "input[placeholder*='验证码'], input[name*='sms']"
        code = await handler.solve(page, input_selector)
        
        if code:
            # 自动填写验证码
            try:
                input_element = await page.query_selector(input_selector)
                if input_element:
                    await input_element.fill(code)
                    return {
                        "success": True,
                        "captcha_type": CaptchaType.SMS.value,
                        "captcha_solved": True,
                        "method": "auto"
                    }
            except Exception as e:
                logger.debug(f"自动填写短信验证码失败, selector={input_selector}, error={e}")
        
        # 等待人工输入
        if self.manual_input:
            return {
                "success": True,
                "captcha_type": CaptchaType.SMS.value,
                "captcha_solved": False,
                "manual_input": True,
                "note": "需要人工输入短信验证码或集成接码平台"
            }
        
        return {
            "success": False,
            "captcha_type": CaptchaType.SMS.value,
            "error": "短信验证码需要接码平台或人工输入"
        }
    
    async def _solve_rotate_captcha_with_data(
        self,
        page: Page,
        recognition_data: Dict[str, Any],
        selector: Optional[str]
    ) -> Dict[str, Any]:
        """使用视觉模型返回的数据处理旋转验证码"""
        rotation_angle = recognition_data.get("rotation_angle")
        direction = recognition_data.get("direction", "clockwise")
        
        if rotation_angle is None:
            logger.warning("视觉模型未返回旋转角度，回退到原有方法")
            return await self._solve_rotate_captcha(page, selector)
        
        try:
            # 查找验证码图片和旋转按钮
            selector_str = selector or ""
            captcha_image = await page.query_selector(f"{selector_str} img, {selector_str} .captcha-image")
            rotate_button = await page.query_selector(f"{selector_str} .rotate-btn, {selector_str} button[title*='旋转']")
            
            if not captcha_image:
                logger.error("未找到验证码图片")
                return await self._solve_rotate_captcha(page, selector)
            
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
                    const img = document.querySelector('{selector_str} img');
                    if (img) {{
                        img.style.transform = 'rotate({rotation_angle}deg)';
                    }}
                """)
            
            logger.info(f"旋转验证码完成（使用视觉模型数据），角度: {rotation_angle}度, 方向: {direction}")
            return {
                "success": True,
                "captcha_type": CaptchaType.ROTATE.value,
                "captcha_solved": True,
                "method": "vision_model",
                "rotation_angle": rotation_angle
            }
            
        except Exception as e:
            logger.error(f"使用视觉模型数据处理旋转验证码失败: {e}，回退到原有方法")
            return await self._solve_rotate_captcha(page, selector)
    
    async def _solve_rotate_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理旋转验证码（使用视觉模型识别旋转角度）（原有方法，作为回退）"""
        handler = RotateCaptchaHandler(vision_model_provider=self.vision_model_provider)
        success = await handler.solve(page, selector or "")
        
        return {
            "success": success,
            "captcha_type": CaptchaType.ROTATE.value,
            "captcha_solved": success
        }
    
    async def _solve_email_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """处理邮箱验证码"""
        handler = EmailCaptchaHandler()
        input_selector = selector or "input[placeholder*='邮箱验证码'], input[name*='email_code']"
        code = await handler.solve(page, input_selector)
        
        if code:
            try:
                input_element = await page.query_selector(input_selector)
                if input_element:
                    await input_element.fill(code)
                    return {
                        "success": True,
                        "captcha_type": CaptchaType.EMAIL.value,
                        "captcha_solved": True,
                        "method": "auto"
                    }
            except Exception as e:
                logger.debug(f"自动填写邮箱验证码失败, selector={input_selector}, error={e}")
        
        if self.manual_input:
            return {
                "success": True,
                "captcha_type": CaptchaType.EMAIL.value,
                "captcha_solved": False,
                "manual_input": True,
                "note": "需要人工输入邮箱验证码或集成邮箱接收服务"
            }
        
        return {
            "success": False,
            "captcha_type": CaptchaType.EMAIL.value,
            "error": "邮箱验证码需要邮箱接收服务或人工输入"
        }
    
    async def _solve_generic_captcha(self, page: Page, selector: Optional[str]) -> Dict[str, Any]:
        """通用验证码处理（回退到原有逻辑）"""
        has_captcha = await self.captcha_handler.detect_captcha(page)
        if not has_captcha:
            return {"success": True, "captcha_detected": False, "captcha_type": "unknown"}
        
        captcha_text = await self.captcha_handler.solve_captcha(page, selector)
        
        if captcha_text:
            # 查找验证码输入框并填写
            if await self._fill_captcha_input(page, captcha_text):
                return {
                    "success": True,
                    "captcha_type": "unknown",
                    "captcha_solved": True,
                    "method": "generic"
                }
        
        if self.manual_input:
            return {
                "success": True,
                "captcha_type": "unknown",
                "captcha_solved": False,
                "manual_input": True
            }
        
        return {
            "success": False,
            "captcha_type": "unknown",
            "error": "Failed to solve captcha"
        }
