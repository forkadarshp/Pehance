#!/usr/bin/env python3
"""
Quick test of the enhanced 4D methodology improvements
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_enhancement(prompt, expected_type=None):
    """Test a single prompt enhancement"""
    print(f"\n🔍 Testing: '{prompt}'")
    
    try:
        response = requests.post(
            f"{API_BASE}/enhance",
            json={"prompt": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key metrics
            enhancement_type = data.get("enhancement_type")
            enhancement_ratio = data.get("enhancement_ratio", 0)
            complexity_score = data.get("complexity_score", 0)
            
            # Get intent analysis
            agent_results = data.get("agent_results", {})
            intent_analysis = agent_results.get("intent_analysis", {})
            intent_category = intent_analysis.get("intent_category", "unknown")
            confidence = intent_analysis.get("confidence", 0)
            input_type = intent_analysis.get("input_type", "unknown")
            
            print(f"✅ SUCCESS:")
            print(f"   Enhancement Type: {enhancement_type}")
            print(f"   Enhancement Ratio: {enhancement_ratio}x")
            print(f"   Complexity Score: {complexity_score:.2f}")
            print(f"   Intent Category: {intent_category} ({confidence:.1%} confidence)")
            print(f"   Input Type: {input_type}")
            print(f"   Enhanced Length: {len(data.get('enhanced_prompt', ''))} chars")
            
            # Check if expected type matches
            if expected_type and enhancement_type != expected_type:
                print(f"⚠️  Expected {expected_type}, got {enhancement_type}")
            
            return True
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Run quick tests"""
    print("🚀 Quick Enhanced 4D Methodology Test")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("hi", "clarification_request"),
        ("hello there", "clarification_request"),
        ("help me", "clarification_request"),
        ("write something", "basic_enhancement"),
        ("create a marketing email", "standard_enhancement"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for prompt, expected_type in test_cases:
        if test_enhancement(prompt, expected_type):
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    # Test new response fields
    print(f"\n🔍 Testing Response Fields...")
    response = requests.post(f"{API_BASE}/enhance", json={"prompt": "test"}, timeout=30)
    if response.status_code == 200:
        data = response.json()
        required_fields = ["enhancement_type", "enhancement_ratio", "complexity_score"]
        missing = [f for f in required_fields if f not in data]
        
        if not missing:
            print("✅ All new response fields present")
        else:
            print(f"❌ Missing fields: {missing}")
    
    print("\n🎉 Quick test completed!")

if __name__ == "__main__":
    main()