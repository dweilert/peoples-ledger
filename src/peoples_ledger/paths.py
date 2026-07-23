from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "schemas"
DATA_DIR = REPO_ROOT / "data"
BUILD_DIR = REPO_ROOT / "build"
REPORT_ARTIFACT_DIR = BUILD_DIR / "reports"
CANDIDATE_AUDIT_ARTIFACT_DIR = BUILD_DIR / "candidate-audit"
SOURCE_REGISTRY_PATH = DATA_DIR / "sources" / "registry.json"
DECISION_LEDGER_PATH = DATA_DIR / "ledger" / "ai_decision_ledger.jsonl"
TCJA_ANALYSIS_UNIT_PATH = DATA_DIR / "exemplars" / "tcja_2017_representative_provisions_analysis_unit.json"
SOURCE_SNAPSHOT_MANIFEST_PATH = DATA_DIR / "sources" / "snapshots.json"
PROMPT_TEMPLATE_REGISTRY_PATH = DATA_DIR / "ai" / "prompt_templates.json"
CANDIDATE_EXTRACTION_POLICY_PATH = DATA_DIR / "ai" / "candidate_extraction_policies.json"
SOURCE_ACQUISITION_MANIFEST_PATH = DATA_DIR / "fixtures" / "source_acquisition" / "ira_2022_source_manifest.json"
CANDIDATE_ANALYSIS_QUEUE_PATH = DATA_DIR / "fixtures" / "candidate_queue" / "ira_2022_candidate_analysis_units.json"
CANDIDATE_REVIEW_RECORDS_PATH = DATA_DIR / "fixtures" / "candidate_reviews" / "ira_2022_candidate_review_records.json"
