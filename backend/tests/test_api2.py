import asyncio
import sys
sys.path.insert(0, '/app')

import httpx

async def test_api():
    api_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
    api_key = "sk-196dd431d25e41e998e9298d4d598baa"
    
    test_texts = [
        "儿童支气管哮喘是一种常见的慢性呼吸道疾病",
        "哮喘的诊断需要结合临床症状和肺功能检查"
    ]
    
    print(f"测试API调用(尝试不同格式)...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 尝试原始阿里云格式
        response = await client.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "text-embedding-v3",
                "input": {
                    "texts": test_texts
                }
            }
        )
        
        print(f"\n响应状态: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")

if __name__ == "__main__":
    asyncio.run(test_api())
