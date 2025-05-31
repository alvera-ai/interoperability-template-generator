#!/bin/bash

echo "🚀 Starting API Interoperability Template Generator..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️ Streamlit not found. Installing dependencies..."
    python3 setup.py
fi

# Start the application
echo "📋 Starting Streamlit application..."
python3 -m streamlit run app.py --server.port=8501 --server.address=localhost

echo "👋 Application stopped." 