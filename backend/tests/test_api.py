import asyncio
import sys
sys.path.insert(0, '/app')

import httpx

async def test_api():
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/"
    api_key = "sk-196dd431d25e41e998e9298d4d598baa"
    
    test_texts = [
        "儿童支气管哮喘是一种常见的慢性呼吸道疾病",
        "哮喘的诊断需要结合临床症状和肺功能检查"
    ]
    
    print(f"测试API调用...")
    print(f"URL: {api_url}embeddings")
    print(f"文本1长度: {len(test_texts[0])}")
    print(f"文本2长度: {len(test_texts[1])}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{api_url}embeddings",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "text-embedding-v3",
                "input": {
                    "texts": test_texts
                },
                "parameters": {
                    "text_type": "document"
                }
            }
        )
        
        print(f"\n响应状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功!")
            print(f"嵌入数量: {len(result['output']['embeddings'])}")
            print(f"向量维度: {len(result['output']['embeddings'][0]['embedding'])}")
        else:
            print(f"❌ 失败: {response.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_api())
