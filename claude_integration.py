import json
import logging
from typing import Dict, Any, Tuple, Optional
from config import config

logger = logging.getLogger(__name__)

# Only import anthropic if we have an API key
anthropic = None
if config.has_anthropic_key():
    try:
        import anthropic
    except ImportError:
        logger.error("Anthropic library not installed. Run: pip install anthropic")

class ClaudeTemplateGenerator:
    """Generate conversion templates using Claude AI."""
    
    def __init__(self):
        self.client = None
        if config.has_anthropic_key() and anthropic:
            try:
                self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
                logger.info("Claude client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
    
    def is_available(self) -> bool:
        """Check if Claude integration is available."""
        return self.client is not None
    
    def generate_conversion_template(self, 
                                   openapi_spec_name: str,
                                   api_response_schema: Dict[str, Any], 
                                   db_table_schema: str,
                                   table_name: str) -> Tuple[bool, str, str]:
        """Generate a conversion template using Claude."""
        
        if not self.is_available():
            return False, "Claude integration not available. Check API key configuration.", ""
        
        try:
            # Prepare the prompt for Claude
            prompt = self._create_conversion_prompt(
                openapi_spec_name, api_response_schema, db_table_schema, table_name
            )
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the conversion logic from Claude's response
            response_text = message.content[0].text if message.content else ""
            conversion_logic = self._extract_conversion_logic(response_text)
            
            if conversion_logic:
                return True, "Conversion template generated successfully", conversion_logic
            else:
                return False, "Failed to extract valid conversion logic from Claude's response", ""
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return False, f"Error calling Claude API: {str(e)}", ""
    
    def _create_conversion_prompt(self, 
                                openapi_spec_name: str,
                                api_response_schema: Dict[str, Any], 
                                db_table_schema: str,
                                table_name: str) -> str:
        """Create a prompt for Claude to generate conversion logic."""
        
        return f"""
You are an expert data transformation engineer. I need you to generate Python code that converts JSON data from an OpenAPI response format to a database-compatible format.

**OpenAPI Spec Name:** {openapi_spec_name}

**API Response Schema (JSON Schema format):**
```json
{json.dumps(api_response_schema, indent=2)}
```

**Target Database Table Schema (CREATE TABLE statement):**
```sql
{db_table_schema}
```

**Target Table Name:** {table_name}

**CRITICAL REQUIREMENTS:**
1. ALWAYS initialize `output_data = {{}}` at the beginning
2. NEVER create empty if statements - always include a body with at least a pass statement
3. Handle field mapping, data type conversions, and any necessary transformations
4. Only include fields that exist in both the API response and database table
5. Handle missing or null values appropriately with proper defaults
6. The code must be syntactically correct Python
7. Use only these available variables: `input_data`, `output_data`, `json`
8. Include proper error handling for type conversions
9. Provide sensible defaults for required fields

**MANDATORY Structure - Follow this pattern:**
```python
# Initialize output data dictionary
output_data = {{}}

# Direct field mappings with type conversion
if 'api_field' in input_data:
    output_data['db_field'] = str(input_data['api_field'])

# Handle nested objects safely
if 'nested_object' in input_data and isinstance(input_data['nested_object'], dict):
    nested = input_data['nested_object']
    if 'field' in nested:
        output_data['mapped_field'] = str(nested['field'])

# Provide defaults for required fields
if 'required_field' not in output_data:
    output_data['required_field'] = 'default_value'
```

Generate ONLY valid Python code that follows this structure. Do not include markdown formatting, explanations, or any text outside the Python code:
"""

    def _extract_conversion_logic(self, response_text: str) -> str:
        """Extract Python code from Claude's response."""
        try:
            # Look for code blocks
            if '```python' in response_text:
                start = response_text.find('```python') + 9
                end = response_text.find('```', start)
                if end > start:
                    return response_text[start:end].strip()
            
            # If no code blocks, look for code-like patterns
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                if end > start:
                    return response_text[start:end].strip()
            
            # If no code blocks found, try to extract Python-like content
            lines = response_text.split('\n')
            python_lines = []
            in_code = False
            
            for line in lines:
                stripped = line.strip()
                if any(keyword in stripped for keyword in ['output_data', 'input_data', 'if ', 'for ', '=']):
                    in_code = True
                    python_lines.append(line)
                elif in_code and (stripped == '' or stripped.startswith('#')):
                    python_lines.append(line)
                elif in_code and not any(char in stripped for char in ['.', ':', '(', ')']):
                    break
                elif not in_code and stripped.startswith('#'):
                    python_lines.append(line)
            
            if python_lines:
                return '\n'.join(python_lines)
            
            # Fallback: return the entire response if it looks like code
            if 'output_data' in response_text and 'input_data' in response_text:
                return response_text.strip()
                
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting conversion logic: {e}")
            return ""
    
    def test_conversion_logic(self, 
                            conversion_logic: str, 
                            test_input: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Test the generated conversion logic with sample data."""
        try:
            # Create a safe execution environment
            safe_globals = {
                'json': json,
                'input_data': test_input,
                'output_data': {}
            }
            
            # Execute the conversion logic
            exec(conversion_logic, safe_globals)
            output_data = safe_globals.get('output_data', {})
            
            if output_data:
                return True, "Test successful", output_data
            else:
                return False, "No output data generated", {}
                
        except Exception as e:
            return False, f"Test failed: {str(e)}", {}

# Global instance
claude_generator = ClaudeTemplateGenerator() 