"""Kiểm thử cho module ``src/eda_brightness.py`` (mục 2.2 của báo cáo).

Ba nhóm kiểm tra:

1. Hàm tính toán chạy đúng trên dữ liệu tổng hợp có đáp án biết trước: thống kê mô tả,
   AUC (tách hoàn hảo cho 1,0; đồng hạng cho 0,5), tỉ lệ nằm trong khoảng tứ phân vị.
2. Hàm ghi kết quả tạo đủ hai tệp, đúng bốn lớp, đúng số cột.
3. Tệp CSV đã commit khớp với ``splits/manifest.csv`` để số trong báo cáo truy vết được.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.eda_brightness import (
    CLASS_ORDER,
    auc_against_rest,
    build_outputs,
    color_mode_counts,
    format_markdown_table,
    format_vn,
    load_manifest,
    share_in_reference_iqr,
    summarize_by_class,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "splits" / "manifest.csv"
COMMITTED_CSV = REPO_ROOT / "results" / "eda" / "brightness_by_class.csv"
COMMITTED_JSON = REPO_ROOT / "results" / "eda" / "brightness_channels.json"


def make_frame(rows: list[tuple[str, str, float, str]]) -> pd.DataFrame:
    """Dựng DataFrame tối thiểu đúng bốn cột mà module yêu cầu."""
    return pd.DataFrame(
        rows, columns=["image_id", "label", "mean_brightness", "color_mode"]
    )


def test_summarize_by_class_matches_hand_computed_values() -> None:
    """Ba giá trị 10, 20, 30 cho trung bình 20, SD mẫu 10, trung vị 20, tứ phân vị 15–25."""
    frame = make_frame(
        [
            ("a1", "COVID", 10.0, "L"),
            ("a2", "COVID", 20.0, "L"),
            ("a3", "COVID", 30.0, "L"),
            ("b1", "Normal", 0.0, "L"),
            ("b2", "Normal", 0.0, "L"),
            ("c1", "Lung_Opacity", 12.0, "L"),
            ("d1", "Viral Pneumonia", 14.0, "L"),
        ]
    )

    summary = summarize_by_class(frame)
    covid = summary.loc[summary["label"] == "COVID"].iloc[0]

    assert list(summary["label"]) == CLASS_ORDER
    assert covid["n"] == 3
    assert covid["mean"] == pytest.approx(20.0)
    assert covid["sd"] == pytest.approx(10.0)
    assert covid["median"] == pytest.approx(20.0)
    assert covid["q1"] == pytest.approx(15.0)
    assert covid["q3"] == pytest.approx(25.0)
    assert covid["min"] == pytest.approx(10.0)
    assert covid["max"] == pytest.approx(30.0)


def test_auc_against_rest_detects_perfect_separation() -> None:
    """Lớp cần tách sáng hơn toàn bộ phần còn lại thì AUC bằng 1,0; ngược lại bằng 0,0."""
    high = make_frame(
        [
            ("a1", "COVID", 40.0, "L"),
            ("a2", "COVID", 50.0, "L"),
            ("b1", "Normal", 10.0, "L"),
            ("c1", "Lung_Opacity", 20.0, "L"),
            ("d1", "Viral Pneumonia", 30.0, "L"),
        ]
    )
    low = make_frame(
        [
            ("a1", "COVID", 10.0, "L"),
            ("a2", "COVID", 15.0, "L"),
            ("b1", "Normal", 40.0, "L"),
            ("c1", "Lung_Opacity", 50.0, "L"),
            ("d1", "Viral Pneumonia", 60.0, "L"),
        ]
    )

    assert auc_against_rest(high, "COVID") == pytest.approx(1.0)
    assert auc_against_rest(low, "COVID") == pytest.approx(0.0)


def test_auc_against_rest_is_half_when_all_values_tie() -> None:
    """Không có thứ tự nào để xếp hạng thì AUC phải bằng 0,5, không phải 0,0."""
    frame = make_frame(
        [
            ("a1", "COVID", 7.0, "L"),
            ("a2", "COVID", 7.0, "L"),
            ("b1", "Normal", 7.0, "L"),
            ("c1", "Lung_Opacity", 7.0, "L"),
            ("d1", "Viral Pneumonia", 7.0, "L"),
        ]
    )

    assert auc_against_rest(frame, "COVID") == pytest.approx(0.5)


def test_share_in_reference_iqr_counts_boundaries() -> None:
    """Biên khoảng tứ phân vị được tính là nằm trong, nên giá trị đúng bằng q1 và q3 vẫn đếm."""
    frame = make_frame(
        [
            ("n1", "Normal", 0.0, "L"),
            ("n2", "Normal", 10.0, "L"),
            ("n3", "Normal", 20.0, "L"),
            ("n4", "Normal", 30.0, "L"),
            ("n5", "Normal", 40.0, "L"),
            ("c1", "COVID", 10.0, "L"),
            ("c2", "COVID", 30.0, "L"),
            ("c3", "COVID", 99.0, "L"),
        ]
    )

    # q1 = 10, q3 = 30: n2, n3, n4, c1, c2 nằm trong, tức 5/8.
    assert share_in_reference_iqr(frame, "Normal") == pytest.approx(5 / 8)


def test_color_mode_counts_separates_rgb_from_grayscale() -> None:
    """Chỉ lớp Viral Pneumonia có ảnh RGB trong dữ liệu tổng hợp này."""
    frame = make_frame(
        [
            ("a1", "COVID", 1.0, "L"),
            ("b1", "Normal", 2.0, "L"),
            ("c1", "Lung_Opacity", 3.0, "L"),
            ("d1", "Viral Pneumonia", 4.0, "L"),
            ("d2", "Viral Pneumonia", 5.0, "RGB"),
        ]
    )

    counts = color_mode_counts(frame)

    assert counts["COVID"] == {"L": 1}
    assert counts["Viral Pneumonia"] == {"L": 1, "RGB": 1}


def test_load_manifest_rejects_missing_column_and_unknown_label(tmp_path: Path) -> None:
    """Manifest hỏng phải dừng sớm thay vì cho ra bảng thiếu lớp hoặc thiếu cột."""
    missing_col = tmp_path / "missing_col.csv"
    make_frame([("a1", "COVID", 1.0, "L")]).drop(columns=["color_mode"]).to_csv(
        missing_col, index=False
    )

    unknown_label = tmp_path / "unknown_label.csv"
    make_frame([("a1", "COVID", 1.0, "L"), ("b1", "SARS", 2.0, "L")]).to_csv(
        unknown_label, index=False
    )

    blank_value = tmp_path / "blank_value.csv"
    frame = make_frame([("a1", "COVID", 1.0, "L")]).astype({"mean_brightness": float})
    frame.loc[0, "mean_brightness"] = float("nan")
    frame.to_csv(blank_value, index=False)

    with pytest.raises(ValueError, match="thiếu cột"):
        load_manifest(missing_col)
    with pytest.raises(ValueError, match="nhãn lạ"):
        load_manifest(unknown_label)
    with pytest.raises(ValueError, match="mean_brightness"):
        load_manifest(blank_value)


def test_build_outputs_writes_csv_and_json(tmp_path: Path) -> None:
    """Hai tệp kết quả phải xuất hiện, CSV đủ bốn lớp, JSON đủ khoá dùng trong mục 2.2."""
    manifest = tmp_path / "manifest.csv"
    make_frame(
        [
            ("a1", "COVID", 40.0, "L"),
            ("a2", "COVID", 44.0, "L"),
            ("b1", "Normal", 20.0, "L"),
            ("b2", "Normal", 22.0, "L"),
            ("c1", "Lung_Opacity", 10.0, "L"),
            ("c2", "Lung_Opacity", 12.0, "L"),
            ("d1", "Viral Pneumonia", 30.0, "L"),
            ("d2", "Viral Pneumonia", 32.0, "RGB"),
        ]
    ).to_csv(manifest, index=False)
    out_dir = tmp_path / "eda"

    written = build_outputs(manifest, out_dir)

    assert set(written) == {"brightness_by_class.csv", "brightness_channels.json"}
    summary = pd.read_csv(written["brightness_by_class.csv"])
    assert list(summary["label"]) == CLASS_ORDER
    assert summary["n"].sum() == 8
    assert "auc_vs_rest" in summary.columns

    channels = json.loads(written["brightness_channels.json"].read_text(encoding="utf-8"))
    assert channels["n_images"] == 8
    assert channels["auc_covid_vs_rest"] == pytest.approx(1.0)
    assert 0.0 <= channels["share_in_normal_iqr"] <= 1.0
    assert channels["color_mode_counts"]["Viral Pneumonia"] == {"L": 1, "RGB": 1}


def test_format_vn_uses_vietnamese_separators() -> None:
    """Số nguyên ngăn nghìn bằng dấu chấm, số thực ngăn thập phân bằng dấu phẩy."""
    assert format_vn(21165, 0) == "21.165"
    assert format_vn(139.521) == "139,5"
    assert format_vn(0.658469, 4) == "0,6585"


def test_markdown_table_has_one_row_per_class() -> None:
    """Bảng dán vào báo cáo phải có bốn dòng dữ liệu cộng hai dòng tiêu đề."""
    summary = pd.DataFrame(
        [
            {"label": label, "n": 10, "mean": 1.0, "sd": 0.1, "median": 1.0,
             "q1": 0.5, "q3": 1.5, "min": 0.0, "max": 2.0, "auc_vs_rest": 0.5}
            for label in CLASS_ORDER
        ]
    )

    lines = format_markdown_table(summary).splitlines()

    assert len(lines) == 6
    assert all(line.startswith("|") for line in lines)


@pytest.mark.skipif(
    not (MANIFEST.exists() and COMMITTED_CSV.exists()),
    reason="Thiếu manifest hoặc CSV kết quả đã commit",
)
def test_committed_csv_reproduces_from_manifest() -> None:
    """Số đang dùng trong báo cáo phải tính lại được từ manifest đã commit."""
    expected = summarize_by_class(load_manifest(MANIFEST)).set_index("label")
    committed = pd.read_csv(COMMITTED_CSV).set_index("label")

    assert list(committed.index) == CLASS_ORDER
    assert int(committed["n"].sum()) == 21165
    for column in ("mean", "sd", "median", "q1", "q3", "min", "max", "auc_vs_rest"):
        pd.testing.assert_series_equal(
            committed[column].astype(float),
            expected[column].astype(float),
            check_names=False,
            rtol=0,
            atol=1e-6,
        )


@pytest.mark.skipif(
    not COMMITTED_JSON.exists(), reason="Thiếu JSON kết quả đã commit"
)
def test_committed_json_records_source_and_counts() -> None:
    """JSON phải trỏ đúng nguồn dữ liệu và tổng số ảnh để truy vết."""
    channels = json.loads(COMMITTED_JSON.read_text(encoding="utf-8"))

    assert channels["source"].endswith("splits/manifest.csv")
    assert channels["n_images"] == 21165
    assert channels["reference_label_for_iqr"] == "Normal"
    assert channels["color_mode_counts"]["Viral Pneumonia"] == {"L": 1205, "RGB": 140}
