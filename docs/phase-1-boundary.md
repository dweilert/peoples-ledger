# Phase 1 Boundary

Phase 1 should begin only after Phase 0 is accepted as the executable trust foundation. The goal is to add the first real automation paths while preserving the same evidence, privacy, provenance, and testing discipline.

## Phase 1 Goal

Prototype controlled source ingestion and deterministic statutory transformation for a narrow federal-tax slice, using fixture-backed workflows before any live monitoring or broad bill coverage.

## In Scope

### Source Ingestion Prototype

- Add connectors or import scripts for selected Congress.gov and GovInfo records.
- Preserve source identity, retrieval timestamps, URLs, content hashes, and raw-to-structured provenance.
- Start with fixture-first ingestion before live network workflows.
- Keep source snapshot manifests as the control plane for what is accepted.

Initial status: started with offline TCJA source-ingestion fixtures. The first implementation validates fixture metadata, computes stable content hashes, emits source records and snapshot records, and fails when fixture text no longer matches the expected hash.

Required tests:

- fixture ingestion produces stable source records
- source hashes match expected fixture hashes
- missing or changed source metadata fails validation
- no ingestion output bypasses schema validation

### Deterministic Statutory Transformation Engine

- Implement a small set of supported amendment operations.
- Represent unsupported or ambiguous amendment language as abstentions, not guessed transformations.
- Produce before/after hashes, operation records, reconciliation status, and review triggers.
- Keep LLM usage limited to candidate extraction or explanation; deterministic validators decide publishability.

Initial status: started with fixture-backed `replace_text` and `insert_after` operations. Successful operations emit schema-compatible statutory-transformation records; unmatched, ambiguous, or incomplete operations abstain with review triggers and do not produce valid transformation records.

Required tests:

- supported operations produce expected before/after fixtures
- round-trip reconciliation passes for known fixtures
- ambiguous operations abstain and create review triggers
- transformed outputs link to source spans and affected authority

### Automated Assurance Scaffold

- Add validation orchestration that runs schema, source-link, transformation, privacy, perspective-invariance, and ledger checks together.
- Add risk-tier stubs for publication routing.
- Add challenge-agent/test-double interfaces without depending on live model calls.

Initial status: started with `make assure`, which runs the bundled assurance gate and reports named check results, risk tier, publication state, publication allowance, and review triggers.

Required tests:

- failed validators block publication-state advancement
- risk-tier outputs are deterministic for fixtures
- challenge-agent disagreement is recorded in the AI Decision Ledger
- validation results are preserved in decision records

### Report Assembly Prototype

- Generate a public JSON or static HTML report from the exemplar records.
- Preserve the distinction between fact, estimate, flag, finding, opinion, publication state, model scenario, and perspective.
- Keep downloadable data traceable to schemas and source snapshots.

Initial status: started with a public JSON report assembled from the exemplar, source manifest, decision trace, model scenarios, perspective profiles, and assurance status. The report is available through `make report` and the local backend.

Required tests:

- generated report snapshots are stable
- every displayed claim traces to evidence
- no automated indicator uses prohibited shortcut language
- perspective views preserve invariant evidence and model-scenario definitions

### Browser-Local Privacy Hardening

- Add browser-level tests for local household-like controls.
- Intercept network requests and fail if local values leave the browser.
- Keep third-party scripts absent unless explicitly reviewed.

Required tests:

- Playwright or equivalent request interception proves local inputs are not transmitted
- server logs do not receive local values
- frontend remains on an allowlisted endpoint set

## Out Of Scope

Phase 1 should not include:

- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- household financial data transmission or server storage
- state-level modeling
- production auth or user accounts
- final licensing/IP decisions
- claims of motive, corruption, or reviewed loophole findings

## Exit Criteria

Phase 1 is complete when:

- fixture-backed ingestion can produce validated source records and snapshots
- at least one deterministic statutory transformation operation works end to end
- ambiguous statutory operations abstain with review triggers
- generated reports remain traceable and snapshot-tested
- AI Decision Ledger entries record validation, risk, disagreement, source hashes, and model scenario
- browser-level privacy tests prove local values do not leave the client
- CI runs the full Phase 0 and Phase 1 test set

## Development Discipline

Every Phase 1 change must land with its tests. The expected pattern is:

1. Add or update fixtures.
2. Add failing tests for the trust claim.
3. Implement the smallest code path that satisfies the tests.
4. Run `make validate` and `make test`.
5. Update documentation if the boundary, data contract, or user-visible behavior changes.

Testing remains part of implementation, not a follow-up task.
