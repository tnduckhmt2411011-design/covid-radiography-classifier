"""Sinh Hình 3.1 cho báo cáo: ma trận nhầm lẫn chuẩn hóa theo hàng.

Số liệu đọc từ ``results/rq2_ghep_svm_s42/metrics.json`` (khóa ``confusion_matrix``),
đã commit và không đọc ảnh. Mỗi hàng chia cho tổng hàng, nên ô trên đường chéo là recall
của lớp đó. Hình ghi kèm số đếm gốc trong ngoặc để bảng và hình không lệch nhau.

Chạy: ``python -m scripts.report_figures``
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

CLASS_NAMES: Sequence[str] = ("COVID", "Lung_Opacity", "Normal", "Viral Pneumonia")

DEFAULT_METRICS = REPO_ROOT / "results" / "rq2_ghep_svm_s42" / "metrics.json"
DEFAULT_OUT = REPO_ROOT / "report" / "figures" / "03_ma_tran_nham_lon_svm_val.png"


def load_confusion(metrics_path: Path) -> np.ndarray:
    """Đọc ma trận nhầm lẫn từ tệp metrics và kiểm kích thước 4×4."""
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    matrix = payload.get("confusion_matrix")
    if matrix is None:
        raise ValueError(f"{metrics_path} khong co khoa 'confusion_matrix'")
    array = np.asarray(matrix, dtype=int)
    if array.shape != (4, 4):
        raise ValueError(f"Ma tran phai 4x4, thuc te {array.shape}")
    return array


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    """Chia mỗi hàng cho tổng hàng; hàng toàn 0 giữ nguyên để tránh chia cho 0."""
    totals = matrix.sum(axis=1, keepdims=True)
    safe = np.where(totals > 0, totals, 1)
    return matrix / safe


def draw(matrix: np.ndarray, out_path: Path, title: str) -> Path:
    """Vẽ heatmap recall theo hàng cho ma trận nhầm lẫn."""
    row_normalized = normalize_rows(matrix)
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    image = ax.imshow(row_normalized, cmap="Blues", vmin=0.0, vmax=1.0)

    ax.set_xticks(range(4), CLASS_NAMES, rotation=20, ha="right")
    ax.set_yticks(range(4), CLASS_NAMES)
    ax.set_xlabel("Nhãn dự đoán")
    ax.set_ylabel("Nhãn thực")
    ax.set_title(title)

    for i in range(4):
        for j in range(4):
            value = matrix[i, j]
            share = row_normalized[i, j]
            color = "white" if share > 0.55 else "black"
            ax.text(
                j,
                i,
                f"{value}\n{share:.0%}",
                ha="center",
                va="center",
                fontsize=9,
                color=color,
            )

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    ax.set_aspect("equal")
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def build(metrics_path: Path, out_path: Path) -> Dict[str, object]:
    """Đọc số liệu, vẽ hình và trả về thông tin dùng cho báo cáo."""
    matrix = load_confusion(metrics_path)
    path = draw(matrix, out_path, "Ma trận nhầm lẫn của SVM trên tập validation (3.174 ảnh)")
    row_normalized = normalize_rows(matrix)
    diagonal = row_normalized.diagonal().tolist()
    return {
        "figure": path.as_posix(),
        "counts": matrix.tolist(),
        "row_recall": [round(x, 4) for x in diagonal],
    }


def main(argv: List[str] | None = None) -> int:
    """Điểm vào CLI."""
    parser = argparse.ArgumentParser(description="Vẽ ma trận nhầm lẫn cho báo cáo.")
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    info = build(args.metrics, args.out)
    print(f"Đã ghi {info['figure']}")
    print(f"Recall theo hàng: {info['row_recall']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
