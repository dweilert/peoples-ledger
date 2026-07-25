# Phase 3 Boundary

Phase 3 starts only after Phase 2 closure and explicit project-owner approval. This boundary defines a planning-only first unit for a disabled-by-default candidate promotion request evaluator. It does not authorize candidate promotion, public candidate reporting, live AI providers, broad ingestion, microsimulation, live monitoring, state modeling, household financial data handling, or final licensing/IP decisions.

## Phase 3 Goal

Define the smallest future path from blocked Phase 2 promotion artifacts toward a promotion evaluator that can explain which gate would fail first, without executing promotion or changing any public output.

The first Phase 3 unit is planning only:

- document the disabled-by-default promotion request evaluator contract
- identify required schemas, fixtures, and tests
- preserve all Phase 2 blockers until explicitly implemented
- keep candidate records draft-only
- keep public reports candidate-free

## Recommended First Unit

Create a disabled-by-default promotion request evaluator plan.

The plan should define a future evaluator that:

- reads candidate promotion request fixtures
- reads candidate promotion gate reports
- reads source promotion manifests
- reads candidate review records
- reads promotion decision ledger stubs
- returns the first failing gate in deterministic order
- returns all blockers for audit use
- never mutates candidates
- never appends to the live AI Decision Ledger
- never adds candidate content to public reports
- never calls a live AI provider
- never transmits or stores household financial data

## Gate Order

The future evaluator should use this deterministic order:

1. schema
2. source
3. extraction_prompt
4. privacy
5. human_review
6. ledger
7. public_report
8. risk
9. promotion_disabled

Until Phase 3 implementation is explicitly approved, `promotion_disabled` remains the final hard stop even if earlier gates are represented as passing in a future fixture.

## In Scope

### Planning Documentation

- Add or update planning docs.
- Name the evaluator inputs, outputs, and gate order.
- Define expected future tests.
- Preserve all Phase 2 blocked boundaries.

### Executable Documentation Tests

- Assert the Phase 3 boundary exists.
- Assert it names the disabled-by-default evaluator.
- Assert the deterministic gate order is documented.
- Assert the out-of-scope list blocks promotion, public reporting, live providers, broader modeling, household financial data handling, and final licensing/IP decisions.

### Optional Future Schema Drafts

Schema drafts may be planned but not enabled. Any future schema must stay fixture-only until a later approved implementation slice.

## Out Of Scope

Phase 3 planning must not include:

- candidate promotion execution
- public report inclusion for candidates
- promotion-specific prompt-template approval for live use
- live AI provider use
- real human-review approval
- public source registry mutation
- broad bill ingestion
- live congressional monitoring
- full tax microsimulation
- state-level modeling
- household financial data transmission or storage
- production authentication or user accounts
- final licensing/IP decisions
- claims of motive, corruption, or reviewed loophole findings

## Required Future Tests

Before any evaluator implementation, add tests that prove:

- the evaluator is disabled by default
- gate order is deterministic
- missing or invalid candidate promotion requests fail schema first
- source mismatches fail source before prompt or review gates
- unapproved promotion prompt templates fail extraction_prompt
- household financial data markers fail privacy
- blocking review records fail human_review
- missing promotion decision ledger entries fail ledger
- public report candidate leakage must fail public_report
- unresolved risk triggers fail risk
- promotion_disabled remains a hard stop until explicitly removed by a future approved scope

## Exit Criteria For Phase 3 Planning Slice

The planning slice is complete when:

- this boundary document exists
- executable tests cover the boundary document
- Phase 2 acceptance still passes
- no promotion implementation exists
- no public candidate reporting exists
- no live provider path is enabled
- household financial data remains blocked
