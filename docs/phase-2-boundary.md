# Phase 2 Boundary

Phase 2 should begin only after Phase 1 is merged and `make phase1-acceptance` passes. The goal is to move from a single manual exemplar toward a controlled source-acquisition and candidate-analysis pipeline while keeping publication, privacy, provenance, and human-review controls intact.

## Phase 2 Goal

Prototype a guarded federal-source acquisition path for one additional narrow federal-tax source set, ending at candidate records that are not publicly publishable until they pass deterministic validation and review gates.

## Recommended First Unit

Build a fixture-first source acquisition manifest for a second federal-tax source set.

The first unit should:

- define a source-acquisition manifest schema
- add offline fixtures for one additional federal-tax source set
- validate source identity, URL, publisher, retrieval timestamp, and content hash
- produce candidate source records and source snapshots only
- keep candidate provision extraction out of public reports until validation gates are added
- keep all household financial data out of payloads, logs, prompts, and ledger entries

## In Scope

### Source Acquisition Manifests

- Add a schema for acquisition manifests.
- Represent source systems, URLs, expected hashes, retrieval policy, and storage mode.
- Start with checked-in fixtures and deterministic hash verification.
- Preserve source snapshots as the control plane for accepted material.

Initial status: started with a fixture-only IRA 2022 federal-tax source manifest that emits candidate source records and snapshots while remaining draft-only and excluded from public reports.

Required tests:

- manifests validate against schema
- fixture content hashes match expected hashes
- missing source identity or changed fixture text fails
- generated source records and snapshots match checked-in expected outputs

### Candidate Analysis Queue

- Represent candidate analysis units as draft-only records.
- Require explicit links to source snapshots.
- Require publication state `machine_parsed` or `draft` until assurance passes.
- Prevent candidate records from appearing in public reports by default.

Required tests:

- draft candidates cannot be reported as provisional analysis
- missing source snapshots block candidate advancement
- candidate IDs, source refs, and publication states are deterministic

Initial status: started with a draft-only IRA 2022 candidate queue fixture. The queue validates source-snapshot links against the source-acquisition manifest, disables model scenarios and perspective rendering, and remains absent from public reports.

### Review And Promotion Gates

- Extend the assurance gate for candidate-to-exemplar promotion.
- Require prompt-template approval for any AI-assisted extraction.
- Keep live providers disabled unless credentials, template approval, and human-review policy are explicitly configured.

Required tests:

- candidate promotion fails on schema, source, prompt, privacy, or ledger errors
- live-provider attempts fail without explicit authorization
- human-review-required states are represented in AI Decision Ledger entries

Initial status: started with a read-only promotion gate report. It returns deterministic blockers for schema, source-snapshot, prompt-template, privacy, human-review, ledger, and implementation-disabled gates, while leaving candidate publication state as `draft`.

Initial status: started with a deterministic candidate locator-extraction ledger stub. It records restricted AI Decision Ledger entries against a temporary ledger during assurance, does not call live providers, and does not promote or publicly report candidate content.

Initial status: added `candidate-status` as a read-only CLI inspection command for draft candidates, source references, and promotion blockers. It does not append to the AI Decision Ledger or expose candidates through public reports.

Initial status: added `/candidates/status` as a read-only backend endpoint with the same safe payload as the CLI status command. It does not append to the AI Decision Ledger, promote candidates, or add candidates to public report responses.

Initial status: added a minimal frontend candidate-status panel that reads `/candidates/status` and displays draft state and blockers without sending local privacy-control values or adding candidates to public report content.

Initial status: added `phase2-acceptance` as an executable checklist covering source acquisition, candidate queue, promotion blockers, extraction dry run, CLI/backend/frontend status, privacy, public-report exclusion, scope boundaries, assurance, and CI gating.

Initial status: added a candidate extraction policy registry for dry-run-only deterministic locator extraction. Candidate extraction policies must use deterministic providers, disable live providers, reference candidate source records, and remain disallowed for promotion use.

Initial status: added candidate review records as human-review stubs. These records document blocking findings and required followups while keeping candidates draft-only and disallowing promotion approval.

Initial status: added a candidate review ledger stub that records blocked human-review decisions in a restricted AI Decision Ledger entry during explicit calls or temporary-ledger assurance dry runs. It does not approve or promote candidates.

Initial status: added local candidate audit bundles for candidate status, promotion blockers, review records, and dry-run ledger summaries. These artifacts are explicitly internal candidate-audit output and remain separate from public reports.

## Out Of Scope

Phase 2 should not include:

- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- state-level modeling
- household financial data transmission or server storage
- production authentication or user accounts
- final licensing/IP decisions
- claims of motive, corruption, or reviewed loophole findings

## Exit Criteria

Phase 2 is complete when:

- a second federal-tax source set can be acquired from fixtures into validated source records and snapshots
- candidate records remain draft-only until deterministic promotion gates pass
- promotion gates preserve source, prompt-template, privacy, ledger, and review controls
- public reports still include only validated/provisional analysis records
- out-of-scope boundaries remain executable acceptance checks
- CI runs the full Phase 0, Phase 1, and Phase 2 non-browser test set

## Development Discipline

Every Phase 2 change must land with tests. The expected pattern remains:

1. Add or update schemas and fixtures.
2. Add failing tests for the trust claim.
3. Implement the smallest deterministic path that satisfies the tests.
4. Run `make validate`, `make assure`, `make phase1-acceptance`, and `make test`.
5. Run `make test-browser` when frontend privacy behavior changes.
6. Update documentation if the boundary, data contract, or user-visible behavior changes.
