from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentExtractionRequest(BaseModel):
    model_version: str = "vlm"  # 用于PDF/DOC/PPT/图片
    ocr: bool = True
    extract_tables: bool = True
    extract_images: bool = True


class DocumentExtractionResponse(BaseModel):
    task_id: str
    status: str
    extracted_content: Optional[Dict[str, Any]] = None
    extraction_metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class DocumentContent(BaseModel):
    filename: str
    content_type: str
    text_content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[Dict[str, Any]]] = None


class MedicalDocumentCreate(BaseModel):
    medical_case_id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    file_path: str


class MedicalDocumentResponse(MedicalDocumentCreate):
    id: uuid.UUID
    upload_status: str
    extracted_content: Optional[Dict[str, Any]]
    extraction_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True