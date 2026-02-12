"""
MinerU Service - Dynamic Configuration Version
Uses runtime configuration from database with environment fallback
"""

import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.temp_file_hosting import TemporaryFileHosting
from app.services.oss_service import os_service
from app.services.dynamic_config_service import (
    DynamicConfigService, 
    get_mineru_token_sync,
    get_mineru_api_url_sync
)
import logging
import asyncio
import os

logger = logging.getLogger(__name__)


class MinerUService:
    """
    MinerU Document Extraction Service with Dynamic Configuration
    
    Uses MinerU API for extracting text from documents and images.
    Configuration is read dynamically from database (priority) or environment.
    
    API Endpoint: https://mineru.net/api/v4/extract/task
    """
    
    def __init__(self, db: Optional[Any] = None):
        """
        Initialize MinerU Service
        
        Args:
            db: Optional database session. If provided, will read config from DB.
                If None, uses sync fallback to environment/settings.
        """
        self.db = db
        self._api_url: Optional[str] = None
        self._token: Optional[str] = None
        self._source: Optional[str] = None
    
    async def _refresh_config(self) -> Dict[str, str]:
        """
        Refresh configuration from database or environment
        
        Returns:
            Dict with 'api_url', 'token', and 'source'
        """
        if self.db:
            # Use async DB service
            config = await DynamicConfigService.get_mineru_config(self.db)
            self._api_url = config["api_url"]
            self._token = config["token"]
            self._source = config["source"]
        else:
            # Use sync fallback
            self._api_url = get_mineru_api_url_sync()
            self._token = get_mineru_token_sync()
            self._source = "sync_fallback"
        
        return {
            "api_url": self._api_url,
            "token": self._token,
            "source": self._source
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with current token"""
        token = self._token or get_mineru_token_sync()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _get_api_url(self) -> str:
        """Get API URL"""
        return self._api_url or get_mineru_api_url_sync()

    async def extract_document_content(
        self, 
        file_path: str,
        extract_tables: bool = True,
        extract_images: bool = False,
        ocr: bool = True,
        wait_for_completion: bool = True,
        max_wait_time: int = 120
    ) -> Dict[str, Any]:
        """
        Extract document content using MinerU API
        
        Args:
            file_path: Local file path or URL to document
            extract_tables: Whether to extract tables
            extract_images: Whether to extract images
            ocr: Whether to use OCR for images
            wait_for_completion: Whether to wait for extraction to complete
            max_wait_time: Maximum time to wait for completion (seconds)
            
        Returns:
            Dict with extraction results including text content
        """
        try:
            # Refresh configuration before extraction
            config = await self._refresh_config()
            
            if not config["token"]:
                logger.error("❌ MinerU token not configured")
                return {
                    "success": False,
                    "status": "failed",
                    "error": "MinerU API token not configured. Please set it in Admin > AI Model Settings.",
                    "code": "NOT_CONFIGURED"
                }
            
            logger.info(f"🔑 Using MinerU config from: {config['source']}")
            
            # Check if it's a local file or URL
            if os.path.exists(file_path):
                # Local file - need to get public URL
                logger.info(f"Processing local file: {file_path}")
                public_url = None
                
                # Priority 1: Try Alibaba Cloud OSS (recommended for production)
                if os_service.is_configured():
                    logger.info("🔄 Trying Alibaba Cloud OSS...")
                    public_url = await os_service.upload_and_get_url(file_path, expiration=3600)
                    if public_url:
                        logger.info(f"✅ OSS upload successful: {public_url[:50]}...")
                else:
                    logger.warning("⚠️ OSS not configured, skipping")
                
                # Priority 2: Try external temporary hosting services
                if not public_url:
                    logger.info("🔄 Trying temporary file hosting services...")
                    public_url = await TemporaryFileHosting.get_public_url(file_path)
                    if public_url:
                        logger.info(f"✅ Temporary hosting successful: {public_url[:50]}...")
                
                # Priority 3: Use local file server as fallback (if configured)
                if not public_url:
                    logger.warning("⚠️ External hosting failed, trying local file server fallback")
                    file_name = os.path.basename(file_path)
                    base_url = getattr(settings, 'public_file_url', None)
                    if base_url:
                        public_url = f"{base_url.rstrip('/')}/{file_name}"
                        logger.info(f"✅ Using local file server: {public_url}")
                    else:
                        return {
                            "success": False,
                            "status": "failed",
                            "error": "Failed to get public URL for file. Please configure OSS or PUBLIC_FILE_URL."
                        }
                
                file_data = public_url
            else:
                # Assume it's already a URL
                file_data = file_path
                logger.info(f"Using provided URL: {file_data[:50]}...")
            
            # Step 1: Submit extraction task
            api_url = self._get_api_url()
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "extract_type": "parse",
                    "url": file_data,
                    "ocr": ocr,
                    "extract_tables": extract_tables,
                    "extract_images": extract_images
                }
                
                logger.info(f"📤 Submitting extraction task to MinerU API...")
                
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 401:
                    error_detail = response.json() if response.text else {}
                    error_msg = error_detail.get('msg', 'Unauthorized')
                    logger.error(f"❌ MinerU API 401 Unauthorized: {error_msg}")
                    
                    # Check if token is from DB or environment
                    if self._source == "database":
                        error_text = "MinerU API token from database is expired or invalid. Please update it in Admin > AI Model Settings."
                    else:
                        error_text = "MinerU API token is expired or invalid. Please update MINERU_TOKEN in admin settings or .env file."
                    
                    return {
                        "success": False,
                        "status": "failed",
                        "error": error_text,
                        "code": 401,
                        "detail": error_msg
                    }
                
                if response.status_code != 200:
                    logger.error(f"MinerU API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "status": "failed",
                        "error": f"API error: {response.status_code}",
                        "detail": response.text
                    }
                
                result = response.json()
                if result.get('code') != 0:
                    error_msg = result.get('msg', 'Unknown error')
                    logger.error(f"MinerU API error: code={result.get('code')}, msg={error_msg}")
                    return {
                        "success": False,
                        "status": "failed",
                        "error": error_msg,
                        "code": result.get('code')
                    }
                
                task_id = result.get('data', {}).get('task_id')
                logger.info(f"✅ MinerU task created: {task_id}")
                
                # Step 2: Wait for completion and download result
                if wait_for_completion and task_id:
                    return await self._wait_and_download_result(
                        task_id, extract_tables, extract_images, ocr, max_wait_time
                    )
                else:
                    # Return task info only
                    return {
                        "success": True,
                        "status": "submitted",
                        "task_id": task_id,
                        "data": result.get('data', {})
                    }

        except httpx.TimeoutException:
            logger.error("MinerU API timeout")
            return {"success": False, "status": "failed", "error": "Request timeout"}
        except Exception as e:
            logger.error(f"MinerU API error: {str(e)}")
            return {"success": False, "status": "failed", "error": str(e)}
    
    async def _wait_and_download_result(
        self, 
        task_id: str, 
        extract_tables: bool,
        extract_images: bool,
        ocr: bool,
        max_wait_time: int = 120
    ) -> Dict[str, Any]:
        """
        Wait for MinerU task completion and download result
        """
        import zipfile
        import io
        
        api_url = self._get_api_url()
        headers = self._get_headers()
        task_url = f"{api_url}/{task_id}"
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Poll for task completion
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait_time:
                    logger.warning(f"⏱️ Timeout waiting for task {task_id}")
                    return {
                        "success": True,
                        "status": "processing",
                        "task_id": task_id,
                        "error": "Timeout waiting for extraction completion"
                    }
                
                # Check task status
                status_response = await client.get(task_url, headers=headers)
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result.get('code') == 0:
                        state = status_result.get('data', {}).get('state')
                        
                        if state == 'done':
                            # Task completed, download result
                            zip_url = status_result.get('data', {}).get('full_zip_url')
                            if zip_url:
                                logger.info(f"📥 Downloading extraction result from {zip_url[:60]}...")
                                
                                # Download ZIP file
                                zip_response = await client.get(zip_url, timeout=60.0)
                                if zip_response.status_code == 200:
                                    # Extract content from ZIP
                                    try:
                                        with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zf:
                                            # Find full.md file
                                            markdown_content = ""
                                            text_content = ""
                                            
                                            for filename in zf.namelist():
                                                if filename.endswith('full.md'):
                                                    markdown_content = zf.read(filename).decode('utf-8')
                                                    text_content = markdown_content  # Use markdown as text
                                                    logger.info(f"✅ Extracted content from {filename}")
                                                    break
                                            
                                            if markdown_content:
                                                return {
                                                    "success": True,
                                                    "status": "completed",
                                                    "task_id": task_id,
                                                    "text_content": text_content,
                                                    "markdown_content": markdown_content,
                                                    "extraction_metadata": {
                                                        "ocr_used": ocr,
                                                        "extract_tables": extract_tables,
                                                        "extract_images": extract_images,
                                                        "wait_time": elapsed
                                                    }
                                                }
                                            else:
                                                return {
                                                    "success": False,
                                                    "status": "failed",
                                                    "error": "No markdown content found in extraction result"
                                                }
                                    except Exception as e:
                                        logger.error(f"❌ Failed to extract ZIP: {e}")
                                        return {
                                            "success": False,
                                            "status": "failed",
                                            "error": f"Failed to extract result: {str(e)}"
                                        }
                                else:
                                    return {
                                        "success": False,
                                        "status": "failed",
                                        "error": f"Failed to download result: {zip_response.status_code}"
                                    }
                            else:
                                return {
                                    "success": False,
                                    "status": "failed",
                                    "error": "No download URL in completed task"
                                }
                        elif state == 'failed':
                            err_msg = status_result.get('data', {}).get('err_msg', 'Unknown error')
                            return {
                                "success": False,
                                "status": "failed",
                                "error": f"Extraction failed: {err_msg}"
                            }
                        else:
                            # Still processing, wait and retry
                            logger.info(f"⏳ Task {task_id} status: {state}, waiting...")
                            await asyncio.sleep(3)
                    else:
                        return {
                            "success": False,
                            "status": "failed",
                            "error": status_result.get('msg', 'Failed to check task status')
                        }
                else:
                    return {
                        "success": False,
                        "status": "failed",
                        "error": f"Failed to check task status: {status_response.status_code}"
                    }

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        return mime_types.get(ext, 'application/octet-stream')

    def is_file_supported(self, filename: str) -> bool:
        """Check if file type is supported"""
        supported_extensions = {
            '.pdf', '.doc', '.docx', '.ppt', '.pptx', 
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'
        }
        
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in supported_extensions)

    def get_file_type(self, filename: str) -> str:
        """Get file type category"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return 'pdf'
        elif filename_lower.endswith(('.doc', '.docx')):
            return 'document'
        elif filename_lower.endswith(('.ppt', '.pptx')):
            return 'presentation'
        elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')):
            return 'image'
        else:
            return 'unknown'

    async def health_check(self) -> Dict[str, Any]:
        """Check MinerU API health"""
        try:
            api_url = self._get_api_url()
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try a simple request to check if API is accessible
                response = await client.get(
                    api_url.replace('/task', '/health'),
                    headers=headers
                )
                return {
                    "healthy": response.status_code == 200,
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"MinerU health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
