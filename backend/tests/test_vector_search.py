import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.database import AsyncSessionLocal
from app.services.kb_vectorization_service import KnowledgeBaseVectorizationService
from app.services.vector_embedding_service import VectorEmbeddingService

async def test():
    async with AsyncSessionLocal() as db:
        # 测试VectorEmbeddingService直接调用
        print("测试VectorEmbeddingService...")
        vector_service = VectorEmbeddingService(db)
        
        # 获取配置
        config = await vector_service.get_active_config()
        print(f"配置URL: {config.api_url}")
        
        # 生成单个嵌入
        try:
            embedding = await vector_service.generate_embedding("测试文本")
            print(f"✅ 嵌入生成成功，维度: {len(embedding)}")
        except Exception as e:
            print(f"❌ 嵌入生成失败: {e}")
        
        # 测试知识库服务
        print("\n测试KnowledgeBaseVectorizationService...")
        kb_service = KnowledgeBaseVectorizationService(db)
        
        try:
            chunks = await kb_service.search_similar_chunks(
                query_text="儿童哮喘症状",
                disease_category="respiratory",
                top_k=3,
                min_similarity=0.5
            )
            print(f"✅ 搜索成功，找到 {len(chunks)} 个块")
            for i, chunk in enumerate(chunks[:2]):
                print(f"  块 {i+1}: {chunk.get('text', '')[:80]}...")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
