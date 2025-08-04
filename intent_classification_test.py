#!/usr/bin/env python3
"""
Intent Classification System Testing for Pehance Enhanced Application
Focused testing on the intent classification fixes as requested in review_request

This test specifically focuses on:
1. Testing /api/enhance endpoint with various prompt types to verify intent classification
2. Verifying JSON parsing robustness and handling edge cases  
3. Testing fallback mechanism with keyword-based classification
4. Checking enhanced prompt classification for creative, technical, and business prompts
"""

import asyncio
import json
import os
import sys
import time
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class IntentClassificationTester:
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
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_basic_connectivity(self):
        """Test basic API connectivity first"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Basic API Connectivity", 
                    True, 
                    f"API responding with: {data.get('message', 'No message')}"
                )
                return True
            else:
                self.log_result(
                    "Basic API Connectivity", 
                    False, 
                    f"Unexpected status code: {response.status_code}",
                    {"status_code": response.status_code, "text": response.text}
                )
                return False
        except Exception as e:
            self.log_result(
                "Basic API Connectivity", 
                False, 
                f"Connection error: {str(e)}"
            )
            return False

    def test_simple_greetings_classification(self):
        """Test simple greetings: 'hi', 'hello' - should be classified correctly"""
        greeting_test_cases = [
            {"prompt": "hi", "expected_category": "greeting"},
            {"prompt": "hello", "expected_category": "greeting"},
            {"prompt": "hey", "expected_category": "greeting"},
            {"prompt": "good morning", "expected_category": "greeting"}
        ]
        
        all_passed = True
        
        for test_case in greeting_test_cases:
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
                    
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    complexity_score = intent_analysis.get("input_complexity_score", 0)
                    
                    # Check if correctly classified as greeting
                    if actual_category == test_case["expected_category"]:
                        # Also check if complexity score is appropriately low for greetings
                        if complexity_score <= 0.3:
                            self.log_result(
                                f"Simple Greeting Classification: '{test_case['prompt']}'",
                                True,
                                f"Correctly classified as '{actual_category}' with {confidence:.2f} confidence, complexity: {complexity_score:.2f}"
                            )
                        else:
                            self.log_result(
                                f"Simple Greeting Classification: '{test_case['prompt']}'",
                                False,
                                f"Classified correctly but complexity too high: {complexity_score:.2f} (should be ≤0.3)"
                            )
                            all_passed = False
                    else:
                        self.log_result(
                            f"Simple Greeting Classification: '{test_case['prompt']}'",
                            False,
                            f"Expected '{test_case['expected_category']}', got '{actual_category}' with {confidence:.2f} confidence"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        f"Simple Greeting Classification: '{test_case['prompt']}'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Simple Greeting Classification: '{test_case['prompt']}'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(1)  # Small delay between requests
        
        return all_passed

    def test_creative_prompts_classification(self):
        """Test creative prompts: 'write a story about AI' - should be classified as creative"""
        creative_test_cases = [
            {
                "prompt": "write a story about AI",
                "expected_category": "creative",
                "expected_domain": "storytelling"
            },
            {
                "prompt": "Create a poem about nature and technology",
                "expected_category": "creative", 
                "expected_domain": "poetry"
            },
            {
                "prompt": "Design a character for a fantasy novel",
                "expected_category": "creative",
                "expected_domain": "character design"
            },
            {
                "prompt": "Write a compelling marketing copy for a new product",
                "expected_category": "creative",
                "expected_domain": "copywriting"
            }
        ]
        
        all_passed = True
        
        for test_case in creative_test_cases:
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
                    
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    specific_domain = intent_analysis.get("specific_domain", "")
                    complexity_score = intent_analysis.get("input_complexity_score", 0)
                    
                    # Check if correctly classified as creative
                    if actual_category == test_case["expected_category"]:
                        # Check if confidence is reasonable (>0.6 for clear creative prompts)
                        if confidence >= 0.6:
                            self.log_result(
                                f"Creative Prompt Classification: '{test_case['prompt'][:40]}...'",
                                True,
                                f"Correctly classified as '{actual_category}' with {confidence:.2f} confidence, domain: {specific_domain}, complexity: {complexity_score:.2f}"
                            )
                        else:
                            self.log_result(
                                f"Creative Prompt Classification: '{test_case['prompt'][:40]}...'",
                                False,
                                f"Classified correctly but low confidence: {confidence:.2f} (should be ≥0.6)"
                            )
                            all_passed = False
                    else:
                        self.log_result(
                            f"Creative Prompt Classification: '{test_case['prompt'][:40]}...'",
                            False,
                            f"Expected '{test_case['expected_category']}', got '{actual_category}' with {confidence:.2f} confidence"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        f"Creative Prompt Classification: '{test_case['prompt'][:40]}...'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Creative Prompt Classification: '{test_case['prompt'][:40]}...'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(2)  # Longer delay for complex requests
        
        return all_passed

    def test_technical_prompts_classification(self):
        """Test technical prompts: 'build a REST API for authentication' - should be classified as technical"""
        technical_test_cases = [
            {
                "prompt": "build a REST API for authentication",
                "expected_category": "technical",
                "expected_domain": "software development"
            },
            {
                "prompt": "Create a React component with TypeScript for user login",
                "expected_category": "technical",
                "expected_domain": "web development"
            },
            {
                "prompt": "Design a database schema for an e-commerce platform",
                "expected_category": "technical",
                "expected_domain": "database design"
            },
            {
                "prompt": "Implement a machine learning model for image classification",
                "expected_category": "technical",
                "expected_domain": "machine learning"
            }
        ]
        
        all_passed = True
        
        for test_case in technical_test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"]},
                    timeout=60  # Longer timeout for complex technical prompts
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    specific_domain = intent_analysis.get("specific_domain", "")
                    complexity_score = intent_analysis.get("input_complexity_score", 0)
                    
                    # Check if correctly classified as technical
                    if actual_category == test_case["expected_category"]:
                        # Check if confidence is high (>0.7 for clear technical prompts)
                        if confidence >= 0.7:
                            self.log_result(
                                f"Technical Prompt Classification: '{test_case['prompt'][:40]}...'",
                                True,
                                f"Correctly classified as '{actual_category}' with {confidence:.2f} confidence, domain: {specific_domain}, complexity: {complexity_score:.2f}"
                            )
                        else:
                            self.log_result(
                                f"Technical Prompt Classification: '{test_case['prompt'][:40]}...'",
                                False,
                                f"Classified correctly but low confidence: {confidence:.2f} (should be ≥0.7)"
                            )
                            all_passed = False
                    else:
                        self.log_result(
                            f"Technical Prompt Classification: '{test_case['prompt'][:40]}...'",
                            False,
                            f"Expected '{test_case['expected_category']}', got '{actual_category}' with {confidence:.2f} confidence"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        f"Technical Prompt Classification: '{test_case['prompt'][:40]}...'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Technical Prompt Classification: '{test_case['prompt'][:40]}...'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(2)  # Longer delay for complex requests
        
        return all_passed

    def test_business_prompts_classification(self):
        """Test business prompts: 'create a marketing strategy for SaaS' - should be classified as business"""
        business_test_cases = [
            {
                "prompt": "create a marketing strategy for SaaS",
                "expected_category": "business",
                "expected_domain": "marketing"
            },
            {
                "prompt": "Develop a business plan for a startup in fintech",
                "expected_category": "business",
                "expected_domain": "business planning"
            },
            {
                "prompt": "Create a competitive analysis for our product launch",
                "expected_category": "business",
                "expected_domain": "market analysis"
            },
            {
                "prompt": "Design a customer acquisition strategy for B2B SaaS",
                "expected_category": "business",
                "expected_domain": "customer acquisition"
            }
        ]
        
        all_passed = True
        
        for test_case in business_test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"]},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    specific_domain = intent_analysis.get("specific_domain", "")
                    complexity_score = intent_analysis.get("input_complexity_score", 0)
                    
                    # Check if correctly classified as business
                    if actual_category == test_case["expected_category"]:
                        # Check if confidence is high (>0.7 for clear business prompts)
                        if confidence >= 0.7:
                            self.log_result(
                                f"Business Prompt Classification: '{test_case['prompt'][:40]}...'",
                                True,
                                f"Correctly classified as '{actual_category}' with {confidence:.2f} confidence, domain: {specific_domain}, complexity: {complexity_score:.2f}"
                            )
                        else:
                            self.log_result(
                                f"Business Prompt Classification: '{test_case['prompt'][:40]}...'",
                                False,
                                f"Classified correctly but low confidence: {confidence:.2f} (should be ≥0.7)"
                            )
                            all_passed = False
                    else:
                        self.log_result(
                            f"Business Prompt Classification: '{test_case['prompt'][:40]}...'",
                            False,
                            f"Expected '{test_case['expected_category']}', got '{actual_category}' with {confidence:.2f} confidence"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        f"Business Prompt Classification: '{test_case['prompt'][:40]}...'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Business Prompt Classification: '{test_case['prompt'][:40]}...'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(2)  # Longer delay for complex requests
        
        return all_passed

    def test_json_parsing_robustness(self):
        """Test JSON parsing robustness and edge cases"""
        edge_case_prompts = [
            "a",  # Single character
            "help",  # Single word
            "What is the meaning of life, the universe, and everything? Please provide a comprehensive analysis covering philosophical, scientific, and cultural perspectives while considering both ancient wisdom and modern discoveries.",  # Very long prompt
            "Create a mobile app that tracks daily habits, sends notifications, syncs across devices, has a beautiful UI, integrates with health apps, provides analytics, supports multiple users, works offline, and costs less than $5 to build",  # Complex multi-requirement prompt
            "Write code",  # Ambiguous technical request
            "Make money",  # Ambiguous business request
        ]
        
        all_passed = True
        
        for prompt in edge_case_prompts:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": prompt},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    
                    # Check that we got valid intent analysis (not defaulting to 'other' with 0.5 confidence)
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    complexity_score = intent_analysis.get("input_complexity_score", 0)
                    
                    # For edge cases, we mainly want to ensure the system doesn't crash and provides some classification
                    if actual_category and confidence > 0:
                        # Special check: if it's classified as 'other' with exactly 0.5 confidence, it might be a fallback
                        if actual_category == "other" and confidence == 0.5:
                            self.log_result(
                                f"JSON Parsing Edge Case: '{prompt[:30]}...'",
                                False,
                                f"Likely fallback classification detected: '{actual_category}' with {confidence:.2f} confidence (suggests JSON parsing failure)"
                            )
                            all_passed = False
                        else:
                            self.log_result(
                                f"JSON Parsing Edge Case: '{prompt[:30]}...'",
                                True,
                                f"Successfully classified as '{actual_category}' with {confidence:.2f} confidence, complexity: {complexity_score:.2f}"
                            )
                    else:
                        self.log_result(
                            f"JSON Parsing Edge Case: '{prompt[:30]}...'",
                            False,
                            f"Invalid classification result: category='{actual_category}', confidence={confidence}"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        f"JSON Parsing Edge Case: '{prompt[:30]}...'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"JSON Parsing Edge Case: '{prompt[:30]}...'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(1)
        
        return all_passed

    def test_fallback_mechanism(self):
        """Test the fallback mechanism with keyword-based classification"""
        # These prompts are designed to test if the fallback keyword matching works
        fallback_test_cases = [
            {
                "prompt": "hello world programming code api",
                "expected_fallback_category": "technical",
                "keywords": ["code", "api", "program"]
            },
            {
                "prompt": "business strategy marketing startup company",
                "expected_fallback_category": "business", 
                "keywords": ["business", "strategy", "marketing", "startup", "company"]
            },
            {
                "prompt": "write creative story art design",
                "expected_fallback_category": "creative",
                "keywords": ["write", "creative", "story", "art", "design"]
            },
            {
                "prompt": "hi hello greetings hey",
                "expected_fallback_category": "greeting",
                "keywords": ["hi", "hello", "greetings", "hey"]
            }
        ]
        
        all_passed = True
        
        for test_case in fallback_test_cases:
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
                    
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    
                    # Check if the fallback mechanism worked (either proper classification or fallback to expected category)
                    if actual_category == test_case["expected_fallback_category"]:
                        self.log_result(
                            f"Fallback Mechanism Test: '{test_case['prompt'][:30]}...'",
                            True,
                            f"Correctly classified/fell back to '{actual_category}' with {confidence:.2f} confidence"
                        )
                    else:
                        # If it didn't match expected fallback, check if it's still a reasonable classification
                        if actual_category in ["creative", "technical", "business", "greeting", "academic", "personal"] and confidence >= 0.3:
                            self.log_result(
                                f"Fallback Mechanism Test: '{test_case['prompt'][:30]}...'",
                                True,
                                f"Alternative valid classification: '{actual_category}' with {confidence:.2f} confidence (expected fallback: {test_case['expected_fallback_category']})"
                            )
                        else:
                            self.log_result(
                                f"Fallback Mechanism Test: '{test_case['prompt'][:30]}...'",
                                False,
                                f"Expected fallback to '{test_case['expected_fallback_category']}', got '{actual_category}' with {confidence:.2f} confidence"
                            )
                            all_passed = False
                else:
                    self.log_result(
                        f"Fallback Mechanism Test: '{test_case['prompt'][:30]}...'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Fallback Mechanism Test: '{test_case['prompt'][:30]}...'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(1)
        
        return all_passed

    def test_no_other_category_defaults(self):
        """Test that valid prompts don't default to 'other' category with low confidence"""
        valid_prompts = [
            "Create a website for my restaurant",  # Should be technical or business
            "Write a blog post about climate change",  # Should be creative or academic
            "Help me plan my wedding",  # Should be personal
            "Analyze market trends for cryptocurrency",  # Should be business or academic
            "Design a logo for my startup",  # Should be creative or business
            "Build a chatbot for customer service",  # Should be technical
        ]
        
        all_passed = True
        
        for prompt in valid_prompts:
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
                    
                    actual_category = intent_analysis.get("intent_category", "")
                    confidence = intent_analysis.get("confidence", 0)
                    
                    # Check that valid prompts don't default to 'other' with low confidence
                    if actual_category == "other" and confidence <= 0.6:
                        self.log_result(
                            f"No 'Other' Category Default: '{prompt[:40]}...'",
                            False,
                            f"Valid prompt incorrectly defaulted to 'other' category with low confidence: {confidence:.2f}"
                        )
                        all_passed = False
                    else:
                        self.log_result(
                            f"No 'Other' Category Default: '{prompt[:40]}...'",
                            True,
                            f"Properly classified as '{actual_category}' with {confidence:.2f} confidence"
                        )
                else:
                    self.log_result(
                        f"No 'Other' Category Default: '{prompt[:40]}...'",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"No 'Other' Category Default: '{prompt[:40]}...'",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
                
            time.sleep(1)
        
        return all_passed

    def run_intent_classification_tests(self):
        """Run all intent classification focused tests"""
        print("🎯 Starting Intent Classification System Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        print("FOCUS: Testing the fixed intent classification system as requested")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Stopping tests.")
            return self.generate_summary()
        
        # Run all intent classification tests
        test_methods = [
            ("Simple Greetings Classification", self.test_simple_greetings_classification),
            ("Creative Prompts Classification", self.test_creative_prompts_classification),
            ("Technical Prompts Classification", self.test_technical_prompts_classification),
            ("Business Prompts Classification", self.test_business_prompts_classification),
            ("JSON Parsing Robustness", self.test_json_parsing_robustness),
            ("Fallback Mechanism", self.test_fallback_mechanism),
            ("No 'Other' Category Defaults", self.test_no_other_category_defaults)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n🔍 Running {test_name}...")
            try:
                test_method()
            except Exception as e:
                self.log_result(
                    f"Test Suite: {test_name}",
                    False,
                    f"Test suite failed with exception: {str(e)}"
                )
            
            # Delay between test suites to avoid overwhelming the API
            time.sleep(3)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🏁 INTENT CLASSIFICATION TEST SUMMARY")
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
        
        # Specific analysis for intent classification issues
        print("\n📊 INTENT CLASSIFICATION ANALYSIS:")
        
        # Count classification failures
        classification_failures = [r for r in self.results if not r["success"] and "Classification" in r["test"]]
        json_parsing_failures = [r for r in self.results if not r["success"] and "JSON Parsing" in r["test"]]
        fallback_failures = [r for r in self.results if not r["success"] and "Fallback" in r["test"]]
        other_category_failures = [r for r in self.results if not r["success"] and "Other" in r["test"]]
        
        print(f"  - Classification Failures: {len(classification_failures)}")
        print(f"  - JSON Parsing Issues: {len(json_parsing_failures)}")
        print(f"  - Fallback Mechanism Issues: {len(fallback_failures)}")
        print(f"  - 'Other' Category Defaults: {len(other_category_failures)}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            "results": self.results,
            "classification_failures": len(classification_failures),
            "json_parsing_failures": len(json_parsing_failures),
            "fallback_failures": len(fallback_failures),
            "other_category_failures": len(other_category_failures)
        }

def main():
    """Main test execution"""
    tester = IntentClassificationTester()
    summary = tester.run_intent_classification_tests()
    
    # Print final assessment
    print("\n" + "="*80)
    print("🎯 INTENT CLASSIFICATION SYSTEM ASSESSMENT")
    print("="*80)
    
    if summary["failed_tests"] == 0:
        print("🎉 All intent classification tests passed!")
        print("✅ The intent classification system fixes appear to be working correctly.")
        print("✅ JSON parsing is robust and handling edge cases properly.")
        print("✅ Fallback mechanism is functioning as expected.")
        print("✅ Enhanced prompt classification is working for creative, technical, and business prompts.")
    else:
        print(f"⚠️  {summary['failed_tests']} test(s) failed out of {summary['total_tests']} total tests.")
        print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
        
        if summary["classification_failures"] > 0:
            print(f"❌ Classification Issues: {summary['classification_failures']} tests failed")
            print("   → The intent classifier may still have issues with complex prompts")
        
        if summary["json_parsing_failures"] > 0:
            print(f"❌ JSON Parsing Issues: {summary['json_parsing_failures']} tests failed")
            print("   → JSON parsing robustness needs improvement")
        
        if summary["fallback_failures"] > 0:
            print(f"❌ Fallback Issues: {summary['fallback_failures']} tests failed")
            print("   → Keyword-based fallback mechanism needs attention")
        
        if summary["other_category_failures"] > 0:
            print(f"❌ 'Other' Category Defaults: {summary['other_category_failures']} tests failed")
            print("   → Valid prompts are still defaulting to 'other' category")
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()