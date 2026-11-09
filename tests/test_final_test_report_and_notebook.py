"""Kiểm thử cho S5-04 (đánh giá test một lần) và S5-05 (báo cáo test, ma trận nhầm lẫn và notebook 10)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.final_test_runner import (
    CONFIRM_STRING_SHA256,
    EXPECTED_SPLIT_SHA256,
    EXPECTED_SPLIT_SIZES,
    G5_TOLERANCE,
    REFERENCE_VAL_MACRO_F1,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FINAL_RESULTS_DIR = REPO_ROOT / "results" / "final_test"
NOTEBOOK_10_PATH = REPO_ROOT / "notebooks" / "10_final_test_eval.ipynb"
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap.md"


def test_final_test_results_directory_structure() -> None:
    assert FINAL_RESULTS_DIR.is_dir(), f"Thư mục {FINAL_RESULTS_DIR} không tồn tại"
    required_files = [
        "UNLOCK_RECORD.json",
        "final_test_report.json",
        "metrics.json",
        "preds_test.csv",
        "config.yaml",
        "r5_gioi_han.md",
        "log",
        "confusion_matrix_test.png",
    ]
    for fname in required_files:
        p = FINAL_RESULTS_DIR / fname
        assert p.is_file(), f"Thiếu tệp bắt buộc: {p}"


def test_unlock_record_contents() -> None:
    rec_path = FINAL_RESULTS_DIR / "UNLOCK_RECORD.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    assert rec["split_sha256"] == EXPECTED_SPLIT_SHA256
    assert rec["confirm_sha256"] == CONFIRM_STRING_SHA256
    assert abs(rec["val_macro_f1"] - REFERENCE_VAL_MACRO_F1) <= G5_TOLERANCE
    assert len(rec["commit"]) == 40
    assert rec["utc_time"].endswith("Z")


def test_preds_test_validity() -> None:
    preds_path = FINAL_RESULTS_DIR / "preds_test.csv"
    df = pd.read_csv(preds_path)
    assert len(df) == EXPECTED_SPLIT_SIZES["test"]
    assert not df["image_id"].duplicated().any()
    expected_cols = [
        "image_id",
        "y_true",
        "y_pred",
        "prob_COVID",
        "prob_Lung_Opacity",
        "prob_Normal",
        "prob_Viral Pneumonia",
    ]
    assert list(df.columns) == expected_cols
    assert set(df["y_true"].unique()).issubset({0, 1, 2, 3})
    assert set(df["y_pred"].unique()).issubset({0, 1, 2, 3})

    proba_matrix = df[expected_cols[3:]].to_numpy()
    np.testing.assert_allclose(proba_matrix.sum(axis=1), 1.0, atol=1e-5)


def test_final_test_report_metrics_and_ci() -> None:
    rep_path = FINAL_RESULTS_DIR / "final_test_report.json"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))

    assert rep["ci95_low"] <= rep["macro_f1"] <= rep["ci95_high"]
    assert rep["r4_sampling_error"]["n_all"] == EXPECTED_SPLIT_SIZES["test"]
    assert rep["r4_sampling_error"]["n_boot"] == 2000
    assert "gia thuyet chua kiem chung" in rep["interpretation_note"]
    assert "cause" not in rep and "explanation" not in rep

    r2 = rep["r2_normal_lung_opacity"]
    assert set(r2.keys()) == {"LO_to_LO", "LO_to_Normal", "Normal_to_LO", "Normal_to_Normal"}


def test_notebook_10_structure_and_execution() -> None:
    assert NOTEBOOK_10_PATH.is_file(), f"Thiếu notebook {NOTEBOOK_10_PATH}"
    nb = json.loads(NOTEBOOK_10_PATH.read_text(encoding="utf-8"))

    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) >= 5, "Notebook 10 phải có ít nhất 5 code cells"

    # Đảm bảo toàn bộ các code cell đều có kết quả chạy (outputs không rỗng)
    for idx, cell in enumerate(code_cells):
        assert cell["outputs"], f"Cell code số {idx+1} chưa được thực thi (outputs rỗng)"

    # Không chứa import framework deep learning
    text = NOTEBOOK_10_PATH.read_text(encoding="utf-8")
    for lib in ("torch", "tensorflow", "keras", "timm"):
        assert f"import {lib}" not in text
        assert f"from {lib}" not in text


def test_roadmap_updated_s504_s505() -> None:
    content = ROADMAP_PATH.read_text(encoding="utf-8")
    assert "24/33" in content
    assert "72.7%" in content
    assert "| S5-04 | T10 |" in content and "| Xong |" in content
    assert "| S5-05 | T10 |" in content and "| Xong |" in content
