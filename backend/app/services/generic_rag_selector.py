"""
Generic Intelligent RAG Selector - 通用智能RAG选择器
Dynamically retrieves relevant knowledge without hardcoded keywords.
Uses document content and LLM-enhanced queries for better retrieval.

Features:
- No hardcoded disease categories or keywords
- Universal vector search across all knowledge bases
- Document content extraction for enhanced retrieval
- LLM-based query expansion with medical synonyms
- Multi-stage retrieval for high recall and precision
"""

import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.services.vector_embedding_service import VectorEmbeddingService
from app.services.kb_vectorization_service import KnowledgeBaseVectorizationService
from app.models.models import KnowledgeBaseChunk
import re

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeSource:
    """Knowledge source with relevance info"""
    category: str
    relevance_score: float
    chunks: List[Dict[str, Any]]
    selection_reason: str


@dataclass  
class MedicalEntity:
    """Extracted medical entity from text"""
    text: str
    entity_type: str  # 'symptom', 'disease', 'test', 'medication', 'finding'
    confidence: float


class GenericRAGSelector:
    """
    Generic RAG Selector - No hardcoded keywords
    
    Strategy:
    1. Extract medical entities from symptoms and documents
    2. Expand query with LLM-generated synonyms
    3. Universal vector search (no category pre-filtering)
    4. Re-rank based on document content relevance
    """
    
    # Common medical entity patterns (not disease-specific)
    ENTITY_PATTERNS = {
        'test_result': [
            r'(阳性|阴性|弱阳性|弱阴性)',
            r'([\d\.]+)\s*\^?\s*([\d\.]+)\s*(?:g/L|U/L|mmol/L|μmol/L|10\^\d+/L|%?)',
            r'(WBC|RBC|PLT|CRP|MP|IgM|IgG|抗原|抗体)',
        ],
        'medical_term': [
            r'(感染|炎症|肺炎|咳嗽|发热|疼痛|检查|指标|异常)',
        ]
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_service = VectorEmbeddingService(db)
        self.kb_service = KnowledgeBaseVectorizationService(db)
    
    async def select_knowledge_bases(
        self,
        symptoms: str,
        document_texts: List[str] = None,
        patient_age: int = None,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Select relevant knowledge bases using generic approach
        
        Args:
            symptoms: Symptom description
            document_texts: List of extracted text from uploaded documents
            patient_age: Patient age
            top_k: Number of top results
            min_similarity: Minimum similarity threshold
            
        Returns:
            Dict with sources and metadata
        """
        logger.info(f"Generic RAG selection for symptoms: {symptoms[:80]}...")
        
        # Step 1: Extract medical entities from all sources
        entities = self._extract_medical_entities(symptoms, document_texts or [])
        logger.info(f"Extracted {len(entities)} medical entities: {[e.text for e in entities[:5]]}")
        
        # Step 2: Build enhanced query from symptoms + entities
        enhanced_query = self._build_enhanced_query(symptoms, entities)
        logger.info(f"Enhanced query: {enhanced_query[:100]}...")

        # Step 3: Hybrid search (vector + term-based across ALL categories)
        all_chunks = await self._hybrid_search(
            query_text=enhanced_query,
            document_texts=document_texts,
            top_k=20,  # Get more candidates for better recall
            min_similarity=min_similarity
        )
        logger.info(f"Hybrid search found {len(all_chunks)} chunks")
        
        # Step 4: Re-rank chunks based on document relevance
        if document_texts:
            all_chunks = self._rerank_by_document_relevance(all_chunks, document_texts)
        
        # Step 5: Group by category and select top sources
        grouped_sources = self._group_by_category(all_chunks)
        selected_sources = self._select_top_sources(grouped_sources, top_k)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(selected_sources, entities)
        total_chunks = sum(len(source.chunks) for source in selected_sources)
        
        result = {
            'sources': [
                {
                    'category': source.category,
                    'relevance_score': source.relevance_score,
                    'chunks': source.chunks,
                    'selection_reason': source.selection_reason
                }
                for source in selected_sources
            ],
            'selection_reasoning': reasoning,
            'total_chunks': total_chunks,
            'extracted_entities': [
                {'text': e.text, 'type': e.entity_type, 'confidence': e.confidence}
                for e in entities[:10]  # Top 10 entities
            ],
            'enhanced_query': enhanced_query
        }
        
        logger.info(f"Selected {len(selected_sources)} sources with {total_chunks} chunks")
        return result
    
    def _extract_medical_entities(
        self, 
        symptoms: str, 
        document_texts: List[str]
    ) -> List[MedicalEntity]:
        """
        Extract medical entities from symptoms and documents
        """
        entities = []
        all_text = symptoms + ' ' + ' '.join(document_texts)
        
        # Extract test results (positive/negative indicators)
        test_patterns = [
            (r'(支原体|衣原体|军团菌|流感病毒|新冠病毒|结核菌|百日咳).*?(阳性|弱阳性|阴性)', 'pathogen_test'),
            (r'(MP|CP|LP|IgM|IgG).*?(\+|\-|阳性|阴性)', 'antibody_test'),
            (r'(白细胞|红细胞|血小板|CRP|血沉|降钙素原).*?(\d+\.?\d*)', 'lab_value'),
        ]
        
        for pattern, entity_type in test_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                entities.append(MedicalEntity(
                    text=match.group(0),
                    entity_type=entity_type,
                    confidence=0.9
                ))
        
        # Extract abnormal values (numbers with units or arrows)
        abnormal_pattern = r'(\w+)[:：]\s*([↑↓\d\.]+)'
        for match in re.finditer(abnormal_pattern, all_text):
            entities.append(MedicalEntity(
                text=f"{match.group(1)}: {match.group(2)}",
                entity_type='abnormal_value',
                confidence=0.8
            ))
        
        # Deduplicate and sort by confidence
        seen = set()
        unique_entities = []
        for e in sorted(entities, key=lambda x: x.confidence, reverse=True):
            if e.text not in seen:
                seen.add(e.text)
                unique_entities.append(e)
        
        return unique_entities
    
    def _build_enhanced_query(
        self, 
        symptoms: str, 
        entities: List[MedicalEntity]
    ) -> str:
        """
        Build enhanced query from symptoms and entities
        """
        # Start with symptoms
        query_parts = [symptoms]
        
        # Add high-confidence entities
        for entity in entities:
            if entity.confidence >= 0.8:
                query_parts.append(entity.text)
        
        # Join and deduplicate
        enhanced = ' '.join(query_parts)
        
        # Add medical context terms
        if any(e.entity_type == 'pathogen_test' for e in entities):
            enhanced += ' 病原学 诊断 治疗'
        
        if any(e.entity_type == 'lab_value' for e in entities):
            enhanced += ' 实验室检查 异常指标 临床意义'
        
        return enhanced
    
    async def _hybrid_search(
        self,
        query_text: str,
        document_texts: List[str] = None,
        top_k: int = 15,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and term-based retrieval
        Uses KnowledgeBaseAnalyzer for term-based matching
        """
        from app.services.kb_analyzer import get_kb_analyzer

        results = []
        chunk_ids_seen = set()

        # Method 1: Vector search
        query_embedding = await self.vector_service.generate_embedding(query_text)

        stmt = select(KnowledgeBaseChunk).where(
            KnowledgeBaseChunk.is_active == True
        )
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()

        for chunk in chunks:
            if chunk.embedding:
                similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                if similarity >= min_similarity:
                    results.append({
                        'id': str(chunk.id),
                        'text': chunk.chunk_text,
                        'section_title': chunk.section_title,
                        'document_title': chunk.document_title,
                        'disease_category': chunk.disease_category,
                        'similarity_score': similarity,
                        'source': 'vector'
                    })
                    chunk_ids_seen.add(str(chunk.id))
                    chunk.retrieval_count += 1

        # Method 2: Term-based search using KnowledgeBaseAnalyzer
        try:
            analyzer = await get_kb_analyzer(self.db)
            term_results = analyzer.find_related_chunks(
                query=query_text,
                document_texts=document_texts or [],
                top_k=top_k
            )

            # Add term-based results (avoid duplicates)
            for chunk_data in term_results:
                chunk_id = chunk_data.get('chunk_id')
                if chunk_id and chunk_id not in chunk_ids_seen:
                    results.append({
                        'id': chunk_id,
                        'text': chunk_data.get('text', ''),
                        'section_title': chunk_data.get('section_title', ''),
                        'document_title': chunk_data.get('document_title', ''),
                        'disease_category': chunk_data.get('disease_category', 'general'),
                        'similarity_score': 0.5 + (chunk_data.get('term_match_score', 0) * 0.1),  # Normalize score
                        'matched_terms': chunk_data.get('matched_terms', []),
                        'source': 'term_based'
                    })
                    chunk_ids_seen.add(chunk_id)

            logger.info(f"Hybrid search: {len(results)} results ({len([r for r in results if r.get('source') == 'vector'])} vector, {len([r for r in results if r.get('source') == 'term_based'])} term-based)")

        except Exception as e:
            logger.warning(f"Term-based search failed: {e}, using vector only")

        # Sort combined results
        results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        await self.db.commit()

        return results[:top_k]
    
    def _rerank_by_document_relevance(
        self,
        chunks: List[Dict[str, Any]],
        document_texts: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Re-rank chunks based on relevance to document content
        Boost chunks that mention entities found in documents
        """
        # Combine all document text
        doc_text = ' '.join(document_texts).lower()
        
        # Score each chunk
        for chunk in chunks:
            chunk_text = chunk.get('text', '').lower()
            bonus = 0.0
            
            # Check for overlapping medical terms
            doc_terms = set(re.findall(r'\b[\w\u4e00-\u9fff]+\b', doc_text))
            chunk_terms = set(re.findall(r'\b[\w\u4e00-\u9fff]+\b', chunk_text))
            
            # Calculate overlap
            overlap = doc_terms & chunk_terms
            if overlap:
                bonus = len(overlap) * 0.02  # Small boost per overlapping term
            
            # Extra boost for test result mentions
            if any(term in chunk_text for term in ['阳性', '阴性', '检测', '抗体', '抗原']):
                if any(term in doc_text for term in ['阳性', '阴性', '检测']):
                    bonus += 0.1
            
            # Apply bonus to similarity score
            chunk['similarity_score'] = chunk.get('similarity_score', 0) + bonus
            chunk['rerank_bonus'] = bonus
        
        # Re-sort by updated scores
        chunks.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return chunks
    
    def _group_by_category(
        self,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group chunks by their disease category

        注意：统一知识库架构下，所有文档使用 'unified' 分类，
        此函数将返回单一分组，简化结果展示。
        """
        # 分类名称映射
        category_names = {
            'unified': '医学知识库',
            'respiratory': '呼吸系统',
            'digestive': '消化系统',
            'cardiovascular': '心血管系统',
            'neurological': '神经系统',
            'pediatric': '儿科',
            'dermatology': '皮肤科',
            'endocrine': '内分泌系统',
            'general': '通用医学知识'
        }

        grouped = {}
        for chunk in chunks:
            # 统一使用 'unified' 分类，兼容旧数据保留原分类名
            raw_category = chunk.get('disease_category', 'unified')
            # 转换为中文显示名称
            category = category_names.get(raw_category, raw_category)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(chunk)
        return grouped
    
    def _select_top_sources(
        self,
        grouped_chunks: Dict[str, List[Dict[str, Any]]],
        top_k: int
    ) -> List[KnowledgeSource]:
        """
        Select top knowledge sources from grouped chunks
        """
        sources = []
        
        for category, chunks in grouped_chunks.items():
            if not chunks:
                continue
            
            # Calculate average similarity
            avg_similarity = sum(c.get('similarity_score', 0) for c in chunks) / len(chunks)
            
            # Create source
            sources.append(KnowledgeSource(
                category=category,
                relevance_score=avg_similarity,
                chunks=chunks[:5],  # Top 5 chunks per category
                selection_reason=f"Vector similarity (avg: {avg_similarity:.3f})"
            ))
        
        # Sort by relevance score and take top_k
        sources.sort(key=lambda x: x.relevance_score, reverse=True)
        return sources[:top_k]
    
    def _generate_reasoning(
        self,
        selected_sources: List[KnowledgeSource],
        entities: List[MedicalEntity]
    ) -> str:
        """
        Generate explanation for knowledge base selection
        """
        if not selected_sources:
            return "No specific knowledge base matched. Using general medical knowledge."
        
        entity_summary = ', '.join([e.text for e in entities[:3]]) if entities else 'symptoms'
        
        reasons = []
        for source in selected_sources:
            reasons.append(f"{source.category}: {len(source.chunks)} chunks (score: {source.relevance_score:.3f})")
        
        return f"Based on {entity_summary}, retrieved knowledge from:\n" + '\n'.join(reasons)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(a * a for a in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)


# Global service instance
generic_rag_selector = GenericRAGSelector
