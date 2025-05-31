import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "api_results.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create table for API call results
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_prompt TEXT,
                        api_endpoint TEXT,
                        schema_used TEXT,
                        response_data TEXT,
                        status_code INTEGER,
                        response_headers TEXT
                    )
                ''')
                
                # Create table for OpenAPI specs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS openapi_specs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        spec_name TEXT,
                        spec_content TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def store_api_result(self, user_prompt: str, api_endpoint: str, schema_used: str, 
                        response_data: Dict[Any, Any], status_code: int, 
                        response_headers: Dict[str, str]) -> int:
        """Store API call result in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO api_results 
                    (user_prompt, api_endpoint, schema_used, response_data, status_code, response_headers)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_prompt,
                    api_endpoint,
                    schema_used,
                    json.dumps(response_data),
                    status_code,
                    json.dumps(response_headers)
                ))
                
                result_id = cursor.lastrowid
                conn.commit()
                logger.info(f"API result stored with ID: {result_id}")
                return result_id
        except Exception as e:
            logger.error(f"Error storing API result: {e}")
            raise
    
    def store_openapi_spec(self, spec_name: str, spec_content: str) -> int:
        """Store OpenAPI specification in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO openapi_specs (spec_name, spec_content)
                    VALUES (?, ?)
                ''', (spec_name, spec_content))
                
                spec_id = cursor.lastrowid
                conn.commit()
                logger.info(f"OpenAPI spec stored with ID: {spec_id}")
                return spec_id
        except Exception as e:
            logger.error(f"Error storing OpenAPI spec: {e}")
            raise
    
    def get_recent_results(self, limit: int = 10) -> pd.DataFrame:
        """Get recent API call results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT id, timestamp, user_prompt, api_endpoint, status_code
                    FROM api_results
                    ORDER BY timestamp DESC
                    LIMIT ?
                '''
                df = pd.read_sql_query(query, conn, params=(limit,))
                return df
        except Exception as e:
            logger.error(f"Error getting recent results: {e}")
            return pd.DataFrame()
    
    def get_result_details(self, result_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific API result."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM api_results WHERE id = ?
                ''', (result_id,))
                
                result = cursor.fetchone()
                if result:
                    columns = [description[0] for description in cursor.description]
                    result_dict = dict(zip(columns, result))
                    
                    # Parse JSON fields
                    result_dict['response_data'] = json.loads(result_dict['response_data'])
                    result_dict['response_headers'] = json.loads(result_dict['response_headers'])
                    
                    return result_dict
                return {}
        except Exception as e:
            logger.error(f"Error getting result details: {e}")
            return {} 