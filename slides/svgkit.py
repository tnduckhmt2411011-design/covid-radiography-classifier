"""Bộ khung sinh SVG cho 34 trang của bộ slide, theo hợp đồng SVG của ppt-master.

Quy tắc do hợp đồng của ppt-master đặt ra, và là cách bộ khung này viết mã:

* mỗi trang là một ``.svg`` 1280×720 gắn một Master/Layout đã khai báo;
* phần tử con trực tiếp của gốc phải nằm trong khung nhìn và **không chồng lấn**
  nhau, nên mỗi vùng nội dung được gói trong một **vùng gốc** (:class:`Zone`) có
  ``data-pptx-bounds`` bao trùm;
* không id nào lặp lại trong toàn bộ deck: mọi id mang tiền tố số trang
  (:meth:`Page.nid`);
* chỉ một phần tử con trực tiếp mang ``data-pptx-carrier="true"`` trong mỗi ô
  placeholder.

Đơn vị: 1 px = 0,75 pt. Cỡ chữ ghi bằng px, hệ thống đo chữ của ppt-master nhận
pt nên mọi phép đo quy đổi qua :data:`PT`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

SKILL_SCRIPTS = Path(r"D:\Tools\ppt-master\skills\ppt-master\scripts")
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))
from text_measure import wrap_text  # noqa: E402  (thư viện đo chữ của ppt-master)

# ------------------------------------------------------------------ canvas
W, H = 1280, 720
PT = 0.75  # 1 px = 0,75 pt

MARGIN = 82  # 0,85 in
CONTENT_W = W - 2 * MARGIN  # 1116

KICKER_Y = 36
TITLE_BOX_Y = 68
HEADER_RULE_Y = 160
CONTENT_TOP = 197
CONTENT_BOTTOM = 612
CONTENT_H = CONTENT_BOTTOM - CONTENT_TOP
FOOTER_RULE_Y = 628
FOOTER_Y = 648

FONT_ROOT = "Segoe UI, Arial, sans-serif"
FONT = "Segoe UI"

# ------------------------------------------------------------------ màu
PAPER = "#F7F4EE"
INK = "#161D26"
INK_SOFT = "#4A5560"
INK_FAINT = "#7A8493"
TEAL = "#0F766E"
TEAL_LIGHT = "#7FBFB6"
TEAL_PALE = "#E4EFEC"
AMBER = "#B45309"
AMBER_PALE = "#F3E7D6"
LINE = "#D8D2C4"
CARD = "#FFFFFF"
PLATE = "#EFEAE0"
CARD_DARK = "#222B36"
TEXT_ON_DARK = "#F2EFE7"
SOFT_ON_DARK = "#9AA6B4"
RULE_ON_DARK = "#39424F"

# ------------------------------------------------------------------ cỡ chữ
SIZE_KICKER = 19  # 14,25 pt
SIZE_TITLE = 42  # 31,5 pt
SIZE_TITLE_SMALL = 34
SIZE_BODY = 21  # 15,75 pt
SIZE_BODY_STRONG = 22
SIZE_SMALL = 19  # 14,25 pt — sàn 14 pt của quy chuẩn deck
SIZE_FOOTER = 15  # 11,25 pt
SIZE_NUMBER = 150
LINE_H = 30

# ------------------------------------------------------------------ master/layout
MASTERS = {
    "light": ("cxr_content_master", "Nội dung CXR"),
    "dark": ("cxr_divider_master", "Chương CXR"),
}
LAYOUTS = {
    "cover": ("cover", "Bìa"),
    "divider": ("section_divider", "Mở chương"),
    "content": ("title_content", "Tiêu đề và nội dung"),
    "number": ("big_number", "Số lớn"),
    "appendix": ("appendix", "Dự phòng"),
    "closing": ("closing", "Cảm ơn"),
}

# Ô placeholder dùng lại cho mọi trang cùng một layout: id, số thứ tự và bounds
# phải giống nhau từ trang này sang trang khác (hợp đồng layout của ppt-master).
SLOTS = {
    "title": ("title-slot", 0, (82, 57, 1116, 97)),
    "footer": ("footer-slot", 1, (82, 634, 900, 24)),
    "slide-number": ("slide-number-slot", 2, (998, 634, 200, 24)),
}


def measure(text: str, size: float, *, weight: str = "normal") -> float:
    """Đo một dòng, trả về px (thư viện đo của ppt-master nhận pt)."""
    return wrap_text(text, size=size * PT, max_width=10_000, family=FONT, weight=weight)[1][0] / PT


def wrap(text: str, size: float, max_width: float, *, weight: str = "normal") -> list[str]:
    """Ngắt dòng cho vừa ô rộng ``max_width`` px; trả danh sách dòng."""
    lines, _, _ = wrap_text(text, size=size * PT, max_width=max_width * PT, family=FONT, weight=weight)
    return lines


def _num(value: float) -> str:
    return f"{value:g}"


def _attrs(pairs: dict) -> str:
    return "".join(f' {key}="{value}"' for key, value in pairs.items() if value is not None)


def slug(text: str, limit: int = 24) -> str:
    keep = [ch.lower() if ch.isalnum() else "-" for ch in text]
    return ("".join(keep).strip("-") or "muc")[:limit]


# ------------------------------------------------------------------ vùng gốc
class Zone:
    """Một vùng gốc: gom mọi phần tử con, rồi xuất ra một ``<g>`` có đủ bounds."""

    def __init__(self, page: "Page", gid: str, x: float, y: float, w: float, h: float,
                 *, gap: int = 0):
        self.page = page
        self.gid = gid
        self.box = (int(x), int(y), int(w), int(h))
        self.items: list[str] = []
        self.gap = gap  # nới theo ý muốn khi ước lượng bề rộng chữ chưa khớp

    # -- hình khối
    def card(self, *, fill: str = CARD, stroke: str | None = None, radius: float = 8,
             opacity: float | None = None) -> "Zone":
        self.items.append(self.page.rect(f"{self.gid}-card", *self.box, fill=fill or CARD,
                                         stroke=stroke, radius=radius, opacity=opacity))
        return self

    def plate(self, *, fill: str = PLATE, radius: float = 8) -> "Zone":
        return self.card(fill=fill, stroke=None, radius=radius)

    def line(self, gid: str, x1: float, y1: float, x2: float, y2: float, *, stroke: str = LINE,
             width: float = 1.0, dash: str | None = None) -> "Zone":
        self.items.append(self.page.line(gid, x1, y1, x2, y2, stroke=stroke, width=width, dash=dash))
        return self

    def image(self, gid: str, href: str, x: float, y: float, w: float, h: float) -> "Zone":
        self.items.append(self.page.image(gid, href, x, y, w, h))
        return self

    def rect(self, gid: str, x: float, y: float, w: float, h: float, *, fill: str = TEAL,
             radius: float = 0) -> "Zone":
        self.items.append(self.page.rect(gid, x, y, w, h, fill=fill, radius=radius))
        return self

    # -- chữ
    def text(self, gid: str, x: float, y: float, content: str, *, size: float = 21,
             color: str = INK, weight: str = "normal", anchor: str | None = None,
             max_width: float | None = None, line_h: float = LINE_H, opacity: float | None = None,
             carrier: bool = False, plain: bool = False) -> "Zone":
        self.items.append(self.page.text(gid, x, y, content, size=size, color=color,
                                         weight=weight, anchor=anchor, max_width=max_width,
                                         line_h=line_h, opacity=opacity, carrier=carrier,
                                         plain=plain, gap=self.gap))
        return self

    def add(self, xml: str) -> "Zone":
        self.items.append(xml)
        return self

    def done(self) -> str:
        x, y, w, h = self.box
        inner = "".join(self.items)
        return f'<g id="{self.page.nid(self.gid)}" data-pptx-bounds="{x} {y} {w} {h}">{inner}</g>'


# ------------------------------------------------------------------ trang
class Page:
    """Một trang slide: giữ master, layout và dồn dần các vùng nội dung."""

    def __init__(self, filename: str, *, layout: str, master: str = "light",
                 kicker: str | None = None, title: str | None = None, source: str | None = None,
                 page_no: int | None = None, total: int | None = 28, numbered: bool = True,
                 title_size: float = SIZE_TITLE, title_gap: int = 0):
        self.filename = filename
        self.layout_key = layout
        self.master_key = master
        self.dark = master == "dark" or layout in {"cover", "divider", "number", "closing"}
        self.kicker_text = kicker
        self.title_text = title
        self.source = source
        self.page_no = page_no
        self.total = total
        self.numbered = numbered
        self.title_size = title_size
        self.title_gap = title_gap
        self.parts: list[str] = []
        self.next_idx = 0
        self.prefix = filename.split("_")[0]

    def nid(self, gid: str) -> str:
        """Id duy nhất trong toàn bộ deck: mọi id mang tiền tố số trang."""
        return f"{self.prefix}-{gid}"

    def zone(self, gid: str, x: float, y: float, w: float, h: float, *, gap: int = 0) -> Zone:
        return Zone(self, gid, x, y, w, h, gap=gap)

    # ---------------------------------------------------------------- chrome
    def _chrome(self) -> str:
        if self.dark:
            return self.rect("master-background", 0, 0, W, H, fill=INK, layer="master")
        return (
            self.rect("master-background", 0, 0, W, H, fill=PAPER, layer="master")
            + self.line("master-header-rule", MARGIN, HEADER_RULE_Y, W - MARGIN, HEADER_RULE_Y,
                        stroke=LINE, width=1, layer="master")
            + self.line("master-footer-rule", MARGIN, FOOTER_RULE_Y, W - MARGIN, FOOTER_RULE_Y,
                        stroke=LINE, width=1, layer="master")
        )

    def kicker(self) -> str:
        if not self.kicker_text:
            return ""
        return self.text("kicker", MARGIN, KICKER_Y, self.kicker_text, size=SIZE_KICKER,
                         color=(TEAL if not self.dark else TEAL_LIGHT), weight="bold")

    def title(self) -> str:
        if not self.title_text:
            return ""
        size = self.title_size
        lines = wrap(self.title_text, size, CONTENT_W, weight="bold")
        if len(lines) > 2 and size != SIZE_TITLE_SMALL:
            size = SIZE_TITLE_SMALL
            lines = wrap(self.title_text, size, CONTENT_W, weight="bold")
        if len(lines) > 2:
            raise ValueError(f"Tiêu đề quá 2 dòng: {self.title_text!r}")
        baselines = [112] if len(lines) == 1 else [93, 93 + 45]
        color = INK if not self.dark else TEXT_ON_DARK
        return self.slot("title", MARGIN, baselines[0], lines, size=size, color=color, step=45)

    def carrier(self, gid: str, x: float, first_baseline: float, lines: list[str], *,
                size: float, color: str, step: float = 45, weight: bool = True) -> str:
        """Một carrier nhiều dòng kiểu dy-stacked: xuất ra đúng một khung chữ."""
        pairs = {"id": self.nid(gid), "x": _num(x), "y": _num(first_baseline),
                 "font-size": _num(size), "fill": color, "data-pptx-carrier": "true"}
        if weight:
            pairs["font-weight"] = "700"
        tspans = [f'<tspan x="{_num(x)}">{escape(lines[0])}</tspan>']
        tspans += [f'<tspan x="{_num(x)}" dy="{_num(step)}">{escape(line)}</tspan>'
                   for line in lines[1:]]
        return f"<text{_attrs(pairs)}>{''.join(tspans)}</text>"

    def slot(self, role: str, x: float, first_baseline: float, lines: list[str], *,
             size: float, color: str, step: float = 45, carrier_gid: str | None = None,
             weight: bool = True, bounds: tuple[int, int, int, int] | None = None) -> str:
        """Ô placeholder: bounds và id cố định theo vai trò để mọi trang cùng layout khớp."""
        name, number, box = SLOTS[role]
        carrier = self.carrier(carrier_gid or (name + "-carrier"), x, first_baseline, lines,
                               size=size, color=color, step=step, weight=weight)
        return self._placeholder("title" if role == "title" else role, name,
                                 bounds or box, carrier, idx=number)

    def footer(self) -> str:
        if not self.source:
            return ""
        name, number, box = SLOTS["footer"]
        carrier = self.text("footer-carrier", box[0], FOOTER_Y, self.source, size=SIZE_FOOTER,
                            color=INK_FAINT, carrier=True, plain=True)
        return self._placeholder("footer", name, box, carrier, idx=number)

    def page_number(self) -> str:
        if not self.numbered or not self.page_no:
            return ""
        name, number, box = SLOTS["slide-number"]
        label = f"{self.page_no} / {self.total}" if self.total else str(self.page_no)
        carrier = self.text("page-number-carrier", box[0] + box[2], FOOTER_Y, label, size=SIZE_FOOTER,
                            color=INK_FAINT, anchor="end", carrier=True, plain=True)
        return self._placeholder("slide-number", name, box, carrier, idx=number)

    # ---------------------------------------------------------------- primitive
    def _placeholder(self, kind: str, name: str, bounds: tuple[int, int, int, int], xml: str,
                     idx: int | None = None) -> str:
        x, y, w, h = bounds
        number = idx if idx is not None else self._idx()
        return (
            f'<g id="{name}" data-pptx-placeholder="{kind}" data-pptx-idx="{number}" '
            f'data-pptx-bounds="{x} {y} {w} {h}">{xml}</g>'
        )

    def _idx(self) -> int:
        value = self.next_idx
        self.next_idx += 1
        return value

    def text(self, gid: str, x: float, y: float, content: str, *, size: float = 21,
             color: str = INK, weight: str = "normal", anchor: str | None = None,
             carrier: bool = False, plain: bool = False, max_width: float | None = None,
             line_h: float = LINE_H, opacity: float | None = None, gap: int = 0) -> str:
        """Một khối chữ, bọc trong ``<g>`` có bounds vừa đủ quanh nội dung đo được."""
        lines = wrap(content, size, max_width, weight=weight) if max_width else [content]
        attrs = {"id": self.nid(f"{gid}-carrier") if carrier else self.nid(gid + "-text"),
                 "x": _num(x), "y": _num(y), "font-size": _num(size), "fill": color}
        if weight != "normal":
            attrs["font-weight"] = "700" if weight == "bold" else weight
        if anchor:
            attrs["text-anchor"] = anchor
        if opacity is not None:
            attrs["opacity"] = _num(opacity)
        if carrier:
            attrs["data-pptx-carrier"] = "true"
        inner = "".join(self._tspan(line, x, y + index * line_h, size, color)
                        for index, line in enumerate(lines))
        xml = f"<text{_attrs(attrs)}>{inner}</text>"
        if plain:
            return xml
        width = int(max_width if len(lines) > 1 else measure(lines[0], size, weight=weight)) + gap + 2
        top = int(y - size * 0.88)
        height = int((len(lines) - 1) * line_h + size * 1.3)
        left = int(x - width) if anchor == "end" else int(x)
        return (f'<g id="{self.nid(gid)}" data-pptx-bounds="{left} {top} {width} {height}">'
                f"{xml}</g>")

    @staticmethod
    def _tspan(line: str, x: float, y: float, size: float, color: str) -> str:
        return f'<tspan x="{_num(x)}" y="{_num(y)}" fill="{color}" font-size="{_num(size)}">{escape(line)}</tspan>'

    def rect(self, gid: str, x: float, y: float, w: float, h: float, *, fill: str = CARD,
             stroke: str | None = None, width: float = 1.0, radius: float = 0,
             opacity: float | None = None, layer: str | None = None) -> str:
        attrs = {"id": (gid if layer else self.nid(gid)), "x": _num(x), "y": _num(y), "width": _num(w),
                 "height": _num(h), "fill": fill}
        if radius:
            attrs["rx"] = _num(radius)
        if stroke:
            attrs["stroke"] = stroke
            attrs["stroke-width"] = _num(width)
        if opacity is not None:
            attrs["opacity"] = _num(opacity)
        if layer:
            attrs["data-pptx-layer"] = layer
            attrs["data-pptx-editable"] = "false"
        return f"<rect{_attrs(attrs)}/>"

    def line(self, gid: str, x1: float, y1: float, x2: float, y2: float, *, stroke: str = LINE,
             width: float = 1.0, layer: str | None = None, dash: str | None = None) -> str:
        attrs = {"id": (gid if layer else self.nid(gid)), "x1": _num(x1), "y1": _num(y1),
                 "x2": _num(x2), "y2": _num(y2), "stroke": stroke, "stroke-width": _num(width)}
        if dash:
            attrs["stroke-dasharray"] = dash
        if layer:
            attrs["data-pptx-layer"] = layer
            attrs["data-pptx-editable"] = "false"
        return f"<line{_attrs(attrs)}/>"

    def image(self, gid: str, href: str, x: float, y: float, w: float, h: float) -> str:
        gid = self.nid(gid)
        return (
            f'<g id="{gid}" data-pptx-bounds="{int(x)} {int(y)} {int(w)} {int(h)}">'
            f'<image href="{escape(href)}" x="{_num(x)}" y="{_num(y)}" width="{_num(w)}" '
            f'height="{_num(h)}" preserveAspectRatio="xMidYMid meet"/></g>'
        )

    # ---------------------------------------------------------------- render
    def content(self, *items: str) -> "Page":
        self.parts.extend(items)
        return self

    def render(self) -> str:
        master_id, master_name = MASTERS[self.master_key]
        layout_id, layout_name = LAYOUTS[self.layout_key]
        body = (self._chrome() + self.kicker() + self.title() + "".join(self.parts)
                + self.footer() + self.page_number())
        lang = ' lang="vi-VN"'
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}"{lang} font-family="{FONT_ROOT}" '
            f'data-pptx-master="{master_id}" data-pptx-master-name="{master_name}" '
            f'data-pptx-layout="{layout_id}" data-pptx-layout-name="{layout_name}">\n'
            f"{body}\n</svg>\n"
        )

    def write(self, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / self.filename
        path.write_text(self.render(), encoding="utf-8")
        return path


# ------------------------------------------------------------------ khung sẵn
def bullet_zone(page: Page, gid: str, x: float, y: float, w: float, items: list[str], *,
                size: float = SIZE_BODY, dark: bool = False, gap: int = 16, line_h: float = 30,
                marker: str = "—") -> str:
    """Vùng danh sách: gạch đầu dòng và mỗi ý ngắt dòng theo bề rộng đã cho."""
    zone = page.zone(gid, x, y, w, 10)
    cursor = y
    for index, item in enumerate(items):
        lines = wrap(item, size, w - 34)
        zone.add(page.text(f"{gid}-{index}-mark", x, cursor, marker, size=size,
                           color=(TEAL_LIGHT if dark else TEAL)))
        zone.add(page.text(f"{gid}-{index}-body", x + 34, cursor, item, size=size,
                           color=(SOFT_ON_DARK if dark else INK), max_width=w - 34, line_h=line_h))
        cursor += len(lines) * line_h + gap
    zone.box = (int(x), int(y - size), int(w), int(cursor - y - gap + size * 1.6))
    return zone.done()


def note_zone(page: Page, gid: str, x: float, y: float, w: float, text: str, *, dark: bool = False,
              fill: str | None = None, stroke: str | None = None, size: float = SIZE_SMALL,
              line_h: float = 26, color: str | None = None) -> str:
    """Dải chú thích có nền: nguồn, cảnh báo hoặc phát biểu D4."""
    lines = wrap(text, size, w - 44)
    height = len(lines) * line_h + 26
    zone = page.zone(gid, x, y, w, height)
    zone.card(fill=fill or (CARD_DARK if dark else PLATE), stroke=stroke, radius=6)
    zone.add(page.text(f"{gid}-text", x + 22, y + 22 + size, text, size=size,
                       color=color or (TEXT_ON_DARK if dark else INK), max_width=w - 44,
                       line_h=line_h))
    return zone.done()
