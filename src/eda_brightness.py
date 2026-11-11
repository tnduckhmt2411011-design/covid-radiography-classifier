"""Module eda_brightness.py

Trách nhiệm: tổng hợp độ sáng trung bình của từng lớp cho mục 2.2 của báo cáo.

Nguồn số liệu duy nhất là ``splits/manifest.csv`` — tệp đã commit, mỗi dòng một ảnh, cột
``mean_brightness`` do ``notebooks/01_download_and_eda.ipynb`` tính bằng trung bình mảng điểm ảnh
của tệp gốc (thang 0–255). Toàn bộ 140 ảnh ở hệ màu ``RGB`` đều có R = G = B nên giá trị trung
bình ba kênh trùng với trung bình ảnh xám.

Module không đọc ảnh, không đọc riêng tập test, không huấn luyện mô hình. Đầu ra:

- ``results/eda/brightness_by_class.csv``: thống kê mô tả theo lớp, có một dòng cho mỗi lớp.
- ``results/eda/brightness_channels.json``: các số dẫn xuất dùng trong mục 2.2 (AUC của lớp
  COVID so với ba lớp còn lại, tỉ lệ ảnh nằm trong khoảng tứ phân vị của lớp Normal, số ảnh
  theo hệ màu).

Cột ``auc_vs_rest`` là xác suất một ảnh của lớp đang xét sáng hơn một ảnh ngẫu nhiên thuộc ba
lớp còn lại. Giá trị dưới 0,5 nghĩa là lớp đó tối hơn phần còn lại; đó không phải "kém hơn ngẫu
nhiên" mà chỉ là chiều của phép so sánh.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import pandas as pd

# Thứ tự lớp giữ nguyên như bảng trong báo cáo và ma trận nhầm lẫn.
CLASS_ORDER: List[str] = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]

REQUIRED_COLUMNS = ["image_id", "label", "mean_brightness", "color_mode"]

DEFAULT_MANIFEST = Path("splits") / "manifest.csv"
DEFAULT_OUT_DIR = Path("results") / "eda"


def load_manifest(path: Path) -> pd.DataFrame:
    """Đọc manifest và kiểm các cột cần thiết cùng bốn nhãn lớp."""
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Manifest thiếu cột: {', '.join(missing)}")
    unknown = sorted(set(df["label"]) - set(CLASS_ORDER))
    if unknown:
        raise ValueError(f"Manifest có nhãn lạ: {', '.join(unknown)}")
    if df["mean_brightness"].isna().any():
        raise ValueError("Manifest có giá trị mean_brightness rỗng.")
    return df


def summarize_by_class(df: pd.DataFrame) -> pd.DataFrame:
    """Thống kê độ sáng theo lớp: n, trung bình, độ lệch chuẩn, trung vị, tứ phân vị, min, max, AUC.

    Cột ``auc_distance_to_half`` là khoảng cách từ AUC đến 0,5, dùng để so mức tách lớp giữa các
    lớp mà không phải diễn giải chiều của phép so sánh.
    """
    rows: List[Dict[str, object]] = []
    for label in CLASS_ORDER:
        values = df.loc[df["label"] == label, "mean_brightness"].to_numpy(dtype=float)
        if values.size == 0:
            raise ValueError(f"Lớp {label} không có ảnh nào trong manifest.")
        rows.append(
            {
                "label": label,
                "n": int(values.size),
                "mean": float(values.mean()),
                "sd": float(values.std(ddof=1)),
                "median": float(pd.Series(values).median()),
                "q1": float(pd.Series(values).quantile(0.25)),
                "q3": float(pd.Series(values).quantile(0.75)),
                "min": float(values.min()),
                "max": float(values.max()),
                "auc_vs_rest": auc_against_rest(df, label),
                "auc_distance_to_half": abs(auc_against_rest(df, label) - 0.5),
            }
        )
    return pd.DataFrame(rows)


def auc_against_rest(df: pd.DataFrame, label: str) -> float:
    """AUC của độ sáng khi tách ``label`` khỏi ba lớp còn lại, tính bằng hạng trung bình (có xử lý đồng hạng)."""
    scores = df["mean_brightness"].to_numpy(dtype=float)
    is_positive = (df["label"] == label).to_numpy()
    n_pos = int(is_positive.sum())
    n_neg = int((~is_positive).size - n_pos)
    if n_pos == 0 or n_neg == 0:
        raise ValueError("Cần ít nhất một ảnh mỗi phía để tính AUC.")

    ranks = pd.Series(scores).rank(method="average").to_numpy(dtype=float)
    rank_sum = ranks[is_positive].sum()
    return float((rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def share_in_reference_iqr(df: pd.DataFrame, reference: str) -> float:
    """Tỉ lệ toàn bộ ảnh có độ sáng nằm trong khoảng tứ phân vị của lớp ``reference``."""
    ref = df.loc[df["label"] == reference, "mean_brightness"]
    q1, q3 = ref.quantile(0.25), ref.quantile(0.75)
    inside = df["mean_brightness"].between(q1, q3, inclusive="both")
    return float(inside.mean())


def color_mode_counts(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """Số ảnh theo hệ màu của từng lớp, ví dụ ``{"Viral Pneumonia": {"L": 1205, "RGB": 140}}``."""
    counts: Dict[str, Dict[str, int]] = {}
    for label in CLASS_ORDER:
        subset = df.loc[df["label"] == label, "color_mode"].value_counts()
        counts[label] = {str(k): int(v) for k, v in subset.items()}
    return counts


def build_outputs(manifest_path: Path, out_dir: Path) -> Dict[str, Path]:
    """Ghi hai tệp kết quả và trả về đường dẫn của chúng."""
    df = load_manifest(manifest_path)
    summary = summarize_by_class(df)

    covid = summary.loc[summary["label"] == "COVID"].iloc[0]
    channels = {
        "source": manifest_path.as_posix(),
        "n_images": int(len(df)),
        "brightness_scale": "0-255, trung bình mảng điểm ảnh của tệp gốc",
        "auc_covid_vs_rest": round(float(covid["auc_vs_rest"]), 4),
        "auc_note": "AUC là xác suất ảnh của lớp sáng hơn một ảnh ngẫu nhiên của ba lớp còn lại",
        "reference_label_for_iqr": "Normal",
        "share_in_normal_iqr": round(share_in_reference_iqr(df, "Normal"), 4),
        "color_mode_counts": color_mode_counts(df),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "brightness_by_class.csv"
    channels_path = out_dir / "brightness_channels.json"

    summary.round(6).to_csv(summary_path, index=False)
    channels_path.write_text(
        json.dumps(channels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"brightness_by_class.csv": summary_path, "brightness_channels.json": channels_path}


def format_vn(value: float, decimals: int = 1) -> str:
    """Định dạng số kiểu Việt Nam: dấu chấm ngăn cách hàng nghìn, dấu phẩy ngăn cách thập phân.

    Chỉ dùng một chữ số thập phân cho độ sáng vì một số trung vị và tứ phân vị rơi đúng mốc
    ,xx5 (ví dụ 142,595), khi đó làm tròn hai chữ số sẽ phụ thuộc quy ước và dễ bị đọc sai.
    """
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def format_markdown_table(summary: pd.DataFrame) -> str:
    """Kết xuất bảng Markdown để dán vào báo cáo, độ sáng một chữ số thập phân, AUC bốn."""
    lines = [
        "| Lớp | n | Trung bình ± SD | Trung vị | Khoảng tứ phân vị | Nhỏ nhất | AUC so với ba lớp còn lại |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['label']} | {format_vn(row['n'], 0)} | "
            f"{format_vn(row['mean'])} ± {format_vn(row['sd'])} | {format_vn(row['median'])} | "
            f"{format_vn(row['q1'])}–{format_vn(row['q3'])} | {format_vn(row['min'])} | "
            f"{format_vn(row['auc_vs_rest'], 4)} |"
        )
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Điểm vào CLI: đọc manifest, ghi kết quả và in bảng Markdown."""
    parser = argparse.ArgumentParser(description="Thống kê độ sáng theo lớp cho mục 2.2.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args(argv)

    written = build_outputs(args.manifest, args.out_dir)
    summary = summarize_by_class(load_manifest(args.manifest))

    print(format_markdown_table(summary))
    for name, path in written.items():
        print(f"Đã ghi {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
