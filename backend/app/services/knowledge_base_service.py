"""
知识库基础服务
支持模块化知识库加载和卸载
支持多疾病管理和未来扩展
"""
import os
import json
import logging
from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from app.db.database import get_db
from app.models.models import User, Disease

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge")


# ===============================
# 数据模型
# ===============================

class KnowledgeBaseCreate(BaseModel):
    """创建知识库基础"""
    disease_name: str = Field(..., description="疾病名称，例如：支气管哮喘")
    disease_code: str = Field(..., description="疾病代码，例如：J45")
    diseases_json: str = Field(..., description="疾病列表 JSON 文件名")
    guidelines_json: str = Field(..., description="诊疗指南 JSON 文件名")
    description: Optional[str] = Field(None, description="知识库描述")


class DiseaseInfoCreate(BaseModel):
    """创建疾病信息"""
    name: str = Field(..., description="疾病名称")
    code: str = Field(..., description="疾病代码")
    category: Optional[str] = Field(None, description="疾病分类（如：respiratory, endocrine等）")
    symptoms: List[str] = Field(..., description="症状列表")
    causes: List[str] = Field(..., description="病因列表")
    diagnosis_criteria: List[str] = Field(..., description="诊断标准")
    treatment: List[str] = Field(..., description="治疗方案")
    prevention: List[str] = Field(..., description="预防措施")
    complications: List[str] = Field(..., description="并发症")
    patient_education: List[str] = Field(..., description="患者教育要点")


class GuidelineInfoCreate(BaseModel):
    """创建指南信息"""
    name: str = Field(..., description="指南名称")
    source: str = Field(..., description="来源，例如：GINA, 中华医学会")
    year: Optional[int] = Field(None, description="年份")
    key_points: List[str] = Field(..., description="关键点")
    diagnostic_steps: List[str] = Field(..., description="诊断步骤")
    treatment_principles: List[str] = Field(..., description="治疗原则")


class KnowledgeBaseResponse(BaseModel):
    """知识库基础响应"""
    id: str
    disease_name: str
    disease_code: str
    is_active: bool
    description: Optional[str]
    version: Optional[str]
    diseases_json: str
    guidelines_json: str
    active_markers: Optional[dict] = None
    created_at: datetime
    disease_count: int
    guideline_count: int
    file_size: int


class DiseaseResponse(BaseModel):
    """疾病信息响应"""
    id: str
    name: str
    code: str
    category: Optional[str]
    symptoms: List[str]
    causes: List[str]
    diagnosis_criteria: List[str]
    treatment: List[str]
    prevention: List[str]
    complications: List[str]
    patient_education: List[str]
    guidelines_count: int


class GuidelineResponse(BaseModel):
    """指南信息响应"""
    id: str
    name: str
    source: str
    year: Optional[int]
    key_points: List[str]
    diagnostic_steps: List[str]
    treatment_principles: List[str]
    guidelines_count: int


class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应"""
    bases: List[KnowledgeBaseResponse]
    total: int


# ===============================
# 知识库加载器
# ===============================

class ModularKnowledgeLoader:
    """模块化知识库加载器"""
    
    def __init__(self, kb_root: str):
        self.kb_root = Path(kb_root)
        self.diseases_root = self.kb_root / "diseases"
        self.guidelines_root = self.kb_root / "guidelines"
        self.active_root = self.kb_root / "active"
        self.archive_root = self.kb_root / "archive"
        self._cache: Dict[str, dict] = {}
    
    def _get_base_directory(self, disease_name: str) -> Path:
        """获取疾病目录（支持多疾病）"""
        # 标准化疾病名称（移除空格和特殊字符）
        standardized_name = disease_name.lower().replace(' ', '_').replace('-', '_')
        
        # 支持的疾病分类
        disease_categories = {
            'pediatric_bronchial_asthma': 'diseases/pediatric_bronchial_asthma',
            'adult_bronchial_asthma': 'diseases/adult_bronchial_asthma',
            'diabetes': 'diseases/diabetes',
            'hypertension': 'diseases/hypertension',
            'gastrointestinal': 'diseases/gastrointestinal',
            'respiratory': 'diseases/respiratory',
            'cardiovascular': 'diseases/cardiovascular',
            'endocrine': 'diseases/endocrine',
            'infectious': 'diseases/infectious',
            'autoimmune': 'diseases/autoimmune',
            'metabolic': 'diseases/metabolic',
            'hematological': 'diseases/hematological',
            'oncological': 'diseases/oncological',
            'neurological': 'diseases/neurological',
            'dermatological': 'diseases/dermatological',
            'rheumatological': 'diseases/rheumatological',
            'pulmonary': 'diseases/pulmonary',
            'cardiovascular': 'diseases/cardiovascular',
            'renal': 'diseases/renal',
            'hepatological': 'diseases/hepatological',
            'gastroenterological': 'diseases/gastroenterological',
            'endocrine': 'diseases/endocrine',
            'pediatric_diabetes': 'diseases/pediatric_diabetes',
            'adult_diabetes': 'diseases/adult_diabetes',
            'musculoskeletal': 'diseases/musculoskeletal',
            'neurological': 'diseases/neurological',
            'ophthalmological': 'diseases/ophthalmological',
            'otolaryngological': 'diseases/otolaryngological',
            'reproductive': 'diseases/reproductive'
        }
        
        # 从疾病名称推断目录
        if standardized_name in disease_categories:
            category_dir = self.diseases_root / standardized_name
        else:
            # 默认使用"respiratory"分类
            category_dir = self.diseases_root / "respiratory"
        
        # 检查目录是否存在
        if not category_dir.exists():
            # 使用"respiratory"分类
            category_dir = self.diseases_root / "respiratory"
        
        return category_dir
    
    def list_available_bases(self) -> List[str]:
        """列出所有可用的知识库"""
        available_bases = []
        
        # 遍历所有疾病分类目录
        for disease_dir in self.diseases_root.iterdir():
            if not disease_dir.is_dir():
                continue
            
            disease_name = disease_dir.name
            disease_json = self.diseases_root / f"{disease_name}.json"
            
            # 检查是否有有效的知识库文件
            if disease_json.exists():
                # 读取元数据
                try:
                    with open(disease_json, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        total_size = disease_json.stat().st_size
                    
                    # 获取疾病列表
                    diseases_count = len(metadata.get('diseases', []))
                    guidelines_count = len(metadata.get('guidelines', []))
                    
                    available_bases.append(disease_name)
                    
                    logger.info(f"找到知识库: {disease_name} ({diseases_count} 疾病, {guidelines_count} 指南)")
                except Exception as e:
                    logger.error(f"读取知识库元数据失败: {e}")
        
        # 按疾病名称排序
        return sorted(available_bases, reverse=False)
    
    def load_base(self, disease_name: str) -> Dict:
        """加载指定的知识库"""
        if disease_name in self._cache:
            return self._cache[disease_name]
        
        # 获取疾病目录
        category_dir = self._get_base_directory(disease_name)
        
        # 读取疾病 JSON 文件
        disease_json = category_dir / f"{disease_name}.json"
        
        if not disease_json.exists():
            raise HTTPException(
                status_code=404,
                detail=f"知识库 '{disease_name}' 未找到"
            )
        
        data = {}
        
        # 读取疾病信息
        try:
            with open(disease_json, 'r', encoding='utf-8') as f:
                disease_metadata = json.load(f)
                data['diseases'] = disease_metadata.get('diseases', [])
                data['guidelines'] = disease_metadata.get('guidelines', [])
        except Exception:
            data['diseases'] = []
            data['guidelines'] = []
        
        data['name'] = disease_name
        data['diseases_file'] = str(disease_json)
        data['guidelines_file'] = str(disease_json.parent / "guidelines.json")
        data['loaded_at'] = datetime.utcnow()
        data['disease_count'] = len(data.get('diseases', []))
        data['guideline_count'] = len(data.get('guidelines', []))
        
        # 缓存
        self._cache[disease_name] = data
        
        return data
    
    async def get_diseases(self, disease_name: str, db: AsyncSession = Depends(get_db)) -> List[DiseaseResponse]:
        """获取疾病列表"""
        if disease_name in self._cache:
            diseases_data = self._cache[disease_name].get('diseases', [])
            return [DiseaseResponse(**disease) for disease in diseases_data]
        
        # 加载知识库
        kb_data = await self.load_base(disease_name)
        
        if 'diseases' in kb_data:
            diseases = kb_data.get('diseases', [])
            return [DiseaseResponse(**disease) for disease in diseases]
        
        return []
    
    async def get_guidelines(self, disease_name: str, db: AsyncSession = Depends(get_db)) -> List[GuidelineResponse]:
        """获取诊疗指南"""
        if disease_name in self._cache:
            guidelines_data = self._cache[disease_name].get('guidelines', [])
            return [GuidelineResponse(**guideline) for guideline in guidelines_data]
        
        # 加载知识库
        kb_data = await self.load_base(disease_name)
        
        if 'guidelines' in kb_data:
            guidelines = kb_data.get('guidelines', [])
            return [GuidelineResponse(**guideline) for guideline in guidelines]
        
        return []


# ===============================
# 服务单例
# ===============================

_knowledge_loader: Optional[ModularKnowledgeLoader] = None

def get_knowledge_loader() -> ModularKnowledgeLoader:
    """获取知识库加载器单例"""
    global _knowledge_loader
    if _knowledge_loader is None:
        kb_root = "/app/data/knowledge_bases"
        _knowledge_loader = ModularKnowledgeLoader(kb_root)
    return _knowledge_loader


# ===============================
# API 端点
# ===============================

@router.get("/bases", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases(db: AsyncSession = Depends(get_db)):
    """列出所有可用的知识库"""
    loader = get_knowledge_loader()
    bases = loader.list_available_bases()
    
    return {
        "bases": bases,
        "total": len(bases),
        "message": f"找到 {len(bases)} 个可用知识库"
    }


@router.get("/bases/{disease_name}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    disease_name: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定知识库的详细信息"""
    loader = get_knowledge_loader()
    
    try:
        data = await loader.load_base(disease_name)
        
        # 获取是否激活
        active_file = loader.active_dir / f"{disease_name}.json"
        is_active = active_file.exists() if active_file else False
        
        return KnowledgeBaseResponse(
            id = f"kb-{disease_name}",
            disease_name = data.get('name', disease_name),
            disease_code = data.get('diseases_file', 'N/A').replace('/app/data/knowledge_bases/diseases/', '').replace('.json', ''),
            is_active = is_active,
            description = f"知识库包含 {data.get('disease_count', 0)} 个疾病和 {data.get('guideline_count', 0)} 个指南",
            version = "1.0.0",
            diseases_json = str(data.get('diseases_file', 'N/A')).replace('/app/data/knowledge_bases/diseases/', '').replace('.json', ''),
            guidelines_json = str(data.get('guidelines_file', 'N/A')).replace('/app/data/knowledge_bases/diseases/', '').replace('.json', ''),
            active_markers = {"activated_at": "当前会话" if is_active else None} if is_active else None,
            created_at = datetime.utcnow(),
            disease_count = data.get('disease_count', 0),
            guideline_count = data.get('guideline_count', 0),
            file_size = data.get('file_size', 0)
        )
    except Exception as e:
        logger.error(f"加载知识库失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"加载知识库失败: {str(e)}"
        )


@router.put("/bases/{disease_name}/activate", response_model=Dict)
async def activate_knowledge_base(
    disease_name: str,
    db: AsyncSession = Depends(get_db)
):
    """激活指定的知识库"""
    loader = get_knowledge_loader()
    active_dir = loader.active_dir
    
    # 检查知识库是否存在
    category_dir = loader._get_base_directory(disease_name)
    disease_json = category_dir / f"{disease_name}.json"
    
    if not disease_json.exists():
        raise HTTPException(
            status_code=404,
            detail=f"知识库 '{disease_name}' 未找到"
        )
    
    # 创建激活标记
    active_file = active_dir / f"{disease_name}.json"
    if not active_file.exists():
        active_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入激活信息
    with open(active_file, 'w', encoding='utf-8') as f:
        json.dump({
            "activated_at": datetime.utcnow().isoformat(),
            "disease_name": disease_name,
            "activated_by": "system"
        }, f, ensure_ascii=False, indent=2)
    
    # 清除缓存
    if disease_name in loader._cache:
        loader._cache[disease_name]['is_active'] = True
        loader._cache[disease_name]['active_markers'] = {
            "activated_at": datetime.utcnow().isoformat(),
            "activated_by": "system"
        }
    
    logger.info(f"知识库已激活: {disease_name}")
    
    return {
        "message": f"知识库 '{disease_name}' 已激活",
        "activated_at": datetime.utcnow().isoformat(),
        "active_markers": {
            "activated_at": datetime.utcnow().isoformat(),
            "activated_by": "system"
        }
    }


@router.put("/bases/{disease_name}/deactivate", response_model=Dict)
async def deactivate_knowledge_base(
    disease_name: str,
    db: AsyncSession = Depends(get_db)
):
    """停用指定的知识库"""
    loader = get_knowledge_loader()
    active_file = loader.active_dir / f"{disease_name}.json"
    
    # 检查知识库是否存在
    category_dir = loader._get_base_directory(disease_name)
    disease_json = category_dir / f"{disease_name}.json"
    
    if not disease_json.exists():
        raise HTTPException(
            status_code=404,
            detail=f"知识库 '{disease_name}' 未找到"
        )
    
    # 删除激活标记
    if active_file.exists():
        active_file.unlink()
    
    # 更新缓存
    if disease_name in loader._cache:
        loader._cache[disease_name]['is_active'] = False
        loader._cache[disease_name]['active_markers'] = None
    
    logger.info(f"知识库已停用: {disease_name}")
    
    return {
        "message": f"知识库 '{disease_name}' 已停用",
        "deactivated_at": datetime.utcnow().isoformat(),
        "active_markers": None
    }


# ===============================
# 初始化
# ===============================

# 启动时打印模块信息
@router.on_event("startup")
async def startup_event():
    logger.info("知识库服务已启动")
    logger.info(f"知识库根目录: {get_knowledge_loader().kb_root}")
    logger.info("模块化知识库系统已初始化")
