"""
Vector Embedding Service - RAG Support | 向量嵌入服务 - RAG支持
Manages vector model configurations and generates embeddings for RAG.

Features:
- Vector model configuration management (CRUD)
- Connection testing for embedding models
- Text embedding generation
- Batch processing support
- Compatible with OpenAI API format

支持：
- 向量模型配置管理
- 连接测试
- 文本嵌入生成
- 批量处理
- OpenAI API兼容
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from types import SimpleNamespace
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.models import VectorEmbeddingConfig
from app.core.config import settings
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class VectorEmbeddingService:
    """
    Vector Embedding Service / 向量嵌入服务
    
    Manages embedding model configurations and generates text embeddings.
    """
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self._default_config = None
    
    async def create_config(
        self,
        name: str,
        provider: str,
        model_id: str,
        api_url: str,
        api_key: str,
        vector_dimension: int = 1536,
        max_input_length: int = 8192,
        created_by: uuid.UUID = None
    ) -> VectorEmbeddingConfig:
        """
        Create new embedding configuration / 创建新的嵌入配置
        """
        config = VectorEmbeddingConfig(
            id=uuid.uuid4(),
            name=name,
            provider=provider,
            model_id=model_id,
            api_url=api_url,
            api_key=api_key,
            vector_dimension=vector_dimension,
            max_input_length=max_input_length,
            is_active=False,  # New configs are inactive until tested
            is_default=False,
            test_status='untested',
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        
        logger.info(f"Created embedding config: {name} ({provider}/{model_id})")
        return config
    
    async def test_config(self, config_id: uuid.UUID) -> Dict[str, Any]:
        """
        Test embedding configuration / 测试嵌入配置
        
        Returns:
            {
                'success': bool,
                'latency_ms': int,
                'vector_dimension': int,
                'error': str (if failed)
            }
        """
        # Get config
        stmt = select(VectorEmbeddingConfig).where(VectorEmbeddingConfig.id == config_id)
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            return {'success': False, 'error': 'Config not found'}
        
        # Test text
        test_text = "This is a test sentence for embedding generation."
        
        start_time = datetime.utcnow()
        
        try:
            # Generate test embedding
            embedding = await self._generate_embedding(
                text=test_text,
                api_url=config.api_url,
                api_key=config.api_key,
                model_id=config.model_id
            )
            
            end_time = datetime.utcnow()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Verify dimension
            actual_dimension = len(embedding) if embedding else 0
            
            # Update config status
            success = actual_dimension == config.vector_dimension
            
            update_values = {
                'test_status': 'success' if success else 'failed',
                'last_tested_at': datetime.utcnow(),
                'test_error_message': None if success else f'Dimension mismatch: expected {config.vector_dimension}, got {actual_dimension}',
                'updated_at': datetime.utcnow()
            }
            
            stmt = (
                update(VectorEmbeddingConfig)
                .where(VectorEmbeddingConfig.id == config_id)
                .values(**update_values)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            if success:
                logger.info(f"Config {config.name} test passed: {latency_ms}ms, dimension={actual_dimension}")
                return {
                    'success': True,
                    'latency_ms': latency_ms,
                    'vector_dimension': actual_dimension
                }
            else:
                logger.warning(f"Config {config.name} test failed: dimension mismatch")
                return {
                    'success': False,
                    'error': f'Dimension mismatch: expected {config.vector_dimension}, got {actual_dimension}'
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Config {config.name} test failed: {error_msg}")
            
            # Update config status
            stmt = (
                update(VectorEmbeddingConfig)
                .where(VectorEmbeddingConfig.id == config_id)
                .values(
                    test_status='failed',
                    last_tested_at=datetime.utcnow(),
                    test_error_message=error_msg,
                    updated_at=datetime.utcnow()
                )
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return {
                'success': False,
                'error': error_msg
            }
    
    async def _generate_embedding(
        self,
        text: str,
        api_url: str,
        api_key: str,
        model_id: str,
        provider: str = None
    ) -> List[float]:
        """
        Generate embedding for text / 为文本生成嵌入向量
        
        Compatible with OpenAI API and Qwen API format.
        """
        # Check if it's Qwen API
        is_qwen = provider == 'qwen' or 'dashscope' in api_url.lower() or 'aliyun' in api_url.lower()
        
        # Determine URL - for some providers, the full URL is in api_url
        api_endpoint = api_url
        if not api_endpoint.endswith('/embeddings') and not 'text-embedding/text-embedding' in api_endpoint:
            api_endpoint = f"{api_endpoint.rstrip('/')}embeddings"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if is_qwen:
                # Qwen API format
                response = await client.post(
                    api_endpoint,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": model_id or "text-embedding-v3",
                        "input": {
                            "texts": [text]
                        },
                        "parameters": {
                            "text_type": "document"
                        }
                    }
                )
            else:
                # OpenAI API format
                response = await client.post(
                    api_endpoint,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": model_id,
                        "input": text,
                        "encoding_format": "float"
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle Qwen response format
                if is_qwen and 'output' in result and 'embeddings' in result['output']:
                    return result['output']['embeddings'][0]['embedding']
                # Handle OpenAI response format
                elif 'data' in result and result['data']:
                    return result['data'][0]['embedding']
                else:
                    raise ValueError(f"Invalid response format from embedding API: {result}")
            else:
                raise Exception(f"Embedding API error: {response.status_code} - {response.text}")
    
    async def generate_embedding(
        self,
        text: str,
        config_id: uuid.UUID = None
    ) -> List[float]:
        """
        Generate embedding using specified or default config / 生成嵌入向量
        """
        # Get config from vector_embedding_configs table
        config = None
        if config_id:
            stmt = select(VectorEmbeddingConfig).where(
                VectorEmbeddingConfig.id == config_id,
                VectorEmbeddingConfig.is_active == True
            )
            result = await self.db.execute(stmt)
            config = result.scalar_one_or_none()
        else:
            # Use default config
            stmt = select(VectorEmbeddingConfig).where(
                VectorEmbeddingConfig.is_default == True,
                VectorEmbeddingConfig.is_active == True
            )
            result = await self.db.execute(stmt)
            config = result.scalar_one_or_none()
        
        # If not found in vector_embedding_configs, try ai_model_configurations (embedding type)
        if not config:
            try:
                from app.services.dynamic_config_service import DynamicConfigService
                from types import SimpleNamespace
                embedding_config = await DynamicConfigService.get_embedding_config(self.db)
                if embedding_config.get("source") != "environment":
                    # Create a temporary config object
                    config = SimpleNamespace(
                        api_url=embedding_config["api_url"],
                        api_key=embedding_config["api_key"],
                        model_id=embedding_config["model_id"],
                        provider='dashscope' if 'dashscope' in embedding_config["api_url"].lower() else 'openai'
                    )
                    logger.info(f"Using embedding config from ai_model_configurations: {config.model_id}")
            except Exception as e:
                logger.error(f"Error reading embedding config from ai_model_configurations: {e}")
        
        if not config:
            raise ValueError("No active embedding configuration found")
        
        return await self._generate_embedding(
            text=text,
            api_url=config.api_url,
            api_key=config.api_key,
            model_id=config.model_id,
            provider=getattr(config, 'provider', None)
        )
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        config_id: uuid.UUID = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts / 批量生成嵌入向量
        """
        if not texts:
            return []
        
        # Try to get config from vector_embedding_configs table first
        config = None
        if config_id:
            stmt = select(VectorEmbeddingConfig).where(
                VectorEmbeddingConfig.id == config_id,
                VectorEmbeddingConfig.is_active == True
            )
        else:
            stmt = select(VectorEmbeddingConfig).where(
                VectorEmbeddingConfig.is_default == True,
                VectorEmbeddingConfig.is_active == True
            )
        
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()
        
        # If not found in vector_embedding_configs, try ai_model_configurations (embedding type)
        if not config:
            try:
                from app.services.dynamic_config_service import DynamicConfigService
                embedding_config = await DynamicConfigService.get_embedding_config(self.db)
                if embedding_config.get("source") != "environment":
                    # Create a temporary config object
                    config = SimpleNamespace(
                        api_url=embedding_config["api_url"],
                        api_key=embedding_config["api_key"],
                        model_id=embedding_config["model_id"],
                        provider='dashscope' if 'dashscope' in embedding_config["api_url"].lower() else 'openai'
                    )
                    logger.info(f"Using embedding config from ai_model_configurations: {config.model_id}")
            except Exception as e:
                logger.error(f"Error reading embedding config from ai_model_configurations: {e}")
        
        if not config:
            raise ValueError("No active embedding configuration found")
        
        # Check if it's Qwen API
        is_qwen = config.provider == 'qwen' or 'dashscope' in config.api_url.lower()
        
        # Process in batches of 10 (Qwen limit for batch embedding)
        batch_size = 10 if is_qwen else 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Determine URL - for some providers, the full URL is in api_url
                api_endpoint = config.api_url
                if not api_endpoint.endswith('/embeddings') and not 'text-embedding/text-embedding' in api_endpoint:
                    api_endpoint = f"{api_endpoint.rstrip('/')}embeddings"
                
                if is_qwen:
                    # Qwen API format
                    response = await client.post(
                        api_endpoint,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {config.api_key}"
                        },
                        json={
                            "model": config.model_id or "text-embedding-v3",
                            "input": {
                                "texts": batch
                            }
                        }
                    )
                else:
                    # OpenAI API format
                    response = await client.post(
                        api_endpoint,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {config.api_key}"
                        },
                        json={
                            "model": config.model_id,
                            "input": batch,
                            "encoding_format": "float"
                        }
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle Qwen response format
                    if is_qwen and 'output' in result and 'embeddings' in result['output']:
                        batch_embeddings = [item['embedding'] for item in result['output']['embeddings']]
                        all_embeddings.extend(batch_embeddings)
                    # Handle OpenAI response format
                    elif 'data' in result:
                        batch_embeddings = [item['embedding'] for item in result['data']]
                        all_embeddings.extend(batch_embeddings)
                    else:
                        raise ValueError(f"Invalid response format from embedding API: {result}")
                else:
                    raise Exception(f"Embedding API error: {response.status_code} - {response.text}")
        
        return all_embeddings
    
    async def set_active(self, config_id: uuid.UUID, is_active: bool = True):
        """Set configuration active/inactive / 设置配置激活状态"""
        stmt = (
            update(VectorEmbeddingConfig)
            .where(VectorEmbeddingConfig.id == config_id)
            .values(is_active=is_active, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        logger.info(f"Set config {config_id} active={is_active}")
    
    async def set_default(self, config_id: uuid.UUID):
        """Set configuration as default / 设置为默认配置"""
        # First, unset current default
        stmt = (
            update(VectorEmbeddingConfig)
            .where(VectorEmbeddingConfig.is_default == True)
            .values(is_default=False, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        
        # Set new default
        stmt = (
            update(VectorEmbeddingConfig)
            .where(VectorEmbeddingConfig.id == config_id)
            .values(is_default=True, is_active=True, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        logger.info(f"Set config {config_id} as default")
    
    async def get_all_configs(self) -> List[VectorEmbeddingConfig]:
        """Get all embedding configurations / 获取所有配置"""
        stmt = select(VectorEmbeddingConfig).order_by(VectorEmbeddingConfig.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_active_config(self) -> Optional[VectorEmbeddingConfig]:
        """Get active configuration / 获取激活的配置"""
        # First try default
        stmt = select(VectorEmbeddingConfig).where(
            VectorEmbeddingConfig.is_default == True,
            VectorEmbeddingConfig.is_active == True
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if config:
            return config
        
        # Otherwise return first active config
        stmt = select(VectorEmbeddingConfig).where(
            VectorEmbeddingConfig.is_active == True
        ).order_by(VectorEmbeddingConfig.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_config(self, config_id: uuid.UUID) -> bool:
        """Delete configuration / 删除配置"""
        stmt = select(VectorEmbeddingConfig).where(VectorEmbeddingConfig.id == config_id)
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            return False
        
        await self.db.delete(config)
        await self.db.commit()
        
        logger.info(f"Deleted config {config_id}")
        return True


# Global service instance
vector_service = VectorEmbeddingService()


# Convenience functions for direct use
async def generate_embedding(text: str, db: AsyncSession = None) -> List[float]:
    """Generate embedding using default config / 使用默认配置生成嵌入"""
    service = VectorEmbeddingService(db)
    return await service.generate_embedding(text)


async def generate_embeddings_batch(texts: List[str], db: AsyncSession = None) -> List[List[float]]:
    """Generate embeddings in batch / 批量生成嵌入"""
    service = VectorEmbeddingService(db)
    return await service.generate_embeddings_batch(texts)
