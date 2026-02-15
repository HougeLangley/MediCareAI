"""
Vector Embedding API Endpoints | 向量嵌入API端点
Admin-only endpoints for managing embedding models and knowledge base.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.services.vector_embedding_service import VectorEmbeddingService
from app.services.kb_vectorization_service import KnowledgeBaseVectorizationService
from app.core.deps import get_current_active_user
from app.models.models import User
import uuid

router = APIRouter()


@router.get("/configs", response_model=list[dict])
async def list_embedding_configs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """List all embedding configurations (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = VectorEmbeddingService(db)
    configs = await service.get_all_configs()
    
    return [
        {
            "id": str(config.id),
            "name": config.name,
            "provider": config.provider,
            "model_id": config.model_id,
            "vector_dimension": config.vector_dimension,
            "is_active": config.is_active,
            "is_default": config.is_default,
            "test_status": config.test_status,
            "last_tested_at": config.last_tested_at.isoformat() if config.last_tested_at else None,
            "created_at": config.created_at.isoformat() if config.created_at else None
        }
        for config in configs
    ]


@router.post("/configs", response_model=dict)
async def create_embedding_config(
    name: str,
    provider: str,
    model_id: str,
    api_url: str,
    api_key: str,
    vector_dimension: int = 1536,
    max_input_length: int = 8192,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Create new embedding configuration (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = VectorEmbeddingService(db)
    config = await service.create_config(
        name=name,
        provider=provider,
        model_id=model_id,
        api_url=api_url,
        api_key=api_key,
        vector_dimension=vector_dimension,
        max_input_length=max_input_length,
        created_by=current_user.id
    )
    
    return {
        "id": str(config.id),
        "name": config.name,
        "provider": config.provider,
        "model_id": config.model_id,
        "test_status": config.test_status,
        "message": "Configuration created. Please test the connection."
    }


@router.post("/configs/{config_id}/test", response_model=dict)
async def test_embedding_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Test embedding configuration (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = VectorEmbeddingService(db)
    result = await service.test_config(config_id)
    
    return result


@router.post("/configs/{config_id}/activate")
async def activate_embedding_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Activate embedding configuration (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = VectorEmbeddingService(db)
    await service.set_active(config_id, True)
    
    return {"message": "Configuration activated"}


@router.post("/configs/{config_id}/set-default")
async def set_default_embedding_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Set default embedding configuration (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = VectorEmbeddingService(db)
    await service.set_default(config_id)
    
    return {"message": "Configuration set as default"}


@router.delete("/configs/{config_id}")
async def delete_embedding_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete embedding configuration (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = VectorEmbeddingService(db)
    success = await service.delete_config(config_id)
    
    if success:
        return {"message": "Configuration deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )


@router.post("/knowledge-base/vectorize")
async def vectorize_knowledge_document(
    document_content: str,
    document_title: str,
    disease_category: str,
    disease_id: uuid.UUID = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Vectorize a knowledge base document (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = KnowledgeBaseVectorizationService(db)
    result = await service.vectorize_markdown_document(
        document_content=document_content,
        document_title=document_title,
        disease_category=disease_category,
        disease_id=disease_id,
        source_type='disease_guideline',
        created_by=current_user.id
    )
    
    return result


@router.get("/knowledge-base/statistics")
async def get_kb_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get knowledge base vectorization statistics (Admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = KnowledgeBaseVectorizationService(db)
    stats = await service.get_chunk_statistics()
    
    return stats


@router.post("/knowledge-base/search")
async def search_knowledge_base(
    query: str,
    disease_category: str = None,
    top_k: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """Search knowledge base using vector similarity"""
    # Allow all authenticated users to search
    service = KnowledgeBaseVectorizationService(db)
    results = await service.search_similar_chunks(
        query_text=query,
        disease_category=disease_category,
        top_k=top_k,
        min_similarity=0.6
    )

    return results


@router.post("/knowledge-base/build-indices")
async def build_kb_indices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Build adaptive indices from knowledge base content (Admin only).

    This analyzes all knowledge base documents and builds dynamic term indices
    for enhanced retrieval. Should be called after adding new documents.
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    from app.services.kb_analyzer import refresh_kb_indices

    try:
        stats = await refresh_kb_indices(db)
        return {
            "success": True,
            "message": "Knowledge base indices built successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build indices: {str(e)}"
        )


@router.get("/knowledge-base/indices-stats")
async def get_kb_indices_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get knowledge base analyzer statistics (Admin only).

    Returns statistics about the dynamic term indices.
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    from app.services.kb_analyzer import get_kb_analyzer

    try:
        analyzer = await get_kb_analyzer(db)
        stats = analyzer.export_index_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
