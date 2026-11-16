"""Chuyển toàn bộ báo cáo markdown trong `report/` sang một tệp `.docx` chuẩn CTUT.

Chạy: python -m scripts.build_report_docx --out report/dist/BaoCao_BTL_HocMay_Nhom10.docx
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT_NAME = "Times New Roman"


def _set_style_fonts(style, font_name: str = FONT_NAME) -> None:
    """Đặt đồng bộ font Times New Roman cho mọi họ ký tự (kể cả eastAsia) và xóa theme font."""
    style.font.name = font_name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), font_name)
    for theme_attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if qn(theme_attr) in rfonts.attrib:
            del rfonts.attrib[qn(theme_attr)]


def configure_a4_section(section) -> None:
    """Áp dụng khổ giấy A4 đứng và lề chuẩn CTUT (trên/dưới/phải 2,0 cm, trái 3,0 cm)."""
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(1.25)
    section.footer_distance = Cm(1.25)


def new_document() -> Document:
    """Khởi tạo Document chuẩn CTUT (A4, Times New Roman, các style Normal và Heading 1–3)."""
    doc = Document()
    configure_a4_section(doc.sections[0])

    normal = doc.styles["Normal"]
    _set_style_fonts(normal)
    normal.font.size = Pt(13)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.line_spacing = 1.3
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.first_line_indent = Cm(1.0)
    normal.paragraph_format.space_before = Pt(4)
    normal.paragraph_format.space_after = Pt(4)

    h1 = doc.styles["Heading 1"]
    _set_style_fonts(h1)
    h1.font.size = Pt(15)
    h1.font.bold = True
    h1.font.all_caps = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.first_line_indent = Cm(0)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(8)
    h1.paragraph_format.keep_with_next = True

    h2 = doc.styles["Heading 2"]
    _set_style_fonts(h2)
    h2.font.size = Pt(13.5)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h2.paragraph_format.first_line_indent = Cm(0)
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.keep_with_next = True

    h3 = doc.styles["Heading 3"]
    _set_style_fonts(h3)
    h3.font.size = Pt(13)
    h3.font.bold = True
    h3.font.italic = True
    h3.font.color.rgb = RGBColor(0, 0, 0)
    h3.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h3.paragraph_format.first_line_indent = Cm(0)
    h3.paragraph_format.space_before = Pt(6)
    h3.paragraph_format.space_after = Pt(4)
    h3.paragraph_format.keep_with_next = True

    for cap_name, align, keep_next in (
        ("Caption Table", WD_ALIGN_PARAGRAPH.LEFT, True),
        ("Caption Figure", WD_ALIGN_PARAGRAPH.CENTER, False),
    ):
        cap = doc.styles.add_style(cap_name, WD_STYLE_TYPE.PARAGRAPH)
        cap.base_style = normal
        _set_style_fonts(cap)
        cap.font.size = Pt(11)
        cap.font.bold = True
        cap.font.color.rgb = RGBColor(0, 0, 0)
        cap.paragraph_format.alignment = align
        cap.paragraph_format.first_line_indent = Cm(0)
        cap.paragraph_format.space_before = Pt(6)
        cap.paragraph_format.space_after = Pt(4)
        cap.paragraph_format.keep_with_next = keep_next

    return doc


def strip_technical_notes(md: str) -> str:
    """Loại bỏ từ dòng `## Ghi chú kỹ thuật` trở đi và dấu `---` ngay trước đó."""
    out: list[str] = []
    for line in md.splitlines():
        if re.match(r"^##\s+Ghi chú kỹ thuật\b", line.strip(), re.IGNORECASE):
            break
        out.append(line)
    while out and out[-1].strip() in ("", "---"):
        out.pop()
    return "\n".join(out) + ("\n" if out else "")


def build_docx(report_dir: Path, out_path: Path) -> Path:
    """Dựng tệp .docx hoàn chỉnh từ thư mục `report/`."""
    raise NotImplementedError("Implemented in Task B4")
