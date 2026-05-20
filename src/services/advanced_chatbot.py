"""
Advanced Chatbot with Multi-Step Agents, RAG, Real-time Analysis, Voice, and Structured Output.

Implements all 5 Groq patterns:
1. Multi-step autonomous agents (Agents Autonomes "Multi-étapes")
2. Ultra-fast RAG (RAG Ultra-Rapide)
3. Real-time data flow analysis (Analyse de Flux de Données)
4. Natural voice chatbot (Chatbots avec "Voix" Naturelle)
5. Structured data extraction (Extraction de Données Structurées)
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import re

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
)

log = get_logger(__name__)

try:
    from groq import Groq
    _GROQ = True
except ImportError:
    _GROQ = False

try:
    from langchain_groq import ChatGroq
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
    from langchain.vectorstores import Chroma
    from langchain.embeddings import SentenceTransformerEmbeddings
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.chains import ConversationChain
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain.agents import initialize_agent, AgentType
    _LANGCHAIN = True
except ImportError:
    _LANGCHAIN = False


# ════════════════════════════════════════════════════════════════════════════
# LIGHTWEIGHT CONVERSATIONAL AGENT (Lightweight Bilingual Multi-Domain)
# ════════════════════════════════════════════════════════════════════════════

class ConversationalAgent:
    """
    Lightweight bilingual conversational agent for multi-domain intelligence.
    Generalized from CFO Agent, now works across Finance, HR, Ops, ESG, etc.
    
    Features:
    - Conversation memory (recent 10 exchanges)
    - Bilingual (French/English) with language auto-detection
    - Multi-domain capabilities (Finance, Growth, HR, Ops, People, ESG)
    - Direct Groq API (no LangChain overhead)
    - Token-efficient with context windowing
    """

    def __init__(self, session_id: str = "default", domain: str = "general"):
        self.session_id = session_id
        self.domain = domain  # "finance", "hr", "ops", "general", etc.
        self.conversation_history: List[Dict[str, str]] = []
        self.client = None
        if _GROQ and settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)

    def _build_system_prompt(self, domain: str = None) -> str:
        """Build domain-aware system prompt with bilingual support."""
        if domain is None:
            domain = self.domain
        lang = "French" if I18N.lang() == "fr" else "English"

        domain_capabilities = {
            "finance": "Analyze KPIs (Revenue, Profitability, Cash Flow), Predict trends using Monte Carlo, Process invoices, Generate financial reports",
            "hr": "Analyze HR metrics (Recruitment, Attrition, Training), Compensation planning, Team dynamics, Career development",
            "ops": "Monitor operational metrics (Efficiency, Quality, Safety), Identify bottlenecks, Suggest process improvements, Real-time alerts",
            "esg": "Track ESG metrics (Environmental, Social, Governance), Sustainability reporting, Risk assessment, Compliance",
            "growth": "Analyze growth metrics (User acquisition, Retention, LTV/CAC), Market analysis, Competitive positioning, Expansion strategy",
            "general": "Multi-domain intelligence: Finance, HR, Ops, ESG, Growth. Answer questions, provide insights, suggest actions"
        }

        capabilities = domain_capabilities.get(domain, domain_capabilities["general"])

        system_prompt = f"""You are the OmniIntelOS Conversational Agent.
LANGUAGE: Respond in {lang}.
DOMAIN: {domain.upper()}

CAPABILITIES:
- {capabilities}
- Access to company knowledge base and documents
- Real-time data analysis and trend detection
- Structured data extraction (invoices, contracts, forms)
- Multi-step reasoning and problem-solving

PERSONALITY:
- Professional, precise, and helpful
- Action-oriented with clear recommendations
- Proactive in offering analysis or reports when relevant
- Bilingual and culturally sensitive

CONVERSATION CONTEXT:
Recent exchanges (max 10 messages):
{self._format_history()}

INSTRUCTIONS:
- Be concise but thorough
- Offer to generate reports or run simulations when relevant
- Ask clarifying questions if needed
- Reference data sources when available
"""
        return system_prompt

    def _format_history(self) -> str:
        """Format recent conversation history for context (max 10 messages)."""
        if not self.conversation_history:
            return "No previous conversation."

        recent = self.conversation_history[-10:]
        formatted = []
        for msg in recent:
            role = "USER" if msg["role"] == "user" else "AGENT"
            content = msg['content'][:150]  # Truncate long messages
            formatted.append(f"{role}: {content}...")

        return "\n".join(formatted)

    def chat(self, user_input: str, context: str = "") -> str:
        """Chat with conversation memory and multi-domain awareness."""
        if not self.client:
            return (
                "Agent non disponible (clé API manquante)."
                if I18N.lang() == "fr"
                else "Agent unavailable (missing API key)."
            )

        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_input})

            # Build system prompt with domain and language
            system_prompt = self._build_system_prompt()

            # Add additional context if provided
            if context:
                system_prompt += f"\n\nADDITIONAL CONTEXT:\n{context}"

            # Call Groq directly (lightweight, no LangChain overhead)
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9
            )

            agent_response = response.choices[0].message.content

            # Add agent response to history
            self.conversation_history.append({"role": "assistant", "content": agent_response})

            # Keep history manageable (max 20 messages = 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return agent_response

        except Exception as exc:
            log.error("Conversational agent error: %s", exc)
            return (
                f"Erreur agent: {str(exc)[:100]}"
                if I18N.lang() == "fr"
                else f"Agent error: {str(exc)[:100]}"
            )

    def set_domain(self, domain: str) -> None:
        """Switch to a different domain (finance, hr, ops, etc.)."""
        self.domain = domain
        log.info("Agent domain switched to: %s", domain)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []


# ════════════════════════════════════════════════════════════
# PATTERN 1: MULTI-STEP AUTONOMOUS AGENTS (Agents Autonomes Multi-étapes)
# ════════════════════════════════════════════════════════════

class MultiStepAgent:
    """
    Executes complex tasks through multiple LLM calls with reasoning and action.
    
    Example flow:
    - User asks: "Analyze our Q4 revenue drop and suggest fixes"
    - Agent: 1) Retrieves data → 2) Analyzes causes → 3) Simulates solutions → 4) Generates report
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.conversation_memory: List[Dict[str, str]] = []
        self.max_steps = 5
        self.step_count = 0

    def _think(self, query: str, context: str = "") -> str:
        """Step 1: Reasoning - Plan the approach."""
        if not self.client:
            return ""

        prompt = f"""You are an intelligent financial analyst agent.
Given the query and context, think step-by-step about how to approach this problem.
Identify the data you need, analyses to perform, and insights to generate.

Query: {query}
Context: {context}

Provide a brief reasoning plan (2-3 sentences):"""

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content

    def _act(self, query: str, reasoning: str, tools: List[str]) -> Dict[str, Any]:
        """Step 2: Action - Execute the plan using available tools."""
        if not self.client:
            return {}

        tools_str = ", ".join(tools)
        prompt = f"""Based on the reasoning below, determine which tools/data sources to use:

Query: {query}
Reasoning: {reasoning}
Available Tools: {tools_str}

For each step, specify:
1. The tool/data source to use
2. The specific query/parameters
3. Expected outcome

Format as JSON."""

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"steps": [response.choices[0].message.content]}

    def _synthesize(self, query: str, reasoning: str, action_results: Dict[str, Any]) -> str:
        """Step 3: Synthesis - Combine results into coherent response."""
        if not self.client:
            return ""

        results_json = json.dumps(action_results, indent=2)
        prompt = f"""Based on the reasoning and action results below, generate a comprehensive response.

Query: {query}
Reasoning: {reasoning}
Results:
{results_json}

Provide a clear, actionable response with:
1. Key findings
2. Insights from the data
3. Specific recommendations
4. Next steps

Be concise but thorough."""

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.5
        )
        return response.choices[0].message.content

    def execute(self, query: str, context: str = "", tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute multi-step agent workflow."""
        self.step_count = 0

        if tools is None:
            tools = ["financial_data", "knowledge_base", "ml_models", "api_integrations"]

        # Step 1: Think
        log.info("Agent Step 1: Thinking...")
        reasoning = self._think(query, context)
        self.step_count += 1

        # Step 2: Act
        log.info("Agent Step 2: Acting...")
        action_results = self._act(query, reasoning, tools)
        self.step_count += 1

        # Step 3: Synthesize
        log.info("Agent Step 3: Synthesizing...")
        final_response = self._synthesize(query, reasoning, action_results)
        self.step_count += 1

        return {
            "query": query,
            "reasoning": reasoning,
            "actions": action_results,
            "response": final_response,
            "steps_executed": self.step_count,
            "timestamp": datetime.utcnow().isoformat()
        }


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 2: ULTRA-FAST RAG (RAG Ultra-Rapide)
# ════════════════════════════════════════════════════════════════════════════

class UltraFastRAG:
    """
    Retrieval-Augmented Generation with instant context injection.
    
    Features:
    - Near-instant document retrieval via vector similarity
    - Groq inference for rapid generation
    - Minimal latency (milliseconds)
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.cache: Dict[str, Any] = {}
        self.max_cache_size = 100

    def _retrieve_documents(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """Retrieve most relevant documents using semantic similarity."""
        try:
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity

            docs = get_knowledge_docs()
            if docs.empty:
                return []

            # Get query embedding
            model = SentenceTransformer(settings.EMBEDDING_MODEL)
            query_emb = model.encode([query])[0]

            # Compare with document embeddings
            results = []
            for _, doc in docs.iterrows():
                if pd.isna(doc.get("embedding")):
                    continue
                try:
                    doc_emb = np.array(json.loads(doc["embedding"]))
                    similarity = cosine_similarity([query_emb], [doc_emb])[0][0]
                    results.append((doc["title"], doc["content"][:500], similarity))
                except Exception:
                    continue

            # Sort by similarity and return top-k
            results.sort(key=lambda x: x[2], reverse=True)
            return results[:top_k]

        except Exception as exc:
            log.error("Document retrieval error: %s", exc)
            return []

    def _build_rag_prompt(self, query: str, documents: List[Tuple[str, str, float]]) -> str:
        """Build prompt with retrieved context."""
        doc_context = "\n\n".join(
            f"📄 **{title}** (relevance: {sim:.1%})\n{content}"
            for title, content, sim in documents
        )

        return f"""You are a knowledgeable financial analyst with access to company documents and data.

RETRIEVED CONTEXT:
{doc_context if doc_context else "(No documents found)"}

USER QUERY: {query}

Based on the context above, provide a comprehensive answer. If information is incomplete, clearly state what additional data would help.

RESPONSE:"""

    def answer(self, query: str, top_k: int = 5, use_cache: bool = True) -> Dict[str, Any]:
        """Generate RAG-based answer with retrieved documents."""
        if not self.client:
            return {"answer": "Groq client not available", "documents": []}

        # Check cache
        cache_key = f"rag:{query}"
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        # Retrieve documents
        documents = self._retrieve_documents(query, top_k)

        # Build and execute prompt
        prompt = self._build_rag_prompt(query, documents)

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.4
        )

        answer = response.choices[0].message.content

        # Cache result
        result = {
            "query": query,
            "answer": answer,
            "documents": [
                {"title": title, "content": content[:300], "relevance": f"{sim:.1%}"}
                for title, content, sim in documents
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

        if len(self.cache) < self.max_cache_size:
            self.cache[cache_key] = result

        return result


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 3: REAL-TIME DATA FLOW ANALYSIS (Analyse de Flux de Données)
# ════════════════════════════════════════════════════════════════════════════

class RealTimeAnalyzer:
    """
    Process streaming data or logs for anomalies, patterns, and alerts.
    
    Features:
    - High-velocity text processing
    - Anomaly detection
    - Real-time sentiment analysis
    - Instant alert generation
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.anomaly_threshold = 0.7
        self.alert_queue: List[Dict[str, Any]] = []

    def _detect_anomalies(self, data_stream: str) -> List[Dict[str, Any]]:
        """Detect anomalies in streaming data."""
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

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return [{"anomaly": response.choices[0].message.content, "severity": 5}]

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

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"sentiment": "unknown"}

    def process_stream(self, data_stream: str) -> Dict[str, Any]:
        """Process streaming data for anomalies and insights."""
        anomalies = self._detect_anomalies(data_stream)
        sentiment = self._analyze_sentiment(data_stream)

        result = {
            "anomalies": [a for a in anomalies if a.get("severity", 5) >= self.anomaly_threshold * 10],
            "sentiment": sentiment,
            "alert_count": len([a for a in anomalies if a.get("severity", 5) >= 7]),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Queue high-severity alerts
        for anomaly in result["anomalies"]:
            if anomaly.get("severity", 0) >= 8:
                self.alert_queue.append({
                    "anomaly": anomaly,
                    "timestamp": result["timestamp"]
                })

        return result

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Retrieve queued alerts."""
        alerts = self.alert_queue.copy()
        self.alert_queue.clear()
        return alerts


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 4: NATURAL VOICE CHATBOT (Chatbots avec "Voix" Naturelle)
# ════════════════════════════════════════════════════════════════════════════

class VoiceChatbot:
    """
    Conversational interface with instant responses (no gaps/delays).
    
    Features:
    - Speech-to-Text (Groq Whisper)
    - Instant text generation (Groq LLM)
    - Text-to-Speech (integration ready)
    - Natural conversation flow
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are a friendly, intelligent financial assistant.
Respond naturally and conversationally. Keep responses concise but informative.
If you need clarification, ask directly. Be proactive in offering insights."""

        # LangChain integration with memory and streaming
        self.langchain_chat = None
        self.memory = None
        self.conversation_chain = None
        self.rag_chain = None
        self.token_usage = {"total_tokens": 0, "total_cost": 0.0}

        if _LANGCHAIN and _GROQ:
            try:
                self.langchain_chat = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name=settings.LLM_MODEL,
                    temperature=0.7,
                    max_tokens=512,
                    streaming=True  # Enable streaming
                )

                # Initialize conversation memory (last 10 messages)
                self.memory = ConversationBufferWindowMemory(
                    k=10,
                    memory_key="history",
                    return_messages=True
                )

                # Create conversation chain with memory
                self.conversation_chain = ConversationChain(
                    llm=self.langchain_chat,
                    memory=self.memory,
                    verbose=False
                )

                # Initialize web search with Tavily
                if settings.TAVILY_API_KEY:
                    self.web_search = TavilySearchResults(
                        tavily_api_key=settings.TAVILY_API_KEY,
                        max_results=3
                    )

                # Initialize embeddings for RAG
                self.embeddings = SentenceTransformerEmbeddings(
                    model_name="all-MiniLM-L6-v2"
                )
                # Initialize vector store (will be populated with knowledge base)
                self.vectorstore = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory="./chroma_db"
                )
                # Create RAG chain
                self._setup_rag_chain()
                # Create enhanced RAG with web search
                self._setup_enhanced_rag_chain()
            except Exception as e:
                log.warning("LangChain initialization failed: %s", e)

    def _setup_rag_chain(self):
        """Setup RAG chain for document-based Q&A."""
        if not self.langchain_chat:
            return

        prompt_template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}
Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.langchain_chat,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT}
        )

    def _setup_enhanced_rag_chain(self):
        """Setup enhanced RAG chain with web search fallback."""
        if not self.langchain_chat or not self.web_search:
            return

        # Create an agent that can use both RAG and web search
        from langchain.agents import Tool
        from langchain.chains import RetrievalQA

        # Define tools
        knowledge_base_tool = Tool(
            name="KnowledgeBase",
            description="Search the local knowledge base for company-specific information",
            func=self._search_knowledge_base
        )

        web_search_tool = Tool(
            name="WebSearch",
            description="Search the web for current information and general knowledge",
            func=self._search_web
        )

        # Create agent with tools
        self.enhanced_rag_chain = initialize_agent(
            tools=[knowledge_base_tool, web_search_tool],
            llm=self.langchain_chat,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            max_iterations=3,  # Limit to control costs
            handle_parsing_errors=True
        )

    def _search_knowledge_base(self, query: str) -> str:
        """Search local knowledge base."""
        if not self.rag_chain:
            return "Knowledge base not available"

        try:
            result = self.rag_chain.invoke({"query": query})
            return result["result"]
        except Exception as e:
            log.error("RAG query error: %s", e)
            return "Unable to query knowledge base"

    def _search_web(self, query: str) -> str:
        """Search web using Tavily."""
        if not self.web_search:
            return "Web search not available"

        try:
            results = self.web_search.invoke({"query": query})
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append(f"• {result['title']}: {result['content'][:200]}...")
            return "\n".join(formatted_results)
        except Exception as e:
            log.error("Web search error: %s", e)
            return "Unable to search web"

    def transcribe(self, audio_file_path: str) -> str:
        """Convert speech to text using Groq Whisper."""
        if not self.client:
            return ""

        try:
            with open(audio_file_path, "rb") as audio:
                transcript = self.client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-large-v3-turbo",
                    language="en"
                )
            return transcript.text
        except Exception as exc:
            log.error("Transcription error: %s", exc)
            return ""

    def chat(self, user_message: str) -> str:
        """Generate natural response with conversation memory using LangChain."""
        # Fallback to direct Groq if LangChain not available
        if not self.conversation_chain:
            return self._chat_fallback(user_message)

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Use conversation chain with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.conversation_chain.predict(input=user_message)

                # Track token usage (approximate)
                estimated_tokens = len(user_message.split()) + len(response.split())
                self.token_usage["total_tokens"] += estimated_tokens
                # Groq pricing: ~$0.0001 per 1K tokens for Llama models
                self.token_usage["total_cost"] += (estimated_tokens / 1000) * 0.0001

                # Log token usage periodically
                if self.token_usage["total_tokens"] % 1000 < estimated_tokens:
                    log.info(f"Token usage: {self.token_usage}")

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

                return response

            except Exception as e:
                if attempt == max_retries - 1:
                    log.error(f"LangChain chat failed after {max_retries} attempts: {e}")
                    return self._chat_fallback(user_message)
                else:
                    log.warning(f"LangChain chat attempt {attempt + 1} failed: {e}")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff

    def get_token_usage(self) -> Dict[str, float]:
        """Get current token usage statistics."""
        return self.token_usage.copy()

    def _chat_fallback(self, user_message: str) -> str:
        """Fallback chat method using direct Groq client."""
        if not self.client:
            return "Service unavailable"

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Keep last 10 messages for context
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history[-10:]

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9
        )

        assistant_message = response.choices[0].message.content

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def add_to_knowledge_base(self, documents: List[Dict[str, str]]):
        """Add documents to the knowledge base for RAG."""
        if not self.vectorstore:
            return

        try:
            docs = [
                Document(page_content=doc["content"], metadata=doc.get("metadata", {}))
                for doc in documents
            ]
            self.vectorstore.add_documents(docs)
            log.info("Added %d documents to knowledge base", len(docs))
        except Exception as e:
            log.error("Failed to add documents to knowledge base: %s", e)

    def query_knowledge_base(self, question: str) -> str:
        """Query the knowledge base using enhanced RAG with web search fallback."""
        # Use enhanced agent if available (includes web search)
        if self.enhanced_rag_chain:
            try:
                result = self.enhanced_rag_chain.invoke({
                    "input": f"Answer this question using available tools: {question}. "
                           "First check the knowledge base, then search the web if needed for current information."
                })
                return result["output"]
            except Exception as e:
                log.error("Enhanced RAG query error: %s", e)
                # Fallback to basic RAG

        # Fallback to basic RAG
        if not self.rag_chain:
            return "Knowledge base not available"

        try:
            result = self.rag_chain.invoke({"query": question})
            return result["result"]
        except Exception as e:
            log.error("RAG query error: %s", e)
            return "Unable to query knowledge base"

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# ════════════════════════════════════════════════════════════════════════════
# PATTERN 5: STRUCTURED DATA EXTRACTION (Extraction de Données Structurées)
# ════════════════════════════════════════════════════════════════════════════

class StructuredExtractor:
    """
    Extract structured data (JSON) from unstructured text.
    
    Features:
    - Schema-based extraction
    - Batch processing
    - Validation and error handling
    - Supports invoices, forms, contracts, etc.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None

    def _define_schema(self, extraction_type: str) -> Dict[str, Any]:
        """Define extraction schema based on type."""
        schemas = {
            "invoice": {
                "invoice_number": "string",
                "date": "string (YYYY-MM-DD)",
                "vendor": "string",
                "total_amount": "number",
                "currency": "string",
                "line_items": [
                    {
                        "description": "string",
                        "quantity": "number",
                        "unit_price": "number",
                        "total": "number"
                    }
                ]
            },
            "financial_statement": {
                "statement_type": "string (P&L, Balance Sheet, Cash Flow)",
                "period": "string (YYYY-MM-DD to YYYY-MM-DD)",
                "line_items": [
                    {
                        "category": "string",
                        "amount": "number",
                        "currency": "string",
                        "percentage_of_total": "number"
                    }
                ],
                "summary_metrics": {}
            },
            "contract": {
                "parties": ["string"],
                "start_date": "string",
                "end_date": "string",
                "key_terms": ["string"],
                "obligations": ["string"],
                "penalties": ["string"],
                "termination_clauses": ["string"]
            }
        }
        return schemas.get(extraction_type, {})

    def extract(self, text: str, schema_type: str = "invoice") -> Dict[str, Any]:
        """Extract structured data from text."""
        if not self.client:
            return {}

        schema = self._define_schema(schema_type)
        schema_json = json.dumps(schema, indent=2)

        prompt = f"""Extract structured data from the following text and return as valid JSON.
Follow the schema exactly. If a field is missing, use null.

TEXT:
{text}

SCHEMA:
{schema_json}

Return ONLY valid JSON, no additional text."""

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.1  # Very low temperature for consistency
        )

        try:
            extracted_data = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "data": extracted_data,
                "schema_type": schema_type
            }
        except json.JSONDecodeError as exc:
            log.error("JSON extraction error: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "raw_response": response.choices[0].message.content
            }

    def batch_extract(self, documents: List[str], schema_type: str = "invoice") -> List[Dict[str, Any]]:
        """Extract data from multiple documents."""
        results = []
        for doc in documents:
            result = self.extract(doc, schema_type)
            results.append(result)
        return results


# ════════════════════════════════════════════════════════════════════════════
# UNIFIED ADVANCED CHATBOT (Combines All 5 Patterns)
# ════════════════════════════════════════════════════════════════════════════

class AdvancedChatbot:
    """
    Unified chatbot combining all 5 Groq patterns for comprehensive intelligence.
    
    Capabilities:
    1. Multi-step autonomous agents (complex problem solving)
    2. Ultra-fast RAG (document-aware responses)
    3. Real-time analysis (anomaly detection, sentiment)
    4. Natural voice interface (conversational)
    5. Structured extraction (data parsing)
    6. Lightweight conversational agent (bilingual, multi-domain, memory-efficient)
    """

    def __init__(self, conversation_id: Optional[str] = None, domain: str = "general"):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.domain = domain
        self.agent = MultiStepAgent()
        self.rag = UltraFastRAG()
        self.analyzer = RealTimeAnalyzer()
        self.voice = VoiceChatbot()
        self.extractor = StructuredExtractor()
        self.conversational_agent = ConversationalAgent(session_id=self.conversation_id, domain=domain)
        self.client = Groq(api_key=settings.GROQ_API_KEY) if _GROQ else None

    def _detect_intent(self, message: str) -> str:
        """Detect user intent to route to appropriate handler."""
        intents = {
            "complex_analysis": ["analyze", "investigate", "diagnose", "explain", "why"],
            "document_query": ["what", "how", "tell", "find", "search", "reference"],
            "real_time": ["monitor", "stream", "alert", "detect", "anomaly"],
            "extraction": ["extract", "parse", "get", "pull", "export"],
            "conversation": ["hi", "hello", "how", "chat", "talk"]
        }

        message_lower = message.lower()
        for intent, keywords in intents.items():
            if any(kw in message_lower for kw in keywords):
                return intent

        return "conversation"

    def process(self, message: str, mode: str = "auto", context: str = "") -> Dict[str, Any]:
        """
        Process user message through appropriate pattern(s).

        Args:
            message: User input
            mode: 'auto' (detect), 'agent', 'rag', 'analysis', 'extraction', 'voice'
            context: Additional context

        Returns:
            Response with metadata
        """
        if not self.client:
            return {"error": "Groq not configured"}

        # Auto-detect intent if needed
        if mode == "auto":
            mode = self._detect_intent(message)

        result = {
            "conversation_id": self.conversation_id,
            "message": message,
            "mode": mode,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Route to appropriate handler
        if mode == "complex_analysis":
            agent_result = self.agent.execute(message, context)
            result.update({
                "response": agent_result["response"],
                "reasoning": agent_result["reasoning"],
                "type": "multi_step_agent"
            })

        elif mode == "document_query":
            rag_result = self.rag.answer(message)
            result.update({
                "response": rag_result["answer"],
                "sources": rag_result["documents"],
                "type": "rag"
            })

        elif mode == "real_time":
            analysis_result = self.analyzer.process_stream(message)
            result.update({
                "anomalies": analysis_result["anomalies"],
                "alerts": self.analyzer.get_alerts(),
                "type": "real_time_analysis"
            })

        elif mode == "extraction":
            extraction_result = self.extractor.extract(message)
            result.update({
                "extracted_data": extraction_result.get("data"),
                "type": "structured_extraction"
            })

        else:  # conversation
            response = self.conversational_agent.chat(message, context)
            result.update({
                "response": response,
                "type": "natural_conversation",
                "domain": self.domain
            })

        # Store conversation
        store_conversation(
            self.conversation_id,
            message,
            result.get("response", json.dumps(result)),
            language=I18N.lang()
        )

        return result

    def process_voice(self, audio_file_path: str) -> Dict[str, Any]:
        """Process voice input end-to-end."""
        # Transcribe
        transcribed = self.voice.transcribe(audio_file_path)
        if not transcribed:
            return {"error": "Transcription failed"}

        # Process as natural conversation
        result = self.process(transcribed, mode="conversation")
        result["transcribed_text"] = transcribed

        return result

    def clear_history(self):
        """Clear conversation history."""
        self.voice.clear_history()
        self.conversational_agent.clear_history()

    def set_domain(self, domain: str) -> None:
        """Switch to a different domain (finance, hr, ops, esg, growth, general)."""
        self.domain = domain
        self.conversational_agent.set_domain(domain)
        log.info("Advanced chatbot domain switched to: %s", domain)


# ════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

# Singleton instance
_advanced_chatbot: Optional[AdvancedChatbot] = None


def get_advanced_chatbot(conversation_id: Optional[str] = None) -> AdvancedChatbot:
    """Get or create advanced chatbot instance."""
    global _advanced_chatbot
    if _advanced_chatbot is None or conversation_id:
        _advanced_chatbot = AdvancedChatbot(conversation_id)
    return _advanced_chatbot


def chat(message: str, mode: str = "auto") -> Dict[str, Any]:
    """Convenience function for chatting."""
    chatbot = get_advanced_chatbot()
    return chatbot.process(message, mode)
