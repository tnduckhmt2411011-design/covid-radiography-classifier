"""Bộ kiểm thử tự động cho Hình 4.1 (macro-F1 năm kịch bản RQ3)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from scripts.report_figures_rq3 import (
    SCENARIO_LABELS,
    SCENARIO_ORDER,
    build,
    load_baselines,
    load_scenarios,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = REPO_ROOT / "results" / "report_rq3" / "r1_summary.csv"
B0 = REPO_ROOT / "results" / "b0_majority" / "metrics.json"
A0 = REPO_ROOT / "results" / "a0_shortcut" / "metrics.json"


def _write_summary(path: Path) -> None:
    """Ghi một tệp summary giả lập gồm năm kịch bản, xáo trộn thứ tự dòng."""
    fields = [
        "scenario",
        "features",
        "classifier",
        "seed",
        "is_deterministic",
        "n_seeds",
        "macro_f1",
        "ci95_low",
        "ci95_high",
    ]
    rows = [
        ["out_to_out", "ghep", "svm", "42", "True", "1", "0.8921", "0.8807", "0.9031"],
        ["orig_to_orig", "ghep", "svm", "42", "True", "1", "0.9024", "0.8909", "0.9129"],
        ["orig_to_out", "ghep", "svm", "42", "True", "1", "0.2084", "0.1953", "0.2220"],
        ["lung_to_lung", "ghep", "svm", "42", "True", "1", "0.8490", "0.8333", "0.8625"],
        ["orig_to_lung", "ghep", "svm", "42", "True", "1", "0.0723", "0.0677", "0.0770"],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)


def test_load_scenarios_orders_by_fixed_sequence(tmp_path: Path) -> None:
    """Năm kịch bản phải được xếp theo SCENARIO_ORDER, không theo thứ tự dòng tệp."""
    summary = tmp_path / "r1_summary.csv"
    _write_summary(summary)

    rows = load_scenarios(summary)

    assert [row["scenario"] for row in rows] == list(SCENARIO_ORDER)
    assert rows[0]["macro_f1"] == pytest.approx(0.9024)
    assert rows[2]["ci95_high"] == pytest.approx(0.9031)


def test_load_scenarios_rejects_missing_scenario(tmp_path: Path) -> None:
    """Thiếu bất kỳ kịch bản nào trong năm kịch bản thì phải báo lỗi."""
    summary = tmp_path / "r1_summary.csv"
    fields = ["scenario", "macro_f1", "ci95_low", "ci95_high"]
    with summary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerow(["orig_to_orig", "0.9024", "0.8909", "0.9129"])
    with pytest.raises(ValueError):
        load_scenarios(summary)


def test_load_baselines_reads_two_files(tmp_path: Path) -> None:
    """Hai mốc nền phải đọc đúng khóa từ tệp nguồn tương ứng."""
    b0_path = tmp_path / "b0.json"
    b0_path.write_text(
        json.dumps({"accuracy": 0.4824, "macro_f1": 0.1627}), encoding="utf-8"
    )
    a0_path = tmp_path / "a0.json"
    a0_path.write_text(
        json.dumps({"random_forest": {"macro_f1": 0.2397}}), encoding="utf-8"
    )

    baselines = load_baselines(b0_path, a0_path)

    assert baselines == {"b0": pytest.approx(0.1627), "a0": pytest.approx(0.2397)}


def test_build_writes_figure_and_returns_values(tmp_path: Path) -> None:
    """Hàm build phải ghi tệp hình và trả về đúng năm kịch bản cùng hai mốc nền."""
    summary = tmp_path / "r1_summary.csv"
    _write_summary(summary)
    b0_path = tmp_path / "b0.json"
    b0_path.write_text(json.dumps({"macro_f1": 0.1627}), encoding="utf-8")
    a0_path = tmp_path / "a0.json"
    a0_path.write_text(
        json.dumps({"random_forest": {"macro_f1": 0.2397}}), encoding="utf-8"
    )
    out = tmp_path / "fig.png"

    info = build(summary, b0_path, a0_path, out)

    assert out.exists()
    assert info["scenarios"] == list(SCENARIO_ORDER)
    assert info["macro_f1"][0] == 0.9024
    assert info["baselines"] == {"b0": 0.1627, "a0": 0.2397}


def test_scenario_labels_cover_all_scenarios() -> None:
    """Mỗi kịch bản phải có đúng một nhãn tiếng Việt để vẽ trục x."""
    assert len(SCENARIO_LABELS) == len(SCENARIO_ORDER)
    assert all(label.strip() for label in SCENARIO_LABELS)


@pytest.mark.skipif(
    not SUMMARY.exists() or not B0.exists() or not A0.exists(),
    reason="Thiếu tệp nguồn RQ3/B0/A0",
)
def test_baselines_match_repo_files() -> None:
    """Hai mốc nền trong hình phải trùng với giá trị đọc trực tiếp từ tệp trong repo."""
    baselines = load_baselines(B0, A0)

    assert baselines["b0"] == pytest.approx(
        json.loads(B0.read_text(encoding="utf-8"))["macro_f1"]
    )
    assert baselines["a0"] == pytest.approx(
        json.loads(A0.read_text(encoding="utf-8"))["random_forest"]["macro_f1"]
    )
