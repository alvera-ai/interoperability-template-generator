# API Interoperability Template Generator

A powerful Streamlit application for testing APIs using OpenAPI specifications with PostgreSQL/SQLite database integration and table creation capabilities.

## 🚀 Features

- **OpenAPI Specification Support**: Load OpenAPI specs via file upload, URL, or direct paste
- **Database Table Creation**: Execute CREATE TABLE commands in PostgreSQL or SQLite
- **Dual Database Support**: Choose between PostgreSQL and SQLite
- **Interactive Testing**: User-friendly interface for API endpoint testing
- **Database Storage**: Store all API call results for future reference
- **Table Metadata Tracking**: Track created tables and their creation commands
- **Multiple Input Methods**: Support for YAML and JSON OpenAPI specifications
- **Real-time Results**: View API responses and table creation results immediately
- **History Tracking**: Browse previous API calls and created tables

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- PostgreSQL (optional, for PostgreSQL mode)

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

### 1. Configure Database (New!)

Navigate to "Database Settings" to choose your database:

**SQLite (Default)**:
- No setup required
- Local file storage
- Great for development and testing

**PostgreSQL**:
- Configure connection details
- Production-ready
- Better for concurrent usage

### 2. Load OpenAPI Specification

Choose one of three methods to load your OpenAPI specification:

- **Upload File**: Upload a `.yaml`, `.yml`, or `.json` file
- **Paste Content**: Directly paste your OpenAPI specification
- **URL**: Provide a URL to fetch the specification

### 3. Create Database Tables (New!)

Provide a CREATE TABLE command to create tables for storing API response data:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Enter User Prompt

Describe what you want to test, including table creation context:
"Get user information for user ID 1 and prepare users table for data storage"

### 5. Execute Operations

- **Create Table**: Execute your CREATE TABLE command
- **Test API**: Select endpoints and configure parameters
- **Store Results**: All results are automatically stored with table metadata

### 6. View Results

- See real-time API responses
- Track created tables and their schemas
- All results are stored with table creation context

## 📊 New Pages

### Created Tables
- View all tables created through the application
- See table schemas and creation commands
- Track when and why tables were created

### Database Settings
- Switch between SQLite and PostgreSQL
- Configure PostgreSQL connection details
- View current database status

## 🏗️ Project Structure

```
interoperability-template-generator/
├── app.py                 # Main Streamlit application (updated)
├── database.py            # Database management with PostgreSQL support
├── api_handler.py         # API handling and OpenAPI processing
├── requirements.txt       # Python dependencies (includes psycopg2)
├── README.md             # This file
├── example_openapi.yaml   # Example OpenAPI specification
├── setup.py              # Updated setup script
└── api_results.db        # SQLite database (created automatically)
```

## 🔧 Configuration

### SQLite Mode (Default)
- Database file (`api_results.db`) created automatically
- No additional setup required
- Perfect for development and single-user scenarios

### PostgreSQL Mode
Configure these connection parameters:
- **Host**: PostgreSQL server address
- **Port**: Database port (default: 5432)
- **Database**: Database name
- **Username**: Database user
- **Password**: User password

### Database Tables

Both SQLite and PostgreSQL support these tables:

1. **api_results**: Stores API call results
   - Added: `created_table_name`, `create_table_command`

2. **openapi_specs**: Stores OpenAPI specifications

3. **created_tables_metadata** (New): Tracks created tables
   - `table_name`: Name of the created table
   - `create_command`: The SQL command used
   - `created_by_prompt`: User prompt that triggered creation
   - `timestamp`: When the table was created

## 🧪 Example Usage

1. **Configure Database**:
   - Go to "Database Settings"
   - Choose PostgreSQL or keep SQLite
   - Apply configuration

2. **Load OpenAPI Spec**:
   - Upload `example_openapi.yaml`
   - Click "Load OpenAPI Spec"

3. **Create a Table**:
   ```sql
   CREATE TABLE test_users (
       id INTEGER PRIMARY KEY,
       name TEXT NOT NULL,
       email TEXT UNIQUE
   );
   ```

4. **Test API**:
   - Enter prompt: "Get user data for ID 1 and store in test_users table"
   - Select `/users/{userId}` endpoint
   - Execute the API call

5. **View Results**:
   - Check "Created Tables" page for table metadata
   - View "Database Results" for API call history

## 🆕 New Features

### CREATE TABLE Command Execution
- Execute SQL CREATE TABLE statements
- Support for both PostgreSQL and SQLite syntax
- Automatic table name extraction
- Error handling and validation

### Database Flexibility
- Switch between SQLite and PostgreSQL
- PostgreSQL connection management
- Automatic schema creation

### Enhanced Tracking
- Track table creation alongside API calls
- Store CREATE TABLE commands for reference
- Link API responses with created tables

## 🛡️ Error Handling

Enhanced error handling for:
- Invalid CREATE TABLE syntax
- Database connection failures
- PostgreSQL authentication issues
- Table creation conflicts
- Cross-database compatibility

## 🔮 Future Enhancements

- **Data Insertion**: Automatic INSERT statement generation from API responses
- **Table Management**: DROP, ALTER table operations
- **Schema Migration**: Version control for database schemas
- **Query Builder**: Visual query construction
- **Data Validation**: Type checking before insertion
- **Bulk Operations**: Multiple table creation and API testing
- **Export/Import**: Database schema export and import functionality

## 🆘 Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -p 5432 -U username -d database_name
```

### Permission Issues with Table Creation
- Ensure database user has CREATE TABLE privileges
- Check database exists and is accessible
- Verify schema permissions in PostgreSQL

### SQLite vs PostgreSQL Syntax
- Use `SERIAL` for auto-increment in PostgreSQL
- Use `INTEGER PRIMARY KEY` for SQLite
- The app handles both syntaxes appropriately

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
