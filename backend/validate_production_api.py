#!/usr/bin/env python3
"""
Production API Validation Script for QuizBattle
Tests all critical API endpoints and validates functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://quizbattle-backend.onrender.com"
TEST_USER = {
    "username": "testuser123",
    "email": "testuser123@example.com",
    "password": "Test@1234"
}

TEST_ADMIN = {
    "username": "admin",
    "password": "admin123"
}

class APIValidator:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details="", response_time=0):
        """Log test results"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details,
            "response_time": f"{response_time:.2f}ms",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status else "❌"
        print(f"{status_emoji} {test_name}: {details} ({response_time:.2f}ms)")
        
    def test_endpoint(self, method, url, data=None, headers=None, expected_status=200):
        """Generic endpoint testing method"""
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == expected_status:
                return True, response, response_time
            else:
                return False, response, response_time
                
        except Exception as e:
            return False, str(e), 0
    
    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🔍 Testing Basic Endpoints...")
        print("-" * 40)
        
        # Test root endpoint
        success, response, rt = self.test_endpoint("GET", f"{BASE_URL}/")
        if success:
            try:
                data = response.json()
                details = f"API: {data.get('name', 'Unknown')}, Status: {data.get('status', 'Unknown')}"
            except:
                details = "Root endpoint accessible but invalid JSON"
        else:
            details = f"Failed: {response.status_code if hasattr(response, 'status_code') else response}"
        self.log_test("Root Endpoint", success, details, rt)
        
        # Test health endpoint
        success, response, rt = self.test_endpoint("GET", f"{BASE_URL}/health")
        if success:
            try:
                data = response.json()
                details = f"Status: {data.get('status', 'Unknown')}, Version: {data.get('version', 'Unknown')}"
            except:
                details = "Health endpoint accessible but invalid JSON"
        else:
            details = f"Failed: {response.status_code if hasattr(response, 'status_code') else response}"
        self.log_test("Health Endpoint", success, details, rt)
    
    def test_authentication(self):
        """Test user authentication system"""
        print("\n👤 Testing Authentication System...")
        print("-" * 40)
        
        # Test user registration
        success, response, rt = self.test_endpoint(
            "POST", 
            f"{BASE_URL}/api/auth/register", 
            data=TEST_USER,
            expected_status=201
        )
        
        if success:
            try:
                data = response.json()
                details = f"User created: {data.get('message', 'Success')}"
            except:
                details = "Registration succeeded but invalid JSON response"
        else:
            # Check if user already exists
            if hasattr(response, 'status_code') and response.status_code == 400:
                try:
                    error_data = response.json()
                    if "already exists" in error_data.get('error', ''):
                        details = "User already exists (expected for repeat tests)"
                        success = True
                    else:
                        details = f"Registration failed: {error_data.get('error', 'Unknown error')}"
                except:
                    details = f"Registration failed with status {response.status_code}"
            else:
                details = f"Registration failed: {response.status_code if hasattr(response, 'status_code') else response}"
        
        self.log_test("User Registration", success, details, rt)
        
        # Test user login
        success, response, rt = self.test_endpoint(
            "POST",
            f"{BASE_URL}/api/auth/login",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        
        if success:
            try:
                data = response.json()
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details = f"Login successful, Token: {'Present' if self.user_token else 'Missing'}, User: {user_info.get('username', 'Unknown')}"
            except:
                details = "Login succeeded but invalid JSON response"
        else:
            details = f"Login failed: {response.status_code if hasattr(response, 'status_code') else response}"
        
        self.log_test("User Login", success, details, rt)
        
        # Test admin login
        success, response, rt = self.test_endpoint(
            "POST",
            f"{BASE_URL}/api/auth/admin/login",
            data=TEST_ADMIN
        )
        
        if success:
            try:
                data = response.json()
                self.admin_token = data.get('access_token')
                admin_info = data.get('admin', {})
                details = f"Admin login successful, Token: {'Present' if self.admin_token else 'Missing'}, Admin: {admin_info.get('username', 'Unknown')}"
            except:
                details = "Admin login succeeded but invalid JSON response"
        else:
            details = f"Admin login failed: {response.status_code if hasattr(response, 'status_code') else response}"
        
        self.log_test("Admin Login", success, details, rt)
    
    def test_protected_routes(self):
        """Test JWT-protected routes"""
        print("\n🔐 Testing Protected Routes...")
        print("-" * 40)
        
        if not self.user_token:
            self.log_test("Protected Routes", False, "No user token available", 0)
            return
        
        # Test user profile endpoint
        headers = {"Authorization": f"Bearer {self.user_token}"}
        success, response, rt = self.test_endpoint(
            "GET",
            f"{BASE_URL}/api/auth/profile",
            headers=headers
        )
        
        if success:
            try:
                data = response.json()
                user_info = data.get('user', {})
                details = f"Profile retrieved: {user_info.get('username', 'Unknown')}, ID: {user_info.get('id', 'Unknown')}"
            except:
                details = "Profile endpoint accessible but invalid JSON"
        else:
            details = f"Profile access failed: {response.status_code if hasattr(response, 'status_code') else response}"
        
        self.log_test("User Profile", success, details, rt)
    
    def test_admin_endpoints(self):
        """Test admin-protected endpoints"""
        print("\n👨‍💼 Testing Admin Endpoints...")
        print("-" * 40)
        
        if not self.admin_token:
            self.log_test("Admin Endpoints", False, "No admin token available", 0)
            return
        
        # Test admin dashboard
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        success, response, rt = self.test_endpoint(
            "GET",
            f"{BASE_URL}/api/admin/dashboard",
            headers=headers
        )
        
        if success:
            try:
                data = response.json()
                stats = data.get('stats', {})
                details = f"Dashboard access successful. Users: {stats.get('total_users', 'Unknown')}, Questions: {stats.get('total_questions', 'Unknown')}"
            except:
                details = "Dashboard accessible but invalid JSON response"
        else:
            details = f"Dashboard access failed: {response.status_code if hasattr(response, 'status_code') else response}"
        
        self.log_test("Admin Dashboard", success, details, rt)
        
        # Test admin questions endpoint
        success, response, rt = self.test_endpoint(
            "GET",
            f"{BASE_URL}/api/admin/questions",
            headers=headers
        )
        
        if success:
            try:
                data = response.json()
                questions = data.get('questions', [])
                details = f"Questions endpoint accessible. Count: {len(questions)}"
            except:
                details = "Questions endpoint accessible but invalid JSON response"
        else:
            details = f"Questions access failed: {response.status_code if hasattr(response, 'status_code') else response}"
        
        self.log_test("Admin Questions", success, details, rt)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🧪 QUIZBATTLE API VALIDATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            print(f"    Details: {result['details']}")
            print(f"    Response Time: {result['response_time']}")
            print()
        
        # Determine overall status
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED - API IS READY FOR PRODUCTION!")
            status = "READY"
        elif failed_tests <= 2:
            print("⚠️ MINOR ISSUES FOUND - REVIEW BEFORE PRODUCTION")
            status = "REVIEW"
        else:
            print("❌ CRITICAL ISSUES FOUND - NOT READY FOR PRODUCTION")
            status = "NOT_READY"
        
        print(f"\n🎯 PRODUCTION READINESS: {status}")
        print(f"📅 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return status == "READY"
    
    def run_all_tests(self):
        """Run comprehensive API validation"""
        print("🚀 Starting QuizBattle API Validation...")
        print(f"🎯 Target: {BASE_URL}")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run test suites
        self.test_basic_endpoints()
        self.test_authentication()
        self.test_protected_routes()
        self.test_admin_endpoints()
        
        # Generate report
        return self.generate_report()

def main():
    """Main validation function"""
    validator = APIValidator()
    
    try:
        success = validator.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()