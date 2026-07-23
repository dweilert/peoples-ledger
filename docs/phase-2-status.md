# Phase 2 Status

This status page tracks the Phase 2 boundary defined in `docs/phase-2-boundary.md`. Testing remains integrated: each completed item below landed with schema, unit, integration, browser, assurance, or acceptance coverage.

## Current Checkpoint

Status: candidate pipeline checkpoint implemented for one additional federal-tax source set.

Run the checkpoint with:

```bash
make validate
make assure
make phase2-acceptance
PYTHONPATH=src python3 -m peoples_ledger.cli candidate-status
make export-candidate-audit
make test
make test-browser
```

## Completed Slices

### Fixture-Only Source Acquisition

Status: implemented for the IRA 2022 federal-tax candidate source set.

- `source_acquisition_manifest` schema exists.
- IRA 2022 source-acquisition fixture is checked in.
- Candidate source records and snapshots are generated deterministically.
- Fixture text is hash-checked with `sha256:` content hashes.
- Network retrieval remains disabled.
- Candidate sources remain excluded from the public source registry and public reports.

### Draft Candidate Analysis Queue

Status: implemented for one candidate analysis unit.

- `candidate_analysis_unit` schema exists.
- Candidate queue fixture is checked in.
- Candidate records remain `draft`.
- Candidate source snapshot refs are validated against source acquisition output.
- Model scenarios and perspective rendering are disabled for candidates.
- Public reports do not include candidate analysis units or candidate provisions.

### Promotion Gate Reports

Status: implemented as read-only blocker reports.

- `candidate_promotion_gate_report` schema exists.
- Promotion evaluation returns structured blockers.
- Current blockers cover prompt-template approval, human review, ledger readiness, and promotion-disabled policy.
- Evaluation is non-mutating and keeps candidates in draft.
- Promotion remains disabled even if nominal fixture requirements are toggled true.

### Candidate Extraction Governance

Status: implemented for deterministic dry runs only.

- `candidate_extraction_policy` schema exists.
- Candidate extraction policy registry is checked in separately from public prompt templates.
- Candidate extraction policy requires deterministic providers.
- Live providers are rejected.
- Required candidate source refs are enforced.
- Promotion use is disallowed.
- Candidate locator extraction can record restricted AI Decision Ledger entries in explicit calls.
- Assurance validates extraction through a temporary ledger dry run.

### Candidate Review Governance

Status: implemented as blocking review stubs.

- `candidate_review_record` schema exists.
- Candidate review fixture is checked in.
- Review records validate candidate, source snapshot, and candidate provision links.
- Review records cannot approve promotion.
- Review records require blocking findings, required followups, and a future ledger entry.
- Candidate review ledger recording can write restricted blocked-review AI Decision Ledger entries in explicit calls.
- Assurance validates review ledger behavior through a temporary ledger dry run.

### Candidate Status Surfaces

Status: implemented for CLI, backend, and frontend inspection.

- `candidate-status` prints draft candidate status and promotion blockers.
- `/candidates/status` exposes the same read-only payload.
- The frontend displays a minimal Phase 2 candidate-status panel.
- Status surfaces include review status and blocking findings.
- Status surfaces do not append to the AI Decision Ledger.
- Browser privacy tests allowlist the candidate-status endpoint and still prove local-only controls do not transmit values.

### Candidate Audit Bundle

Status: implemented for local internal artifacts.

- `make export-candidate-audit` writes a local candidate audit artifact and manifest.
- Candidate audit bundles include candidate status, promotion gate reports, review records, and dry-run ledger summaries.
- Audit manifests include byte counts and `sha256:` hashes.
- Candidate audit bundles are internal candidate-audit output, not public reports.
- Generated audit artifacts live under ignored `build/candidate-audit`.

### Phase 2 Acceptance Gate

Status: implemented and included in CI.

- `make phase2-acceptance` runs executable Phase 2 boundary checks.
- CI runs `make phase2-acceptance`.
- Acceptance covers source acquisition, draft queue behavior, promotion blockers, extraction governance, review governance, status surfaces, audit bundles, public-report exclusion, privacy, scope boundaries, and assurance.

### Candidate-To-Exemplar Promotion Contract

Status: documented and covered by executable contract tests.

- `docs/phase-2-promotion-contract.md` defines the future gates required before a draft candidate can become public/provisional analysis.
- Current promotion remains blocked by `promotion_disabled`, missing promotion-specific prompt-template approval, blocking human review, missing promotion decision ledger entries, and public-report exclusion.
- The contract names schema, source, extraction/prompt, privacy, human review, ledger, public report, and risk gates.
- Skipped future tests define the expected promotion behavior without enabling promotion in the current POC.

### Candidate Promotion Request Stub

Status: implemented as fixture-only blocked requests.

- `candidate_promotion_request` schema exists.
- The IRA 2022 candidate promotion request fixture validates against the schema.
- Promotion request fixtures must remain `blocked`.
- Execution, public-report inclusion, ledger append, live provider use, and household financial data are disallowed by schema and validation.
- Promotion request source refs must match candidate source snapshot refs.
- Promotion request blockers must include the current candidate promotion gate report blockers.
- Assurance and Phase 2 acceptance both validate promotion request fixtures.

### Source Promotion Manifest Stub

Status: implemented as a fixture-only blocked manifest.

- `source_promotion_manifest` schema exists.
- The IRA 2022 source promotion manifest validates candidate source records and snapshots against source-acquisition output.
- Source promotion manifests must remain `blocked`.
- Registry updates, public-report inclusion, and ledger appends are disallowed by schema and validation.
- Proposed source actions must remain `proposed_noop`.
- Proposed candidate source IDs must not appear in the public source registry.
- Assurance and Phase 2 acceptance both validate source promotion manifests.

### Promotion Decision Ledger Stub

Status: implemented as an offline fixture only.

- A blocked promotion decision AI Decision Ledger entry fixture exists for the IRA 2022 candidate.
- The fixture validates against `ai_decision_ledger_entry`.
- The fixture hash is verified with the same hash function as live ledger entries.
- The fixture links to the blocked candidate promotion request and candidate source refs.
- Promotion execution, live provider calls, public-report inclusion, and live ledger append are false in structured output.
- The fixture must remain absent from the live append-oriented AI Decision Ledger.
- Assurance and Phase 2 acceptance both validate the ledger-stub fixture.

### Promotion Audit Cross-Check

Status: implemented for internal audit consistency.

- The promotion audit cross-check compares candidate status, promotion gate reports, promotion request fixtures, source promotion manifests, review records, and promotion-decision ledger stubs.
- Cross-checks require matching candidate IDs, blocker gates, and candidate source refs.
- Cross-checks verify candidates remain draft, review remains blocked, source promotion remains blocked, decision stubs remain out of the live ledger, and public reports exclude candidates.
- The internal candidate audit bundle includes the promotion audit cross-check result.
- Assurance and Phase 2 acceptance both validate the cross-check.

## Still Blocked

These are intentionally blocked in the current POC:

- candidate promotion to provisional analysis
- public report inclusion for candidates
- promotion-specific prompt-template approval
- live AI provider use
- real human-review approval
- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- state-level modeling
- household financial data transmission or storage
- final licensing/IP decisions

## Recommended Next Work

The next useful unit is a small read-only CLI/backend status addition for the promotion audit cross-check. It should expose the same safe internal status summary without appending ledger entries, mutating candidates, or adding candidate records to public reports.
