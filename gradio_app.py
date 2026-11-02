import os
import sys
import tempfile
import gradio as gr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.engine.redliner import ContractRedliner
from backend.engine.docx_exporter import DocxRedlineExporter

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def get_samples():
    samples = {}
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".txt"):
                name = f.replace(".txt", "").replace("_", " ").title()
                with open(os.path.join(DATA_DIR, f), "r", encoding="utf-8") as fl:
                    samples[name] = fl.read()
    return samples

SAMPLES = get_samples()

def audit_contract(contract_text, doc_title):
    if not contract_text or not contract_text.strip():
        return (
            "⚠️ Please enter or select contract text.",
            "",
            None
        )

    report = ContractRedliner.analyze_document(contract_text, title=doc_title or "Agreement Review")

    risk_color = "#EF4444" if report.overall_risk == "CRITICAL" else ("#F59E0B" if report.overall_risk == "HIGH" else "#10B981")
    summary_md = f"""
### 📜 Audit Summary: <span style='color:{risk_color}; font-weight:bold;'>{report.overall_risk} RISK</span>
- **Document Reference**: `{report.contract_id}`
- **Composite Exposure Score**: **{report.composite_risk_score}/100**
- **Clause Breakdown**: 🔴 {report.critical_count} Critical | 🟠 {report.high_count} High | 🟡 {report.medium_count} Medium | 🟢 {report.acceptable_count} Standard
- **Executive Finding**: {report.executive_summary}
"""

    clauses_md_list = []
    for c in report.clauses:
        badge = f"<b style='color:{'#EF4444' if c.risk_level=='CRITICAL' else ('#F59E0B' if c.risk_level=='HIGH' else '#10B981')}'>{c.risk_level}</b>"
        is_deviated = c.risk_level != "ACCEPTABLE"
        diff_view = f"""
> **❌ Original Clause:**  
> ~~{c.original_text}~~  
>  
> **✅ Proposed Playbook Redline:**  
> **{c.suggested_redline}**  
""" if is_deviated else f"> *Standard boilerplate terms compliant with company playbook.*"

        clauses_md_list.append(f"""
### {c.section_title} [{c.category.replace('_', ' ')}] — {badge}
**Finding**: {c.risk_reasoning}  
{f"**Playbook Rule**: *{c.playbook_rule_violated}*" if c.playbook_rule_violated else ""}  
{diff_view}
---
""")

    clauses_md = "\n".join(clauses_md_list)

    # Generate DOCX export
    temp_docx = os.path.join(tempfile.gettempdir(), f"{report.contract_id}_redline.docx")
    DocxRedlineExporter.export_redline(report, temp_docx)

    return summary_md, clauses_md, temp_docx

def load_sample(name):
    return SAMPLES.get(name, "")

with gr.Blocks(title="ContractRisk AI | Legal Redlining") as demo:
    gr.Markdown("""
    # 📜 Enterprise Contract Risk Intelligence & Automated Redlining
    ### AI LegalTech Engine for Commercial Contract Auditing & DOCX Redlining
    *Benchmarks agreements against corporate compliance playbooks and auto-generates Word redlines.*
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Agreement Setup")
            doc_title = gr.Textbox(value="Commercial Master Services Agreement", label="Contract Document Title")
            sample_dropdown = gr.Dropdown(choices=list(SAMPLES.keys()), label="Choose Sample Agreement", value=list(SAMPLES.keys())[0] if SAMPLES else None)
            load_btn = gr.Button("Load Agreement Template")

        with gr.Column(scale=2):
            gr.Markdown("### 📝 Contract Text & Clauses")
            contract_input = gr.Textbox(
                value=list(SAMPLES.values())[0] if SAMPLES else "",
                lines=12,
                label="Contract Input Text"
            )
            audit_btn = gr.Button("⚡ Audit & Redline Contract", variant="primary")

    load_btn.click(fn=load_sample, inputs=[sample_dropdown], outputs=[contract_input])

    gr.Markdown("---")
    gr.Markdown("## 🛡️ Audit Findings & Clause-by-Clause Redlines")

    with gr.Row():
        with gr.Column(scale=1):
            summary_output = gr.Markdown("Click 'Audit & Redline Contract' to begin legal review.")
            docx_download = gr.File(label="📥 Download Redlined Word (.docx)")
        with gr.Column(scale=2):
            clauses_output = gr.Markdown()

    audit_btn.click(
        fn=audit_contract,
        inputs=[contract_input, doc_title],
        outputs=[summary_output, clauses_output, docx_download]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7862)

