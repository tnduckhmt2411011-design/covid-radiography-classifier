import sys
from pathlib import Path
from collections import Counter
import json
import pandas as pd
from PIL import Image

print("=== BẮT ĐẦU ĐO KÍCH THƯỚC TOÀN BỘ MASK TRÊN KAGGLE ===")

# 1. Định vị DATA_ROOT
possible_roots = [
    Path("/kaggle/input/datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset"),
    Path("/kaggle/input/datasets/tawsifurrahman/covid19-radiography-database"),
    Path("/kaggle/input/covid19-radiography-database/COVID-19_Radiography_Dataset"),
    Path("/kaggle/input/covid19-radiography-database"),
]

data_root = None
for r in possible_roots:
    if r.exists() and (r / "COVID" / "masks").exists():
        data_root = r
        break

if data_root is None:
    for p in Path("/kaggle/input").rglob("masks"):
        if p.is_dir() and p.parent.name == "COVID":
            data_root = p.parent.parent
            break

print(f"DATA_ROOT = {data_root}")

# 2. Định vị manifest.csv
manifest_path = None
if Path("splits/manifest.csv").exists():
    manifest_path = Path("splits/manifest.csv")
elif Path("manifest.csv").exists():
    manifest_path = Path("manifest.csv")
else:
    for p in Path("/kaggle/input").rglob("manifest.csv"):
        manifest_path = p
        break

print(f"Đọc manifest từ: {manifest_path}")

df = pd.read_csv(manifest_path)
print("Tổng số dòng trong manifest:", len(df))
print("rel_mask_path head(3):", df["rel_mask_path"].head(3).tolist())

# Kiểm tra đường dẫn 3 mask đầu
for p in df["rel_mask_path"].head(3):
    fp = data_root / p
    print(f"Kiểm tra file: {fp} -> exists={fp.exists()}")

# Đo kích thước mask theo đúng đoạn code của user
sizes = Counter(Image.open(f"{data_root}/{p}").size for p in df["rel_mask_path"])
print("Kết quả Counter sizes:", sizes)

# Chi tiết theo lớp
sizes_by_class = {}
for idx, row in df.iterrows():
    p = row["rel_mask_path"]
    lbl = row["label"]
    sz = Image.open(f"{data_root}/{p}").size
    if lbl not in sizes_by_class:
        sizes_by_class[lbl] = Counter()
    sizes_by_class[lbl][sz] += 1

print("\n=== TỔNG KẾT KÍCH THƯỚC MASK ===")
print(f"Tổng số mask đã đo: {sum(sizes.values())}")
print(f"Số kích thước khác nhau: {len(sizes)}")
for sz, cnt in sizes.items():
    print(f" - Kích thước {sz}: {cnt} mask")

print("\nPhân bố theo từng lớp:")
for lbl, c in sorted(sizes_by_class.items()):
    print(f" - {lbl}: {dict(c)}")

# Lưu báo cáo JSON ra /kaggle/working/mask_sizes_report.json
report = {
    "data_root": str(data_root),
    "manifest_path": str(manifest_path),
    "total_masks": sum(sizes.values()),
    "unique_sizes_count": len(sizes),
    "sizes": {f"{w}x{h}": cnt for (w, h), cnt in sizes.items()},
    "sizes_by_class": {
        lbl: {f"{w}x{h}": cnt for (w, h), cnt in c.items()}
        for lbl, c in sizes_by_class.items()
    }
}

with open("/kaggle/working/mask_sizes_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("ĐÃ HOÀN TẤT VÀ LƯU BÁO CÁO mask_sizes_report.json")
