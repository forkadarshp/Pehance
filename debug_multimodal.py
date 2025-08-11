#!/usr/bin/env python3
"""
Debug the multimodal endpoint 422 error
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

# Test case that's failing
test_case = {"mode": "multi"}

try:
    response = requests.post(
        f"{BASE_URL}/enhance-multimodal",
        json=test_case,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")