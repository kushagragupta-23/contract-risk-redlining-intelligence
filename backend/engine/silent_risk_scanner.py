"""
Silent Risk & Omission Scanner for Commercial Agreements.
Detects missing mandatory protections that expose the enterprise to hidden legal liability:
1. Data Protection & Security Incident Notification (GDPR/CCPA/HIPAA)
2. Audit Rights & SOC 2 Compliance Verification
3. Force Majeure & Epidemic Carve-Outs
4. Post-Termination Confidentiality Survival (3-5 Years)
5. Governing Law, Exclusive Venue & Jury Waiver
"""

import re
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class MissingProtection:
    category: str
    severity: str        # CRITICAL, HIGH, MEDIUM
    risk_title: str
    impact_rationale: str
    recommended_clause_title: str
    recommended_clause_text: str
    talking_point_for_counsel: str


ESSENTIAL_PROTECTION_SPEC = [
    {
        "category": "DATA_PRIVACY_SECURITY",
        "severity": "CRITICAL",
        "keywords": ["data protection", "gdpr", "personal data", "security incident", "data breach", "dpa", "hipaa", "privacy"],
        "risk_title": "Omission of Data Protection & 72-Hour Security Breach Notification",
        "impact_rationale": "Contract contains no formal Data Processing Addendum (DPA) or security incident notification timeline, exposing Company to regulatory fines up to 4% global turnover under GDPR/CCPA.",
        "recommended_clause_title": "Data Privacy & Security Breach Notification Clause",
        "recommended_clause_text": "Vendor shall maintain reasonable and appropriate administrative, physical, and technical safeguards compliant with ISO 27001 / SOC 2 Type II to protect Customer Data. In the event of a confirmed security incident or unauthorized access to Customer Data, Vendor shall notify Customer in writing within seventy-two (72) hours of discovery and take immediate remedial action at its sole expense.",
        "talking_point_for_counsel": "Standard enterprise vendor onboarding requirement under GDPR Article 33 and US state privacy laws. Unacceptable to proceed without breach notification commitment."
    },
    {
        "category": "AUDIT_COMPLIANCE",
        "severity": "HIGH",
        "keywords": ["audit rights", "inspection", "soc 2", "books and records", "right to audit", "compliance verification"],
        "risk_title": "Omission of Customer Security & Compliance Audit Rights",
        "impact_rationale": "Company has no contractual right to inspect counterparty security certifications or conduct annual compliance audits.",
        "recommended_clause_title": "Annual Security & Compliance Audit Clause",
        "recommended_clause_text": "Upon thirty (30) days prior written notice, Customer (or an independent accredited third-party auditor) shall have the right, at Customer's expense, to inspect Vendor's security posture, SOC 2 Type II audit reports, and compliance records once per calendar year during normal business hours.",
        "talking_point_for_counsel": "Mandated by enterprise governance and third-party vendor risk management frameworks."
    },
    {
        "category": "CONFIDENTIALITY_SURVIVAL",
        "severity": "HIGH",
        "keywords": ["confidentiality survive", "survival", "survive termination", "trade secret perpetual"],
        "risk_title": "Omission of Post-Termination Confidentiality Survival",
        "impact_rationale": "Nondisclosure obligations may extinguish immediately upon contract termination, leaving proprietary trade secrets unprotected.",
        "recommended_clause_title": "Survival of Nondisclosure Obligations",
        "recommended_clause_text": "The confidentiality obligations set forth herein shall survive the expiration or termination of this Agreement for a period of five (5) years; provided that with respect to any information constituting a trade secret under applicable law, such obligations shall survive in perpetuity.",
        "talking_point_for_counsel": "Universal market standard. Trade secrets cannot lose protection simply because a commercial contract term expires."
    },
    {
        "category": "FORCE_MAJEURE",
        "severity": "MEDIUM",
        "keywords": ["force majeure", "act of god", "unforeseeable", "epidemic", "pandemic"],
        "risk_title": "Omission of Force Majeure with Written Notice & Payment Exclusion",
        "impact_rationale": "Absence of force majeure rules creates ambiguity during macro supply-chain disruptions, grid outages, or declared public health emergencies.",
        "recommended_clause_title": "Balanced Force Majeure Clause",
        "recommended_clause_text": "Neither party shall be liable for failure or delay in performing obligations (excluding payment of accrued fees) due to causes beyond its reasonable control, including acts of God, war, pandemic, or government embargo, provided prompt written notice is delivered within five (5) business days.",
        "talking_point_for_counsel": "Standard clause balancing operational relief while clarifying that monetary payment obligations are not excused."
    },
    {
        "category": "GOVERNING_LAW_JURISDICTION",
        "severity": "MEDIUM",
        "keywords": ["governing law", "jurisdiction", "exclusive venue", "courts of", "dispute resolution"],
        "risk_title": "Omission of Explicit Governing Law & Venue Selection",
        "impact_rationale": "Leaves dispute venue open to costly jurisdictional forum-shopping and multi-state conflict-of-law litigation.",
        "recommended_clause_title": "Governing Law & Forum Selection Clause",
        "recommended_clause_text": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict-of-laws principles. Each party irrevocably submits to the exclusive personal jurisdiction and venue of the state and federal courts located in Wilmington, Delaware.",
        "talking_point_for_counsel": "Essential for litigation certainty and predictable legal interpretation."
    }
]


class SilentRiskScanner:
    """Scans contract text for missing essential legal protections."""

    @classmethod
    def scan_for_omissions(cls, contract_text: str) -> List[Dict[str, Any]]:
        text_lower = contract_text.lower()
        omissions = []

        for spec in ESSENTIAL_PROTECTION_SPEC:
            has_match = any(kw in text_lower for kw in spec["keywords"])
            if not has_match:
                omissions.append({
                    "category": spec["category"],
                    "severity": spec["severity"],
                    "risk_title": spec["risk_title"],
                    "impact_rationale": spec["impact_rationale"],
                    "recommended_clause_title": spec["recommended_clause_title"],
                    "recommended_clause_text": spec["recommended_clause_text"],
                    "talking_point_for_counsel": spec["talking_point_for_counsel"]
                })

        return omissions
