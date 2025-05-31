import streamlit as st
import json
import yaml
import pandas as pd
from typing import Dict, Any
import logging
from datetime import datetime

from database import DatabaseManager
from api_handler import APIHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'api_handler' not in st.session_state:
    st.session_state.api_handler = APIHandler()
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'openapi_loaded' not in st.session_state:
    st.session_state.openapi_loaded = False

# Page configuration
st.set_page_config(
    page_title="API Interoperability Tester",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
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
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🔗 API Interoperability Template Generator</h1>
    <p>Test APIs using OpenAPI specifications with schema validation</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["API Tester", "Database Results", "API Documentation"]
)

if page == "API Tester":
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-header"><h3>📝 Input Configuration</h3></div>', unsafe_allow_html=True)
        
        # OpenAPI Spec Input
        st.subheader("1. OpenAPI Specification")
        spec_input_method = st.radio(
            "How would you like to provide the OpenAPI spec?",
            ["Upload File", "Paste Content", "URL"]
        )
        
        openapi_content = None
        file_type = "yaml"
        
        if spec_input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose an OpenAPI spec file",
                type=['yaml', 'yml', 'json'],
                help="Upload your OpenAPI specification file"
            )
            
            if uploaded_file is not None:
                file_type = uploaded_file.name.split('.')[-1]
                openapi_content = uploaded_file.read().decode('utf-8')
                
        elif spec_input_method == "Paste Content":
            file_type = st.selectbox("File type", ["yaml", "json"])
            openapi_content = st.text_area(
                "Paste your OpenAPI specification",
                height=200,
                placeholder="Paste your OpenAPI spec here..."
            )
            
        elif spec_input_method == "URL":
            spec_url = st.text_input("OpenAPI Spec URL")
            if spec_url:
                try:
                    import requests
                    response = requests.get(spec_url)
                    openapi_content = response.text
                    file_type = "yaml" if spec_url.endswith(('.yaml', '.yml')) else "json"
                except Exception as e:
                    st.error(f"Error fetching from URL: {e}")
        
        # Load OpenAPI spec
        if openapi_content and st.button("Load OpenAPI Spec"):
            with st.spinner("Loading and validating OpenAPI specification..."):
                if st.session_state.api_handler.load_openapi_spec(openapi_content, file_type):
                    st.session_state.openapi_loaded = True
                    # Store in database
                    spec_name = f"spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    st.session_state.db_manager.store_openapi_spec(spec_name, openapi_content)
                    st.markdown('<div class="success-box">✅ OpenAPI specification loaded successfully!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">❌ Failed to load OpenAPI specification. Please check the format.</div>', unsafe_allow_html=True)
        
        # Schema Input
        st.subheader("2. Response Schema (Optional)")
        schema_input = st.text_area(
            "JSON Schema for validation",
            height=150,
            placeholder='{\n  "type": "object",\n  "properties": {\n    "id": {"type": "integer"},\n    "name": {"type": "string"}\n  }\n}',
            help="Provide a JSON schema to validate API responses"
        )
        
        # User Prompt
        st.subheader("3. User Prompt")
        user_prompt = st.text_area(
            "Describe what you want to test",
            height=100,
            placeholder="e.g., Get user information for user ID 123",
            help="Describe your API testing scenario"
        )
    
    with col2:
        st.markdown('<div class="section-header"><h3>🚀 API Testing</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.openapi_loaded:
            # Show available endpoints
            endpoints = st.session_state.api_handler.get_available_endpoints()
            
            if endpoints:
                st.subheader("Available GET Endpoints")
                selected_endpoint = st.selectbox(
                    "Choose an endpoint to test",
                    list(endpoints.keys()),
                    format_func=lambda x: f"{x} - {endpoints[x].get('summary', 'No description')}"
                )
                
                if selected_endpoint:
                    endpoint_info = endpoints[selected_endpoint]
                    
                    with st.expander("Endpoint Details"):
                        st.write(f"**Path:** {selected_endpoint}")
                        st.write(f"**Summary:** {endpoint_info.get('summary', 'N/A')}")
                        st.write(f"**Description:** {endpoint_info.get('description', 'N/A')}")
                        
                        if endpoint_info.get('parameters'):
                            st.write("**Parameters:**")
                            for param in endpoint_info['parameters']:
                                st.write(f"- {param.get('name')} ({param.get('in', 'query')}): {param.get('description', 'No description')}")
                    
                    # Parameters input
                    st.subheader("Request Parameters")
                    
                    # Auto-extract parameters from prompt
                    auto_params = {}
                    if user_prompt:
                        auto_params = st.session_state.api_handler.extract_parameters_from_prompt(
                            user_prompt, selected_endpoint
                        )
                    
                    # Manual parameter input
                    params = {}
                    if endpoint_info.get('parameters'):
                        for param in endpoint_info['parameters']:
                            param_name = param.get('name', '')
                            param_type = param.get('type', 'string')
                            default_value = auto_params.get(param_name, '')
                            
                            if param_type == 'integer':
                                params[param_name] = st.number_input(
                                    f"{param_name} ({param.get('description', '')})",
                                    value=int(default_value) if default_value.isdigit() else 0
                                )
                            else:
                                params[param_name] = st.text_input(
                                    f"{param_name} ({param.get('description', '')})",
                                    value=default_value
                                )
                    
                    # Additional headers
                    with st.expander("Additional Headers (Optional)"):
                        headers_text = st.text_area(
                            "Headers (JSON format)",
                            placeholder='{"Authorization": "Bearer token", "Custom-Header": "value"}',
                            height=100
                        )
                    
                    # Make API call
                    if st.button("🚀 Execute API Call", type="primary"):
                        if not user_prompt:
                            st.warning("Please provide a user prompt describing your test scenario.")
                        else:
                            with st.spinner("Making API call..."):
                                # Parse headers
                                headers = {}
                                if headers_text:
                                    try:
                                        headers = json.loads(headers_text)
                                    except json.JSONDecodeError:
                                        st.warning("Invalid JSON in headers. Using default headers.")
                                
                                # Clean up parameters (remove empty values)
                                clean_params = {k: v for k, v in params.items() if v}
                                
                                # Make the request
                                status_code, response_data, response_headers = st.session_state.api_handler.make_get_request(
                                    selected_endpoint, clean_params, headers
                                )
                                
                                # Validate against schema if provided
                                schema_validation_result = ""
                                if schema_input:
                                    try:
                                        schema = json.loads(schema_input)
                                        is_valid, validation_msg = st.session_state.api_handler.validate_schema(
                                            response_data, schema
                                        )
                                        schema_validation_result = f"Schema Validation: {'✅ Valid' if is_valid else '❌ Invalid'} - {validation_msg}"
                                    except json.JSONDecodeError:
                                        schema_validation_result = "❌ Invalid schema format"
                                
                                # Store result in database
                                result_id = st.session_state.db_manager.store_api_result(
                                    user_prompt=user_prompt,
                                    api_endpoint=selected_endpoint,
                                    schema_used=schema_input or "None",
                                    response_data=response_data,
                                    status_code=status_code,
                                    response_headers=response_headers
                                )
                                
                                # Display results
                                st.subheader("🎯 API Response")
                                
                                # Status
                                status_color = "green" if 200 <= status_code < 300 else "red"
                                st.markdown(f"**Status Code:** <span style='color: {status_color}'>{status_code}</span>", unsafe_allow_html=True)
                                
                                # Schema validation
                                if schema_validation_result:
                                    st.markdown(f"**{schema_validation_result}**")
                                
                                # Response data
                                st.subheader("Response Data")
                                st.json(response_data)
                                
                                # Response headers
                                with st.expander("Response Headers"):
                                    st.json(response_headers)
                                
                                st.success(f"✅ Result stored in database with ID: {result_id}")
            else:
                st.warning("No GET endpoints found in the OpenAPI specification.")
        else:
            st.info("👆 Please load an OpenAPI specification first to see available endpoints.")

elif page == "Database Results":
    st.markdown('<div class="section-header"><h3>📊 Stored API Results</h3></div>', unsafe_allow_html=True)
    
    # Recent results
    st.subheader("Recent API Calls")
    
    limit = st.slider("Number of results to show", 5, 50, 10)
    recent_results = st.session_state.db_manager.get_recent_results(limit)
    
    if not recent_results.empty:
        # Display results table
        st.dataframe(recent_results, use_container_width=True)
        
        # Result details
        if not recent_results.empty:
            selected_id = st.selectbox(
                "Select a result to view details",
                recent_results['id'].tolist(),
                format_func=lambda x: f"ID {x}: {recent_results[recent_results['id']==x]['user_prompt'].iloc[0][:50]}..."
            )
            
            if selected_id:
                result_details = st.session_state.db_manager.get_result_details(selected_id)
                
                if result_details:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Request Details")
                        st.write(f"**Timestamp:** {result_details['timestamp']}")
                        st.write(f"**User Prompt:** {result_details['user_prompt']}")
                        st.write(f"**API Endpoint:** {result_details['api_endpoint']}")
                        st.write(f"**Status Code:** {result_details['status_code']}")
                    
                    with col2:
                        st.subheader("Schema Used")
                        if result_details['schema_used'] != "None":
                            st.code(result_details['schema_used'], language='json')
                        else:
                            st.write("No schema validation used")
                    
                    st.subheader("Response Data")
                    st.json(result_details['response_data'])
                    
                    with st.expander("Response Headers"):
                        st.json(result_details['response_headers'])
    else:
        st.info("No API results found. Make some API calls first!")

elif page == "API Documentation":
    st.markdown('<div class="section-header"><h3>📚 API Documentation</h3></div>', unsafe_allow_html=True)
    
    if st.session_state.openapi_loaded:
        # Display OpenAPI spec info
        spec = st.session_state.api_handler.openapi_spec
        
        if spec:
            st.subheader("API Information")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write(f"**Title:** {spec.get('info', {}).get('title', 'N/A')}")
                st.write(f"**Version:** {spec.get('info', {}).get('version', 'N/A')}")
                st.write(f"**Description:** {spec.get('info', {}).get('description', 'N/A')}")
            
            with col2:
                st.write(f"**Base URL:** {st.session_state.api_handler.base_url}")
                if 'servers' in spec:
                    st.write("**Servers:**")
                    for server in spec['servers']:
                        st.write(f"- {server.get('url', 'N/A')}")
            
            # Endpoints documentation
            st.subheader("Available Endpoints")
            endpoints = st.session_state.api_handler.get_available_endpoints()
            
            for path, info in endpoints.items():
                with st.expander(f"GET {path}"):
                    st.write(f"**Summary:** {info.get('summary', 'N/A')}")
                    st.write(f"**Description:** {info.get('description', 'N/A')}")
                    
                    if info.get('parameters'):
                        st.write("**Parameters:**")
                        params_df = pd.DataFrame(info['parameters'])
                        st.dataframe(params_df[['name', 'in', 'description', 'required']] if 'required' in params_df.columns else params_df)
                    
                    if info.get('responses'):
                        st.write("**Responses:**")
                        for code, response in info['responses'].items():
                            st.write(f"- **{code}:** {response.get('description', 'No description')}")
    else:
        st.info("Load an OpenAPI specification to view documentation.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Built with ❤️ using Streamlit | API Interoperability Template Generator"
    "</div>",
    unsafe_allow_html=True
) 