"""
Background tasks for document processing
Handles async document extraction to prevent API timeouts
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.database import async_session_maker
from app.models.models import MedicalDocument
from app.services.mineru_service import MinerUService
from app.services.pii_cleaner_service import pii_cleaner
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


async def process_document_extraction(
    document_id: uuid.UUID,
    user_id: uuid.UUID,
    extract_tables: bool = True,
    extract_images: bool = False,
    ocr: bool = True
):
    """
    Background task to process document extraction
    
    This function runs asynchronously to:
    1. Upload file to OSS
    2. Call MinerU API for extraction
    3. Perform PII cleaning
    4. Update document status
    
    Args:
        document_id: UUID of the document to process
        user_id: UUID of the user who owns the document
        extract_tables: Whether to extract tables
        extract_images: Whether to extract images  
        ocr: Whether to use OCR
    """
    logger.info(f"🔄 Starting background extraction for document {document_id}")
    
    async with async_session_maker() as db:
        try:
            # Get document info
            result = await db.execute(
                select(MedicalDocument).where(MedicalDocument.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                logger.error(f"❌ Document {document_id} not found")
                return
            
            # Update status to processing
            await db.execute(
                update(MedicalDocument)
                .where(MedicalDocument.id == document_id)
                .values(upload_status="processing")
            )
            await db.commit()
            
            # Initialize MinerU service with DB session for dynamic config
            mineru_service = MinerUService(db=db)
            
            # Perform extraction
            logger.info(f"📄 Extracting content from {document.file_path}")
            extraction_result = await mineru_service.extract_document_content(
                document.file_path,
                extract_tables=extract_tables,
                extract_images=extract_images,
                ocr=ocr,
                wait_for_completion=True,
                max_wait_time=300  # 5 minutes max wait
            )
            
            # Check if extraction was successful
            if extraction_result.get("status") == "completed":
                logger.info(f"✅ Extraction completed for document {document_id}")
                
                # Perform PII cleaning
                pii_cleaning_result = None
                extracted_text = extraction_result.get("text_content", "")
                
                if extracted_text:
                    logger.info(f"🔒 Starting PII cleaning for document {document_id}")
                    pii_cleaning_result = pii_cleaner.clean_text(extracted_text)
                    logger.info(f"✅ PII cleaning completed: {len(pii_cleaning_result['pii_detected'])} items detected")
                
                # Update document with results
                # Prepare extracted content - include text and markdown
                extracted_data = {
                    "text": extraction_result.get("text_content", ""),
                    "markdown": extraction_result.get("markdown_content", ""),
                }
                
                update_values = {
                    "upload_status": "processed",
                    "extracted_content": extracted_data,
                    "extraction_metadata": extraction_result.get("extraction_metadata"),
                    "updated_at": datetime.utcnow()
                }
                
                if pii_cleaning_result:
                    update_values["cleaned_content"] = {
                        "text": pii_cleaning_result["cleaned_text"],
                        "metadata": {
                            "stats": pii_cleaning_result["cleaning_stats"],
                            "confidence": pii_cleaning_result["confidence_score"]
                        }
                    }
                    update_values["pii_cleaning_status"] = "completed"
                    update_values["pii_detected"] = pii_cleaning_result["pii_detected"]
                    update_values["cleaning_confidence"] = pii_cleaning_result["confidence_score"]
                
                await db.execute(
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(**update_values)
                )
                await db.commit()
                
                logger.info(f"✅ Document {document_id} processing completed successfully")
                
            elif extraction_result.get("status") == "processing":
                # Task submitted but not completed yet
                logger.info(f"⏳ Document {document_id} extraction submitted, task_id: {extraction_result.get('task_id')}")
                
                await db.execute(
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(
                        upload_status="processing",
                        extraction_metadata={
                            "task_id": extraction_result.get("task_id"),
                            "status": "submitted",
                            "submitted_at": datetime.utcnow().isoformat()
                        }
                    )
                )
                await db.commit()
                
            else:
                # Extraction failed
                error_msg = extraction_result.get("error", "Unknown error")
                logger.error(f"❌ Extraction failed for document {document_id}: {error_msg}")
                
                # Check if it's a token error
                if "token" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    error_detail = "MinerU API token expired or invalid. Please contact administrator."
                else:
                    error_detail = error_msg
                
                await db.execute(
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(
                        upload_status="failed",
                        pii_cleaning_status="failed",
                        extraction_metadata={
                            "error": error_detail,
                            "code": extraction_result.get("code"),
                            "failed_at": datetime.utcnow().isoformat()
                        }
                    )
                )
                await db.commit()
                
        except Exception as e:
            logger.error(f"❌ Error in background extraction for document {document_id}: {e}")
            
            # Update document status to failed
            try:
                await db.execute(
                    update(MedicalDocument)
                    .where(MedicalDocument.id == document_id)
                    .values(
                        upload_status="failed",
                        pii_cleaning_status="failed",
                        extraction_metadata={
                            "error": str(e),
                            "failed_at": datetime.utcnow().isoformat()
                        }
                    )
                )
                await db.commit()
            except Exception as update_error:
                logger.error(f"❌ Failed to update document status: {update_error}")


async def check_and_resume_processing_documents():
    """
    Check for documents stuck in 'processing' status and resume if needed
    This can be called on startup to handle interrupted processes
    """
    logger.info("🔍 Checking for documents stuck in processing status...")
    
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                select(MedicalDocument).where(MedicalDocument.upload_status == "processing")
            )
            documents = result.scalars().all()
            
            if documents:
                logger.info(f"Found {len(documents)} documents in processing state")
                
                for doc in documents:
                    # Check if document has been processing for too long (>10 minutes)
                    processing_time = datetime.utcnow() - doc.updated_at
                    if processing_time.total_seconds() > 600:  # 10 minutes
                        logger.warning(f"Document {doc.id} has been processing for {processing_time}, marking as failed")
                        await db.execute(
                            update(MedicalDocument)
                            .where(MedicalDocument.id == doc.id)
                            .values(
                                upload_status="failed",
                                extraction_metadata={
                                    "error": "Processing timeout - exceeded 10 minutes",
                                    "failed_at": datetime.utcnow().isoformat()
                                }
                            )
                        )
                    else:
                        logger.info(f"Document {doc.id} still processing, will check again later")
                
                await db.commit()
            else:
                logger.info("No documents stuck in processing state")
                
        except Exception as e:
            logger.error(f"Error checking processing documents: {e}")
