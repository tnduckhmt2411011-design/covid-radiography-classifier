"""Bộ kiểm thử tự động cho Hình 5.1 (ma trận nhầm lẫn trên tập test độc lập).

Kiểm thử viết trước (TDD): các hàm của ``scripts.report_figures_final_test``
chưa tồn tại ở lần chạy đầu, bộ kiểm thử phải fail cho đến khi module được viết.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pytest

from scripts.report_figures_final_test import (
    CLASS_LABELS,
    build,
    load_metrics,
    normalize_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
METRICS = REPO_ROOT / "results" / "final_test" / "metrics.json"


def _write_metrics(path: Path, *, macro_f1: float = 0.8714) -> None:
    """Ghi một tệp metrics giả lập gồm bốn lớp và ma trận nhầm lẫn 4×4."""
    payload = {
        "accuracy": 0.8656,
        "balanced_accuracy": 0.8744,
        "macro_f1": macro_f1,
        "weighted_f1": 0.8659,
        "macro_precision": 0.8687,
        "macro_recall": 0.8744,
        "per_class": {
            "COVID": {
                "precision": 0.9257,
                "recall": 0.9171,
                "f1": 0.9214,
                "support": 543,
            },
            "Lung_Opacity": {
                "precision": 0.8013,
                "recall": 0.8296,
                "f1": 0.8152,
                "support": 904,
            },
            "Normal": {
                "precision": 0.8844,
                "recall": 0.8659,
                "f1": 0.8751,
                "support": 1529,
            },
            "Viral Pneumonia": {
                "precision": 0.8634,
                "recall": 0.885,
                "f1": 0.8741,
                "support": 200,
            },
        },
        "confusion_matrix": [
            [498, 22, 18, 5],
            [12, 750, 142, 0],
            [20, 162, 1324, 23],
            [8, 2, 13, 177],
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_class_labels_match_per_class_keys() -> None:
    """Thứ tự nhãn lớp trong hình phải trùng thứ tự khóa của per_class."""
    assert list(CLASS_LABELS) == [
        "COVID",
        "Lung_Opacity",
        "Normal",
        "Viral Pneumonia",
    ]


def test_load_metrics_reads_matrix_and_classes(tmp_path: Path) -> None:
    """Hàm đọc phải trả về đúng ma trận 4×4 và bốn lớp."""
    path = tmp_path / "metrics.json"
    _write_metrics(path)

    metrics = load_metrics(path)

    assert metrics["macro_f1"] == pytest.approx(0.8714)
    assert list(metrics["per_class"].keys()) == list(CLASS_LABELS)
    assert metrics["confusion_matrix"][1][1] == 750
    assert metrics["confusion_matrix"][3][3] == 177


def test_load_metrics_rejects_missing_confusion_matrix(tmp_path: Path) -> None:
    """Thiếu ma trận nhầm lẫn thì phải báo lỗi, không vẽ hình với dữ liệu thiếu."""
    path = tmp_path / "metrics.json"
    payload = json.loads(json.dumps({"per_class": {}, "macro_f1": 0.5}))
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_metrics(path)


def test_load_metrics_rejects_wrong_matrix_shape(tmp_path: Path) -> None:
    """Ma trận không đúng 4×4 thì phải báo lỗi."""
    path = tmp_path / "metrics.json"
    _write_metrics(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["confusion_matrix"] = [[1, 2], [3, 4]]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_metrics(path)


def test_row_normalization_matches_source_recall(tmp_path: Path) -> None:
    """Hàng chuẩn hóa phải cho đúng recall từng lớp như tệp nguồn (ô chéo)."""
    path = tmp_path / "metrics.json"
    _write_metrics(path)
    metrics = load_metrics(path)

    shares = normalize_rows(metrics["confusion_matrix"])

    assert len(shares) == 4 and all(len(row) == 4 for row in shares)
    for i in range(4):
        total = sum(metrics["confusion_matrix"][i])
        assert sum(shares[i]) == pytest.approx(1.0)
        for j in range(4):
            assert shares[i][j] == pytest.approx(
                metrics["confusion_matrix"][i][j] / total
            )
    # Hàng tổng 0 không gây lỗi chia.
    assert normalize_rows([[0, 0], [1, 1]]) == [[0.0, 0.0], [0.5, 0.5]]


def test_build_writes_figure_and_returns_source_values(tmp_path: Path) -> None:
    """Hàm build phải ghi tệp hình và trả về đúng số liệu của tệp nguồn."""
    path = tmp_path / "metrics.json"
    _write_metrics(path)
    out = tmp_path / "fig.png"

    info = build(path, out)

    assert out.exists()
    assert info["classes"] == list(CLASS_LABELS)
    assert info["confusion_matrix"][1][1] == 750
    assert info["accuracy"] == pytest.approx(0.8656)
    assert info["macro_f1"] == pytest.approx(0.8714)


def test_build_uses_real_metrics_file(tmp_path: Path) -> None:
    """Vẽ từ chính tệp metrics của repo: số trả về phải trùng tệp nguồn."""
    if not METRICS.exists():
        pytest.skip("Thiếu tệp nguồn results/final_test/metrics.json")
    source = json.loads(METRICS.read_text(encoding="utf-8"))
    out = tmp_path / "fig.png"

    info = build(METRICS, out)

    assert out.exists()
    assert info["confusion_matrix"] == source["confusion_matrix"]
    assert info["macro_f1"] == pytest.approx(source["macro_f1"])
    assert info["per_class"]["COVID"]["support"] == pytest.approx(543)


def test_figure_rows_pinned_to_repo_file(tmp_path: Path) -> None:
    """Hàng chuẩn hóa trên hình phải khớp từng ô với metrics.json trong repo.

    Đây là chốt chặn chép nhầm: nếu ai sửa tay nhãn trong hình hoặc trong chương
    lệch với tệp nguồn, kiểm thử này fail.
    """
    if not METRICS.exists():
        pytest.skip("Thiếu tệp nguồn results/final_test/metrics.json")
    source = json.loads(METRICS.read_text(encoding="utf-8"))
    matrix: List[List[int]] = source["confusion_matrix"]

    shares = normalize_rows(matrix)

    for i, row in enumerate(matrix):
        total = sum(row)
        for j, value in enumerate(row):
            assert shares[i][j] == pytest.approx(value / total)
    # Ô chéo chính là recall lớp đó trong per_class của tệp nguồn.
    for i, label in enumerate(CLASS_LABELS):
        recall = float(source["per_class"][label]["recall"])
        assert shares[i][i] == pytest.approx(recall)


def test_supports_sum_to_test_size(tmp_path: Path) -> None:
    """Tổng support bốn lớp phải bằng 3.176 ảnh tập test."""
    if not METRICS.exists():
        pytest.skip("Thiếu tệp nguồn results/final_test/metrics.json")
    metrics = load_metrics(METRICS)

    total = sum(int(v["support"]) for v in metrics["per_class"].values())

    assert total == 3176


def test_build_returns_dict_of_expected_shape(tmp_path: Path) -> None:
    """Kiểu dữ liệu trả về của build phải ổn định cho báo cáo và công cụ khác."""
    path = tmp_path / "metrics.json"
    _write_metrics(path)

    info: Dict[str, object] = build(path, tmp_path / "fig.png")

    for key in ("figure", "classes", "confusion_matrix", "per_class", "accuracy", "macro_f1"):
        assert key in info, f"Thiếu khóa {key}"
