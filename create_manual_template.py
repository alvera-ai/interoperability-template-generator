#!/usr/bin/env python3
"""
Script to manually create a working conversion template for the demo
Run this script to insert a working template into your database
"""

import sqlite3
import json
from datetime import datetime

# Conversion logic that works correctly
CONVERSION_LOGIC = '''# Initialize output data dictionary
output_data = {}

# Direct field mappings with type conversion
if 'id' in input_data:
    output_data['user_id'] = int(input_data['id'])

if 'name' in input_data:
    output_data['full_name'] = str(input_data['name'])

if 'username' in input_data:
    output_data['username'] = str(input_data['username'])

if 'email' in input_data:
    output_data['email'] = str(input_data['email'])

if 'phone' in input_data:
    output_data['phone'] = str(input_data['phone'])

if 'website' in input_data:
    output_data['website'] = str(input_data['website'])

# Handle nested address object safely
if 'address' in input_data and isinstance(input_data['address'], dict):
    address = input_data['address']
    
    if 'street' in address:
        output_data['street'] = str(address['street'])
    
    if 'suite' in address:
        output_data['suite'] = str(address['suite'])
    
    if 'city' in address:
        output_data['city'] = str(address['city'])
    
    if 'zipcode' in address:
        output_data['zipcode'] = str(address['zipcode'])
    
    # Handle nested geo coordinates
    if 'geo' in address and isinstance(address['geo'], dict):
        geo = address['geo']
        
        if 'lat' in geo:
            try:
                output_data['latitude'] = float(geo['lat'])
            except (ValueError, TypeError):
                output_data['latitude'] = None
        
        if 'lng' in geo:
            try:
                output_data['longitude'] = float(geo['lng'])
            except (ValueError, TypeError):
                output_data['longitude'] = None

# Handle nested company object safely
if 'company' in input_data and isinstance(input_data['company'], dict):
    company = input_data['company']
    
    if 'name' in company:
        output_data['company_name'] = str(company['name'])
    
    if 'catchPhrase' in company:
        output_data['company_catchphrase'] = str(company['catchPhrase'])
    
    if 'bs' in company:
        output_data['company_bs'] = str(company['bs'])

# Provide defaults for required fields
if 'user_id' not in output_data:
    output_data['user_id'] = 0

if 'full_name' not in output_data:
    output_data['full_name'] = 'Unknown User'

if 'username' not in output_data:
    output_data['username'] = 'unknown'

if 'email' not in output_data:
    output_data['email'] = 'unknown@example.com'
'''

API_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "suite": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"},
                "geo": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "string"},
                        "lng": {"type": "string"}
                    }
                }
            }
        },
        "phone": {"type": "string"},
        "website": {"type": "string", "format": "uri"},
        "company": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "catchPhrase": {"type": "string"},
                "bs": {"type": "string"}
            }
        }
    },
    "required": ["id", "name", "username", "email"]
}

DB_SCHEMA = '''CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    website VARCHAR(200),
    street VARCHAR(100),
    suite VARCHAR(50),
    city VARCHAR(50),
    zipcode VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    company_name VARCHAR(100),
    company_catchphrase TEXT,
    company_bs TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);'''

def create_manual_template():
    """Create a working conversion template manually."""
    
    # Connect to the SQLite database
    db_path = "api_results.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if conversion_templates table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversion_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    openapi_spec_name TEXT NOT NULL,
                    api_response_schema TEXT NOT NULL,
                    db_table_schema TEXT NOT NULL,
                    conversion_logic TEXT NOT NULL,
                    created_by TEXT DEFAULT 'manual',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert the working template
            cursor.execute("""
                INSERT OR REPLACE INTO conversion_templates 
                (template_name, openapi_spec_name, api_response_schema, db_table_schema, conversion_logic, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'users_api_to_db_template',
                'JSONPlaceholder Users API',
                json.dumps(API_SCHEMA),
                DB_SCHEMA,
                CONVERSION_LOGIC,
                'manual_script'
            ))
            
            conn.commit()
            print("✅ Working conversion template created successfully!")
            print("Template name: 'users_api_to_db_template'")
            print("You can now use this template in your app for the demo.")
            
    except Exception as e:
        print(f"❌ Error creating template: {e}")

if __name__ == "__main__":
    create_manual_template() 