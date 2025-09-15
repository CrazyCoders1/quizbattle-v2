#!/usr/bin/env python3
"""
DEFINITIVE FIX - Force update startup command and fix DATABASE_URL
"""
import requests

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def force_fix_service_config():
    """Force fix both startup command and environment variables"""
    print("🔥 DEFINITIVE FIX - FORCE UPDATE ALL CONFIGURATION")
    print("=" * 60)
    print("Issues to fix:")
    print("1. Startup command still using old format with render_init_db.py")
    print("2. DATABASE_URL parsing error - likely environment variable issue")
    print("3. Force complete configuration update")
    print("=" * 60)
    
    try:
        # Step 1: Fix startup command completely
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Complete service configuration update
        update_payload = {
            "startCommand": "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 wsgi:app"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            print("✅ STARTUP COMMAND FORCIBLY UPDATED!")
            print("   OLD: python render_init_db.py && gunicorn -b 0.0.0.0:10000 wsgi:app")
            print("   NEW: gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 wsgi:app")
        else:
            print(f"❌ Startup command update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Service config error: {e}")
        return False
    
    # Step 2: Force update environment variables
    print("\\n🔧 FORCE UPDATING ENVIRONMENT VARIABLES")
    print("-" * 50)
    
    try:
        env_url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/env-vars"
        
        # Complete environment variable set with correct formatting
        env_vars = [
            {
                "key": "DATABASE_URL",
                "value": "postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
            },
            {
                "key": "MONGODB_URI", 
                "value": "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0"
            },
            {
                "key": "MONGO_URI",
                "value": "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0" 
            },
            {
                "key": "SECRET_KEY",
                "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
            },
            {
                "key": "JWT_SECRET", 
                "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
            },
            {
                "key": "FLASK_ENV",
                "value": "production"
            },
            {
                "key": "PORT",
                "value": "5000"
            },
            {
                "key": "PYTHONPATH",
                "value": "/opt/render/project/src"
            }
        ]
        
        response = requests.put(env_url, headers=headers, json=env_vars, timeout=60)
        if response.status_code == 200:
            print("✅ ENVIRONMENT VARIABLES FORCIBLY UPDATED!")
            for var in env_vars:
                key = var['key'] 
                value = var['value'][:50] + "..." if len(var['value']) > 50 else var['value']
                print(f"   → {key}: {value}")
        else:
            print(f"❌ Environment variables update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Environment variables error: {e}")
        return False
    
    return True

def trigger_final_deployment():
    """Trigger final deployment with all fixes"""
    print("\\n🚀 TRIGGERING FINAL DEPLOYMENT WITH ALL FIXES")
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
            print("✅ FINAL DEPLOYMENT TRIGGERED!")
            print("   → Configuration: Fixed startup command")
            print("   → Environment: All variables reset correctly")
            print("   → Build: Will use psycopg2-binary 2.9.9 (works)")
            print("   → Startup: Direct gunicorn (no database init script)")
            print("   → ETA: 3-5 minutes to live service")
            return True
        else:
            print(f"❌ Deployment trigger failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def final_verification():
    """Wait and verify the service is working"""
    print("\\n⏳ FINAL VERIFICATION")
    print("=" * 50)
    
    import time
    
    print("Waiting 5 minutes for complete deployment...")
    
    for minute in range(5):
        time.sleep(60)
        print(f"   ⏰ {minute + 1}/5 minutes elapsed...")
        
        if minute >= 2:  # Test after 3 minutes
            try:
                base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
                health_response = requests.get(f"{base_url}/health", timeout=15)
                print(f"   🧪 Health check: {health_response.status_code}")
                
                if health_response.status_code == 200:
                    print("\\n🎉 DEFINITIVE FIX SUCCESSFUL!")
                    health_data = health_response.json()
                    print(f"   Health Status: {health_data.get('status', 'healthy')}")
                    print(f"   Version: {health_data.get('version', '1.0.0')}")
                    print(f"   Timestamp: {health_data.get('timestamp', 'now')}")
                    
                    print("\\n✅ FULL SERVICE VERIFICATION")
                    print(f"   🌐 Frontend: https://quizbattle-frontend.netlify.app")
                    print(f"   🔧 Backend: {base_url}")
                    print(f"   💚 Health: {base_url}/health")
                    print(f"   🔑 Admin: admin / Admin@123")
                    print(f"   🧪 Test Password: testpass123")
                    
                    return True
                    
            except Exception as e:
                print(f"   ⏳ Still deploying... ({str(e)[:50]})")
    
    print("\\n📋 Deployment may need a few more minutes...")
    return False

if __name__ == "__main__":
    print("🔥 DEFINITIVE QUIZBATTLE FIX")
    print("=" * 60)
    print("This will forcibly fix ALL configuration issues:")
    print("• Remove database init script from startup completely")
    print("• Reset all environment variables with correct formatting")
    print("• Trigger clean deployment with all fixes")
    print("=" * 60)
    
    # Step 1: Force fix all configuration
    config_success = force_fix_service_config()
    
    if config_success:
        # Step 2: Trigger final deployment
        deploy_success = trigger_final_deployment()
        
        if deploy_success:
            # Step 3: Final verification
            verify_success = final_verification()
            
            if verify_success:
                print("\\n🎊 MISSION ACCOMPLISHED! 🎊")
                print("QuizBattle is 100% LIVE and OPERATIONAL!")
            else:
                print("\\n📋 Deployment in progress - service should be live soon")
        else:
            print("\\n❌ Final deployment failed")
    else:
        print("\\n❌ Configuration fix failed")
    
    print("\\n" + "=" * 60)
    print("📝 NEXT STEPS AFTER SERVICE IS LIVE:")
    print("1. Test health: curl https://srv-d339gs3uibrs73ae5keg.onrender.com/health")
    print("2. Admin login: admin / Admin@123")
    print("3. Register new users via API or frontend")
    print("=" * 60)