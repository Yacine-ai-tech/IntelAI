"""
⚡ LAZY LOADER — Ultra-Fast Startup with On-Demand Model Loading

This module provides lazy loading for heavy ML dependencies to achieve:
- Sub-second application startup
- On-demand model initialization
- Memory-efficient resource management
- Caching for repeated use

USAGE:
    from src.services.lazy_loader import get_sentence_transformer, get_groq_client
    
    # Models are only loaded when first accessed
    model = get_sentence_transformer()
    client = get_groq_client()
"""
from __future__ import annotations

import threading
from typing import Any, Optional
from functools import lru_cache

from src.core.config import settings
from src.core.logger import get_logger

log = get_logger(__name__)

# Global locks for thread-safe lazy loading
_locks = {
    'groq': threading.Lock(),
    'sentence_transformer': threading.Lock(),
    'tavily': threading.Lock(),
    'tfidf': threading.Lock(),
}

# Global cache for loaded models
_cache: dict[str, Any] = {}


@lru_cache(maxsize=1)
def get_groq_client():
    """Return the Groq client. Raises RuntimeError if key is missing or groq is not installed."""
    with _locks['groq']:
        if 'groq' not in _cache:
            if not settings.GROQ_API_KEY:
                raise RuntimeError(
                    "GROQ_API_KEY is not set. Groq is required — set it in .env and restart."
                )
            try:
                from groq import Groq
            except ImportError as exc:
                raise RuntimeError(
                    "groq package is not installed. Run: pip install groq"
                ) from exc
            _cache['groq'] = Groq(api_key=settings.GROQ_API_KEY)
            log.info("✓ Groq client loaded")
        return _cache['groq']


@lru_cache(maxsize=1)
def get_sentence_transformer(model_name: str = None):
    """Lazy load SentenceTransformer model."""
    model_name = model_name or settings.EMBEDDING_MODEL
    cache_key = f'sentence_transformer_{model_name}'
    
    with _locks['sentence_transformer']:
        if cache_key not in _cache:
            try:
                log.info(f"Loading SentenceTransformer: {model_name} (first use may take 10-30s)...")
                from sentence_transformers import SentenceTransformer
                _cache[cache_key] = SentenceTransformer(model_name)
                log.info(f"✓ SentenceTransformer loaded: {model_name}")
            except ImportError:
                log.warning("SentenceTransformer not available - install with: pip install sentence-transformers")
                _cache[cache_key] = None
            except Exception as e:
                log.error(f"Error loading SentenceTransformer: {e}")
                _cache[cache_key] = None
        return _cache[cache_key]


@lru_cache(maxsize=1)
def get_tavily_client():
    """Return the Tavily client. Raises RuntimeError if key is missing or tavily is not installed."""
    with _locks['tavily']:
        if 'tavily' not in _cache:
            if not settings.TAVILY_API_KEY:
                raise RuntimeError(
                    "TAVILY_API_KEY is not set. Tavily is required — set it in .env and restart."
                )
            try:
                from tavily import TavilyClient
            except ImportError as exc:
                raise RuntimeError(
                    "tavily-python package is not installed. Run: pip install tavily-python"
                ) from exc
            _cache['tavily'] = TavilyClient(api_key=settings.TAVILY_API_KEY)
            log.info("✓ Tavily client loaded")
        return _cache['tavily']


@lru_cache(maxsize=1)
def get_tfidf_vectorizer():
    """Lazy load TF-IDF vectorizer."""
    with _locks['tfidf']:
        if 'tfidf' not in _cache:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                _cache['tfidf'] = TfidfVectorizer(max_features=1000, stop_words='english')
                log.info("✓ TF-IDF vectorizer loaded")
            except ImportError:
                log.warning("scikit-learn not available - install with: pip install scikit-learn")
                _cache['tfidf'] = None
            except Exception as e:
                log.error(f"Error loading TF-IDF: {e}")
                _cache['tfidf'] = None
        return _cache['tfidf']


def check_dependencies() -> dict[str, bool]:
    """Check which dependencies are available without loading them."""
    import importlib.util
    
    deps = {}
    
    # Check if modules exist without importing them
    deps['groq'] = importlib.util.find_spec('groq') is not None
    deps['sentence_transformers'] = importlib.util.find_spec('sentence_transformers') is not None
    deps['tavily'] = importlib.util.find_spec('tavily') is not None
    deps['sklearn'] = importlib.util.find_spec('sklearn') is not None
    deps['pypdf2'] = importlib.util.find_spec('PyPDF2') is not None
    deps['python_docx'] = importlib.util.find_spec('docx') is not None
    
    return deps


def preload_critical_models():
    """Preload critical models in background thread."""
    def _preload():
        try:
            # Load most commonly used models
            get_groq_client()
            # SentenceTransformer is heavy, skip for faster startup
            # get_sentence_transformer()
        except Exception as e:
            log.error(f"Error preloading models: {e}")
    
    thread = threading.Thread(target=_preload, daemon=True)
    thread.start()


def clear_cache():
    """Clear all cached models to free memory."""
    global _cache
    _cache.clear()
    get_groq_client.cache_clear()
    get_sentence_transformer.cache_clear()
    get_tavily_client.cache_clear()
    get_tfidf_vectorizer.cache_clear()
    log.info("Model cache cleared")
