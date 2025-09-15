#!/usr/bin/env python3
"""
Fix deployment issues and create a working configuration
"""
import requests
import time

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def fix_environment_variables():
    """Fix environment variable mismatches"""
    print("🔧 FIXING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    # Fix the environment variables to match what the app expects
    env_vars = [
        {"key": "DATABASE_URL", "value": "postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"},
        {"key": "MONGO_URI", "value": "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0"},
        {"key": "MONGODB_URI", "value": "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0"},
        {"key": "JWT_SECRET", "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"},
        {"key": "SECRET_KEY", "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"},
        {"key": "FLASK_ENV", "value": "production"},
        {"key": "PORT", "value": "5000"},
        {"key": "MONGODB_DB", "value": "quizbattle"}
    ]
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/env-vars"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.put(url, headers=headers, json=env_vars, timeout=60)
        if response.status_code == 200:
            print("✅ Environment variables updated")
            for var in env_vars:
                print(f"   → {var['key']}: Set")
            return True
        else:
            print(f"❌ Failed to update env vars: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_service_configuration():
    """Update service configuration for better compatibility"""
    print("\\n🔧 UPDATING SERVICE CONFIGURATION")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Update to use a simpler, more reliable startup process
        update_payload = {
            "startCommand": "gunicorn --bind 0.0.0.0:$PORT wsgi:app"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            print("✅ Service configuration updated")
            print("   → Start command: gunicorn --bind 0.0.0.0:$PORT wsgi:app")
            return True
        else:
            print(f"❌ Config update failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def trigger_deployment():
    """Trigger a new deployment"""
    print("\\n🚀 TRIGGERING DEPLOYMENT")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {"clearCache": "clear"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 201:
            deploy_info = response.json()
            deploy_id = deploy_info.get('id', 'unknown')
            print(f"✅ Deployment triggered: {deploy_id}")
            return deploy_id
        else:
            print(f"❌ Deploy failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def monitor_deployment(deploy_id):
    """Monitor deployment progress"""
    print("\\n⏳ MONITORING DEPLOYMENT")
    print("=" * 50)
    
    if not deploy_id:
        print("❌ No deploy ID to monitor")
        return False
    
    headers = {
        'Authorization': f'Bearer {RENDER_API_KEY}',
        'Accept': 'application/json'
    }
    
    for attempt in range(20):  # Monitor for 10 minutes
        try:
            url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys/{deploy_id}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                deploy_info = response.json()
                status = deploy_info.get('status', 'unknown')
                
                print(f"   Attempt {attempt + 1}/20: {status}")
                
                if status == 'live':
                    print("✅ Deployment successful!")
                    return True
                elif status in ['build_failed', 'failed']:
                    print(f"❌ Deployment failed: {status}")
                    return False
                    
            time.sleep(30)  # Wait 30 seconds
            
        except Exception as e:
            print(f"   Error: {e}")
            time.sleep(30)
    
    print("⏰ Monitoring timeout")
    return False

def test_endpoints():
    """Test if endpoints are working"""
    print("\\n🧪 TESTING ENDPOINTS")
    print("=" * 50)
    
    base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health", timeout=30)
        print(f"Health check: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health: {health_data}")
            
            # Test root endpoint
            root_response = requests.get(f"{base_url}/", timeout=30)
            print(f"Root endpoint: {root_response.status_code}")
            
            if root_response.status_code == 200:
                print("✅ All basic endpoints working!")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QUIZBATTLE DEPLOYMENT FIX")
    print("=" * 60)
    
    # Step 1: Fix environment variables
    env_fixed = fix_environment_variables()
    
    # Step 2: Update service configuration
    config_updated = update_service_configuration()
    
    if env_fixed and config_updated:
        # Step 3: Trigger deployment
        deploy_id = trigger_deployment()
        
        if deploy_id:
            # Step 4: Monitor deployment
            deployment_success = monitor_deployment(deploy_id)
            
            if deployment_success:
                # Step 5: Test endpoints
                endpoints_working = test_endpoints()
                
                print("\\n" + "=" * 60)
                print("📊 FINAL RESULTS")
                print("=" * 60)
                print(f"✅ Environment Fixed: {'YES' if env_fixed else 'NO'}")
                print(f"✅ Config Updated: {'YES' if config_updated else 'NO'}")
                print(f"✅ Deployment Success: {'YES' if deployment_success else 'NO'}")
                print(f"✅ Endpoints Working: {'YES' if endpoints_working else 'NO'}")
                
                if endpoints_working:
                    print("\\n🎉 DEPLOYMENT SUCCESSFUL!")
                    print(f"🌐 Backend URL: {base_url}")
                    print(f"🔗 Health Check: {base_url}/health")
                    print(f"🔗 API Root: {base_url}/api/")
                else:
                    print("\\n⚠️ Deployment completed but endpoints need verification")
            else:
                print("\\n❌ Deployment failed")
        else:
            print("\\n❌ Failed to trigger deployment")
    else:
        print("\\n❌ Failed to fix environment/config")