# API Interoperability Template Generator

A powerful Streamlit application for testing APIs using OpenAPI specifications with schema validation and database storage.

## 🚀 Features

- **OpenAPI Specification Support**: Load OpenAPI specs via file upload, URL, or direct paste
- **Schema Validation**: Validate API responses against JSON schemas
- **Interactive Testing**: User-friendly interface for API endpoint testing
- **Database Storage**: Store all API call results for future reference
- **Multiple Input Methods**: Support for YAML and JSON OpenAPI specifications
- **Real-time Results**: View API responses and validation results immediately
- **History Tracking**: Browse previous API calls and their results

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd interoperability-template-generator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

4. **Open your browser** and navigate to `http://localhost:8501`

## 💡 Usage

### 1. Load OpenAPI Specification

Choose one of three methods to load your OpenAPI specification:

- **Upload File**: Upload a `.yaml`, `.yml`, or `.json` file
- **Paste Content**: Directly paste your OpenAPI specification
- **URL**: Provide a URL to fetch the specification

### 2. Define Response Schema (Optional)

Provide a JSON schema to validate API responses. Example:

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "email": {"type": "string", "format": "email"}
  },
  "required": ["id", "name"]
}
```

### 3. Enter User Prompt

Describe what you want to test. The application will attempt to extract parameters from your prompt automatically.

### 4. Execute API Calls

- Select an endpoint from the available GET endpoints
- Configure parameters (auto-populated from your prompt when possible)
- Add custom headers if needed
- Execute the API call and view results

### 5. View Results

- See real-time API responses
- Validate responses against your schema
- All results are automatically stored in the database

## 📊 Database Results

Navigate to the "Database Results" page to:

- View recent API call history
- Filter and search through stored results
- View detailed information about specific API calls
- Analyze response patterns and status codes

## 📚 API Documentation

The "API Documentation" page provides:

- Overview of the loaded OpenAPI specification
- Detailed endpoint documentation
- Parameter descriptions and requirements
- Response schemas and examples

## 🏗️ Project Structure

```
interoperability-template-generator/
├── app.py                 # Main Streamlit application
├── database.py            # Database management module
├── api_handler.py         # API handling and OpenAPI processing
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── example_openapi.yaml   # Example OpenAPI specification
└── api_results.db        # SQLite database (created automatically)
```

## 🔧 Configuration

The application uses SQLite for data storage by default. The database file (`api_results.db`) is created automatically in the project directory.

### Database Tables

1. **api_results**: Stores API call results
   - `id`: Primary key
   - `timestamp`: When the call was made
   - `user_prompt`: User's description
   - `api_endpoint`: Called endpoint
   - `schema_used`: Validation schema
   - `response_data`: API response
   - `status_code`: HTTP status code
   - `response_headers`: Response headers

2. **openapi_specs**: Stores OpenAPI specifications
   - `id`: Primary key
   - `timestamp`: When the spec was loaded
   - `spec_name`: Name/identifier
   - `spec_content`: Full specification content

## 🧪 Example Usage

1. Load the provided `example_openapi.yaml` file
2. Enter a prompt like: "Get user information for user ID 123"
3. Select the `/users/{userId}` endpoint
4. The application will auto-populate `userId` with `123`
5. Execute the call and view results

## 🛡️ Error Handling

The application includes comprehensive error handling for:

- Invalid OpenAPI specifications
- Network connectivity issues
- Invalid JSON schemas
- API endpoint errors
- Database operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the application logs for error messages
2. Ensure your OpenAPI specification is valid
3. Verify network connectivity for external APIs
4. Review the database permissions

## 🔮 Future Enhancements

- Support for POST, PUT, DELETE methods
- Advanced parameter extraction using NLP
- Export results to various formats
- API performance analytics
- Authentication handling
- Bulk testing capabilities
- Custom validation rules
