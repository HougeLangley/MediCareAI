"""
AI Model Configuration Service | AI模型配置服务

Manages AI model configurations with encryption and database storage.
管理AI模型配置，支持加密和数据库存储。
"""
import os
import base64
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from cryptography.fernet import Fernet

from app.models.ai_model_config import AIModelConfiguration

logger = logging.getLogger(__name__)

# Default master key for this project
DEFAULT_MASTER_KEY = "zhanxiaopi"

def derive_fernet_key(master_key: str) -> bytes:
    """Derive a valid Fernet key from a string | 从字符串派生有效的Fernet密钥"""
    return base64.urlsafe_b64encode(hashlib.sha256(master_key.encode()).digest())


class AIModelConfigService:
    """
    AI Model Configuration Service | AI模型配置服务
    
    Provides CRUD operations for AI model configurations with encryption.
    提供AI模型配置的增删改查操作，支持加密存储。
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher | 获取或创建加密器"""
        key_str = os.getenv("API_KEY_MASTER_KEY") or DEFAULT_MASTER_KEY
        if not os.getenv("API_KEY_MASTER_KEY"):
            logger.info("Using default API_KEY_MASTER_KEY for MediCare_AI")
        
        try:
            # Derive proper Fernet key from string
            key = derive_fernet_key(key_str)
            return Fernet(key)
        except Exception as e:
            # If key derivation fails, use default
            logger.error(f"Invalid API_KEY_MASTER_KEY: {e}, using default key")
            return Fernet(derive_fernet_key(DEFAULT_MASTER_KEY))
    
    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt API key | 加密API密钥"""
        return self._cipher.encrypt(api_key.encode()).decode()
    
    def _decrypt_key(self, encrypted_key: str) -> Optional[str]:
        """Decrypt API key | 解密API密钥
        
        Returns None if decryption fails (e.g., wrong encryption key).
        """
        try:
            return self._cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {str(e)}")
            return None
    
    async def get_config(self, model_type: str) -> Optional[AIModelConfiguration]:
        """
        Get configuration for a model type | 获取指定类型的模型配置
        
        Args:
            model_type: Model type (diagnosis, mineru, embedding)
            
        Returns:
            AIModelConfiguration or None
        """
        result = await self.db.execute(
            select(AIModelConfiguration).where(
                AIModelConfiguration.model_type == model_type
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_configs(self) -> Dict[str, AIModelConfiguration]:
        """
        Get all model configurations | 获取所有模型配置
        
        Returns:
            Dictionary mapping model_type to configuration
        """
        result = await self.db.execute(select(AIModelConfiguration))
        configs = result.scalars().all()
        return {config.model_type: config for config in configs}
    
    def _update_env_file(self, model_type: str, api_url: str, api_key: str, model_id: str) -> bool:
        """
        Update .env file with new configuration | 更新.env文件
        
        Args:
            model_type: Model type identifier
            api_url: API endpoint URL
            api_key: API key
            model_id: Model identifier
            
        Returns:
            True if updated successfully
        """
        try:
            # Find .env file path
            env_paths = [
                "/app/.env",  # Docker container path
                os.path.join(os.getcwd(), ".env"),  # Current working directory
                os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"),  # Relative to service
            ]
            
            env_file = None
            for path in env_paths:
                if os.path.exists(path):
                    env_file = path
                    break
            
            if not env_file:
                logger.warning("Could not find .env file to update")
                return False
            
            # Map model_type to environment variable names
            env_mappings = {
                "diagnosis": {
                    "AI_API_URL": api_url,
                    "AI_API_KEY": api_key,
                    "AI_MODEL_ID": model_id
                },
                "mineru": {
                    "MINERU_TOKEN": api_key
                },
                "embedding": {
                    "EMBEDDING_API_URL": api_url,
                    "EMBEDDING_API_KEY": api_key,
                    "EMBEDDING_MODEL_ID": model_id
                }
            }
            
            updates = env_mappings.get(model_type)
            if not updates:
                logger.warning(f"No .env mapping for model type: {model_type}")
                return False
            
            # Read current .env content
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update each variable
            for key, value in updates.items():
                # Escape special characters for regex
                escaped_key = key.replace('$', '\\$')
                
                # Check if variable already exists
                pattern = f"^{escaped_key}=.*$"
                import re
                if re.search(pattern, content, re.MULTILINE):
                    # Update existing variable
                    content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
                    logger.info(f"Updated {key} in .env file")
                else:
                    # Add new variable
                    content += f"\n{key}={value}\n"
                    logger.info(f"Added {key} to .env file")
            
            # Write updated content back
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Also update current process environment
            for key, value in updates.items():
                os.environ[key] = value
            
            logger.info(f"Successfully updated .env file for {model_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update .env file: {str(e)}")
            return False

    async def save_config(
        self,
        model_type: str,
        model_name: str,
        api_url: str,
        api_key: str,
        model_id: str,
        enabled: bool = True,
        config_metadata: Optional[Dict[str, Any]] = None
    ) -> AIModelConfiguration:
        """
        Save or update model configuration | 保存或更新模型配置
        
        Args:
            model_type: Model type identifier
            model_name: Display name
            api_url: API endpoint URL
            api_key: API key (will be encrypted)
            model_id: Model identifier
            enabled: Whether the model is enabled
            config_metadata: Additional configuration metadata
            
        Returns:
            Saved AIModelConfiguration
        """
        # Check if config exists
        existing = await self.get_config(model_type)
        
        encrypted_key = self._encrypt_key(api_key)
        
        if existing:
            # Update existing
            existing.model_name = model_name
            existing.api_url = api_url
            existing.api_key_encrypted = encrypted_key
            existing.model_id = model_id
            existing.enabled = enabled
            if config_metadata:
                existing.config_metadata = config_metadata
            existing.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(existing)
            logger.info(f"Updated AI model configuration: {model_type}")
            
            # Update .env file
            self._update_env_file(model_type, api_url, api_key, model_id)
            
            return existing
        else:
            # Create new
            config = AIModelConfiguration(
                model_type=model_type,
                model_name=model_name,
                api_url=api_url,
                api_key_encrypted=encrypted_key,
                model_id=model_id,
                enabled=enabled,
                config_metadata=config_metadata or {}
            )
            self.db.add(config)
            await self.db.commit()
            await self.db.refresh(config)
            logger.info(f"Created AI model configuration: {model_type}")
            
            # Update .env file
            self._update_env_file(model_type, api_url, api_key, model_id)
            
            return config
    
    async def update_test_status(
        self,
        model_type: str,
        test_status: str,
        latency_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update test status for a model | 更新模型的测试状态
        
        Args:
            model_type: Model type identifier
            test_status: Test status (success, failed)
            latency_ms: Test latency in milliseconds
            error_message: Error message if test failed
            
        Returns:
            True if updated successfully
        """
        config = await self.get_config(model_type)
        if not config:
            return False
        
        config.test_status = test_status
        config.last_tested = datetime.utcnow()
        config.latency_ms = str(latency_ms) if latency_ms else None
        config.error_message = error_message
        
        await self.db.commit()
        return True
    
    async def get_config_with_decrypted_key(
        self,
        model_type: str,
        fallback_to_env: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get configuration with decrypted API key | 获取配置（包含解密的API密钥）
        
        Args:
            model_type: Model type identifier
            fallback_to_env: Whether to fallback to environment variables if no DB config
            
        Returns:
            Configuration dictionary or None
        """
        config = await self.get_config(model_type)
        
        if config:
            # Try to decrypt the API key
            decrypted_key = self._decrypt_key(config.api_key_encrypted)
            
            # If decryption failed and fallback is enabled, use environment variables
            if decrypted_key is None and fallback_to_env:
                logger.warning(f"Failed to decrypt API key for {model_type}, falling back to environment variables")
                env_mappings = {
                    "diagnosis": {
                        "api_url": os.getenv("AI_API_URL", ""),
                        "api_key": os.getenv("AI_API_KEY", ""),
                        "model_id": os.getenv("AI_MODEL_ID", ""),
                        "model_name": "诊断AI模型"
                    },
                    "mineru": {
                        "api_url": os.getenv("MINERU_API_URL", "https://mineru.com/api"),
                        "api_key": os.getenv("MINERU_TOKEN", ""),
                        "model_id": "mineru-default",
                        "model_name": "文档提取 (MinerU)"
                    },
                    "embedding": {
                        "api_url": os.getenv("EMBEDDING_API_URL", ""),
                        "api_key": os.getenv("EMBEDDING_API_KEY", ""),
                        "model_id": os.getenv("EMBEDDING_MODEL_ID", ""),
                        "model_name": "向量嵌入模型"
                    }
                }
                env_config = env_mappings.get(model_type)
                if env_config and env_config["api_url"] and env_config["api_key"]:
                    return {
                        "model_type": model_type,
                        "model_name": env_config["model_name"],
                        "api_url": env_config["api_url"],
                        "api_key": env_config["api_key"],
                        "model_id": env_config["model_id"],
                        "enabled": True,
                        "config_metadata": {},
                        "last_tested": config.last_tested,
                        "test_status": config.test_status,
                        "latency_ms": config.latency_ms,
                        "error_message": config.error_message,
                        "source": "environment"
                    }
            
            return {
                "model_type": config.model_type,
                "model_name": config.model_name,
                "api_url": config.api_url,
                "api_key": decrypted_key or "",
                "model_id": config.model_id,
                "enabled": config.enabled,
                "config_metadata": config.config_metadata,
                "last_tested": config.last_tested,
                "test_status": config.test_status,
                "latency_ms": config.latency_ms,
                "error_message": config.error_message,
                "source": "database"
            }
        
        if fallback_to_env:
            # Fallback to environment variables
            env_mappings = {
                "diagnosis": {
                    "api_url": os.getenv("AI_API_URL", ""),
                    "api_key": os.getenv("AI_API_KEY", ""),
                    "model_id": os.getenv("AI_MODEL_ID", ""),
                    "model_name": "诊断AI模型"
                },
                "mineru": {
                    "api_url": os.getenv("MINERU_API_URL", "https://mineru.com/api"),
                    "api_key": os.getenv("MINERU_TOKEN", ""),
                    "model_id": "mineru-default",
                    "model_name": "文档提取 (MinerU)"
                },
                "embedding": {
                    "api_url": os.getenv("EMBEDDING_API_URL", ""),
                    "api_key": os.getenv("EMBEDDING_API_KEY", ""),
                    "model_id": os.getenv("EMBEDDING_MODEL_ID", ""),
                    "model_name": "向量嵌入模型"
                }
            }
            
            env_config = env_mappings.get(model_type)
            if env_config and env_config["api_url"] and env_config["api_key"]:
                return {
                    "model_type": model_type,
                    "model_name": env_config["model_name"],
                    "api_url": env_config["api_url"],
                    "api_key": env_config["api_key"],
                    "model_id": env_config["model_id"],
                    "enabled": True,
                    "config_metadata": {},
                    "source": "environment"
                }
        
        return None
    
    async def delete_config(self, model_type: str) -> bool:
        """
        Delete a model configuration | 删除模型配置
        
        Args:
            model_type: Model type identifier
            
        Returns:
            True if deleted successfully
        """
        config = await self.get_config(model_type)
        if not config:
            return False
        
        await self.db.delete(config)
        await self.db.commit()
        logger.info(f"Deleted AI model configuration: {model_type}")
        return True


# Convenience function for dependency injection
def get_ai_model_config_service(db: AsyncSession) -> AIModelConfigService:
    """Get AI model config service instance | 获取AI模型配置服务实例"""
    return AIModelConfigService(db)
