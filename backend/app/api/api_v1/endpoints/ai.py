"""
AI 诊断 API 端点 - 完整工作流集成
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import uuid
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, MedicalDocument, PatientChronicCondition, ChronicDisease
from app.services.ai_service import ai_service
from app.services.patient_service import PatientService
from app.services.medical_case_service import MedicalCaseService
from app.core.config import settings
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ComprehensiveDiagnosisRequest(BaseModel):
    """完整诊断请求"""
    symptoms: str
    severity: str = "moderate"
    duration: Optional[str] = None
    onset_time: Optional[str] = None
    triggers: Optional[str] = None
    previous_diseases: Optional[str] = None
    uploaded_files: Optional[List[str]] = []
    document_ids: Optional[List[uuid.UUID]] = []
    disease_category: str = "respiratory"
    language: str = "zh"
    case_id: Optional[uuid.UUID] = None
    share_with_doctor: bool = False
    doctor_id: Optional[uuid.UUID] = None  # 保留单医生字段用于向后兼容
    doctor_ids: Optional[List[uuid.UUID]] = []  # 支持同时@多个医生


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


async def create_shared_case(db: AsyncSession, medical_case, patient: User):
    """
    创建共享病例记录供医生浏览
    Create shared case record for doctors to browse
    """
    from app.models.models import SharedMedicalCase, DataSharingConsent
    from datetime import datetime
    from sqlalchemy import select
    
    stmt = select(SharedMedicalCase).where(
        SharedMedicalCase.original_case_id == medical_case.id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.visible_to_doctors = True
        existing.anonymized_symptoms = medical_case.symptoms
        existing.anonymized_diagnosis = medical_case.diagnosis or 'AI诊断结果'
        await db.commit()
        logger.info(f"更新共享病例: {existing.id}")
        return existing

    consent = DataSharingConsent(
        patient_id=patient.id,
        share_type='platform_anonymous',
        consent_version='1.0',
        consent_text='患者同意将匿名化后的诊断信息共享给认证医生用于医疗咨询和学术研究。',
        ip_address='127.0.0.1',  # TODO: Get actual client IP from request
        is_active=True
    )
    db.add(consent)
    await db.flush()

    shared_case = SharedMedicalCase(
        original_case_id=medical_case.id,
        consent_id=consent.id,
        visible_to_doctors=True,
        visible_for_research=True,
        anonymized_symptoms=medical_case.symptoms,
        anonymized_diagnosis=medical_case.diagnosis or 'AI诊断结果',
        anonymous_patient_profile={
            'age_range': '30-40岁' if patient.date_of_birth else '未知',
            'gender': patient.gender or '未知',
            'city_tier': '一线城市'
        },
        view_count=0
    )
    db.add(shared_case)
    await db.commit()
    await db.refresh(shared_case)
    
    logger.info(f"创建共享病例成功: {shared_case.id}, 原病例: {medical_case.id}")
    return shared_case


async def share_case_with_doctor(db: AsyncSession, medical_case, patient: User, doctor_id: uuid.UUID):
    """
    将病例分享给特定医生
    Share case with specific doctor
    """
    from app.models.models import SharedMedicalCase, DataSharingConsent, DoctorPatientRelation
    from app.services.pii_cleaner_service import PIICleanerService
    from datetime import datetime, timedelta
    from sqlalchemy import select, and_
    
    pii_cleaner = PIICleanerService()
    
    # 为@提及医生创建独立的私有共享病例记录
    # 无论是否存在公开共享记录，都创建新的私有记录
    valid_until = datetime.utcnow() + timedelta(days=365)
    
    consent = DataSharingConsent(
        patient_id=patient.id,
        share_type='to_specific_doctor',
        target_doctor_id=doctor_id,
        consent_version='1.0',
        consent_text='患者同意将诊断信息共享给指定的医生，分享内容将自动脱敏处理。',
        valid_until=valid_until,
        ip_address='127.0.0.1'
    )
    db.add(consent)
    await db.flush()
    
    def create_anonymous_profile_v2(patient_user: User):
        if patient_user.role != 'patient':
            return {}
        return patient_user.generate_anonymous_profile()
    
    anonymous_profile = create_anonymous_profile_v2(patient)
    
    async def clean_medical_content_v2(content):
        if not content:
            return None
        try:
            result = pii_cleaner.clean_text(content)
            return result["cleaned_text"]
        except Exception:
            return content
    
    anonymized_symptoms = await clean_medical_content_v2(medical_case.symptoms)
    anonymized_diagnosis = await clean_medical_content_v2(medical_case.diagnosis)

    # 创建新的私有共享病例记录（专门用于@提及）
    shared_case = SharedMedicalCase(
        original_case_id=medical_case.id,
        consent_id=consent.id,
        anonymous_patient_profile=anonymous_profile,
        anonymized_symptoms=anonymized_symptoms,
        anonymized_diagnosis=anonymized_diagnosis,
        visible_to_doctors=False,
        visible_for_research=False
    )
    db.add(shared_case)
    await db.flush()
    
    existing_relation_result = await db.execute(
        select(DoctorPatientRelation).where(
            and_(
                DoctorPatientRelation.patient_id == patient.id,
                DoctorPatientRelation.doctor_id == doctor_id,
                DoctorPatientRelation.status.in_(['pending', 'active'])
            )
        )
    )
    
    existing_relation = existing_relation_result.scalar_one_or_none()
    
    if not existing_relation:
        # 创建新的关系
        relation = DoctorPatientRelation(
            patient_id=patient.id,
            doctor_id=doctor_id,
            status="pending",
            initiated_by="patient_at",
            patient_message=f"患者在症状提交时@提及您，病例:{medical_case.title or '未命名病例'}",
            share_all_cases=False,
            shared_case_ids=[str(shared_case.id)]
        )
        db.add(relation)
    else:
        # 更新现有关系，添加新的共享病例ID
        case_id_str = str(shared_case.id)
        if existing_relation.shared_case_ids is None:
            existing_relation.shared_case_ids = []
        if case_id_str not in existing_relation.shared_case_ids:
            existing_relation.shared_case_ids.append(case_id_str)
    
    await db.commit()
    
    logger.info(f"病例已分享给医生: doctor_id={doctor_id}, case_id={medical_case.id}")
    return shared_case


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
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
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
        
        # 2. 获取预提取的文档内容（如果提供了document_ids）
        extracted_documents = []
        if request.document_ids:
            logger.info(f"Fetching {len(request.document_ids)} pre-extracted documents from database...")
            stmt = select(MedicalDocument).where(
                MedicalDocument.id.in_(request.document_ids),
                MedicalDocument.upload_status == "processed"  # 只获取已处理完成的文档
            )
            result = await db.execute(stmt)
            documents = result.scalars().all()
            
            for doc in documents:
                # Extract text content from extracted_content (handle both old string format and new object format)
                extracted_text = None
                if doc.extracted_content:
                    if isinstance(doc.extracted_content, dict):
                        # New format: {text: "...", markdown: "..."}
                        extracted_text = doc.extracted_content.get("text") or doc.extracted_content.get("markdown")
                    elif isinstance(doc.extracted_content, str):
                        # Old format: direct string
                        extracted_text = doc.extracted_content
                
                # Extract text from cleaned_content object (handle format: {text: "...", metadata: {...}})
                cleaned_text = None
                if doc.cleaned_content:
                    if isinstance(doc.cleaned_content, dict):
                        cleaned_text = doc.cleaned_content.get("text")
                    elif isinstance(doc.cleaned_content, str):
                        cleaned_text = doc.cleaned_content
                
                extracted_documents.append({
                    "id": str(doc.id),
                    "original_filename": doc.original_filename,
                    "extracted_content": extracted_text,
                    "cleaned_content": cleaned_text,
                    "pii_cleaning_status": doc.pii_cleaning_status,
                    "pii_detected": doc.pii_detected or []
                })
            
            logger.info(f"Found {len(extracted_documents)} processed documents")

        # 3. 获取患者的慢性病信息
        logger.info("Fetching patient's chronic diseases...")
        chronic_diseases = []
        try:
            stmt = select(PatientChronicCondition, ChronicDisease).join(
                ChronicDisease,
                PatientChronicCondition.disease_id == ChronicDisease.id
            ).where(
                PatientChronicCondition.patient_id == current_user.id,
                PatientChronicCondition.is_active == True
            )
            result = await db.execute(stmt)
            conditions = result.all()

            for condition, disease in conditions:
                chronic_diseases.append({
                    "id": str(disease.id),
                    "icd10_code": disease.icd10_code,
                    "icd10_name": disease.icd10_name,
                    "disease_type": disease.disease_type,
                    "severity": condition.severity,
                    "medical_notes": disease.medical_notes
                })
            logger.info(f"Found {len(chronic_diseases)} chronic diseases for patient")
        except Exception as e:
            logger.warning(f"Failed to fetch chronic diseases: {e}")

        # 4. Reload AI configuration from database before calling AI
        logger.info("Reloading AI configuration from database...")
        ai_config_reloaded = await ai_service.reload_config_from_db(db)
        if ai_config_reloaded:
            logger.info("✅ AI configuration reloaded from database")
        else:
            logger.warning("⚠️ Using fallback AI configuration from environment")

        # 5. 调用完整诊断流程（包含慢性病信息）
        result = await ai_service.comprehensive_diagnosis(
            symptoms=request.symptoms,
            patient_info=patient_info,
            duration=request.duration,
            severity=request.severity,
            uploaded_files=request.uploaded_files or [],
            disease_category=request.disease_category,
            language=request.language,
            extracted_documents=extracted_documents if extracted_documents else None,
            user_id=str(current_user.id),
            db=db,
            chronic_diseases=chronic_diseases if chronic_diseases else None
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', '诊断失败')
            )
        
        # 3. 保存诊断结果到病历记录
        medical_case = None
        try:
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
            
            # 创建病历记录 - 使用current_user.id作为patient_id
            medical_case = await case_service.create_medical_case(
                patient_id=current_user.id,
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
            # 知识库溯源信息（新增）
            "knowledge_base_sources": result.get("knowledge_base_sources", []),
            "knowledge_base_selection_reasoning": result.get("knowledge_base_selection_reasoning", ""),
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


@router.post("/comprehensive-diagnosis-stream")
async def comprehensive_diagnosis_stream(
    request: ComprehensiveDiagnosisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    完整诊断工作流（流式输出）
    
    整合：个人信息 + 诊疗提交信息(MinerU提取) + 知识库信息 -> AI诊断（流式返回）
    
    工作流程：
    1. 获取患者个人信息
    2. 提取上传文件的文本内容（MinerU）
    3. 查询相关医学知识库
    4. 整合所有信息提交给AI模型（流式输出）
    5. 返回流式诊断结果
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
        
        # 2. 获取预提取的文档内容（如果提供了document_ids）
        extracted_documents = []
        if request.document_ids:
            logger.info(f"Fetching {len(request.document_ids)} pre-extracted documents from database...")
            stmt = select(MedicalDocument).where(
                MedicalDocument.id.in_(request.document_ids),
                MedicalDocument.upload_status == "processed"  # 只获取已处理完成的文档
            )
            result = await db.execute(stmt)
            documents = result.scalars().all()

            for doc in documents:
                # Extract text content from extracted_content (handle both old string format and new object format)
                extracted_text = None
                if doc.extracted_content:
                    if isinstance(doc.extracted_content, dict):
                        # New format: {text: "...", markdown: "..."}
                        extracted_text = doc.extracted_content.get("text") or doc.extracted_content.get("markdown")
                    elif isinstance(doc.extracted_content, str):
                        # Old format: direct string
                        extracted_text = doc.extracted_content
                
                # Extract text from cleaned_content object (handle format: {text: "...", metadata: {...}})
                cleaned_text = None
                if doc.cleaned_content:
                    if isinstance(doc.cleaned_content, dict):
                        cleaned_text = doc.cleaned_content.get("text")
                    elif isinstance(doc.cleaned_content, str):
                        cleaned_text = doc.cleaned_content
                
                extracted_documents.append({
                    "id": str(doc.id),
                    "original_filename": doc.original_filename,
                    "extracted_content": extracted_text,
                    "cleaned_content": cleaned_text,
                    "pii_cleaning_status": doc.pii_cleaning_status,
                    "pii_detected": doc.pii_detected or []
                })

            logger.info(f"Found {len(extracted_documents)} processed documents")

        # 3. 获取患者的慢性病信息
        logger.info("Fetching patient's chronic diseases for streaming...")
        chronic_diseases = []
        try:
            stmt = select(PatientChronicCondition, ChronicDisease).join(
                ChronicDisease,
                PatientChronicCondition.disease_id == ChronicDisease.id
            ).where(
                PatientChronicCondition.patient_id == current_user.id,
                PatientChronicCondition.is_active == True
            )
            result = await db.execute(stmt)
            conditions = result.all()

            for condition, disease in conditions:
                chronic_diseases.append({
                    "id": str(disease.id),
                    "icd10_code": disease.icd10_code,
                    "icd10_name": disease.icd10_name,
                    "disease_type": disease.disease_type,
                    "severity": condition.severity,
                    "medical_notes": disease.medical_notes
                })
            logger.info(f"Found {len(chronic_diseases)} chronic diseases for patient (streaming)")
        except Exception as e:
            logger.warning(f"Failed to fetch chronic diseases for streaming: {e}")

        # 4. 查询知识库（在流式输出前获取，以便在结束时返回）
        from app.services.generic_rag_selector import GenericRAGSelector
        from datetime import datetime

        kb_sources = []
        kb_selection_reasoning = ""
        try:
            # 计算患者年龄
            patient_age = None
            date_of_birth_str = patient_info.get('date_of_birth')
            if date_of_birth_str and date_of_birth_str != 'None':
                try:
                    birth_date = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
                    today = datetime.now()
                    patient_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                except (ValueError, TypeError):
                    patient_age = None

            # 提取文档内容用于增强检索
            document_texts = []
            for doc in extracted_documents:
                if doc.get('cleaned_content'):
                    document_texts.append(doc['cleaned_content'])
                elif doc.get('extracted_content'):
                    document_texts.append(doc['extracted_content'])

            selector = GenericRAGSelector(db)
            rag_result = await selector.select_knowledge_bases(
                symptoms=request.symptoms,
                document_texts=document_texts,
                patient_age=patient_age,
                top_k=5,
                min_similarity=0.5
            )
            
            # 格式化知识库源信息
            for source in rag_result.get('sources', []):
                category = source.get('category', '')
                chunks_data = []
                for chunk in source.get('chunks', []):
                    chunks_data.append({
                        "chunk_id": chunk.get('chunk_id'),
                        "section_title": chunk.get('section_title', category),
                        "text_preview": chunk.get('text', '')[:200] + "..." if len(chunk.get('text', '')) > 200 else chunk.get('text', ''),
                        "similarity_score": chunk.get('similarity_score', 0),
                        "source_file": chunk.get('source_file')
                    })
                
                # 获取分类显示名称
                category_names = {
                    'respiratory': '呼吸系统疾病',
                    'cardiovascular': '心血管系统疾病',
                    'digestive': '消化系统疾病',
                    'pediatric': '儿科疾病',
                    'dermatology': '皮肤疾病',
                    'neurological': '神经系统疾病',
                    'general': '通用医学知识'
                }
                
                kb_sources.append({
                    "category": category,
                    "category_name": category_names.get(category, category),
                    "relevance_score": source.get('relevance_score', 0),
                    "selection_reason": source.get('selection_reason', ''),
                    "chunks_count": len(source.get('chunks', [])),
                    "chunks": chunks_data
                })
            
            kb_selection_reasoning = rag_result.get('selection_reasoning', '')
            logger.info(f"知识库查询完成，找到 {len(kb_sources)} 个知识源")
        except Exception as kb_error:
            logger.warning(f"流式诊断前知识库查询失败: {kb_error}")

        # 4. Reload AI configuration from database before streaming
        logger.info("Reloading AI configuration from database for streaming...")
        ai_config_reloaded = await ai_service.reload_config_from_db(db)
        if ai_config_reloaded:
            logger.info("✅ AI configuration reloaded from database for streaming")
        else:
            logger.warning("⚠️ Using fallback AI configuration from environment for streaming")

        # 6. 调用流式诊断流程（包含慢性病信息）
        async def generate_stream():
            """生成流式输出"""
            full_diagnosis = ""

            async for chunk in ai_service.comprehensive_diagnosis_stream(
                symptoms=request.symptoms,
                patient_info=patient_info,
                duration=request.duration,
                severity=request.severity,
                uploaded_files=request.uploaded_files or [],
                extracted_documents=extracted_documents if extracted_documents else None,
                disease_category=request.disease_category,
                language=request.language,
                user_id=str(current_user.id),
                db=db,
                chronic_diseases=chronic_diseases if chronic_diseases else None
            ):
                full_diagnosis += chunk
                # 发送 SSE 格式数据
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
            
            # 3. 保存诊断结果到病历记录 - 直接使用current_user.id
            try:
                case_service = MedicalCaseService(db)
                
                if request.case_id:
                    # 如果提供了case_id，更新现有病历
                    medical_case = await case_service.get_medical_case_by_id(
                        case_id=request.case_id,
                        patient_id=current_user.id
                    )
                    
                    if medical_case:
                        # 更新病历的诊断结果
                        medical_case.diagnosis = full_diagnosis
                        medical_case.status = 'completed'
                        # 设置分享权限
                        medical_case.is_shared = request.share_with_doctor
                        medical_case.share_scope = 'to_doctor' if request.share_with_doctor else 'private'
                        await db.commit()
                        await db.refresh(medical_case)
                        logger.info(f"已更新现有病历的诊断结果: {medical_case.id}, 分享权限: {request.share_with_doctor}")
                        
                        # 1. 如果用户勾选了"允许将本次诊断信息共享给医生端"，创建公开共享病例记录（所有医生可见）
                        if request.share_with_doctor:
                            await create_shared_case(db, medical_case, current_user)
                        
                        # 2. 如果用户@提及了特定医生，无论是否勾选共享，都要分享给这些医生（私有共享）
                        doctors_to_share = []
                        if request.doctor_ids:
                            doctors_to_share.extend(request.doctor_ids)
                        if request.doctor_id:
                            doctors_to_share.append(request.doctor_id)
                        
                        # 去重
                        doctors_to_share = list(set(doctors_to_share))
                        
                        for doctor_id in doctors_to_share:
                            try:
                                await share_case_with_doctor(db, medical_case, current_user, doctor_id)
                                logger.info(f"病例已@分享给指定医生: {doctor_id}")
                            except Exception as share_error:
                                logger.error(f"@分享给医生 {doctor_id} 失败: {str(share_error)}")
                    else:
                        logger.warning(f"未找到指定的病历ID: {request.case_id}，将创建新病历")
                        medical_case = None
                
                if not request.case_id or not medical_case:
                    # 创建新病历记录 - 使用current_user.id作为patient_id
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
                    
                    medical_case = await case_service.create_medical_case(
                        patient_id=current_user.id,
                        title=title,
                        symptoms=request.symptoms,
                        diagnosis=full_diagnosis,
                        severity=request.severity,
                        description=description or ""
                    )
                    
                    # 设置分享权限
                    medical_case.is_shared = request.share_with_doctor
                    medical_case.share_scope = 'to_doctor' if request.share_with_doctor else 'private'
                    await db.commit()
                    await db.refresh(medical_case)
                    
                    # AI诊断完成，更新病历状态为"已完成"
                    medical_case = await case_service.update_medical_case_status(
                        case_id=medical_case.id,
                        patient_id=current_user.id,
                        status='completed'
                    )
                    logger.info(f"病历状态已更新为'completed': {medical_case.id}, 分享权限: {request.share_with_doctor}")
                    
                    # 1. 如果用户勾选了"允许将本次诊断信息共享给医生端"，创建公开共享病例记录（所有医生可见）
                    if request.share_with_doctor:
                        await create_shared_case(db, medical_case, current_user)
                    
                    # 2. 如果用户@提及了特定医生，无论是否勾选共享，都要分享给这些医生（私有共享）
                    doctors_to_share = []
                    if request.doctor_ids:
                        doctors_to_share.extend(request.doctor_ids)
                    if request.doctor_id:
                        doctors_to_share.append(request.doctor_id)
                    
                    # 去重
                    doctors_to_share = list(set(doctors_to_share))
                    
                    for doctor_id in doctors_to_share:
                        try:
                            await share_case_with_doctor(db, medical_case, current_user, doctor_id)
                            logger.info(f"病例已@分享给指定医生: {doctor_id}")
                        except Exception as share_error:
                            logger.error(f"@分享给医生 {doctor_id} 失败: {str(share_error)}")

                # 发送完成信息
                completion_data = {
                    'done': True,
                    'case_id': str(medical_case.id),
                    'saved_to_records': True,
                    'status': 'completed',
                    'model_used': ai_service.model_id,  # 使用实际配置的模型ID
                    'tokens_used': len(full_diagnosis) * 2,  # 估算token用量
                    'created_at': medical_case.created_at.isoformat() if medical_case.created_at else datetime.utcnow().isoformat(),
                    'knowledge_base_sources': kb_sources,
                    'knowledge_base_selection_reasoning': kb_selection_reasoning
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
            except Exception as save_error:
                logger.error(f"保存病历记录失败: {str(save_error)}")
                # 保存失败不影响诊断结果返回，只是记录日志
                completion_data = {
                    'done': True,
                    'case_id': f"case-{current_user.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    'saved_to_records': False,
                    'save_error': str(save_error),
                    'knowledge_base_sources': kb_sources,
                    'knowledge_base_selection_reasoning': kb_selection_reasoning
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"流式诊断流程失败: {str(e)}")
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
