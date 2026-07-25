# Project Handoff

Last updated: 2026-07-25

## Current Status

Phase 2 is complete for the bounded POC and merged to `main`.

Latest merged work:

- PR #14: read-only promotion audit CLI/backend status
- PR #15: frontend promotion audit panel with privacy tests
- PR #16: Phase 2 closure checklist and executable closure tests

Current branch to start from: `main`

Latest known `main` commit at handoff:

```text
137f6a2 Add Phase 2 closure checklist (#16)
```

Phase 2 closure is documented in `docs/phase-2-closure-checklist.md`.

## Validation At Handoff

The final Phase 2 closure pass used:

```bash
make validate
make assure
make phase1-acceptance
make phase2-acceptance
make test
make test-browser
```

Last full unit-suite result at handoff:

```text
Ran 197 tests
OK (skipped=3)
```

At the original Phase 2 handoff, the 3 skipped tests were intentional future-promotion contract tests. Current Phase 3 implementation has 3 skipped tests, all inherited from the original Phase 2 future-promotion contract.

## What Is Complete

- Phase 0/1 executable POC foundation
- TCJA manual exemplar
- source registry and source snapshots
- append-oriented AI Decision Ledger
- provider-neutral AI adapter with deterministic test doubles
- fixture-first source ingestion and statutory transformation
- public JSON/HTML report/export artifacts
- browser-local privacy hardening
- Phase 2 IRA 2022 fixture-only source acquisition
- draft candidate analysis queue
- candidate promotion blocker reports
- candidate extraction/review governance stubs
- candidate audit bundle
- candidate-to-exemplar promotion contract
- candidate promotion request stub
- source promotion manifest stub
- promotion decision ledger stub
- promotion audit cross-check
- CLI/backend/frontend status surfaces for candidate and promotion audit state
- Phase 2 closure checklist

## Still Intentionally Blocked

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
- production authentication or user accounts
- final licensing/IP decisions
- claims of motive, corruption, or reviewed loophole findings

## Recommended Next Step

Phase 3 implementation has started and now covers all disabled-by-default evaluator fixture gates. Continue only with read-only fixture evaluation. Do not implement real promotion.

Current first Phase 3 planning slice:

- `docs/phase-3-boundary.md` defines one disabled-by-default promotion request evaluator plan
- `docs/phase-3-promotion-evaluator-contract.md` defines the future evaluator contract without implementation
- `data/fixtures/phase3/promotion_evaluator_contract_examples.json` defines fixture-only expected failures for each evaluator gate
- `docs/phase-3-implementation-entry-checklist.md` defines the conditions required before evaluator implementation can start
- `docs/phase-3-evaluator-risk-review.md` records documentation-only risks and stop conditions for the evaluator boundary
- `docs/phase-3-planning-closure-checklist.md` records the planning artifacts, validation standard, blocked scope, and implementation decision point
- `src/peoples_ledger/promotion_request_evaluator.py` implements all Phase 3 evaluator fixture examples while keeping every result blocked
- `promotion-evaluator-status` exposes the evaluator status as read-only CLI JSON
- `/candidates/promotion-evaluator` exposes the evaluator status as read-only backend JSON
- the frontend displays `/candidates/promotion-evaluator` as a read-only Phase 3 evaluator panel with no promotion action
- `tests/test_phase3_boundary.py` provides executable planning/documentation tests
- `tests/test_phase3_promotion_evaluator_contract.py` covers the future evaluator contract
- `tests/test_phase3_promotion_evaluator_fixtures.py` validates the fixture-only examples
- `tests/test_phase3_promotion_evaluator_future.py` contains skipped future implementation tests for each fixture case
- `tests/test_phase3_implementation_entry_checklist.py` validates the implementation-entry checklist
- `tests/test_phase3_evaluator_risk_review.py` validates the risk review
- `tests/test_phase3_planning_closure.py` validates the planning closure checklist
- `tests/test_phase3_promotion_evaluator_status.py` validates the evaluator status builder and CLI
- keep promotion, public candidate reporting, live providers, broad ingestion, microsimulation, live monitoring, state modeling, and household financial data handling out of scope

## Continuation Prompt

Use this prompt when resuming the project:

```text
Continue work on The People's Ledger repository at /Users/bob/peoples-ledger.

Start by reading:
- README.md
- docs/phase-2-closure-checklist.md
- docs/phase-2-status.md
- docs/phase-2-promotion-contract.md
- docs/phase-3-boundary.md
- docs/phase-3-promotion-evaluator-contract.md
- docs/phase-3-implementation-entry-checklist.md
- docs/phase-3-evaluator-risk-review.md
- docs/phase-3-planning-closure-checklist.md
- data/fixtures/phase3/promotion_evaluator_contract_examples.json
- docs/project-handoff.md

Current status:
- Phase 2 is complete for the bounded POC and merged to main.
- Phase 3 disabled-by-default evaluator fixture implementation covers all Phase 3 gate examples.
- Latest known Phase 2 closure commit: 137f6a2 Add Phase 2 closure checklist (#16).
- The last complete validation passed:
  - make validate
  - make assure
  - make phase1-acceptance
  - make phase2-acceptance
  - make test
  - make test-browser
- The full unit suite last passed with 258 tests and 3 intentionally skipped future-promotion contract tests.

Continue with disabled-by-default Phase 3 evaluator implementation only. Keep promotion execution disabled.

Recommended next unit:
Add a checked API/status contract snapshot for the Phase 3 evaluator payload so future UI or backend changes cannot silently loosen blocked, fixture-only, no-mutation semantics. Keep promotion disabled. Do not implement promotion.

Keep these out of scope:
- candidate promotion execution
- public report inclusion for candidates
- live AI provider use
- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- state-level modeling
- household financial data transmission or storage
- production authentication or user accounts
- final licensing/IP decisions
- claims of motive, corruption, or reviewed loophole findings

Development expectations:
- Work on a feature branch using the codex/ prefix.
- Add or update tests with every change.
- Run focused tests first, then make validate, make assure, make phase1-acceptance, make phase2-acceptance, make test, and make test-browser when frontend/privacy behavior changes.
- Open a pull request, wait for checks, merge only after checks pass, and do not merge directly to main.
- Keep going autonomously unless user input is genuinely required.
```

## Why Use Pull Requests Instead Of Direct Commits To Main

Use feature branches and pull requests even when working alone because they create a durable checkpoint for each unit of work.

Benefits:

- Each PR has a clear scope, title, summary, test record, and out-of-scope list.
- GitHub Actions runs on the proposed change before it enters `main`.
- Review history stays readable: Phase 2 can be reconstructed from PR #3 through PR #16.
- Small PRs make rollback or diagnosis easier if a later change breaks something.
- `main` stays stable as the known-good branch.
- The workflow prevents accidental mixing of unrelated work.

Direct commits to `main` are faster in the moment, but they lose the checkpoint and review boundary. For this POC, PRs are useful because the project is building a trust/audit system; the development process should preserve the same kind of traceability the product is trying to provide.
