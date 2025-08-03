#!/usr/bin/env python3
"""
Focused Backend Testing for Pehance - Testing the key functionality after Groq API key update
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_basic_connectivity():
    """Test basic API connectivity"""
    print("🔗 Testing basic API connectivity...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            print("✅ Basic API connectivity: PASS")
            return True
        else:
            print(f"❌ Basic API connectivity: FAIL - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic API connectivity: FAIL - {str(e)}")
        return False

def test_groq_api_connectivity():
    """Test Groq API connectivity using the test-groq endpoint"""
    print("🤖 Testing Groq API connectivity...")
    try:
        response = requests.post(
            f"{API_BASE}/test-groq",
            json={"prompt": "Hello, this is a test message"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False) and data.get("response", "").strip():
                print(f"✅ Groq API connectivity: PASS - Model: {data.get('model', 'unknown')}")
                return True
            else:
                print(f"❌ Groq API connectivity: FAIL - Invalid response: {data}")
                return False
        else:
            print(f"❌ Groq API connectivity: FAIL - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Groq API connectivity: FAIL - {str(e)}")
        return False

def test_enhance_endpoint_simple():
    """Test enhance endpoint with simple prompt"""
    print("✨ Testing enhance endpoint with simple prompt...")
    try:
        response = requests.post(
            f"{API_BASE}/enhance",
            json={"prompt": "Write a short story about AI"},
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["id", "original_prompt", "enhanced_prompt", "agent_results", "success"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Simple enhance test: FAIL - Missing fields: {missing_fields}")
                return False
            
            if data.get("success", False):
                intent_analysis = data.get("agent_results", {}).get("intent_analysis", {})
                intent_category = intent_analysis.get("intent_category", "unknown")
                print(f"✅ Simple enhance test: PASS - Intent: {intent_category}")
                return True
            else:
                print(f"❌ Simple enhance test: FAIL - Success=false, Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ Simple enhance test: FAIL - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Simple enhance test: FAIL - {str(e)}")
        return False

def test_enhance_endpoint_technical():
    """Test enhance endpoint with technical prompt"""
    print("🔧 Testing enhance endpoint with technical prompt...")
    try:
        response = requests.post(
            f"{API_BASE}/enhance",
            json={"prompt": "Help me build a React application for managing tasks"},
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                intent_analysis = data.get("agent_results", {}).get("intent_analysis", {})
                intent_category = intent_analysis.get("intent_category", "unknown")
                enhanced_prompt = data.get("enhanced_prompt", "")
                
                # Check if it's classified as technical
                if intent_category == "technical":
                    print(f"✅ Technical enhance test: PASS - Correctly classified as technical")
                    return True
                else:
                    print(f"❌ Technical enhance test: FAIL - Expected 'technical', got '{intent_category}'")
                    return False
            else:
                print(f"❌ Technical enhance test: FAIL - Success=false, Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ Technical enhance test: FAIL - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Technical enhance test: FAIL - {str(e)}")
        return False

def test_enhance_endpoint_business():
    """Test enhance endpoint with business prompt"""
    print("💼 Testing enhance endpoint with business prompt...")
    try:
        response = requests.post(
            f"{API_BASE}/enhance",
            json={"prompt": "Create a comprehensive marketing strategy for a SaaS startup"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                intent_analysis = data.get("agent_results", {}).get("intent_analysis", {})
                intent_category = intent_analysis.get("intent_category", "unknown")
                
                # Check if it's classified as business
                if intent_category == "business":
                    print(f"✅ Business enhance test: PASS - Correctly classified as business")
                    return True
                else:
                    print(f"❌ Business enhance test: FAIL - Expected 'business', got '{intent_category}'")
                    return False
            else:
                print(f"❌ Business enhance test: FAIL - Success=false, Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ Business enhance test: FAIL - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Business enhance test: FAIL - {str(e)}")
        return False

def main():
    """Run focused backend tests"""
    print("🚀 Starting Focused Pehance Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    tests = [
        test_basic_connectivity,
        test_groq_api_connectivity,
        test_enhance_endpoint_simple,
        test_enhance_endpoint_technical,
        test_enhance_endpoint_business
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print("🏁 FOCUSED TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 All focused tests passed! The Groq API connectivity issue is resolved.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)