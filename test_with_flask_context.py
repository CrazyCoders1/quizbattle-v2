"""
OpenRouter PDF Extraction Test with Flask Context
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from app.services.openrouter_pdf_extractor import get_openrouter_extractor
from app.services.pdf_extractor import get_extractor

# Sample text
SAMPLE_TEXT = """
CBSE Class 11 Physics Mock Test

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

Answer Key: 1-A, 2-B
"""

def test_openrouter_integration():
    """Test OpenRouter integration within Flask context"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Testing OpenRouter Integration with Flask Context")
        print("=" * 60)
        
        try:
            # Test 1: Initialize OpenRouter
            print("\n1. Testing OpenRouter Initialization")
            extractor = get_openrouter_extractor()
            
            if extractor.openrouter:
                print(f"✅ OpenRouter initialized with {len(extractor.openrouter.MODELS)} models")
                print(f"   API key loaded: {'Yes' if 'OpenRouter' in extractor.api_keys else 'No'}")
                print(f"   First 3 models: {extractor.openrouter.MODELS[:3]}")
            else:
                print("❌ OpenRouter not initialized")
                return False
            
            # Test 2: Basic extraction
            print("\n2. Testing Basic Question Extraction")
            questions = extractor.extract_questions_from_text(
                SAMPLE_TEXT, "CBSE 11 Physics", "mixed"
            )
            
            print(f"   📊 Questions extracted: {len(questions)}")
            
            if questions:
                print("   ✅ Extraction successful!")
                first_q = questions[0]
                print(f"   📝 Sample question: {first_q['question'][:60]}...")
                print(f"   🎯 Difficulty: {first_q.get('difficulty', 'N/A')}")
                print(f"   🔧 Method: {first_q.get('extraction_method', 'N/A')}")
                
                # Show all extraction methods used
                methods = {}
                for q in questions:
                    method = q.get('extraction_method', 'unknown')
                    methods[method] = methods.get(method, 0) + 1
                
                print(f"   🔍 Methods used:")
                for method, count in methods.items():
                    print(f"      {method}: {count} questions")
            else:
                print("   ⚠️ No questions extracted")
            
            # Test 3: Main extractor integration
            print("\n3. Testing Main Extractor Integration")
            main_extractor = get_extractor()
            main_questions = main_extractor.extract_questions_from_text(
                SAMPLE_TEXT, "CBSE 11 Physics", "mixed"
            )
            
            print(f"   📊 Main extractor questions: {len(main_questions)}")
            
            if main_questions:
                print("   ✅ Main extractor working!")
                methods = {}
                for q in main_questions:
                    method = q.get('extraction_method', 'unknown')
                    methods[method] = methods.get(method, 0) + 1
                
                print(f"   🔍 Methods used:")
                for method, count in methods.items():
                    print(f"      {method}: {count} questions")
            else:
                print("   ⚠️ Main extractor returned no questions")
            
            # Results
            print(f"\n📋 RESULTS SUMMARY")
            print(f"   OpenRouter Direct: {len(questions)} questions")
            print(f"   Main Extractor: {len(main_questions)} questions")
            
            success = len(questions) > 0 or len(main_questions) > 0
            print(f"   🎯 Overall: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
            return success
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_openrouter_integration()
    print(f"\n{'✅ Integration test passed!' if success else '❌ Integration test failed!'}")
    sys.exit(0 if success else 1)