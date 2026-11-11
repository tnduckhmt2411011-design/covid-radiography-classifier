"""Sinh Hình 4.1 cho báo cáo: macro-F1 năm kịch bản RQ3 kèm khoảng tin cậy và các mốc nền.

Số liệu đọc từ các tệp đã commit, không đọc ảnh:

- ``results/report_rq3/r1_summary.csv`` (macro-F1 và khoảng tin cậy 95% của năm kịch bản);
- ``results/b0_majority/metrics.json`` (mốc tầm thường B0);
- ``results/a0_shortcut/metrics.json`` (mốc metadata A0).

Hai đường mốc nằm ngoài cột nên được trừ từ cùng các tệp này, không ghi số trực tiếp trong hình.
Nhãn trục x dùng tên mô tả tiếng Việt thay cho mã kịch bản, khớp với cách gọi trong chương.

Chạy: ``python -m scripts.report_figures_rq3``
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

# Thu tu hop le cua nam kich ban; khong phu thuoc thu tu dong trong tep CSV.
SCENARIO_ORDER: Sequence[str] = (
    "orig_to_orig",
    "lung_to_lung",
    "out_to_out",
    "orig_to_lung",
    "orig_to_out",
)

# Nhan tieng Viet cho truc x, theo thu tu SCENARIO_ORDER.
SCENARIO_LABELS: Sequence[str] = (
    "Ảnh gốc\ncả hai tập",
    "Chỉ phổi\ncả hai tập",
    "Chỉ ngoài phổi\ncả hai tập",
    "Gốc học,\nphổi đánh giá",
    "Gốc học,\nngoài phổi đánh giá",
)

DEFAULT_SUMMARY = REPO_ROOT / "results" / "report_rq3" / "r1_summary.csv"
DEFAULT_B0 = REPO_ROOT / "results" / "b0_majority" / "metrics.json"
DEFAULT_A0 = REPO_ROOT / "results" / "a0_shortcut" / "metrics.json"
DEFAULT_OUT = REPO_ROOT / "report" / "figures" / "04_macro_f1_kich_ban_rq3.png"


def load_scenarios(summary_path: Path) -> List[Dict[str, float]]:
    """Doc macro-F1 va khoang tin cậy cua nam kich ban, xep theo SCENARIO_ORDER."""
    rows: Dict[str, Dict[str, float]] = {}
    with summary_path.open(newline="", encoding="utf-8") as handle:
        for record in csv.DictReader(handle):
            scenario = record["scenario"].strip()
            rows[scenario] = {
                "macro_f1": float(record["macro_f1"]),
                "ci95_low": float(record["ci95_low"]),
                "ci95_high": float(record["ci95_high"]),
            }
    missing = [name for name in SCENARIO_ORDER if name not in rows]
    if missing:
        raise ValueError(f"Thieu kich ban: {missing}")
    return [{"scenario": name, **rows[name]} for name in SCENARIO_ORDER]


def load_baselines(b0_path: Path, a0_path: Path) -> Dict[str, float]:
    """Doc hai moc nen: B0 va A0."""
    b0 = json.loads(b0_path.read_text(encoding="utf-8"))
    a0 = json.loads(a0_path.read_text(encoding="utf-8"))
    return {
        "b0": float(b0["macro_f1"]),
        "a0": float(a0["random_forest"]["macro_f1"]),
    }


def draw(
    rows: Sequence[Dict[str, float]],
    baselines: Dict[str, float],
    out_path: Path,
) -> Path:
    """Ve bieu do cot macro-F1 kem que khoang tin cậy va hai duong moc nen."""
    values = np.array([float(row["macro_f1"]) for row in rows], dtype=float)
    lows = np.array([float(row["ci95_low"]) for row in rows], dtype=float)
    highs = np.array([float(row["ci95_high"]) for row in rows], dtype=float)

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    positions = np.arange(len(rows))
    ax.bar(positions, values, width=0.58, color="#4C72B0", zorder=2)
    ax.errorbar(
        positions,
        values,
        yerr=np.vstack([values - lows, highs - values]),
        fmt="none",
        ecolor="#2F2F2F",
        elinewidth=1.2,
        capsize=4,
        zorder=3,
    )

    # Nho ruong ben phai de dat nhan moc nen, tranh de len cot va que khoang tin cậy.
    right_edge = len(rows) - 0.5 + 1.9
    ax.set_xlim(-0.6, right_edge)
    lines = [
        (baselines["b0"], "Mốc tầm thường B0", "#C44E52"),
        (baselines["a0"], "Mốc metadata A0", "#DD8452"),
    ]
    for value, label, color in lines:
        ax.axhline(value, linestyle="--", linewidth=1.1, color=color, zorder=1)
        ax.text(
            len(rows) - 0.35,
            value + 0.012,
            label,
            color=color,
            fontsize=8,
            ha="left",
            va="bottom",
        )

    ax.set_xticks(positions, SCENARIO_LABELS, fontsize=8)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Macro-F1 (3.174 ảnh validation)")
    ax.set_xlabel("Kịch bản")
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6, zorder=0)
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build(
    summary_path: Path,
    b0_path: Path,
    a0_path: Path,
    out_path: Path,
) -> Dict[str, object]:
    """Doc so lieu, ve hinh va tra ve thong tin dung cho bao cao."""
    rows = load_scenarios(summary_path)
    baselines = load_baselines(b0_path, a0_path)
    path = draw(rows, baselines, out_path)
    return {
        "figure": path.as_posix(),
        "scenarios": [row["scenario"] for row in rows],
        "macro_f1": [round(float(row["macro_f1"]), 4) for row in rows],
        "ci95_low": [round(float(row["ci95_low"]), 4) for row in rows],
        "ci95_high": [round(float(row["ci95_high"]), 4) for row in rows],
        "baselines": {key: round(value, 4) for key, value in baselines.items()},
    }


def main(argv: List[str] | None = None) -> int:
    """Diem vao CLI."""
    parser = argparse.ArgumentParser(description="Ve bieu do RQ3 cho bao cao.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--b0", type=Path, default=DEFAULT_B0)
    parser.add_argument("--a0", type=Path, default=DEFAULT_A0)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    info = build(args.summary, args.b0, args.a0, args.out)
    print(f"Da ghi {info['figure']}")
    print(f"Kich ban: {info['scenarios']}")
    print(f"Macro-F1: {info['macro_f1']}")
    print(f"Moc nen: {info['baselines']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
