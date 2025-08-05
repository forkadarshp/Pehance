#!/usr/bin/env python3
"""
Review Request Specific Testing for Pehance Enhanced Multi-Model System
Tests the specific requirements mentioned in the review request
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class ReviewRequestTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: dict = None):
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
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_basic_endpoints(self):
        """Test /api/ and /api/status endpoints for basic connectivity"""
        
        # Test /api/ endpoint
        try:
            response = requests.get(f"{API_BASE}/", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Basic API Endpoint (/api/)",
                    True,
                    f"API responding correctly: {data.get('message', 'No message')}"
                )
            else:
                self.log_result(
                    "Basic API Endpoint (/api/)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Basic API Endpoint (/api/)",
                False,
                f"Connection error: {str(e)}"
            )
        
        # Test /api/status endpoint
        try:
            response = requests.get(f"{API_BASE}/status", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Status API Endpoint (/api/status)",
                    True,
                    f"Status endpoint responding correctly with {len(data)} status checks"
                )
            else:
                self.log_result(
                    "Status API Endpoint (/api/status)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Status API Endpoint (/api/status)",
                False,
                f"Connection error: {str(e)}"
            )

    def test_models_endpoint(self):
        """Test /api/test-models endpoint to verify model availability"""
        try:
            response = requests.get(f"{API_BASE}/test-models", timeout=60)
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["success", "models", "summary", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Model Availability Test (/api/test-models)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Check if success is true
                if not data.get("success", False):
                    self.log_result(
                        "Model Availability Test (/api/test-models)",
                        False,
                        "API returned success=false",
                        data
                    )
                    return
                
                # Check models data
                models = data.get("models", {})
                summary = data.get("summary", {})
                
                # Verify key models are present
                key_models = [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant", 
                    "moonshotai/kimi-k2-instruct"
                ]
                
                available_key_models = []
                for model in key_models:
                    if model in models and models[model].get("available", False):
                        available_key_models.append(model)
                
                total_models = summary.get("total_models", 0)
                available_models = summary.get("available_models", 0)
                availability_rate = summary.get("availability_rate", "0%")
                
                self.log_result(
                    "Model Availability Test (/api/test-models)",
                    True,
                    f"Models tested: {total_models}, Available: {available_models} ({availability_rate}). Key models available: {available_key_models}"
                )
                
            else:
                self.log_result(
                    "Model Availability Test (/api/test-models)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Model Availability Test (/api/test-models)",
                False,
                f"Request error: {str(e)}"
            )

    def test_enhance_single_mode(self):
        """Test /api/enhance endpoint with single mode"""
        test_prompt = "help me code a todo list"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check enhanced response structure
                required_fields = ["enhanced_prompt", "agent_results", "models_used", "enhancement_type", "enhancement_ratio", "complexity_score"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Enhanced Response Structure (Single Mode)",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Check models_used field
                models_used = data.get("models_used", {})
                if not models_used or not isinstance(models_used, dict):
                    self.log_result(
                        "Enhanced Response Structure (Single Mode)",
                        False,
                        "models_used field is missing or not a dictionary",
                        data
                    )
                    return
                
                # Check that enhancement happened
                enhanced_prompt = data.get("enhanced_prompt", "")
                if len(enhanced_prompt) <= len(test_prompt) * 2:
                    self.log_result(
                        "Enhanced Response Structure (Single Mode)",
                        False,
                        f"Enhancement seems insufficient. Original: {len(test_prompt)} chars, Enhanced: {len(enhanced_prompt)} chars"
                    )
                    return
                
                # Check enhancement type (should not be clarification_request in single mode)
                enhancement_type = data.get("enhancement_type", "")
                if enhancement_type == "clarification_request":
                    self.log_result(
                        "Enhanced Response Structure (Single Mode)",
                        False,
                        "Single mode should not ask for clarification, but got clarification_request enhancement type"
                    )
                    return
                
                self.log_result(
                    "Enhanced Response Structure (Single Mode)",
                    True,
                    f"All fields present. Enhancement: {enhancement_type}, Ratio: {data.get('enhancement_ratio', 0):.1f}x, Models used: {list(models_used.keys())}"
                )
                
            else:
                self.log_result(
                    "Enhanced Response Structure (Single Mode)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Enhanced Response Structure (Single Mode)",
                False,
                f"Request error: {str(e)}"
            )

    def test_enhance_multi_mode(self):
        """Test /api/enhance endpoint with multi mode"""
        test_prompt = "help me"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "multi"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that multi mode allows clarification requests
                enhancement_type = data.get("enhancement_type", "")
                
                # For a vague prompt like "help me", multi mode should ask for clarification
                if enhancement_type != "clarification_request":
                    self.log_result(
                        "Multi Mode Clarification Test",
                        False,
                        f"Expected clarification_request for vague prompt in multi mode, got: {enhancement_type}"
                    )
                    return
                
                # Check models_used field is present
                models_used = data.get("models_used", {})
                if not models_used:
                    self.log_result(
                        "Multi Mode Clarification Test",
                        False,
                        "models_used field is missing"
                    )
                    return
                
                self.log_result(
                    "Multi Mode Clarification Test",
                    True,
                    f"Multi mode correctly asks for clarification. Enhancement type: {enhancement_type}, Models used: {list(models_used.keys())}"
                )
                
            else:
                self.log_result(
                    "Multi Mode Clarification Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Multi Mode Clarification Test",
                False,
                f"Request error: {str(e)}"
            )

    def test_enhanced_greetings(self):
        """Test enhanced response for basic greetings"""
        test_prompt = "hi"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check intent analysis
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                
                # Should be classified as greeting
                intent_category = intent_analysis.get("intent_category", "")
                if intent_category != "greeting":
                    self.log_result(
                        "Enhanced Greeting Response Test",
                        False,
                        f"Expected 'greeting' classification, got: {intent_category}"
                    )
                    return
                
                # Check confidence is high
                confidence = intent_analysis.get("confidence", 0)
                if confidence < 0.8:
                    self.log_result(
                        "Enhanced Greeting Response Test",
                        False,
                        f"Low confidence for greeting classification: {confidence}"
                    )
                    return
                
                # Check enhancement type
                enhancement_type = data.get("enhancement_type", "")
                complexity_score = data.get("complexity_score", 0)
                
                self.log_result(
                    "Enhanced Greeting Response Test",
                    True,
                    f"Greeting correctly classified with {confidence:.2f} confidence. Enhancement: {enhancement_type}, Complexity: {complexity_score:.2f}"
                )
                
            else:
                self.log_result(
                    "Enhanced Greeting Response Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Enhanced Greeting Response Test",
                False,
                f"Request error: {str(e)}"
            )

    def test_complex_technical_request(self):
        """Test complex technical request to verify multi-agent system"""
        test_prompt = "Build a scalable microservices architecture for an e-commerce platform with real-time inventory management, user authentication, payment processing, and analytics dashboard"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=90
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that it's classified as technical
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                intent_category = intent_analysis.get("intent_category", "")
                
                if intent_category != "technical":
                    self.log_result(
                        "Complex Technical Request Test",
                        False,
                        f"Expected 'technical' classification, got: {intent_category}"
                    )
                    return
                
                # Check complexity score is high
                complexity_score = data.get("complexity_score", 0)
                if complexity_score < 0.6:
                    self.log_result(
                        "Complex Technical Request Test",
                        False,
                        f"Expected high complexity score for complex technical request, got: {complexity_score}"
                    )
                    return
                
                # Check models_used includes high-reasoning models
                models_used = data.get("models_used", {})
                high_reasoning_models = ["llama-3.3-70b-versatile", "moonshotai/kimi-k2-instruct"]
                used_high_reasoning = any(model in str(models_used.values()) for model in high_reasoning_models)
                
                if not used_high_reasoning:
                    self.log_result(
                        "Complex Technical Request Test",
                        False,
                        f"Expected high-reasoning models for complex request. Models used: {models_used}"
                    )
                    return
                
                # Check enhancement ratio is reasonable
                enhancement_ratio = data.get("enhancement_ratio", 0)
                if enhancement_ratio < 5:
                    self.log_result(
                        "Complex Technical Request Test",
                        False,
                        f"Expected significant enhancement for complex request, got ratio: {enhancement_ratio}"
                    )
                    return
                
                self.log_result(
                    "Complex Technical Request Test",
                    True,
                    f"Complex technical request handled correctly. Intent: {intent_category}, Complexity: {complexity_score:.2f}, Enhancement ratio: {enhancement_ratio:.1f}x, High-reasoning models used: {used_high_reasoning}"
                )
                
            else:
                self.log_result(
                    "Complex Technical Request Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Complex Technical Request Test",
                False,
                f"Request error: {str(e)}"
            )

    def run_review_tests(self):
        """Run all review request specific tests"""
        print("🚀 Starting Review Request Specific Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        # Run all tests as specified in review request
        test_methods = [
            self.test_basic_endpoints,
            self.test_models_endpoint,
            self.test_enhance_single_mode,
            self.test_enhance_multi_mode,
            self.test_enhanced_greetings,
            self.test_complex_technical_request
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(
                    f"Test Method: {test_method.__name__}",
                    False,
                    f"Test method failed with exception: {str(e)}"
                )
            
            # Small delay between test suites
            time.sleep(2)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("🏁 REVIEW REQUEST TEST SUMMARY")
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
    tester = ReviewRequestTester()
    summary = tester.run_review_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All review request tests passed!")
        return 0
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        return 1

if __name__ == "__main__":
    main()