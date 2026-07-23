# Milestones 1 and 2 POC

## Delivered Structure

- `schemas/`: enforceable JSON contracts for source records, legislative documents, provisions, analysis units, claims and evidence, narrow-benefit indicators, model scenarios, perspective profiles, and AI Decision Ledger entries.
- `src/peoples_ledger/`: backend/domain code, source registry, decision ledger, privacy guard, AI adapter, CLI, and local HTTP API.
- `frontend/`: static browser UI for inspecting the bundled TCJA analysis unit through the local API.
- `data/sources/registry.json`: initial public-source registry.
- `data/sources/snapshots.json`: source snapshot manifest.
- `data/exemplars/tcja_2017_representative_provisions_analysis_unit.json`: manually curated TCJA analysis unit.
- `tests/`: unit, schema, regression, and integration tests.
- `docs/testing-strategy.md`: integrated testing approach and future merge gates.

## Version 0.3 Alignment

The manual exemplar uses a ten-provision representative TCJA subset and includes v0.3 acceptance scaffolding for deterministic statutory transformation records, source spans, publication states, governed model scenarios, three perspective profiles, perspective invariance checks, and complete AI Decision Ledger retention, disclosure, redaction, and supersession fields.

Testing is treated as part of the implementation contract. Each future feature, schema change, data fixture, model scenario, AI workflow, privacy boundary, or publication path should land with tests that state the trust claim being proven.

## Explicit Non-Goals

The POC intentionally does not begin broad bill ingestion, full tax microsimulation, live congressional monitoring, or state-level modeling.

## Privacy Guardrail

The POC rejects payloads containing household financial data keys before AI adapter calls or decision-ledger writes. Bundled model scenarios are qualitative or aggregate and carry `uses_household_financial_data: false`.

## License

Licensing and intellectual-property decisions are deferred. The package metadata records this as `License decision deferred`.
