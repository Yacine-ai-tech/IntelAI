"""
OmniSmart Chatbot Service — IntelAI's persona-routed RAG copilot.

The single chatbot service for IntelAI. Resolves a role persona (CEO/CFO/…) that
scopes which data it may read (RBAC), retrieves a live KPI snapshot + grounded
knowledge docs, and answers with inline numbered citations.

Features:
- Persona-routed RAG with per-role data-access scoping (RBAC)
- Live KPI snapshot injection + hybrid/GraphRAG-lite document retrieval
- Grounded answers with canonical, deduplicated source citations
- Lightweight bilingual (EN/FR) conversational agent
- Token-efficient context windowing

USAGE:
    from src.services.omnismart_chatbot import OmniSmartChatbot
    
    chatbot = OmniSmartChatbot(conversation_id="user_session", domain="finance")
    
    # Process queries across all 5 patterns + conversational agent
    result = chatbot.process(
        message="Analyze Q4 revenue trends and suggest optimizations",
        mode="auto",  # or: agent, rag, analysis, extraction, conversation, voice
        context="Additional context..."
    )
    
    print(result["response"])
    print(result["type"])  # Pattern used
"""

from __future__ import annotations

import json
import uuid
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from io import BytesIO
import re
import logging

import numpy as np
import pandas as pd

from src.core.config import settings
from src.core.i18n import I18N, t
from src.core.logger import get_logger
from src.services.pg_store import (
    get_conversation_history,
    get_conversations,
    get_knowledge_docs,
    store_conversation,
    store_knowledge_docs,
    store_chat_session,
)

log = get_logger(__name__)

# ════════════════════════════════════════════════════════════════════════════
# LAZY-LOADED DEPENDENCIES
# ════════════════════════════════════════════════════════════════════════════

_GROQ = False
_SBERT = False
_TFIDF = False

try:
    from groq import Groq
    _GROQ = True
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer
    _SBERT = True
except Exception:
    pass

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _TFIDF = True
except ImportError:
    pass


# ════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 1: MULTI-STEP AUTONOMOUS AGENTS
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 2: ULTRA-FAST RAG WITH KNOWLEDGE BASE INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

class UltraFastRAG:
    """Vector-based document retrieval with semantic search and context injection."""

    def __init__(self, system_instruction: Optional[str] = None):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.cache: Dict[str, Any] = {}
        self.max_cache_size = 100
        self.embedding_model = None
        self.vectorstore = None
        
        if _SBERT:
            try:
                self.embedding_model = SentenceTransformer(
                    settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2"
                )
            except Exception as e:
                log.warning("Failed to load embedding model: %s", e)
        
        default_instruction = (
            "You are a knowledgeable analyst with access to company knowledge base. "
            "Use retrieved context to answer accurately and provide citations."
        )
        self.system_instruction = system_instruction or default_instruction

    def _retrieve_documents(
        self,
        query: str,
        top_k: int = 5,
        language: Optional[str] = None,
    ) -> List[Tuple[str, str, float]]:
        """Retrieve most relevant documents using semantic similarity."""
        try:
            # Persistent vector store (chroma/pgvector/qdrant) — dense hits from the store
            # fused with BM25 + reranker. No-op (returns None) when VECTOR_STORE=memory.
            try:
                from src.services.vector_store import vector_store_retrieve
                vr = vector_store_retrieve(query, top_k, language)
                if vr:
                    return vr
            except Exception as e:
                log.warning("Vector store retrieval skipped: %s", e)

            docs = get_knowledge_docs()
            if docs.empty:
                return []
            
            # Filter by language if specified
            if language and "language" in docs.columns:
                lang_docs = docs[docs["language"] == language]
                if not lang_docs.empty:
                    docs = lang_docs

            # Hybrid retrieval (dense + BM25 + RRF + reranker) — opt-in via USE_HYBRID_RETRIEVAL.
            # Falls through to the vector/TF-IDF path below when disabled or unavailable.
            try:
                from src.services.hybrid_retrieval import hybrid_enabled, hybrid_doc_retrieve
                if hybrid_enabled():
                    records = list(zip(docs["title"].tolist(), docs["content"].fillna("").tolist()))
                    hy = hybrid_doc_retrieve(query, records, top_k)
                    if hy:
                        return hy
            except Exception as e:
                log.warning("Hybrid retrieval skipped: %s", e)

            # Semantic search with embeddings
            if _SBERT and self.embedding_model and "embedding" in docs.columns:
                try:
                    query_embedding = self.embedding_model.encode([query])[0]
                    doc_embeddings = []
                    
                    for emb_str in docs["embedding"]:
                        if emb_str and isinstance(emb_str, str):
                            try:
                                doc_embeddings.append(np.array(json.loads(emb_str)))
                            except:
                                doc_embeddings.append(np.zeros_like(query_embedding))
                        else:
                            doc_embeddings.append(np.zeros_like(query_embedding))
                    
                    if doc_embeddings:
                        doc_embeddings = np.array(doc_embeddings)
                        similarities = cosine_similarity(
                            [query_embedding],
                            doc_embeddings
                        )[0]
                        
                        top_indices = np.argsort(similarities)[::-1][:top_k]
                        results = []
                        for idx in top_indices:
                            if similarities[idx] > 0.3:  # Relevance threshold
                                results.append((
                                    docs.iloc[idx]["title"],
                                    docs.iloc[idx]["content"],
                                    float(similarities[idx]),
                                ))
                        return results
                except Exception as e:
                    log.warning("Semantic search failed: %s", e)
            
            # Fallback to TF-IDF
            if _TFIDF:
                try:
                    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
                    doc_vectors = vectorizer.fit_transform(docs["content"].fillna(""))
                    query_vector = vectorizer.transform([query])
                    similarities = cosine_similarity(query_vector, doc_vectors)[0]
                    
                    top_indices = np.argsort(similarities)[::-1][:top_k]
                    results = []
                    for idx in top_indices:
                        if similarities[idx] > 0.1:
                            results.append((
                                docs.iloc[idx]["title"],
                                docs.iloc[idx]["content"],
                                float(similarities[idx]),
                            ))
                    return results
                except Exception as e:
                    log.warning("TF-IDF search failed: %s", e)
            
            # Fallback: simple keyword search
            query_terms = query.lower().split()
            scored_docs = []
            for idx, row in docs.iterrows():
                content_lower = (row["content"] or "").lower()
                score = sum(1 for term in query_terms if term in content_lower)
                if score > 0:
                    scored_docs.append((idx, score))
            
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            results = []
            for idx, score in scored_docs[:top_k]:
                results.append((
                    docs.iloc[idx]["title"],
                    docs.iloc[idx]["content"],
                    float(score) / len(query_terms) if query_terms else 0.5,
                ))
            return results
            
        except Exception as e:
            log.error("Document retrieval error: %s", e)
            return []

    def _build_rag_prompt(
        self,
        query: str,
        documents: List[Tuple[str, str, float]],
    ) -> Tuple[str, str]:
        """Return ``(system_instruction, user_content)`` split for prompt-cache
        friendliness: the instruction is stable per language (a cacheable prefix),
        while the retrieved docs + query are volatile and go in the user turn."""
        doc_context = "\n\n".join(
            f"📄 **{title}** (relevance: {sim:.1%})\n{content[:300]}..."
            for title, content, sim in documents
        )
        lang_instruction = "Répondez en français." if I18N.lang() == "fr" else "Reply in English."

        system_instruction = (
            f"{lang_instruction}\n\n"
            "You answer questions using the retrieved knowledge-base context provided in the "
            "user message. Provide a comprehensive, accurate answer, cite sources where relevant, "
            "and if information is incomplete, state what additional data would help."
        )
        user_content = (
            "RETRIEVED CONTEXT FROM KNOWLEDGE BASE:\n"
            f"{doc_context if doc_context else '(No relevant documents found)'}\n\n"
            f"USER QUERY: {query}"
        )
        return system_instruction, user_content

    def answer(
        self,
        query: str,
        top_k: int = 5,
        use_cache: bool = True,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate RAG-based answer with retrieved documents."""
        if not self.client:
            return {
                "query": query,
                "response": "RAG unavailable (Groq not configured)",
                "sources": [],
                "type": "rag",
            }
        
        # Check cache
        cache_key = f"rag:{query}"
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Retrieve documents (vector / TF-IDF / keyword over the knowledge base)
        documents = self._retrieve_documents(query, top_k, language)

        # GraphRAG-lite: for multi-hop entity queries, prepend graph-selected KPI
        # records (opt-in via USE_GRAPH_RAG; no-op + safe fallback otherwise).
        try:
            from src.services.graph_retrieval import graph_kpi_context
            graph_docs = graph_kpi_context(query, top_k=min(top_k, 6))
            if graph_docs:
                seen = {t for t, _, _ in graph_docs}
                documents = graph_docs + [d for d in documents if d[0] not in seen]
        except Exception as e:
            log.warning("GraphRAG-lite augmentation skipped: %s", e)

        # Build prompt (stable system instruction + volatile docs/query) — cache-friendly
        system_instruction, user_content = self._build_rag_prompt(query, documents)

        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=1024,
                temperature=0.4,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            log.error("RAG generation error: %s", e)
            answer = f"Error generating response: {str(e)[:100]}"
        
        result = {
            "query": query,
            "response": answer,
            "sources": normalize_sources([
                {"title": title, "snippet": content[:240], "relevance": sim}
                for title, content, sim in documents
            ]),
            "type": "rag",
            "document_count": len(documents),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache result
        if len(self.cache) < self.max_cache_size:
            self.cache[cache_key] = result
        
        return result


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 3: REAL-TIME DATA FLOW ANALYSIS
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 4: NATURAL VOICE CHATBOT
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 5: STRUCTURED DATA EXTRACTION
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# LIGHTWEIGHT CONVERSATIONAL AGENT (Bilingual, Multi-Domain, Memory-Efficient)
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# PERSONA SYSTEM (Integrated from persona_factory.py)
# ════════════════════════════════════════════════════════════════════════════

PERSONA_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "ceo": {
        "display_name": "CEO Strategist",
        "system_prompt": (
            "You are the CEO Intelligence Agent for IntelAI.\n"
            "You provide strategic insights, market analysis, M&A guidance, and board-level reporting.\n"
            "Focus on: growth trajectory, competitive positioning, organizational health.\n"
            "Always think in terms of long-term value creation. Be concise for executives. "
            "Use bullet points. Quantify everything."
        ),
        "allowed_tools": ["kpi_query", "forecast", "report_generate", "market_analysis"],
        "data_access": ["Finance", "Growth", "Operations", "People", "ESG", "IT", "Logistics"],
        "temperature": 0.4,
    },
    "cfo": {
        "display_name": "CFO Analyst",
        "system_prompt": (
            "You are the CFO Intelligence Agent for IntelAI.\n"
            "You provide financial analysis, budget variance reports, cash flow forecasting, "
            "and financial statement generation. Be precise with numbers. Flag risks proactively. "
            "Always reference the data behind conclusions."
        ),
        "allowed_tools": ["kpi_query", "forecast", "financial_statements", "budget_analysis"],
        "data_access": ["Finance", "Growth"],
        "temperature": 0.2,
    },
    "cto": {
        "display_name": "CTO Advisor",
        "system_prompt": (
            "You are the CTO Intelligence Agent for IntelAI.\n"
            "You advise on technology strategy, infrastructure costs, security posture, and engineering metrics.\n"
            "Analyze burn rate vs. engineering output. Evaluate build-vs-buy decisions."
        ),
        "allowed_tools": ["kpi_query", "risk_analysis", "technology_metrics"],
        "data_access": ["IT", "Operations", "Finance"],
        "temperature": 0.3,
    },
    "coo": {
        "display_name": "COO Operations",
        "system_prompt": (
            "You are the COO Intelligence Agent for IntelAI.\n"
            "You focus on operational efficiency, supply chain metrics, process optimization. "
            "Track cycle times, throughput, resource utilization. Identify bottlenecks."
        ),
        "allowed_tools": ["kpi_query", "operations_metrics", "supply_chain"],
        "data_access": ["Operations", "Logistics", "Growth", "People"],
        "temperature": 0.3,
    },
    "chro": {
        "display_name": "CHRO People",
        "system_prompt": (
            "You are the CHRO Intelligence Agent for IntelAI.\n"
            "You focus on talent management, workforce analytics, engagement scores, diversity metrics. "
            "Balance people metrics with business outcomes. Recommend retention improvements."
        ),
        "allowed_tools": ["kpi_query", "people_metrics", "engagement_analysis"],
        "data_access": ["People", "ESG"],
        "temperature": 0.4,
    },
    "esg": {
        "display_name": "ESG & Sustainability",
        "system_prompt": (
            "You are the ESG Intelligence Agent for IntelAI.\n"
            "You track environmental, social, and governance metrics. "
            "Analyze carbon footprint, diversity indices, safety records. Help prepare ESG reports."
        ),
        "allowed_tools": ["kpi_query", "esg_metrics", "sustainability_report"],
        "data_access": ["ESG", "Operations", "People"],
        "temperature": 0.3,
    },
    "risk": {
        "display_name": "Risk & Compliance",
        "system_prompt": (
            "You are the Risk & Compliance Intelligence Agent for IntelAI.\n"
            "You monitor operational risks, compliance requirements, anomaly detection. "
            "Proactively flag issues and recommend mitigation strategies."
        ),
        "allowed_tools": ["kpi_query", "risk_analysis", "anomaly_detection"],
        "data_access": ["Finance", "Operations", "ESG", "IT"],
        "temperature": 0.2,
    },
    "analyst": {
        "display_name": "Business Analyst",
        "system_prompt": (
            "You are the Business Analyst Agent for IntelAI.\n"
            "You perform data analysis, create insights, run forecasts, generate reports. "
            "Be thorough, data-driven, communicate with supporting evidence."
        ),
        "allowed_tools": ["kpi_query", "forecast", "data_analysis", "report_generate"],
        "data_access": ["Finance", "Growth", "Operations", "People", "IT", "Logistics", "ESG"],
        "temperature": 0.3,
    },
    "general": {
        "display_name": "IntelAI Assistant",
        "system_prompt": (
            "You are the IntelAI Intelligence Assistant.\n"
            "You help users understand data, answer KPI questions, generate insights, navigate the platform. "
            "Adapt communication to user needs. Be helpful, accurate, proactive."
        ),
        "allowed_tools": ["kpi_query", "forecast", "data_analysis"],
        "data_access": ["Finance", "Growth", "Operations", "People"],
        "temperature": 0.3,
    },
}

ROLE_PERSONA_MAP = {
    "admin": "ceo", "ceo": "ceo", "cfo": "cfo", "cto": "cto",
    "coo": "coo", "chro": "chro", "hr": "chro", "esg": "esg", "risk": "risk",
    "analyst": "analyst", "viewer": "general", "operations": "coo", "it": "cto",
    "custom": "general",
}


class PersonaContext:
    """Resolved persona with configuration."""
    def __init__(self, name: str, display_name: str, system_prompt: str,
                 allowed_tools: List[str], data_access: List[str],
                 temperature: float, language: str = "en"):
        self.name = name
        self.display_name = display_name
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools
        self.data_access = data_access
        self.temperature = temperature
        self.language = language

    def add_language_instruction(self) -> str:
        """Add language instruction to system prompt."""
        lang_label = "French" if self.language == "fr" else "English"
        return f"{self.system_prompt}\n\nIMPORTANT: Respond in {lang_label}."


# ════════════════════════════════════════════════════════════════════════════
# CITATIONS — one canonical schema for every retrieval path
# ════════════════════════════════════════════════════════════════════════════

def normalize_sources(raw: List[Any], cap: int = 8) -> List[Dict[str, Any]]:
    """Canonicalise citations from any retrieval path into one robust, scalable
    shape so every surface renders identical, deduplicated, traceable sources.

    Output item: ``{id, title, type, relevance (0..1 float|None), snippet, source}``.
    Deduped by title (keeps the max relevance), live/KPI sources pinned first, then
    by relevance desc, capped, and 1-indexed for inline ``[n]`` citations.
    Accepts heterogeneous inputs (strings, ``{title,relevance}``, ``{title,preview,
    relevance:"87%"}``…) so callers never have to agree on a format.
    """
    def _rel(v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                f = float(v.strip().rstrip("%"))
            except ValueError:
                return None
        else:
            try:
                f = float(v)
            except (TypeError, ValueError):
                return None
        if f != f:  # NaN
            return None
        return round(f / 100 if f > 1 else f, 3)

    seen: Dict[str, Dict[str, Any]] = {}
    for s in raw or []:
        if not isinstance(s, dict):
            s = {"title": str(s)}
        title = str(s.get("title") or s.get("source") or "source").strip()
        if not title:
            continue
        key = title.lower()
        rel = _rel(s.get("relevance"))
        if key in seen:
            ex = seen[key]
            if rel is not None and (ex.get("relevance") is None or rel > ex["relevance"]):
                ex["relevance"] = rel
            continue
        snippet = (s.get("snippet") or s.get("preview") or "").strip()
        seen[key] = {
            "title": title,
            "type": s.get("type") or ("glossary" if key.startswith("glossary") else "knowledge"),
            "relevance": rel,
            "snippet": snippet[:240] or None,
            "source": s.get("source"),
        }
    items = list(seen.values())
    items.sort(key=lambda x: (0 if x["type"] == "kpi" else 1, -(x.get("relevance") or 0.0)))
    items = items[:cap]
    for i, it in enumerate(items, 1):
        it["id"] = i
    return items


# ════════════════════════════════════════════════════════════════════════════
# AGENT PERSONA FACTORY
# ════════════════════════════════════════════════════════════════════════════

class AgentPersonaFactory:
    """
    Dynamic agent persona factory.
    
    Resolves the appropriate persona based on:
    1. Explicit persona name (if provided)
    2. User role mapping
    3. Fallback to 'general'
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ and settings.GROQ_API_KEY else None
        # Personas are defined in-memory (PERSONA_TEMPLATES) — the single source of truth.
        self._db_personas: Dict[str, Dict] = {}

    # ── RBAC: persona scope guardrails ──────────────────────────────────────
    def _persona_scope(self, name: str) -> set:
        """The data categories a persona is allowed to read (lowercased)."""
        tmpl = self._db_personas.get(name) or PERSONA_TEMPLATES.get(name, {})
        return {c.lower() for c in tmpl.get("data_access", [])}

    def allowed_personas_for_role(self, user_role: str) -> List[str]:
        """Personas a user may switch to *without* widening their data scope.

        A persona is permitted iff its ``data_access`` is a subset of the role's
        own scope (its default persona). admin/ceo carry full scope, so every
        persona qualifies for them; a CFO cannot impersonate, say, the CHRO to
        reach People data. This is the persona-level RBAC the strategy requires.
        """
        default = ROLE_PERSONA_MAP.get(user_role, "general")
        base_scope = self._persona_scope(default)
        out: List[str] = []
        for name in {**PERSONA_TEMPLATES, **self._db_personas}:
            if name == default or self._persona_scope(name).issubset(base_scope):
                out.append(name)
        return out

    def resolve_persona(
        self,
        user_role: str,
        persona_override: Optional[str] = None,
        language: str = "en",
    ) -> PersonaContext:
        """Resolve the best persona for the given user role."""
        # Priority: explicit override → role mapping → general
        persona_name = persona_override or ROLE_PERSONA_MAP.get(user_role, "general")

        # RBAC guard: never let an override widen the caller's data scope.
        if persona_override and persona_override not in self.allowed_personas_for_role(user_role):
            fallback = ROLE_PERSONA_MAP.get(user_role, "general")
            log.warning("RBAC: role '%s' may not use persona '%s' — using '%s'",
                        user_role, persona_override, fallback)
            persona_name = fallback

        # Try DB personas first, then in-memory templates
        template = self._db_personas.get(persona_name) or PERSONA_TEMPLATES.get(persona_name, PERSONA_TEMPLATES["general"])

        # Ensure temperature and tools are in template
        temp = template.get("temperature", 0.3)
        tools = template.get("allowed_tools", [])
        data_access = template.get("data_access", [])
        display_name = template.get("display_name", persona_name.upper())
        system_prompt = template.get("system_prompt", "You are a helpful assistant.")

        # Add language instruction to system prompt
        lang_label = "French" if language == "fr" else "English"
        system_prompt = f"{system_prompt}\n\nIMPORTANT: Respond in {lang_label}."

        return PersonaContext(
            name=persona_name,
            display_name=display_name,
            system_prompt=system_prompt,
            allowed_tools=tools,
            data_access=data_access,
            temperature=temp,
            language=language,
        )

    def _retrieve_context(self, message: str, persona: "PersonaContext", language: str = "en"):
        """Persona-routed RAG: gather a live KPI snapshot (scoped to the persona's
        data_access) + relevant knowledge docs. Returns (context_text, sources)."""
        raw_sources: List[Dict[str, Any]] = []
        kpi_block: Optional[str] = None
        doc_blocks: List[Tuple[str, str]] = []
        scope = {c.lower() for c in (getattr(persona, "data_access", None) or [])}

        # 1) Live KPI snapshot (latest period), scoped to the persona's domains (RBAC)
        try:
            from src.services.pg_store import get_kpi_metrics
            df = get_kpi_metrics()
            if df is not None and not df.empty:
                latest = sorted(df["period"].unique())[-1]
                cur = df[df["period"] == latest]
                if scope:
                    cur = cur[cur["category"].str.lower().isin(scope)]
                lines, cats = [], []
                for cat in sorted(cur["category"].unique()):
                    cdf = cur[cur["category"] == cat]
                    metrics = "; ".join(
                        f"{r.metric}={r.value}{(' ' + r.unit) if getattr(r, 'unit', '') else ''}"
                        for r in cdf.itertuples()
                    )
                    lines.append(f"- {cat} ({latest}): {metrics}")
                    cats.append(cat)
                if lines:
                    kpi_block = "\n".join(lines)
                    raw_sources.append({
                        "title": f"Live KPI snapshot · {latest}", "type": "kpi", "relevance": 1.0,
                        "snippet": f"{', '.join(cats)} metrics for {latest}", "source": f"kpi/{latest}",
                    })
        except Exception as e:
            log.warning("KPI context retrieval failed: %s", e)

        # 2) Relevant knowledge docs (hybrid / GraphRAG-lite / vector)
        try:
            docs = _get_shared_rag()._retrieve_documents(message, top_k=6, language=language)
            for title, content, score in (docs or []):
                doc_blocks.append((str(title), str(content)))
                raw_sources.append({
                    "title": str(title),
                    "type": "glossary" if str(title).lower().startswith("glossary") else "knowledge",
                    "relevance": round(float(score), 3),
                    "snippet": str(content)[:240],
                })
        except Exception as e:
            log.warning("Doc context retrieval failed: %s", e)

        sources = normalize_sources(raw_sources)

        # Build the context with [n] markers aligned to the citation ids, so the model
        # can cite inline as [1], [2] … and the chips match exactly.
        by_title = {s["title"].lower(): s for s in sources}
        parts: List[str] = []
        if kpi_block is not None:
            sid = next((s["id"] for s in sources if s["type"] == "kpi"), None)
            parts.append(f"[{sid}] LIVE KPI SNAPSHOT:\n{kpi_block}" if sid else f"LIVE KPI SNAPSHOT:\n{kpi_block}")
        for title, text in doc_blocks:
            s = by_title.get(title.lower())
            if s:
                parts.append(f"[{s['id']}] {title}: {text[:500]}")

        return ("\n\n".join(parts), sources)

    def chat(
        self,
        message: str,
        user_role: str,
        persona_override: Optional[str] = None,
        language: str = "en",
        history: Optional[List[Dict[str, str]]] = None,
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Send a chat message through the resolved persona.
        
        Returns dict with: response, persona_used, tokens_used, latency_ms
        """
        if not self.client:
            return {
                "response": "AI agent unavailable (missing API key)." if language != "fr" else "Agent IA non disponible (clé API manquante).",
                "persona_used": "none",
                "tokens_used": 0,
                "latency_ms": 0,
            }

        persona = self.resolve_persona(user_role, persona_override, language)
        start = time.time()

        # ── Persona-routed RAG: auto-retrieve grounded data + sources ──
        retrieved_ctx, sources = self._retrieve_context(message, persona, language)
        full_context = "\n\n".join(c for c in [context, retrieved_ctx] if c).strip()

        # Prompt-cache friendly layout: the system message (persona prompt + fixed
        # grounding instruction) is IDENTICAL for every request with the same persona,
        # so it forms a long stable prefix that Groq auto-caches at 50% (and that Anthropic
        # caches via cache_control). The volatile live data + question go LAST, in the user
        # turn, so they never invalidate the cached prefix.
        system_prompt = (
            persona.system_prompt + "\n\n"
            "You have DIRECT access to the company's live data, provided with the user's message "
            "below. Answer the question directly using those numbers — never ask the user to supply "
            "data or to pick a focus area when the data is already provided. Be specific and quote the "
            "metric values. CITE your sources inline using the bracketed numbers shown in the data "
            "block, e.g. 'Revenue is $3.6M [1]'. Only use citation numbers that appear in the data "
            "block and never invent one. Only use data within your access scope; if a figure is "
            "genuinely missing, say so in one short sentence."
        )
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

        # Conversation history (last 10 messages) — after the cached system prefix.
        if history:
            messages.extend(history[-10:])

        # Volatile live data + question last, so the cached prefix stays valid.
        data_block = (
            f"=== LIVE DATA (scope: {', '.join(persona.data_access) or 'all'}) ===\n"
            f"{full_context if full_context else '(no data retrieved)'}"
        )
        messages.append({"role": "user", "content": f"{data_block}\n\n=== QUESTION ===\n{message}"})

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                max_tokens=2048,
                temperature=persona.temperature,
                top_p=0.9,
            )

            reply = response.choices[0].message.content
            tokens = getattr(response.usage, 'total_tokens', 0) if response.usage else 0
            latency = int((time.time() - start) * 1000)

            return {
                "response": reply,
                "persona_used": persona.name,
                "persona_display": persona.display_name,
                "tokens_used": tokens,
                "latency_ms": latency,
                "sources": sources,
            }
        except Exception as exc:
            log.error("Persona chat error (%s): %s", persona.name, exc)
            return {
                "response": f"Error: {exc}",
                "persona_used": persona.name,
                "tokens_used": 0,
                "latency_ms": int((time.time() - start) * 1000),
            }

    def list_personas(self, user_role: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available personas. When ``user_role`` is given, return only the
        personas that role may use (RBAC — see ``allowed_personas_for_role``)."""
        all_personas = {**PERSONA_TEMPLATES, **self._db_personas}
        allowed = set(self.allowed_personas_for_role(user_role)) if user_role else None
        result = []
        for name, template in all_personas.items():
            if allowed is not None and name not in allowed:
                continue
            result.append({
                "name": name,
                "display_name": template.get("display_name", name),
                "data_access": template.get("data_access", []),
                "allowed_tools": template.get("allowed_tools", []),
            })
        return result

    def get_persona_for_role(self, role: str) -> str:
        """Get the default persona name for a given role."""
        return ROLE_PERSONA_MAP.get(role, "general")


# ── Convenience singleton ──────────────────────────────────────────────────
_factory: Optional[AgentPersonaFactory] = None

def get_persona_factory() -> AgentPersonaFactory:
    """Get or create the singleton persona factory."""
    global _factory
    if _factory is None:
        _factory = AgentPersonaFactory()
    return _factory


# Shared retriever for persona-routed RAG (knowledge docs + hybrid/GraphRAG).
_SHARED_RAG: Optional["UltraFastRAG"] = None

def _get_shared_rag() -> "UltraFastRAG":
    global _SHARED_RAG
    if _SHARED_RAG is None:
        _SHARED_RAG = UltraFastRAG()
    return _SHARED_RAG


# ════════════════════════════════════════════════════════════════════════════
# OMNISMART UNIFIED CHATBOT (with integrated persona system)
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS & BACKWARD COMPATIBILITY
# ════════════════════════════════════════════════════════════════════════════


# Backward compatibility aliases

# Backward compatibility function aliases


__all__ = [
    "UltraFastRAG", "PersonaContext", "AgentPersonaFactory",
    "get_persona_factory", "normalize_sources",
    "PERSONA_TEMPLATES", "ROLE_PERSONA_MAP",
]
