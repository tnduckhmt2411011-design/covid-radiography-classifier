"""Kiểm thử cho S4-06: Phân tích chi tiết các ca dự đoán sai trên notebooks/09_error_analysis.ipynb."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_error_analysis_files_exist_and_valid() -> None:
    """Kiểm tra các tệp kết quả phân tích lỗi trong results/error_analysis/ (S4-06)."""
    err_dir = REPO_ROOT / "results" / "error_analysis"
    expected_files = [
        "val_misclassified_cases.csv",
        "confusion_pairs_summary.csv",
        "typical_clinical_confusions.csv",
        "error_analysis_summary.md",
    ]
    for fname in expected_files:
        fpath = err_dir / fname
        assert fpath.is_file(), f"Thiếu tệp phân tích lỗi S4-06: {fpath}"

    mis_df = pd.read_csv(err_dir / "val_misclassified_cases.csv")
    # Mô hình đóng băng rq2_ghep_svm_s42 đạt accuracy 2825/3174 => đúng 349 ca dự đoán sai trên val
    assert len(mis_df) == 349
    assert (mis_df["y_true"] != mis_df["y_pred"]).all()
    assert (mis_df["true_label"] != mis_df["pred_label"]).all()
    req_cols = {
        "image_id",
        "y_true",
        "y_pred",
        "true_label",
        "pred_label",
        "proba_true",
        "proba_pred",
        "margin",
        "error_type",
        "mean_brightness",
        "color_mode",
        "group_id",
        "wrong_in_gb",
        "wrong_in_rf",
        "consensus_hard_error",
    }
    assert req_cols.issubset(mis_df.columns)

    pairs_df = pd.read_csv(err_dir / "confusion_pairs_summary.csv")
    assert len(pairs_df) == 12  # 4 x 3 cặp nhầm lẫn ngoài đường chéo chính
    assert int(pairs_df["count"].sum()) == 349

    # Kiểm tra cặp nhầm lẫn lớn nhất: Normal <-> Lung_Opacity (144 + 124 = 268 ca)
    lo_norm = pairs_df[
        ((pairs_df["true_label"] == "Lung_Opacity") & (pairs_df["pred_label"] == "Normal"))
        | ((pairs_df["true_label"] == "Normal") & (pairs_df["pred_label"] == "Lung_Opacity"))
    ]
    assert int(lo_norm["count"].sum()) == 268

    typ_df = pd.read_csv(err_dir / "typical_clinical_confusions.csv")
    assert len(typ_df) >= 20
    # Đảm bảo có đầy đủ các nhóm nhầm lẫn giữa COVID, Lung_Opacity và Viral Pneumonia
    clinical_groups = set(typ_df["clinical_group"].unique())
    assert "COVID <-> Lung_Opacity" in clinical_groups
    assert "COVID <-> Viral Pneumonia" in clinical_groups
    assert "Lung_Opacity <-> Viral Pneumonia" in clinical_groups
    assert "Lung_Opacity <-> Normal" in clinical_groups

    summary_md = (err_dir / "error_analysis_summary.md").read_text(encoding="utf-8")
    assert "rq2_ghep_svm_s42" in summary_md
    assert "COVID" in summary_md and "Lung_Opacity" in summary_md and "Viral Pneumonia" in summary_md


def test_notebook_09_error_analysis_structure_and_execution() -> None:
    """Kiểm tra cấu trúc và chạy thử toàn bộ code cells của notebooks/09_error_analysis.ipynb."""
    nb_path = REPO_ROOT / "notebooks" / "09_error_analysis.ipynb"
    assert nb_path.is_file()

    nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = nb_data.get("cells", [])
    code_cells = [c for c in cells if c.get("cell_type") == "code" and "".join(c.get("source", [])).strip()]
    md_cells = [c for c in cells if c.get("cell_type") == "markdown" and "".join(c.get("source", [])).strip()]

    assert len(code_cells) >= 4, "Notebook 09 phải có ít nhất 4 cell mã nguồn hoàn chỉnh"
    assert len(md_cells) >= 4, "Notebook 09 phải có ít nhất 4 cell thuyết minh Markdown"

    forbidden = ("import torch", "from torch", "import tensorflow", "import keras", "import timm")
    ns: dict = {"__name__": "__main__"}
    for idx, cell in enumerate(code_cells):
        src = "".join(cell.get("source", []))
        for bad in forbidden:
            assert bad not in src, f"Cell {idx} vi phạm cổng H7 ({bad})"
        exec(compile(src, f"{nb_path.name}#cell_{idx}", "exec"), ns)
