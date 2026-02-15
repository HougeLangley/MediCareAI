"""
Security Utilities | 安全工具

Encryption and decryption utilities for sensitive data like API keys.
敏感数据（如API密钥）的加密和解密工具。
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

# Default master key for this project
DEFAULT_MASTER_KEY = "zhanxiaopi"

def derive_fernet_key(master_key: str) -> bytes:
    """Derive a valid Fernet key from a string | 从字符串派生有效的Fernet密钥"""
    return base64.urlsafe_b64encode(hashlib.sha256(master_key.encode()).digest())


class APIKeySecurity:
    """API key security manager | API密钥安全管理器"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize API key security manager.
        初始化API密钥安全管理器。
        
        Args:
            master_key: Master key for encryption. If None, uses environment variable.
        """
        self.master_key = master_key or os.getenv("API_KEY_MASTER_KEY") or DEFAULT_MASTER_KEY
        if not os.getenv("API_KEY_MASTER_KEY"):
            logger.info("Using default API_KEY_MASTER_KEY for MediCare_AI")
        
        # Derive encryption key from master key
        self.fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet cipher from master key | 从主密钥创建Fernet密码器"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'medicare_ai_salt',  # Fixed salt for consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt API key.
        加密API密钥。
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key (base64 encoded)
        """
        try:
            encrypted = self.fernet.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt API key: {str(e)}")
            raise
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt API key.
        解密API密钥。
        
        Args:
            encrypted_key: Encrypted API key (base64 encoded)
            
        Returns:
            Plain text API key
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {str(e)}")
            raise
    
    def mask_api_key(self, api_key: str, visible_chars: int = 4) -> str:
        """
        Mask API key for display.
        脱敏显示API密钥。
        
        Args:
            api_key: Plain text API key
            visible_chars: Number of characters to show at beginning and end
            
        Returns:
            Masked API key (e.g., "sk-****xxxx")
        """
        if not api_key or len(api_key) <= visible_chars * 2:
            return "*" * len(api_key) if api_key else ""
        
        prefix = api_key[:visible_chars]
        suffix = api_key[-visible_chars:]
        masked_length = len(api_key) - visible_chars * 2
        
        return f"{prefix}{'*' * masked_length}{suffix}"
    
    def validate_api_key_format(self, api_key: str, key_type: str = "openai") -> bool:
        """
        Validate API key format.
        验证API密钥格式。
        
        Args:
            api_key: API key to validate
            key_type: Type of API key (openai, mineru, etc.)
            
        Returns:
            True if format is valid
        """
        if not api_key:
            return False
        
        if key_type == "openai":
            # OpenAI keys start with "sk-"
            return api_key.startswith("sk-") and len(api_key) >= 20
        elif key_type == "mineru":
            # MinerU tokens are typically UUID-like or longer strings
            return len(api_key) >= 10
        elif key_type == "qwen":
            # Qwen/Dashscope keys are typically longer strings
            return len(api_key) >= 10
        elif key_type == "generic":
            # Generic/local LLM (vLLM, Ollama, etc.) - minimal validation
            # Allow empty for local models without auth, or any key format
            return True
        else:
            # Generic validation
            return len(api_key) >= 10
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Create hash of API key for comparison without storing the key.
        创建API密钥哈希用于比较而不存储密钥。
        
        Args:
            api_key: API key to hash
            
        Returns:
            SHA-256 hash of the API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()


# Global instance
api_key_security = APIKeySecurity()


def encrypt_api_key(api_key: str) -> str:
    """Convenience function to encrypt API key | 加密API密钥的便捷函数"""
    return api_key_security.encrypt_api_key(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """Convenience function to decrypt API key | 解密API密钥的便捷函数"""
    return api_key_security.decrypt_api_key(encrypted_key)


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """Convenience function to mask API key | 脱敏API密钥的便捷函数"""
    return api_key_security.mask_api_key(api_key, visible_chars)


def validate_api_key_format(api_key: str, key_type: str = "openai") -> bool:
    """Convenience function to validate API key format | 验证API密钥格式的便捷函数"""
    return api_key_security.validate_api_key_format(api_key, key_type)


def hash_api_key(api_key: str) -> str:
    """Convenience function to hash API key | 哈希API密钥的便捷函数"""
    return api_key_security.hash_api_key(api_key)


# Simple base64 encoding for backward compatibility (less secure)
def simple_encode(data: str) -> str:
    """Simple base64 encoding (for backward compatibility) | 简单base64编码（向后兼容）"""
    return base64.b64encode(data.encode()).decode()


def simple_decode(encoded_data: str) -> str:
    """Simple base64 decoding (for backward compatibility) | 简单base64解码（向后兼容）"""
    return base64.b64decode(encoded_data.encode()).decode()