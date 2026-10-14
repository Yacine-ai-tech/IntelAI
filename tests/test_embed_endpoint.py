import numpy as np
import pytest

pytestmark = pytest.mark.unit


def test_embed_endpoint_returns_vectors(monkeypatch):
    import asyncio
    from src.api import server

    monkeypatch.setattr("src.services.vector_store._embed", lambda texts: np.ones((len(texts), 4), dtype="float32"))
    out = asyncio.run(server.embed_texts(server.EmbedRequest(texts=["a", "b"])))
    assert out["dim"] == 4
    assert len(out["embeddings"]) == 2 and out["embeddings"][0] == [1.0, 1.0, 1.0, 1.0]


def test_embed_request_bounds():
    from pydantic import ValidationError
    from src.api import server

    with pytest.raises(ValidationError):
        server.EmbedRequest(texts=[])
    with pytest.raises(ValidationError):
        server.EmbedRequest(texts=["x"] * 300)


def test_document_language_is_inferred_from_file_names():
    from src.services.pg_store import infer_document_language as f

    assert f("esg_2021_fr.md", "ESG", None) == "fr"
    assert f("esg_2021_en.md", "ESG", None) == "en"
    assert f("omniintelos_handbook_2026_fr.pdf", "Corporate", "en") == "fr"
    assert f("report", "glossary/fr/finance/arr.md", None) == "fr"
