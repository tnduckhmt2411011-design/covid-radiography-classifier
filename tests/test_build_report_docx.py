"""Kiểm thử dựng bản Word (.docx) từ các tệp markdown trong `report/`."""
from __future__ import annotations

from pathlib import Path

import pytest

docx = pytest.importorskip("docx")
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

from scripts.build_report_docx import (
    add_cover,
    add_section_break,
    add_toc_field,
    build_docx,
    new_document,
    render_markdown,
    strip_technical_notes,
)


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


def test_table_booktabs() -> None:
    doc = new_document()
    md = (
        "| Lớp | Số ảnh | Macro-F1 |\n"
        "| :--- | ---: | :---: |\n"
        "| COVID | 543 | 0,9214 |\n"
        "| Normal | 1.529 | 0,8751 |\n"
    )
    render_markdown(doc, md, Path("report"))
    assert len(doc.tables) == 1
    tbl = doc.tables[0]
    assert len(tbl.rows) == 3
    assert len(tbl.columns) == 3

    tbl_borders = tbl._tbl.tblPr.find(qn("w:tblBorders"))
    assert tbl_borders is not None
    assert tbl_borders.find(qn("w:top")).get(qn("w:val")) == "single"
    assert int(tbl_borders.find(qn("w:top")).get(qn("w:sz"))) >= 12
    assert tbl_borders.find(qn("w:bottom")).get(qn("w:val")) == "single"
    assert int(tbl_borders.find(qn("w:bottom")).get(qn("w:sz"))) >= 12
    assert tbl_borders.find(qn("w:insideV")).get(qn("w:val")) == "none"
    assert tbl_borders.find(qn("w:left")).get(qn("w:val")) == "none"
    assert tbl_borders.find(qn("w:right")).get(qn("w:val")) == "none"

    hdr_cell = tbl.rows[0].cells[0]
    shd = hdr_cell._tc.tcPr.find(qn("w:shd"))
    assert shd is not None and shd.get(qn("w:fill")).upper() == "D9D9D9"
    hdr_borders = hdr_cell._tc.tcPr.find(qn("w:tcBorders"))
    assert hdr_borders is not None and hdr_borders.find(qn("w:bottom")).get(qn("w:val")) == "single"

    assert tbl.rows[1].cells[0].paragraphs[0].runs[0].font.size == Pt(10.5)
    assert tbl.rows[1].cells[1].paragraphs[0].alignment == WD_ALIGN_PARAGRAPH.RIGHT
    assert tbl.rows[1].cells[2].paragraphs[0].alignment == WD_ALIGN_PARAGRAPH.CENTER


def test_caption_placement() -> None:
    doc = new_document()
    md = (
        "Xem Bảng 3.1 và Hình 3.1.\n\n"
        "**Bảng 3.1: Kết quả kiểm thử**\n\n"
        "| A | B |\n| :--- | ---: |\n| x | 1 |\n\n"
        "![Ma trận nhầm lẫn](../figures/03_ma_tran_nham_lon_svm_val.png)\n\n"
        "**Hình 3.1: Ma trận nhầm lẫn**\n"
    )
    render_markdown(doc, md, Path("report"))
    styles = [p.style.name for p in doc.paragraphs]
    assert "Caption Table" in styles
    assert "Caption Figure" in styles
    cap_tab = next(p for p in doc.paragraphs if p.style.name == "Caption Table")
    cap_fig = next(p for p in doc.paragraphs if p.style.name == "Caption Figure")
    assert cap_tab.text.startswith("Bảng 3.1:")
    assert cap_fig.text.startswith("Hình 3.1:")
    assert cap_fig.alignment == WD_ALIGN_PARAGRAPH.CENTER


def test_image_fits_margins() -> None:
    doc = new_document()
    md = "![Ma trận](../figures/03_ma_tran_nham_lon_svm_val.png)\n"
    render_markdown(doc, md, Path("report"))
    assert len(doc.inline_shapes) == 1
    shape = doc.inline_shapes[0]
    assert shape.width.cm <= 15.5
    img_para = next(p for p in doc.paragraphs if p._p.xpath(".//w:drawing"))
    assert img_para.alignment == WD_ALIGN_PARAGRAPH.CENTER


def test_inline_math() -> None:
    doc = new_document()
    md = "$u$ và $D = 0$, độ lệch $\\pm$ và tập $\\{-1, 1\\}$."
    render_markdown(doc, md, Path("report"))
    p = doc.paragraphs[0]
    txt = p.text
    assert "$" not in txt
    assert "±" in txt
    assert "{−1, 1}" in txt or "{-1, 1}" in txt
    u_runs = [r for r in p.runs if r.text.strip() == "u"]
    assert u_runs and u_runs[0].italic is True


def test_display_equation() -> None:
    doc = new_document()
    md = "$$D = \\frac{64 - u \\cdot v}{2} \\qquad (2.1)$$\n"
    render_markdown(doc, md, Path("report"))
    omath_paras = [p for p in doc.paragraphs if p._p.findall(qn("m:oMathPara"))]
    assert len(omath_paras) == 1
    p = omath_paras[0]
    assert "(2.1)" in "".join(t.text or "" for t in p._p.iter(qn("w:t")))
    tabs = p._p.pPr.find(qn("w:tabs"))
    assert tabs is not None
    assert any(t.get(qn("w:val")) == "right" for t in tabs.findall(qn("w:tab")))


def test_no_raw_markdown_leaks() -> None:
    doc = new_document()
    md = (
        "Đoạn có **in đậm**, *in nghiêng*, mã `StandardScaler`, "
        "liên kết [`README`](README.md), $T = 0$ và $\\pm$.\n\n"
        "- Mục **một** với `code`\n"
        "1. Mục đánh số\n\n"
        "> Trích dẫn **quan trọng**\n\n"
        "$$D = \\frac{64 - u \\cdot v}{2} \\qquad (2.1)$$\n"
    )
    render_markdown(doc, md, Path("report"))
    for p in doc.paragraphs:
        for bad in ("**", "`", "](", "$$", "\\frac"):
            assert bad not in p.text, (bad, p.text)
    code_runs = [r for p in doc.paragraphs for r in p.runs if r.font.name == "Consolas"]
    assert code_runs and code_runs[0].font.size == Pt(11)


def _all_instr_texts(doc) -> list[str]:
    out = [el.text or "" for el in doc.element.iter(qn("w:instrText"))]
    for sec in doc.sections:
        for hdr_ftr in (sec.header, sec.footer):
            out.extend(el.text or "" for el in hdr_ftr._element.iter(qn("w:instrText")))
    return out


def test_cover_has_no_page_number() -> None:
    doc = new_document()
    add_section_break(doc, "none", None)
    sec0 = doc.sections[0]
    assert "".join(p.text for p in sec0.footer.paragraphs).strip() == ""
    assert not list(sec0.footer._element.iter(qn("w:instrText")))


def test_front_matter_roman_numbering() -> None:
    doc = new_document()
    add_section_break(doc, "none", None)
    doc.add_paragraph("Cover")
    add_section_break(doc, "lowerRoman", 1)
    sec1 = doc.sections[1]
    pg_type = sec1._sectPr.find(qn("w:pgNumType"))
    assert pg_type is not None
    assert pg_type.get(qn("w:fmt")) == "lowerRoman"
    assert pg_type.get(qn("w:start")) == "1"
    instrs = [el.text or "" for el in sec1.footer._element.iter(qn("w:instrText"))]
    assert any("PAGE" in ins for ins in instrs)
    assert sec1.footer.paragraphs[0].alignment == WD_ALIGN_PARAGRAPH.CENTER


def test_body_arabic_restart() -> None:
    doc = new_document()
    add_section_break(doc, "none", None)
    doc.add_paragraph("Cover")
    add_section_break(doc, "lowerRoman", 1)
    doc.add_paragraph("Front")
    add_section_break(doc, "decimal", 1)
    sec2 = doc.sections[2]
    pg_type = sec2._sectPr.find(qn("w:pgNumType"))
    assert pg_type is not None
    assert pg_type.get(qn("w:fmt")) == "decimal"
    assert pg_type.get(qn("w:start")) == "1"


def test_each_chapter_starts_new_page() -> None:
    doc = new_document()
    render_markdown(doc, "# CHƯƠNG 1. MỞ ĐẦU\n\nNội dung.\n\n# CHƯƠNG 2. PHƯƠNG PHÁP\n\nNội dung 2.\n", Path("report"))
    h1s = [p for p in doc.paragraphs if p.style.name == "Heading 1"]
    assert len(h1s) == 2
    for h1 in h1s:
        assert h1.paragraph_format.page_break_before is True or h1.style.paragraph_format.page_break_before is True


def test_toc_fields_present() -> None:
    doc = new_document()
    add_toc_field(doc, r'TOC \o "1-3" \h \z \u')
    add_toc_field(doc, r'TOC \h \z \t "Caption Table,1"')
    add_toc_field(doc, r'TOC \h \z \t "Caption Figure,1"')
    instrs = [s.strip() for s in _all_instr_texts(doc)]
    assert instrs.count(r'TOC \o "1-3" \h \z \u') == 1
    assert instrs.count(r'TOC \h \z \t "Caption Table,1"') == 1
    assert instrs.count(r'TOC \h \z \t "Caption Figure,1"') == 1
    upd = doc.settings.element.find(qn("w:updateFields"))
    assert upd is not None and upd.get(qn("w:val")) == "true"


def test_cover_content() -> None:
    doc = new_document()
    add_section_break(doc, "none", None)
    cover_md = Path("report/00a_trang_bia_va_loi.md").read_text(encoding="utf-8")
    border_png = Path("report/figures/khung_trang_bia.png")
    add_cover(doc, cover_md, border_png, subtitle=False)
    doc.add_page_break()
    add_cover(doc, cover_md, border_png, subtitle=True)

    full_txt = "\n".join(p.text for p in doc.paragraphs)
    assert "TRƯỜNG ĐẠI HỌC KỸ THUẬT" in full_txt
    assert "TS. Lê Anh Nhã Uyên" in full_txt
    for suffix in ("011", "021", "003", "022", "014", "046"):
        assert f"KHMT2411{suffix}" in full_txt
    assert "Cần Thơ – Tháng 11/2026" in full_txt
    assert "[Chèn logo CTUT]" in full_txt

    anchors = list(doc.sections[0].header._element.iter(qn("wp:anchor")))
    assert anchors and anchors[0].get("behindDoc") == "1"


def test_full_build_order(tmp_path: Path) -> None:
    out = build_docx(Path("report"), tmp_path / "out.docx")
    assert out.exists() and out.stat().st_size > 200_000
    doc = docx.Document(str(out))
    h1_titles = [p.text.strip() for p in doc.paragraphs if p.style.name == "Heading 1"]
    assert len(h1_titles) == 8
    for i in range(1, 7):
        assert h1_titles[i - 1].startswith(f"CHƯƠNG {i}.")
    assert h1_titles[6] == "TÀI LIỆU THAM KHẢO"
    assert h1_titles[7] == "PHỤ LỤC"


def test_counts(tmp_path: Path) -> None:
    out = build_docx(Path("report"), tmp_path / "out.docx")
    doc = docx.Document(str(out))
    cap_tables = [p for p in doc.paragraphs if p.style.name == "Caption Table"]
    cap_figs = [p for p in doc.paragraphs if p.style.name == "Caption Figure"]
    assert len(cap_tables) == 32
    assert len(cap_figs) == 4
    full_txt = "\n".join(p.text for p in doc.paragraphs)
    for idx in range(1, 14):
        assert f"[{idx}] " in full_txt


def test_no_technical_notes_and_no_paths(tmp_path: Path) -> None:
    out = build_docx(Path("report"), tmp_path / "out.docx")
    doc = docx.Document(str(out))
    paras = doc.paragraphs
    ch1_idx = next(i for i, p in enumerate(paras) if p.style.name == "Heading 1" and p.text.startswith("CHƯƠNG 1."))
    refs_idx = next(i for i, p in enumerate(paras) if p.style.name == "Heading 1" and p.text == "TÀI LIỆU THAM KHẢO")
    body_txt = "\n".join(p.text for p in paras[ch1_idx:refs_idx])
    all_txt = "\n".join(p.text for p in paras) + "\n" + "\n".join(
        c.text for tbl in doc.tables for row in tbl.rows for c in row.cells
    )
    assert "Ghi chú kỹ thuật" not in all_txt
    assert "results/" not in body_txt
    assert "src/" not in body_txt
    for bad in ("**", "`", "](", "$$", "\\frac", "[^"):
        assert bad not in all_txt, bad


def test_fonts_all_times_new_roman(tmp_path: Path) -> None:
    out = build_docx(Path("report"), tmp_path / "out.docx")
    doc = docx.Document(str(out))
    all_runs = [r for p in doc.paragraphs for r in p.runs]
    all_runs.extend(r for tbl in doc.tables for row in tbl.rows for c in row.cells for p in c.paragraphs for r in p.runs)
    for r in all_runs:
        if r.font.name is None:
            continue
        assert r.font.name in ("Times New Roman", "Consolas"), r.font.name


def test_numbers_survive_conversion(tmp_path: Path) -> None:
    out = build_docx(Path("report"), tmp_path / "out.docx")
    doc = docx.Document(str(out))
    all_txt = "\n".join(p.text for p in doc.paragraphs) + "\n" + "\n".join(
        c.text for tbl in doc.tables for row in tbl.rows for c in row.cells
    )
    for num in ("3.174", "0,8714", "71,19%", "351"):
        assert num in all_txt, num
