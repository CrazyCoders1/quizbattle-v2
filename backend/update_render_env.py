#!/usr/bin/env python3
"""
Update Render service environment variables
"""
import requests

# Render API configuration
SERVICE_ID = 'srv-d339gs3uibrs73ae5keg'
API_KEY = 'rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi'

def update_env_vars():
    url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Environment variables to set
    env_vars = {
        'DATABASE_URL': 'postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require',
        'MONGO_URI': 'mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0',
        'JWT_SECRET': 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0',
        'FLASK_ENV': 'production'
    }
    
    print('Updating Render environment variables...')
    
    # Get existing environment variables
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'Failed to get existing variables: {response.status_code}')
        return False
    
    existing_vars = {var['key']: var['id'] for var in response.json()}
    
    # Update/create each environment variable
    for key, value in env_vars.items():
        print(f'Setting {key}...')
        
        if key in existing_vars:
            # Update existing variable
            update_url = f'{url}/{existing_vars[key]}'
            response = requests.put(update_url, headers=headers, json={'key': key, 'value': value})
        else:
            # Create new variable
            response = requests.post(url, headers=headers, json={'key': key, 'value': value})
        
        if response.status_code in [200, 201]:
            print(f'✅ {key} updated successfully')
        else:
            print(f'❌ Failed to update {key}: {response.status_code}')
    
    return True

def trigger_deploy():
    url = f'https://api.render.com/v1/services/{SERVICE_ID}/deploys'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print('Triggering redeploy...')
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        deploy_data = response.json()
        deploy_id = deploy_data.get('id', 'unknown')
        print(f'✅ Deploy triggered successfully - Deploy ID: {deploy_id}')
        return True
    else:
        print(f'❌ Deploy failed: {response.status_code}')
        return False

if __name__ == '__main__':
    if update_env_vars():
        trigger_deploy()
        print('🎉 Environment update and redeploy initiated!')
    else:
        print('❌ Failed to update environment variables')