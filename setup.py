#!/usr/bin/env python3
"""
Setup script for the API Interoperability Template Generator
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    requirements = [
        "streamlit==1.28.1",
        "requests==2.31.0",
        "pandas==2.0.3",
        "sqlalchemy==2.0.21",
        "pyyaml==6.0.1",
        "jsonschema==4.19.1",
        "openapi-spec-validator==0.6.0"
    ]
    
    print("Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def validate_installation():
    """Validate that all required modules can be imported."""
    modules = [
        ("streamlit", "Streamlit"),
        ("requests", "Requests"),
        ("pandas", "Pandas"),
        ("sqlalchemy", "SQLAlchemy"),
        ("yaml", "PyYAML"),
        ("jsonschema", "JSON Schema"),
        ("openapi_spec_validator", "OpenAPI Spec Validator")
    ]
    
    print("\nValidating installation...")
    all_valid = True
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name} is available")
        except ImportError:
            print(f"❌ {name} is not available")
            all_valid = False
    
    return all_valid

def main():
    """Main setup function."""
    print("🚀 Setting up API Interoperability Template Generator")
    print(f"Python version: {sys.version}")
    
    # Install requirements
    if install_requirements():
        print("\n✅ All packages installed successfully!")
    else:
        print("\n❌ Some packages failed to install")
        return False
    
    # Validate installation
    if validate_installation():
        print("\n✅ Setup completed successfully!")
        print("\nTo run the application:")
        print("  python3 app.py")
        print("  or")
        print("  streamlit run app.py")
        return True
    else:
        print("\n❌ Setup validation failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 