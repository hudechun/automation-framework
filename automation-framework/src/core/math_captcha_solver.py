"""
数学计算题验证码求解器
支持识别和计算数学表达式验证码，如 "6-9=?"、"3+5=?" 等
"""
import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class MathCaptchaSolver:
    """
    数学计算题验证码求解器
    
    支持的格式：
    - "6-9=?" -> -3
    - "3+5=?" -> 8
    - "2*4=?" -> 8
    - "10/2=?" -> 5
    - "6 - 9 = ?" -> -3 (支持空格)
    - "6-9=？" -> -3 (支持中文问号)
    """
    
    # 支持的运算符映射
    OPERATOR_MAP = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '×': lambda a, b: a * b,  # 中文乘号
        '/': lambda a, b: a / b if b != 0 else None,
        '÷': lambda a, b: a / b if b != 0 else None,  # 中文除号
    }
    
    @classmethod
    def is_math_captcha(cls, text: str) -> bool:
        """
        判断文本是否是数学计算题验证码
        
        Args:
            text: 验证码文本
            
        Returns:
            是否是数学计算题
        """
        if not text:
            return False
        
        # 清理文本：移除空格、等号、问号等
        cleaned = re.sub(r'[\s=？?]', '', text)
        
        # 匹配模式：数字 运算符 数字
        # 例如：6-9, 3+5, 2*4, 10/2
        pattern = r'^(\d+)([+\-*/×÷])(\d+)$'
        match = re.match(pattern, cleaned)
        
        return match is not None
    
    @classmethod
    def solve(cls, text: str) -> Optional[Tuple[int, str]]:
        """
        求解数学计算题验证码
        
        Args:
            text: 验证码文本，如 "6-9=?"、"3+5=?" 等
            
        Returns:
            (计算结果, 原始表达式) 元组，如果无法计算返回 None
            例如：(-3, "6-9=?")
        """
        if not text:
            return None
        
        try:
            # 清理文本：移除空格、等号、问号等
            cleaned = re.sub(r'[\s=？?]', '', text)
            
            # 匹配模式：数字 运算符 数字
            pattern = r'^(\d+)([+\-*/×÷])(\d+)$'
            match = re.match(pattern, cleaned)
            
            if not match:
                logger.debug(f"无法匹配数学表达式: {text}")
                return None
            
            num1_str, operator, num2_str = match.groups()
            num1 = int(num1_str)
            num2 = int(num2_str)
            
            # 获取计算函数
            calc_func = cls.OPERATOR_MAP.get(operator)
            if not calc_func:
                logger.warning(f"不支持的运算符: {operator}")
                return None
            
            # 计算结果
            result = calc_func(num1, num2)
            
            if result is None:
                logger.warning(f"计算结果为None（可能是除零错误）: {text}")
                return None
            
            # 转换为整数（如果是整数）
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            logger.info(f"数学计算题求解: {text} -> {result}")
            return (result, text)
            
        except ValueError as e:
            logger.error(f"解析数字失败: {e}, 文本: {text}")
            return None
        except Exception as e:
            logger.error(f"计算数学表达式失败: {e}, 文本: {text}")
            return None
    
    @classmethod
    def extract_and_solve(cls, text: str) -> Optional[str]:
        """
        从文本中提取数学表达式并求解，返回结果字符串
        
        Args:
            text: 可能包含数学表达式的文本
            
        Returns:
            计算结果字符串，如果无法计算返回 None
        """
        # 先尝试直接求解
        result = cls.solve(text)
        if result:
            return str(result[0])
        
        # 如果直接求解失败，尝试从文本中提取数学表达式
        # 匹配模式：数字 运算符 数字 = ?
        patterns = [
            r'(\d+)\s*([+\-*/×÷])\s*(\d+)\s*[=＝]\s*[？?]',  # 标准格式
            r'(\d+)\s*([+\-*/×÷])\s*(\d+)',  # 无等号和问号
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                num1_str, operator, num2_str = match.groups()
                expression = f"{num1_str}{operator}{num2_str}"
                result = cls.solve(expression)
                if result:
                    return str(result[0])
        
        return None
