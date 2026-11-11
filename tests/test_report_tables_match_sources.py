"""Chặn chép nhầm giữa bảng trong ``report/`` và tệp số liệu nguồn.

Vụ bảng RQ3 từng bị chép tay lệch 23 ô so với CSV là lý do có bộ test này: mỗi
bảng then chốt của báo cáo được đọc trực tiếp từ tệp `.md` và đối chiếu với
tệp kết quả tương ứng. Bảng lệch một ô cũng làm test thất bại.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "report"


def read_table_rows(chapter_file: str, caption_pattern: str) -> list[str]:
    """Trả về các dòng dữ liệu của bảng (bắt đầu '|') sau dòng caption."""
    text = (REPORT / chapter_file).read_text(encoding="utf-8")
    m = re.search(caption_pattern, text)
    if m is None:
        pytest.fail(f"Khong tim thay caption {caption_pattern!r} trong {chapter_file}")
    lines = text[m.end():].splitlines()
    rows: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            rows.append(stripped)
            continue
        if rows:
            break
    if len(rows) < 3:
        pytest.fail(f"Bang {caption_pattern!r} trong {chapter_file} co qua it dong: {rows}")
    return rows[1:]  # bỏ dòng phân cách tiêu đề


def cells(row: str) -> list[str]:
    """Tách ô của một dòng bảng markdown."""
    return [c.strip() for c in row.strip().strip("|").split("|")]


# ---------- Bảng 3.1: macro-F1 bốn nhóm đặc trưng ----------
def test_table_3_1_feature_groups_match_summary_csv() -> None:
    """Bảng 3.1 phải khớp `results/report_rq1/r1_summary.csv` đến từng ô."""
    rows = {cells(r)[0]: r for r in read_table_rows("03_ket_qua_rq1_rq2.md", r"\*\*Bảng 3\.1:")}
    csv = pd.read_csv(REPO_ROOT / "results/report_rq1/r1_summary.csv")
    for features, label in [("ghep", "Ghép"), ("glcmlbp", "GLCM kết hợp LBP"), ("hist", "Histogram"), ("hog", "HOG")]:
        row = csv[csv["features"] == features].iloc[0]
        report_row = next((r for k, r in rows.items() if k.startswith(label)), None)
        assert report_row is not None, f"Thiếu hàng '{label}' trong Bảng 3.1"
        got = cells(report_row)
        assert got[1] == "152" if features == "ghep" else True
        expect_point = f"{row['macro_f1_mean']:.4f}".replace(".", ",")
        expect_sd = f"{row['macro_f1_std']:.4f}".replace(".", ",")
        assert got[2] == f"{expect_point} ± {expect_sd}", f"{label}: {got[2]}"
        expect_ci = f"[{row['ci95_low']:.4f}; {row['ci95_high']:.4f}]".replace(".", ",")
        assert got[3] == expect_ci, f"{label}: {got[3]}"
        expect_recall = f"{row['recall_Viral Pneumonia_mean']:.4f}".replace(".", ",")
        assert got[-1] == expect_recall, f"{label}: {got[-1]}"


# ---------- Bảng 4.1: năm kịch bản RQ3 ----------
def test_table_4_1_scenarios_match_summary_csv() -> None:
    """Bảng 4.1 phải khớp `results/report_rq3/r1_summary.csv` (macro-F1, CI)."""
    rows = read_table_rows("04_hoc_loi_tat_rq3.md", r"\*\*Bảng 4\.1:")
    csv = pd.read_csv(REPO_ROOT / "results/report_rq3/r1_summary.csv")
    labels = {
        "orig_to_orig": "Ảnh gốc cả hai tập",
        "lung_to_lung": "Chỉ phổi cả hai tập",
        "out_to_out": "Chỉ ngoài phổi cả hai tập",
    }
    for scenario, label in labels.items():
        row = csv[csv["scenario"] == scenario].iloc[0]
        report_row = next((r for r in rows if cells(r)[0] == label), None)
        assert report_row is not None, f"Thiếu hàng '{label}' trong Bảng 4.1"
        got = cells(report_row)
        assert got[1] == f"{row['macro_f1']:.4f}".replace(".", ","), f"{label}: {got[1]}"
        expect_ci = f"[{row['ci95_low']:.4f}; {row['ci95_high']:.4f}]".replace(".", ",")
        assert got[2] == expect_ci, f"{label}: {got[2]}"
    for label in ["Ảnh gốc cả hai tập", "Chỉ phổi cả hai tập", "Chỉ ngoài phổi cả hai tập"]:
        assert any(cells(r)[0] == label for r in rows), f"Bảng 4.1 thiếu hàng hợp lệ: {label}"


# ---------- Bảng 5.1: chỉ số trên tập test ----------
def test_table_5_1_overall_metrics_match_final_test_report() -> None:
    """Bảng 5.1 phải khớp `final_test_report.json` và `metrics.json`."""
    rows = {cells(r)[0]: cells(r)[1] for r in read_table_rows("05_ket_qua_test_va_trien_khai.md", r"\*\*Bảng 5\.1:")}
    report = pd.read_json(REPO_ROOT / "results/final_test/final_test_report.json", typ="series")
    metrics = pd.read_json(REPO_ROOT / "results/final_test/metrics.json", typ="series")

    def f4(value: float) -> str:
        return f"{value:.4f}".replace(".", ",")

    assert rows["Macro-F1"] == f4(float(report["macro_f1"]))
    expect_ci = f"[{f4(float(report['ci95_low']))}; {f4(float(report['ci95_high']))}]"
    ci_values = [v for k, v in rows.items() if k.startswith("Khoảng tin cậy")]
    assert ci_values and ci_values[0] == expect_ci, f"CI: {ci_values}"
    assert rows["Accuracy"] == f"{100 * float(report['accuracy']):.2f}%".replace(".", ",")
    assert rows["Balanced accuracy"] == f"{100 * float(metrics['balanced_accuracy']):.2f}%".replace(".", ",")
    assert rows["Weighted F1"] == f4(float(metrics["weighted_f1"]))
    assert rows["Macro precision"] == f4(float(metrics["macro_precision"]))


# ---------- Bảng 6.1: CI RF RQ2 và hàng test ----------
def test_table_6_1_reference_ci_matches_rq2_summary() -> None:
    """Hàng RQ2 của Bảng 6.1 phải khớp CSV RQ2 (cận trên CI 0,8716)."""
    rows = read_table_rows("06_thao_luan_gioi_han_huong_phat_trien.md", r"\*\*Bảng 6\.1:")
    csv = pd.read_csv(REPO_ROOT / "results/report_rq2/r1_summary.csv")
    rf = csv[csv["classifier"] == "rf"].iloc[0]
    expect = f"[{rf['ci95_low']:.4f}; {rf['ci95_high']:.4f}]".replace(".", ",")
    assert any(cells(r)[0].startswith("RQ2: Random Forest") and cells(r)[2] == expect for r in rows), \
        f"CI RQ2 RF phải là {expect}"
    report = pd.read_json(REPO_ROOT / "results/final_test/final_test_report.json", typ="series")
    test_row = next(r for r in rows if cells(r)[0].startswith("Tập test"))
    assert cells(test_row)[1] == f"{float(report['macro_f1']):.4f}".replace(".", ",")
