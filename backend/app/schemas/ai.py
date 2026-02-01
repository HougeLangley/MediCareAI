from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class AIDiagnosisRequest(BaseModel):
    medical_case_id: uuid.UUID
    patient_info: Dict[str, Any]
    symptoms: Optional[str] = None
    clinical_findings: Optional[Dict[str, Any]] = None
    documents_content: Optional[List[Dict[str, Any]]] = None
    disease_guidelines: Optional[Dict[str, Any]] = None


class AITreatmentRequest(BaseModel):
    medical_case_id: uuid.UUID
    diagnosis: str
    severity: str
    patient_info: Dict[str, Any]
    current_medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    contraindications: Optional[List[str]] = None


class AIFollowUpRequest(BaseModel):
    medical_case_id: uuid.UUID
    current_status: str
    treatment_plan: str
    last_follow_up_notes: Optional[str] = None
    patient_compliance: Optional[str] = None


class AIResponse(BaseModel):
    response: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    recommendations: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    references: Optional[List[str]] = None


class AIFeedbackCreate(BaseModel):
    medical_case_id: uuid.UUID
    feedback_type: str = Field(..., pattern="^(diagnosis|treatment|follow_up)$")
    input_data: Dict[str, Any]
    ai_response: Dict[str, Any]
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    recommendations: Optional[str] = None
    follow_up_plan: Optional[Dict[str, Any]] = None


class AIFeedbackResponse(AIFeedbackCreate):
    id: uuid.UUID
    is_reviewed: bool
    reviewed_by: Optional[uuid.UUID] = None
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIFeedbackReview(BaseModel):
    is_approved: bool
    review_notes: Optional[str] = None


class AIFeedbackSummary(BaseModel):
    id: uuid.UUID
    feedback_type: str
    confidence_score: Optional[float]
    created_at: datetime
    is_reviewed: bool
    
    class Config:
        from_attributes = True