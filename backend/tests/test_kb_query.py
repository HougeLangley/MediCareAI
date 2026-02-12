import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.database import AsyncSessionLocal
from app.services.smart_rag_selector import SmartRAGSelector

async def test_kb_query():
    """测试知识库查询"""
    print("🧪 测试知识库查询功能...")
    
    async with AsyncSessionLocal() as db:
        # 创建RAG选择器
        selector = SmartRAGSelector(db)
        
        # 测试查询 - 儿童哮喘症状
        test_symptoms = [
            "5岁儿童反复咳嗽、喘息，夜间加重",
            "孩子运动后气喘，呼吸困难",
            "婴儿出现湿疹，随后咳嗽喘息"
        ]
        
        for symptoms in test_symptoms:
            print(f"\n📝 测试症状: {symptoms}")
            try:
                result = await selector.select_knowledge_bases(
                    symptoms=symptoms,
                    patient_age=5,
                    patient_gender="male",
                    top_k=3,
                    use_vector_search=True
                )
                
                print(f"✅ 查询成功!")
                print(f"   找到 {len(result.get('sources', []))} 个知识源")
                print(f"   推理: {result.get('reasoning', '无')[:100]}...")
                
                for i, source in enumerate(result.get('sources', [])[:2]):
                    print(f"\n   来源 {i+1}:")
                    print(f"     类别: {source.get('category', 'N/A')}")
                    print(f"     相关度: {source.get('relevance_score', 0):.2f}")
                    print(f"     块数: {len(source.get('chunks', []))}")
                    
                    # 显示第一个块的内容预览
                    chunks = source.get('chunks', [])
                    if chunks:
                        print(f"     内容预览: {chunks[0].get('text', '')[:100]}...")
                
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kb_query())
