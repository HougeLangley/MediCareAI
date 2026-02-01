from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql+asyncpg://medicare_user:password@medicare_postgres:5432/medicare_ai"

    # Redis配置
    redis_url: str = "redis://:password@medicare_redis:6379/0"
    redis_password: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow"
    }
    
    # JWT配置
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # MinerU API配置
    mineru_token: str = ""
    mineru_api_url: str = "https://mineru.net/api/v4/extract/task"
    
    # AI API配置
    ai_api_key: str = ""
    ai_api_url: str = "http://172.30.66.203:8033/v1/"
    ai_model_id: str = "unsloth/GLM-4.7-Flash-GGUF:BF16"
    
    # 文件上传配置
    max_file_size: int = 200 * 1024 * 1024  # 200MB
    upload_path: str = "/app/uploads"
    
    # 安全配置
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # 应用配置
    debug: bool = False
    testing: bool = False
    log_level: str = "INFO"
    log_format: str = "json"
    
    # 分页配置
    default_page_size: int = 20
    max_page_size: int = 100


settings = Settings()