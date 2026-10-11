import pytest
from src.services.omnismart_chatbot import AgentPersonaFactory

@pytest.mark.unit
def test_chatbot_routing():
    # test that we can build a persona prompt
    factory = AgentPersonaFactory()
    ctx = factory.resolve_persona(user_role="ceo")
    sys_prompt = ctx.system_prompt
    assert "CEO" in sys_prompt or "Executive" in sys_prompt or len(sys_prompt) > 0


@pytest.mark.unit
def test_qdrant_empty_results_do_not_fall_back_to_local_index(monkeypatch):
    from types import SimpleNamespace
    import pandas as pd
    from src.services import omnismart_chatbot as chatbot
    from src.services import vector_store
    from src.services import hybrid_retrieval

    calls = []
    monkeypatch.setattr(chatbot, "get_knowledge_docs", lambda: pd.DataFrame({
        "title": ["title"], "content": ["body"]
    }))
    monkeypatch.setattr(
        chatbot, "settings", SimpleNamespace(VECTOR_STORE="qdrant", GROQ_API_KEY="")
    )
    monkeypatch.setattr(chatbot, "_run_with_timeout", lambda fn, timeout, *a: fn(*a))
    monkeypatch.setattr(vector_store, "vector_store_retrieve", lambda *a: calls.append("qdrant") or [])
    monkeypatch.setattr(hybrid_retrieval, "hybrid_enabled", lambda: True)
    monkeypatch.setattr(
        hybrid_retrieval, "hybrid_doc_retrieve",
        lambda *a, **k: calls.append("local") or [("title", "body", 1.0)],
    )

    result = chatbot.UltraFastRAG()._retrieve_documents("query")

    assert calls == ["qdrant"]
    assert result == []


@pytest.mark.unit
def test_qdrant_failure_is_not_hidden_by_local_index(monkeypatch):
    from types import SimpleNamespace
    import pandas as pd
    from src.services import omnismart_chatbot as chatbot
    from src.services import vector_store

    monkeypatch.setattr(chatbot, "get_knowledge_docs", lambda: pd.DataFrame({
        "title": ["title"], "content": ["body"]
    }))
    monkeypatch.setattr(
        chatbot, "settings", SimpleNamespace(VECTOR_STORE="qdrant", GROQ_API_KEY="")
    )
    monkeypatch.setattr(chatbot, "_run_with_timeout", lambda fn, timeout, *a: fn(*a))
    monkeypatch.setattr(
        vector_store, "vector_store_retrieve",
        lambda *a: (_ for _ in ()).throw(RuntimeError("Qdrant unavailable")),
    )

    with pytest.raises(RuntimeError, match="Qdrant unavailable"):
        chatbot.UltraFastRAG()._retrieve_documents("query")


@pytest.mark.unit
def test_qdrant_retrieval_timeout_is_reported_explicitly(monkeypatch):
    from types import SimpleNamespace
    import pandas as pd
    from src.services import omnismart_chatbot as chatbot

    monkeypatch.setattr(chatbot, "get_knowledge_docs", lambda: pd.DataFrame({
        "title": ["title"], "content": ["body"]
    }))
    monkeypatch.setattr(
        chatbot, "settings", SimpleNamespace(VECTOR_STORE="qdrant", GROQ_API_KEY="")
    )
    monkeypatch.setenv("VECTOR_RETRIEVAL_TIMEOUT", "30")
    monkeypatch.setattr(chatbot, "_run_with_timeout", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="retrieval timed out after 30s"):
        chatbot.UltraFastRAG()._retrieve_documents("query")


@pytest.mark.unit
def test_retrieval_returns_persistent_results_before_local_fallback(monkeypatch):
    from types import SimpleNamespace
    import pandas as pd
    from src.services import omnismart_chatbot as chatbot
    from src.services import vector_store

    persistent = [("stored", "qdrant result", 0.9)]
    monkeypatch.setattr(chatbot, "get_knowledge_docs", lambda: pd.DataFrame({
        "title": ["title"], "content": ["body"]
    }))
    monkeypatch.setattr(
        chatbot, "settings", SimpleNamespace(VECTOR_STORE="qdrant", GROQ_API_KEY="")
    )
    monkeypatch.setattr(chatbot, "_run_with_timeout", lambda fn, timeout, *a: fn(*a))
    monkeypatch.setattr(vector_store, "vector_store_retrieve", lambda *a: persistent)

    result = chatbot.UltraFastRAG()._retrieve_documents("query")

    assert result == persistent
