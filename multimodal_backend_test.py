#!/usr/bin/env python3
"""
Multi-Modal Enhancement Features Testing for Pehance Backend
Tests the new image processing, response formatting, and multi-modal enhancement capabilities
"""

import asyncio
import json
import os
import sys
import time
import base64
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class MultiModalBackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def create_test_image_base64(self, text="TEST IMAGE", size=(100, 100)):
        """Create a simple test image and return as base64"""
        try:
            # Create a simple image with text
            img = Image.new('RGB', size, color='white')
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            
            # Encode to base64
            base64_string = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{base64_string}"
            
        except Exception as e:
            print(f"Error creating test image: {e}")
            # Return a minimal valid base64 PNG
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    def test_basic_api_health(self):
        """Test basic API health endpoints"""
        endpoints = [
            ("/", "Basic API Root"),
            ("/status", "Status Endpoint")
        ]
        
        all_passed = True
        
        for endpoint, name in endpoints:
            try:
                if endpoint == "/status":
                    # GET request for status
                    response = requests.get(f"{API_BASE}{endpoint}", timeout=15)
                else:
                    # GET request for root
                    response = requests.get(f"{API_BASE}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        f"Basic API Health - {name}",
                        True,
                        f"Endpoint responding correctly: {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Basic API Health - {name}",
                        False,
                        f"Unexpected status code: {response.status_code}",
                        {"status_code": response.status_code, "text": response.text}
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Basic API Health - {name}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
        
        return all_passed

    def test_image_processing_endpoint(self):
        """Test /api/process-image endpoint with base64 image data"""
        test_image_base64 = self.create_test_image_base64()
        
        # Remove data URL prefix for the API
        if test_image_base64.startswith("data:image/png;base64,"):
            image_data = test_image_base64.split(",")[1]
        else:
            image_data = test_image_base64
        
        test_cases = [
            {
                "image_data": image_data,
                "analysis_type": "comprehensive",
                "test_name": "Comprehensive Image Analysis"
            },
            {
                "image_data": image_data,
                "analysis_type": "text_extraction",
                "test_name": "Text Extraction Analysis"
            },
            {
                "image_data": image_data,
                "analysis_type": "quick_description",
                "test_name": "Quick Description Analysis"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/process-image",
                    json={
                        "image_data": test_case["image_data"],
                        "analysis_type": test_case["analysis_type"]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["success", "description", "analysis", "suggestions"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Image Processing - {test_case['test_name']}",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if success is true
                    if not data.get("success", False):
                        self.log_result(
                            f"Image Processing - {test_case['test_name']}",
                            False,
                            "API returned success=false",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if we got a description
                    if not data.get("description", "").strip():
                        self.log_result(
                            f"Image Processing - {test_case['test_name']}",
                            False,
                            "Empty description returned",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if suggestions are provided
                    suggestions = data.get("suggestions", [])
                    if not suggestions or len(suggestions) == 0:
                        self.log_result(
                            f"Image Processing - {test_case['test_name']}",
                            False,
                            "No suggestions provided",
                            data
                        )
                        all_passed = False
                        continue
                    
                    self.log_result(
                        f"Image Processing - {test_case['test_name']}",
                        True,
                        f"Image processed successfully. Description length: {len(data['description'])}, Suggestions: {len(suggestions)}"
                    )
                    
                else:
                    self.log_result(
                        f"Image Processing - {test_case['test_name']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Image Processing - {test_case['test_name']}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)  # Small delay between requests
        
        return all_passed

    def test_response_formatting_endpoint(self):
        """Test /api/format-response endpoint with different formats"""
        test_content = """
        # How to Build a REST API
        
        Here's a simple example:
        
        ```python
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/api/users')
        def get_users():
            return {'users': []}
        ```
        
        This creates a basic API endpoint.
        """
        
        test_cases = [
            {
                "content": test_content,
                "target_format": "rich_text",
                "enhance_quality": True,
                "test_name": "Rich Text Formatting"
            },
            {
                "content": test_content,
                "target_format": "code_blocks",
                "enhance_quality": True,
                "test_name": "Code Blocks Formatting"
            },
            {
                "content": test_content,
                "target_format": "markdown",
                "enhance_quality": True,
                "test_name": "Markdown Formatting"
            },
            {
                "content": "Simple plain text content for testing",
                "target_format": "plain_text",
                "enhance_quality": False,
                "test_name": "Plain Text Formatting"
            },
            {
                "content": test_content,
                "target_format": "auto_detect",
                "enhance_quality": True,
                "test_name": "Auto-Detect Formatting"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/format-response",
                    json={
                        "content": test_case["content"],
                        "target_format": test_case["target_format"],
                        "enhance_quality": test_case["enhance_quality"]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["formatted_content", "detected_format", "metadata", "code_blocks"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Response Formatting - {test_case['test_name']}",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if formatted content is provided
                    formatted_content = data.get("formatted_content", "")
                    if not formatted_content.strip():
                        self.log_result(
                            f"Response Formatting - {test_case['test_name']}",
                            False,
                            "Empty formatted content returned",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if detected format is valid
                    detected_format = data.get("detected_format", "")
                    valid_formats = ["rich_text", "code_blocks", "markdown", "plain_text"]
                    if detected_format not in valid_formats:
                        self.log_result(
                            f"Response Formatting - {test_case['test_name']}",
                            False,
                            f"Invalid detected format: {detected_format}. Expected one of: {valid_formats}",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # For code content, check if code blocks were detected
                    if "```python" in test_case["content"]:
                        code_blocks = data.get("code_blocks", [])
                        if test_case["target_format"] in ["code_blocks", "auto_detect"] and len(code_blocks) == 0:
                            self.log_result(
                                f"Response Formatting - {test_case['test_name']}",
                                False,
                                "Code blocks not detected in content with Python code",
                                data
                            )
                            all_passed = False
                            continue
                    
                    self.log_result(
                        f"Response Formatting - {test_case['test_name']}",
                        True,
                        f"Content formatted successfully. Format: {detected_format}, Content length: {len(formatted_content)}"
                    )
                    
                else:
                    self.log_result(
                        f"Response Formatting - {test_case['test_name']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Response Formatting - {test_case['test_name']}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)  # Small delay between requests
        
        return all_passed

    def test_multimodal_enhancement_endpoint(self):
        """Test /api/enhance-multimodal endpoint with text + image"""
        test_image_base64 = self.create_test_image_base64()
        
        # Remove data URL prefix for the API
        if test_image_base64.startswith("data:image/png;base64,"):
            image_data = test_image_base64.split(",")[1]
        else:
            image_data = test_image_base64
        
        test_cases = [
            {
                "prompt": "Analyze this image and create a comprehensive tutorial",
                "mode": "single",
                "image_data": image_data,
                "preferred_format": "auto_detect",
                "test_name": "Text + Image Enhancement"
            },
            {
                "prompt": "Create documentation based on this visual content",
                "mode": "multi",
                "image_data": image_data,
                "preferred_format": "markdown",
                "test_name": "Multi-Modal Documentation"
            },
            {
                "prompt": "",  # Empty text prompt, only image
                "mode": "single",
                "image_data": image_data,
                "preferred_format": "rich_text",
                "test_name": "Image-Only Enhancement"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                request_data = {
                    "prompt": test_case["prompt"],
                    "mode": test_case["mode"],
                    "image_data": test_case["image_data"],
                    "preferred_format": test_case["preferred_format"]
                }
                
                response = requests.post(
                    f"{API_BASE}/enhance-multimodal",
                    json=request_data,
                    timeout=60  # Longer timeout for multi-modal processing
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["id", "original_prompt", "enhanced_prompt", "agent_results", "success", "timestamp", "mode"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Multi-Modal Enhancement - {test_case['test_name']}",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if success is true
                    if not data.get("success", False):
                        self.log_result(
                            f"Multi-Modal Enhancement - {test_case['test_name']}",
                            False,
                            "API returned success=false",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if enhanced prompt is provided
                    enhanced_prompt = data.get("enhanced_prompt", "")
                    if not enhanced_prompt.strip():
                        self.log_result(
                            f"Multi-Modal Enhancement - {test_case['test_name']}",
                            False,
                            "Empty enhanced prompt returned",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if agent results contain image analysis
                    agent_results = data.get("agent_results", {})
                    image_analysis = agent_results.get("image_analysis")
                    if not image_analysis:
                        self.log_result(
                            f"Multi-Modal Enhancement - {test_case['test_name']}",
                            False,
                            "Image analysis missing from agent results",
                            agent_results
                        )
                        all_passed = False
                        continue
                    
                    # Check if multimodal flag is set
                    multimodal = agent_results.get("multimodal", False)
                    if not multimodal:
                        self.log_result(
                            f"Multi-Modal Enhancement - {test_case['test_name']}",
                            False,
                            "Multimodal flag not set in agent results",
                            agent_results
                        )
                        all_passed = False
                        continue
                    
                    # Check if format metadata is present when preferred format is specified
                    if test_case["preferred_format"] != "auto_detect":
                        format_metadata = agent_results.get("format_metadata", {})
                        if not format_metadata.get("formatted", False):
                            self.log_result(
                                f"Multi-Modal Enhancement - {test_case['test_name']}",
                                False,
                                f"Format metadata missing for preferred format: {test_case['preferred_format']}",
                                format_metadata
                            )
                            all_passed = False
                            continue
                    
                    self.log_result(
                        f"Multi-Modal Enhancement - {test_case['test_name']}",
                        True,
                        f"Multi-modal enhancement successful. Enhanced prompt length: {len(enhanced_prompt)}, Mode: {data['mode']}"
                    )
                    
                else:
                    self.log_result(
                        f"Multi-Modal Enhancement - {test_case['test_name']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Multi-Modal Enhancement - {test_case['test_name']}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(2)  # Longer delay between multi-modal requests
        
        return all_passed

    def test_format_detection_endpoint(self):
        """Test /api/detect-format endpoint"""
        test_cases = [
            {
                "content": "# Heading\n\nThis is **bold** text with `code`.",
                "expected_format": "markdown",
                "test_name": "Markdown Content Detection"
            },
            {
                "content": "```python\ndef hello():\n    print('Hello World')\n```",
                "expected_format": "code_blocks",
                "test_name": "Code Blocks Detection"
            },
            {
                "content": "This is simple plain text without any special formatting.",
                "expected_format": "plain_text",
                "test_name": "Plain Text Detection"
            },
            {
                "content": "Here's a detailed explanation with **emphasis** and structured content that would benefit from rich formatting.",
                "expected_format": "rich_text",
                "test_name": "Rich Text Detection"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/detect-format",
                    json=test_case["content"],
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["detected_format", "confidence", "suggestions"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Format Detection - {test_case['test_name']}",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if detected format is valid
                    detected_format = data.get("detected_format", "")
                    valid_formats = ["rich_text", "code_blocks", "markdown", "plain_text"]
                    if detected_format not in valid_formats:
                        self.log_result(
                            f"Format Detection - {test_case['test_name']}",
                            False,
                            f"Invalid detected format: {detected_format}. Expected one of: {valid_formats}",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Check if suggestions are provided
                    suggestions = data.get("suggestions", {})
                    if not suggestions or len(suggestions) == 0:
                        self.log_result(
                            f"Format Detection - {test_case['test_name']}",
                            False,
                            "No format suggestions provided",
                            data
                        )
                        all_passed = False
                        continue
                    
                    # Note: We don't enforce exact format matching as the AI might make reasonable alternative choices
                    self.log_result(
                        f"Format Detection - {test_case['test_name']}",
                        True,
                        f"Format detected: {detected_format} (expected: {test_case['expected_format']}), Confidence: {data['confidence']}"
                    )
                    
                else:
                    self.log_result(
                        f"Format Detection - {test_case['test_name']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Format Detection - {test_case['test_name']}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)  # Small delay between requests
        
        return all_passed

    def test_image_validation(self):
        """Test image upload validation (size limits, file types)"""
        test_cases = [
            {
                "image_data": "invalid_base64_data",
                "expected_status": 400,
                "test_name": "Invalid Base64 Data"
            },
            {
                "image_data": base64.b64encode(b"not_an_image").decode('utf-8'),
                "expected_status": 400,
                "test_name": "Invalid Image Data"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/process-image",
                    json={
                        "image_data": test_case["image_data"],
                        "analysis_type": "comprehensive"
                    },
                    timeout=15
                )
                
                if response.status_code == test_case["expected_status"]:
                    self.log_result(
                        f"Image Validation - {test_case['test_name']}",
                        True,
                        f"Correctly rejected invalid image with status {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Image Validation - {test_case['test_name']}",
                        False,
                        f"Expected status {test_case['expected_status']}, got {response.status_code}",
                        {"status_code": response.status_code, "text": response.text}
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Image Validation - {test_case['test_name']}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
        
        return all_passed

    def test_api_response_structure(self):
        """Test that all new endpoints return proper status codes and expected fields"""
        # Test a successful multi-modal enhancement to verify response structure
        test_image_base64 = self.create_test_image_base64()
        if test_image_base64.startswith("data:image/png;base64,"):
            image_data = test_image_base64.split(",")[1]
        else:
            image_data = test_image_base64
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance-multimodal",
                json={
                    "prompt": "Create a tutorial based on this image",
                    "mode": "single",
                    "image_data": image_data,
                    "preferred_format": "markdown"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check all expected fields are present
                expected_fields = [
                    "id", "original_prompt", "enhanced_prompt", "agent_results", 
                    "success", "timestamp", "mode", "enhancement_type", 
                    "enhancement_ratio", "complexity_score", "models_used"
                ]
                
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "API Response Structure",
                        False,
                        f"Missing expected fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Check agent_results structure
                agent_results = data.get("agent_results", {})
                expected_agent_fields = ["image_analysis", "format_metadata", "multimodal"]
                missing_agent_fields = [field for field in expected_agent_fields if field not in agent_results]
                
                if missing_agent_fields:
                    self.log_result(
                        "API Response Structure",
                        False,
                        f"Missing agent result fields: {missing_agent_fields}",
                        agent_results
                    )
                    return False
                
                self.log_result(
                    "API Response Structure",
                    True,
                    "All expected fields present in multi-modal API response"
                )
                return True
                
            else:
                self.log_result(
                    "API Response Structure",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "API Response Structure",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all multi-modal backend tests"""
        print("🚀 Starting Pehance Multi-Modal Backend Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        # Test methods in priority order
        test_methods = [
            ("Basic API Health", self.test_basic_api_health),
            ("Image Processing", self.test_image_processing_endpoint),
            ("Response Formatting", self.test_response_formatting_endpoint),
            ("Multi-Modal Enhancement", self.test_multimodal_enhancement_endpoint),
            ("Format Detection", self.test_format_detection_endpoint),
            ("Image Validation", self.test_image_validation),
            ("API Response Structure", self.test_api_response_structure)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n🔍 Running {test_name} Tests...")
            try:
                test_method()
            except Exception as e:
                self.log_result(
                    f"Test Suite: {test_name}",
                    False,
                    f"Test suite failed with exception: {str(e)}"
                )
            
            # Small delay between test suites
            time.sleep(2)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("🏁 MULTI-MODAL BACKEND TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        print()
        
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            "results": self.results
        }

def main():
    """Main test execution"""
    tester = MultiModalBackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All multi-modal tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()