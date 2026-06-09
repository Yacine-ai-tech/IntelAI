/**
 * DataHub Data Ingestion Control Panel
 *
 * Features:
 * - Auto-ingest data with percentage control
 * - Filter by domains and companies
 * - Delete ingested data
 * - Manual data upload
 * - Real-time ingestion progress
 * - Ingestion history tracking
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styles/data-ingestion.css';

// Vite doesn't expose `process.env` in the browser. Use import.meta.env (Vite)
// but fall back to process when available (for legacy CRA setups).
const API_BASE_URL = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL)
  ? process.env.REACT_APP_API_URL
  : (import.meta.env.VITE_REACT_APP_API_URL || 'http://localhost:8000/api/v1');

// ════════════════════════════════════════════════════════════════════════════
// DATA STRUCTURES
// ════════════════════════════════════════════════════════════════════════════

const DOMAINS = ['Finance', 'Growth', 'Operations', 'People', 'ESG'];
const DEFAULT_COMPANIES = [
  'CloudSync Pro',
  'DataFlow Analytics',
  'HealthCare Analytics',
  'SecureShield Corp',
  'SolarTech Innovations',
  'NeuralNet Labs',
  'EduPlatform Pro',
  'LendingTree Digital',
  'ServerLess Tech',
  'CarePath Digital',
];

// ════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ════════════════════════════════════════════════════════════════════════════

export default function DataIngestionPanel() {
  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [ingestionStatus, setIngestionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Ingestion parameters
  const [ingestionPercentage, setIngestionPercentage] = useState(100);
  const [selectedDomains, setSelectedDomains] = useState(new Set(DOMAINS));
  const [selectedCompanies, setSelectedCompanies] = useState(new Set(DEFAULT_COMPANIES));
  const [ingestionHistory, setIngestionHistory] = useState([]);

  // Manual upload
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadType, setUploadType] = useState('csv');
  const fileInputRef = useRef(null);

  // ════════════════════════════════════════════════════════════════════════════
  // API CALLS
  // ════════════════════════════════════════════════════════════════════════════

  const getAuthToken = () => localStorage.getItem('auth_token');

  const fetchDatasetInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/data-ingestion/dataset-info`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setDatasetInfo(response.data);
    } catch (err) {
      console.error('Failed to fetch dataset info:', err);
      setError('Failed to load dataset information');
    }
  };

  const fetchIngestionStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/data-ingestion/status`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setIngestionStatus(response.data);
    } catch (err) {
      console.error('Failed to fetch ingestion status:', err);
    }
  };

  const ingestAllData = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const config = {
        percentage: ingestionPercentage,
        domains: Array.from(selectedDomains),
        companies: Array.from(selectedCompanies),
      };

      const response = await axios.post(`${API_BASE_URL}/data-ingestion/ingest-all`, config, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setSuccess(`Successfully ingested ${response.data.ingested_count || 0} records`);
      await fetchDatasetInfo();
      await fetchIngestionStatus();

      // Add to history
      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'bulk_ingest',
        config,
        result: response.data,
      }, ...prev.slice(0, 9)]);

    } catch (err) {
      console.error('Ingestion failed:', err);
      setError(err.response?.data?.detail || 'Ingestion failed');
    } finally {
      setLoading(false);
    }
  };

  const ingestByDomains = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const domainPercentages = {};
      Array.from(selectedDomains).forEach(domain => {
        domainPercentages[domain] = ingestionPercentage;
      });

      const response = await axios.post(`${API_BASE_URL}/data-ingestion/ingest-by-domains`, {
        domain_percentages: domainPercentages,
        companies: Array.from(selectedCompanies),
      }, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setSuccess(`Successfully ingested data by domains`);
      await fetchDatasetInfo();

      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'domain_ingest',
        config: { domain_percentages: domainPercentages },
        result: response.data,
      }, ...prev.slice(0, 9)]);

    } catch (err) {
      console.error('Domain ingestion failed:', err);
      setError(err.response?.data?.detail || 'Domain ingestion failed');
    } finally {
      setLoading(false);
    }
  };

  const ingestByCompanies = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const companyPercentages = {};
      Array.from(selectedCompanies).forEach(company => {
        companyPercentages[company] = ingestionPercentage;
      });

      const response = await axios.post(`${API_BASE_URL}/data-ingestion/ingest-by-companies`, {
        company_percentages: companyPercentages,
        domains: Array.from(selectedDomains),
      }, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setSuccess(`Successfully ingested data by companies`);
      await fetchDatasetInfo();

      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'company_ingest',
        config: { company_percentages: companyPercentages },
        result: response.data,
      }, ...prev.slice(0, 9)]);

    } catch (err) {
      console.error('Company ingestion failed:', err);
      setError(err.response?.data?.detail || 'Company ingestion failed');
    } finally {
      setLoading(false);
    }
  };

  const deleteAllData = async () => {
    if (!confirm('Are you sure you want to delete ALL ingested data? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await axios.delete(`${API_BASE_URL}/data-ingestion/delete-all`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setSuccess('All ingested data deleted successfully');
      await fetchDatasetInfo();
      await fetchIngestionStatus();

      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'delete_all',
        result: { message: 'All data deleted' },
      }, ...prev.slice(0, 9)]);

    } catch (err) {
      console.error('Delete failed:', err);
      setError(err.response?.data?.detail || 'Delete failed');
    } finally {
      setLoading(false);
    }
  };

  const deleteDomainData = async (domain) => {
    if (!confirm(`Are you sure you want to delete all data for domain: ${domain}?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await axios.delete(`${API_BASE_URL}/data-ingestion/delete-domain/${domain}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setSuccess(`Data for domain ${domain} deleted successfully`);
      await fetchDatasetInfo();

      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'delete_domain',
        config: { domain },
        result: { message: `Domain ${domain} data deleted` },
      }, ...prev.slice(0, 9)]);

    } catch (err) {
      console.error('Domain delete failed:', err);
      setError(err.response?.data?.detail || 'Domain delete failed');
    } finally {
      setLoading(false);
    }
  };

  const deleteCompanyData = async (company) => {
    if (!confirm(`Are you sure you want to delete all data for company: ${company}?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await axios.delete(`${API_BASE_URL}/data-ingestion/delete-company/${company}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setSuccess(`Data for company ${company} deleted successfully`);
      await fetchDatasetInfo();

      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'delete_company',
        config: { company },
        result: { message: `Company ${company} data deleted` },
      }, ...prev.slice(0, 9)]);

    } catch (err) {
      console.error('Company delete failed:', err);
      setError(err.response?.data?.detail || 'Company delete failed');
    } finally {
      setLoading(false);
    }
  };

  const handleManualUpload = async () => {
    if (!uploadFile) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('type', uploadType);

      const response = await axios.post(`${API_BASE_URL}/data-ingestion/upload-manual`, formData, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          'Content-Type': 'multipart/form-data',
        }
      });

      setSuccess(`File uploaded successfully: ${response.data.message}`);
      await fetchDatasetInfo();

      setIngestionHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'manual_upload',
        config: { filename: uploadFile.name, type: uploadType },
        result: response.data,
      }, ...prev.slice(0, 9)]);

      // Reset form
      setUploadFile(null);
      setUploadType('csv');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  // ════════════════════════════════════════════════════════════════════════════
  // EFFECTS
  // ════════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    fetchDatasetInfo();
    fetchIngestionStatus();
  }, []);

  // ════════════════════════════════════════════════════════════════════════════
  // RENDER HELPERS
  // ════════════════════════════════════════════════════════════════════════════

  const renderOverviewTab = () => (
    <div className="ingestion-overview">
      <h3>Dataset Overview</h3>
      {datasetInfo ? (
        <div className="dataset-stats">
          <div className="stat-card">
            <h4>Total Records</h4>
            <p className="stat-value">{datasetInfo.total_records?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="stat-card">
            <h4>Companies</h4>
            <p className="stat-value">{datasetInfo.companies?.length || 0}</p>
          </div>
          <div className="stat-card">
            <h4>Domains</h4>
            <p className="stat-value">{datasetInfo.domains?.length || 0}</p>
          </div>
          <div className="stat-card">
            <h4>Last Updated</h4>
            <p className="stat-value">
              {datasetInfo.last_updated ? new Date(datasetInfo.last_updated).toLocaleDateString() : 'Never'}
            </p>
          </div>
        </div>
      ) : (
        <p>Loading dataset information...</p>
      )}

      <h3>Ingestion Status</h3>
      {ingestionStatus ? (
        <div className="status-info">
          <p><strong>Status:</strong> {ingestionStatus.status || 'Unknown'}</p>
          <p><strong>Last Activity:</strong> {ingestionStatus.last_activity || 'None'}</p>
          <p><strong>Progress:</strong> {ingestionStatus.progress || 'N/A'}</p>
        </div>
      ) : (
        <p>Loading ingestion status...</p>
      )}
    </div>
  );

  const renderIngestTab = () => (
    <div className="ingestion-controls">
      <h3>Data Ingestion Controls</h3>

      <div className="control-group">
        <label>Ingestion Percentage: {ingestionPercentage}%</label>
        <input
          type="range"
          min="1"
          max="100"
          value={ingestionPercentage}
          onChange={(e) => setIngestionPercentage(parseInt(e.target.value))}
          className="percentage-slider"
        />
      </div>

      <div className="control-group">
        <label>Domains to Include:</label>
        <div className="checkbox-group">
          {DOMAINS.map(domain => (
            <label key={domain} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedDomains.has(domain)}
                onChange={(e) => {
                  const newSelected = new Set(selectedDomains);
                  if (e.target.checked) {
                    newSelected.add(domain);
                  } else {
                    newSelected.delete(domain);
                  }
                  setSelectedDomains(newSelected);
                }}
              />
              {domain}
            </label>
          ))}
        </div>
      </div>

      <div className="control-group">
        <label>Companies to Include:</label>
        <div className="checkbox-group">
          {DEFAULT_COMPANIES.map(company => (
            <label key={company} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedCompanies.has(company)}
                onChange={(e) => {
                  const newSelected = new Set(selectedCompanies);
                  if (e.target.checked) {
                    newSelected.add(company);
                  } else {
                    newSelected.delete(company);
                  }
                  setSelectedCompanies(newSelected);
                }}
              />
              {company}
            </label>
          ))}
        </div>
      </div>

      <div className="action-buttons">
        <button
          onClick={ingestAllData}
          disabled={loading || selectedDomains.size === 0 || selectedCompanies.size === 0}
          className="btn-primary"
        >
          {loading ? 'Ingesting...' : 'Ingest All Data'}
        </button>

        <button
          onClick={ingestByDomains}
          disabled={loading || selectedDomains.size === 0}
          className="btn-secondary"
        >
          {loading ? 'Ingesting...' : 'Ingest by Domains'}
        </button>

        <button
          onClick={ingestByCompanies}
          disabled={loading || selectedCompanies.size === 0}
          className="btn-secondary"
        >
          {loading ? 'Ingesting...' : 'Ingest by Companies'}
        </button>
      </div>
    </div>
  );

  const renderManageTab = () => (
    <div className="data-management">
      <h3>Data Management</h3>

      <div className="danger-zone">
        <h4>⚠️ Danger Zone</h4>
        <p>These actions will permanently delete data. Use with caution.</p>

        <div className="delete-actions">
          <button
            onClick={deleteAllData}
            disabled={loading}
            className="btn-danger"
          >
            {loading ? 'Deleting...' : 'Delete ALL Data'}
          </button>
        </div>

        {datasetInfo?.domains && (
          <div className="domain-delete">
            <h4>Delete by Domain:</h4>
            <div className="domain-buttons">
              {datasetInfo.domains.map(domain => (
                <button
                  key={domain}
                  onClick={() => deleteDomainData(domain)}
                  disabled={loading}
                  className="btn-warning"
                >
                  Delete {domain}
                </button>
              ))}
            </div>
          </div>
        )}

        {datasetInfo?.companies && (
          <div className="company-delete">
            <h4>Delete by Company:</h4>
            <div className="company-buttons">
              {datasetInfo.companies.slice(0, 10).map(company => (
                <button
                  key={company}
                  onClick={() => deleteCompanyData(company)}
                  disabled={loading}
                  className="btn-warning"
                >
                  Delete {company}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderHistoryTab = () => (
    <div className="ingestion-history">
      <h3>Ingestion History</h3>

      {ingestionHistory.length === 0 ? (
        <p>No ingestion history available.</p>
      ) : (
        <div className="history-list">
          {ingestionHistory.map(entry => (
            <div key={entry.id} className="history-entry">
              <div className="history-header">
                <span className="history-type">{entry.type.replace('_', ' ').toUpperCase()}</span>
                <span className="history-time">
                  {new Date(entry.timestamp).toLocaleString()}
                </span>
              </div>
              <div className="history-details">
                {entry.config && (
                  <pre className="history-config">
                    {JSON.stringify(entry.config, null, 2)}
                  </pre>
                )}
                {entry.result && (
                  <pre className="history-result">
                    {JSON.stringify(entry.result, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderManualUploadTab = () => (
    <div className="manual-upload">
      <h3>Manual Data Upload</h3>

      <div className="upload-form">
        <div className="control-group">
          <label>File Type:</label>
          <select
            value={uploadType}
            onChange={(e) => setUploadType(e.target.value)}
            className="upload-select"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <div className="control-group">
          <label>Select File:</label>
          <input
            type="file"
            ref={fileInputRef}
            accept={uploadType === 'csv' ? '.csv' : '.json'}
            onChange={(e) => setUploadFile(e.target.files[0])}
            className="file-input"
          />
        </div>

        {uploadFile && (
          <div className="file-info">
            <p><strong>Selected:</strong> {uploadFile.name}</p>
            <p><strong>Size:</strong> {(uploadFile.size / 1024).toFixed(1)} KB</p>
          </div>
        )}

        <button
          onClick={handleManualUpload}
          disabled={loading || !uploadFile}
          className="btn-primary"
        >
          {loading ? 'Uploading...' : 'Upload File'}
        </button>
      </div>
    </div>
  );

  // ════════════════════════════════════════════════════════════════════════════
  // MAIN RENDER
  // ════════════════════════════════════════════════════════════════════════════

  return (
    <div className="data-ingestion-panel">
      <div className="panel-header">
        <h2>Data Ingestion Control Panel</h2>
        <p>Manage automatic and manual data ingestion for your IntelAI platform</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <strong>Success:</strong> {success}
        </div>
      )}

      <div className="ingestion-tabs">
        <div className="tab-buttons">
          <button
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={activeTab === 'ingest' ? 'active' : ''}
            onClick={() => setActiveTab('ingest')}
          >
            Ingest
          </button>
          <button
            className={activeTab === 'manage' ? 'active' : ''}
            onClick={() => setActiveTab('manage')}
          >
            Manage
          </button>
          <button
            className={activeTab === 'history' ? 'active' : ''}
            onClick={() => setActiveTab('history')}
          >
            History
          </button>
          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Manual Upload
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'ingest' && renderIngestTab()}
          {activeTab === 'manage' && renderManageTab()}
          {activeTab === 'history' && renderHistoryTab()}
          {activeTab === 'upload' && renderManualUploadTab()}
        </div>
      </div>
    </div>
  );
}