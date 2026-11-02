import os
import io
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from backend.models.schemas import (
    ContractAnalysisRequest,
    ContractAuditReport
)
from backend.engine.redliner import ContractRedliner
from backend.engine.docx_exporter import DocxRedlineExporter
from backend.engine.playbook_rules import LegalPlaybook, PLAYBOOK_PROFILES
from backend.engine.legal_scraper import LegalPlaybookScraperEngine
from backend.engine.playbook_rag import PlaybookHybridRAGEngine

router = APIRouter(prefix="/api/v1", tags=["Contract Intelligence"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

scraper = LegalPlaybookScraperEngine()
scraper.run_playbook_scrape()
rag_engine = PlaybookHybridRAGEngine()

REPORTS_CACHE: Dict[str, ContractAuditReport] = {}

class CustomRuleRequest(BaseModel):
    domain: str
    required_criteria: str
    fallback_redline: str
    critical_risk_message: str

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Contract Risk Intelligence & Redlining Platform",
        "version": "1.0.0",
        "contracts_available": len([f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]) if os.path.exists(DATA_DIR) else 0,
        "active_profile": LegalPlaybook.ACTIVE_PROFILE,
        "playbook_rules_enforced": len(LegalPlaybook.PLAYBOOK),
        "scraped_rules_count": len(scraper.scraped_rules)
    }

@router.get("/playbook/profiles")
def list_playbook_profiles():
    """Returns the available negotiating playbook profiles (Vendor Balanced, Buyer Aggressive, Healthcare)."""
    return {
        "active_profile": LegalPlaybook.ACTIVE_PROFILE,
        "profiles": LegalPlaybook.get_profiles()
    }

@router.post("/playbook/profiles/{profile_id}/activate")
def activate_playbook_profile(profile_id: str):
    """Switches the active legal playbook posture and re-indexes the Hybrid RAG store."""
    success = LegalPlaybook.set_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Playbook profile '{profile_id}' not found.")
    rag_engine.rebuild()
    return {
        "status": "success",
        "active_profile": profile_id,
        "active_name": PLAYBOOK_PROFILES[profile_id]["name"],
        "rules_enforced": len(LegalPlaybook.PLAYBOOK)
    }

@router.get("/playbook/rules")
def get_playbook_rules():
    return {
        "playbook_version": "2026.1 Enterprise Legal Standard",
        "active_profile": LegalPlaybook.ACTIVE_PROFILE,
        "scraped_rules_history": scraper.scraped_rules,
        "rules": [
            {
                "domain": cat,
                "criteria": data["required_criteria"],
                "fallback_redline": data["fallback_redline"],
                "risk_message": data["critical_risk_message"]
            }
            for cat, data in LegalPlaybook.PLAYBOOK.items()
        ]
    }

@router.post("/playbook/scrape")
def trigger_legal_playbook_scrape():
    """Scrapes legal gazettes and model terms with BeautifulSoup4 and dynamically updates the Playbook."""
    res = scraper.run_playbook_scrape()
    rag_engine.rebuild()
    return res

@router.post("/playbook/custom-rule")
def add_custom_playbook_rule(request: CustomRuleRequest):
    """Allows users to customize, update, or append custom legal rules to the active Playbook."""
    LegalPlaybook.update_rule(
        domain=request.domain.upper(),
        required_criteria=request.required_criteria,
        fallback_redline=request.fallback_redline,
        critical_risk_message=request.critical_risk_message
    )
    rag_engine.rebuild()
    return {
        "status": "success",
        "message": f"Rule for {request.domain.upper()} updated in active playbook.",
        "rules_count": len(LegalPlaybook.PLAYBOOK)
    }

@router.get("/samples")
def list_samples() -> List[Dict[str, str]]:
    samples = []
    if os.path.exists(DATA_DIR):
        for filename in sorted(os.listdir(DATA_DIR)):
            if filename.endswith(".txt"):
                samples.append({
                    "id": filename,
                    "title": filename.replace(".txt", "").replace("_", " ").title()
                })
    return samples

@router.get("/samples/{sample_id}")
def get_sample_content(sample_id: str):
    file_path = os.path.join(DATA_DIR, sample_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return {"id": sample_id, "content": f.read()}

@router.post("/analyze", response_model=ContractAuditReport)
def analyze_contract(request: ContractAnalysisRequest):
    content = ""
    title = request.document_title or "Commercial Agreement Review"

    if request.sample_id:
        file_path = os.path.join(DATA_DIR, request.sample_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            title = request.sample_id.replace(".txt", "").replace("_", " ").title()
    elif request.contract_text:
        content = request.contract_text

    if not content:
        raise HTTPException(status_code=400, detail="Either 'contract_text' or 'sample_id' must be provided.")

    report = ContractRedliner.analyze_document(
        content,
        title=title,
        posture=request.posture,
        estimated_acv=request.estimated_acv or 100000.0
    )
    REPORTS_CACHE[report.contract_id] = report

    # Generate DOCX export automatically
    export_path = os.path.join(EXPORTS_DIR, f"{report.contract_id}_redline.docx")
    DocxRedlineExporter.export_redline(report, export_path)

    return report

@router.post("/upload-contract", response_model=ContractAuditReport)
async def upload_and_analyze_contract(file: UploadFile = File(...)):
    """
    Accepts uploaded contract files (.docx, .pdf, .txt),
    extracts the legal text, executes the 8-domain classifier,
    benchmarks against the active Playbook posture, and generates Word .docx redlines.
    """
    contents = await file.read()
    filename = file.filename.lower()
    text = ""

    if filename.endswith(".txt"):
        text = contents.decode("utf-8", errors="replace")

    elif filename.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(contents))
            full_paras = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        full_paras.append(row_text)
            text = "\n\n".join(full_paras)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse Word (.docx) file: {str(e)}")

    elif filename.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(contents))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF file: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="Only .docx, .pdf, and .txt files are supported for contract auditing.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Extracted document is empty or could not be read.")

    doc_title = file.filename.rsplit(".", 1)[0].replace("_", " ").title()
    report = ContractRedliner.analyze_document(text, title=doc_title)
    REPORTS_CACHE[report.contract_id] = report

    # Pre-generate Word redline
    export_path = os.path.join(EXPORTS_DIR, f"{report.contract_id}_redline.docx")
    DocxRedlineExporter.export_redline(report, export_path)

    return report

@router.get("/export-docx/{contract_id}")
def download_docx_redline(contract_id: str):
    export_path = os.path.join(EXPORTS_DIR, f"{contract_id}_redline.docx")
    if not os.path.exists(export_path):
        if contract_id in REPORTS_CACHE:
            DocxRedlineExporter.export_redline(REPORTS_CACHE[contract_id], export_path)
        else:
            raise HTTPException(status_code=404, detail=f"Redline export for {contract_id} not found.")

    return FileResponse(
        export_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"Redline_{contract_id}.docx"
    )
