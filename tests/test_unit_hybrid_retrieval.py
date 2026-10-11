import pytest

@pytest.mark.unit
def test_rrf_merge_logic():
    # Dummy results from vector search and keyword search
    vector_results = [{"id": "doc1", "score": 0.9}, {"id": "doc2", "score": 0.8}]
    keyword_results = [{"id": "doc2", "score": 10.5}, {"id": "doc3", "score": 5.2}]
    
    # RRF (Reciprocal Rank Fusion) logic
    k = 60
    rrf_scores = {}
    
    for rank, doc in enumerate(vector_results):
        doc_id = doc["id"]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        
    for rank, doc in enumerate(keyword_results):
        doc_id = doc["id"]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        
    # doc2 should be ranked highest because it appears in both
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    assert sorted_docs[0][0] == "doc2"
    assert len(sorted_docs) == 3


@pytest.mark.unit
def test_local_embedding_model_is_shared_between_retrievers(monkeypatch):
    from types import SimpleNamespace
    from src.services import hybrid_retrieval as retrieval
    from src.services import vector_store

    created = []

    class FakeEmbedder:
        def __init__(self, model_name, device):
            created.append((model_name, device))

    monkeypatch.setattr(retrieval, "_LOCAL_EMBED", True)
    monkeypatch.setattr(retrieval, "SentenceTransformer", FakeEmbedder, raising=False)
    monkeypatch.setattr(
        vector_store, "settings", SimpleNamespace(EMBEDDING_MODEL="test/bge-m3")
    )
    retrieval._LOCAL_EMBEDDERS.clear()

    try:
        hybrid = retrieval.HybridRetriever(embedding_model="test/bge-m3")
        first = hybrid._ensure_embedder()
        second = vector_store._embedder()

        assert first is second
        assert created == [("test/bge-m3", "cpu")]
    finally:
        retrieval._LOCAL_EMBEDDERS.clear()


@pytest.mark.unit
def test_local_embedding_uses_bounded_batches_and_normalization(monkeypatch):
    from src.services import hybrid_retrieval as retrieval

    class FakeEmbedder:
        def encode(self, texts, **kwargs):
            assert texts == ["query"]
            assert kwargs["batch_size"] == 4
            assert kwargs["normalize_embeddings"] is True
            return [[1.0, 0.0]]

    monkeypatch.setenv("EMBEDDING_PROVIDER", "local")
    monkeypatch.setenv("EMBED_BATCH_SIZE", "4")
    monkeypatch.setattr(retrieval, "_LOCAL_EMBED", True)
    retriever = retrieval.HybridRetriever()
    retriever._embedder = FakeEmbedder()

    assert retriever._encode(["query"]) == [[1.0, 0.0]]


@pytest.mark.unit
def test_local_inference_is_serialized_across_calls():
    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor
    from src.services.hybrid_retrieval import encode_local_embeddings

    class FakeEmbedder:
        active = 0
        max_active = 0
        state_lock = threading.Lock()

        def encode(self, texts, **kwargs):
            with self.state_lock:
                self.active += 1
                self.max_active = max(self.max_active, self.active)
            time.sleep(0.02)
            with self.state_lock:
                self.active -= 1
            return texts

    model = FakeEmbedder()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: encode_local_embeddings(model, ["query"], 1), range(8)))

    assert model.max_active == 1


@pytest.mark.unit
def test_local_reranker_uses_cpu_and_bounded_batches(monkeypatch):
    from src.services import hybrid_retrieval as retrieval

    class FakeReranker:
        def __init__(self, model_name, device, max_length):
            assert model_name == "BAAI/bge-reranker-v2-m3"
            assert device == "cpu"
            assert max_length == 512

        def predict(self, pairs, batch_size):
            assert pairs == [("query", "candidate")]
            assert batch_size == 3
            return [0.9]

    monkeypatch.setattr(retrieval, "_RERANKER", True)
    monkeypatch.setattr(retrieval, "CrossEncoder", FakeReranker, raising=False)
    monkeypatch.setattr(retrieval, "_RERANK_RETRIEVER", None)
    monkeypatch.setenv("RERANK_BATCH_SIZE", "3")
    monkeypatch.setenv("RERANK_BACKEND", "torch")

    assert retrieval._rerank_local("query", ["candidate"]) == [0.9]


@pytest.mark.unit
def test_local_reranker_rejects_unknown_backend(monkeypatch):
    from src.services import hybrid_retrieval as retrieval

    monkeypatch.setattr(retrieval, "_RERANKER", True)
    monkeypatch.setattr(retrieval, "_RERANK_RETRIEVER", None)
    monkeypatch.setenv("RERANK_BACKEND", "remote-fallback")

    with pytest.raises(RuntimeError, match="RERANK_BACKEND"):
        retrieval._rerank_local("query", ["candidate"])


@pytest.mark.unit
def test_local_reranker_selects_configured_onnx_backend(monkeypatch):
    from src.services import hybrid_retrieval as retrieval

    retriever = retrieval.HybridRetriever()
    loaded = object()
    monkeypatch.setattr(retrieval, "_RERANKER", True)
    monkeypatch.setattr(retrieval, "_RERANK_RETRIEVER", retriever)
    monkeypatch.setattr(retriever, "_load_onnx_int8_reranker", lambda max_length: loaded)
    monkeypatch.setenv("RERANK_BACKEND", "onnx-int8")
    monkeypatch.setenv("RERANK_MAX_LENGTH", "384")

    assert retriever._ensure_reranker(force=True) is loaded


@pytest.mark.unit
def test_local_reranker_model_load_is_shared_across_concurrent_calls(monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from src.services import hybrid_retrieval as retrieval

    created = []

    class FakeReranker:
        def __init__(self, model_name, device, max_length):
            created.append((model_name, device))
            assert max_length == 512

        def predict(self, pairs, batch_size):
            return [0.5] * len(pairs)

    monkeypatch.setattr(retrieval, "_RERANKER", True)
    monkeypatch.setattr(retrieval, "CrossEncoder", FakeReranker, raising=False)
    monkeypatch.setattr(retrieval, "_RERANK_RETRIEVER", None)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(
            lambda _: retrieval._rerank_local("query", ["candidate"]), range(8)
        ))

    assert results == [[0.5]] * 8
    assert created == [("BAAI/bge-reranker-v2-m3", "cpu")]


@pytest.mark.unit
def test_hybrid_status_requires_dense_sparse_and_local_reranker(monkeypatch):
    from types import SimpleNamespace
    from src.services import hybrid_retrieval as retrieval

    monkeypatch.setenv("USE_HYBRID_RETRIEVAL", "true")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "local")
    monkeypatch.setenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    monkeypatch.setenv("USE_RERANKER", "true")
    monkeypatch.setenv("RERANK_PROVIDER", "local")
    monkeypatch.setenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
    monkeypatch.setattr(retrieval, "_HYBRID", SimpleNamespace(
        _chunk_vecs=SimpleNamespace(shape=(1, 1024)),
        _bm25=object(),
        embedding_model_name="BAAI/bge-m3",
    ))
    monkeypatch.setattr(retrieval, "_RERANK_RETRIEVER", None)

    assert retrieval.hybrid_status() == "unavailable: local BGE reranker is not ready"
    monkeypatch.setattr(retrieval, "_RERANK_RETRIEVER", SimpleNamespace(
        _reranker=object(), reranker_model_name="BAAI/bge-reranker-v2-m3"
    ))
    assert retrieval.hybrid_status() == (
        "ready: BAAI/bge-m3 dense (1024d) + BM25/RRF + "
        "BAAI/bge-reranker-v2-m3 local reranker"
    )


@pytest.mark.unit
def test_hybrid_index_rebuilds_when_document_content_changes(monkeypatch):
    from src.services import hybrid_retrieval as retrieval

    monkeypatch.setenv("USE_HYBRID_RETRIEVAL", "true")
    monkeypatch.setenv("USE_RERANKER", "false")
    monkeypatch.setattr(retrieval, "_DENSE", False)
    monkeypatch.setattr(retrieval, "_BM25", True)
    monkeypatch.setattr(retrieval, "_HYBRID", None)
    monkeypatch.setattr(retrieval, "_HYBRID_SIG", None)

    retrieval.hybrid_doc_retrieve("content", [("title", "alpha")], top_k=1)
    first_index = retrieval._HYBRID
    retrieval.hybrid_doc_retrieve("content", [("title", "bravo")], top_k=1)

    assert retrieval._HYBRID is not first_index
    assert any("bravo" in chunk for chunk in retrieval._HYBRID._chunks)
