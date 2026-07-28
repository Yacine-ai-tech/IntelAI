import React from 'react';
import { BookOpen, Monitor, Terminal, FileCode, CheckCircle, ShieldAlert, 
         Database, Brain, Globe, Zap, Server, Users, ChartBar, AlertTriangle, 
         Lightbulb, Settings, BarChart3, MessageSquare, Network } from 'lucide-react';

export default function UserGuidePage() {
  return (
    <div className="p-8 max-w-6xl mx-auto h-full overflow-y-auto">
      <div className="flex items-center gap-3 mb-8">
        <BookOpen className="w-10 h-10 text-blue-500" />
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
          IntelAI - Complete User Guide
        </h1>
      </div>

      <p className="text-lg text-gray-300 mb-8 leading-relaxed">
        IntelAI is an enterprise-grade business intelligence platform with AI-powered copilot capabilities. 
        It provides real-time KPI dashboards, domain-specific analytics, conversational AI assistance, 
        and advanced features like Monte Carlo simulations and GraphRAG knowledge relationships.
      </p>

      <div className="space-y-8 text-gray-200">
        
        {/* What is IntelAI */}
        <section className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
            <Brain className="w-6 h-6 text-purple-400" /> What is IntelAI?
          </h2>
          <div className="space-y-4">
            <p className="text-gray-300">
              IntelAI is a comprehensive business intelligence platform with <strong className="text-blue-400">9 key capabilities</strong>:
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-green-400 text-lg mb-2">📊 Domain Dashboards</h3>
                <p className="text-sm text-gray-300">Finance, Growth, Operations, People, ESG, IT, Risk, Governance views with real-time KPIs.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-blue-400 text-lg mb-2">🤖 AI Copilot</h3>
                <p className="text-sm text-gray-300">Conversational AI assistant with 9 domain-specific personas for natural language queries.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-purple-400 text-lg mb-2">🔍 Hybrid RAG</h3>
                <p className="text-sm text-gray-300">Reciprocal Rank Fusion combining BM25 keyword search with dense vector embeddings.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-red-400 text-lg mb-2">📈 Forecasting</h3>
                <p className="text-sm text-gray-300">Time-series forecasting with Monte Carlo simulations for predictive analytics.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-yellow-400 text-lg mb-2">🕸️ GraphRAG</h3>
                <p className="text-sm text-gray-300">Knowledge graph relationships for multi-hop queries and context understanding.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-cyan-400 text-lg mb-2">📋 Glossary</h3>
                <p className="text-sm text-gray-300">Comprehensive business metrics glossary with definitions and benchmarking.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-orange-400 text-lg mb-2">🎯 Scenarios</h3>
                <p className="text-sm text-gray-300">7 business scenarios for testing: healthy, declining, crisis modes, and more.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-pink-400 text-lg mb-2">👥 RBAC</h3>
                <p className="text-sm text-gray-300">Role-based access control with 11 roles from admin to viewer.</p>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <h3 className="font-semibold text-indigo-400 text-lg mb-2">🌐 Bilingual</h3>
                <p className="text-sm text-gray-300">English/French support with localized formatting and currency display.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Domain Personas */}
        <section className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
            <Users className="w-6 h-6 text-green-400" /> 9 Domain-Specific AI Personas
          </h2>
          <p className="text-gray-300 mb-4">
            IntelAI's copilot automatically routes queries through specialized personas for accurate, context-aware responses:
          </p>
          <div className="grid md:grid-cols-3 gap-3">
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-blue-400 font-semibold">💼 Finance Persona</span>
              <p className="text-xs text-gray-400 mt-1">Revenue, margins, EBITDA analysis</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-green-400 font-semibold">📈 Growth Persona</span>
              <p className="text-xs text-gray-400 mt-1">Customer acquisition, churn, retention</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-purple-400 font-semibold">⚙️ Operations Persona</span>
              <p className="text-xs text-gray-400 mt-1">OEE, quality, logistics efficiency</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-orange-400 font-semibold">👥 People Persona</span>
              <p className="text-xs text-gray-400 mt-1">Headcount, turnover, hiring metrics</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-teal-400 font-semibold">🌱 ESG Persona</span>
              <p className="text-xs text-gray-400 mt-1">Environmental, social, governance</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-red-400 font-semibold">🛡️ Risk Persona</span>
              <p className="text-xs text-gray-400 mt-1">Risk assessment, compliance, audits</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-cyan-400 font-semibold">💻 IT Persona</span>
              <p className="text-xs text-gray-400 mt-1">Infrastructure, uptime, security</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-pink-400 font-semibold">⚖️ Governance Persona</span>
              <p className="text-xs text-gray-400 mt-1">Board oversight, compliance, policies</p>
            </div>
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
              <span className="text-yellow-400 font-semibold">📊 Analytics Persona</span>
              <p className="text-xs text-gray-400 mt-1">Cross-domain analysis and insights</p>
            </div>
          </div>
        </section>

        {/* Configuration & Setup */}
        <section className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
            <Settings className="w-6 h-6 text-amber-400" /> Configuration & Setup
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-blue-400 text-lg mb-2 flex items-center gap-2">
                <Database className="w-5 h-5" /> Database Setup
              </h3>
              <ul className="text-sm text-gray-300 space-y-2">
                <li>• PostgreSQL with pgvector extension</li>
                <li>• Neon database recommended for free tier</li>
                <li>• Qdrant for vector store (production)</li>
                <li>• Chroma for local development</li>
              </ul>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-green-400 text-lg mb-2 flex items-center gap-2">
                <Zap className="w-5 h-5" /> Required API Keys
              </h3>
              <ul className="text-sm text-gray-300 space-y-2">
                <li>• <strong>GROQ_API_KEY:</strong> Default LLM provider</li>
                <li>• <strong>ANTHROPIC_API_KEY:</strong> Reasoning LLM</li>
                <li>• <strong>OPENAI_API_KEY:</strong> Optional backup</li>
                <li>• <strong>TAVILY_API_KEY:</strong> Web search capability</li>
              </ul>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-purple-400 text-lg mb-2 flex items-center gap-2">
                <Monitor className="w-5 h-5" /> Installation
              </h3>
              <pre className="bg-gray-950 p-3 rounded-lg text-xs font-mono text-green-300 overflow-x-auto">
{`git clone https://github.com/Yacine-ai-tech/IntelAI
cd IntelAI
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.data.seed  # Seed KPI data`}
              </pre>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-red-400 text-lg mb-2 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" /> Data Scenarios
              </h3>
              <p className="text-sm text-gray-300 mb-2">Use Admin panel to switch between 7 business scenarios:</p>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• <strong>Healthy:</strong> S&P 500 baseline metrics</li>
                <li>• <strong>Declining Financial:</strong> Revenue contraction</li>
                <li>• <strong>High Churn Crisis:</strong> Customer retention failure</li>
                <li>• <strong>Operational Meltdown:</strong> OEE collapse</li>
                <li>• <strong>Talent Crisis:</strong> High attrition rates</li>
                <li>• <strong>Cybersecurity Breach:</strong> Security incidents</li>
                <li>• <strong>ESG Failure:</strong> Governance issues</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Real-World Use Cases */}
        <section className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
            <Lightbulb className="w-6 h-6 text-yellow-400" /> Real-World Use Cases
          </h2>
          
          <div className="space-y-4">
            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-blue-400 text-lg mb-2">🏢 Executive Briefing</h3>
              <p className="text-sm text-gray-300">
                "Generate a comprehensive executive briefing covering all business domains with key risks, opportunities, and recommendations."
              </p>
              <p className="text-xs text-gray-500 mt-2">Persona: Analytics | Features: Cross-domain analysis, GraphRAG</p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-green-400 text-lg mb-2">💰 Financial Analysis</h3>
              <p className="text-sm text-gray-300">
                "Analyze our revenue trends, profit margins, and provide a 6-month forecast with confidence intervals."
              </p>
              <p className="text-xs text-gray-500 mt-2">Persona: Finance | Features: Forecasting, Monte Carlo</p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-purple-400 text-lg mb-2">👥 HR Strategy</h3>
              <p className="text-sm text-gray-300">
                "Review our headcount trends, turnover rates, and recommend strategies to improve employee retention."
              </p>
              <p className="text-xs text-gray-500 mt-2">Persona: People | Features: KPI analysis, Benchmarking</p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-red-400 text-lg mb-2">⚠️ Risk Assessment</h3>
              <p className="text-sm text-gray-300">
                "Identify potential risks across all business domains and prioritize them by severity and likelihood."
              </p>
              <p className="text-xs text-gray-500 mt-2">Persona: Risk | Features: Anomaly detection, Cross-domain analysis</p>
            </div>
          </div>
        </section>

        {/* Advanced Features */}
        <section className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
            <BarChart3 className="w-6 h-6 text-cyan-400" /> Advanced Features
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-purple-400 text-lg mb-2 flex items-center gap-2">
                <Network className="w-5 h-5" /> GraphRAG Knowledge Graph
              </h3>
              <p className="text-sm text-gray-300">
                Entity-graph ranking of KPI records enables multi-hop queries. For example, asking "How does high employee turnover affect our revenue?" 
                can traverse relationships between People and Finance domains for comprehensive answers.
              </p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-blue-400 text-lg mb-2 flex items-center gap-2">
                <MessageSquare className="w-5 h-5" /> Conversational Interface
              </h3>
              <p className="text-sm text-gray-300">
                Natural language interface with context-aware responses. The copilot maintains conversation history, 
                understands follow-up questions, and provides cited sources for all information.
              </p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-green-400 text-lg mb-2 flex items-center gap-2">
                <Globe className="w-5 h-5" /> Hybrid Search Engine
              </h3>
              <p className="text-sm text-gray-300">
                Combines BM25 keyword search with dense vector embeddings using Reciprocal Rank Fusion. 
                Supports hosted rerank backstops (Cohere/Jina) for resilience when local models are unavailable.
              </p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-orange-400 text-lg mb-2 flex items-center gap-2">
                <Server className="w-5 h-5" /> Production Ready
              </h3>
              <p className="text-sm text-gray-300">
                Docker deployment with Render/Railway support. Health checks, observability, and 
                telemetry included. Scales efficiently on free-tier infrastructure (512MB RAM).
              </p>
            </div>
          </div>
        </section>

        {/* Security & Best Practices */}
        <section className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
            <ShieldAlert className="w-6 h-6 text-red-400" /> Security & Best Practices
          </h2>
          <ul className="space-y-3">
            <li className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
              <span className="text-sm text-gray-300"><strong>RBAC Implementation:</strong> Use role-based access control to restrict sensitive financial and HR data to authorized personnel only.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
              <span className="text-sm text-gray-300"><strong>Secure API Keys:</strong> Never commit .env files. Rotate API keys regularly and use different keys for dev/staging/prod environments.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
              <span className="text-sm text-gray-300"><strong>Database Security:</strong> Use Neon's built-in security features, enable SSL, and implement connection pooling for production.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
              <span className="text-sm text-gray-300"><strong>Audit Logging:</strong> Enable audit trails for sensitive operations and review regularly for unauthorized access attempts.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
              <span className="text-sm text-gray-300"><strong>Scenario Testing:</strong> Always test new features in non-production scenarios before deploying to healthy production data.</span>
            </li>
          </ul>
        </section>

      </div>
    </div>
  );
}