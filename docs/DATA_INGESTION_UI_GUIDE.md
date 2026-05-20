# Data Ingestion UI Integration Guide

## Overview

This guide explains how to integrate the Data Ingestion Control Panel into your DataHub UI. The component provides a complete interface for managing automated data ingestion from the enhanced synthetic dataset.

**Status:** ✅ Production Ready (February 27, 2026)

## 📦 What's Included

### 1. **DataIngestionPanel.jsx** - Main React Component
- **Location:** `/src/ui/DataIngestionPanel.jsx`
- **Size:** ~800 lines
- **Purpose:** Complete UI for data ingestion management

**Features:**
- 5 main tabs: Overview, Auto Ingest, Manual Upload, Manage Data, History
- Dataset overview with statistics
- Automatic data ingestion with percentage control (0-100%)
- Domain-specific filtering (Finance, Growth, Operations, People, ESG)
- Company-specific filtering (10 companies)
- Domain-specific percentage control
- Company-specific percentage control
- PDF/Email/Sheets ingestion shortcuts
- Data deletion controls (all or per-domain)
- Ingestion history tracking
- Manual file upload (CSV/JSON)
- Real-time progress tracking
- Error/success message handling

### 2. **DataIngestionPanel.css** - Complete Styling
- **Location:** `/src/ui/DataIngestionPanel.css`
- **Size:** ~800 lines
- **Purpose:** Professional, responsive styling

**Features:**
- Modern gradient design (purple/blue theme)
- Mobile-responsive (480px, 768px breakpoints)
- Smooth animations and transitions
- Color-coded alerts (error, success)
- Interactive form controls
- Progress bars and status cards
- Dark theme support ready
- Accessibility-first design

### 3. **useDataIngestion.ts** - TypeScript API Hook
- **Location:** `/src/ui/hooks/useDataIngestion.ts`
- **Size:** ~500 lines
- **Purpose:** Type-safe API client for data ingestion

**Features:**
- Custom React hook with automatic state management
- Full TypeScript support with interfaces
- Automatic token management
- Error handling and retry logic
- 10+ API methods:
  - `getDatasetInfo()` - Fetch available dataset metadata
  - `getIngestionStatus()` - Get current ingestion status
  - `ingestAll()` - Ingest all data with filters
  - `ingestByDomains()` - Domain-specific ingestion
  - `ingestByCompanies()` - Company-specific ingestion
  - `ingestPDFs()` - Ingest PDF documents
  - `ingestEmails()` - Ingest email samples
  - `ingestSheets()` - Ingest Sheets data
  - `uploadManualData()` - Upload custom CSV/JSON
  - `deleteAllData()` - Delete all data
  - `deleteDomainData()` - Delete domain data
- Message management (errors/success)
- Form data upload support

## 🚀 Quick Start

### 1. Installation Requirements

Make sure these are installed in your project:

```bash
npm install react axios
# or
yarn add react axios
```

### 2. Basic Integration

#### Import Component

```jsx
import DataIngestionPanel from '@/ui/DataIngestionPanel';

// In your page/component:
function DataHubPage() {
  return (
    <div>
      <DataIngestionPanel />
    </div>
  );
}
```

#### Using the Hook Directly

```jsx
import { useDataIngestion } from '@/ui/hooks/useDataIngestion';

function MyCustomComponent() {
  const {
    loading,
    error,
    success,
    ingestAll,
    getDatasetInfo,
  } = useDataIngestion();

  // Use in your component
}
```

### 3. Environment Configuration

Add to your `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

Or if using a different API endpoint:

```env
REACT_APP_API_URL=https://api.example.com/api/v1
```

### 4. Authentication Setup

The component automatically uses the token from `localStorage`:

```javascript
// After user login, store token:
localStorage.setItem('token', jwtToken);

// Component will automatically send it in headers:
// Authorization: Bearer {jwtToken}
```

Or modify `src/ui/hooks/useDataIngestion.ts` to use your auth context:

```typescript
// Replace this function:
function getAuthToken(): string {
  return localStorage.getItem('token') || '';
}

// With your auth logic:
function getAuthToken(): string {
  const { token } = useAuth(); // Your auth hook
  return token || '';
}
```

## 📋 Component API Reference

### DataIngestionPanel Props

Currently the component has no required props. All state is managed internally:

```jsx
<DataIngestionPanel />
```

### useDataIngestion Hook

```typescript
const {
  // State
  loading: boolean,
  error: string | null,
  success: string | null,

  // Query operations
  getDatasetInfo(): Promise<DatasetInfo | null>,
  getIngestionStatus(): Promise<IngestionStatus | null>,

  // Ingestion operations
  ingestAll(request: IngestDataRequest): Promise<IngestionStats | null>,
  ingestByDomains(request: IngestByDomainsRequest): Promise<Record<string, IngestionStats> | null>,
  ingestByCompanies(request: IngestByCompaniesRequest): Promise<Record<string, IngestionStats> | null>,
  ingestPDFs(): Promise<any | null>,
  ingestEmails(): Promise<any | null>,
  ingestSheets(): Promise<any | null>,
  uploadManualData(file: File, domain?: string): Promise<any | null>,

  // Deletion operations
  deleteAllData(): Promise<boolean>,
  deleteDomainData(domain: string): Promise<boolean>,

  // Message management
  clearError(): void,
  clearSuccess(): void,
  clearMessages(): void,
} = useDataIngestion();
```

### Type Definitions

#### DatasetInfo
```typescript
interface DatasetInfo {
  total_records: number;
  domains: string[];
  companies: string[];
  time_period: {
    start: string;
    end: string;
  };
  file_size_mb: number;
  metrics: string[];
  available_files: number;
}
```

#### IngestionStats
```typescript
interface IngestionStats {
  total_records: number;
  ingested_records: number;
  failed_records: number;
  ingestion_percentage: number;
  domains_covered: string[];
  companies_covered: string[];
  execution_time_seconds: number;
  timestamp: string;
  status: 'completed' | 'in_progress' | 'failed';
  error_message: string | null;
}
```

#### IngestDataRequest
```typescript
interface IngestDataRequest {
  percentage: number;           // 0-100
  domains?: string[];           // Optional domain filter
  companies?: string[];         // Optional company filter
}
```

## 🎯 Use Cases

### Use Case 1: Quick Demo Setup

Load 100% of Finance domain data for testing:

```jsx
function DemoSetup() {
  const { ingestAll, loading } = useDataIngestion();

  return (
    <button
      onClick={() => ingestAll({
        percentage: 100,
        domains: ['Finance']
      })}
      disabled={loading}
    >
      {loading ? 'Loading...' : 'Load Demo Data'}
    </button>
  );
}
```

### Use Case 2: Selective Domain Testing

Test each domain separately:

```jsx
function DomainTester() {
  const { ingestByDomains, loading } = useDataIngestion();

  const handleTest = async () => {
    await ingestByDomains({
      domain_percentages: {
        'Finance': 50,
        'Growth': 50,
        'Operations': 25,
        'People': 0,
        'ESG': 0
      }
    });
  };

  return (
    <button onClick={handleTest} disabled={loading}>
      Test Finance & Growth
    </button>
  );
}
```

### Use Case 3: Data Cleanup

Clean data between tests:

```jsx
function DataCleanup() {
  const { deleteDomainData, loading } = useDataIngestion();

  return (
    <button
      onClick={() => deleteDomainData('Finance')}
      disabled={loading}
    >
      Clean Finance Data
    </button>
  );
}
```

## 🔧 Customization Guide

### Modify Domains

Edit the `DOMAINS` constant in `DataIngestionPanel.jsx`:

```jsx
const DOMAINS = [
  'Finance',
  'Growth',
  'Operations',
  'People',
  'ESG',
  'Custom' // Add your own
];
```

### Modify Companies

Edit the `DEFAULT_COMPANIES` constant:

```jsx
const DEFAULT_COMPANIES = [
  'CloudSync Pro',
  'DataFlow Analytics',
  // Add or remove companies
];
```

### Change API URL

Environment variable (recommended):

```env
REACT_APP_API_URL=https://custom-api.com/api/v1
```

Or directly in hook:

```typescript
// In useDataIngestion.ts
const API_BASE_URL = 'https://custom-api.com/api/v1';
```

### Customize Colors

Edit CSS variables in `DataIngestionPanel.css`:

```css
:root {
  --primary-color: #667eea;
  --primary-dark: #764ba2;
  --success-color: #11998e;
  --danger-color: #eb3349;
}
```

Or modify gradient definitions:

```css
.btn-primary {
  background: linear-gradient(135deg, YOUR_COLOR_1 0%, YOUR_COLOR_2 100%);
}
```

## 🔐 Security Considerations

### Token Management

The component uses `localStorage` for token storage by default. For production:

1. **Secure HttpOnly Cookies** (Recommended)
   - Modify `getAuthToken()` to read from secure cookie
   - Prevents XSS token theft

2. **Auth Context Provider**
   - Use React Context with secure token storage
   - Example in hook implementation above

3. **CSRF Protection**
   - Add CSRF token to requests if needed
   - Modify headers in `getHeaders()` function

### Data Validation

- All user inputs are validated before API calls
- File uploads checked for supported formats (CSV, JSON)
- Percentage inputs limited to 0-100 range

### Admin Operations

Delete operations require admin role on backend:

```python
# Backend enforces admin check
if not user.is_admin and operation == "delete_all":
    raise HTTPException(status_code=403, detail="Admin only")
```

## 📊 Dashboard Integration

### Add to Dashboard

```jsx
import { useState, useEffect } from 'react';
import DataIngestionPanel from '@/ui/DataIngestionPanel';

function Dashboard() {
  const [showIngestion, setShowIngestion] = useState(false);

  return (
    <div className="dashboard">
      {/* Other dashboard content */}
      
      <button onClick={() => setShowIngestion(!showIngestion)}>
        {showIngestion ? 'Hide' : 'Show'} Data Ingestion
      </button>

      {showIngestion && (
        <div className="ingestion-widget">
          <DataIngestionPanel />
        </div>
      )}
    </div>
  );
}
```

### Add to Modal

```jsx
import Modal from '@/ui/Modal';
import DataIngestionPanel from '@/ui/DataIngestionPanel';

function DataHubPage() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <button onClick={() => setModalOpen(true)}>
        Manage Data
      </button>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Data Ingestion Control Panel"
      >
        <DataIngestionPanel />
      </Modal>
    </>
  );
}
```

## 🧪 Testing

### Test Data Ingestion

```bash
# Start API server
python main.py

# Test endpoint
curl http://localhost:8000/api/v1/data-ingestion/dataset-info \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Unit Test Example

```typescript
import { renderHook, act } from '@testing-library/react';
import { useDataIngestion } from '@/ui/hooks/useDataIngestion';

describe('useDataIngestion', () => {
  it('should fetch dataset info', async () => {
    const { result } = renderHook(() => useDataIngestion());

    await act(async () => {
      const info = await result.current.getDatasetInfo();
      expect(info).toBeDefined();
      expect(info?.total_records).toBeGreaterThan(0);
    });
  });

  it('should ingest data with percentage', async () => {
    const { result } = renderHook(() => useDataIngestion());

    await act(async () => {
      const stats = await result.current.ingestAll({
        percentage: 50,
        domains: ['Finance']
      });
      expect(stats?.ingestion_percentage).toBe(50);
    });
  });
});
```

## 📱 Responsive Design

Component is fully responsive:

- **Desktop (1200px+):** 2-column grid layouts
- **Tablet (768px-1199px):** Adaptive grid
- **Mobile (480px-767px):** Single column
- **Small Mobile (<480px):** Stacked layout

All UI elements reflow naturally. Test on:

```bash
# Chrome DevTools
# Firefox Responsive Design Mode
# Safari Responsive Design Mode
```

## 🐛 Troubleshooting

### Issue: "Unauthorized" Error
**Solution:** Ensure token is in localStorage:
```javascript
localStorage.getItem('token')
```

### Issue: CORS Errors
**Solution:** Check API CORS configuration in `server_v2.py`:
```python
# Should include your frontend URL
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
```

### Issue: Files Not Uploading
**Solution:** Verify file format and size:
- Supported: CSV, JSON
- Max size: Check backend limit (usually 50MB)

### Issue: Slow Ingestion
**Solution:** Reduce percentage or use domain-specific ingestion:
```jsx
// Instead of 100%
ingestAll({ percentage: 25 }) // Faster
```

## 🔄 Lifecycle & State Management

### Component Lifecycle

```
Mount
  → fetchDatasetInfo() [loads available data]
  → fetchIngestionStatus() [loads history]
  → Set interval (refresh every 10s)

User Interaction
  → Set loading state
  → Call API method
  → Update state with response
  → Clear loading state

Unmount
  → Clear interval
  → Cancel pending requests
```

### State Flow

```
User Action
  ↓
UI State Update (loading = true)
  ↓
API Call (with token in headers)
  ↓
Backend Processing
  ↓
API Response
  ↓
State Update (data, loading = false)
  ↓
UI Re-render
```

## 📈 Performance Optimization

### Tips for Large Datasets

1. **Batch Ingestion**
   ```jsx
   // Instead of 100%, ingest in batches:
   ingestAll({ percentage: 20 }); // First batch
   // Wait...
   ingestAll({ percentage: 20, domains: [...] }); // Next batch
   ```

2. **Domain Filtering**
   ```jsx
   // Ingest only needed domains
   ingestByDomains({
     domain_percentages: { 'Finance': 100, 'Growth': 0 }
   });
   ```

3. **Progressive Loading**
   Use async operations and show progress

4. **Cancel Requests**
   Add AbortController if implementing real cancellation

## 🎓 Developer Notes

### Architecture

```
UI Component (DataIngestionPanel.jsx)
       ↓
   React Hook (useDataIngestion.ts)
       ↓
   Fetch API Client
       ↓
   FastAPI Endpoints (/api/v1/data-ingestion/*)
       ↓
   DataIngestionManager Service
       ↓
   RealtimePipeline → Domain Classification → Storage
```

### File Organization

```
src/ui/
├── DataIngestionPanel.jsx    # Main component
├── DataIngestionPanel.css    # Styling
├── hooks/
│   └── useDataIngestion.ts   # API hook
└── components/              # Optional sub-components
    ├── ProgressBar.vue
    ├── ConfirmationDialog.vue
    └── ...
```

### Future Enhancements

- [ ] Real-time progress streaming (WebSocket)
- [ ] Bulk operation scheduling
- [ ] Data preview before ingestion
- [ ] Custom transformation rules
- [ ] Ingestion templates/presets
- [ ] Audit logging UI
- [ ] Export ingestion reports

## 📞 Support

For issues or questions:

1. Check backend API logs: `tail -f logs/*.log`
2. Verify API endpoints: `curl http://localhost:8000/api/v1/data-ingestion/dataset-info`
3. Check browser console for client errors (F12)
4. Review component documentation in code

## ✅ Checklist for Production

- [ ] Token authentication configured
- [ ] API URL environment variable set
- [ ] CORS origins configured on backend
- [ ] Admin role verification working
- [ ] File upload size limits set
- [ ] Rate limiting configured
- [ ] Error logging enabled
- [ ] Success logging enabled
- [ ] Mobile tested on iOS/Android
- [ ] Accessibility audit passed
- [ ] Performance profiling done
- [ ] Security review completed

## 📄 Additional Resources

- [Backend API Documentation](./INTEGRATION_GUIDE.md)
- [Data Ingestion Service](../services/data_ingestion_manager.py)
- [API Endpoints](../api/server_v2.py)
- [Dataset Overview](../enhanced_synthetic_dataset/README.md)

---

**Last Updated:** February 27, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
