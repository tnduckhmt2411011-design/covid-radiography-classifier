"""Kiểm thử cho S4-03 (báo cáo RQ2 và notebook 06) và S4-04 (biên bản chốt bộ phân loại RQ2)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.bootstrap import build_rq2_report, load_rq2_predictions

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_rq2_report_synthetic(tmp_path: Path) -> None:
    """Kiểm tra hàm build_rq2_report trên dữ liệu giả lập (3 mô hình tất định 1 seed + 3 mô hình ngẫu nhiên 3 seed)."""
    results_dir = tmp_path / "results"
    out_dir = tmp_path / "report_rq2"
    classifiers = ["lr", "knn", "dt", "rf", "svm", "gb"]
    det_clfs = {"lr", "knn", "svm"}
    seeds = [42, 43, 44]
    n = 120

    rng = np.random.default_rng(808)
    image_ids = [f"img_{i:04d}" for i in range(n)]
    y_true = rng.integers(0, 4, size=n).tolist()

    for clf in classifiers:
        clf_seeds = [42] if clf in det_clfs else seeds
        for s in clf_seeds:
            run_dir = results_dir / f"rq2_ghep_{clf}_s{s}"
            run_dir.mkdir(parents=True, exist_ok=True)
            y_pred = rng.integers(0, 4, size=n).tolist()
            pd.DataFrame({
                "image_id": image_ids,
                "y_true": y_true,
                "y_pred": y_pred,
            }).to_csv(run_dir / "preds_val.csv", index=False)

    df_loaded = load_rq2_predictions(results_dir, "ghep", "svm", 42, expected_n=n)
    assert len(df_loaded) == n

    report_files = build_rq2_report(
        results_dir=results_dir,
        out_dir=out_dir,
        features="ghep",
        classifiers=classifiers,
        seeds=seeds,
        deterministic_classifiers=list(det_clfs),
        reference="rf",
        n_boot=40,
        rng_seed=42,
        expected_n=n,
        threshold_path=REPO_ROOT / "results" / "threshold_v3.md",
    )

    assert len(report_files) == 8
    per_seed_df = pd.read_csv(report_files["r1_per_seed.csv"])
    assert len(per_seed_df) == 12

    summary_df = pd.read_csv(report_files["r1_summary.csv"])
    assert len(summary_df) == 6
    for _, row in summary_df.iterrows():
        if row["classifier"] in det_clfs:
            assert int(row["n_seeds"]) == 1
            assert bool(row["is_deterministic"]) is True
            assert float(row["macro_f1_std"]) == 0.0
        else:
            assert int(row["n_seeds"]) == 3
            assert bool(row["is_deterministic"]) is False

    boot_df = pd.read_csv(report_files["r1_bootstrap_vs_reference.csv"])
    assert len(boot_df) == 5
    assert "rf" not in boot_df["candidate"].tolist()


def test_rq2_official_report_files_exist_and_valid() -> None:
    """Kiểm tra đủ 8 tệp báo cáo R1-R5 trong results/report_rq2/ và tính đúng đắn số liệu."""
    report_dir = REPO_ROOT / "results" / "report_rq2"
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
        assert fpath.is_file(), f"Thiếu tệp báo cáo chính thức RQ2: {fpath}"

    per_seed_df = pd.read_csv(report_dir / "r1_per_seed.csv")
    assert len(per_seed_df) == 12

    summary_df = pd.read_csv(report_dir / "r1_summary.csv")
    assert list(summary_df["classifier"]) == ["lr", "knn", "dt", "rf", "svm", "gb"]
    assert (summary_df["macro_f1_mean"] > 0.2397).all()  # Vượt cổng H4 (A0 = 0.2397)

    best_row = summary_df.sort_values("macro_f1_mean", ascending=False).iloc[0]
    assert best_row["classifier"] == "svm"
    assert abs(float(best_row["macro_f1_mean"]) - 0.902445) < 1e-5

    boot_df = pd.read_csv(report_dir / "r1_bootstrap_vs_reference.csv")
    svm_vs_rf = boot_df[boot_df["candidate"] == "svm"].iloc[0]
    assert svm_vs_rf["reference"] == "rf"
    assert float(svm_vs_rf["point_diff"]) >= 0.005
    assert float(svm_vs_rf["ci_low"]) > 0.0
    assert bool(svm_vs_rf["contains_zero"]) is False


def test_rq2_classifier_selection_record_exists_and_valid() -> None:
    """Kiểm tra biên bản chốt cấu hình mô hình tối ưu nhất và đóng băng tham số thực nghiệm (S4-04)."""
    record_path = REPO_ROOT / "results" / "rq2_classifier_selection_record.md"
    assert record_path.is_file(), "Thiếu biên bản chốt mô hình results/rq2_classifier_selection_record.md"

    content = record_path.read_text(encoding="utf-8")
    assert "svm" in content
    assert "ghep" in content
    assert "StandardScaler" in content
    assert "0,005" in content or "0.005" in content
    assert "rq2_cost_rank_record.md" in content
    assert "threshold_v3.md" in content


def test_notebook_06_rq2_classifiers_structure_and_execution() -> None:
    """Kiểm tra cấu trúc và chạy thử toàn bộ code cells của notebooks/06_rq2_classifiers.ipynb."""
    nb_path = REPO_ROOT / "notebooks" / "06_rq2_classifiers.ipynb"
    assert nb_path.is_file()

    nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = nb_data.get("cells", [])
    code_cells = [c for c in cells if c.get("cell_type") == "code" and "".join(c.get("source", [])).strip()]
    md_cells = [c for c in cells if c.get("cell_type") == "markdown" and "".join(c.get("source", [])).strip()]

    assert len(code_cells) >= 4, "Notebook 06 phải có ít nhất 4 cell mã nguồn hoàn chỉnh"
    assert len(md_cells) >= 4, "Notebook 06 phải có ít nhất 4 cell thuyết minh Markdown"

    forbidden = ("import torch", "from torch", "import tensorflow", "import keras", "import timm")
    ns: dict = {"__name__": "__main__"}
    for idx, cell in enumerate(code_cells):
        src = "".join(cell.get("source", []))
        for bad in forbidden:
            assert bad not in src, f"Cell {idx} vi phạm cổng H7 ({bad})"
        exec(compile(src, f"{nb_path.name}#cell_{idx}", "exec"), ns)
