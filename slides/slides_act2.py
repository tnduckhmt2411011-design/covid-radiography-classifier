"""Slide 10–18: chương 3 (RQ1 và RQ2) và chương 4 (mô hình nhìn vào đâu)."""

from __future__ import annotations

from . import svgkit as k
from .data import D, fmt, fmt_ci, fmt_delta, fmt_int, fmt_pct
from .texts import D4

CH3 = "CHƯƠNG 3 · KẾT QUẢ RQ1 VÀ RQ2"
CH4 = "CHƯƠNG 4 · MÔ HÌNH NHÌN VÀO ĐÂU"


def divider(filename: str, *, chapter: str, title: str, page_no: int, body: str) -> k.Page:
    """Slide mở hồi: nền tối, chương và câu hỏi, không số."""
    page = k.Page(filename, layout="divider", master="dark", kicker=None, title=None,
                  page_no=page_no)
    page.content(
        page.text("chapter", 82, 210, chapter, size=19, color=k.TEAL_LIGHT, weight="bold"),
        page.line("divider-rule", 82, 232, 170, 232, stroke=k.TEAL, width=3),
        page.slot("title", 82, 320, k.wrap(title, 52, k.CONTENT_W - 80, weight="bold"),
                  size=52, color=k.TEXT_ON_DARK, step=58,
                  carrier_gid="divider-title-carrier", bounds=(82, 268, k.CONTENT_W, 130)),
        page.text("divider-body", 82, 430, body, size=22, color=k.SOFT_ON_DARK,
                  max_width=k.CONTENT_W - 260, line_h=32),
    )
    return page


def chart_page(filename: str, *, kicker: str, title: str, source: str, page_no: int,
               image: str, image_w: int, image_h: int, cards: list[tuple[str, str, str]],
               note: tuple[str, str] | None = None) -> k.Page:
    """Khung chung cho slide biểu đồ: hình bên trái, các thẻ số bên phải.

    ``cards`` là danh sách (khóa, giá trị, chú thích); ``note`` là (chú thích dưới
    hình, màu nền).
    """
    page = k.Page(filename, layout="content", kicker=kicker, title=title, source=source,
                  page_no=page_no)
    caption = note[0] if note else ""
    lines = k.wrap(caption, k.SIZE_SMALL, image_w - 24) if caption else []
    card_h = image_h + 46 + (len(lines) * 28 if lines else 0)
    zone = page.zone("chart", 82, 208, image_w + 32, card_h)
    zone.card()
    zone.image("figure", image, 98, 222, image_w, image_h)
    if lines:
        zone.text("chart-caption", 110, 222 + image_h + 34, caption, size=k.SIZE_SMALL,
                  color=k.INK, max_width=image_w - 24, line_h=28)
    page.content(zone.done())

    x = 82 + image_w + 44
    width = 1198 - x
    for index, (key, value, caption_text) in enumerate(cards[:3]):
        y = 214 + index * 132
        zone = page.zone(f"card-{key}", x, y, width, 124)
        zone.card()
        zone.text(f"card-{key}-cap", x + 16, y + 34, caption_text, size=19, color=k.INK_SOFT,
                  max_width=width - 32, line_h=24)
        zone.text(f"card-{key}-val", x + 16, y + 98, value, size=38, color=k.TEAL, weight="bold")
        page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 10
def slide_10() -> k.Page:
    return divider("10_mo_chuong3.svg", chapter="CHƯƠNG 3", page_no=10,
                   title="Kết quả trên 3.174 ảnh validation",
                   body="Câu hỏi 1: nhóm đặc trưng nào lấy được tín hiệu nhất. "
                        "Câu hỏi 2: bộ phân loại nào phù hợp với 152 chiều đặc trưng.")


# ------------------------------------------------------------------ slide 11
def slide_11() -> k.Page:
    rows = sorted(D["rq1"], key=lambda row: row["macro_f1"], reverse=True)
    cards = [(row["key"], fmt(row["macro_f1"]), f"{_NAME_RQ1[row['key']]} · CI {fmt_ci(*row['ci'])}")
             for row in rows]
    return chart_page(
        "11_rq1.svg", kicker=CH3, page_no=11,
        title="Nhóm ghép dẫn đầu với 0,8599 ± 0,0030",
        source="Nguồn: results/report_rq1/r1_summary.csv · "
               "results/b0_majority, a0_shortcut/metrics.json",
        image="../images/fig_rq1_ci.png", image_w=736, image_h=274,
        cards=cards,
        note=("Hai mốc nền B0 = 0,1627 và A0 = 0,2397 nằm ngoài khoảng tin cậy của cả bốn "
              "nhóm đặc trưng.", k.AMBER_PALE),
    )


_NAME_RQ1 = {"ghep": "Ghép 152 chiều", "glcmlbp": "GLCM + LBP 88", "hist": "Histogram 64",
             "hog": "HOG 10.404"}


# ------------------------------------------------------------------ slide 12
def slide_12() -> k.Page:
    ghep = next(row for row in D["rq1"] if row["key"] == "ghep")
    hog = next(row for row in D["rq1"] if row["key"] == "hog")
    glcmlbp = next(row for row in D["rq1"] if row["key"] == "glcmlbp")
    cards = [
        ("ghép", fmt_delta(ghep["delta"]["diff"]),
         f"Ghép − Histogram · {fmt_ci(*ghep['delta']['ci'])}"),
        ("glcm", fmt_delta(glcmlbp["delta"]["diff"]),
         f"GLCM + LBP − Histogram · {fmt_ci(*glcmlbp['delta']['ci'])}"),
        ("hog", fmt_delta(hog["delta"]["diff"]),
         f"HOG − Histogram · {fmt_ci(*hog['delta']['ci'])}"),
    ]
    page = chart_page(
        "12_rq1_delta.svg", kicker=CH3, page_no=12,
        title="Chỉ nói “tốt hơn” khi khoảng tin cậy không chứa 0",
        source="Nguồn: results/report_rq1/r1_bootstrap_vs_reference.csv · "
               "results/rq1_cost_rank_record.md",
        image="../images/fig_rq1_delta.png", image_w=736, image_h=244,
        cards=cards,
        note=(f"Chi phí cũng đi theo cỡ chiều: ghep tốn {fmt(D['rq1_cost']['ratio'], 1)} lần hist "
              "cho mỗi ảnh. Cam = khoảng tin cậy chứa 0.", k.AMBER_PALE),
    )
    return page


# ------------------------------------------------------------------ slide 13
def slide_13() -> k.Page:
    svm = next(row for row in D["rq2"] if row["key"] == "svm")
    rf = next(row for row in D["rq2"] if row["key"] == "rf")
    dt = next(row for row in D["rq2"] if row["key"] == "dt")
    delta = svm["delta"]
    cards = [
        ("svm", fmt(svm["macro_f1"]), f"SVM RBF · CI {fmt_ci(*svm['ci'])}"),
        ("rf", fmt(rf["macro_f1"]), f"Random Forest · CI {fmt_ci(*rf['ci'])}"),
        ("dt", fmt(dt["macro_f1"]), f"Decision Tree · CI {fmt_ci(*dt['ci'])}"),
    ]
    return chart_page(
        "13_rq2.svg", kicker=CH3, page_no=13,
        title="SVM RBF 0,9024, hơn Random Forest 0,0442",
        source="Nguồn: results/report_rq2/r1_summary.csv · "
               "results/report_rq2/r1_bootstrap_vs_reference.csv",
        image="../images/fig_rq2_ci.png", image_w=736, image_h=274,
        cards=cards,
        note=(f"Δ SVM − RF = {fmt_delta(delta['diff'])} {fmt_ci(*delta['ci'])}; "
              f"validation còn lại {fmt_int(D['val_errors']['n'])} lỗi, trong đó "
              f"{fmt_int(D['val_errors']['normal_lung_opacity'])} lỗi thuộc cặp "
              "Normal ↔ Lung_Opacity.", k.TEAL_PALE),
    )


# ------------------------------------------------------------------ slide 14
def slide_14() -> k.Page:
    return divider("14_mo_chuong4.svg", chapter="CHƯƠNG 4", page_no=14,
                   title="Mô hình nhìn vào đâu để phân loại?",
                   body="Câu hỏi 3: mô hình dựa vào vùng phổi, hay vào vùng xung quanh. "
                        "Che và cắt vùng phổi rồi đo lại trên chính ảnh đó.")


# ------------------------------------------------------------------ slide 15
def slide_15() -> k.Page:
    scenarios = D["rq3"]["scenarios"]
    drop = D["rq3"]["diffs"][("lung_to_lung", "orig_to_orig")]
    cards = [
        ("orig", fmt(scenarios["orig_to_orig"]["macro_f1"]), "Ảnh gốc · CI " + fmt_ci(*scenarios["orig_to_orig"]["ci"])),
        ("lung", fmt(scenarios["lung_to_lung"]["macro_f1"]), "Chỉ phổi · CI " + fmt_ci(*scenarios["lung_to_lung"]["ci"])),
        ("out", fmt(scenarios["out_to_out"]["macro_f1"]), "Ngoài phổi · CI " + fmt_ci(*scenarios["out_to_out"]["ci"])),
    ]
    return chart_page(
        "15_rq3.svg", kicker=CH4, page_no=15,
        title="Che phổi làm mất 0,0535 macro-F1",
        source="Nguồn: results/report_rq3/r1_summary.csv · "
               "results/report_rq3/r3_shortcut_bootstrap.csv",
        image="../images/fig_rq3_scenarios.png", image_w=736, image_h=281,
        cards=cards,
        note=(f"Δ chỉ phổi − gốc = {fmt_delta(drop['diff'])} "
              f"{fmt_ci(*drop['ci'])}; khoảng tin cậy không chứa 0.", k.AMBER_PALE),
    )


# ------------------------------------------------------------------ slide 16
def slide_16() -> k.Page:
    scenarios = D["rq3"]["scenarios"]
    full = scenarios["orig_to_orig"]["macro_f1"]
    outside = scenarios["out_to_out"]["macro_f1"]
    diff = D["rq3"]["diffs"][("orig_to_orig", "out_to_out")]
    page = k.Page("16_rq3_ngoai_phoi.svg", layout="content", kicker=CH4, page_no=16,
                  title="Che sạch phổi vẫn còn 0,8921 — và khoảng tin cậy chứa 0",
                  source="Nguồn: results/report_rq3/r3_shortcut_bootstrap.csv · "
                         "results/rq3_mask_check/")
    zone = page.zone("pair", 82, 214, 1116, 244)
    zone.card()
    zone.text("pair-full-cap", 112, 258, "Ảnh gốc", size=19, color=k.INK_SOFT)
    zone.text("pair-full", 112, 342, fmt(full), size=96, color=k.TEAL, weight="bold")
    zone.text("pair-out-cap", 470, 258, "Chỉ vùng ngoài phổi", size=19, color=k.INK_SOFT)
    zone.text("pair-out", 470, 342, fmt(outside), size=96, color=k.TEAL, weight="bold")
    zone.text("pair-delta", 840, 300, f"Δ {fmt_delta(diff['diff'])}", size=44, color=k.AMBER,
              weight="bold")
    zone.text("pair-delta-ci", 840, 348, f"{fmt_ci(*diff['ci'])}", size=21, color=k.INK_SOFT)
    zone.text("pair-delta-flag", 840, 376, "khoảng tin cậy chứa 0", size=19, color=k.AMBER,
              weight="bold")
    zone.text("pair-delta-note", 840, 408,
              "Không đủ căn cứ để nói vùng phổi là nguồn tín hiệu duy nhất.",
              size=21, color=k.INK, max_width=336, line_h=26)
    page.content(zone.done())

    page.content(page.text("mask-label", 82, 476, "CÁCH CHE VÙNG PHỔI TRÊN ẢNH CỦA BỐN LỚP",
                           size=19, color=k.TEAL, weight="bold"))
    classes = ["COVID", "Lung_Opacity", "Normal", "Viral_Pneumonia"]
    for index, label in enumerate(classes):
        x = 82 + index * 284
        zone = page.zone(f"mask{index}", x, 500, 276, 108)
        zone.card()
        zone.image(f"mask-image{index}", f"../images/mask_strip_{label}.png", x + 10, 510, 256, 26)
        zone.text(f"mask-cap{index}", x + 14, 570, _MASK_NAME[label], size=19,
                  color=k.INK_SOFT, max_width=252)
        page.content(zone.done())
    return page


_MASK_NAME = {
    "COVID": "COVID-19: ảnh gốc, chỉ phổi, ngoài phổi",
    "Lung_Opacity": "Lung Opacity: ảnh gốc, chỉ phổi, ngoài phổi",
    "Normal": "Normal: ảnh gốc, chỉ phổi, ngoài phổi",
    "Viral_Pneumonia": "Viral Pneumonia: ảnh gốc, chỉ phổi, ngoài phổi",
}


# ------------------------------------------------------------------ slide 17
def slide_17() -> k.Page:
    blocks = {block["block"]: block for block in D["permutation"]["outside_only"]}
    lung = {block["block"]: block for block in D["permutation"]["lung_only"]}
    cards = [
        ("glcm", fmt(lung["glcm_60"]["importance"]), "Chỉ phổi · GLCM 60 chiều"),
        ("lbp", fmt(blocks["lbp_28"]["importance"]), "Ngoài phổi · LBP 28 chiều"),
        ("hist", fmt(blocks["hist_64"]["importance"]), "Ngoài phổi · Histogram 64 chiều"),
    ]
    return chart_page(
        "17_rq3_perm.svg", kicker=CH4, page_no=17,
        title="Khi buộc nhìn trong phổi, GLCM mới lên tiếng",
        source="Nguồn: results/rq3_permutation_importance.csv",
        image="../images/fig_rq3_perm.png", image_w=736, image_h=251,
        cards=cards,
        note=(f"Xáo trộn GLCM trong vùng phổi làm mất {fmt(lung['glcm_60']['importance'])} "
              f"macro-F1; xáo trộn LBP ngoài phổi làm mất "
              f"{fmt(blocks['lbp_28']['importance'])}.", k.TEAL_PALE),
    )


# ------------------------------------------------------------------ slide 18
def slide_18() -> k.Page:
    page = k.Page("18_phan_chung.svg", layout="content", kicker=CH4, page_no=18,
                  title="Ba giả thuyết, bốn điều kiện bác bỏ",
                  source="Nguồn: report/04 mục 4.3 · results/threshold_v3.md (R3)")
    page.content(page.text("hyp-label", 82, 222, "BA GIẢ THUYẾT (CHƯA KIỂM CHỨNG)", size=19,
                           color=k.TEAL, weight="bold"))
    hypotheses = [
        ("Tuổi nhi", "Ảnh bệnh nhi có độ sáng và độ tương phản khác ảnh người lớn"),
        ("Ký hiệu thiết bị", "Mỗi máy X-quang để lại dấu vận riêng trên ảnh"),
        ("Covariate shift", "Tập test khác train về phân bố nguồn ảnh"),
    ]
    for index, (name, detail) in enumerate(hypotheses):
        y = 250 + index * 106
        zone = page.zone(f"hyp{index}", 82, y, 548, 96)
        zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
        zone.text(f"hyp{index}-name", 102, y + 36, name, size=21, color=k.INK, weight="bold")
        zone.text(f"hyp{index}-tag", 462, y + 36, "chưa kiểm chứng", size=19, color=k.AMBER,
                  weight="bold")
        zone.text(f"hyp{index}-note", 102, y + 64, detail, size=19, color=k.INK_SOFT, max_width=500)
        page.content(zone.done())

    page.content(page.text("fals-label", 640, 222, "BỐN ĐIỀU KIỆN BÁC BỎ", size=19,
                           color=k.TEAL, weight="bold"))
    conditions = [
        "Δ của kịch bản “ngoài phổi” mà khoảng tin cậy chứa 0",
        "Macro-F1 test nằm ngoài khoảng tin cậy của val",
        "Permutation importance khối ngoài phổi về 0",
        "Mô hình chỉ ngoài phổi tụng xuống dưới mốc A0",
    ]
    zone = page.zone("fals", 640, 250, 558, 218)
    zone.card()
    for index, item in enumerate(conditions):
        y = 292 + index * 42
        zone.text(f"cond{index}-num", 660, y, f"{index + 1}", size=21, color=k.TEAL_LIGHT,
                  weight="bold")
        zone.text(f"cond{index}-text", 688, y, item, size=21, color=k.INK, max_width=482)
    page.content(zone.done())
    page.content(k.note_zone(page, "d4-note", 640, 490, 558,
                             "Quy tắc D4: " + D4, fill=k.TEAL_PALE, size=21, line_h=30))
    return page


def pages():
    return [slide_10(), slide_11(), slide_12(), slide_13(), slide_14(), slide_15(), slide_16(),
            slide_17(), slide_18()]
