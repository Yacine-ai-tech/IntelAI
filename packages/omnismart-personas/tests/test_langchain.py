"""LangChain adapter tests (skipped when langchain-core isn't installed)."""
import pytest

pytest.importorskip("langchain_core")

from omnismart_personas import persona_for_role  # noqa: E402
from omnismart_personas.langchain import (  # noqa: E402
    persona_chat_prompt,
    persona_retriever_filter,
    persona_system_message,
)


def test_persona_chat_prompt_formats_context_and_question():
    persona = persona_for_role("cfo")
    prompt = persona_chat_prompt(persona)
    msgs = prompt.format_messages(context="Revenue = 3.6M", question="How is revenue?")
    # system (persona) + human (templated) message
    assert len(msgs) == 2
    assert "Revenue = 3.6M" in msgs[1].content
    assert "How is revenue?" in msgs[1].content
    # CFO scope leaks into the system prompt
    assert "Finance" in msgs[0].content


def test_persona_system_message_carries_scope():
    msg = persona_system_message(persona_for_role("chro"))
    assert "People" in msg.content


def test_persona_retriever_filter_enforces_scope():
    class Doc:
        def __init__(self, text, category):
            self.page_content = text
            self.metadata = {"category": category}

    cfo = persona_for_role("cfo")  # Finance / Growth scope
    docs = [Doc("a", "Finance"), Doc("b", "People"), Doc("c", "Growth"), Doc("d", None)]
    kept = persona_retriever_filter(cfo, docs)
    cats = [d.metadata["category"] for d in kept]
    assert "Finance" in cats and "Growth" in cats
    assert "People" not in cats          # out of scope → dropped
    assert None in cats                  # no domain metadata → kept
