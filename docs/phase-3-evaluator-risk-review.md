# Phase 3 Evaluator Risk Review

This review documents risks for a future disabled-by-default promotion request evaluator. It is documentation and test scope only. It does not approve implementation, does not create evaluator code, and does not relax any blocker defined in the Phase 3 boundary or implementation-entry checklist.

## Risk Posture

The evaluator is a trust-boundary component because it will eventually summarize whether candidate records are eligible for promotion. Even while disabled, the design must prevent readers, tests, or future code from confusing a blocked evaluation with approval.

The current posture is `implementation_blocked`.

## Primary Risks And Mitigations

| Risk | Failure Mode | Required Mitigation |
| --- | --- | --- |
| Approval confusion | A blocked evaluator result is mistaken for promotion approval. | `status` remains `blocked`; `promotion_disabled` remains active; public reports stay candidate-free. |
| Gate-order drift | Later gates are reported before earlier failures. | Tests assert deterministic order from `schema` through `promotion_disabled`. |
| Privacy regression | Household financial data markers are inspected after review, ledger, report, or risk gates. | Privacy must fail before later gates and must keep all mutation flags false. |
| Fixture-to-production creep | Fixture-only records are treated as public registry or report inputs. | Source registry mutation, report updates, and ledger appends remain forbidden. |
| Live-provider leakage | Candidate or household payloads are sent to a live model. | Live provider paths remain absent unless explicitly approved in a later scope. |
| Human-review overclaim | Blocking review stubs are treated as approval. | Review records must require explicit approval and current stubs remain blockers. |
| Ledger integrity gap | A future evaluator records decisions outside the append-oriented ledger rules. | No live append is allowed in planning; future implementation must test ledger behavior before enabling writes. |
| Public report leakage | Candidate identifiers or candidate provisions appear in public JSON, HTML, exports, or bundles. | Public report leak checks fail `public_report`; candidate content remains excluded. |
| Risk understatement | High-risk or unresolved review triggers are hidden behind disabled status. | Evaluator outputs may list all blockers, but `first_failing_gate` remains deterministic. |
| Claim overreach | Output suggests motive, corruption, or loophole findings. | Messages and remediation hints must stay factual and must not make those claims. |

## Stop Conditions

Work must stop and remain documentation-only if any proposed change would:

- remove `promotion_disabled`
- mark a candidate as promotable
- create or store a promoted analysis unit
- append to the live AI Decision Ledger
- mutate the public source registry
- add candidates to public reports or exports
- call or configure a live AI provider
- store household financial data
- transmit household financial data
- approve human review
- approve promotion prompt templates for live use
- broaden bill ingestion, live monitoring, microsimulation, or state modeling

## Review Controls

Before any implementation PR is opened, the reviewer should verify:

- the implementation-entry checklist has explicit project-owner approval
- a failing or unskipped test exists before code changes
- the evaluator reads local fixtures only
- the evaluator returns blocked result shapes only
- no mutation flags can become true
- no public report artifact includes candidates
- no AI Decision Ledger append occurs outside approved ledger APIs
- household-data markers fail privacy before later gates
- skipped future tests are unskipped one gate at a time
- all broad-scope non-goals remain absent

## Residual Risk

Residual risk remains high until implementation exists and is reviewed because documentation cannot enforce runtime behavior by itself. The current mitigation is to keep implementation absent, keep future tests skipped, and require explicit project-owner approval before any evaluator code begins.

## Exit Criteria For This Review

This risk-review slice is complete when:

- this document exists
- executable tests validate the risk review
- README and handoff point to this review
- implementation-entry checklist tests still pass
- Phase 2 acceptance still passes
- no evaluator implementation exists
- no promotion, public candidate reporting, live provider path, source registry mutation, or household-data storage is enabled
