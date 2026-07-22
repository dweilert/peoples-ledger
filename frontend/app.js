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

async function refresh() {
  try {
    const [unit, sources, ledger] = await Promise.all([
      fetchJson("/analysis-units/tcja-2017-representative-provisions"),
      fetchJson("/sources"),
      fetchJson("/ai-decision-ledger")
    ]);
    renderAnalysis(unit);
    renderSources(sources);
    renderLedger(ledger);
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
