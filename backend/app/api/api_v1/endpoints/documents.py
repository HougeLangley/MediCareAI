from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.schemas.document import (
    MedicalDocumentResponse, 
    DocumentExtractionRequest,
    DocumentExtractionResponse
)
from app.services.document_service import DocumentService
from app.core.deps import get_current_active_user
from app.models.models import User
import uuid

router = APIRouter()


@router.post("/upload", response_model=MedicalDocumentResponse)
async def upload_document(
    medical_case_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicalDocumentResponse:
    document_service = DocumentService(db)
    document = await document_service.upload_document(medical_case_id, file, current_user.id)
    return document


@router.get("/case/{medical_case_id}", response_model=List[MedicalDocumentResponse])
async def get_case_documents(
    medical_case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    document_service = DocumentService(db)
    documents = await document_service.get_documents_by_case(medical_case_id, current_user.id)
    return documents


@router.get("/{document_id}", response_model=MedicalDocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicalDocumentResponse:
    document_service = DocumentService(db)
    document = await document_service.get_document_by_id(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.post("/{document_id}/extract", response_model=MedicalDocumentResponse)
async def extract_document_content(
    document_id: uuid.UUID,
    extraction_request: DocumentExtractionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MedicalDocumentResponse:
    document_service = DocumentService(db)
    document = await document_service.extract_document_content(
        document_id, extraction_request, current_user.id
    )
    return document


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    document_service = DocumentService(db)
    document = await document_service.get_document_by_id(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.upload_status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content not yet extracted"
        )
    
    return {
        "document_id": document.id,
        "extracted_content": document.extracted_content,
        "extraction_metadata": document.extraction_metadata
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    document_service = DocumentService(db)
    await document_service.delete_document(document_id, current_user.id)
    return {"message": "Document deleted successfully"}