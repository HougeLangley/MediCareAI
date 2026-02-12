"""
测试知识库溯源功能 / Test Knowledge Base Attribution
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.ai_service import ai_service

async def test_diagnosis_with_kb_attribution():
    """测试带知识库溯源的AI诊断"""
    print("=" * 60)
    print("测试AI诊断知识库溯源功能")
    print("=" * 60)
    
    # 模拟患者信息
    patient_info = {
        "full_name": "测试患者",
        "gender": "男",
        "date_of_birth": "2019-01-01",
        "phone": "13800138000"
    }
    
    # 测试症状 - 儿童哮喘相关
    symptoms = "5岁儿童，反复咳嗽3个月，夜间加重，伴有喘息声，运动后症状明显"
    
    print(f"\n患者症状: {symptoms}")
    print("\n调用AI诊断...")
    print("-" * 60)
    
    try:
        result = await ai_service.comprehensive_diagnosis(
            symptoms=symptoms,
            patient_info=patient_info,
            duration="3个月",
            severity="moderate",
            disease_category="respiratory",
            language="zh"
        )
        
        if result.get('success'):
            print("✅ 诊断成功!")
            print(f"\n使用的AI模型: {result.get('model_used', 'Unknown')}")
            print(f"Token使用量: {result.get('tokens_used', 0)}")
            print(f"请求耗时: {result.get('request_duration_ms', 0)}ms")
            
            # 检查知识库溯源信息
            kb_sources = result.get('knowledge_base_sources', [])
            print(f"\n📚 知识库溯源信息:")
            print(f"   引用知识库数量: {len(kb_sources)}")
            
            if kb_sources:
                for i, source in enumerate(kb_sources, 1):
                    print(f"\n   [{i}] {source.get('category_name', source.get('category'))}")
                    print(f"       分类: {source.get('category')}")
                    print(f"       相关度得分: {source.get('relevance_score', 0):.2f}")
                    print(f"       选择原因: {source.get('selection_reason')}")
                    print(f"       引用分块数: {source.get('chunks_count', 0)}")
                    
                    # 显示部分引用的内容
                    chunks = source.get('chunks', [])
                    if chunks:
                        print(f"       引用内容预览:")
                        for j, chunk in enumerate(chunks[:2], 1):  # 只显示前2个
                            print(f"         - [{j}] {chunk.get('section_title', 'Unknown')}")
                            print(f"           相似度: {chunk.get('similarity_score', 0):.2f}")
                            text_preview = chunk.get('text_preview', '')[:80]
                            print(f"           内容: {text_preview}...")
            else:
                print("   ⚠️ 未返回知识库溯源信息")
            
            # 显示选择原因
            reasoning = result.get('knowledge_base_selection_reasoning', '')
            if reasoning:
                print(f"\n🤔 知识库选择原因: {reasoning[:200]}...")
            
            print("\n" + "=" * 60)
            print("诊断结果预览:")
            print("=" * 60)
            diagnosis = result.get('diagnosis', '')
            print(diagnosis[:500] + "..." if len(diagnosis) > 500 else diagnosis)
            
            return True
        else:
            print(f"❌ 诊断失败: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_diagnosis_with_kb_attribution())
    sys.exit(0 if success else 1)
