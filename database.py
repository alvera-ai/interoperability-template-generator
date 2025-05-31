import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import re
import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Text
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "api_results.db", use_postgres: bool = False, postgres_config: Dict[str, str] = None):
        self.db_path = db_path
        self.use_postgres = use_postgres
        self.postgres_config = postgres_config or {}
        self.engine = None
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            if self.use_postgres:
                self._init_postgres()
            else:
                self._init_sqlite()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
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
                    response_headers TEXT,
                    created_table_name TEXT,
                    create_table_command TEXT
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
            
            # Create table for tracking created tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS created_tables_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    table_name TEXT UNIQUE,
                    create_command TEXT,
                    created_by_prompt TEXT,
                    api_result_id INTEGER
                )
            ''')
            
            conn.commit()
    
    def _init_postgres(self):
        """Initialize PostgreSQL database."""
        # Build connection string
        host = self.postgres_config.get('host', 'localhost')
        port = self.postgres_config.get('port', '5432')
        database = self.postgres_config.get('database', 'api_interop')
        username = self.postgres_config.get('username', 'postgres')
        password = self.postgres_config.get('password', '')
        
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(connection_string)
        
        # Create tables using SQLAlchemy
        metadata = MetaData()
        
        # API results table
        api_results = Table('api_results', metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime, default=datetime.utcnow),
            Column('user_prompt', Text),
            Column('api_endpoint', String(500)),
            Column('schema_used', Text),
            Column('response_data', Text),
            Column('status_code', Integer),
            Column('response_headers', Text),
            Column('created_table_name', String(255)),
            Column('create_table_command', Text)
        )
        
        # OpenAPI specs table
        openapi_specs = Table('openapi_specs', metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime, default=datetime.utcnow),
            Column('spec_name', String(255)),
            Column('spec_content', Text)
        )
        
        # Created tables metadata
        created_tables_metadata = Table('created_tables_metadata', metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime, default=datetime.utcnow),
            Column('table_name', String(255), unique=True),
            Column('create_command', Text),
            Column('created_by_prompt', Text),
            Column('api_result_id', Integer)
        )
        
        metadata.create_all(self.engine)
    
    def execute_create_table(self, create_command: str, user_prompt: str) -> tuple[bool, str, Optional[str]]:
        """Execute CREATE TABLE command and return success status, message, and table name."""
        try:
            # Extract table name from CREATE TABLE command
            table_name = self._extract_table_name(create_command)
            if not table_name:
                return False, "Could not extract table name from command", None
            
            if self.use_postgres:
                return self._execute_postgres_create_table(create_command, user_prompt, table_name)
            else:
                return self._execute_sqlite_create_table(create_command, user_prompt, table_name)
                
        except Exception as e:
            logger.error(f"Error executing CREATE TABLE: {e}")
            return False, f"Error executing CREATE TABLE: {str(e)}", None
    
    def _extract_table_name(self, create_command: str) -> Optional[str]:
        """Extract table name from CREATE TABLE command."""
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`)?(\w+)(?:`)?'
        match = re.search(pattern, create_command, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _execute_postgres_create_table(self, create_command: str, user_prompt: str, table_name: str) -> tuple[bool, str, str]:
        """Execute CREATE TABLE in PostgreSQL."""
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    # Execute the CREATE TABLE command
                    conn.execute(text(create_command))
                    
                    # Store metadata
                    metadata_query = text("""
                        INSERT INTO created_tables_metadata (table_name, create_command, created_by_prompt)
                        VALUES (:table_name, :create_command, :created_by_prompt)
                        ON CONFLICT (table_name) DO UPDATE SET
                        create_command = EXCLUDED.create_command,
                        created_by_prompt = EXCLUDED.created_by_prompt,
                        timestamp = CURRENT_TIMESTAMP
                    """)
                    
                    conn.execute(metadata_query, {
                        'table_name': table_name,
                        'create_command': create_command,
                        'created_by_prompt': user_prompt
                    })
            
            return True, f"Table '{table_name}' created successfully in PostgreSQL", table_name
            
        except Exception as e:
            return False, f"PostgreSQL error: {str(e)}", table_name
    
    def _execute_sqlite_create_table(self, create_command: str, user_prompt: str, table_name: str) -> tuple[bool, str, str]:
        """Execute CREATE TABLE in SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Execute the CREATE TABLE command
                cursor.execute(create_command)
                
                # Store metadata
                cursor.execute('''
                    INSERT OR REPLACE INTO created_tables_metadata 
                    (table_name, create_command, created_by_prompt, timestamp)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (table_name, create_command, user_prompt))
                
                conn.commit()
            
            return True, f"Table '{table_name}' created successfully in SQLite", table_name
            
        except Exception as e:
            return False, f"SQLite error: {str(e)}", table_name
    
    def store_api_result(self, user_prompt: str, api_endpoint: str, schema_used: str, 
                        response_data: Dict[Any, Any], status_code: int, 
                        response_headers: Dict[str, str], created_table_name: str = None,
                        create_table_command: str = None) -> int:
        """Store API call result in the database."""
        try:
            if self.use_postgres:
                return self._store_api_result_postgres(
                    user_prompt, api_endpoint, schema_used, response_data, 
                    status_code, response_headers, created_table_name, create_table_command
                )
            else:
                return self._store_api_result_sqlite(
                    user_prompt, api_endpoint, schema_used, response_data, 
                    status_code, response_headers, created_table_name, create_table_command
                )
        except Exception as e:
            logger.error(f"Error storing API result: {e}")
            raise
    
    def _store_api_result_postgres(self, user_prompt: str, api_endpoint: str, schema_used: str, 
                                  response_data: Dict[Any, Any], status_code: int, 
                                  response_headers: Dict[str, str], created_table_name: str,
                                  create_table_command: str) -> int:
        """Store API result in PostgreSQL."""
        with self.engine.connect() as conn:
            with conn.begin():
                query = text("""
                    INSERT INTO api_results 
                    (user_prompt, api_endpoint, schema_used, response_data, status_code, 
                     response_headers, created_table_name, create_table_command)
                    VALUES (:user_prompt, :api_endpoint, :schema_used, :response_data, 
                            :status_code, :response_headers, :created_table_name, :create_table_command)
                    RETURNING id
                """)
                
                result = conn.execute(query, {
                    'user_prompt': user_prompt,
                    'api_endpoint': api_endpoint,
                    'schema_used': schema_used,
                    'response_data': json.dumps(response_data),
                    'status_code': status_code,
                    'response_headers': json.dumps(response_headers),
                    'created_table_name': created_table_name,
                    'create_table_command': create_table_command
                })
                
                result_id = result.fetchone()[0]
                logger.info(f"API result stored with ID: {result_id}")
                return result_id
    
    def _store_api_result_sqlite(self, user_prompt: str, api_endpoint: str, schema_used: str, 
                                response_data: Dict[Any, Any], status_code: int, 
                                response_headers: Dict[str, str], created_table_name: str,
                                create_table_command: str) -> int:
        """Store API result in SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_results 
                (user_prompt, api_endpoint, schema_used, response_data, status_code, 
                 response_headers, created_table_name, create_table_command)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_prompt,
                api_endpoint,
                schema_used,
                json.dumps(response_data),
                status_code,
                json.dumps(response_headers),
                created_table_name,
                create_table_command
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            logger.info(f"API result stored with ID: {result_id}")
            return result_id
    
    def store_openapi_spec(self, spec_name: str, spec_content: str) -> int:
        """Store OpenAPI specification in the database."""
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    with conn.begin():
                        query = text("""
                            INSERT INTO openapi_specs (spec_name, spec_content)
                            VALUES (:spec_name, :spec_content)
                            RETURNING id
                        """)
                        
                        result = conn.execute(query, {
                            'spec_name': spec_name,
                            'spec_content': spec_content
                        })
                        
                        spec_id = result.fetchone()[0]
            else:
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
            if self.use_postgres:
                query = """
                    SELECT id, timestamp, user_prompt, api_endpoint, status_code, 
                           created_table_name, create_table_command
                    FROM api_results
                    ORDER BY timestamp DESC
                    LIMIT %s
                """
                return pd.read_sql_query(query, self.engine, params=(limit,))
            else:
                with sqlite3.connect(self.db_path) as conn:
                    query = '''
                        SELECT id, timestamp, user_prompt, api_endpoint, status_code,
                               created_table_name, create_table_command
                        FROM api_results
                        ORDER BY timestamp DESC
                        LIMIT ?
                    '''
                    return pd.read_sql_query(query, conn, params=(limit,))
        except Exception as e:
            logger.error(f"Error getting recent results: {e}")
            return pd.DataFrame()
    
    def get_created_tables(self) -> pd.DataFrame:
        """Get list of created tables."""
        try:
            if self.use_postgres:
                query = """
                    SELECT table_name, timestamp, created_by_prompt, create_command
                    FROM created_tables_metadata
                    ORDER BY timestamp DESC
                """
                return pd.read_sql_query(query, self.engine)
            else:
                with sqlite3.connect(self.db_path) as conn:
                    query = '''
                        SELECT table_name, timestamp, created_by_prompt, create_command
                        FROM created_tables_metadata
                        ORDER BY timestamp DESC
                    '''
                    return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting created tables: {e}")
            return pd.DataFrame()
    
    def get_result_details(self, result_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific API result."""
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    query = text("SELECT * FROM api_results WHERE id = :id")
                    result = conn.execute(query, {'id': result_id}).fetchone()
                    
                    if result:
                        columns = result.keys()
                        result_dict = dict(zip(columns, result))
                        
                        # Parse JSON fields
                        result_dict['response_data'] = json.loads(result_dict['response_data'])
                        result_dict['response_headers'] = json.loads(result_dict['response_headers'])
                        
                        return result_dict
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM api_results WHERE id = ?', (result_id,))
                    
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