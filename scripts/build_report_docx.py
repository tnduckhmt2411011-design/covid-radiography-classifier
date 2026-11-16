"""Chuyển toàn bộ báo cáo markdown trong `report/` sang một tệp `.docx` chuẩn CTUT.

Chạy: python -m scripts.build_report_docx --out report/dist/BaoCao_BTL_HocMay_Nhom10.docx
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import nsmap, qn
from docx.shared import Cm, Pt, RGBColor
from markdown_it import MarkdownIt
from PIL import Image

FONT_NAME = "Times New Roman"
CODE_FONT = "Consolas"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
if "m" not in nsmap:
    nsmap["m"] = MATH_NS


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


def extract_footnote_defs(md: str) -> dict[str, str]:
    """Trích các định nghĩa chú thích chân trang dạng `[^key]: nội dung`."""
    defs: dict[str, str] = {}
    for line in md.splitlines():
        m = re.match(r"^\[\^([^\]]+)\]:\s*(.+)$", line.strip())
        if m:
            defs[m.group(1)] = m.group(2).strip()
    return defs


def _set_run_font(run, font_name: str = FONT_NAME, size_pt: float | None = None) -> None:
    run.font.name = font_name
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), font_name)


def _translate_math_expr(expr: str) -> str:
    """Chuyển tập ký hiệu LaTeX nhỏ trong báo cáo sang ký tự Unicode chuẩn."""
    s = expr.strip()
    replacements = (
        (r"\pm", "±"),
        (r"\cdot", "·"),
        (r"\times", "×"),
        (r"\ge", "≥"),
        (r"\le", "≤"),
        (r"\in", "∈"),
        (r"\{", "{"),
        (r"\}", "}"),
        ("-", "−"),
    )
    for src, dst in replacements:
        s = s.replace(src, dst)
    return re.sub(r"\s+", " ", s)


def _add_inline_math_runs(para, expr: str, size_pt: float | None = None, bold: bool = False) -> None:
    """Render biểu thức toán trong dòng: biến chữ cái in nghiêng, toán tử/số viết thẳng."""
    cleaned = _translate_math_expr(expr)
    for tok in re.findall(r"[A-Za-z]+|[^A-Za-z]+", cleaned):
        run = para.add_run(tok)
        _set_run_font(run, FONT_NAME, size_pt=size_pt)
        if bold:
            run.bold = True
        if tok.isalpha():
            run.italic = True


def _omml_elem(tag: str) -> OxmlElement:
    return OxmlElement(f"m:{tag}")


def _omml_run(text: str, italic: bool = False) -> OxmlElement:
    r = _omml_elem("r")
    if not italic:
        rpr = _omml_elem("rPr")
        sty = _omml_elem("sty")
        sty.set(qn("m:val"), "p")
        rpr.append(sty)
        r.append(rpr)
    wrpr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(attr), "Cambria Math")
    wrpr.append(rf)
    r.append(wrpr)
    t = _omml_elem("t")
    t.text = text
    r.append(t)
    return r


def omml_fraction(num_runs: list[OxmlElement], den_runs: list[OxmlElement]) -> OxmlElement:
    """Tạo phần tử phân số OMML `m:f`."""
    frac = _omml_elem("f")
    num = _omml_elem("num")
    for el in num_runs:
        num.append(el)
    den = _omml_elem("den")
    for el in den_runs:
        den.append(el)
    frac.append(num)
    frac.append(den)
    return frac


def _add_display_equation(doc: Document, raw_expr: str) -> None:
    """Render công thức khối `$$...$$` bằng `m:oMathPara` và số công thức căn phải bằng tab."""
    inner = raw_expr.strip().strip("$").strip()
    eq_num = ""
    m_num = re.search(r"(?:\\qquad|\\quad)?\s*(\(\d+\.\d+\))\s*$", inner)
    if m_num:
        eq_num = m_num.group(1)
        inner = inner[: m_num.start()].strip()

    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    for val, pos in (("center", "4536"), ("right", "9072")):
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), val)
        tab.set(qn("w:pos"), pos)
        tabs.append(tab)
    pPr.append(tabs)

    tab_lead = p.add_run()
    _set_run_font(tab_lead, FONT_NAME)
    tab_lead.add_tab()

    omath_para = _omml_elem("oMathPara")
    omath = _omml_elem("oMath")
    m_frac = re.match(r"^(.+?)=\s*\\frac\{(.+?)\}\{(.+?)\}$", inner)
    if m_frac:
        lhs = _translate_math_expr(m_frac.group(1))
        for tok in re.findall(r"[A-Za-z]+|[^A-Za-z]+", lhs):
            omath.append(_omml_run(tok, italic=tok.isalpha()))
        omath.append(_omml_run(" = ", italic=False))
        num_txt = _translate_math_expr(m_frac.group(2))
        den_txt = _translate_math_expr(m_frac.group(3))
        num_els = [_omml_run(tok, italic=tok.isalpha()) for tok in re.findall(r"[A-Za-z]+|[^A-Za-z]+", num_txt)]
        den_els = [_omml_run(tok, italic=tok.isalpha()) for tok in re.findall(r"[A-Za-z]+|[^A-Za-z]+", den_txt)]
        omath.append(omml_fraction(num_els, den_els))
    else:
        txt = _translate_math_expr(inner)
        for tok in re.findall(r"[A-Za-z]+|[^A-Za-z]+", txt):
            omath.append(_omml_run(tok, italic=tok.isalpha()))
    omath_para.append(omath)
    p._p.append(omath_para)

    if eq_num:
        tab_end = p.add_run()
        _set_run_font(tab_end, FONT_NAME)
        tab_end.add_tab()
        num_run = p.add_run(eq_num)
        _set_run_font(num_run, FONT_NAME)


def _protect_math_and_footnotes(
    md: str,
) -> tuple[str, dict[str, str], dict[str, str]]:
    """Thay công thức khối, công thức trong dòng bằng thẻ tạm để markdown-it không làm mất `\\`."""
    blocks: dict[str, str] = {}
    inlines: dict[str, str] = {}
    out_lines: list[str] = []
    b_idx = 0
    i_idx = 0
    in_fence = False

    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        if re.match(r"^\$\$.+\$\$\s*$", line.strip()):
            key = f"MATHBLOCKTOKEN{b_idx}END"
            b_idx += 1
            blocks[key] = line.strip()
            out_lines.append("")
            out_lines.append(key)
            out_lines.append("")
            continue

        # Bảo vệ nội dung ngoài backtick có dấu $...$
        parts = re.split(r"(`[^`]*`)", line)
        for j in range(0, len(parts), 2):
            def _repl_math(m: re.Match[str]) -> str:
                nonlocal i_idx
                k = f"MATHINLINETOKEN{i_idx}END"
                i_idx += 1
                inlines[k] = m.group(1)
                return k

            parts[j] = re.sub(r"(?<!\\)\$([^$\n]+?)\$", _repl_math, parts[j])
        out_lines.append("".join(parts))

    return "\n".join(out_lines), blocks, inlines


def _resolve_image_path(src: str, base_dir: Path) -> Path:
    cand = (base_dir / src).resolve()
    if cand.exists():
        return cand
    if src.startswith("../"):
        alt = (base_dir / src.removeprefix("../")).resolve()
        if alt.exists():
            return alt
    raise FileNotFoundError(f"Không tìm thấy tệp ảnh '{src}' từ '{base_dir}'")


def _add_image_paragraph(doc: Document, src: str, base_dir: Path) -> None:
    img_path = _resolve_image_path(src, base_dir)
    with Image.open(img_path) as im:
        w_px, _ = im.size
        dpi = im.info.get("dpi", (150, 150))
        dpi_x = float(dpi[0]) if isinstance(dpi, tuple) and dpi[0] else 150.0
    width_cm = min(max((w_px / dpi_x) * 2.54, 10.0), 15.0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(img_path), width=Cm(width_cm))


def _render_inline_tokens(
    para,
    children,
    *,
    inline_math: Mapping[str, str],
    footnote_map: dict[str, int],
    keep_urls: bool = False,
    size_pt: float | None = None,
    force_bold: bool = False,
    force_italic: bool = False,
) -> None:
    bold = force_bold
    italic = force_italic
    link_href: str | None = None

    def _emit_text_segment(seg: str) -> None:
        # Tách math placeholder và footnote [^key]
        token_re = re.compile(r"(MATHINLINETOKEN\d+END|\[\^[^\]]+\])")
        for chunk in token_re.split(seg):
            if not chunk:
                continue
            if chunk in inline_math:
                _add_inline_math_runs(para, inline_math[chunk], size_pt=size_pt, bold=bold)
            elif chunk.startswith("[^") and chunk.endswith("]"):
                key = chunk[2:-1]
                num = footnote_map.setdefault(key, len(footnote_map) + 1)
                r = para.add_run(f"[{num}]")
                _set_run_font(r, FONT_NAME, size_pt=size_pt)
                r.font.superscript = True
            else:
                r = para.add_run(chunk)
                _set_run_font(r, FONT_NAME, size_pt=size_pt)
                if bold:
                    r.bold = True
                if italic:
                    r.italic = True

    for tok in children or []:
        t = tok.type
        if t == "text":
            _emit_text_segment(tok.content)
        elif t == "softbreak":
            _emit_text_segment(" ")
        elif t == "hardbreak":
            r = para.add_run()
            r.add_break()
        elif t == "code_inline":
            r = para.add_run(tok.content)
            _set_run_font(r, CODE_FONT, size_pt=size_pt if size_pt is not None else 11.0)
            if bold:
                r.bold = True
        elif t == "strong_open":
            bold = True
        elif t == "strong_close":
            bold = force_bold
        elif t == "em_open":
            italic = True
        elif t == "em_close":
            italic = force_italic
        elif t == "link_open":
            link_href = tok.attrGet("href")
        elif t == "link_close":
            if keep_urls and link_href and link_href.startswith("http"):
                r = para.add_run(f" ({link_href})")
                _set_run_font(r, FONT_NAME, size_pt=size_pt)
            link_href = None


def _style_booktabs_table(table, col_aligns: list[int]) -> None:
    """Định dạng bảng chuẩn Booktabs: không kẻ dọc, viền trên/dưới đậm, tiêu đề xám D9D9D9."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    tbl_pr = table._tbl.tblPr
    tbl_borders = tbl_pr.find(qn("w:tblBorders"))
    if tbl_borders is None:
        tbl_borders = OxmlElement("w:tblBorders")
        tbl_pr.append(tbl_borders)
    for edge in ("top", "bottom", "left", "right", "insideH", "insideV"):
        old = tbl_borders.find(qn(f"w:{edge}"))
        if old is not None:
            tbl_borders.remove(old)
        el = OxmlElement(f"w:{edge}")
        if edge in ("top", "bottom"):
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "12")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "000000")
        else:
            el.set(qn("w:val"), "none")
        tbl_borders.append(el)

    # Đặt cell margins gọn
    tbl_cell_mar = tbl_pr.find(qn("w:tblCellMar"))
    if tbl_cell_mar is None:
        tbl_cell_mar = OxmlElement("w:tblCellMar")
        tbl_pr.append(tbl_cell_mar)
    for side, w in (("top", "45"), ("bottom", "45"), ("left", "85"), ("right", "85")):
        old = tbl_cell_mar.find(qn(f"w:{side}"))
        if old is not None:
            tbl_cell_mar.remove(old)
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), w)
        el.set(qn("w:type"), "dxa")
        tbl_cell_mar.append(el)

    for r_idx, row in enumerate(table.rows):
        tr_pr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_pr.append(cant_split)
        if r_idx == 0:
            tr_pr.append(OxmlElement("w:tblHeader"))
        for c_idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            if r_idx == 0:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "D9D9D9")
                tc_pr.append(shd)
                tc_borders = OxmlElement("w:tcBorders")
                bot = OxmlElement("w:bottom")
                bot.set(qn("w:val"), "single")
                bot.set(qn("w:sz"), "6")
                bot.set(qn("w:space"), "0")
                bot.set(qn("w:color"), "000000")
                tc_borders.append(bot)
                tc_pr.append(tc_borders)
            align = col_aligns[c_idx] if c_idx < len(col_aligns) else WD_ALIGN_PARAGRAPH.LEFT
            for p in cell.paragraphs:
                p.alignment = align
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.15


def _parse_align(attr_style: str | None) -> int:
    if not attr_style:
        return WD_ALIGN_PARAGRAPH.LEFT
    if "right" in attr_style:
        return WD_ALIGN_PARAGRAPH.RIGHT
    if "center" in attr_style:
        return WD_ALIGN_PARAGRAPH.CENTER
    return WD_ALIGN_PARAGRAPH.LEFT


def _is_caption_text(inline_tok) -> str | None:
    """Trả về 'Caption Table' hoặc 'Caption Figure' nếu đoạn chỉ gồm nhãn chú thích in đậm."""
    raw = (inline_tok.content or "").strip()
    if re.match(r"^\*\*(Bảng)\s+[A-Z0-9]+\.\d+", raw):
        return "Caption Table"
    if re.match(r"^\*\*(Hình)\s+[A-Z0-9]+\.\d+", raw):
        return "Caption Figure"
    return None


def _is_table_note_text(inline_tok) -> bool:
    raw = (inline_tok.content or "").strip()
    return raw.startswith("*(") and raw.endswith(")*")


def render_markdown(
    doc: Document,
    md: str,
    base_dir: Path,
    *,
    keep_urls: bool = False,
    footnote_defs: Mapping[str, str] | None = None,
    footnote_state: dict[str, int] | None = None,
) -> None:
    """Kết xuất nội dung markdown (đã bỏ Ghi chú kỹ thuật) thành các phần tử Word."""
    local_defs = dict(footnote_defs or {})
    local_defs.update(extract_footnote_defs(md))
    # Loại bỏ các dòng định nghĩa [^key]: ... khỏi thân markdown trước khi parse
    cleaned_lines = [l for l in md.splitlines() if not re.match(r"^\[\^([^\]]+)\]:\s*", l.strip())]
    protected, block_math, inline_math = _protect_math_and_footnotes("\n".join(cleaned_lines))

    parser = MarkdownIt("commonmark").enable("table")
    tokens = parser.parse(protected)
    fn_map = footnote_state if footnote_state is not None else {}
    fn_start_count = len(fn_map)

    list_stack: list[tuple[str, int]] = []  # ("bullet"|"ordered", counter)
    in_blockquote = False
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        t = tok.type

        if t == "heading_open":
            level = int(tok.tag[1])
            inline_tok = tokens[i + 1]
            style_name = f"Heading {min(level, 3)}"
            p = doc.add_paragraph(style=doc.styles[style_name])
            _render_inline_tokens(
                p,
                inline_tok.children,
                inline_math=inline_math,
                footnote_map=fn_map,
                keep_urls=keep_urls,
            )
            i += 3
            continue

        if t == "blockquote_open":
            in_blockquote = True
            i += 1
            continue
        if t == "blockquote_close":
            in_blockquote = False
            i += 1
            continue

        if t == "bullet_list_open":
            list_stack.append(("bullet", 0))
            i += 1
            continue
        if t == "bullet_list_close":
            list_stack.pop()
            i += 1
            continue
        if t == "ordered_list_open":
            start = int(tok.attrGet("start") or 1)
            list_stack.append(("ordered", start - 1))
            i += 1
            continue
        if t == "ordered_list_close":
            list_stack.pop()
            i += 1
            continue
        if t == "list_item_open":
            if list_stack and list_stack[-1][0] == "ordered":
                kind, cnt = list_stack[-1]
                list_stack[-1] = (kind, cnt + 1)
            i += 1
            continue
        if t == "list_item_close":
            i += 1
            continue

        if t == "fence":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "F5F5F5")
            pPr.append(shd)
            r = p.add_run(tok.content.rstrip("\n"))
            _set_run_font(r, CODE_FONT, size_pt=10.0)
            i += 1
            continue

        if t == "hr":
            i += 1
            continue

        if t == "table_open":
            rows_data: list[tuple[bool, list[tuple[int, object]]]] = []
            col_aligns: list[int] = []
            j = i + 1
            in_head = False
            cur_row: list[tuple[int, object]] = []
            cur_align = WD_ALIGN_PARAGRAPH.LEFT
            while j < n and tokens[j].type != "table_close":
                tt = tokens[j].type
                if tt == "thead_open":
                    in_head = True
                elif tt == "thead_close":
                    in_head = False
                elif tt == "tr_open":
                    cur_row = []
                elif tt == "tr_close":
                    rows_data.append((in_head, cur_row))
                elif tt in ("th_open", "td_open"):
                    cur_align = _parse_align(tokens[j].attrGet("style"))
                    if in_head:
                        col_aligns.append(cur_align)
                elif tt == "inline":
                    cur_row.append((cur_align, tokens[j]))
                j += 1

            if rows_data:
                ncols = max(len(r[1]) for r in rows_data)
                tbl = doc.add_table(rows=len(rows_data), cols=ncols)
                for r_idx, (is_hdr, row_cells) in enumerate(rows_data):
                    for c_idx, (_, cell_inline) in enumerate(row_cells):
                        p = tbl.rows[r_idx].cells[c_idx].paragraphs[0]
                        _render_inline_tokens(
                            p,
                            cell_inline.children,
                            inline_math=inline_math,
                            footnote_map=fn_map,
                            keep_urls=keep_urls,
                            size_pt=10.5,
                            force_bold=is_hdr,
                        )
                _style_booktabs_table(tbl, col_aligns)
            i = j + 1
            continue

        if t == "paragraph_open":
            inline_tok = tokens[i + 1]
            raw_content = inline_tok.content.strip()

            # Công thức khối
            if raw_content in block_math:
                _add_display_equation(doc, block_math[raw_content])
                i += 3
                continue

            # Đoạn chỉ có một ảnh
            children = inline_tok.children or []
            if len(children) == 1 and children[0].type == "image":
                src = children[0].attrGet("src") or ""
                _add_image_paragraph(doc, src, base_dir)
                i += 3
                continue

            cap_style = _is_caption_text(inline_tok)
            if cap_style:
                p = doc.add_paragraph(style=doc.styles[cap_style])
                p.alignment = doc.styles[cap_style].paragraph_format.alignment
                _render_inline_tokens(
                    p,
                    children,
                    inline_math=inline_math,
                    footnote_map=fn_map,
                    keep_urls=keep_urls,
                    size_pt=11.0,
                    force_bold=True,
                )
            elif _is_table_note_text(inline_tok):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(6)
                _render_inline_tokens(
                    p,
                    children,
                    inline_math=inline_math,
                    footnote_map=fn_map,
                    keep_urls=keep_urls,
                    size_pt=10.5,
                    force_italic=True,
                )
            elif list_stack:
                kind, cnt = list_stack[-1]
                depth = len(list_stack)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.8 * depth + 0.5)
                p.paragraph_format.first_line_indent = Cm(-0.45)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(3)
                prefix = "• " if kind == "bullet" else f"{cnt}. "
                r_pre = p.add_run(prefix)
                _set_run_font(r_pre, FONT_NAME)
                _render_inline_tokens(
                    p,
                    children,
                    inline_math=inline_math,
                    footnote_map=fn_map,
                    keep_urls=keep_urls,
                )
            elif in_blockquote:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1.0)
                p.paragraph_format.right_indent = Cm(0.5)
                p.paragraph_format.first_line_indent = Cm(0)
                _render_inline_tokens(
                    p,
                    children,
                    inline_math=inline_math,
                    footnote_map=fn_map,
                    keep_urls=keep_urls,
                )
            else:
                p = doc.add_paragraph()
                _render_inline_tokens(
                    p,
                    children,
                    inline_math=inline_math,
                    footnote_map=fn_map,
                    keep_urls=keep_urls,
                )
            i += 3
            continue

        i += 1

    # Chú thích chân trang phát sinh trong đoạn vừa render (nếu có)
    new_fns = [(k, num) for k, num in fn_map.items() if num > fn_start_count and k in local_defs]
    if new_fns:
        for key, num in sorted(new_fns, key=lambda x: x[1]):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            r_num = p.add_run(f"[{num}] ")
            _set_run_font(r_num, FONT_NAME, size_pt=10.5)
            r_num.bold = True
            r_txt = p.add_run(local_defs[key])
            _set_run_font(r_txt, FONT_NAME, size_pt=10.5)


def build_docx(report_dir: Path, out_path: Path) -> Path:
    """Dựng tệp .docx hoàn chỉnh từ thư mục `report/`."""
    raise NotImplementedError("Implemented in Task B4")
