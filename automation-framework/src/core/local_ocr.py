"""
本地OCR服务 - 支持Tesseract OCR本地运行
"""
import logging
import io
from typing import Optional, Dict, Any
from PIL import Image
import asyncio

logger = logging.getLogger(__name__)


class LocalOCR:
    """
    本地OCR服务（基于Tesseract）
    
    支持：
    - Tesseract OCR（需要系统安装Tesseract）
    - 图像预处理（提高识别率）
    - 多语言支持
    """
    
    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        lang: str = "eng+chi_sim",
        config: Optional[str] = None
    ):
        """
        初始化本地OCR
        
        Args:
            tesseract_cmd: Tesseract可执行文件路径（如果不在PATH中）
            lang: 语言代码（如"eng", "chi_sim", "eng+chi_sim"）
            config: Tesseract配置参数（如"--psm 7"）
        """
        self.tesseract_cmd = tesseract_cmd
        self.lang = lang
        self.config = config or "--psm 7"
        self._tesseract_available = None
    
    def _check_tesseract_available(self) -> bool:
        """检查Tesseract是否可用"""
        if self._tesseract_available is not None:
            return self._tesseract_available
        
        try:
            import pytesseract
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            
            # 尝试获取版本信息
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR可用，版本: {version}")
            self._tesseract_available = True
            return True
        except Exception as e:
            logger.warning(f"Tesseract OCR不可用: {e}")
            logger.warning("请安装Tesseract OCR:")
            logger.warning("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            logger.warning("  macOS: brew install tesseract")
            logger.warning("  Linux: sudo apt-get install tesseract-ocr")
            self._tesseract_available = False
            return False
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        图像预处理（提高OCR识别率）
        
        Args:
            image: PIL Image对象
            
        Returns:
            预处理后的图像
        """
        from PIL import ImageEnhance, ImageFilter
        
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # 增强锐度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # 应用去噪滤镜
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    async def recognize(
        self,
        image_bytes: bytes,
        preprocess: bool = True,
        lang: Optional[str] = None,
        config: Optional[str] = None
    ) -> Optional[str]:
        """
        识别图像中的文字（异步）
        
        Args:
            image_bytes: 图像字节数据
            preprocess: 是否预处理图像
            lang: 语言代码（覆盖初始化时的设置）
            config: Tesseract配置（覆盖初始化时的设置）
            
        Returns:
            识别出的文字，失败返回None
        """
        if not self._check_tesseract_available():
            return None
        
        try:
            # 在线程池中执行OCR（避免阻塞）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._recognize_sync,
                image_bytes,
                preprocess,
                lang or self.lang,
                config or self.config
            )
            return result
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return None
    
    def _recognize_sync(
        self,
        image_bytes: bytes,
        preprocess: bool,
        lang: str,
        config: str
    ) -> Optional[str]:
        """
        同步OCR识别（在线程池中执行）
        
        Args:
            image_bytes: 图像字节数据
            preprocess: 是否预处理
            lang: 语言代码
            config: Tesseract配置
            
        Returns:
            识别出的文字
        """
        import pytesseract
        
        try:
            # 设置Tesseract路径（如果需要）
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            
            # 加载图像
            image = Image.open(io.BytesIO(image_bytes))
            
            # 预处理（如果需要）
            if preprocess:
                image = self._preprocess_image(image)
            
            # OCR识别
            text = pytesseract.image_to_string(
                image,
                lang=lang,
                config=config
            )
            
            # 清理结果
            text = self._clean_text(text)
            
            logger.debug(f"OCR识别结果: {text}")
            return text if text else None
            
        except Exception as e:
            logger.error(f"OCR识别异常: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        清理OCR识别结果
        
        Args:
            text: 原始识别文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除空白字符
        text = text.strip()
        
        # 移除特殊字符（保留字母、数字、中文）
        import re
        # 保留字母、数字、中文、常见符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff+\-*/=()]', '', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', '', text)
        
        return text
    
    def recognize_sync(
        self,
        image_bytes: bytes,
        preprocess: bool = True,
        lang: Optional[str] = None,
        config: Optional[str] = None
    ) -> Optional[str]:
        """
        同步OCR识别（直接调用）
        
        Args:
            image_bytes: 图像字节数据
            preprocess: 是否预处理
            lang: 语言代码
            config: Tesseract配置
            
        Returns:
            识别出的文字
        """
        return self._recognize_sync(
            image_bytes,
            preprocess,
            lang or self.lang,
            config or self.config
        )
    
    def is_available(self) -> bool:
        """检查OCR是否可用"""
        return self._check_tesseract_available()
    
    def get_supported_languages(self) -> list:
        """
        获取支持的语言列表
        
        Returns:
            支持的语言代码列表
        """
        if not self._check_tesseract_available():
            return []
        
        try:
            import pytesseract
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            
            langs = pytesseract.get_languages()
            return langs
        except Exception as e:
            logger.error(f"获取支持语言失败: {e}")
            return []


# 全局OCR实例
_global_local_ocr: Optional[LocalOCR] = None


def get_local_ocr(
    tesseract_cmd: Optional[str] = None,
    lang: str = "eng+chi_sim"
) -> LocalOCR:
    """
    获取全局本地OCR实例
    
    Args:
        tesseract_cmd: Tesseract可执行文件路径
        lang: 语言代码
        
    Returns:
        LocalOCR实例
    """
    global _global_local_ocr
    
    if _global_local_ocr is None:
        _global_local_ocr = LocalOCR(
            tesseract_cmd=tesseract_cmd,
            lang=lang
        )
    
    return _global_local_ocr
