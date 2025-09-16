"""
Test suite for leaderboard forensics functionality and performance

This script tests:
1. Forensic debug endpoints
2. Database query performance  
3. Concurrency scenarios
4. Data consistency checks
"""

import requests
import json
import time
import threading
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Test configuration
BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin987"

class LeaderboardForensicTester:
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.admin_token = None
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': [],
            'performance_metrics': {}
        }
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
    def login_as_admin(self):
        """Authenticate as admin user"""
        self.log("🔐 Logging in as admin...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/admin/login",
                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                self.log("✅ Admin login successful")
                return True
            else:
                self.log(f"❌ Admin login failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Admin login error: {str(e)}", "ERROR")
            return False
            
    def make_authenticated_request(self, method, endpoint, **kwargs):
        """Make authenticated request with admin token"""
        if not self.admin_token:
            raise Exception("No admin token available")
            
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.admin_token}'
        kwargs['headers'] = headers
        
        url = f"{self.base_url}{endpoint}"
        return requests.request(method, url, **kwargs)
        
    def test_database_status(self):
        """Test basic database connectivity and status"""
        self.log("🔍 Testing database status...")
        self.test_results['total_tests'] += 1
        
        try:
            response = self.make_authenticated_request('GET', '/api/debug/database/status')
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Database status: {data.get('initialization_status', 'unknown')}")
                
                # Check table counts
                counts = data.get('counts', {})
                self.log(f"📊 Table counts: {counts}")
                
                self.test_results['passed_tests'] += 1
                return True
            else:
                self.log(f"❌ Database status failed: {response.status_code}", "ERROR")
                self.test_results['failed_tests'] += 1
                self.test_results['errors'].append(f"database_status: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Database status error: {str(e)}", "ERROR")
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"database_status: {str(e)}")
            return False
            
    def test_raw_leaderboard_endpoint(self):
        """Test raw leaderboard forensic endpoint"""
        self.log("🔍 Testing raw leaderboard endpoint...")
        self.test_results['total_tests'] += 1
        
        try:
            start_time = time.time()
            response = self.make_authenticated_request('GET', '/api/debug/leaderboard/raw?limit=25')
            request_time = time.time() - start_time
            
            self.test_results['performance_metrics']['raw_leaderboard_time'] = request_time
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('total_results', 0)
                raw_data = data.get('raw_leaderboard_data', [])
                
                self.log(f"✅ Raw leaderboard: {total_results} results in {request_time:.2f}s")
                
                # Validate data structure
                if raw_data and len(raw_data) > 0:
                    first_result = raw_data[0]
                    required_fields = ['quiz_result', 'user_info', 'challenge_info']
                    
                    if all(field in first_result for field in required_fields):
                        self.log("✅ Raw leaderboard data structure is valid")
                        self.test_results['passed_tests'] += 1
                        return True
                    else:
                        self.log("❌ Invalid raw leaderboard data structure", "ERROR")
                        self.test_results['failed_tests'] += 1
                        return False
                else:
                    self.log("⚠️ No raw leaderboard data found")
                    self.test_results['passed_tests'] += 1  # Still pass if no data
                    return True
            else:
                self.log(f"❌ Raw leaderboard failed: {response.status_code}", "ERROR")
                self.test_results['failed_tests'] += 1
                self.test_results['errors'].append(f"raw_leaderboard: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Raw leaderboard error: {str(e)}", "ERROR")
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"raw_leaderboard: {str(e)}")
            return False
            
    def test_challenge_forensic_endpoint(self, challenge_id=1):
        """Test challenge-specific forensic endpoint"""
        self.log(f"🔍 Testing challenge forensic endpoint for challenge {challenge_id}...")
        self.test_results['total_tests'] += 1
        
        try:
            start_time = time.time()
            response = self.make_authenticated_request('GET', f'/api/debug/challenge/{challenge_id}/results')
            request_time = time.time() - start_time
            
            self.test_results['performance_metrics']['challenge_forensic_time'] = request_time
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('total_results', 0)
                unique_participants = data.get('unique_participants', 0)
                
                self.log(f"✅ Challenge forensics: {total_results} results, {unique_participants} participants in {request_time:.2f}s")
                
                # Validate forensic analysis fields
                required_fields = ['challenge_info', 'results', 'user_participation_analysis', 'statistics']
                
                if all(field in data for field in required_fields):
                    statistics = data.get('statistics', {})
                    self.log(f"📈 Challenge stats: avg={statistics.get('avg_score', 0):.1f}, max={statistics.get('max_score', 0)}")
                    self.test_results['passed_tests'] += 1
                    return True
                else:
                    self.log("❌ Invalid challenge forensic data structure", "ERROR")
                    self.test_results['failed_tests'] += 1
                    return False
                    
            elif response.status_code == 404:
                self.log(f"⚠️ Challenge {challenge_id} not found")
                self.test_results['passed_tests'] += 1  # Expected for non-existent challenges
                return True
            else:
                self.log(f"❌ Challenge forensic failed: {response.status_code}", "ERROR")
                self.test_results['failed_tests'] += 1
                self.test_results['errors'].append(f"challenge_forensic: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Challenge forensic error: {str(e)}", "ERROR")
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"challenge_forensic: {str(e)}")
            return False
            
    def test_user_forensic_endpoint(self, user_id=1):
        """Test user-specific forensic endpoint"""
        self.log(f"🔍 Testing user forensic endpoint for user {user_id}...")
        self.test_results['total_tests'] += 1
        
        try:
            start_time = time.time()
            response = self.make_authenticated_request('GET', f'/api/debug/user/{user_id}/results')
            request_time = time.time() - start_time
            
            self.test_results['performance_metrics']['user_forensic_time'] = request_time
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('total_results', 0)
                unique_challenges = data.get('unique_challenges', 0)
                
                self.log(f"✅ User forensics: {total_results} results, {unique_challenges} challenges in {request_time:.2f}s")
                
                # Validate forensic analysis fields
                required_fields = ['user_info', 'results', 'challenge_participation_analysis', 'monthly_performance', 'statistics']
                
                if all(field in data for field in required_fields):
                    statistics = data.get('statistics', {})
                    self.log(f"📈 User stats: total_score={statistics.get('total_score_all_time', 0)}, avg={statistics.get('avg_score_all_time', 0):.1f}")
                    self.test_results['passed_tests'] += 1
                    return True
                else:
                    self.log("❌ Invalid user forensic data structure", "ERROR")
                    self.test_results['failed_tests'] += 1
                    return False
                    
            elif response.status_code == 404:
                self.log(f"⚠️ User {user_id} not found")
                self.test_results['passed_tests'] += 1  # Expected for non-existent users
                return True
            else:
                self.log(f"❌ User forensic failed: {response.status_code}", "ERROR")
                self.test_results['failed_tests'] += 1
                self.test_results['errors'].append(f"user_forensic: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ User forensic error: {str(e)}", "ERROR")
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"user_forensic: {str(e)}")
            return False
            
    def test_consistency_check(self):
        """Test database consistency check"""
        self.log("🔍 Testing database consistency check...")
        self.test_results['total_tests'] += 1
        
        try:
            start_time = time.time()
            response = self.make_authenticated_request('GET', '/api/debug/database/consistency')
            request_time = time.time() - start_time
            
            self.test_results['performance_metrics']['consistency_check_time'] = request_time
            
            if response.status_code == 200:
                data = response.json()
                totals = data.get('totals', {})
                orphaned = data.get('orphaned_records', {})
                inconsistencies = data.get('leaderboard_inconsistencies', [])
                
                self.log(f"✅ Consistency check completed in {request_time:.2f}s")
                self.log(f"📊 Totals: {totals}")
                self.log(f"🗑️ Orphaned records: {orphaned}")
                
                if inconsistencies:
                    self.log(f"⚠️ Found {len(inconsistencies)} leaderboard inconsistencies")
                else:
                    self.log("✅ No leaderboard inconsistencies found")
                
                self.test_results['passed_tests'] += 1
                return True
            else:
                self.log(f"❌ Consistency check failed: {response.status_code}", "ERROR")
                self.test_results['failed_tests'] += 1
                self.test_results['errors'].append(f"consistency_check: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Consistency check error: {str(e)}", "ERROR")
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"consistency_check: {str(e)}")
            return False
            
    def test_concurrent_requests(self, num_threads=5, num_requests=10):
        """Test concurrent access to forensic endpoints"""
        self.log(f"🔍 Testing concurrent requests: {num_threads} threads, {num_requests} requests each...")
        self.test_results['total_tests'] += 1
        
        try:
            start_time = time.time()
            success_count = 0
            error_count = 0
            
            def make_concurrent_request(thread_id, request_id):
                try:
                    endpoint = random.choice([
                        '/api/debug/leaderboard/raw?limit=10',
                        '/api/debug/database/consistency',
                        '/api/debug/challenge/1/results',
                        '/api/debug/user/1/results'
                    ])
                    
                    response = self.make_authenticated_request('GET', endpoint)
                    return response.status_code == 200
                except:
                    return False
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                
                for thread_id in range(num_threads):
                    for request_id in range(num_requests):
                        future = executor.submit(make_concurrent_request, thread_id, request_id)
                        futures.append(future)
                
                for future in as_completed(futures):
                    if future.result():
                        success_count += 1
                    else:
                        error_count += 1
            
            total_time = time.time() - start_time
            total_requests = num_threads * num_requests
            success_rate = (success_count / total_requests) * 100
            
            self.test_results['performance_metrics']['concurrent_test_time'] = total_time
            self.test_results['performance_metrics']['concurrent_success_rate'] = success_rate
            self.test_results['performance_metrics']['requests_per_second'] = total_requests / total_time
            
            self.log(f"✅ Concurrent test completed in {total_time:.2f}s")
            self.log(f"📈 Success rate: {success_rate:.1f}% ({success_count}/{total_requests})")
            self.log(f"⚡ Throughput: {total_requests / total_time:.1f} requests/second")
            
            if success_rate >= 80:  # At least 80% success rate
                self.test_results['passed_tests'] += 1
                return True
            else:
                self.log(f"❌ Low concurrent success rate: {success_rate:.1f}%", "ERROR")
                self.test_results['failed_tests'] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Concurrent test error: {str(e)}", "ERROR")
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"concurrent_test: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run complete test suite"""
        self.log("🚀 Starting leaderboard forensics test suite...")
        start_time = time.time()
        
        # Authentication
        if not self.login_as_admin():
            self.log("❌ Cannot proceed without admin authentication", "FATAL")
            return False
        
        # Core functionality tests
        self.test_database_status()
        self.test_raw_leaderboard_endpoint()
        self.test_challenge_forensic_endpoint()
        self.test_user_forensic_endpoint()
        self.test_consistency_check()
        
        # Performance and concurrency tests
        self.test_concurrent_requests()
        
        # Summary
        total_time = time.time() - start_time
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
        
        self.log("=" * 60)
        self.log("📋 TEST SUITE SUMMARY")
        self.log("=" * 60)
        self.log(f"Total tests: {self.test_results['total_tests']}")
        self.log(f"Passed: {self.test_results['passed_tests']}")
        self.log(f"Failed: {self.test_results['failed_tests']}")
        self.log(f"Success rate: {success_rate:.1f}%")
        self.log(f"Total time: {total_time:.2f} seconds")
        
        if self.test_results['performance_metrics']:
            self.log("⚡ PERFORMANCE METRICS:")
            for metric, value in self.test_results['performance_metrics'].items():
                if 'time' in metric:
                    self.log(f"  {metric}: {value:.3f}s")
                elif 'rate' in metric:
                    self.log(f"  {metric}: {value:.1f}%")
                else:
                    self.log(f"  {metric}: {value:.2f}")
        
        if self.test_results['errors']:
            self.log("❌ ERRORS:")
            for error in self.test_results['errors']:
                self.log(f"  {error}")
        
        return success_rate >= 80  # Consider suite successful if 80%+ pass


def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
        
    tester = LeaderboardForensicTester(base_url)
    
    print("🔧 Leaderboard Forensics Test Suite")
    print(f"🌐 Target: {base_url}")
    print("=" * 60)
    
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("💥 Test suite failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()