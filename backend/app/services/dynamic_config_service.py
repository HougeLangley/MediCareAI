"""
Dynamic Configuration Service
Provides runtime configuration from database with environment fallback
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.ai_model_config import AIModelConfiguration
import base64
import hashlib
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Default master key for this project
DEFAULT_MASTER_KEY = "zhanxiaopi"


def derive_fernet_key(master_key: str) -> bytes:
    """Derive a valid Fernet key from a string"""
    return base64.urlsafe_b64encode(hashlib.sha256(master_key.encode()).digest())


def get_cipher() -> Fernet:
    """Get encryption cipher"""
    key_str = os.getenv("API_KEY_MASTER_KEY") or DEFAULT_MASTER_KEY
    try:
        key = derive_fernet_key(key_str)
        return Fernet(key)
    except Exception as e:
        logger.error(f"Invalid API_KEY_MASTER_KEY: {e}, using default key")
        return Fernet(derive_fernet_key(DEFAULT_MASTER_KEY))


def decrypt_key(encrypted_key: str) -> Optional[str]:
    """Decrypt API key"""
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_key.encode()).decode()
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {str(e)}")
        return None


class DynamicConfigService:
    """
    Dynamic Configuration Service
    
    Reads configuration from database (real-time) with environment fallback.
    This ensures admin updates are immediately effective without restart.
    """
    
    @staticmethod
    async def get_mineru_config(db: AsyncSession) -> Dict[str, str]:
        """
        Get MinerU configuration from database or environment
        
        Priority:
        1. Database (ai_model_config table) - if exists and enabled
        2. Environment variables (updated at runtime via os.environ)
        3. Settings object (startup values)
        
        Returns:
            Dict with 'api_url' and 'token'
        """
        # Try database first
        try:
            result = await db.execute(
                select(AIModelConfiguration).where(
                    AIModelConfiguration.model_type == "mineru"
                )
            )
            config = result.scalar_one_or_none()
            
            if config and config.enabled and config.api_key_encrypted:
                decrypted_key = decrypt_key(config.api_key_encrypted)
                if decrypted_key:
                    # Validate and correct API URL
                    api_url = config.api_url or "https://mineru.net/api/v4/extract/task"
                    
                    # Fix common URL mistakes
                    if api_url == "https://mineru.com/api" or api_url == "https://mineru.com/api/v4/extract/task":
                        logger.warning(f"⚠️ Invalid MinerU URL detected in DB: {api_url}, correcting to https://mineru.net/api/v4/extract/task")
                        api_url = "https://mineru.net/api/v4/extract/task"
                    
                    # Ensure URL ends with /v4/extract/task
                    if not api_url.endswith('/v4/extract/task'):
                        if 'mineru.net' in api_url or 'mineru.com' in api_url:
                            logger.warning(f"⚠️ MinerU URL may be incomplete: {api_url}, using default")
                            api_url = "https://mineru.net/api/v4/extract/task"
                    
                    logger.info(f"✅ Using MinerU config from database (URL: {api_url})")
                    return {
                        "api_url": api_url,
                        "token": decrypted_key,
                        "source": "database"
                    }
                else:
                    logger.warning("⚠️ Failed to decrypt MinerU key from database")
        except Exception as e:
            logger.error(f"Error reading MinerU config from database: {e}")
        
        # Try environment variables (updated at runtime)
        env_token = os.environ.get("MINERU_TOKEN", "")
        if env_token:
            logger.info("✅ Using MinerU config from environment variables")
            return {
                "api_url": os.environ.get("MINERU_API_URL", "https://mineru.net/api/v4/extract/task"),
                "token": env_token,
                "source": "environment"
            }
        
        # Fallback to settings (startup values)
        if settings.mineru_token:
            logger.info("✅ Using MinerU config from settings (startup)")
            return {
                "api_url": settings.mineru_api_url,
                "token": settings.mineru_token,
                "source": "settings"
            }
        
        logger.error("❌ No MinerU configuration found!")
        return {
            "api_url": "https://mineru.net/api/v4/extract/task",
            "token": "",
            "source": "none"
        }
    
    @staticmethod
    async def get_ai_config(db: AsyncSession) -> Dict[str, str]:
        """Get AI diagnosis configuration from database or environment"""
        try:
            result = await db.execute(
                select(AIModelConfiguration).where(
                    AIModelConfiguration.model_type == "diagnosis"
                )
            )
            config = result.scalar_one_or_none()
            
            if config and config.enabled and config.api_key_encrypted:
                decrypted_key = decrypt_key(config.api_key_encrypted)
                if decrypted_key:
                    return {
                        "api_url": config.api_url,
                        "api_key": decrypted_key,
                        "model_id": config.model_id,
                        "source": "database"
                    }
        except Exception as e:
            logger.error(f"Error reading AI config from database: {e}")
        
        # Fallback to environment/settings
        return {
            "api_url": os.environ.get("AI_API_URL") or settings.ai_api_url,
            "api_key": os.environ.get("AI_API_KEY") or settings.ai_api_key,
            "model_id": os.environ.get("AI_MODEL_ID") or settings.ai_model_id,
            "source": "environment"
        }
    
    @staticmethod
    async def get_embedding_config(db: AsyncSession) -> Dict[str, str]:
        """Get embedding configuration from database or environment"""
        try:
            result = await db.execute(
                select(AIModelConfiguration).where(
                    AIModelConfiguration.model_type == "embedding"
                )
            )
            config = result.scalar_one_or_none()
            
            if config and config.enabled and config.api_key_encrypted:
                decrypted_key = decrypt_key(config.api_key_encrypted)
                if decrypted_key:
                    return {
                        "api_url": config.api_url,
                        "api_key": decrypted_key,
                        "model_id": config.model_id,
                        "source": "database"
                    }
        except Exception as e:
            logger.error(f"Error reading embedding config from database: {e}")
        
        # Fallback to environment/settings
        return {
            "api_url": os.environ.get("EMBEDDING_API_URL") or settings.embedding_api_url,
            "api_key": os.environ.get("EMBEDDING_API_KEY") or settings.embedding_api_key,
            "model_id": os.environ.get("EMBEDDING_MODEL_ID") or settings.embedding_model_id,
            "source": "environment"
        }


# Simple non-async version for services that can't easily use async
def get_mineru_token_sync() -> str:
    """
    Synchronous version to get MinerU token.
    Priority: os.environ > settings
    
    Note: This doesn't check database (requires async).
    Use this for simple cases where DB access is not available.
    """
    # Check environment first (updated at runtime)
    token = os.environ.get("MINERU_TOKEN", "")
    if token:
        return token
    
    # Fallback to settings
    return settings.mineru_token


def get_mineru_api_url_sync() -> str:
    """Synchronous version to get MinerU API URL"""
    return os.environ.get("MINERU_API_URL") or settings.mineru_api_url
