from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "schemas"
DATA_DIR = REPO_ROOT / "data"
SOURCE_REGISTRY_PATH = DATA_DIR / "sources" / "registry.json"
DECISION_LEDGER_PATH = DATA_DIR / "ledger" / "ai_decision_ledger.jsonl"
TCJA_ANALYSIS_UNIT_PATH = DATA_DIR / "exemplars" / "tcja_2017_representative_provisions_analysis_unit.json"
SOURCE_SNAPSHOT_MANIFEST_PATH = DATA_DIR / "sources" / "snapshots.json"
