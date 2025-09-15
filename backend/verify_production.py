#!/usr/bin/env python3
"""
Production Verification Script for QuizBattle
Test all critical endpoints after Render deployment
"""
import requests
import json
import time
import sys

# Production URLs
BACKEND_URL = "https://quizbattle-backend.onrender.com"
FRONTEND_URL = "https://quizbattle-frontend.netlify.app"

def test_endpoint(method, url, data=None, expected_status=200, test_name="Test"):
    """Test a single endpoint and return result"""
    try:
        print(f"🧪 {test_name}: {method} {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, timeout=30)
        elif method.upper() == 'POST':
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"   ✅ PASS")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"   ❌ FAIL (expected {expected_status}, got {response.status_code})")
            print(f"   Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def run_production_verification():
    """Run comprehensive production verification"""
    print("=" * 60)
    print("🚀 QUIZBATTLE PRODUCTION VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Test 1: Backend Health
    results.append(test_endpoint(
        'GET', 
        f"{BACKEND_URL}/health",
        expected_status=200,
        test_name="Backend Health Check"
    ))
    
    # Test 2: User Registration
    test_user = {
        "username": f"smoketest{int(time.time())}",
        "email": f"smoketest{int(time.time())}@example.com", 
        "password": "Test@1234"
    }
    
    results.append(test_endpoint(
        'POST',
        f"{BACKEND_URL}/api/auth/register", 
        data=test_user,
        expected_status=201,
        test_name="User Registration"
    ))
    
    # Test 3: Admin Login
    admin_creds = {
        "username": "admin",
        "password": "admin123"
    }
    
    results.append(test_endpoint(
        'POST',
        f"{BACKEND_URL}/api/auth/admin/login",
        data=admin_creds, 
        expected_status=200,
        test_name="Admin Login"
    ))
    
    # Test 4: Frontend Health
    results.append(test_endpoint(
        'GET',
        FRONTEND_URL,
        expected_status=200,
        test_name="Frontend Deployment"
    ))
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - PRODUCTION READY!")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED - NEEDS ATTENTION")
        return False

if __name__ == '__main__':
    success = run_production_verification()
    sys.exit(0 if success else 1)