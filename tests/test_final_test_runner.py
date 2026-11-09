"""Kiểm thử TDD cho src/final_test_runner.py (S5-04, S5-05): đánh giá tập test MỘT lần duy nhất.

Toàn bộ test dùng dữ liệu giả; không đọc tập test thật.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import pytest
import yaml

from src.final_test_runner import (
    CONFIRM_STRING_SHA256,
    EXPECTED_SPLIT_SHA256,
    EXPECTED_SPLIT_SIZES,
    G5_TOLERANCE,
    REFERENCE_VAL_MACRO_F1,
    check_frozen_config,
    check_split_integrity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = REPO_ROOT / "results" / "rq3_ghep_svm_orig_to_orig_s42"


def _write_split_csv(path: Path, sizes: Dict[str, int]) -> str:
    """Tạo split_v1.csv giả với số dòng cho từng split và trả về SHA256."""
    rows = []
    for split, n in sizes.items():
        for i in range(n):
            rows.append({"image_id": f"{split}-{i}.png", "label": "COVID", "split": split})
    pd.DataFrame(rows).to_csv(path, index=False)
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- Task 1: G1, G2


def test_constants_match_spec() -> None:
    assert EXPECTED_SPLIT_SHA256 == "f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98"
    assert EXPECTED_SPLIT_SIZES == {"train": 14815, "val": 3174, "test": 3176}
    assert REFERENCE_VAL_MACRO_F1 == 0.9024
    assert G5_TOLERANCE == 0.002


def test_g1_accepts_valid(tmp_path: Path) -> None:
    sizes = {"train": 6, "val": 3, "test": 2}
    csv_path = tmp_path / "split_v1.csv"
    sha = _write_split_csv(csv_path, sizes)
    assert check_split_integrity(csv_path, expected_sha256=sha, expected_sizes=sizes) == sha


def test_g1_rejects_wrong_sha(tmp_path: Path) -> None:
    sizes = {"train": 6, "val": 3, "test": 2}
    csv_path = tmp_path / "split_v1.csv"
    _write_split_csv(csv_path, sizes)
    with pytest.raises(ValueError, match="SHA256"):
        check_split_integrity(csv_path, expected_sha256="0" * 64, expected_sizes=sizes)


def test_g1_rejects_wrong_sizes(tmp_path: Path) -> None:
    csv_path = tmp_path / "split_v1.csv"
    sha = _write_split_csv(csv_path, {"train": 6, "val": 3, "test": 1})
    with pytest.raises(ValueError, match="test"):
        check_split_integrity(
            csv_path,
            expected_sha256=sha,
            expected_sizes={"train": 6, "val": 3, "test": 2},
        )


def test_g1_real_split_file_matches_constants() -> None:
    """Chỉ đọc tệp manifest splits/split_v1.csv (không đọc ảnh)."""
    assert (
        check_split_integrity(REPO_ROOT / "splits" / "split_v1.csv") == EXPECTED_SPLIT_SHA256
    )


def _reference_config() -> Dict[str, Any]:
    return yaml.safe_load((REFERENCE_DIR / "config.yaml").read_text(encoding="utf-8"))


def test_g2_accepts_repo_reference_config() -> None:
    check_frozen_config(_reference_config())


@pytest.mark.parametrize(
    "path,value",
    [
        (("hyperparameters", "probability"), False),
        (("hyperparameters", "C"), 1.0),
        (("hyperparameters", "gamma"), "auto"),
        (("hyperparameters", "class_weight"), None),
        (("hyperparameters", "random_state"), 7),
        (("seed",), 7),
        (("preprocessing", "scaler"), "MinMaxScaler"),
        (("eval_mask_mode",), "lung_only"),
        (("train_mask_mode",), "outside_only"),
        (("evaluation", "allow_test"), True),
        (("features",), "hist"),
        (("classifier_tag",), "rf"),
        (("split", "sha256"), "0" * 64),
    ],
)
def test_g2_rejects_each_changed_field(path: Tuple[str, ...], value: Any) -> None:
    cfg = copy.deepcopy(_reference_config())
    node = cfg
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError):
        check_frozen_config(cfg)


def test_g2_rejects_missing_field() -> None:
    cfg = copy.deepcopy(_reference_config())
    del cfg["hyperparameters"]["probability"]
    with pytest.raises(ValueError):
        check_frozen_config(cfg)


# ---------------------------------------------------------------- Task 2: G3, G4, G6

from src.final_test_runner import (  # noqa: E402
    UNLOCK_RECORD_NAME,
    check_confirm_final,
    check_not_already_unlocked,
    write_unlock_record,
)

TEST_CONFIRM_TEXT = "CHUOI-XAC-NHAN-DUNG-CHO-KIEM-THU"
TEST_CONFIRM_SHA = hashlib.sha256(TEST_CONFIRM_TEXT.encode("utf-8")).hexdigest()


def test_g3_passes_on_empty_dir(tmp_path: Path) -> None:
    check_not_already_unlocked(tmp_path)


def test_g3_refuses_when_record_exists(tmp_path: Path) -> None:
    final_dir = tmp_path / "final_test"
    final_dir.mkdir()
    (final_dir / UNLOCK_RECORD_NAME).write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="G3"):
        check_not_already_unlocked(tmp_path)


def test_g3_dry_dir_does_not_block(tmp_path: Path) -> None:
    (tmp_path / "dry").mkdir()
    (tmp_path / "dry" / "dry_summary.json").write_text("{}", encoding="utf-8")
    check_not_already_unlocked(tmp_path)


def test_g4_missing_file(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


def test_g4_wrong_string(tmp_path: Path) -> None:
    (tmp_path / "CONFIRM_FINAL").write_text("SAI-CHUOI", encoding="utf-8")
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


def test_g4_empty_string(tmp_path: Path) -> None:
    (tmp_path / "CONFIRM_FINAL").write_text("", encoding="utf-8")
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


def test_g4_rejects_string_with_extra_text(tmp_path: Path) -> None:
    (tmp_path / "CONFIRM_FINAL").write_text(TEST_CONFIRM_TEXT + " them", encoding="utf-8")
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


@pytest.mark.parametrize("tail", ["", "\n", "\r\n"])
def test_g4_correct_string_accepts_trailing_newline(tmp_path: Path, tail: str) -> None:
    (tmp_path / "CONFIRM_FINAL").write_bytes((TEST_CONFIRM_TEXT + tail).encode("utf-8"))
    assert check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA) == TEST_CONFIRM_SHA


def test_g6_record_contains_fields_and_is_valid_json(tmp_path: Path) -> None:
    final_dir = tmp_path / "final_test"
    path = write_unlock_record(
        final_dir,
        commit="a" * 40,
        split_sha256=EXPECTED_SPLIT_SHA256,
        val_macro_f1=0.9024,
        confirm_sha256=TEST_CONFIRM_SHA,
    )
    assert path == final_dir / UNLOCK_RECORD_NAME
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["commit"] == "a" * 40
    assert rec["split_sha256"] == EXPECTED_SPLIT_SHA256
    assert rec["val_macro_f1"] == 0.9024
    assert rec["confirm_sha256"] == TEST_CONFIRM_SHA
    assert rec["utc_time"].endswith("Z")


def test_g6_refuses_to_overwrite_existing_record(tmp_path: Path) -> None:
    final_dir = tmp_path / "final_test"
    kwargs = dict(
        commit="a" * 40,
        split_sha256=EXPECTED_SPLIT_SHA256,
        val_macro_f1=0.9024,
        confirm_sha256=TEST_CONFIRM_SHA,
    )
    write_unlock_record(final_dir, **kwargs)
    with pytest.raises(RuntimeError, match="G3"):
        write_unlock_record(final_dir, **kwargs)
