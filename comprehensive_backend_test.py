#!/usr/bin/env python3
"""
Comprehensive Backend Regression Testing for Pehance
Tests all endpoints as specified in the review request
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

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Sample base64 image for testing (small 1x1 pixel PNG)
SAMPLE_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

class ComprehensiveBackendTester:
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

    def test_root_endpoint(self):
        """Test GET /api/ (root endpoint)"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result(
                        "GET /api/ (root)",
                        True,
                        f"Root endpoint responding: {data.get('message')}"
                    )
                    return True
                else:
                    self.log_result(
                        "GET /api/ (root)",
                        False,
                        "Missing 'message' field in response",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "GET /api/ (root)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "GET /api/ (root)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_status_endpoints(self):
        """Test GET /api/status (health) and POST /api/status (create)"""
        # Test GET /api/status
        try:
            response = requests.get(f"{API_BASE}/status", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "GET /api/status (health)",
                    True,
                    f"Status endpoint responding with {len(data)} status checks"
                )
            else:
                self.log_result(
                    "GET /api/status (health)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "GET /api/status (health)",
                False,
                f"Request error: {str(e)}"
            )
            return False

        # Test POST /api/status
        try:
            test_data = {"client_name": "test_client_regression"}
            response = requests.post(f"{API_BASE}/status", json=test_data, timeout=30)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "client_name", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "POST /api/status (create)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                if data["client_name"] != test_data["client_name"]:
                    self.log_result(
                        "POST /api/status (create)",
                        False,
                        f"Client name mismatch: expected {test_data['client_name']}, got {data['client_name']}"
                    )
                    return False
                
                self.log_result(
                    "POST /api/status (create)",
                    True,
                    f"Status check created with ID: {data['id']}"
                )
                return True
            else:
                self.log_result(
                    "POST /api/status (create)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/status (create)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_model_availability(self):
        """Test GET /api/test-models (model availability summary)"""
        try:
            response = requests.get(f"{API_BASE}/test-models", timeout=60)
            if response.status_code == 200:
                data = response.json()
                
                # Check required top-level fields
                required_fields = ["success", "models", "summary", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "GET /api/test-models",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                if not data.get("success", False):
                    self.log_result(
                        "GET /api/test-models",
                        False,
                        "API returned success=false",
                        data
                    )
                    return False
                
                # Check summary structure
                summary = data.get("summary", {})
                required_summary_fields = ["total_models", "available_models", "availability_rate"]
                missing_summary_fields = [field for field in required_summary_fields if field not in summary]
                
                if missing_summary_fields:
                    self.log_result(
                        "GET /api/test-models",
                        False,
                        f"Missing summary fields: {missing_summary_fields}",
                        summary
                    )
                    return False
                
                # Check models structure
                models = data.get("models", {})
                if not models:
                    self.log_result(
                        "GET /api/test-models",
                        False,
                        "No models found in response"
                    )
                    return False
                
                # Check at least one model has proper structure
                first_model_name = list(models.keys())[0]
                first_model = models[first_model_name]
                required_model_fields = ["available", "status", "performance_tokens_sec", "features", "tier"]
                missing_model_fields = [field for field in required_model_fields if field not in first_model]
                
                if missing_model_fields:
                    self.log_result(
                        "GET /api/test-models",
                        False,
                        f"Missing model fields in {first_model_name}: {missing_model_fields}",
                        first_model
                    )
                    return False
                
                self.log_result(
                    "GET /api/test-models",
                    True,
                    f"Model availability: {summary['available_models']}/{summary['total_models']} ({summary['availability_rate']})"
                )
                return True
            else:
                self.log_result(
                    "GET /api/test-models",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "GET /api/test-models",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_enhance_endpoint_validation(self):
        """Test POST /api/enhance with empty prompt validation (should return 400)"""
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": ""},
                timeout=30
            )
            
            if response.status_code == 400:
                self.log_result(
                    "POST /api/enhance (empty prompt validation)",
                    True,
                    "Correctly returned 400 for empty prompt"
                )
                return True
            else:
                self.log_result(
                    "POST /api/enhance (empty prompt validation)",
                    False,
                    f"Expected 400 for empty prompt, got {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/enhance (empty prompt validation)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_enhance_endpoint_single_mode(self):
        """Test POST /api/enhance in single mode with valid prompt"""
        test_prompt = "Create a comprehensive guide for learning Python programming"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ["enhanced_prompt", "agent_results", "mode", "enhancement_type", "enhancement_ratio", "complexity_score", "models_used"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "POST /api/enhance (single mode)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify mode is single
                if data.get("mode") != "single":
                    self.log_result(
                        "POST /api/enhance (single mode)",
                        False,
                        f"Expected mode 'single', got '{data.get('mode')}'"
                    )
                    return False
                
                # Verify enhancement occurred
                if data["enhanced_prompt"] == test_prompt:
                    self.log_result(
                        "POST /api/enhance (single mode)",
                        False,
                        "Enhanced prompt is identical to original - no enhancement occurred"
                    )
                    return False
                
                # Verify no clarification follow-ups in single mode
                enhanced_prompt = data["enhanced_prompt"].lower()
                clarification_indicators = ["what would you like", "could you specify", "would you prefer", "do you want"]
                has_clarification = any(indicator in enhanced_prompt for indicator in clarification_indicators)
                
                if has_clarification:
                    self.log_result(
                        "POST /api/enhance (single mode)",
                        False,
                        "Single mode should not contain clarification follow-ups"
                    )
                    return False
                
                self.log_result(
                    "POST /api/enhance (single mode)",
                    True,
                    f"Single mode working correctly. Enhancement ratio: {data.get('enhancement_ratio', 0)}x, Type: {data.get('enhancement_type')}"
                )
                return True
            else:
                self.log_result(
                    "POST /api/enhance (single mode)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/enhance (single mode)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_enhance_endpoint_multi_mode(self):
        """Test POST /api/enhance in multi mode with valid prompt"""
        test_prompt = "Help me with my project"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "multi"},
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ["enhanced_prompt", "agent_results", "mode", "enhancement_type", "enhancement_ratio", "complexity_score"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "POST /api/enhance (multi mode)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify mode is multi
                if data.get("mode") != "multi":
                    self.log_result(
                        "POST /api/enhance (multi mode)",
                        False,
                        f"Expected mode 'multi', got '{data.get('mode')}'"
                    )
                    return False
                
                # For vague prompts in multi mode, clarification requests are acceptable
                enhancement_type = data.get("enhancement_type", "")
                if enhancement_type == "clarification_request":
                    self.log_result(
                        "POST /api/enhance (multi mode)",
                        True,
                        f"Multi mode correctly requesting clarification for vague prompt. Type: {enhancement_type}"
                    )
                    return True
                
                # If not clarification, verify enhancement occurred
                if data["enhanced_prompt"] == test_prompt:
                    self.log_result(
                        "POST /api/enhance (multi mode)",
                        False,
                        "Enhanced prompt is identical to original - no enhancement occurred"
                    )
                    return False
                
                self.log_result(
                    "POST /api/enhance (multi mode)",
                    True,
                    f"Multi mode working correctly. Enhancement ratio: {data.get('enhancement_ratio', 0)}x, Type: {enhancement_type}"
                )
                return True
            else:
                self.log_result(
                    "POST /api/enhance (multi mode)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/enhance (multi mode)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_format_response_endpoint(self):
        """Test POST /api/format-response with different target_format values"""
        test_content = "This is a sample content for formatting. It includes code: print('hello world') and some explanatory text."
        
        formats_to_test = ["rich_text", "code_blocks", "markdown", "plain_text", "auto_detect"]
        
        for target_format in formats_to_test:
            try:
                response = requests.post(
                    f"{API_BASE}/format-response",
                    json={
                        "content": test_content,
                        "target_format": target_format,
                        "enhance_quality": True
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required response fields
                    required_fields = ["formatted_content", "detected_format", "metadata", "code_blocks"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"POST /api/format-response ({target_format})",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        continue
                    
                    # Verify formatting occurred
                    if not data.get("formatted_content"):
                        self.log_result(
                            f"POST /api/format-response ({target_format})",
                            False,
                            "Empty formatted_content in response"
                        )
                        continue
                    
                    self.log_result(
                        f"POST /api/format-response ({target_format})",
                        True,
                        f"Format: {data.get('detected_format')}, Content length: {len(data.get('formatted_content', ''))}"
                    )
                else:
                    self.log_result(
                        f"POST /api/format-response ({target_format})",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    f"POST /api/format-response ({target_format})",
                    False,
                    f"Request error: {str(e)}"
                )
            
            time.sleep(1)  # Small delay between requests

    def test_detect_format_endpoint(self):
        """Test POST /api/detect-format with content string"""
        test_cases = [
            {
                "content": "# This is a markdown title\n\n## Subtitle\n\n- List item 1\n- List item 2",
                "expected_format": "markdown",
                "test_name": "Markdown content"
            },
            {
                "content": "def hello_world():\n    print('Hello, World!')\n    return True",
                "expected_format": "code",
                "test_name": "Code content"
            },
            {
                "content": "This is plain text content without any special formatting.",
                "expected_format": "plain_text",
                "test_name": "Plain text content"
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/detect-format",
                    json={"content": test_case["content"]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required response fields
                    required_fields = ["detected_format", "confidence", "suggestions"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"POST /api/detect-format ({test_case['test_name']})",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        continue
                    
                    # Verify format detection
                    detected_format = data.get("detected_format", "")
                    if not detected_format:
                        self.log_result(
                            f"POST /api/detect-format ({test_case['test_name']})",
                            False,
                            "Empty detected_format in response"
                        )
                        continue
                    
                    self.log_result(
                        f"POST /api/detect-format ({test_case['test_name']})",
                        True,
                        f"Detected format: {detected_format}, Confidence: {data.get('confidence')}"
                    )
                else:
                    self.log_result(
                        f"POST /api/detect-format ({test_case['test_name']})",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    f"POST /api/detect-format ({test_case['test_name']})",
                    False,
                    f"Request error: {str(e)}"
                )
            
            time.sleep(1)  # Small delay between requests

    def test_process_image_endpoint(self):
        """Test POST /api/process-image with base64 image"""
        analysis_types = ["comprehensive", "text_extraction", "quick_description"]
        
        for analysis_type in analysis_types:
            try:
                response = requests.post(
                    f"{API_BASE}/process-image",
                    json={
                        "image_data": SAMPLE_BASE64_IMAGE,
                        "analysis_type": analysis_type
                    },
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required response fields
                    required_fields = ["success", "description", "analysis", "suggestions"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"POST /api/process-image ({analysis_type})",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        continue
                    
                    # Verify success
                    if not data.get("success", False):
                        self.log_result(
                            f"POST /api/process-image ({analysis_type})",
                            False,
                            "API returned success=false",
                            data
                        )
                        continue
                    
                    # Verify description exists
                    if not data.get("description"):
                        self.log_result(
                            f"POST /api/process-image ({analysis_type})",
                            False,
                            "Empty description in response"
                        )
                        continue
                    
                    # Verify analysis structure
                    analysis = data.get("analysis", {})
                    if not isinstance(analysis, dict):
                        self.log_result(
                            f"POST /api/process-image ({analysis_type})",
                            False,
                            "Analysis field is not a dictionary"
                        )
                        continue
                    
                    # Verify suggestions
                    suggestions = data.get("suggestions", [])
                    if not isinstance(suggestions, list):
                        self.log_result(
                            f"POST /api/process-image ({analysis_type})",
                            False,
                            "Suggestions field is not a list"
                        )
                        continue
                    
                    self.log_result(
                        f"POST /api/process-image ({analysis_type})",
                        True,
                        f"Image processed successfully. Description length: {len(data.get('description', ''))}, Suggestions: {len(suggestions)}"
                    )
                else:
                    self.log_result(
                        f"POST /api/process-image ({analysis_type})",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    f"POST /api/process-image ({analysis_type})",
                    False,
                    f"Request error: {str(e)}"
                )
            
            time.sleep(2)  # Longer delay for image processing

    def test_enhance_multimodal_text_and_image(self):
        """Test POST /api/enhance-multimodal with text+image"""
        try:
            response = requests.post(
                f"{API_BASE}/enhance-multimodal",
                json={
                    "prompt": "Analyze this image and create a detailed description",
                    "image_data": SAMPLE_BASE64_IMAGE,
                    "mode": "single",
                    "preferred_format": "rich_text"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ["enhanced_prompt", "agent_results", "mode"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "POST /api/enhance-multimodal (text+image)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Check agent_results for multimodal flags
                agent_results = data.get("agent_results", {})
                if not agent_results.get("multimodal", False):
                    self.log_result(
                        "POST /api/enhance-multimodal (text+image)",
                        False,
                        "Multimodal flag not set in agent_results"
                    )
                    return False
                
                # Check for image analysis
                if "image_analysis" not in agent_results:
                    self.log_result(
                        "POST /api/enhance-multimodal (text+image)",
                        False,
                        "Image analysis missing from agent_results"
                    )
                    return False
                
                # Check for format metadata when preferred_format specified
                if "format_metadata" not in agent_results:
                    self.log_result(
                        "POST /api/enhance-multimodal (text+image)",
                        False,
                        "Format metadata missing when preferred_format specified"
                    )
                    return False
                
                self.log_result(
                    "POST /api/enhance-multimodal (text+image)",
                    True,
                    f"Multimodal enhancement successful. Enhanced length: {len(data.get('enhanced_prompt', ''))}"
                )
                return True
            else:
                self.log_result(
                    "POST /api/enhance-multimodal (text+image)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/enhance-multimodal (text+image)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_enhance_multimodal_image_only(self):
        """Test POST /api/enhance-multimodal with image-only"""
        try:
            response = requests.post(
                f"{API_BASE}/enhance-multimodal",
                json={
                    "image_data": SAMPLE_BASE64_IMAGE,
                    "mode": "single",
                    "preferred_format": "markdown"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ["enhanced_prompt", "agent_results", "mode"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "POST /api/enhance-multimodal (image-only)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Check agent_results for multimodal flags
                agent_results = data.get("agent_results", {})
                if not agent_results.get("multimodal", False):
                    self.log_result(
                        "POST /api/enhance-multimodal (image-only)",
                        False,
                        "Multimodal flag not set in agent_results"
                    )
                    return False
                
                # Check for image analysis
                if "image_analysis" not in agent_results:
                    self.log_result(
                        "POST /api/enhance-multimodal (image-only)",
                        False,
                        "Image analysis missing from agent_results"
                    )
                    return False
                
                # Check for format metadata when preferred_format specified
                format_metadata = agent_results.get("format_metadata", {})
                if not format_metadata.get("formatted", False):
                    self.log_result(
                        "POST /api/enhance-multimodal (image-only)",
                        False,
                        "Format metadata indicates content was not formatted despite preferred_format"
                    )
                    return False
                
                self.log_result(
                    "POST /api/enhance-multimodal (image-only)",
                    True,
                    f"Image-only multimodal enhancement successful. Format: {format_metadata.get('format_type')}"
                )
                return True
            else:
                self.log_result(
                    "POST /api/enhance-multimodal (image-only)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/enhance-multimodal (image-only)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_enhance_multimodal_validation(self):
        """Test POST /api/enhance-multimodal validation (should return 400 when both prompt and image are missing)"""
        try:
            response = requests.post(
                f"{API_BASE}/enhance-multimodal",
                json={"mode": "single"},
                timeout=30
            )
            
            if response.status_code == 400:
                self.log_result(
                    "POST /api/enhance-multimodal (validation)",
                    True,
                    "Correctly returned 400 when both prompt and image are missing"
                )
                return True
            else:
                self.log_result(
                    "POST /api/enhance-multimodal (validation)",
                    False,
                    f"Expected 400 for missing prompt and image, got {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "POST /api/enhance-multimodal (validation)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Regression Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test methods in order of review request
        test_methods = [
            # 1) Basic endpoints
            self.test_root_endpoint,
            self.test_status_endpoints,
            
            # 2) Model availability
            self.test_model_availability,
            
            # 3) Enhance endpoint tests
            self.test_enhance_endpoint_validation,
            self.test_enhance_endpoint_single_mode,
            self.test_enhance_endpoint_multi_mode,
            
            # 4) Response formatting
            self.test_format_response_endpoint,
            self.test_detect_format_endpoint,
            
            # 5) Image processing
            self.test_process_image_endpoint,
            
            # 6) Multimodal enhancement
            self.test_enhance_multimodal_text_and_image,
            self.test_enhance_multimodal_image_only,
            self.test_enhance_multimodal_validation,
        ]
        
        for test_method in test_methods:
            try:
                print(f"Running {test_method.__name__}...")
                test_method()
            except Exception as e:
                self.log_result(
                    f"Test Method: {test_method.__name__}",
                    False,
                    f"Test method failed with exception: {str(e)}"
                )
            
            # Small delay between test suites
            time.sleep(1)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🏁 COMPREHENSIVE BACKEND TEST SUMMARY")
        print("=" * 80)
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
    tester = ComprehensiveBackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All comprehensive backend tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()