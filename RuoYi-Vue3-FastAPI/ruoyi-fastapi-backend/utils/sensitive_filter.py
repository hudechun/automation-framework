"""
敏感信息脱敏工具
用于日志和异常信息的脱敏处理
"""
import re
import logging
from typing import Any, Dict, List


class SensitiveDataFilter(logging.Filter):
    """日志敏感数据过滤器"""
    
    def filter(self, record):
        """过滤日志记录中的敏感信息"""
        if hasattr(record, 'msg'):
            record.msg = self._mask_sensitive(str(record.msg))
        
        # 处理args中的敏感信息
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = mask_sensitive_data(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    mask_sensitive_data(arg) if isinstance(arg, dict) else arg
                    for arg in record.args
                )
        
        return True
    
    def _mask_sensitive(self, text: str) -> str:
        """脱敏文本中的敏感信息"""
        # 脱敏API Key (sk_test_xxx, sk_live_xxx)
        text = re.sub(r'sk_(test|live)_[a-zA-Z0-9]+', 'sk_***MASKED***', text)
        
        # 脱敏App ID (app_xxx)
        text = re.sub(r'app_[a-zA-Z0-9]{16,}', 'app_***MASKED***', text)
        
        # 脱敏手机号
        text = re.sub(r'1[3-9]\d{9}', '***MASKED***', text)
        
        # 脱敏身份证号
        text = re.sub(r'\d{17}[\dXx]', '***MASKED***', text)
        
        # 脱敏邮箱
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '***@***.***', text)
        
        # 脱敏银行卡号
        text = re.sub(r'\d{16,19}', '****CARD****', text)
        
        # 脱敏密钥关键词
        sensitive_patterns = [
            (r'api_key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'api_key: ***MASKED***'),
            (r'private_key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'private_key: ***MASKED***'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'secret: ***MASKED***'),
            (r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'password: ***MASKED***'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'token: ***MASKED***'),
        ]
        
        for pattern, replacement in sensitive_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text


def mask_sensitive_data(data: Any) -> Any:
    """
    脱敏敏感数据（递归处理）
    
    :param data: 原始数据
    :return: 脱敏后的数据
    """
    if isinstance(data, dict):
        return _mask_dict(data)
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(mask_sensitive_data(item) for item in data)
    else:
        return data


def _mask_dict(data: Dict) -> Dict:
    """脱敏字典数据"""
    masked = {}
    
    # 需要脱敏的键名
    sensitive_keys = [
        'api_key', 'private_key', 'alipay_public_key', 'app_secret',
        'api_v3_key', 'password', 'secret', 'token', 'credential',
        'sign', 'signature', 'cert_serial_no', 'private_cert_path',
        'access_token', 'refresh_token', 'session_key'
    ]
    
    for key, value in data.items():
        # 检查键名是否包含敏感词
        if any(s in key.lower() for s in sensitive_keys):
            masked[key] = '***MASKED***'
        elif isinstance(value, (dict, list, tuple)):
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value
    
    return masked


def mask_exception_message(message: str) -> str:
    """
    脱敏异常信息
    
    :param message: 原始异常信息
    :return: 脱敏后的异常信息
    """
    # 移除文件路径
    message = re.sub(r'[A-Za-z]:\\[^"\'<>\|\s]+', '***PATH***', message)
    message = re.sub(r'/[^"\'<>\|\s]+', '***PATH***', message)
    
    # 移除IP地址
    message = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '***IP***', message)
    
    # 移除端口号
    message = re.sub(r':\d{2,5}(?=\s|$|/)', ':***PORT***', message)
    
    # 使用日志过滤器的脱敏逻辑
    filter_instance = SensitiveDataFilter()
    return filter_instance._mask_sensitive(message)


def get_safe_error_message(error: Exception, default_message: str = '操作失败，请稍后重试') -> str:
    """
    获取安全的错误信息（用于返回给用户）
    
    :param error: 异常对象
    :param default_message: 默认错误信息
    :return: 安全的错误信息
    """
    # 对于ServiceException，可以返回原始消息（业务异常）
    from exceptions.exception import ServiceException
    if isinstance(error, ServiceException):
        return str(error)
    
    # 对于其他异常，返回通用错误信息
    return default_message
