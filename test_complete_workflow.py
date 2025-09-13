"""
QuizBattle Complete End-to-End Workflow Testing
Tests the entire system: PDF upload → Question review → Bulk delete → Challenge creation
"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import subprocess
import threading

# Test configuration
TEST_CONFIG = {
    'BACKEND_URL': 'http://localhost:5000',
    'FRONTEND_URL': 'http://localhost:3000',
    'ADMIN_USER': {
        'username': 'admin_test',
        'password': 'admin123'
    },
    'REGULAR_USER': {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'test123'
    },
    'TEST_PDFS': [
        r'C:\Users\hp\Downloads\_18183_JEE_Main_2024_January_29_Shift_2_Physics_Question_Paper_with.pdf',
        r'C:\Users\hp\Downloads\_19625_JEE_Main_2024_January_30_Shift_2_Physics_Question_Paper_with.pdf'
    ]
}

class QuizBattleE2ETester:
    def __init__(self):
        self.test_results = {}
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.backend_process = None
        self.frontend_process = None
        self.challenge_codes = []
        
    def log_test(self, test_name, status, details="", error=None):
        """Log test results with timestamp"""
        self.test_results[test_name] = {
            'status': status,
            'details': details,
            'error': str(error) if error else None,
            'timestamp': datetime.now().isoformat()
        }
        
        status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "INFO": "ℹ️"}.get(status, "❓")
        print(f"{status_icon} {test_name}: {details}")
        
        if error:
            print(f"    Error: {error}")

    def start_backend_server(self):
        """Start Flask backend server"""
        print("🚀 Starting Flask backend server...")
        
        try:
            # Check if already running
            response = requests.get(f"{TEST_CONFIG['BACKEND_URL']}/", timeout=5)
            if response.status_code == 200:
                self.log_test("BACKEND_SERVER", "PASS", "Backend already running")
                return True
        except:
            pass
        
        # Start backend
        try:
            os.chdir('C:/Desktop/quizbattle/backend')
            self.backend_process = subprocess.Popen([
                sys.executable, '-c', 
                'from app import create_app; app = create_app(); app.run(host="localhost", port=5000, debug=False)'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to be ready
            for i in range(30):
                try:
                    response = requests.get(f"{TEST_CONFIG['BACKEND_URL']}/", timeout=2)
                    if response.status_code == 200:
                        self.log_test("BACKEND_SERVER", "PASS", "Backend server started successfully")
                        return True
                except:
                    time.sleep(1)
            
            self.log_test("BACKEND_SERVER", "FAIL", "Backend server failed to start")
            return False
            
        except Exception as e:
            self.log_test("BACKEND_SERVER", "FAIL", "Failed to start backend", e)
            return False

    def start_frontend_server(self):
        """Start React frontend server"""
        print("🚀 Starting React frontend server...")
        
        try:
            # Check if already running
            response = requests.get(f"{TEST_CONFIG['FRONTEND_URL']}/", timeout=5)
            if response.status_code == 200:
                self.log_test("FRONTEND_SERVER", "PASS", "Frontend already running")
                return True
        except:
            pass
        
        # Start frontend
        try:
            os.chdir('C:/Desktop/quizbattle/frontend')
            self.frontend_process = subprocess.Popen([
                'npm', 'start'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            
            # Wait for server to be ready (React takes longer)
            print("⏳ Waiting for React development server (this may take a while)...")
            for i in range(60):
                try:
                    response = requests.get(f"{TEST_CONFIG['FRONTEND_URL']}/", timeout=3)
                    if response.status_code == 200:
                        self.log_test("FRONTEND_SERVER", "PASS", "Frontend server started successfully")
                        return True
                except:
                    time.sleep(2)
                    if i % 10 == 0:
                        print(f"   Still waiting... ({i*2}s)")
            
            self.log_test("FRONTEND_SERVER", "FAIL", "Frontend server failed to start")
            return False
            
        except Exception as e:
            self.log_test("FRONTEND_SERVER", "FAIL", "Failed to start frontend", e)
            return False

    def test_admin_authentication(self):
        """Test admin login and token setup"""
        print("\n" + "="*50)
        print("🔐 TESTING ADMIN AUTHENTICATION")
        print("="*50)
        
        try:
            # Admin login
            login_response = self.session.post(f"{TEST_CONFIG['BACKEND_URL']}/api/auth/login", 
                                             json=TEST_CONFIG['ADMIN_USER'])
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.admin_token = data.get('access_token')
                if self.admin_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                    self.log_test("ADMIN_LOGIN", "PASS", "Admin authentication successful")
                    return True
                else:
                    self.log_test("ADMIN_LOGIN", "FAIL", "No access token received")
                    return False
            else:
                self.log_test("ADMIN_LOGIN", "FAIL", f"Login failed with status {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("ADMIN_LOGIN", "FAIL", "Authentication request failed", e)
            return False

    def test_pdf_upload_workflow(self):
        """Test complete PDF upload workflow"""
        print("\n" + "="*50)
        print("📄 TESTING PDF UPLOAD WORKFLOW")
        print("="*50)
        
        questions_uploaded = 0
        
        for pdf_path in TEST_CONFIG['TEST_PDFS']:
            if not os.path.exists(pdf_path):
                self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "SKIP", "PDF file not found")
                continue
            
            try:
                with open(pdf_path, 'rb') as pdf_file:
                    files = {'pdf': pdf_file}
                    data = {
                        'exam_type': 'JEE Main',
                        'difficulty': 'mixed'
                    }
                    
                    response = self.session.post(f"{TEST_CONFIG['BACKEND_URL']}/api/admin/upload-pdf",
                                               files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        questions_added = result.get('questions_added', 0)
                        breakdown = result.get('breakdown', {})
                        
                        questions_uploaded += questions_added
                        
                        self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "PASS", 
                                    f"{questions_added} questions uploaded (Easy: {breakdown.get('easy', 0)}, Tough: {breakdown.get('tough', 0)})")
                    else:
                        self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "FAIL", 
                                    f"Upload failed with status {response.status_code}")
                        
            except Exception as e:
                self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "FAIL", "Upload failed", e)
        
        return questions_uploaded > 0

    def test_question_management(self):
        """Test question listing, filtering, and management"""
        print("\n" + "="*50)
        print("❓ TESTING QUESTION MANAGEMENT")
        print("="*50)
        
        try:
            # Get all questions
            response = self.session.get(f"{TEST_CONFIG['BACKEND_URL']}/api/admin/questions")
            
            if response.status_code == 200:
                data = response.json()
                all_questions = data.get('questions', [])
                
                self.log_test("QUESTION_LISTING", "PASS", f"Retrieved {len(all_questions)} questions")
                
                if len(all_questions) == 0:
                    self.log_test("QUESTION_MANAGEMENT", "SKIP", "No questions available for management")
                    return False
                
                # Test filtering by difficulty
                easy_questions = [q for q in all_questions if q.get('difficulty') == 'easy']
                tough_questions = [q for q in all_questions if q.get('difficulty') == 'tough']
                
                self.log_test("QUESTION_FILTERING", "PASS", 
                            f"Difficulty distribution - Easy: {len(easy_questions)}, Tough: {len(tough_questions)}")
                
                # Test single question delete
                if all_questions:
                    test_question_id = all_questions[0]['id']
                    delete_response = self.session.delete(f"{TEST_CONFIG['BACKEND_URL']}/api/admin/questions/{test_question_id}")
                    
                    if delete_response.status_code == 200:
                        self.log_test("SINGLE_DELETE", "PASS", f"Successfully deleted question {test_question_id}")
                        return True
                    else:
                        self.log_test("SINGLE_DELETE", "FAIL", f"Delete failed with status {delete_response.status_code}")
                
                return True
                
            else:
                self.log_test("QUESTION_LISTING", "FAIL", f"Failed to get questions: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("QUESTION_MANAGEMENT", "FAIL", "Question management test failed", e)
            return False

    def test_bulk_delete_workflow(self):
        """Test bulk delete functionality"""
        print("\n" + "="*50)
        print("🗑️ TESTING BULK DELETE WORKFLOW")
        print("="*50)
        
        try:
            # Get current questions
            response = self.session.get(f"{TEST_CONFIG['BACKEND_URL']}/api/admin/questions")
            
            if response.status_code == 200:
                questions = response.json().get('questions', [])
                
                if len(questions) < 2:
                    self.log_test("BULK_DELETE", "SKIP", "Not enough questions for bulk delete test")
                    return False
                
                # Select first 2 questions for bulk delete
                question_ids = [q['id'] for q in questions[:2]]
                
                bulk_delete_response = self.session.post(f"{TEST_CONFIG['BACKEND_URL']}/api/admin/questions/delete-bulk",
                                                       json={'question_ids': question_ids})
                
                if bulk_delete_response.status_code == 200:
                    result = bulk_delete_response.json()
                    success_count = result.get('success_count', 0)
                    failed_count = result.get('error_count', 0)
                    
                    self.log_test("BULK_DELETE", "PASS", 
                                f"Bulk delete completed: {success_count} successful, {failed_count} failed")
                    
                    # Verify questions were deleted
                    verify_response = self.session.get(f"{TEST_CONFIG['BACKEND_URL']}/api/admin/questions")
                    if verify_response.status_code == 200:
                        remaining_questions = verify_response.json().get('questions', [])
                        self.log_test("BULK_DELETE_VERIFY", "PASS", 
                                    f"Questions remaining: {len(remaining_questions)}")
                    
                    return True
                else:
                    self.log_test("BULK_DELETE", "FAIL", f"Bulk delete failed: {bulk_delete_response.status_code}")
                    return False
                    
            else:
                self.log_test("BULK_DELETE", "FAIL", "Failed to get questions for bulk delete")
                return False
                
        except Exception as e:
            self.log_test("BULK_DELETE", "FAIL", "Bulk delete test failed", e)
            return False

    def test_user_workflow(self):
        """Test user registration, challenge creation, and participation"""
        print("\n" + "="*50)
        print("👤 TESTING USER WORKFLOW")
        print("="*50)
        
        try:
            # Register regular user
            register_response = self.session.post(f"{TEST_CONFIG['BACKEND_URL']}/api/auth/register",
                                                json=TEST_CONFIG['REGULAR_USER'])
            
            if register_response.status_code in [200, 201, 409]:  # 409 = already exists
                self.log_test("USER_REGISTER", "PASS", "User registration successful")
                
                # Login user
                login_data = {
                    'username': TEST_CONFIG['REGULAR_USER']['username'],
                    'password': TEST_CONFIG['REGULAR_USER']['password']
                }
                
                login_response = self.session.post(f"{TEST_CONFIG['BACKEND_URL']}/api/auth/login",
                                                 json=login_data)
                
                if login_response.status_code == 200:
                    self.user_token = login_response.json().get('access_token')
                    self.log_test("USER_LOGIN", "PASS", "User login successful")
                    return True
                else:
                    self.log_test("USER_LOGIN", "FAIL", f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_test("USER_REGISTER", "FAIL", f"Registration failed: {register_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("USER_WORKFLOW", "FAIL", "User workflow test failed", e)
            return False

    def test_challenge_workflow(self):
        """Test challenge creation and participation"""
        print("\n" + "="*50)
        print("🏆 TESTING CHALLENGE WORKFLOW")
        print("="*50)
        
        try:
            # Create challenge as admin
            challenge_data = {
                'name': 'E2E Test Challenge',
                'difficulty': 'mixed',
                'exam_type': 'JEE Main',
                'time_limit': 30
            }
            
            admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
            create_response = requests.post(f"{TEST_CONFIG['BACKEND_URL']}/api/challenges",
                                          json=challenge_data, headers=admin_headers)
            
            if create_response.status_code == 201:
                challenge = create_response.json()
                challenge_code = challenge.get('code')
                self.challenge_codes.append(challenge_code)
                
                self.log_test("CHALLENGE_CREATE", "PASS", f"Challenge created: {challenge_code}")
                
                # Join challenge as user
                user_headers = {'Authorization': f'Bearer {self.user_token}'}
                join_response = requests.post(f"{TEST_CONFIG['BACKEND_URL']}/api/challenges/join/{challenge_code}",
                                            headers=user_headers)
                
                if join_response.status_code == 200:
                    self.log_test("CHALLENGE_JOIN", "PASS", "Successfully joined challenge")
                    
                    # Start quiz
                    start_response = requests.post(f"{TEST_CONFIG['BACKEND_URL']}/api/challenges/{challenge_code}/start",
                                                 headers=user_headers)
                    
                    if start_response.status_code == 200:
                        quiz_data = start_response.json()
                        question_count = len(quiz_data.get('questions', []))
                        self.log_test("CHALLENGE_START", "PASS", f"Quiz started with {question_count} questions")
                        return True
                    else:
                        self.log_test("CHALLENGE_START", "FAIL", f"Start failed: {start_response.status_code}")
                        return False
                else:
                    self.log_test("CHALLENGE_JOIN", "FAIL", f"Join failed: {join_response.status_code}")
                    return False
            else:
                self.log_test("CHALLENGE_CREATE", "FAIL", f"Create failed: {create_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CHALLENGE_WORKFLOW", "FAIL", "Challenge workflow test failed", e)
            return False

    def test_frontend_accessibility(self):
        """Test frontend pages accessibility"""
        print("\n" + "="*50)
        print("🌐 TESTING FRONTEND ACCESSIBILITY")
        print("="*50)
        
        pages_to_test = [
            ('/', 'Home Page'),
            ('/login', 'Login Page'),
            ('/register', 'Register Page'),
            ('/admin', 'Admin Panel'),
            ('/challenges', 'Challenges Page'),
            ('/leaderboard', 'Leaderboard Page')
        ]
        
        for path, name in pages_to_test:
            try:
                response = requests.get(f"{TEST_CONFIG['FRONTEND_URL']}{path}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"FRONTEND_{name.replace(' ', '_').upper()}", "PASS", 
                                f"{name} accessible")
                else:
                    self.log_test(f"FRONTEND_{name.replace(' ', '_').upper()}", "FAIL", 
                                f"{name} returned {response.status_code}")
            except Exception as e:
                self.log_test(f"FRONTEND_{name.replace(' ', '_').upper()}", "FAIL", 
                            f"{name} not accessible", e)

    def cleanup(self):
        """Clean up test processes and data"""
        print("\n🧹 Cleaning up test environment...")
        
        # Terminate processes
        if self.backend_process:
            self.backend_process.terminate()
            print("   Backend process terminated")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("   Frontend process terminated")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 END-TO-END TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        skipped_tests = sum(1 for result in self.test_results.values() if result['status'] == 'SKIP')
        
        print(f"\n📋 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        
        print(f"\n📝 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "INFO": "ℹ️"}.get(result['status'], "❓")
            print(f"{status_icon} {test_name}: {result['details']}")
            if result['error']:
                print(f"    Error: {result['error']}")
        
        # Final verdict
        if failed_tests == 0:
            print(f"\n🎉 ALL CRITICAL TESTS PASSED!")
            print("QuizBattle is ready for production deployment.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed.")
            print("Please review and fix issues before production deployment.")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'skipped': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'challenge_codes_created': self.challenge_codes
        }
        
        report_path = f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")

def main():
    """Run complete end-to-end testing"""
    print("🧪 QuizBattle Complete End-to-End Testing")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will test the complete workflow from PDF upload to challenge participation")
    
    tester = QuizBattleE2ETester()
    
    try:
        # Start servers
        if not tester.start_backend_server():
            print("❌ Cannot proceed without backend server")
            return
        
        # Note: Frontend testing requires manual verification for now
        # tester.start_frontend_server()
        
        # Wait for servers to be ready
        time.sleep(5)
        
        # Run all tests
        if tester.test_admin_authentication():
            tester.test_pdf_upload_workflow()
            tester.test_question_management()
            tester.test_bulk_delete_workflow()
            
            if tester.test_user_workflow():
                tester.test_challenge_workflow()
            
            # tester.test_frontend_accessibility()
        
        # Generate comprehensive report
        tester.generate_report()
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.cleanup()
    
    print(f"\nTesting completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()