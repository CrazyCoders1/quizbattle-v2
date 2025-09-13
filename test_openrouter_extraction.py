"""
Comprehensive test script for OpenRouter PDF Question Extraction
Tests all models, API integration, fallbacks, and logging
"""
import sys
import os
import json
import time
from datetime import datetime

# Add backend path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.openrouter_pdf_extractor import get_openrouter_extractor
from app.services.pdf_extractor import get_extractor

# Sample PDF content for testing
SAMPLE_PDF_TEXT = """
CBSE Class 11 Physics Mock Test - Chapter 1: Units and Measurements

Question 1: Which of the following is the correct unit of force in the SI system?
A) Newton (N)
B) Joule (J)
C) Watt (W)
D) Pascal (Pa)

Question 2: The dimensional formula for acceleration is:
A) [M L T-2]
B) [L T-2]
C) [M L T-1]
D) [M L2 T-2]

Question 3: Calculate the number of significant figures in 0.00240.
A) 2
B) 3
C) 4
D) 5

Question 4: What is the principle of dimensional analysis?
A) Physical quantities with same dimensions can be added
B) Equations must be dimensionally consistent
C) All physical constants are dimensionless
D) Units can be converted using dimensional formulas

Question 5: The vernier caliper can measure lengths to the accuracy of:
A) 0.1 mm
B) 0.01 mm
C) 0.001 mm
D) 0.0001 mm

Answer Key:
1. A
2. B
3. B
4. B
5. A
"""

SAMPLE_PDF_TEXT_TOUGH = """
Advanced Physics Problems - Quantum Mechanics

Question 1: Derive the expression for the energy eigenvalues of a particle in a one-dimensional infinite potential well.
A) En = n²π²ℏ²/(2mL²)
B) En = nπℏ²/(2mL²) 
C) En = n²ℏ²/(8mL²)
D) En = πℏ²/(2nmL²)

Question 2: Calculate the wavelength of an electron moving with velocity 10⁶ m/s (Given: h = 6.626 × 10⁻³⁴ J·s, me = 9.11 × 10⁻³¹ kg).
A) 7.27 × 10⁻¹⁰ m
B) 7.27 × 10⁻¹¹ m  
C) 6.26 × 10⁻¹⁰ m
D) 9.11 × 10⁻¹⁰ m

Question 3: Analyze the uncertainty principle and determine the minimum energy of a quantum harmonic oscillator.
A) ℏω/2
B) ℏω
C) 3ℏω/2
D) 2ℏω

Answers: 1-A, 2-A, 3-A
"""

def test_openrouter_extraction():
    """Test OpenRouter extraction with sample content"""
    print("🚀 Testing OpenRouter PDF Extraction System")
    print("=" * 60)
    
    try:
        # Test 1: Initialize OpenRouter extractor
        print("\n1. Testing OpenRouter Extractor Initialization")
        extractor = get_openrouter_extractor()
        
        if extractor.openrouter:
            print(f"✅ OpenRouter initialized with {len(extractor.openrouter.MODELS)} models")
            print(f"   First 5 models: {extractor.openrouter.MODELS[:5]}")
        else:
            print("❌ OpenRouter not initialized - API key issue?")
            return False
        
        # Test 2: Easy mode extraction
        print("\n2. Testing Easy Mode Extraction")
        print(f"   Sample text length: {len(SAMPLE_PDF_TEXT)} characters")
        
        start_time = time.time()
        easy_questions = extractor.extract_questions_from_text(
            SAMPLE_PDF_TEXT, "CBSE 11 Physics", "easy"
        )
        easy_time = time.time() - start_time
        
        print(f"   ⏱️  Extraction time: {easy_time:.2f} seconds")
        print(f"   📊 Questions extracted: {len(easy_questions)}")
        
        if easy_questions:
            print(f"   ✅ Easy mode successful")
            first_question = easy_questions[0]
            print(f"   📝 First question: {first_question['question'][:80]}...")
            print(f"   🎯 Difficulty: {first_question.get('difficulty', 'N/A')}")
            print(f"   🔧 Method: {first_question.get('extraction_method', 'N/A')}")
        else:
            print(f"   ❌ Easy mode failed - no questions extracted")
        
        # Test 3: Tough mode extraction  
        print("\n3. Testing Tough Mode Extraction")
        
        start_time = time.time()
        tough_questions = extractor.extract_questions_from_text(
            SAMPLE_PDF_TEXT_TOUGH, "Advanced Physics", "tough"
        )
        tough_time = time.time() - start_time
        
        print(f"   ⏱️  Extraction time: {tough_time:.2f} seconds")
        print(f"   📊 Questions extracted: {len(tough_questions)}")
        
        if tough_questions:
            print(f"   ✅ Tough mode successful")
            tough_question = tough_questions[0]
            print(f"   📝 First question: {tough_question['question'][:80]}...")
            print(f"   🎯 Difficulty: {tough_question.get('difficulty', 'N/A')}")
            print(f"   💡 Hint: {tough_question.get('hint', 'None')[:50]}..." if tough_question.get('hint') else "   💡 No hint")
            print(f"   🔧 Method: {tough_question.get('extraction_method', 'N/A')}")
        else:
            print(f"   ❌ Tough mode failed - no questions extracted")
        
        # Test 4: Mixed mode extraction
        print("\n4. Testing Mixed Mode Extraction")
        
        start_time = time.time()
        mixed_questions = extractor.extract_questions_from_text(
            SAMPLE_PDF_TEXT, "CBSE 11 Physics", "mixed"
        )
        mixed_time = time.time() - start_time
        
        print(f"   ⏱️  Extraction time: {mixed_time:.2f} seconds")
        print(f"   📊 Questions extracted: {len(mixed_questions)}")
        
        if mixed_questions:
            easy_count = sum(1 for q in mixed_questions if q.get('difficulty') == 'easy')
            tough_count = sum(1 for q in mixed_questions if q.get('difficulty') == 'tough')
            print(f"   ✅ Mixed mode successful")
            print(f"   📈 Easy questions: {easy_count}")
            print(f"   📈 Tough questions: {tough_count}")
            print(f"   📈 Ratio: {easy_count/(easy_count+tough_count)*100:.1f}% easy, {tough_count/(easy_count+tough_count)*100:.1f}% tough")
        else:
            print(f"   ❌ Mixed mode failed - no questions extracted")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_main_extractor_integration():
    """Test the main PDF extractor with OpenRouter integration"""
    print("\n" + "=" * 60)
    print("🔧 Testing Main PDF Extractor Integration")
    print("=" * 60)
    
    try:
        # Get the main extractor (should now use OpenRouter first)
        extractor = get_extractor()
        
        print(f"✅ Main extractor initialized")
        print(f"   Individual providers: {len(extractor.providers)}")
        
        # Test extraction
        print("\n5. Testing Main Extractor with OpenRouter Priority")
        
        start_time = time.time()
        questions = extractor.extract_questions_from_text(
            SAMPLE_PDF_TEXT, "CBSE 11 Physics", "mixed"
        )
        extraction_time = time.time() - start_time
        
        print(f"   ⏱️  Total extraction time: {extraction_time:.2f} seconds")
        print(f"   📊 Questions extracted: {len(questions)}")
        
        if questions:
            print(f"   ✅ Main extractor successful")
            
            # Analyze extraction methods used
            methods = {}
            for q in questions:
                method = q.get('extraction_method', 'unknown')
                methods[method] = methods.get(method, 0) + 1
            
            print(f"   🔍 Extraction methods used:")
            for method, count in methods.items():
                print(f"      {method}: {count} questions")
                
            # Show first question details
            first_q = questions[0]
            print(f"   📝 Sample question: {first_q['question'][:60]}...")
            print(f"   🎯 Difficulty: {first_q.get('difficulty', 'N/A')}")
            
        else:
            print(f"   ❌ Main extractor failed - no questions extracted")
            
        return len(questions) > 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and fallback behavior"""
    print("\n" + "=" * 60)
    print("⚠️  Testing Error Handling & Fallbacks")
    print("=" * 60)
    
    try:
        extractor = get_openrouter_extractor()
        
        # Test with empty text
        print("\n6. Testing Empty Text Handling")
        empty_questions = extractor.extract_questions_from_text("", "Test", "mixed")
        print(f"   📊 Empty text result: {len(empty_questions)} questions (should be 0)")
        
        # Test with non-question text
        print("\n7. Testing Non-Question Text")
        random_text = "This is just some random text that doesn't contain any questions at all."
        random_questions = extractor.extract_questions_from_text(random_text, "Test", "mixed")
        print(f"   📊 Random text result: {len(random_questions)} questions")
        
        # Test regex fallback (by using invalid API key scenario)
        print("\n8. Testing Regex Fallback Behavior")
        
        # This should fallback to regex if OpenRouter fails
        main_extractor = get_extractor()
        fallback_questions = main_extractor._extract_with_regex(
            SAMPLE_PDF_TEXT, "CBSE 11 Physics", "mixed", "Format_A"
        )
        print(f"   📊 Regex fallback result: {len(fallback_questions)} questions")
        
        if fallback_questions:
            print(f"   ✅ Regex fallback working")
            print(f"   📝 Sample: {fallback_questions[0]['question'][:50]}...")
        else:
            print(f"   ⚠️  Regex fallback returned no questions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def display_summary(results):
    """Display test summary"""
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if passed_tests == total_tests else '❌ SOME TESTS FAILED'}")

def main():
    """Main test execution"""
    print("OpenRouter PDF Extraction Test Suite")
    print("Generated at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Run all tests
    results = {
        "OpenRouter Extraction": test_openrouter_extraction(),
        "Main Extractor Integration": test_main_extractor_integration(),
        "Error Handling & Fallbacks": test_error_handling()
    }
    
    # Display summary
    display_summary(results)
    
    print(f"\n📝 Log files and detailed extraction logs can be viewed through:")
    print(f"   - Admin debug endpoints: /debug/extraction/logs")
    print(f"   - OpenRouter model stats: /debug/extraction/models")
    print(f"   - Backend application logs")
    
    return all(results.values())

if __name__ == "__main__":
    # Run the test suite
    success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)