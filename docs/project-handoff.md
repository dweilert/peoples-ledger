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

The 3 skipped tests are intentional future-promotion contract tests. They define behavior that must stay blocked until a future phase explicitly implements promotion gates.

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

Phase 3 planning has started. Continue planning only unless the project owner explicitly approves implementation. Do not implement real promotion yet.

Current first Phase 3 planning slice:

- `docs/phase-3-boundary.md` defines one disabled-by-default promotion request evaluator plan
- `docs/phase-3-promotion-evaluator-contract.md` defines the future evaluator contract without implementation
- `tests/test_phase3_boundary.py` provides executable planning/documentation tests
- `tests/test_phase3_promotion_evaluator_contract.py` covers the future evaluator contract
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
- docs/project-handoff.md

Current status:
- Phase 2 is complete for the bounded POC and merged to main.
- Latest known Phase 2 closure commit: 137f6a2 Add Phase 2 closure checklist (#16).
- The last complete validation passed:
  - make validate
  - make assure
  - make phase1-acceptance
  - make phase2-acceptance
  - make test
  - make test-browser
- The full unit suite last passed with 197 tests and 3 intentionally skipped future-promotion contract tests.

Continue with Phase 3 planning only unless I explicitly approve implementation.

Recommended next unit:
Add fixture-only Phase 3 evaluator contract examples for each gate failure. These should be documentation fixtures or skipped future tests only. Do not implement promotion.

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
