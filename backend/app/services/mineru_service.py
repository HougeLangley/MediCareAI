import httpx
import json
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.document import DocumentExtractionRequest, DocumentExtractionResponse
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


class MinerUService:
    def __init__(self):
        self.api_url = settings.mineru_api_url
        self.token = settings.mineru_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def create_extraction_task(
        self, 
        file_path: str, 
        extraction_request: DocumentExtractionRequest
    ) -> str:
        """创建文档提取任务"""
        
        payload = {
            "file_path": file_path,
            "model_version": extraction_request.model_version,
            "ocr": extraction_request.ocr,
            "extract_tables": extraction_request.extract_tables,
            "extract_images": extraction_request.extract_images
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("task_id")
                else:
                    logger.error(f"MinerU API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create extraction task: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="MinerU API timeout"
            )
        except httpx.RequestError as e:
            logger.error(f"MinerU API request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MinerU API service unavailable"
            )

    async def get_extraction_status(self, task_id: str) -> DocumentExtractionResponse:
        """获取提取任务状态"""
        
        status_url = f"{self.api_url}/{task_id}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    status_url,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return DocumentExtractionResponse(
                        task_id=task_id,
                        status=result.get("status", "unknown"),
                        extracted_content=result.get("extracted_content"),
                        extraction_metadata=result.get("extraction_metadata"),
                        error_message=result.get("error_message")
                    )
                else:
                    logger.error(f"MinerU status check error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to get extraction status: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="MinerU API timeout"
            )
        except httpx.RequestError as e:
            logger.error(f"MinerU API request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MinerU API service unavailable"
            )

    async def wait_for_extraction_completion(
        self, 
        task_id: str, 
        max_wait_time: int = 300
    ) -> DocumentExtractionResponse:
        """等待提取任务完成"""
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                extraction_result = await self.get_extraction_status(task_id)
                
                if extraction_result.status == "completed":
                    return extraction_result
                elif extraction_result.status == "failed":
                    return extraction_result
                elif extraction_result.status in ["processing", "queued"]:
                    await asyncio.sleep(5)  # 等待5秒后再次检查
                else:
                    logger.warning(f"Unknown extraction status: {extraction_result.status}")
                    await asyncio.sleep(5)
                    
            except HTTPException as e:
                if e.status_code in [408, 503]:
                    # 超时或服务不可用，继续重试
                    await asyncio.sleep(10)
                else:
                    raise e
        
        # 超时
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Extraction task {task_id} timed out after {max_wait_time} seconds"
        )

    async def extract_document_content(
        self, 
        file_path: str, 
        extraction_request: Optional[DocumentExtractionRequest] = None
    ) -> DocumentExtractionResponse:
        """完整文档提取流程"""
        
        if extraction_request is None:
            extraction_request = DocumentExtractionRequest()
        
        # 创建提取任务
        task_id = await self.create_extraction_task(file_path, extraction_request)
        logger.info(f"Created extraction task: {task_id}")
        
        # 等待任务完成
        result = await self.wait_for_extraction_completion(task_id)
        logger.info(f"Extraction task {task_id} completed with status: {result.status}")
        
        return result

    def is_file_supported(self, filename: str) -> bool:
        """检查文件类型是否支持"""
        supported_extensions = {
            '.pdf', '.doc', '.docx', '.ppt', '.pptx', 
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'
        }
        
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in supported_extensions)

    def get_file_type(self, filename: str) -> str:
        """获取文件类型"""
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