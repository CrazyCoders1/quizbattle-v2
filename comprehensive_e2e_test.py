"""
QuizBattle Comprehensive End-to-End Testing Suite
Tests all user features, admin features, and system performance
"""
import asyncio
import aiohttp
import requests
import json
import time
import threading
import concurrent.futures
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import subprocess
import random
import string

# Add backend to path for direct testing
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

class QuizBattleE2ETester:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.frontend_url = 'http://localhost:3000'
        self.session = requests.Session()
        self.test_results = {}
        self.issues_found = []
        self.admin_token = None
        self.user_tokens = []
        self.challenge_codes = []
        self.test_users = []
        
        # Test configuration
        self.admin_creds = {'username': 'admin_test', 'password': 'admin123'}
        self.concurrent_users = 50
        
    def log_test(self, test_name, status, details="", error=None, screenshot_path=None):
        """Log test results with timestamp and optional error details"""
        self.test_results[test_name] = {
            'status': status,
            'details': details,
            'error': str(error) if error else None,
            'timestamp': datetime.now().isoformat(),
            'screenshot': screenshot_path
        }
        
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(status, "❓")
        print(f"{status_icon} {test_name}: {details}")
        
        if error:
            print(f"    Error: {error}")
            self.issues_found.append({
                'test': test_name,
                'error': str(error),
                'details': details,
                'timestamp': datetime.now().isoformat()
            })
        
        if screenshot_path:
            print(f"    Screenshot: {screenshot_path}")

    def start_backend_server(self):
        """Start Flask backend server for testing"""
        print("🚀 Starting Flask backend server...")
        
        try:
            # Check if already running
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("BACKEND_SERVER", "PASS", "Backend already running")
                return True
        except:
            pass
        
        # Start backend in development mode for testing
        try:
            os.chdir('C:/Desktop/quizbattle/backend')
            self.backend_process = subprocess.Popen([
                sys.executable, '-c', 
                'from app import create_app; app = create_app(); app.run(host="localhost", port=5000, debug=False)'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            # Wait for server to be ready
            for i in range(30):
                try:
                    response = requests.get(f"{self.base_url}/", timeout=2)
                    if response.status_code == 200:
                        self.log_test("BACKEND_SERVER", "PASS", "Backend server started successfully")
                        return True
                except:
                    time.sleep(1)
            
            self.log_test("BACKEND_SERVER", "FAIL", "Backend server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            self.log_test("BACKEND_SERVER", "FAIL", "Failed to start backend", e)
            return False

    # =================== USER FEATURE TESTS ===================
    
    def test_user_authentication_flow(self):
        """Test complete user registration, login, logout flow"""
        print("\n" + "="*60)
        print("👤 TESTING USER AUTHENTICATION FLOW")
        print("="*60)
        
        # Generate unique test user
        username = f"testuser_{int(time.time())}"
        email = f"{username}@test.com"
        password = "testpass123"
        
        try:
            # Test user registration
            register_data = {
                'username': username,
                'email': email,
                'password': password
            }
            
            register_response = self.session.post(f"{self.base_url}/api/auth/register", 
                                                json=register_data)
            
            if register_response.status_code in [200, 201]:
                self.log_test("USER_REGISTER", "PASS", f"User {username} registered successfully")
            else:
                self.log_test("USER_REGISTER", "FAIL", 
                            f"Registration failed: {register_response.status_code}", 
                            register_response.text)
                return False
            
            # Test user login
            login_data = {'username': username, 'password': password}
            login_response = self.session.post(f"{self.base_url}/api/auth/login", 
                                             json=login_data)
            
            if login_response.status_code == 200:
                user_data = login_response.json()
                user_token = user_data.get('access_token')
                if user_token:
                    self.log_test("USER_LOGIN", "PASS", "User login successful, JWT token received")
                    
                    # Test JWT token validation
                    headers = {'Authorization': f'Bearer {user_token}'}
                    profile_response = self.session.get(f"{self.base_url}/api/auth/profile", 
                                                      headers=headers)
                    
                    if profile_response.status_code == 200:
                        self.log_test("JWT_VALIDATION", "PASS", "JWT token validation successful")
                        
                        # Store user for later tests
                        self.test_users.append({
                            'username': username,
                            'token': user_token,
                            'headers': headers
                        })
                        
                        # Test logout (token invalidation)
                        logout_response = self.session.post(f"{self.base_url}/api/auth/logout", 
                                                          headers=headers)
                        
                        # After logout, token should be invalid
                        profile_response_after_logout = self.session.get(f"{self.base_url}/api/auth/profile", 
                                                                        headers=headers)
                        
                        if profile_response_after_logout.status_code == 401:
                            self.log_test("USER_LOGOUT", "PASS", "Logout successful, token invalidated")
                        else:
                            self.log_test("USER_LOGOUT", "WARN", 
                                        "Logout response unclear, token still seems valid")
                        
                        return True
                    else:
                        self.log_test("JWT_VALIDATION", "FAIL", 
                                    f"JWT validation failed: {profile_response.status_code}")
                        return False
                else:
                    self.log_test("USER_LOGIN", "FAIL", "No JWT token received in login response")
                    return False
            else:
                self.log_test("USER_LOGIN", "FAIL", 
                            f"Login failed: {login_response.status_code}", 
                            login_response.text)
                return False
                
        except Exception as e:
            self.log_test("USER_AUTH_FLOW", "FAIL", "Authentication flow test failed", e)
            return False

    def test_challenge_join_and_participation(self):
        """Test challenge joining by code and full participation flow"""
        print("\n" + "="*60)
        print("🎯 TESTING CHALLENGE JOIN & PARTICIPATION")
        print("="*60)
        
        try:
            # First login as admin to create a challenge
            admin_login = self.session.post(f"{self.base_url}/api/auth/login", 
                                          json=self.admin_creds)
            
            if admin_login.status_code != 200:
                self.log_test("ADMIN_LOGIN_FOR_CHALLENGE", "FAIL", "Could not login as admin")
                return False
                
            admin_token = admin_login.json().get('access_token')
            admin_headers = {'Authorization': f'Bearer {admin_token}'}
            
            # Create a test challenge
            challenge_data = {
                'name': 'E2E Test Challenge',
                'difficulty': 'mixed',
                'exam_type': 'JEE Main',
                'time_limit': 10  # 10 minutes for testing
            }
            
            challenge_response = self.session.post(f"{self.base_url}/api/challenges", 
                                                 json=challenge_data, headers=admin_headers)
            
            if challenge_response.status_code == 201:
                challenge = challenge_response.json()
                challenge_code = challenge.get('code')
                self.challenge_codes.append(challenge_code)
                self.log_test("CHALLENGE_CREATE", "PASS", f"Challenge created: {challenge_code}")
                
                # Test joining challenge with code
                if self.test_users:
                    user = self.test_users[0]
                    join_response = self.session.post(f"{self.base_url}/api/challenges/join/{challenge_code}",
                                                    headers=user['headers'])
                    
                    if join_response.status_code == 200:
                        self.log_test("CHALLENGE_JOIN", "PASS", "Successfully joined challenge by code")
                        
                        # Test starting the quiz
                        start_response = self.session.post(f"{self.base_url}/api/challenges/{challenge_code}/start",
                                                         headers=user['headers'])
                        
                        if start_response.status_code == 200:
                            quiz_data = start_response.json()
                            questions = quiz_data.get('questions', [])
                            
                            if questions:
                                self.log_test("QUIZ_START", "PASS", 
                                            f"Quiz started successfully with {len(questions)} questions")
                                
                                # Test quiz submission with scoring rules
                                answers = []
                                correct_count = 0
                                
                                for i, question in enumerate(questions):
                                    # Simulate answering (50% correct for realistic testing)
                                    if i % 2 == 0:
                                        # Correct answer
                                        answers.append({
                                            'question_id': question.get('id'),
                                            'selected_answer': question.get('correct_answer')
                                        })
                                        correct_count += 1
                                    else:
                                        # Wrong answer
                                        wrong_answer = (question.get('correct_answer', 0) + 1) % 4
                                        answers.append({
                                            'question_id': question.get('id'),
                                            'selected_answer': wrong_answer
                                        })
                                
                                # Submit quiz
                                submission_data = {
                                    'answers': answers,
                                    'time_taken': 300  # 5 minutes
                                }
                                
                                submit_response = self.session.post(
                                    f"{self.base_url}/api/challenges/{challenge_code}/submit",
                                    json=submission_data, headers=user['headers'])
                                
                                if submit_response.status_code == 200:
                                    result = submit_response.json()
                                    score = result.get('score', 0)
                                    
                                    # Verify JEE scoring rules (+4 for correct, -1 for wrong)
                                    wrong_count = len(questions) - correct_count
                                    expected_score = (correct_count * 4) - (wrong_count * 1)
                                    
                                    if score == expected_score:
                                        self.log_test("SCORING_RULES", "PASS", 
                                                    f"JEE scoring rules working correctly: {score} points")
                                    else:
                                        self.log_test("SCORING_RULES", "FAIL", 
                                                    f"Scoring mismatch. Expected: {expected_score}, Got: {score}")
                                    
                                    self.log_test("QUIZ_SUBMIT", "PASS", "Quiz submission successful")
                                    return True
                                else:
                                    self.log_test("QUIZ_SUBMIT", "FAIL", 
                                                f"Quiz submission failed: {submit_response.status_code}")
                                    return False
                            else:
                                self.log_test("QUIZ_START", "FAIL", "No questions received in quiz")
                                return False
                        else:
                            self.log_test("QUIZ_START", "FAIL", 
                                        f"Quiz start failed: {start_response.status_code}")
                            return False
                    else:
                        self.log_test("CHALLENGE_JOIN", "FAIL", 
                                    f"Challenge join failed: {join_response.status_code}")
                        return False
                else:
                    self.log_test("CHALLENGE_JOIN", "SKIP", "No test users available")
                    return False
            else:
                self.log_test("CHALLENGE_CREATE", "FAIL", 
                            f"Challenge creation failed: {challenge_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CHALLENGE_FLOW", "FAIL", "Challenge flow test failed", e)
            return False

    def test_leaderboard_updates(self):
        """Test leaderboard functionality and updates"""
        print("\n" + "="*60)
        print("🏆 TESTING LEADERBOARD UPDATES")
        print("="*60)
        
        try:
            if self.challenge_codes:
                challenge_code = self.challenge_codes[0]
                
                # Test challenge-specific leaderboard
                leaderboard_response = self.session.get(f"{self.base_url}/api/leaderboard/{challenge_code}")
                
                if leaderboard_response.status_code == 200:
                    leaderboard_data = leaderboard_response.json()
                    participants = leaderboard_data.get('participants', [])
                    
                    self.log_test("CHALLENGE_LEADERBOARD", "PASS", 
                                f"Challenge leaderboard retrieved with {len(participants)} participants")
                    
                    # Test global leaderboard
                    global_leaderboard = self.session.get(f"{self.base_url}/api/leaderboard")
                    
                    if global_leaderboard.status_code == 200:
                        self.log_test("GLOBAL_LEADERBOARD", "PASS", "Global leaderboard accessible")
                        return True
                    else:
                        self.log_test("GLOBAL_LEADERBOARD", "FAIL", 
                                    f"Global leaderboard failed: {global_leaderboard.status_code}")
                        return False
                else:
                    self.log_test("CHALLENGE_LEADERBOARD", "FAIL", 
                                f"Challenge leaderboard failed: {leaderboard_response.status_code}")
                    return False
            else:
                self.log_test("LEADERBOARD_TEST", "SKIP", "No challenge codes available for testing")
                return False
                
        except Exception as e:
            self.log_test("LEADERBOARD_TEST", "FAIL", "Leaderboard test failed", e)
            return False

    def test_concurrent_users(self):
        """Test system with concurrent users in same challenge"""
        print("\n" + "="*60)
        print("👥 TESTING CONCURRENT USERS (50 users)")
        print("="*60)
        
        async def create_concurrent_user(session, user_id):
            """Create and test a single concurrent user"""
            try:
                username = f"concurrent_user_{user_id}_{int(time.time())}"
                email = f"{username}@test.com"
                password = "testpass123"
                
                # Register user
                async with session.post(f"{self.base_url}/api/auth/register", 
                                      json={'username': username, 'email': email, 'password': password}) as resp:
                    if resp.status not in [200, 201]:
                        return {'user_id': user_id, 'status': 'REGISTER_FAIL', 'error': await resp.text()}
                
                # Login user
                async with session.post(f"{self.base_url}/api/auth/login", 
                                      json={'username': username, 'password': password}) as resp:
                    if resp.status != 200:
                        return {'user_id': user_id, 'status': 'LOGIN_FAIL', 'error': await resp.text()}
                    
                    user_data = await resp.json()
                    token = user_data.get('access_token')
                    headers = {'Authorization': f'Bearer {token}'}
                
                # Join challenge if available
                if self.challenge_codes:
                    challenge_code = self.challenge_codes[0]
                    async with session.post(f"{self.base_url}/api/challenges/join/{challenge_code}",
                                          headers=headers) as resp:
                        if resp.status != 200:
                            return {'user_id': user_id, 'status': 'JOIN_FAIL', 'error': await resp.text()}
                    
                    # Start quiz
                    async with session.post(f"{self.base_url}/api/challenges/{challenge_code}/start",
                                          headers=headers) as resp:
                        if resp.status == 200:
                            return {'user_id': user_id, 'status': 'SUCCESS'}
                        else:
                            return {'user_id': user_id, 'status': 'START_FAIL', 'error': await resp.text()}
                
                return {'user_id': user_id, 'status': 'NO_CHALLENGE'}
                
            except Exception as e:
                return {'user_id': user_id, 'status': 'EXCEPTION', 'error': str(e)}
        
        async def run_concurrent_test():
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                tasks = []
                
                for i in range(self.concurrent_users):
                    task = create_concurrent_user(session, i)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return results
        
        try:
            # Run concurrent test
            start_time = time.time()
            results = asyncio.run(run_concurrent_test())
            end_time = time.time()
            
            # Analyze results
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'SUCCESS')
            failed = len(results) - successful
            duration = end_time - start_time
            
            if successful >= self.concurrent_users * 0.8:  # 80% success rate acceptable
                self.log_test("CONCURRENT_USERS", "PASS", 
                            f"{successful}/{self.concurrent_users} users successful in {duration:.2f}s")
            else:
                self.log_test("CONCURRENT_USERS", "FAIL", 
                            f"Only {successful}/{self.concurrent_users} users successful",
                            f"Failed users: {failed}")
                
                # Log first few failures for debugging
                failures = [r for r in results if isinstance(r, dict) and r.get('status') != 'SUCCESS'][:5]
                for failure in failures:
                    print(f"    Failure example: {failure}")
            
            return successful >= self.concurrent_users * 0.8
            
        except Exception as e:
            self.log_test("CONCURRENT_USERS", "FAIL", "Concurrent user test failed", e)
            return False

    # =================== ADMIN FEATURE TESTS ===================
    
    def test_admin_secure_access(self):
        """Test admin secure access control"""
        print("\n" + "="*60)
        print("🔐 TESTING ADMIN SECURE ACCESS CONTROL")
        print("="*60)
        
        try:
            # Test admin login
            admin_response = self.session.post(f"{self.base_url}/api/auth/login", 
                                             json=self.admin_creds)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                self.admin_token = admin_data.get('access_token')
                admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
                
                self.log_test("ADMIN_LOGIN", "PASS", "Admin login successful")
                
                # Test admin dashboard access
                dashboard_response = self.session.get(f"{self.base_url}/api/admin/dashboard", 
                                                    headers=admin_headers)
                
                if dashboard_response.status_code == 200:
                    self.log_test("ADMIN_DASHBOARD", "PASS", "Admin dashboard accessible")
                    
                    # Test regular user cannot access admin endpoints
                    if self.test_users:
                        user_headers = self.test_users[0]['headers']
                        unauthorized_response = self.session.get(f"{self.base_url}/api/admin/dashboard", 
                                                               headers=user_headers)
                        
                        if unauthorized_response.status_code == 403:
                            self.log_test("ADMIN_ACCESS_CONTROL", "PASS", 
                                        "Regular users properly blocked from admin endpoints")
                        else:
                            self.log_test("ADMIN_ACCESS_CONTROL", "FAIL", 
                                        "Regular users can access admin endpoints!")
                    
                    return True
                else:
                    self.log_test("ADMIN_DASHBOARD", "FAIL", 
                                f"Admin dashboard access failed: {dashboard_response.status_code}")
                    return False
            else:
                self.log_test("ADMIN_LOGIN", "FAIL", 
                            f"Admin login failed: {admin_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("ADMIN_ACCESS", "FAIL", "Admin access test failed", e)
            return False

    def test_pdf_upload_with_images(self):
        """Test PDF upload and AI image classification"""
        print("\n" + "="*60)
        print("📄 TESTING PDF UPLOAD WITH IMAGE CLASSIFICATION")
        print("="*60)
        
        # Test PDFs (if available)
        test_pdfs = [
            r'C:\Users\hp\Downloads\_18183_JEE_Main_2024_January_29_Shift_2_Physics_Question_Paper_with.pdf',
            r'C:\Users\hp\Downloads\_19625_JEE_Main_2024_January_30_Shift_2_Physics_Question_Paper_with.pdf'
        ]
        
        if not self.admin_token:
            self.log_test("PDF_UPLOAD", "SKIP", "No admin token available")
            return False
        
        admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        for pdf_path in test_pdfs:
            if not os.path.exists(pdf_path):
                self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "SKIP", "PDF file not found")
                continue
            
            try:
                # Test PDF upload
                with open(pdf_path, 'rb') as pdf_file:
                    files = {'pdf': pdf_file}
                    data = {
                        'exam_type': 'JEE Main',
                        'difficulty': 'mixed'
                    }
                    
                    upload_response = self.session.post(f"{self.base_url}/api/admin/upload-pdf",
                                                      files=files, data=data, headers=admin_headers)
                    
                    if upload_response.status_code == 200:
                        result = upload_response.json()
                        questions_added = result.get('questions_added', 0)
                        breakdown = result.get('breakdown', {})
                        
                        # Check if AI properly classified difficulty
                        easy_count = breakdown.get('easy', 0)
                        tough_count = breakdown.get('tough', 0)
                        
                        if easy_count > 0 and tough_count > 0:
                            self.log_test(f"AI_CLASSIFICATION_{Path(pdf_path).name}", "PASS",
                                        f"AI properly classified: {easy_count} easy, {tough_count} tough")
                        elif questions_added > 0:
                            self.log_test(f"AI_CLASSIFICATION_{Path(pdf_path).name}", "WARN",
                                        f"Questions extracted but classification may be incomplete")
                        
                        self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "PASS", 
                                    f"{questions_added} questions uploaded successfully")
                    else:
                        self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "FAIL", 
                                    f"Upload failed: {upload_response.status_code}")
                        
            except Exception as e:
                self.log_test(f"PDF_UPLOAD_{Path(pdf_path).name}", "FAIL", "Upload failed", e)
        
        return True

    def test_bulk_delete_verification(self):
        """Test bulk delete and verify questions don't reappear"""
        print("\n" + "="*60)
        print("🗑️ TESTING BULK DELETE VERIFICATION")
        print("="*60)
        
        if not self.admin_token:
            self.log_test("BULK_DELETE", "SKIP", "No admin token available")
            return False
        
        admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            # Get current questions
            questions_response = self.session.get(f"{self.base_url}/api/admin/questions", 
                                                headers=admin_headers)
            
            if questions_response.status_code == 200:
                questions = questions_response.json().get('questions', [])
                
                if len(questions) >= 2:
                    # Select first 2 questions for bulk delete
                    questions_to_delete = questions[:2]
                    question_ids = [q['id'] for q in questions_to_delete]
                    
                    # Perform bulk delete
                    bulk_delete_response = self.session.post(f"{self.base_url}/api/admin/questions/delete-bulk",
                                                           json={'question_ids': question_ids},
                                                           headers=admin_headers)
                    
                    if bulk_delete_response.status_code == 200:
                        result = bulk_delete_response.json()
                        success_count = result.get('success_count', 0)
                        
                        self.log_test("BULK_DELETE_API", "PASS", 
                                    f"Bulk delete successful: {success_count} questions deleted")
                        
                        # Verify questions don't reappear in question list
                        time.sleep(1)  # Brief wait
                        verify_response = self.session.get(f"{self.base_url}/api/admin/questions", 
                                                         headers=admin_headers)
                        
                        if verify_response.status_code == 200:
                            remaining_questions = verify_response.json().get('questions', [])
                            remaining_ids = [q['id'] for q in remaining_questions]
                            
                            deleted_ids_still_present = [qid for qid in question_ids if qid in remaining_ids]
                            
                            if not deleted_ids_still_present:
                                self.log_test("BULK_DELETE_VERIFY", "PASS", 
                                            "Deleted questions do not reappear in question list")
                                
                                # Create a new challenge and verify deleted questions don't appear
                                challenge_data = {
                                    'name': 'Bulk Delete Test Challenge',
                                    'difficulty': 'mixed',
                                    'exam_type': 'JEE Main',
                                    'time_limit': 30
                                }
                                
                                challenge_response = self.session.post(f"{self.base_url}/api/challenges", 
                                                                     json=challenge_data, 
                                                                     headers=admin_headers)
                                
                                if challenge_response.status_code == 201:
                                    challenge_code = challenge_response.json().get('code')
                                    
                                    # Try to start quiz and check if deleted questions appear
                                    if self.test_users:
                                        user_headers = self.test_users[0]['headers']
                                        join_response = self.session.post(f"{self.base_url}/api/challenges/join/{challenge_code}",
                                                                        headers=user_headers)
                                        
                                        if join_response.status_code == 200:
                                            start_response = self.session.post(f"{self.base_url}/api/challenges/{challenge_code}/start",
                                                                             headers=user_headers)
                                            
                                            if start_response.status_code == 200:
                                                quiz_questions = start_response.json().get('questions', [])
                                                quiz_question_ids = [q.get('id') for q in quiz_questions]
                                                
                                                deleted_in_quiz = [qid for qid in question_ids if qid in quiz_question_ids]
                                                
                                                if not deleted_in_quiz:
                                                    self.log_test("BULK_DELETE_CHALLENGE_VERIFY", "PASS", 
                                                                "Deleted questions do not appear in new challenges")
                                                else:
                                                    self.log_test("BULK_DELETE_CHALLENGE_VERIFY", "FAIL", 
                                                                f"Deleted questions still appear in challenges: {deleted_in_quiz}")
                                
                                return True
                            else:
                                self.log_test("BULK_DELETE_VERIFY", "FAIL", 
                                            f"Deleted questions still present: {deleted_ids_still_present}")
                                return False
                        else:
                            self.log_test("BULK_DELETE_VERIFY", "FAIL", 
                                        "Could not verify deletion - API call failed")
                            return False
                    else:
                        self.log_test("BULK_DELETE_API", "FAIL", 
                                    f"Bulk delete failed: {bulk_delete_response.status_code}")
                        return False
                else:
                    self.log_test("BULK_DELETE", "SKIP", "Not enough questions available for bulk delete test")
                    return False
            else:
                self.log_test("BULK_DELETE", "FAIL", 
                            f"Could not get questions: {questions_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("BULK_DELETE", "FAIL", "Bulk delete test failed", e)
            return False

    def test_challenge_difficulty_modes(self):
        """Test challenge creation with different difficulty modes"""
        print("\n" + "="*60)
        print("🎯 TESTING CHALLENGE DIFFICULTY MODES")
        print("="*60)
        
        if not self.admin_token:
            self.log_test("DIFFICULTY_MODES", "SKIP", "No admin token available")
            return False
        
        admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        difficulty_modes = ['easy', 'tough', 'mixed']
        
        for difficulty in difficulty_modes:
            try:
                challenge_data = {
                    'name': f'{difficulty.title()} Test Challenge',
                    'difficulty': difficulty,
                    'exam_type': 'JEE Main',
                    'time_limit': 30
                }
                
                challenge_response = self.session.post(f"{self.base_url}/api/challenges", 
                                                     json=challenge_data, 
                                                     headers=admin_headers)
                
                if challenge_response.status_code == 201:
                    challenge = challenge_response.json()
                    challenge_code = challenge.get('code')
                    
                    self.log_test(f"CHALLENGE_CREATE_{difficulty.upper()}", "PASS", 
                                f"{difficulty} challenge created: {challenge_code}")
                    
                    # Test the challenge with a user
                    if self.test_users:
                        user_headers = self.test_users[0]['headers']
                        join_response = self.session.post(f"{self.base_url}/api/challenges/join/{challenge_code}",
                                                        headers=user_headers)
                        
                        if join_response.status_code == 200:
                            start_response = self.session.post(f"{self.base_url}/api/challenges/{challenge_code}/start",
                                                             headers=user_headers)
                            
                            if start_response.status_code == 200:
                                quiz_data = start_response.json()
                                questions = quiz_data.get('questions', [])
                                
                                if questions:
                                    # Verify difficulty distribution
                                    easy_count = sum(1 for q in questions if q.get('difficulty') == 'easy')
                                    tough_count = sum(1 for q in questions if q.get('difficulty') == 'tough')
                                    
                                    if difficulty == 'easy' and easy_count > tough_count:
                                        self.log_test(f"DIFFICULTY_DISTRIBUTION_EASY", "PASS", 
                                                    f"Easy mode: {easy_count} easy, {tough_count} tough")
                                    elif difficulty == 'tough' and tough_count > easy_count:
                                        self.log_test(f"DIFFICULTY_DISTRIBUTION_TOUGH", "PASS", 
                                                    f"Tough mode: {easy_count} easy, {tough_count} tough")
                                    elif difficulty == 'mixed':
                                        if easy_count > 0 and tough_count > 0:
                                            ratio = easy_count / (easy_count + tough_count) if (easy_count + tough_count) > 0 else 0
                                            if 0.4 <= ratio <= 0.7:  # 40-70% easy is acceptable for mixed
                                                self.log_test(f"DIFFICULTY_DISTRIBUTION_MIXED", "PASS", 
                                                            f"Mixed mode: {easy_count} easy, {tough_count} tough (ratio: {ratio:.2f})")
                                            else:
                                                self.log_test(f"DIFFICULTY_DISTRIBUTION_MIXED", "WARN", 
                                                            f"Mixed mode ratio suboptimal: {ratio:.2f}")
                                        else:
                                            self.log_test(f"DIFFICULTY_DISTRIBUTION_MIXED", "FAIL", 
                                                        "Mixed mode should have both easy and tough questions")
                                
                else:
                    self.log_test(f"CHALLENGE_CREATE_{difficulty.upper()}", "FAIL", 
                                f"Challenge creation failed: {challenge_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"DIFFICULTY_MODE_{difficulty.upper()}", "FAIL", 
                            f"{difficulty} mode test failed", e)
        
        return True

    # =================== SYSTEM TESTS ===================
    
    def test_api_rate_limiting(self):
        """Test API rate limiting functionality"""
        print("\n" + "="*60)
        print("🚦 TESTING API RATE LIMITING")
        print("="*60)
        
        try:
            # Test login endpoint rate limiting
            rapid_requests = []
            for i in range(10):  # Send 10 rapid requests
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/api/auth/login", 
                                           json={'username': 'nonexistent', 'password': 'wrong'})
                end_time = time.time()
                
                rapid_requests.append({
                    'status_code': response.status_code,
                    'duration': end_time - start_time
                })
                
                time.sleep(0.1)  # Small delay between requests
            
            # Check if any requests were rate limited (429 status code)
            rate_limited = [r for r in rapid_requests if r['status_code'] == 429]
            
            if rate_limited:
                self.log_test("RATE_LIMITING", "PASS", 
                            f"Rate limiting working: {len(rate_limited)} requests blocked")
            else:
                self.log_test("RATE_LIMITING", "WARN", 
                            "No rate limiting detected - may need configuration")
            
            return True
            
        except Exception as e:
            self.log_test("RATE_LIMITING", "FAIL", "Rate limiting test failed", e)
            return False

    def test_jwt_expiry(self):
        """Test JWT token expiry handling"""
        print("\n" + "="*60)
        print("⏰ TESTING JWT TOKEN EXPIRY")
        print("="*60)
        
        try:
            # Create a user for testing
            username = f"expiry_test_{int(time.time())}"
            register_data = {
                'username': username,
                'email': f"{username}@test.com",
                'password': 'testpass123'
            }
            
            register_response = self.session.post(f"{self.base_url}/api/auth/register", 
                                                json=register_data)
            
            if register_response.status_code in [200, 201]:
                # Login to get token
                login_response = self.session.post(f"{self.base_url}/api/auth/login", 
                                                 json={'username': username, 'password': 'testpass123'})
                
                if login_response.status_code == 200:
                    token = login_response.json().get('access_token')
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    # Test immediate token validity
                    profile_response = self.session.get(f"{self.base_url}/api/auth/profile", 
                                                      headers=headers)
                    
                    if profile_response.status_code == 200:
                        self.log_test("JWT_VALID", "PASS", "Fresh JWT token works correctly")
                        
                        # For comprehensive testing, we'd need to wait for actual expiry
                        # or modify JWT settings to have very short expiry for testing
                        # For now, test with an obviously invalid token
                        
                        invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
                        invalid_response = self.session.get(f"{self.base_url}/api/auth/profile", 
                                                          headers=invalid_headers)
                        
                        if invalid_response.status_code == 401:
                            self.log_test("JWT_INVALID", "PASS", "Invalid JWT properly rejected")
                            return True
                        else:
                            self.log_test("JWT_INVALID", "FAIL", "Invalid JWT not properly handled")
                            return False
                    else:
                        self.log_test("JWT_VALID", "FAIL", "Fresh JWT token doesn't work")
                        return False
                else:
                    self.log_test("JWT_EXPIRY_LOGIN", "FAIL", "Could not login for JWT expiry test")
                    return False
            else:
                self.log_test("JWT_EXPIRY_REGISTER", "FAIL", "Could not register for JWT expiry test")
                return False
                
        except Exception as e:
            self.log_test("JWT_EXPIRY", "FAIL", "JWT expiry test failed", e)
            return False

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n" + "="*60)
        print("🛡️ TESTING ERROR HANDLING")
        print("="*60)
        
        try:
            # Test invalid challenge code
            invalid_join = self.session.post(f"{self.base_url}/api/challenges/join/INVALID123")
            
            if invalid_join.status_code in [400, 404]:
                self.log_test("INVALID_CHALLENGE_CODE", "PASS", 
                            "Invalid challenge codes properly rejected")
            else:
                self.log_test("INVALID_CHALLENGE_CODE", "FAIL", 
                            f"Invalid challenge code handling unclear: {invalid_join.status_code}")
            
            # Test malformed JSON
            malformed_response = self.session.post(f"{self.base_url}/api/auth/login", 
                                                 data="invalid json")
            
            if malformed_response.status_code == 400:
                self.log_test("MALFORMED_JSON", "PASS", "Malformed JSON properly rejected")
            else:
                self.log_test("MALFORMED_JSON", "FAIL", 
                            f"Malformed JSON handling unclear: {malformed_response.status_code}")
            
            # Test missing required fields
            incomplete_data = {'username': 'test'}  # Missing password
            incomplete_response = self.session.post(f"{self.base_url}/api/auth/login", 
                                                  json=incomplete_data)
            
            if incomplete_response.status_code == 400:
                self.log_test("MISSING_FIELDS", "PASS", "Missing required fields properly handled")
            else:
                self.log_test("MISSING_FIELDS", "FAIL", 
                            f"Missing fields handling unclear: {incomplete_response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("ERROR_HANDLING", "FAIL", "Error handling test failed", e)
            return False

    def cleanup(self):
        """Clean up test processes and data"""
        print("\n🧹 Cleaning up test environment...")
        
        if hasattr(self, 'backend_process'):
            try:
                self.backend_process.terminate()
                print("   Backend process terminated")
            except:
                pass

    def generate_comprehensive_report(self):
        """Generate detailed test report with all findings"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE END-TO-END TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        warning_tests = sum(1 for result in self.test_results.values() if result['status'] == 'WARN')
        skipped_tests = sum(1 for result in self.test_results.values() if result['status'] == 'SKIP')
        
        print(f"\n📋 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Detailed results by category
        categories = {
            'User Features': ['USER_', 'CHALLENGE_', 'QUIZ_', 'LEADERBOARD_', 'CONCURRENT_', 'SCORING_'],
            'Admin Features': ['ADMIN_', 'PDF_', 'BULK_', 'AI_', 'DIFFICULTY_'],
            'System Tests': ['RATE_', 'JWT_', 'ERROR_', 'BACKEND_']
        }
        
        for category, prefixes in categories.items():
            print(f"\n📂 {category}:")
            category_tests = {name: result for name, result in self.test_results.items() 
                            if any(name.startswith(prefix) for prefix in prefixes)}
            
            for test_name, result in category_tests.items():
                status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(result['status'], "❓")
                print(f"  {status_icon} {test_name}: {result['details']}")
                if result['error']:
                    print(f"      Error: {result['error']}")
        
        # Issues found
        if self.issues_found:
            print(f"\n🐛 ISSUES FOUND ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"{i}. {issue['test']}: {issue['error']}")
                print(f"   Details: {issue['details']}")
                print(f"   Time: {issue['timestamp']}")
        
        # Final recommendation
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! System is production-ready.")
        elif failed_tests <= 2:
            print(f"\n⚠️ Minor issues found ({failed_tests} failures). Review and fix before production.")
        else:
            print(f"\n🚨 Significant issues found ({failed_tests} failures). NOT ready for production.")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warning_tests,
                'skipped': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'issues_found': self.issues_found,
            'test_users_created': len(self.test_users),
            'challenges_created': len(self.challenge_codes)
        }
        
        report_path = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return failed_tests == 0

def main():
    """Run comprehensive end-to-end testing"""
    print("🧪 QuizBattle Comprehensive End-to-End Testing Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will test ALL features mentioned in your requirements")
    
    tester = QuizBattleE2ETester()
    
    try:
        # Start backend
        if not tester.start_backend_server():
            print("❌ Cannot proceed without backend server")
            return False
        
        time.sleep(5)  # Wait for server to be fully ready
        
        # Run all test categories
        print("\n🚀 Starting comprehensive testing...")
        
        # USER FEATURES
        tester.test_user_authentication_flow()
        tester.test_challenge_join_and_participation()
        tester.test_leaderboard_updates()
        tester.test_concurrent_users()
        
        # ADMIN FEATURES
        tester.test_admin_secure_access()
        tester.test_pdf_upload_with_images()
        tester.test_bulk_delete_verification()
        tester.test_challenge_difficulty_modes()
        
        # SYSTEM TESTS
        tester.test_api_rate_limiting()
        tester.test_jwt_expiry()
        tester.test_error_handling()
        
        # Generate comprehensive report
        success = tester.generate_comprehensive_report()
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        tester.cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)