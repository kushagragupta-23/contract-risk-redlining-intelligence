import pytest
from backend.engine.playbook_rag import PlaybookHybridRAGEngine

def test_playbook_hybrid_rag_search():
    engine = PlaybookHybridRAGEngine(rrf_k=60)
    
    # Query for unlimited liability clause
    results = engine.search_playbook("in no event shall liability be capped for any indirect damages", top_k=1)
    assert len(results) >= 1
    assert results[0]["category"] == "LIMITATION_OF_LIABILITY"
    assert "fees paid" in results[0]["fallback"]
    assert results[0]["rrf_score"] > 0.0

    # Query for intellectual property work product
    ip_results = engine.search_playbook("Client shall own all background intellectual property and patent rights", top_k=1)
    assert len(ip_results) >= 1
    assert ip_results[0]["category"] == "INTELLECTUAL_PROPERTY"

