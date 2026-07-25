# Phase 3 Implementation Entry Checklist

This checklist defines the conditions that must be satisfied before any disabled-by-default promotion request evaluator implementation begins. It is documentation and test scope only. It does not approve implementation and does not change the current rule that promotion execution is blocked.

## Entry Decision

Implementation may not begin until all of these are true:

- project-owner approval explicitly names evaluator implementation
- a new feature branch is created from current `main`
- the Phase 3 boundary, evaluator contract, fixture examples, and skipped future tests are still present
- implementation starts by unskipping or adding one focused failing test
- the first implementation slice keeps `promotion_disabled` as a hard stop
- no candidate promotion execution is enabled
- no candidate is added to public reports
- no live AI provider path is enabled
- no public source registry mutation is enabled
- no household financial data is transmitted or stored

## Required Pre-Implementation Artifacts

These artifacts must exist before implementation work begins:

- `docs/phase-3-boundary.md`
- `docs/phase-3-promotion-evaluator-contract.md`
- `data/fixtures/phase3/promotion_evaluator_contract_examples.json`
- `tests/test_phase3_promotion_evaluator_contract.py`
- `tests/test_phase3_promotion_evaluator_fixtures.py`
- `tests/test_phase3_promotion_evaluator_future.py`

## First Implementation Slice Rules

The first approved implementation slice must be read-only and fixture-only.

It may:

- add `src/peoples_ledger/promotion_request_evaluator.py`
- load the Phase 3 contract examples
- return deterministic blocked result shapes
- evaluate only local fixtures
- keep mutation flags false
- keep live provider flags false
- keep public report change flags false
- keep ledger append flags false
- keep `promotion_disabled` active

It must not:

- promote a candidate
- create a promoted analysis unit
- append to the live AI Decision Ledger
- update public JSON, HTML, export, or downloadable report bundles
- update the public source registry
- approve human review
- approve a promotion prompt template for live use
- call a live AI provider
- transmit or store household financial data
- infer motive, corruption, or loophole findings

## Test-First Sequence

Implementation must advance in this order:

1. unskip or add the schema-first failing test
2. implement the smallest read-only code needed for that test
3. run the focused future evaluator test
4. run fixture, contract, boundary, and handoff tests
5. run `make validate`
6. run `make assure`
7. run `make phase1-acceptance`
8. run `make phase2-acceptance`
9. run `make test`
10. run `make test-browser` if frontend, backend, or privacy behavior changes
11. open a pull request
12. wait for checks
13. merge only after checks pass

No later gate test should be unskipped until earlier gate behavior is deterministic and merged.

## Privacy Entry Bar

Before implementation begins, the branch must preserve these privacy rules:

- household-specific amounts, filing facts, tax facts, and financial profile values remain absent from fixtures
- synthetic markers may be boolean or descriptive only
- privacy failures return before human review, ledger, public report, risk, or disabled gates
- no evaluator output may contain a household value
- no evaluator path may store browser-local or API-submitted household values
- no evaluator path may transmit candidate or household payloads to a live provider

## Exit Criteria For Planning

This checklist slice is complete when:

- this document exists
- executable tests validate this checklist
- README and handoff point to this checklist
- Phase 3 contract and fixture tests still pass
- Phase 2 acceptance still passes
- no evaluator implementation exists beyond approved read-only fixture slices
- no candidate promotion, public report inclusion, live provider path, source registry mutation, or household-data storage is enabled
