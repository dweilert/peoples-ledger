# The People's Ledger

Initial proof of concept for Milestones 1 and 2.

This repository establishes executable foundations for:

- enforceable schemas for core policy-analysis records
- an initial source registry
- an append-oriented AI Decision Ledger
- a provider-neutral AI adapter with deterministic test doubles
- one manually curated TCJA analysis unit with expected outputs
- a small local backend and static frontend
- unit, schema, regression, and integration tests

The POC is aligned to the Foundational Product and System Design v0.3 acceptance criteria for the bounded manual exemplar: a representative 8-12 provision TCJA subset, source spans, deterministic statutory-transformation records, governed model scenarios, three perspective profiles, perspective invariance checks, and complete AI Decision Ledger provenance fields.

Licensing and intellectual-property decisions are intentionally deferred.

## Quick Start

```bash
make test
make validate
make run
```

Then open `frontend/index.html` or call the local API at `http://127.0.0.1:8787`.

## Scope Boundaries

This POC does not implement broad bill ingestion, full tax microsimulation, live congressional monitoring, or state-level modeling.

The code enforces the Milestone 1 and 2 privacy constraint: household financial data must not be transmitted or stored. Model scenarios use public aggregate assumptions only.
