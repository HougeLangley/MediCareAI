"""
AI Model Configuration Model | AI模型配置模型

Stores AI model configurations in database for dynamic management.
将AI模型配置存储在数据库中以实现动态管理。
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base


class AIModelConfiguration(Base):
    """
    AI Model Configuration | AI模型配置
    
    Stores configuration for AI models with multi-provider support.
    存储AI模型配置，支持多提供商（云端和本地）。
    """
    __tablename__ = "ai_model_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Model identification | 模型标识
    model_type = Column(String(50), nullable=False, unique=True, index=True,
                       comment="Model type: diagnosis, mineru, embedding, oss")
    model_name = Column(String(255), nullable=False,
                       comment="Display name of the model")
    
    # Provider selection | 提供商选择
    provider = Column(String(50), nullable=False, default="custom",
                     comment="AI provider: openai, zhipu, kimi, deepseek, ollama, vllm, lmstudio, custom")
    
    # Configuration | 配置
    api_url = Column(String(500), nullable=False,
                    comment="API endpoint URL")
    api_key_encrypted = Column(Text, nullable=True,
                              comment="Encrypted API key (optional for local providers)")
    model_id = Column(String(255), nullable=False,
                     comment="Model identifier")
    enabled = Column(Boolean, default=True,
                    comment="Whether the model is enabled")
    
    # Additional settings | 额外设置
    config_metadata = Column(JSONB, default=dict,
                            comment="Additional configuration metadata including provider-specific settings")
    
    # Test status | 测试状态
    last_tested = Column(DateTime(timezone=True), nullable=True,
                        comment="Last test timestamp")
    test_status = Column(String(20), nullable=True,
                        comment="Last test status: success, failed")
    latency_ms = Column(String(50), nullable=True,
                       comment="Last test latency in milliseconds")
    error_message = Column(Text, nullable=True,
                          comment="Last error message if test failed")
    
    # Audit timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIModelConfiguration(model_type='{self.model_type}', enabled={self.enabled})>"
