"""LangChain adapter — drop IntelAI personas into any LangChain RAG chain.

Optional integration; install the extra::

    pip install "omnismart-personas[langchain]"

Example (LCEL)::

    from omnismart_personas import persona_for_role
    from omnismart_personas.langchain import persona_chat_prompt, persona_retriever_filter
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser

    persona = persona_for_role("cfo")
    prompt = persona_chat_prompt(persona)            # system = persona scope; {context}/{question}
    chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()

    docs = persona_retriever_filter(persona, retriever.invoke(question))  # RBAC on retrieval
    answer = chain.invoke({"context": "\n".join(d.page_content for d in docs),
                           "question": question})

The persona's data-access scope drives both the system prompt and ``persona_retriever_filter``,
so the same role boundaries IntelAI enforces work in any LangChain pipeline.
"""
from __future__ import annotations

from typing import Any, List

from .context import build_system_prompt
from .templates import Persona

_HUMAN_TEMPLATE = (
    "RETRIEVED CONTEXT:\n{context}\n\n"
    "USER QUERY: {question}\n\n"
    "Answer using only the retrieved context and your scope. Cite sources where relevant."
)


def _require_langchain() -> None:
    try:
        import langchain_core  # noqa: F401
    except ImportError as e:  # pragma: no cover - import guard
        raise ImportError(
            "LangChain integration requires langchain-core. "
            "Install it with: pip install 'omnismart-personas[langchain]'"
        ) from e


def persona_chat_prompt(persona: Persona, *, language: str = "en"):
    """A LangChain ``ChatPromptTemplate``: a static persona system message (its scope +
    instructions) followed by a human turn templated with ``{context}`` and ``{question}`` —
    ready to pipe into any LCEL chain. The system content is passed as a ``SystemMessage``
    (not a template) so persona prompts containing braces never break formatting."""
    _require_langchain()
    from langchain_core.messages import SystemMessage
    from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
    system = SystemMessage(content=build_system_prompt(persona, language=language))
    human = HumanMessagePromptTemplate.from_template(_HUMAN_TEMPLATE)
    return ChatPromptTemplate.from_messages([system, human])


def persona_system_message(persona: Persona, *, language: str = "en"):
    """The persona's composed system prompt as a LangChain ``SystemMessage``."""
    _require_langchain()
    from langchain_core.messages import SystemMessage
    return SystemMessage(content=build_system_prompt(persona, language=language))


def persona_retriever_filter(
    persona: Persona, docs: List[Any], *, domain_key: str = "category"
) -> List[Any]:
    """Enforce the persona's data-access scope on a LangChain retriever's output: drop any
    ``Document`` whose ``metadata[domain_key]`` is outside scope. Documents with no domain
    metadata are kept (can't prove they're out of scope). This brings IntelAI's RBAC to any
    LangChain retriever — the same boundaries, enforced after retrieval."""
    kept: List[Any] = []
    for d in docs:
        meta = getattr(d, "metadata", None) or {}
        domain = meta.get(domain_key)
        if domain is None or persona.can_access(str(domain)):
            kept.append(d)
    return kept
