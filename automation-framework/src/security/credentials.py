"""
凭证管理 - 安全存储和管理敏感凭证
"""
import keyring
from typing import Optional, Dict, List
from cryptography.fernet import Fernet
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    凭证管理器 - 集成系统密钥链和加密存储
    """
    
    def __init__(
        self,
        service_name: str = "automation-framework",
        encryption_key: Optional[bytes] = None
    ):
        self.service_name = service_name
        
        # 初始化加密
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # 生成或加载加密密钥
            self.cipher = self._init_cipher()
    
    def _init_cipher(self) -> Fernet:
        """
        初始化加密器
        
        Returns:
            Fernet加密器
        """
        # 尝试从系统密钥链加载密钥
        try:
            key = keyring.get_password(self.service_name, "encryption_key")
            if key:
                return Fernet(key.encode())
        except Exception as e:
            logger.warning(f"Failed to load encryption key from keyring: {e}")
        
        # 生成新密钥
        key = Fernet.generate_key()
        
        # 保存到系统密钥链
        try:
            keyring.set_password(
                self.service_name,
                "encryption_key",
                key.decode()
            )
        except Exception as e:
            logger.warning(f"Failed to save encryption key to keyring: {e}")
        
        return Fernet(key)
    
    def store_credential(
        self,
        username: str,
        password: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        存储凭证
        
        Args:
            username: 用户名
            password: 密码
            metadata: 元数据（如URL、描述等）
            
        Returns:
            是否成功
        """
        try:
            # 加密密码
            encrypted_password = self.encrypt(password)
            
            # 构建凭证数据
            credential_data = {
                "password": encrypted_password,
                "metadata": metadata or {}
            }
            
            # 存储到系统密钥链
            keyring.set_password(
                self.service_name,
                username,
                json.dumps(credential_data)
            )
            
            logger.info(f"Stored credential for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credential: {e}")
            return False
    
    def get_credential(self, username: str) -> Optional[Dict]:
        """
        获取凭证
        
        Args:
            username: 用户名
            
        Returns:
            凭证字典（包含password和metadata）
        """
        try:
            # 从系统密钥链获取
            credential_json = keyring.get_password(self.service_name, username)
            
            if not credential_json:
                return None
            
            # 解析凭证数据
            credential_data = json.loads(credential_json)
            
            # 解密密码
            encrypted_password = credential_data["password"]
            password = self.decrypt(encrypted_password)
            
            return {
                "username": username,
                "password": password,
                "metadata": credential_data.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get credential: {e}")
            return None
    
    def delete_credential(self, username: str) -> bool:
        """
        删除凭证
        
        Args:
            username: 用户名
            
        Returns:
            是否成功
        """
        try:
            keyring.delete_password(self.service_name, username)
            logger.info(f"Deleted credential for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete credential: {e}")
            return False
    
    def list_credentials(self) -> List[str]:
        """
        列出所有凭证
        
        Returns:
            用户名列表
        """
        # 注意：keyring库不提供列出所有凭证的功能
        # 这里返回空列表，实际使用时需要维护一个索引
        logger.warning("list_credentials not fully implemented")
        return []
    
    def encrypt(self, data: str) -> str:
        """
        加密数据
        
        Args:
            data: 明文数据
            
        Returns:
            加密后的数据（Base64编码）
        """
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密数据（Base64编码）
            
        Returns:
            明文数据
        """
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def update_credential(
        self,
        username: str,
        password: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        更新凭证
        
        Args:
            username: 用户名
            password: 新密码（可选）
            metadata: 新元数据（可选）
            
        Returns:
            是否成功
        """
        # 获取现有凭证
        existing = self.get_credential(username)
        if not existing:
            return False
        
        # 更新字段
        new_password = password if password else existing["password"]
        new_metadata = metadata if metadata else existing["metadata"]
        
        # 存储更新后的凭证
        return self.store_credential(username, new_password, new_metadata)
