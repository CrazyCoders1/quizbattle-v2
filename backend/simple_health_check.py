#!/usr/bin/env python3
import requests
import time
import json

def check_health():
    """Check if the service is responding to health checks"""
    service_url = "https://srv-d339gs3uibrs73ae5keg.onrender.com"
    
    print(f"🏥 Testing service health at {service_url}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        "/",
        "/health", 
        "/api/debug/health",
        "/api/setup"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{service_url}{endpoint}"
            print(f"🔍 Testing {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response (text): {response.text[:100]}...")
            else:
                print(f"   Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)}")
        
        print()

if __name__ == "__main__":
    check_health()