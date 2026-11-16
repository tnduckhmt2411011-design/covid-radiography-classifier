"""Xuất deck: kiểm toán → PPTX → vá phông chữ → PDF (WPS) → ảnh PNG để duyệt.

Chạy::

    python -m slides.export                 # toàn bộ pipeline
    python -m slides.export --skip-render   # dừng ở PPTX/PDF

WPS mở bằng COM ``Kwpp.Application`` (máy dựng bài không có Microsoft PowerPoint).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SLIDES = Path(__file__).resolve().parent
PROJECT = SLIDES / "s6_03_bao_ve_cuoi_ky_ppt169_20261112"
SKILL = Path(r"D:\Tools\ppt-master\skills\ppt-master")
DECK_PPTX = SLIDES / "deck_bao_ve.pptx"
DECK_PDF = SLIDES / "deck_bao_ve.pdf"
PNG_DIR = SLIDES / "render"
TMP = Path(os.environ.get("TEMP", r"C:\Users\LENOVO\AppData\Local\Temp")) / "opencode"

FONT_FIXES = [
    ('typeface="+mj-lt"', 'typeface="Segoe UI"'),
    ('typeface="+mn-lt"', 'typeface="Segoe UI"'),
    ('typeface="+mj-ea"', 'typeface="Segoe UI"'),
    ('typeface="+mn-ea"', 'typeface="Segoe UI"'),
    ('typeface="+mj-cs"', 'typeface="Segoe UI"'),
    ('typeface="+mn-cs"', 'typeface="Segoe UI"'),
]


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("$", " ".join(str(part) for part in command))
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", **kwargs)


def check() -> int:
    return run([sys.executable, str(SKILL / "scripts/svg_quality_checker.py"), str(PROJECT),
                "--quick-generate", "--canonical-authoring", "--stage", "final", "--json"]).returncode


def latest_export() -> Path:
    exports = sorted((PROJECT / "exports").glob("*.pptx"))
    if not exports:
        raise FileNotFoundError("không thấy PPTX trong exports/")
    return exports[-1]


def to_pptx() -> Path:
    result = run([sys.executable, str(SKILL / "scripts/svg_to_pptx.py"), str(PROJECT),
                  "--quick-generate", "--no-notes"])
    print(result.stdout[-1500:])
    if result.returncode != 0:
        raise SystemExit(result.stdout[-2000:] + result.stderr[-2000:])
    source = latest_export()
    patch_fonts(source, DECK_PPTX)
    return DECK_PPTX


def patch_fonts(source: Path, target: Path) -> None:
    """Thay tham chiếu phông của theme bằng tên phông tường minh (WPS bỏ qua +mj-lt)."""
    temporary = target.with_suffix(".tmp")
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                for old, new in FONT_FIXES:
                    text = text.replace(old, new)
                data = text.encode("utf-8")
            zout.writestr(item, data)
    os.replace(temporary, target)
    print("đã vá phông:", target)


def to_pdf(pptx: Path, pdf: Path) -> None:
    script = TMP / "export_pdf.ps1"
    TMP.mkdir(parents=True, exist_ok=True)
    script.write_text(
        "$pptx = '%s'\n$pdf = '%s'\n$wps = New-Object -ComObject Kwpp.Application\n"
        "$wps.Visible = $true\n$pres = $wps.Presentations.Open($pptx, $true, $false, $false)\n"
        "$pres.SaveAs($pdf, 32)\n$pres.Close()\n$wps.Quit()\n"
        "Write-Output ('pdf size: ' + (Get-Item $pdf).Length)\n" % (pptx, pdf),
        encoding="utf-8",
    )
    result = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)])
    print(result.stdout[-800:])
    if not pdf.exists():
        raise SystemExit("WPS không xuất được PDF: " + result.stderr[-500:])


def to_png(pdf: Path, out_dir: Path, *, dpi: int = 110) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    code = (
        "import pymupdf, pathlib\n"
        f"pdf = {str(pdf)!r}\n"
        f"out_dir = pathlib.Path({str(out_dir)!r})\n"
        f"doc = pymupdf.open(pdf)\n"
        f"for i, page in enumerate(doc, 1):\n"
        f"    page.get_pixmap(dpi={dpi}).save(str(out_dir / ('p%02d.png' % i)))\n"
        "print('da ve', len(doc), 'trang')\n"
    )
    result = run([sys.executable, "-c", code])
    print(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()

    status = check()
    if status != 0:
        raise SystemExit("kiểm toán SVG chưa đạt (xuất PDF dừng lại)")
    pptx = to_pptx()
    to_pdf(pptx, DECK_PDF)
    if not args.skip_render:
        to_png(DECK_PDF, PNG_DIR, dpi=args.dpi)
    return 0


if __name__ == "__main__":
    sys.exit(main())
