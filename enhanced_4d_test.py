#!/usr/bin/env python3
"""
Enhanced 4D Methodology Testing for Pehance Prompt Enhancement System
Tests the anti-over-enhancement improvements and proportional response features
"""

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

class Enhanced4DMethodologyTester:
    """Enhanced tester for 4D methodology improvements and anti-over-enhancement features"""
    
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
            print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
        print()

    def test_basic_connectivity(self):
        """Test basic API connectivity"""
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

    def test_simple_inputs_anti_over_enhancement(self):
        """Test simple inputs that should NOT get overly complex responses"""
        print("🎯 Testing Simple Input Anti-Over-Enhancement...")
        
        simple_test_cases = [
            {
                "input": "hi",
                "expected_type": "clarification_request",
                "max_ratio": 1.5,
                "description": "Simple greeting should get clarification request"
            },
            {
                "input": "hello",
                "expected_type": "clarification_request", 
                "max_ratio": 1.5,
                "description": "Basic greeting should get conversational response"
            },
            {
                "input": "help me",
                "expected_type": "clarification_request",
                "max_ratio": 2.0,
                "description": "Vague request should ask for more details"
            },
            {
                "input": "write something",
                "expected_type": "basic_enhancement",
                "max_ratio": 3.0,
                "description": "Minimal request should get basic enhancement"
            }
        ]
        
        all_passed = True
        
        for test_case in simple_test_cases:
            print(f"  Testing: '{test_case['input']}'")
            
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["input"]},
                    timeout=30
                )
                
                if response.status_code != 200:
                    self.log_result(
                        f"Simple Input: {test_case['input']}", 
                        False, 
                        f"API error: HTTP {response.status_code}", 
                        {"status_code": response.status_code, "text": response.text}
                    )
                    all_passed = False
                    continue
                
                data = response.json()
                
                # Check enhancement type
                enhancement_type = data.get("enhancement_type")
                enhancement_ratio = data.get("enhancement_ratio", 0)
                complexity_score = data.get("complexity_score", 0)
                
                # Validate enhancement type
                type_correct = enhancement_type == test_case["expected_type"]
                
                # Validate enhancement ratio (should be proportional)
                ratio_appropriate = enhancement_ratio <= test_case["max_ratio"]
                
                # Validate complexity score (should be low for simple inputs)
                complexity_appropriate = complexity_score <= 0.5
                
                if type_correct and ratio_appropriate and complexity_appropriate:
                    self.log_result(
                        f"Simple Input: {test_case['input']}", 
                        True, 
                        f"✅ Type: {enhancement_type}, Ratio: {enhancement_ratio}x, Complexity: {complexity_score:.2f}"
                    )
                else:
                    issues = []
                    if not type_correct:
                        issues.append(f"Wrong type: got {enhancement_type}, expected {test_case['expected_type']}")
                    if not ratio_appropriate:
                        issues.append(f"Ratio too high: {enhancement_ratio}x > {test_case['max_ratio']}x")
                    if not complexity_appropriate:
                        issues.append(f"Complexity too high: {complexity_score:.2f} > 0.5")
                    
                    self.log_result(
                        f"Simple Input: {test_case['input']}", 
                        False, 
                        f"❌ Issues: {'; '.join(issues)}", 
                        data
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Simple Input: {test_case['input']}", 
                    False, 
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)  # Rate limiting
        
        return all_passed

    def test_complexity_progression(self):
        """Test inputs of increasing complexity for proportional enhancement"""
        print("📈 Testing Complexity Progression...")
        
        complexity_test_cases = [
            {
                "input": "help me write a story",
                "expected_type": "basic_enhancement",
                "min_ratio": 1.5,
                "max_ratio": 3.0,
                "min_complexity": 0.2,
                "max_complexity": 0.5,
                "description": "Basic story request"
            },
            {
                "input": "create a marketing email for my startup",
                "expected_type": "standard_enhancement",
                "min_ratio": 3.0,
                "max_ratio": 6.0,
                "min_complexity": 0.4,
                "max_complexity": 0.7,
                "description": "Intermediate marketing request"
            },
            {
                "input": "develop a comprehensive content strategy for a SaaS company targeting enterprise clients with integration challenges",
                "expected_type": "advanced_enhancement",
                "min_ratio": 5.0,
                "max_ratio": 15.0,
                "min_complexity": 0.7,
                "max_complexity": 1.0,
                "description": "Advanced business strategy request"
            }
        ]
        
        all_passed = True
        
        for test_case in complexity_test_cases:
            print(f"  Testing: '{test_case['input'][:50]}...'")
            
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["input"]},
                    timeout=45
                )
                
                if response.status_code != 200:
                    self.log_result(
                        f"Complexity Test: {test_case['description']}", 
                        False, 
                        f"API error: HTTP {response.status_code}", 
                        {"status_code": response.status_code, "text": response.text}
                    )
                    all_passed = False
                    continue
                
                data = response.json()
                enhancement_type = data.get("enhancement_type")
                enhancement_ratio = data.get("enhancement_ratio", 0)
                complexity_score = data.get("complexity_score", 0)
                
                # Validate enhancement type
                type_correct = enhancement_type == test_case["expected_type"]
                
                # Validate enhancement ratio is within expected range
                ratio_appropriate = test_case["min_ratio"] <= enhancement_ratio <= test_case["max_ratio"]
                
                # Validate complexity score is within expected range
                complexity_appropriate = test_case["min_complexity"] <= complexity_score <= test_case["max_complexity"]
                
                if type_correct and ratio_appropriate and complexity_appropriate:
                    self.log_result(
                        f"Complexity Test: {test_case['description']}", 
                        True, 
                        f"✅ Type: {enhancement_type}, Ratio: {enhancement_ratio}x, Complexity: {complexity_score:.2f}"
                    )
                else:
                    issues = []
                    if not type_correct:
                        issues.append(f"Wrong type: got {enhancement_type}, expected {test_case['expected_type']}")
                    if not ratio_appropriate:
                        issues.append(f"Ratio out of range: {enhancement_ratio}x not in [{test_case['min_ratio']}-{test_case['max_ratio']}]")
                    if not complexity_appropriate:
                        issues.append(f"Complexity out of range: {complexity_score:.2f} not in [{test_case['min_complexity']}-{test_case['max_complexity']}]")
                    
                    self.log_result(
                        f"Complexity Test: {test_case['description']}", 
                        False, 
                        f"❌ Issues: {'; '.join(issues)}", 
                        data
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Complexity Test: {test_case['description']}", 
                    False, 
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(2)  # Rate limiting for complex requests
        
        return all_passed

    def test_new_response_fields(self):
        """Test that API returns all the new enhanced fields"""
        print("🔍 Testing New Response Fields...")
        
        test_prompt = "create a marketing strategy for my tech startup"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt},
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_result("New Response Fields", False, f"API error: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check for required new fields
            required_fields = [
                "enhancement_type",
                "enhancement_ratio", 
                "complexity_score"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
            
            # Check intent_analysis structure
            agent_results = data.get("agent_results", {})
            intent_analysis = agent_results.get("intent_analysis", {})
            required_intent_fields = [
                "input_complexity_score",
                "enhancement_recommended",
                "suggested_action",
                "input_type"
            ]
            
            missing_intent_fields = []
            for field in required_intent_fields:
                if field not in intent_analysis:
                    missing_intent_fields.append(field)
            
            if not missing_fields and not missing_intent_fields:
                self.log_result(
                    "New Response Fields", 
                    True, 
                    f"✅ All required fields present: {required_fields + required_intent_fields}"
                )
                return True
            else:
                issues = []
                if missing_fields:
                    issues.append(f"Missing response fields: {missing_fields}")
                if missing_intent_fields:
                    issues.append(f"Missing intent analysis fields: {missing_intent_fields}")
                
                self.log_result(
                    "New Response Fields", 
                    False, 
                    f"❌ {'; '.join(issues)}", 
                    data
                )
                return False
                
        except Exception as e:
            self.log_result(
                "New Response Fields", 
                False, 
                f"Request error: {str(e)}"
            )
            return False

    def test_smart_routing(self):
        """Test that smart routing works correctly"""
        print("🛣️ Testing Smart Routing...")
        
        routing_test_cases = [
            {
                "input": "hey there",
                "expected_route": "clarification_request",
                "description": "Simple greeting should route to clarification"
            },
            {
                "input": "help",
                "expected_route": "clarification_request", 
                "description": "Minimal input should route to clarification"
            },
            {
                "input": "write a blog post about AI",
                "expected_route": "basic_enhancement",
                "description": "Basic request should route to basic enhancement"
            },
            {
                "input": "develop a comprehensive AI strategy for enterprise transformation including risk assessment and implementation roadmap",
                "expected_route": "advanced_enhancement",
                "description": "Complex request should route to advanced enhancement"
            }
        ]
        
        all_passed = True
        
        for test_case in routing_test_cases:
            print(f"  Testing routing for: '{test_case['input'][:40]}...'")
            
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["input"]},
                    timeout=30
                )
                
                if response.status_code != 200:
                    self.log_result(
                        f"Routing: {test_case['description']}", 
                        False, 
                        f"API error: HTTP {response.status_code}"
                    )
                    all_passed = False
                    continue
                
                data = response.json()
                enhancement_type = data.get("enhancement_type")
                
                if enhancement_type == test_case["expected_route"]:
                    self.log_result(
                        f"Routing: {test_case['description']}", 
                        True, 
                        f"✅ Correctly routed to {enhancement_type}"
                    )
                else:
                    self.log_result(
                        f"Routing: {test_case['description']}", 
                        False, 
                        f"❌ Wrong route: got {enhancement_type}, expected {test_case['expected_route']}", 
                        data
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Routing: {test_case['description']}", 
                    False, 
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)
        
        return all_passed

    def test_4d_methodology_implementation(self):
        """Test that 4D methodology is properly implemented"""
        print("🎯 Testing 4D Methodology Implementation...")
        
        complex_prompt = "create a comprehensive digital marketing strategy for a B2B SaaS company targeting mid-market enterprises in the healthcare sector"
        
        try:
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": complex_prompt},
                timeout=45
            )
            
            if response.status_code != 200:
                self.log_result("4D Methodology", False, f"API error: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check for 4D methodology indicators
            agent_results = data.get("agent_results", {})
            process_steps = agent_results.get("process_steps", [])
            methodology_applied = agent_results.get("4d_methodology_applied", False)
            
            # Check if methodology was applied
            methodology_indicators = [
                methodology_applied,
                len(process_steps) >= 2,  # Should have multiple steps
                data.get("enhancement_type") in ["standard_enhancement", "advanced_enhancement"]
            ]
            
            if all(methodology_indicators):
                self.log_result(
                    "4D Methodology Implementation", 
                    True, 
                    f"✅ 4D methodology applied: {process_steps}, methodology_applied: {methodology_applied}"
                )
                return True
            else:
                issues = []
                if not methodology_applied:
                    issues.append("4d_methodology_applied is False")
                if len(process_steps) < 2:
                    issues.append(f"Too few process steps: {process_steps}")
                if data.get("enhancement_type") not in ["standard_enhancement", "advanced_enhancement"]:
                    issues.append(f"Wrong enhancement type for complex input: {data.get('enhancement_type')}")
                
                self.log_result(
                    "4D Methodology Implementation", 
                    False, 
                    f"❌ Issues: {'; '.join(issues)}", 
                    data
                )
                return False
                
        except Exception as e:
            self.log_result(
                "4D Methodology Implementation", 
                False, 
                f"Request error: {str(e)}"
            )
            return False

    def test_anti_over_enhancement_ratios(self):
        """Test that enhancement ratios are reasonable and not excessive"""
        print("⚖️ Testing Anti-Over-Enhancement Ratios...")
        
        # Test cases with maximum acceptable ratios
        ratio_test_cases = [
            {"input": "hi", "max_ratio": 2.0, "description": "Greeting"},
            {"input": "help", "max_ratio": 3.0, "description": "Single word"},
            {"input": "write a story", "max_ratio": 5.0, "description": "Basic request"},
            {"input": "create marketing content", "max_ratio": 8.0, "description": "Intermediate request"}
        ]
        
        excessive_ratios = []
        all_passed = True
        
        for test_case in ratio_test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["input"]},
                    timeout=30
                )
                
                if response.status_code != 200:
                    self.log_result(
                        f"Ratio Test: {test_case['description']}", 
                        False, 
                        f"API error: HTTP {response.status_code}"
                    )
                    all_passed = False
                    continue
                
                data = response.json()
                enhancement_ratio = data.get("enhancement_ratio", 0)
                
                if enhancement_ratio <= test_case["max_ratio"]:
                    self.log_result(
                        f"Ratio Test: {test_case['description']}", 
                        True, 
                        f"✅ Appropriate ratio: {enhancement_ratio}x (≤ {test_case['max_ratio']}x)"
                    )
                else:
                    excessive_ratios.append({
                        "input": test_case["input"],
                        "ratio": enhancement_ratio,
                        "max_expected": test_case["max_ratio"]
                    })
                    self.log_result(
                        f"Ratio Test: {test_case['description']}", 
                        False, 
                        f"❌ Excessive ratio: {enhancement_ratio}x > {test_case['max_ratio']}x", 
                        data
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Ratio Test: {test_case['description']}", 
                    False, 
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(1)
        
        # Overall anti-over-enhancement assessment
        if not excessive_ratios:
            self.log_result(
                "Overall Anti-Over-Enhancement", 
                True, 
                "✅ No excessive enhancement ratios detected"
            )
        else:
            self.log_result(
                "Overall Anti-Over-Enhancement", 
                False, 
                f"❌ Found {len(excessive_ratios)} cases with excessive ratios"
            )
            all_passed = False
        
        return all_passed

    def run_enhanced_4d_tests(self):
        """Run all enhanced 4D methodology tests"""
        print("🚀 Starting Enhanced 4D Methodology Testing for Pehance")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Stopping tests.")
            return self.generate_summary()
        
        # Run all enhanced 4D methodology tests
        test_methods = [
            self.test_simple_inputs_anti_over_enhancement,
            self.test_complexity_progression,
            self.test_new_response_fields,
            self.test_smart_routing,
            self.test_4d_methodology_implementation,
            self.test_anti_over_enhancement_ratios
        ]
        
        for test_method in test_methods:
            try:
                print(f"\n🔍 Running: {test_method.__name__}")
                test_method()
            except Exception as e:
                self.log_result(
                    f"Test Method: {test_method.__name__}",
                    False,
                    f"Test method failed with exception: {str(e)}"
                )
            
            # Delay between test suites to respect rate limits
            time.sleep(3)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🏁 ENHANCED 4D METHODOLOGY TEST SUMMARY")
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
    tester = Enhanced4DMethodologyTester()
    summary = tester.run_enhanced_4d_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {summary['failed_tests']} test(s) failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()