#!/usr/bin/env python3
"""
Check Python version compatibility for QuizBattle deployment
"""
import sys
import platform

print(f"🐍 Python Version Check:")
print(f"   Version: {sys.version}")
print(f"   Version Info: {sys.version_info}")
print(f"   Platform: {platform.platform()}")
print(f"   Machine: {platform.machine()}")

# Check if we're on the problematic Python 3.13
if sys.version_info >= (3, 13):
    print("⚠️  WARNING: Python 3.13+ detected!")
    print("   This may cause psycopg2 compatibility issues.")
    print("   Recommended: Use Python 3.11 or 3.12")
elif sys.version_info >= (3, 11):
    print("✅ Python version is compatible!")
else:
    print("⚠️  WARNING: Python version may be too old!")
    print("   Recommended: Use Python 3.11+")

# Test psycopg2 import
try:
    import psycopg2
    print("✅ psycopg2 import successful!")
except ImportError as e:
    print(f"❌ psycopg2 import failed: {e}")
    
    # Try to give helpful advice
    if "undefined symbol" in str(e):
        print("💡 This is likely a Python version compatibility issue")
        print("   Solution: Use Python 3.11 or downgrade psycopg2-binary")
    elif "No module named" in str(e):
        print("💡 psycopg2 is not installed")
        print("   Solution: pip install psycopg2-binary")

print("🏁 Python check complete!")