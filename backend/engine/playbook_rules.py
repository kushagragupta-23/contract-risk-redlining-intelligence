from typing import Dict, Any, Tuple, List

# Multiple distinct commercial legal playbooks for different negotiating postures
PLAYBOOK_PROFILES = {
    "vendor_balanced": {
        "name": "Standard Vendor SaaS Playbook (Balanced v2.6)",
        "description": "Standard SaaS market terms balancing liability caps, mutual indemnities, and IP retention.",
        "rules": {
            "LIMITATION_OF_LIABILITY": {
                "unacceptable_indicators": ["unlimited liability", "in no event shall liability be capped", "solely liable for all indirect", "without limitation", "no cap on damages"],
                "required_criteria": "Liability must be mutual and capped at total fees paid in preceding 12 months.",
                "fallback_redline": "Neither party's aggregate liability arising out of or related to this Agreement shall exceed the total fees paid or payable by Client in the twelve (12) months preceding the incident giving rise to liability. In no event shall either party be liable for indirect, special, incidental, or consequential damages.",
                "compromise_fallback": "Either party's aggregate liability shall be capped at two times (2x) the total fees paid in the preceding twelve (12) months. Standard exclusion of consequential damages applies.",
                "walkaway_threshold": "Uncapped liability for commercial claims or consequential damages without mutual cap.",
                "talking_points": [
                    "SaaS market standard: 94% of enterprise tech MSAs cap liability at 12 months fees paid.",
                    "Uncapped liability is uninsurable under standard Errors & Omissions (E&O) and cyber risk policies.",
                    "Mutual waiver of consequential damages protects both parties from speculative lost profit claims."
                ],
                "critical_risk_message": "Uncapped or unilateral liability exposure detected. Company is exposed to unlimited damages."
            },
            "INDEMNIFICATION": {
                "unacceptable_indicators": ["indemnify, defend, and hold harmless against any and all claims whatsoever", "solely indemnify", "regardless of negligence", "indemnify against all losses"],
                "required_criteria": "Indemnity must be mutual, capped, and limited to direct third-party IP infringement or gross negligence.",
                "fallback_redline": "Each party shall defend, indemnify, and hold harmless the other party from and against direct claims, damages, and reasonable legal costs resulting from third-party claims alleging that the indemnifying party's technology or deliverable infringes a valid patent, copyright, or trademark, provided prompt written notice of such claim is provided.",
                "compromise_fallback": "Vendor indemnifies Customer for third-party IP infringement subject to a super-cap of three times (3x) contract value, conditioned upon prompt notice and sole defense control.",
                "walkaway_threshold": "Indemnification for strict liability, counterparty breach, or uncapped claims without control of defense.",
                "talking_points": [
                    "Indemnity must be limited to direct third-party claims alleging intellectual property infringement.",
                    "Indemnifying party must have sole right to control defense and settlement to manage legal costs.",
                    "Customer must provide prompt notice; delayed notice prejudice waives indemnification rights."
                ],
                "critical_risk_message": "Broad, unilateral indemnification covering uncapped indirect claims or strict liability."
            },
            "TERMINATION": {
                "unacceptable_indicators": ["terminate immediately without notice", "terminate at sole discretion without cure period", "no right to terminate"],
                "required_criteria": "Termination for convenience requires at least 30 days prior written notice. Termination for cause requires 30-day cure period.",
                "fallback_redline": "Either party may terminate this Agreement: (a) for convenience upon thirty (30) days prior written notice to the other party; or (b) immediately upon written notice if the other party breaches any material term and fails to cure such breach within thirty (30) days of receipt of notice.",
                "compromise_fallback": "Termination for convenience requires sixty (60) days prior written notice plus payment of pro-rata committed implementation fees.",
                "walkaway_threshold": "Immediate unilateral termination without cause or cure rights.",
                "talking_points": [
                    "30-day cure period allows both operational teams to remediate technical defects before legal termination.",
                    "Termination for convenience must provide sufficient transition window to prevent service disruptions."
                ],
                "critical_risk_message": "Unilateral immediate termination without cause or cure rights creates operational vulnerability."
            },
            "INTELLECTUAL_PROPERTY": {
                "unacceptable_indicators": ["all intellectual property developed by either party shall immediately become sole property of client", "transfer all background ip", "perpetual irrevocable assignment of preexisting materials"],
                "required_criteria": "Background IP must remain with original creator. Work Product assignment is conditioned on full payment.",
                "fallback_redline": "Each party retains all right, title, and interest in its preexisting intellectual property. Conditioned upon receipt of full payment, Vendor assigns to Client all right, title, and interest in bespoke deliverables created specifically for Client under an executed Statement of Work.",
                "compromise_fallback": "Vendor grants an irrevocable, perpetual, royalty-free non-exclusive license to use background IP embedded within the deliverables.",
                "walkaway_threshold": "Assignment of vendor preexisting background source code, tools, or algorithms.",
                "talking_points": [
                    "Vendor cannot assign core software engine or developer tooling used across multiple enterprise clients.",
                    "Client receives full exclusive ownership of custom bespoke deliverables once invoices are settled."
                ],
                "critical_risk_message": "Overreaching IP assignment threatens proprietary background code, tools, and libraries."
            },
            "NON_COMPETE": {
                "unacceptable_indicators": ["shall not directly or indirectly compete", "prohibited from developing competing products", "worldwide non-compete"],
                "required_criteria": "Post-termination non-competes are void under FTC 16 CFR Part 910. Strike out completely; retain customer non-solicit only.",
                "fallback_redline": "[DELETED - Prohibited under FTC 16 CFR Part 910]. Neither party shall actively solicit for employment the key personnel of the other party during the term and for six (6) months thereafter without prior written consent.",
                "compromise_fallback": "Vendor agrees not to build customized clones of Client's proprietary business logic for direct named competitors for a period of 6 months.",
                "walkaway_threshold": "General commercial non-competes restricting company from serving industry sector.",
                "talking_points": [
                    "Federal Trade Commission final rule 16 CFR Part 910 classifies non-competes as unfair competition.",
                    "Software vendors must remain free to serve their broader enterprise client vertical."
                ],
                "critical_risk_message": "Overly broad non-compete covenant unenforceable under FTC final rule and restricts core market operations."
            }
        }
    },
    "buyer_aggressive": {
        "name": "Enterprise Buyer / Customer Defensive Playbook",
        "description": "Aggressive customer-side playbook demanding uncapped vendor IP indemnities, 2x fee super-caps, and work-for-hire IP.",
        "rules": {
            "LIMITATION_OF_LIABILITY": {
                "unacceptable_indicators": ["cap customer liability to fees", "waiver of customer consequential damages"],
                "required_criteria": "Vendor liability for breach of confidentiality and data security must be uncapped or capped at minimum 3x annual contract value.",
                "fallback_redline": "Customer's liability hereunder shall not exceed the fees paid in the preceding six (6) months. Vendor's liability for data security breaches, gross negligence, or confidentiality shall be subject to a super-cap equal to three times (3x) the total annual contract value.",
                "compromise_fallback": "Vendor liability for data security and confidentiality capped at $5,000,000 USD or 2x fees paid, whichever is higher.",
                "walkaway_threshold": "No super-cap for customer data loss or confidentiality leaks.",
                "talking_points": [
                    "Customer entrusts critical commercial and personal data; standard 1x fee cap is completely inadequate.",
                    "Data breaches carry forensic, legal notification, and regulatory costs far exceeding subscription fees."
                ],
                "critical_risk_message": "Inadequate liability cap for vendor failure to protect customer data."
            },
            "INDEMNIFICATION": {
                "unacceptable_indicators": ["customer indemnifies vendor for use", "sole remedy clause"],
                "required_criteria": "Vendor must unconditionally indemnify Customer against all third-party patent, copyright, and trade secret claims with no dollar limitation.",
                "fallback_redline": "Vendor shall defend, indemnify, and hold harmless Customer, its directors, officers, and end users against any and all claims, damages, liabilities, and defense costs arising out of any third-party claim alleging intellectual property infringement.",
                "compromise_fallback": "Vendor indemnifies Customer for IP infringement; Customer provides prompt notice and reasonable cooperation.",
                "walkaway_threshold": "Customer required to indemnify vendor for standard use of vendor's software.",
                "talking_points": [
                    "Vendor has full visibility and control over its codebase; Customer cannot bear IP infringement risk."
                ],
                "critical_risk_message": "Indemnity lacks broad customer defense protections."
            },
            "INTELLECTUAL_PROPERTY": {
                "unacceptable_indicators": ["vendor retains all deliverables", "license only to customer"],
                "required_criteria": "Customer must own all deliverables, configurations, models, and work product developed under the agreement as works made for hire.",
                "fallback_redline": "Customer shall be the sole and exclusive owner of all deliverables, custom software, reports, and IP created under this Agreement, which shall be deemed work made for hire.",
                "compromise_fallback": "Customer owns all bespoke outputs and data; Vendor retains underlying generic libraries.",
                "walkaway_threshold": "Vendor retaining ownership of customer-funded bespoke workflows or models.",
                "talking_points": [
                    "Funded development must vest in Customer as work made for hire."
                ],
                "critical_risk_message": "Contract fails to assign work product ownership to Customer."
            },
            "TERMINATION": {
                "unacceptable_indicators": ["customer cannot terminate for convenience", "termination fee applies"],
                "required_criteria": "Customer may terminate for convenience with 15 days notice without early termination penalty.",
                "fallback_redline": "Customer may terminate this Agreement or any SOW at any time, with or without cause, upon fifteen (15) days written notice without penalty.",
                "compromise_fallback": "Termination for convenience with thirty (30) days notice with no penalty fees.",
                "walkaway_threshold": "Strict lock-in with mandatory acceleration of all unbilled multi-year fees.",
                "talking_points": [
                    "Enterprise flexibility requires uninhibited exit rights if vendor roadmap changes."
                ],
                "critical_risk_message": "Restrictions on Customer's unilateral right to exit the relationship."
            }
        }
    },
    "healthcare_regulated": {
        "name": "Healthcare & Regulated Data Playbook (HIPAA / DPA)",
        "description": "Strict compliance playbook for HIPAA, Protected Health Information (PHI), and SOC2 cloud vendors.",
        "rules": {
            "LIMITATION_OF_LIABILITY": {
                "unacceptable_indicators": ["cap liability for hipaa breach", "consequential damages waived for data breach"],
                "required_criteria": "Liability for unauthorized PHI disclosure or regulatory fines under HIPAA/HITECH must be completely uncapped.",
                "fallback_redline": "The limitations of liability shall not apply to either party's breach of its data protection, confidentiality, or Business Associate Agreement obligations, nor to statutory fines imposed under HIPAA or HITECH.",
                "compromise_fallback": "HIPAA breach liability capped at standalone super-cap equal to Vendor's maximum professional cyber liability insurance policy ($10M).",
                "walkaway_threshold": "Any cap on liability that applies to HIPAA fines or statutory health data violations.",
                "talking_points": [
                    "HHS Office for Civil Rights fines cannot be limited by private commercial contracts.",
                    "Covered Entity faces mandatory regulatory sanctions if Business Associate breaches PHI."
                ],
                "critical_risk_message": "Illegal attempt to cap liability for HIPAA data breaches."
            },
            "AUDIT_RIGHTS": {
                "unacceptable_indicators": ["no right to audit", "audit restricted to once every three years", "vendor charges for audit"],
                "required_criteria": "Covered Entity and HHS regulators must have annual or breach-triggered on-site and electronic audit access with 5 days notice.",
                "fallback_redline": "Upon reasonable notice of not less than five (5) business days, Covered Entity or its designated independent auditor may inspect and audit Business Associate's security facilities, SOC2 reports, and access logs.",
                "compromise_fallback": "Annual remote electronic audit of SOC 2 Type II reports and HIPAA risk assessment documents.",
                "walkaway_threshold": "Complete refusal of audit verification rights.",
                "talking_points": [
                    "HIPAA Security Rule 45 CFR § 164.308 requires Covered Entity to obtain satisfactory assurances."
                ],
                "critical_risk_message": "Inadequate audit rights violate HIPAA Security Rule requirements."
            },
            "TERMINATION": {
                "unacceptable_indicators": ["no immediate termination for privacy breach", "30 day cure for data leak"],
                "required_criteria": "Covered Entity may terminate immediately upon suspicion of any security incident without cure period.",
                "fallback_redline": "Covered Entity may terminate this Agreement immediately if Business Associate suffers a security incident or fails to maintain HIPAA administrative, physical, or technical safeguards.",
                "compromise_fallback": "Covered Entity may suspend access immediately and terminate if breach is not remediated in 5 business days.",
                "walkaway_threshold": "30-day cure period for active health record data exfiltration.",
                "talking_points": [
                    "Immediate termination is required under HIPAA Business Associate rules upon material privacy breach."
                ],
                "critical_risk_message": "Lacks immediate termination remedy for health data compromises."
            }
        }
    }
}

class LegalPlaybook:
    ACTIVE_PROFILE = "vendor_balanced"
    PLAYBOOK = PLAYBOOK_PROFILES["vendor_balanced"]["rules"].copy()

    @classmethod
    def set_profile(cls, profile_key: str):
        if profile_key in PLAYBOOK_PROFILES:
            cls.ACTIVE_PROFILE = profile_key
            cls.PLAYBOOK = PLAYBOOK_PROFILES[profile_key]["rules"].copy()
            return True
        return False

    @classmethod
    def get_profiles(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": k,
                "name": v["name"],
                "description": v["description"],
                "rules_count": len(v["rules"]),
                "is_active": (k == cls.ACTIVE_PROFILE)
            }
            for k, v in PLAYBOOK_PROFILES.items()
        ]

    @classmethod
    def update_rule(
        cls,
        domain: str,
        required_criteria: str,
        fallback_redline: str,
        critical_risk_message: str,
        compromise_fallback: str = "",
        walkaway_threshold: str = "",
        talking_points: List[str] = None
    ):
        cls.PLAYBOOK[domain] = {
            "unacceptable_indicators": [f"violates {domain.lower()}"],
            "required_criteria": required_criteria,
            "fallback_redline": fallback_redline,
            "compromise_fallback": compromise_fallback or fallback_redline,
            "walkaway_threshold": walkaway_threshold or "Severe departure from market standard.",
            "talking_points": talking_points or ["Required under updated statutory guidelines."],
            "critical_risk_message": critical_risk_message
        }
