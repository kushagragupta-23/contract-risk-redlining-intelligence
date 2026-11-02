from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

RiskLevel = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "ACCEPTABLE"]
ClauseCategory = Literal[
    "LIMITATION_OF_LIABILITY",
    "INDEMNIFICATION",
    "TERMINATION",
    "INTELLECTUAL_PROPERTY",
    "CONFIDENTIALITY",
    "GOVERNING_LAW",
    "NON_SOLICITATION",
    "WARRANTY_DISCLAIMER",
    "DATA_PRIVACY_SECURITY",
    "AUDIT_RIGHTS",
    "GENERAL"
]

class AnalyzedClause(BaseModel):
    clause_id: str
    section_title: str
    category: ClauseCategory
    cuad_category: Optional[str] = Field(default=None, description="Official Berkeley CUAD 41-Taxonomy Clause Label")
    original_text: str
    risk_level: RiskLevel
    risk_reasoning: str
    playbook_rule_violated: Optional[str] = None
    suggested_redline: str
    compromise_fallback: Optional[str] = None
    walkaway_threshold: Optional[str] = None
    talking_points: List[str] = []
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)

class MissingProtectionItem(BaseModel):
    category: str
    severity: str
    risk_title: str
    impact_rationale: str
    recommended_clause_title: str
    recommended_clause_text: str
    talking_point_for_counsel: str

class ContractAuditReport(BaseModel):
    contract_id: str
    document_title: str
    analyzed_at: str
    total_clauses_analyzed: int
    composite_risk_score: float = Field(description="Normalized 0-100 composite risk score")
    contract_health_grade: str = Field(default="C", description="Executive A/B/C/D/F rating")
    overall_risk: RiskLevel
    negotiation_posture: str = "vendor_balanced"
    critical_count: int
    high_count: int
    medium_count: int
    acceptable_count: int
    missing_protections: List[MissingProtectionItem] = []
    defined_terms_report: Optional[Dict[str, Any]] = None
    exposure_analysis: Optional[Dict[str, Any]] = None
    clauses: List[AnalyzedClause]
    executive_summary: str
    redline_docx_available: bool = False

class ContractAnalysisRequest(BaseModel):
    contract_text: Optional[str] = None
    sample_id: Optional[str] = None
    document_title: Optional[str] = "Service Agreement Review"
    posture: Optional[str] = "vendor_balanced"
    estimated_acv: Optional[float] = 100000.0
