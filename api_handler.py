import requests
import yaml
import json
from typing import Dict, Any, List, Optional, Tuple
import logging
from urllib.parse import urljoin, urlparse
from openapi_spec_validator import validate_spec
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

class APIHandler:
    def __init__(self):
        self.openapi_spec = None
        self.base_url = None
        self.endpoints = {}
    
    def load_openapi_spec(self, spec_content: str, file_type: str = "yaml") -> bool:
        """Load and validate OpenAPI specification."""
        try:
            if file_type.lower() in ["yaml", "yml"]:
                self.openapi_spec = yaml.safe_load(spec_content)
            else:
                self.openapi_spec = json.loads(spec_content)
            
            # Validate the OpenAPI spec
            validate_spec(self.openapi_spec)
            
            # Extract base URL
            if "servers" in self.openapi_spec and self.openapi_spec["servers"]:
                self.base_url = self.openapi_spec["servers"][0]["url"]
            else:
                # Fallback for older specs
                self.base_url = f"https://{self.openapi_spec.get('host', 'localhost')}"
                if "basePath" in self.openapi_spec:
                    self.base_url = urljoin(self.base_url, self.openapi_spec["basePath"])
            
            # Extract endpoints
            self._extract_endpoints()
            
            logger.info("OpenAPI spec loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading OpenAPI spec: {e}")
            return False
    
    def _extract_endpoints(self):
        """Extract GET endpoints from the OpenAPI spec."""
        self.endpoints = {}
        
        if "paths" not in self.openapi_spec:
            return
        
        for path, methods in self.openapi_spec["paths"].items():
            if "get" in methods:
                endpoint_info = {
                    "path": path,
                    "summary": methods["get"].get("summary", ""),
                    "description": methods["get"].get("description", ""),
                    "parameters": methods["get"].get("parameters", []),
                    "responses": methods["get"].get("responses", {})
                }
                self.endpoints[path] = endpoint_info
    
    def get_available_endpoints(self) -> Dict[str, Any]:
        """Get all available GET endpoints."""
        return self.endpoints
    
    def validate_schema(self, data: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data against a JSON schema."""
        try:
            validate(instance=data, schema=schema)
            return True, "Valid"
        except ValidationError as e:
            return False, str(e)
    
    def make_get_request(self, endpoint_path: str, params: Dict[str, Any] = None, 
                        headers: Dict[str, str] = None) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """Make a GET request to the specified endpoint."""
        try:
            if not self.base_url:
                raise ValueError("No base URL available. Please load an OpenAPI spec first.")
            
            # Construct full URL
            url = urljoin(self.base_url, endpoint_path.lstrip('/'))
            
            # Default headers
            default_headers = {
                "Accept": "application/json",
                "User-Agent": "Streamlit-API-Tester/1.0"
            }
            
            if headers:
                default_headers.update(headers)
            
            # Make the request
            response = requests.get(url, params=params, headers=default_headers, timeout=30)
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"raw_response": response.text}
            
            return response.status_code, response_data, dict(response.headers)
            
        except Exception as e:
            logger.error(f"Error making GET request: {e}")
            return 500, {"error": str(e)}, {}
    
    def get_endpoint_schema(self, endpoint_path: str, response_code: str = "200") -> Optional[Dict[str, Any]]:
        """Get the response schema for a specific endpoint."""
        try:
            if endpoint_path not in self.endpoints:
                return None
            
            endpoint = self.endpoints[endpoint_path]
            responses = endpoint.get("responses", {})
            
            if response_code in responses:
                response_info = responses[response_code]
                if "content" in response_info:
                    # OpenAPI 3.x format
                    for content_type, content_info in response_info["content"].items():
                        if "schema" in content_info:
                            return content_info["schema"]
                elif "schema" in response_info:
                    # OpenAPI 2.x format
                    return response_info["schema"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting endpoint schema: {e}")
            return None
    
    def extract_parameters_from_prompt(self, prompt: str, endpoint_path: str) -> Dict[str, Any]:
        """Extract potential parameters from user prompt for the given endpoint."""
        # This is a simplified implementation
        # In a real-world scenario, you might want to use NLP or more sophisticated parsing
        
        parameters = {}
        
        if endpoint_path not in self.endpoints:
            return parameters
        
        endpoint_params = self.endpoints[endpoint_path].get("parameters", [])
        
        # Simple keyword extraction based on parameter names
        prompt_lower = prompt.lower()
        
        for param in endpoint_params:
            param_name = param.get("name", "")
            if param_name.lower() in prompt_lower:
                # Extract value (this is very basic - could be enhanced)
                words = prompt_lower.split()
                try:
                    param_index = words.index(param_name.lower())
                    if param_index + 1 < len(words):
                        parameters[param_name] = words[param_index + 1]
                except ValueError:
                    continue
        
        return parameters 