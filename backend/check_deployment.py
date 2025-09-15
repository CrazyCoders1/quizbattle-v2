#!/usr/bin/env python3
"""
Check current deployment status and manually trigger if needed
"""
import requests
import time

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def check_recent_deployments():
    """Check recent deployments"""
    print("🔍 CHECKING RECENT DEPLOYMENTS")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            deploys = response.json()
            
            print(f"Found {len(deploys)} recent deployments:")
            for i, deploy in enumerate(deploys[:5], 1):
                deploy_id = deploy.get('id', 'unknown')
                status = deploy.get('status', 'unknown')
                created_at = deploy.get('createdAt', 'unknown')
                commit = deploy.get('commit', {}).get('sha', 'unknown')[:8]
                
                print(f"   {i}. {deploy_id} - {status} - {created_at} - {commit}")
                
                if i == 1:  # Monitor the latest deployment
                    return deploy_id, status
            
        else:
            print(f"❌ Failed to get deployments: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return None, None

def monitor_deployment(deploy_id, initial_status):
    """Monitor specific deployment"""
    print(f"\\n⏳ MONITORING DEPLOYMENT: {deploy_id}")
    print("=" * 50)
    
    headers = {
        'Authorization': f'Bearer {RENDER_API_KEY}',
        'Accept': 'application/json'
    }
    
    current_status = initial_status
    
    for attempt in range(30):  # 15 minutes
        try:
            url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys/{deploy_id}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                deploy_info = response.json()
                status = deploy_info.get('status', 'unknown')
                
                if status != current_status:
                    print(f"   Status changed: {current_status} → {status}")
                    current_status = status
                else:
                    print(f"   [{attempt + 1:2d}/30] Status: {status}")
                
                if status == 'live':
                    print("\\n✅ DEPLOYMENT IS LIVE!")
                    return True
                elif status in ['build_failed', 'failed']:
                    print(f"\\n❌ DEPLOYMENT FAILED: {status}")
                    return False
                    
            time.sleep(30)
            
        except Exception as e:
            print(f"   Error: {e}")
            time.sleep(30)
    
    print(f"\\n⏰ Monitoring timeout - last status: {current_status}")
    return current_status == 'live'

def test_live_service():
    """Test if service is responding"""
    print("\\n🧪 TESTING LIVE SERVICE")
    print("=" * 50)
    
    base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health", timeout=30)
        print(f"   Health endpoint: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Health check: {health_data.get('status', 'unknown')}")
            
            # Test root endpoint
            root_response = requests.get(f"{base_url}/", timeout=30)
            print(f"   Root endpoint: {root_response.status_code}")
            
            if root_response.status_code == 200:
                print("\\n✅ SERVICE IS FULLY OPERATIONAL!")
                print(f"🌐 Frontend: https://quizbattle-frontend.netlify.app")
                print(f"🔧 Backend: {base_url}")
                print(f"💚 Health: {base_url}/health")
                print("\\n🔑 Admin Login:")
                print("   Username: admin")  
                print("   Password: Admin@123")
                return True
        
        print("\\n⚠️ Service responding but with issues")
        return False
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QUIZBATTLE DEPLOYMENT STATUS CHECK")
    print("=" * 60)
    
    # Check recent deployments
    deploy_id, status = check_recent_deployments()
    
    if deploy_id and status:
        if status in ['build_in_progress', 'update_in_progress', 'queued']:
            # Monitor ongoing deployment
            success = monitor_deployment(deploy_id, status)
            
        elif status == 'live':
            print("\\n✅ Latest deployment is already live!")
            success = True
            
        else:
            print(f"\\n⚠️ Latest deployment status: {status}")
            success = False
        
        if success:
            # Test the live service
            test_live_service()
        
    else:
        print("\\n❌ Could not determine deployment status")