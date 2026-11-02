import pytest
from backend.engine.clause_classifier import ClauseClassifier

SAMPLE_CONTRACT = """
1. Limitation of Liability
In no event shall liability be capped for any breach under this Agreement, and Vendor shall have unlimited liability.

2. Intellectual Property
All intellectual property developed by either party shall immediately become sole property of client.

3. Termination
Client may terminate immediately without notice at sole discretion.
"""

def test_classifier_segmentation():
    clauses = ClauseClassifier.segment_contract(SAMPLE_CONTRACT)
    assert len(clauses) >= 3
    assert clauses[0]["clause_id"] == "CLAUSE_01"

def test_category_matching():
    cat, conf = ClauseClassifier.classify_text("In no event shall aggregate liability exceed total fees paid.")
    assert cat == "LIMITATION_OF_LIABILITY"
    assert conf > 0.90

    cat_ip, conf_ip = ClauseClassifier.classify_text("Vendor assigns all proprietary rights, copyright, and patent rights.")
    assert cat_ip == "INTELLECTUAL_PROPERTY"

