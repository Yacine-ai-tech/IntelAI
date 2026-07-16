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
