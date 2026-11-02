import os
from typing import List
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_COLOR_INDEX
from backend.models.schemas import ContractAuditReport

class DocxRedlineExporter:
    """Exports structured audit reports into standardized redlined DOCX documents."""

    @staticmethod
    def export_redline(report: ContractAuditReport, output_path: str):
        doc = Document()

        # Document Header
        title_para = doc.add_heading(report.document_title, level=0)
        p_sub = doc.add_paragraph()
        p_sub.add_run("Automated Legal Redline & Risk Audit Report\n").bold = True
        p_sub.add_run(f"Audit Reference: {report.contract_id} | Date: {report.analyzed_at}\n")
        p_sub.add_run(f"Composite Risk Rating: {report.overall_risk} ({report.composite_risk_score}/100)").font.color.rgb = RGBColor(180, 0, 0)

        doc.add_heading("Executive Audit Summary", level=1)
        doc.add_paragraph(report.executive_summary)

        # Financial Exposure Section
        if report.exposure_analysis:
            doc.add_heading("Financial Exposure & Balance Sheet Liability", level=1)
            exp = report.exposure_analysis
            p_exp = doc.add_paragraph()
            p_exp.add_run(f"Estimated ACV: ${exp.get('estimated_acv_usd', 0):,.0f} USD\n")
            p_exp.add_run(f"Liability Multiplier: {exp.get('liability_multiplier')}x\n")
            p_exp.add_run(f"Exposure Rating: {exp.get('balance_sheet_exposure_level')}\n")
            p_exp.add_run(f"Insurance Recommendation: {exp.get('insurance_recommendation')}\n")
            p_exp.add_run(f"CFO Advisory: {exp.get('cfo_summary')}\n")

        # Missing Protections Section
        if report.missing_protections:
            doc.add_heading("Missing Mandatory Protections (Silent Risks)", level=1)
            for m in report.missing_protections:
                p_m = doc.add_paragraph()
                p_m.add_run(f"[{m.severity}] {m.risk_title}\n").bold = True
                p_m.add_run(f"Impact: {m.impact_rationale}\n")
                p_m.add_run(f"Recommended Addition ({m.recommended_clause_title}):\n").italic = True
                p_m.add_run(m.recommended_clause_text + "\n")

        # Defined Terms Section
        if report.defined_terms_report:
            doc.add_heading("Defined Terms Consistency & Drafting Integrity", level=1)
            dt = report.defined_terms_report
            p_dt = doc.add_paragraph()
            p_dt.add_run(f"Consistency Score: {dt.get('consistency_health_score')}/100 | Total Definitions: {dt.get('total_definitions_found')}\n")
            p_dt.add_run(f"Orphaned Capitalized Terms Detected: {dt.get('orphaned_terms_count')}\n")
            for o in dt.get("orphaned_terms", [])[:5]:
                p_dt.add_run(f"  * \"{o.get('term')}\" (Used {o.get('occurrences')}x without definition)\n")

        doc.add_heading("Clause-by-Clause Redline Analysis", level=1)

        for clause in report.clauses:
            cuad_info = f" | {clause.cuad_category}" if clause.cuad_category else ""
            sec_heading = doc.add_heading(f"{clause.section_title} [{clause.category}{cuad_info}]", level=2)
            
            p_risk = doc.add_paragraph()
            r_run = p_risk.add_run(f"Risk Rating: {clause.risk_level}\n")
            r_run.bold = True
            if clause.risk_level in ["CRITICAL", "HIGH"]:
                r_run.font.color.rgb = RGBColor(200, 30, 30)
            elif clause.risk_level == "MEDIUM":
                r_run.font.color.rgb = RGBColor(220, 140, 0)
            else:
                r_run.font.color.rgb = RGBColor(30, 140, 50)

            p_risk.add_run(f"Finding: {clause.risk_reasoning}\n")
            if clause.playbook_rule_violated:
                p_risk.add_run(f"Playbook Standard: {clause.playbook_rule_violated}\n").italic = True

            # Redline Comparison
            if clause.risk_level in ["CRITICAL", "HIGH", "MEDIUM"]:
                doc.add_paragraph("Original Clause (Struck Out):").italic = True
                p_orig = doc.add_paragraph()
                orig_run = p_orig.add_run(clause.original_text)
                orig_run.font.strike = True
                orig_run.font.color.rgb = RGBColor(120, 120, 120)

                doc.add_paragraph("Proposed Playbook Redline (Replacement):").italic = True
                p_red = doc.add_paragraph()
                red_run = p_red.add_run(clause.suggested_redline)
                red_run.bold = True
                red_run.font.highlight_color = WD_COLOR_INDEX.YELLOW
            else:
                p_ok = doc.add_paragraph()
                p_ok.add_run("Status: Compliant with Playbook standards.")

            doc.add_paragraph("-" * 40)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        return output_path

