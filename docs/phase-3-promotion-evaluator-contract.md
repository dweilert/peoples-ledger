# Phase 3 Promotion Request Evaluator Contract

This contract defines the future disabled-by-default promotion request evaluator. It is a planning artifact for Phase 3. It does not implement promotion, does not authorize promotion, and does not change any candidate, source registry, public report, or live AI Decision Ledger state.

## Contract Goal

The evaluator will explain the first gate that blocks a candidate promotion request and all blockers that remain unresolved. It must be deterministic, local-only, fixture-driven, and safe to run in tests before any promotion path exists.

The evaluator is not a promotion executor. A passing response is impossible while `promotion_disabled` remains active.

## Proposed Interface

Future module name, if implementation is later approved:

```text
peoples_ledger.promotion_request_evaluator
```

Future entry point, if implementation is later approved:

```text
evaluate_promotion_request(request_id: str, fixture_root: Path | None = None) -> PromotionEvaluationResult
```

Approved Phase 3 implementation slices may create this module and entry point for the schema, source, extraction-prompt, privacy, and human-review fixture cases only. Later gates remain skipped until their own approved implementation slices.

## Required Inputs

The future evaluator may read only local fixture artifacts:

- `candidate_promotion_request`
- `candidate_analysis_unit`
- `candidate_promotion_gate_report`
- `source_promotion_manifest`
- `candidate_review_record`
- `promotion_decision_ledger_stub`
- `public_report_candidate_leak_check`
- `risk_review_status`

Inputs must be read-only. The evaluator must not write candidate records, source registry records, report artifacts, AI Decision Ledger entries, prompt-template records, or household financial data.

## Result Shape

A future result must expose this logical shape:

```text
request_id: str
candidate_analysis_unit_id: str
status: "blocked"
first_failing_gate: str
gate_order: list[str]
blockers: list[PromotionEvaluationBlocker]
mutation_performed: false
ledger_appended: false
public_report_changed: false
live_provider_called: false
household_financial_data_detected: bool
```

`status` must remain `blocked` until a later approved phase removes the `promotion_disabled` hard stop.

## Blocker Shape

A future blocker must expose this logical shape:

```text
gate: str
code: str
message: str
source_artifact: str
source_ref: str | null
remediation_hint: str
```

Messages and remediation hints must be factual. They must not claim motive, corruption, or loophole findings.

## Gate Order

The evaluator must inspect gates in this deterministic order:

1. schema
2. source
3. extraction_prompt
4. privacy
5. human_review
6. ledger
7. public_report
8. risk
9. promotion_disabled

`first_failing_gate` is the earliest failing gate in that list. `blockers` may include later failures for audit visibility, but the first failure must never be reordered for convenience.

## Error Taxonomy

The future evaluator should use stable blocker codes:

- `schema.invalid_request`
- `schema.missing_candidate`
- `source.manifest_missing`
- `source.snapshot_hash_mismatch`
- `source.registry_mutation_required`
- `extraction_prompt.template_unapproved`
- `extraction_prompt.live_provider_unapproved`
- `privacy.household_financial_data_detected`
- `privacy.egress_requested`
- `human_review.not_approved`
- `human_review.blocking_findings_present`
- `ledger.decision_stub_missing`
- `ledger.live_append_required`
- `public_report.candidate_leakage_detected`
- `risk.unresolved_review_trigger`
- `promotion_disabled.phase3_hard_stop`

The taxonomy is intentionally narrower than a full promotion system. It is enough to preserve the POC boundary and make future failures testable.

## Privacy Rules

The evaluator must fail `privacy` before review, ledger, report, risk, or promotion-disabled gates when any input includes household financial data markers, household-specific tax facts, egress requests, live provider requests, local-storage of household values, or browser/API payload fields that look like household financial data.

The evaluator must not redact and continue. It must return a privacy blocker and keep all mutation flags false.

## Output Rules

The evaluator may return structured JSON-like data for local inspection. It must not:

- append to the live AI Decision Ledger
- create a promotion decision entry
- mark a candidate as approved
- mark a candidate as promotable
- create a promoted analysis unit
- update source registry records
- update public JSON, HTML, export, or downloadable report bundles
- call a live AI provider
- transmit or store household financial data

## Required Fixtures Before Implementation

Before any implementation slice starts, add fixtures that represent:

- invalid request fails `schema`
- source hash mismatch fails `source`
- unapproved prompt template fails `extraction_prompt`
- household data marker fails `privacy`
- blocking review record fails `human_review`
- missing decision ledger stub fails `ledger`
- candidate leak marker fails `public_report`
- unresolved risk trigger fails `risk`
- otherwise clean request still fails `promotion_disabled`

These fixtures must remain local and candidate-only.

## Required Tests Before Implementation

Before evaluator code exists, executable documentation tests must assert:

- this contract exists
- the interface is limited to approved schema, source, extraction-prompt, privacy, and human-review implementation slices
- required input fixture names are present
- result and blocker shapes are documented
- stable blocker codes are documented
- privacy failure precedence is documented
- all mutation and egress outputs are forbidden
- gate order matches the Phase 3 boundary
- implementation module remains limited to approved schema, source, extraction-prompt, privacy, and human-review fixture cases

Fixture-only examples are defined in `data/fixtures/phase3/promotion_evaluator_contract_examples.json`. They describe the expected first failing gate, primary blocker code, and no-mutation flags for each planned gate without creating an evaluator implementation.

When implementation is later approved, tests must be added before code for each fixture case listed above.

## Exit Criteria For This Contract Slice

This planning slice is complete when:

- this contract document exists
- README and handoff point to it
- executable documentation tests cover the contract
- Phase 2 and Phase 3 boundary tests still pass
- no promotion request evaluator implementation beyond approved schema, source, extraction-prompt, privacy, and human-review fixture cases exists
- no candidate is promoted
- no public report contains candidate content
- no live provider path is enabled
- no household financial data is transmitted or stored
