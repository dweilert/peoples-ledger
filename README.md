# The People's Ledger

Initial proof of concept for Milestones 1 and 2.

This repository establishes executable foundations for:

- enforceable schemas for core policy-analysis records
- an initial source registry
- an append-oriented AI Decision Ledger
- a provider-neutral AI adapter with deterministic test doubles
- an approved prompt-template registry for AI governance
- one manually curated TCJA analysis unit with expected outputs
- a small local backend and static frontend
- unit, schema, regression, and integration tests

The POC is aligned to the Foundational Product and System Design v0.3 acceptance criteria for the bounded manual exemplar: a representative 8-12 provision TCJA subset, source spans, deterministic statutory-transformation records, governed model scenarios, three perspective profiles, perspective invariance checks, and complete AI Decision Ledger provenance fields.

See `docs/project-handoff.md` for the current handoff note, `docs/phase-0-acceptance-checklist.md` for the Phase 0 acceptance mapping, `docs/testing-strategy.md` for the integrated testing approach, `docs/phase-1-boundary.md` and `docs/phase-1-status.md` for Phase 1, `docs/phase-2-boundary.md`, `docs/phase-2-status.md`, `docs/phase-2-promotion-contract.md`, plus `docs/phase-2-closure-checklist.md` for Phase 2, and `docs/phase-3-boundary.md` plus `docs/phase-3-promotion-evaluator-contract.md` for Phase 3 planning.

Licensing and intellectual-property decisions are intentionally deferred.

## Quick Start

```bash
make test
make validate
make assure
make phase1-acceptance
make phase2-acceptance
PYTHONPATH=src python3 -m peoples_ledger.cli candidate-status
PYTHONPATH=src python3 -m peoples_ledger.cli promotion-audit-status
make test-browser
make report
make report-html
make export-report
make export-candidate-audit
make run
```

Then open `frontend/index.html` or call the local API at `http://127.0.0.1:8787`.

CI runs `make validate`, `make assure`, `make phase1-acceptance`, and `make test` on pushes and pull requests. `make test-browser` is an explicit local browser-privacy check that requires the Playwright CLI and a Chromium browser install.

Phase 2 acceptance is executable with `make phase2-acceptance` and is included in CI while Phase 2 work is active.

The first Phase 1 workstream is fixture-first source ingestion; it is offline, deterministic, and covered by tests before any live connector work.

Phase 2 has begun with fixture-only source-acquisition manifests for a second federal-tax source set. These records are candidate-only, deterministic, and excluded from public reports until promotion gates exist.

The Phase 2 candidate queue is also fixture-first: draft analysis candidates link to acquired source snapshots, disable model/perspective rendering, and cannot be promoted or reported until explicit gates are implemented.

Promotion gate evaluation has begun as a read-only report: it explains blocking schema, source, prompt-template, privacy, human-review, ledger, and implementation gates while keeping candidates in draft.

Candidate locator extraction is represented by a deterministic ledger stub. It writes restricted AI Decision Ledger entries in tests or explicit calls, while assurance uses a temporary ledger and no live provider.

Candidate extraction policy is checked in separately from public prompt templates. It is dry-run-only, deterministic-provider-only, tied to candidate source refs, and disallowed for promotion use.

Candidate review records are human-review stubs: they document blocking findings and required followups without approving promotion or changing draft candidate state.

Candidate review ledger recording is also a stub: it can record a restricted blocked-review AI Decision Ledger entry, while assurance uses only a temporary ledger dry run.

Candidate audit bundles are local artifacts exported with `make export-candidate-audit`. They collect candidate status, blockers, review records, and dry-run ledger summaries without adding candidate content to public reports.

`candidate-status` prints draft Phase 2 candidate status and promotion blockers without appending ledger entries or changing public reports.

The backend also exposes the same read-only payload at `/candidates/status` for local inspection without ledger writes or public-report changes.

The frontend includes a small Phase 2 candidate-status panel that displays draft candidates and blockers from `/candidates/status` without collecting or transmitting household financial data.

The candidate-to-exemplar promotion contract is documented and covered by executable tests. It defines future schema, source, prompt, privacy, review, ledger, report, and risk gates while keeping promotion disabled in the current POC.

Candidate promotion requests are represented as fixture-only blocked records. The schema and assurance gates disallow execution, public-report inclusion, ledger appends, live providers, and household financial data.

Candidate source promotion is also represented as a fixture-only blocked manifest. It validates proposed source records and snapshots against source-acquisition output while keeping the public source registry unchanged.

A blocked promotion decision AI Decision Ledger entry exists as an offline fixture. It validates the future ledger payload shape and hash while remaining absent from the live append-oriented ledger.

An internal promotion audit cross-check compares candidate status, promotion requests, source promotion manifests, review records, and decision stubs for consistent blockers and source refs.

The same promotion audit cross-check is exposed through the read-only `promotion-audit-status` CLI command, `/candidates/promotion-audit` backend endpoint, and frontend promotion audit panel.

Phase 2 is complete for the bounded POC. The closure checklist records the exit criteria, remaining intentional blockers, and Phase 3 entry criteria without starting Phase 3 work.

Phase 3 implementation has started with approved schema, source, extraction-prompt, privacy, and human-review disabled-by-default promotion request evaluator slices. No candidate promotion execution is enabled.

The Phase 3 promotion request evaluator contract now defines the future read-only fixture inputs, deterministic gate order, result shape, blocker codes, privacy precedence, and mutation prohibitions while keeping the evaluator unimplemented.

Phase 3 evaluator contract examples live at `data/fixtures/phase3/promotion_evaluator_contract_examples.json`. They cover each first-failing gate as fixture-only expected outputs and still do not promote candidates or alter public reports.

Skipped future evaluator tests now name the required behavior for later fixture cases while schema, source, extraction-prompt, privacy, and human-review evaluator slices exist.

The Phase 3 implementation-entry checklist at `docs/phase-3-implementation-entry-checklist.md` defines what must be true before any evaluator code can be started, including owner approval, test-first sequencing, read-only fixture scope, and privacy gates.

The Phase 3 evaluator risk review at `docs/phase-3-evaluator-risk-review.md` records approval-confusion, privacy, fixture-creep, live-provider, ledger, public-report, and claim-overreach risks while later gates remain blocked.

The Phase 3 planning closure checklist at `docs/phase-3-planning-closure-checklist.md` records the current planning artifacts, validation standard, blocked scope, and implementation decision point.

The first statutory transformation slice is also fixture-first: supported operations produce validated transformation records, while ambiguous operations abstain instead of guessing.

The first report assembly slice emits a public JSON report with source traces, decision trace, model scenarios, perspective profiles, and assurance status.

Browser-local privacy hardening includes a dependency-free JavaScript runtime test and an explicit Playwright request-interception test that proves local-only controls do not trigger network calls or transmit local values.

Challenge-agent disagreement recording has begun with a deterministic test double that can write complete AI Decision Ledger entries.

Prompt-template governance is offline and enforceable: `make assure` validates the approved template registry, adapter requests with prompt-template versions require approved provider, task, and source refs, and live providers are rejected unless explicitly authorized in the template record.

Report artifact packaging writes JSON, HTML, a manifest with `sha256:` hashes, and a downloadable zip bundle.

## Scope Boundaries

This POC does not implement broad bill ingestion, full tax microsimulation, live congressional monitoring, or state-level modeling.

The code enforces the Milestone 1 and 2 privacy constraint: household financial data must not be transmitted or stored. Model scenarios use public aggregate assumptions only.
