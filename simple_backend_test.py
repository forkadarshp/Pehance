#!/usr/bin/env python3
"""
Simple Backend Test for Pehance Multi-Agent Enhancement System
"""

import requests
import json
import time

API_BASE = "http://localhost:8001/api"

def test_basic_api():
    """Test basic API connectivity"""
    print("🔍 Testing basic API connectivity...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=30)
        if response.status_code == 200:
            print("✅ Basic API connectivity: PASS")
            return True
        else:
            print(f"❌ Basic API connectivity: FAIL - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic API connectivity: FAIL - {str(e)}")
        return False

def test_enhance_endpoint():
    """Test the enhance endpoint"""
    print("🔍 Testing /api/enhance endpoint...")
    try:
        test_prompt = "Create a mobile app for tracking daily habits"
        response = requests.post(
            f"{API_BASE}/enhance",
            json={"prompt": test_prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["id", "original_prompt", "enhanced_prompt", "agent_results", "success"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Enhance endpoint: FAIL - Missing fields: {missing_fields}")
                return False
            
            # Check if enhancement happened
            if len(data["enhanced_prompt"]) <= len(test_prompt):
                print("❌ Enhance endpoint: FAIL - No enhancement occurred")
                return False
            
            print("✅ Enhance endpoint: PASS")
            print(f"   Original length: {len(test_prompt)} chars")
            print(f"   Enhanced length: {len(data['enhanced_prompt'])} chars")
            return True
            
        else:
            print(f"❌ Enhance endpoint: FAIL - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Enhance endpoint: FAIL - {str(e)}")
        return False

def test_intent_classification():
    """Test intent classification"""
    print("🔍 Testing intent classification...")
    try:
        test_cases = [
            {"prompt": "Build a REST API for user authentication", "expected": "technical"},
            {"prompt": "Write a creative story about time travel", "expected": "creative"},
            {"prompt": "Create a marketing strategy for product launch", "expected": "business"}
        ]
        
        passed = 0
        for test_case in test_cases:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_case["prompt"]},
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                actual_intent = intent_analysis.get("intent_category", "")
                
                if actual_intent == test_case["expected"]:
                    print(f"   ✅ '{test_case['prompt'][:30]}...' -> {actual_intent}")
                    passed += 1
                else:
                    print(f"   ❌ '{test_case['prompt'][:30]}...' -> Expected: {test_case['expected']}, Got: {actual_intent}")
            else:
                print(f"   ❌ '{test_case['prompt'][:30]}...' -> HTTP {response.status_code}")
            
            time.sleep(2)  # Delay between requests
        
        if passed == len(test_cases):
            print("✅ Intent classification: PASS")
            return True
        else:
            print(f"❌ Intent classification: FAIL - {passed}/{len(test_cases)} passed")
            return False
            
    except Exception as e:
        print(f"❌ Intent classification: FAIL - {str(e)}")
        return False

def test_multi_agent_system():
    """Test multi-agent system components"""
    print("🔍 Testing multi-agent system...")
    try:
        test_prompt = "Develop a comprehensive project management system"
        response = requests.post(
            f"{API_BASE}/enhance",
            json={"prompt": test_prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_results = data.get("agent_results", {})
            
            # Check for intent analysis
            intent_analysis = agent_results.get("intent_analysis", {})
            required_intent_fields = ["intent_category", "confidence", "complexity_level"]
            missing_intent_fields = [field for field in required_intent_fields if field not in intent_analysis]
            
            if missing_intent_fields:
                print(f"❌ Multi-agent system: FAIL - Missing intent fields: {missing_intent_fields}")
                return False
            
            # Check process steps
            process_steps = agent_results.get("process_steps", [])
            if not process_steps:
                print("❌ Multi-agent system: FAIL - No process steps recorded")
                return False
            
            print("✅ Multi-agent system: PASS")
            print(f"   Intent: {intent_analysis.get('intent_category')} ({intent_analysis.get('confidence', 0):.2f} confidence)")
            print(f"   Complexity: {intent_analysis.get('complexity_level')}")
            print(f"   Process steps: {len(process_steps)}")
            return True
            
        else:
            print(f"❌ Multi-agent system: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-agent system: FAIL - {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Pehance Backend Testing")
    print("=" * 50)
    
    tests = [
        test_basic_api,
        test_enhance_endpoint,
        test_intent_classification,
        test_multi_agent_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"🏁 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)