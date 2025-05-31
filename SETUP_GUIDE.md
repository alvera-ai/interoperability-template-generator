# Setup Guide

## Environment Configuration

### 1. API Key Setup

To use the Claude AI conversion template feature, you need to set up your Anthropic API key:

#### Create .env file:
```bash
cp .env.example .env
```

#### Edit .env file:
```bash
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here

# Database Configuration (optional)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=api_interop
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=your_password_here
```

#### Get your Anthropic API Key:
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up/Login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

### 2. Install Dependencies

```bash
# Create conda environment
conda create -n interoperability-template python=3.11 -y
conda activate interoperability-template

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run app.py
```

## Features Overview

### Core Features:
1. **OpenAPI Spec Upload** - Load and parse OpenAPI specifications
2. **Database Table Creation** - Execute CREATE TABLE commands
3. **JSON Data Insertion** - Insert JSON data into created tables
4. **Schema Conversion** - Convert API schemas to database formats

### Claude AI Features (requires API key):
5. **Template Generation** - Use Claude to generate conversion templates
6. **Template Application** - Apply templates to transform API responses
7. **Intelligent Mapping** - AI-powered field mapping and type conversion

## Security Notes

- The `.env` file is automatically ignored by git (see `.gitignore`)
- Never commit API keys to version control
- Use environment variables for production deployments
- The application will work without Claude features if no API key is provided

## Troubleshooting

### Claude Features Not Working:
1. Check if `.env` file exists and contains valid API key
2. Verify API key is active in Anthropic Console
3. Check console logs for authentication errors

### Database Issues:
1. SQLite is used by default (no setup required)
2. For PostgreSQL, configure connection details in `.env`
3. Ensure database exists and user has proper permissions

### Dependencies:
```bash
# If anthropic installation fails:
pip install anthropic --upgrade

# If streamlit issues:
pip install streamlit --upgrade
``` 