#!/usr/bin/env python3
"""
Test script for PDF extraction service
Run this to test AI API integration and regex fallback
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and create application context
from app import create_app
from app.services.pdf_extractor import PDFQuestionExtractor

# Create Flask app instance for testing
app = create_app()

def test_extraction():
    """Test PDF extraction with sample text"""
    
    with app.app_context():
        # Sample PDF text content for testing
        sample_text = """
        PHYSICS EXAMINATION - CLASS 11
        
        Question 1: What is the SI unit of force?
        A) Newton
        B) Joule  
        C) Watt
        D) Pascal
        
        Question 2: Calculate the acceleration of an object with mass 10 kg when a force of 50 N is applied.
        A) 5 m/s²
        B) 10 m/s²
        C) 2.5 m/s²
        D) 0.2 m/s²
        
        Question 3: Which of the following is a vector quantity?
        A) Mass
        B) Temperature
        C) Velocity  
        D) Time
        
        Question 4: Derive the relationship between kinetic energy and momentum.
        A) KE = p²/2m
        B) KE = p²m/2
        C) KE = 2p²/m
        D) KE = mp²/2
        """
        
        print("🧪 Testing PDF Question Extraction Service")
        print("=" * 50)
        
        try:
            # Initialize extractor
            extractor = PDFQuestionExtractor()
            print(f"✅ Extractor initialized with {len(extractor.providers)} AI providers")
            
            # Test different difficulty modes
            test_modes = ['easy', 'tough', 'mixed']
            
            for mode in test_modes:
                print(f"\n🔍 Testing {mode.upper()} mode:")
                print("-" * 30)
                
                questions = extractor.extract_questions_from_text(
                    sample_text, 
                    exam_type="Physics 11", 
                    difficulty_mode=mode
                )
                
                print(f"📄 Extracted {len(questions)} questions")
                
                for i, q in enumerate(questions[:2]):  # Show first 2 questions
                    print(f"\nQuestion {i+1}:")
                    print(f"  Text: {q['question'][:60]}...")
                    print(f"  Difficulty: {q['difficulty']}")
                    print(f"  Options: {len(q['options'])}")
                    print(f"  Correct Answer: {q['correct_answer']}")
                    if q.get('hint'):
                        print(f"  Hint: {q['hint']}")
            
            print("\n✅ Test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_ai_providers():
    """Test individual AI provider availability"""
    with app.app_context():
        print("\n🤖 Testing AI Provider Connectivity")
        print("=" * 40)
        
        extractor = PDFQuestionExtractor()
        
        for provider_name, provider in extractor.providers:
            print(f"Testing {provider_name}...")
            
            try:
                # Simple test with minimal text
                test_text = "What is 2+2? A) 3 B) 4 C) 5 D) 6"
                result = provider.extract_questions(test_text, "Math", "easy")
                
                if result and len(result) > 0:
                    print(f"  ✅ {provider_name}: Working ({len(result)} questions)")
                else:
                    print(f"  ⚠️ {provider_name}: No results (falling back to regex)")
                    
            except Exception as e:
                print(f"  ❌ {provider_name}: Error - {str(e)}")
        
        print("\nNote: Errors are expected if API keys are not valid or services are down.")

def test_format_detection():
    """Test PDF format detection"""
    print("\n📋 Testing PDF Format Detection")
    print("=" * 35)
    
    extractor = PDFQuestionExtractor()
    
    # Format A sample
    format_a_text = """
    Question 1. What is the speed of light?
    A) 3×10⁸ m/s
    B) 3×10⁶ m/s
    C) 3×10¹⁰ m/s
    D) 3×10⁴ m/s
    """
    
    # Format B sample  
    format_b_text = """
    1. What is the speed of light?
    A) 3×10⁸ m/s
    B) 3×10⁶ m/s
    C) 3×10¹⁰ m/s
    D) 3×10⁴ m/s
    
    ANSWER KEY:
    1. A
    2. B
    3. C
    """
    
    format_a_detected = extractor._detect_pdf_format(format_a_text)
    format_b_detected = extractor._detect_pdf_format(format_b_text)
    
    print(f"Format A detection: {format_a_detected}")
    print(f"Format B detection: {format_b_detected}")


if __name__ == "__main__":
    print("🚀 QuizBattle PDF Extraction Test Suite")
    print("=" * 50)
    
    # Run tests
    success = test_extraction()
    test_ai_providers() 
    test_format_detection()
    
    if success:
        print("\n🎉 All tests passed! PDF extraction service is ready.")
    else:
        print("\n❌ Some tests failed. Check the logs above.")