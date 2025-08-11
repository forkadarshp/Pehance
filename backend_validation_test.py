#!/usr/bin/env python3
"""
Backend Validation Testing for Recent Changes
Focus: Empty prompt validation and detect-format endpoint testing
"""

import requests
import json
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8001/api"
TIMEOUT = 30

def log_test(test_name, status, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {status_symbol} {test_name}")
    if details:
        print(f"    {details}")

def test_basic_connectivity():
    """Test basic API connectivity"""
    print("\n🔍 BASIC CONNECTIVITY TESTS")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            log_test("GET /api/", "PASS", f"Response: {response.json()}")
        else:
            log_test("GET /api/", "FAIL", f"Status: {response.status_code}")
            
        # Test status endpoint
        response = requests.get(f"{BASE_URL}/status", timeout=TIMEOUT)
        if response.status_code == 200:
            log_test("GET /api/status", "PASS", f"Status checks count: {len(response.json())}")
        else:
            log_test("GET /api/status", "FAIL", f"Status: {response.status_code}")
            
    except Exception as e:
        log_test("Basic Connectivity", "FAIL", f"Connection error: {str(e)}")

def test_enhance_empty_prompt_validation():
    """Test /api/enhance endpoint with empty prompt validation"""
    print("\n🔍 ENHANCE ENDPOINT EMPTY PROMPT VALIDATION")
    
    test_cases = [
        {"prompt": "", "mode": "single", "expected_detail": "Prompt cannot be empty"},
        {"prompt": "   ", "mode": "single", "expected_detail": "Prompt cannot be empty"},
        {"prompt": "\n\t  \n", "mode": "single", "expected_detail": "Prompt cannot be empty"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/enhance",
                json=test_case,
                timeout=TIMEOUT
            )
            
            if response.status_code == 400:
                response_data = response.json()
                if response_data.get("detail") == test_case["expected_detail"]:
                    log_test(f"Empty prompt test {i}", "PASS", f"Correct 400 error: {response_data['detail']}")
                else:
                    log_test(f"Empty prompt test {i}", "FAIL", f"Wrong error message: {response_data.get('detail')}")
            else:
                log_test(f"Empty prompt test {i}", "FAIL", f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            log_test(f"Empty prompt test {i}", "FAIL", f"Request error: {str(e)}")

def test_enhance_multimodal_validation():
    """Test /api/enhance-multimodal endpoint validation"""
    print("\n🔍 ENHANCE-MULTIMODAL ENDPOINT VALIDATION")
    
    test_cases = [
        {
            "prompt": "", 
            "mode": "multi", 
            "expected_detail": "Either prompt or image_data is required"
        },
        {
            "prompt": "   ", 
            "mode": "multi", 
            "expected_detail": "Either prompt or image_data is required"
        },
        {
            "mode": "multi", 
            "expected_detail": "Either prompt or image_data is required"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/enhance-multimodal",
                json=test_case,
                timeout=TIMEOUT
            )
            
            if response.status_code == 400:
                response_data = response.json()
                if response_data.get("detail") == test_case["expected_detail"]:
                    log_test(f"Multimodal validation test {i}", "PASS", f"Correct 400 error: {response_data['detail']}")
                else:
                    log_test(f"Multimodal validation test {i}", "FAIL", f"Wrong error message: {response_data.get('detail')}")
            else:
                log_test(f"Multimodal validation test {i}", "FAIL", f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            log_test(f"Multimodal validation test {i}", "FAIL", f"Request error: {str(e)}")

def test_detect_format_endpoint():
    """Test /api/detect-format endpoint with JSON body and response model"""
    print("\n🔍 DETECT-FORMAT ENDPOINT TESTING")
    
    test_cases = [
        {
            "content": "some text with ```code``` and # headings",
            "expected_fields": ["detected_format", "confidence", "suggestions"]
        },
        {
            "content": "# This is a markdown heading\n\n## Subheading\n\n- List item 1\n- List item 2",
            "expected_fields": ["detected_format", "confidence", "suggestions"]
        },
        {
            "content": "```python\ndef hello():\n    print('Hello World')\n```",
            "expected_fields": ["detected_format", "confidence", "suggestions"]
        }
    ]
    
    valid_formats = ["rich_text", "code_blocks", "markdown", "plain_text", "auto_detect"]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/detect-format",
                json={"content": test_case["content"]},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check required fields
                missing_fields = []
                for field in test_case["expected_fields"]:
                    if field not in response_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    log_test(f"Detect format test {i}", "FAIL", f"Missing fields: {missing_fields}")
                else:
                    # Check if detected_format is valid
                    detected_format = response_data.get("detected_format")
                    if detected_format in valid_formats:
                        log_test(f"Detect format test {i}", "PASS", 
                               f"Format: {detected_format}, Confidence: {response_data.get('confidence')}")
                    else:
                        log_test(f"Detect format test {i}", "WARN", 
                               f"Unexpected format: {detected_format} (not in enum)")
            else:
                log_test(f"Detect format test {i}", "FAIL", f"Expected 200, got {response.status_code}")
                
        except Exception as e:
            log_test(f"Detect format test {i}", "FAIL", f"Request error: {str(e)}")

def test_sanity_check_working_endpoints():
    """Sanity check that we didn't break existing working endpoints"""
    print("\n🔍 SANITY CHECK - EXISTING ENDPOINTS")
    
    try:
        # Test enhance with valid prompt
        response = requests.post(
            f"{BASE_URL}/enhance",
            json={"prompt": "Write a story about AI", "mode": "single"},
            timeout=60  # Longer timeout for actual enhancement
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if "enhanced_prompt" in response_data and len(response_data["enhanced_prompt"]) > 50:
                log_test("Valid enhance request", "PASS", f"Enhanced prompt length: {len(response_data['enhanced_prompt'])}")
            else:
                log_test("Valid enhance request", "FAIL", "Enhanced prompt too short or missing")
        else:
            log_test("Valid enhance request", "FAIL", f"Status: {response.status_code}")
            
    except Exception as e:
        log_test("Valid enhance request", "FAIL", f"Request error: {str(e)}")

def main():
    """Run all validation tests"""
    print("🚀 BACKEND VALIDATION TESTING - RECENT CHANGES")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all test suites
    test_basic_connectivity()
    test_enhance_empty_prompt_validation()
    test_enhance_multimodal_validation()
    test_detect_format_endpoint()
    test_sanity_check_working_endpoints()
    
    print("\n✅ BACKEND VALIDATION TESTING COMPLETED")

if __name__ == "__main__":
    main()