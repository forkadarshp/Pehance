#!/usr/bin/env python3
"""
4-D Methodology Implementation Testing
Tests the improved 4-D methodology with different complexity levels as requested in the review.

Test Cases:
1. Basic/Casual Input Test: "hi" - should be classified as "other" category, basic complexity
2. Intermediate Complexity Test: "Help me create a todo app using React" - should be classified as "technical", intermediate complexity  
3. Advanced Complexity Test: Enterprise-grade microservices architecture - should be classified as "technical", advanced complexity

Verification Points:
- Check intent classification accuracy and complexity detection
- Verify that context gathering is skipped for basic requests
- Confirm 4-D methodology is applied appropriately based on complexity
- Ensure enhanced prompts are proportional to input complexity
- Test that the multi-agent system produces sensible, contextual enhancements
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

class FourDMethodologyTester:
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
        print()

    def test_basic_casual_input(self):
        """Test Case 1: Basic/Casual Input - 'hi'"""
        test_prompt = "hi"
        
        try:
            print(f"🧪 Testing Basic/Casual Input: '{test_prompt}'")
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                
                # Check intent classification
                intent_category = intent_analysis.get("intent_category", "")
                complexity_level = intent_analysis.get("complexity_level", "")
                confidence = intent_analysis.get("confidence", 0)
                
                # Verify expected classification
                expected_category = "other"
                expected_complexity = "basic"
                
                classification_correct = intent_category == expected_category
                complexity_correct = complexity_level.lower() == expected_complexity
                
                # Check response proportionality (should be brief for basic input)
                original_length = len(test_prompt)
                enhanced_length = len(data.get("enhanced_prompt", ""))
                enhancement_ratio = enhanced_length / original_length if original_length > 0 else 0
                
                # For basic input like "hi", enhancement should be proportional (not over-engineered)
                proportional_response = enhancement_ratio < 50  # Not more than 50x the original
                
                success = classification_correct and complexity_correct and proportional_response
                
                details = f"Intent: {intent_category} (expected: {expected_category}), " \
                         f"Complexity: {complexity_level} (expected: {expected_complexity}), " \
                         f"Confidence: {confidence:.2f}, " \
                         f"Enhancement ratio: {enhancement_ratio:.1f}x, " \
                         f"Enhanced length: {enhanced_length} chars"
                
                if not classification_correct:
                    details += f" | ❌ Wrong intent classification"
                if not complexity_correct:
                    details += f" | ❌ Wrong complexity level"
                if not proportional_response:
                    details += f" | ❌ Over-engineered response for basic input"
                
                self.log_result(
                    "Basic/Casual Input Test ('hi')",
                    success,
                    details,
                    {
                        "intent_category": intent_category,
                        "complexity_level": complexity_level,
                        "confidence": confidence,
                        "enhancement_ratio": enhancement_ratio,
                        "enhanced_prompt_preview": data.get("enhanced_prompt", "")[:200] + "..."
                    }
                )
                return success
                
            else:
                self.log_result(
                    "Basic/Casual Input Test ('hi')",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Basic/Casual Input Test ('hi')",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_intermediate_complexity(self):
        """Test Case 2: Intermediate Complexity - React todo app"""
        test_prompt = "Help me create a todo app using React"
        
        try:
            print(f"🧪 Testing Intermediate Complexity: '{test_prompt}'")
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt},
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                
                # Check intent classification
                intent_category = intent_analysis.get("intent_category", "")
                complexity_level = intent_analysis.get("complexity_level", "")
                confidence = intent_analysis.get("confidence", 0)
                domain = intent_analysis.get("domain", "")
                
                # Verify expected classification
                expected_category = "technical"
                expected_complexity = "intermediate"
                
                classification_correct = intent_category == expected_category
                complexity_correct = complexity_level.lower() == expected_complexity
                
                # Check if 4-D methodology is applied appropriately
                enhanced_prompt = data.get("enhanced_prompt", "")
                original_length = len(test_prompt)
                enhanced_length = len(enhanced_prompt)
                enhancement_ratio = enhanced_length / original_length
                
                # For intermediate complexity, expect structured enhancement
                has_structure = any(keyword in enhanced_prompt.lower() for keyword in [
                    "requirements", "specifications", "features", "components", 
                    "architecture", "implementation", "best practices"
                ])
                
                # Should have domain context for React development
                has_domain_context = any(keyword in enhanced_prompt.lower() for keyword in [
                    "react", "component", "state", "hooks", "jsx", "frontend"
                ])
                
                # Enhancement should be substantial but not excessive
                appropriate_enhancement = 5 < enhancement_ratio < 100
                
                success = (classification_correct and complexity_correct and 
                          has_structure and has_domain_context and appropriate_enhancement)
                
                details = f"Intent: {intent_category} (expected: {expected_category}), " \
                         f"Complexity: {complexity_level} (expected: {expected_complexity}), " \
                         f"Domain: {domain}, Confidence: {confidence:.2f}, " \
                         f"Enhancement ratio: {enhancement_ratio:.1f}x, " \
                         f"Has structure: {has_structure}, Has domain context: {has_domain_context}"
                
                if not classification_correct:
                    details += f" | ❌ Wrong intent classification"
                if not complexity_correct:
                    details += f" | ❌ Wrong complexity level"
                if not has_structure:
                    details += f" | ❌ Missing structured approach"
                if not has_domain_context:
                    details += f" | ❌ Missing domain-specific context"
                if not appropriate_enhancement:
                    details += f" | ❌ Inappropriate enhancement level"
                
                self.log_result(
                    "Intermediate Complexity Test (React Todo App)",
                    success,
                    details,
                    {
                        "intent_category": intent_category,
                        "complexity_level": complexity_level,
                        "domain": domain,
                        "confidence": confidence,
                        "enhancement_ratio": enhancement_ratio,
                        "enhanced_prompt_preview": enhanced_prompt[:300] + "..."
                    }
                )
                return success
                
            else:
                self.log_result(
                    "Intermediate Complexity Test (React Todo App)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Intermediate Complexity Test (React Todo App)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_advanced_complexity(self):
        """Test Case 3: Advanced Complexity - Enterprise microservices architecture"""
        test_prompt = ("Design a comprehensive enterprise-grade microservices architecture for a fintech platform "
                      "handling real-time transactions with PCI DSS compliance, fault tolerance, and global scalability requirements")
        
        try:
            print(f"🧪 Testing Advanced Complexity: '{test_prompt[:80]}...'")
            response = requests.post(
                f"{API_BASE}/enhance",
                json={"prompt": test_prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_results = data.get("agent_results", {})
                intent_analysis = agent_results.get("intent_analysis", {})
                
                # Check intent classification
                intent_category = intent_analysis.get("intent_category", "")
                complexity_level = intent_analysis.get("complexity_level", "")
                confidence = intent_analysis.get("confidence", 0)
                domain = intent_analysis.get("domain", "")
                
                # Verify expected classification
                expected_category = "technical"
                expected_complexity = "advanced"
                
                classification_correct = intent_category == expected_category
                complexity_correct = complexity_level.lower() == expected_complexity
                
                # Check if full 4-D methodology is applied
                enhanced_prompt = data.get("enhanced_prompt", "")
                original_length = len(test_prompt)
                enhanced_length = len(enhanced_prompt)
                enhancement_ratio = enhanced_length / original_length
                
                # For advanced complexity, expect extensive domain research and methodology
                advanced_keywords = [
                    "microservices", "architecture", "scalability", "compliance", "security",
                    "fault tolerance", "distributed", "api gateway", "service mesh",
                    "monitoring", "logging", "deployment", "containerization"
                ]
                
                fintech_keywords = [
                    "pci dss", "financial", "transaction", "payment", "security",
                    "audit", "compliance", "encryption", "fraud"
                ]
                
                has_advanced_concepts = sum(1 for keyword in advanced_keywords 
                                          if keyword in enhanced_prompt.lower()) >= 5
                
                has_domain_expertise = sum(1 for keyword in fintech_keywords 
                                         if keyword in enhanced_prompt.lower()) >= 3
                
                # Should have extensive enhancement for advanced complexity
                extensive_enhancement = enhancement_ratio > 10
                
                # Check for structured approach (sections, requirements, etc.)
                has_comprehensive_structure = any(keyword in enhanced_prompt.lower() for keyword in [
                    "requirements", "architecture", "implementation", "security", 
                    "deployment", "monitoring", "testing", "compliance"
                ])
                
                success = (classification_correct and complexity_correct and 
                          has_advanced_concepts and has_domain_expertise and 
                          extensive_enhancement and has_comprehensive_structure)
                
                details = f"Intent: {intent_category} (expected: {expected_category}), " \
                         f"Complexity: {complexity_level} (expected: {expected_complexity}), " \
                         f"Domain: {domain}, Confidence: {confidence:.2f}, " \
                         f"Enhancement ratio: {enhancement_ratio:.1f}x, " \
                         f"Advanced concepts: {has_advanced_concepts}, " \
                         f"Domain expertise: {has_domain_expertise}, " \
                         f"Comprehensive structure: {has_comprehensive_structure}"
                
                if not classification_correct:
                    details += f" | ❌ Wrong intent classification"
                if not complexity_correct:
                    details += f" | ❌ Wrong complexity level"
                if not has_advanced_concepts:
                    details += f" | ❌ Missing advanced technical concepts"
                if not has_domain_expertise:
                    details += f" | ❌ Missing fintech domain expertise"
                if not extensive_enhancement:
                    details += f" | ❌ Insufficient enhancement for advanced complexity"
                if not has_comprehensive_structure:
                    details += f" | ❌ Missing comprehensive structure"
                
                self.log_result(
                    "Advanced Complexity Test (Enterprise Microservices)",
                    success,
                    details,
                    {
                        "intent_category": intent_category,
                        "complexity_level": complexity_level,
                        "domain": domain,
                        "confidence": confidence,
                        "enhancement_ratio": enhancement_ratio,
                        "enhanced_prompt_preview": enhanced_prompt[:500] + "..."
                    }
                )
                return success
                
            else:
                self.log_result(
                    "Advanced Complexity Test (Enterprise Microservices)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Advanced Complexity Test (Enterprise Microservices)",
                False,
                f"Request error: {str(e)}"
            )
            return False

    def test_context_gathering_behavior(self):
        """Test that context gathering is appropriately applied based on complexity"""
        test_cases = [
            {
                "prompt": "hello",
                "expected_behavior": "minimal_context",
                "description": "Basic greeting should skip extensive context gathering"
            },
            {
                "prompt": "Build a machine learning model for fraud detection",
                "expected_behavior": "extensive_context",
                "description": "Complex technical task should include extensive context gathering"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                print(f"🧪 Testing Context Gathering: {test_case['description']}")
                response = requests.post(
                    f"{API_BASE}/enhance",
                    json={"prompt": test_case["prompt"]},
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    enhanced_prompt = data.get("enhanced_prompt", "")
                    agent_results = data.get("agent_results", {})
                    intent_analysis = agent_results.get("intent_analysis", {})
                    
                    complexity = intent_analysis.get("complexity_level", "").lower()
                    enhancement_ratio = len(enhanced_prompt) / len(test_case["prompt"])
                    
                    if test_case["expected_behavior"] == "minimal_context":
                        # For basic prompts, context should be minimal
                        appropriate_context = enhancement_ratio < 20 and complexity in ["basic", "simple"]
                        behavior_description = f"Minimal context applied (ratio: {enhancement_ratio:.1f}x, complexity: {complexity})"
                    else:
                        # For complex prompts, context should be extensive
                        appropriate_context = enhancement_ratio > 5 and complexity in ["intermediate", "advanced", "complex"]
                        behavior_description = f"Extensive context applied (ratio: {enhancement_ratio:.1f}x, complexity: {complexity})"
                    
                    if appropriate_context:
                        self.log_result(
                            f"Context Gathering: {test_case['description']}",
                            True,
                            behavior_description
                        )
                    else:
                        self.log_result(
                            f"Context Gathering: {test_case['description']}",
                            False,
                            f"Inappropriate context level - {behavior_description}"
                        )
                        all_passed = False
                        
                else:
                    self.log_result(
                        f"Context Gathering: {test_case['description']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Context Gathering: {test_case['description']}",
                    False,
                    f"Request error: {str(e)}"
                )
                all_passed = False
            
            time.sleep(2)  # Delay between requests
        
        return all_passed

    def run_4d_methodology_tests(self):
        """Run all 4-D methodology tests"""
        print("🚀 Starting 4-D Methodology Implementation Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test basic connectivity first
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code != 200:
                print("❌ Basic connectivity failed. Stopping tests.")
                return self.generate_summary()
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return self.generate_summary()
        
        # Run the three main test cases
        test_methods = [
            self.test_basic_casual_input,
            self.test_intermediate_complexity,
            self.test_advanced_complexity,
            self.test_context_gathering_behavior
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
            
            # Delay between test suites to avoid rate limiting
            time.sleep(3)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🏁 4-D METHODOLOGY TEST SUMMARY")
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
    tester = FourDMethodologyTester()
    summary = tester.run_4d_methodology_tests()
    
    # Print final assessment
    print("\n" + "="*80)
    print("📊 FINAL ASSESSMENT")
    print("="*80)
    
    if summary["failed_tests"] == 0:
        print("🎉 All 4-D methodology tests passed!")
        print("✅ Intent classification accuracy verified")
        print("✅ Complexity detection working correctly") 
        print("✅ Context gathering appropriately applied")
        print("✅ Enhanced prompts proportional to input complexity")
        print("✅ Multi-agent system producing contextual enhancements")
    else:
        print(f"⚠️  {summary['failed_tests']} test(s) failed.")
        print("❌ 4-D methodology implementation needs attention")
    
    return summary

if __name__ == "__main__":
    main()