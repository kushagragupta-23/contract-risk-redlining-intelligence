document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = document.getElementById("themeIcon");
  const sampleSelect = document.getElementById("sampleSelect");
  const contractInput = document.getElementById("contractInput");
  const runAuditBtn = document.getElementById("runAuditBtn");
  const exportDocxBtn = document.getElementById("exportDocxBtn");
  const contractStatusBadge = document.getElementById("contractStatusBadge");
  const auditOutputContainer = document.getElementById("auditOutputContainer");
  const metricsPanel = document.getElementById("metricsPanel");

  // Playbook & Scraper elements
  const playbookProfileSelect = document.getElementById("playbookProfileSelect");
  const scrapeLegalRulesBtn = document.getElementById("scrapeLegalRulesBtn");
  const playbookRulesList = document.getElementById("playbookRulesList");
  const kpiActiveProfile = document.getElementById("kpiActiveProfile");
  const kpiProfileSub = document.getElementById("kpiProfileSub");
  const kpiRulesCount = document.getElementById("kpiRulesCount");

  // Custom Rule elements
  const customRuleDomain = document.getElementById("customRuleDomain");
  const customRuleCriteria = document.getElementById("customRuleCriteria");
  const customRuleRedline = document.getElementById("customRuleRedline");
  const saveCustomRuleBtn = document.getElementById("saveCustomRuleBtn");

  // Upload elements
  const contractUploadZone = document.getElementById("contractUploadZone");
  const contractFileInput = document.getElementById("contractFileInput");

  let currentContractId = null;

  function initTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    themeIcon.textContent = current === "dark" ? "☀️" : "🌙";
  }

  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    themeIcon.textContent = next === "dark" ? "☀️" : "🌙";
  });

  // Load sample agreements
  async function loadSamples() {
    try {
      const res = await fetch("/api/v1/samples");
      const samples = await res.json();
      sampleSelect.innerHTML = '<option value="">-- Choose Sample Agreement --</option>';
      samples.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.title;
        sampleSelect.appendChild(opt);
      });
      if (samples.length > 0) {
        sampleSelect.value = samples[0].id;
        loadSampleContent(samples[0].id);
      }
    } catch (err) {
      console.error("Failed to load samples:", err);
    }
  }

  async function loadSampleContent(sampleId) {
    if (!sampleId) return;
    try {
      const res = await fetch(`/api/v1/samples/${sampleId}`);
      const data = await res.json();
      contractInput.value = data.content;
      contractStatusBadge.textContent = "Agreement loaded";
    } catch (err) {
      console.error("Failed to load sample content:", err);
    }
  }

  sampleSelect.addEventListener("change", (e) => {
    loadSampleContent(e.target.value);
  });

  // Load Playbook Rules into Sidebar
  async function loadPlaybookRules() {
    try {
      const res = await fetch("/api/v1/playbook/rules");
      const data = await res.json();
      kpiRulesCount.textContent = `${data.rules.length} Policies Active`;

      playbookRulesList.innerHTML = "";
      data.rules.forEach((r, idx) => {
        const item = document.createElement("div");
        item.className = "playbook-item";
        item.innerHTML = `
          <strong>${idx + 1}. ${r.domain.replace("_", " ")}</strong>
          <p>${r.criteria}</p>
        `;
        playbookRulesList.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load playbook rules:", err);
    }
  }

  // Switch Playbook Negotiating Posture
  playbookProfileSelect.addEventListener("change", async (e) => {
    const profileId = e.target.value;
    try {
      const res = await fetch(`/api/v1/playbook/profiles/${profileId}/activate`, { method: "POST" });
      const data = await res.json();
      kpiActiveProfile.textContent = data.active_name.split("(")[0];
      kpiProfileSub.textContent = data.active_name.includes("(") ? data.active_name.split("(")[1].replace(")", "") : "Active Posture";
      alert(`✅ Negotiating posture switched to: ${data.active_name}\nEnforcing ${data.rules_enforced} rules.`);
      await loadPlaybookRules();
      if (contractInput.value.trim()) {
        runAuditBtn.click();
      }
    } catch (err) {
      alert("Failed to switch posture: " + err.message);
    }
  });

  // Trigger BeautifulSoup Legal Scraper
  scrapeLegalRulesBtn.addEventListener("click", async () => {
    scrapeLegalRulesBtn.disabled = true;
    scrapeLegalRulesBtn.textContent = "⏳ Scraping Legal Gazettes...";

    try {
      const res = await fetch("/api/v1/playbook/scrape", { method: "POST" });
      const data = await res.json();
      alert(`✅ Legal Scraper Finished!\nIngested ${data.rules_updated} updated policies from FTC, Delaware DGCL, and EU AI Act using BeautifulSoup4.\nPlaybook re-indexed in Hybrid RAG.`);
      await loadPlaybookRules();
    } catch (err) {
      alert("Scraper error: " + err.message);
    } finally {
      scrapeLegalRulesBtn.disabled = false;
      scrapeLegalRulesBtn.textContent = "⟳ Scrape Legal Rules (BS4)";
    }
  });

  // Save Custom Rule
  saveCustomRuleBtn.addEventListener("click", async () => {
    const domain = customRuleDomain.value.trim();
    const criteria = customRuleCriteria.value.trim();
    const redline = customRuleRedline.value.trim();

    if (!domain || !criteria || !redline) {
      alert("Please enter Domain, Criteria, and Fallback Redline text.");
      return;
    }

    try {
      const res = await fetch("/api/v1/playbook/custom-rule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: domain,
          required_criteria: criteria,
          fallback_redline: redline,
          critical_risk_message: `Custom rule violated: ${criteria}`
        })
      });
      const data = await res.json();
      alert(`✅ Custom rule added for ${domain.toUpperCase()}!\nActive rules: ${data.rules_count}`);
      customRuleDomain.value = "";
      customRuleCriteria.value = "";
      customRuleRedline.value = "";
      await loadPlaybookRules();
    } catch (err) {
      alert("Failed to save custom rule: " + err.message);
    }
  });

  // File Upload Handlers (.docx, .pdf, .txt)
  contractUploadZone.addEventListener("click", () => contractFileInput.click());

  contractUploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    contractUploadZone.classList.add("dragover");
  });

  contractUploadZone.addEventListener("dragleave", () => {
    contractUploadZone.classList.remove("dragover");
  });

  contractUploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    contractUploadZone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleContractUpload(e.dataTransfer.files[0]);
    }
  });

  contractFileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleContractUpload(e.target.files[0]);
    }
  });

  async function handleContractUpload(file) {
    contractStatusBadge.textContent = `Uploading ${file.name}...`;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/v1/upload-contract", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const report = await res.json();
      currentContractId = report.contract_id;
      contractInput.value = `[Uploaded File: ${file.name}]\n\nAudit executed across ${report.total_clauses_analyzed} commercial clauses.`;
      contractStatusBadge.textContent = "Upload Audit Complete";
      renderAuditReport(report);
    } catch (err) {
      alert("Contract upload error: " + err.message);
      contractStatusBadge.textContent = "Upload failed";
    } finally {
      contractFileInput.value = "";
    }
  }

  // Execute Contract Audit
  runAuditBtn.addEventListener("click", async () => {
    const text = contractInput.value.trim();
    if (!text) {
      alert("Please paste contract text or select an agreement template.");
      return;
    }

    runAuditBtn.disabled = true;
    runAuditBtn.textContent = "⏳ Auditing Playbook...";
    contractStatusBadge.textContent = "Auditing clauses";

    try {
      const res = await fetch("/api/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contract_text: text,
          document_title: sampleSelect.options[sampleSelect.selectedIndex]?.text || "Commercial Agreement"
        })
      });

      const report = await res.json();
      currentContractId = report.contract_id;
      renderAuditReport(report);
    } catch (err) {
      alert("Audit error: " + err.message);
    } finally {
      runAuditBtn.disabled = false;
      runAuditBtn.textContent = "⚡ Audit & Redline Contract";
      contractStatusBadge.textContent = "Audit complete";
    }
  });

  function renderAuditReport(report) {
    exportDocxBtn.style.display = "inline-flex";
    metricsPanel.style.display = "block";

    document.getElementById("sideRiskRating").textContent = report.overall_risk_rating;
    document.getElementById("sideScore").textContent = `${report.composite_exposure_score}/100`;
    document.getElementById("sideClauseCount").textContent = report.total_clauses_analyzed;
    document.getElementById("sideRiskCount").textContent = report.critical_clauses_count + report.high_risk_clauses_count;

    const riskBadgeClass = report.overall_risk === "CRITICAL" ? "pill-CRITICAL" :
                          (report.overall_risk === "HIGH" ? "pill-HIGH" : "pill-LOW");

    // 1. Financial Exposure & Balance Sheet Liability Card
    let exposureHtml = "";
    if (report.exposure_analysis) {
      const exp = report.exposure_analysis;
      const isUncapped = exp.liability_multiplier === "UNCAPPED" || exp.liability_multiplier >= 10.0;
      const expColor = isUncapped ? "var(--red)" : (exp.liability_multiplier > 1.0 ? "var(--amber)" : "var(--green)");
      exposureHtml = `
        <div class="report-section" style="border: 1px solid var(--line); border-radius: 8px; background: var(--bg-soft); padding: 16px; margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h3 style="margin: 0; display: flex; align-items: center; gap: 8px; color: var(--text);">
              💰 Financial Exposure &amp; Balance Sheet Liability Analysis
            </h3>
            <span class="badge" style="background: ${expColor}22; color: ${expColor}; border: 1px solid ${expColor}; font-weight: 700; font-size: 11px;">
              ${exp.balance_sheet_exposure_level.replace(/_/g, ' ')}
            </span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 12px;">
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 10px;">
              <span style="font-size: 10.5px; color: var(--text-dim); text-transform: uppercase;">Estimated Deal Value (ACV)</span>
              <div style="font-size: 16px; font-weight: 700; color: var(--text);">$${Number(exp.estimated_acv_usd).toLocaleString()} USD</div>
            </div>
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 10px;">
              <span style="font-size: 10.5px; color: var(--text-dim); text-transform: uppercase;">Direct Liability Cap</span>
              <div style="font-size: 16px; font-weight: 700; color: ${expColor};">${exp.liability_multiplier}x ACV</div>
            </div>
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 10px;">
              <span style="font-size: 10.5px; color: var(--text-dim); text-transform: uppercase;">Max Direct Exposure</span>
              <div style="font-size: 16px; font-weight: 700; color: ${expColor};">
                ${exp.max_direct_exposure_usd ? '$' + Number(exp.max_direct_exposure_usd).toLocaleString() + ' USD' : 'UNCAPPED (Entire Balance Sheet)'}
              </div>
            </div>
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 10px;">
              <span style="font-size: 10.5px; color: var(--text-dim); text-transform: uppercase;">Consequential Damages</span>
              <div style="font-size: 12px; font-weight: 600; color: var(--text); margin-top: 3px;">
                ${exp.consequential_damages_status.replace(/_/g, ' ')}
              </div>
            </div>
          </div>

          <div style="font-size: 12px; color: var(--text); background: var(--panel); border-left: 3px solid var(--blue); padding: 8px 12px; border-radius: 0 4px 4px 0; margin-bottom: 8px;">
            <b>CFO Advisory Memo:</b> ${exp.cfo_summary}
          </div>
          <div style="font-size: 11.5px; color: var(--text-dim);">
            🛡️ <b>Insurance Underwriting Requirement:</b> ${exp.insurance_recommendation}
          </div>
        </div>
      `;
    }

    // 2. Defined Terms & Drafting Integrity Card
    let definedTermsHtml = "";
    if (report.defined_terms_report) {
      const dt = report.defined_terms_report;
      const dtScoreColor = dt.consistency_health_score >= 80 ? "var(--green)" : (dt.consistency_health_score >= 60 ? "var(--amber)" : "var(--red)");
      definedTermsHtml = `
        <div class="report-section" style="border: 1px solid var(--line); border-radius: 8px; background: var(--bg-soft); padding: 16px; margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0; display: flex; align-items: center; gap: 8px; color: var(--text);">
              📐 Defined Terms &amp; Drafting Integrity Audit
            </h3>
            <span class="badge" style="background: ${dtScoreColor}22; color: ${dtScoreColor}; border: 1px solid ${dtScoreColor}; font-weight: 700; font-size: 11px;">
              Consistency Health: ${dt.consistency_health_score}/100
            </span>
          </div>

          <p style="font-size: 12px; color: var(--text-dim); margin-bottom: 10px;">
            Detected <b>${dt.total_definitions_found}</b> formal definitions. Scanned for orphaned capitalized terms and dead definitions:
          </p>

          ${dt.orphaned_terms_count > 0 ? `
            <div style="margin-bottom: 10px;">
              <strong style="font-size: 12px; color: var(--amber);">⚠️ Orphaned Defined Terms (${dt.orphaned_terms_count} terms capitalized but never defined):</strong>
              <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 6px;">
                ${dt.orphaned_terms.map(o => `
                  <div style="background: var(--panel); border: 1px dashed var(--amber); border-radius: 4px; padding: 6px 10px; font-size: 11.5px;">
                    <span style="font-weight: 700; color: var(--text); font-family: monospace;">"${o.term}"</span> (referenced ${o.occurrences}x)
                    <div style="color: var(--text-dim); font-size: 11px; margin-top: 2px;">Remedy: ${o.remedy}</div>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : '<div style="font-size: 11.5px; color: var(--green);">✅ No orphaned defined terms detected. All capitalized terms have formal definitions.</div>'}

          ${dt.dead_terms_count > 0 ? `
            <div style="margin-top: 8px;">
              <span style="font-size: 11.5px; color: var(--text-dim);">Unused / Dead Definitions (Defined in Section 1 but never invoked): </span>
              ${dt.dead_terms.map(d => `<span class="badge" style="font-size: 10px; margin-right: 4px;">"${d}"</span>`).join('')}
            </div>
          ` : ''}
        </div>
      `;
    }

    let clausesHtml = report.clauses.map(c => `
      <div class="redline-clause-card">
        <div class="clause-header">
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <span class="clause-title">${c.section_title || c.category}</span>
            <span class="domain-tag">${c.category}</span>
            ${c.cuad_category ? `<span class="badge" style="font-size: 10px; font-family: monospace; background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3);">${c.cuad_category}</span>` : ''}
          </div>
          <span class="risk-pill pill-${c.risk_level}">${c.risk_level}</span>
        </div>

        <div class="diff-container">
          <div class="diff-box diff-original">
            <span class="diff-label">Original Contract Clause</span>
            ${c.original_text}
          </div>
          <div class="diff-box diff-suggested">
            <span class="diff-label">Playbook Standard Redline</span>
            ${c.suggested_redline}
          </div>
        </div>

        <div class="rationale-box">
          <strong>Playbook Finding:</strong> ${c.risk_reasoning}
        </div>

        ${c.compromise_fallback ? `
        <details style="margin-top: 8px; font-size: 12px; background: var(--bg-soft); border: 1px solid var(--line); border-radius: 6px; padding: 8px 12px;">
          <summary style="cursor: pointer; font-weight: 600; color: var(--blue);">
            🎯 Negotiation Strategy: 3-Tier Fallback Hierarchy &amp; Talking Points
          </summary>
          <div style="margin-top: 8px;">
            <div style="margin-bottom: 6px;">
              <span style="font-weight: 600; color: var(--amber);">Secondary Compromise Position:</span>
              <div style="font-family: monospace; font-size: 11px; background: var(--panel); padding: 6px 8px; border-radius: 4px; margin-top: 2px;">
                ${c.compromise_fallback}
              </div>
            </div>
            <div style="margin-bottom: 6px;">
              <span style="font-weight: 600; color: var(--red);">Walk-Away Boundary:</span> ${c.walkaway_threshold || 'None'}
            </div>
            ${(c.talking_points && c.talking_points.length > 0) ? `
              <div style="margin-top: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-weight: 600; color: var(--text);">Counsel Talking Points:</span>
                  <button class="btn pill" style="font-size: 10px; padding: 2px 8px;" onclick="navigator.clipboard.writeText(${JSON.stringify(c.talking_points.join('\n\n'))}); alert('Copied counsel talking points to clipboard!');">📋 Copy Points</button>
                </div>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                  ${c.talking_points.map(tp => `<li>${tp}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
          </div>
        </details>
        ` : ''}
      </div>
    `).join("");

    const omissionsHtml = (report.missing_protections && report.missing_protections.length > 0) ? `
      <div class="report-section" style="border-left: 4px solid var(--red); padding-left: 14px; margin-bottom: 20px;">
        <h3 style="color: var(--red); display: flex; align-items: center; gap: 8px;">
          ⚠️ Missing Mandatory Protections (${report.missing_protections.length} Silent Risks Detected)
        </h3>
        <p style="font-size: 12.5px; color: var(--text-dim); margin-bottom: 10px;">
          Counterparty draft completely omits essential protective clauses standard in enterprise agreements:
        </p>
        <div style="display: flex; flex-direction: column; gap: 10px;">
          ${report.missing_protections.map(m => `
            <div style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 13px; color: var(--red);">🚨 ${m.risk_title}</strong>
                <span class="badge pill-${m.severity}" style="font-size: 10px;">${m.severity} OMISSION</span>
              </div>
              <p style="font-size: 12px; color: var(--text); margin: 6px 0;">${m.impact_rationale}</p>
              <div style="background: var(--panel); border: 1px dashed var(--line); border-radius: 4px; padding: 8px 12px; font-family: monospace; font-size: 11.5px; color: var(--text);">
                <b>Recommended Standard Clause:</b><br/>${m.recommended_clause_text}
              </div>
              <div style="font-size: 11px; color: var(--blue); margin-top: 6px;">
                💡 <b>Talking Point for Counterparty Counsel:</b> "${m.talking_point_for_counsel}"
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    ` : '';

    auditOutputContainer.innerHTML = `
      <div class="report-header">
        <div>
          <h2>Enterprise Contract Vulnerability Audit</h2>
          <div class="report-meta">
            Contract ID: <code>${report.contract_id}</code> · Posture: <b>${(report.negotiation_posture || 'vendor_balanced').toUpperCase()}</b> · Health: <b>${report.contract_health_grade}</b>
          </div>
        </div>
        <div>
          <span class="badge ${riskBadgeClass}" style="font-size: 13px; padding: 6px 14px;">
            ${report.overall_risk} EXPOSURE (${report.composite_risk_score}/100)
          </span>
        </div>
      </div>

      <div style="background: rgba(37,99,235,0.06); border: 1px solid var(--line); border-radius: 8px; padding: 12px 16px; margin: 12px 0; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 11px; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px; font-weight: 700;">Executive Contract Rating</span>
          <div style="font-size: 18px; font-weight: 800; color: var(--blue); margin-top: 2px;">${report.contract_health_grade}</div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 11px; color: var(--text-dim);">Negotiating Strategy Posture</span>
          <div style="font-size: 13px; font-weight: 700; color: var(--text);">${(report.negotiation_posture || 'vendor_balanced').replace('_', ' ').toUpperCase()}</div>
        </div>
      </div>

      ${omissionsHtml}
      ${exposureHtml}
      ${definedTermsHtml}

      <div class="report-section">
        <h3>Executive Vulnerability Summary</h3>
        <p style="font-size: 13.5px; line-height: 1.6; color: var(--text);">${report.executive_summary}</p>
      </div>

      <div class="report-section">
        <h3>Clause-by-Clause Redline &amp; Playbook Benchmark (${report.clauses.length} Clauses)</h3>
        <div class="clauses-list">${clausesHtml}</div>
      </div>
    `;
  }

  // Export DOCX
  exportDocxBtn.addEventListener("click", () => {
    if (currentContractId) {
      window.open(`/api/v1/export-docx/${currentContractId}`, "_blank");
    }
  });

  initTheme();
  loadPlaybookRules();
  loadSamples();
});
