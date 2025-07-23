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
from config import config
from claude_integration import claude_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def resolve_schema_references(schema: Dict[str, Any], openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively resolve $ref references in OpenAPI schemas."""
    if not isinstance(schema, dict):
        return schema
    
    # If this is a reference, resolve it
    if '$ref' in schema:
        ref_path = schema['$ref']
        if ref_path.startswith('#/'):
            # Remove the '#/' and split by '/'
            path_parts = ref_path[2:].split('/')
            resolved_schema = openapi_spec
            
            # Navigate to the referenced schema
            for part in path_parts:
                if part in resolved_schema:
                    resolved_schema = resolved_schema[part]
                else:
                    logger.warning(f"Could not resolve reference: {ref_path}")
                    return schema  # Return original if can't resolve
            
            # Recursively resolve any references in the resolved schema
            return resolve_schema_references(resolved_schema, openapi_spec)
        else:
            logger.warning(f"External references not supported: {ref_path}")
            return schema
    
    # If this is an object, recursively resolve all its properties
    resolved_schema = {}
    for key, value in schema.items():
        if key == 'properties' and isinstance(value, dict):
            # Resolve all properties
            resolved_schema[key] = {
                prop_name: resolve_schema_references(prop_value, openapi_spec)
                for prop_name, prop_value in value.items()
            }
        elif key == 'items' and isinstance(value, dict):
            # Resolve array items schema
            resolved_schema[key] = resolve_schema_references(value, openapi_spec)
        elif key == 'allOf' and isinstance(value, list):
            # Resolve allOf schemas
            resolved_schema[key] = [
                resolve_schema_references(item, openapi_spec) for item in value
            ]
        elif key == 'anyOf' and isinstance(value, list):
            # Resolve anyOf schemas
            resolved_schema[key] = [
                resolve_schema_references(item, openapi_spec) for item in value
            ]
        elif key == 'oneOf' and isinstance(value, list):
            # Resolve oneOf schemas
            resolved_schema[key] = [
                resolve_schema_references(item, openapi_spec) for item in value
            ]
        elif isinstance(value, dict):
            # Recursively resolve nested objects
            resolved_schema[key] = resolve_schema_references(value, openapi_spec)
        else:
            # Keep primitive values as-is
            resolved_schema[key] = value
    
    return resolved_schema

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
                # Resolve $ref references to show full schema
                if schema and st.session_state.api_handler.openapi_spec:
                    schema_details = resolve_schema_references(schema, st.session_state.api_handler.openapi_spec)
                else:
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

# Section 6: Claude Template Generation with Editable Code
st.markdown('<div class="section-header"><h3>6. 🤖 Generate & Edit Conversion Template (Claude AI)</h3></div>', unsafe_allow_html=True)

if claude_generator.is_available():
    # Template Configuration
    st.subheader("Template Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Template name input
        template_name = st.text_input(
            "Template Name:",
            placeholder="users_api_to_db_template",
            help="Unique name for this conversion template"
        )
        
        # OpenAPI spec selection (if loaded)
        openapi_spec_name = "Unknown"
        if st.session_state.openapi_loaded:
            openapi_spec_name = st.text_input(
                "OpenAPI Spec Name:",
                value="loaded_spec",
                help="Name of the OpenAPI specification"
            )
        else:
            st.info("Load an OpenAPI specification first to generate templates")
    
    with col2:
        st.write("")  # spacing
        st.write("")  # spacing
        
        # Generate button
        generate_button = st.button("🤖 Generate with Claude", type="primary", use_container_width=True)
    
    # API and table selection for template generation
    col1, col2 = st.columns(2)
    
    with col1:
        # API endpoint selection for schema
        if st.session_state.openapi_loaded and st.session_state.api_endpoints:
            selected_api_for_template = st.selectbox(
                "Select API Endpoint for Template:",
                list(st.session_state.api_endpoints.keys()),
                key="template_api_select",
                help="Choose the API endpoint to extract response schema from"
            )
        else:
            selected_api_for_template = None
    
    with col2:
        # Database table selection
        if not created_tables.empty:
            selected_table_for_template = st.selectbox(
                "Select Target Database Table:",
                created_tables['table_name'].tolist(),
                key="template_table_select",
                help="Choose the database table to map the API response to"
            )
        else:
            selected_table_for_template = None
            st.warning("Create a database table first")
    
    # Initialize session state for generated code
    if 'generated_conversion_logic' not in st.session_state:
        st.session_state.generated_conversion_logic = ""
    if 'claude_generation_success' not in st.session_state:
        st.session_state.claude_generation_success = False
    
    # Generate conversion logic with Claude
    if generate_button:
        if template_name and selected_api_for_template and selected_table_for_template:
            # Get API response schema
            endpoint_info = st.session_state.api_endpoints[selected_api_for_template]
            api_schema = {}
            responses = endpoint_info.get('responses', {})
            if '200' in responses:
                response_200 = responses['200']
                content = response_200.get('content', {})
                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    # Resolve $ref references to show full schema
                    if schema and st.session_state.api_handler.openapi_spec:
                        api_schema = resolve_schema_references(schema, st.session_state.api_handler.openapi_spec)
                    else:
                        api_schema = schema
            
            # Get database table schema
            table_info = created_tables[created_tables['table_name'] == selected_table_for_template].iloc[0]
            db_schema = table_info['create_command']
            
            if api_schema:
                with st.spinner("🤖 Claude is generating your conversion template..."):
                    success, message, conversion_logic = claude_generator.generate_conversion_template(
                        openapi_spec_name, api_schema, db_schema, selected_table_for_template
                    )
                    
                    if success:
                        st.session_state.generated_conversion_logic = conversion_logic
                        st.session_state.claude_generation_success = True
                        st.session_state.api_schema_for_template = api_schema
                        st.session_state.db_schema_for_template = db_schema
                        st.markdown(f'<div class="success-box">✅ Conversion logic generated! You can now edit it below.</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error(f"Failed to generate template: {message}")
            else:
                st.error("No API response schema found for the selected endpoint")
        else:
            missing = []
            if not template_name:
                missing.append("Template Name")
            if not selected_api_for_template:
                missing.append("API Endpoint")
            if not selected_table_for_template:
                missing.append("Database Table")
            st.error(f"Please provide: {', '.join(missing)}")
    
    # Editable conversion logic interface
    if st.session_state.claude_generation_success and st.session_state.generated_conversion_logic:
        st.subheader("🔧 Edit Generated Conversion Logic")
        st.info("💡 Tip: You can modify the generated code to fix any syntax errors or customize the conversion logic.")
        
        # Editable text area with the generated code
        edited_conversion_logic = st.text_area(
            "Conversion Logic (Python Code):",
            value=st.session_state.generated_conversion_logic,
            height=400,
            help="Edit the generated Python code. Make sure to keep the 'input_data' and 'output_data' variables.",
            key="conversion_logic_editor"
        )
        
        # Test and Save buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            test_button = st.button("🧪 Test Code", type="secondary", use_container_width=True)
        
        with col2:
            save_button = st.button("💾 Save Template", type="primary", use_container_width=True)
        
        # Test the conversion logic
        if test_button:
            if edited_conversion_logic.strip():
                # Create sample test data based on the API schema
                test_data = {}
                if 'api_schema_for_template' in st.session_state:
                    api_schema = st.session_state.api_schema_for_template
                    if api_schema.get('type') == 'object' and 'properties' in api_schema:
                        properties = api_schema['properties']
                        for prop_name, prop_info in properties.items():
                            prop_type = prop_info.get('type', 'string')
                            if prop_type == 'integer':
                                test_data[prop_name] = 123
                            elif prop_type == 'string':
                                if 'email' in prop_name.lower():
                                    test_data[prop_name] = "test@example.com"
                                else:
                                    test_data[prop_name] = f"test_{prop_name}"
                            elif prop_type == 'object':
                                # Handle nested objects
                                nested_props = prop_info.get('properties', {})
                                nested_obj = {}
                                for nested_name, nested_info in nested_props.items():
                                    nested_type = nested_info.get('type', 'string')
                                    if nested_type == 'string':
                                        nested_obj[nested_name] = f"test_{nested_name}"
                                    elif nested_type == 'object':
                                        # Handle deeply nested objects
                                        deep_props = nested_info.get('properties', {})
                                        deep_obj = {}
                                        for deep_name, deep_info in deep_props.items():
                                            deep_obj[deep_name] = f"test_{deep_name}"
                                        nested_obj[nested_name] = deep_obj
                                test_data[prop_name] = nested_obj
                
                with st.spinner("🧪 Testing conversion logic..."):
                    test_success, test_message, test_output = claude_generator.test_conversion_logic(
                        edited_conversion_logic, test_data
                    )
                    
                    if test_success:
                        st.markdown(f'<div class="success-box">✅ Test successful!</div>', unsafe_allow_html=True)
                        st.subheader("📋 Test Results:")
                        
                        col_test1, col_test2 = st.columns(2)
                        with col_test1:
                            st.write("**Input Data:**")
                            st.json(test_data)
                        
                        with col_test2:
                            st.write("**Output Data:**")
                            st.json(test_output)
                    else:
                        st.markdown(f'<div class="error-box">❌ Test failed: {test_message}</div>', unsafe_allow_html=True)
                        st.warning("Please fix the syntax errors in your conversion logic.")
            else:
                st.warning("Please enter conversion logic to test.")
        
        # Save the template
        if save_button:
            if template_name and edited_conversion_logic.strip():
                # Test the logic first before saving
                test_success, test_message, _ = claude_generator.test_conversion_logic(
                    edited_conversion_logic, {"test": "data"}
                )
                
                if test_success:
                    # Store the template
                    store_success, store_message = st.session_state.db_manager.store_conversion_template(
                        template_name, 
                        openapi_spec_name, 
                        json.dumps(st.session_state.get('api_schema_for_template', {})), 
                        st.session_state.get('db_schema_for_template', ''), 
                        edited_conversion_logic, 
                        "Claude AI (Edited)"
                    )
                    
                    if store_success:
                        st.markdown(f'<div class="success-box">✅ Template saved successfully!</div>', unsafe_allow_html=True)
                        st.balloons()
                        
                        # Clear the generated logic to allow new generation
                        st.session_state.generated_conversion_logic = ""
                        st.session_state.claude_generation_success = False
                        
                        st.rerun()
                    else:
                        st.error(f"Failed to save template: {store_message}")
                else:
                    st.error(f"Cannot save template with syntax errors: {test_message}")
            else:
                st.error("Please provide a template name and conversion logic.")

else:
    st.warning("🔑 Claude AI features are not available. Please configure your Anthropic API key in the .env file.")
    st.info("See SETUP_GUIDE.md for instructions on setting up your API key.")

# Section 7: Conversion Templates Management
st.markdown('<div class="section-header"><h3>7. 📋 Conversion Templates</h3></div>', unsafe_allow_html=True)

# Get existing templates
conversion_templates = st.session_state.db_manager.get_conversion_templates()

if not conversion_templates.empty:
    st.subheader("📊 Existing Templates")
    st.dataframe(conversion_templates, use_container_width=True, hide_index=True)
else:
    st.info("No conversion templates created yet. Generate your first template above.")

# Section 8: Apply Conversion Template & Insert to Database
st.markdown('<div class="section-header"><h3>8. 🔄 Convert API Response & Insert to Database</h3></div>', unsafe_allow_html=True)

if not conversion_templates.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("API Response JSON Input")
        
        # Template selection
        selected_template = st.selectbox(
            "Select Conversion Template:",
            conversion_templates['template_name'].tolist(),
            key="apply_template_select",
            help="Choose a template to apply to your JSON data"
        )
        
        # JSON input for conversion
        api_response_json = st.text_area(
            "API Response JSON:",
            height=350,
            placeholder='''{
  "id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true,
  "profile": {
    "age": 30,
    "department": "Engineering"
  }
}''',
            help="Paste the JSON response from your API that you want to convert and insert"
        )
    
    with col2:
        st.subheader("Convert & Insert")
        
        # Target table selection for insertion
        if not created_tables.empty:
            target_table_for_insertion = st.selectbox(
                "Target Table for Insertion:",
                created_tables['table_name'].tolist(),
                key="target_insertion_table",
                help="Choose which table to insert the converted data into"
            )
        else:
            target_table_for_insertion = None
        
        st.write("")  # spacing
        
        if st.button("🔄 Convert & Insert to Database", type="primary", use_container_width=True):
            if selected_template and api_response_json.strip() and target_table_for_insertion:
                try:
                    # Parse the input JSON
                    input_json = json.loads(api_response_json)
                    
                    with st.spinner("🔄 Converting JSON using template..."):
                        # Apply the conversion template
                        convert_success, convert_message, converted_data = st.session_state.db_manager.apply_conversion_template(
                            selected_template, input_json
                        )
                        
                        if convert_success and converted_data:
                            st.markdown(f'<div class="success-box">✅ Conversion successful!</div>', unsafe_allow_html=True)
                            
                            # Show the converted data
                            st.subheader("📋 Converted Data:")
                            converted_df = pd.DataFrame([converted_data])
                            st.dataframe(converted_df, use_container_width=True, hide_index=True)
                            
                            # Insert into database
                            with st.spinner(f"📥 Inserting into table '{target_table_for_insertion}'..."):
                                insert_success, insert_message = st.session_state.db_manager.insert_json_data(
                                    converted_data, target_table_for_insertion
                                )
                                
                                if insert_success:
                                    st.markdown(f'<div class="success-box">✅ {insert_message}</div>', unsafe_allow_html=True)
                                    st.balloons()
                                    st.rerun()  # Refresh to show updated data
                                else:
                                    st.markdown(f'<div class="error-box">❌ Insertion failed: {insert_message}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-box">❌ Conversion failed: {convert_message}</div>', unsafe_allow_html=True)
                            
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON format: {str(e)}")
            else:
                missing = []
                if not selected_template:
                    missing.append("Template")
                if not api_response_json.strip():
                    missing.append("API Response JSON")
                if not target_table_for_insertion:
                    missing.append("Target Table")
                st.error(f"Please provide: {', '.join(missing)}")

else:
    st.info("Create conversion templates first to convert and insert your API data.")

# Section 9: View Database Results
st.markdown('<div class="section-header"><h3>9. 📊 View Database Results</h3></div>', unsafe_allow_html=True)

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