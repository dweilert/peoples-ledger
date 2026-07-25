# Phase 3 Evaluator Slice Completion Checklist

This checklist records the current Phase 3 evaluator slice as implemented but disabled. It approves only the read-only, fixture-only evaluator status path already present in this POC. It does not approve candidate promotion execution.

## Completed Surface

- `src/peoples_ledger/promotion_request_evaluator.py` evaluates all checked Phase 3 fixture examples.
- `promotion-evaluator-status` prints read-only evaluator status JSON.
- `/candidates/promotion-evaluator` exposes read-only evaluator status JSON.
- The frontend renders the Phase 3 evaluator status panel with blocked status, first failing gates, blocker codes, and no-mutation flags.
- `data/fixtures/phase3/promotion_evaluator_status_contract.json` snapshots the stable status contract view.
- `schemas/phase3_promotion_evaluator_status.schema.json` validates the stable status contract view.
- `make assure` includes `phase3_promotion_evaluator_status_contract`.

## Required Invariants

- evaluator status remains `blocked`
- `promotion_disabled` remains in first-failing gates
- promotion execution remains false
- live provider calls remain false
- live AI Decision Ledger appends remain false
- public report changes remain false
- household financial data storage remains false
- candidate public-report inclusion remains blocked
- public source registry mutation remains blocked

## Validation Standard

The completion standard for this evaluator slice is:

```bash
make validate
make assure
make phase1-acceptance
make phase2-acceptance
make test
make test-browser
```

The full unit suite currently includes 269 tests with 3 intentional future-promotion skips.

## Still Out Of Scope

- candidate promotion execution
- promoted analysis-unit creation
- public candidate reporting
- live AI provider use
- live AI Decision Ledger promotion append
- public source registry mutation
- human-review approval
- promotion prompt-template approval for live use
- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- state-level modeling
- household financial data transmission or storage
- final licensing/IP decisions
- motive, corruption, or loophole findings

## Remaining Work In This Slice

This evaluator slice is complete when:

- this checklist exists
- executable tests validate this checklist
- README and handoff link this checklist
- `make assure` includes `phase3_promotion_evaluator_status_contract`
- the backend evaluator endpoint validates against the status schema contract view
- the frontend evaluator panel has rendering regression coverage
- the checked status snapshot remains blocked and no-mutation
- no promotion, public candidate reporting, live provider path, source registry mutation, or household-data storage is enabled
