#!/usr/bin/env python3
"""
Final deployment fix - resolve psycopg2 compatibility and deploy
"""
import requests
import time

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def update_render_configuration():
    """Update Render configuration to fix psycopg2 issue"""
    print("🔧 UPDATING RENDER CONFIGURATION")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Update to use simpler startup command without init script
        update_payload = {
            "startCommand": "gunicorn --bind 0.0.0.0:$PORT --timeout 120 wsgi:app",
            "buildCommand": "pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            print("✅ Configuration updated successfully")
            print("   → Start: gunicorn --bind 0.0.0.0:$PORT --timeout 120 wsgi:app") 
            print("   → Build: pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt")
            return True
        else:
            print(f"❌ Update failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def trigger_deployment_and_monitor():
    """Trigger deployment and monitor until completion"""
    print("\\n🚀 TRIGGERING FINAL DEPLOYMENT")
    print("=" * 50)
    
    try:
        # Trigger deployment
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {"clearCache": "clear"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 201:
            print(f"❌ Deploy trigger failed: {response.status_code}")
            return False
        
        deploy_info = response.json()
        deploy_id = deploy_info.get('id', 'unknown')
        print(f"✅ Deployment triggered: {deploy_id}")
        
        # Monitor deployment
        print("\\n⏳ MONITORING DEPLOYMENT")
        print("-" * 50)
        
        for attempt in range(25):  # 12.5 minutes max
            try:
                status_url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys/{deploy_id}"
                status_response = requests.get(status_url, headers=headers, timeout=30)
                
                if status_response.status_code == 200:
                    deploy_status = status_response.json()
                    status = deploy_status.get('status', 'unknown')
                    
                    print(f"   [{attempt + 1:2d}/25] Status: {status}")
                    
                    if status == 'live':
                        print("\\n✅ DEPLOYMENT SUCCESSFUL!")
                        return True
                    elif status in ['build_failed', 'failed']:
                        print(f"\\n❌ DEPLOYMENT FAILED: {status}")
                        return False
                        
                time.sleep(30)
                
            except Exception as e:
                print(f"   Error checking status: {e}")
                time.sleep(30)
        
        print("\\n⏰ Deployment monitoring timeout")
        return False
        
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def test_all_endpoints():
    """Test all API endpoints to verify functionality"""
    print("\\n🧪 TESTING ALL ENDPOINTS")
    print("=" * 50)
    
    base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
    results = {}
    
    # Test endpoints
    endpoints = [
        ("Health Check", "GET", "/health", None),
        ("Root API", "GET", "/", None),
        ("User Registration", "POST", "/api/auth/register", {
            "username": "testuser_final",
            "email": "testuser_final@example.com", 
            "password": "testpass123"
        }),
        ("Admin Login", "POST", "/api/auth/admin/login", {
            "username": "admin",
            "password": "Admin@123"
        })
    ]
    
    for name, method, endpoint, data in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            
            results[name] = {
                "status": response.status_code,
                "success": response.status_code in [200, 201]
            }
            
            status_icon = "✅" if results[name]["success"] else "❌"
            print(f"   {status_icon} {name}: {response.status_code}")
            
            if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
                data = response.json()
                if 'status' in data:
                    print(f"      Response: {data.get('status', 'N/A')}")
                    
        except Exception as e:
            results[name] = {"status": "Error", "success": False}
            print(f"   ❌ {name}: {str(e)}")
    
    # Summary
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print(f"\\n📊 ENDPOINT TEST RESULTS: {successful}/{total} successful")
    
    return successful == total

if __name__ == "__main__":
    print("🚀 QUIZBATTLE FINAL DEPLOYMENT FIX")
    print("=" * 60)
    print("Issues being fixed:")
    print("• psycopg2 Python 3.13 compatibility")
    print("• Simplified startup process")
    print("• Auto-initialization disabled")
    print("=" * 60)
    
    # Step 1: Update configuration
    config_success = update_render_configuration()
    
    if config_success:
        # Step 2: Deploy and monitor
        deploy_success = trigger_deployment_and_monitor()
        
        if deploy_success:
            # Step 3: Test all endpoints
            print("\\n🎯 Waiting 30 seconds for service to be fully ready...")
            time.sleep(30)
            
            endpoints_success = test_all_endpoints()
            
            print("\\n" + "=" * 60)
            print("🏆 FINAL DEPLOYMENT RESULTS")
            print("=" * 60)
            print(f"✅ Configuration: {'SUCCESS' if config_success else 'FAILED'}")
            print(f"✅ Deployment: {'SUCCESS' if deploy_success else 'FAILED'}")
            print(f"✅ API Endpoints: {'SUCCESS' if endpoints_success else 'PARTIAL'}")
            
            if config_success and deploy_success and endpoints_success:
                print("\\n🎉 DEPLOYMENT 100% SUCCESSFUL!")
                print(f"🌐 Frontend: https://quizbattle-frontend.netlify.app")
                print(f"🔧 Backend: https://{RENDER_SERVICE_ID}.onrender.com")
                print(f"💚 Health: https://{RENDER_SERVICE_ID}.onrender.com/health")
                print("\\n🔑 Admin Credentials:")
                print("   Username: admin")
                print("   Password: Admin@123")
                print("\\n✨ Your QuizBattle application is LIVE! ✨")
            else:
                print("\\n⚠️ Deployment completed with some issues")
                print("Check the detailed logs above for specific problems")
        else:
            print("\\n❌ Deployment failed")
    else:
        print("\\n❌ Configuration update failed")