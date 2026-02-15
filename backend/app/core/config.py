from __future__ import annotations

import os
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the MediCare AI application."""
    
    database_url: str = "postgresql+asyncpg://medicare_user:password@medicare_postgres:5432/medicareai"
    redis_url: str = "redis://:password@medicare_redis:6379/0"
    redis_password: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow"
    }
    
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    mineru_token: str = ""
    mineru_api_url: str = "https://mineru.net/api/v4/extract/task"
    
    ai_api_key: str = ""
    ai_api_url: str = "http://172.30.66.203:8033/v1/"
    ai_model_id: str = "unsloth/GLM-4.7-Flash-GGUF:BF16"
    
    # Embedding model settings (Qwen)
    embedding_api_key: str = ""
    embedding_api_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_model_id: str = "text-embedding-v3"
    embedding_dimensions: int = 1024
    
    max_file_size: int = 200 * 1024 * 1024  # 200MB
    upload_path: str = "/app/uploads"
    
    # Public file URL for MinerU API access (optional fallback)
    # If set, will be used as fallback when external hosting services fail
    # Example: "http://your-server.com/api/v1/documents/file"
    public_file_url: Optional[str] = None
    
    # Alibaba Cloud OSS Configuration
    oss_access_key_id: Optional[str] = None
    oss_access_key_secret: Optional[str] = None
    oss_bucket: Optional[str] = None
    oss_endpoint: Optional[str] = None
    
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    debug: bool = False
    testing: bool = False
    log_level: str = "INFO"
    log_format: str = "json"
    
    default_page_size: int = 20
    max_page_size: int = 100
    
    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Encode password in database URL if needed."""
        if "@" in v and ":" in v.split("@")[0]:
            # URL might contain unencoded password
            parts = v.split("://")
            if len(parts) == 2:
                auth_part = parts[1].split("@")[0]
                if ":" in auth_part:
                    user, password = auth_part.split(":", 1)
                    encoded_password = quote_plus(password)
                    v = v.replace(f"{user}:{password}@", f"{user}:{encoded_password}@")
        return v
    
    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Encode password in redis URL if needed."""
        if "@" in v and ":" in v.split("@")[0]:
            # URL might contain unencoded password
            parts = v.split("://")
            if len(parts) == 2:
                auth_part = parts[1].split("@")[0]
                if ":" in auth_part and not auth_part.startswith(":"):
                    user, password = auth_part.split(":", 1)
                    encoded_password = quote_plus(password)
                    v = v.replace(f"{user}:{password}@", f"{user}:{encoded_password}@")
        return v


settings = Settings()