import { useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api'
import {
  Workflow, Box, Plus, Play, Pause, Trash2, Settings,
  Clock, CheckCircle, AlertCircle, Zap, GitBranch,
  ArrowRight, Circle, Square, Diamond, Database, FileText,
  Mail, Globe, Server
} from 'lucide-react'

// Node type icons mapping
const NODE_ICONS = {
  'webhook': Globe,
  'trigger': Zap,
  'action': Play,
  'condition': Diamond,
  'database': Database,
  'document': FileText,
  'email': Mail,
  'api': Server,
  'default': Box,
}

// Node color mapping
const NODE_COLORS = {
  'webhook': '#22c55e',
  'trigger': '#eab308',
  'action': '#3b82f6',
  'condition': '#f59e0b',
  'database': '#8b5cf6',
  'document': '#ec4899',
  'email': '#06b6d4',
  'api': '#6366f1',
  'default': '#64748b',
}

function WorkflowNode({ node, onSelect, selected }) {
  const NodeIcon = NODE_ICONS[node.type] || NODE_ICONS.default
  const nodeColor = NODE_COLORS[node.type] || NODE_COLORS.default

  return (
    <div
      onClick={() => onSelect?.(node)}
      style={{
        position: 'absolute',
        left: `${node.x}px`,
        top: `${node.y}px`,
        width: 160,
        padding: 12,
        background: selected ? 'var(--primary)' : 'white',
        border: `2px solid ${nodeColor}`,
        borderRadius: 8,
        cursor: 'pointer',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        transition: 'all 0.2s',
        transform: selected ? 'scale(1.05)' : 'scale(1)',
      }}
      onMouseEnter={(e) => {
        if (!selected) {
          e.currentTarget.style.transform = 'scale(1.05)'
          e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)'
        }
      }}
      onMouseLeave={(e) => {
        if (!selected) {
          e.currentTarget.style.transform = 'scale(1)'
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'
        }
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ 
          width: 32, 
          height: 32, 
          background: nodeColor, 
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <NodeIcon size={16} style={{ color: 'white' }} />
        </div>
        <div style={{ 
          flex: 1, 
          fontSize: '0.875rem', 
          fontWeight: 600,
          color: selected ? 'white' : 'inherit',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis'
        }}>
          {node.name}
        </div>
      </div>
      <div style={{ 
        fontSize: '0.75rem', 
        color: selected ? 'rgba(255,255,255,0.8)' : 'var(--text-muted)' 
      }}>
        {node.type}
      </div>
      {node.status && (
        <div style={{ 
          marginTop: 8, 
          fontSize: '0.75rem',
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          color: selected ? 'white' : 'inherit'
        }}>
          {node.status === 'active' ? (
            <CheckCircle size={12} style={{ color: selected ? 'white' : 'var(--success)' }} />
          ) : (
            <AlertCircle size={12} style={{ color: selected ? 'white' : 'var(--warning)' }} />
          )}
          {node.status}
        </div>
      )}
    </div>
  )
}

function WorkflowConnection({ from, to }) {
  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    >
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill="#64748b"
          />
        </marker>
      </defs>
      <line
        x1={from.x + 80}
        y1={from.y + 40}
        x2={to.x + 80}
        y2={to.y + 40}
        stroke="#64748b"
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
      />
    </svg>
  )
}

function WorkflowCard({ workflow, onSelect, onExecute, onDelete, isActive }) {
  return (
    <div 
      className="card"
      style={{ 
        cursor: 'pointer',
        transition: 'all 0.2s',
        border: isActive ? '2px solid var(--primary)' : 'none'
      }}
      onClick={() => onSelect?.(workflow)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ 
            width: 48, 
            height: 48, 
            background: 'var(--primary-bg)', 
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Workflow size={24} style={{ color: 'var(--primary)' }} />
          </div>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>
              {workflow.name}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              {workflow.description || 'No description'}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn btn-primary"
            onClick={(e) => {
              e.stopPropagation()
              onExecute?.(workflow)
            }}
            style={{ padding: '8px 12px' }}
          >
            <Play size={14} />
          </button>
          <button
            className="btn btn-danger"
            onClick={(e) => {
              e.stopPropagation()
              onDelete?.(workflow.id)
            }}
            style={{ padding: '8px 12px' }}
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 16, fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <GitBranch size={14} />
          {workflow.nodes?.length || 0} nodes
        </span>
        {workflow.last_run && (
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Clock size={14} />
            {new Date(workflow.last_run).toLocaleString()}
          </span>
        )}
        {workflow.status && (
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {workflow.status === 'active' ? (
              <CheckCircle size={14} style={{ color: 'var(--success)' }} />
            ) : (
              <AlertCircle size={14} style={{ color: 'var(--warning)' }} />
            )}
            {workflow.status}
          </span>
        )}
      </div>
    </div>
  )
}

export default function N8NWorkflowPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)

  // Get n8n nodes
  const { data: nodes = [], isLoading: nodesLoading } = useQuery({
    queryKey: ['n8n-nodes'],
    queryFn: () => api.getN8NNodes?.().then(res => res.data?.nodes || []) || [],
    staleTime: 2 * 60 * 1000, // 2 minutes
  })

  // Mock workflows data (in real implementation, this would come from API)
  const mockWorkflows = [
    {
      id: '1',
      name: 'Data Ingestion Pipeline',
      description: 'Automated data ingestion from multiple sources',
      status: 'active',
      last_run: new Date(Date.now() - 3600000).toISOString(),
      nodes: [
        { id: '1', type: 'webhook', name: 'Webhook Trigger', x: 50, y: 50, status: 'active' },
        { id: '2', type: 'database', name: 'Store Data', x: 250, y: 50, status: 'active' },
        { id: '3', type: 'action', name: 'Process Data', x: 450, y: 50, status: 'active' },
      ],
      connections: [['1', '2'], ['2', '3']]
    },
    {
      id: '2',
      name: 'Daily Report Generator',
      description: 'Generate daily reports and send via email',
      status: 'active',
      last_run: new Date(Date.now() - 86400000).toISOString(),
      nodes: [
        { id: '1', type: 'trigger', name: 'Schedule Trigger', x: 50, y: 100, status: 'active' },
        { id: '2', type: 'database', name: 'Query Database', x: 250, y: 100, status: 'active' },
        { id: '3', type: 'document', name: 'Generate Report', x: 450, y: 100, status: 'active' },
        { id: '4', type: 'email', name: 'Send Email', x: 650, y: 100, status: 'active' },
      ],
      connections: [['1', '2'], ['2', '3'], ['3', '4']]
    },
    {
      id: '3',
      name: 'Customer Onboarding',
      description: 'Automated customer onboarding workflow',
      status: 'paused',
      last_run: new Date(Date.now() - 172800000).toISOString(),
      nodes: [
        { id: '1', type: 'webhook', name: 'New Customer', x: 50, y: 150, status: 'inactive' },
        { id: '2', type: 'action', name: 'Create Account', x: 250, y: 150, status: 'inactive' },
        { id: '3', type: 'email', name: 'Welcome Email', x: 450, y: 150, status: 'inactive' },
      ],
      connections: [['1', '2'], ['2', '3']]
    }
  ]

  const handleExecuteWorkflow = (workflow) => {
    console.log('Executing workflow:', workflow.id)
    // In real implementation, this would call the execute API
    alert(`Executing workflow: ${workflow.name}`)
  }

  const handleDeleteWorkflow = (workflowId) => {
    console.log('Deleting workflow:', workflowId)
    // In real implementation, this would call the delete API
    if (confirm('Are you sure you want to delete this workflow?')) {
      alert(`Workflow ${workflowId} would be deleted`)
    }
  }

  return (
    <div>
      <h1 className="page-title">
        <Workflow size={24} />
        {t('workflowAutomation')}
      </h1>
      <p className="page-subtitle">
        Design, manage, and execute automated workflows with n8n integration
      </p>

      {/* Workflow List */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Active Workflows</h2>
          <button className="btn btn-primary">
            <Plus size={16} />
            New Workflow
          </button>
        </div>

        <div style={{ display: 'grid', gap: 16 }}>
          {mockWorkflows.map(workflow => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onSelect={setSelectedWorkflow}
              onExecute={handleExecuteWorkflow}
              onDelete={handleDeleteWorkflow}
              isActive={selectedWorkflow?.id === workflow.id}
            />
          ))}
        </div>
      </div>

      {/* Workflow Visualization */}
      {selectedWorkflow && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0 }}>
              Workflow: {selectedWorkflow.name}
            </h2>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary">
                <Settings size={16} />
                Edit
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => handleExecuteWorkflow(selectedWorkflow)}
              >
                <Play size={16} />
                Execute
              </button>
            </div>
          </div>

          {/* Workflow Canvas */}
          <div style={{ 
            position: 'relative',
            height: 400,
            background: 'var(--card-bg)',
            borderRadius: 8,
            border: '2px dashed var(--border)',
            overflow: 'hidden'
          }}>
            {/* Connections */}
            {selectedWorkflow.connections?.map(([fromId, toId], index) => {
              const fromNode = selectedWorkflow.nodes.find(n => n.id === fromId)
              const toNode = selectedWorkflow.nodes.find(n => n.id === toId)
              if (!fromNode || !toNode) return null
              return (
                <WorkflowConnection key={index} from={fromNode} to={toNode} />
              )
            })}

            {/* Nodes */}
            {selectedWorkflow.nodes?.map(node => (
              <WorkflowNode
                key={node.id}
                node={node}
                selected={selectedNode?.id === node.id}
                onSelect={setSelectedNode}
              />
            ))}
          </div>

          {/* Node Details */}
          {selectedNode && (
            <div style={{ 
              marginTop: 16, 
              padding: 16, 
              background: 'var(--card-bg)', 
              borderRadius: 8 
            }}>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>
                {selectedNode.name}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                Type: {selectedNode.type}
              </div>
              {selectedNode.status && (
                <div style={{ fontSize: '0.875rem' }}>
                  Status: {selectedNode.status}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Available N8N Nodes */}
      {!nodesLoading && nodes.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Available N8N Nodes</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {nodes.map(node => (
              <div 
                key={node.name}
                style={{ 
                  padding: '8px 12px', 
                  background: 'var(--card-bg)', 
                  borderRadius: 4,
                  fontSize: '0.875rem',
                  border: '1px solid var(--border)'
                }}
              >
                {node.name}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}