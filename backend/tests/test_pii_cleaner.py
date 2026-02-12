#!/usr/bin/env python3
"""
PII Cleaner Test Script | PII清理测试脚本
Tests the PII cleaning functionality to ensure privacy protection works correctly.
"""

import sys
import json
sys.path.insert(0, '/home/houge/Dev/MediCare_AI/backend')

from app.services.pii_cleaner_service import pii_cleaner, clean_text, detect_pii, anonymize_for_sharing


def test_basic_pii_cleaning():
    """Test basic PII cleaning functionality"""
    print("\n" + "="*60)
    print("Test 1: Basic PII Cleaning")
    print("="*60)
    
    test_text = """
    患者姓名：张三
    身份证号：110101199001011234
    电话：13800138000
    地址：北京市朝阳区某某街道123号
    就诊医院：北京协和医院
    主治医生：李医生
    病历号：M202401001
    
    患者主诉：咳嗽、发热3天
    现病史：患者于3天前无明显诱因出现咳嗽，伴有发热...
    """
    
    result = pii_cleaner.clean_text(test_text)
    
    print(f"Original text length: {len(test_text)}")
    print(f"Cleaned text length: {len(result['cleaned_text'])}")
    print(f"PII detected: {len(result['pii_detected'])}")
    print(f"Confidence score: {result['confidence_score']:.2f}")
    
    print("\nDetected PII items:")
    for pii in result['pii_detected']:
        print(f"  - {pii['type']}: {pii['original'][:30]}... -> {pii['replacement']}")
    
    print("\nCleaned text preview:")
    print(result['cleaned_text'][:500])
    
    # Verify all PII types are detected
    detected_types = set([pii['type'] for pii in result['pii_detected']])
    expected_types = {'name', 'id_number', 'phone', 'hospital', 'doctor_name', 'address', 'medical_record_number'}
    
    missing = expected_types - detected_types
    if missing:
        print(f"\n⚠️  Warning: Missing PII types: {missing}")
        return False
    else:
        print(f"\n✅ All expected PII types detected")
        return True


def test_anonymize_for_sharing():
    """Test anonymization for data sharing"""
    print("\n" + "="*60)
    print("Test 2: Anonymize for Sharing")
    print("="*60)
    
    patient_info = {
        "full_name": "张三",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "address": "北京市朝阳区",
        "phone": "13800138000"
    }
    
    medical_text = """
    患者张三，男，34岁，因咳嗽、发热3天就诊。
    既往史：无特殊。
    查体：体温38.5℃，咽部充血...
    """
    
    result = anonymize_for_sharing(medical_text, patient_info)
    
    print("Anonymous profile:")
    print(json.dumps(result['anonymous_profile'], indent=2, ensure_ascii=False))
    
    print(f"\nOriginal text: {medical_text[:100]}...")
    print(f"\nAnonymized text: {result['anonymized_text'][:100]}...")
    print(f"\nSafe for sharing: {result['safe_for_sharing']}")
    print(f"PII detected count: {result['pii_cleaning']['stats']['total_pii']}")
    
    if result['safe_for_sharing'] and result['anonymous_profile']:
        print("\n✅ Anonymization successful")
        return True
    else:
        print("\n❌ Anonymization failed")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*60)
    print("Test 3: Edge Cases")
    print("="*60)
    
    # Empty text
    result = pii_cleaner.clean_text("")
    assert result['cleaned_text'] == "", "Empty text should return empty"
    print("✅ Empty text handled correctly")
    
    # None input
    result = pii_cleaner.clean_text(None)
    assert result['cleaned_text'] is None, "None input should return None"
    print("✅ None input handled correctly")
    
    # Text without PII
    clean_text = "这是一段正常的医疗描述，没有任何个人身份信息。"
    result = pii_cleaner.clean_text(clean_text)
    assert len(result['pii_detected']) == 0, "Clean text should have no PII"
    assert result['confidence_score'] == 1.0, "Clean text should have confidence 1.0"
    print("✅ Text without PII handled correctly")
    
    return True


def test_confidence_scoring():
    """Test confidence scoring"""
    print("\n" + "="*60)
    print("Test 4: Confidence Scoring")
    print("="*60)
    
    # High confidence (ID number)
    text_with_id = "身份证号：110101199001011234"
    result = pii_cleaner.clean_text(text_with_id)
    avg_confidence = sum([pii['confidence'] for pii in result['pii_detected']]) / len(result['pii_detected'])
    print(f"ID number detection confidence: {avg_confidence:.2f}")
    assert avg_confidence >= 0.9, "ID number should have high confidence"
    
    # Medium confidence (name)
    text_with_name = "患者姓名：张三"
    result = pii_cleaner.clean_text(text_with_name)
    avg_confidence = sum([pii['confidence'] for pii in result['pii_detected']]) / len(result['pii_detected'])
    print(f"Name detection confidence: {avg_confidence:.2f}")
    
    print("\n✅ Confidence scoring working correctly")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PII Cleaner Service Test Suite")
    print("="*60)
    
    tests = [
        ("Basic PII Cleaning", test_basic_pii_cleaning),
        ("Anonymize for Sharing", test_anonymize_for_sharing),
        ("Edge Cases", test_edge_cases),
        ("Confidence Scoring", test_confidence_scoring),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
