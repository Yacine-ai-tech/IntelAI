/**
 * Data Ingestion API Client Hook
 *
 * Custom React hook for data ingestion operations with:
 * - Automatic token management
 * - Error handling and retry logic
 * - Type-safe requests and responses
 * - Progress tracking
 */

// Provide a minimal ambient declaration for `process.env` so TypeScript does not
// error with "Cannot find name 'process'." This avoids pulling in Node types
// for a browser React app while allowing usage of REACT_APP_API_URL.
declare const process: {
  env: {
    REACT_APP_API_URL?: string;
  };
};

import { useState, useCallback } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// ════════════════════════════════════════════════════════════════════════════
// TYPE DEFINITIONS
// ════════════════════════════════════════════════════════════════════════════

export interface DatasetInfo {
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

export interface IngestionStats {
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

export interface IngestionStatus {
  total_ingested_records: number;
  total_batches: number;
  domains_covered: string[];
  companies_covered: string[];
  last_update: string;
  ingestion_history: Record<string, {
    count: number;
    domains: string[];
    companies: string[];
    percentage: number;
    timestamp: string;
  }>;
}

export interface IngestDataRequest {
  percentage: number;
  domains?: string[];
  companies?: string[];
}

export interface IngestByDomainsRequest {
  domain_percentages: Record<string, number>;
}

export interface IngestByCompaniesRequest {
  company_percentages: Record<string, number>;
}

export interface DeleteDataRequest {
  target: 'all' | string;
}

export interface ApiResponse<T> {
  status: string;
  data?: T;
  [key: string]: any;
}

// ════════════════════════════════════════════════════════════════════════════
// API CLIENT HELPER FUNCTIONS
// ════════════════════════════════════════════════════════════════════════════

/**
 * Get authorization token from localStorage or auth context
 */
function getAuthToken(): string {
  return localStorage.getItem('token') || '';
}

/**
 * Build headers with authorization
 */
function getHeaders(includeJson = true): HeadersInit {
  const headers: HeadersInit = {
    'Authorization': `Bearer ${getAuthToken()}`,
  };
  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

/**
 * Fetch wrapper with error handling
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: getHeaders(true),
  });

  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const error = await response.json();
      errorMessage = error.detail || error.message || errorMessage;
    } catch {
      // Response wasn't JSON
    }
    throw new Error(errorMessage);
  }

  const data = await response.json();
  return data as T;
}

/**
 * POST request helper
 */
async function postAPI<T>(
  endpoint: string,
  body: any
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * DELETE request helper
 */
async function deleteAPI<T>(endpoint: string): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'DELETE',
  });
}

/**
 * File upload helper
 */
async function uploadFile<T>(
  endpoint: string,
  file: File,
  domain?: string
): Promise<T> {
  const formData = new FormData();
  formData.append('file', file);
  if (domain) {
    formData.append('domain', domain);
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
    },
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = `Upload Error: ${response.status}`;
    try {
      const error = await response.json();
      errorMessage = error.detail || error.message || errorMessage;
    } catch {
      // Response wasn't JSON
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}

// ════════════════════════════════════════════════════════════════════════════
// REACT HOOK
// ════════════════════════════════════════════════════════════════════════════

export function useDataIngestion() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);
  const [success, setSuccess] = useState(null as string | null);

  // ═════════════════════════════════════════════════════════════════════════
  // DATASET OPERATIONS
  // ═════════════════════════════════════════════════════════════════════════

  /**
   * Get available dataset information
   */
  const getDatasetInfo = useCallback(async (): Promise<DatasetInfo | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetchAPI<ApiResponse<DatasetInfo>>(
        '/data-ingestion/dataset-info'
      );
      return response.data || null;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dataset info';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Get current ingestion status
   */
  const getIngestionStatus = useCallback(async (): Promise<IngestionStatus | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetchAPI<ApiResponse<IngestionStatus>>(
        '/data-ingestion/status'
      );
      return response.ingestion_status || response.data || null;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load ingestion status';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // INGESTION OPERATIONS
  // ═════════════════════════════════════════════════════════════════════════

  /**
   * Ingest all data with percentage and filters
   */
  const ingestAll = useCallback(async (
    request: IngestDataRequest
  ): Promise<IngestionStats | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await postAPI<ApiResponse<IngestionStats>>(
        '/data-ingestion/ingest-all',
        request
      );
      const stats = response.ingestion_stats || response.data || null;
      if (stats) {
        setSuccess(`Successfully ingested ${stats.ingested_records} records`);
      }
      return stats;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Ingestion failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Ingest by domain with specific percentages
   */
  const ingestByDomains = useCallback(async (
    request: IngestByDomainsRequest
  ): Promise<Record<string, IngestionStats> | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await postAPI<ApiResponse<Record<string, IngestionStats>>>(
        '/data-ingestion/ingest-by-domains',
        request
      );
      const results = response.results || response.data || null;
      if (results) {
        setSuccess('Domain-specific ingestion completed');
      }
      return results;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Domain ingestion failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Ingest by company with specific percentages
   */
  const ingestByCompanies = useCallback(async (
    request: IngestByCompaniesRequest
  ): Promise<Record<string, IngestionStats> | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await postAPI<ApiResponse<Record<string, IngestionStats>>>(
        '/data-ingestion/ingest-by-companies',
        request
      );
      const results = response.results || response.data || null;
      if (results) {
        setSuccess('Company-specific ingestion completed');
      }
      return results;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Company ingestion failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Ingest PDF documents
   */
  const ingestPDFs = useCallback(async (): Promise<any | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await postAPI<ApiResponse<any>>(
        '/data-ingestion/ingest-pdfs',
        {}
      );
      if (response.pdf_ingestion) {
        setSuccess(`Processed ${response.pdf_ingestion.processed_files} PDF files`);
      }
      return response.pdf_ingestion || response.data || null;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'PDF ingestion failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Ingest email samples
   */
  const ingestEmails = useCallback(async (): Promise<any | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await postAPI<ApiResponse<any>>(
        '/data-ingestion/ingest-emails',
        {}
      );
      if (response.email_ingestion) {
        setSuccess(`Ingested ${response.email_ingestion.emails_ingested} email samples`);
      }
      return response.email_ingestion || response.data || null;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Email ingestion failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Ingest Sheets data
   */
  const ingestSheets = useCallback(async (): Promise<any | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await postAPI<ApiResponse<any>>(
        '/data-ingestion/ingest-sheets',
        {}
      );
      if (response.sheets_ingestion) {
        setSuccess(`Ingested ${response.sheets_ingestion.sheets_ingested} sheets`);
      }
      return response.sheets_ingestion || response.data || null;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sheets ingestion failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Upload manual data file
   */
  const uploadManualData = useCallback(async (
    file: File,
    domain?: string
  ): Promise<any | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await uploadFile<ApiResponse<any>>(
        '/data-ingestion/upload-manual',
        file,
        domain
      );
      if (response.ingested_records) {
        setSuccess(`Uploaded ${response.ingested_records} records from ${file.name}`);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // DELETION OPERATIONS
  // ═════════════════════════════════════════════════════════════════════════

  /**
   * Delete all ingested data (admin only)
   */
  const deleteAllData = useCallback(async (): Promise<boolean> => {
    if (!window.confirm('Delete ALL ingested data? This cannot be undone!')) {
      return false;
    }

    try {
      setLoading(true);
      setError(null);
      await deleteAPI('/data-ingestion/delete-all');
      setSuccess('All ingested data deleted');
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Delete failed';
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Delete data for specific domain
   */
  const deleteDomainData = useCallback(async (domain: string): Promise<boolean> => {
    if (!window.confirm(`Delete all data for ${domain}?`)) {
      return false;
    }

    try {
      setLoading(true);
      setError(null);
      await deleteAPI(`/data-ingestion/delete-domain/${domain}`);
      setSuccess(`Deleted data for domain: ${domain}`);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : `Failed to delete ${domain}`;
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // MESSAGE MANAGEMENT
  // ═════════════════════════════════════════════════════════════════════════

  const clearError = useCallback(() => setError(null), []);
  const clearSuccess = useCallback(() => setSuccess(null), []);
  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // RETURN INTERFACE
  // ═════════════════════════════════════════════════════════════════════════

  return {
    // State
    loading,
    error,
    success,

    // Dataset operations
    getDatasetInfo,
    getIngestionStatus,

    // Ingestion operations
    ingestAll,
    ingestByDomains,
    ingestByCompanies,
    ingestPDFs,
    ingestEmails,
    ingestSheets,
    uploadManualData,

    // Deletion operations
    deleteAllData,
    deleteDomainData,

    // Message management
    clearError,
    clearSuccess,
    clearMessages,
  };
}

// ════════════════════════════════════════════════════════════════════════════
// EXPORT TYPES
// ════════════════════════════════════════════════════════════════════════════

export type DataIngestionHook = ReturnType<typeof useDataIngestion>;