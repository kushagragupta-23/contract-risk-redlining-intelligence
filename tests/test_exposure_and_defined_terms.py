import pytest
from backend.engine.defined_terms_analyzer import DefinedTermsAnalyzer
from backend.engine.exposure_calculator import ExposureCalculator
from backend.engine.redliner import ContractRedliner

SAMPLE_CONTRACT_WITH_TERMS = """
MASTER SERVICES AGREEMENT
Between Alpha Solutions ("Vendor") and Beta Corp ("Customer").

1. Definitions.
"Authorized Users" shall mean employees or contractors authorized by Customer.
"Service Downtime" means any unplanned disruption exceeding thirty consecutive minutes.
"DeadDefinitionTerm" shall mean an operational specification that is never used again.

2. Limitation of Liability.
In no event shall the aggregate liability of either party exceed the total fees paid under this Agreement in the twelve (12) months preceding the incident.
Neither party shall be liable for indirect, consequential, or punitive damages.

3. Performance and Obligations.
Customer shall ensure that Authorized Users do not abuse the proprietary environment.
Vendor shall remediate any Service Downtime in accordance with Exhibit A.
However, the Security Coordinator and Incident Commander must notify the Executive Committee.
"""

SAMPLE_UNCAPPED_CONTRACT = """
VENDOR AGREEMENT
1. Liability.
Vendor shall have unlimited liability for all claims arising out of this Agreement.
Customer shall not be liable for any damages whatsoever.
"""

def test_defined_terms_analyzer():
    res = DefinedTermsAnalyzer.analyze(SAMPLE_CONTRACT_WITH_TERMS)
    assert res["total_definitions_found"] >= 2
    assert "Authorized Users" in res["defined_terms"] or "Service Downtime" in res["defined_terms"]
    # Dead definition detection
    assert res["dead_terms_count"] >= 1
    assert any("DeadDefinitionTerm" in term for term in res["dead_terms"])
    # Orphaned definition detection
    assert res["orphaned_terms_count"] >= 1
    assert any(o["term"] in ["Security Coordinator", "Incident Commander", "Executive Committee"] for o in res["orphaned_terms"])
    assert 0 <= res["consistency_health_score"] <= 100

def test_exposure_calculator_capped_contract():
    clauses = []
    res = ExposureCalculator.calculate_exposure(SAMPLE_CONTRACT_WITH_TERMS, clauses, estimated_acv=100000.0)
    assert res["estimated_acv_usd"] == 100000.0
    assert res["liability_multiplier"] == 1.0
    assert res["max_direct_exposure_usd"] == 100000.0
    assert res["consequential_damages_status"] == "MUTUAL_WAIVER_PROTECTED"
    assert res["balance_sheet_exposure_level"] == "FAVORABLE_BALANCED_EXPOSURE"
    assert res["financial_risk_score"] < 50.0

def test_exposure_calculator_uncapped_contract():
    clauses = []
    res = ExposureCalculator.calculate_exposure(SAMPLE_UNCAPPED_CONTRACT, clauses, estimated_acv=250000.0)
    assert res["liability_cap_type"] == "UNCAPPED_LIABILITY"
    assert res["liability_multiplier"] == "UNCAPPED"
    assert res["max_direct_exposure_usd"] is None
    assert res["balance_sheet_exposure_level"] == "CRITICAL_BALANCE_SHEET_EXPOSURE"
    assert res["financial_risk_score"] >= 90.0

def test_full_redliner_cuad_and_exposure_integration():
    report = ContractRedliner.analyze_document(SAMPLE_CONTRACT_WITH_TERMS, title="Term and Exposure Audit Test", estimated_acv=150000.0)
    assert report.total_clauses_analyzed >= 2
    assert report.defined_terms_report is not None
    assert report.exposure_analysis is not None
    assert report.exposure_analysis["estimated_acv_usd"] == 150000.0
    # CUAD categories present
    assert any(c.cuad_category == "CUAD_01_CAP_ON_LIABILITY" for c in report.clauses)
