# Phase 1 Status

This status page tracks the Phase 1 boundary defined in `docs/phase-1-boundary.md`. Testing remains integrated: each completed item below landed with validation or test coverage.

## Completed Slices

### Fixture-First Source Ingestion

Status: implemented for POC fixtures.

- Offline TCJA source-ingestion fixtures exist.
- Fixture text produces deterministic `sha256:` hashes.
- Generated source records and snapshot records validate against schemas.
- Generated records are compared against the checked-in registry and snapshot manifest.
- Hash mismatch and missing metadata have negative tests.

### Deterministic Statutory Transformation Slice

Status: implemented for first operations.

- `replace_text` is supported.
- `insert_after` is supported.
- Successful operations emit schema-compatible statutory-transformation records.
- Before/after hashes are stable.
- Unmatched, ambiguous, and incomplete operations abstain with review triggers.

### Automated Assurance Gate

Status: implemented for current POC.

- `make assure` runs named checks.
- The gate reports publication allowance, publication state, risk tier, and review triggers.
- CI runs `make validate`, `make assure`, and `make test`.

### Public Report Assembly

Status: implemented for JSON and static HTML report.

- `make report` emits a public JSON report.
- `make report-html` emits a static HTML report.
- The backend exposes `/reports/tcja-2017-representative-provisions`.
- The backend exposes `/reports/tcja-2017-representative-provisions.html`.
- Report output includes source manifest, decision trace, model scenarios, perspective profiles, publication decision, and assurance checks.
- Snapshot-style tests protect the report shape.

### Browser-Local Privacy Hardening

Status: implemented without external browser dependencies.

- Frontend local-only controls have static privacy tests.
- A Node-backed test executes frontend JavaScript with a stubbed DOM and fetch layer.
- Local-only control changes do not trigger network calls.
- Full Playwright request interception remains a later enhancement when browser dependencies are added.

### Challenge-Agent Disagreement Recording

Status: implemented with deterministic test double.

- A deterministic challenge agent reviews the exemplar.
- Nonblocking disagreement is represented.
- Under-representative coverage blocks in tests.
- Challenge reviews can write complete AI Decision Ledger records.

### Publication-State Advancement Policy

Status: implemented for first rules.

- Passing assurance allows provisional analytical publication.
- Assurance failure blocks advancement.
- Blocking challenge disagreement prevents provisional advancement.
- High-risk outputs require review.

### Correction Workflow Fixture

Status: implemented for first regression fixture.

- A correction-record schema exists.
- A POC correction fixture preserves target, root cause, previous output, corrected output, superseded decision, and regression-test reference.
- Correction recording writes a hash-chained AI Decision Ledger entry with `publication_state: corrected`.
- Public reports surface correction records.

### Risk Scoring Dimensions

Status: implemented for first deterministic dimensions.

- Risk scoring includes assurance failures, challenge disagreement, unknown indicator count, and representative coverage.
- Public reports include risk dimensions, rationale, and tier.
- Tests cover current POC risk, assurance failure, blocking challenge disagreement, and under-representative coverage.

## Remaining Phase 1 Enhancements

These are useful but no longer block the first Phase 1 POC slice:

- add real Playwright browser request-interception tests
- add more statutory transformation operation fixtures
- add authoritative post-enactment round-trip fixtures
- add richer static HTML styling and downloadable artifact packaging
- add more correction workflow fixtures and correction-derived regression tests
- add more risk scoring dimensions as new automation paths create new risks
- add challenge-agent disagreement comparison across multiple deterministic agents

## Still Out Of Scope

- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- household financial data transmission or server storage
- state-level modeling
- production authentication
- final licensing/IP strategy
- claims of motive, corruption, or reviewed loophole findings
