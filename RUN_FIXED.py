#!/usr/bin/env python3
"""
Run Fixed Project Setu
"""

import subprocess
import sys
import os

def main():
    print("🏥 Starting Project Setu...")
    
    # Change to project directory
    os.chdir("project_setu")
    
    # Kill any existing streamlit processes
    try:
        subprocess.run(["pkill", "-f", "streamlit"], check=False)
    except:
        pass
    
    # Launch the fixed interface
    cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_beautiful.py",
        "--server.port=8506"
    ]
    
    print("🚀 FIXED interface at: http://localhost:8506")
    print("🔐 Credentials: ABHA ID: 12-3456-7890-1234, Password: testpassword")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
