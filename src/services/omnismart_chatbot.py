"""
🚀 OmniSmart Chatbot Service — Unified Intelligence Operating System

Merges advanced_chatbot.py and unified_chatbot.py with full LangChain integration.
Implements all 5 Groq patterns + lightweight conversational agent + full-featured RAG.

Features:
- Multi-step autonomous agents (complex problem solving)
- Ultra-fast RAG with knowledge base integration
- Real-time data flow analysis (anomalies, sentiment)
- Natural voice interface (speech-to-text, text-to-speech)
- Structured data extraction (invoices, contracts, forms)
- Lightweight bilingual conversational AI (memory-efficient, multi-domain)
- Full LangChain integration for enhanced capabilities
- Dynamic knowledge base querying
- Domain-aware personalization
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
import requests

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
_LANGCHAIN = False
_PDF = False
_DOCX = False
_SBERT = False
_TFIDF = False
_TAVILY = False
_GTTS = False

try:
    from groq import Groq
    _GROQ = True
except ImportError:
    pass

try:
    from langchain_groq import ChatGroq
    from langchain.chains import RetrievalQA, ConversationChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
    from langchain.vectorstores import Chroma
    from langchain.embeddings import SentenceTransformerEmbeddings
    from langchain.memory import ConversationBufferWindowMemory
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain.agents import initialize_agent, AgentType, Tool
    _LANGCHAIN = True
except ImportError:
    pass

try:
    from PyPDF2 import PdfReader
    _PDF = True
except ImportError:
    pass

try:
    from docx import Document as DocxDocument
    _DOCX = True
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

try:
    from tavily import TavilyClient
    _TAVILY = True
except ImportError:
    pass

try:
    from gtts import gTTS
    _GTTS = True
except ImportError:
    pass


# ════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def _chunk_text(text: str, size: int = 512, overlap: int = 128) -> List[str]:
    """Split text into overlapping chunks for processing."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else end
    return [c for c in chunks if c]


def parse_pdf(content: BytesIO) -> str:
    """Extract text from PDF file."""
    if not _PDF:
        return "[PDF parsing unavailable — install PyPDF2]"
    try:
        text = ""
        for page in PdfReader(content).pages:
            text += (page.extract_text() or "") + "\n"
        return text.strip()
    except Exception as exc:
        log.error("PDF parse error: %s", exc)
        return f"[PDF error: {str(exc)[:100]}]"


def parse_docx(content: BytesIO) -> str:
    """Extract text from DOCX file."""
    if not _DOCX:
        return "[DOCX parsing unavailable — install python-docx]"
    try:
        text = "\n".join(p.text for p in DocxDocument(content).paragraphs)
        return text.strip()
    except Exception as exc:
        log.error("DOCX parse error: %s", exc)
        return f"[DOCX error: {str(exc)[:100]}]"


def ingest_document(
    title: str,
    content: str,
    source: str = "upload",
    doc_type: str = "general",
    language: str = "en",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Ingest document into knowledge base with semantic embeddings.
    
    Args:
        title: Document title
        content: Document text content
        source: Origin (upload, email, drive, etc.)
        doc_type: Type (invoice, contract, report, email, etc.)
        language: Language code (en, fr, etc.)
        metadata: Additional metadata dict
    
    Returns:
        Dict with ingestion stats
    """
    try:
        chunks = _chunk_text(content)
        embeddings = None
        
        # Generate embeddings if SBERT available
        if _SBERT:
            try:
                model = SentenceTransformer(settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2")
                embeddings = model.encode(chunks, show_progress_bar=False)
            except Exception as e:
                log.warning("Failed to generate embeddings: %s", e)
        
        records = []
        for i, chunk in enumerate(chunks):
            record = {
                "doc_id": str(uuid.uuid4()),
                "title": title,
                "chunk_index": i,
                "content": chunk,
                "source": source,
                "doc_type": doc_type,
                "language": language,
                "embedding": json.dumps(embeddings[i].tolist()) if embeddings is not None else None,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.utcnow().isoformat(),
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        store_knowledge_docs(df)
        
        log.info("Ingested %d chunks for '%s' (%s)", len(chunks), title, language)
        return {
            "success": True,
            "title": title,
            "chunks_count": len(chunks),
            "source": source,
            "doc_type": doc_type,
        }
    except Exception as e:
        log.error("Document ingestion error: %s", e)
        return {
            "success": False,
            "error": str(e)[:200],
        }


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search web using Tavily if available."""
    if not _TAVILY or not settings.TAVILY_API_KEY:
        return []
    
    try:
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(query, max_results=max_results, include_answer=True)
        
        results = []
        if response.get("answer"):
            results.append({
                "source": "Tavily Summary",
                "content": response["answer"],
                "url": None,
            })
        
        for result in response.get("results", []):
            results.append({
                "source": result.get("title", "Unknown"),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
            })
        
        return results
    except Exception as e:
        log.error("Web search error: %s", e)
        return []


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 1: MULTI-STEP AUTONOMOUS AGENTS
# ════════════════════════════════════════════════════════════════════════════

class MultiStepAgent:
    """Execute complex tasks through reasoning → action → synthesis."""

    def __init__(self, system_instruction: Optional[str] = None):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.memory: List[Dict[str, str]] = []
        self.system_instruction = system_instruction or (
            "You are an intelligent enterprise analyst. Think step-by-step about complex problems, "
            "identify data needed, perform analyses, and synthesize comprehensive insights."
        )

    def _think(self, query: str, context: str = "") -> str:
        """Step 1: Reasoning."""
        if not self.client:
            return "Agent unavailable"
        
        prompt = f"""Given the query and context, think step-by-step about the best approach.
Identify what data you need and what analyses to perform.

Query: {query}
Context: {context}

Brief reasoning plan (2-3 sentences):"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            log.error("Think step error: %s", e)
            return ""

    def _act(self, query: str, reasoning: str, tools: List[str]) -> Dict[str, Any]:
        """Step 2: Action."""
        if not self.client:
            return {}
        
        tools_str = ", ".join(tools)
        prompt = f"""Based on this reasoning, which tools should we use?

Query: {query}
Reasoning: {reasoning}
Available Tools: {tools_str}

For each step, specify the tool, query, and expected outcome. Format as JSON."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {"actions": response.choices[0].message.content}
        except Exception as e:
            log.error("Act step error: %s", e)
            return {}

    def _synthesize(self, query: str, reasoning: str, action_results: Dict[str, Any]) -> str:
        """Step 3: Synthesis."""
        if not self.client:
            return ""
        
        results_json = json.dumps(action_results, indent=2)
        prompt = f"""Based on the reasoning and results, generate a comprehensive response.

Query: {query}
Reasoning: {reasoning}
Results:
{results_json}

Provide key findings, insights, recommendations, and next steps."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.5,
            )
            return response.choices[0].message.content
        except Exception as e:
            log.error("Synthesize step error: %s", e)
            return ""

    def execute(
        self,
        query: str,
        context: str = "",
        tools: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute multi-step workflow."""
        if tools is None:
            tools = ["data_retrieval", "analysis", "forecasting", "simulation"]
        
        reasoning = self._think(query, context)
        action_results = self._act(query, reasoning, tools)
        final_response = self._synthesize(query, reasoning, action_results)
        
        return {
            "query": query,
            "reasoning": reasoning,
            "actions": action_results,
            "response": final_response,
            "type": "multi_step_agent",
            "timestamp": datetime.utcnow().isoformat(),
        }


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
    ) -> str:
        """Build prompt with retrieved context."""
        doc_context = "\n\n".join(
            f"📄 **{title}** (relevance: {sim:.1%})\n{content[:300]}..."
            for title, content, sim in documents
        )
        
        lang_instruction = (
            "Répondez en français."
            if I18N.lang() == "fr"
            else "Reply in English."
        )
        
        return f"""{lang_instruction}

RETRIEVED CONTEXT FROM KNOWLEDGE BASE:
{doc_context if doc_context else "(No relevant documents found)"}

USER QUERY: {query}

Based on the context above, provide a comprehensive, accurate answer. 
Cite sources where relevant. If information is incomplete, state what additional data would help."""

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

        # Build prompt
        prompt = self._build_rag_prompt(query, documents)
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
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

class RealTimeAnalyzer:
    """Process streaming data for anomalies, patterns, and alerts."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.anomaly_threshold = 0.7
        self.alert_queue: List[Dict[str, Any]] = []

    def _detect_anomalies(self, data_stream: str) -> List[Dict[str, Any]]:
        """Detect anomalies in data."""
        if not self.client:
            return []
        
        prompt = f"""Analyze the following data stream for anomalies, unusual patterns, or concerning trends.
For each anomaly found, explain:
1. What is anomalous
2. Severity (1-10)
3. Potential impact
4. Recommended action

Data:
{data_stream}

Format response as JSON array of anomalies."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return []
        except Exception as e:
            log.error("Anomaly detection error: %s", e)
            return []

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotional tone."""
        if not self.client:
            return {}
        
        prompt = f"""Analyze the sentiment and tone of this text. Provide:
1. Overall sentiment (positive/negative/neutral)
2. Confidence (0-1)
3. Key emotional indicators
4. Tone (professional/casual/urgent/etc.)

Text: {text}

Format as JSON."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.2,
            )
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            log.error("Sentiment analysis error: %s", e)
            return {}

    def process_stream(self, data_stream: str) -> Dict[str, Any]:
        """Process streaming data for anomalies and insights."""
        anomalies = self._detect_anomalies(data_stream)
        sentiment = self._analyze_sentiment(data_stream)
        
        result = {
            "anomalies": [
                a for a in anomalies
                if a.get("severity", 5) >= self.anomaly_threshold * 10
            ],
            "sentiment": sentiment,
            "alert_count": len([
                a for a in anomalies
                if a.get("severity", 5) >= 7
            ]),
            "type": "real_time_analysis",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return result


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 4: NATURAL VOICE CHATBOT
# ════════════════════════════════════════════════════════════════════════════

class VoiceChatbot:
    """Conversational interface with speech-to-text and text-to-speech."""

    def __init__(self, system_instruction: Optional[str] = None):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.conversation_history: List[Dict[str, str]] = []
        default_prompt = (
            "You are a friendly, intelligent assistant. "
            "Respond naturally, conversationally, and helpfully."
        )
        self.system_prompt = system_instruction or default_prompt

    def transcribe(self, audio_file_path: str) -> str:
        """Convert speech to text using Groq Whisper."""
        if not self.client:
            return ""
        
        try:
            with open(audio_file_path, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    file=(audio_file_path, f, "audio/wav"),
                    model="whisper-large-v3",
                )
            return transcript.text
        except Exception as e:
            log.error("Transcription error: %s", e)
            return ""

    def chat(self, user_message: str) -> str:
        """Generate conversational response."""
        if not self.client:
            return "Chatbot unavailable (Groq not configured)"
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ] + self.conversation_history[-10:]
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.9,
            )
            
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message,
            })
            
            return assistant_message
        except Exception as e:
            log.error("Chat error: %s", e)
            return f"Error: {str(e)[:100]}"

    def generate_audio(self, text: str, output_path: str = "/tmp/response.mp3") -> Optional[str]:
        """Convert text to speech using gTTS."""
        if not _GTTS or not text or len(text) > 2000:
            return None
        
        try:
            lang = "fr" if I18N.lang() == "fr" else "en"
            tts = gTTS(text, lang=lang, slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            log.error("Text-to-speech error: %s", e)
            return None

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 5: STRUCTURED DATA EXTRACTION
# ════════════════════════════════════════════════════════════════════════════

class StructuredExtractor:
    """Extract structured JSON data from unstructured text."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None

    def _define_schema(self, extraction_type: str) -> Dict[str, Any]:
        """Define extraction schema."""
        schemas = {
            "invoice": {
                "invoice_number": "string",
                "date": "string (YYYY-MM-DD)",
                "vendor": "string",
                "items": [{
                    "description": "string",
                    "quantity": "number",
                    "unit_price": "number",
                    "total": "number",
                }],
                "subtotal": "number",
                "tax": "number",
                "total_amount": "number",
                "currency": "string",
            },
            "contract": {
                "parties": ["string"],
                "start_date": "string",
                "end_date": "string",
                "key_terms": ["string"],
                "obligations": ["string"],
            },
            "report": {
                "title": "string",
                "date": "string",
                "sections": [{
                    "heading": "string",
                    "content": "string",
                }],
                "key_findings": ["string"],
                "recommendations": ["string"],
            },
        }
        return schemas.get(extraction_type, {})

    def extract(self, text: str, schema_type: str = "invoice") -> Dict[str, Any]:
        """Extract structured data from text."""
        if not self.client:
            return {"error": "Extractor unavailable"}
        
        schema = self._define_schema(schema_type)
        schema_json = json.dumps(schema, indent=2)
        
        prompt = f"""Extract structured data from the text and return ONLY valid JSON.
Follow the schema exactly. Use null for missing fields.

SCHEMA:
{schema_json}

TEXT:
{text}

EXTRACTED JSON:"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.1,
            )
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {"raw": response.choices[0].message.content}
        except Exception as e:
            log.error("Extraction error: %s", e)
            return {"error": str(e)[:200]}


# ════════════════════════════════════════════════════════════════════════════
# LIGHTWEIGHT CONVERSATIONAL AGENT (Bilingual, Multi-Domain, Memory-Efficient)
# ════════════════════════════════════════════════════════════════════════════

class LightweightConversationalAgent:
    """
    Lightweight bilingual conversational agent with knowledge base integration.
    
    Features:
    - Multi-domain support (finance, hr, ops, esg, growth, general)
    - Bilingual (FR/EN) with auto-detection
    - Direct Groq API (no LangChain overhead)
    - Dynamic knowledge base querying
    - Conversation memory (last 10 exchanges)
    - Token-efficient context windowing
    """

    def __init__(
        self,
        session_id: str = "default",
        domain: str = "general",
        rag: Optional[UltraFastRAG] = None,
    ):
        self.session_id = session_id
        self.domain = domain
        self.conversation_history: List[Dict[str, str]] = []
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.rag = rag  # Optional RAG for knowledge base queries

    def _build_system_prompt(self) -> str:
        """Build domain-aware system prompt."""
        lang = "French" if I18N.lang() == "fr" else "English"
        
        domain_info = {
            "finance": "You specialize in financial analysis, KPI tracking, forecasting, and financial reporting.",
            "hr": "You specialize in human resources, talent management, compensation, and team dynamics.",
            "ops": "You specialize in operations, process optimization, efficiency, and logistics.",
            "esg": "You specialize in environmental, social, and governance metrics and sustainability.",
            "growth": "You specialize in growth metrics, market analysis, and customer acquisition.",
            "general": "You are a general-purpose assistant covering all business domains.",
        }
        
        prompt = f"""You are the OmniSmart Conversational Assistant.

LANGUAGE: {lang}
DOMAIN: {self.domain.upper()}
CAPABILITIES: {domain_info.get(self.domain, domain_info["general"])}

PERSONALITY:
- Professional and action-oriented
- Concise but thorough
- Proactive in offering insights
- Bilingual and culturally sensitive

CONVERSATION MEMORY (last 10 exchanges):
{self._format_history()}

INSTRUCTIONS:
- Be helpful and clear
- Reference data when available
- Offer to run analyses or generate reports when relevant
- Ask clarifying questions if needed
"""
        return prompt

    def _format_history(self) -> str:
        """Format recent conversation for context."""
        if not self.conversation_history:
            return "(No previous conversation)"
        
        recent = self.conversation_history[-10:]
        formatted = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:100] + ("..." if len(msg["content"]) > 100 else "")
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)

    def chat(
        self,
        user_input: str,
        context: str = "",
        use_knowledge_base: bool = True,
    ) -> str:
        """Chat with memory and optional knowledge base integration."""
        if not self.client:
            return (
                "Assistant non disponible."
                if I18N.lang() == "fr"
                else "Assistant unavailable."
            )
        
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
            })
            
            # Build system prompt
            system_prompt = self._build_system_prompt()
            
            # Query knowledge base if available
            kb_context = ""
            if use_knowledge_base and self.rag:
                try:
                    rag_result = self.rag.answer(
                        user_input,
                        top_k=3,
                        use_cache=True,
                        language=I18N.lang(),
                    )
                    if rag_result.get("sources"):
                        kb_context = "KNOWLEDGE BASE RESULTS:\n"
                        for source in rag_result["sources"]:
                            kb_context += f"- {source['title']}: {source['preview']}\n"
                        system_prompt += f"\n\n{kb_context}"
                except Exception as e:
                    log.warning("KB query failed: %s", e)
            
            # Add additional context if provided
            if context:
                system_prompt += f"\n\nADDITIONAL CONTEXT:\n{context}"
            
            # Generate response
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9,
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response,
            })
            
            # Keep history manageable (max 20 messages = 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_response
        
        except Exception as e:
            log.error("Conversational agent error: %s", e)
            return (
                f"Erreur: {str(e)[:100]}"
                if I18N.lang() == "fr"
                else f"Error: {str(e)[:100]}"
            )

    def set_domain(self, domain: str) -> None:
        """Switch domain dynamically."""
        self.domain = domain
        log.info("Agent domain switched to: %s", domain)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []


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
        self._db_personas: Dict[str, Dict] = {}
        self._load_db_personas()

    def _load_db_personas(self):
        """Load personas from database (if available)."""
        try:
            from src.core.pg_engine import get_sync_session
            from src.models.pg_models import AgentPersona
            session = get_sync_session()
            personas = session.query(AgentPersona).filter(AgentPersona.is_active == True).all()
            for p in personas:
                self._db_personas[p.name] = {
                    "display_name": p.display_name,
                    "system_prompt": p.system_prompt,
                    "allowed_tools": p.allowed_tools or [],
                    "data_access": p.data_access or [],
                    "temperature": p.temperature,
                    "max_tokens": p.max_tokens,
                }
            session.close()
            if self._db_personas:
                log.info("Loaded %d personas from database", len(self._db_personas))
        except Exception as e:
            log.info("Using in-memory persona templates (DB not available: %s)", str(e)[:60])

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

        # Build messages
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": persona.system_prompt},
            {"role": "system", "content": (
                "You have DIRECT access to the company's live data, provided below. Answer the "
                "user's question directly using these numbers — never ask the user to supply data "
                "or to pick a focus area when the data is already here. Be specific and quote the "
                "metric values. CITE your sources inline using the bracketed numbers shown in the "
                "context, e.g. 'Revenue is $3.6M [1]'. Only use citation numbers that appear below "
                "and never invent one. Only use data within your access scope; if a figure is "
                "genuinely missing, say so in one short sentence.\n\n"
                f"=== LIVE DATA (scope: {', '.join(persona.data_access) or 'all'}) ===\n"
                f"{full_context if full_context else '(no data retrieved)'}"
            )},
        ]

        # Add conversation history (last 10 messages)
        if history:
            for msg in history[-10:]:
                messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": message})

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

class OmniSmartChatbot:
    """
    Unified chatbot combining all 5 Groq patterns + lightweight conversational agent.
    
    Intelligently routes queries to the best pattern for each use case.
    """

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        domain: str = "general",
        username: Optional[str] = None,
        user_role: str = "general",
        persona_override: Optional[str] = None,
    ):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.domain = domain
        self.username = username or "anonymous"
        self.user_role = user_role
        
        # Resolve persona
        self.persona = self._resolve_persona(user_role, persona_override)
        
        # Initialize all patterns
        self.agent = MultiStepAgent(system_instruction=self.persona.add_language_instruction())
        self.rag = UltraFastRAG(system_instruction=self.persona.add_language_instruction())
        self.analyzer = RealTimeAnalyzer()
        self.voice = VoiceChatbot(system_instruction=self.persona.add_language_instruction())
        self.extractor = StructuredExtractor()
        self.conversational = LightweightConversationalAgent(
            session_id=self.conversation_id,
            domain=domain,
            rag=self.rag,
        )
        
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.message_count = 0
        
        log.info(
            "OmniSmartChatbot initialized: user=%s, role=%s, persona=%s, domain=%s",
            self.username, self.user_role, self.persona.name, self.domain
        )

    def _resolve_persona(self, user_role: str, persona_override: Optional[str] = None) -> PersonaContext:
        """Resolve persona from user role."""
        persona_name = persona_override or ROLE_PERSONA_MAP.get(user_role, "general")
        template = PERSONA_TEMPLATES.get(persona_name, PERSONA_TEMPLATES["general"])
        
        return PersonaContext(
            name=persona_name,
            display_name=template.get("display_name", persona_name.upper()),
            system_prompt=template.get("system_prompt", ""),
            allowed_tools=template.get("allowed_tools", []),
            data_access=template.get("data_access", []),
            temperature=template.get("temperature", 0.3),
            language=I18N.lang(),
        )

    def set_persona(self, persona_name: str) -> None:
        """Dynamically change persona."""
        self.persona = self._resolve_persona(self.user_role, persona_name)
        log.info("Chatbot persona switched to: %s for conversation %s", persona_name, self.conversation_id)

    def _detect_intent(self, message: str) -> str:
        """Detect intent to route to appropriate handler."""
        message_lower = message.lower()
        
        # Extraction intent
        if any(word in message_lower for word in [
            "extract", "parse", "invoice", "contract", "form", "data from"
        ]):
            return "extraction"
        
        # Analysis intent
        if any(word in message_lower for word in [
            "analyze", "anomaly", "alert", "detect", "trend", "pattern",
            "anomalies", "sentiment", "unusual", "concerning"
        ]):
            return "analysis"
        
        # Agent intent (complex, multi-step)
        if any(word in message_lower for word in [
            "optimize", "recommend", "forecast", "simulate", "strategy",
            "plan", "solve", "complex", "comprehensive"
        ]):
            return "agent"
        
        # RAG intent (knowledge base)
        if any(word in message_lower for word in [
            "document", "search", "knowledge", "find", "look up",
            "policy", "contract", "manual", "guide"
        ]):
            return "rag"
        
        # Voice intent
        if any(word in message_lower for word in [
            "audio", "speech", "transcribe", "voice", "listen"
        ]):
            return "voice"
        
        # Default to conversation
        return "conversation"

    def process(
        self,
        message: str,
        mode: str = "auto",
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Process message across all patterns.
        
        Modes:
        - auto: Automatically detect best pattern
        - agent: Multi-step autonomous agent
        - rag: Knowledge base retrieval
        - analysis: Real-time anomaly/sentiment analysis
        - extraction: Structured data extraction
        - conversation: Conversational response
        - voice: Voice/speech processing
        """
        self.message_count += 1
        
        # Auto-detect mode if requested
        if mode == "auto":
            mode = self._detect_intent(message)
        
        result = {
            "conversation_id": self.conversation_id,
            "domain": self.domain,
            "message_count": self.message_count,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        try:
            if mode == "agent":
                agent_result = self.agent.execute(message, context)
                result.update(agent_result)
            
            elif mode == "rag":
                rag_result = self.rag.answer(message, top_k=5, language=I18N.lang())
                result.update(rag_result)
            
            elif mode == "analysis":
                analysis_result = self.analyzer.process_stream(message)
                result.update(analysis_result)
            
            elif mode == "extraction":
                # Infer type from message
                schema_type = "invoice"
                if "contract" in message.lower():
                    schema_type = "contract"
                elif "report" in message.lower():
                    schema_type = "report"
                extraction_result = self.extractor.extract(message, schema_type)
                result.update({
                    "extracted_data": extraction_result,
                    "type": "extraction",
                })
            
            elif mode == "voice":
                # Placeholder for voice processing
                result.update({
                    "response": "Voice processing not implemented in text mode",
                    "type": "voice",
                })
            
            else:  # conversation (default)
                response = self.conversational.chat(
                    message,
                    context=context,
                    use_knowledge_base=True,
                )
                result.update({
                    "response": response,
                    "type": "conversation",
                    "domain": self.domain,
                })
            
            # Store conversation
            try:
                store_conversation(
                    conversation_id=self.conversation_id,
                    username=self.username,
                    mode=mode,
                    user_message=message,
                    ai_response=result.get("response", ""),
                    context=context,
                )
            except Exception as e:
                log.warning("Failed to store conversation: %s", e)
            
            return result
        
        except Exception as e:
            log.error("Process error: %s", e)
            result.update({
                "response": f"Error: {str(e)[:200]}",
                "type": "error",
                "error": str(e)[:200],
            })
            return result

    def set_domain(self, domain: str) -> None:
        """Switch domain for personalization."""
        self.domain = domain
        self.conversational.set_domain(domain)
        log.info("Chatbot domain switched to: %s for conversation %s", domain, self.conversation_id)

    def clear_history(self) -> None:
        """Clear all conversation history."""
        self.conversational.clear_history()
        self.voice.clear_history()
        log.info("Cleared history for conversation %s", self.conversation_id)

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary."""
        return {
            "conversation_id": self.conversation_id,
            "domain": self.domain,
            "message_count": self.message_count,
            "history_length": len(self.conversational.conversation_history),
            "history_preview": self.conversational.conversation_history[-5:],
        }


# ════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS & BACKWARD COMPATIBILITY
# ════════════════════════════════════════════════════════════════════════════

_omnismart_instance: Optional[OmniSmartChatbot] = None


def get_omnismart_chatbot(
    conversation_id: Optional[str] = None,
    domain: str = "general",
    username: Optional[str] = None,
) -> OmniSmartChatbot:
    """Get or create OmniSmart chatbot instance."""
    global _omnismart_instance
    if _omnismart_instance is None or conversation_id:
        _omnismart_instance = OmniSmartChatbot(
            conversation_id=conversation_id,
            domain=domain,
            username=username,
        )
    return _omnismart_instance


def chat(
    message: str,
    mode: str = "auto",
    context: str = "",
    conversation_id: Optional[str] = None,
    domain: str = "general",
) -> Dict[str, Any]:
    """Convenience function for chatting."""
    chatbot = get_omnismart_chatbot(conversation_id, domain)
    return chatbot.process(message, mode, context)


# Backward compatibility aliases
AdvancedChatbot = OmniSmartChatbot
UnifiedChatbot = OmniSmartChatbot
ConversationalAgent = LightweightConversationalAgent

# Backward compatibility function aliases
def get_unified_chatbot(conversation_id: Optional[str] = None) -> OmniSmartChatbot:
    """Get or create unified chatbot instance (backward compatibility alias)."""
    return get_omnismart_chatbot(conversation_id, domain="general")

__all__ = [
    "OmniSmartChatbot",
    "MultiStepAgent",
    "UltraFastRAG",
    "RealTimeAnalyzer",
    "VoiceChatbot",
    "StructuredExtractor",
    "LightweightConversationalAgent",
    "get_omnismart_chatbot",
    "get_unified_chatbot",
    "chat",
    "ingest_document",
    "search_web",
    "parse_pdf",
    "parse_docx",
    # Persona system
    "PersonaContext",
    "AgentPersonaFactory",
    "get_persona_factory",
    "PERSONA_TEMPLATES",
    "ROLE_PERSONA_MAP",
    # Backward compatibility
    "AdvancedChatbot",
    "UnifiedChatbot",
    "ConversationalAgent",
]
