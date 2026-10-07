import React, { useState } from 'react'
import {
  Award, TrendingUp, Share2, ShieldCheck, CheckCircle2,
  Terminal, ArrowRight, BookOpen, Layers, BarChart3, AlertCircle
} from 'lucide-react'
import { PageHeader, Panel, Grid, Stat } from '../components/ui'
import { Link } from 'react-router-dom'

const FORECAST_RESULTS = [
  { metric: 'System Uptime', meanApe: '0.33%', medianApe: '0.17%', n: 74, status: 'Optimal' },
  { metric: 'Headcount', meanApe: '1.74%', medianApe: '1.72%', n: 74, status: 'Optimal' },
  { metric: 'Customers', meanApe: '3.71%', medianApe: '3.30%', n: 74, status: 'Strong' },
  { metric: 'ARR', meanApe: '5.56%', medianApe: '5.04%', n: 74, status: 'Strong' },
  { metric: 'Revenue', meanApe: '6.61%', medianApe: '6.01%', n: 74, status: 'Strong' },
  { metric: 'Gross Margin', meanApe: '9.88%', medianApe: '8.78%', n: 74, status: 'Moderate' },
]

const GRAPH_COVERAGE = [
  { domain: 'Finance', rows: 1872, inferred: 1872, coverage: '100.0%' },
  { domain: 'Growth', rows: 1248, inferred: 1248, coverage: '100.0%' },
  { domain: 'People', rows: 1092, inferred: 1092, coverage: '100.0%' },
  { domain: 'IT', rows: 1092, inferred: 1092, coverage: '100.0%' },
  { domain: 'Operations', rows: 936, inferred: 936, coverage: '100.0%' },
  { domain: 'ESG', rows: 936, inferred: 936, coverage: '100.0%' },
  { domain: 'Logistics', rows: 702, inferred: 702, coverage: '100.0%' },
]

const MULTI_HOP_QUERIES = [
  { query: 'Compare headcount expansion against finance gross margin trajectory', departments: ['People', 'Finance'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Analyze logistics fill rate correlation with IT system uptime incidents', departments: ['Logistics', 'IT'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Evaluate carbon footprint reduction impact on operations unit costs', departments: ['ESG', 'Operations'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Examine customer acquisition cost versus ARR acceleration across cohorts', departments: ['Growth', 'Finance'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Assess warehouse dispatch backlog impact on growth customer retention', departments: ['Logistics', 'Growth'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Review employee training completion against operations safety incident counts', departments: ['People', 'Operations'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Audit IT security posture alignment with governance and ESG compliance scores', departments: ['IT', 'ESG'], result: 'Passed (2/2 depts retrieved)' },
  { query: 'Cross-reference facilities energy efficiency with operating expenditure variance', departments: ['ESG', 'Finance'], result: 'Passed (2/2 depts retrieved)' },
]

export default function BenchmarkPage() {
  const [activeTab, setActiveTab] = useState('forecasting')

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 60 }}>
      <PageHeader
        icon={Award}
        title="IntelAI — Verified Empirical Benchmarks"
        subtitle="Empirical backtests, knowledge-graph entity coverage, and persona boundary validation across 7,878 live records."
        actions={
          <div style={{ display: 'flex', gap: 10 }}>
            <Link to="/research" className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <BookOpen size={16} /> Research Design
            </Link>
          </div>
        }
      />

      {/* KPI Cards */}
      <Grid min={250} style={{ marginBottom: 28 }}>
        <Stat
          label="Forecasting Mean APE"
          value="4.64%"
          unit="error"
          hint="Across 444 3-month-ahead backtest forecasts"
          trend={-7.84}
          good="down"
          icon={TrendingUp}
          accent="var(--ok)"
        />
        <Stat
          label="Graph Entity Coverage"
          value="100.0%"
          unit="inferred"
          hint="7,878 / 7,878 KPI rows across 7 domains"
          icon={Share2}
          accent="var(--primary)"
        />
        <Stat
          label="Multi-Hop Query Resolution"
          value="8 / 8"
          unit="queries"
          hint="100% cross-department relational recall"
          icon={Layers}
          accent="var(--ok)"
        />
        <Stat
          label="RBAC Persona Isolation"
          value="100.0%"
          unit="enforced"
          hint="0 cross-role data leaks across 9 personas"
          icon={ShieldCheck}
          accent="var(--primary)"
        />
      </Grid>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: 10, borderBottom: '1px solid var(--border)', marginBottom: 24, paddingBottom: 8 }}>
        <button
          onClick={() => setActiveTab('forecasting')}
          className={`btn ${activeTab === 'forecasting' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '.9rem' }}
        >
          1. Forecasting Backtest
        </button>
        <button
          onClick={() => setActiveTab('graph')}
          className={`btn ${activeTab === 'graph' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '.9rem' }}
        >
          2. GraphRAG-Lite Coverage
        </button>
        <button
          onClick={() => setActiveTab('multihop')}
          className={`btn ${activeTab === 'multihop' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '.9rem' }}
        >
          3. Multi-Hop Relational Retrieval
        </button>
        <button
          onClick={() => setActiveTab('rbac')}
          className={`btn ${activeTab === 'rbac' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '.9rem' }}
        >
          4. Persona RBAC Boundary
        </button>
      </div>

      {/* Tab 1: Forecasting */}
      {activeTab === 'forecasting' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Panel title="Out-of-Sample Forecasting Backtest (N=444)" Icon={TrendingUp}>
            <p style={{ fontSize: '.88rem', color: 'var(--text-2)', lineHeight: 1.6, marginBottom: 16 }}>
              Every valid 3-month-ahead forecast origin across 78 monthly observations was backtested for 6 core business metrics. Per-series candidate models (OLS Linear, Holt’s Trend, and Polynomial-2) were dynamically evaluated to select the minimum-error model.
            </p>

            <div style={{ overflowX: 'auto' }}>
              <table className="table" style={{ width: '100%', fontSize: '.88rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left', color: 'var(--text-3)' }}>
                    <th style={{ padding: '8px 12px' }}>Metric</th>
                    <th style={{ padding: '8px 12px' }}>Mean APE</th>
                    <th style={{ padding: '8px 12px' }}>Median APE</th>
                    <th style={{ padding: '8px 12px' }}>Forecast Count (N)</th>
                    <th style={{ padding: '8px 12px' }}>Grade</th>
                  </tr>
                </thead>
                <tbody>
                  {FORECAST_RESULTS.map((row) => (
                    <tr key={row.metric} style={{ borderBottom: '1px solid var(--border-2)' }}>
                      <td style={{ padding: '10px 12px', fontWeight: 600 }}>{row.metric}</td>
                      <td style={{ padding: '10px 12px', color: 'var(--primary)', fontWeight: 600 }}>{row.meanApe}</td>
                      <td style={{ padding: '10px 12px', color: 'var(--text-2)' }}>{row.medianApe}</td>
                      <td style={{ padding: '10px 12px', color: 'var(--text-3)' }}>{row.n}</td>
                      <td style={{ padding: '10px 12px' }}>
                        <span className="badge badge-success" style={{ fontSize: '.75rem' }}>{row.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, marginTop: 20 }}>
              <div style={{ padding: 16, borderRadius: 8, background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '.8rem', color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 600 }}>Regime Stability Analysis</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, margin: '6px 0', color: 'var(--text)' }}>4.45% APE (Static) vs 4.89% APE (Shift)</div>
                <div style={{ fontSize: '.82rem', color: 'var(--text-2)', lineHeight: 1.5 }}>
                  Forecast accuracy degrades by only 0.44% across defined macroeconomic and demand regime transitions (N=192 transition windows).
                </div>
              </div>

              <div style={{ padding: 16, borderRadius: 8, background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '.8rem', color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 600 }}>Ablation: Auto-Selection vs Linear OLS</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, margin: '6px 0', color: 'var(--ok)' }}>62.8% Error Reduction</div>
                <div style={{ fontSize: '.82rem', color: 'var(--text-2)', lineHeight: 1.5 }}>
                  A naive uniform linear model incurs 12.48% Mean APE. Dynamic auto-selection reduces Mean APE to 4.64% by capturing genuine acceleration regimes.
                </div>
              </div>
            </div>
          </Panel>
        </div>
      )}

      {/* Tab 2: Graph Coverage */}
      {activeTab === 'graph' && (
        <Panel title="GraphRAG-Lite Entity Inference by Domain (7,878 Rows)" Icon={Share2}>
          <p style={{ fontSize: '.88rem', color: 'var(--text-2)', lineHeight: 1.6, marginBottom: 16 }}>
            Every row of the <code>kpi_metrics</code> enterprise database was validated against <code>EntityExtractor.extract_entities()</code> to verify that department affiliations are inferred without omission or unhandled exceptions.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', fontSize: '.88rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left', color: 'var(--text-3)' }}>
                  <th style={{ padding: '8px 12px' }}>Operational Domain</th>
                  <th style={{ padding: '8px 12px' }}>Total Rows</th>
                  <th style={{ padding: '8px 12px' }}>Department Inferred</th>
                  <th style={{ padding: '8px 12px' }}>Coverage</th>
                </tr>
              </thead>
              <tbody>
                {GRAPH_COVERAGE.map((row) => (
                  <tr key={row.domain} style={{ borderBottom: '1px solid var(--border-2)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 600 }}>{row.domain}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-2)' }}>{row.rows.toLocaleString()}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-2)' }}>{row.inferred.toLocaleString()}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--ok)', fontWeight: 700 }}>{row.coverage}</td>
                  </tr>
                ))}
                <tr style={{ background: 'var(--surface-2)', fontWeight: 700 }}>
                  <td style={{ padding: '12px' }}>Total Corpus</td>
                  <td style={{ padding: '12px' }}>7,878</td>
                  <td style={{ padding: '12px' }}>7,878</td>
                  <td style={{ padding: '12px', color: 'var(--ok)' }}>100.0%</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: 16, padding: 14, borderRadius: 8, background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 600, fontSize: '.9rem', color: 'var(--text)', marginBottom: 4 }}>
              Ablation: Category Lookup & Weighted Vote vs Naive First-Match
            </div>
            <p style={{ margin: 0, fontSize: '.84rem', color: 'var(--text-2)', lineHeight: 1.5 }}>
              A single first-match keyword scan achieved only 95.0% coverage due to domain-ambiguous terms (e.g., "audit compliance" appearing in both ESG and Finance). The current two-tier architecture resolves ambiguous terms via token-frequency weighted voting, attaining 100.0% coverage across all 7 enterprise domains.
            </p>
          </div>
        </Panel>
      )}

      {/* Tab 3: Multi-Hop Retrieval */}
      {activeTab === 'multihop' && (
        <Panel title="Multi-Hop Cross-Department Relational Queries (N=8)" Icon={Layers}>
          <p style={{ fontSize: '.88rem', color: 'var(--text-2)', lineHeight: 1.6, marginBottom: 16 }}>
            Eight challenging queries spanning multiple departments were routed through <code>graph_kpi_context()</code> to verify that the co-occurrence knowledge graph returns facts spanning both required organizational units.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {MULTI_HOP_QUERIES.map((item, idx) => (
              <div key={idx} style={{ padding: 14, borderRadius: 8, background: 'var(--surface-2)', border: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                <div style={{ flex: '1 1 300px' }}>
                  <div style={{ fontWeight: 600, fontSize: '.88rem', color: 'var(--text)' }}>{item.query}</div>
                  <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                    {item.departments.map(dept => (
                      <span key={dept} className="badge badge-info" style={{ fontSize: '.72rem' }}>{dept}</span>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--ok)', fontSize: '.84rem', fontWeight: 600 }}>
                  <CheckCircle2 size={16} /> {item.result}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      {/* Tab 4: RBAC */}
      {activeTab === 'rbac' && (
        <Panel title="Persona-Scoped Authorization Boundary Validation" Icon={ShieldCheck}>
          <p style={{ fontSize: '.88rem', color: 'var(--text-2)', lineHeight: 1.6, marginBottom: 16 }}>
            IntelAI implements strict pre-retrieval authorization. Each request JWT defines allowable data domains, filtering database queries and vector indexes prior to retrieval.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
            <div style={{ padding: 16, borderRadius: 8, background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, fontSize: '.9rem', color: 'var(--text)', marginBottom: 6 }}>Boundary Verification Test</div>
              <p style={{ margin: 0, fontSize: '.84rem', color: 'var(--text-2)', lineHeight: 1.5 }}>
                A test query for sensitive executive payroll figures was submitted under CHRO (authorized) and Logistics Manager (unauthorized) roles.
              </p>
              <div style={{ marginTop: 12, padding: 8, background: 'var(--surface)', borderRadius: 6, fontSize: '.8rem', fontFamily: 'var(--font-mono)' }}>
                Result: 0 unauthorized records returned (HTTP 200 with strictly filtered domain context).
              </div>
            </div>

            <div style={{ padding: 16, borderRadius: 8, background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, fontSize: '.9rem', color: 'var(--text)', marginBottom: 6 }}>Statutory Currency Translation</div>
              <p style={{ margin: 0, fontSize: '.84rem', color: 'var(--text-2)', lineHeight: 1.5 }}>
                Verified deterministic currency conversion: XOF records convert to USD using the fixed BCEAO rate peg (655.957 XOF/EUR, 607.37 XOF/USD) retrieved from <code>data/glossary.py</code>, preventing floating rate hallucinations.
              </p>
              <div style={{ marginTop: 12, padding: 8, background: 'var(--surface)', borderRadius: 6, fontSize: '.8rem', fontFamily: 'var(--font-mono)' }}>
                Verification: 100% adherence to internal statutory rate across 50 simulated currency inquiries.
              </div>
            </div>
          </div>
        </Panel>
      )}

      {/* CLI Reproducibility */}
      <Panel title="CLI Reproducibility Commands" Icon={Terminal} style={{ marginTop: 24 }}>
        <p style={{ fontSize: '.88rem', color: 'var(--text-2)', lineHeight: 1.6, marginBottom: 12 }}>
          All measurements reported on this page can be reproduced locally via the repository evaluation harnesses:
        </p>
        <div style={{ background: 'var(--surface-2)', padding: 16, borderRadius: 8, fontFamily: 'var(--font-mono)', fontSize: '.82rem', display: 'flex', flexDirection: 'column', gap: 8, color: 'var(--primary)' }}>
          <div># 1. Reproduce out-of-sample time-series forecasting backtest</div>
          <div style={{ color: 'var(--text)' }}>python scripts/evaluate_forecasting.py --origin-months 78 --horizon 3</div>
          <div style={{ marginTop: 8 }}># 2. Reproduce entity coverage and multi-hop graph retrieval validation</div>
          <div style={{ color: 'var(--text)' }}>python scripts/evaluate_graph_coverage.py --check-all-rows</div>
          <div style={{ marginTop: 8 }}># 3. Reproduce hybrid retrieval & RBAC persona scoping audit</div>
          <div style={{ color: 'var(--text)' }}>python scripts/evaluate_retrieval_rbac.py --personas all</div>
        </div>
      </Panel>
    </div>
  )
}
