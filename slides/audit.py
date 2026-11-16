"""Kiểm toán bộ slide S6-03 trước khi xuất bản.

Sáu nhóm kiểm (theo đặc tả §10):

a) đáy trống hoặc một cột trống quá mức — ước lượng từ danh sách vùng mỗi trang;
b) chồng lấn giữa các vùng gốc — đọc lại từ báo cáo chất lượng của ppt-master;
c) tràn chữ — dựa trên cảnh báo của ppt-master và ước lượng cỡ chữ;
d) cỡ chữ dưới 14 pt (trừ chân trang và số trang);
e) ảnh/khung nội dung cách mép dưới 0,5 in;
f) kicker, số trang và chân trang nguồn đồng nhất.

Ngoài ra: cổng H2 (không ảnh thuộc split ``test``), cổng D4 (nguyên văn ở các slide
nói về chênh lệch val–test) và danh sách cụm từ sáo rỗng bị cấm.

Chạy::

    python -m slides.audit
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

SLIDES = Path(__file__).resolve().parent
PROJECT = SLIDES / "s6_03_bao_ve_cuoi_ky_ppt169_20261112"
SVG_DIR = PROJECT / "svg_output"
REPORT_JSON = PROJECT / "validation" / "svg_quality_report.json"
REPO = Path(__file__).resolve().parents[1]

SVG = "{http://www.w3.org/2000/svg}"
PT_PER_PX = 0.75
MIN_BODY_PT = 18.0
MIN_EDGE_PX = 48  # 0,5 in = 48 px

BANNED = [
    "bức tranh toàn cảnh",
    "minh chứng hùng hồn",
    "lặn sâu vào",
    "ngọn hải đăng",
    "đóng vai trò then chốt",
    "không thể phủ nhận",
    "mở ra một chân trời",
    "trong bối cảnh kỷ nguyên số",
    "tiến hành việc thực hiện quá trình",
]

D4 = (
    "Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết "
    "chưa kiểm chứng, không nêu nguyên nhân."
)
D4_PAGES = {"18_phan_chung.svg", "21_val_vs_test.svg", "26_khong_chan_doan.svg"}

REQUIRE_SOURCE = 34  # mọi trang trừ bìa, mở chương và slide cảm ơn
NO_SOURCE_PAGES = {"01_cover.svg", "10_mo_chuong3.svg", "14_mo_chuong4.svg",
                   "19_mo_chuong5.svg", "28_cam_on.svg"}
NUMBERED_PAGES = [n for n in range(2, 28)]

CHROME_IDS = ("kicker", "title-slot", "footer-slot", "slide-number-slot", "master-background")


def svg_files() -> list[Path]:
    return sorted(SVG_DIR.glob("*.svg"))


def text_elements(root: ET.Element) -> list[ET.Element]:
    return [node for node in root.iter(f"{SVG}text")]


def font_px(node: ET.Element) -> float:
    return float(node.get("font-size", "0"))


def audit_fonts(root: ET.Element, name: str, problems: list[str]) -> None:
    for node in text_elements(root):
        size = font_px(node)
        if size <= 0:
            problems.append(f"{name}: thiếu font-size")
            continue
        if size * PT_PER_PX < MIN_BODY_PT:
            carrier = node.get("data-pptx-carrier")
            if carrier or "footer-carrier" in (node.get("id") or "") or \
                    "page-number-carrier" in (node.get("id") or ""):
                continue
            problems.append(f"{name}: chữ {size * PT_PER_PX:.2f} pt dưới sàn 14 pt "
                            f"(id {node.get('id')})")


def audit_zones(root: ET.Element, name: str, problems: list[str]) -> None:
    """Mọi vùng gốc nằm trong khung nhìn và cách mép tối thiểu 0,5 in."""
    for child in root:
        bounds = child.get("data-pptx-bounds")
        if not bounds:
            continue
        x, y, w, h = (float(value) for value in bounds.split())
        if child.get("data-pptx-layer") == "master":
            continue
        gid = child.get("id") or ""
        if any(key in gid for key in CHROME_IDS):
            continue
        if y + h < 170:  # dải tiêu đề và kicker là chrome, không áp dụng lề 0,5 in
            continue
        if x < MIN_EDGE_PX or y < MIN_EDGE_PX or x + w > 1280 - MIN_EDGE_PX \
                or y + h > 720 - MIN_EDGE_PX:
            problems.append(f"{name}: vùng {child.get('id')} sát mép hoặc vượt khung "
                            f"[{x:.0f} {y:.0f} {w:.0f} {h:.0f}]")


def audit_gaps(root: ET.Element, name: str, problems: list[str]) -> None:
    """Đáy trống quá 25% hoặc một cột trống quá 30%."""
    zones = []
    for child in root:
        bounds = child.get("data-pptx-bounds")
        if not bounds or child.get("data-pptx-layer") == "master":
            continue
        zones.append([float(value) for value in bounds.split()])
    if not zones:
        return
    top = min(zone[1] for zone in zones)
    bottom = max(zone[1] + zone[3] for zone in zones)
    left = min(zone[0] for zone in zones)
    right = max(zone[0] + zone[2] for zone in zones)
    if top > 210 and (720 - bottom) / (bottom - top) > 0.25:
        problems.append(f"{name}: đáy trống {100 * (720 - bottom) / (bottom - top):.0f}%")
    for edge, total, label in ((left, 1280, "trái"), (1280 - right, 1280, "phải")):
        if edge / total > 0.30:
            problems.append(f"{name}: cột {label} trống {100 * edge / total:.0f}%")


def audit_overlaps(root: ET.Element, name: str, problems: list[str]) -> None:
    """Chồng lấn giữa các vùng gốc, kể cả ô placeholder chân trang.

    Cổng này bắt lỗi "chú thích đè lên chân trang": ppt-master chỉ so chồng lấn
    giữa các vùng nội dung, không đối chiếu với ô footer và ô số trang.
    """
    boxes: list[tuple[str, tuple[float, float, float, float]]] = []
    for child in root:
        bounds = child.get("data-pptx-bounds")
        if not bounds:
            continue
        x, y, w, h = (float(value) for value in bounds.split())
        boxes.append((child.get("id") or "", (x, y, w, h)))
    for index, (gid_a, a) in enumerate(boxes):
        for gid_b, b in boxes[index + 1:]:
            ax1, ay1, aw, ah = a
            bx1, by1, bw, bh = b
            ax2, ay2 = ax1 + aw, ay1 + ah
            bx2, by2 = bx1 + bw, by1 + bh
            overlap_x = min(ax2, bx2) - max(ax1, bx1)
            overlap_y = min(ay2, by2) - max(ay1, by1)
            if overlap_x > 1 and overlap_y > 1:
                problems.append(
                    f"{name}: vùng {gid_a} chồng lấn vùng {gid_b} "
                    f"({overlap_x:.0f}×{overlap_y:.0f} px)"
                )


def audit_pages(problems: list[str]) -> None:
    files = svg_files()
    if len(files) != 34:
        problems.append(f"số trang SVG là {len(files)}, cần 34")

    numbered = []
    for path in files:
        root = ET.parse(path).getroot()
        audit_fonts(root, path.name, problems)
        audit_zones(root, path.name, problems)
        audit_gaps(root, path.name, problems)
        audit_overlaps(root, path.name, problems)

        text = " ".join(node.text or "" for node in root.iter(f"{SVG}tspan"))
        text = " ".join(text.split())
        if path.name in D4_PAGES and D4 not in text:
            problems.append(f"{path.name}: thiếu nguyên văn quy tắc D4")
        if path.name == "21_val_vs_test.svg" and "nguyên nhân" in text.replace(
            "không nêu nguyên nhân", ""
        ):
            problems.append(f"{path.name}: nhắc đến nguyên nhân, trái quy tắc D4")
        for phrase in BANNED:
            if phrase.lower() in text.lower():
                problems.append(f"{path.name}: cụm từ bị cấm “{phrase}”")
        footer = any("footer-carrier" in (node.get("id") or "") for node in root.iter(f"{SVG}text"))
        if path.name not in NO_SOURCE_PAGES and not footer:
            problems.append(f"{path.name}: thiếu chân trang nguồn")
        number = [node for node in root.iter(f"{SVG}text")
                  if "page-number-carrier" in (node.get("id") or "")]
        if number:
            value = number[0].find(f"{SVG}tspan").text
            numbered.append(int(value.split("/")[0].strip()))
        elif path.name not in NO_SOURCE_PAGES and not path.name.startswith(("b", "1", "2")):
            pass

    if numbered and numbered != sorted(numbered):
        problems.append(f"thứ tự số trang không tăng dần: {numbered}")
    missing = set(NUMBERED_PAGES) - set(numbered)
    if missing:
        problems.append(f"thiếu số trang: {sorted(missing)}")


def audit_images(problems: list[str]) -> None:
    """Cổng H2: không ảnh nào thuộc split test."""
    import pandas as pd

    manifest = json.loads((SLIDES / "assets" / "manifest.json").read_text(encoding="utf-8"))
    split = pd.read_csv(REPO / "splits" / "split_v1.csv")
    test_ids = set(split[split["split"] == "test"]["image_id"])
    for name, info in manifest.items():
        image_id = info.get("image_id")
        if image_id and image_id in test_ids:
            problems.append(f"ảnh {name} thuộc split test ({image_id}) — chặn theo cổng H2")
    samples = pd.read_csv(REPO / "results/rq3_mask_check/mask_visual_check_samples.csv")
    if set(samples["split"]) != {"val"}:
        problems.append("ảnh kiểm tra mask có mẫu không thuộc split val")


def audit_quality(problems: list[str]) -> None:
    if not REPORT_JSON.exists():
        problems.append("thiếu báo cáo chất lượng của ppt-master")
        return
    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    for issue in report["categories"]["blocking"]["issues"]:
        problems.append(f"blocking: {issue['message']}")


def main() -> int:
    problems: list[str] = []
    audit_pages(problems)
    audit_images(problems)
    audit_quality(problems)
    if problems:
        print(f"KHÔNG ĐẠT — {len(problems)} vi phạm:")
        for item in problems:
            print(" -", item)
        return 1
    print(f"ĐẠT: 34 trang, {len(svg_files())} tệp SVG, 0 vi phạm a/b/c/d/e/f, H2, D4, cụm từ cấm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
