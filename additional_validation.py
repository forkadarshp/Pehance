#!/usr/bin/env python3
"""
Additional validation tests to ensure we didn't break anything
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_enhance_with_none_prompt():
    """Test enhance endpoint when prompt is None"""
    try:
        response = requests.post(
            f"{BASE_URL}/enhance",
            json={"mode": "single"},  # No prompt field
            timeout=30
        )
        
        print(f"Enhance with no prompt field - Status: {response.status_code}")
        if response.status_code == 400:
            print(f"✅ Correct 400 error: {response.json()['detail']}")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multimodal_with_valid_prompt():
    """Test multimodal endpoint with valid prompt"""
    try:
        response = requests.post(
            f"{BASE_URL}/enhance-multimodal",
            json={"prompt": "Write a story about AI", "mode": "single"},
            timeout=60
        )
        
        print(f"Multimodal with valid prompt - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Enhanced prompt length: {len(data.get('enhanced_prompt', ''))}")
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 ADDITIONAL VALIDATION TESTS")
    test_enhance_with_none_prompt()
    test_multimodal_with_valid_prompt()
    print("✅ ADDITIONAL TESTS COMPLETED")