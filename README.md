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

See `docs/phase-0-acceptance-checklist.md` for the Phase 0 acceptance mapping, `docs/testing-strategy.md` for the integrated testing approach, `docs/phase-1-boundary.md` and `docs/phase-1-status.md` for Phase 1, and `docs/phase-2-boundary.md` for the next planned work.

Licensing and intellectual-property decisions are intentionally deferred.

## Quick Start

```bash
make test
make validate
make assure
make phase1-acceptance
make phase2-acceptance
PYTHONPATH=src python3 -m peoples_ledger.cli candidate-status
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

The first statutory transformation slice is also fixture-first: supported operations produce validated transformation records, while ambiguous operations abstain instead of guessing.

The first report assembly slice emits a public JSON report with source traces, decision trace, model scenarios, perspective profiles, and assurance status.

Browser-local privacy hardening includes a dependency-free JavaScript runtime test and an explicit Playwright request-interception test that proves local-only controls do not trigger network calls or transmit local values.

Challenge-agent disagreement recording has begun with a deterministic test double that can write complete AI Decision Ledger entries.

Prompt-template governance is offline and enforceable: `make assure` validates the approved template registry, adapter requests with prompt-template versions require approved provider, task, and source refs, and live providers are rejected unless explicitly authorized in the template record.

Report artifact packaging writes JSON, HTML, a manifest with `sha256:` hashes, and a downloadable zip bundle.

## Scope Boundaries

This POC does not implement broad bill ingestion, full tax microsimulation, live congressional monitoring, or state-level modeling.

The code enforces the Milestone 1 and 2 privacy constraint: household financial data must not be transmitted or stored. Model scenarios use public aggregate assumptions only.
