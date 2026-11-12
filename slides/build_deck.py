"""Ráp 34 trang S6-03: sinh SVG, sao ảnh, gọi kiểm toán và xuất PPTX/PDF.

Cách chạy::

    python -m slides.build_deck            # toàn bộ 28 + 6 trang
    python -m slides.build_deck --svg-only # chỉ sinh SVG và sao ảnh
    python -m slides.build_deck --only act1 # chỉ một nhóm trang (soạn/kiểm nhanh)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SLIDES = Path(__file__).resolve().parent
PROJECT = SLIDES / "s6_03_bao_ve_cuoi_ky_ppt169_20261112"
SVG_OUT = PROJECT / "svg_output"
IMAGES = PROJECT / "images"
EXPORTS = PROJECT / "exports"

FILES = ["charts"] + [f"{name}.png" for name in sorted(p.stem for p in (SLIDES / "figures").glob("*.png"))]


def stage(pages) -> list[Path]:
    """Sao toàn bộ ảnh cần dùng vào ``images/`` của dự án ppt-master."""
    written = []
    for source in sorted((SLIDES / "figures").glob("*.png")):
        shutil.copyfile(source, IMAGES / source.name)
        written.append(source.name)
    for source in sorted((SLIDES / "assets").glob("*.png")):
        shutil.copyfile(source, IMAGES / source.name)
        written.append(source.name)
    for page in pages:
        page.write(SVG_OUT)
        written.append(page.filename)
    return written


def clean_svg() -> None:
    if SVG_OUT.exists():
        for path in SVG_OUT.glob("*.svg"):
            path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--svg-only", action="store_true")
    parser.add_argument("--only", choices=["act1", "act2", "act3", "backup"], default=None)
    args = parser.parse_args()

    from . import slides_act1

    groups = {
        "act1": slides_act1.pages,
    }
    available = {"act1": True}
    for name in ("act2", "act3", "backup"):
        try:
            module = __import__(f"slides.slides_{name}", fromlist=["pages"])
            groups[name] = module.pages
            available[name] = True
        except ImportError:
            available[name] = False
    if args.only is None and not all(available.values()):
        missing = [name for name, ok in available.items() if not ok]
        raise SystemExit(f"thiếu nhóm trang {missing}; chạy từng nhóm bằng --only")
    pages = []
    for name in (["act1", "act2", "act3", "backup"] if args.only is None else [args.only]):
        pages.extend(groups[name]())

    IMAGES.mkdir(parents=True, exist_ok=True)
    clean_svg()
    written = stage(pages)
    print(f"đã sinh {len(pages)} trang SVG vào {SVG_OUT}")
    print(f"đã sao {len([w for w in written if w.endswith('png')])} ảnh vào {IMAGES}")

    if args.svg_only:
        return 0

    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
