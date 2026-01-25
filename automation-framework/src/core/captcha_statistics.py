"""
验证码统计模块 - 统计验证码类型和处理结果
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import logging

from .captcha_types import CaptchaType

logger = logging.getLogger(__name__)


class CaptchaStatistics:
    """验证码统计器"""
    
    def __init__(self):
        """初始化统计器"""
        self.type_counts: Dict[str, int] = defaultdict(int)  # 验证码类型计数
        self.success_counts: Dict[str, int] = defaultdict(int)  # 成功次数
        self.failure_counts: Dict[str, int] = defaultdict(int)  # 失败次数
        self.method_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))  # 处理方法计数
        self.total_count = 0  # 总验证码数量
    
    def record_captcha(
        self,
        captcha_type: CaptchaType,
        success: bool,
        method: Optional[str] = None
    ) -> None:
        """
        记录验证码处理结果
        
        Args:
            captcha_type: 验证码类型
            success: 是否成功
            method: 处理方法（如"vision", "ocr", "manual"）
        """
        type_str = captcha_type.value
        self.type_counts[type_str] += 1
        self.total_count += 1
        
        if success:
            self.success_counts[type_str] += 1
        else:
            self.failure_counts[type_str] += 1
        
        if method:
            self.method_counts[type_str][method] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total": self.total_count,
            "by_type": {},
            "success_rate": {},
            "method_distribution": {}
        }
        
        for captcha_type in CaptchaType:
            type_str = captcha_type.value
            count = self.type_counts[type_str]
            success = self.success_counts[type_str]
            failure = self.failure_counts[type_str]
            
            if count > 0:
                stats["by_type"][type_str] = {
                    "count": count,
                    "success": success,
                    "failure": failure,
                    "success_rate": success / count if count > 0 else 0
                }
                
                stats["success_rate"][type_str] = success / count if count > 0 else 0
                
                stats["method_distribution"][type_str] = dict(self.method_counts[type_str])
        
        return stats
    
    def get_type_distribution(self) -> Dict[str, float]:
        """
        获取验证码类型分布
        
        Returns:
            类型分布字典（百分比）
        """
        if self.total_count == 0:
            return {}
        
        distribution = {}
        for type_str, count in self.type_counts.items():
            distribution[type_str] = count / self.total_count
        
        return distribution
    
    def reset(self) -> None:
        """重置统计"""
        self.type_counts.clear()
        self.success_counts.clear()
        self.failure_counts.clear()
        self.method_counts.clear()
        self.total_count = 0


# 全局统计器实例
_global_statistics = CaptchaStatistics()


def get_global_statistics() -> CaptchaStatistics:
    """获取全局统计器实例"""
    return _global_statistics
