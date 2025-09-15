#!/usr/bin/env python3
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_deployment_logs():
    """Get detailed deployment logs from Render API"""
    api_key = os.getenv('RENDER_API_KEY')
    service_id = "srv-d339gs3uibrs73ae5keg"
    
    if not api_key:
        print("❌ RENDER_API_KEY not found in environment")
        return
        
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Fetching recent deployments...")
    
    # Get recent deployments
    response = requests.get(
        f"https://api.render.com/v1/services/{service_id}/deploys",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get deployments: {response.status_code}")
        print(response.text)
        return
        
    deployments = response.json()
    if not deployments:
        print("❌ No deployments found")
        return
        
    # Get the latest deployment
    latest_deploy = deployments[0]
    deploy_id = latest_deploy['id']
    status = latest_deploy.get('status', 'unknown')
    created = latest_deploy.get('createdAt', 'unknown')
    
    print(f"📋 Latest Deployment:")
    print(f"   ID: {deploy_id}")
    print(f"   Status: {status}")
    print(f"   Created: {created}")
    print()
    
    # Get logs for this deployment
    print("📝 Fetching build logs...")
    
    logs_response = requests.get(
        f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}/logs",
        headers=headers
    )
    
    if logs_response.status_code != 200:
        print(f"❌ Failed to get logs: {logs_response.status_code}")
        print(logs_response.text)
        return
        
    logs_data = logs_response.json()
    
    if logs_data:
        print("🔍 BUILD LOGS:")
        print("=" * 60)
        for log_entry in logs_data[-50:]:  # Show last 50 log entries
            timestamp = log_entry.get('timestamp', '')
            message = log_entry.get('message', '')
            print(f"[{timestamp}] {message}")
    else:
        print("❌ No logs available")
        
if __name__ == "__main__":
    get_deployment_logs()