#!/usr/bin/env python3
"""
Multi-Model Integration System Testing for Pehance
Tests the enhanced multi-model system with specific scenarios from review request
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class MultiModelSystemTester:
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
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
        print()

    def test_model_availability(self):
        """Test /api/test-models endpoint to confirm all models including moonshotai/kimi-k2-instruct are available"""
        try:
            response = requests.get(f"{API_BASE}/test-models", timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["success", "models", "summary"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Model Availability Test",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                if not data.get("success", False):
                    self.log_result(
                        "Model Availability Test",
                        False,
                        "API returned success=false",
                        data
                    )
                    return False
                
                models = data.get("models", {})
                summary = data.get("summary", {})
                
                # Check for specific models mentioned in review request
                expected_models = [
                    "moonshotai/kimi-k2-instruct",
                    "qwen-qwq-32b", 
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant"
                ]
                
                available_expected_models = []
                unavailable_expected_models = []
                
                for model in expected_models:
                    if model in models and models[model].get("available", False):
                        available_expected_models.append(model)
                    else:
                        unavailable_expected_models.append(model)
                
                # Check tier system
                tier_models_found = {}
                for model_name, model_info in models.items():
                    tier = model_info.get("tier", "Unknown")
                    if tier not in tier_models_found:
                        tier_models_found[tier] = []
                    tier_models_found[tier].append(model_name)
                
                details = f"Total models: {summary.get('total_models', 0)}, Available: {summary.get('available_models', 0)} ({summary.get('availability_rate', '0%')})"
                details += f"\nExpected models available: {len(available_expected_models)}/{len(expected_models)}"
                details += f"\nAvailable expected models: {available_expected_models}"
                if unavailable_expected_models:
                    details += f"\nUnavailable expected models: {unavailable_expected_models}"
                details += f"\nTier distribution: {list(tier_models_found.keys())}"
                
                # Consider test passed if at least 70% of expected models are available
                success = len(available_expected_models) >= len(expected_models) * 0.7
                
                self.log_result(
                    "Model Availability Test",
                    success,
                    details
                )
                return success
                
            else:
                self.log_result(
                    "Model Availability Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Model Availability Test",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_single_turn_comprehensive(self):
        """Test single-turn mode comprehensive test with 'help me code a todo list'"""
        test_prompt = "help me code a todo list"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that it's single mode
                if data.get("mode") != "single":
                    self.log_result(
                        "Single-Turn Mode Comprehensive Test",
                        False,
                        f"Expected mode 'single', got '{data.get('mode')}'"
                    )
                    return False
                
                # Check that it provides comprehensive enhancement (not basic)
                enhanced_prompt = data.get("enhanced_prompt", "")
                original_prompt = data.get("original_prompt", "")
                
                # Should be significantly enhanced (at least 5x longer for comprehensive)
                enhancement_ratio = len(enhanced_prompt) / len(original_prompt) if len(original_prompt) > 0 else 0
                
                if enhancement_ratio < 5:
                    self.log_result(
                        "Single-Turn Mode Comprehensive Test",
                        False,
                        f"Enhancement ratio {enhancement_ratio:.1f}x is too low for comprehensive enhancement (expected >5x)"
                    )
                    return False
                
                # Check that it doesn't ask for clarification (single-turn should never ask)
                if "clarification" in enhanced_prompt.lower() or "more information" in enhanced_prompt.lower():
                    self.log_result(
                        "Single-Turn Mode Comprehensive Test",
                        False,
                        "Single-turn mode should never ask for clarification"
                    )
                    return False
                
                # Check enhancement type
                enhancement_type = data.get("enhancement_type")
                if enhancement_type == "clarification_request":
                    self.log_result(
                        "Single-Turn Mode Comprehensive Test",
                        False,
                        "Single-turn mode should not return clarification_request enhancement type"
                    )
                    return False
                
                # Check models_used field
                models_used = data.get("models_used", {})
                if not models_used:
                    self.log_result(
                        "Single-Turn Mode Comprehensive Test",
                        False,
                        "models_used field is missing or empty"
                    )
                    return False
                
                # Check for advanced models usage
                advanced_models = ["moonshotai/kimi-k2-instruct", "qwen-qwq-32b", "llama-3.3-70b-versatile"]
                used_advanced_model = any(model in str(models_used) for model in advanced_models)
                
                details = f"Enhancement ratio: {enhancement_ratio:.1f}x, Enhancement type: {enhancement_type}"
                details += f"\nModels used: {list(models_used.keys()) if models_used else 'None'}"
                details += f"\nUsed advanced model: {used_advanced_model}"
                details += f"\nEnhanced prompt length: {len(enhanced_prompt)} chars"
                
                self.log_result(
                    "Single-Turn Mode Comprehensive Test",
                    True,
                    details
                )
                return True
                
            else:
                self.log_result(
                    "Single-Turn Mode Comprehensive Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Single-Turn Mode Comprehensive Test",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_multi_turn_mode(self):
        """Test multi-turn mode with 'help me' to ensure it asks for clarification properly"""
        test_prompt = "help me"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "multi"},
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that it's multi mode
                if data.get("mode") != "multi":
                    self.log_result(
                        "Multi-Turn Mode Test",
                        False,
                        f"Expected mode 'multi', got '{data.get('mode')}'"
                    )
                    return False
                
                # Check enhancement type - should be clarification_request for vague input
                enhancement_type = data.get("enhancement_type")
                if enhancement_type != "clarification_request":
                    self.log_result(
                        "Multi-Turn Mode Test",
                        False,
                        f"Expected enhancement_type 'clarification_request', got '{enhancement_type}'"
                    )
                    return False
                
                # Check that it asks for clarification
                enhanced_prompt = data.get("enhanced_prompt", "")
                clarification_indicators = ["what", "which", "how", "clarify", "more specific", "tell me more"]
                has_clarification = any(indicator in enhanced_prompt.lower() for indicator in clarification_indicators)
                
                if not has_clarification:
                    self.log_result(
                        "Multi-Turn Mode Test",
                        False,
                        "Multi-turn mode should ask for clarification with vague input like 'help me'"
                    )
                    return False
                
                # Check models_used field
                models_used = data.get("models_used", {})
                
                details = f"Enhancement type: {enhancement_type}"
                details += f"\nModels used: {list(models_used.keys()) if models_used else 'None'}"
                details += f"\nAsks for clarification: {has_clarification}"
                details += f"\nEnhanced prompt preview: {enhanced_prompt[:100]}..."
                
                self.log_result(
                    "Multi-Turn Mode Test",
                    True,
                    details
                )
                return True
                
            else:
                self.log_result(
                    "Multi-Turn Mode Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Multi-Turn Mode Test",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_enhanced_greetings(self):
        """Test enhanced greetings with 'hi' in single mode to get enhanced greeting response"""
        test_prompt = "hi"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that it's single mode
                if data.get("mode") != "single":
                    self.log_result(
                        "Enhanced Greetings Test",
                        False,
                        f"Expected mode 'single', got '{data.get('mode')}'"
                    )
                    return False
                
                # Check intent classification
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                intent_category = intent_analysis.get("intent_category", "")
                
                if intent_category != "greeting":
                    self.log_result(
                        "Enhanced Greetings Test",
                        False,
                        f"Expected intent_category 'greeting', got '{intent_category}'"
                    )
                    return False
                
                # Check enhancement type - should be enhanced_greeting for single mode
                enhancement_type = data.get("enhancement_type")
                expected_types = ["enhanced_greeting", "clarification_request"]  # Both are acceptable for greetings
                
                if enhancement_type not in expected_types:
                    self.log_result(
                        "Enhanced Greetings Test",
                        False,
                        f"Expected enhancement_type in {expected_types}, got '{enhancement_type}'"
                    )
                    return False
                
                # Check that response is enhanced but not over-enhanced
                enhanced_prompt = data.get("enhanced_prompt", "")
                enhancement_ratio = data.get("enhancement_ratio", 0)
                
                # For greetings, enhancement ratio should be reasonable (not excessive)
                if enhancement_ratio > 100:  # Prevent over-enhancement
                    self.log_result(
                        "Enhanced Greetings Test",
                        False,
                        f"Enhancement ratio {enhancement_ratio}x is too high for greeting (over-enhancement)"
                    )
                    return False
                
                # Check complexity score - should be low for simple greeting
                complexity_score = data.get("complexity_score", 0)
                if complexity_score > 0.5:
                    self.log_result(
                        "Enhanced Greetings Test",
                        False,
                        f"Complexity score {complexity_score} is too high for simple greeting"
                    )
                    return False
                
                details = f"Intent: {intent_category}, Enhancement type: {enhancement_type}"
                details += f"\nEnhancement ratio: {enhancement_ratio}x, Complexity: {complexity_score}"
                details += f"\nConfidence: {intent_analysis.get('confidence', 0):.2f}"
                details += f"\nEnhanced response preview: {enhanced_prompt[:100]}..."
                
                self.log_result(
                    "Enhanced Greetings Test",
                    True,
                    details
                )
                return True
                
            else:
                self.log_result(
                    "Enhanced Greetings Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Enhanced Greetings Test",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_models_tracking(self):
        """Test that models_used field is properly returned with actual model names"""
        test_prompt = "Create a comprehensive business plan for a tech startup"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check models_used field exists
                models_used = data.get("models_used")
                if models_used is None:
                    self.log_result(
                        "Models Tracking Test",
                        False,
                        "models_used field is missing from response"
                    )
                    return False
                
                if not isinstance(models_used, dict):
                    self.log_result(
                        "Models Tracking Test",
                        False,
                        f"models_used should be a dict, got {type(models_used)}"
                    )
                    return False
                
                if not models_used:
                    self.log_result(
                        "Models Tracking Test",
                        False,
                        "models_used dict is empty"
                    )
                    return False
                
                # Check that model names are actual model names (not None or empty)
                valid_models = []
                invalid_models = []
                
                for step, model in models_used.items():
                    if model and isinstance(model, str) and len(model) > 0:
                        valid_models.append(f"{step}: {model}")
                    else:
                        invalid_models.append(f"{step}: {model}")
                
                if not valid_models:
                    self.log_result(
                        "Models Tracking Test",
                        False,
                        f"No valid model names found. Invalid models: {invalid_models}"
                    )
                    return False
                
                # Check for expected agent steps
                expected_steps = ["intent_classifier", "supporting_content", "best_practices", "dynamic_enhancer"]
                found_steps = list(models_used.keys())
                missing_steps = [step for step in expected_steps if step not in found_steps]
                
                details = f"Models used: {valid_models}"
                details += f"\nAgent steps found: {found_steps}"
                if missing_steps:
                    details += f"\nMissing steps: {missing_steps}"
                if invalid_models:
                    details += f"\nInvalid models: {invalid_models}"
                
                # Consider success if we have valid models for most steps
                success = len(valid_models) >= 3 and len(invalid_models) <= 1
                
                self.log_result(
                    "Models Tracking Test",
                    success,
                    details
                )
                return success
                
            else:
                self.log_result(
                    "Models Tracking Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Models Tracking Test",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_complex_enhancement(self):
        """Test complex prompt to ensure it uses high-reasoning models (llama-3.3-70b-versatile)"""
        test_prompt = "Design a distributed microservices architecture for a high-traffic e-commerce platform that can handle 1 million concurrent users, with real-time inventory management, fraud detection, and personalized recommendation engine, considering scalability, fault tolerance, security, and cost optimization"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt, "mode": "single"},
                timeout=90
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check complexity score - should be high for complex technical prompt
                complexity_score = data.get("complexity_score", 0)
                if complexity_score < 0.7:
                    self.log_result(
                        "Complex Enhancement Test",
                        False,
                        f"Complexity score {complexity_score} is too low for complex technical prompt (expected >0.7)"
                    )
                    return False
                
                # Check intent classification
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                intent_category = intent_analysis.get("intent_category", "")
                
                if intent_category != "technical":
                    self.log_result(
                        "Complex Enhancement Test",
                        False,
                        f"Expected intent_category 'technical', got '{intent_category}'"
                    )
                    return False
                
                # Check models used - should include high-reasoning models
                models_used = data.get("models_used", {})
                high_reasoning_models = ["llama-3.3-70b-versatile", "qwen-qwq-32b", "moonshotai/kimi-k2-instruct"]
                
                used_high_reasoning = []
                for step, model in models_used.items():
                    if model in high_reasoning_models:
                        used_high_reasoning.append(f"{step}: {model}")
                
                if not used_high_reasoning:
                    # Check if any high-reasoning model is mentioned in the model names
                    all_models_str = str(models_used)
                    found_reasoning_models = [model for model in high_reasoning_models if model in all_models_str]
                    
                    if not found_reasoning_models:
                        self.log_result(
                            "Complex Enhancement Test",
                            False,
                            f"No high-reasoning models used for complex task. Models used: {models_used}"
                        )
                        return False
                    else:
                        used_high_reasoning = found_reasoning_models
                
                # Check enhancement quality
                enhanced_prompt = data.get("enhanced_prompt", "")
                enhancement_ratio = data.get("enhancement_ratio", 0)
                
                # Complex prompts should get substantial enhancement
                if enhancement_ratio < 2:
                    self.log_result(
                        "Complex Enhancement Test",
                        False,
                        f"Enhancement ratio {enhancement_ratio}x is too low for complex prompt"
                    )
                    return False
                
                details = f"Complexity score: {complexity_score}, Intent: {intent_category}"
                details += f"\nEnhancement ratio: {enhancement_ratio}x"
                details += f"\nHigh-reasoning models used: {used_high_reasoning}"
                details += f"\nAll models used: {list(models_used.keys())}"
                details += f"\nEnhanced prompt length: {len(enhanced_prompt)} chars"
                
                self.log_result(
                    "Complex Enhancement Test",
                    True,
                    details
                )
                return True
                
            else:
                self.log_result(
                    "Complex Enhancement Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Complex Enhancement Test",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all multi-model system tests"""
        print("🚀 Starting Multi-Model Integration System Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Run all tests in order
        test_methods = [
            self.test_model_availability,
            self.test_single_turn_comprehensive,
            self.test_multi_turn_mode,
            self.test_enhanced_greetings,
            self.test_models_tracking,
            self.test_complex_enhancement
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
            
            # Small delay between tests
            time.sleep(3)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🏁 MULTI-MODEL SYSTEM TEST SUMMARY")
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
    tester = MultiModelSystemTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All multi-model system tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()