#!/usr/bin/env python3
"""
Diagnose deployment issues and fix problems
"""
import requests
import pymongo
import os

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"

def check_deployment_logs():
    """Get deployment logs to see what failed"""
    print("🔍 CHECKING DEPLOYMENT LOGS")
    print("=" * 50)
    
    try:
        # Get recent deploys
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            deploys = response.json()
            
            # Get the most recent deploy
            if deploys:
                latest_deploy = deploys[0]
                deploy_id = latest_deploy.get('id', 'unknown')
                status = latest_deploy.get('status', 'unknown')
                created_at = latest_deploy.get('createdAt', 'unknown')
                
                print(f"Latest Deploy ID: {deploy_id}")
                print(f"Status: {status}")
                print(f"Created: {created_at}")
                
                # Get deploy logs
                logs_url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys/{deploy_id}/logs"
                logs_response = requests.get(logs_url, headers=headers, timeout=30)
                
                if logs_response.status_code == 200:
                    logs = logs_response.json()
                    print("\\n📋 DEPLOY LOGS (last 10 entries):")
                    print("-" * 50)
                    
                    for log_entry in logs[-10:]:
                        timestamp = log_entry.get('timestamp', 'Unknown')
                        message = log_entry.get('message', 'No message')
                        print(f"[{timestamp}] {message}")
                else:
                    print(f"❌ Failed to get logs: {logs_response.status_code}")
            else:
                print("❌ No deploys found")
        else:
            print(f"❌ Failed to get deploys: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def test_mongodb_connection():
    """Test different MongoDB URI formats"""
    print("\\n🔍 TESTING MONGODB CONNECTION")
    print("=" * 50)
    
    # Try different URI formats
    test_uris = [
        "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.mongodb.net/quizbattle?retryWrites=true&w=majority",
        "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0",
        "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority"
    ]
    
    for i, uri in enumerate(test_uris, 1):
        print(f"\\n🧪 Testing URI format {i}:")
        print(f"   {uri[:50]}...")
        
        try:
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
            db = client.quizbattle
            
            # Test connection
            result = db.admin.command('ping')
            print(f"   ✅ SUCCESS: {result}")
            
            # Get cluster info
            server_info = client.server_info()
            print(f"   📊 MongoDB Version: {server_info.get('version', 'unknown')}")
            
            client.close()
            return uri
            
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
    
    return None

def fix_deployment_issues():
    """Fix the deployment issues"""
    print("\\n🔧 FIXING DEPLOYMENT ISSUES")
    print("=" * 50)
    
    # 1. Test and fix MongoDB URI
    working_uri = test_mongodb_connection()
    if working_uri:
        print(f"\\n✅ Found working MongoDB URI")
        
        # Update environment variables with correct URI
        env_vars = [
            {"key": "DATABASE_URL", "value": "postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"},
            {"key": "MONGODB_URI", "value": working_uri},
            {"key": "SECRET_KEY", "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"},
            {"key": "JWT_SECRET", "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"},
            {"key": "FLASK_ENV", "value": "production"},
            {"key": "PORT", "value": "5000"}
        ]
        
        try:
            url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/env-vars"
            headers = {
                'Authorization': f'Bearer {RENDER_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.put(url, headers=headers, json=env_vars, timeout=60)
            if response.status_code == 200:
                print("✅ Updated environment variables with correct MongoDB URI")
            else:
                print(f"❌ Failed to update env vars: {response.status_code}")
        except Exception as e:
            print(f"❌ Error updating env vars: {e}")
    
    # 2. Trigger new deployment
    print("\\n🔄 Triggering new deployment...")
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
            print(f"✅ New deployment triggered: {deploy_id}")
            print("   ⏳ Wait 5-10 minutes for deployment to complete")
            return deploy_id
        else:
            print(f"❌ Failed to trigger deploy: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error triggering deploy: {e}")
    
    return None

def check_service_status():
    """Check current service status"""
    print("\\n📊 CHECKING SERVICE STATUS")
    print("=" * 50)
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            service = response.json()
            print(f"Service Name: {service.get('name', 'unknown')}")
            print(f"Service State: {service.get('state', 'unknown')}")
            print(f"Runtime: {service.get('runtime', 'unknown')}")
            print(f"Build Command: {service.get('buildCommand', 'unknown')}")
            print(f"Start Command: {service.get('startCommand', 'unknown')}")
            print(f"Root Directory: {service.get('rootDir', 'unknown')}")
            print(f"Repository: {service.get('repo', 'unknown')}")
            print(f"Last Updated: {service.get('updatedAt', 'unknown')}")
        else:
            print(f"❌ Failed to get service status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking service status: {e}")

if __name__ == "__main__":
    print("🚀 QUIZBATTLE DEPLOYMENT DIAGNOSTICS")
    print("=" * 60)
    
    check_service_status()
    check_deployment_logs()
    fix_deployment_issues()
    
    print("\\n" + "=" * 60)
    print("📝 NEXT STEPS:")
    print("1. Wait 5-10 minutes for new deployment to complete")
    print("2. Check https://srv-d339gs3uibrs73ae5keg.onrender.com/health")
    print("3. Run production verification script")
    print("=" * 60)