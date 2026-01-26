"""
配置加密工具
用于加密和解密敏感配置信息
"""
import os
import base64
from cryptography.fernet import Fernet
from exceptions.exception import ServiceException


class ConfigCrypto:
    """配置加密工具类"""
    
    @staticmethod
    def get_key() -> bytes:
        """
        获取加密密钥（从环境变量）
        
        :return: 加密密钥
        :raises ServiceException: 未设置加密密钥
        """
        key = os.getenv('CONFIG_ENCRYPTION_KEY')
        if not key:
            raise ServiceException(message='未设置CONFIG_ENCRYPTION_KEY环境变量，请先生成并配置加密密钥')
        return key.encode()
    
    @staticmethod
    def encrypt(data: str) -> str:
        """
        加密配置数据
        
        :param data: 原始数据
        :return: 加密后的数据（Base64编码）
        """
        try:
            f = Fernet(ConfigCrypto.get_key())
            encrypted = f.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            raise ServiceException(message=f'配置加密失败: {str(e)}')
    
    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """
        解密配置数据
        
        :param encrypted_data: 加密的数据（Base64编码）
        :return: 原始数据
        """
        try:
            f = Fernet(ConfigCrypto.get_key())
            decrypted = f.decrypt(base64.b64decode(encrypted_data))
            return decrypted.decode()
        except Exception as e:
            raise ServiceException(message=f'配置解密失败: {str(e)}')
    
    @staticmethod
    def encrypt_dict(data: dict, sensitive_keys: list = None) -> dict:
        """
        加密字典中的敏感字段
        
        :param data: 原始字典
        :param sensitive_keys: 需要加密的字段列表
        :return: 加密后的字典
        """
        if sensitive_keys is None:
            sensitive_keys = [
                'api_key', 'private_key', 'alipay_public_key',
                'api_v3_key', 'app_secret', 'secret_key',
                'private_cert_path', 'cert_serial_no'
            ]
        
        encrypted_data = data.copy()
        for key in sensitive_keys:
            if key in encrypted_data and encrypted_data[key]:
                encrypted_data[key] = ConfigCrypto.encrypt(str(encrypted_data[key]))
                encrypted_data[f'{key}_encrypted'] = True  # 标记已加密
        
        return encrypted_data
    
    @staticmethod
    def decrypt_dict(data: dict, sensitive_keys: list = None) -> dict:
        """
        解密字典中的敏感字段
        
        :param data: 加密的字典
        :param sensitive_keys: 需要解密的字段列表
        :return: 解密后的字典
        """
        if sensitive_keys is None:
            sensitive_keys = [
                'api_key', 'private_key', 'alipay_public_key',
                'api_v3_key', 'app_secret', 'secret_key',
                'private_cert_path', 'cert_serial_no'
            ]
        
        decrypted_data = data.copy()
        for key in sensitive_keys:
            # 检查是否已加密
            if f'{key}_encrypted' in decrypted_data and decrypted_data[f'{key}_encrypted']:
                if key in decrypted_data and decrypted_data[key]:
                    decrypted_data[key] = ConfigCrypto.decrypt(decrypted_data[key])
                    del decrypted_data[f'{key}_encrypted']  # 移除加密标记
        
        return decrypted_data
