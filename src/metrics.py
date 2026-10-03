"""Module metrics.py

Trách nhiệm:
- Tính toán toàn diện các chỉ số đánh giá cho bài toán phân loại X-quang 4 lớp (phụ trách: TV6).
- Chỉ số chính: Macro-F1 (tiêu chí chính để chọn mô hình và lưu best checkpoint), Balanced Accuracy.
- Chỉ số chi tiết: Accuracy, Weighted-F1, Per-class Precision, Per-class Recall, Per-class F1.
- Xuất ma trận nhầm lẫn (Confusion Matrix) dạng số liệu và biểu đồ trực quan hóa.
"""

from typing import Dict, List, Optional, Union
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

DEFAULT_CLASS_NAMES = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]


def compute_metrics(
    y_true: Union[List[int], np.ndarray],
    y_pred: Union[List[int], np.ndarray],
    class_names: Optional[List[str]] = None,
) -> Dict[str, Union[float, Dict[str, float], List[List[int]]]]:
    """Tính toán toàn bộ các thước đo hiệu năng phân loại đa lớp.

    Args:
        y_true: Danh sách hoặc mảng nhãn thực tế (ground truth).
        y_pred: Danh sách hoặc mảng nhãn mô hình dự đoán.
        class_names: Danh sách tên các lớp (mặc định 4 lớp).

    Returns:
        Dict chứa:
        - 'accuracy': float
        - 'balanced_accuracy': float
        - 'macro_f1': float (thước đo chính)
        - 'weighted_f1': float
        - 'macro_precision': float
        - 'macro_recall': float
        - 'per_class': Dict tên lớp -> {'precision', 'recall', 'f1', 'support'}
        - 'confusion_matrix': List[List[int]]
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if class_names is None:
        class_names = DEFAULT_CLASS_NAMES
    num_classes = len(class_names)

    acc = float(accuracy_score(y_true, y_pred))
    balanced_acc = float(balanced_accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    macro_prec = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, average="macro", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))

    # Per-class metrics
    per_class_prec = precision_score(y_true, y_pred, average=None, labels=list(range(num_classes)), zero_division=0)
    per_class_rec = recall_score(y_true, y_pred, average=None, labels=list(range(num_classes)), zero_division=0)
    per_class_f1 = f1_score(y_true, y_pred, average=None, labels=list(range(num_classes)), zero_division=0)

    per_class_dict = {}
    for idx, name in enumerate(class_names):
        support_count = int(np.sum(y_true == idx))
        per_class_dict[name] = {
            "precision": float(per_class_prec[idx]),
            "recall": float(per_class_rec[idx]),
            "f1": float(per_class_f1[idx]),
            "support": support_count,
        }

    return {
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(balanced_acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "per_class": per_class_dict,
        "confusion_matrix": cm.tolist(),
    }


def plot_confusion_matrix(
    cm: Union[List[List[int]], np.ndarray],
    class_names: Optional[List[str]] = None,
    save_path: Optional[str] = None,
    normalize: bool = False,
    title: str = "Confusion Matrix",
) -> plt.Figure:
    """Vẽ và lưu biểu đồ ma trận nhầm lẫn bằng Matplotlib.

    Args:
        cm: Ma trận nhầm lẫn dạng 2D array hoặc list.
        class_names: Danh sách tên lớp hiển thị trên các trục.
        save_path: Đường dẫn lưu file ảnh (tùy chọn).
        normalize: True nếu muốn chuẩn hóa tỷ lệ theo hàng (Recall per class).
        title: Tiêu đề biểu đồ.

    Returns:
        plt.Figure: Đối tượng Figure của matplotlib.
    """
    cm = np.asarray(cm)
    if class_names is None:
        class_names = DEFAULT_CLASS_NAMES

    if normalize:
        row_sums = cm.sum(axis=1)[:, np.newaxis]
        row_sums[row_sums == 0] = 1
        cm_display = cm.astype("float") / row_sums
        fmt = ".2%"
    else:
        cm_display = cm
        fmt = "d"

    fig, ax = plt.subplots(figsize=(7, 6))
    cax = ax.matshow(cm_display, cmap="Blues")
    fig.colorbar(cax)

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=30, ha="left", fontsize=9)
    ax.set_yticklabels(class_names, fontsize=9)
    ax.set_xlabel("Predicted Label", fontweight="bold", labelpad=10)
    ax.set_ylabel("True Label", fontweight="bold", labelpad=10)
    ax.set_title(title, fontweight="bold", pad=15)

    thresh = cm_display.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val_str = f"{cm_display[i, j]:{fmt}}"
            color = "white" if cm_display[i, j] > thresh else "black"
            ax.text(j, i, val_str, ha="center", va="center", color=color, fontsize=9)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Đã lưu ma trận nhầm lẫn tại: {save_path}")

    return fig
