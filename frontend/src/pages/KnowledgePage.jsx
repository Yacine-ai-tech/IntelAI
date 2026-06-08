import { useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api'
import {
  Search, Database, FileText, Clock, TrendingUp, AlertCircle,
  CheckCircle, Filter, Download, Share, BookOpen, Zap
} from 'lucide-react'

function SearchResult({ result, onPreview }) {
  return (
    <div 
      className="card"
      style={{ 
        marginBottom: 12, 
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s'
      }}
      onClick={() => onPreview?.(result)}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)'
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <div style={{ 
          width: 40, 
          height: 40, 
          background: 'var(--primary-bg)', 
          borderRadius: 8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <FileText size={20} style={{ color: 'var(--primary)' }} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>
            {result.title || result.name || 'Untitled Document'}
          </div>
          <div style={{ 
            fontSize: '0.875rem', 
            color: 'var(--text-muted)', 
            marginBottom: 8,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
            {result.content || result.summary || result.text || 'No content preview available'}
          </div>
          <div style={{ display: 'flex', gap: 16, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {result.score && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <TrendingUp size={12} />
                {(result.score * 100).toFixed(1)}% relevance
              </span>
            )}
            {result.source && (
              <span>Source: {result.source}</span>
            )}
            {result.category && (
              <span>Category: {result.category}</span>
            )}
            {result.created_at && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <Clock size={12} />
                {new Date(result.created_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function KnowledgeStats({ stats }) {
  const statItems = [
    { label: 'Total Documents', value: stats.total_documents || 0, icon: Database },
    { label: 'Indexed Items', value: stats.indexed_items || 0, icon: FileText },
    { label: 'Search Queries', value: stats.total_queries || 0, icon: Search },
    { label: 'Avg Response Time', value: `${stats.avg_response_time || 0}ms`, icon: Zap },
  ]

  return (
    <div className="kpi-grid" style={{ marginBottom: 24 }}>
      {statItems.map((item, index) => {
        const Icon = item.icon
        return (
          <div key={index} className="kpi-card">
            <div className="kpi-icon-wrap" style={{ background: 'var(--primary-bg)', color: 'var(--primary)' }}>
              <Icon size={20} />
            </div>
            <div className="kpi-label">{item.label}</div>
            <div className="kpi-value">{item.value.toLocaleString()}</div>
          </div>
        )
      })}
    </div>
  )
}

export default function KnowledgePage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [topK, setTopK] = useState(10)
  const [selectedResult, setSelectedResult] = useState(null)

  // Knowledge stats query
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['knowledge-stats'],
    queryFn: () => api.getKnowledgeStats?.().then(res => res.data) || {},
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: async (query) => {
      const params = new URLSearchParams({
        query: query,
        top_k: topK.toString(),
      })
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory)
      }
      const res = await api.knowledgeSearch(params.toString())
      return res.data
    },
    onSuccess: () => {
      // Invalidate stats after search
      queryClient.invalidateQueries(['knowledge-stats'])
    },
  })

  const handleSearch = (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    searchMutation.mutate(searchQuery)
  }

  const handleCategoryChange = (category) => {
    setSelectedCategory(category)
    if (searchMutation.data) {
      // Re-run search with new category
      searchMutation.mutate(searchQuery)
    }
  }

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'finance', label: 'Finance' },
    { value: 'hr', label: 'HR' },
    { value: 'operations', label: 'Operations' },
    { value: 'it', label: 'IT' },
    { value: 'logistics', label: 'Logistics' },
    { value: 'esg', label: 'ESG' },
    { value: 'growth', label: 'Growth' },
  ]

  return (
    <div>
      <h1 className="page-title">
        <BookOpen size={24} />
        {t('knowledgeBase')}
      </h1>
      <p className="page-subtitle">
        Search across all documents, reports, and data using hybrid retrieval with AI-powered ranking
      </p>

      {/* Knowledge Stats */}
      {!statsLoading && stats && <KnowledgeStats stats={stats} />}

      {/* Search Interface */}
      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={handleSearch}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: 12, 
                  top: '50%', 
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)' 
                }} 
              />
              <input
                type="text"
                className="form-input"
                placeholder="Search knowledge base..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ paddingLeft: 40 }}
                disabled={searchMutation.isPending}
              />
            </div>
            
            <button
              className="btn btn-primary"
              type="submit"
              disabled={!searchQuery.trim() || searchMutation.isPending}
            >
              <Search size={16} />
              {searchMutation.isPending ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Search Options */}
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Filter size={16} style={{ color: 'var(--text-muted)' }} />
              <select
                className="form-input"
                value={selectedCategory}
                onChange={(e) => handleCategoryChange(e.target.value)}
                style={{ width: 150 }}
              >
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Results:</span>
              <select
                className="form-input"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
                style={{ width: 100 }}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {searchMutation.isPending && (
        <div style={{ 
          textAlign: 'center', 
          padding: 40, 
          color: 'var(--text-muted)' 
        }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }} />
          <span>Searching knowledge base...</span>
        </div>
      )}

      {searchMutation.data && searchMutation.data.results && (
        <div>
          <div style={{ 
            marginBottom: 16, 
            fontSize: '0.875rem', 
            color: 'var(--text-muted)' 
          }}>
            Found {searchMutation.data.results.length} results for "{searchQuery}"
            {searchMutation.data.search_time && (
              <span style={{ marginLeft: 8 }}>
                ({searchMutation.data.search_time.toFixed(3)}s)
              </span>
            )}
          </div>

          {searchMutation.data.results.length > 0 ? (
            searchMutation.data.results.map((result, index) => (
              <SearchResult 
                key={index} 
                result={result} 
                onPreview={setSelectedResult}
              />
            ))
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: 40, 
              color: 'var(--text-muted)' 
            }}>
              <Search size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
              <p>No results found. Try different search terms or filters.</p>
            </div>
          )}
        </div>
      )}

      {/* Result Preview Modal */}
      {selectedResult && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          background: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div 
            className="card"
            style={{ 
              maxWidth: 800, 
              maxHeight: '80vh', 
              overflowY: 'auto',
              width: '90%'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0 }}>
                {selectedResult.title || selectedResult.name || 'Document Preview'}
              </h3>
              <button 
                className="btn btn-secondary"
                onClick={() => setSelectedResult(null)}
              >
                Close
              </button>
            </div>
            
            <div style={{ 
              padding: 16, 
              background: 'var(--card-bg)', 
              borderRadius: 8,
              whiteSpace: 'pre-wrap',
              lineHeight: 1.6
            }}>
              {selectedResult.content || selectedResult.summary || selectedResult.text || 'No content available'}
            </div>

            {selectedResult.metadata && (
              <div style={{ marginTop: 16, padding: 12, background: 'var(--card-bg)', borderRadius: 8 }}>
                <div style={{ fontWeight: 600, marginBottom: 8 }}>Metadata</div>
                {Object.entries(selectedResult.metadata).map(([key, value]) => (
                  <div key={key} style={{ fontSize: '0.875rem', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-muted)' }}>{key}:</span> {value}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Error */}
      {searchMutation.error && (
        <div style={{ 
          padding: 16, 
          background: 'var(--danger-bg)', 
          borderRadius: 8,
          color: 'var(--danger)',
          display: 'flex',
          alignItems: 'center',
          gap: 8
        }}>
          <AlertCircle size={16} />
          <span>
            Search failed: {searchMutation.error.message || 'Unknown error'}
          </span>
        </div>
      )}
    </div>
  )
}