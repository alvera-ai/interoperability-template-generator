import streamlit as st
import json
import yaml
import pandas as pd
from typing import Dict, Any
import logging
import os
from datetime import datetime
import sqlite3

from database import DatabaseManager
from api_handler import APIHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'api_handler' not in st.session_state:
    st.session_state.api_handler = APIHandler()
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager(use_postgres=False)
if 'openapi_loaded' not in st.session_state:
    st.session_state.openapi_loaded = False
if 'api_endpoints' not in st.session_state:
    st.session_state.api_endpoints = {}

# Page configuration
st.set_page_config(
    page_title="API Interoperability Tester",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🔗 API Interoperability Template Generator</h1>
    <p>Upload OpenAPI specs, create database tables, and convert schemas</p>
</div>
""", unsafe_allow_html=True)

# Section 1: OpenAPI Spec Upload
st.markdown('<div class="section-header"><h3>1. 📤 Upload OpenAPI Specification</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose an OpenAPI spec file",
        type=['yaml', 'yml', 'json'],
        help="Upload your OpenAPI specification file"
    )

with col2:
    if uploaded_file is not None: 
        if st.button("🚀 Load OpenAPI Spec", type="primary", use_container_width=True):
            file_type = uploaded_file.name.split('.')[-1]
            openapi_content = uploaded_file.read().decode('utf-8')
            
            with st.spinner("Loading OpenAPI specification..."):
                if st.session_state.api_handler.load_openapi_spec(openapi_content, file_type):
                    st.session_state.openapi_loaded = True
                    st.session_state.api_endpoints = st.session_state.api_handler.get_available_endpoints()
                    # Store in database
                    spec_name = f"spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    st.session_state.db_manager.store_openapi_spec(spec_name, openapi_content)
                    st.success("✅ OpenAPI specification loaded successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to load OpenAPI specification. Please check the format.")

# Section 2: API Endpoints Table
st.markdown('<div class="section-header"><h3>2. 📋 API Endpoints & Schema Details</h3></div>', unsafe_allow_html=True)

if st.session_state.openapi_loaded and st.session_state.api_endpoints:
    # Prepare data for the table
    api_data = []
    for endpoint_path, endpoint_info in st.session_state.api_endpoints.items():
        # Get response schema for 200 status code
        schema_details = {}
        responses = endpoint_info.get('responses', {})
        if '200' in responses:
            response_200 = responses['200']
            content = response_200.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                schema_details = schema
        
        api_data.append({
            'API Endpoint': endpoint_path,
            'Schema Details (JSON)': json.dumps(schema_details, indent=2) if schema_details else "No schema available"
        })
    
    if api_data:
        api_df = pd.DataFrame(api_data)
        st.dataframe(api_df, use_container_width=True, hide_index=True)
    else:
        st.info("No API endpoints found in the specification.")
else:
    st.info("👆 Please upload and load an OpenAPI specification to view endpoints.")

# Section 3: CREATE TABLE Command
st.markdown('<div class="section-header"><h3>3. 🗃️ Create Database Table</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    create_table_command = st.text_area(
        "SQL CREATE TABLE Command *",
        height=200,
        placeholder='''CREATE TABLE api_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100),
    email VARCHAR(100),
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''',
        help="Provide a SQL CREATE TABLE statement (Required)"
    )

with col2:
    st.write("")  # spacing
    st.write("")  # spacing
    if st.button("🗃️ Create Table", type="primary", use_container_width=True):
        if create_table_command.strip():
            with st.spinner("Creating table..."):
                success, message, table_name = st.session_state.db_manager.execute_create_table(
                    create_table_command, "Manual table creation"
                )
                
                if success:
                    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
                    st.balloons()
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
        else:
            st.error("Please enter a CREATE TABLE command.")

# Section 4: Created Tables Display
st.markdown('<div class="section-header"><h3>4. 📊 Created Tables & Schemas</h3></div>', unsafe_allow_html=True)

created_tables = st.session_state.db_manager.get_created_tables()

if not created_tables.empty:
    # Prepare table data
    table_display_data = []
    for _, row in created_tables.iterrows():
        table_display_data.append({
            'Table Name': row['table_name'],
            'Schema (CREATE Command)': row['create_command'],
            'Created At': row['timestamp']
        })
    
    table_df = pd.DataFrame(table_display_data)
    st.dataframe(table_df, use_container_width=True, hide_index=True)
else:
    st.info("No tables created yet. Create your first table above.")

# Section 5: API and Table Selection
st.markdown('<div class="section-header"><h3>5. 🔗 API & Table Selection</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Select API Endpoint")
    if st.session_state.openapi_loaded and st.session_state.api_endpoints:
        selected_api = st.selectbox(
            "Choose API Endpoint:",
            list(st.session_state.api_endpoints.keys()),
            format_func=lambda x: f"{x} - {st.session_state.api_endpoints[x].get('summary', 'No description')}"
        )
    else:
        st.info("Load an OpenAPI spec first")
        selected_api = None

with col2:
    st.subheader("Select Database Table")
    if not created_tables.empty:
        def format_table_option(table_name):
            timestamp = created_tables[created_tables['table_name']==table_name]['timestamp'].iloc[0]
            return f"{table_name} - {timestamp}"
        
        selected_table = st.selectbox(
            "Choose Database Table:",
            created_tables['table_name'].tolist(),
            format_func=format_table_option
        )
    else:
        st.info("Create a table first")
        selected_table = None

# Section 6: Schema Conversion
st.markdown('<div class="section-header"><h3>6. 🔄 JSON Schema Conversion</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input: API Response Schema")
    
    # Auto-populate with selected API schema if available
    auto_schema = ""
    if selected_api and st.session_state.api_endpoints:
        endpoint_info = st.session_state.api_endpoints[selected_api]
        responses = endpoint_info.get('responses', {})
        if '200' in responses:
            response_200 = responses['200']
            content = response_200.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                if schema:
                    auto_schema = json.dumps(schema, indent=2)
    
    input_json_schema = st.text_area(
        "JSON Schema (from OpenAPI response):",
        height=300,
        value=auto_schema,
        placeholder='''{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "email": {"type": "string"},
    "created_at": {"type": "string", "format": "date-time"}
  }
}''',
        help="Paste the JSON schema from your OpenAPI specification"
    )

with col2:
    st.subheader("Output: Database Table Schema")
    
    if st.button("🔄 Convert Schema", type="secondary", use_container_width=True):
        if input_json_schema.strip():
            try:
                # Parse the input JSON schema
                schema = json.loads(input_json_schema)
                
                # Convert to database-compatible format
                converted_schemas = []
                
                if selected_table and not created_tables.empty:
                    # Get the CREATE TABLE command for the selected table
                    table_info = created_tables[created_tables['table_name'] == selected_table].iloc[0]
                    create_command = table_info['create_command']
                    
                    # Generate sample INSERT statements based on the schema
                    if schema.get('type') == 'object' and 'properties' in schema:
                        properties = schema['properties']
                        
                        # Create sample data based on schema
                        sample_data = {}
                        for prop_name, prop_info in properties.items():
                            prop_type = prop_info.get('type', 'string')
                            if prop_type == 'integer':
                                sample_data[prop_name] = 123
                            elif prop_type == 'string':
                                if 'format' in prop_info and prop_info['format'] == 'date-time':
                                    sample_data[prop_name] = datetime.now().isoformat()
                                elif 'email' in prop_name.lower():
                                    sample_data[prop_name] = "user@example.com"
                                else:
                                    sample_data[prop_name] = f"sample_{prop_name}"
                            elif prop_type == 'boolean':
                                sample_data[prop_name] = True
                            else:
                                sample_data[prop_name] = f"sample_{prop_name}"
                        
                        # Create multiple sample records
                        for i in range(3):
                            record = sample_data.copy()
                            if 'id' in record:
                                record['id'] = i + 1
                            if 'name' in record:
                                record['name'] = f"User {i + 1}"
                            
                            converted_schemas.append({
                                'Record': i + 1,
                                'Table': selected_table,
                                'JSON Data': json.dumps(record, indent=2)
                            })
                    
                    if converted_schemas:
                        conversion_df = pd.DataFrame(converted_schemas)
                        st.dataframe(conversion_df, use_container_width=True, hide_index=True)
                        
                        # Show INSERT statement examples
                        st.subheader("💡 Sample INSERT Statements")
                        columns = list(sample_data.keys())
                        values_placeholder = ', '.join(['%s'] * len(columns))
                        insert_statement = f"INSERT INTO {selected_table} ({', '.join(columns)}) VALUES ({values_placeholder});"
                        st.code(insert_statement, language='sql')
                        
                        # Show actual values for first record
                        if converted_schemas:
                            first_record = json.loads(converted_schemas[0]['JSON Data'])
                            values = [str(first_record[col]) for col in columns]
                            quoted_values = [f"'{v}'" for v in values]
                            actual_insert = f"INSERT INTO {selected_table} ({', '.join(columns)}) VALUES ({', '.join(quoted_values)});"
                            st.code(actual_insert, language='sql')
                    else:
                        st.warning("Could not generate sample data from the provided schema.")
                else:
                    st.warning("Please select a database table first.")
                    
            except json.JSONDecodeError:
                st.error("Invalid JSON schema. Please check the format.")
        else:
            st.warning("Please enter a JSON schema to convert.")
    
    # Display area for converted schemas
    st.text_area(
        "Converted Table Schemas:",
        height=200,
        placeholder="Converted schemas will appear here after conversion...",
        disabled=True,
        key="output_area"
    )

# Section 7: JSON Data Insertion
st.markdown('<div class="section-header"><h3>7. 📥 Insert JSON Data into Table</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("JSON Data Input")
    
    # Show table structure for selected table if available
    if selected_table and not created_tables.empty:
        table_structure = st.session_state.db_manager.get_table_structure(selected_table)
        if table_structure and 'columns' in table_structure:
            st.info(f"**Table Structure for '{selected_table}':**")
            structure_info = []
            for col in table_structure['columns']:
                nullable = "nullable" if col.get('nullable', True) else "not null"
                pk = " (PK)" if col.get('primary_key', False) else ""
                structure_info.append(f"• **{col['name']}**: {col['type']} ({nullable}){pk}")
            st.markdown("\n".join(structure_info))
    
    # JSON input text area
    json_input = st.text_area(
        "JSON Data to Insert:",
        height=250,
        placeholder='''{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "user_id": 12345,
  "data": {"role": "admin", "department": "IT"}
}''',
        help="Enter the JSON data you want to insert into the selected table"
    )

with col2:
    st.subheader("Table Selection & Insertion")
    
    # Table selection for insertion (duplicate of earlier selection for convenience)
    insert_table = st.selectbox(
        "Select Table for Insertion:",
        created_tables['table_name'].tolist() if not created_tables.empty else [],
        key="insert_table_select",
        help="Choose which table to insert the JSON data into"
    )
    
    st.write("")  # spacing
    st.write("")  # spacing
    
    if st.button("📥 Insert JSON Data", type="primary", use_container_width=True):
        if json_input.strip() and insert_table:
            try:
                # Parse JSON data
                json_data = json.loads(json_input)
                
                with st.spinner(f"Inserting data into table '{insert_table}'..."):
                    success, message = st.session_state.db_manager.insert_json_data(json_data, insert_table)
                    
                    if success:
                        st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
                        st.balloons()
                        
                        # Show what was inserted
                        st.subheader("📋 Inserted Data")
                        inserted_df = pd.DataFrame([json_data])
                        st.dataframe(inserted_df, use_container_width=True, hide_index=True)
                        
                    else:
                        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                        
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {str(e)}")
        else:
            if not json_input.strip():
                st.error("Please enter JSON data to insert.")
            if not insert_table:
                st.error("Please select a table for insertion.")

# Section 8: Inserted Data Viewer
st.markdown('<div class="section-header"><h3>8. 📊 View Table Data</h3></div>', unsafe_allow_html=True)

if not created_tables.empty:
    view_table = st.selectbox(
        "Select Table to View Data:",
        created_tables['table_name'].tolist(),
        key="view_table_select",
        help="Choose which table's data you want to view"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🔍 View Data", type="secondary", use_container_width=True):
            if view_table:
                try:
                    # Query the selected table
                    if st.session_state.db_manager.use_postgres:
                        with st.session_state.db_manager.engine.connect() as conn:
                            query_result = pd.read_sql_query(f"SELECT * FROM {view_table} ORDER BY id DESC LIMIT 50", conn)
                    else:
                        with sqlite3.connect(st.session_state.db_manager.db_path) as conn:
                            query_result = pd.read_sql_query(f"SELECT * FROM {view_table} ORDER BY id DESC LIMIT 50", conn)
                    
                    if not query_result.empty:
                        st.subheader(f"📋 Data from '{view_table}' (Latest 50 records)")
                        st.dataframe(query_result, use_container_width=True, hide_index=True)
                        
                        # Show record count
                        st.info(f"Showing {len(query_result)} records from table '{view_table}'")
                    else:
                        st.info(f"No data found in table '{view_table}'")
                        
                except Exception as e:
                    st.error(f"Error querying table: {str(e)}")
    
    with col2:
        st.write("")  # spacing for alignment

else:
    st.info("Create a table first to view its data.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Built with ❤️ using Streamlit | Single Page API-Database Integration Tool"
    "</div>",
    unsafe_allow_html=True
) 