# Phase 2 Candidate-To-Exemplar Promotion Contract

This contract defines the future path from a draft candidate analysis unit to a public/provisional exemplar. It is intentionally a design and testing boundary for the current POC: promotion remains disabled until every gate below has an implementation, deterministic fixtures, and acceptance coverage.

## Purpose

The promotion path must prove that a candidate record can be trusted as public report material without weakening the source, privacy, review, and AI governance controls established in Phase 0, Phase 1, and the first Phase 2 slices.

Promotion may only convert a candidate into a public/provisional analysis unit after all required gates pass. A failed, missing, or unimplemented gate must keep the candidate in draft state.

## Current POC Status

The current POC has:

- a fixture-only source-acquisition manifest and deterministic source snapshots
- a draft candidate analysis queue
- read-only promotion gate reports
- deterministic candidate extraction and review ledger stubs
- candidate review records with blocking findings
- candidate status surfaces for CLI, backend, and frontend inspection
- local candidate audit bundles

The current POC still blocks promotion because:

- `promotion_disabled` remains an active blocker
- no promotion-specific prompt template is approved
- human review records cannot approve promotion
- no promotion decision AI Decision Ledger entry exists
- candidate records remain excluded from public reports

## Non-Goals

This contract does not authorize:

- candidate promotion implementation in the current slice
- public report inclusion for candidate records
- live AI provider use
- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- state-level modeling
- household financial data transmission or storage
- production authentication or user accounts
- final licensing/IP decisions
- claims of motive, corruption, or reviewed loophole findings

## Required Gates

### Schema Gate

The candidate analysis unit must be converted into the full `analysis_unit` schema before public use. The promoted record must include validated provisions, claims and evidence, narrow-benefit indicators, model scenarios, perspective profiles, expected outputs, and source traces.

Schema validation must reject incomplete promoted records, draft-only fields in public records, candidate-only source references, and any record that would omit provenance needed for assurance.

### Source Gate

Candidate source records and snapshots may enter the public source registry only through a deterministic source promotion manifest or registry diff. The promoted sources must include stable IDs, publisher identity, authoritative locators, retrieval metadata, byte counts, and `sha256:` content hashes.

The gate must reject changed fixture text, missing hash checks, missing locator policy, unresolved candidate source references, and source material that has not been reviewed.

### Extraction And Prompt Gate

Any AI-assisted extraction used for promotion must run under an approved promotion-specific prompt template. The provider must be deterministic or explicitly authorized for the promotion task. Live providers must remain rejected unless credentials, provider policy, prompt-template approval, and human-review policy all authorize them.

Candidate dry-run extraction policies are not sufficient for promotion.

### Privacy Gate

Promotion inputs, outputs, logs, audit bundles, and AI Decision Ledger entries must assert that no household financial data is transmitted or stored. Promotion must use public statutory, public fiscal, and public aggregate assumptions only.

### Human Review Gate

A future promotion record must require a human review decision of `approved`. Current blocking review records must not pass. Review must cover candidate provisions, source spans, evidence links, narrow-benefit indicators, model scenario assumptions, expected outputs, and any challenged extraction decisions.

### Ledger Gate

Promotion must append complete AI Decision Ledger entries for extraction, human review, the promotion decision, and supersession when a promoted record replaces a previous exemplar. Ledger entries must include source refs, prompt-template refs when applicable, model/provider identity, deterministic test-double identity when applicable, abstentions or blockers, privacy assertions, and review status.

### Public Report Gate

Only promoted and validated records may appear in public reports. Candidate records, candidate provisions, candidate source snapshots, and blocked review records must remain excluded from report JSON, report HTML, export manifests, and downloadable bundles.

### Risk Gate

The promotion flow must evaluate risk tier and review triggers before public use. A high-risk extraction, disputed evidence link, changed source hash, missing source trace, or unresolved review finding must block promotion.

## Required Future Artifacts

Promotion implementation should add these artifacts before enabling any candidate-to-exemplar transition:

- `candidate_promotion_request` schema
- source promotion manifest or public source registry diff
- promoted analysis-unit expected fixture
- promotion decision AI Decision Ledger entry fixture
- promotion-specific prompt-template fixture
- promotion regression tests
- candidate-to-exemplar acceptance gate

## Test Strategy

Testing remains part of the development path, not a postscript. This contract is covered by executable documentation tests today and skipped future contract tests that name the behavior required before promotion can be enabled.

Future promotion work must follow this sequence:

1. Add or update schemas and fixtures.
2. Add failing tests for the trust claim being implemented.
3. Implement the smallest deterministic path that satisfies the tests.
4. Run focused schema, unit, regression, and integration tests.
5. Run `make validate`, `make assure`, `make phase1-acceptance`, `make phase2-acceptance`, and `make test`.
6. Run `make test-browser` when public report, backend, frontend, privacy, or export behavior changes.
