"""Kiểm thử dựng bản Word (.docx) từ các tệp markdown trong `report/`."""
from __future__ import annotations

import pytest

docx = pytest.importorskip("docx")
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

from scripts.build_report_docx import build_docx, new_document, strip_technical_notes


def _rfonts_dict(style) -> dict[str, str]:
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    assert rfonts is not None, f"Style {style.name} thiếu w:rFonts"
    return {
        "ascii": rfonts.get(qn("w:ascii")),
        "hAnsi": rfonts.get(qn("w:hAnsi")),
        "eastAsia": rfonts.get(qn("w:eastAsia")),
    }


def test_page_setup_a4_margins() -> None:
    doc = new_document()
    sec = doc.sections[0]
    assert sec.page_width.cm == pytest.approx(21.0, abs=0.05)
    assert sec.page_height.cm == pytest.approx(29.7, abs=0.05)
    assert sec.left_margin.cm == pytest.approx(3.0, abs=0.05)
    assert sec.right_margin.cm == pytest.approx(2.0, abs=0.05)
    assert sec.top_margin.cm == pytest.approx(2.0, abs=0.05)
    assert sec.bottom_margin.cm == pytest.approx(2.0, abs=0.05)


def test_normal_style_font() -> None:
    doc = new_document()
    normal = doc.styles["Normal"]
    assert normal.font.name == "Times New Roman"
    assert normal.font.size == Pt(13)
    assert normal.paragraph_format.line_spacing == pytest.approx(1.3, abs=0.01)
    assert normal.paragraph_format.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY
    assert normal.paragraph_format.first_line_indent.cm == pytest.approx(1.0, abs=0.05)
    assert normal.paragraph_format.space_before == Pt(4)
    assert normal.paragraph_format.space_after == Pt(4)
    fonts = _rfonts_dict(normal)
    assert fonts["ascii"] == "Times New Roman"
    assert fonts["hAnsi"] == "Times New Roman"
    assert fonts["eastAsia"] == "Times New Roman"


def test_heading_styles() -> None:
    doc = new_document()
    h1 = doc.styles["Heading 1"]
    h2 = doc.styles["Heading 2"]
    h3 = doc.styles["Heading 3"]

    assert h1.font.all_caps is True
    assert h1.font.bold is True
    assert h1.font.size == Pt(15)
    assert h2.font.bold is True
    assert h2.font.size == Pt(13.5)
    assert h3.font.bold is True
    assert h3.font.italic is True
    assert h3.font.size == Pt(13)

    for st in (h1, h2, h3):
        fonts = _rfonts_dict(st)
        assert fonts == {
            "ascii": "Times New Roman",
            "hAnsi": "Times New Roman",
            "eastAsia": "Times New Roman",
        }


def test_strip_technical_notes() -> None:
    sample = (
        "# CHƯƠNG 1. GIỚI THIỆU\n\n"
        "Đoạn văn hợp lệ.\n\n"
        "---\n\n"
        "## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)\n\n"
        "- Nguồn: `results/foo.csv`\n"
    )
    cleaned = strip_technical_notes(sample)
    assert "Đoạn văn hợp lệ." in cleaned
    assert "Ghi chú kỹ thuật" not in cleaned
    assert "results/foo.csv" not in cleaned
    assert not cleaned.rstrip().endswith("---")
    assert callable(build_docx)
