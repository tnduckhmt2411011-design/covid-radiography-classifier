"""Kiểm thử cho S4-07 (visual mask check), S5-01 (báo cáo RQ3 và notebook 08), S5-02 (permutation importance), và S5-03 (kết luận shortcut learning)."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.bootstrap import build_rq3_report, load_rq3_predictions

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_rq3_report_synthetic(tmp_path: Path) -> None:
    """Kiểm tra hàm build_rq3_report trên dữ liệu giả lập cho 5 kịch bản thực nghiệm của RQ3."""
    results_dir = tmp_path / "results"
    out_dir = tmp_path / "report_rq3"
    scenarios = ["orig_to_orig", "lung_to_lung", "out_to_out", "orig_to_lung", "orig_to_out"]
    n = 120
    seed = 42

    rng = np.random.default_rng(909)
    image_ids = [f"img_{i:04d}" for i in range(n)]
    y_true = rng.integers(0, 4, size=n).tolist()

    for sc in scenarios:
        run_dir = results_dir / f"rq3_ghep_svm_{sc}_s{seed}"
        run_dir.mkdir(parents=True, exist_ok=True)
        y_pred = rng.integers(0, 4, size=n).tolist()
        pd.DataFrame({
            "image_id": image_ids,
            "y_true": y_true,
            "y_pred": y_pred,
        }).to_csv(run_dir / "preds_val.csv", index=False)

    df_loaded = load_rq3_predictions(results_dir, "lung_to_lung", seed=seed, expected_n=n)
    assert len(df_loaded) == n
    assert set(df_loaded.columns) == {"image_id", "y_true", "y_pred"}

    report_files = build_rq3_report(
        results_dir=results_dir,
        out_dir=out_dir,
        scenarios=scenarios,
        seed=seed,
        reference="orig_to_orig",
        n_boot=40,
        rng_seed=42,
        expected_n=n,
        threshold_path=REPO_ROOT / "results" / "threshold_v3.md",
    )

    assert len(report_files) == 9
    for fname, p in report_files.items():
        assert p.is_file(), f"Tệp {fname} chưa được tạo"

    per_sc_df = pd.read_csv(report_files["r1_per_scenario.csv"])
    assert len(per_sc_df) == 5

    summary_df = pd.read_csv(report_files["r1_summary.csv"])
    assert len(summary_df) == 5
    assert set(summary_df["scenario"]) == set(scenarios)

    boot_df = pd.read_csv(report_files["r1_bootstrap_vs_reference.csv"])
    assert len(boot_df) == 4
    assert "orig_to_orig" not in boot_df["candidate"].tolist()

    shortcut_df = pd.read_csv(report_files["r3_shortcut_bootstrap.csv"])
    assert len(shortcut_df) >= 2
    pairs = list(zip(shortcut_df["scenario_a"], shortcut_df["scenario_b"]))
    assert ("lung_to_lung", "orig_to_orig") in pairs
    assert ("lung_to_lung", "out_to_out") in pairs


def test_rq3_comparison_protocol_record_exists_and_valid() -> None:
    """Kiểm tra biên bản đóng băng so sánh chính RQ3 trước khi mở điểm."""
    record_path = REPO_ROOT / "results" / "rq3_comparison_protocol_record.md"
    assert record_path.is_file(), "Thiếu biên bản results/rq3_comparison_protocol_record.md"

    content = record_path.read_text(encoding="utf-8")
    assert "orig_to_orig" in content
    assert "lung_to_lung" in content
    assert "out_to_out" in content
    assert "threshold_v3.md" in content
    assert "0,005" in content or "0.005" in content
    assert "9ce35960cac5ea48967ce2ef640c56515ed8933b" in content


def test_rq3_mask_check_files_exist_and_valid() -> None:
    """Kiểm tra kết quả kiểm tra căn chỉnh mặt nạ phổi S4-07."""
    check_dir = REPO_ROOT / "results" / "rq3_mask_check"
    assert check_dir.is_dir(), "Thiếu thư mục results/rq3_mask_check"

    summary_file = check_dir / "mask_alignment_summary.json"
    assert summary_file.is_file(), "Thiếu mask_alignment_summary.json"
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["total_visual_samples"] == 80
    assert summary["samples_per_class"] == 20
    assert summary["empty_masks_count"] == 0
    assert summary["all_centered"] is True

    samples_csv = check_dir / "mask_visual_check_samples.csv"
    assert samples_csv.is_file(), "Thiếu mask_visual_check_samples.csv"
    df = pd.read_csv(samples_csv)
    assert len(df) == 80
    assert set(df["label"].unique()) == {"COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"}

    for c_name in ("COVID", "Lung_Opacity", "Normal", "Viral_Pneumonia"):
        sheet_path = check_dir / f"mask_visual_check_{c_name}.png"
        assert sheet_path.is_file(), f"Thiếu {sheet_path.name}"


def test_rq3_official_report_files_exist_and_valid() -> None:
    """Kiểm tra đầy đủ 9 tệp báo cáo chuẩn của RQ3 trong results/report_rq3/."""
    report_dir = REPO_ROOT / "results" / "report_rq3"
    assert report_dir.is_dir(), "Thiếu thư mục results/report_rq3"

    expected_files = [
        "r1_per_scenario.csv",
        "r1_summary.csv",
        "r1_confusion_matrices.json",
        "r1_bootstrap_vs_reference.csv",
        "r3_shortcut_bootstrap.csv",
        "r2_normal_lung_opacity.csv",
        "r4_sampling_error.csv",
        "r5_gioi_han.md",
        "bootstrap_config.json",
    ]
    for ef in expected_files:
        assert (report_dir / ef).is_file(), f"Thiếu tệp {ef} trong report_rq3"

    summary_df = pd.read_csv(report_dir / "r1_summary.csv")
    assert len(summary_df) == 5
    sc_map = dict(zip(summary_df["scenario"], summary_df["macro_f1"]))
    assert abs(sc_map["orig_to_orig"] - 0.9024) < 0.001
    assert abs(sc_map["lung_to_lung"] - 0.8490) < 0.001
    assert abs(sc_map["out_to_out"] - 0.8921) < 0.001

    shortcut_df = pd.read_csv(report_dir / "r3_shortcut_bootstrap.csv")
    primary_row = shortcut_df[
        (shortcut_df["scenario_a"] == "lung_to_lung") & (shortcut_df["scenario_b"] == "orig_to_orig")
    ].iloc[0]
    assert float(primary_row["point_diff"]) < 0.0
    assert bool(primary_row["contains_zero"]) is False

    out_row = shortcut_df[
        (shortcut_df["scenario_a"] == "orig_to_orig") & (shortcut_df["scenario_b"] == "out_to_out")
    ].iloc[0]
    assert bool(out_row["contains_zero"]) is True


def test_rq3_permutation_importance_file_exists_and_valid() -> None:
    """Kiểm tra bảng permutation importance 10 khối trong results/rq3_permutation_importance.csv (S5-02)."""
    perm_csv = REPO_ROOT / "results" / "rq3_permutation_importance.csv"
    assert perm_csv.is_file(), "Thiếu results/rq3_permutation_importance.csv"
    df = pd.read_csv(perm_csv)
    assert len(df) == 30  # 10 khối x 3 modes
    assert set(df["mask_mode"].unique()) == {"original", "lung_only", "outside_only"}
    assert set(df["n_dims"].unique()) == {10, 12, 18, 28, 60, 64}


def test_rq3_shortcut_learning_conclusion_exists_and_valid() -> None:
    """Kiểm tra văn bản kết luận Shortcut Learning S5-03."""
    conc_path = REPO_ROOT / "results" / "rq3_shortcut_learning_conclusion.md"
    assert conc_path.is_file(), "Thiếu results/rq3_shortcut_learning_conclusion.md"
    content = conc_path.read_text(encoding="utf-8")
    assert "orig_to_orig" in content
    assert "lung_to_lung" in content
    assert "out_to_out" in content
    assert "0.8921" in content or "0,8921" in content
    assert "0.8490" in content or "0,8490" in content
    assert "S5-04" in content


_RQ3_SCENARIO_RE = re.compile(r"(orig_to_orig|orig_to_lung|orig_to_out|lung_to_lung|out_to_out)")


def _parse_vn_number(text: str) -> float:
    """Chuyển '0,9024', '95,72%', '**0,9024**' thành float."""
    cleaned = text.replace("*", "").replace("%", "").replace(",", ".").strip()
    return float(cleaned)


def _parse_rq3_conclusion_table(md_text: str) -> dict[str, dict[str, float]]:
    """Đọc bảng tổng hợp 5 kịch bản RQ3 trong tệp kết luận thành dict theo tên kịch bản."""
    parsed: dict[str, dict[str, float]] = {}
    for line in md_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) != 10:
            continue
        match = _RQ3_SCENARIO_RE.search(cells[0])
        if match is None:
            continue
        ci_numbers = re.findall(r"\d+[.,]\d+", cells[4])
        assert len(ci_numbers) == 2, f"Không đọc được CI ở dòng: {stripped}"
        ci_low, ci_high = ci_numbers
        parsed[match.group(1)] = {
            "macro_f1": _parse_vn_number(cells[3]),
            "ci95_low": _parse_vn_number(ci_low),
            "ci95_high": _parse_vn_number(ci_high),
            "accuracy": _parse_vn_number(cells[5]) / 100.0,
            "recall_COVID": _parse_vn_number(cells[6]) / 100.0,
            "recall_Lung_Opacity": _parse_vn_number(cells[7]) / 100.0,
            "recall_Normal": _parse_vn_number(cells[8]) / 100.0,
            "recall_Viral Pneumonia": _parse_vn_number(cells[9]) / 100.0,
        }
    return parsed


def test_rq3_shortcut_learning_conclusion_table_matches_csv() -> None:
    """Bảng trong tệp kết luận RQ3 phải khớp số liệu gốc, không được chép tay lệch.

    Bảng này từng bị lệch Accuracy/Recall ở cả 5 kịch bản dù Macro-F1 vẫn đúng, nên
    kiểm thử đối chiếu từng ô với report_rq3/r1_summary.csv và r4_sampling_error.csv.
    """
    conc_path = REPO_ROOT / "results" / "rq3_shortcut_learning_conclusion.md"
    table = _parse_rq3_conclusion_table(conc_path.read_text(encoding="utf-8"))

    summary = pd.read_csv(REPO_ROOT / "results" / "report_rq3" / "r1_summary.csv")
    sampling = pd.read_csv(REPO_ROOT / "results" / "report_rq3" / "r4_sampling_error.csv")
    summary = summary.set_index("scenario")
    sampling = sampling.set_index("scenario")

    expected_scenarios = {"orig_to_orig", "lung_to_lung", "out_to_out", "orig_to_lung", "orig_to_out"}
    assert set(table) == expected_scenarios, f"Bảng thiếu hoặc thừa kịch bản: {sorted(table)}"

    columns = (
        "macro_f1",
        "ci95_low",
        "ci95_high",
        "accuracy",
        "recall_COVID",
        "recall_Lung_Opacity",
        "recall_Normal",
        "recall_Viral Pneumonia",
    )
    for scenario in sorted(expected_scenarios):
        row = summary.loc[scenario]
        expected = {
            "macro_f1": float(row["macro_f1"]),
            "ci95_low": float(row["ci95_low"]),
            "ci95_high": float(row["ci95_high"]),
            "accuracy": float(sampling.loc[scenario]["p_accuracy"]),
            "recall_COVID": float(row["recall_COVID"]),
            "recall_Lung_Opacity": float(row["recall_Lung_Opacity"]),
            "recall_Normal": float(row["recall_Normal"]),
            "recall_Viral Pneumonia": float(row["recall_Viral Pneumonia"]),
        }
        for column in columns:
            assert math.isclose(table[scenario][column], expected[column], abs_tol=6e-5), (
                f"{scenario}.{column}: bảng ghi {table[scenario][column]:.6f}, "
                f"CSV gốc {expected[column]:.6f}"
            )


def test_rq3_shortcut_learning_conclusion_reports_glcm_on_outside_only() -> None:
    """Nhận định permutation importance ở outside_only phải nêu cả GLCM, không chỉ LBP và Histogram."""
    content = (REPO_ROOT / "results" / "rq3_shortcut_learning_conclusion.md").read_text(encoding="utf-8")
    perm = pd.read_csv(REPO_ROOT / "results" / "rq3_permutation_importance.csv")
    outside = perm[(perm["mask_mode"] == "outside_only") & (perm["block_name"].isin(["hist_64", "glcm_60", "lbp_28"]))]
    values = dict(zip(outside["block_name"], outside["importance_mean"]))
    assert set(values) == {"hist_64", "glcm_60", "lbp_28"}
    assert "0,3526" in content or "0.3526" in content, (
        "Thiếu giá trị GLCM 0,3526 trong nhận định outside_only"
    )


def test_notebook_08_rq3_masked_eval_structure_and_execution() -> None:
    """Kiểm tra cấu trúc và chạy thử toàn bộ code cells của notebooks/08_rq3_masked_eval.ipynb."""
    nb_path = REPO_ROOT / "notebooks" / "08_rq3_masked_eval.ipynb"
    assert nb_path.is_file(), "Thiếu notebooks/08_rq3_masked_eval.ipynb"

    nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = nb_data.get("cells", [])
    code_cells = [c for c in cells if c.get("cell_type") == "code" and "".join(c.get("source", [])).strip()]
    md_cells = [c for c in cells if c.get("cell_type") == "markdown" and "".join(c.get("source", [])).strip()]

    assert len(code_cells) >= 5, "Notebook 08 phải có ít nhất 5 code cells"
    assert len(md_cells) >= 5, "Notebook 08 phải có ít nhất 5 markdown cells"

    forbidden = ("import torch", "from torch", "import tensorflow", "import keras", "import timm")
    ns: dict = {"__name__": "__main__"}
    for idx, cell in enumerate(code_cells):
        src = "".join(cell.get("source", []))
        for bad in forbidden:
            assert bad not in src, f"Cell {idx} vi phạm cổng H7 ({bad})"
        exec(compile(src, f"{nb_path.name}#cell_{idx}", "exec"), ns)
