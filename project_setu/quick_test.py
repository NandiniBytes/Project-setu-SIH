#!/usr/bin/env python3
"""
Project Setu - Quick Test Script
Simple testing without complex dependencies.
"""

import sys
from pathlib import Path
import json

def test_basic_setup():
    """Test basic project setup"""
    print("🧪 Project Setu - Quick Test")
    print("=" * 40)
    
    # Test 1: File structure
    print("\n📁 Testing file structure...")
    required_files = [
        "main.py", "streamlit_app.py", "requirements.txt",
        "models.py", "schemas.py", "database.py"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {missing}")
    else:
        print("✅ All core files present")
    
    # Test 2: Data files
    print("\n💾 Testing data files...")
    codesystem_file = Path("../CodeSystem-NAMASTE.json")
    if codesystem_file.exists():
        try:
            with open(codesystem_file, 'r') as f:
                data = json.load(f)
            concepts = len(data.get('concept', []))
            print(f"✅ CodeSystem found with {concepts} concepts")
        except Exception as e:
            print(f"❌ CodeSystem error: {e}")
    else:
        print("❌ CodeSystem-NAMASTE.json not found")
    
    # Test 3: Basic imports
    print("\n📦 Testing basic imports...")
    try:
        import fastapi
        import streamlit
        import pandas
        print("✅ Core packages available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
    
    # Test 4: Simple module test
    print("\n🔧 Testing modules...")
    try:
        from models import Doctor
        print("✅ Models can be imported")
    except Exception as e:
        print(f"⚠️ Model import issue: {e}")
    
    print("\n" + "=" * 40)
    print("🚀 Quick test complete!")
    print("\nNext steps:")
    print("1. Install missing packages: pip install -r requirements.txt")
    print("2. Start FastAPI: python3 run_fastapi.py")
    print("3. Start Streamlit: python3 run_streamlit.py")

if __name__ == "__main__":
    test_basic_setup()
