import os
import tempfile
import pytest
from backend.engine.redliner import ContractRedliner
from backend.engine.docx_exporter import DocxRedlineExporter

SAMPLE_HIGH_RISK = """
1. Limitation of Liability
In no event shall liability be capped for any breach under this Agreement, and Vendor shall have unlimited liability for all damages.

2. Confidentiality
Each party agrees to hold all disclosed trade secrets in strict confidence for three years.
"""

def test_contract_redliner_risk_scoring():
    report = ContractRedliner.analyze_document(SAMPLE_HIGH_RISK, "High Risk NDA")
    assert report.total_clauses_analyzed >= 2
    assert report.critical_count >= 1
    assert report.overall_risk in ["CRITICAL", "HIGH"]
    assert report.composite_risk_score > 30.0

def test_docx_export():
    report = ContractRedliner.analyze_document(SAMPLE_HIGH_RISK, "Export Test Contract")
    with tempfile.TemporaryDirectory() as temp_dir:
        out_file = os.path.join(temp_dir, "test_redline.docx")
        exported_path = DocxRedlineExporter.export_redline(report, out_file)

        assert os.path.exists(exported_path)
        assert os.path.getsize(exported_path) > 1000
