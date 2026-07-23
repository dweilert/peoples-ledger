from __future__ import annotations

from typing import Any
from html import escape

from .analysis import load_analysis_unit
from .assurance import run_assurance_gate
from .decision_ledger import DecisionLedger
from .corrections import load_correction_records
from .publication import decide_publication_state
from .risk import score_risk
from .source_registry import SourceRegistry, load_source_snapshots


def build_public_report() -> dict[str, Any]:
    unit = load_analysis_unit()
    sources = SourceRegistry.load()
    snapshots = {snapshot["source_record_id"]: snapshot for snapshot in load_source_snapshots()}
    ledger_entries = DecisionLedger().read_all()
    assurance = run_assurance_gate()
    publication = decide_publication_state(assurance)
    risk = score_risk(unit, assurance)

    return {
        "report_id": f"report_{unit['id']}_phase1_poc",
        "analysis_unit_id": unit["id"],
        "title": unit["title"],
        "publication": publication.__dict__,
        "risk": risk.__dict__,
        "summary": unit["expected_outputs"]["plain_language_summary"],
        "known_limits": unit["expected_outputs"]["known_limits"],
        "legislative_document": unit["legislative_document"],
        "model_scenarios": unit["model_scenarios"],
        "provisions": [_provision_view(provision) for provision in unit["provisions"]],
        "claims": unit["claims"],
        "narrow_benefit_indicators": unit["narrow_benefit_indicators"],
        "perspective_profiles": [_perspective_view(profile) for profile in unit["perspective_profiles"]],
        "source_manifest": [_source_view(source, snapshots[source["id"]]) for source in sources.all()],
        "decision_trace": [_decision_view(entry) for entry in ledger_entries],
        "corrections": load_correction_records(),
        "assurance": {
            "checks": [check.__dict__ for check in assurance.checks],
            "review_triggers": assurance.review_triggers,
        },
    }


def build_public_report_html(report: dict[str, Any] | None = None) -> str:
    report = report or build_public_report()
    provisions = "\n".join(
        f"""<article class="item">
          <h3>{escape(provision['label'])}</h3>
          <p>{escape(provision['summary'])}</p>
          <dl>
            <dt>Policy area</dt><dd>{escape(provision['policy_area'])}</dd>
            <dt>Publication state</dt><dd>{escape(provision['publication_state'])}</dd>
            <dt>Source spans</dt><dd>{len(provision['source_spans'])}</dd>
          </dl>
        </article>"""
        for provision in report["provisions"]
    )
    sources = "\n".join(
        f"""<li>
          <a href="{escape(source['url'])}">{escape(source['title'])}</a>
          <span>{escape(source['publisher'])}</span>
          <code>{escape(source['snapshot']['content_hash'])}</code>
        </li>"""
        for source in report["source_manifest"]
    )
    perspectives = "\n".join(
        f"<li><strong>{escape(profile['label'])}</strong> v{escape(profile['version'])}</li>"
        for profile in report["perspective_profiles"]
    )
    corrections = "\n".join(
        f"<li>{escape(correction['id'])}: {escape(correction['root_cause'])}</li>"
        for correction in report["corrections"]
    )
    checks = "\n".join(
        f"<li><span>{escape(check['name'])}</span><strong>{'pass' if check['passed'] else 'fail'}</strong></li>"
        for check in report["assurance"]["checks"]
    )
    indicators = "\n".join(
        f"<li><strong>{escape(indicator['label'])}</strong>: {escape(indicator['signal'])}</li>"
        for indicator in report["narrow_benefit_indicators"]
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(report['title'])}</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f6f7f9;
        --panel: #ffffff;
        --ink: #17202a;
        --muted: #5c6b7a;
        --line: #d7dde5;
        --accent: #0f766e;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--ink);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.5;
      }}
      main {{
        max-width: 1120px;
        margin: 0 auto;
        padding: 32px 20px 48px;
      }}
      header {{
        border-bottom: 1px solid var(--line);
        margin-bottom: 24px;
        padding-bottom: 18px;
      }}
      h1 {{ margin: 0 0 8px; font-size: 32px; line-height: 1.15; }}
      h2 {{ margin: 0 0 14px; font-size: 20px; }}
      h3 {{ margin: 0 0 8px; font-size: 16px; }}
      p {{ margin: 0; }}
      section {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        margin-top: 16px;
        padding: 18px;
      }}
      .summary {{
        color: var(--muted);
        max-width: 860px;
      }}
      .metrics {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin-top: 18px;
      }}
      .metric {{
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 12px;
        background: #fbfcfd;
      }}
      .metric span {{ display: block; color: var(--muted); font-size: 13px; }}
      .metric strong {{ display: block; font-size: 20px; margin-top: 3px; }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 12px;
      }}
      .item {{
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 14px;
      }}
      dl {{
        display: grid;
        grid-template-columns: minmax(110px, auto) 1fr;
        gap: 4px 10px;
        margin: 12px 0 0;
        font-size: 13px;
      }}
      dt {{ color: var(--muted); }}
      dd {{ margin: 0; }}
      ul {{ margin: 0; padding-left: 20px; }}
      li + li {{ margin-top: 8px; }}
      code {{
        display: block;
        color: var(--accent);
        font-size: 12px;
        overflow-wrap: anywhere;
      }}
      .checks {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 8px;
        padding: 0;
        list-style: none;
      }}
      .checks li {{
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        margin: 0;
        padding: 10px 12px;
      }}
      a {{ color: var(--accent); }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>{escape(report['title'])}</h1>
        <p class="summary" data-report-id="{escape(report['report_id'])}">{escape(report['summary'])}</p>
        <div class="metrics" aria-label="Report metrics">
          <div class="metric"><span>Publication state</span><strong>{escape(report['publication']['state'])}</strong></div>
          <div class="metric"><span>Risk tier</span><strong>{report['risk']['tier']}</strong></div>
          <div class="metric"><span>Provisions</span><strong>{len(report['provisions'])}</strong></div>
          <div class="metric"><span>Sources</span><strong>{len(report['source_manifest'])}</strong></div>
        </div>
      </header>
      <section>
        <h2>Publication</h2>
        <p>{escape(report['publication']['rationale'])}</p>
      </section>
      <section>
        <h2>Provisions</h2>
        <div class="grid">{provisions}</div>
      </section>
      <section>
        <h2>Narrow-Benefit Indicators</h2>
        <ul>{indicators}</ul>
      </section>
      <section>
        <h2>Sources</h2>
        <ul>{sources}</ul>
      </section>
      <section>
        <h2>Perspectives</h2>
        <ul>{perspectives}</ul>
      </section>
      <section>
        <h2>Corrections</h2>
        <ul>{corrections}</ul>
      </section>
      <section>
        <h2>Assurance Checks</h2>
        <ul class="checks">{checks}</ul>
      </section>
    </main>
  </body>
</html>
"""


def _provision_view(provision: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": provision["id"],
        "label": provision["label"],
        "summary": provision["summary"],
        "policy_area": provision["policy_area"],
        "baseline_id": provision["baseline_id"],
        "effective_window": provision.get("effective_window"),
        "publication_state": provision["publication_state"],
        "source_spans": provision["source_spans"],
        "decision_ids": provision["decision_ids"],
    }


def _perspective_view(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": profile["id"],
        "label": profile["label"],
        "version": profile["version"],
        "author": profile["author"],
        "priorities": profile["priorities"],
        "questions": profile["questions"],
        "permitted_model_scenarios": profile["permitted_model_scenarios"],
        "limitations": profile["limitations"],
    }


def _source_view(source: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": source["id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "source_type": source["source_type"],
        "snapshot": {
            "retrieved_at": snapshot["retrieved_at"],
            "content_hash": snapshot["content_hash"],
            "locator_policy": snapshot["locator_policy"],
            "storage": snapshot["storage"],
        },
    }


def _decision_view(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "decision_type": entry["decision_type"],
        "model": entry["model"],
        "model_scenario_id": entry["model_scenario_id"],
        "source_snapshot_ids": entry["source_snapshot_ids"],
        "validation_results": entry["validation_results"],
        "risk_tier": entry["risk_tier"],
        "publication_lane": entry["publication_lane"],
        "publication_state": entry["publication_state"],
        "disclosure_class": entry["disclosure_class"],
        "entry_hash": entry["entry_hash"],
        "previous_entry_hash": entry["previous_entry_hash"],
    }
