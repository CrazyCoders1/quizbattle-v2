#!/usr/bin/env python3
"""
Update Render environment variables to fix missing SECRET_KEY and MONGODB_URI
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_render_env_variables():
    """Update Render service environment variables"""
    
    service_id = os.getenv('RENDER_SERVICE_ID', 'srv-cteo4c08fa8c73b22s2g')
    api_key = os.getenv('RENDER_API_KEY')
    
    if not api_key:
        print("❌ RENDER_API_KEY not found in environment")
        print("   Please set it in your .env file to update Render configuration")
        return False
    
    # Environment variables to set/update
    env_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'MONGODB_URI': os.getenv('MONGODB_URI'),
        'SECRET_KEY': os.getenv('SECRET_KEY'), 
        'JWT_SECRET': os.getenv('JWT_SECRET'),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'production'),
        'PORT': os.getenv('PORT', '5000')
    }
    
    print("=" * 60)
    print("🔧 UPDATING RENDER ENVIRONMENT VARIABLES")
    print("=" * 60)
    print(f"Service ID: {service_id}")
    
    # Prepare environment variables for Render API
    env_vars_list = []
    for key, value in env_vars.items():
        if value:
            env_vars_list.append({
                'key': key,
                'value': value
            })
            print(f"✅ Setting {key}: {value[:30]}...")
        else:
            print(f"⚠️  Skipping {key}: not set locally")
    
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = env_vars_list
    
    try:
        print(f"\n🚀 Sending update request to Render...")
        response = requests.put(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Environment variables updated successfully!")
            
            # Display updated variables
            for env_var in result:
                key = env_var.get('key', 'Unknown')
                print(f"   → {key}: Set")
                
            return True
            
        else:
            print(f"❌ Failed to update environment variables")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating environment variables: {str(e)}")
        return False

def trigger_render_redeploy():
    """Trigger a redeploy to apply environment variable changes"""
    
    service_id = os.getenv('RENDER_SERVICE_ID', 'srv-cteo4c08fa8c73b22s2g')
    api_key = os.getenv('RENDER_API_KEY')
    
    if not api_key:
        return False
    
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'clearCache': 'clear'
    }
    
    try:
        print(f"\n🔄 Triggering redeploy with cache clear...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 201:
            deploy = response.json()
            deploy_id = deploy.get('id', 'Unknown')
            print(f"✅ Redeploy triggered successfully!")
            print(f"   Deploy ID: {deploy_id}")
            print(f"   Status: {deploy.get('status', 'Unknown')}")
            return True
            
        else:
            print(f"❌ Failed to trigger redeploy")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering redeploy: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Render Environment Variables Update")
    
    # Update environment variables
    env_updated = update_render_env_variables()
    
    if env_updated:
        # Trigger redeploy
        deploy_triggered = trigger_render_redeploy()
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        
        if deploy_triggered:
            print("✅ Configuration updated and redeploy triggered!")
            print("   → Environment variables are now set correctly")
            print("   → Service is redeploying with new configuration")
            print("\n⏳ Wait 3-5 minutes for deployment to complete")
            print("   Then run: python verify_production.py")
        else:
            print("⚠️  Environment updated but redeploy failed")
            print("   → Go to Render dashboard and manually trigger redeploy")
    else:
        print("❌ Failed to update environment variables")
        print("   → Check your RENDER_API_KEY and try again")