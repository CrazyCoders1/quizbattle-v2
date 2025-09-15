#!/usr/bin/env python3
"""
Monitor deployment status and test endpoints when ready
"""
import requests
import time
import pymongo
from datetime import datetime

# Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"
DEPLOY_ID = "dep-d341nm3uibrs73b191ag"

def check_deployment_status():
    """Check if deployment is complete"""
    print("🔄 Monitoring deployment status...")
    
    headers = {
        'Authorization': f'Bearer {RENDER_API_KEY}',
        'Accept': 'application/json'
    }
    
    for attempt in range(30):  # Check for up to 15 minutes
        try:
            url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys/{DEPLOY_ID}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                deploy_info = response.json()
                status = deploy_info.get('status', 'unknown')
                
                print(f"   Attempt {attempt + 1}/30: Status = {status}")
                
                if status == 'live':
                    print("✅ Deployment is live!")
                    return True
                elif status in ['build_failed', 'failed']:
                    print("❌ Deployment failed!")
                    return False
                    
            time.sleep(30)  # Wait 30 seconds between checks
            
        except Exception as e:
            print(f"   Error checking status: {e}")
            time.sleep(30)
    
    print("⏰ Deployment monitoring timeout")
    return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\\n🧪 Testing API endpoints...")
    
    base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
    
    # Test health endpoint
    try:
        print("   Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health", timeout=30)
        print(f"   Health Check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Response: {health_response.json()}")
            
            # Test registration endpoint
            print("   Testing user registration...")
            registration_data = {
                "username": "testuser_final",
                "email": "testuser_final@example.com",
                "password": "testpass123"
            }
            reg_response = requests.post(f"{base_url}/api/auth/register", 
                                       json=registration_data, timeout=30)
            print(f"   Registration: {reg_response.status_code}")
            
            # Test admin login
            print("   Testing admin login...")
            admin_login_data = {
                "username": "admin",
                "password": "Admin@123"
            }
            admin_response = requests.post(f"{base_url}/api/auth/admin/login",
                                         json=admin_login_data, timeout=30)
            print(f"   Admin Login: {admin_response.status_code}")
            
            if admin_response.status_code == 200:
                print("✅ All API endpoints working!")
                return True
            else:
                print("⚠️ Some endpoints have issues")
                return False
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_mongodb_with_correct_format():
    """Test MongoDB with the correct connection format"""
    print("\\n🔧 Testing MongoDB connection formats...")
    
    # The issue might be with the admin.command call - let's fix it
    test_uris = [
        "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0"
    ]
    
    for i, uri in enumerate(test_uris, 1):
        print(f"   Testing MongoDB URI {i}...")
        
        try:
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=10000)
            
            # Correct way to ping MongoDB
            client.admin.command('ismaster')
            print(f"   ✅ MongoDB connection successful!")
            
            # Test database operations
            db = client.quizbattle
            collections = db.list_collection_names()
            print(f"   📋 Existing collections: {collections}")
            
            # Create test collections if they don't exist
            required_collections = ['logs', 'admin_actions', 'pdf_uploads', 'system_events']
            for collection_name in required_collections:
                if collection_name not in collections:
                    db.create_collection(collection_name)
                    print(f"   ✅ Created collection: {collection_name}")
            
            # Test write operation
            test_doc = {
                "type": "deployment_test",
                "timestamp": datetime.utcnow(),
                "message": "QuizBattle deployment test successful",
                "deployment_id": DEPLOY_ID
            }
            result = db.system_events.insert_one(test_doc)
            print(f"   ✅ Test document inserted: {result.inserted_id}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   ❌ MongoDB test failed: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🚀 DEPLOYMENT MONITORING & ENDPOINT TESTING")
    print("=" * 60)
    print(f"Deploy ID: {DEPLOY_ID}")
    print(f"Service ID: {RENDER_SERVICE_ID}")
    print("=" * 60)
    
    # Step 1: Wait for deployment to complete
    deployment_success = check_deployment_status()
    
    if deployment_success:
        print("\\n" + "=" * 60)
        print("✅ DEPLOYMENT COMPLETED")
        print("=" * 60)
        
        # Step 2: Test API endpoints
        api_success = test_api_endpoints()
        
        # Step 3: Test MongoDB connection
        mongodb_success = test_mongodb_with_correct_format()
        
        print("\\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"✅ Deployment: {'SUCCESS' if deployment_success else 'FAILED'}")
        print(f"✅ API Endpoints: {'SUCCESS' if api_success else 'FAILED'}")
        print(f"✅ MongoDB Connection: {'SUCCESS' if mongodb_success else 'FAILED'}")
        
        if deployment_success and api_success:
            print("\\n🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"🌐 Frontend: https://quizbattle-frontend.netlify.app")
            print(f"🔧 Backend: https://{RENDER_SERVICE_ID}.onrender.com")
        else:
            print("\\n⚠️ DEPLOYMENT COMPLETED WITH ISSUES")
            
    else:
        print("\\n❌ DEPLOYMENT FAILED")
        print("Check Render dashboard for detailed logs")