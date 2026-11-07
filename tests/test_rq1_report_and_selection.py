"""Kiểm thử cho S3-05 (báo cáo RQ1 và notebook 05) và S3-06 (biên bản chốt nhóm đặc trưng RQ1)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_rq1_official_report_files_exist_and_valid() -> None:
    """Kiểm tra đủ 8 tệp báo cáo R1-R5 trong results/report_rq1/ và tính đúng đắn số liệu."""
    report_dir = REPO_ROOT / "results" / "report_rq1"
    expected_files = [
        "r1_per_seed.csv",
        "r1_summary.csv",
        "r1_confusion_matrices.json",
        "r1_bootstrap_vs_reference.csv",
        "r2_normal_lung_opacity.csv",
        "r4_sampling_error.csv",
        "r5_gioi_han.md",
        "bootstrap_config.json",
    ]
    for fname in expected_files:
        fpath = report_dir / fname
        assert fpath.is_file(), f"Thiếu tệp báo cáo chính thức: {fpath}"

    summary_df = pd.read_csv(report_dir / "r1_summary.csv")
    assert list(summary_df["features"]) == ["hist", "glcmlbp", "hog", "ghep"]
    assert (summary_df["n_seeds"] == 3).all()
    assert (summary_df["macro_f1_mean"] > 0.2397).all()  # Vượt cổng H4 (A0 = 0.2397)

    best_row = summary_df.sort_values("macro_f1_mean", ascending=False).iloc[0]
    assert best_row["features"] == "ghep"

    boot_df = pd.read_csv(report_dir / "r1_bootstrap_vs_reference.csv")
    ghep_vs_hist = boot_df[boot_df["candidate"] == "ghep"].iloc[0]
    assert ghep_vs_hist["reference"] == "hist"
    assert float(ghep_vs_hist["point_diff"]) >= 0.005
    assert float(ghep_vs_hist["ci_low"]) > 0.0
    assert bool(ghep_vs_hist["contains_zero"]) is False


def test_rq1_feature_selection_record_exists_and_valid() -> None:
    """Kiểm tra biên bản chốt nhóm đặc trưng tốt nhất của RQ1 cho RQ2 (S3-06)."""
    record_path = REPO_ROOT / "results" / "rq1_feature_selection_record.md"
    assert record_path.is_file(), "Thiếu biên bản chốt nhóm đặc trưng results/rq1_feature_selection_record.md"

    content = record_path.read_text(encoding="utf-8")
    assert "ghep" in content
    assert "0,005" in content or "0.005" in content
    assert "rq1_cost_rank_record.md" in content
    assert "threshold_v3.md" in content


def test_notebook_05_rq1_features_structure_and_execution() -> None:
    """Kiểm tra cấu trúc và chạy thử toàn bộ code cells của notebooks/05_rq1_features.ipynb."""
    nb_path = REPO_ROOT / "notebooks" / "05_rq1_features.ipynb"
    assert nb_path.is_file()

    nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = nb_data.get("cells", [])
    code_cells = [c for c in cells if c.get("cell_type") == "code" and "".join(c.get("source", [])).strip()]
    md_cells = [c for c in cells if c.get("cell_type") == "markdown" and "".join(c.get("source", [])).strip()]

    assert len(code_cells) >= 4, "Notebook 05 phải có ít nhất 4 cell mã nguồn hoàn chỉnh"
    assert len(md_cells) >= 4, "Notebook 05 phải có ít nhất 4 cell thuyết minh Markdown"

    forbidden = ("import torch", "from torch", "import tensorflow", "import keras", "import timm")
    ns: dict = {"__name__": "__main__"}
    for idx, cell in enumerate(code_cells):
        src = "".join(cell.get("source", []))
        for bad in forbidden:
            assert bad not in src, f"Cell {idx} vi phạm cổng H7 ({bad})"
        exec(compile(src, f"{nb_path.name}#cell_{idx}", "exec"), ns)
