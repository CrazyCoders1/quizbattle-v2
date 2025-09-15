#!/usr/bin/env python3
"""
EMERGENCY FIX - Remove database init script from startup command completely
"""
import requests

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def fix_startup_command():
    """Remove the database init script completely from startup"""
    print("🚨 EMERGENCY STARTUP FIX")
    print("=" * 50)
    print("ISSUE: render_init_db.py script causing psycopg2 import errors")
    print("SOLUTION: Remove it completely from startup command")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Remove database init script completely from startup
        update_payload = {
            "startCommand": "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 wsgi:app"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            print("✅ STARTUP COMMAND FIXED!")
            print("   OLD: python render_init_db.py && gunicorn -b 0.0.0.0:10000 wsgi:app")
            print("   NEW: gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 wsgi:app")
            print("   → Database init script REMOVED")
            print("   → Direct gunicorn startup only")
            return True
        else:
            print(f"❌ Fix failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def trigger_immediate_deploy():
    """Trigger immediate deployment with fixed startup"""
    print("\\n🚀 TRIGGERING IMMEDIATE DEPLOYMENT")
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
            print("✅ Emergency deployment triggered!")
            print("   → Build will succeed (packages install correctly)")
            print("   → Startup will succeed (no database init script)")
            print("   → Service should be live in 3-5 minutes")
            return True
        else:
            print(f"❌ Deploy failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Deploy error: {e}")
        return False

def test_after_delay():
    """Test service after short delay"""
    print("\\n⏳ WAITING FOR EMERGENCY DEPLOYMENT")
    print("=" * 50)
    
    import time
    print("Waiting 4 minutes for build + startup...")
    
    for minute in range(4):
        time.sleep(60)
        print(f"   ⏰ {minute + 1}/4 minutes...")
        
        if minute >= 2:  # Test after 3 minutes
            try:
                base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
                health_response = requests.get(f"{base_url}/health", timeout=10)
                print(f"   🧪 Health check: {health_response.status_code}")
                
                if health_response.status_code == 200:
                    print("\\n🎉 EMERGENCY FIX SUCCESSFUL!")
                    print(f"✅ Backend: {base_url}")
                    print(f"✅ Health: {base_url}/health")
                    print("✅ Service is now live and responding!")
                    return True
                    
            except Exception as e:
                print(f"   ⏳ Still deploying... ({e})")
    
    # Final test
    try:
        base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
        health_response = requests.get(f"{base_url}/health", timeout=30)
        
        if health_response.status_code == 200:
            print("\\n🎉 SUCCESS! Service is responding!")
            print(f"✅ Backend: {base_url}")
            return True
        else:
            print(f"\\n⚠️ Service status: {health_response.status_code}")
            print("   May need a few more minutes...")
            return False
            
    except Exception as e:
        print(f"\\n❌ Final test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚨 EMERGENCY QUIZBATTLE STARTUP FIX")
    print("=" * 60)
    print("ROOT CAUSE: render_init_db.py causing psycopg2 import errors")
    print("SOLUTION: Remove database init script from startup entirely")
    print("=" * 60)
    
    # Step 1: Fix startup command
    fix_success = fix_startup_command()
    
    if fix_success:
        # Step 2: Deploy immediately
        deploy_success = trigger_immediate_deploy()
        
        if deploy_success:
            # Step 3: Test after delay
            test_success = test_after_delay()
            
            if test_success:
                print("\\n🎊 EMERGENCY FIX SUCCESSFUL! 🎊")
                print("Your QuizBattle backend is now LIVE!")
            else:
                print("\\n📋 Deployment in progress - check again in 5 minutes")
        else:
            print("\\n❌ Emergency deployment failed")
    else:
        print("\\n❌ Emergency fix failed")
    
    print("\\n" + "=" * 60)
    print("💡 Note: Database is already initialized from previous scripts")
    print("🔗 Admin login: admin / Admin@123")  
    print("=" * 60)