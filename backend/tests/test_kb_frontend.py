"""
测试知识库溯源API响应 / Test KB Attribution API Response
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.smart_rag_selector import SmartRAGSelector
from app.db.database import AsyncSessionLocal

async def test_kb_response():
    """测试知识库溯源数据结构"""
    print("=" * 60)
    print("测试知识库溯源API响应格式")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        selector = SmartRAGSelector(db)
        rag_result = await selector.select_knowledge_bases(
            symptoms='5岁儿童，反复咳嗽，夜间加重，伴有喘息声',
            patient_age=5,
            top_k=3,
            use_vector_search=True
        )
        
        # 模拟前端接收到的数据结构
        kb_sources = []
        for source in rag_result.get('sources', []):
            category = source.get('category', '')
            
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
            
            chunks_data = []
            for chunk in source.get('chunks', []):
                text = chunk.get('text', '')
                chunks_data.append({
                    "chunk_id": chunk.get('chunk_id'),
                    "section_title": chunk.get('section_title', category),
                    "text_preview": text[:200] + "..." if len(text) > 200 else text,
                    "similarity_score": chunk.get('similarity_score', 0),
                    "source_file": chunk.get('source_file')
                })
            
            kb_sources.append({
                "category": category,
                "category_name": category_names.get(category, category),
                "relevance_score": source.get('relevance_score', 0),
                "selection_reason": source.get('selection_reason', ''),
                "chunks_count": len(source.get('chunks', [])),
                "chunks": chunks_data
            })
        
        print(f"\n✅ 找到 {len(kb_sources)} 个知识库源:")
        print()
        
        for i, source in enumerate(kb_sources, 1):
            print(f"[{i}] {source['category_name']}")
            print(f"    分类: {source['category']}")
            print(f"    相关度: {source['relevance_score']:.2f}")
            print(f"    选择原因: {source['selection_reason']}")
            print(f"    引用分块数: {source['chunks_count']}")
            
            if source['chunks']:
                print(f"    引用内容预览:")
                for j, chunk in enumerate(source['chunks'][:2], 1):
                    print(f"      - [{j}] {chunk['section_title']} (相似度: {chunk['similarity_score']:.2f})")
                    print(f"        {chunk['text_preview'][:80]}...")
            print()
        
        # 模拟API响应
        api_response = {
            'done': True,
            'case_id': 'test-case-id',
            'knowledge_base_sources': kb_sources,
            'knowledge_base_selection_reasoning': rag_result.get('selection_reasoning', '')
        }
        
        print("=" * 60)
        print("模拟API响应数据结构:")
        print("=" * 60)
        import json
        print(json.dumps(api_response, indent=2, ensure_ascii=False)[:1500] + "...")
        
        return True

if __name__ == "__main__":
    success = asyncio.run(test_kb_response())
    sys.exit(0 if success else 1)
