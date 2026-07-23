# Testing Strategy

Testing is part of the development approach for The People's Ledger. New behavior should not be treated as complete until the relevant tests, fixtures, and validation gates are updated with it.

## Development Rule

Every feature, schema change, data fixture, model scenario, AI workflow, privacy boundary, or publication path must include tests in the same change set. A pull request should explain what trust claim the tests prove.

## Required Test Layers

### Contract Tests

Purpose: protect the public data model.

- Validate every bundled fixture against its schema.
- Include negative tests for missing or invalid required fields.
- Version schemas before accepting incompatible changes.
- Add migration tests when persisted data must move between schema versions.

### Provenance Tests

Purpose: prove every public output can be traced.

- Every provision has source spans.
- Every claim has evidence.
- Every indicator points to existing claim evidence.
- Every source span references a registered source snapshot.
- Every material AI action has a valid AI Decision Ledger entry.
- Ledger hash-chain verification detects mutation or broken ordering.

### Privacy Tests

Purpose: enforce the no-household-financial-data boundary.

- Backend code rejects household financial fields before AI calls or ledger writes.
- Frontend household-like controls remain browser-local.
- Browser-local controls have no form submission names, storage path, or backend submission path.
- Network calls are allowlisted.
- Future browser tests must intercept requests and fail if local values leave the browser.

### Deterministic Transformation Tests

Purpose: keep statutory reconstruction out of unsupported AI-only logic.

- Amendment operations must be deterministic and fixture-backed.
- Before/after hashes must match expected outputs.
- Round-trip reconciliation must pass where authoritative post-enactment text is available.
- Ambiguous operations must abstain and escalate instead of guessing.
- AI may propose candidate transformations, but deterministic validators decide whether an operation is publishable.

### AI Adapter Tests

Purpose: keep AI provider use inspectable and replaceable.

- Provider-neutral adapters must work with deterministic test doubles.
- Outputs must carry provider, model, model version, prompt-template version, source refs, and ledger provenance.
- Unsupported prose cannot enter public outputs without source references and validation.
- Model disagreement, validation failures, and review triggers must be represented in ledger entries.

### Scenario And Perspective Tests

Purpose: prevent hidden steering.

- Perspective profiles cannot alter common evidence.
- Perspective profiles cannot alter statutory transformations.
- Perspective profiles cannot alter governed model-scenario parameters.
- Material counterevidence remains available in every profile.
- Every technical output identifies a `model_scenario_id`.

### Regression Tests

Purpose: make corrections durable.

- Every correction should add or update a test that would have caught the issue.
- Source locator errors become locator regressions.
- Incorrect indicators become indicator regressions.
- Failed transformations become before/after fixture regressions.
- Privacy defects become egress or rejection regressions.

### Integration Tests

Purpose: verify the product works as an executable system.

- CLI validation succeeds.
- Backend endpoints return valid records.
- Frontend uses only approved API endpoints.
- Ledger append/read works end to end.
- Future ingestion tests should cover source acquisition to candidate provision to validation to publication state.

### Golden Exemplar Tests

Purpose: keep the manual TCJA exemplar stable and useful.

- The representative 8-12 provision subset remains complete.
- Expected summaries and public JSON outputs remain stable unless intentionally changed.
- Source spans, transformations, claims, indicators, model scenarios, perspectives, and decision entries stay mutually linked.
- Known edge cases remain represented: sunsets, interactions, entity-form advantage, geographic concentration, business provisions, estate provisions, and international rules.

## Merge Gates

Before merge, CI must pass:

- `make validate`
- `make test`

As the project grows, add gates for:

- type checks
- linting
- browser egress tests
- generated report snapshot tests
- source snapshot hash checks
- coverage thresholds for deterministic policy logic

## Phase Discipline

Phase 0 tests prove schema validity, traceability, privacy boundaries, ledger integrity, perspective invariance, and executable POC behavior.

Phase 1 tests should add deterministic statutory transformation fixtures, source-ingestion fixtures, abstention/escalation cases, challenge-agent disagreement cases, stronger source snapshot verification, report snapshot tests, and browser-level privacy egress tests. See `docs/phase-1-boundary.md`.
