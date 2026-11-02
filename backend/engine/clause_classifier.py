import re
from typing import List, Dict, Any
from backend.models.schemas import ClauseCategory

class ClauseClassifier:
    """Classifies contract text paragraphs into standardized legal clause categories."""

    CATEGORY_PATTERNS = [
        ("LIMITATION_OF_LIABILITY", [
            r'limitation of liability', r'liability cap', r'consequential damages',
            r'aggregate liability', r'maximum liability', r'in no event shall.*liable'
        ]),
        ("INDEMNIFICATION", [
            r'indemnif', r'hold harmless', r'defend and indemnify', r'indemnity obligations'
        ]),
        ("TERMINATION", [
            r'termination', r'term and termination', r'terminate for cause',
            r'terminate for convenience', r'survival upon termination'
        ]),
        ("INTELLECTUAL_PROPERTY", [
            r'intellectual property', r'work for hire', r'ownership of deliverables',
            r'proprietary rights', r'patent rights', r'background ip'
        ]),
        ("CONFIDENTIALITY", [
            r'confidentiality', r'confidential information', r'non-disclosure', r'proprietary information'
        ]),
        ("NON_SOLICITATION", [
            r'non-solicitation', r'solicit.*employee', r'hire or entice away', r'non-compete'
        ]),
        ("GOVERNING_LAW", [
            r'governing law', r'jurisdiction', r'dispute resolution', r'arbitration', r'venue'
        ]),
        ("WARRANTY_DISCLAIMER", [
            r'warranty', r'disclaimer of warranties', r'as is', r'merchantability', r'fitness for a particular purpose'
        ])
    ]

    @classmethod
    def segment_contract(cls, text: str) -> List[Dict[str, Any]]:
        # Normalize linebreaks
        text = text.replace('\r\n', '\n')

        # Split on numbered sections or clause titles
        section_splits = re.split(r'\n(?=(?:[0-9]{1,2}\.|\bSection\s+[0-9]|\bArticle\s+[0-9]|\b[A-Z\s]{4,}:))', text)

        clauses = []
        clause_counter = 1
        for sec in section_splits:
            clean = sec.strip()
            if len(clean) < 30:
                continue

            lines = clean.split('\n')
            first_line = lines[0].strip()
            body_text = "\n".join(lines[1:]).strip() if len(lines) > 1 else clean

            # Extract title if present
            title = first_line[:60] if len(first_line) <= 80 else f"Clause {clause_counter}"

            category, confidence = cls.classify_text(clean)

            clauses.append({
                "clause_id": f"CLAUSE_{clause_counter:02d}",
                "title": title,
                "raw_text": clean,
                "category": category,
                "confidence": confidence
            })
            clause_counter += 1

        return clauses

    @classmethod
    def classify_text(cls, text: str) -> tuple[ClauseCategory, float]:
        text_lower = text.lower()

        for category, patterns in cls.CATEGORY_PATTERNS:
            for pat in patterns:
                if re.search(pat, text_lower):
                    return category, 0.96

        return "GENERAL", 0.70

