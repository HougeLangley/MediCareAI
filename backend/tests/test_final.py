import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.database import AsyncSessionLocal
from app.models.models import VectorEmbeddingConfig
from app.services.vector_embedding_service import VectorEmbeddingService

async def test():
    async with AsyncSessionLocal() as db:
        service = VectorEmbeddingService(db)
        
        # 获取配置
        config = await service.get_active_config()
        print(f"配置URL: {config.api_url}")
        print(f"配置模型: {config.model_id}")
        
        # 测试生成嵌入
        texts = ["儿童支气管哮喘是一种常见的慢性呼吸道疾病"]
        try:
            embeddings = await service.generate_embeddings_batch(texts)
            print(f"✅ 成功生成嵌入!")
            print(f"向量维度: {len(embeddings[0])}")
        except Exception as e:
            print(f"❌ 失败: {e}")

if __name__ == "__main__":
    asyncio.run(test())
