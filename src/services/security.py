import re
import logging

log = logging.getLogger(__name__)

class SecurityScanner:
    """
    Enterprise-grade Data Loss Prevention (DLP) for RAG ingestion.
    Scans for and redacts critical secrets (API keys, private keys, passwords)
    before they are vectorized or stored in the database.
    Aligns with 2025/2026 Zero Trust architecture standards.
    """
    
    # Common regex patterns for high-risk secrets
    PATTERNS = [
        # Cloud/API Keys
        (r"(?i)(api[_-]?key|secret|token|password)[\"']?\s*[:=]\s*[\"']?([a-zA-Z0-9\-_]{16,})[\"']?", r"\1 = [REDACTED_SECRET]"),
        # AWS Access Key
        (r"(?i)(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_ACCESS_KEY]"),
        # RSA/SSH Private Keys
        (r"-----BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY-----.*?-----END \1 PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
        # Generic Bearer Tokens
        (r"(?i)Bearer\s+([a-zA-Z0-9\-\._~\+/]+=*)", "Bearer [REDACTED_TOKEN]"),
        # OpenAI/Anthropic/Groq keys
        (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_AI_API_KEY]"),
        (r"(gsk_[a-zA-Z0-9]{20,})", "[REDACTED_GROQ_KEY]"),
        # Social Security Numbers (US)
        (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
        # Credit Card Numbers
        (r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_CC]"),
    ]

    @classmethod
    def redact_text(cls, text: str) -> str:
        if not text:
            return text
            
        redacted = text
        try:
            for pattern, replacement in cls.PATTERNS:
                # Handle group replacements
                if '\\' in replacement or '\1' in replacement:
                    redacted = re.sub(pattern, replacement, redacted, flags=re.DOTALL)
                else:
                    redacted = re.sub(pattern, replacement, redacted, flags=re.DOTALL)
        except Exception as e:
            log.error("DLP Regex Error: %s", e)
            
        return redacted
