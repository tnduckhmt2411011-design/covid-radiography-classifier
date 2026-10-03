"""Kiểm thử đơn vị cho module src/metrics.py.

Tuần 3 (Sprint 2) - Track B.
Phụ trách: TV6.
"""

import numpy as np
import pytest
from src.metrics import compute_metrics, plot_confusion_matrix, DEFAULT_CLASS_NAMES


def test_compute_metrics_perfect_prediction():
    """Kiểm tra trường hợp dự đoán hoàn hảo 100%."""
    y_true = [0, 1, 2, 3, 0, 1, 2, 3]
    y_pred = [0, 1, 2, 3, 0, 1, 2, 3]

    res = compute_metrics(y_true, y_pred)
    assert res["accuracy"] == 1.0
    assert res["balanced_accuracy"] == 1.0
    assert res["macro_f1"] == 1.0
    assert res["weighted_f1"] == 1.0
    assert res["macro_precision"] == 1.0
    assert res["macro_recall"] == 1.0

    # Kiểm tra per_class
    for cls in DEFAULT_CLASS_NAMES:
        assert res["per_class"][cls]["f1"] == 1.0
        assert res["per_class"][cls]["support"] == 2


def test_compute_metrics_all_wrong():
    """Kiểm tra trường hợp dự đoán sai hoàn toàn."""
    y_true = [0, 0, 0, 0]
    y_pred = [1, 1, 1, 1]

    res = compute_metrics(y_true, y_pred)
    assert res["accuracy"] == 0.0
    assert res["balanced_accuracy"] == 0.0


def test_compute_metrics_partial_accuracy():
    """Kiểm tra tính toán với ma trận nhầm lẫn đã biết."""
    # 2 mẫu lớp 0 (1 đúng, 1 sai thành 1)
    # 2 mẫu lớp 1 (cả 2 đúng)
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 1, 1]

    res = compute_metrics(y_true, y_pred, class_names=["COVID", "Normal"])
    # Accuracy = 3/4 = 0.75
    assert res["accuracy"] == 0.75

    # Recall lớp 0 = 1/2 = 0.5; Recall lớp 1 = 2/2 = 1.0 -> Balanced Acc = (0.5 + 1.0)/2 = 0.75
    assert res["balanced_accuracy"] == 0.75

    # Precision lớp 0 = 1/1 = 1.0; Precision lớp 1 = 2/3 = 0.6667
    assert res["per_class"]["COVID"]["precision"] == 1.0
    assert round(res["per_class"]["Normal"]["precision"], 4) == 0.6667


def test_plot_confusion_matrix():
    """Kiểm tra hàm vẽ ma trận nhầm lẫn chạy không sinh lỗi."""
    cm = [[10, 2], [1, 15]]
    fig = plot_confusion_matrix(cm, class_names=["COVID", "Normal"], normalize=True)
    assert fig is not None


if __name__ == "__main__":
    test_compute_metrics_perfect_prediction()
    test_compute_metrics_all_wrong()
    test_compute_metrics_partial_accuracy()
    test_plot_confusion_matrix()
    print("Tất cả bài kiểm tra metrics đều ĐẠT!")
