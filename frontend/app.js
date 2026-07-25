const apiBase = "http://127.0.0.1:8787";

async function fetchJson(path, options) {
  const response = await fetch(`${apiBase}${path}`, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderAnalysis(unit) {
  const claims = unit.claims.map((claim) => `<li>${claim.claim}</li>`).join("");
  document.querySelector("#analysis").innerHTML = `
    <p><strong>${unit.title}</strong></p>
    <p>${unit.expected_outputs.plain_language_summary}</p>
    <ul>${claims}</ul>
  `;
}

function renderSources(payload) {
  const rows = payload.sources
    .map((source) => `<li><a href="${source.url}">${source.title}</a> (${source.publisher})</li>`)
    .join("");
  document.querySelector("#sources").innerHTML = `<ul>${rows}</ul>`;
}

function renderLedger(payload) {
  document.querySelector("#ledger").textContent = JSON.stringify(payload.entries, null, 2);
}

function renderCandidateStatus(payload) {
  const rows = payload.candidates
    .map((candidate) => {
      const blockers = candidate.promotion_blockers.map((blocker) => `<li>${blocker.gate}: ${blocker.reason}</li>`).join("");
      const provisions = candidate.candidate_provision_ids.join(", ");
      return `
        <article class="candidate-item">
          <h3>${candidate.title}</h3>
          <dl>
            <dt>Publication state</dt><dd>${candidate.publication_state}</dd>
            <dt>Promotable</dt><dd>${candidate.promotable ? "yes" : "no"}</dd>
            <dt>Sources</dt><dd>${candidate.source_record_ids.length}</dd>
            <dt>Candidate provisions</dt><dd>${provisions}</dd>
          </dl>
          <ul>${blockers}</ul>
        </article>
      `;
    })
    .join("");
  document.querySelector("#candidate-status").innerHTML = rows || "<p>No draft candidates.</p>";
}

function renderPromotionAudit(payload) {
  const summaries = payload.candidate_summaries
    .map((summary) => {
      const blockers = summary.blocker_gates.join(", ");
      return `
        <article class="candidate-item">
          <h3>${summary.candidate_analysis_unit_id}</h3>
          <dl>
            <dt>Candidate IDs match</dt><dd>${payload.candidate_ids_match ? "yes" : "no"}</dd>
            <dt>Publication state</dt><dd>${summary.publication_state}</dd>
            <dt>Promotion decision</dt><dd>${summary.promotion_decision}</dd>
            <dt>Blockers match</dt><dd>${summary.blockers_match ? "yes" : "no"}</dd>
            <dt>Source refs match</dt><dd>${summary.source_refs_match ? "yes" : "no"}</dd>
            <dt>Public report includes candidate</dt><dd>${summary.public_report_includes_candidate ? "yes" : "no"}</dd>
          </dl>
          <p>${blockers}</p>
        </article>
      `;
    })
    .join("");
  document.querySelector("#promotion-audit").innerHTML = summaries || "<p>No promotion audit records.</p>";
}

function renderPromotionEvaluator(payload) {
  const safetyFlags = [
    ["Promotion execution allowed", payload.promotion_execution_allowed],
    ["Ledger appended", payload.ledger_appended],
    ["Public report changed", payload.public_report_changed],
    ["Live provider called", payload.live_provider_called],
    ["Household financial data storage allowed", payload.household_financial_data_storage_allowed]
  ]
    .map(([label, value]) => `<dt>${label}</dt><dd>${value ? "yes" : "no"}`)
    .join("");
  const evaluations = payload.evaluations
    .map((evaluation) => {
      const blockerCodes = evaluation.blockers.map((blocker) => `<li>${blocker.code}</li>`).join("");
      return `
        <article class="candidate-item">
          <h3>${evaluation.request_id}</h3>
          <dl>
            <dt>Status</dt><dd>${evaluation.status}</dd>
            <dt>First failing gate</dt><dd>${evaluation.first_failing_gate}</dd>
            <dt>Candidate</dt><dd>${evaluation.candidate_analysis_unit_id || "not supplied"}</dd>
          </dl>
          <ul>${blockerCodes}</ul>
        </article>
      `;
    })
    .join("");
  document.querySelector("#promotion-evaluator").innerHTML = `
    <dl>
      <dt>Status</dt><dd>${payload.status}</dd>
      <dt>Fixture</dt><dd>${payload.fixture_id}</dd>
      <dt>Evaluations</dt><dd>${payload.evaluation_count}</dd>
      <dt>First failing gates</dt><dd>${payload.first_failing_gates.join(", ")}</dd>
      ${safetyFlags}
    </dl>
    <div class="stacked-list">${evaluations}</div>
  `;
}

async function refresh() {
  try {
    const [unit, sources, ledger, _report, candidateStatus, promotionAudit, promotionEvaluator] = await Promise.all([
      fetchJson("/analysis-units/tcja-2017-representative-provisions"),
      fetchJson("/sources"),
      fetchJson("/ai-decision-ledger"),
      fetchJson("/reports/tcja-2017-representative-provisions"),
      fetchJson("/candidates/status"),
      fetchJson("/candidates/promotion-audit"),
      fetchJson("/candidates/promotion-evaluator")
    ]);
    renderAnalysis(unit);
    renderSources(sources);
    renderLedger(ledger);
    renderCandidateStatus(candidateStatus);
    renderPromotionAudit(promotionAudit);
    renderPromotionEvaluator(promotionEvaluator);
  } catch (error) {
    document.querySelector("#analysis").textContent = `${error.message}. Start the backend with make run.`;
  }
}

document.querySelector("#refresh").addEventListener("click", refresh);
document.querySelector("#summarize").addEventListener("click", async () => {
  await fetchJson("/analysis-units/tcja-2017-representative-provisions/summarize", { method: "POST" });
  await refresh();
});

function updateLocalPrivacyCheck() {
  const filingUnit = document.querySelector("#filing-unit").value;
  const dependents = Number(document.querySelector("#dependents").value || 0);
  const itemizes = document.querySelector("#itemizes").checked;
  const tags = [filingUnit, dependents > 0 ? "dependents" : "no dependents", itemizes ? "itemizer" : "standard deduction"];
  document.querySelector("#local-result").textContent = `Local only: ${tags.join(", ")}. No household financial values are collected or sent.`;
}

for (const element of document.querySelectorAll("[data-local-only='true']")) {
  element.addEventListener("input", updateLocalPrivacyCheck);
  element.addEventListener("change", updateLocalPrivacyCheck);
}

document.querySelector("#clear-local").addEventListener("click", () => {
  document.querySelector("#filing-unit").value = "single";
  document.querySelector("#dependents").value = "0";
  document.querySelector("#itemizes").checked = false;
  updateLocalPrivacyCheck();
});

updateLocalPrivacyCheck();
refresh();
