"""
Reranking Service - 重排序服务

Provides unified interface for document reranking in RAG pipeline.
为RAG流程中的文档重排序提供统一接口。

Features | 功能特点:
- 支持多种重排序提供商 (阿里云百炼、Cohere、Jina、博查)
- 与现有AI模型配置系统集成
- 批量处理和缓存优化
- 异步API调用支持
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import httpx
import json
import logging
from datetime import datetime
import hashlib
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.reranking_provider_adapter import (
    get_rerank_adapter,
    get_all_rerank_providers,
    get_rerank_provider_info,
    RerankResult,
)
from app.services.ai_model_config_service import AIModelConfigService

logger = logging.getLogger(__name__)


class RerankingService:
    """
    重排序服务
    Reranking Service
    """

    def __init__(self, db: AsyncSession = None):
        self.db = db
        self._adapter = None
        self._config = None
        self._cache = {}  # 简单的内存缓存

    async def _load_config(self) -> Optional[Dict[str, Any]]:
        """
        加载重排序模型配置
        Load reranking model configuration
        """
        if not self.db:
            return None

        try:
            config_service = AIModelConfigService(self.db)
            config = await config_service.get_config_with_decrypted_key("rerank")

            if not config or not config.get("enabled"):
                return None

            return config
        except Exception as e:
            logger.warning(f"Failed to load rerank config: {e}")
            return None

    def _get_adapter(self, config: Dict[str, Any]):
        """
        获取重排序适配器
        Get reranking adapter
        """
        provider = config.get("provider", "custom")
        api_url = config.get("api_url", "")
        api_key = config.get("api_key", "")
        model_id = config.get("model_id", "")

        if not api_url:
            # Use default URL from provider info
            info = get_rerank_provider_info(provider)
            api_url = info.get("default_url", "")

        return get_rerank_adapter(
            provider=provider, api_url=api_url, api_key=api_key, model_id=model_id
        )

    def _get_cache_key(
        self, query: str, documents: List[str], top_n: Optional[int]
    ) -> str:
        """Generate cache key for request | 生成请求缓存键"""
        content = f"{query}:{json.dumps(documents)}:{top_n}"
        return hashlib.md5(content.encode()).hexdigest()

    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        use_cache: bool = True,
    ) -> Tuple[List[RerankResult], Dict[str, Any]]:
        """
        对文档进行重排序
        Rerank documents based on query relevance

        Args:
            query: Search query
            documents: List of documents to rerank
            top_n: Number of top results to return (None = all)
            use_cache: Whether to use caching

        Returns:
            Tuple of (reranked_results, metadata)
        """
        # Load configuration
        config = await self._load_config()
        if not config:
            logger.debug("Reranking not configured, returning original order")
            # Return original order if not configured
            results = [
                RerankResult(document=doc, index=i, relevance_score=1.0 - (i * 0.01))
                for i, doc in enumerate(documents)
            ]
            return results, {"used": False, "reason": "not_configured"}

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(query, documents, top_n)
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                # Check if cache is still valid (30 minutes)
                if (datetime.now() - cached_result["timestamp"]).seconds < 1800:
                    logger.debug("Using cached reranking result")
                    return cached_result["results"], cached_result["metadata"]

        try:
            # Get adapter
            adapter = self._get_adapter(config)

            # Prepare request
            url = adapter.get_rerank_url()
            headers = adapter.get_headers()
            body = adapter.format_request_body(query, documents, top_n)

            logger.debug(f"Calling rerank API: {url}")

            # Make API call
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                response_data = response.json()

            # Parse response
            results = adapter.parse_response(response_data)

            # Limit to top_n if specified
            if top_n and len(results) > top_n:
                results = results[:top_n]

            # Prepare metadata
            metadata = {
                "used": True,
                "provider": config.get("provider", "unknown"),
                "model_id": config.get("model_id", "unknown"),
                "total_documents": len(documents),
                "returned_results": len(results),
            }

            # Cache result
            if use_cache:
                self._cache[cache_key] = {
                    "results": results,
                    "metadata": metadata,
                    "timestamp": datetime.now(),
                }

            return results, metadata

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Rerank API HTTP error: {e.response.status_code} - {e.response.text}"
            )
            # Return original order on error
            results = [
                RerankResult(document=doc, index=i, relevance_score=1.0 - (i * 0.01))
                for i, doc in enumerate(documents)
            ]
            return results, {
                "used": False,
                "reason": f"api_error_{e.response.status_code}",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Rerank error: {e}")
            # Return original order on error
            results = [
                RerankResult(document=doc, index=i, relevance_score=1.0 - (i * 0.01))
                for i, doc in enumerate(documents)
            ]
            return results, {"used": False, "reason": "error", "error": str(e)}

    async def rerank_chunks(
        self, query: str, chunks: List[Dict[str, Any]], top_n: Optional[int] = 5
    ) -> List[Dict[str, Any]]:
        """
        对知识库块进行重排序并返回完整块信息
        Rerank knowledge base chunks and return full chunk info

        Args:
            query: Search query
            chunks: List of chunk dictionaries with 'text' field
            top_n: Number of top results to return

        Returns:
            Reranked list of chunks
        """
        if not chunks:
            return []

        # Extract text from chunks
        texts = [chunk.get("text", "") for chunk in chunks]

        # Rerank
        results, metadata = await self.rerank(query, texts, top_n=top_n)

        if not metadata.get("used"):
            logger.debug(f"Reranking not used: {metadata.get('reason')}")
            return chunks[:top_n] if top_n else chunks

        # Map reranked results back to chunks
        reranked_chunks = []
        for result in results:
            if result.index < len(chunks):
                chunk = chunks[result.index].copy()
                chunk["rerank_score"] = result.relevance_score
                chunk["reranked"] = True
                reranked_chunks.append(chunk)

        logger.info(
            f"Reranking completed: {len(chunks)} -> {len(reranked_chunks)} chunks"
        )
        return reranked_chunks

    async def is_configured(self) -> bool:
        """Check if reranking is properly configured | 检查是否已配置"""
        config = await self._load_config()
        return config is not None and config.get("enabled", False)

    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration info | 获取当前配置信息"""
        return {
            "providers": get_all_rerank_providers(),
            "configured": self._config is not None,
            "config": self._config,
        }

    async def test_connection(self) -> Dict[str, Any]:
        """
        测试重排序服务连接
        Test reranking service connection

        Returns:
            Dict with success status and details
        """
        config = await self._load_config()
        if not config:
            return {"success": False, "error_message": "重排序模型未配置"}

        try:
            # Get adapter
            adapter = self._get_adapter(config)

            # Prepare test request
            url = adapter.get_rerank_url()
            headers = adapter.get_headers()
            test_documents = ["测试文档1", "测试文档2", "测试文档3"]
            body = adapter.format_request_body("测试查询", test_documents, top_n=2)

            # Make test API call
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()

            return {
                "success": True,
                "message": "连接成功",
                "provider": config.get("provider"),
                "model_id": config.get("model_id"),
                "latency_ms": 0,  # Could measure actual latency here
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"API错误: HTTP {e.response.status_code}"
            try:
                error_detail = e.response.json()
                if "error" in error_detail:
                    error_msg += f" - {error_detail['error']}"
            except:
                error_msg += f" - {e.response.text[:200]}"

            return {"success": False, "error_message": error_msg}
        except Exception as e:
            return {"success": False, "error_message": f"连接失败: {str(e)}"}

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        Health check
        """
        try:
            is_configured = await self.is_configured()
            if not is_configured:
                return {
                    "status": "not_configured",
                    "healthy": True,
                    "message": "Reranking service is available but not configured",
                }

            test_result = await self.test_connection()
            if test_result.get("success"):
                return {
                    "status": "healthy",
                    "healthy": True,
                    "provider": test_result.get("provider"),
                    "model_id": test_result.get("model_id"),
                }
            else:
                return {
                    "status": "unhealthy",
                    "healthy": False,
                    "error": test_result.get("error_message"),
                }
        except Exception as e:
            return {"status": "error", "healthy": False, "error": str(e)}
