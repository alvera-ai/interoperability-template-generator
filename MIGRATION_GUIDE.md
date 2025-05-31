# Migration Guide: Schema Validation → CREATE TABLE Commands

## 🔄 What Changed?

The application has been enhanced from **JSON Schema Validation** to **Database Table Creation** functionality. Here's what you need to know:

## ⚡ Quick Migration

### Before (Schema Validation)
```json
{
  "type": "object", 
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"}
  }
}
```

### After (CREATE TABLE Commands)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🆕 New Features

### 1. Database Choice
- **SQLite**: Default, no setup required
- **PostgreSQL**: Production-ready, configurable

### 2. Table Creation
- Execute CREATE TABLE statements
- Automatic table name extraction
- Error handling and validation

### 3. Enhanced Tracking
- Track created tables with metadata
- Link API calls to table creation
- Store creation commands for reference

## 🎯 Migration Steps

### Step 1: Update Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Choose Database Type
- Go to "Database Settings" page
- Select SQLite or PostgreSQL
- Configure connection if using PostgreSQL

### Step 3: Convert Schemas to CREATE TABLE
Transform your JSON schemas into SQL CREATE TABLE statements:

#### Example Conversion:

**Old JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "userId": {"type": "integer"},
    "name": {"type": "string", "maxLength": 100},
    "email": {"type": "string", "format": "email"},
    "active": {"type": "boolean"}
  },
  "required": ["userId", "name", "email"]
}
```

**New CREATE TABLE:**
```sql
CREATE TABLE users (
    userId INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 4: Update Your Workflow
1. **Create Table First**: Execute CREATE TABLE command
2. **Test API**: Run your API calls as before  
3. **View Results**: Check both API results and created tables

## 🔧 Database-Specific Syntax

### SQLite Syntax
```sql
CREATE TABLE example (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### PostgreSQL Syntax
```sql
CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 New Pages & Features

### Created Tables Page
- View all tables created through the app
- See table schemas and creation commands
- Track creation timestamps and prompts

### Database Settings Page
- Configure PostgreSQL connection
- Switch between database types
- View current database status

### Enhanced Database Results
- Shows created table information
- Links API calls to table creation
- Displays CREATE TABLE commands used

## 🚀 Benefits of the New System

### Before: Schema Validation
- ✅ Validated API responses
- ❌ No data persistence structure
- ❌ No table management

### After: CREATE TABLE Commands  
- ✅ Creates actual database tables
- ✅ Supports multiple database types
- ✅ Tracks table metadata
- ✅ Prepares for data insertion
- ✅ Production-ready database integration

## 🎯 Common Migration Patterns

### Pattern 1: Simple Object Schema
```json
// OLD
{"type": "object", "properties": {"id": {"type": "integer"}}}

// NEW  
CREATE TABLE items (id INTEGER PRIMARY KEY);
```

### Pattern 2: Complex Schema with Validation
```json
// OLD
{
  "type": "object",
  "properties": {
    "user_id": {"type": "integer", "minimum": 1},
    "username": {"type": "string", "minLength": 3, "maxLength": 50},
    "email": {"type": "string", "format": "email"}
  },
  "required": ["user_id", "username", "email"]
}

// NEW
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY CHECK (user_id > 0),
    username VARCHAR(50) NOT NULL CHECK (LENGTH(username) >= 3),
    email VARCHAR(255) NOT NULL CHECK (email LIKE '%@%.%'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Pattern 3: Array/List Schema
```json
// OLD
{
  "type": "array",
  "items": {
    "type": "object", 
    "properties": {"id": {"type": "integer"}}
  }
}

// NEW - Create table for individual items
CREATE TABLE list_items (
    id INTEGER PRIMARY KEY,
    list_id INTEGER,
    item_data JSONB,  -- PostgreSQL
    -- item_data TEXT,  -- SQLite
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛠️ Testing Your Migration

1. **Test Table Creation**:
   ```sql
   CREATE TABLE test_migration (
       id SERIAL PRIMARY KEY,
       test_field VARCHAR(100)
   );
   ```

2. **Test API Call**: Use existing OpenAPI specs

3. **Verify Results**: Check "Created Tables" page

4. **Review Storage**: Check "Database Results" for linked data

## 🚨 Breaking Changes

### Removed Features
- JSON Schema validation (replaced by table creation)
- Schema validation results display

### Changed Behavior
- "Schema" field now expects SQL CREATE TABLE commands
- Results show table creation status instead of validation status
- Database structure is now persistent and queryable

### Migration Required For
- Applications relying on JSON schema validation
- Custom validation logic
- Schema validation error handling

## 🆘 Need Help?

### Common Issues

**Issue**: "Could not extract table name"
**Solution**: Ensure your CREATE TABLE syntax is correct:
```sql
-- ✅ Good
CREATE TABLE my_table (id INTEGER);

-- ❌ Bad  
CREATE my_table (id INTEGER);
```

**Issue**: PostgreSQL connection fails
**Solution**: Check database settings and ensure PostgreSQL is running

**Issue**: Table already exists
**Solution**: Use `CREATE TABLE IF NOT EXISTS` or drop the existing table

### Getting Support
1. Check the troubleshooting section in README.md
2. Verify your SQL syntax
3. Test with SQLite first, then migrate to PostgreSQL
4. Review the example CREATE TABLE commands provided

## 🎉 Ready to Use!

Your application now supports:
- ✅ Real database table creation
- ✅ PostgreSQL and SQLite support  
- ✅ Enhanced data tracking
- ✅ Production-ready database integration

Start creating tables and testing APIs with persistent data storage! 