import uuid
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any, Optional
from backend.models.schemas import (
    AnalyzedClause,
    ContractAuditReport,
    MissingProtectionItem,
    RiskLevel
)
from .clause_classifier import ClauseClassifier
from .playbook_rules import LegalPlaybook
from .silent_risk_scanner import SilentRiskScanner
from .defined_terms_analyzer import DefinedTermsAnalyzer
from .exposure_calculator import ExposureCalculator

class ContractRedliner:
    """
    Evaluates segmented contract clauses against active negotiating playbook rules.
    Runs silent risk omission scanning, fallback hierarchy generation, health grading,
    CUAD taxonomy tagging, defined terms integrity auditing, and financial exposure calculations.
    """

    CUAD_TAXONOMY_MAP: Dict[str, str] = {
        "LIMITATION_OF_LIABILITY": "CUAD_01_CAP_ON_LIABILITY",
        "INDEMNIFICATION": "CUAD_04_INDEMNIFICATION",
        "TERMINATION": "CUAD_20_TERMINATION_FOR_CONVENIENCE",
        "INTELLECTUAL_PROPERTY": "CUAD_15_IP_OWNERSHIP_ASSIGNMENT",
        "CONFIDENTIALITY": "CUAD_12_CONFIDENTIALITY_RESTRICTIONS",
        "GOVERNING_LAW": "CUAD_03_GOVERNING_LAW_AND_VENUE",
        "NON_SOLICITATION": "CUAD_18_NON_SOLICITATION_OF_EMPLOYEES",
        "WARRANTY_DISCLAIMER": "CUAD_38_WARRANTY_DISCLAIMER",
        "DATA_PRIVACY_SECURITY": "CUAD_10_DATA_SECURITY_AND_PRIVACY",
        "AUDIT_RIGHTS": "CUAD_07_AUDIT_RIGHTS",
        "GENERAL": "CUAD_41_GENERAL_PROVISIONS",
    }

    @classmethod
    def analyze_document(
        cls,
        text: str,
        title: str = "Agreement Audit",
        posture: Optional[str] = None,
        estimated_acv: float = 100000.0
    ) -> ContractAuditReport:
        if posture:
            LegalPlaybook.set_profile(posture)

        raw_clauses = ClauseClassifier.segment_contract(text)
        analyzed_clauses: List[AnalyzedClause] = []

        critical_count = 0
        high_count = 0
        medium_count = 0
        acceptable_count = 0

        for item in raw_clauses:
            cat = item["category"]
            clause_text = item["raw_text"]
            cid = item["clause_id"]
            sec_title = item["title"]

            eval_res = cls._evaluate_clause(cat, clause_text)

            risk_level = eval_res["risk_level"]
            if risk_level == "CRITICAL":
                critical_count += 1
            elif risk_level == "HIGH":
                high_count += 1
            elif risk_level == "MEDIUM":
                medium_count += 1
            else:
                acceptable_count += 1

            cuad_tag = cls.CUAD_TAXONOMY_MAP.get(cat, "CUAD_41_GENERAL_PROVISIONS")

            analyzed_clauses.append(AnalyzedClause(
                clause_id=cid,
                section_title=sec_title,
                category=cat,
                cuad_category=cuad_tag,
                original_text=clause_text,
                risk_level=risk_level,
                risk_reasoning=eval_res["reasoning"],
                playbook_rule_violated=eval_res["rule_violated"],
                suggested_redline=eval_res["suggested_redline"],
                compromise_fallback=eval_res.get("compromise_fallback"),
                walkaway_threshold=eval_res.get("walkaway_threshold"),
                talking_points=eval_res.get("talking_points", []),
                confidence_score=item["confidence"]
            ))

        # Scan for Missing Essential Protections (Silent Risks)
        raw_omissions = SilentRiskScanner.scan_for_omissions(text)
        missing_protections = [MissingProtectionItem(**o) for o in raw_omissions]

        # Scan for Defined Terms Consistency & Orphaned References
        defined_terms_report = DefinedTermsAnalyzer.analyze(text)

        # Calculate Quantitative Financial Exposure vs ACV
        exposure_analysis = ExposureCalculator.calculate_exposure(text, analyzed_clauses, estimated_acv=estimated_acv)

        total_clauses = max(1, len(analyzed_clauses))
        # Composite risk formula: Critical = 35pts, High = 20pts, Medium = 10pts, Omission = 15pts
        omission_penalty = len(missing_protections) * 12
        raw_risk_pts = (critical_count * 35) + (high_count * 20) + (medium_count * 10) + omission_penalty
        composite_score = min(100.0, round((raw_risk_pts / ((total_clauses * 25) + 30)) * 100, 1))

        if critical_count > 0 or composite_score >= 70:
            overall_risk: RiskLevel = "CRITICAL"
        elif high_count > 0 or composite_score >= 45:
            overall_risk = "HIGH"
        elif medium_count > 0 or composite_score >= 25:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "ACCEPTABLE"

        # Calculate Contract Health Grade (A/B/C/D/F)
        if composite_score <= 15.0 and len(missing_protections) == 0:
            health_grade = "Grade A (Execution Ready)"
        elif composite_score <= 35.0:
            health_grade = "Grade B (Minor Market Revisions)"
        elif composite_score <= 65.0:
            health_grade = "Grade C (Substantial Redline Required)"
        elif composite_score <= 85.0:
            health_grade = "Grade D (High Legal Jeopardy)"
        else:
            health_grade = "Grade F (Walk-Away / Extreme Risk)"

        summary = (
            f"Analyzed {total_clauses} clauses across key commercial domains under {LegalPlaybook.ACTIVE_PROFILE} posture. "
            f"Detected {critical_count} critical risks, {high_count} high risks, and {len(missing_protections)} missing essential protections. "
            f"Drafting Integrity: {defined_terms_report.get('consistency_health_score', 100)}/100 ({defined_terms_report.get('orphaned_terms_count', 0)} orphaned terms). "
            f"Financial Exposure: {exposure_analysis.get('balance_sheet_exposure_level', 'STANDARD')}. "
            f"Overall health rating: {health_grade} with composite exposure index {composite_score}/100."
        )

        return ContractAuditReport(
            contract_id=f"CTR-{uuid.uuid4().hex[:8].upper()}",
            document_title=title,
            analyzed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_clauses_analyzed=total_clauses,
            composite_risk_score=composite_score,
            contract_health_grade=health_grade,
            overall_risk=overall_risk,
            negotiation_posture=LegalPlaybook.ACTIVE_PROFILE,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            acceptable_count=acceptable_count,
            missing_protections=missing_protections,
            defined_terms_report=defined_terms_report,
            exposure_analysis=exposure_analysis,
            clauses=analyzed_clauses,
            executive_summary=summary,
            redline_docx_available=True
        )

    @classmethod
    def _evaluate_clause(cls, category: str, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        playbook = LegalPlaybook.PLAYBOOK.get(category)

        if not playbook:
            return {
                "risk_level": "ACCEPTABLE",
                "reasoning": "Standard operational boilerplate; conforms to baseline contracting standards.",
                "rule_violated": None,
                "suggested_redline": text,
                "compromise_fallback": None,
                "walkaway_threshold": None,
                "talking_points": []
            }

        unacceptable = playbook.get("unacceptable_indicators", [])
        is_violated = any(ind in text_lower for ind in unacceptable)

        if is_violated:
            return {
                "risk_level": "CRITICAL",
                "reasoning": playbook.get("critical_risk_message", "Predatory deviation from standard negotiating position."),
                "rule_violated": playbook.get("required_criteria"),
                "suggested_redline": playbook.get("fallback_redline", text),
                "compromise_fallback": playbook.get("compromise_fallback", playbook.get("fallback_redline", text)),
                "walkaway_threshold": playbook.get("walkaway_threshold", "Uncapped risk exposure."),
                "talking_points": playbook.get("talking_points", ["Standard commercial balance required."])
            }

        # Check soft criteria
        req = playbook.get("required_criteria", "").lower()
        if "mutual" in req and "mutual" not in text_lower:
            return {
                "risk_level": "HIGH",
                "reasoning": "Unilateral obligation detected. Contract lacks mandatory mutuality required by corporate policy.",
                "rule_violated": playbook.get("required_criteria"),
                "suggested_redline": playbook.get("fallback_redline", text),
                "compromise_fallback": playbook.get("compromise_fallback"),
                "walkaway_threshold": playbook.get("walkaway_threshold"),
                "talking_points": playbook.get("talking_points", [])
            }

        return {
            "risk_level": "ACCEPTABLE",
            "reasoning": "Clause aligns with active legal playbook parameters and liability risk threshold.",
            "rule_violated": None,
            "suggested_redline": text,
            "compromise_fallback": None,
            "walkaway_threshold": None,
            "talking_points": []
        }
