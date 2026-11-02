"""
Quantitative Financial Exposure & Balance Sheet Liability Calculator.
Benchmarks contract liability terms against Annual Contract Value (ACV)
to calculate balance sheet exposure, super-cap multiples, and insurance requirements.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ExposureReport:
    estimated_acv_usd: float
    liability_cap_type: str
    liability_multiplier: float
    max_direct_exposure_usd: Optional[float]
    balance_sheet_exposure_level: str
    consequential_damages_status: str
    supercap_carveouts: List[str]
    insurance_recommendation: str
    cfo_summary: str
    financial_risk_score: float  # 0-100


class ExposureCalculator:
    """Calculates quantitative contract liability risk and balance sheet exposure."""

    @classmethod
    def calculate_exposure(
        cls,
        text: str,
        analyzed_clauses: List[Any],
        estimated_acv: float = 100000.0
    ) -> Dict[str, Any]:
        text_lower = text.lower()

        # 1. Determine Liability Cap Type and Multiplier
        cap_type = "STANDARD_1X_ACV"
        multiplier = 1.0
        max_exposure: Optional[float] = estimated_acv

        if "in no event shall the aggregate liability exceed" in text_lower or "fees paid" in text_lower:
            # Check for multiple of fees
            if "twelve (12) months" in text_lower or "12 months" in text_lower or "preceding 12 months" in text_lower:
                if "two times" in text_lower or "2x" in text_lower or "twice" in text_lower:
                    cap_type = "2X_FEES_CAP"
                    multiplier = 2.0
                    max_exposure = estimated_acv * 2.0
                elif "three times" in text_lower or "3x" in text_lower:
                    cap_type = "3X_FEES_CAP"
                    multiplier = 3.0
                    max_exposure = estimated_acv * 3.0
                elif "five times" in text_lower or "5x" in text_lower:
                    cap_type = "5X_FEES_CAP"
                    multiplier = 5.0
                    max_exposure = estimated_acv * 5.0
                else:
                    cap_type = "1X_FEES_PAID_12M"
                    multiplier = 1.0
                    max_exposure = estimated_acv
            else:
                cap_type = "AGGREGATE_FEES_CAP"
                multiplier = 1.0
                max_exposure = estimated_acv

        # Check for explicit uncapped or unlimited liability
        if "unlimited liability" in text_lower or "shall not be subject to any limitation of liability" in text_lower or (
            "liability" in text_lower and "uncapped" in text_lower
        ) or ("no limitation" in text_lower and "liability" in text_lower):
            cap_type = "UNCAPPED_LIABILITY"
            multiplier = 999.0
            max_exposure = None

        # Check for fixed dollar figures in limitation clauses
        fixed_dollar_match = re.search(r'(?:aggregate liability|maximum liability|liability cap)[^\.\n]{1,60}\$([0-9,]+)', text_lower)
        if fixed_dollar_match:
            try:
                amt = float(fixed_dollar_match.group(1).replace(",", ""))
                cap_type = f"FIXED_DOLLAR_CAP_${int(amt):,}"
                multiplier = round(amt / estimated_acv, 2)
                max_exposure = amt
            except ValueError:
                pass

        # 2. Consequential Damages Waiver Status
        consequential_status = "MUTUAL_WAIVER_PROTECTED"
        if "consequential" in text_lower or "indirect damages" in text_lower or "lost profits" in text_lower:
            if "neither party" in text_lower or "in no event shall either party" in text_lower:
                consequential_status = "MUTUAL_WAIVER_PROTECTED"
            elif "in no event shall vendor" in text_lower or "supplier shall not be liable" in text_lower:
                consequential_status = "UNILATERAL_ONE_SIDED_EXCLUSION"
            elif "customer shall not be liable" in text_lower:
                consequential_status = "UNILATERAL_BUYER_FAVORED"
            else:
                consequential_status = "PARTIAL_OR_AMBIGUOUS_WAIVER"
        else:
            consequential_status = "MISSING_CONSEQUENTIAL_DAMAGES_WAIVER"

        # 3. Supercap & Carve-Out Analysis
        carveouts = []
        if "indemnification" in text_lower and ("carve-out" in text_lower or "shall not apply to indemnification" in text_lower or "excluding liability under section" in text_lower or "not subject to" in text_lower):
            carveouts.append("Uncapped IP & Third-Party Indemnification Carve-out")
        
        if "data protection" in text_lower or "security breach" in text_lower or "confidentiality" in text_lower:
            if "confidentiality" in text_lower and ("unlimited" in text_lower or "not subject to the limitation" in text_lower):
                carveouts.append("Uncapped Confidentiality Breach Liability")
            if "data protection" in text_lower and ("super-cap" in text_lower or "2x" in text_lower or "3x" in text_lower):
                carveouts.append("2x-3x Super-Cap for Data Privacy / Cybersecurity Incidents")

        if not carveouts:
            if "shall not apply to" in text_lower:
                carveouts.append("General Statutory / Gross Negligence Carve-outs Only")
            else:
                carveouts.append("Standard Mutual Commercial Carve-outs")

        # 4. Exposure Level & Financial Risk Scoring
        if multiplier >= 10.0 or cap_type == "UNCAPPED_LIABILITY" or consequential_status == "MISSING_CONSEQUENTIAL_DAMAGES_WAIVER":
            exposure_level = "CRITICAL_BALANCE_SHEET_EXPOSURE"
            fin_score = 92.0
            insurance_rec = "Mandatory $10M+ Commercial General & Tech E&O Umbrella Policy before signing."
        elif multiplier >= 3.0 or consequential_status == "UNILATERAL_ONE_SIDED_EXCLUSION":
            exposure_level = "ELEVATED_FINANCIAL_EXPOSURE"
            fin_score = 68.0
            insurance_rec = "Requires $5M Tech E&O + Cyber Risk Rider to bridge super-cap carveouts."
        elif multiplier > 1.0:
            exposure_level = "MODERATE_EXPOSURE"
            fin_score = 42.0
            insurance_rec = "Standard $2M Commercial General Liability sufficient."
        else:
            exposure_level = "FAVORABLE_BALANCED_EXPOSURE"
            fin_score = 18.0
            insurance_rec = "Baseline corporate liability coverage adequate ($1M-$2M standard policy)."

        # 5. CFO / General Counsel Summary
        if max_exposure is not None:
            exposure_str = f"${max_exposure:,.0f} USD ({multiplier}x Annual Contract Value)"
        else:
            exposure_str = "UNCAPPED (Exposes entire corporate balance sheet)"

        cfo_summary = (
            f"Under estimated Annual Contract Value of ${estimated_acv:,.0f}, maximum direct liability is evaluated at "
            f"{exposure_str}. Consequential damages posture: {consequential_status.replace('_', ' ')}. "
            f"Risk Rating: {exposure_level.replace('_', ' ')} (Score: {fin_score}/100)."
        )

        return {
            "estimated_acv_usd": estimated_acv,
            "liability_cap_type": cap_type,
            "liability_multiplier": multiplier if multiplier != 999.0 else "UNCAPPED",
            "max_direct_exposure_usd": max_exposure,
            "balance_sheet_exposure_level": exposure_level,
            "consequential_damages_status": consequential_status,
            "supercap_carveouts": carveouts,
            "insurance_recommendation": insurance_rec,
            "cfo_summary": cfo_summary,
            "financial_risk_score": fin_score
        }
