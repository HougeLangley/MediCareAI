"""
AI Service - Multi-provider AI integration
Supports: OpenAI, Zhipu, Kimi, DeepSeek, Ollama, vLLM, LM Studio, and custom providers
Complete workflow: personal info + medical submission + knowledge base -> AI diagnosis
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from app.core.config import settings
from app.services.knowledge_base_service import get_knowledge_loader
from app.services.system_monitoring_service import AIDiagnosisLogger
from app.services.ai_provider_adapters import (
    get_provider_adapter,
    get_provider_default_url,
    provider_requires_key,
    AIProviderAdapter
)

logger = logging.getLogger(__name__)


class AIService:
    """AI Service class with multi-provider support."""
    
    def __init__(self):
        """Initialize AI Service with default settings."""
        self._api_url = settings.ai_api_url
        self._api_key = settings.ai_api_key
        self._model_id = settings.ai_model_id
        self._provider = "custom"  # 默认提供商
        self._config_source = "settings"
        self._adapter: Optional[AIProviderAdapter] = None
    
    async def reload_config_from_db(self, db) -> bool:
        """
        Reload AI configuration from database with provider support.
        
        Args:
            db: Database session
            
        Returns:
            True if config was reloaded from database, False otherwise
        """
        try:
            from app.services.ai_model_config_service import AIModelConfigService
            config_service = AIModelConfigService(db)
            config = await config_service.get_config_with_decrypted_key("diagnosis", fallback_to_env=True)
            
            if config and config.get("api_url"):
                self._api_url = config["api_url"]
                self._api_key = config.get("api_key", "")
                self._model_id = config.get("model_id", "")
                self._provider = config.get("config_metadata", {}).get("provider", "custom")
                self._config_source = config.get("source", "database")
                
                # 创建适配器
                self._adapter = get_provider_adapter(
                    provider=self._provider,
                    api_url=self._api_url,
                    api_key=self._api_key,
                    model_id=self._model_id
                )
                
                logger.info(f"✅ AI configuration reloaded from {self._config_source}: "
                          f"provider={self._provider}, url={self._api_url}")
                return True
        except Exception as e:
            logger.error(f"Failed to reload AI config from database: {e}")
        return False
    
    def _get_adapter(self) -> AIProviderAdapter:
        """Get or create the provider adapter"""
        if self._adapter is None:
            self._adapter = get_provider_adapter(
                provider=self._provider,
                api_url=self._api_url,
                api_key=self._api_key,
                model_id=self._model_id
            )
        return self._adapter
    
    @property
    def api_url(self) -> str:
        """Get API URL for chat completions endpoint."""
        url = self._api_url
        # 如果URL已经包含 chat/completions，直接使用完整URL
        if 'chat/completions' in url:
            return url
        # 否则确保有尾部斜杠，后续再添加 chat/completions
        return url if url.endswith('/') else f"{self._api_url}/"

    @property
    def chat_completions_url(self) -> str:
        """Get the full chat completions endpoint URL."""
        base_url = self.api_url
        # 如果URL已经包含 chat/completions，直接返回
        if 'chat/completions' in base_url:
            return base_url
        # 否则拼接 chat/completions 路径
        return f"{base_url}chat/completions"

    @property
    def api_key(self) -> str:
        """Get API key."""
        return self._api_key
    
    @property
    def model_id(self) -> str:
        """Get model ID."""
        return self._model_id
    
    async def chat_with_glm(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Chat with AI model using provider adapter.
        Supports multiple providers: OpenAI, Zhipu, Kimi, DeepSeek, Ollama, etc.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            API response result
        """
        adapter = self._get_adapter()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    adapter.get_chat_completions_url(),
                    headers=adapter.get_headers(),
                    json=adapter.format_request_body(
                        messages=messages,
                        max_tokens=8192,
                        temperature=0.7,
                        stream=False
                    )
                )

                if response.status_code == 200:
                    result = response.json()
                    content = adapter.parse_response(result)
                    if content:
                        return {
                            "success": True,
                            "content": content,
                            "model": result.get('model', ''),
                            "usage": result.get('usage', {})
                        }
                    return {
                        "success": False,
                        "error": "Invalid response format",
                        "data": result
                    }
                else:
                    error_text = response.text
                    logger.error(f"AI API error: {response.status_code} - {error_text[:500]}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "detail": error_text[:1000]
                    }

        except httpx.TimeoutException:
            logger.error("AI API timeout")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"AI API error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def chat_with_glm_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Stream chat with AI model using provider adapter.
        Supports multiple providers: OpenAI, Zhipu, Kimi, DeepSeek, Ollama, etc.
        
        Args:
            messages: List of conversation messages
            
        Yields:
            Streaming text chunks
        """
        adapter = self._get_adapter()
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST",
                    adapter.get_chat_completions_url(),
                    headers=adapter.get_headers(),
                    json=adapter.format_request_body(
                        messages=messages,
                        max_tokens=8192,
                        temperature=0.7,
                        stream=True
                    )
                ) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            content = await adapter.stream_parse(line)
                            if content is not None:
                                yield content
                            elif content is None and line.startswith("data: ["):
                                # Handle [DONE] signal
                                break
                    else:
                        error_text = await response.aread()
                        logger.error(f"Streaming API error: {response.status_code} - {error_text[:500]}")
                        yield f"[ERROR] API error: {response.status_code}"

        except httpx.TimeoutException:
            logger.error("Streaming API timeout")
            yield "[ERROR] Request timeout"
        except Exception as e:
            logger.error(f"Streaming API error: {str(e)}")
            yield f"[ERROR] {str(e)}"

    async def query_knowledge_base(self, symptoms: str, disease_category: str = "respiratory", patient_info: Dict = None, document_texts: List[str] = None) -> Dict[str, Any]:
        """
        Query knowledge base using Generic RAG selector with universal search.
        
        Args:
            symptoms: Symptom description
            disease_category: Disease category (legacy, now auto-detected)
            patient_info: Optional patient info for better matching
            document_texts: Optional list of extracted text from uploaded documents
            
        Returns:
            Knowledge base information with RAG sources
        """
        try:
            from sqlalchemy.ext.asyncio import AsyncSession
            from app.db.database import AsyncSessionLocal
            from app.services.generic_rag_selector import GenericRAGSelector
            
            async with AsyncSessionLocal() as db:
                # Use Generic RAG Selector for universal knowledge base search
                selector = GenericRAGSelector(db)
                
                patient_age = None
                if patient_info:
                    patient_age = patient_info.get('age')
                
                # Universal search across all knowledge bases
                rag_result = await selector.select_knowledge_bases(
                    symptoms=symptoms,
                    document_texts=document_texts or [],
                    patient_age=patient_age,
                    top_k=5,
                    min_similarity=0.5
                )
                
                # Log extracted entities for debugging
                if rag_result.get('extracted_entities'):
                    entities_str = ', '.join([e['text'] for e in rag_result['extracted_entities'][:5]])
                    logger.info(f"Generic RAG extracted entities: {entities_str}")
                
                # Build knowledge context from selected sources
                knowledge_context = []
                guidelines_context = []
                sources_used = []
                
                for source in rag_result.get('sources', []):
                    category = source.get('category', '')
                    sources_used.append(category)
                    
                    # Add chunks to context
                    for chunk in source.get('chunks', []):
                        chunk_text = chunk.get('text', '')
                        if chunk_text:
                            knowledge_context.append(f"""
【{chunk.get('section_title', category)}】(相似度: {chunk.get('similarity_score', 0):.2f})
{chunk_text[:500]}
""")
                    
                    # Fallback to legacy loader if no vector chunks
                    if not source.get('chunks'):
                        loader = get_knowledge_loader()
                        kb_data = loader.load_base(category)
                        
                        diseases = kb_data.get('diseases', [])
                        for disease in diseases[:2]:
                            disease_info = f"""
疾病名称: {disease.get('name', '未知')}
症状: {', '.join(disease.get('symptoms', [])[:5])}
治疗方案: {', '.join(disease.get('treatment', [])[:3])}
"""
                            knowledge_context.append(disease_info)
                
                # If no RAG sources found, use legacy method
                if not rag_result.get('sources'):
                    logger.warning("No RAG sources found, falling back to legacy method")
                    loader = get_knowledge_loader()
                    kb_data = loader.load_base(disease_category)
                    
                    diseases = kb_data.get('diseases', [])
                    guidelines = kb_data.get('guidelines', [])
                    
                    for disease in diseases[:3]:
                        disease_info = f"""
疾病名称: {disease.get('name', '未知')}
症状: {', '.join(disease.get('symptoms', [])[:5])}
诊断标准: {', '.join(disease.get('diagnosis_criteria', [])[:3])}
治疗方案: {', '.join(disease.get('treatment', [])[:3])}
"""
                        knowledge_context.append(disease_info)
                    
                    for guideline in guidelines[:2]:
                        guide_info = f"""
指南: {guideline.get('name', '未知')}
来源: {guideline.get('source', '未知')}
关键点: {', '.join(guideline.get('key_points', [])[:3])}
"""
                        guidelines_context.append(guide_info)
                    
                    sources_used = [disease_category]
                
                return {
                    "success": True,
                    "diseases_info": "\n".join(knowledge_context),
                    "guidelines_info": "\n".join(guidelines_context),
                    "source": ",".join(sources_used) if sources_used else disease_category,
                    "rag_info": {
                        "sources": rag_result.get('sources', []),
                        "selection_reasoning": rag_result.get('selection_reasoning', ''),
                        "total_chunks": rag_result.get('total_chunks', 0)
                    }
                }
                
        except Exception as e:
            logger.error(f"Knowledge base query failed: {str(e)}")
            # Fallback to legacy method
            try:
                loader = get_knowledge_loader()
                kb_data = loader.load_base(disease_category)
                
                diseases = kb_data.get('diseases', [])
                guidelines = kb_data.get('guidelines', [])
                
                knowledge_context = []
                for disease in diseases[:3]:
                    disease_info = f"""
疾病名称: {disease.get('name', '未知')}
症状: {', '.join(disease.get('symptoms', [])[:5])}
诊断标准: {', '.join(disease.get('diagnosis_criteria', [])[:3])}
治疗方案: {', '.join(disease.get('treatment', [])[:3])}
"""
                    knowledge_context.append(disease_info)
                
                return {
                    "success": True,
                    "diseases_info": "\n".join(knowledge_context),
                    "guidelines_info": "",
                    "source": disease_category,
                    "rag_info": {"error": str(e), "fallback": True}
                }
            except Exception as fallback_error:
                return {
                    "success": False,
                    "error": str(e),
                    "diseases_info": "",
                    "guidelines_info": ""
                }

    async def extract_document_with_mineru(self, file_url: str) -> Dict[str, Any]:
        """
        Extract document content using MinerU.
        
        Args:
            file_url: File URL or file path
            
        Returns:
            Extraction result
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    settings.mineru_api_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.mineru_token}"
                    },
                    json={
                        "extract_type": "parse",
                        "url": file_url
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 0:
                        return {
                            "success": True,
                            "data": result.get('data', {}),
                            "text_content": result.get('data', {}).get('text', '')
                        }
                    else:
                        logger.error(f"MinerU API error: code={result.get('code')}, msg={result.get('msg')}")
                        return {
                            "success": False,
                            "error": result.get('msg', 'Unknown error'),
                            "code": result.get('code')
                        }
                else:
                    logger.error(f"MinerU API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "detail": response.text
                    }

        except httpx.TimeoutException:
            logger.error("MinerU API timeout")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"MinerU API error: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_category_display_name(self, category: str) -> str:
        """Get display name for knowledge base category / 获取知识库分类显示名称"""
        category_names = {
            'respiratory': '呼吸系统疾病',
            'cardiovascular': '心血管系统疾病',
            'digestive': '消化系统疾病',
            'pediatric': '儿科疾病',
            'dermatology': '皮肤疾病',
            'neurological': '神经系统疾病',
            'general': '通用医学知识'
        }
        return category_names.get(category, category)

    async def comprehensive_diagnosis(
        self,
        symptoms: str,
        patient_info: Dict[str, Any],
        duration: Optional[str] = None,
        severity: Optional[str] = None,
        uploaded_files: Optional[List[str]] = None,
        disease_category: str = "respiratory",
        language: str = "zh",
        extracted_documents: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None,
        db: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Complete diagnosis workflow.
        
        Integrates: personal info + medical submission + knowledge base -> AI diagnosis
        
        Args:
            language: Language preference - "zh" for Chinese, "en" for English
            extracted_documents: Pre-extracted documents with MinerU (from database)
        """
        import uuid
        
        # Track request timing for logging
        start_time = time.time()
        request_type = "comprehensive_diagnosis"
        status = "success"
        error_message = None
        tokens_input = 0
        tokens_output = 0
        
        logger.info(f"Starting comprehensive diagnosis workflow (language: {language})...")
        
        # Process uploaded files with MinerU
        extracted_texts = []
        extraction_details = []  # Store detailed extraction info for display
        
        # Use pre-extracted documents from database if provided
        if extracted_documents:
            logger.info(f"Using {len(extracted_documents)} pre-extracted documents from database...")
            for doc in extracted_documents:
                # Get original extracted content
                extracted_content = doc.get('extracted_content', {})
                if isinstance(extracted_content, dict):
                    text_content = extracted_content.get('text', '')
                else:
                    text_content = str(extracted_content)
                
                # Get cleaned content (PII cleaned) if available
                cleaned_content = doc.get('cleaned_content', {})
                if isinstance(cleaned_content, dict):
                    cleaned_text = cleaned_content.get('text', text_content)
                else:
                    cleaned_text = str(cleaned_content) if cleaned_content else text_content
                
                if text_content:
                    extracted_texts.append(cleaned_text[:2000])
                    extraction_details.append({
                        "filename": doc.get('original_filename', 'Unknown'),
                        "original_length": len(text_content),
                        "cleaned_length": len(cleaned_text),
                        "pii_status": doc.get('pii_cleaning_status', 'unknown'),
                        "pii_detected_count": len(doc.get('pii_detected', []))
                    })
                    logger.info(f"Document processed: {doc.get('original_filename')}, "
                              f"PII status: {doc.get('pii_cleaning_status')}")
        
        # Process uploaded files with MinerU (legacy support)
        elif uploaded_files:
            logger.info(f"Extracting {len(uploaded_files)} files with MinerU...")
            for file_url in uploaded_files:
                extraction_result = await self.extract_document_with_mineru(file_url)
                if extraction_result.get('success'):
                    text_content = extraction_result.get('text_content', '')
                    if text_content:
                        extracted_texts.append(text_content[:2000])
                        extraction_details.append({
                            "filename": file_url,
                            "original_length": len(text_content),
                            "source": "live_extraction"
                        })
                        logger.info(f"File extraction successful, content length: {len(text_content)}")
                else:
                    logger.warning(f"File extraction failed: {extraction_result.get('error')}")
        
        # Query knowledge base with document texts for enhanced retrieval
        logger.info(f"Querying knowledge base: {disease_category}...")
        kb_result = await self.query_knowledge_base(symptoms, disease_category, patient_info, extracted_texts)

        # Build complete prompt
        prompt = self._build_diagnosis_prompt(
            patient_info=patient_info,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            extracted_texts=extracted_texts,
            knowledge_base=kb_result,
            language=language
        )
        
        logger.info("Calling AI model for diagnosis...")
        
        # 根据语言选择系统提示词
        if language == "zh":
            system_prompt = "你是一位经验丰富的全科医生。请根据患者信息、症状描述、相关检查数据和医疗知识库提供专业的中文诊断。请确保你的回答使用中文。"
        else:
            system_prompt = "You are a professional general practitioner with rich clinical experience. Please provide professional diagnosis in English based on the patient information, symptom description, relevant examination data and medical knowledge base. Please ensure your answer is in English."
        
        # Call AI for diagnosis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Calculate approximate input tokens (rough estimate: 4 chars per token for Chinese)
        prompt_length = len(prompt)
        tokens_input = prompt_length // 4 if language == "zh" else prompt_length // 5
        
        result = await self.chat_with_glm(messages)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        if result.get('success'):
            # Get token usage from response
            usage = result.get('usage', {})
            tokens_input = usage.get('prompt_tokens', tokens_input)
            tokens_output = usage.get('completion_tokens', len(result.get('content', '')) // 4 if language == "zh" else len(result.get('content', '')) // 5)
            status = "success"
            
            # Log AI diagnosis if user_id and db are provided
            if user_id and db:
                try:
                    ai_logger = AIDiagnosisLogger(db)
                    await ai_logger.log_diagnosis(
                        user_id=uuid.UUID(user_id),
                        request_type=request_type,
                        ai_model_id=self.model_id,
                        ai_api_url=self.api_url,
                        duration_ms=duration_ms,
                        tokens_input=tokens_input,
                        tokens_output=tokens_output,
                        status=status,
                        error_message=""
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log AI diagnosis: {log_error}")
            
            # Build knowledge base sources for response
            knowledge_base_sources = []
            if kb_result.get('success') and kb_result.get('rag_info', {}).get('sources'):
                for source in kb_result['rag_info']['sources']:
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
                    
                    knowledge_base_sources.append({
                        "category": category,
                        "category_name": self._get_category_display_name(category),
                        "relevance_score": source.get('relevance_score', 0),
                        "selection_reason": source.get('selection_reason', ''),
                        "chunks_count": len(source.get('chunks', [])),
                        "chunks": chunks_data
                    })
            
            return {
                "success": True,
                "diagnosis": result['content'],
                "model_used": self.model_id,
                "tokens_used": result.get('usage', {}).get('total_tokens', 0),
                "request_duration_ms": duration_ms,
                "workflow": {
                    "patient_info_included": bool(patient_info),
                    "files_processed": len(extracted_texts),
                    "documents_detail": extraction_details,  # 详细的文档处理信息
                    "knowledge_base_queried": kb_result.get('success', False),
                    "knowledge_source": kb_result.get('source', ''),
                    "knowledge_base_sources_count": len(knowledge_base_sources)
                },
                # 知识库溯源信息（新增）
                "knowledge_base_sources": knowledge_base_sources,
                "knowledge_base_selection_reasoning": kb_result.get('rag_info', {}).get('selection_reasoning', ''),
                # 显示MinerU提取的内容给患者（新增）
                "extracted_documents": {
                    "count": len(extraction_details),
                    "documents": extraction_details,
                    "extracted_texts_preview": [text[:200] + "..." if len(text) > 200 else text 
                                               for text in extracted_texts] if extracted_texts else []
                } if extraction_details else None
            }
        else:
            # Failed request
            status = "error"
            error_message = result.get('error', 'Unknown error')
            
            # Log failed AI diagnosis
            if user_id and db:
                try:
                    ai_logger = AIDiagnosisLogger(db)
                    await ai_logger.log_diagnosis(
                        user_id=uuid.UUID(user_id),
                        request_type=request_type,
                        ai_model_id=self.model_id,
                        ai_api_url=self.api_url,
                        duration_ms=duration_ms,
                        tokens_input=tokens_input,
                        tokens_output=0,
                        status=status,
                        error_message=error_message
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log AI diagnosis error: {log_error}")
            
            return {
                "success": False,
                "error": error_message,
                "diagnosis": "AI analysis failed, please try again later",
                "request_duration_ms": duration_ms,
                "extracted_documents": {
                    "count": len(extraction_details),
                    "documents": extraction_details
                } if extraction_details else None
            }

    async def comprehensive_diagnosis_stream(
        self,
        symptoms: str,
        patient_info: Dict[str, Any],
        duration: Optional[str] = None,
        severity: Optional[str] = None,
        uploaded_files: Optional[List[str]] = None,
        extracted_documents: Optional[List[Dict[str, Any]]] = None,
        disease_category: str = "respiratory",
        language: str = "zh",
        user_id: Optional[str] = None,
        db: Optional[Any] = None
    ) -> AsyncGenerator[str, None]:
        """
        Complete diagnosis workflow (streaming).

        Integrates: personal info + medical submission info + knowledge base -> AI diagnosis (streaming)

        Args:
            language: Language preference - "zh" for Chinese, "en" for English
            user_id: User ID for logging
            db: Database session for logging
        """
        import time
        import uuid
        start_time = time.time()
        request_type = "comprehensive_diagnosis"
        status = "success"
        error_message = None
        tokens_input = 0
        tokens_output = 0

        logger.info(f"Starting comprehensive diagnosis workflow (streaming, language: {language})...")

        # Process uploaded files with MinerU (legacy support)
        extracted_texts = []
        if uploaded_files:
            logger.info(f"Extracting {len(uploaded_files)} files...")
            for file_url in uploaded_files:
                extraction_result = await self.extract_document_with_mineru(file_url)
                if extraction_result.get('success'):
                    text_content = extraction_result.get('text_content', '')
                    if text_content:
                        extracted_texts.append(text_content[:2000])
                        logger.info(f"File extraction successful, content length: {len(text_content)}")
                else:
                    logger.warning(f"File extraction failed: {extraction_result.get('error')}")

        # Add pre-extracted documents from database
        if extracted_documents:
            logger.info(f"Adding {len(extracted_documents)} pre-extracted documents...")
            for doc in extracted_documents:
                # Get content from cleaned_content (dict with 'text' field) or extracted_content
                content = ''
                cleaned = doc.get('cleaned_content')
                if cleaned and isinstance(cleaned, dict):
                    content = cleaned.get('text', '')
                elif cleaned:
                    content = str(cleaned)
                else:
                    extracted = doc.get('extracted_content', '')
                    if isinstance(extracted, dict):
                        content = str(extracted)
                    else:
                        content = extracted
                
                if content:
                    extracted_texts.append(f"[{doc.get('original_filename', 'Document')}]:\n{content[:2000]}")
                    logger.info(f"Added document content: {doc.get('original_filename', 'Document')}, length: {len(content)}")

        # Query knowledge base with document texts for enhanced retrieval
        logger.info(f"Querying knowledge base: {disease_category}...")
        kb_result = await self.query_knowledge_base(symptoms, disease_category, patient_info, extracted_texts)

        # Build complete prompt
        prompt = self._build_diagnosis_prompt(
            patient_info=patient_info,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            extracted_texts=extracted_texts,
            knowledge_base=kb_result,
            language=language
        )
        
        logger.info("Calling AI model for streaming diagnosis...")
        
        # 根据语言选择系统提示词
        if language == "zh":
            system_prompt = """你是一位经验丰富的全科医生。请根据患者信息、症状描述、相关检查数据和医疗知识库提供专业的中文诊断。

特别重要：如果患者上传了检查报告（如血常规、病原体检测等），你必须：
1) 仔细分析报告中的每一项指标
2) 明确指出哪些指标异常（超出参考范围）
3) 解释每个异常指标可能的临床意义
4) 结合异常指标和症状给出综合诊断

请确保你的回答完整，包括：
1) 初步诊断（按可能性排序的表格）
2) 详细分析（必须包含检查报告异常指标分析）
3) 建议检查项目
4) 治疗方案
5) 注意事项

请使用中文回答。"""
        else:
            system_prompt = """You are a professional general practitioner with rich clinical experience. Please provide professional diagnosis in English based on the patient information, symptom description, relevant examination data and medical knowledge base.

Important: If the patient has uploaded examination reports (such as blood tests, pathogen tests, etc.), you MUST:
1) Carefully analyze each indicator in the report
2) Clearly identify which indicators are abnormal (outside reference ranges)
3) Explain the possible clinical significance of each abnormal indicator
4) Provide comprehensive diagnosis combining abnormal indicators with symptoms

Please ensure your answer is complete, including:
1) Preliminary diagnosis (table sorted by probability)
2) Detailed analysis (must include analysis of abnormal indicators from examination reports)
3) Recommended examinations
4) Treatment plan
5) Precautions

Please answer in English."""
        
        # Call AI for streaming diagnosis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        chunk_count = 0
        total_chars = 0
        try:
            async for chunk in self.chat_with_glm_stream(messages):
                chunk_count += 1
                total_chars += len(chunk)
                yield chunk
        except Exception as e:
            status = "error"
            error_message = str(e)
            logger.error(f"Streaming diagnosis failed: {error_message}")
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log AI diagnosis if user_id and db are provided
            if user_id and db:
                try:
                    from app.services.system_monitoring_service import AIDiagnosisLogger
                    ai_logger = AIDiagnosisLogger(db)
                    await ai_logger.log_diagnosis(
                        user_id=uuid.UUID(user_id),
                        request_type=request_type,
                        ai_model_id=self.model_id,
                        ai_api_url=self.api_url,
                        duration_ms=duration_ms,
                        tokens_input=tokens_input,
                        tokens_output=total_chars // 4,  # Estimate tokens from characters
                        status=status,
                        error_message=error_message or ""
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log AI diagnosis: {log_error}")

            logger.info(f"Streaming diagnosis completed, {chunk_count} chunks, {total_chars} characters, status: {status}")

    def _build_diagnosis_prompt(
        self,
        patient_info: Dict[str, Any],
        symptoms: str,
        duration: Optional[str],
        severity: Optional[str],
        extracted_texts: List[str],
        knowledge_base: Dict[str, Any],
        language: str = "zh"
    ) -> str:
        """
        Build diagnosis prompt.
        
        Structure: personal info + medical submission info + knowledge base info
        
        Args:
            language: Language preference - "zh" for Chinese, "en" for English
        """
        prompt_parts = []
        
        # 根据语言选择文本
        if language == "zh":
            # 中文版本
            prompt_parts.append("=" * 50)
            prompt_parts.append("【第1部分：患者个人信息】")
            prompt_parts.append("=" * 50)
            
            if patient_info:
                prompt_parts.append(f"姓名: {patient_info.get('full_name', '未知')}")
                prompt_parts.append(f"性别: {patient_info.get('gender', '未知')}")
                prompt_parts.append(f"出生日期: {patient_info.get('date_of_birth', '未知')}")
                prompt_parts.append(f"电话: {patient_info.get('phone', '未知')}")
                prompt_parts.append(f"紧急联系人: {patient_info.get('emergency_contact', '未知')}")
                prompt_parts.append(f"地址: {patient_info.get('address', '未知')}")
                prompt_parts.append(f"备注: {patient_info.get('notes', '无')}")
            else:
                prompt_parts.append("无详细的个人信息")
            
            # Part 2: Medical Submission Information
            prompt_parts.append("\n" + "=" * 50)
            prompt_parts.append("【第2部分：诊疗提交信息】")
            prompt_parts.append("=" * 50)
            
            prompt_parts.append(f"\n症状描述:\n{symptoms}")
            
            if duration:
                prompt_parts.append(f"\n症状持续时间: {duration}")
            
            if severity:
                prompt_parts.append(f"\n严重程度: {severity}")
            
            # Add MinerU extracted file content
            if extracted_texts:
                prompt_parts.append("\n" + "=" * 50)
                prompt_parts.append("【上传的检查报告/材料 - 非常重要】")
                prompt_parts.append("=" * 50)
                prompt_parts.append("以下是通过OCR从患者上传的检查报告中提取的内容。")
                prompt_parts.append("你必须仔细分析其中的每一项指标，特别关注：")
                prompt_parts.append("- 哪些指标超出了参考范围（异常）")
                prompt_parts.append("- 异常指标可能代表什么健康问题")
                prompt_parts.append("- 如何结合这些异常指标和症状进行诊断")
                prompt_parts.append("")
                for i, text in enumerate(extracted_texts, 1):
                    prompt_parts.append(f"\n[检查报告 {i} 内容]:")
                    prompt_parts.append(text[:2000])  # 增加字符数以获取更多信息
            
            # Part 3: Knowledge Base Information
            prompt_parts.append("\n" + "=" * 50)
            prompt_parts.append("【第3部分：医疗知识库参考】")
            prompt_parts.append("=" * 50)
            
            if knowledge_base.get('success'):
                if knowledge_base.get('diseases_info'):
                    prompt_parts.append("\n[相关疾病信息]:")
                    prompt_parts.append(knowledge_base['diseases_info'])
                
                if knowledge_base.get('guidelines_info'):
                    prompt_parts.append("\n[治疗指南参考]:")
                    prompt_parts.append(knowledge_base['guidelines_info'])
            else:
                prompt_parts.append("\n(知识库暂时不可用，基于通用医疗知识进行分析)")
            
            # Diagnosis Requirements
            prompt_parts.append("\n" + "=" * 50)
            prompt_parts.append("【诊断要求 - 请严格遵循】")
            prompt_parts.append("=" * 50)
            prompt_parts.append("""
请根据以上三部分内容提供以下中文诊断内容：

1. **初步诊断**：根据症状和检查数据提供可能的诊断（按可能性排序）

2. **检查报告分析**（如果有上传检查报告，这是必选项）：
   - 列出报告中所有异常指标（超出参考范围的数值）
   - 对每个异常指标，解释其临床意义
   - 分析异常指标与患者症状之间的关联
   - 例如："白细胞计数13.04（参考范围4.0-12.0）偏高，提示可能存在感染或炎症"

3. **诊断依据**：结合知识库和检查报告异常指标解释诊断推理

4. **鉴别诊断**：列出需要排除的其他疾病

5. **建议检查**：列出推荐的进一步检查

6. **治疗方案**：基于知识库的治疗建议

7. **注意事项**：用药提醒、生活建议等

8. **就医建议**：是否需要立即就医，建议就诊科室

**【重要 - 知识库引用标注要求】**
在诊断报告的相关部分，当你引用了上述【第3部分：医疗知识库参考】中的内容时，请使用以下格式标注：
- 在引用内容后添加标注：[知识库: {章节标题}]
- 例如："根据临床表现，儿童哮喘诊断需要考虑反复发作性喘息[知识库: 儿童哮喘诊断标准]"
- 如果是综合多个知识库内容，可以标注：[知识库: 综合多个来源]

这样做是为了让患者知道哪些诊断依据来自权威医学知识库，增强诊断的可信度。

重要提醒：
- 如果患者上传了检查报告，你必须在诊断中明确提及异常指标及其意义
- **请务必在诊断中标注引用的知识库来源，这很重要**
- 诊断仅供参考，不能替代专业医生的诊疗
- 如有紧急情况，请立即就医
- 根据患者个人信息（如过敏史等）提供个性化建议
""")
        else:
            # English version
            prompt_parts.append("=" * 50)
            prompt_parts.append("【Part 1: Patient Personal Information】")
            prompt_parts.append("=" * 50)
            
            if patient_info:
                prompt_parts.append(f"Name: {patient_info.get('full_name', 'Unknown')}")
                prompt_parts.append(f"Gender: {patient_info.get('gender', 'Unknown')}")
                prompt_parts.append(f"Date of Birth: {patient_info.get('date_of_birth', 'Unknown')}")
                prompt_parts.append(f"Phone: {patient_info.get('phone', 'Unknown')}")
                prompt_parts.append(f"Emergency Contact: {patient_info.get('emergency_contact', 'Unknown')}")
                prompt_parts.append(f"Address: {patient_info.get('address', 'Unknown')}")
                prompt_parts.append(f"Notes: {patient_info.get('notes', 'None')}")
            else:
                prompt_parts.append("No detailed personal information available")
            
            # Part 2: Medical Submission Information
            prompt_parts.append("\n" + "=" * 50)
            prompt_parts.append("【Part 2: Medical Submission Information】")
            prompt_parts.append("=" * 50)
            
            prompt_parts.append(f"\nSymptom Description:\n{symptoms}")
            
            if duration:
                prompt_parts.append(f"\nSymptom Duration: {duration}")
            
            if severity:
                prompt_parts.append(f"\nSeverity: {severity}")
            
            # Add MinerU extracted file content
            if extracted_texts:
                prompt_parts.append("\n" + "=" * 50)
                prompt_parts.append("【Uploaded Examination Reports/Materials - Very Important】")
                prompt_parts.append("=" * 50)
                prompt_parts.append("The following content is extracted from examination reports uploaded by the patient using OCR.")
                prompt_parts.append("You must carefully analyze each indicator in the report, with special attention to:")
                prompt_parts.append("- Which indicators are outside the reference range (abnormal)")
                prompt_parts.append("- What health issues abnormal indicators may represent")
                prompt_parts.append("- How to combine these abnormal indicators with symptoms for diagnosis")
                prompt_parts.append("")
                for i, text in enumerate(extracted_texts, 1):
                    prompt_parts.append(f"\n[Examination Report {i} content]:")
                    prompt_parts.append(text[:2000])  # Increased character limit
            
            # Part 3: Knowledge Base Information
            prompt_parts.append("\n" + "=" * 50)
            prompt_parts.append("【Part 3: Medical Knowledge Base Reference】")
            prompt_parts.append("=" * 50)
            
            if knowledge_base.get('success'):
                if knowledge_base.get('diseases_info'):
                    prompt_parts.append("\n[Relevant Disease Information]:")
                    prompt_parts.append(knowledge_base['diseases_info'])
                
                if knowledge_base.get('guidelines_info'):
                    prompt_parts.append("\n[Treatment Guidelines Reference]:")
                    prompt_parts.append(knowledge_base['guidelines_info'])
            else:
                prompt_parts.append("\n(Knowledge base temporarily unavailable, analyzing based on general medical knowledge)")
            
            # Diagnosis Requirements
            prompt_parts.append("\n" + "=" * 50)
            prompt_parts.append("【Diagnosis Requirements - Please Follow Strictly】")
            prompt_parts.append("=" * 50)
            prompt_parts.append("""
Please provide the following diagnosis content based on the three parts above:

1. **Preliminary Diagnosis**: Possible diagnoses based on symptoms and examination data (sorted by probability)

2. **Examination Report Analysis** (If examination reports were uploaded, this is REQUIRED):
   - List all abnormal indicators in the report (values outside reference range)
   - Explain the clinical significance of each abnormal indicator
   - Analyze the correlation between abnormal indicators and patient symptoms
   - Example: "White blood cell count 13.04 (reference range 4.0-12.0) is elevated, suggesting possible infection or inflammation"

3. **Diagnosis Basis**: Explain diagnosis reasoning combining knowledge base and abnormal indicators from examination reports

4. **Differential Diagnosis**: List other diseases to exclude

5. **Recommended Examinations**: List further examinations to recommend

6. **Treatment Plan**: Treatment recommendations based on knowledge base

7. **Precautions**: Medication reminders, lifestyle suggestions, etc.

8. **Medical Advice**: Whether immediate medical attention is needed, recommended departments

**[IMPORTANT - Knowledge Base Citation Requirements]**
When you reference content from the [Part 3: Medical Knowledge Base Reference] above in your diagnosis report, please use the following format to cite the source:
- Add citation after the referenced content: [Knowledge Base: {Section Title}]
- Example: "According to clinical manifestations, childhood asthma diagnosis needs to consider recurrent wheezing [Knowledge Base: Childhood Asthma Diagnostic Criteria]"
- If synthesizing multiple knowledge base sources, you can use: [Knowledge Base: Multiple Sources]

This helps patients understand which diagnostic basis comes from authoritative medical knowledge bases, enhancing the credibility of the diagnosis.

Important Reminders:
- If the patient uploaded examination reports, you MUST mention abnormal indicators and their significance in the diagnosis
- **Please be sure to cite knowledge base sources in your diagnosis, this is very important**
- Diagnosis is for reference only and cannot replace professional doctor's consultation
- In case of emergency, seek medical attention immediately
- Provide personalized suggestions based on patient personal information (such as allergy history)
""")
        
        return "\n".join(prompt_parts)

    async def analyze_symptoms(self, symptoms: str, patient_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        AI analyze symptoms (simplified version, backward compatible)
        """
        # Call complete diagnosis workflow
        result = await self.comprehensive_diagnosis(
            symptoms=symptoms,
            patient_info=patient_info or {}
        )
        
        return {
            "diagnosis": result.get('diagnosis', ''),
            "model_used": result.get('model_used', ''),
            "tokens_used": result.get('tokens_used', 0),
            "error": result.get('error')
        }

    async def extract_medical_report(self, file_url: str) -> Dict[str, Any]:
        """
        Extract medical report content
        """
        result = await self.extract_document_with_mineru(file_url)

        if not result.get('success'):
            return result

        return {
            "success": True,
            "raw_data": result.get('data', {}),
            "extracted_text": result.get('text_content', ''),
            "extracted_fields": {}
        }


# Global instance
ai_service = AIService()