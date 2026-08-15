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
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import re

import numpy as np
import requests

from src.core.config import settings
from src.core.i18n import I18N
from src.core.logger import get_logger
from src.services.pg_store import (
    get_knowledge_docs,
)

log = get_logger(__name__)


def _dogfood_to_rageval(query: str, answer: str, contexts: List[str], persona: str,
                         model: str, tokens_used: int, latency_ms: float) -> None:
    """Fire-and-forget: score this live chat interaction via a RAGeval-compatible
    evaluation service, if one is configured. Same generic HTTP contract as
    scripts/evaluate_with_rageval.py (POST {url}/eval/log with
    {query,answer,contexts,persona,model,tokens_used,latency_ms}) — RAG_EVALUATOR_URL
    has no default, so this is a no-op unless the deployer points it at a real service;
    it is never hardcoded to a specific evaluator's name or URL. Runs on a background
    thread so a slow or unreachable evaluator never adds latency to the chat response.
    """
    url = os.environ.get("RAG_EVALUATOR_URL", "").strip().rstrip("/")
    if not url:
        return
    token = os.environ.get("RAG_EVALUATOR_TOKEN", "").strip()

    def _send() -> None:
        try:
            headers = {"Content-Type": "application/json"}
            if token:
                # Sent under both names — see scripts/evaluate_with_rageval.py for why:
                # generic `Authorization: Bearer` for any compatible evaluator, plus
                # `X-OmniIntel-Internal-Token` because the upstream RAGeval project's own
                # internal-token gate (REQUIRE_INTERNAL_TOKEN=true by default) only checks
                # that header — without it, this call 403s silently against a real RAGeval
                # deployment even with a correct RAG_EVALUATOR_TOKEN.
                headers["Authorization"] = f"Bearer {token}"
                headers["X-OmniIntel-Internal-Token"] = token
            requests.post(
                f"{url}/eval/log",
                json={"query": query, "answer": answer, "contexts": contexts,
                      "persona": persona, "model": model,
                      "tokens_used": tokens_used, "latency_ms": latency_ms},
                headers=headers, timeout=5,
            )
        except Exception as e:
            log.warning("RAGeval dogfood log failed (non-fatal): %s", e)

    threading.Thread(target=_send, daemon=True).start()

# ════════════════════════════════════════════════════════════════════════════
# LAZY-LOADED DEPENDENCIES
# ════════════════════════════════════════════════════════════════════════════

_GROQ = False
_SBERT = False
_TFIDF = False

try:
    from groq import Groq  # type: ignore
    _GROQ = True
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer
    _SBERT = True
except Exception:
    import logging; logging.error('Unhandled exception', exc_info=True)
    pass

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _TFIDF = True
except ImportError:
    pass


# ════════════════════════════════════════════════════════════════════════════
# PROVIDER-AGNOSTIC LLM COMPLETION
# ════════════════════════════════════════════════════════════════════════════

_GROQ_CLIENT = None


def _groq_client():
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None and _GROQ and settings.GROQ_API_KEY:
        _GROQ_CLIENT = Groq(api_key=settings.GROQ_API_KEY)
    return _GROQ_CLIENT


def llm_available() -> bool:
    """Whether the configured provider can serve a completion: the Groq SDK for
    LLM_PROVIDER=groq, otherwise LiteLLM (which reaches Anthropic/OpenAI/Ollama/…)."""
    if (settings.LLM_PROVIDER or "groq").lower() == "groq":
        return _groq_client() is not None
    try:
        import importlib.util
        return importlib.util.find_spec("litellm") is not None
    except ImportError:
        return False


def llm_complete(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 1024,
    top_p: Optional[float] = None,
    model: Optional[str] = None,
    persona_name: Optional[str] = None,
) -> Tuple[str, int, str]:
    """Provider-agnostic chat completion → (text, tokens_used, resolved_model).

    Uses llm_router to resolve the correct model (Claude vs Groq) based on persona tier.
    Groq models use the native SDK for maximum speed; others route via LiteLLM. The
    resolved model string is returned too so callers (e.g. RAGeval dogfood logging)
    can attribute cost/quality to the model that actually served the request.
    """
    from src.services.llm_router import _resolve, PERSONA_TIER_MAP, _apply_cache_control

    tier = "default"
    if persona_name and persona_name.lower() in PERSONA_TIER_MAP:
        tier = PERSONA_TIER_MAP[persona_name.lower()]

    resolved_model = model or _resolve(tier)
    # Neither the Groq SDK nor LiteLLM bound this by default — a provider having
    # connectivity trouble hung the whole chat request (confirmed live: >2 min on a
    # single message) with nothing in this codebase to cut it short.
    timeout_s = float(os.getenv("LLM_TIMEOUT", "30"))

    # Fast path: use native Groq SDK if resolved model is a Groq model
    client = _groq_client()
    if resolved_model.startswith("groq/") and client is not None:
        actual_model = resolved_model.replace("groq/", "")
        kw: Dict[str, Any] = {"model": actual_model, "messages": messages,
                              "temperature": temperature, "max_tokens": max_tokens,
                              "timeout": timeout_s}
        if top_p is not None:
            kw["top_p"] = top_p
        r = client.chat.completions.create(**kw)
        tokens = getattr(r.usage, "total_tokens", 0) if getattr(r, "usage", None) else 0
        return r.choices[0].message.content, tokens, resolved_model

    # Any other provider → LiteLLM
    from litellm import completion  # type: ignore
    msgs = _apply_cache_control(messages, resolved_model)
    kw = {"model": resolved_model, "messages": msgs, "temperature": temperature,
          "max_tokens": max_tokens, "timeout": timeout_s}
    # Anthropic rejects a request that sets both temperature and top_p ("cannot both be
    # specified for this model") — every other provider here accepts both, so this is
    # scoped to Anthropic specifically rather than dropping top_p for everyone.
    if top_p is not None and not resolved_model.startswith("anthropic/"):
        kw["top_p"] = top_p
    r = completion(**kw)
    text = r.choices[0].message.content
    usage = getattr(r, "usage", None)
    tokens = getattr(usage, "total_tokens", 0) if usage else 0
    return text, tokens, resolved_model


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
                            except Exception:
                                doc_embeddings.append(np.zeros_like(query_embedding))
                        else:
                            doc_embeddings.append(np.zeros_like(query_embedding))
                    
                    if doc_embeddings:
                        doc_embeddings = np.array(doc_embeddings)
                        similarities = cosine_similarity(
                            np.array([query_embedding]),  # type: ignore
                            doc_embeddings                # type: ignore
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
            
            # Fallback to TF-IDF.
            # max_features was 100, which capped the vocabulary at the 100 most frequent
            # corpus terms — measured on the real 733-doc knowledge base, "runway" was not
            # among them, so "What is our cash runway in months?" scored 0.0000 against
            # EVERY document and this path returned nothing. With a realistic vocabulary the
            # same query scores 0.63 and matches 26 documents. Also index title+content:
            # titles carry the metric name ("Glossary: Cash Runway") and were being ignored.
            if _TFIDF:
                try:
                    corpus = (docs["title"].fillna("") + ". " + docs["title"].fillna("")
                              + ". " + docs["content"].fillna(""))
                    vectorizer = TfidfVectorizer(
                        max_features=50000, stop_words="english", sublinear_tf=True,
                        ngram_range=(1, 2),
                    )
                    doc_vectors = vectorizer.fit_transform(corpus)
                    query_vector = vectorizer.transform([query])
                    similarities = cosine_similarity(query_vector, doc_vectors)[0]

                    top_indices = np.argsort(similarities)[::-1][:top_k]
                    results = []
                    for idx in top_indices:
                        if similarities[idx] > 0.05:
                            results.append((
                                docs.iloc[idx]["title"],
                                docs.iloc[idx]["content"],
                                float(similarities[idx]),
                            ))
                    # Only return if something actually matched — an empty list here used to
                    # be returned as the final answer, skipping the keyword fallback below.
                    if results:
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
        if not llm_available():
            return {
                "query": query,
                "response": "RAG unavailable (no LLM provider configured)",
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

        # Generate response (provider-agnostic — LLM_PROVIDER selects Groq/LiteLLM)
        try:
            answer, _, _ = llm_complete(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=1024,
                temperature=0.4,
            )
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "Use bullet points. Quantify everything. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Always reference the data behind conclusions. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Analyze burn rate vs. engineering output. Evaluate build-vs-buy decisions. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Track cycle times, throughput, resource utilization. Identify bottlenecks. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Balance people metrics with business outcomes. Recommend retention improvements. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Analyze carbon footprint, diversity indices, safety records. Help prepare ESG reports. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Proactively flag issues and recommend mitigation strategies. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Be thorough, data-driven, communicate with supporting evidence. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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
            "Adapt communication to user needs. Be helpful, accurate, proactive. "
            "Ground every statement in the provided data and cite it; when you do recommend, tie it to a specific figure."
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

# The 7 business domains personas are scoped to (lowercased). Mirrors the ``data_access``
# values in PERSONA_TEMPLATES — used to enforce RBAC on retrieved knowledge docs.
_KPI_DOMAINS = {"finance", "growth", "operations", "people", "esg", "it", "logistics"}


def _doc_domain(title: str) -> Optional[str]:
    """Return the business domain a *company* KPI doc belongs to, or None for
    domain-agnostic docs (glossary definitions, untagged knowledge). Recognises the two
    title shapes the KPI docs use — ``"Headcount (People) — 2026-12"`` and
    ``"People KPI Summary — 2026-12"`` — so retrieval can be scoped to a persona's
    ``data_access`` the same way the live KPI snapshot is."""
    t = (title or "").lower()
    m = re.search(r"\(([a-z& ]+)\)", t)  # "... (People)"
    if m and m.group(1).strip() in _KPI_DOMAINS:
        return m.group(1).strip()
    for d in _KPI_DOMAINS:  # "People KPI Summary ...", "Finance KPI Summary ..."
        if t.startswith(d + " kpi") or t.startswith(d + " summary"):
            return d
    return None


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
# REAL-TIME WEB SEARCH (Tavily) — augments RAG with trustworthy, citable web sources
# ════════════════════════════════════════════════════════════════════════════

def tavily_search(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Real-time web search via Tavily. Returns trustworthy results with URLs so the
    copilot can cite the live web. Stdlib-only (urllib); returns [] when no key is set
    or on any error, so the chat path degrades gracefully to internal RAG."""
    key = getattr(settings, "TAVILY_API_KEY", "")
    if not key or not query or not query.strip():
        return []
    import urllib.request as _u
    payload = json.dumps({
        "api_key": key,
        "query": query.strip()[:400],
        "max_results": max(1, min(int(max_results or 4), 8)),
        "search_depth": "basic",
        "include_answer": False,
    }).encode()
    try:
        req = _u.Request("https://api.tavily.com/search", data=payload,
                         headers={"Content-Type": "application/json"}, method="POST")
        with _u.urlopen(req, timeout=9) as r:
            data = json.loads(r.read())
        out: List[Dict[str, Any]] = []
        for it in (data.get("results") or []):
            url = (it.get("url") or "").strip()
            if not url:
                continue
            out.append({
                "title": (it.get("title") or url).strip()[:140],
                "url": url,
                "content": (it.get("content") or "").strip()[:600],
                "score": float(it.get("score", 0) or 0),
            })
        return out
    except Exception as e:  # network/key/quota — never break the chat
        log.warning("Tavily web search failed: %s", e)
        return []


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

        # NOTE: language is enforced centrally in chat() so the reply mirrors the
        # language of the user's actual question — this lets a user switch from
        # English to French (or back) mid-conversation and get answered correctly.

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

        # 1) Live KPI snapshot (latest period), scoped to the persona's domains (RBAC).
        # PLUS: a question naming a specific past period ("... in 2024-01?", "for 2021-01")
        # asks about a period that is, by definition, almost never the latest one — the
        # snapshot alone can never ground those, no matter how good retrieval otherwise
        # is. Detect a YYYY-MM in the message and fetch that period's rows too.
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
                    # snippet carries the real values, not just "X metrics for Y" — a
                    # citation chip that only names the category+period gives a reader
                    # (or an eval judge checking groundedness) nothing to actually verify
                    # the cited number against.
                    raw_sources.append({
                        "title": f"Live KPI snapshot · {latest}", "type": "kpi", "relevance": 1.0,
                        "snippet": kpi_block[:400], "source": f"kpi/{latest}",
                    })

                asked_periods = set(re.findall(r"\b(?:19|20)\d{2}-(?:0[1-9]|1[0-2])\b", message))
                asked_periods.discard(latest)
                if asked_periods:
                    hist = df[df["period"].isin(asked_periods)]
                    if scope:
                        hist = hist[hist["category"].str.lower().isin(scope)]
                    hist_lines = []
                    for period in sorted(asked_periods & set(hist["period"].unique())):
                        pdf = hist[hist["period"] == period]
                        for cat in sorted(pdf["category"].unique()):
                            cdf = pdf[pdf["category"] == cat]
                            metrics = "; ".join(
                                f"{r.metric}={r.value}{(' ' + r.unit) if getattr(r, 'unit', '') else ''}"
                                for r in cdf.itertuples()
                            )
                            hist_lines.append(f"- {cat} ({period}): {metrics}")
                    if hist_lines:
                        hist_block = "\n".join(hist_lines)
                        parts_period = ", ".join(sorted(asked_periods & set(hist["period"].unique())))
                        raw_sources.append({
                            "title": f"Historical KPI data · {parts_period}", "type": "kpi", "relevance": 1.0,
                            "snippet": hist_block[:400], "source": f"kpi/{parts_period}",
                        })
                        kpi_block = (kpi_block + "\n\n" + hist_block) if kpi_block else hist_block
        except Exception as e:
            log.warning("KPI context retrieval failed: %s", e)

        # 2) Relevant knowledge docs (hybrid / GraphRAG-lite / vector) — RBAC-scoped.
        # The live KPI snapshot above is filtered to the persona's data_access; the doc
        # retrieval must be too, or a CFO could read People/HR figures via the knowledge
        # base (e.g. "Headcount (People)", "People KPI Summary"). Drop any *company* KPI
        # doc whose domain is outside scope. Domain-agnostic docs (glossary definitions,
        # untagged docs) are kept — they carry no scoped company data.
        try:
            docs = _get_shared_rag()._retrieve_documents(message, top_k=6, language=language)
            for title, content, score in (docs or []):
                dom = _doc_domain(title)
                if scope and dom and dom not in scope:
                    continue  # out-of-scope company data — persona RBAC
                doc_blocks.append((title, content))
                raw_sources.append({
                    "title": title,
                    "type": "glossary" if title.lower().startswith("glossary") else "knowledge",
                    "relevance": round(score, 3),
                    "snippet": content[:240],
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

    @staticmethod
    def _detect_language(text: str) -> str:
        """Best-effort FR/EN detection for a single message so the reply mirrors the
        language the user actually wrote in — even when they switch mid-conversation."""
        t = (text or "").lower().strip()
        if not t:
            return "en"
        # Accented characters are a strong French signal.
        if any(c in t for c in "àâçéèêëîïôûùüœ"):
            return "fr"
        pad = f" {t} "
        fr_markers = (" le ", " la ", " les ", " des ", " une ", " un ", " est ", " sont ",
                      " quel ", " quelle ", " pourquoi ", " comment ", " combien ", " nos ",
                      " notre ", " pour ", " avec ", " sur ", " dans ", "bonjour", "merci",
                      " ce ", " cette ", " qui ", " que ", "résum", "prévis", "donne", " plan ")
        en_markers = (" the ", " is ", " are ", " what ", " why ", " how ", " our ", " show ",
                      " give ", " which ", " and ", " for ", " with ", "hello", " hi ", "please",
                      "summar", "forecast", "revenue", " should ", " can ")
        fr = sum(1 for m in fr_markers if m in pad)
        en = sum(1 for m in en_markers if m in pad)
        return "fr" if fr > en else "en"

    @staticmethod
    def _is_smalltalk(text: str) -> bool:
        """Greeting / thanks / identity chit-chat that should NOT trigger a KPI dump."""
        t = (text or "").strip().lower().rstrip("!.?…")
        if not t:
            return True
        greetings = {
            "hi", "hey", "hello", "yo", "hiya", "sup", "gm", "good morning", "good afternoon",
            "good evening", "bonjour", "bonsoir", "salut", "coucou", "thanks", "thank you",
            "merci", "ok", "okay", "cool", "nice", "great", "who are you", "what can you do",
            "help", "aide", "qui es-tu", "que peux-tu faire", "how are you", "ça va", "ca va",
        }
        if t in greetings:
            return True
        # very short openers like "hi there", "hello!" with no data keywords
        if len(t.split()) <= 3 and any(t.startswith(g) for g in ("hi", "hey", "hello", "bonjour", "salut", "thanks", "merci")):
            return True
        return False

    @staticmethod
    def _needs_web(text: str, context: str = "") -> bool:
        """True when a question calls for external / real-time / benchmark information that the
        internal KPI snapshot + knowledge base cannot answer on their own. Uses LLM for intelligent judgment."""
        t = (text or "").lower()
        if not t.strip():
            return False
        
        from src.core.config import settings
        prompt = (
            "You are a routing agent for a corporate AI copilot. The user asked: {query}\n"
            "The internal knowledge base returned the following data:\n---\n{context}\n---\n"
            "Does the query ask for external market data, news, competitor intel, or current events that are NOT adequately answered by the internal data above? "
            "Consider the lack of data if the query asks about real-time events. "
            "Reply with exactly one word: YES or NO."
        ).format(query=t, context=(context or "No internal data found.")[:2000])
        
        try:
            reply, _, _ = llm_complete(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.0,
                model=getattr(settings, "LLM_JUDGE", getattr(settings, "LLM_MODEL", "groq/llama-3.3-70b-versatile"))
            )
            if "yes" in reply.lower():
                return True
            if "no" in reply.lower():
                return False
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("LLM Judge failed for _needs_web: %s", e)

        # Fallback to smart triggers if LLM is down
        triggers = (
            "benchmark", "industry", "market", "competitor", "competition", "peer", " vs ",
            "versus", "news", "latest", "regulation", "gdpr", "csrd", "sec filing", "best practice",
            "macro", "inflation", "interest rate", "industry standard", "industry average",
            "external", "compare to other", "how do other", "current events", "what's happening",
            "actualité", "marché", "concurrent", "réglementation", "secteur", "meilleures pratiques",
            "tendance du marché", "moyenne du secteur",
        )
        return any(x in t for x in triggers)

    def _web_context(self, query: str, max_results: int, start_id: int):
        """Fetch real-time web results and format them as citable context blocks.
        Returns (block_text, web_sources) with ids continuing after the internal sources."""
        results = tavily_search(query, max_results)
        if not results:
            return "", []
        parts, sources = [], []
        for i, r in enumerate(results, start=start_id + 1):
            parts.append(f"[{i}] (WEB) {r['title']} — {r['url']}: {r['content']}")
            rel = round(min(max(r.get("score", 0.0), 0.0), 1.0), 3)
            sources.append({
                "id": i, "title": r["title"], "type": "web", "url": r["url"],
                "relevance": rel or None, "snippet": r["content"][:240],
            })
        header = ("=== WEB RESULTS (real-time; cite by [n]; prefer recent, trustworthy sources) ===")
        return header + "\n" + "\n".join(parts), sources

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
        # Answer in the language of the CURRENT message (users may switch mid-chat).
        # The detected language drives retrieval + any fallback text; the LLM is also
        # instructed (system prompt) to mirror the question language in its reply.
        detected = self._detect_language(message)
        if detected:
            language = detected
        elif not language or language == "auto":
            language = "en"
        
        if not llm_available():
            return {
                "response": "AI agent unavailable (missing API key)." if language != "fr" else "Agent IA non disponible (clé API manquante).",
                "persona_used": "none",
                "tokens_used": 0,
                "latency_ms": 0,
            }

        persona = self.resolve_persona(user_role, persona_override, language)
        start = time.time()

        # ── Persona-routed RAG: auto-retrieve grounded data + sources ──
        # Skip retrieval for greetings / small talk so the copilot answers briefly
        # instead of dumping a KPI analysis at someone who just said "hi".
        if self._is_smalltalk(message):
            retrieved_ctx, sources = "", []
        else:
            retrieved_ctx, sources = self._retrieve_context(message, persona, language)
            # Augment with real-time web search (Tavily) when the question needs external,
            # current or benchmark data — web results are cited by [n] like any other source.
            if self._needs_web(message, retrieved_ctx):
                max_id = max((s.get("id", 0) for s in sources), default=0)
                web_ctx, web_sources = self._web_context(message, settings.WEB_SEARCH_MAX_RESULTS, max_id)
                if web_ctx:
                    retrieved_ctx = (retrieved_ctx + "\n\n" + web_ctx).strip() if retrieved_ctx else web_ctx
                    sources = sources + web_sources
        full_context = "\n\n".join(c for c in [context, retrieved_ctx] if c).strip()

        # Prompt-cache friendly layout: the system message (persona prompt + fixed
        # grounding instruction) is IDENTICAL for every request with the same persona,
        # so it forms a long stable prefix that Groq auto-caches at 50% (and that Anthropic
        # caches via cache_control). The volatile live data + question go LAST, in the user
        # turn, so they never invalidate the cached prefix.
        system_prompt = (
            persona.system_prompt + "\n\n"
            "STEP 1 — CLASSIFY THE USER'S INTENT before answering, and size your reply to it:\n"
            "* GREETING / SMALL TALK / META (e.g. 'hi', 'hello', 'bonjour', 'thanks', 'who are you', "
            "'what can you do') -> reply in ONE or TWO short friendly sentences and briefly say what you "
            "can help with. Do NOT list metrics, do NOT analyze data, do NOT produce a plan. Stop there.\n"
            "* SIMPLE DATA LOOKUP (e.g. 'what is our revenue?') -> give the specific number(s) in 1–3 "
            "sentences with citations. No roadmap, no action plan.\n"
            "* ADVICE / 'what should I do' -> a short, specific recommendation tied to a figure; add a "
            "brief action plan only if it genuinely helps.\n"
            "* EXPLICIT PLAN / STRATEGY / 'give me a plan / roadmap / step-by-step' -> a tailored, "
            "prioritized action plan grounded in the data (each step: what to do, which figure justifies "
            "it, expected impact).\n"
            "Only include an action plan when the user actually asked for one. Never pad with generic advice.\n"
            "* CAUSE ANALYSIS & FALLBACK: If asked WHY an anomaly or event occurred, you MUST ONLY state the root causes explicitly found in the internal data.\n"
            "If the internal data lacks the cause:\n"
            "  1) State clearly: 'The root cause is not present in the current knowledge base.'\n"
            "  2) Instruct the user on what data they should provide or upload (e.g., 'Please upload recent incident post-mortems, QA reports, or market analyses to the Data Hub.').\n"
            "  3) Use the provided WEB RESULTS (if available) to offer an industry-standard benchmark or similar known case to help them make an informed decision (e.g., 'In similar industry cases, this is handled by...'). ALWAYS cite the web sources using [n]. Do NOT generate hypothetical generic reasons.\n\n"
            "STEP 2 — WHEN (and only when) the user asks about the business or its data, use the LIVE DATA "
            "block below directly: quote the metric values, mirroring the exact currency and number format "
            "shown (e.g. '$3.6M', '3,6 M€', '3,6 Md FCFA' — never convert currencies), and CITE sources "
            "inline with the bracketed numbers shown, e.g. 'Revenue is 3.6M [1]'. Only use citation numbers "
            "that appear in the data block; never invent one. Stay STRICTLY within your data-access scope: "
            "answer only from the domains you own. If the user asks for figures outside your scope (another "
            "executive's area — e.g. a CFO asked for headcount/attrition, or a CHRO asked for revenue/cash), "
            "do NOT guess or fabricate: say in one short sentence that it's outside your remit and point to the "
            "role that owns it (e.g. 'that's the CHRO's domain'). If a figure genuinely is missing, say so in "
            "one short sentence. Never ask the user to supply data that is already provided.\n\n"
            "WEB RESULTS: if a '=== WEB RESULTS ===' block is present, use it for external / current / "
            "benchmark facts, prefer recent and trustworthy sources, and CITE each web fact by its [n] "
            "(same bracket scheme). Never state a web claim without its citation.\n\n"
            "FORMAT: clean, well-structured markdown — real bullets with '- ', bold with **, no stray or "
            "unmatched symbols. Keep it as short as the intent allows.\n\n"
            f"LANGUAGE (critical): the user's current message is written in "
            f"{'FRENCH' if language == 'fr' else 'ENGLISH'}. Write your ENTIRE reply in "
            f"{'FRENCH' if language == 'fr' else 'ENGLISH'} — this is decided per message and overrides "
            "the language of earlier turns."
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
            reply, tokens, resolved_model = llm_complete(
                messages=messages,
                max_tokens=2048,
                temperature=persona.temperature,
                top_p=0.9,
                persona_name=persona.name,
            )
            latency = int((time.time() - start) * 1000)

            _dogfood_to_rageval(
                query=message, answer=reply,
                contexts=[f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}" for s in sources],
                persona=persona.name, model=resolved_model,
                tokens_used=tokens, latency_ms=latency,
            )

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
                "latency_ms": (time.time() - start) * 1000,
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
