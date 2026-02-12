#!/usr/bin/env python3
"""
MinerU Document Extraction Test Script
Tests MinerU integration with medical document images

Usage:
    cd /home/houge/Dev/MediCare_AI/backend
    python3 test_mineru_extraction.py

Requirements:
    - Valid MinerU API token in .env file
    - Test images in /home/houge/ directory
"""

import asyncio
import httpx
import json
import base64
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Failed to import settings: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


class MinerUTester:
    """Test MinerU document extraction"""
    
    def __init__(self):
        self.api_url = settings.mineru_api_url
        self.token = settings.mineru_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def check_configuration(self) -> bool:
        """Check if MinerU is properly configured"""
        print("\n🔧 Checking MinerU configuration...")
        print(f"   API URL: {self.api_url}")
        print(f"   Token configured: {'✅ Yes' if self.token and self.token != 'your_mineru_token_here' else '❌ No (using placeholder)'}")
        
        if not self.token or self.token == 'your_mineru_token_here':
            print("\n⚠️  WARNING: MinerU token not configured!")
            print("   Please update MINERU_TOKEN in your .env file")
            return False
        return True
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    async def test_health_check(self) -> bool:
        """Test MinerU API health"""
        print("\n🏥 Testing MinerU API health...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try the main API endpoint
                response = await client.get(
                    "https://mineru.net/api/v4/health",
                    headers=self.headers
                )
                print(f"   Health check status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ API is accessible")
                    return True
                else:
                    print(f"   ⚠️  API returned: {response.text[:200]}")
                    return False
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False
    
    async def extract_document(self, image_path: str) -> dict:
        """Extract document using MinerU API"""
        filename = os.path.basename(image_path)
        print(f"\n📄 Testing extraction: {filename}")
        print(f"   File path: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"   ❌ File not found: {image_path}")
            return {"success": False, "error": "File not found"}
        
        # Get file info
        file_size = os.path.getsize(image_path)
        print(f"   File size: {file_size / 1024:.1f} KB")
        
        # Encode image
        try:
            image_data = self.encode_image(image_path)
            print(f"   Base64 encoded size: {len(image_data) / 1024:.1f} KB")
        except Exception as e:
            print(f"   ❌ Failed to encode image: {e}")
            return {"success": False, "error": f"Encoding failed: {e}"}
        
        # Determine mime type
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        # Prepare file data
        file_data = f"data:{mime_type};base64,{image_data}"
        
        # Call MinerU API
        print(f"   Calling MinerU API...")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "extract_type": "parse",
                        "file": file_data,
                        "ocr": True,
                        "extract_tables": True,
                        "extract_images": False
                    }
                )
                
                print(f"   Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('code') == 0:
                        data = result.get('data', {})
                        extracted_text = data.get('text', '')
                        markdown = data.get('markdown', '')
                        pages = data.get('pages', 0)
                        
                        print(f"   ✅ Extraction successful!")
                        print(f"   📊 Pages: {pages}")
                        print(f"   📝 Text length: {len(extracted_text)} characters")
                        print(f"   📄 Markdown length: {len(markdown)} characters")
                        
                        # Show preview
                        preview = extracted_text[:200] if extracted_text else markdown[:200]
                        if preview:
                            print(f"\n   📝 Preview:")
                            print(f"   {preview}...")
                        
                        return {
                            "success": True,
                            "data": data,
                            "text": extracted_text,
                            "markdown": markdown,
                            "pages": pages
                        }
                    else:
                        error_msg = result.get('msg', 'Unknown error')
                        print(f"   ❌ API error: code={result.get('code')}, msg={error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "code": result.get('code')
                        }
                else:
                    error_text = response.text[:500]
                    print(f"   ❌ HTTP error {response.status_code}: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {error_text}"
                    }
                    
        except httpx.TimeoutException:
            print(f"   ❌ Request timeout")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_tests(self):
        """Run all tests"""
        print("=" * 70)
        print("🧪 MinerU Document Extraction Test Suite")
        print("=" * 70)
        
        # Check configuration
        if not self.check_configuration():
            print("\n⚠️  Configuration check failed. Tests cannot continue.")
            print("   Please configure MINERU_TOKEN and try again.")
            return
        
        # Test images
        test_images = [
            "/home/houge/特殊病原体.jpg",
            "/home/houge/血常规.jpg"
        ]
        
        results = []
        
        for image_path in test_images:
            if os.path.exists(image_path):
                result = await self.extract_document(image_path)
                results.append({
                    "file": os.path.basename(image_path),
                    "success": result.get("success", False),
                    "error": result.get("error")
                })
            else:
                print(f"\n⚠️  Skipping {os.path.basename(image_path)}: File not found")
                results.append({
                    "file": os.path.basename(image_path),
                    "success": False,
                    "error": "File not found"
                })
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        
        passed = sum(1 for r in results if r["success"])
        failed = len(results) - passed
        
        for r in results:
            status = "✅ PASS" if r["success"] else "❌ FAIL"
            print(f"   {status} - {r['file']}")
            if not r["success"] and r["error"]:
                print(f"         Error: {r['error'][:100]}")
        
        print(f"\n   Total: {len(results)} | Passed: {passed} | Failed: {failed}")
        
        if passed == len(results):
            print("\n🎉 All tests passed! MinerU extraction is working correctly.")
        elif passed > 0:
            print("\n⚠️  Some tests failed. Check errors above.")
        else:
            print("\n❌ All tests failed. Please check your MinerU configuration.")


async def main():
    """Main test runner"""
    tester = MinerUTester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
