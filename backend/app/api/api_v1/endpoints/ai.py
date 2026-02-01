"""
AI 诊断 API 端点 - 完整工作流集成
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User
from app.services.ai_service import ai_service
from app.services.patient_service import PatientService
from app.services.medical_case_service import MedicalCaseService

router = APIRouter()


class ComprehensiveDiagnosisRequest(BaseModel):
    """完整诊断请求"""
    symptoms: str
    severity: str = "moderate"
    duration: Optional[str] = None
    onset_time: Optional[str] = None
    triggers: Optional[str] = None
    previous_diseases: Optional[str] = None
    uploaded_files: Optional[List[str]] = []  # 文件URL列表
    disease_category: str = "respiratory"  # 疾病分类


class SymptomAnalysisRequest(BaseModel):
    """症状分析请求（向后兼容）"""
    symptoms: str
    severity: str = "moderate"
    duration: Optional[str] = None
    patient_info: Optional[Dict[str, Any]] = None


class DocumentExtractionRequest(BaseModel):
    """文档提取请求"""
    file_url: str
    extraction_type: str = "medical_report"


@router.post("/diagnose")
async def diagnose_symptoms(
    request: SymptomAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    AI 症状诊断（简化版，向后兼容）
    """
    try:
        result = await ai_service.analyze_symptoms(
            symptoms=request.symptoms,
            patient_info=request.patient_info
        )

        if "error" in result and result["error"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        return {
            "case_id": f"case-{current_user.id}",
            "diagnosis": result["diagnosis"],
            "model_used": result.get("model_used", ""),
            "tokens_used": result.get("tokens_used", 0),
            "severity": request.severity,
            "status": "completed"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"诊断失败: {str(e)}"
        )


@router.post("/comprehensive-diagnosis")
async def comprehensive_diagnosis(
    request: ComprehensiveDiagnosisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    完整诊断工作流
    
    整合：个人信息 + 诊疗提交信息(MinerU提取) + 知识库信息 -> AI诊断
    
    工作流程：
    1. 获取患者个人信息
    2. 提取上传文件的文本内容（MinerU）
    3. 查询相关医学知识库
    4. 整合所有信息提交给AI模型
    5. 返回完整诊断结果
    """
    try:
        # 1. 获取患者个人信息
        patient_service = PatientService(db)
        patients = await patient_service.get_patients_by_user(current_user.id, skip=0, limit=1)
        
        patient_info = {
            "full_name": current_user.full_name,
            "email": current_user.email
        }
        
        if patients:
            patient = patients[0]
            patient_info.update({
                "gender": patient.gender,
                "date_of_birth": str(patient.date_of_birth) if patient.date_of_birth else None,
                "phone": patient.phone,
                "address": patient.address,
                "emergency_contact": patient.emergency_contact,
                "notes": patient.notes
            })
        
        # 2. 调用完整诊断流程
        result = await ai_service.comprehensive_diagnosis(
            symptoms=request.symptoms,
            patient_info=patient_info,
            duration=request.duration,
            severity=request.severity,
            uploaded_files=request.uploaded_files or [],
            disease_category=request.disease_category
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', '诊断失败')
            )
        
        # 3. 保存诊断结果到病历记录
        medical_case = None
        try:
            if patients:
                patient = patients[0]
                case_service = MedicalCaseService(db)
                
                # 构建病历标题
                title = f"AI诊断 - {request.severity}"
                if request.duration:
                    title += f" - {request.duration}"
                
                # 构建详细描述
                description_parts = []
                if request.triggers:
                    description_parts.append(f"诱发因素: {request.triggers}")
                if request.previous_diseases:
                    description_parts.append(f"既往病史: {request.previous_diseases}")
                description = " | ".join(description_parts) if description_parts else None
                
                # 创建病历记录
                medical_case = await case_service.create_medical_case(
                    patient_id=patient.id,
                    title=title,
                    symptoms=request.symptoms,
                    diagnosis=result["diagnosis"],
                    severity=request.severity,
                    description=description or ""
                )
                logger.info(f"病历记录已创建: {medical_case.id}")
        except Exception as save_error:
            logger.error(f"保存病历记录失败: {str(save_error)}")
            # 保存失败不影响诊断结果返回，只是记录日志

        return {
            "success": True,
            "case_id": str(medical_case.id) if medical_case else f"case-{current_user.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "diagnosis": result["diagnosis"],
            "model_used": result.get("model_used", ""),
            "tokens_used": result.get("tokens_used", 0),
            "severity": request.severity,
            "duration": request.duration,
            "workflow_info": result.get("workflow", {}),
            "created_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "saved_to_records": medical_case is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完整诊断流程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"诊断失败: {str(e)}"
        )


@router.post("/extract-document")
async def extract_medical_document(
    request: DocumentExtractionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    文档内容提取

    使用 MinerU 提取医疗文档内容
    """
    try:
        result = await ai_service.extract_medical_report(request.file_url)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "文档提取失败")
            )

        return {
            "success": True,
            "extracted_data": result.get("raw_data", {}),
            "extracted_text": result.get("extracted_text", ""),
            "extraction_type": request.extraction_type
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档提取失败: {str(e)}"
        )


@router.get("/test")
async def test_ai_connection():
    """
    测试 AI 连接
    """
    try:
        # 测试 GLM-4.7-Flash
        glm_result = await ai_service.chat_with_glm([
            {"role": "user", "content": "你好，请简单自我介绍一下"}
        ])

        return {
            "glm_connection": {
                "status": "success" if glm_result.get("success") else "failed",
                "result": glm_result.get("content", glm_result.get("error"))
            }
        }

    except Exception as e:
        return {
            "glm_connection": {
                "status": "error",
                "error": str(e)
            }
        }


# 导入 datetime 用于生成 case_id
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
