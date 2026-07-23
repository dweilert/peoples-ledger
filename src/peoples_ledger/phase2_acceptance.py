from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .assurance import run_assurance_gate
from .candidate_audit import build_candidate_audit_bundle, validate_candidate_audit_bundle
from .candidate_extraction import validate_candidate_extraction_stub
from .candidate_extraction_policy import CandidateExtractionPolicyRegistry, validate_candidate_extraction_policy_registry
from .candidate_promotion import evaluate_candidate_promotion, validate_candidate_promotion_gate_reports
from .candidate_promotion_audit import build_candidate_promotion_audit_cross_check, validate_candidate_promotion_audit_cross_check
from .candidate_promotion_decision import (
    load_candidate_promotion_decision_ledger_stubs,
    validate_candidate_promotion_decision_ledger_stubs,
)
from .candidate_promotion_request import load_candidate_promotion_requests, validate_candidate_promotion_requests
from .candidate_queue import load_candidate_analysis_queue, validate_candidate_analysis_queue
from .candidate_review import load_candidate_review_records, validate_candidate_review_ledger_stub, validate_candidate_review_records
from .candidate_status import build_candidate_status
from .decision_ledger import DecisionLedger
from .paths import REPO_ROOT
from .reporting import build_public_report
from .source_acquisition import acquire_source_records_from_manifest, load_source_acquisition_manifest
from .source_promotion import load_source_promotion_manifest, validate_source_promotion_manifest
from .source_registry import SourceRegistry


@dataclass(frozen=True)
class Phase2AcceptanceCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Phase2AcceptanceReport:
    checks: list[Phase2AcceptanceCheck]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def run_phase2_acceptance() -> Phase2AcceptanceReport:
    checks = [
        _run_check("source_acquisition_candidates_validate", _source_acquisition_candidates_validate),
        _run_check("source_promotion_manifest_blocks_registry_changes", _source_promotion_manifest_blocks_registry_changes),
        _run_check("candidate_queue_draft_only", _candidate_queue_draft_only),
        _run_check("candidate_promotion_reports_block", _candidate_promotion_reports_block),
        _run_check("candidate_promotion_request_stub_validates", _candidate_promotion_request_stub_validates),
        _run_check("candidate_promotion_decision_ledger_stub_validates", _candidate_promotion_decision_ledger_stub_validates),
        _run_check("candidate_promotion_audit_cross_check", _candidate_promotion_audit_cross_check),
        _run_check("candidate_extraction_policy_registry", _candidate_extraction_policy_registry),
        _run_check("candidate_extraction_stub_validates", _candidate_extraction_stub_validates),
        _run_check("candidate_review_records_block", _candidate_review_records_block),
        _run_check("candidate_review_ledger_stub_validates", _candidate_review_ledger_stub_validates),
        _run_check("candidate_audit_bundle_validates", _candidate_audit_bundle_validates),
        _run_check("candidate_status_surfaces_blockers", _candidate_status_surfaces_blockers),
        _run_check("promotion_audit_status_surfaces_defined", _promotion_audit_status_surfaces_defined),
        _run_check("frontend_candidate_status_target_defined", _frontend_candidate_status_target_defined),
        _run_check("public_report_excludes_candidates", _public_report_excludes_candidates),
        _run_check("phase2_privacy_boundaries_preserved", _phase2_privacy_boundaries_preserved),
        _run_check("phase2_scope_boundaries_preserved", _phase2_scope_boundaries_preserved),
        _run_check("ci_phase2_gate_defined", _ci_phase2_gate_defined),
        _run_check("assurance_gate_passes", lambda: _require(run_assurance_gate().passed, "assurance gate did not pass")),
    ]
    return Phase2AcceptanceReport(checks=checks)


def _run_check(name: str, fn: Callable[[], object]) -> Phase2AcceptanceCheck:
    try:
        fn()
    except Exception as exc:
        return Phase2AcceptanceCheck(name=name, passed=False, detail=str(exc))
    return Phase2AcceptanceCheck(name=name, passed=True, detail="ok")


def _source_acquisition_candidates_validate() -> None:
    manifest = load_source_acquisition_manifest()
    records, snapshots = acquire_source_records_from_manifest()
    _require(manifest["candidate_publication_state"] == "draft", "source acquisition manifest is not draft")
    _require(manifest["report_visibility"] == "excluded_until_promoted", "source acquisition manifest is reportable")
    _require(not manifest["retrieval_policy"]["network_allowed"], "source acquisition allows network retrieval")
    _require({record["id"] for record in records} == {snapshot["source_record_id"] for snapshot in snapshots}, "source record/snapshot ids differ")
    public_source_ids = set(SourceRegistry.load().records)
    _require(not ({record["id"] for record in records} & public_source_ids), "candidate sources leaked into public source registry")


def _source_promotion_manifest_blocks_registry_changes() -> None:
    validate_source_promotion_manifest()
    manifest = load_source_promotion_manifest()
    _require(manifest["promotion_state"] == "blocked", "source promotion manifest is not blocked")
    _require(not manifest["registry_update_allowed"], "source promotion manifest allows registry updates")
    _require(not manifest["public_report_inclusion_allowed"], "source promotion manifest allows public reporting")
    _require(not manifest["ledger_append_allowed"], "source promotion manifest allows ledger appends")
    public_source_ids = set(SourceRegistry.load().records)
    proposed_source_ids = {source["source_record"]["id"] for source in manifest["proposed_sources"]}
    _require(not (public_source_ids & proposed_source_ids), "source promotion manifest leaked into public registry")
    for proposed in manifest["proposed_sources"]:
        _require(
            proposed["registry_action"] == "proposed_noop",
            f"source promotion action is not no-op: {proposed['source_record']['id']}",
        )


def _candidate_queue_draft_only() -> None:
    validate_candidate_analysis_queue()
    candidates = load_candidate_analysis_queue()
    _require(candidates, "candidate queue is empty")
    for candidate in candidates:
        _require(candidate["status"] == "draft", f"candidate is not draft: {candidate['id']}")
        _require(candidate["publication_state"] == "draft", f"candidate publication state is not draft: {candidate['id']}")
        _require(not candidate["model_scenario_policy"]["allowed"], f"candidate model scenario is enabled: {candidate['id']}")
        _require(not candidate["perspective_policy"]["allowed"], f"candidate perspective rendering is enabled: {candidate['id']}")


def _candidate_promotion_reports_block() -> None:
    candidates = load_candidate_analysis_queue()
    validate_candidate_promotion_gate_reports(candidates)
    for candidate in candidates:
        report = evaluate_candidate_promotion(candidate)
        _require(not report["promotable"], f"candidate is promotable: {candidate['id']}")
        _require(report["publication_state_after_evaluation"] == "draft", f"candidate did not remain draft: {candidate['id']}")
        blocker_gates = {blocker["gate"] for blocker in report["blockers"]}
        _require("promotion_disabled" in blocker_gates, f"promotion-disabled blocker missing: {candidate['id']}")


def _candidate_promotion_request_stub_validates() -> None:
    validate_candidate_promotion_requests()
    requests = load_candidate_promotion_requests()
    _require(requests, "candidate promotion request fixture is empty")
    for request in requests:
        _require(request["request_status"] == "blocked", f"promotion request is not blocked: {request['id']}")
        _require(
            not request["execution_policy"]["promotion_execution_allowed"],
            f"promotion request allows execution: {request['id']}",
        )
        _require(
            not request["execution_policy"]["public_report_inclusion_allowed"],
            f"promotion request allows public report inclusion: {request['id']}",
        )
        _require(
            not request["execution_policy"]["ledger_append_allowed"],
            f"promotion request allows ledger append: {request['id']}",
        )
        _require(
            not request["execution_policy"]["household_financial_data_allowed"],
            f"promotion request allows household financial data: {request['id']}",
        )


def _candidate_promotion_decision_ledger_stub_validates() -> None:
    validate_candidate_promotion_decision_ledger_stubs()
    entries = load_candidate_promotion_decision_ledger_stubs()
    live_ledger_ids = {entry["id"] for entry in DecisionLedger().read_all()}
    _require(entries, "candidate promotion decision ledger stub fixture is empty")
    for entry in entries:
        output = entry["structured_output"]
        _require(entry["id"] not in live_ledger_ids, f"promotion decision stub is in live ledger: {entry['id']}")
        _require(output["promotion_decision"] == "blocked", f"promotion decision stub is not blocked: {entry['id']}")
        _require(not output["promotion_executed"], f"promotion decision stub executed promotion: {entry['id']}")
        _require(not output["public_report_inclusion_allowed"], f"promotion decision stub allows reporting: {entry['id']}")
        _require(not output["live_ledger_append_allowed"], f"promotion decision stub allows live append: {entry['id']}")
        _require(output["publication_state_after_decision"] == "draft", f"promotion decision did not keep draft: {entry['id']}")
        _require(entry["disclosure_class"] == "restricted", f"promotion decision stub is public: {entry['id']}")


def _candidate_promotion_audit_cross_check() -> None:
    validate_candidate_promotion_audit_cross_check()
    cross_check = build_candidate_promotion_audit_cross_check()
    _require(cross_check["candidate_ids_match"], "promotion audit candidate ids do not match")
    _require(not cross_check["public_report_includes_candidates"], "promotion audit found candidate public-report leakage")
    _require(cross_check["source_promotion_state"] == "blocked", "promotion audit source promotion is not blocked")
    _require(not cross_check["source_registry_update_allowed"], "promotion audit allows source registry updates")
    for summary in cross_check["candidate_summaries"]:
        _require(summary["blockers_match"], f"promotion audit blockers do not match: {summary['candidate_analysis_unit_id']}")
        _require(summary["source_refs_match"], f"promotion audit source refs do not match: {summary['candidate_analysis_unit_id']}")
        _require(
            not summary["decision_stub_in_live_ledger"],
            f"promotion audit found decision stub in live ledger: {summary['candidate_analysis_unit_id']}",
        )


def _candidate_extraction_stub_validates() -> None:
    validate_candidate_extraction_stub(load_candidate_analysis_queue())


def _candidate_extraction_policy_registry() -> None:
    registry = validate_candidate_extraction_policy_registry()
    for policy in registry.policies.values():
        _require(policy["status"] == "approved_for_dry_run", f"candidate policy is not dry-run approved: {policy['version']}")
        _require(policy["provider"].startswith("deterministic-"), f"candidate policy is not deterministic: {policy['version']}")
        _require(not policy["live_provider_authorized"], f"candidate policy authorizes live provider: {policy['version']}")
        _require(not policy["promotion_use_allowed"], f"candidate policy allows promotion use: {policy['version']}")
    candidate = load_candidate_analysis_queue()[0]
    source_refs = [ref["source_record_id"] for ref in candidate["source_snapshot_refs"]]
    CandidateExtractionPolicyRegistry.load().require_dry_run(
        "candidate-locator-extraction-poc-v1",
        "candidate_locator_extraction",
        source_refs,
    )


def _candidate_review_records_block() -> None:
    validate_candidate_review_records()
    records = load_candidate_review_records()
    _require(records, "candidate review records are empty")
    for record in records:
        _require(record["review_status"] != "approved", f"candidate review approves promotion: {record['id']}")
        _require(record["promotion_recommendation"] == "blocked", f"candidate review does not block promotion: {record['id']}")
        _require(record["publication_state_after_review"] == "draft", f"candidate review does not keep draft state: {record['id']}")
        _require(record["ledger_entry_required"], f"candidate review does not require ledger entry: {record['id']}")


def _candidate_review_ledger_stub_validates() -> None:
    validate_candidate_review_ledger_stub(load_candidate_review_records())


def _candidate_audit_bundle_validates() -> None:
    validate_candidate_audit_bundle()
    bundle = build_candidate_audit_bundle()
    _require(bundle["publication_scope"] == "internal_candidate_audit_only", "candidate audit bundle has unsafe scope")
    _require(not bundle["public_report_includes_candidates"], "candidate audit bundle detected candidate report leakage")
    _require(bundle["dry_run_ledger_summaries"]["candidate_extraction"], "candidate audit bundle missing extraction ledger summaries")
    _require(bundle["dry_run_ledger_summaries"]["candidate_review"], "candidate audit bundle missing review ledger summaries")


def _candidate_status_surfaces_blockers() -> None:
    status = build_candidate_status()
    _require(status["status"] == "ok", "candidate status did not return ok")
    _require(status["candidate_count"] == len(load_candidate_analysis_queue()), "candidate status count mismatch")
    _require(not status["public_report_includes_candidates"], "candidate status says public reports include candidates")
    _require(not status["ledger_appended"], "candidate status appended ledger")
    for candidate in status["candidates"]:
        _require(candidate["publication_state"] == "draft", f"candidate status not draft: {candidate['id']}")
        _require(not candidate["promotable"], f"candidate status promotable: {candidate['id']}")
        _require(candidate["promotion_blockers"], f"candidate status missing blockers: {candidate['id']}")
        _require(candidate["review_status"] in {"review_required", "blocked"}, f"candidate status review is not blocking: {candidate['id']}")


def _promotion_audit_status_surfaces_defined() -> None:
    cli = _read_repo_file("src/peoples_ledger/cli.py")
    server = _read_repo_file("src/peoples_ledger/backend/server.py")
    backend_test = _read_repo_file("tests/test_backend_integration.py")
    cli_test = _read_repo_file("tests/test_candidate_promotion_audit.py")
    _require("promotion-audit-status" in cli, "CLI missing promotion-audit-status")
    _require("/candidates/promotion-audit" in server, "backend missing promotion audit endpoint")
    _require("/candidates/promotion-audit" in backend_test, "backend test missing promotion audit endpoint")
    _require("promotion-audit-status" in cli_test, "CLI test missing promotion audit status command")


def _frontend_candidate_status_target_defined() -> None:
    app_js = _read_repo_file("frontend/app.js")
    index_html = _read_repo_file("frontend/index.html")
    frontend_test = _read_repo_file("tests/test_frontend_privacy.py")
    browser_test = _read_repo_file("tests/browser/privacy_egress.spec.js")
    _require("/candidates/status" in app_js, "frontend does not fetch candidate status")
    _require("/candidates/promotion-audit" in app_js, "frontend does not fetch promotion audit status")
    _require("candidate-status" in index_html, "frontend missing candidate status panel")
    _require("promotion-audit" in index_html, "frontend missing promotion audit panel")
    _require("/candidates/status" in frontend_test, "frontend privacy allowlist missing candidate status")
    _require("/candidates/promotion-audit" in frontend_test, "frontend privacy allowlist missing promotion audit status")
    _require("/candidates/status" in browser_test, "browser privacy spec missing candidate status fixture")
    _require("/candidates/promotion-audit" in browser_test, "browser privacy spec missing promotion audit fixture")


def _public_report_excludes_candidates() -> None:
    report = build_public_report()
    candidates = load_candidate_analysis_queue()
    candidate_ids = {candidate["id"] for candidate in candidates}
    candidate_provision_ids = {
        provision["id"]
        for candidate in candidates
        for provision in candidate["candidate_provisions"]
    }
    _require("candidate_analysis_units" not in report, "public report exposes candidate analysis units")
    _require(report["analysis_unit_id"] not in candidate_ids, "public report uses candidate analysis unit id")
    _require(not (candidate_provision_ids & {provision["id"] for provision in report["provisions"]}), "public report exposes candidate provisions")


def _phase2_privacy_boundaries_preserved() -> None:
    candidates = load_candidate_analysis_queue()
    for candidate in candidates:
        _require(not candidate["privacy"]["uses_household_financial_data"], f"candidate uses household data: {candidate['id']}")
        _require(not candidate["privacy"]["egress_allowed"], f"candidate permits household egress: {candidate['id']}")
    status = build_candidate_status()
    serialized = str(status).lower()
    for forbidden in ("household_income", "adjusted_gross_income", "ssn", "taxpayer_id"):
        _require(forbidden not in serialized, f"candidate status includes private field marker: {forbidden}")


def _phase2_scope_boundaries_preserved() -> None:
    forbidden_paths = [
        "src/peoples_ledger/bill_ingestion.py",
        "src/peoples_ledger/live_congressional_monitoring.py",
        "src/peoples_ledger/microsimulation.py",
        "src/peoples_ledger/state_modeling.py",
    ]
    for relative_path in forbidden_paths:
        _require(not (REPO_ROOT / relative_path).exists(), f"out-of-scope module exists: {relative_path}")
    docs = _read_repo_file("docs/phase-2-boundary.md")
    for phrase in ("broad bill ingestion", "live congressional monitoring", "full tax microsimulation", "state-level modeling"):
        _require(phrase in docs, f"phase 2 boundary missing out-of-scope phrase: {phrase}")


def _ci_phase2_gate_defined() -> None:
    workflow = _read_repo_file(".github/workflows/ci.yml")
    makefile = _read_repo_file("Makefile")
    _require("make phase2-acceptance" in workflow, "CI missing make phase2-acceptance")
    _require("phase2-acceptance:" in makefile, "Makefile missing phase2-acceptance target")


def _read_repo_file(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)
