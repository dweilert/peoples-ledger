# Phase 0 Acceptance Checklist

This checklist maps Phase 0 to the Foundational Product and System Design v0.3 Appendix H. Phase 0 remains a bounded manual exemplar and does not start broad ingestion, live monitoring, full tax microsimulation, state modeling, or final licensing/IP decisions.

Testing is integrated into the acceptance approach. The testing layers and future gates are defined in `docs/testing-strategy.md`.

## Evidence

Status: implemented for the manual exemplar.

- Ten representative TCJA provisions are recorded.
- Each provision has source spans and source-record references.
- Each claim has at least one evidence record.
- Source registry records are paired with a snapshot manifest containing retrieval date, URL, hash, locator policy, and storage mode.

## Decision Provenance

Status: implemented for POC records.

- The AI Decision Ledger is JSONL and append-oriented.
- Entries include model scenario, retention, disclosure, redaction, deletion authorization, supersession, validation, risk, publication lane, and publication state fields.
- Entries are hash-chained with `previous_entry_hash` and `entry_hash`.
- Tests detect mutated ledger content.

## Calculations

Status: stubbed by design.

- No authoritative arithmetic is performed by an LLM.
- No tax liability or distributional magnitude is calculated in Phase 0.
- Model scenarios are qualitative and explicitly marked as not using household financial data.

## Automation

Status: scaffolded.

- Deterministic test doubles exist for provider-neutral AI integration.
- Automated ingestion, challenge agents, and sampling workflow are deferred to Phase 1.

## Quality Measurement

Status: scaffolded.

- Tests cover schemas, fixture regression, privacy rejection, ledger integrity, backend integration, source snapshots, and frontend egress constraints.
- False-negative, escalation, disagreement, and sample-error reporting are deferred until automated pipelines exist.

## Perspective Integrity

Status: implemented for the manual exemplar.

- Three perspective profiles are present.
- Each profile references governed model scenarios.
- Invariance checks require profiles not to alter common evidence, statutory transformations, model-scenario parameters, or counterevidence.

## Corrections

Status: scaffolded.

- Ledger entries include supersession fields.
- Correction workflow, root-cause records, and correction-derived regression tests are deferred until there is a real corrected finding.

## Public Clarity

Status: implemented for POC.

- Schemas distinguish source records, provisions, transformations, claims, indicators, model scenarios, perspective profiles, and ledger entries.
- Publication states and lanes are represented in data.
- The static frontend displays the analysis unit, source registry, and AI Decision Ledger.

## Household Privacy

Status: implemented for Phase 0.

- Backend privacy guards reject household financial keys before AI calls or ledger writes.
- The frontend local privacy panel collects only non-financial illustrative characteristics.
- Local controls have no form names, no storage path, and no backend submission path.
- Tests verify frontend network calls are allowlisted and household financial field names are absent.

## Statutory Transformation

Status: implemented as manual deterministic snapshots.

- Each provision has a statutory-transformation record.
- Each transformation records source span, affected authority, before/after hashes, deterministic status, round-trip status, and reconciliation status.
- A real deterministic amendment engine is deferred to Phase 1.

## Scenario Governance

Status: implemented for POC.

- Technical outputs identify `canonical_base_v1`.
- Perspective profiles may reference the scenario but cannot modify its parameters.
- Tests enforce profile invariance.
