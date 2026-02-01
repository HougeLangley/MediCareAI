from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status, UploadFile
from app.models.models import MedicalDocument, MedicalCase
from app.schemas.document import MedicalDocumentCreate, DocumentExtractionRequest
from app.services.mineru_service import MinerUService
from app.core.config import settings
from datetime import datetime
import uuid
import os
import aiofiles
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mineru_service = MinerUService()

    async def get_document_by_id(
        self, 
        document_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> MedicalDocument | None:
        """获取文档详情"""
        stmt = (
            select(MedicalDocument)
            .join(MedicalCase)
            .join(User)  # 需要添加User表的join
            .where(
                MedicalDocument.id == document_id,
                User.id == user_id
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
            .join(User)  # 需要添加User表的join
            .where(
                MedicalDocument.medical_case_id == medical_case_id,
                User.id == user_id
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
            MedicalCase.id == medical_case_id
            # 需要添加user_id过滤
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
            upload_status="uploaded"
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
        """提取文档内容"""
        
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
                extraction_request
            )

            # 更新文档记录
            if extraction_result.status == "completed":
                stmt = (
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(
                        upload_status="processed",
                        extracted_content=extraction_result.extracted_content,
                        extraction_metadata=extraction_result.extraction_metadata,
                        updated_at=datetime.utcnow()
                    )
                )
            else:
                # 提取失败
                stmt = (
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(
                        upload_status="failed",
                        extraction_metadata={
                            "error": extraction_result.error_message,
                            "task_id": extraction_result.task_id
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