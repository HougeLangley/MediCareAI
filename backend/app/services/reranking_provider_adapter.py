"""
Reranking Service - 重排序服务

Provides document reranking capabilities using external reranking models.
支持使用外部重排序模型对检索结果进行精确排序。

Supported Providers | 支持的提供商:
- bailian: 阿里云百炼 (qwen3-rerank, gte-rerank-v2)
- cohere: Cohere Rerank API
- jina: Jina AI Reranker
- bocha: 博查AI (bocha-semantic-reranker)
- custom: 其他OpenAI兼容API
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """重排序结果 | Reranking result"""

    document: str
    index: int
    relevance_score: float


class RerankProviderAdapter(ABC):
    """Base adapter for reranking providers | 重排序提供商基础适配器"""

    def __init__(self, api_url: str, api_key: str, model_id: str, **kwargs):
        self.api_url = api_url
        self.api_key = api_key
        self.model_id = model_id
        self.extra_config = kwargs

    @abstractmethod
    def get_rerank_url(self) -> str:
        """Get the rerank endpoint URL | 获取重排序端点URL"""
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get request headers | 获取请求头"""
        pass

    @abstractmethod
    def format_request_body(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """Format request body for the provider | 格式化请求体"""
        pass

    @abstractmethod
    def parse_response(self, response_data: Dict[str, Any]) -> List[RerankResult]:
        """Parse response from the provider | 解析响应"""
        pass


class BailianRerankAdapter(RerankProviderAdapter):
    """
    阿里云百炼重排序适配器
    API文档: https://help.aliyun.com/document_detail/2773526.html
    支持模型: qwen3-rerank, gte-rerank-v2, qwen3-vl-rerank
    """

    DEFAULT_MODELS = {
        "qwen3-rerank": "qwen3-rerank",
        "gte-rerank-v2": "gte-rerank-v2",
        "qwen3-vl-rerank": "qwen3-vl-rerank",
    }

    def __init__(
        self, api_url: str, api_key: str, model_id: str = "qwen3-rerank", **kwargs
    ):
        if not api_url:
            api_url = "https://dashscope.aliyuncs.com/compatible-api/v1"
        super().__init__(api_url, api_key, model_id, **kwargs)

    def get_rerank_url(self) -> str:
        """百炼重排序端点 (兼容OpenAI格式)"""
        base = self.api_url.rstrip("/")
        return f"{base}/reranks"

    def get_headers(self) -> Dict[str, str]:
        """百炼认证头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_body(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """格式化百炼重排序请求"""
        body = {"model": self.model_id, "query": query, "documents": documents}
        if top_n:
            body["top_n"] = top_n
        return body

    def parse_response(self, response_data: Dict[str, Any]) -> List[RerankResult]:
        """解析百炼重排序响应 (兼容OpenAI格式)"""
        results = []
        for item in response_data.get("results", []):
            results.append(
                RerankResult(
                    document=item.get("document", {}).get("text", ""),
                    index=item.get("index", 0),
                    relevance_score=item.get("relevance_score", 0.0),
                )
            )
        return results


class CohereRerankAdapter(RerankProviderAdapter):
    """
    Cohere Rerank API适配器
    支持模型: rerank-multilingual-v3.0, rerank-v3.5
    """

    DEFAULT_MODELS = {
        "rerank-multilingual-v3.0": "rerank-multilingual-v3.0",
        "rerank-v3.5": "rerank-v3.5",
    }

    def __init__(
        self,
        api_url: str,
        api_key: str,
        model_id: str = "rerank-multilingual-v3.0",
        **kwargs,
    ):
        if not api_url:
            api_url = "https://api.cohere.com"
        super().__init__(api_url, api_key, model_id, **kwargs)

    def get_rerank_url(self) -> str:
        """Cohere rerank端点"""
        base = self.api_url.rstrip("/")
        return f"{base}/v2/rerank"

    def get_headers(self) -> Dict[str, str]:
        """Cohere认证头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_body(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """格式化Cohere重排序请求"""
        body = {"model": self.model_id, "query": query, "documents": documents}
        if top_n:
            body["top_n"] = top_n
        return body

    def parse_response(self, response_data: Dict[str, Any]) -> List[RerankResult]:
        """解析Cohere重排序响应"""
        results = []
        for item in response_data.get("results", []):
            results.append(
                RerankResult(
                    document=item.get("document", {}).get("text", ""),
                    index=item.get("index", 0),
                    relevance_score=item.get("relevance_score", 0.0),
                )
            )
        return results


class JinaRerankAdapter(RerankProviderAdapter):
    """
    Jina AI Reranker适配器
    支持模型: jina-reranker-v2-base-multilingual
    """

    DEFAULT_MODELS = {
        "jina-reranker-v2-base-multilingual": "jina-reranker-v2-base-multilingual"
    }

    def __init__(
        self,
        api_url: str,
        api_key: str,
        model_id: str = "jina-reranker-v2-base-multilingual",
        **kwargs,
    ):
        if not api_url:
            api_url = "https://api.jina.ai"
        super().__init__(api_url, api_key, model_id, **kwargs)

    def get_rerank_url(self) -> str:
        """Jina rerank端点"""
        base = self.api_url.rstrip("/")
        return f"{base}/v1/rerank"

    def get_headers(self) -> Dict[str, str]:
        """Jina认证头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_body(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """格式化Jina重排序请求"""
        body = {"model": self.model_id, "query": query, "documents": documents}
        if top_n:
            body["top_n"] = top_n
        return body

    def parse_response(self, response_data: Dict[str, Any]) -> List[RerankResult]:
        """解析Jina重排序响应"""
        results = []
        for item in response_data.get("results", []):
            results.append(
                RerankResult(
                    document=item.get("document", {}).get("text", ""),
                    index=item.get("index", 0),
                    relevance_score=item.get("relevance_score", 0.0),
                )
            )
        return results


class BochaRerankAdapter(RerankProviderAdapter):
    """
    博查AI语义重排序适配器 (国内)
    支持模型: bocha-semantic-reranker
    """

    DEFAULT_MODELS = {"bocha-semantic-reranker": "bocha-semantic-reranker"}

    def __init__(
        self,
        api_url: str,
        api_key: str,
        model_id: str = "bocha-semantic-reranker",
        **kwargs,
    ):
        if not api_url:
            api_url = "https://api.bochaai.com"
        super().__init__(api_url, api_key, model_id, **kwargs)

    def get_rerank_url(self) -> str:
        """博查rerank端点"""
        base = self.api_url.rstrip("/")
        return f"{base}/v1/rerank"

    def get_headers(self) -> Dict[str, str]:
        """博查认证头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_body(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """格式化博查重排序请求"""
        body = {"model": self.model_id, "query": query, "documents": documents}
        if top_n:
            body["top_n"] = top_n
        return body

    def parse_response(self, response_data: Dict[str, Any]) -> List[RerankResult]:
        """解析博查重排序响应"""
        results = []
        for item in response_data.get("results", []):
            results.append(
                RerankResult(
                    document=item.get("document", {}).get("text", ""),
                    index=item.get("index", 0),
                    relevance_score=item.get("relevance_score", 0.0),
                )
            )
        return results


class CustomRerankAdapter(RerankProviderAdapter):
    """
    自定义/OpenAI兼容重排序适配器
    适用于其他兼容OpenAI rerank格式的API
    """

    def __init__(self, api_url: str, api_key: str, model_id: str = "custom", **kwargs):
        super().__init__(api_url, api_key, model_id, **kwargs)

    def get_rerank_url(self) -> str:
        base = self.api_url.rstrip("/")
        if "/v1" in base:
            return f"{base}/rerank"
        return f"{base}/v1/rerank"

    def get_headers(self) -> Dict[str, str]:
        """自定义认证头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_body(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """格式化自定义重排序请求 (OpenAI兼容格式)"""
        body = {"model": self.model_id, "query": query, "documents": documents}
        if top_n:
            body["top_n"] = top_n
        return body

    def parse_response(self, response_data: Dict[str, Any]) -> List[RerankResult]:
        """解析自定义重排序响应 (OpenAI兼容格式)"""
        results = []
        for item in response_data.get("results", []):
            results.append(
                RerankResult(
                    document=item.get("document", {}).get("text", ""),
                    index=item.get("index", 0),
                    relevance_score=item.get("relevance_score", 0.0),
                )
            )
        return results


# Provider registry | 提供商注册表
RERANK_ADAPTERS = {
    "bailian": BailianRerankAdapter,
    "cohere": CohereRerankAdapter,
    "jina": JinaRerankAdapter,
    "bocha": BochaRerankAdapter,
    "custom": CustomRerankAdapter,
}

# Provider metadata | 提供商元数据
RERANK_PROVIDER_INFO = {
    "bailian": {
        "name": "Bailian",
        "name_zh": "阿里云百炼",
        "default_url": "https://dashscope.aliyuncs.com/compatible-api/v1",
        "default_model": "qwen3-rerank",
        "requires_key": True,
        "models": ["qwen3-rerank", "gte-rerank-v2", "qwen3-vl-rerank"],
    },
    "cohere": {
        "name": "Cohere",
        "name_zh": "Cohere",
        "default_url": "https://api.cohere.com",
        "default_model": "rerank-multilingual-v3.0",
        "requires_key": True,
        "models": ["rerank-multilingual-v3.0", "rerank-v3.5"],
    },
    "jina": {
        "name": "Jina AI",
        "name_zh": "Jina AI",
        "default_url": "https://api.jina.ai",
        "default_model": "jina-reranker-v2-base-multilingual",
        "requires_key": True,
        "models": ["jina-reranker-v2-base-multilingual"],
    },
    "bocha": {
        "name": "Bocha AI",
        "name_zh": "博查AI",
        "default_url": "https://api.bochaai.com",
        "default_model": "bocha-semantic-reranker",
        "requires_key": True,
        "models": ["bocha-semantic-reranker"],
    },
    "custom": {
        "name": "Custom",
        "name_zh": "自定义 (OpenAI兼容)",
        "default_url": "",
        "default_model": "custom",
        "requires_key": True,
        "models": ["custom"],
    },
}


def get_rerank_adapter(
    provider: str, api_url: str, api_key: str, model_id: str = None, **kwargs
) -> RerankProviderAdapter:
    """
    Factory function to get appropriate rerank adapter | 获取重排序适配器的工厂函数

    Args:
        provider: Provider key (bailian, cohere, jina, bocha, custom)
        api_url: API endpoint URL
        api_key: API key
        model_id: Model identifier
        **kwargs: Additional configuration

    Returns:
        RerankProviderAdapter instance
    """
    adapter_class = RERANK_ADAPTERS.get(provider.lower(), CustomRerankAdapter)

    # Get default model if not provided
    if not model_id and provider.lower() in RERANK_PROVIDER_INFO:
        model_id = RERANK_PROVIDER_INFO[provider.lower()]["default_model"]
    elif not model_id:
        model_id = "custom"

    return adapter_class(api_url, api_key, model_id, **kwargs)


def get_rerank_provider_info(provider: str) -> Dict[str, Any]:
    """Get provider information | 获取提供商信息"""
    return RERANK_PROVIDER_INFO.get(provider.lower(), RERANK_PROVIDER_INFO["custom"])


def get_rerank_provider_models(provider: str) -> List[str]:
    """Get default models for a provider | 获取提供商默认模型列表"""
    info = RERANK_PROVIDER_INFO.get(provider.lower(), {})
    return info.get("models", ["custom"])


def get_all_rerank_providers() -> Dict[str, Dict[str, Any]]:
    """Get all available reranking providers | 获取所有可用提供商"""
    return RERANK_PROVIDER_INFO.copy()
