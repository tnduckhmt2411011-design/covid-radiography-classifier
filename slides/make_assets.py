"""Chuẩn bị ảnh đứng trên slide: cắt ảnh val, dải mask, logo, ảnh chụp demo.

Mọi ảnh đều ghi rõ nguồn trong ``manifest.json`` và bị chặn nếu ``image_id``
thuộc split ``test`` (cổng H2 của báo cáo). Không ảnh nào được đổi nội dung; chỉ
cắt khung và đổi cỡ.

Cách chạy::

    python -m slides.make_assets
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "assets"
CXR_ROOT = Path(r"D:\cxr_data\COVID-19_Radiography_Dataset")
LOGO_SOURCE = Path(r"C:\Users\LENOVO\AppData\Local\Temp\opencode\ctut_logo_clean.png")
SPLIT_CSV = REPO / "splits" / "split_v1.csv"
MASK_DIR = REPO / "results" / "rq3_mask_check"
SCREENSHOT = Path(__file__).resolve().parent / "assets" / "screenshot_demo.png"

IMAGE_SIZE = 299


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_split() -> pd.DataFrame:
    if not SPLIT_CSV.exists():
        raise FileNotFoundError(f"thiếu {SPLIT_CSV}")
    return pd.read_csv(SPLIT_CSV)


def val_image(split: pd.DataFrame, image_id: str) -> Path:
    """Trả đường dẫn ảnh thuộc split ``val``; chặn nếu tên không khớp hoặc thuộc split khác."""
    row = split[split["image_id"] == image_id]
    if row.empty:
        raise LookupError(f"{image_id} không có trong splits/split_v1.csv")
    entry = row.iloc[0]
    if str(entry["split"]) != "val":
        raise PermissionError(f"{image_id} thuộc split '{entry['split']}', cổng H2 chỉ cho ảnh val")
    for path in CXR_ROOT.rglob(image_id):
        if path.parent.name == "images":
            return path
    raise FileNotFoundError(f"không thấy tệp ảnh của {image_id} trong {CXR_ROOT}")


def crop_square(source: Path, target: Path, size: int = IMAGE_SIZE) -> None:
    image = Image.open(source).convert("L")
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def mask_strip(source: Path, target: Path, width: int = 1100) -> None:
    """Cắt một dãng ba ô (gốc · chỉ phổi · ngoài phổi) từ ảnh kiểm tra mask."""
    image = Image.open(source).convert("L")
    strip = image.crop((0, 0, image.width, image.height // 20))
    scale = width / strip.width
    strip = strip.resize((width, int(strip.height * scale)), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    strip.save(target)


def build() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    split = load_split()
    manifest: dict[str, dict] = {}

    if LOGO_SOURCE.exists():
        target = OUT / "logo_ctut.png"
        shutil.copyfile(LOGO_SOURCE, target)
        manifest["logo_ctut.png"] = {"source": str(LOGO_SOURCE), "sha256": sha256(target), "kind": "logo"}
    else:
        raise FileNotFoundError(f"thiếu logo {LOGO_SOURCE}")

    cases = {
        "case_correct.png": ("COVID-1006.png", 0.9979, "COVID"),
        "case_error.png": ("Normal-9540.png", 0.9700, "Lung_Opacity"),
    }
    for target_name, (image_id, probability, predicted) in cases.items():
        source = val_image(split, image_id)
        crop_square(source, OUT / target_name)
        manifest[target_name] = {
            "source": str(source),
            "split": "val",
            "image_id": image_id,
            "sha256": sha256(OUT / target_name),
            "kind": "xray",
            "probability": probability,
            "predicted": predicted,
        }

    if SCREENSHOT.exists():
        manifest["screenshot_demo.png"] = {
            "source": "slides/capture_demo.py (Streamlit chạy thật trên 127.0.0.1:8501)",
            "image_id": "COVID-1006.png",
            "split": "val",
            "sha256": sha256(SCREENSHOT),
            "kind": "screenshot",
        }
    else:
        raise FileNotFoundError("thiếu slides/assets/screenshot_demo.png; chạy slides.capture_demo trước")

    samples = pd.read_csv(MASK_DIR / "mask_visual_check_samples.csv")
    if set(samples["split"]) != {"val"}:
        raise PermissionError("ảnh kiểm tra mask có mẫu không thuộc split val")
    for label in ("COVID", "Lung_Opacity", "Normal", "Viral_Pneumonia"):
        source = MASK_DIR / f"mask_visual_check_{label}.png"
        if not source.exists():
            raise FileNotFoundError(f"thiếu {source}")
        target = OUT / f"mask_strip_{label}.png"
        mask_strip(source, target)
        count = int((samples[samples["label"] == label.replace('_', ' ')]).shape[0])
        manifest[target.name] = {
            "source": str(source),
            "split": "val",
            "samples": count,
            "sha256": sha256(target),
            "kind": "mask",
        }

    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = build()
    for name, info in result.items():
        print(f"{name:26} {info['kind']:10} {info['source']}")
    sys.exit(0)
