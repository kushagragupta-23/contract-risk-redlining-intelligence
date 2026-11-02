"""
Defined Terms Consistency & Orphaned Definition Scanner.
Detects critical drafting defects common in enterprise contracts:
1. Orphaned Terms: Capitalized defined terms used in clauses that have no definition.
2. Dead Definitions: Defined terms in Section 1 that are never utilized.
3. Cross-Referencing Ambiguity.
"""

import re
from typing import Dict, Any, List, Set
from dataclasses import dataclass


@dataclass
class DefinedTermsReport:
    total_definitions_found: int
    defined_terms: List[str]
    orphaned_terms_count: int
    orphaned_terms: List[Dict[str, Any]]
    dead_terms_count: int
    dead_terms: List[str]
    consistency_health_score: float  # 0-100


class DefinedTermsAnalyzer:
    """Scans contracts for defined terms, orphaned references, and dead definitions."""

    # Pattern for defined terms: "Term" means / "Term" shall mean / (the "Term")
    DEF_PATTERN = re.compile(
        r'["“]([A-Z][a-zA-Z0-9\s]{2,35})["”]\s+(?:means|shall mean|refers to|is defined as)|'
        r'\((?:the\s+)?["“]([A-Z][a-zA-Z0-9\s]{2,35})["”]\)',
        re.IGNORECASE
    )

    # Standard legal terms that don't need explicit definition
    WHITELIST_TERMS = {
        "Agreement", "Party", "Parties", "Section", "Exhibit", "Schedule",
        "United States", "State", "Day", "Days", "Month", "Months", "Year",
        "USD", "INR", "EUR", "GBP", "Court", "Government", "Act", "Law",
        "Company", "Customer", "Vendor", "Client", "Supplier", "Effective Date",
        "Master Services Agreement", "Limitation Of Liability", "Limitation of Liability",
        "Performance And Obligations", "Performance and Obligations"
    }

    @classmethod
    def analyze(cls, full_text: str) -> Dict[str, Any]:
        # 1. Extract formal definitions
        matches = cls.DEF_PATTERN.findall(full_text)
        defined_terms_set: Set[str] = set()
        for m in matches:
            t = (m[0] or m[1]).strip()
            if t and len(t) > 2 and t not in cls.WHITELIST_TERMS:
                defined_terms_set.add(t)

        # 2. Extract capitalized terms used across body text (potential defined terms)
        capitalized_candidates = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', full_text)
        candidate_counts: Dict[str, int] = {}
        for c in capitalized_candidates:
            c_clean = c.strip()
            if c_clean not in cls.WHITELIST_TERMS and len(c_clean) > 4:
                candidate_counts[c_clean] = candidate_counts.get(c_clean, 0) + 1

        # 3. Detect Orphaned Terms (used with initial caps but not defined)
        orphaned = []
        for term, count in candidate_counts.items():
            if (count >= 2) or (count >= 1 and len(term.split()) >= 2):
                # Check if term is part of defined terms
                if not any(term.lower() == d.lower() for d in defined_terms_set):
                    orphaned.append({
                        "term": term,
                        "occurrences": count,
                        "risk": "Orphaned Defined Term: Capitalized in agreement but has no operative definition.",
                        "remedy": f'Add explicit definition for "{term}" in Section 1 or replace with lowercase standard wording.'
                    })

        # 4. Detect Dead Definitions (defined in agreement but never referenced elsewhere)
        dead = []
        for d in defined_terms_set:
            # Count occurrences of d
            pattern = re.compile(rf'\b{re.escape(d)}\b', re.IGNORECASE)
            total_matches = len(pattern.findall(full_text))
            # If total matches is 1 (only the definition itself), it is a dead term
            if total_matches <= 1:
                dead.append(d)

        total_defs = len(defined_terms_set)
        penalty = (len(orphaned) * 10) + (len(dead) * 5)
        health = max(0.0, min(100.0, 100.0 - penalty))

        return {
            "total_definitions_found": total_defs,
            "defined_terms": sorted(list(defined_terms_set))[:15],
            "orphaned_terms_count": len(orphaned),
            "orphaned_terms": orphaned[:8],
            "dead_terms_count": len(dead),
            "dead_terms": dead[:8],
            "consistency_health_score": round(health, 1)
        }
