from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status, UploadFile
from app.models.models import MedicalDocument, MedicalCase, User
from app.schemas.document import MedicalDocumentCreate, DocumentExtractionRequest
from app.services.mineru_service import MinerUService
from app.services.pii_cleaner_service import pii_cleaner
from app.core.config import settings
from datetime import datetime
import uuid
import os
import aiofiles
import logging
import json

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Pass db session to MinerUService for dynamic configuration from database
        self.mineru_service = MinerUService(db=db)

    async def get_document_by_id(
        self, 
        document_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> MedicalDocument | None:
        """获取文档详情"""
        stmt = (
            select(MedicalDocument)
            .join(MedicalCase)
            .where(
                MedicalDocument.id == document_id,
                MedicalCase.patient_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_documents_by_case(
        self, 
        medical_case_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> list[MedicalDocument]:
        """获取病例的所有文档"""
        stmt = (
            select(MedicalDocument)
            .join(MedicalCase)
            .where(
                MedicalDocument.medical_case_id == medical_case_id,
                MedicalCase.patient_id == user_id
            )
            .order_by(MedicalDocument.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def upload_document(
        self, 
        medical_case_id: uuid.UUID, 
        file: UploadFile,
        user_id: uuid.UUID
    ) -> MedicalDocument:
        """上传文档"""
        
        # 验证医疗案例是否属于当前用户
        case_stmt = select(MedicalCase).where(
            MedicalCase.id == medical_case_id,
            MedicalCase.patient_id == user_id
        )
        case_result = await self.db.execute(case_stmt)
        medical_case = case_result.scalar_one_or_none()
        
        if not medical_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical case not found"
            )

        # 验证文件类型
        if not self.mineru_service.is_file_supported(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not supported"
            )

        # 验证文件大小
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds limit of {settings.max_file_size} bytes"
            )

        # 生成文件名和路径
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.upload_path, unique_filename)
        
        # 确保上传目录存在
        os.makedirs(settings.upload_path, exist_ok=True)

        # 保存文件
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving file"
            )

        # 创建文档记录
        medical_document = MedicalDocument(
            medical_case_id=medical_case_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_type=self.mineru_service.get_file_type(file.filename),
            file_size=file.size,
            file_path=file_path,
            upload_status="uploaded",
            pii_cleaning_status="pending"  # PII清理状态
        )

        try:
            self.db.add(medical_document)
            await self.db.commit()
            await self.db.refresh(medical_document)
            return medical_document
        except Exception as e:
            # 如果数据库操作失败，删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating document record"
            )

    async def extract_document_content(
        self, 
        document_id: uuid.UUID,
        extraction_request: DocumentExtractionRequest,
        user_id: uuid.UUID
    ) -> MedicalDocument:
        """提取文档内容（包含PII清理）"""
        
        # 获取文档
        document = await self.get_document_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # 检查文档状态
        if document.upload_status not in ["uploaded", "processed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is not ready for extraction"
            )

        # 更新状态为处理中
        stmt = (
            update(MedicalDocument)
            .where(MedicalDocument.id == document_id)
            .values(upload_status="processing")
        )
        await self.db.execute(stmt)
        await self.db.commit()

        try:
            # 调用MinerU API提取内容
            extraction_result = await self.mineru_service.extract_document_content(
                document.file_path, 
                extract_tables=getattr(extraction_request, 'extract_tables', True),
                extract_images=getattr(extraction_request, 'extract_images', False),
                ocr=getattr(extraction_request, 'ocr', True)
            )

            # PII清理：自动清理提取的内容
            pii_cleaning_result = None
            if extraction_result.get("status") == "completed" and extraction_result.get("text_content"):
                logger.info(f"Starting PII cleaning for document {document_id}")
                
                # 获取原始提取的文本内容
                extracted_text = extraction_result.get("text_content", "")
                
                # 执行PII清理
                pii_cleaning_result = pii_cleaner.clean_text(extracted_text)
                
                logger.info(f"PII cleaning completed: {len(pii_cleaning_result['pii_detected'])} items detected, "
                          f"confidence: {pii_cleaning_result['confidence_score']:.2f}")

            # 更新文档记录
            if extraction_result.get("status") == "completed":
                update_values = {
                    "upload_status": "processed",
                    "extracted_content": extraction_result.get("data"),
                    "extraction_metadata": extraction_result.get("extraction_metadata"),
                    "updated_at": datetime.utcnow()
                }
                
                # 添加PII清理结果
                if pii_cleaning_result:
                    update_values["cleaned_content"] = {
                        "text": pii_cleaning_result["cleaned_text"],
                        "metadata": {
                            "stats": pii_cleaning_result["cleaning_stats"],
                            "confidence": pii_cleaning_result["confidence_score"]
                        }
                    }
                    update_values["pii_cleaning_status"] = "completed"
                    update_values["pii_detected"] = pii_cleaning_result["pii_detected"]
                    update_values["cleaning_confidence"] = pii_cleaning_result["confidence_score"]
                
                stmt = (
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(**update_values)
                )
            else:
                # 提取失败
                stmt = (
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(
                        upload_status="failed",
                        pii_cleaning_status="failed",
                        extraction_metadata={
                            "error": extraction_result.get("error", "Unknown error"),
                            "code": extraction_result.get("code")
                        },
                        updated_at=datetime.utcnow()
                    )
                )

            await self.db.execute(stmt)
            await self.db.commit()

            # 重新获取更新后的文档
            await self.db.refresh(document)
            return document

        except Exception as e:
            logger.error(f"Error extracting document content: {e}")
            
            # 更新状态为失败
            stmt = (
                update(MedicalDocument)
                .where(MedicalDocument.id == document_id)
                .values(
                    upload_status="failed",
                    pii_cleaning_status="failed",
                    extraction_metadata={"error": str(e)},
                    updated_at=datetime.utcnow()
                )
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error extracting document content"
            )

    async def get_document_with_pii_status(
        self, 
        document_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> dict:
        """获取文档详情（包含PII清理状态）"""
        
        document = await self.get_document_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # 构建返回数据
        result = {
            "id": str(document.id),
            "medical_case_id": str(document.medical_case_id),
            "filename": document.filename,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "upload_status": document.upload_status,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None,
            
            # PII清理状态
            "pii_cleaning": {
                "status": document.pii_cleaning_status,
                "confidence": document.cleaning_confidence,
                "pii_detected_count": len(document.pii_detected) if document.pii_detected else 0,
                "pii_types": list(set([pii.get("type") for pii in document.pii_detected])) if document.pii_detected else []
            }
        }

        # 根据状态添加提取内容
        if document.upload_status == "processed":
            result["extracted_content"] = document.extracted_content
            result["cleaned_content"] = document.cleaned_content
            
            # 详细的PII检测信息
            if document.pii_detected:
                result["pii_cleaning"]["details"] = [
                    {
                        "type": pii.get("type"),
                        "replacement": pii.get("replacement"),
                        "confidence": pii.get("confidence")
                    }
                    for pii in document.pii_detected
                ]

        return result

    async def delete_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """删除文档"""
        
        document = await self.get_document_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # 删除文件
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.warning(f"Error deleting file {document.file_path}: {e}")

        # 删除数据库记录
        try:
            await self.db.delete(document)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting document record: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting document"
            )
