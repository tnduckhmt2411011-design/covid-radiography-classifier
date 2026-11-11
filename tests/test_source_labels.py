"""Kiểm thử cho S6-01 (tách ảnh lớp Normal theo nguồn gốc)."""

from __future__ import annotations

import csv
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from src.source_labels import (
    build,
    parse_source_labels,
    read_labels,
    source_counts,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LABELS_CSV = REPO_ROOT / "results" / "eda" / "normal_source_labels.csv"
SPLIT_CSV = REPO_ROOT / "splits" / "split_v1.csv"

EXPECTED_COUNTS = {"rsna": 8851, "mooney": 1341}


def _write_fake_xlsx(path: Path, rows: list[tuple[str, str]]) -> Path:
    """Tạo một tệp xlsx tối giản gồm hai cột FILE NAME và URL cho kiểm thử parser."""
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    header = ["FILE NAME", "FORMAT", "SIZE", "URL"]
    # Mỗi dòng dữ liệu chỉ cần hai chuỗi: tên tệp (cột A) và URL (cột D).
    data_strings = []
    for name, url in rows:
        data_strings.append(name)
        data_strings.append(url)
    all_strings = header + data_strings

    shared_items = "".join(f"<si><t>{text}</t></si>" for text in all_strings)
    shared = (
        f'<?xml version="1.0"?><sst xmlns="{ns}" count="{len(all_strings)}" '
        f'uniqueCount="{len(all_strings)}">{shared_items}</sst>'
    )

    header_cells = "".join(
        f'<c r="{column}1" t="s"><v>{index}</v></c>'
        for index, column in enumerate(["A", "B", "C", "D"])
    )
    body_cells = []
    for offset in range(len(rows)):
        row_index = offset + 2
        name_index = len(header) + offset * 2
        url_index = name_index + 1
        body_cells.append((row_index, name_index, url_index))

    sheet = (
        f'<?xml version="1.0"?><worksheet xmlns="{ns}"><sheetData>'
        f"<row>{header_cells}</row>"
        + "".join(
            f'<row><c r="A{row_index}" t="s"><v>{name_index}</v></c>'
            f'<c r="D{row_index}" t="s"><v>{url_index}</v></c></row>'
            for row_index, name_index, url_index in body_cells
        )
        + "</sheetData></worksheet>"
    )

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/sharedStrings.xml", shared)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return path


def test_parse_source_labels_separates_two_sources(tmp_path: Path) -> None:
    """Parser phải đổi NORMAL-<n> thành Normal-<n>.png và gán đúng nguồn."""
    xlsx = _write_fake_xlsx(
        tmp_path / "Normal.metadata.xlsx",
        [
            ("NORMAL-1", "https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data"),
            ("NORMAL-2", "https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia"),
            ("NORMAL-3", "https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia"),
        ],
    )

    labels = parse_source_labels(xlsx)

    assert labels == {
        "Normal-1.png": "rsna",
        "Normal-2.png": "mooney",
        "Normal-3.png": "mooney",
    }
    assert source_counts(labels) == {"rsna": 1, "mooney": 2}


def test_parse_source_labels_rejects_unexpected_name(tmp_path: Path) -> None:
    """Tên tệp không đúng dạng NORMAL-<n> phải làm parser dừng."""
    xlsx = _write_fake_xlsx(
        tmp_path / "Normal.metadata.xlsx",
        [("NORMAL-1", "https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data"),
         ("CXR-9", "https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia")],
    )
    with pytest.raises(ValueError):
        parse_source_labels(xlsx)


def test_build_writes_sorted_csv(tmp_path: Path) -> None:
    """CSV ghi ra phải có hai cột và các dòng theo thứ tự số của image_id."""
    xlsx = _write_fake_xlsx(
        tmp_path / "Normal.metadata.xlsx",
        [
            ("NORMAL-10", "https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia"),
            ("NORMAL-2", "https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data"),
        ],
    )
    out = tmp_path / "labels.csv"

    info = build(xlsx, out)

    assert out.exists()
    assert info["n"] == 2
    assert info["counts"] == {"mooney": 1, "rsna": 1}
    with out.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    # Hang tieu de roi den Normal-2 truoc Normal-10 (theo so, khong theo chu).
    assert rows[1:] == [["Normal-2.png", "rsna"], ["Normal-10.png", "mooney"]]


@pytest.mark.skipif(not LABELS_CSV.exists(), reason="Thieu CSV nguon anh da commit")
def test_committed_labels_match_split() -> None:
    """CSV đã commit phải đủ 10.192 ảnh của lớp Normal và khớp với split_v1.csv."""
    labels = read_labels(LABELS_CSV)
    assert source_counts(labels) == EXPECTED_COUNTS

    split = pd.read_csv(SPLIT_CSV)
    normal_ids = set(split.loc[split["label"] == "Normal", "image_id"])
    assert set(labels) == normal_ids

    # Moi anh thuoc dung mot nguon, khong co gia tri la.
    assert set(source_counts(labels)) == {"rsna", "mooney"}


@pytest.mark.skipif(not (LABELS_CSV.exists() and SPLIT_CSV.exists()), reason="Thieu CSV")
def test_mooney_images_all_in_one_kaggle_source() -> None:
    """Nhóm Mooney phải chiếm 13,2% lớp Normal, khớp với hồ sơ nguồn gốc."""
    labels = read_labels(LABELS_CSV)
    share = source_counts(labels)["mooney"] / len(labels)
    assert share == pytest.approx(1341 / 10192, abs=1e-4)
