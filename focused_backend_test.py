#!/usr/bin/env python3
"""
Focused Backend Testing for Pehance Enhanced Prompt Functionality
Tests the specific requirements from the review request
"""

import json
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class PehanceFocusedTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
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
            "details": details
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_basic_health_endpoints(self):
        """Test the basic backend health endpoints (/api/ and /api/status)"""
        
        # Test /api/ endpoint
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_result(
                        "Basic Health Endpoint (/api/)",
                        True,
                        f"Endpoint responding correctly with message: {data.get('message')}"
                    )
                else:
                    self.log_result(
                        "Basic Health Endpoint (/api/)",
                        False,
                        f"Unexpected response: {data}"
                    )
            else:
                self.log_result(
                    "Basic Health Endpoint (/api/)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Basic Health Endpoint (/api/)",
                False,
                f"Request error: {str(e)}"
            )
        
        # Test /api/status endpoint
        try:
            response = requests.get(f"{API_BASE}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Status Health Endpoint (/api/status)",
                        True,
                        f"Status endpoint responding correctly with {len(data)} status checks"
                    )
                else:
                    self.log_result(
                        "Status Health Endpoint (/api/status)",
                        False,
                        f"Expected list response, got: {type(data)}"
                    )
            else:
                self.log_result(
                    "Status Health Endpoint (/api/status)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Status Health Endpoint (/api/status)",
                False,
                f"Request error: {str(e)}"
            )

    def test_enhance_endpoint_with_sample_prompt(self):
        """Test the /api/enhance endpoint with the specific sample prompt from review request"""
        
        sample_prompt = "Help me create a comprehensive marketing strategy for a new SaaS product targeting small businesses"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": sample_prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if enhancement occurred
                enhanced_prompt = data.get("enhanced_prompt", "")
                if len(enhanced_prompt) > len(sample_prompt) * 2:
                    self.log_result(
                        "Sample Prompt Enhancement",
                        True,
                        f"Successfully enhanced prompt from {len(sample_prompt)} to {len(enhanced_prompt)} characters"
                    )
                    return data
                else:
                    self.log_result(
                        "Sample Prompt Enhancement",
                        False,
                        f"Enhancement insufficient: {len(enhanced_prompt)} chars vs original {len(sample_prompt)} chars"
                    )
                    return None
            else:
                self.log_result(
                    "Sample Prompt Enhancement",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Sample Prompt Enhancement",
                False,
                f"Request error: {str(e)}"
            )
            return None

    def test_multi_agent_system_functionality(self, sample_response_data):
        """Verify the multi-agent system is functioning properly"""
        
        if not sample_response_data:
            self.log_result(
                "Multi-Agent System Functionality",
                False,
                "No sample response data available for testing"
            )
            return
        
        agent_results = sample_response_data.get("agent_results", {})
        
        # Check for required multi-agent components
        required_components = [
            "intent_analysis",
            "enhanced_prompt", 
            "process_steps"
        ]
        
        missing_components = [comp for comp in required_components if comp not in agent_results]
        
        if missing_components:
            self.log_result(
                "Multi-Agent System Functionality",
                False,
                f"Missing multi-agent components: {missing_components}"
            )
            return
        
        # Check process steps for multi-agent pipeline
        process_steps = agent_results.get("process_steps", [])
        expected_steps = [
            "intent_classification",
            "knowledge_research", 
            "best_practices_gathering",
            "dynamic_enhancement"
        ]
        
        missing_steps = [step for step in expected_steps if step not in process_steps]
        
        if missing_steps:
            self.log_result(
                "Multi-Agent System Functionality",
                False,
                f"Missing process steps: {missing_steps}. Found: {process_steps}"
            )
            return
        
        self.log_result(
            "Multi-Agent System Functionality",
            True,
            f"All multi-agent components present. Process steps: {process_steps}"
        )

    def test_response_structure(self, sample_response_data):
        """Check response structure includes enhanced_prompt and agent_results with intent_analysis"""
        
        if not sample_response_data:
            self.log_result(
                "Response Structure Validation",
                False,
                "No sample response data available for testing"
            )
            return
        
        # Check top-level required fields
        required_top_level = [
            "id", "original_prompt", "enhanced_prompt", 
            "agent_results", "success", "timestamp"
        ]
        
        missing_top_level = [field for field in required_top_level if field not in sample_response_data]
        
        if missing_top_level:
            self.log_result(
                "Response Structure Validation",
                False,
                f"Missing top-level fields: {missing_top_level}"
            )
            return
        
        # Check agent_results structure
        agent_results = sample_response_data.get("agent_results", {})
        intent_analysis = agent_results.get("intent_analysis", {})
        
        required_intent_fields = ["intent_category", "confidence", "specific_domain", "complexity_level"]
        missing_intent_fields = [field for field in required_intent_fields if field not in intent_analysis]
        
        if missing_intent_fields:
            self.log_result(
                "Response Structure Validation",
                False,
                f"Missing intent_analysis fields: {missing_intent_fields}"
            )
            return
        
        # Validate intent analysis values
        intent_category = intent_analysis.get("intent_category")
        confidence = intent_analysis.get("confidence")
        
        if intent_category != "business":
            self.log_result(
                "Response Structure Validation",
                False,
                f"Expected 'business' intent for marketing strategy prompt, got: {intent_category}"
            )
            return
        
        if not isinstance(confidence, (int, float)) or confidence < 0.8:
            self.log_result(
                "Response Structure Validation",
                False,
                f"Expected high confidence (>0.8) for clear business prompt, got: {confidence}"
            )
            return
        
        self.log_result(
            "Response Structure Validation",
            True,
            f"All required fields present. Intent: {intent_category}, Confidence: {confidence:.2f}"
        )

    def test_api_frontend_compatibility(self):
        """Confirm the API is compatible with the sophisticated frontend interface"""
        
        # Test with different prompt types that the frontend might send
        test_prompts = [
            {
                "prompt": "Write a creative story about artificial intelligence",
                "expected_intent": "creative"
            },
            {
                "prompt": "Build a scalable React application with authentication",
                "expected_intent": "technical"
            },
            {
                "prompt": "Develop a business plan for a startup",
                "expected_intent": "business"
            }
        ]
        
        all_compatible = True
        
        for test_case in test_prompts:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    actual_intent = intent_analysis.get("intent_category", "")
                    
                    if actual_intent == test_case["expected_intent"]:
                        print(f"   ✅ {test_case['expected_intent'].title()} prompt classified correctly")
                    else:
                        print(f"   ⚠️  {test_case['expected_intent'].title()} prompt classified as {actual_intent}")
                        # Don't fail the test for this, as classification can vary
                else:
                    print(f"   ❌ {test_case['expected_intent'].title()} prompt failed: HTTP {response.status_code}")
                    all_compatible = False
                    
            except Exception as e:
                print(f"   ❌ {test_case['expected_intent'].title()} prompt error: {str(e)}")
                all_compatible = False
            
            time.sleep(1)  # Small delay between requests
        
        if all_compatible:
            self.log_result(
                "API Frontend Compatibility",
                True,
                "API successfully handles various prompt types from frontend"
            )
        else:
            self.log_result(
                "API Frontend Compatibility",
                False,
                "API compatibility issues detected with frontend prompt types"
            )

    def run_focused_tests(self):
        """Run all focused tests based on review requirements"""
        print("🎯 Starting Focused Pehance Backend Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        # 1. Test basic backend health endpoints
        self.test_basic_health_endpoints()
        
        # 2. Test the /api/enhance endpoint with sample prompt
        sample_response = self.test_enhance_endpoint_with_sample_prompt()
        
        # 3. Verify multi-agent system functionality
        self.test_multi_agent_system_functionality(sample_response)
        
        # 4. Check response structure
        self.test_response_structure(sample_response)
        
        # 5. Confirm API compatibility with frontend
        self.test_api_frontend_compatibility()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("🏁 FOCUSED TEST SUMMARY")
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
    tester = PehanceFocusedTester()
    summary = tester.run_focused_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All focused tests passed!")
        return 0
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)