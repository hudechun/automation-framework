"""
自适应验证码处理策略
根据验证码场景自动调整处理方法和参数
"""
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
import logging
import time
import asyncio
from dataclasses import dataclass, field
from collections import defaultdict

from .captcha_types import CaptchaType
from .captcha_vision_recognizer import CaptchaVisionRecognizer
from .math_captcha_solver import MathCaptcha_solver

logger = logging.getLogger(__name__)


class StrategyPriority(Enum):
    """策略优先级"""
    HIGH = "high"      # 高优先级（成功率高的方法）
    MEDIUM = "medium"  # 中等优先级（默认方法）
    LOW = "low"        # 低优先级（备用方法）


@dataclass
class StrategyResult:
    """策略执行结果"""
    success: bool
    method: str
    confidence: float = 0.0
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyConfig:
    """策略配置"""
    max_attempts: int = 3  # 最大尝试次数
    confidence_threshold: float = 0.5  # 置信度阈值
    enable_fallback: bool = True  # 是否启用回退
    enable_learning: bool = True  # 是否启用学习
    adaptive_params: bool = True  # 是否自适应调整参数


class AdaptiveCaptchaStrategy:
    """
    自适应验证码处理策略管理器
    
    功能：
    1. 多策略尝试：按优先级尝试不同的处理方法
    2. 置信度评估：根据置信度选择最佳策略
    3. 历史学习：记录成功/失败，优先使用成功率高的方法
    4. 动态参数调整：根据验证码复杂度调整参数
    5. 自适应重试：根据错误类型调整重试策略
    """
    
    def __init__(
        self,
        vision_model_provider: Optional[str] = None,
        config: Optional[StrategyConfig] = None
    ):
        """
        初始化自适应策略管理器
        
        Args:
            vision_model_provider: 视觉模型提供商
            config: 策略配置
        """
        self.vision_model_provider = vision_model_provider
        self.config = config or StrategyConfig()
        self.vision_recognizer = CaptchaVisionRecognizer(vision_model_provider)
        
        # 历史记录：记录每种验证码类型和方法的成功率
        self._strategy_history: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(
            lambda: defaultdict(lambda: {
                "success_count": 0,
                "failure_count": 0,
                "total_time": 0.0,
                "avg_confidence": 0.0,
                "last_success_time": None
            })
        )
        
        # 策略优先级映射
        self._strategy_priority = {
            "vision_model": StrategyPriority.HIGH,
            "math_calculator": StrategyPriority.HIGH,
            "ocr": StrategyPriority.MEDIUM,
            "fallback": StrategyPriority.LOW,
            "manual": StrategyPriority.LOW,
        }
    
    def _calculate_strategy_score(
        self,
        captcha_type: str,
        method: str
    ) -> float:
        """
        计算策略得分（用于排序）
        
        得分 = 成功率 * 0.6 + 平均置信度 * 0.3 + 时效性 * 0.1
        
        Args:
            captcha_type: 验证码类型
            method: 处理方法
            
        Returns:
            策略得分（0-1）
        """
        history = self._strategy_history[captcha_type][method]
        success_count = history["success_count"]
        failure_count = history["failure_count"]
        total = success_count + failure_count
        
        if total == 0:
            # 新方法，使用默认优先级
            priority_weight = {
                StrategyPriority.HIGH: 0.7,
                StrategyPriority.MEDIUM: 0.5,
                StrategyPriority.LOW: 0.3
            }
            return priority_weight.get(self._strategy_priority.get(method, StrategyPriority.MEDIUM), 0.5)
        
        # 成功率
        success_rate = success_count / total if total > 0 else 0.0
        
        # 平均置信度
        avg_confidence = history["avg_confidence"]
        
        # 时效性（最近成功的时间权重）
        recency_score = 1.0
        if history["last_success_time"]:
            time_since_success = time.time() - history["last_success_time"]
            # 24小时内的成功记录给予更高权重
            recency_score = max(0.5, 1.0 - (time_since_success / 86400))
        
        # 综合得分
        score = success_rate * 0.6 + avg_confidence * 0.3 + recency_score * 0.1
        
        return score
    
    def _get_strategy_sequence(
        self,
        captcha_type: str,
        recognition_data: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        获取策略执行序列（按得分排序）
        
        Args:
            captcha_type: 验证码类型
            recognition_data: 视觉模型识别结果
            
        Returns:
            策略序列 [(method, params), ...]
        """
        strategies = []
        
        # 根据验证码类型和识别结果选择策略
        if captcha_type == "image":
            # 图形验证码策略序列
            if recognition_data:
                confidence = recognition_data.get("confidence", 0.0)
                data = recognition_data.get("data", {})
                text = data.get("text", "")
                
                # 检查是否是数学计算题
                if text and MathCaptchaSolver.is_math_captcha(text):
                    strategies.append(("math_calculator", {"text": text}))
                
                # 如果置信度高，优先使用视觉模型
                if confidence > self.config.confidence_threshold:
                    strategies.append(("vision_model", recognition_data))
            
            # OCR作为备用
            strategies.append(("ocr", {}))
            
            # 回退策略
            if self.config.enable_fallback:
                strategies.append(("fallback", {}))
        
        elif captcha_type == "slider":
            # 滑动验证码策略序列
            if recognition_data and recognition_data.get("confidence", 0.0) > self.config.confidence_threshold:
                strategies.append(("vision_model", recognition_data))
            else:
                strategies.append(("vision_model", recognition_data))  # 仍然尝试
                strategies.append(("fallback", {}))
        
        elif captcha_type in ["click", "puzzle", "rotate"]:
            # 点选/拼图/旋转验证码策略序列
            if recognition_data and recognition_data.get("confidence", 0.0) > self.config.confidence_threshold:
                strategies.append(("vision_model", recognition_data))
            else:
                strategies.append(("vision_model", recognition_data))
                strategies.append(("fallback", {}))
        
        else:
            # 其他类型使用回退策略
            strategies.append(("fallback", {}))
        
        # 如果启用学习，按历史得分排序
        if self.config.enable_learning:
            strategies.sort(
                key=lambda x: self._calculate_strategy_score(captcha_type, x[0]),
                reverse=True
            )
        
        return strategies
    
    def _record_strategy_result(
        self,
        captcha_type: str,
        method: str,
        result: StrategyResult
    ):
        """
        记录策略执行结果（用于学习）
        
        Args:
            captcha_type: 验证码类型
            method: 处理方法
            result: 执行结果
        """
        if not self.config.enable_learning:
            return
        
        history = self._strategy_history[captcha_type][method]
        
        if result.success:
            history["success_count"] += 1
            history["last_success_time"] = time.time()
        else:
            history["failure_count"] += 1
        
        # 更新平均置信度
        total_attempts = history["success_count"] + history["failure_count"]
        if total_attempts > 0:
            current_avg = history["avg_confidence"]
            history["avg_confidence"] = (
                (current_avg * (total_attempts - 1) + result.confidence) / total_attempts
            )
        
        # 更新平均执行时间
        history["total_time"] += result.execution_time
        if total_attempts > 0:
            history["avg_time"] = history["total_time"] / total_attempts
    
    def _adaptive_adjust_params(
        self,
        captcha_type: str,
        method: str,
        base_params: Dict[str, Any],
        recognition_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        自适应调整参数
        
        Args:
            captcha_type: 验证码类型
            method: 处理方法
            base_params: 基础参数
            recognition_data: 识别结果
            
        Returns:
            调整后的参数
        """
        if not self.config.adaptive_params:
            return base_params
        
        adjusted_params = base_params.copy()
        history = self._strategy_history[captcha_type][method]
        
        # 根据历史成功率调整参数
        success_count = history["success_count"]
        failure_count = history["failure_count"]
        total = success_count + failure_count
        
        if total > 0:
            success_rate = success_count / total
            
            # 如果成功率低，增加重试次数或调整超时时间
            if success_rate < 0.5:
                if "max_retries" in adjusted_params:
                    adjusted_params["max_retries"] = min(
                        adjusted_params.get("max_retries", 3) + 1,
                        5
                    )
                if "timeout" in adjusted_params:
                    adjusted_params["timeout"] = int(
                        adjusted_params.get("timeout", 60000) * 1.5
                    )
            
            # 根据置信度调整参数
            if recognition_data:
                confidence = recognition_data.get("confidence", 0.0)
                
                # 如果置信度低，使用更保守的参数
                if confidence < 0.6:
                    if "calibration_tests" in adjusted_params:
                        adjusted_params["calibration_tests"] = min(
                            adjusted_params.get("calibration_tests", 5) + 2,
                            10
                        )
        
        return adjusted_params
    
    async def execute_adaptive_strategy(
        self,
        captcha_type: str,
        recognition_data: Optional[Dict[str, Any]] = None,
        handler_func: Optional[callable] = None,
        **kwargs
    ) -> StrategyResult:
        """
        执行自适应策略
        
        Args:
            captcha_type: 验证码类型
            recognition_data: 视觉模型识别结果
            handler_func: 处理函数（接受method和params，返回处理结果）
            **kwargs: 额外参数
            
        Returns:
            策略执行结果
        """
        # 获取策略序列
        strategies = self._get_strategy_sequence(captcha_type, recognition_data)
        
        last_error = None
        
        for attempt in range(self.config.max_attempts):
            for method, params in strategies:
                try:
                    # 自适应调整参数
                    adjusted_params = self._adaptive_adjust_params(
                        captcha_type, method, params, recognition_data
                    )
                    
                    # 合并额外参数
                    final_params = {**adjusted_params, **kwargs}
                    
                    # 执行策略
                    start_time = time.time()
                    
                    if handler_func:
                        result = await handler_func(method, final_params)
                    else:
                        result = await self._default_handler(method, final_params)
                    
                    execution_time = time.time() - start_time
                    
                    # 判断是否成功
                    success = result.get("success", False) if isinstance(result, dict) else bool(result)
                    confidence = result.get("confidence", 0.0) if isinstance(result, dict) else 0.0
                    
                    strategy_result = StrategyResult(
                        success=success,
                        method=method,
                        confidence=confidence,
                        execution_time=execution_time,
                        metadata=result if isinstance(result, dict) else {}
                    )
                    
                    # 记录结果
                    self._record_strategy_result(captcha_type, method, strategy_result)
                    
                    if success:
                        logger.info(
                            f"自适应策略成功: {method} (置信度: {confidence:.2f}, "
                            f"耗时: {execution_time:.2f}s, 尝试: {attempt + 1})"
                        )
                        return strategy_result
                    else:
                        logger.warning(
                            f"策略 {method} 失败，尝试下一个策略 (尝试: {attempt + 1})"
                        )
                        last_error = result.get("error", "Unknown error") if isinstance(result, dict) else "Failed"
                
                except Exception as e:
                    logger.error(f"策略 {method} 执行异常: {e}")
                    last_error = str(e)
                    continue
            
            # 如果所有策略都失败，等待后重试
            if attempt < self.config.max_attempts - 1:
                wait_time = (attempt + 1) * 0.5  # 递增等待时间
                logger.info(f"所有策略失败，等待 {wait_time:.1f}s 后重试...")
                await asyncio.sleep(wait_time)
        
        # 所有策略都失败
        logger.error(f"所有自适应策略都失败 (尝试: {self.config.max_attempts} 次)")
        return StrategyResult(
            success=False,
            method="all_failed",
            error=last_error or "All strategies failed"
        )
    
    async def _default_handler(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        默认处理函数（占位符）
        
        Args:
            method: 处理方法
            params: 参数
            
        Returns:
            处理结果
        """
        # 这里应该调用实际的处理函数
        # 实际使用时，应该通过handler_func传入
        return {
            "success": False,
            "error": "No handler function provided"
        }
    
    def get_best_strategy(
        self,
        captcha_type: str
    ) -> Optional[Tuple[str, float]]:
        """
        获取最佳策略（用于查询）
        
        Args:
            captcha_type: 验证码类型
            
        Returns:
            (方法名, 得分) 元组，如果没有历史返回None
        """
        if captcha_type not in self._strategy_history:
            return None
        
        strategies = self._strategy_history[captcha_type]
        if not strategies:
            return None
        
        best_method = max(
            strategies.keys(),
            key=lambda m: self._calculate_strategy_score(captcha_type, m)
        )
        best_score = self._calculate_strategy_score(captcha_type, best_method)
        
        return (best_method, best_score)
    
    def get_strategy_statistics(
        self,
        captcha_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取策略统计信息
        
        Args:
            captcha_type: 验证码类型（如果为None，返回所有类型）
            
        Returns:
            统计信息
        """
        if captcha_type:
            type_history = self._strategy_history.get(captcha_type, {})
            return {
                captcha_type: {
                    method: {
                        "success_rate": (
                            h["success_count"] / (h["success_count"] + h["failure_count"])
                            if (h["success_count"] + h["failure_count"]) > 0 else 0.0
                        ),
                        "avg_confidence": h["avg_confidence"],
                        "avg_time": h.get("avg_time", 0.0),
                        "total_attempts": h["success_count"] + h["failure_count"],
                        **h
                    }
                    for method, h in type_history.items()
                }
            }
        else:
            return {
                ct: {
                    method: {
                        "success_rate": (
                            h["success_count"] / (h["success_count"] + h["failure_count"])
                            if (h["success_count"] + h["failure_count"]) > 0 else 0.0
                        ),
                        "avg_confidence": h["avg_confidence"],
                        "avg_time": h.get("avg_time", 0.0),
                        "total_attempts": h["success_count"] + h["failure_count"],
                    }
                    for method, h in methods.items()
                }
                for ct, methods in self._strategy_history.items()
            }
    
    def reset_statistics(self, captcha_type: Optional[str] = None):
        """
        重置统计信息
        
        Args:
            captcha_type: 验证码类型（如果为None，重置所有类型）
        """
        if captcha_type:
            self._strategy_history.pop(captcha_type, None)
        else:
            self._strategy_history.clear()
        logger.info(f"已重置统计信息: {captcha_type or 'all'}")
