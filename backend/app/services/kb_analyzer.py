"""
Adaptive Knowledge Base Analyzer - 自适应知识库分析器
Automatically analyzes knowledge base content and builds dynamic retrieval indices.

Features:
- Automatic term extraction from knowledge base documents
- Dynamic keyword-to-document mapping
- Periodic index rebuilding
- Content-aware retrieval enhancement
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.models import KnowledgeBaseChunk
import jieba
import jieba.posseg as pseg

logger = logging.getLogger(__name__)


class KnowledgeBaseAnalyzer:
    """
    Analyzes knowledge base content and builds dynamic indices
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._term_index: Dict[str, List[Dict]] = defaultdict(list)
        self._document_terms: Dict[str, Set[str]] = {}
        self._medical_vocab: Set[str] = set()
    
    async def build_indices(self) -> Dict[str, Any]:
        """
        Build dynamic indices from all knowledge base content
        """
        logger.info("🏗️ Building adaptive knowledge base indices...")
        
        # Get all active chunks
        stmt = select(KnowledgeBaseChunk).where(KnowledgeBaseChunk.is_active == True)
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()
        
        logger.info(f"Analyzing {len(chunks)} knowledge base chunks...")
        
        # Clear existing indices
        self._term_index.clear()
        self._document_terms.clear()
        self._medical_vocab.clear()
        
        # Analyze each chunk
        for chunk in chunks:
            await self._analyze_chunk(chunk)
        
        # Build statistics
        stats = {
            'total_chunks': len(chunks),
            'unique_terms': len(self._term_index),
            'medical_terms': len(self._medical_vocab),
            'top_terms': self._get_top_terms(20)
        }
        
        logger.info(f"✅ Index building complete: {stats['unique_terms']} terms, "
                   f"{stats['medical_terms']} medical terms")
        
        return stats
    
    async def _analyze_chunk(self, chunk: KnowledgeBaseChunk):
        """
        Analyze a single chunk and extract terms
        """
        text = chunk.chunk_text or ""
        if not text:
            return
        
        # Extract medical terms using multiple methods
        terms = self._extract_medical_terms(text)
        
        # Store term-to-chunk mapping
        chunk_ref = {
            'chunk_id': str(chunk.id),
            'text': text[:200],  # Store preview
            'section_title': chunk.section_title,
            'document_title': chunk.document_title,
            'disease_category': chunk.disease_category,
            'similarity_boost': 0
        }
        
        for term in terms:
            self._term_index[term].append(chunk_ref)
            self._medical_vocab.add(term)
        
        # Store document-level terms
        doc_key = f"{chunk.document_title}_{chunk.disease_category}"
        if doc_key not in self._document_terms:
            self._document_terms[doc_key] = set()
        self._document_terms[doc_key].update(terms)
    
    def _extract_medical_terms(self, text: str) -> Set[str]:
        """
        Extract medical terms from text using multiple strategies
        """
        terms = set()
        
        # 1. Extract disease names (疾病名称模式)
        disease_patterns = [
            r'([^，。\n]{2,20}(?:炎|病|症|征|癌|瘤|毒|菌|虫|缺乏|亢进|减退|综合征|综合症))',
            r'([^，。\n]{2,15}(?:肺炎|肝炎|肾炎|胃炎|肠炎|脑炎|心肌炎|关节炎))',
            r'(急性|慢性|轻度|中度|重度|原发|继发)?[^，。\n]{2,10}(?:感染|出血|栓塞|梗死|坏死)',
        ]
        
        for pattern in disease_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group(0).strip()
                if len(term) >= 2 and len(term) <= 20:
                    terms.add(term)
        
        # 2. Extract symptoms (症状模式)
        symptom_patterns = [
            r'(咳嗽|咳痰|发热|发烧|胸痛|腹痛|头痛|头晕|恶心|呕吐|腹泻|便秘|皮疹|瘙痒|出血|水肿|休克)',
            r'([\w\u4e00-\u9fff]{2,8}(?:痛|痒|胀|麻|木|酸|沉|晕|咳|喘|烧|热|寒|抖))',
        ]
        
        for pattern in symptom_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                terms.add(match.group(0).strip())
        
        # 3. Extract lab/test indicators (检验指标)
        lab_patterns = [
            r'(白细胞|红细胞|血小板|血红蛋白|CRP|PCT|血沉|ALT|AST|肌酐|尿素氮|血糖|血脂)',
            r'(IgM|IgG|IgA|抗原|抗体|核酸|培养|药敏)',
            r'(阳性|阴性|弱阳性|弱阴性|正常|异常|升高|降低)',
        ]
        
        for pattern in lab_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                terms.add(match.group(0).strip())
        
        # 4. Extract treatment terms (治疗相关)
        treatment_patterns = [
            r'(抗生素|抗病毒|激素|免疫抑制剂|化疗|放疗|手术|输液|吸氧|监护)',
            r'(青霉素|头孢|阿奇|红霉素|甲强龙|地塞米松|布地奈德)',
            r'(治疗|用药|剂量|疗程|静脉|口服|皮下|吸入)',
        ]
        
        for pattern in treatment_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                terms.add(match.group(0).strip())
        
        # 5. Extract pathogens (病原体)
        pathogen_patterns = [
            r'(支原体|衣原体|军团菌|百日咳|结核|流感|新冠|新冠|RSV|腺病毒|肠道病毒)',
            r'(细菌|病毒|真菌|寄生虫|支原体|衣原体|螺旋体|立克次体)',
        ]
        
        for pattern in pathogen_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                terms.add(match.group(0).strip())
        
        # 6. Use jieba for medical word segmentation (if available)
        try:
            words = pseg.cut(text)
            for word, flag in words:
                # Keep medical-related POS tags
                if flag in ['n', 'nz', 'v', 'vn', 'a', 'an'] and len(word) >= 2:
                    if self._is_medical_term(word):
                        terms.add(word)
        except Exception as e:
            logger.debug(f"Jieba segmentation error: {e}")
        
        return terms
    
    def _is_medical_term(self, word: str) -> bool:
        """
        Check if a word is likely a medical term
        """
        medical_suffixes = [
            '炎', '病', '症', '癌', '瘤', '毒', '菌', '虫',
            '炎', '炎', '病', '症', '药', '素', '剂'
        ]
        medical_prefixes = [
            '抗', '解', '止', '麻', '镇', '消', '化', '免'
        ]
        
        return (
            any(word.endswith(suffix) for suffix in medical_suffixes) or
            any(word.startswith(prefix) for prefix in medical_prefixes)
        )
    
    def _get_top_terms(self, n: int = 20) -> List[Tuple[str, int]]:
        """
        Get top N most frequent terms
        """
        term_freq = [(term, len(chunks)) for term, chunks in self._term_index.items()]
        return sorted(term_freq, key=lambda x: x[1], reverse=True)[:n]
    
    def find_related_chunks(self, query: str, document_texts: List[str] = None, top_k: int = 10) -> List[Dict]:
        """
        Find chunks related to query using the dynamic term index
        """
        # Extract terms from query and documents
        query_terms = self._extract_medical_terms(query)
        
        if document_texts:
            for doc_text in document_texts:
                query_terms.update(self._extract_medical_terms(doc_text))
        
        logger.info(f"Query terms extracted: {query_terms}")
        
        # Score chunks based on term overlap
        chunk_scores = defaultdict(lambda: {'score': 0, 'chunk': None, 'matched_terms': []})
        
        for term in query_terms:
            if term in self._term_index:
                for chunk_ref in self._term_index[term]:
                    chunk_id = chunk_ref['chunk_id']
                    chunk_scores[chunk_id]['score'] += 1
                    chunk_scores[chunk_id]['chunk'] = chunk_ref
                    chunk_scores[chunk_id]['matched_terms'].append(term)
        
        # Convert to list and sort by score
        results = []
        for chunk_id, data in chunk_scores.items():
            if data['chunk']:
                chunk_data = data['chunk'].copy()
                chunk_data['term_match_score'] = data['score']
                chunk_data['matched_terms'] = data['matched_terms']
                results.append(chunk_data)
        
        results.sort(key=lambda x: x['term_match_score'], reverse=True)
        return results[:top_k]
    
    def get_term_suggestions(self, partial_term: str) -> List[str]:
        """
        Get term suggestions for autocomplete
        """
        partial_term = partial_term.lower()
        suggestions = []
        
        for term in self._medical_vocab:
            if partial_term in term.lower():
                suggestions.append(term)
        
        return suggestions[:10]
    
    def export_index_stats(self) -> Dict:
        """
        Export index statistics for monitoring
        """
        return {
            'total_terms': len(self._term_index),
            'medical_vocabulary_size': len(self._medical_vocab),
            'document_count': len(self._document_terms),
            'top_diseases': self._get_terms_by_category('disease'),
            'top_symptoms': self._get_terms_by_category('symptom'),
            'top_pathogens': self._get_terms_by_category('pathogen'),
        }
    
    def _get_terms_by_category(self, category: str) -> List[str]:
        """
        Get terms by inferred category
        """
        category_patterns = {
            'disease': ['炎', '病', '症', '癌', '瘤'],
            'symptom': ['痛', '痒', '胀', '麻', '晕', '咳', '热'],
            'pathogen': ['菌', '毒', '虫', '支原体', '衣原体', '螺旋体'],
        }
        
        patterns = category_patterns.get(category, [])
        matching_terms = []
        
        for term in self._medical_vocab:
            if any(pattern in term for pattern in patterns):
                matching_terms.append(term)
        
        return matching_terms[:20]


# Global analyzer instance (will be initialized with DB session)
kb_analyzer = None

async def get_kb_analyzer(db: AsyncSession) -> KnowledgeBaseAnalyzer:
    """Get or create knowledge base analyzer"""
    global kb_analyzer
    if kb_analyzer is None:
        kb_analyzer = KnowledgeBaseAnalyzer(db)
        await kb_analyzer.build_indices()
    return kb_analyzer

async def refresh_kb_indices(db: AsyncSession) -> Dict[str, Any]:
    """Force refresh of knowledge base indices"""
    global kb_analyzer
    kb_analyzer = KnowledgeBaseAnalyzer(db)
    return await kb_analyzer.build_indices()
