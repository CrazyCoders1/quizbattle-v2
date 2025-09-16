#!/usr/bin/env python3
"""
Test script to validate render.yaml configuration
"""

import yaml
import json

def test_render_yaml():
    """Test if render.yaml is valid"""
    try:
        with open('render.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        print("✅ render.yaml is valid YAML")
        print(json.dumps(config, indent=2))
        
        # Check for required fields
        services = config.get('services', [])
        if not services:
            print("❌ No services defined")
            return False
        
        service = services[0]
        required_fields = ['type', 'name', 'env']
        
        for field in required_fields:
            if field not in service:
                print(f"❌ Missing required field: {field}")
                return False
            print(f"✅ {field}: {service[field]}")
        
        # Check if runtime field is NOT present (should be removed)
        if 'runtime' in service:
            print(f"❌ Runtime field should be removed: {service['runtime']}")
            return False
        else:
            print("✅ Runtime field correctly removed")
        
        print("\n🎉 render.yaml configuration is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating render.yaml: {e}")
        return False

if __name__ == "__main__":
    test_render_yaml()