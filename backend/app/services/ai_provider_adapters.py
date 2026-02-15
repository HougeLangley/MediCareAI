"""
AI Provider Adapters | AI提供商适配器

Provides unified interface for multiple AI providers (cloud and local).
支持多种AI提供商的统一接口（云端和本地）。

Supported Providers | 支持的提供商:
- openai: OpenAI API compatible (GPT-4, GPT-3.5)
- zhipu: 智谱AI (GLM-4, GLM-4-Flash)
- kimi: Moonshot AI (Kimi)
- deepseek: DeepSeek AI
- ollama: Ollama (local)
- vllm: vLLM (local)
- lmstudio: LM Studio (local)
- custom: Custom OpenAI-compatible endpoint
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, AsyncGenerator, Optional
import httpx
import json
import logging

logger = logging.getLogger(__name__)


class AIProviderAdapter(ABC):
    """Base adapter for AI providers | AI提供商基础适配器"""
    
    def __init__(self, api_url: str, api_key: str, model_id: str, **kwargs):
        self.api_url = api_url
        self.api_key = api_key
        self.model_id = model_id
        self.extra_config = kwargs
    
    @abstractmethod
    def get_chat_completions_url(self) -> str:
        """Get the chat completions endpoint URL"""
        pass
    
    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        pass
    
    @abstractmethod
    def format_request_body(self, messages: List[Dict[str, str]], 
                           max_tokens: int = 8192,
                           temperature: float = 0.7,
                           stream: bool = False) -> Dict[str, Any]:
        """Format request body for the provider"""
        pass
    
    @abstractmethod
    def parse_response(self, response_data: Dict[str, Any]) -> str:
        """Parse response from the provider"""
        pass
    
    @abstractmethod
    async def stream_parse(self, line: str) -> Optional[str]:
        """Parse a streaming response line"""
        pass


class OpenAICompatibleAdapter(AIProviderAdapter):
    """
    OpenAI-compatible adapter
    Works with: OpenAI, Zhipu, Kimi, DeepSeek, vLLM, LM Studio
    """
    
    def get_chat_completions_url(self) -> str:
        """OpenAI-compatible endpoint"""
        # Handle both full URL and base URL
        if 'chat/completions' in self.api_url:
            return self.api_url
        base = self.api_url.rstrip('/')
        return f"{base}/chat/completions"
    
    def get_headers(self) -> Dict[str, str]:
        """Standard OpenAI headers"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def format_request_body(self, messages: List[Dict[str, str]], 
                           max_tokens: int = 8192,
                           temperature: float = 0.7,
                           stream: bool = False) -> Dict[str, Any]:
        """Standard OpenAI request format"""
        return {
            "model": self.model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
    
    def parse_response(self, response_data: Dict[str, Any]) -> str:
        """Parse OpenAI-compatible response"""
        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0].get('message', {}).get('content', '')
        return ''
    
    async def stream_parse(self, line: str) -> Optional[str]:
        """Parse OpenAI-compatible streaming response"""
        if line.startswith("data: "):
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                return None
            try:
                data = json.loads(data_str)
                if 'choices' in data and data['choices']:
                    delta = data['choices'][0].get('delta', {})
                    return delta.get('content', '')
            except json.JSONDecodeError:
                pass
        return None


class ZhipuAdapter(OpenAICompatibleAdapter):
    """
    智谱AI Adapter
    API文档: https://open.bigmodel.cn/dev/api
    """
    
    # 智谱AI默认模型映射
    DEFAULT_MODELS = {
        'glm-4': 'glm-4',
        'glm-4-flash': 'glm-4-flash',
        'glm-4-plus': 'glm-4-plus',
        'glm-4-air': 'glm-4-air',
        'glm-4.5': 'glm-4.5'
    }
    
    def __init__(self, api_url: str, api_key: str, model_id: str, **kwargs):
        # 智谱AI默认URL
        if not api_url or api_url == 'https://api.openai.com/v1':
            api_url = 'https://open.bigmodel.cn/api/paas/v4'
        super().__init__(api_url, api_key, model_id, **kwargs)
    
    def get_chat_completions_url(self) -> str:
        """智谱AI endpoint"""
        base = self.api_url.rstrip('/')
        return f"{base}/chat/completions"


class KimiAdapter(OpenAICompatibleAdapter):
    """
    Moonshot Kimi Adapter
    API文档: https://platform.moonshot.cn/docs
    """
    
    DEFAULT_MODELS = {
        'kimi-latest': 'kimi-latest',
        'kimi-k2': 'kimi-k2',
        'kimi-k2.5': 'kimi-k2.5',
        'kimi-k1.5': 'kimi-k1.5'
    }
    
    def __init__(self, api_url: str, api_key: str, model_id: str, **kwargs):
        if not api_url or api_url == 'https://api.openai.com/v1':
            api_url = 'https://api.moonshot.cn/v1'
        super().__init__(api_url, api_key, model_id, **kwargs)


class DeepSeekAdapter(OpenAICompatibleAdapter):
    """
    DeepSeek Adapter
    API文档: https://platform.deepseek.com/api-docs
    """
    
    DEFAULT_MODELS = {
        'deepseek-chat': 'deepseek-chat',
        'deepseek-reasoner': 'deepseek-reasoner',
        'deepseek-coder': 'deepseek-coder'
    }
    
    def __init__(self, api_url: str, api_key: str, model_id: str, **kwargs):
        if not api_url or api_url == 'https://api.openai.com/v1':
            api_url = 'https://api.deepseek.com/v1'
        super().__init__(api_url, api_key, model_id, **kwargs)


class OllamaAdapter(OpenAICompatibleAdapter):
    """
    Ollama Adapter
    本地部署，无需API key
    """
    
    def __init__(self, api_url: str, api_key: str = "", model_id: str = "", **kwargs):
        # Ollama默认本地地址
        if not api_url:
            api_url = 'http://localhost:11434'
        # Ollama不需要API key
        super().__init__(api_url, "", model_id, **kwargs)
    
    def get_chat_completions_url(self) -> str:
        """Ollama endpoint (OpenAI compatible mode)"""
        base = self.api_url.rstrip('/')
        return f"{base}/v1/chat/completions"
    
    def get_headers(self) -> Dict[str, str]:
        """Ollama doesn't require auth by default"""
        return {
            "Content-Type": "application/json"
        }


class VLLMAdapter(OpenAICompatibleAdapter):
    """
    vLLM Adapter
    本地部署，支持OpenAI兼容API
    """
    
    def __init__(self, api_url: str, api_key: str = "", model_id: str = "", **kwargs):
        # vLLM默认本地地址
        if not api_url:
            api_url = 'http://localhost:8000'
        super().__init__(api_url, api_key, model_id, **kwargs)
    
    def get_chat_completions_url(self) -> str:
        """vLLM OpenAI-compatible endpoint"""
        base = self.api_url.rstrip('/')
        return f"{base}/v1/chat/completions"


class LMStudioAdapter(OpenAICompatibleAdapter):
    """
    LM Studio Adapter
    本地部署，OpenAI兼容
    """
    
    def __init__(self, api_url: str, api_key: str = "", model_id: str = "", **kwargs):
        # LM Studio默认本地地址
        if not api_url:
            api_url = 'http://localhost:1234'
        super().__init__(api_url, api_key or "not-needed", model_id, **kwargs)
    
    def get_chat_completions_url(self) -> str:
        """LM Studio endpoint"""
        base = self.api_url.rstrip('/')
        return f"{base}/v1/chat/completions"


# Provider registry | 提供商注册表
PROVIDER_ADAPTERS = {
    'openai': OpenAICompatibleAdapter,
    'zhipu': ZhipuAdapter,
    'kimi': KimiAdapter,
    'deepseek': DeepSeekAdapter,
    'ollama': OllamaAdapter,
    'vllm': VLLMAdapter,
    'lmstudio': LMStudioAdapter,
    'custom': OpenAICompatibleAdapter,
}

# Provider display names | 提供商显示名称
PROVIDER_INFO = {
    'openai': {
        'name': 'OpenAI',
        'description': 'OpenAI GPT models',
        'default_url': 'https://api.openai.com/v1',
        'requires_key': True,
        'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
    },
    'zhipu': {
        'name': '智谱AI',
        'description': '智谱AI GLM系列模型',
        'default_url': 'https://open.bigmodel.cn/api/paas/v4',
        'requires_key': True,
        'models': ['glm-4', 'glm-4-flash', 'glm-4-plus', 'glm-4.5']
    },
    'kimi': {
        'name': 'Moonshot (Kimi)',
        'description': '月之暗面Kimi模型',
        'default_url': 'https://api.moonshot.cn/v1',
        'requires_key': True,
        'models': ['kimi-latest', 'kimi-k2', 'kimi-k2.5']
    },
    'deepseek': {
        'name': 'DeepSeek',
        'description': 'DeepSeek大模型',
        'default_url': 'https://api.deepseek.com/v1',
        'requires_key': True,
        'models': ['deepseek-chat', 'deepseek-reasoner', 'deepseek-coder']
    },
    'ollama': {
        'name': 'Ollama (本地)',
        'description': '本地Ollama部署',
        'default_url': 'http://localhost:11434',
        'requires_key': False,
        'models': ['llama2', 'mistral', 'qwen', 'glm4']
    },
    'vllm': {
        'name': 'vLLM (本地)',
        'description': '本地vLLM部署',
        'default_url': 'http://localhost:8000',
        'requires_key': False,
        'models': ['custom']
    },
    'lmstudio': {
        'name': 'LM Studio (本地)',
        'description': 'LM Studio本地推理',
        'default_url': 'http://localhost:1234',
        'requires_key': False,
        'models': ['local-model']
    },
    'custom': {
        'name': '自定义 (OpenAI兼容)',
        'description': '其他OpenAI兼容API',
        'default_url': '',
        'requires_key': True,
        'models': ['custom']
    }
}


def get_provider_adapter(provider: str, api_url: str, api_key: str, 
                         model_id: str, **kwargs) -> AIProviderAdapter:
    """
    Get the appropriate adapter for a provider
    
    Args:
        provider: Provider name (zhipu, kimi, ollama, etc.)
        api_url: API endpoint URL
        api_key: API key
        model_id: Model identifier
        **kwargs: Additional configuration
    
    Returns:
        AIProviderAdapter instance
    """
    adapter_class = PROVIDER_ADAPTERS.get(provider.lower(), OpenAICompatibleAdapter)
    return adapter_class(api_url, api_key, model_id, **kwargs)


def get_provider_default_url(provider: str) -> str:
    """Get default URL for a provider"""
    info = PROVIDER_INFO.get(provider.lower(), {})
    return info.get('default_url', '')


def provider_requires_key(provider: str) -> bool:
    """Check if provider requires API key"""
    info = PROVIDER_INFO.get(provider.lower(), {})
    return info.get('requires_key', True)


def get_provider_models(provider: str) -> List[str]:
    """Get default models for a provider"""
    info = PROVIDER_INFO.get(provider.lower(), {})
    return info.get('models', ['custom'])


def get_all_providers() -> Dict[str, Dict[str, Any]]:
    """Get all available providers"""
    return PROVIDER_INFO.copy()
