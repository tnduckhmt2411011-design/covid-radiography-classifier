"""Sinh Hình 5.1 cho báo cáo: ma trận nhầm lẫn trên tập test độc lập.

Số liệu đọc từ tệp đã commit, không đọc ảnh:

- ``results/final_test/metrics.json`` (ma trận nhầm lẫn 4×4, accuracy,
  macro-F1 và chỉ số từng lớp của lần đánh giá tập test duy nhất).

Nhãn hàng và cột dùng đúng thứ tự khóa ``per_class`` trong tệp nguồn; không
ghi số trực tiếp trong hình. Chú thích hình đặt ở dưới hình trong báo cáo.

Chạy: ``python -m scripts.report_figures_final_test``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

# Thứ tự lớp đúng như khóa per_class trong metrics.json.
CLASS_LABELS: Sequence[str] = (
    "COVID",
    "Lung_Opacity",
    "Normal",
    "Viral Pneumonia",
)

DEFAULT_METRICS = REPO_ROOT / "results" / "final_test" / "metrics.json"
DEFAULT_OUT = REPO_ROOT / "report" / "figures" / "05_ma_tran_nham_lon_test.png"

REQUIRED_KEYS = ("accuracy", "balanced_accuracy", "macro_f1", "per_class", "confusion_matrix")


def load_metrics(metrics_path: Path) -> Dict[str, object]:
    """Đọc metrics.json và kiểm tra cấu trúc trước khi vẽ.

    Raises:
        ValueError: Nếu thiếu khóa bắt buộc, sai bốn lớp hoặc ma trận không 4×4.
    """
    metrics = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
    for key in REQUIRED_KEYS:
        if key not in metrics:
            raise ValueError(f"Thieu khoa '{key}' trong {metrics_path}")
    if list(metrics["per_class"].keys()) != list(CLASS_LABELS):
        raise ValueError(
            "Thu tu lop trong per_class khong dung "
            f"{list(CLASS_LABELS)}: {list(metrics['per_class'].keys())}"
        )
    matrix = metrics["confusion_matrix"]
    if len(matrix) != len(CLASS_LABELS) or any(len(row) != len(CLASS_LABELS) for row in matrix):
        raise ValueError("Ma tran nham lan phai 4x4")
    return metrics


def cell_labels(matrix: Sequence[Sequence[int]]) -> List[List[str]]:
    """Chữ ghi trong từng ô hình: đúng số đếm của ma trận nguồn."""
    return [[str(int(value)) for value in row] for row in matrix]


def draw(metrics: Dict[str, object], out_path: Path) -> Path:
    """Vẽ biểu đồ nhiệt ma trận nhầm lẫn, chữ thể hiện số đếm từng ô."""
    matrix = np.array(metrics["confusion_matrix"], dtype=int)
    labels = cell_labels(matrix)

    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    image = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=int(matrix.max()))
    colorbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.04)
    colorbar.set_label("Số ảnh", fontsize=9)
    colorbar.ax.tick_params(labelsize=8)

    threshold = float(matrix.max()) / 2.0
    for i in range(len(CLASS_LABELS)):
        for j in range(len(CLASS_LABELS)):
            value = matrix[i, j]
            ax.text(
                j,
                i,
                str(value),
                ha="center",
                va="center",
                fontsize=10,
                color="white" if value > threshold else "#1A1A1A",
            )

    ax.set_xticks(range(len(CLASS_LABELS)), CLASS_LABELS, fontsize=9)
    ax.set_yticks(range(len(CLASS_LABELS)), CLASS_LABELS, fontsize=9)
    ax.set_xlabel("Nhãn dự đoán", fontsize=10)
    ax.set_ylabel("Nhãn thực", fontsize=10)
    ax.set_xticks(np.arange(-0.5, len(CLASS_LABELS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(CLASS_LABELS), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build(metrics_path: Path, out_path: Path) -> Dict[str, object]:
    """Đọc số liệu, vẽ hình và trả về thông tin dùng cho báo cáo."""
    metrics = load_metrics(metrics_path)
    path = draw(metrics, out_path)
    return {
        "figure": path.as_posix(),
        "classes": list(CLASS_LABELS),
        "confusion_matrix": [list(row) for row in metrics["confusion_matrix"]],
        "per_class": metrics["per_class"],
        "accuracy": float(metrics["accuracy"]),
        "balanced_accuracy": float(metrics["balanced_accuracy"]),
        "macro_f1": float(metrics["macro_f1"]),
    }


def main(argv: List[str] | None = None) -> int:
    """Điểm vào CLI."""
    parser = argparse.ArgumentParser(description="Ve ma tran nham lan tap test cho bao cao.")
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    info = build(args.metrics, args.out)
    print(f"Da ghi {info['figure']}")
    print(f"Lop: {info['classes']}")
    print(f"Macro-F1: {info['macro_f1']:.4f}")
    print(f"Accuracy: {info['accuracy']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
