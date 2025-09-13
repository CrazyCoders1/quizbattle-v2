#!/usr/bin/env python3
"""
Debug AI providers individually to identify specific issues
"""
import requests
import json
from datetime import datetime
import sys
import os

# Load API keys
def load_api_keys():
    keys = {}
    try:
        with open('../api_keys.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    keys[key.strip()] = value.strip()
        print(f"✅ Loaded {len(keys)} API keys")
        return keys
    except Exception as e:
        print(f"❌ Error loading API keys: {e}")
        return {}

def test_deepseek(api_key):
    """Test DeepSeek API"""
    print("\n🤖 Testing DeepSeek API")
    print("-" * 30)
    
    try:
        # Test simple prompt
        prompt = """
Extract multiple choice questions from the following text. Return ONLY valid JSON array:
[{"question": "What is 2+2?", "options": ["1", "2", "3", "4"], "correct_answer": 3, "difficulty": "easy"}]

Text: What is 2+2? A) 1 B) 2 C) 3 D) 4
"""
        
        print(f"API Key: {api_key[:20]}...")
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1000,
                'temperature': 0.1
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ DeepSeek API working!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ DeepSeek API failed: {response.status_code}")
            print(f"Error Response: {response.text}")
            
            if response.status_code == 402:
                print("💳 Payment Required - Your account needs payment/credits")
            elif response.status_code == 401:
                print("🔑 Unauthorized - Check your API key")
            elif response.status_code == 429:
                print("⏱️ Rate Limited - Too many requests")
            
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek connection error: {e}")
        return False

def test_sambacloud(api_key):
    """Test SambaCloud API"""
    print("\n🌩️ Testing SambaCloud API")
    print("-" * 30)
    
    try:
        prompt = "Extract quiz questions from this content. Return JSON format: What is 2+2? A) 1 B) 2 C) 3 D) 4"
        
        print(f"API Key: {api_key[:20]}...")
        
        response = requests.post(
            'https://api.sambanova.ai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'Meta-Llama-3.1-8B-Instruct',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1000,
                'temperature': 0.2
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SambaCloud API working!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ SambaCloud API failed: {response.status_code}")
            print(f"Error Response: {response.text}")
            
            if response.status_code == 401:
                print("🔑 Unauthorized - Check your API key")
            elif response.status_code == 429:
                print("⏱️ Rate Limited - Too many requests")
            elif response.status_code == 403:
                print("🚫 Forbidden - Check account permissions")
            
            return False
            
    except Exception as e:
        print(f"❌ SambaCloud connection error: {e}")
        return False

def test_openai(api_key):
    """Test OpenAI API"""
    print("\n🤖 Testing OpenAI API")  
    print("-" * 30)
    
    try:
        prompt = "Extract multiple choice questions from this content. Return JSON: What is 2+2? A) 1 B) 2 C) 3 D) 4"
        
        print(f"API Key: {api_key[:20]}...")
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1000,
                'temperature': 0.1
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OpenAI API working!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ OpenAI API failed: {response.status_code}")
            print(f"Error Response: {response.text}")
            
            if response.status_code == 401:
                print("🔑 Unauthorized - Check your API key")
            elif response.status_code == 429:
                print("⏱️ Rate Limited - Check your usage limits")
            elif response.status_code == 403:
                print("🚫 Forbidden - Check account status")
            elif response.status_code == 402:
                print("💳 Payment Required - Check your billing")
            
            return False
            
    except Exception as e:
        print(f"❌ OpenAI connection error: {e}")
        return False

def test_llava(api_key):
    """Test LLaVA API (if available)"""
    print("\n👁️ Testing LLaVA API")
    print("-" * 30)
    
    # LLaVA might use different endpoint structure
    print(f"API Key: {api_key[:20]}...")
    print("⚠️ LLaVA API endpoint not implemented in this test")
    print("(This would typically be used for image processing)")
    return False

def test_network_connectivity():
    """Test basic network connectivity to AI services"""
    print("\n🌐 Testing Network Connectivity")
    print("-" * 35)
    
    test_urls = [
        ("DeepSeek", "https://api.deepseek.com"),
        ("SambaCloud", "https://api.sambanova.ai"),
        ("OpenAI", "https://api.openai.com"),
    ]
    
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {name}: Reachable (Status: {response.status_code})")
        except requests.exceptions.Timeout:
            print(f"⏱️ {name}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection Error")
        except Exception as e:
            print(f"⚠️ {name}: {type(e).__name__}")

def main():
    print("🔧 AI Provider Debug Tool")
    print("=" * 50)
    
    # Test network connectivity first
    test_network_connectivity()
    
    # Load API keys
    keys = load_api_keys()
    if not keys:
        print("❌ No API keys loaded, exiting")
        return
    
    # Test each provider
    results = {}
    
    if 'DeepSeek' in keys:
        results['DeepSeek'] = test_deepseek(keys['DeepSeek'])
    else:
        print("⚠️ DeepSeek key not found")
    
    if 'SambaCloud' in keys:
        results['SambaCloud'] = test_sambacloud(keys['SambaCloud'])  
    else:
        print("⚠️ SambaCloud key not found")
    
    if 'OpenAI' in keys:
        results['OpenAI'] = test_openai(keys['OpenAI'])
    else:
        print("⚠️ OpenAI key not found")
    
    if 'LLAVA' in keys:
        results['LLAVA'] = test_llava(keys['LLAVA'])
    else:
        print("⚠️ LLaVA key not found")
    
    # Summary
    print("\n📊 FINAL RESULTS")
    print("=" * 30)
    working_count = 0
    total_count = 0
    
    for provider, status in results.items():
        total_count += 1
        if status:
            working_count += 1
            print(f"✅ {provider}: WORKING")
        else:
            print(f"❌ {provider}: FAILED")
    
    print(f"\n🎯 Summary: {working_count}/{total_count} providers working")
    
    if working_count == 0:
        print("\n🚨 CRITICAL: No AI providers are working!")
        print("Common fixes:")
        print("1. Check API keys are valid and not expired")
        print("2. Ensure accounts have sufficient credits/payment")
        print("3. Check network connectivity and firewall")
        print("4. Verify API endpoint URLs are correct")
        print("5. Check rate limits and usage quotas")
    
    elif working_count < total_count:
        print(f"\n⚠️ WARNING: Only {working_count} out of {total_count} providers working")
        print("This is still functional since we have fallback mechanisms")
    
    else:
        print("\n🎉 SUCCESS: All AI providers are working!")

if __name__ == '__main__':
    main()