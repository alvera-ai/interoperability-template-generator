import yaml
import json
from typing import Dict, Any, Union, TextIO
import pandas as pd

class SchemaExtractor:
    def __init__(self, openapi_file: Union[str, TextIO]):
        """Initialize with path to OpenAPI specification file or a file-like object."""
        self.openapi_file = openapi_file
        self.spec = self._load_spec()
        
    def _load_spec(self) -> Dict[str, Any]:
        """Load the OpenAPI specification from file."""
        if isinstance(self.openapi_file, str):
            # If it's a file path
            with open(self.openapi_file, 'r') as f:
                if self.openapi_file.endswith(('.yaml', '.yml')):
                    return yaml.safe_load(f)
                elif self.openapi_file.endswith('.json'):
                    return json.load(f)
                else:
                    raise ValueError("File must be either YAML or JSON")
        else:
            # If it's a file-like object
            try:
                return yaml.safe_load(self.openapi_file)
            except yaml.YAMLError:
                # If YAML parsing fails, try JSON
                self.openapi_file.seek(0)  # Reset file pointer
                return json.load(self.openapi_file)

    def _extract_schema_from_response(self, response_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON schema from a response object."""
        if not response_obj or 'content' not in response_obj:
            return {}
        
        # Try to get schema from application/json content type
        content = response_obj.get('content', {})
        json_content = content.get('application/json', {})
        return json_content.get('schema', {})

    def extract_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Extract all API endpoints and their response schemas."""
        schemas = {}
        paths = self.spec.get('paths', {})
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                endpoint_key = f"{method.upper()} {path}"
                
                # Get successful response schema (usually 200 or 201)
                responses = operation.get('responses', {})
                success_response = responses.get('200', responses.get('201', {}))
                schema = self._extract_schema_from_response(success_response)
                
                if schema:
                    # If schema references a component, resolve it
                    if '$ref' in schema:
                        ref_path = schema['$ref'].split('/')
                        schema = self.spec
                        for part in ref_path[1:]:  # Skip the first '#' part
                            schema = schema.get(part, {})
                    
                    schemas[endpoint_key] = schema

        return schemas

    def create_schema_table(self) -> pd.DataFrame:
        """Create a pandas DataFrame with endpoints and their schemas."""
        schemas = self.extract_schemas()
        
        # Convert schemas to DataFrame
        df = pd.DataFrame(
            [(k, json.dumps(v, indent=2)) for k, v in schemas.items()],
            columns=['Endpoint', 'JSON Schema']
        )
        return df

def main():
    # Example usage
    extractor = SchemaExtractor('example_openapi.yaml')
    df = extractor.create_schema_table()
    
    # Display the table
    print("\nAPI Endpoints and Their Schemas:")
    print(df.to_string(index=False))
    
    # Optionally save to CSV
    df.to_csv('api_schemas.csv', index=False)
    print("\nSchemas have been saved to 'api_schemas.csv'")

if __name__ == "__main__":
    main() 