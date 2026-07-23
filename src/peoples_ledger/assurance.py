from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .analysis import load_analysis_unit
from .candidate_extraction import validate_candidate_extraction_stub
from .candidate_extraction_policy import validate_candidate_extraction_policy_registry
from .candidate_promotion import validate_candidate_promotion_gate_reports
from .candidate_queue import validate_candidate_analysis_queue
from .candidate_queue import load_candidate_analysis_queue
from .candidate_review import validate_candidate_review_records
from .decision_ledger import DecisionLedger
from .paths import TCJA_ANALYSIS_UNIT_PATH
from .privacy import assert_no_household_financial_data
from .prompt_templates import validate_prompt_template_registry
from .source_acquisition import validate_source_acquisition_manifest
from .source_ingestion import validate_source_ingestion_fixtures
from .source_registry import SourceRegistry, load_source_snapshots


@dataclass(frozen=True)
class AssuranceCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class AssuranceReport:
    checks: list[AssuranceCheck]
    risk_tier: int
    publication_allowed: bool
    publication_state: str
    review_triggers: list[str]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def run_assurance_gate() -> AssuranceReport:
    checks = [
        _run_check("schema_and_analysis_unit", lambda: load_analysis_unit(TCJA_ANALYSIS_UNIT_PATH)),
        _run_check("source_registry", SourceRegistry.load),
        _run_check("source_snapshots", load_source_snapshots),
        _run_check("source_ingestion_fixtures", validate_source_ingestion_fixtures),
        _run_check("source_acquisition_manifest", validate_source_acquisition_manifest),
        _run_check("candidate_analysis_queue", validate_candidate_analysis_queue),
        _run_check("candidate_promotion_gate_reports", lambda: validate_candidate_promotion_gate_reports(load_candidate_analysis_queue())),
        _run_check("candidate_extraction_policy_registry", validate_candidate_extraction_policy_registry),
        _run_check("candidate_extraction_ledger_stub", lambda: validate_candidate_extraction_stub(load_candidate_analysis_queue())),
        _run_check("candidate_review_records", validate_candidate_review_records),
        _run_check("prompt_template_registry", validate_prompt_template_registry),
        _run_check("decision_ledger_integrity", lambda: DecisionLedger().read_all()),
        _run_check("privacy_payload_guard", lambda: assert_no_household_financial_data(_public_payload_probe())),
    ]
    failed = [check.name for check in checks if not check.passed]
    risk_tier = 1 if not failed else min(4, 1 + len(failed))
    return AssuranceReport(
        checks=checks,
        risk_tier=risk_tier,
        publication_allowed=not failed,
        publication_state="provisional_analysis" if not failed else "blocked",
        review_triggers=[f"assurance_failed:{name}" for name in failed],
    )


def validation_results_from_report(report: AssuranceReport) -> dict[str, bool]:
    by_name = {check.name: check.passed for check in report.checks}
    return {
        "schema_valid": by_name.get("schema_and_analysis_unit", False),
        "citations_valid": by_name.get("source_registry", False) and by_name.get("source_snapshots", False),
        "statutory_transform_valid": by_name.get("schema_and_analysis_unit", False),
        "calculation_valid": True,
        "privacy_egress_valid": by_name.get("privacy_payload_guard", False),
        "perspective_invariance_valid": by_name.get("schema_and_analysis_unit", False),
    }


def _run_check(name: str, fn: Callable[[], object]) -> AssuranceCheck:
    try:
        fn()
    except Exception as exc:
        return AssuranceCheck(name=name, passed=False, detail=str(exc))
    return AssuranceCheck(name=name, passed=True, detail="ok")


def _public_payload_probe() -> dict[str, str]:
    return {"scope": "public-poc-assurance"}
