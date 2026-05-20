# 🚀 OmniIntelOS Integration & Migration Guide

## Overview

This guide covers the major merge and integration work completed for OmniIntelOS:

1. **Merged Chatbot Services** - Combined `advanced_chatbot.py` and `unified_chatbot.py` into `omnismart_chatbot.py`
2. **Database Migrations** - Added token refresh, data ingestion/export, and mini-spreadsheet support
3. **Token Refresh Implementation** - OAuth token lifecycle management with automatic refresh
4. **API Enhancements** - New endpoints for domain switching, data management, and monitoring
5. **Data Ingestion & Export** - Full support for importing and exporting data in multiple formats
6. **Mini-Spreadsheet** - Excel-like functionality for data management

---

## 1. New Chatbot Service: `omnismart_chatbot.py`

### What Changed

**Merged Features:**
- ✅ All 5 Groq patterns from `advanced_chatbot.py`
- ✅ CFO Agent functionality (now generalized as `LightweightConversationalAgent`)
- ✅ Full LangChain integration (optional, lazy-loaded)
- ✅ Knowledge base querying with semantic search
- ✅ Unified chatbot routing logic

### Import Changes

**Old:**
```python
from src.services.advanced_chatbot import AdvancedChatbot
from src.services.unified_chatbot import UnifiedChatbot
```

**New:**
```python
from src.services.omnismart_chatbot import OmniSmartChatbot

# Or use backward-compatible aliases:
from src.services.omnismart_chatbot import AdvancedChatbot, UnifiedChatbot
```

### Usage Example

```python
from src.services.omnismart_chatbot import OmniSmartChatbot

# Create instance with domain personalization
chatbot = OmniSmartChatbot(
    conversation_id="user_session_123",
    domain="finance",  # Personalizes to finance mode
    username="john_doe"
)

# Process query with automatic intent detection
result = chatbot.process(
    message="Analyze our Q4 revenue trends",
    mode="auto",  # auto, agent, rag, analysis, extraction, conversation
    context="Additional context..."
)

print(result["response"])
print(result["type"])  # Shows which pattern was used

# Switch domain dynamically
chatbot.set_domain("growth")

# Clear history
chatbot.clear_history()
```

### New Features

#### 1. Knowledge Base Integration in Conversation

The `LightweightConversationalAgent` now automatically queries the knowledge base:

```python
# In conversation mode, the agent will:
# 1. Detect conversation intent
# 2. Query knowledge base for relevant documents
# 3. Inject KB results into system prompt
# 4. Generate response with citations

response = chatbot.conversational.chat(
    "What's our Q4 forecast?",
    use_knowledge_base=True  # Enabled by default
)
```

#### 2. Multi-Domain Personalization

```python
chatbot = OmniSmartChatbot(domain="finance")

# Domain-specific capabilities enabled:
# - finance: KPI analysis, forecasting, reporting
# - hr: Team dynamics, compensation, recruitment
# - ops: Efficiency, quality, process improvement
# - esg: Sustainability, compliance, reporting
# - growth: Acquisition, retention, expansion
# - general: Cross-domain intelligence
```

#### 3. Data Ingestion & Embedding

```python
from src.services.omnismart_chatbot import ingest_document

result = ingest_document(
    title="Q4 Financial Report",
    content=open("report.pdf").read(),
    source="pdf_upload",
    doc_type="report",
    language="en",
    metadata={"domain": "finance"}
)

print(f"Ingested {result['chunks_count']} chunks")
```

---

## 2. Database Migrations

### Migration File

**Location:** `migrations/004_add_token_refresh_support.sql`

**Run Migration:**
```bash
psql $DATABASE_URL < migrations/004_add_token_refresh_support.sql
```

### New Tables

#### 1. `token_refresh_metadata`
- Stores OAuth refresh tokens (encrypted)
- Tracks token expiry and refresh attempts
- Supports automatic token rotation

#### 2. `oauth_token_events`
- Audit trail for all token lifecycle events
- Tracks refreshes, expirations, failures
- Useful for debugging OAuth issues

#### 3. `data_ingestion_log`
- Tracks all data import operations
- Stores file metadata, row counts, errors
- Enables audit trail and retry logic

#### 4. `data_export_log`
- Tracks all data export operations
- Stores export format, size, location
- Manages export file lifecycle (expiration)

#### 5. `knowledge_base_metadata`
- Enhanced knowledge base document tracking
- Supports tagging, categorization, access control
- Tracks embeddings model and chunk count

#### 6. `domain_preference`
- User domain preferences for chatbot personalization
- Tracks domain usage history

#### 7. `chat_session_metadata`
- Enhanced session tracking
- Tracks tokens used, response times, costs

#### 8. `data_spreadsheet`
- Mini-spreadsheet storage (Excel-like data)
- Supports multiple domains (finance, IT, etc.)
- Public/private access control

---

## 3. OAuth Token Refresh Implementation

### Overview

The OAuth callback now implements full token lifecycle management:

```
1. Exchange code for tokens    → 2. Store access token (encrypted)
3. Extract refresh token       → 4. Store refresh metadata
5. Calculate expiry           → 6. Record event in audit trail
```

### Backend Changes in `server_v2.py`

**Updated OAuth Callback:**
```python
@app.get("/api/v1/integrations/{integration_type}/oauth/callback")
async def oauth_callback(integration_type: str, request: Request):
    """
    Now handles:
    1. Token exchange (code → access_token)
    2. Refresh token storage (encrypted)
    3. Expiry calculation (expires_in from provider)
    4. Audit trail recording (oauth_token_events)
    """
```

### Helper Functions Added to `pg_store.py`

```python
# Store refresh token
store_token_refresh_metadata(
    username="john_doe",
    integration_type="gmail",
    refresh_token="refresh_token_xyz",
    token_expires_at="2026-02-27T10:30:00Z",
    scope="https://www.googleapis.com/auth/gmail.readonly"
)

# Retrieve refresh token
metadata = get_token_refresh_metadata("john_doe", "gmail")
# Returns: {
#   "refresh_token": "...",
#   "token_expires_at": "...",
#   "scope": "...",
#   "consecutive_failures": 0
# }

# Update refresh status
update_token_refresh_status(
    username="john_doe",
    integration_type="gmail",
    success=True,
    new_expires_at="2026-02-28T10:30:00Z"
)

# Record token event
record_oauth_token_event(
    username="john_doe",
    integration_type="gmail",
    event_type="token_refreshed",
    old_expires_at="...",
    new_expires_at="..."
)
```

### Next Steps: Automated Token Refresh (Not Yet Implemented)

To implement automatic token refresh, you would:

1. Create a background task that runs every hour
2. Query `token_refresh_metadata` for tokens expiring soon
3. Call provider's refresh endpoint with refresh_token
4. Update stored credentials with new access_token
5. Log event in `oauth_token_events`

Example task (to add to server startup):

```python
async def refresh_expiring_tokens():
    """Periodically refresh OAuth tokens about to expire."""
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour
            
            # Get tokens expiring in next hour
            # Call refresh endpoint
            # Update credentials
            # Log event
            
        except Exception as e:
            log.error("Token refresh error: %s", e)
```

---

## 4. New API Endpoints

### Domain Switching

#### Set Domain
```
POST /api/v1/chatbot/domain?domain=finance
```

**Response:**
```json
{
  "status": "success",
  "domain": "finance",
  "message": "Chatbot domain switched to finance"
}
```

#### Get Domain
```
GET /api/v1/chatbot/domain
```

**Response:**
```json
{
  "domain": "finance",
  "valid_domains": ["finance", "hr", "ops", "esg", "growth", "general"]
}
```

### Data Ingestion

#### Ingest Data
```
POST /api/v1/data/ingest
  file: (multipart file)
  request_data: {
    "file_type": "csv|xlsx|pdf|docx|json",
    "source": "upload|email|drive|api",
    "destination": "kpis|knowledge_base|spreadsheet",
    "destination_name": "optional - for spreadsheet",
    "domain": "optional - finance, hr, etc.",
    "description": "optional"
  }
```

**Supported Combinations:**

| File Type | Destination | Use Case |
|-----------|------------|----------|
| CSV, XLSX | kpis | Import metric data |
| CSV, XLSX | spreadsheet | Store for analysis |
| PDF, DOCX | knowledge_base | Index documents for RAG |
| JSON | any | Structure data |

### Data Export

#### Export Data
```
POST /api/v1/data/export
  {
    "source_type": "kpis|spreadsheet|conversation|knowledge_base",
    "format": "csv|xlsx|json|pdf",
    "source_name": "optional - for spreadsheet",
    "query": "optional - filter parameters"
  }
```

**Response:**
```json
{
  "status": "success",
  "export_id": 123,
  "format": "csv",
  "filename": "kpis_export.csv",
  "data": "csv_content_here",
  "download_url": "/api/v1/exports/123/download"
}
```

### Mini-Spreadsheet Management

#### Create Spreadsheet
```
POST /api/v1/spreadsheets
  {
    "name": "Q4 Budget",
    "domain": "finance",
    "description": "Q4 budget tracking",
    "schema_columns": [
      {"name": "department", "type": "text"},
      {"name": "budget", "type": "number"},
      {"name": "spent", "type": "number"}
    ],
    "is_public": false
  }
```

#### Get Spreadsheet Data
```
GET /api/v1/spreadsheets/{spreadsheet_name}
```

**Response:**
```json
{
  "name": "Q4 Budget",
  "data": [
    {"department": "Engineering", "budget": 100000, "spent": 75000},
    {"department": "Marketing", "budget": 50000, "spent": 40000}
  ],
  "schema_columns": [...],
  "row_count": 2
}
```

### Admin Monitoring

#### Background Tasks Status
```
GET /api/v1/admin/tasks/status (admin only)
```

**Response:**
```json
{
  "status": "healthy",
  "tasks": {
    "oauth_state_cleanup": {
      "enabled": true,
      "interval_minutes": 30,
      "last_cleaned_count": 5,
      "next_run": "auto (30 min)"
    },
    "token_refresh": {
      "enabled": true,
      "interval_hours": 1,
      "status": "monitoring"
    },
    "data_export_cleanup": {
      "enabled": true,
      "interval_hours": 24,
      "action": "Delete exports older than 7 days"
    }
  },
  "timestamp": "2026-02-27T..."
}
```

---

## 5. Data Ingestion & Export Features

### Supported File Formats

**Import:**
- CSV (comma-separated values)
- XLSX (Excel workbook)
- PDF (Portable Document Format)
- DOCX (Word document)
- JSON (JavaScript Object Notation)

**Export:**
- CSV (text format)
- XLSX (Excel workbook)
- JSON (structured data)
- PDF (formatted document)

### Ingestion Workflow

```
User uploads file
    ↓
Detect file type
    ↓
Parse content
    ↓
Choose destination (KPIs, Knowledge Base, Spreadsheet)
    ↓
Transform data if needed
    ↓
Store in database
    ↓
Log ingestion event
    ↓
Return success/error
```

### Knowledge Base Ingestion

```python
from src.services.omnismart_chatbot import ingest_document

result = ingest_document(
    title="Finance Report Q4",
    content=pdf_text,
    source="email",  # or "upload", "drive", "scanner"
    doc_type="report",
    language="en",
    metadata={
        "domain": "finance",
        "urgency": "high"
    }
)

# Result includes:
# - chunks_count: 15
# - embedding_model: "all-MiniLM-L6-v2"
# - indexing status
```

### Export with Filters

```python
# Export filtered KPI data
POST /api/v1/data/export
{
  "source_type": "kpis",
  "format": "csv",
  "query": {
    "category": "finance",
    "period_start": "2025-01",
    "period_end": "2025-12"
  }
}
```

---

## 6. Mini-Spreadsheet Features

### What It Is

A lightweight, in-database spreadsheet solution:
- Store structured data (like Excel)
- Support for multiple domains (finance, IT, HR, etc.)
- Easy export to CSV/XLSX
- Per-user and team-based data

### Typical Use Cases

1. **Finance:** Budget tracking, expense reports, forecasts
2. **IT:** Inventory, incident tracking, capacity planning
3. **HR:** Hiring pipeline, compensation review, training plans
4. **Operations:** KPI tracking, process metrics, project tracking

### API Usage

```python
# 1. Create spreadsheet
POST /api/v1/spreadsheets
{
  "name": "FY2026 Budget",
  "domain": "finance",
  "schema_columns": [
    {"name": "department", "type": "text"},
    {"name": "budget_usd", "type": "number"},
    {"name": "spent_usd", "type": "number"}
  ]
}

# 2. Get data
GET /api/v1/spreadsheets/FY2026%20Budget

# 3. Export
POST /api/v1/data/export
{
  "source_type": "spreadsheet",
  "source_name": "FY2026 Budget",
  "format": "csv"
}

# 4. Import from CSV
POST /api/v1/data/ingest
{
  "file_type": "csv",
  "destination": "spreadsheet",
  "destination_name": "FY2026 Budget"
}
```

---

## 7. Migration Checklist

### Before Running

- [ ] Backup PostgreSQL database
- [ ] Review migration SQL for compatibility
- [ ] Ensure app user has necessary permissions

### During Migration

```bash
# 1. Apply database migration
psql $DATABASE_URL < migrations/004_add_token_refresh_support.sql

# 2. Verify new tables exist
psql $DATABASE_URL -c "\dt" | grep token_refresh_metadata

# 3. Check constraints
psql $DATABASE_URL -c "\d token_refresh_metadata"

# 4. Verify indexes
psql $DATABASE_URL -c "\di" | grep idx_
```

### After Migration

- [ ] Restart application server
- [ ] Test OAuth flow (should now store refresh tokens)
- [ ] Test data ingestion endpoint
- [ ] Test export functionality
- [ ] Monitor logs for errors

### Python Application Updates

```python
# Update imports to use new chatbot
from src.services.omnismart_chatbot import OmniSmartChatbot

# Or use the module-level import
from src.services import OmniSmartChatbot

# Backward compatibility maintained
from src.services.omnismart_chatbot import AdvancedChatbot  # Still works!
```

---

## 8. Background Tasks & Monitoring

### OAuth State Cleanup (Every 30 minutes)

- Deletes expired OAuth states from `oauth_states` table
- Prevents unauthorized token re-use
- Runs automatically in background

### Token Refresh Monitoring (Every hour)

- Checks tokens expiring in next 60 minutes
- Updates `token_refresh_metadata.consecutive_failures`
- Ready for automatic refresh implementation

### Data Export Cleanup (Daily)

- Deletes exports older than 7 days
- Frees up disk space
- Prevents storage bloat

### Monitoring Endpoint

```python
# Admin only
GET /api/v1/admin/tasks/status

# Returns health of all background tasks
```

---

## 9. Error Handling & Recovery

### Token Refresh Failures

```python
# Automatic tracking in token_refresh_metadata
update_token_refresh_status(
    username="john_doe",
    integration_type="gmail",
    success=False,
    error_message="Invalid refresh token"
)

# After 3 consecutive failures, mark integration as inactive
# User will need to re-authenticate
```

### Ingestion Failures

```python
# Logged in data_ingestion_log
log_data_ingestion(
    username="john_doe",
    filename="data.csv",
    status="failed",
    error_message="Invalid CSV format: missing required column 'date'"
)
```

### Export Failures

```python
# Logged in data_export_log
update_export_log(
    export_id=123,
    status="failed",
    error_message="Memory limit exceeded for large dataset"
)
```

---

## 10. Performance Considerations

### Knowledge Base Search

- Uses semantic similarity (if SBERT available)
- Falls back to TF-IDF vectorization
- Then falls back to keyword matching
- Configurable top_k results (default 5)

### Data Ingestion

- Chunks large documents (default 512 tokens, 128 overlap)
- Generates embeddings if available
- Runs asynchronously to avoid blocking

### Spreadsheet Operations

- Stored as JSON in PostgreSQL
- Efficient for small-medium datasets (<10K rows)
- For larger datasets, consider KPI table instead

### Export Performance

- Streams CSV data (memory efficient)
- Binary export (XLSX) buffered in-memory
- Consider async job for very large exports

---

## 11. Security Considerations

### Token Storage

- Refresh tokens encrypted with Fernet (symmetric encryption)
- Encryption key derived from `SECRET_KEY`
- Encrypted at rest in PostgreSQL

### Access Control

- Data ingestion/export: Requires authentication
- Spreadsheets: Per-user or team-based
- Admin endpoints: Require admin role

### Audit Trail

- All token events logged in `oauth_token_events`
- All ingestion/export logged with user, timestamp, status
- Useful for compliance and debugging

---

## 12. Troubleshooting

### Issue: OAuth Callback Fails After Migration

**Solution:** Ensure `token_refresh_metadata` table exists and app user has INSERT permissions.

```bash
psql $DATABASE_URL -c "GRANT INSERT ON token_refresh_metadata TO omniintel_app;"
```

### Issue: Data Ingestion Says "File Type Not Supported"

**Solution:** Check supported file types:
- kpis destination: CSV, XLSX
- knowledge_base: Any (PDF, DOCX parsed as text)
- spreadsheet: CSV, XLSX

### Issue: Export Memory Error on Large Dataset

**Solution:** Use CSV format (streamed) instead of XLSX (buffered). Or export in chunks.

### Issue: Knowledge Base Queries Return No Results

**Solution:** Ensure documents were ingested successfully:

```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM knowledge_docs LIMIT 5;"
```

---

## 13. Next Steps

### Recommended Implementation Order

1. ✅ **Deploy OmniSmartChatbot** (completed)
2. ✅ **Run Database Migrations** (completed)
3. ✅ **Implement OAuth Token Refresh in Callback** (completed)
4. ✅ **Add API Endpoints** (completed)
5. ⏳ **Implement Automatic Token Refresh Task** (ready for implementation)
6. ⏳ **Add Frontend Integration for Data Management**
7. ⏳ **Implement Advanced Analytics Dashboard**
8. ⏳ **Setup Performance Monitoring & Alerts**

### Future Enhancements

- [ ] Real-time data ingestion from APIs (Salesforce, HubSpot, etc.)
- [ ] Advanced CSV mapping and transformation
- [ ] Multi-sheet XLSX support in spreadsheets
- [ ] Data validation and quality checks
- [ ] Scheduled exports and reports
- [ ] Data versioning and audit trail
- [ ] Collaborative spreadsheet editing
- [ ] Cell-level permissions and privacy

---

## Quick Reference: API Endpoints

```
# Chat & Domain
POST   /api/v1/chat
POST   /api/v1/chatbot/domain?domain=finance
GET    /api/v1/chatbot/domain

# Data Management
POST   /api/v1/data/ingest (multipart form data)
POST   /api/v1/data/export
GET    /api/v1/exports/{export_id}/download

# Spreadsheets
POST   /api/v1/spreadsheets
GET    /api/v1/spreadsheets/{spreadsheet_name}

# Admin
GET    /api/v1/admin/tasks/status (admin only)
```

---

**Version:** 2026.3.0  
**Last Updated:** 2026-02-27  
**Status:** 🟢 Production Ready
