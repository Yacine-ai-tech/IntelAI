-- Migration 004: Add Token Refresh Support for OAuth Integrations
-- Date: 2026-02-27
-- Purpose: Support OAuth token refresh and expiry tracking for long-lived integrations

-- ════════════════════════════════════════════════════════════════
-- 1. Add token expiry columns to integration_credentials table
-- ════════════════════════════════════════════════════════════════

ALTER TABLE integration_credentials
ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS refresh_token TEXT,
ADD COLUMN IF NOT EXISTS refresh_token_encrypted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS last_token_refresh TIMESTAMP,
ADD COLUMN IF NOT EXISTS token_refresh_failed_count INT DEFAULT 0;

-- Create index for efficient querying of expired tokens
CREATE INDEX IF NOT EXISTS idx_integration_creds_expires_at 
ON integration_credentials(token_expires_at) 
WHERE token_expires_at IS NOT NULL;

-- ════════════════════════════════════════════════════════════════
-- 2. Create token_refresh_metadata table for detailed tracking
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS token_refresh_metadata (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),
    integration_type TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,
    scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refresh_attempt TIMESTAMP,
    last_refresh_success TIMESTAMP,
    refresh_attempt_count INT DEFAULT 0,
    consecutive_failures INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT uk_token_refresh_metadata UNIQUE (username, integration_type),
    CONSTRAINT fk_token_refresh_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_token_refresh_expires_at 
ON token_refresh_metadata(token_expires_at)
WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_token_refresh_user 
ON token_refresh_metadata(username, integration_type);

-- ════════════════════════════════════════════════════════════════
-- 3. Create oauth_token_events table for audit trail
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS oauth_token_events (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),
    integration_type TEXT NOT NULL,
    event_type TEXT NOT NULL, -- 'token_issued', 'token_refreshed', 'token_expired', 'refresh_failed', 'revoked'
    old_expires_at TIMESTAMP,
    new_expires_at TIMESTAMP,
    error_message TEXT,
    user_agent TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_token_event_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_oauth_token_events_created_at 
ON oauth_token_events(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_oauth_token_events_user 
ON oauth_token_events(username);

-- ════════════════════════════════════════════════════════════════
-- 4. Create data_ingestion_log table for data import tracking
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS data_ingestion_log (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL, -- csv, xlsx, pdf, docx, json, sql, etc.
    source TEXT NOT NULL, -- upload, email, drive, api, etc.
    row_count INT,
    file_size_bytes INT,
    status TEXT NOT NULL, -- pending, processing, success, failed, partial
    error_message TEXT,
    import_destination TEXT, -- table name or knowledge_base
    mapping_config JSONB, -- column mappings, transformations
    preview_data JSONB, -- sample of first 5 rows
    ingested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_ingestion_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ingestion_created_at 
ON data_ingestion_log(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ingestion_user 
ON data_ingestion_log(username);

CREATE INDEX IF NOT EXISTS idx_ingestion_status 
ON data_ingestion_log(status);

-- ════════════════════════════════════════════════════════════════
-- 5. Create data_export_log table for data extraction tracking
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS data_export_log (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),
    export_name TEXT NOT NULL,
    export_format TEXT NOT NULL, -- csv, xlsx, pdf, json, sql
    source_type TEXT NOT NULL, -- query, report, dashboard, knowledge_base
    row_count INT,
    file_size_bytes INT,
    query JSONB, -- export parameters/filters
    status TEXT NOT NULL, -- pending, processing, completed, failed
    output_location TEXT, -- file path or download URL
    error_message TEXT,
    exported_at TIMESTAMP,
    expiration_at TIMESTAMP, -- when file expires and gets deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_export_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_export_created_at 
ON data_export_log(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_export_user 
ON data_export_log(username);

CREATE INDEX IF NOT EXISTS idx_export_status 
ON data_export_log(status);

-- ════════════════════════════════════════════════════════════════
-- 6. Create knowledge_base_metadata table for enhanced KG features
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS knowledge_base_metadata (
    id SERIAL PRIMARY KEY,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    doc_type TEXT, -- invoice, contract, report, email, manual, policy
    source TEXT, -- upload, email, drive, scanner, api
    language TEXT DEFAULT 'en',
    category TEXT, -- finance, hr, ops, esg, etc.
    tags TEXT[] DEFAULT '{}', -- searchable tags
    owner_username TEXT REFERENCES users(username),
    is_public BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    access_level TEXT DEFAULT 'private', -- private, team, public
    download_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    rating DECIMAL(2,1),
    embedding_model TEXT, -- which embedding model was used
    chunk_count INT,
    searchable_text TEXT, -- full-text search column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_kb_owner FOREIGN KEY (owner_username) REFERENCES users(username) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_kb_searchable_text 
ON knowledge_base_metadata USING GIN(to_tsvector('english', searchable_text));

CREATE INDEX IF NOT EXISTS idx_kb_category 
ON knowledge_base_metadata(category);

CREATE INDEX IF NOT EXISTS idx_kb_doc_type 
ON knowledge_base_metadata(doc_type);

-- ════════════════════════════════════════════════════════════════
-- 7. Create domain_preference table for user personalization
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS domain_preference (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE REFERENCES users(username) ON DELETE CASCADE,
    default_domain TEXT DEFAULT 'general', -- finance, hr, ops, esg, growth, general
    last_used_domain TEXT,
    domain_history JSONB DEFAULT '{}', -- {domain: last_used_timestamp}
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_domain_pref_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_domain_pref_user 
ON domain_preference(username);

-- ════════════════════════════════════════════════════════════════
-- 8. Create chat_session_metadata table for enhanced session tracking
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS chat_session_metadata (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT UNIQUE NOT NULL REFERENCES chat_sessions(conversation_id),
    username TEXT NOT NULL REFERENCES users(username),
    domain TEXT DEFAULT 'general',
    mode TEXT DEFAULT 'conversation', -- conversation, agent, rag, analysis, extraction
    message_count INT DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_duration_seconds INT,
    average_response_time_ms INT,
    total_tokens_used INT DEFAULT 0,
    estimated_cost_usd DECIMAL(8,4) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    closed_at TIMESTAMP,
    
    CONSTRAINT fk_session_meta_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_meta_username 
ON chat_session_metadata(username);

CREATE INDEX IF NOT EXISTS idx_session_meta_active 
ON chat_session_metadata(is_active, last_activity DESC);

-- ════════════════════════════════════════════════════════════════
-- 9. Create mini-spreadsheet table for finance/data features
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS data_spreadsheet (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT, -- finance, it, hr, ops, general
    data JSONB NOT NULL, -- array of rows: [{col1: val, col2: val}, ...]
    schema_columns JSONB, -- [{name: 'col1', type: 'text', ...}, ...]
    row_count INT DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    allow_export BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_spreadsheet_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
    CONSTRAINT uk_spreadsheet_name UNIQUE (username, name)
);

CREATE INDEX IF NOT EXISTS idx_spreadsheet_user 
ON data_spreadsheet(username);

CREATE INDEX IF NOT EXISTS idx_spreadsheet_domain 
ON data_spreadsheet(domain);

-- ════════════════════════════════════════════════════════════════
-- 10. Add cleanup triggers and functions
-- ════════════════════════════════════════════════════════════════

-- Auto-update 'updated_at' columns
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_token_refresh_metadata_update
BEFORE UPDATE ON token_refresh_metadata
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_ingestion_log_update
BEFORE UPDATE ON data_ingestion_log
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_export_log_update
BEFORE UPDATE ON data_export_log
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_kb_metadata_update
BEFORE UPDATE ON knowledge_base_metadata
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_spreadsheet_update
BEFORE UPDATE ON data_spreadsheet
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ════════════════════════════════════════════════════════════════
-- 11. Cleanup function for expired tokens and old logs
-- ════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION cleanup_expired_tokens_and_logs()
RETURNS TABLE(
    expired_tokens_deleted INT,
    old_events_deleted INT,
    old_logs_deleted INT
) AS $$
DECLARE
    v_tokens INT := 0;
    v_events INT := 0;
    v_logs INT := 0;
BEGIN
    -- Delete expired token refresh metadata (older than 30 days from expiry)
    DELETE FROM token_refresh_metadata
    WHERE is_active = FALSE
    OR token_expires_at < NOW() - INTERVAL '30 days';
    GET DIAGNOSTICS v_tokens = ROW_COUNT;
    
    -- Delete old OAuth events (older than 90 days)
    DELETE FROM oauth_token_events
    WHERE created_at < NOW() - INTERVAL '90 days';
    GET DIAGNOSTICS v_events = ROW_COUNT;
    
    -- Delete completed/failed ingestion logs older than 180 days
    DELETE FROM data_ingestion_log
    WHERE created_at < NOW() - INTERVAL '180 days'
    AND status IN ('success', 'failed');
    GET DIAGNOSTICS v_logs = ROW_COUNT;
    
    RETURN QUERY SELECT v_tokens, v_events, v_logs;
END;
$$ LANGUAGE plpgsql;

-- ════════════════════════════════════════════════════════════════
-- 12. Grant permissions to app user
-- ════════════════════════════════════════════════════════════════

-- Assume app user is 'omniintel_app'
GRANT SELECT, INSERT, UPDATE, DELETE ON token_refresh_metadata TO omniintel_app;
GRANT SELECT, INSERT ON oauth_token_events TO omniintel_app;
GRANT SELECT, INSERT, UPDATE ON data_ingestion_log TO omniintel_app;
GRANT SELECT, INSERT, UPDATE ON data_export_log TO omniintel_app;
GRANT SELECT, INSERT, UPDATE ON knowledge_base_metadata TO omniintel_app;
GRANT SELECT, INSERT, UPDATE ON domain_preference TO omniintel_app;
GRANT SELECT, INSERT, UPDATE ON chat_session_metadata TO omniintel_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON data_spreadsheet TO omniintel_app;

-- ════════════════════════════════════════════════════════════════
-- 13. Insert initial domain preferences for existing users
-- ════════════════════════════════════════════════════════════════

INSERT INTO domain_preference (username, default_domain)
SELECT username, 'general'
FROM users
ON CONFLICT (username) DO NOTHING;

-- ════════════════════════════════════════════════════════════════
-- Migration complete
-- ════════════════════════════════════════════════════════════════
-- Run cleanup_expired_tokens_and_logs() periodically (e.g., daily)
-- SELECT cleanup_expired_tokens_and_logs();
