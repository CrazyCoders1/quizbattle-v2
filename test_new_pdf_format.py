"""
Test script for new PDF format integration
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from app.services.openrouter_pdf_extractor import get_openrouter_extractor
from app.services.pdf_extractor import get_extractor

# Sample NEW FORMAT PDF content
NEW_FORMAT_SAMPLE = """
Question: Two polarisers A and B are kept one after the other. Their pass axis makes an 
angle of 45 with each other. An unpolarized light of intensity I0 strikes A first and then B. 
Find the intensity of the light emergent from B. 
Options:
(a) I0/2 
(b) I0/4 
(c) I0/8 
(d) I0/6 
Answer: (b)

Question: Simple pendulum of length 'l = 4' is taken to height 'R' above earth surface 
calculate time period at its height {R → Radius of Earth & Taken π2 = g}
Options:
(a) 4 sec
(b) 8 sec
(c) 2 sec
(d) 10 sec 
Answer: (b)

Question: What is the unit of force?
Options:
(a) Newton
(b) Joule
(c) Watt
(d) Pascal
Answer: (a)
"""

# Sample with numeric question (should be skipped)
NUMERIC_SAMPLE = """
Question: Calculate the value of 5 + 3 × 2
Options:
(a) 16
(b) 11
(c) 10
(d) 13
Answer: (b)

Question: What is the principle of superposition?
Options:
(a) Waves add algebraically
(b) Waves multiply
(c) Waves cancel out
(d) Waves remain separate
Answer: (a)
"""

# Sample with match-the-following (should be skipped)
MATCH_SAMPLE = """
Question: Match the following Column A with Column B
Options:
(a) A-1, B-2, C-3
(b) A-2, B-1, C-3
(c) A-3, B-2, C-1
(d) A-1, B-3, C-2
Answer: (a)

Question: Which law governs electromagnetic induction?
Options:
(a) Faraday's law
(b) Newton's law
(c) Ohm's law
(d) Coulomb's law
Answer: (a)
"""

def test_new_pdf_format():
    """Test new PDF format with Flask context"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Testing NEW PDF Format Integration")
        print("=" * 60)
        
        # Test 1: Format Detection
        print("\n1. Testing PDF Format Detection")
        extractor = get_openrouter_extractor()
        
        pdf_format = extractor._detect_pdf_format(NEW_FORMAT_SAMPLE)
        print(f"   📋 Detected format: {pdf_format}")
        
        if pdf_format == 'New_Format':
            print("   ✅ NEW format correctly detected")
        else:
            print("   ❌ Format detection failed")
            return False
        
        # Test 2: OpenRouter AI Extraction
        print("\n2. Testing AI Extraction (OpenRouter)")
        try:
            ai_questions = extractor.extract_questions_from_text(
                NEW_FORMAT_SAMPLE, "Physics", "mixed"
            )
            
            print(f"   📊 AI extracted: {len(ai_questions)} questions")
            
            if ai_questions:
                print("   ✅ AI extraction successful")
                for i, q in enumerate(ai_questions):
                    print(f"   📝 Q{i+1}: {q['question'][:50]}...")
                    print(f"      🎯 Difficulty: {q['difficulty']}")
                    print(f"      💡 Hint: {'Yes' if q.get('hint') else 'No'}")
                    print(f"      🔧 Method: {q['extraction_method']}")
                    print(f"      ✅ Answer: {q['correct_answer']} ({q['options'][q['correct_answer']]})")
            else:
                print("   ⚠️ AI extraction returned no questions")
                
        except Exception as e:
            print(f"   ❌ AI extraction failed: {e}")
            ai_questions = []
        
        # Test 3: Regex Fallback
        print("\n3. Testing Regex Fallback")
        try:
            regex_questions = extractor._extract_with_regex(
                NEW_FORMAT_SAMPLE, "Physics", "mixed", "New_Format"
            )
            
            print(f"   📊 Regex extracted: {len(regex_questions)} questions")
            
            if regex_questions:
                print("   ✅ Regex fallback working")
                for i, q in enumerate(regex_questions):
                    print(f"   📝 Q{i+1}: {q['question'][:50]}...")
                    print(f"      🎯 Difficulty: {q['difficulty']}")
                    print(f"      💡 Hint: {'Yes' if q.get('hint') else 'No'}")
                    print(f"      🔧 Method: {q['extraction_method']}")
                    print(f"      ✅ Answer: {q['correct_answer']} ({q['options'][q['correct_answer']]})")
            else:
                print("   ❌ Regex fallback failed")
                
        except Exception as e:
            print(f"   ❌ Regex fallback error: {e}")
            regex_questions = []
        
        # Test 4: Question Filtering (Skip numeric/match questions)
        print("\n4. Testing Question Filtering")
        
        # Test numeric question filtering
        numeric_result = extractor._extract_new_format_regex(NUMERIC_SAMPLE, "Math", "easy")
        print(f"   📊 Numeric sample: {len(numeric_result)} questions (should skip numeric)")
        if len(numeric_result) == 1:  # Should only get the valid question
            print("   ✅ Numeric questions correctly filtered")
        else:
            print("   ⚠️ Numeric filtering may need adjustment")
        
        # Test match-the-following filtering
        match_result = extractor._extract_new_format_regex(MATCH_SAMPLE, "General", "easy")
        print(f"   📊 Match sample: {len(match_result)} questions (should skip match type)")
        if len(match_result) == 1:  # Should only get the valid question
            print("   ✅ Match questions correctly filtered")
        else:
            print("   ⚠️ Match filtering may need adjustment")
        
        # Test 5: Difficulty Assignment
        print("\n5. Testing Difficulty Assignment")
        
        # Easy mode
        easy_questions = extractor.extract_questions_from_text(NEW_FORMAT_SAMPLE, "Physics", "easy")
        easy_count = sum(1 for q in easy_questions if q['difficulty'] == 'easy')
        tough_count = sum(1 for q in easy_questions if q['difficulty'] == 'tough')
        print(f"   📈 Easy mode - Easy: {easy_count}, Tough: {tough_count}")
        
        # Tough mode
        tough_questions = extractor.extract_questions_from_text(NEW_FORMAT_SAMPLE, "Physics", "tough")
        tough_only = sum(1 for q in tough_questions if q['difficulty'] == 'tough')
        print(f"   📈 Tough mode - All tough: {tough_only}/{len(tough_questions)}")
        
        # Test 6: Main Extractor Integration
        print("\n6. Testing Main Extractor Integration")
        main_extractor = get_extractor()
        main_questions = main_extractor.extract_questions_from_text(
            NEW_FORMAT_SAMPLE, "Physics", "mixed"
        )
        
        print(f"   📊 Main extractor: {len(main_questions)} questions")
        if main_questions:
            print("   ✅ Main extractor integration working")
            
            # Check database compatibility
            sample_q = main_questions[0]
            required_fields = ['question', 'options', 'correct_answer', 'difficulty', 'hint', 'exam_type']
            missing_fields = [field for field in required_fields if field not in sample_q]
            
            if not missing_fields:
                print("   ✅ Database schema compatible")
            else:
                print(f"   ❌ Missing fields: {missing_fields}")
        
        # Results Summary
        print(f"\n📋 INTEGRATION TEST SUMMARY")
        print(f"   Format Detection: {'✅' if pdf_format == 'New_Format' else '❌'}")
        print(f"   AI Extraction: {'✅' if len(ai_questions) > 0 else '❌'}")
        print(f"   Regex Fallback: {'✅' if len(regex_questions) > 0 else '❌'}")
        print(f"   Question Filtering: {'✅' if len(numeric_result) == 1 and len(match_result) == 1 else '❌'}")
        print(f"   Main Integration: {'✅' if len(main_questions) > 0 else '❌'}")
        
        success = (pdf_format == 'New_Format' and 
                  (len(ai_questions) > 0 or len(regex_questions) > 0) and
                  len(main_questions) > 0)
        
        print(f"   🎯 Overall Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        return success

if __name__ == "__main__":
    success = test_new_pdf_format()
    print(f"\n{'=' * 60}")
    print(f"{'✅ NEW PDF FORMAT INTEGRATION SUCCESSFUL!' if success else '❌ INTEGRATION TEST FAILED!'}")
    sys.exit(0 if success else 1)