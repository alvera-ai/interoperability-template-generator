# Setup Guide

## Environment Configuration

### 1. Configuration File Setup

#### Option A: Using config.py (Recommended)
```bash
# Copy the template to create your config
cp config_template.py config.py

# Edit config.py and replace this line:
# self.anthropic_api_key = self._get_env_var('ANTHROPIC_API_KEY')
# With:
# self.anthropic_api_key = "sk-ant-api03-your-actual-api-key-here"
```

#### Option B: Using .env file
```bash
# Copy example and add your API key
cp env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

### 2. API Key Setup

To use the Claude AI conversion template feature, you need to set up your Anthropic API key:

#### Get your Anthropic API Key:
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up/Login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `config.py` or `.env` file

### 3. Install Dependencies

```bash
# Create conda environment
conda create -n interoperability-template python=3.11 -y
conda activate interoperability-template

# Install requirements
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

## Features Overview

### Core Features:
1. **OpenAPI Spec Upload** - Load and parse OpenAPI specifications
2. **Database Table Creation** - Execute CREATE TABLE commands
3. **Schema Conversion** - Convert API schemas to database formats

### Claude AI Features (requires API key):
4. **Template Generation** - Use Claude to generate conversion templates
5. **Template Application** - Apply templates to transform API responses
6. **Intelligent Mapping** - AI-powered field mapping and type conversion
7. **API Response Conversion** - Convert API JSON to database format and insert

## Security Notes

- The `config.py` file is automatically ignored by git (see `.gitignore`)
- The `config_template.py` is safe to commit (no API keys)
- Never commit API keys to version control
- Use environment variables for production deployments
- The application will work without Claude features if no API key is provided

## File Structure

```
├── config_template.py  # Template file (safe to commit)
├── config.py          # Your local config (gitignored)
├── .env.example       # Environment template
├── .env               # Your environment file (gitignored)
```

## Troubleshooting

### Claude Features Not Working:
1. Check if `config.py` exists and contains valid API key
2. Verify API key is active in Anthropic Console
3. Check console logs for authentication errors
4. Ensure you copied `config_template.py` to `config.py`

### Database Issues:
1. SQLite is used by default (no setup required)
2. For PostgreSQL, configure connection details in `.env` or `config.py`
3. Ensure database exists and user has proper permissions

### Dependencies:
```bash
# If anthropic installation fails:
pip install anthropic --upgrade

# If streamlit issues:
pip install streamlit --upgrade
``` 