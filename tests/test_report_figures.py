"""Bộ kiểm thử tự động cho S6-01 (ma trận nhầm lẫn của mô hình SVM)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from scripts.report_figures import (
    CLASS_NAMES,
    build,
    load_confusion,
    normalize_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
METRICS = REPO_ROOT / "results" / "rq2_ghep_svm_s42" / "metrics.json"


def test_normalize_rows_sums_to_one() -> None:
    """Chuẩn hóa theo hàng nên mỗi hàng có tổng bằng 1."""
    matrix = np.array([[5, 5], [1, 3]])
    normalized = normalize_rows(matrix)
    np.testing.assert_allclose(normalized.sum(axis=1), [1.0, 1.0])
    np.testing.assert_allclose(normalized[1], [0.25, 0.75])


def test_normalize_rows_handles_empty_row() -> None:
    """Hàng toàn 0 không được chia cho 0."""
    matrix = np.array([[0, 0], [2, 2]])
    normalized = normalize_rows(matrix)
    assert np.all(np.isfinite(normalized))
    np.testing.assert_allclose(normalized[1], [0.5, 0.5])


def test_build_writes_figure_and_counts(tmp_path: Path) -> None:
    """Hàm build phải ghi tệp hình và trả về đúng ma trận đã cho."""
    metrics = tmp_path / "metrics.json"
    counts = [[8, 1, 1, 0], [1, 6, 2, 0], [0, 2, 7, 1], [0, 0, 1, 3]]
    metrics.write_text(
        json.dumps({"confusion_matrix": counts}), encoding="utf-8"
    )
    out = tmp_path / "fig.png"

    info = build(metrics, out)

    assert out.exists()
    assert info["counts"] == counts
    # Recall đường chéo: 8/10, 6/9, 7/10, 3/4, làm tròn 4 chữ số như trong báo cáo.
    assert info["row_recall"] == [0.8, round(6 / 9, 4), 0.7, 0.75]


def test_load_confusion_rejects_non_square(tmp_path: Path) -> None:
    """Ma trận không phải 4×4 phải bị từ chối."""
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({"confusion_matrix": [[1, 2], [3, 4]]}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_confusion(metrics)


@pytest.mark.skipif(not METRICS.exists(), reason="Thiếu tệp metrics của lần chạy SVM")
def test_diagonal_matches_metrics_recall() -> None:
    """Recall tính từ ma trận nhầm lẫn phải khớp với recall trong tệp metrics."""
    payload = json.loads(METRICS.read_text(encoding="utf-8"))
    matrix = load_confusion(METRICS)
    diagonal = normalize_rows(matrix).diagonal()

    per_class = payload["per_class"]
    for index, class_name in enumerate(CLASS_NAMES):
        assert diagonal[index] == pytest.approx(per_class[class_name]["recall"])
