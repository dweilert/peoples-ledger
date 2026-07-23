from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .assurance import run_assurance_gate
from .analysis import load_analysis_unit
from .decision_ledger import DecisionLedger
from .paths import REPO_ROOT
from .prompt_templates import PromptTemplateRegistry
from .reporting import build_public_report
from .source_ingestion import validate_source_ingestion_fixtures
from .statutory_transform import AffectedAuthority, SourceSpan, TransformRequest, apply_transform


@dataclass(frozen=True)
class Phase1AcceptanceCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Phase1AcceptanceReport:
    checks: list[Phase1AcceptanceCheck]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def run_phase1_acceptance() -> Phase1AcceptanceReport:
    checks = [
        _run_check("fixture_ingestion_validates", validate_source_ingestion_fixtures),
        _run_check("deterministic_transform_applies", _deterministic_transform_applies),
        _run_check("ambiguous_transform_abstains", _ambiguous_transform_abstains),
        _run_check("report_traceability", _report_traceability),
        _run_check("ledger_validation_fields", _ledger_validation_fields),
        _run_check("browser_privacy_target_defined", _browser_privacy_target_defined),
        _run_check("scope_boundaries_preserved", _scope_boundaries_preserved),
        _run_check("ci_standard_gates_defined", _ci_standard_gates_defined),
        _run_check("assurance_gate_passes", lambda: _require(run_assurance_gate().passed, "assurance gate did not pass")),
    ]
    return Phase1AcceptanceReport(checks=checks)


def _run_check(name: str, fn: Callable[[], object]) -> Phase1AcceptanceCheck:
    try:
        fn()
    except Exception as exc:
        return Phase1AcceptanceCheck(name=name, passed=False, detail=str(exc))
    return Phase1AcceptanceCheck(name=name, passed=True, detail="ok")


def _deterministic_transform_applies() -> None:
    request = TransformRequest(
        id="transform_phase1_acceptance_replace",
        analysis_unit_id="tcja_2017_representative_provisions",
        operation="replace_text",
        current_text="Section 11(b) imposes a 35 percent rate.",
        source_span=SourceSpan(
            source_record_id="pl115_97_public_law",
            locator="Section 13001",
            text_hash="manual-span-sec-13001-corporate-rate",
        ),
        affected_authority=[AffectedAuthority(type="usc", citation="26 USC 11")],
        target_text="35 percent",
        replacement_text="21 percent",
        authoritative_after_text="Section 11(b) imposes a 21 percent rate.",
    )
    result = apply_transform(request)
    _require(result.status == "applied", "transform did not apply")
    _require(result.after_text == "Section 11(b) imposes a 21 percent rate.", "unexpected transform output")
    _require(result.transformation is not None, "transform did not produce a record")
    _require(result.transformation["validation"]["reconciled"], "transform was not reconciled")


def _ambiguous_transform_abstains() -> None:
    request = TransformRequest(
        id="transform_phase1_acceptance_ambiguous",
        analysis_unit_id="tcja_2017_representative_provisions",
        operation="replace_text",
        current_text="rate rate",
        source_span=SourceSpan(
            source_record_id="pl115_97_public_law",
            locator="Section 13001",
            text_hash="manual-span-sec-13001-corporate-rate",
        ),
        affected_authority=[AffectedAuthority(type="usc", citation="26 USC 11")],
        target_text="rate",
        replacement_text="amount",
    )
    result = apply_transform(request)
    _require(result.status == "abstained", "ambiguous transform did not abstain")
    _require("statutory_transform_abstained:target_text_ambiguous" in result.review_triggers, "missing abstention trigger")


def _report_traceability() -> None:
    report = build_public_report()
    _require(report["source_manifest"], "missing source manifest")
    _require(report["decision_trace"], "missing decision trace")
    for provision in report["provisions"]:
        _require(provision["source_spans"], f"provision missing source spans: {provision['id']}")
        _require(provision["decision_ids"], f"provision missing decisions: {provision['id']}")
    claim_ids = {claim["id"] for claim in report["claims"]}
    for indicator in report["narrow_benefit_indicators"]:
        missing = set(indicator["evidence_ids"]) - claim_ids
        _require(not missing, f"indicator {indicator['id']} references unknown evidence: {sorted(missing)}")


def _ledger_validation_fields() -> None:
    entries = DecisionLedger().read_all()
    _require(entries, "ledger is empty")
    required_validation_keys = {
        "schema_valid",
        "citations_valid",
        "statutory_transform_valid",
        "calculation_valid",
        "privacy_egress_valid",
        "perspective_invariance_valid",
    }
    for entry in entries:
        _require(entry["source_hashes"], f"ledger entry missing source hashes: {entry['id']}")
        _require(entry["model_scenario_id"], f"ledger entry missing model scenario: {entry['id']}")
        _require("model_disagreement" in entry, f"ledger entry missing disagreement: {entry['id']}")
        _require(required_validation_keys.issubset(entry["validation_results"]), f"ledger entry missing validation fields: {entry['id']}")


def _browser_privacy_target_defined() -> None:
    makefile = _read_repo_file("Makefile")
    spec = _read_repo_file("tests/browser/privacy_egress.spec.js")
    _require("test-browser:" in makefile, "Makefile missing test-browser target")
    _require("page.route" in spec, "browser privacy spec does not intercept requests")
    _require("local privacy controls do not transmit local values" in spec, "browser privacy spec missing egress test")


def _ci_standard_gates_defined() -> None:
    workflow = _read_repo_file(".github/workflows/ci.yml")
    for target in ("make validate", "make assure", "make test", "make phase1-acceptance"):
        _require(target in workflow, f"CI missing {target}")


def _scope_boundaries_preserved() -> None:
    unit = load_analysis_unit()
    for scenario in unit["model_scenarios"]:
        _require(not scenario["uses_household_financial_data"], f"scenario uses household financial data: {scenario['id']}")
        _require(scenario["model_type"] != "microsimulation_stub", f"microsimulation remains out of scope: {scenario['id']}")

    registry = PromptTemplateRegistry.load()
    for template in registry.templates.values():
        _require(not template["live_provider_authorized"], f"live provider authorization remains out of scope: {template['version']}")

    forbidden_paths = [
        "src/peoples_ledger/state_modeling.py",
        "src/peoples_ledger/live_congressional_monitoring.py",
        "src/peoples_ledger/microsimulation.py",
    ]
    for relative_path in forbidden_paths:
        _require(not (REPO_ROOT / relative_path).exists(), f"out-of-scope module exists: {relative_path}")


def _read_repo_file(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)
