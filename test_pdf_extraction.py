"""
QuizBattle PDF Extraction Testing Script
Tests the PDF extractor with real JEE papers and validates output quality
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Test configuration
TEST_PDFS = [
    r'C:\Users\hp\Downloads\_18183_JEE_Main_2024_January_29_Shift_2_Physics_Question_Paper_with.pdf',
    r'C:\Users\hp\Downloads\_19625_JEE_Main_2024_January_30_Shift_2_Physics_Question_Paper_with.pdf'
]

class PDFExtractionTester:
    def __init__(self):
        self.test_results = {}
        self.issues_found = []
        self.fixes_applied = []
        
    def log_test(self, test_name, status, details="", issues=None):
        """Log test results"""
        self.test_results[test_name] = {
            'status': status,
            'details': details,
            'issues': issues or [],
            'timestamp': datetime.now().isoformat()
        }
        
        status_icon = "✅" if status == "PASS" else ("⚠️" if status == "WARN" else "❌")
        print(f"{status_icon} {test_name}: {details}")
        
        if issues:
            print(f"   Issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"   - {issue}")
            if len(issues) > 3:
                print(f"   ... and {len(issues) - 3} more issues")
            
            self.issues_found.extend(issues)

    def test_pdf_extraction(self):
        """Test PDF extraction with comprehensive analysis"""
        print("🧪 TESTING PDF EXTRACTION WITH REAL JEE PAPERS")
        print("=" * 60)
        
        # Initialize Flask app context
        from app import create_app
        app = create_app()
        
        with app.app_context():
            try:
                from app.services.pdf_extractor import get_extractor
                from PyPDF2 import PdfReader
                
                for pdf_path in TEST_PDFS:
                    if not os.path.exists(pdf_path):
                        print(f"⏭️ Skipping {Path(pdf_path).name} - file not found")
                        continue
                    
                    print(f"\n📄 Testing PDF: {Path(pdf_path).name}")
                    
                    # Test PDF reading
                    try:
                        reader = PdfReader(pdf_path)
                        total_pages = len(reader.pages)
                        
                        # Extract text from all pages
                        raw_text = ""
                        for page_num, page in enumerate(reader.pages):
                            page_text = page.extract_text()
                            raw_text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
                        
                        print(f"   📖 PDF Reading: {total_pages} pages, {len(raw_text)} characters")
                        
                        # Save raw text for analysis
                        raw_text_path = f"raw_text_{Path(pdf_path).stem}.txt"
                        with open(raw_text_path, 'w', encoding='utf-8') as f:
                            f.write(raw_text)
                        print(f"   📝 Raw text saved to: {raw_text_path}")
                        
                    except Exception as e:
                        self.log_test(f"PDF_READ_{Path(pdf_path).name}", "FAIL", 
                                    f"Failed to read PDF: {str(e)}")
                        continue
                    
                    # Test extraction with different difficulty modes
                    for difficulty in ['easy', 'tough', 'mixed']:
                        print(f"\n  🎯 Testing difficulty mode: {difficulty}")
                        
                        try:
                            extractor = get_extractor()
                            questions = extractor.extract_questions_from_text(raw_text, "JEE Main", difficulty)
                            
                            if not questions:
                                self.log_test(f"EXTRACT_{Path(pdf_path).name}_{difficulty}", "FAIL", 
                                            "No questions extracted")
                                continue
                            
                            # Comprehensive analysis
                            issues = self._analyze_extracted_questions(questions, difficulty)
                            
                            # Generate test result
                            total_questions = len(questions)
                            easy_questions = sum(1 for q in questions if q.get('difficulty') == 'easy')
                            tough_questions = sum(1 for q in questions if q.get('difficulty') == 'tough')
                            
                            if len(issues) == 0:
                                status = "PASS"
                            elif len(issues) <= total_questions * 0.1:  # Less than 10% issues
                                status = "WARN"
                            else:
                                status = "FAIL"
                            
                            details = f"{total_questions} questions ({easy_questions} easy, {tough_questions} tough)"
                            
                            self.log_test(f"EXTRACT_{Path(pdf_path).name}_{difficulty}", status, details, issues)
                            
                            # Save extracted questions for manual review
                            output_path = f"extracted_{Path(pdf_path).stem}_{difficulty}.json"
                            with open(output_path, 'w', encoding='utf-8') as f:
                                json.dump({
                                    'pdf_name': Path(pdf_path).name,
                                    'difficulty_mode': difficulty,
                                    'total_questions': total_questions,
                                    'questions': questions,
                                    'analysis': {
                                        'easy_count': easy_questions,
                                        'tough_count': tough_questions,
                                        'issues_found': issues
                                    }
                                }, f, indent=2, ensure_ascii=False)
                            
                            print(f"     💾 Questions saved to: {output_path}")
                            
                        except Exception as e:
                            self.log_test(f"EXTRACT_{Path(pdf_path).name}_{difficulty}", "FAIL",
                                        f"Extraction failed: {str(e)}")
            
            except ImportError as e:
                print(f"❌ Failed to import required modules: {e}")
                return
            except Exception as e:
                print(f"❌ Unexpected error in PDF extraction testing: {e}")
                import traceback
                traceback.print_exc()

    def _analyze_extracted_questions(self, questions, difficulty_mode):
        """Comprehensive analysis of extracted questions"""
        issues = []
        
        for i, question in enumerate(questions):
            q_num = i + 1
            
            # Check question text quality
            question_text = question.get('question', '')
            if len(question_text.strip()) < 10:
                issues.append(f"Q{q_num}: Question text too short ({len(question_text)} chars)")
            
            # Check for ads/unwanted content in question
            unwanted_patterns = ['download', 'www.', 'visit', 'app store', 'play store', 'subscribe']
            for pattern in unwanted_patterns:
                if pattern in question_text.lower():
                    issues.append(f"Q{q_num}: Question contains ads/unwanted content: '{pattern}'")
            
            # Check options
            options = question.get('options', [])
            if len(options) != 4:
                issues.append(f"Q{q_num}: Invalid number of options ({len(options)}, expected 4)")
                continue
            
            # Check each option quality
            for j, option in enumerate(options):
                option_letter = chr(ord('a') + j)
                
                if not option or len(option.strip()) < 1:
                    issues.append(f"Q{q_num} option {option_letter}: Empty or too short")
                    continue
                
                # Check for ads in options
                for pattern in unwanted_patterns:
                    if pattern in option.lower():
                        issues.append(f"Q{q_num} option {option_letter}: Contains ads: '{pattern}'")
                
                # Check for merged content (next question leaked in)
                if 'Question' in option and ':' in option:
                    issues.append(f"Q{q_num} option {option_letter}: Contains merged next question")
                
                # Check for option markers that weren't cleaned
                if option.strip().startswith(('(a)', '(b)', '(c)', '(d)', 'A)', 'B)', 'C)', 'D)')):
                    issues.append(f"Q{q_num} option {option_letter}: Option marker not cleaned: '{option[:20]}...'")
            
            # Check answer validity
            correct_answer = question.get('correct_answer')
            if not isinstance(correct_answer, int) or not (0 <= correct_answer <= 3):
                issues.append(f"Q{q_num}: Invalid answer index ({correct_answer})")
            
            # Check difficulty assignment
            assigned_difficulty = question.get('difficulty')
            if assigned_difficulty not in ['easy', 'tough']:
                issues.append(f"Q{q_num}: Invalid difficulty '{assigned_difficulty}'")
            
            # For mixed mode, check if we have both easy and tough questions
            if difficulty_mode == 'mixed':
                # This will be checked at the end
                pass
        
        # Check overall difficulty distribution for mixed mode
        if difficulty_mode == 'mixed' and len(questions) >= 4:
            easy_count = sum(1 for q in questions if q.get('difficulty') == 'easy')
            tough_count = sum(1 for q in questions if q.get('difficulty') == 'tough')
            
            if easy_count == 0:
                issues.append("Mixed mode: No easy questions found")
            if tough_count == 0:
                issues.append("Mixed mode: No tough questions found")
            
            # Check ratio (should be roughly balanced)
            total = easy_count + tough_count
            if total > 0:
                easy_ratio = easy_count / total
                if easy_ratio < 0.2 or easy_ratio > 0.8:
                    issues.append(f"Mixed mode: Imbalanced difficulty ratio (easy: {easy_ratio:.1%})")
        
        return issues

    def check_for_pattern_issues(self):
        """Check raw text patterns that might cause extraction issues"""
        print("\n🔍 ANALYZING RAW TEXT PATTERNS")
        print("-" * 40)
        
        for pdf_path in TEST_PDFS:
            if not os.path.exists(pdf_path):
                continue
            
            print(f"\n📄 Analyzing: {Path(pdf_path).name}")
            
            raw_text_path = f"raw_text_{Path(pdf_path).stem}.txt"
            if os.path.exists(raw_text_path):
                with open(raw_text_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Look for common patterns
                patterns_to_check = {
                    'Question patterns': [r'Question \d+:', r'Q\.\d+', r'\d+\.\s'],
                    'Option patterns': [r'\([a-d]\)', r'[A-D]\)', r'\([A-D]\)', r'[a-d]\)'],
                    'Answer patterns': [r'Answer:\s*\([a-d]\)', r'Ans:\s*[a-d]', r'Answer\s*[a-d]'],
                    'Ad patterns': [r'download', r'www\.', r'visit', r'app'],
                    'Page markers': [r'Page \d+', r'P\.T\.O', r'--- PAGE \d+ ---']
                }
                
                import re
                for pattern_group, patterns in patterns_to_check.items():
                    print(f"  {pattern_group}:")
                    for pattern in patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        print(f"    '{pattern}': {len(matches)} matches")
                
                # Sample some question-like text
                question_matches = re.findall(r'Question \d+:.*?(?=Question \d+:|$)', text, re.DOTALL | re.IGNORECASE)
                if question_matches:
                    print(f"\n  📝 Sample question found:")
                    sample = question_matches[0][:200] + "..." if len(question_matches[0]) > 200 else question_matches[0]
                    print(f"    {sample}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 PDF EXTRACTION TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        warned_tests = sum(1 for result in self.test_results.values() if result['status'] == 'WARN')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        
        print(f"\n📋 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"⚠️ Warnings: {warned_tests}")
        print(f"❌ Failed: {failed_tests}")
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        
        print(f"\n📝 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(result['status'], "❓")
            print(f"{status_icon} {test_name}: {result['details']}")
            
            if result.get('issues'):
                print(f"    Issues ({len(result['issues'])}):")
                for issue in result['issues'][:3]:  # Show first 3
                    print(f"      - {issue}")
                if len(result['issues']) > 3:
                    print(f"      ... and {len(result['issues']) - 3} more")
        
        # Summary of most common issues
        if self.issues_found:
            print(f"\n🐛 MOST COMMON ISSUES:")
            
            # Group similar issues
            issue_types = {}
            for issue in self.issues_found:
                # Extract issue type
                if ': ' in issue:
                    issue_type = issue.split(': ', 1)[1].split(' ')[0:3]
                    issue_type = ' '.join(issue_type)
                    issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            # Show top 5 issue types
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {count}x {issue_type}")
        
        # Final status and recommendations
        if failed_tests == 0 and warned_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! PDF extraction is working perfectly.")
        elif failed_tests == 0:
            print(f"\n✅ All tests passed with minor warnings. Extraction is functional.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Issues need to be addressed:")
            
            if any('No questions extracted' in str(result.get('details', '')) for result in self.test_results.values()):
                print("  - Extractor is not finding questions in PDF text")
                print("  - Check regex patterns and AI prompt")
            
            if any('ads' in issue.lower() for issue in self.issues_found):
                print("  - Ad content not being properly cleaned from options")
                print("  - Enhance _clean_option_text method")
            
            if any('invalid answer' in issue.lower() for issue in self.issues_found):
                print("  - Answer mapping not working correctly")
                print("  - Check answer extraction regex patterns")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'warned': warned_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'issues_found': self.issues_found
        }
        
        report_path = f"pdf_extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_path}")

def main():
    """Run PDF extraction testing"""
    print("🧪 QuizBattle PDF Extraction Testing & Validation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = PDFExtractionTester()
    
    try:
        # Test PDF extraction
        tester.test_pdf_extraction()
        
        # Analyze patterns in raw text
        tester.check_for_pattern_issues()
        
        # Generate comprehensive report
        tester.generate_report()
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nTesting completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()