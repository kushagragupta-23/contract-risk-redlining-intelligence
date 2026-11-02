import pytest
from backend.engine.silent_risk_scanner import SilentRiskScanner
from backend.engine.redliner import ContractRedliner

SAMPLE_FLAWED_CONTRACT = """
1. SERVICES AND FEES.
Customer shall pay all undisputed fees within thirty (30) days of invoice date.

2. TERMINATION.
Either party may terminate upon thirty (30) days written notice.

3. GOVERNING LAW.
This Agreement shall be governed by the laws of the State of New York.
"""

def test_silent_risk_omission_detection():
    omissions = SilentRiskScanner.scan_for_omissions(SAMPLE_FLAWED_CONTRACT)
    assert len(omissions) >= 2
    categories = [o["category"] for o in omissions]
    assert "DATA_PRIVACY_SECURITY" in categories
    assert "CONFIDENTIALITY_SURVIVAL" in categories

def test_redliner_health_grade_and_omissions():
    report = ContractRedliner.analyze_document(SAMPLE_FLAWED_CONTRACT, title="Deficient Contract Test")
    assert len(report.missing_protections) >= 2
    assert "Grade" in report.contract_health_grade
    assert report.total_clauses_analyzed >= 3

def test_negotiation_talking_points_and_fallbacks():
    sample_text = """
    1. LIMITATION OF LIABILITY.
    Under no circumstances shall Vendor liability be capped under this Agreement, and Vendor shall have unlimited liability for all damages.
    """
    report = ContractRedliner.analyze_document(sample_text, title="Liability Test")
    assert report.critical_count >= 1
    crit_clause = next(c for c in report.clauses if c.risk_level == "CRITICAL")
    assert crit_clause.compromise_fallback is not None
    assert crit_clause.walkaway_threshold is not None
    assert len(crit_clause.talking_points) >= 2
