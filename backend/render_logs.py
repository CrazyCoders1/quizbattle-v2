#!/usr/bin/env python3
"""
Fetch and display Render deployment logs for QuizBattle backend debugging
"""
import requests
import json
import os
from datetime import datetime

def fetch_render_logs():
    """Fetch recent logs from Render service"""
    
    # Read service ID and API key from environment
    service_id = os.getenv('RENDER_SERVICE_ID', 'srv-cteo4c08fa8c73b22s2g')
    api_key = os.getenv('RENDER_API_KEY')
    
    if not api_key:
        print("⚠️  RENDER_API_KEY not found in environment")
        print("   Please set it to fetch logs from Render")
        return
    
    url = f"https://api.render.com/v1/services/{service_id}/logs"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    try:
        print(f"🔍 Fetching logs from Render service: {service_id}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Successfully fetched {len(logs)} log entries")
            
            # Display recent logs
            for log_entry in logs[-20:]:  # Show last 20 entries
                timestamp = log_entry.get('timestamp', 'Unknown time')
                message = log_entry.get('message', 'No message')
                print(f"[{timestamp}] {message}")
                
        else:
            print(f"❌ Failed to fetch logs: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error fetching logs: {str(e)}")

def check_render_service_status():
    """Check current service status"""
    service_id = os.getenv('RENDER_SERVICE_ID', 'srv-cteo4c08fa8c73b22s2g')
    api_key = os.getenv('RENDER_API_KEY')
    
    if not api_key:
        return
        
    url = f"https://api.render.com/v1/services/{service_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            service = response.json()
            print(f"📊 Service Status: {service.get('state', 'unknown')}")
            print(f"   Runtime: {service.get('runtime', 'unknown')}")
            print(f"   Last Deploy: {service.get('updatedAt', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Could not fetch service status: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("📋 RENDER SERVICE LOGS & STATUS")
    print("=" * 60)
    
    check_render_service_status()
    print()
    fetch_render_logs()