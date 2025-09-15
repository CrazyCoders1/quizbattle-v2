#!/usr/bin/env python3
"""
Manual deployment trigger - simple and direct
"""
import requests
import time
import json

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def trigger_manual_deployment():
    """Manually trigger deployment"""
    print("🚀 MANUAL DEPLOYMENT TRIGGER")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "clearCache": "clear"
        }
        
        print(f"Triggering deployment for service: {RENDER_SERVICE_ID}")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [201, 202]:  # Both Created and Accepted are valid
            print("✅ Deployment triggered successfully!")
            if response.text:
                try:
                    deploy_info = response.json()
                    deploy_id = deploy_info.get('id', 'unknown')
                    print(f"Deploy ID: {deploy_id}")
                except:
                    print("Deploy triggered but couldn't parse response")
            return True
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def wait_and_test():
    """Wait and test the service"""
    print("\\n⏳ Waiting 5 minutes for deployment...")
    
    for i in range(5):
        time.sleep(60)  # Wait 1 minute
        print(f"   Waiting... {i+1}/5 minutes")
    
    print("\\n🧪 Testing service...")
    
    try:
        base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
        
        # Test health
        health_response = requests.get(f"{base_url}/health", timeout=30)
        print(f"Health endpoint: {health_response.status_code}")
        
        if health_response.status_code == 200:
            print("✅ Service is responding!")
            health_data = health_response.json()
            print(f"Health status: {health_data.get('status', 'unknown')}")
            
            # Test root
            root_response = requests.get(f"{base_url}/", timeout=30)
            print(f"Root endpoint: {root_response.status_code}")
            
            if root_response.status_code == 200:
                print("\\n🎉 DEPLOYMENT SUCCESSFUL!")
                print(f"🌐 Frontend: https://quizbattle-frontend.netlify.app")
                print(f"🔧 Backend: {base_url}")
                print(f"💚 Health: {base_url}/health") 
                print("\\n🔑 Admin Access:")
                print("   Username: admin")
                print("   Password: Admin@123")
                
                # Test admin login
                try:
                    admin_data = {
                        "username": "admin",
                        "password": "Admin@123"
                    }
                    admin_response = requests.post(f"{base_url}/api/auth/admin/login", 
                                                 json=admin_data, timeout=30)
                    print(f"\\n📋 Admin Login Test: {admin_response.status_code}")
                    if admin_response.status_code == 200:
                        print("   ✅ Admin login working!")
                    else:
                        print(f"   ⚠️  Admin login issue: {admin_response.text[:100]}")
                except Exception as e:
                    print(f"   ❌ Admin login test failed: {e}")
                
                return True
        else:
            print(f"⚠️ Service not ready yet: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QUIZBATTLE MANUAL DEPLOYMENT")
    print("=" * 60)
    print("Fixes applied:")
    print("• psycopg2 compatibility (binary → standard)")
    print("• Auto-initialization disabled")  
    print("• Simple gunicorn startup")
    print("=" * 60)
    
    # Trigger deployment
    success = trigger_manual_deployment()
    
    if success:
        # Wait and test
        wait_and_test()
    else:
        print("\\n❌ Deployment trigger failed")
        print("Try manually via Render dashboard:")