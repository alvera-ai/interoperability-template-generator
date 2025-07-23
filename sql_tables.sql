-- CREATE TABLE statements based on example_openapi.yaml schemas
-- These tables are designed to store user and address data from a REST API
-- The schema follows OpenAPI 3.0.3 specification for JSONPlaceholder API

-- =============================================================================
-- ADDRESS TABLE
-- =============================================================================
-- Purpose: Stores address information for users
-- Source: Maps to OpenAPI schema '#/components/schemas/Address' and nested 'Geo'
-- Relationship: Referenced by User table (one-to-many: one address can have multiple users)
CREATE TABLE address (
    -- Primary key: Auto-incrementing identifier for internal database use
    id SERIAL PRIMARY KEY,
    
    -- Address fields from OpenAPI Address schema
    street VARCHAR(255),           -- Maps to: address.street (string)
    suite VARCHAR(100),            -- Maps to: address.suite (string) 
    city VARCHAR(100),             -- Maps to: address.city (string)
    zipcode VARCHAR(20),           -- Maps to: address.zipcode (string)
    
    -- Geo coordinates from nested Geo object - flattened for easier querying
    latitude VARCHAR(50),          -- Maps to: address.geo.lat (string) - stored as string per API
    longitude VARCHAR(50),         -- Maps to: address.geo.lng (string) - stored as string per API
    
    -- Audit fields for tracking record lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When record was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When record was last modified
);

-- =============================================================================
-- USER TABLE  
-- =============================================================================
-- Purpose: Stores user information from JSONPlaceholder API
-- Source: Maps to OpenAPI schema '#/components/schemas/User'
-- API Endpoint: GET /users/{userId} returns this schema structure
-- Relationships: 
--   - References address table (many-to-one: multiple users can share an address)
--   - Company info is flattened into this table (denormalized for simplicity)
CREATE TABLE user (
    -- Primary key: Uses API's user ID directly (not auto-increment)
    id BIGINT PRIMARY KEY,         -- Maps to: User.id (integer, format: int64, required)
    
    -- Required user identification fields from OpenAPI User schema
    name VARCHAR(255) NOT NULL,    -- Maps to: User.name (string, required) - Full name
    username VARCHAR(100) NOT NULL UNIQUE,  -- Maps to: User.username (string, required) - Unique login name
    email VARCHAR(255) NOT NULL,   -- Maps to: User.email (string, format: email, required)
    
    -- Optional user contact and web presence fields
    phone VARCHAR(50),             -- Maps to: User.phone (string, optional)
    website VARCHAR(500),          -- Maps to: User.website (string, format: uri, optional)
    
    -- Foreign key relationship to address table
    address_id INTEGER REFERENCES address(id),  -- Maps to: User.address (object reference)
    
    -- Company information flattened from nested Company object
    -- Alternative: Could be normalized into separate company table (see commented section below)
    company_name VARCHAR(255),     -- Maps to: User.company.name (string)
    company_catch_phrase TEXT,     -- Maps to: User.company.catchPhrase (string) - can be long text
    company_bs TEXT,               -- Maps to: User.company.bs (string) - business description
    
    -- Audit fields for tracking record lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When user record was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When user record was last modified
    
    -- Note: Email validation removed for SQLite compatibility
    -- In production, implement email validation at the application layer
);

-- =============================================================================
-- ALTERNATIVE NORMALIZED DESIGN (COMMENTED OUT)
-- =============================================================================
-- If you prefer a fully normalized design with separate Company table:
-- This approach reduces data duplication if multiple users work for the same company

-- Company table for normalized design
-- CREATE TABLE company (
--     id SERIAL PRIMARY KEY,              -- Auto-increment company ID
--     name VARCHAR(255),                  -- Maps to: User.company.name
--     catch_phrase TEXT,                  -- Maps to: User.company.catchPhrase  
--     bs TEXT,                           -- Maps to: User.company.bs
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- User table with company foreign key (alternative to above)
-- CREATE TABLE user_with_company_fk (
--     id BIGINT PRIMARY KEY,                        -- Maps to: User.id
--     name VARCHAR(255) NOT NULL,                   -- Maps to: User.name
--     username VARCHAR(100) NOT NULL UNIQUE,       -- Maps to: User.username
--     email VARCHAR(255) NOT NULL,                  -- Maps to: User.email
--     phone VARCHAR(50),                           -- Maps to: User.phone
--     website VARCHAR(500),                        -- Maps to: User.website
--     address_id INTEGER REFERENCES address(id),   -- Maps to: User.address
--     company_id INTEGER REFERENCES company(id),   -- Maps to: User.company (normalized)
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--     
--     -- Note: Email validation removed for SQLite compatibility
--     -- In production, implement email validation at the application layer
-- );

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================
-- These indexes optimize common query patterns for user lookup and filtering

-- User table indexes for fast lookups
CREATE INDEX idx_user_username ON user(username);      -- Fast username-based authentication
CREATE INDEX idx_user_email ON user(email);           -- Fast email-based user lookup  
CREATE INDEX idx_user_address_id ON user(address_id); -- Fast joins between user and address

-- Address table indexes for geographic queries
CREATE INDEX idx_address_city ON address(city);       -- Fast city-based filtering
CREATE INDEX idx_address_zipcode ON address(zipcode); -- Fast postal code lookups

-- =============================================================================
-- USAGE NOTES FOR AI CONVERSION TEMPLATES
-- =============================================================================
-- When converting JSON from API responses to database records:
--
-- 1. USER DATA MAPPING:
--    - API field "id" -> user.id (direct mapping)
--    - API field "name" -> user.name (direct mapping)  
--    - API field "username" -> user.username (direct mapping)
--    - API field "email" -> user.email (direct mapping)
--    - API field "phone" -> user.phone (direct mapping)
--    - API field "website" -> user.website (direct mapping)
--
-- 2. NESTED COMPANY OBJECT FLATTENING:
--    - API field "company.name" -> user.company_name
--    - API field "company.catchPhrase" -> user.company_catch_phrase  
--    - API field "company.bs" -> user.company_bs
--
-- 3. ADDRESS HANDLING (TWO-STEP PROCESS):
--    - First insert address data into address table
--    - Get the generated address.id from the insert
--    - Use that address.id as user.address_id foreign key
--
-- 4. NESTED ADDRESS AND GEO MAPPING:
--    - API field "address.street" -> address.street
--    - API field "address.suite" -> address.suite
--    - API field "address.city" -> address.city  
--    - API field "address.zipcode" -> address.zipcode
--    - API field "address.geo.lat" -> address.latitude
--    - API field "address.geo.lng" -> address.longitude 