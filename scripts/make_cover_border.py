"""Sinh anh khung trang bia cho bao cao (khung kep + hoa van 4 goc).

Chay: .venv-demo/Scripts/python.exe scripts/make_cover_border.py
Ra: report/figures/khung_trang_bia.png (A4 dung, trong den trang, ~300 DPI).

Ve lai bang cu be: khung hai duong kep (net dam ngoai, net mong trong) va hoa van
4 goc gom hai thanh leo duong cheo, xoay oc o dau thanh, la va bong hoa mini.
Hoa van ve mot lan o goc trai-tren roi lat sang ba goc con lai nen doi xung.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report/figures/khung_trang_bia.png"

# A4 dung ti le 210:297; 300 DPI -> 2480 x 3508
W, H = 2480, 3508
MARGIN = 130          # le khung ngoai
FRAME_OUT_W = 12      # net dam ngoai
FRAME_IN_GAP = 95     # khoang cach den khung trong
FRAME_IN_W = 5        # net mong trong
ART = 560             # kich thuoc vung hoa van goc
INK = (0, 0, 0, 255)


def bezier(p0, p1, p2, p3, n=120):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0] + 3 * mt * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1] + 3 * mt * t ** 2 * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def stroke(draw: ImageDraw.ImageDraw, pts, width, color=INK):
    draw.line(pts, fill=color, width=width, joint="curve")


def spiral(cx, cy, r0, r1, turns, phase=0.0, n=90):
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = phase + t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def leaf(cx, cy, ang_deg, length, width, draw, fill=True, width_stroke=3):
    """La hinh hazel: hai cung ba beze, dinh la huong ra xa tam."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    pts = []
    # nua tren
    for i in range(41):
        t = i / 40
        bx = cx + ux * length * t
        by = cy + uy * length * t
        nx = px * math.sin(math.pi * t) * width * 0.5
        ny = py * math.sin(math.pi * t) * width * 0.5
        pts.append((bx + nx, by + ny))
    # nua duoi (nguoc ve)
    for i in range(40, -1, -1):
        t = i / 40
        bx = cx + ux * length * t
        by = cy + uy * length * t
        nx = -px * math.sin(math.pi * t) * width * 0.5
        ny = -py * math.sin(math.pi * t) * width * 0.5
        pts.append((bx + nx, by + ny))
    if fill:
        draw.polygon(pts, fill=INK)
    else:
        stroke(draw, pts, width_stroke)


def petal(cx, cy, ang_deg, length, width, draw, fill=False, width_stroke=4):
    """Canh hoa: ellipse quay duoi dang da giac."""
    a = math.radians(ang_deg)
    pts = []
    for i in range(61):
        t = i / 60
        ang = -math.pi / 2 + t * math.pi
        # toa do trong he cua canh
        lx = (length / 2) * math.cos(ang)
        ly = (width / 2) * math.sin(ang)
        # quay va tinh tien
        x = cx + lx * math.cos(a) - ly * math.sin(a) + (length / 2) * math.cos(a)
        y = cy + lx * math.sin(a) + ly * math.cos(a) + (length / 2) * math.sin(a)
        pts.append((x, y))
    if fill:
        draw.polygon(pts, fill=INK)
    else:
        stroke(draw, pts, width_stroke)


def draw_corner_ornament(layer: Image.Image) -> None:
    """Ve hoa van trong hinh chu nhat ART x ART, goc (0,0) la goc khung.

    Thanh leo bat dau tu be trong goc va leo ra phia trong trang (x+, y+).
    """
    d = ImageDraw.Draw(layer)

    # --- thanh leo chinh: tu goc leo ve goc trong, cong ve phia giua ---
    main = bezier((18, 470), (170, 300), (300, 160), (470, 16))
    stroke(d, main, 9)
    # --- thanh leo phu 1 (sat tren) ---
    v1 = bezier((150, 26), (250, 70), (300, 150), (250, 250))
    stroke(d, v1, 6)
    # --- thanh leo phu 2 (sat trai) ---
    v2 = bezier((26, 150), (70, 250), (150, 300), (250, 250))
    stroke(d, v2, 6)

    # --- xoay oc o hai dau thanh chinh ---
    s_start = spiral(18, 470, 34, 6, -1.35, phase=0.6)
    stroke(d, s_start, 7)
    s_end = spiral(470, 16, 34, 6, 1.35, phase=2.7)
    stroke(d, s_end, 7)

    # --- la tren thanh chinh ---
    leaf(210, 340, -75, 90, 46, d)
    leaf(300, 250, -25, 80, 42, d)
    leaf(300, 250, 200, 76, 40, d)
    # --- la treen thanh phu ---
    leaf(232, 88, 35, 66, 34, d)
    leaf(88, 232, -55, 66, 34, d)

    # --- bong hoa mini o giua goc (gan goc khung nhat) ---
    cx, cy = 100, 100
    for k in range(6):
        petal(cx, cy, k * 60, 88, 40, d)
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=INK, width=7)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=INK)

    # --- qua mong (cham tron) doc thanh leo ---
    for (bx, by, r) in [(128, 400, 9), (190, 330, 8), (390, 120, 8)]:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=INK)


def main() -> int:
    img = Image.new("RGB", (W, H), (255, 255, 255))

    # --- khung kep ---
    d = ImageDraw.Draw(img)
    d.rectangle([MARGIN, MARGIN, W - MARGIN, H - MARGIN], outline=INK, width=FRAME_OUT_W)
    ix, iy = MARGIN + FRAME_IN_GAP, MARGIN + FRAME_IN_GAP
    d.rectangle([ix, iy, W - ix, H - iy], outline=INK, width=FRAME_IN_W)

    # --- hoa van goc: ve 1 lan, lat sang 3 goc con lai ---
    corner = Image.new("RGBA", (ART, ART), (0, 0, 0, 0))
    draw_corner_ornament(corner)
    positions = [
        (MARGIN, MARGIN, corner),                                            # trai-tren
        (W - MARGIN - ART, MARGIN, corner.transpose(Image.FLIP_LEFT_RIGHT)),  # phai-tren
        (MARGIN, H - MARGIN - ART, corner.transpose(Image.FLIP_TOP_BOTTOM)),  # trai-duoi
        (W - MARGIN - ART, H - MARGIN - ART, corner.transpose(Image.ROTATE_180)),  # phai-duoi
    ]
    for x, y, art in positions:
        img.paste(art, (x, y), art)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, dpi=(300, 300))
    print(f"Da ghi {OUT} ({img.size[0]}x{img.size[1]} px)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
