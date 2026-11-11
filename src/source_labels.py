"""Tách ảnh lớp Normal theo nguồn gốc từ tệp metadata của bộ dữ liệu.

Bộ COVID-19 Radiography Database gộp lớp Normal từ hai nguồn: 8.851 ảnh từ cuộc thi
RSNA Pneumonia Detection Challenge và 1.341 ảnh từ bộ `Chest X-Ray Images (Pneumonia)`
của Paul Mooney, và nguồn của từng ảnh chỉ ghi trong `Normal.metadata.xlsx` ở cột `URL`.
Tệp xlsx không nằm trong repo (nguyên tắc không lưu dữ liệu gốc), nên module này đọc nó
khi đã tải về và ghi ra một tệp CSV **được commit**, để mọi số liệu phân tích theo nguồn
trong báo cáo truy vết được từ repo.

Định dạng tệp sinh ra: `results/eda/normal_source_labels.csv`, hai cột `image_id` và
`source`, 10.192 dòng khớp với `splits/split_v1.csv`. Khóa `image_id` dùng cùng dạng với
split (`Normal-1.png`), khác với cột `FILE NAME` của tệp xlsx (`NORMAL-1`).

Module đọc xlsx bằng thư viện chuẩn (zipfile và xml.etree) nên không cần openpyxl, và
không đọc ảnh, không đọc tệp split `test`.

Chạy: ``python -m src.source_labels --xlsx <đường/dẫn/Normal.metadata.xlsx>``
"""

from __future__ import annotations

import argparse
import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
DEFAULT_OUT = Path("results") / "eda" / "normal_source_labels.csv"
SOURCE_OF_INTEREST = "mooney"
_MOONEY_MARKER = "paultimothymooney"
_NORMAL_NAME = re.compile(r"^NORMAL-(\d+)$")


def _read_xlsx_rows(path: Path) -> List[Dict[str, str]]:
    """Đọc sheet đầu tiên của tệp xlsx, trả về list các dict theo cột A, B, C, D."""
    with zipfile.ZipFile(path) as archive:
        shared: List[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(f"{NS}si"):
                shared.append("".join(node.text or "" for node in item.iter(f"{NS}t")))
        sheet_names = [n for n in archive.namelist() if n.startswith("xl/worksheets/sheet")]
        if not sheet_names:
            raise ValueError(f"{path} khong co worksheet")
        root = ET.fromstring(archive.read(sheet_names[0]))

    rows: List[Dict[str, str]] = []
    for row in root.iter(f"{NS}row"):
        cells: Dict[str, str] = {}
        for cell in row.findall(f"{NS}c"):
            column = "".join(ch for ch in cell.get("r", "") if ch.isalpha())
            if cell.get("t") == "s":
                index = cell.find(f"{NS}v")
                cells[column] = shared[int(index.text)] if index is not None else ""
            else:
                value = cell.find(f"{NS}v")
                cells[column] = value.text if value is not None else ""
        rows.append(cells)
    return rows


def parse_source_labels(xlsx_path: Path) -> Dict[str, str]:
    """Đọc `Normal.metadata.xlsx` và trả về map ``image_id`` -> ``rsna`` hoặc ``mooney``."""
    rows = _read_xlsx_rows(xlsx_path)
    if not rows:
        raise ValueError(f"{xlsx_path} khong co du lieu")

    labels: Dict[str, str] = {}
    for row in rows[1:]:
        file_name = (row.get("A") or "").strip()
        url = (row.get("D") or "").strip()
        match = _NORMAL_NAME.match(file_name)
        if match is None:
            raise ValueError(f"Dang ten FILE NAME khong mong doi: {file_name!r}")
        image_id = f"Normal-{match.group(1)}.png"
        if image_id in labels:
            raise ValueError(f"Trung image_id sau khi doi dang ten: {image_id}")
        labels[image_id] = SOURCE_OF_INTEREST if _MOONEY_MARKER in url else "rsna"
    return labels


def write_labels(labels: Dict[str, str], out_path: Path) -> Path:
    """Ghi map nguồn ra CSV, sắp theo image_id để dễ so sánh giữa các lần chạy."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["image_id", "source"])
        for image_id in sorted(labels, key=lambda s: int(s.split("-")[1].split(".")[0])):
            writer.writerow([image_id, labels[image_id]])
    return out_path


def read_labels(path: Path) -> Dict[str, str]:
    """Đọc lại CSV đã ghi, trả về map ``image_id`` -> ``source``."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["image_id"]: row["source"] for row in rows}


def source_counts(labels: Dict[str, str]) -> Dict[str, int]:
    """Đếm số ảnh theo nguồn."""
    return dict(Counter(labels.values()))


def build(xlsx_path: Path, out_path: Path = DEFAULT_OUT) -> Dict[str, object]:
    """Đọc tệp metadata, ghi CSV và trả về thông tin dùng cho báo cáo."""
    labels = parse_source_labels(xlsx_path)
    path = write_labels(labels, out_path)
    return {"csv": path.as_posix(), "n": len(labels), "counts": source_counts(labels)}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Điểm vào CLI."""
    parser = argparse.ArgumentParser(description="Tach anh lop Normal theo nguon tu metadata.")
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    info = build(args.xlsx, args.out)
    print(f"Da ghi {info['csv']}")
    print(f"So anh: {info['n']} | theo nguon: {info['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
