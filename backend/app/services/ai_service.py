"""
AI 服务 - 集成 GLM-4.7-Flash（llama.cpp API）
完整工作流：个人信息 + 诊疗提交信息 + 知识库信息 -> AI 诊断
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.knowledge_base_service import get_knowledge_loader

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务类 - 使用 llama.cpp API"""

    async def chat_with_glm(self, messages: list) -> Dict[str, Any]:
        """
        使用 GLM-4.7-Flash 进行对话（llama.cpp API 格式）

        Args:
            messages: 对话消息列表

        Returns:
            API 响应结果
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # llama.cpp API 格式
                response = await client.post(
                    f"{settings.ai_api_url}chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.ai_api_key}"
                    },
                    json={
                        "model": settings.ai_model_id,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.7,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    # llama.cpp 返回格式与 OpenAI 兼容
                    if 'choices' in result and len(result['choices']) > 0:
                        message = result['choices'][0]['message']
                        # 优先使用 reasoning_content（思考链模型）
                        content = message.get('reasoning_content') or message.get('content', '')
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
                    logger.error(f"GLM API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "detail": response.text
                    }

        except httpx.TimeoutException:
            logger.error("GLM API timeout")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"GLM API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def query_knowledge_base(self, symptoms: str, disease_category: str = "respiratory") -> Dict[str, Any]:
        """
        查询知识库获取相关疾病信息

        Args:
            symptoms: 症状描述
            disease_category: 疾病分类，默认呼吸系统

        Returns:
            知识库信息
        """
        try:
            loader = get_knowledge_loader()
            
            # 加载指定分类的知识库
            kb_data = loader.load_base(disease_category)
            
            # 提取相关疾病信息（简单匹配症状关键词）
            diseases = kb_data.get('diseases', [])
            guidelines = kb_data.get('guidelines', [])
            
            # 构建知识库上下文
            knowledge_context = []
            
            # 添加疾病信息
            for disease in diseases[:3]:  # 取前3个最相关的
                disease_info = f"""
疾病名称: {disease.get('name', '未知')}
症状: {', '.join(disease.get('symptoms', [])[:5])}
诊断标准: {', '.join(disease.get('diagnosis_criteria', [])[:3])}
治疗方案: {', '.join(disease.get('treatment', [])[:3])}
"""
                knowledge_context.append(disease_info)
            
            # 添加指南信息
            guideline_context = []
            for guideline in guidelines[:2]:  # 取前2个指南
                guide_info = f"""
指南: {guideline.get('name', '未知')}
来源: {guideline.get('source', '未知')}
关键点: {', '.join(guideline.get('key_points', [])[:3])}
"""
                guideline_context.append(guide_info)
            
            return {
                "success": True,
                "diseases_info": "\n".join(knowledge_context),
                "guidelines_info": "\n".join(guideline_context),
                "source": disease_category
            }
            
        except Exception as e:
            logger.error(f"知识库查询失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "diseases_info": "",
                "guidelines_info": ""
            }

    async def extract_document_with_mineru(self, file_url: str) -> Dict[str, Any]:
        """
        使用 MinerU 提取文档内容

        Args:
            file_url: 文件 URL 或文件路径

        Returns:
            提取结果
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
                            "text_content": result.get('data', {}).get('text', '')  # 提取的文本内容
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
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"MinerU API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def comprehensive_diagnosis(
        self, 
        symptoms: str,
        patient_info: Dict[str, Any],
        duration: Optional[str] = None,
        severity: Optional[str] = None,
        uploaded_files: Optional[list] = None,
        disease_category: str = "respiratory"
    ) -> Dict[str, Any]:
        """
        完整诊断工作流
        
        整合：个人信息 + 诊疗提交信息(MinerU提取) + 知识库信息 -> AI诊断

        Args:
            symptoms: 症状描述
            patient_info: 患者个人信息
            duration: 症状持续时间
            severity: 严重程度
            uploaded_files: 上传的文件列表(会被MinerU提取)
            disease_category: 疾病分类

        Returns:
            完整诊断结果
        """
        logger.info("开始完整诊断工作流...")
        
        # 1. 处理上传的文件（MinerU提取）
        extracted_texts = []
        if uploaded_files:
            logger.info(f"正在提取 {len(uploaded_files)} 个文件...")
            for file_url in uploaded_files:
                extraction_result = await self.extract_document_with_mineru(file_url)
                if extraction_result.get('success'):
                    text_content = extraction_result.get('text_content', '')
                    if text_content:
                        extracted_texts.append(text_content[:2000])  # 限制长度
                        logger.info(f"文件提取成功，内容长度: {len(text_content)}")
                else:
                    logger.warning(f"文件提取失败: {extraction_result.get('error')}")
        
        # 2. 查询知识库
        logger.info(f"正在查询知识库: {disease_category}...")
        kb_result = await self.query_knowledge_base(symptoms, disease_category)
        
        # 3. 构建完整的提示词
        prompt = self._build_diagnosis_prompt(
            patient_info=patient_info,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            extracted_texts=extracted_texts,
            knowledge_base=kb_result
        )
        
        logger.info("正在调用AI模型进行诊断...")
        
        # 4. 调用AI进行诊断
        messages = [
            {"role": "system", "content": "你是一位专业的全科医生，拥有丰富的临床经验。请根据提供的患者信息、症状描述、相关检查资料和医学知识库，给出专业的诊断意见。"},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_with_glm(messages)
        
        if result.get('success'):
            return {
                "success": True,
                "diagnosis": result['content'],
                "model_used": settings.ai_model_id,
                "tokens_used": result.get('usage', {}).get('total_tokens', 0),
                "workflow": {
                    "patient_info_included": bool(patient_info),
                    "files_processed": len(extracted_texts),
                    "knowledge_base_queried": kb_result.get('success', False),
                    "knowledge_source": kb_result.get('source', '')
                }
            }
        else:
            return {
                "success": False,
                "error": result.get('error'),
                "diagnosis": "AI 分析失败，请稍后重试"
            }

    def _build_diagnosis_prompt(
        self,
        patient_info: Dict[str, Any],
        symptoms: str,
        duration: Optional[str],
        severity: Optional[str],
        extracted_texts: list,
        knowledge_base: Dict[str, Any]
    ) -> str:
        """
        构建诊断提示词
        
        结构：个人信息 + 诊疗提交信息 + 知识库信息
        """
        prompt_parts = []
        
        # === 第一部分：个人信息 ===
        prompt_parts.append("=" * 50)
        prompt_parts.append("【第一部分：患者个人信息】")
        prompt_parts.append("=" * 50)
        
        if patient_info:
            prompt_parts.append(f"姓名: {patient_info.get('full_name', '未知')}")
            prompt_parts.append(f"性别: {patient_info.get('gender', '未知')}")
            prompt_parts.append(f"出生日期: {patient_info.get('date_of_birth', '未知')}")
            prompt_parts.append(f"联系电话: {patient_info.get('phone', '未知')}")
            prompt_parts.append(f"紧急联系人: {patient_info.get('emergency_contact', '未知')}")
            prompt_parts.append(f"居住地址: {patient_info.get('address', '未知')}")
            prompt_parts.append(f"备注信息: {patient_info.get('notes', '无')}")
        else:
            prompt_parts.append("暂无详细的个人信息")
        
        # === 第二部分：诊疗提交信息 ===
        prompt_parts.append("\n" + "=" * 50)
        prompt_parts.append("【第二部分：诊疗提交信息】")
        prompt_parts.append("=" * 50)
        
        prompt_parts.append(f"\n症状描述:\n{symptoms}")
        
        if duration:
            prompt_parts.append(f"\n症状持续时间: {duration}")
        
        if severity:
            prompt_parts.append(f"严重程度: {severity}")
        
        # 添加MinerU提取的文件内容
        if extracted_texts:
            prompt_parts.append("\n--- 上传的检查报告/资料（经MinerU提取）---")
            for i, text in enumerate(extracted_texts, 1):
                prompt_parts.append(f"\n[文件 {i} 内容]:")
                prompt_parts.append(text[:1500])  # 每个文件限制1500字符
        
        # === 第三部分：知识库信息 ===
        prompt_parts.append("\n" + "=" * 50)
        prompt_parts.append("【第三部分：医学知识库参考】")
        prompt_parts.append("=" * 50)
        
        if knowledge_base.get('success'):
            if knowledge_base.get('diseases_info'):
                prompt_parts.append("\n[相关疾病信息]:")
                prompt_parts.append(knowledge_base['diseases_info'])
            
            if knowledge_base.get('guidelines_info'):
                prompt_parts.append("\n[诊疗指南参考]:")
                prompt_parts.append(knowledge_base['guidelines_info'])
        else:
            prompt_parts.append("\n（知识库暂时无法访问，基于通用医学知识进行分析）")
        
        # === 诊断要求 ===
        prompt_parts.append("\n" + "=" * 50)
        prompt_parts.append("【诊断要求】")
        prompt_parts.append("=" * 50)
        prompt_parts.append("""
请基于以上三部分信息，提供以下诊断内容：

1. **初步诊断**：基于症状和检查资料给出可能的诊断（按可能性排序）
2. **诊断依据**：结合知识库说明诊断理由
3. **鉴别诊断**：列出需要排除的其他疾病
4. **建议检查**：列出建议做的进一步检查
5. **治疗方案**：基于知识库给出治疗建议
6. **注意事项**：用药提醒、生活建议等
7. **就医建议**：是否需要立即就医，建议就诊科室

请注意：
- 诊断仅供参考，不能替代专业医生的面诊
- 如有紧急情况，请立即就医
- 结合患者个人信息（如过敏史）给出个性化建议
""")
        
        return "\n".join(prompt_parts)

    async def analyze_symptoms(self, symptoms: str, patient_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        AI 分析症状（简化版，向后兼容）

        Args:
            symptoms: 症状描述
            patient_info: 患者信息（可选）

        Returns:
            AI 分析结果
        """
        # 调用完整的诊断流程
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
        提取医疗报告内容

        Args:
            file_url: 文件 URL

        Returns:
            结构化的医疗报告数据
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


# 全局实例
ai_service = AIService()
