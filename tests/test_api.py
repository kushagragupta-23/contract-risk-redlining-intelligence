import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_samples():
    res = client.get("/api/v1/samples")
    assert res.status_code == 200
    assert len(res.json()) >= 3

def test_analyze_contract():
    payload = {
        "contract_text": (
            "1. Limitation of Liability\n"
            "In no event shall liability be capped for any breach under this Agreement, and Vendor shall have unlimited liability.\n\n"
            "2. Governing Law\n"
            "This Agreement shall be governed exclusively by the courts of New York with foreign jurisdiction with no arbitration."
        ),
        "document_title": "Vendor NDA Test"
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "contract_id" in data
    assert data["critical_count"] >= 1
    assert len(data["clauses"]) >= 2

    # Check DOCX export endpoint
    cid = data["contract_id"]
    docx_res = client.get(f"/api/v1/export-docx/{cid}")
    assert docx_res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument" in docx_res.headers["content-type"]



def test_upload_contract_txt():
    sample_text = "1. Limitation of Liability\nIn no event shall liability be capped under this Agreement, and Vendor shall have unlimited liability.\n"
    res = client.post("/api/v1/upload-contract", files={"file": ("contract.txt", sample_text.encode("utf-8"), "text/plain")})
    assert res.status_code == 200
    data = res.json()
    assert "contract_id" in data
    assert data["critical_count"] >= 1

def test_playbook_profiles():
    res = client.get("/api/v1/playbook/profiles")
    assert res.status_code == 200
    data = res.json()
    assert "profiles" in data
    assert len(data["profiles"]) >= 3

def test_playbook_scrape():
    res = client.post("/api/v1/playbook/scrape")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

def test_playbook_custom_rule():
    payload = {
        "domain": "DATA_SECURITY",
        "required_criteria": "SOC2 Type II audit report must be provided annually.",
        "fallback_redline": "Vendor shall maintain SOC2 Type II certification and provide reports annually.",
        "critical_risk_message": "Missing SOC2 audit protection."
    }
    res = client.post("/api/v1/playbook/custom-rule", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "success"
