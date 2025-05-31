#!/usr/bin/env python3
"""
Simple script to run the API Interoperability Template Generator
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import requests
        import pandas
        import sqlalchemy
        import yaml
        import jsonschema
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main function to run the application."""
    print("🚀 Starting API Interoperability Template Generator...")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found in current directory")
        sys.exit(1)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 