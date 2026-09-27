"""Paths and constants for Phase 1 EDA. No absolute paths are hard-coded except the
default project root, which can be overridden with AMLC_ROOT / AMLC_DATA_ROOT."""
import os
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("AMLC_ROOT", r"E:\Amazon ML Challenge"))
DATA_ROOT = Path(os.environ.get(
    "AMLC_DATA_ROOT", PROJECT_ROOT / "Dataset" / "student_resource" / "dataset"))
ARTIFACT_DIR = Path(os.environ.get("AMLC_ARTIFACTS", PROJECT_ROOT / "artifacts" / "p1"))
REPORT_DIR = Path(os.environ.get("AMLC_REPORTS", PROJECT_ROOT / "Docs" / "reports"))

# name -> (split dir, file name, source number or None for ground truth)
FILES = {
    "train_source1": ("train", "train_source1.tsv", 1),
    "train_source2": ("train", "train_source2.tsv", 2),
    "train_source3": ("train", "train_source3.tsv", 3),
    "train_ground_truth": ("train", "train_ground_truth.tsv", None),
    "test_source1": ("test", "test_source1.tsv", 1),
    "test_source2": ("test", "test_source2.tsv", 2),
    "test_source3": ("test", "test_source3.tsv", 3),
}
SOURCE_COLS = ["entity_id", "business_name", "business_address", "country"]
GT_COLS = ["source1_entity_id", "matched_entity_ids"]

# Row counts measured with `wc -l` in plan.md §2 (header excluded).
EXPECTED_ROWS = {
    "train_source1": 2_206_821, "train_source2": 5_034_616, "train_source3": 5_285_603,
    "train_ground_truth": 2_206_821, "test_source1": 1_732_544,
    "test_source2": 4_887_273, "test_source3": 5_082_316,
}

CHUNK_ROWS = 500_000
SEED = 20260925


def path_of(name: str, data_root: Path = None) -> Path:
    split, fname, _ = FILES[name]
    return Path(data_root or DATA_ROOT) / split / fname
