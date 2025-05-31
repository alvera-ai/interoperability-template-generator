# Quick Start Guide

## 🚀 Running the Application

### Method 1: Direct Streamlit Command (Recommended)
If you've run the setup and packages are installed:

```bash
# Find your streamlit installation
python3 -c "import streamlit; print('Streamlit installed successfully')"

# Run the application
python3 -m streamlit run app.py
```

### Method 2: Using Full Path (macOS/Linux)
If the streamlit command isn't in your PATH:

```bash
# Check your user library path
python3 -c "import site; print(site.USER_BASE)"

# Run using full path (replace with your actual path)
/Users/[username]/Library/Python/3.9/bin/streamlit run app.py
```

### Method 3: Setup and Run
If you haven't installed dependencies yet:

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run the application
python3 -m streamlit run app.py
```

### Method 4: Alternative Setup
If you encounter issues with the provided setup:

```bash
# Install core dependencies only
python3 -m pip install streamlit requests pandas sqlalchemy pyyaml jsonschema openapi-spec-validator

# Run the application
python3 -m streamlit run app.py
```

## 🌐 Accessing the Application

Once running, the application will be available at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://[your-ip]:8501

## 🧪 Testing the Application

1. **Load Example OpenAPI Spec**:
   - Go to the "Upload File" option
   - Upload `example_openapi.yaml`
   - Click "Load OpenAPI Spec"

2. **Test an Endpoint**:
   - Enter a prompt: "Get user information for user ID 1"
   - Select `/users/{userId}` endpoint
   - The app will auto-populate `userId` with `1`
   - Click "Execute API Call"

3. **View Results**:
   - Check the API response
   - Go to "Database Results" page to see stored data
   - Explore "API Documentation" for spec details

## 🛠️ Troubleshooting

### PowerShell Issues
If you encounter PowerShell rendering problems:
- Use Terminal or Command Prompt instead
- Use the direct commands above rather than the helper scripts

### Python Path Issues
If modules aren't found:
```bash
# Check your Python installation
which python3
python3 --version

# Check site packages
python3 -c "import site; print(site.getsitepackages())"
```

### Permission Issues
If you get permission errors:
```bash
# Install with user flag
python3 -m pip install --user -r requirements.txt
```

### Port Already in Use
If port 8501 is busy:
```bash
# Use a different port
python3 -m streamlit run app.py --server.port=8502
```

## 📱 Alternative Access

If you can't access via browser:
- Check firewall settings
- Try http://127.0.0.1:8501
- Look for the "Network URL" in the terminal output

## 🆘 Getting Help

If you're still having issues:
1. Check that Python 3.8+ is installed
2. Verify all dependencies are installed
3. Try running each component individually
4. Check the terminal for error messages

The application includes comprehensive error handling and logging to help diagnose issues. 