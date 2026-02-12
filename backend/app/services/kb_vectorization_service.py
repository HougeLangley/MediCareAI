"""
Knowledge Base Vectorization Service | 知识库向量化服务
Handles document chunking and vectorization for RAG.

Features:
- Text chunking with overlap
- Vector embedding generation
- Storage in PostgreSQL with pgvector
- Duplicate detection via hash
- Support for Markdown documents

支持：
- 文本分块（带重叠）
- 向量嵌入生成
- PostgreSQL pgvector存储
- 哈希去重
- Markdown文档支持
"""

import hashlib
import re
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.models import KnowledgeBaseChunk, Disease
from app.services.vector_embedding_service import VectorEmbeddingService
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Document Chunker / 文档分块器
    
    Splits documents into chunks for vectorization.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks / 将文本分块
        
        Uses recursive character splitting with overlap.
        """
        if not text:
            return []
        
        chunks = []
        current_chunk = ""
        
        # Try to split by separators first
        for separator in self.separators:
            if separator in text:
                parts = text.split(separator)
                for i, part in enumerate(parts):
                    # Add separator back except for first part
                    if i > 0:
                        part = separator + part
                    
                    # If adding this part would exceed chunk size, save current chunk
                    if len(current_chunk) + len(part) > self.chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        
                        # Handle parts that are larger than chunk_size
                        if len(part) > self.chunk_size:
                            # Split large parts further
                            sub_chunks = self._split_large_text(part)
                            chunks.extend(sub_chunks)
                            current_chunk = ""
                        else:
                            current_chunk = part
                    else:
                        current_chunk += part
                
                # Add remaining text
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                return self._merge_small_chunks(chunks)
        
        # Fallback: split by character count
        return self._split_by_characters(text)
    
    def _split_large_text(self, text: str) -> List[str]:
        """Split text that's larger than chunk_size"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk.strip())
        return chunks
    
    def _split_by_characters(self, text: str) -> List[str]:
        """Split text by character count with overlap"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk.strip())
        return chunks
    
    def _merge_small_chunks(self, chunks: List[str], min_size: int = 100) -> List[str]:
        """Merge chunks that are too small"""
        if not chunks:
            return chunks
        
        merged = []
        current = chunks[0]
        
        for chunk in chunks[1:]:
            if len(current) < min_size:
                current += "\n" + chunk
            else:
                merged.append(current)
                current = chunk
        
        merged.append(current)
        return merged


class KnowledgeBaseVectorizationService:
    """
    Knowledge Base Vectorization Service / 知识库向量化服务
    
    Manages vectorization of medical documents.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chunker = DocumentChunker()
        self.vector_service = VectorEmbeddingService(db)
    
    async def vectorize_markdown_document(
        self,
        document_content: str,
        document_title: str,
        disease_category: str,
        disease_id: uuid.UUID = None,
        source_type: str = 'disease_guideline',
        created_by: uuid.UUID = None
    ) -> Dict[str, Any]:
        """
        Vectorize a Markdown document / 向量化Markdown文档
        
        Args:
            document_content: Raw markdown content
            document_title: Document title
            disease_category: Category (e.g., 'respiratory', 'cardiovascular')
            disease_id: Associated disease ID
            source_type: Type of source
            created_by: Admin user ID
            
        Returns:
            {
                'total_chunks': int,
                'new_chunks': int,
                'duplicates': int,
                'chunk_ids': List[uuid.UUID]
            }
        """
        logger.info(f"Starting vectorization: {document_title}")
        
        # Check if document already exists - delete old chunks if re-uploading
        # Use LIKE to catch variations in title (e.g., with/without timestamp suffix)
        from sqlalchemy import delete, text
        try:
            # Try exact match first (don't filter by source_type - old chunks may have different source_type)
            delete_result = await self.db.execute(
                delete(KnowledgeBaseChunk).where(
                    KnowledgeBaseChunk.document_title == document_title
                )
            )
            deleted_count = delete_result.rowcount
            
            # Also try partial match (for titles with timestamps or other suffixes)
            # Extract base title (e.g., "doc.md" -> match "doc.md_*" or "doc.md*")
            base_title = document_title.replace('.md', '')
            if len(base_title) > 10:  # Only if we have a meaningful base title
                partial_result = await self.db.execute(
                    delete(KnowledgeBaseChunk).where(
                        KnowledgeBaseChunk.document_title.like(f'{base_title}%')
                    )
                )
                deleted_count += partial_result.rowcount
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} existing chunks for '{document_title}' (re-uploading)")
            await self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to delete existing chunks: {e}")
            await self.db.rollback()
        
        # Extract sections from markdown
        sections = self._extract_markdown_sections(document_content)
        
        all_chunks = []
        chunk_hashes = []
        
        # Process each section
        for section_title, section_content in sections:
            # Split section into chunks
            chunks = self.chunker.split_text(section_content)
            
            for i, chunk_text in enumerate(chunks):
                # Calculate hash for deduplication
                text_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                
                # Check for duplicates
                stmt = select(KnowledgeBaseChunk).where(
                    KnowledgeBaseChunk.chunk_text_hash == text_hash
                )
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    logger.debug(f"Duplicate chunk found: {text_hash[:16]}...")
                    continue
                
                # Create chunk record
                chunk = KnowledgeBaseChunk(
                    id=uuid.uuid4(),
                    source_type=source_type,
                    disease_id=disease_id,
                    disease_category=disease_category,
                    document_title=document_title,
                    section_title=section_title,
                    chunk_index=i,
                    chunk_text=chunk_text,
                    chunk_text_hash=text_hash,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                all_chunks.append(chunk)
                chunk_hashes.append(text_hash)
        
        if not all_chunks:
            logger.info(f"No new chunks to vectorize for {document_title}")
            return {
                'total_chunks': 0,
                'new_chunks': 0,
                'duplicates': 0,
                'chunk_ids': []
            }
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        chunk_texts = [chunk.chunk_text for chunk in all_chunks]
        
        try:
            embeddings = await self.vector_service.generate_embeddings_batch(chunk_texts)
            
            # Update chunks with embeddings
            for chunk, embedding in zip(all_chunks, embeddings):
                # Get config used
                config = await self.vector_service.get_active_config()
                chunk.embedding = embedding
                chunk.embedding_model_id = config.model_id if config else 'unknown'
            
            # Save to database
            for chunk in all_chunks:
                self.db.add(chunk)
            
            await self.db.commit()
            
            logger.info(f"Vectorization complete: {len(all_chunks)} chunks")
            
            return {
                'total_chunks': len(all_chunks) + len(chunk_hashes) - len(all_chunks),
                'new_chunks': len(all_chunks),
                'duplicates': len(chunk_hashes) - len(all_chunks),
                'chunk_ids': [chunk.id for chunk in all_chunks]
            }
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            await self.db.rollback()
            raise
    
    def _extract_markdown_sections(self, content: str) -> List[tuple]:
        """
        Extract sections from markdown / 从Markdown提取章节
        
        Returns list of (section_title, section_content) tuples.
        """
        sections = []
        
        # Split by headers (## or ###)
        pattern = r'(?:^|\n)(#{2,3}\s+.+?)(?:\n|$)'
        parts = re.split(pattern, content)
        
        if len(parts) == 1:
            # No headers found, treat entire content as one section
            return [("General", content)]
        
        # First part is before first header
        if parts[0].strip():
            sections.append(("Introduction", parts[0].strip()))
        
        # Process header-content pairs
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                header = parts[i].strip()
                section_content = parts[i + 1].strip()
                
                # Remove markdown header markers
                title = re.sub(r'^#{2,3}\s*', '', header)
                
                if section_content:
                    sections.append((title, section_content))
        
        return sections
    
    async def search_similar_chunks(
        self,
        query_text: str,
        disease_category: str = None,
        top_k: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity / 搜索相似块
        
        Args:
            query_text: Query text
            disease_category: Filter by category
            top_k: Number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of chunks with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.vector_service.generate_embedding(query_text)
        
        # Build query
        stmt = select(KnowledgeBaseChunk).where(
            KnowledgeBaseChunk.is_active == True
        )
        
        if disease_category:
            stmt = stmt.where(KnowledgeBaseChunk.disease_category == disease_category)
        
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()
        
        # Calculate cosine similarity
        scored_chunks = []
        for chunk in chunks:
            if chunk.embedding:
                similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                if similarity >= min_similarity:
                    scored_chunks.append({
                        'chunk': chunk,
                        'similarity': similarity
                    })
        
        # Sort by similarity and take top_k
        scored_chunks.sort(key=lambda x: x['similarity'], reverse=True)
        top_chunks = scored_chunks[:top_k]
        
        # Format results
        results = []
        for item in top_chunks:
            chunk = item['chunk']
            results.append({
                'id': str(chunk.id),
                'text': chunk.chunk_text,
                'section_title': chunk.section_title,
                'document_title': chunk.document_title,
                'disease_category': chunk.disease_category,
                'similarity_score': item['similarity']
            })
            
            # Update retrieval count
            chunk.retrieval_count += 1
        
        await self.db.commit()
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(a * a for a in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def get_chunk_statistics(self) -> Dict[str, Any]:
        """Get vectorization statistics / 获取向量化统计"""
        # Total chunks
        stmt = select(KnowledgeBaseChunk)
        result = await self.db.execute(stmt)
        total_chunks = len(result.scalars().all())
        
        # Active chunks
        stmt = select(KnowledgeBaseChunk).where(KnowledgeBaseChunk.is_active == True)
        result = await self.db.execute(stmt)
        active_chunks = len(result.scalars().all())
        
        # Chunks by category
        stmt = select(KnowledgeBaseChunk.disease_category, KnowledgeBaseChunk.id)
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()
        
        categories = {}
        for chunk in chunks:
            cat = chunk.disease_category or 'unknown'
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_chunks': total_chunks,
            'active_chunks': active_chunks,
            'inactive_chunks': total_chunks - active_chunks,
            'categories': categories
        }
    
    async def delete_document_chunks(
        self,
        document_title: str,
        disease_category: str = None
    ) -> int:
        """Delete all chunks for a document / 删除文档的所有块"""
        stmt = delete(KnowledgeBaseChunk).where(
            KnowledgeBaseChunk.document_title == document_title
        )
        
        if disease_category:
            stmt = stmt.where(KnowledgeBaseChunk.disease_category == disease_category)
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        deleted_count = result.rowcount
        logger.info(f"Deleted {deleted_count} chunks for {document_title}")
        
        return deleted_count


# Global service instance
kb_vectorization_service = KnowledgeBaseVectorizationService
