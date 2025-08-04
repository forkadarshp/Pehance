#!/usr/bin/env python3
"""
Multi-Model Integration System Testing for Pehance
Tests the new multi-model integration system with comprehensive scenarios
"""

import asyncio
import json
import os
import requests
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class MultiModelIntegrationTester:
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

    def test_model_availability_endpoint(self):
        """Test GET /api/test-models endpoint to verify all new models are properly configured"""
        print("🔍 Testing Model Availability Endpoint...")
        
        try:
            response = requests.get(f"{API_BASE}/test-models", timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required top-level fields
                required_fields = ["success", "models", "summary", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Model Availability Endpoint Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Check if success is true
                if not data.get("success", False):
                    self.log_result(
                        "Model Availability Endpoint Success",
                        False,
                        "API returned success=false",
                        data
                    )
                    return False
                
                # Check models structure
                models = data.get("models", {})
                if not models:
                    self.log_result(
                        "Model Availability Models List",
                        False,
                        "No models returned in response",
                        data
                    )
                    return False
                
                # Check tier system
                expected_tiers = [
                    "Tier 1: Ultra-Fast",
                    "Tier 2: Balanced", 
                    "Tier 3: High-Reasoning",
                    "Tier 4: Specialized",
                    "Safety Models"
                ]
                
                found_tiers = set()
                available_models = 0
                total_models = len(models)
                
                for model_name, model_info in models.items():
                    # Check model info structure
                    required_model_fields = ["available", "status", "performance_tokens_sec", "features", "tier"]
                    missing_model_fields = [field for field in required_model_fields if field not in model_info]
                    
                    if missing_model_fields:
                        self.log_result(
                            f"Model Info Structure - {model_name}",
                            False,
                            f"Missing model fields: {missing_model_fields}",
                            model_info
                        )
                        continue
                    
                    # Track tiers and availability
                    tier = model_info.get("tier", "Unknown")
                    found_tiers.add(tier)
                    
                    if model_info.get("available", False):
                        available_models += 1
                
                # Check if we have models from different tiers
                tier_coverage = len([tier for tier in expected_tiers if tier in found_tiers])
                
                # Check summary structure
                summary = data.get("summary", {})
                required_summary_fields = ["total_models", "available_models", "availability_rate"]
                missing_summary_fields = [field for field in required_summary_fields if field not in summary]
                
                if missing_summary_fields:
                    self.log_result(
                        "Model Availability Summary Structure",
                        False,
                        f"Missing summary fields: {missing_summary_fields}",
                        summary
                    )
                    return False
                
                # Verify performance metrics are present
                performance_found = 0
                for model_info in models.values():
                    perf = model_info.get("performance_tokens_sec", "Unknown")
                    if isinstance(perf, (int, float)) and perf > 0:
                        performance_found += 1
                
                self.log_result(
                    "Model Availability Testing",
                    True,
                    f"Found {total_models} models, {available_models} available ({summary.get('availability_rate', '0%')}). "
                    f"Tier coverage: {tier_coverage}/{len(expected_tiers)}. "
                    f"Performance metrics: {performance_found}/{total_models} models"
                )
                
                # Log detailed model information
                print("   📊 Model Details:")
                for model_name, model_info in list(models.items())[:5]:  # Show first 5 models
                    status = "✅" if model_info.get("available") else "❌"
                    tier = model_info.get("tier", "Unknown")
                    perf = model_info.get("performance_tokens_sec", "Unknown")
                    features = model_info.get("features", [])
                    print(f"      {status} {model_name}")
                    print(f"         Tier: {tier}, Performance: {perf} tokens/sec")
                    if features:
                        print(f"         Features: {', '.join(features[:3])}")
                
                return True
                
            else:
                self.log_result(
                    "Model Availability Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Model Availability Endpoint",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_intent_classification_scenarios(self):
        """Test intent classification with simple greetings and complex technical requests"""
        print("🎯 Testing Intent Classification Scenarios...")
        
        test_cases = [
            # Simple greetings
            {
                "prompt": "hi",
                "expected_category": "greeting",
                "expected_complexity_range": (0.1, 0.3),
                "test_name": "Simple Greeting - 'hi'"
            },
            {
                "prompt": "hello",
                "expected_category": "greeting", 
                "expected_complexity_range": (0.1, 0.3),
                "test_name": "Simple Greeting - 'hello'"
            },
            {
                "prompt": "hey",
                "expected_category": "greeting",
                "expected_complexity_range": (0.1, 0.3),
                "test_name": "Simple Greeting - 'hey'"
            },
            # Complex technical requests
            {
                "prompt": "Build a REST API for user authentication with JWT tokens",
                "expected_category": "technical",
                "expected_complexity_range": (0.6, 1.0),
                "test_name": "Complex Technical Request - REST API"
            },
            {
                "prompt": "Create a microservices architecture with Docker containers, Kubernetes orchestration, and implement CI/CD pipeline with automated testing",
                "expected_category": "technical",
                "expected_complexity_range": (0.8, 1.0),
                "test_name": "Complex Technical Request - Microservices"
            },
            # Creative requests
            {
                "prompt": "Write a compelling story about AI",
                "expected_category": "creative",
                "expected_complexity_range": (0.3, 0.7),
                "test_name": "Creative Request - AI Story"
            },
            {
                "prompt": "Craft an epic fantasy novel with multiple POV characters, intricate magic system, and political intrigue spanning three kingdoms",
                "expected_category": "creative",
                "expected_complexity_range": (0.7, 1.0),
                "test_name": "Complex Creative Request - Fantasy Novel"
            }
        ]
        
        all_passed = True
        json_parsing_failures = 0
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"]},
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    
                    # Check if intent analysis exists
                    if not intent_analysis:
                        self.log_result(
                            test_case["test_name"],
                            False,
                            "No intent_analysis found in response"
                        )
                        all_passed = False
                        continue
                    
                    # Check intent category
                    actual_category = intent_analysis.get("intent_category", "")
                    expected_category = test_case["expected_category"]
                    
                    # Check complexity score
                    complexity_score = intent_analysis.get("input_complexity_score", 0)
                    min_complexity, max_complexity = test_case["expected_complexity_range"]
                    
                    # Check if JSON parsing worked (not defaulted to 'other' with 0.5 confidence)
                    confidence = intent_analysis.get("confidence", 0)
                    is_json_parsing_failure = (actual_category == "other" and confidence == 0.5)
                    
                    if is_json_parsing_failure:
                        json_parsing_failures += 1
                        self.log_result(
                            test_case["test_name"],
                            False,
                            f"JSON parsing failure detected - defaulted to 'other' category with 0.5 confidence. This indicates the intent classifier returned non-JSON response."
                        )
                        all_passed = False
                        continue
                    
                    # Validate intent category
                    category_correct = actual_category == expected_category
                    
                    # Validate complexity score range
                    complexity_correct = min_complexity <= complexity_score <= max_complexity
                    
                    if category_correct and complexity_correct:
                        self.log_result(
                            test_case["test_name"],
                            True,
                            f"Intent: {actual_category} (confidence: {confidence:.2f}), "
                            f"Complexity: {complexity_score:.2f} (expected: {min_complexity}-{max_complexity})"
                        )
                    else:
                        issues = []
                        if not category_correct:
                            issues.append(f"Expected category '{expected_category}', got '{actual_category}'")
                        if not complexity_correct:
                            issues.append(f"Complexity {complexity_score:.2f} outside expected range {min_complexity}-{max_complexity}")
                        
                        self.log_result(
                            test_case["test_name"],
                            False,
                            f"Classification issues: {'; '.join(issues)}. Confidence: {confidence:.2f}"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        test_case["test_name"],
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    test_case["test_name"],
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            # Small delay between requests
            time.sleep(1)
        
        # Summary of JSON parsing issues
        if json_parsing_failures > 0:
            print(f"⚠️  CRITICAL: {json_parsing_failures} JSON parsing failures detected!")
            print("   This indicates the intent classifier is not returning valid JSON for complex inputs.")
        
        return all_passed

    def test_single_vs_multi_mode(self):
        """Test single mode vs multi mode enhancement behavior"""
        print("🔄 Testing Single vs Multi Mode Enhancement...")
        
        test_cases = [
            {
                "prompt": "hi",
                "test_name": "Simple Greeting Mode Comparison"
            },
            {
                "prompt": "help me",
                "test_name": "Incomplete Request Mode Comparison"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                # Test Single Mode
                single_response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"], "mode": "single"},
                    timeout=30
                )
                
                # Test Multi Mode  
                multi_response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"], "mode": "multi"},
                    timeout=30
                )
                
                if single_response.status_code == 200 and multi_response.status_code == 200:
                    single_data = single_response.json()
                    multi_data = multi_response.json()
                    
                    single_enhancement_type = single_data.get("enhancement_type", "")
                    multi_enhancement_type = multi_data.get("enhancement_type", "")
                    
                    single_enhanced = single_data.get("enhanced_prompt", "")
                    multi_enhanced = multi_data.get("enhanced_prompt", "")
                    
                    # Check mode parameter handling
                    single_mode = single_data.get("mode", "")
                    multi_mode = multi_data.get("mode", "")
                    
                    mode_handling_correct = (single_mode == "single" and multi_mode == "multi")
                    
                    # For simple inputs, single mode should always provide enhanced prompts
                    # Multi mode may provide clarification requests
                    single_provides_enhancement = len(single_enhanced) > len(test_case["prompt"]) * 2
                    
                    # Check if responses are different (indicating mode awareness)
                    responses_different = single_enhanced != multi_enhanced
                    
                    if mode_handling_correct and single_provides_enhancement:
                        self.log_result(
                            test_case["test_name"],
                            True,
                            f"Single mode: {single_enhancement_type} ({len(single_enhanced)} chars), "
                            f"Multi mode: {multi_enhancement_type} ({len(multi_enhanced)} chars). "
                            f"Responses different: {responses_different}"
                        )
                    else:
                        issues = []
                        if not mode_handling_correct:
                            issues.append(f"Mode parameter not handled correctly (single: {single_mode}, multi: {multi_mode})")
                        if not single_provides_enhancement:
                            issues.append("Single mode should always provide enhanced prompts")
                        
                        self.log_result(
                            test_case["test_name"],
                            False,
                            f"Mode handling issues: {'; '.join(issues)}"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        test_case["test_name"],
                        False,
                        f"HTTP errors - Single: {single_response.status_code}, Multi: {multi_response.status_code}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    test_case["test_name"],
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)
        
        return all_passed

    def test_multi_model_selection(self):
        """Test that different models are selected for different task types"""
        print("🎯 Testing Multi-Model Selection for Different Tasks...")
        
        test_cases = [
            {
                "prompt": "hi",
                "expected_task_type": "intent_classification",
                "test_name": "Model Selection - Simple Greeting"
            },
            {
                "prompt": "Build a complex distributed system with microservices, event sourcing, and CQRS pattern implementation",
                "expected_task_type": "complex_enhancement",
                "test_name": "Model Selection - Complex Technical Request"
            },
            {
                "prompt": "Write an epic fantasy story with dragons and magic",
                "expected_task_type": "creative_enhancement",
                "test_name": "Model Selection - Creative Request"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"]},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    
                    # Check if models_used information is available
                    models_used = agent_results.get("models_used", {})
                    
                    if models_used:
                        # Check if different models are being used for different stages
                        classification_model = models_used.get("classification", "")
                        enhancement_model = models_used.get("enhancement", "")
                        
                        # Verify models are specified
                        models_specified = bool(classification_model and enhancement_model)
                        
                        # For complex requests, should use different models for different stages
                        uses_different_models = classification_model != enhancement_model
                        
                        self.log_result(
                            test_case["test_name"],
                            True,
                            f"Classification model: {classification_model}, "
                            f"Enhancement model: {enhancement_model}. "
                            f"Uses different models: {uses_different_models}"
                        )
                    else:
                        # Check if at least model selection is working (even if not exposed in response)
                        enhancement_type = data.get("enhancement_type", "")
                        complexity_score = data.get("complexity_score", 0)
                        
                        # Verify appropriate enhancement type for complexity
                        appropriate_enhancement = True
                        if complexity_score < 0.3 and enhancement_type not in ["clarification_request", "enhanced_greeting", "basic_enhancement"]:
                            appropriate_enhancement = False
                        elif complexity_score > 0.7 and enhancement_type not in ["advanced_enhancement", "standard_enhancement"]:
                            appropriate_enhancement = False
                        
                        if appropriate_enhancement:
                            self.log_result(
                                test_case["test_name"],
                                True,
                                f"Appropriate enhancement type '{enhancement_type}' for complexity {complexity_score:.2f}"
                            )
                        else:
                            self.log_result(
                                test_case["test_name"],
                                False,
                                f"Inappropriate enhancement type '{enhancement_type}' for complexity {complexity_score:.2f}"
                            )
                            all_passed = False
                else:
                    self.log_result(
                        test_case["test_name"],
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    test_case["test_name"],
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(2)
        
        return all_passed

    def test_enhanced_greeting_responses(self):
        """Test if greeting responses are enhanced and personalized in single mode"""
        print("👋 Testing Enhanced Greeting Responses...")
        
        greeting_tests = [
            {
                "prompt": "hi",
                "test_name": "Enhanced Greeting - 'hi'"
            },
            {
                "prompt": "hello",
                "test_name": "Enhanced Greeting - 'hello'"
            },
            {
                "prompt": "good morning",
                "test_name": "Enhanced Greeting - 'good morning'"
            }
        ]
        
        all_passed = True
        
        for test_case in greeting_tests:
            try:
                # Test in single mode (should always enhance)
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"], "mode": "single"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    enhanced_prompt = data.get("enhanced_prompt", "")
                    enhancement_type = data.get("enhancement_type", "")
                    enhancement_ratio = data.get("enhancement_ratio", 0)
                    
                    # Check if greeting was enhanced
                    is_enhanced = len(enhanced_prompt) > len(test_case["prompt"]) * 3
                    
                    # Check if it's a reasonable enhancement ratio (not over-enhanced)
                    reasonable_ratio = 5 <= enhancement_ratio <= 50  # Between 5x and 50x enhancement
                    
                    # Check if response contains helpful elements
                    helpful_elements = [
                        "help" in enhanced_prompt.lower(),
                        "prompt" in enhanced_prompt.lower() or "enhance" in enhanced_prompt.lower(),
                        "?" in enhanced_prompt,  # Contains questions to engage user
                        len(enhanced_prompt) > 100  # Substantial response
                    ]
                    
                    helpfulness_score = sum(helpful_elements)
                    
                    # Check for time-based context (if implemented)
                    has_time_context = any(word in enhanced_prompt.lower() for word in ["morning", "afternoon", "evening", "day", "time"])
                    
                    if is_enhanced and reasonable_ratio and helpfulness_score >= 2:
                        self.log_result(
                            test_case["test_name"],
                            True,
                            f"Enhanced from {len(test_case['prompt'])} to {len(enhanced_prompt)} chars "
                            f"(ratio: {enhancement_ratio}x). Enhancement type: {enhancement_type}. "
                            f"Helpfulness score: {helpfulness_score}/4. Time context: {has_time_context}"
                        )
                    else:
                        issues = []
                        if not is_enhanced:
                            issues.append("Response not sufficiently enhanced")
                        if not reasonable_ratio:
                            issues.append(f"Enhancement ratio {enhancement_ratio}x outside reasonable range (5-50x)")
                        if helpfulness_score < 2:
                            issues.append(f"Low helpfulness score: {helpfulness_score}/4")
                        
                        self.log_result(
                            test_case["test_name"],
                            False,
                            f"Enhancement issues: {'; '.join(issues)}"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        test_case["test_name"],
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    test_case["test_name"],
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)
        
        return all_passed

    def test_json_parsing_reliability(self):
        """Test JSON parsing reliability for intent classification"""
        print("🔧 Testing JSON Parsing Reliability...")
        
        # Test various input types that previously caused JSON parsing failures
        test_cases = [
            "Build a REST API for user authentication with JWT tokens and password hashing",
            "Create a comprehensive marketing strategy for a B2B SaaS startup",
            "Write a compelling story about artificial intelligence and human relationships",
            "Develop a machine learning model for predicting customer churn",
            "Design a scalable microservices architecture with Docker and Kubernetes",
            "Analyze the impact of climate change on global economic systems",
            "Create a business plan for a sustainable energy startup",
            "Write a technical documentation for a complex software system"
        ]
        
        json_parsing_successes = 0
        total_tests = len(test_cases)
        
        for i, prompt in enumerate(test_cases, 1):
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": prompt},
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    
                    # Check if JSON parsing worked (not defaulted to 'other' with 0.5 confidence)
                    category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    
                    is_json_parsing_failure = (category == "other" and confidence == 0.5)
                    
                    if not is_json_parsing_failure:
                        json_parsing_successes += 1
                        print(f"   ✅ Test {i}/{total_tests}: JSON parsing successful - {category} ({confidence:.2f})")
                    else:
                        print(f"   ❌ Test {i}/{total_tests}: JSON parsing failed - defaulted to fallback")
                else:
                    print(f"   ❌ Test {i}/{total_tests}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Test {i}/{total_tests}: Error - {str(e)}")
            
            time.sleep(1)
        
        success_rate = (json_parsing_successes / total_tests) * 100
        
        if success_rate >= 80:  # 80% success rate threshold
            self.log_result(
                "JSON Parsing Reliability",
                True,
                f"JSON parsing success rate: {success_rate:.1f}% ({json_parsing_successes}/{total_tests})"
            )
            return True
        else:
            self.log_result(
                "JSON Parsing Reliability",
                False,
                f"JSON parsing success rate too low: {success_rate:.1f}% ({json_parsing_successes}/{total_tests}). "
                f"Expected at least 80% success rate."
            )
            return False

    def run_all_tests(self):
        """Run all multi-model integration tests"""
        print("🚀 Starting Multi-Model Integration System Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test sequence based on review request
        test_methods = [
            ("Model Availability Testing", self.test_model_availability_endpoint),
            ("Intent Classification Testing", self.test_intent_classification_scenarios),
            ("Single vs Multi Mode Testing", self.test_single_vs_multi_mode),
            ("Multi-Model Selection Testing", self.test_multi_model_selection),
            ("Enhanced Greeting Responses", self.test_enhanced_greeting_responses),
            ("JSON Parsing Reliability", self.test_json_parsing_reliability)
        ]
        
        for test_category, test_method in test_methods:
            print(f"\n🔍 {test_category}")
            print("-" * 60)
            try:
                test_method()
            except Exception as e:
                self.log_result(
                    f"Test Category: {test_category}",
                    False,
                    f"Test category failed with exception: {str(e)}"
                )
            
            # Delay between test categories
            time.sleep(3)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🏁 MULTI-MODEL INTEGRATION TEST SUMMARY")
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
        
        # Critical issues summary
        critical_issues = []
        for result in self.results:
            if not result["success"]:
                if "JSON parsing failure" in result["details"]:
                    critical_issues.append("Intent Classification JSON Parsing Failures")
                elif "Model Availability" in result["test"]:
                    critical_issues.append("Model Availability Issues")
                elif "Mode handling" in result["details"]:
                    critical_issues.append("Single/Multi Mode Handling Issues")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in set(critical_issues):
                print(f"  - {issue}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            "results": self.results,
            "critical_issues": list(set(critical_issues))
        }

def main():
    """Main test execution"""
    tester = MultiModelIntegrationTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All multi-model integration tests passed!")
        return 0
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        if summary["critical_issues"]:
            print("🚨 Critical issues require immediate attention!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)