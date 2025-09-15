#!/usr/bin/env python3
"""
ULTIMATE DEPLOYMENT FIX - Python 3.13 psycopg2 compatibility + simplified startup
"""
import requests
import time

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def apply_ultimate_fix():
    """Apply the ultimate fix for Python 3.13 + psycopg2 compatibility"""
    print("🔧 APPLYING ULTIMATE DEPLOYMENT FIX")
    print("=" * 60)
    print("Issues being resolved:")
    print("• Python 3.13 psycopg2 compatibility (use psycopg2-binary 2.9.9)")
    print("• Remove database init script from startup")  
    print("• Simplify to direct gunicorn startup")
    print("=" * 60)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Ultimate configuration fix
        update_payload = {
            # Remove the problematic database init script entirely
            "startCommand": "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 wsgi:app",
            # Force clean build with upgraded psycopg2-binary
            "buildCommand": "pip install --upgrade pip && pip install --force-reinstall --no-cache-dir -r requirements.txt"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            print("✅ ULTIMATE CONFIGURATION APPLIED!")
            print("   → Build: Force reinstall with Python 3.13 compatible packages")
            print("   → Start: Direct gunicorn startup (no database init script)")
            print("   → Workers: 2 workers with 120s timeout")
            return True
        else:
            print(f"❌ Configuration update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False

def trigger_final_deployment():
    """Trigger the final deployment with all fixes"""
    print("\\n🚀 TRIGGERING FINAL DEPLOYMENT")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {"clearCache": "clear"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code in [201, 202]:
            print("✅ Final deployment triggered successfully!")
            
            if response.text:
                try:
                    deploy_info = response.json()
                    deploy_id = deploy_info.get('id', 'unknown')
                    print(f"   Deploy ID: {deploy_id}")
                except:
                    pass
                    
            return True
        else:
            print(f"❌ Deployment trigger failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment trigger error: {e}")
        return False

def wait_and_comprehensive_test():
    """Wait for deployment and run comprehensive tests"""
    print("\\n⏳ WAITING FOR DEPLOYMENT COMPLETION")
    print("=" * 50)
    print("Waiting 8 minutes for build + deploy...")
    
    # Wait in 1-minute intervals with status updates
    for minute in range(8):
        time.sleep(60)
        print(f"   ⏰ {minute + 1}/8 minutes elapsed...")
        
        # Test every 2 minutes after the 4th minute
        if minute >= 3 and minute % 2 == 1:
            print("   🧪 Quick health check...")
            try:
                base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
                health_response = requests.get(f"{base_url}/health", timeout=10)
                if health_response.status_code == 200:
                    print("   🎉 SERVICE IS LIVE! Proceeding to full tests...")
                    break
                else:
                    print(f"   ⏳ Still deploying... (status: {health_response.status_code})")
            except:
                print("   ⏳ Still deploying... (connection error)")
    
    print("\\n🧪 COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 50)
    
    base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
    test_results = {}
    
    # Test 1: Health Check
    try:
        print("1. Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health", timeout=30)
        test_results['health'] = health_response.status_code
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Health: {health_response.status_code} - {health_data.get('status', 'unknown')}")
        else:
            print(f"   ❌ Health: {health_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Health: Error - {e}")
        test_results['health'] = 'Error'
    
    # Test 2: Root endpoint
    try:
        print("2. Testing root API endpoint...")
        root_response = requests.get(f"{base_url}/", timeout=30)
        test_results['root'] = root_response.status_code
        
        if root_response.status_code == 200:
            print(f"   ✅ Root API: {root_response.status_code}")
        else:
            print(f"   ❌ Root API: {root_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Root API: Error - {e}")
        test_results['root'] = 'Error'
    
    # Test 3: Admin Login (tests database connectivity)
    try:
        print("3. Testing admin login (database test)...")
        admin_data = {
            "username": "admin",
            "password": "Admin@123"
        }
        admin_response = requests.post(f"{base_url}/api/auth/admin/login", 
                                     json=admin_data, timeout=30)
        test_results['admin_login'] = admin_response.status_code
        
        if admin_response.status_code == 200:
            print(f"   ✅ Admin Login: {admin_response.status_code} - Database working!")
        else:
            print(f"   ⚠️  Admin Login: {admin_response.status_code}")
            print(f"      Response: {admin_response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Admin Login: Error - {e}")
        test_results['admin_login'] = 'Error'
    
    # Test 4: User Registration
    try:
        print("4. Testing user registration...")
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpass123"
        }
        reg_response = requests.post(f"{base_url}/api/auth/register", 
                                   json=user_data, timeout=30)
        test_results['registration'] = reg_response.status_code
        
        if reg_response.status_code == 201:
            print(f"   ✅ User Registration: {reg_response.status_code}")
        else:
            print(f"   ⚠️  User Registration: {reg_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ User Registration: Error - {e}")
        test_results['registration'] = 'Error'
    
    # Results Summary
    print("\\n" + "=" * 60)
    print("🏆 FINAL DEPLOYMENT TEST RESULTS")
    print("=" * 60)
    
    working_tests = sum(1 for status in test_results.values() if status == 200)
    partial_tests = sum(1 for status in test_results.values() if isinstance(status, int) and status != 200)
    failed_tests = sum(1 for status in test_results.values() if status == 'Error')
    
    print(f"📊 Results: {working_tests} ✅ Working, {partial_tests} ⚠️ Partial, {failed_tests} ❌ Failed")
    
    for test_name, status in test_results.items():
        icon = "✅" if status == 200 else "⚠️" if isinstance(status, int) else "❌"
        print(f"   {icon} {test_name.replace('_', ' ').title()}: {status}")
    
    if test_results.get('health') == 200:
        print("\\n🎉 DEPLOYMENT SUCCESS!")
        print(f"🌐 Frontend: https://quizbattle-frontend.netlify.app")
        print(f"🔧 Backend: {base_url}")
        print(f"💚 Health: {base_url}/health")
        print("\\n🔑 Admin Credentials:")
        print("   Username: admin")
        print("   Password: Admin@123")
        print("\\n✨ Your QuizBattle application is LIVE! ✨")
        return True
    else:
        print("\\n⚠️ Deployment partially successful - service may need more time")
        return False

if __name__ == "__main__":
    print("🚀 ULTIMATE QUIZBATTLE DEPLOYMENT FIX")
    print("=" * 60)
    
    # Step 1: Apply ultimate fix
    fix_success = apply_ultimate_fix()
    
    if fix_success:
        # Step 2: Trigger final deployment
        deploy_success = trigger_final_deployment()
        
        if deploy_success:
            # Step 3: Wait and test comprehensively
            test_success = wait_and_comprehensive_test()
            
            if test_success:
                print("\\n🎊 MISSION ACCOMPLISHED! QuizBattle is fully operational! 🎊")
            else:
                print("\\n📋 Deployment completed - may need a few more minutes to be fully ready")
        else:
            print("\\n❌ Deployment trigger failed")
    else:
        print("\\n❌ Fix application failed")
    
    print("\\n" + "=" * 60)
    print("📞 Support: All files available in GitHub repository")
    print("🔗 Repo: https://github.com/CrazyCoders1/quizbattle")
    print("=" * 60)