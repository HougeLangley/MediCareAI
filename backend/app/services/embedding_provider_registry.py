"""
Embedding Provider Registry - 嵌入模型提供商注册表

Manages provider presets and URL validation for embedding models.
支持多种嵌入模型提供商的预设配置和 URL 智能验证。
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingProvider:
    """Embedding provider configuration template"""
    key: str
    name: str
    name_zh: str
    default_url: str
    default_model: str
    vector_dimension: int
    batch_size: int
    headers_format: str  # 'bearer', 'api_key', 'none'
    request_format: str  # 'openai', 'qwen', 'custom'
    description: str
    
    def get_formatted_url(self, custom_url: Optional[str] = None) -> str:
        """
        Get formatted URL, validate and auto-correct if needed
        
        Args:
            custom_url: User provided URL (optional)
            
        Returns:
            Formatted and validated URL
        """
        if not custom_url:
            return self.default_url
            
        # Normalize URL
        url = custom_url.strip()
        
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Provider-specific URL validation and formatting
        if self.key == 'dashscope':
            # DashScope embedding API should end with specific path
            if '/compatible-mode' in url:
                # User mistakenly used chat API URL
                logger.warning(f"Detected chat API URL, converting to embedding API")
                url = self.default_url
            elif not url.endswith('/text-embedding'):
                # Auto-complete embedding endpoint
                base = url.rstrip('/')
                if 'services/embeddings' not in base:
                    url = f"{base}/api/v1/services/embeddings/text-embedding/text-embedding"
                    
        elif self.key == 'openai':
            # OpenAI format validation
            if 'embeddings' not in url:
                # Default to standard OpenAI embeddings endpoint
                if url.endswith('/v1'):
                    url = f"{url}/embeddings"
                    
        elif self.key == 'ollama':
            # Ollama local deployment
            if not any(x in url for x in ['/api/embeddings', ':11434']):
                url = f"{url}/api/embeddings"
                
        elif self.key == 'xinference':
            # Xinference local deployment
            if not url.endswith('/v1/embeddings'):
                url = url.replace('/v1/chat/completions', '/v1/embeddings')
                if '/embeddings' not in url:
                    url = f"{url.rstrip('/')}/v1/embeddings"
        
        return url


class EmbeddingProviderRegistry:
    """
    Registry for embedding providers with presets and validation
    
    Features:
    - Provider preset management
    - URL validation and auto-correction
    - Smart URL formatting based on provider
    """
    
    # Provider presets
    PROVIDERS: Dict[str, EmbeddingProvider] = {
        'dashscope': EmbeddingProvider(
            key='dashscope',
            name='DashScope (Aliyun)',
            name_zh='阿里云 DashScope',
            default_url='https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding',
            default_model='text-embedding-v3',
            vector_dimension=1536,
            batch_size=10,
            headers_format='bearer',
            request_format='qwen',
            description='阿里云 DashScope 嵌入模型服务 (推荐)'
        ),
        'openai': EmbeddingProvider(
            key='openai',
            name='OpenAI',
            name_zh='OpenAI',
            default_url='https://api.openai.com/v1/embeddings',
            default_model='text-embedding-3-small',
            vector_dimension=1536,
            batch_size=100,
            headers_format='bearer',
            request_format='openai',
            description='OpenAI 官方嵌入模型服务'
        ),
        'ollama': EmbeddingProvider(
            key='ollama',
            name='Ollama (Local)',
            name_zh='Ollama (本地)',
            default_url='http://localhost:11434/api/embeddings',
            default_model='nomic-embed-text',
            vector_dimension=768,
            batch_size=1,
            headers_format='none',
            request_format='custom',
            description='本地部署的 Ollama 嵌入模型'
        ),
        'xinference': EmbeddingProvider(
            key='xinference',
            name='Xinference (Local)',
            name_zh='Xinference (本地)',
            default_url='http://localhost:9997/v1/embeddings',
            default_model='bge-large-zh-v1.5',
            vector_dimension=1024,
            batch_size=10,
            headers_format='bearer',
            request_format='openai',
            description='本地部署的 Xinference 嵌入模型服务'
        ),
        'vllm': EmbeddingProvider(
            key='vllm',
            name='vLLM (Local)',
            name_zh='vLLM (本地)',
            default_url='http://localhost:8000/v1/embeddings',
            default_model='BAAI/bge-large-zh-v1.5',
            vector_dimension=1024,
            batch_size=32,
            headers_format='bearer',
            request_format='openai',
            description='本地部署的 vLLM 嵌入模型服务'
        ),
        'custom': EmbeddingProvider(
            key='custom',
            name='Custom Provider',
            name_zh='自定义提供商',
            default_url='',
            default_model='',
            vector_dimension=1536,
            batch_size=10,
            headers_format='bearer',
            request_format='openai',
            description='自定义 OpenAI 兼容 API'
        )
    }
    
    @classmethod
    def get_provider(cls, key: str) -> Optional[EmbeddingProvider]:
        """Get provider by key"""
        return cls.PROVIDERS.get(key)
    
    @classmethod
    def list_providers(cls) -> List[Dict[str, str]]:
        """List all available providers"""
        return [
            {
                'key': key,
                'name': provider.name,
                'name_zh': provider.name_zh,
                'default_url': provider.default_url,
                'default_model': provider.default_model,
                'description': provider.description
            }
            for key, provider in cls.PROVIDERS.items()
        ]
    
    @classmethod
    def detect_provider_from_url(cls, url: str) -> Optional[str]:
        """
        Detect provider from URL pattern
        
        Args:
            url: API URL
            
        Returns:
            Provider key or None
        """
        url_lower = url.lower()
        
        if 'dashscope' in url_lower or 'aliyun' in url_lower:
            return 'dashscope'
        elif 'openai.com' in url_lower:
            return 'openai'
        elif ':11434' in url_lower or '/ollama' in url_lower:
            return 'ollama'
        elif 'xinference' in url_lower or ':9997' in url_lower:
            return 'xinference'
        elif 'vllm' in url_lower:
            return 'vllm'
        elif 'localhost' in url_lower or '127.0.0.1' in url_lower:
            # Local deployment, try to detect by port
            if ':11434' in url_lower:
                return 'ollama'
            elif ':9997' in url_lower:
                return 'xinference'
            elif ':8000' in url_lower:
                return 'vllm'
        
        return 'custom'
    
    @classmethod
    def validate_and_format_url(cls, url: str, provider_key: Optional[str] = None) -> Dict[str, any]:
        """
        Validate and format URL for embedding API
        
        Args:
            url: User provided URL
            provider_key: Known provider key (optional)
            
        Returns:
            {
                'valid': bool,
                'formatted_url': str,
                'provider': str,
                'warnings': List[str],
                'suggestions': List[str]
            }
        """
        if not url or not url.strip():
            return {
                'valid': False,
                'formatted_url': '',
                'provider': provider_key or 'unknown',
                'warnings': ['URL is empty'],
                'suggestions': ['Please provide an API URL']
            }
        
        url = url.strip()
        warnings = []
        suggestions = []
        
        # Auto-detect provider if not specified
        if not provider_key:
            provider_key = cls.detect_provider_from_url(url)
            if provider_key:
                suggestions.append(f"Detected provider: {cls.PROVIDERS[provider_key].name_zh}")
        
        provider = cls.get_provider(provider_key)
        if not provider:
            provider = cls.PROVIDERS['custom']
            warnings.append(f"Unknown provider, using custom settings")
        
        # Check for common mistakes
        url_lower = url.lower()
        
        # Detect chat API URL being used for embeddings
        if any(x in url_lower for x in ['/chat/completions', '/compatible-mode', '/v1/chat']):
            warnings.append("This appears to be a chat/completion API URL, not an embeddings API URL")
            suggestions.append(f"Recommended URL for {provider.name_zh}: {provider.default_url}")
        
        # Check for missing protocol
        if not url.startswith(('http://', 'https://')):
            warnings.append("URL is missing protocol (http:// or https://)")
            suggestions.append("Will auto-add https:// prefix")
        
        # Format URL
        formatted_url = provider.get_formatted_url(url)
        
        # Validate URL structure
        try:
            parsed = urlparse(formatted_url)
            if not parsed.netloc:
                return {
                    'valid': False,
                    'formatted_url': formatted_url,
                    'provider': provider_key,
                    'warnings': ['Invalid URL format'],
                    'suggestions': ['Please check the URL format']
                }
        except Exception as e:
            return {
                'valid': False,
                'formatted_url': formatted_url,
                'provider': provider_key,
                'warnings': [f'URL parsing error: {str(e)}'],
                'suggestions': ['Please provide a valid URL']
            }
        
        # Add suggestion if URL was changed
        if formatted_url != url.rstrip('/'):
            suggestions.append(f"URL auto-formatted to: {formatted_url}")
        
        return {
            'valid': True,
            'formatted_url': formatted_url,
            'provider': provider_key,
            'warnings': warnings,
            'suggestions': suggestions
        }


# Global registry instance
provider_registry = EmbeddingProviderRegistry()
