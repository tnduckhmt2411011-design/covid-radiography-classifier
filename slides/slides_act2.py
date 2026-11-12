"""Slide 10–18: chương 3 (RQ1 và RQ2) và chương 4 (mô hình nhìn vào đâu)."""

from __future__ import annotations

from . import svgkit as k
from .data import D, fmt, fmt_ci, fmt_delta, fmt_int, fmt_pct, fmt_seconds
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
    ghep = next(row for row in D["rq1"] if row["key"] == "ghep")
    rules = D["rules"]
    ghep = next(row for row in D["rq1"] if row["key"] == "ghep")
    rules = D["rules"]
    rows = sorted(D["rq1"], key=lambda row: row["macro_f1"], reverse=True)
    cards = [(row["key"], fmt(row["macro_f1"]), f"{_NAME_RQ1[row['key']]} · CI {fmt_ci(*row['ci'])}")
             for row in rows]
    return chart_page(
        "11_rq1.svg", kicker=CH3, page_no=11,
        title=f"Nhóm ghép dẩn đầu với {fmt(ghep['macro_f1'])} ± {fmt(ghep['std'], 4)}",
        source="Nguồn: results/report_rq1/r1_summary.csv · "
               "results/b0_majority, a0_shortcut/metrics.json",
        image="../images/fig_rq1_ci.png", image_w=736, image_h=274,
        cards=cards,
        note=(f"Hai mốc nền B0 = {fmt(D['baselines']['b0'])} và A0 = {fmt(D['baselines']['a0'])} nằm ngoài khoảng tin cậy của cả bốn "
               "nhóm đặc trưng. RQ1 đo với Random Forest cố định 500 cây, không tinh chỉnh siêu tham số.", k.AMBER_PALE),
    )


_NAME_RQ1 = {"ghep": "Ghép 152 chiều", "glcmlbp": "GLCM + LBP 88", "hist": "Histogram 64",
             "hog": "HOG 10.404"}


# ------------------------------------------------------------------ slide 12
def slide_12() -> k.Page:
    rules = D["rules"]
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
        title=f"Chỉ ghi nhận “tốt hơn” khi Δ ≥ {fmt(rules['delta_threshold'], 3)} và CI không chứa 0",
        source="Nguồn: results/report_rq1/r1_bootstrap_vs_reference.csv · "
               "results/rq1_cost_rank_record.md",
        image="../images/fig_rq1_delta.png", image_w=736, image_h=244,
        cards=cards,
        note=(f"Chi phí do phép trích quyết định, không do số chiều: HOG {fmt_int(D['features']['hog'])} chiều tốn {fmt_seconds(D['rq1_cost']['by_group']['hog']['per_image'])}/ảnh, "
               f"GLCM + LBP {D['features']['glcm'] + D['features']['lbp']} chiều tốn {fmt_seconds(D['rq1_cost']['by_group']['glcmlbp']['per_image'])}/ảnh. "
               "Cam = khoảng tin cậy chứa 0.", k.AMBER_PALE),
    )
    return page


# ------------------------------------------------------------------ slide 13
def slide_13() -> k.Page:
    rf_rq1 = next(row for row in D["rq1"] if row["key"] == "ghep")
    rf_rq2 = next(row for row in D["rq2"] if row["key"] == "rf")
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
               "Normal ↔ Lung_Opacity. Random Forest ở RQ2 chọn siêu tham số bằng CV nên ra "
               f"{fmt(rf_rq2['macro_f1'])}, gần bằng Random Forest cố định {fmt(rf_rq1['macro_f1'])} ở RQ1.", k.TEAL_PALE),
    )


# ------------------------------------------------------------------ slide 14
def slide_14() -> k.Page:
    return divider("14_mo_chuong4.svg", chapter="CHƯƠNG 4", page_no=14,
                   title="Nếu che mất vùng phổi thì sao?",
                   body="Câu hỏi 3: che và cắt theo mask phổi có làm "
                        "đổi macro-F1 không. Năm kịch bản: huần luyện "
                        "và đánh giá cùng một chế độ ảnh, "
                        "rồi đo lại trên cùng 3.174 ảnh validation. "
                        "Kịch bản cho biết vùng đó có đủ tín "
                        "hiệu không, không cho biết mô hình gốc dựa "
                        "vào đâu.")


# ------------------------------------------------------------------ slide 15
def slide_15() -> k.Page:
    scenarios = D["rq3"]["scenarios"]
    lung = scenarios["lung_to_lung"]["macro_f1"]
    outside = scenarios["out_to_out"]["macro_f1"]
    gap_lung_out = D["rq3"]["diffs"][("lung_to_lung", "out_to_out")]
    cards = [
        ("orig", fmt(scenarios["orig_to_orig"]["macro_f1"]),
         "Gốc → gốc · CI " + fmt_ci(*scenarios["orig_to_orig"]["ci"])),
        ("lung", fmt(lung),
         "Chỉ phổi → chỉ phổi · CI "
         + fmt_ci(*scenarios["lung_to_lung"]["ci"])),
        ("out", fmt(outside),
         "Ngoài phổi → ngoài phổi · CI "
         + fmt_ci(*scenarios["out_to_out"]["ci"])),
    ]
    return chart_page(
        "15_rq3.svg", kicker=CH4, page_no=15,
        title="Giữ lại vùng phổi làm mất "
              f"{fmt(abs(scenarios['lung_to_lung']['macro_f1'] - scenarios['orig_to_orig']['macro_f1']))}",
        source="Nguồn: results/report_rq3/r1_summary.csv · "
               "results/report_rq3/r3_shortcut_bootstrap.csv",
        image="../images/fig_rq3_scenarios.png", image_w=736, image_h=281,
        cards=cards,
        note=(f"Quy ước A → B: huần luyện trên ảnh dạng A, "
              f"đánh giá trên ảnh dạng B. Chỉ phổi thua gốc "
              f"{fmt_delta(D['rq3']['diffs'][('lung_to_lung', 'orig_to_orig')]['diff'])}; "
              f"chỉ ngoài phổi thua chỉ phổi "
              f"{fmt_delta(gap_lung_out['diff'])} "
              f"{fmt_ci(*gap_lung_out['ci'])} — không chứa 0.",
              k.AMBER_PALE),
    )


# ------------------------------------------------------------------ slide 16
def slide_16() -> k.Page:
    scenarios = D["rq3"]["scenarios"]
    full = scenarios["orig_to_orig"]["macro_f1"]
    outside = scenarios["out_to_out"]["macro_f1"]
    diff = D["rq3"]["diffs"][("orig_to_orig", "out_to_out")]
    page = k.Page("16_rq3_ngoai_phoi.svg", layout="content", kicker=CH4, page_no=16,
                  title=f"Che sạch phổi vẫn còn {fmt(outside)} macro-F1",
                  source="Nguồn: results/report_rq3/r3_shortcut_bootstrap.csv · "
                         "results/rq3_mask_check/ · slides/assets/mask_trio.png")
    zone = page.zone("trio", 82, 214, 624, 316)
    zone.card()
    zone.image("trio-image", "../images/mask_trio.png", 98, 238, 592, 197)
    zone.text("trio-cap", 98, 466, "Ba chế độ của một ảnh validation",
              size=19, color=k.INK_SOFT)
    zone.text("trio-cap2", 98, 494,
              "Ảnh gốc · chỉ giữ vùng phổi · chỉ giữ "
              "vùng ngoài phổi. Cả ba đều là ảnh split val.",
              size=19, color=k.INK, max_width=592, line_h=26)
    page.content(zone.done())

    zone = page.zone("pair", 730, 214, 468, 396)
    zone.card()
    zone.text("pair-full-cap", 756, 252, "Ảnh gốc (gốc → gốc)", size=19,
              color=k.INK_SOFT)
    zone.text("pair-full", 756, 316, fmt(full), size=72, color=k.TEAL, weight="bold")
    zone.text("pair-out-cap", 756, 372,
              "Chỉ vùng ngoài phổi (ngoài phổi → ngoài phổi)",
              size=19, color=k.INK_SOFT)
    zone.text("pair-out", 756, 436, fmt(outside), size=72, color=k.TEAL, weight="bold")
    zone.line("pair-rule", 756, 476, 1172, 476, stroke=k.LINE)
    zone.text("pair-delta", 756, 512,
              f"Δ {fmt_delta(diff['diff'])} {fmt_ci(*diff['ci'])}", size=26, color=k.AMBER,
              weight="bold")
    zone.text("pair-delta-flag", 756, 542, "khoảng tin cậy của hiệu chứa 0",
              size=19, color=k.AMBER, weight="bold")
    zone.text("pair-note", 756, 566,
              "Chưa đủ căn cứ để nói vùng phổi là "
              "nguồn tín hiệu duy nhất.",
              size=19, color=k.INK, max_width=416, line_h=26)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 17
def slide_17() -> k.Page:
    blocks = {block["block"]: block for block in D["permutation"]["outside_only"]}
    lung = {block["block"]: block for block in D["permutation"]["lung_only"]}
    glcm_out, lbp_out = blocks["glcm_60"], blocks["lbp_28"]
    gap = abs(glcm_out["importance"] - lbp_out["importance"])
    noise = max(glcm_out["std"], lbp_out["std"])
    cards = [
        ("glcm", fmt(lung["glcm_60"]["importance"]), "Chỉ phổi · GLCM 60 chiều"),
        ("lbp", fmt(blocks["lbp_28"]["importance"]), "Ngoài phổi · LBP 28 chiều"),
        ("hist", fmt(blocks["hist_64"]["importance"]), "Ngoài phổi · Histogram 64 chiều"),
    ]
    return chart_page(
        "17_rq3_perm.svg", kicker=CH4, page_no=17,
        title=f"GLCM cao nhất khi chỉ nhìn trong phổi: {fmt(lung['glcm_60']['importance'])}",
        source="Nguồn: results/rq3_permutation_importance.csv",
        image="../images/fig_rq3_perm.png", image_w=736, image_h=251,
        cards=cards,
        note=(f"GLCM ngoài phổi đạt {fmt(glcm_out['importance'])} và LBP "
              f"{fmt(lbp_out['importance'])}: chênh {fmt(gap, 4)}, nhỏ hơn độ "
              f"lịch {fmt(noise, 4)} của 10 lần xáo trộn, nên không "
              f"xếp hạng hai khối này. Mức giảm chưa chuẩn hóa "
              f"theo cỡ khối (60 chiều so với 28).", k.AMBER_PALE),
    )


# ------------------------------------------------------------------ slide 18
def slide_18() -> k.Page:
    page = k.Page("18_phan_chung.svg", layout="content", kicker=CH4, page_no=18,
                  title="Ba giả thuyết, bốn câu hỏi cần bằng chứng",
                  source="Nguồn: report/04_hoc_loi_tat_rq3.md mục 4.3 · "
                         "results/threshold_v3.md (R3) · results/final_test/r5_gioi_han.md")
    page.content(page.text("hyp-label", 82, 226, "BA GIẢ THUYẾT (CHƠA KIỂM CHỨNG)",
                           size=19, color=k.TEAL, weight="bold"))
    hypotheses = [
        ("Tuổi nhi", "Giải phẫu lồng ngực trẻ nhỏ ở lớp "
                          "Viral Pneumonia"),
        ("Ký hiệu thiết bị", "Dấu vận máy chụp ngoài vùng "
                                                "phổi ở lớp COVID"),
        ("Dịch chuyển phân phối", "Che vùng làm đổi phân phối "
                                                    "cả ba khối đặc trưng"),
    ]
    for index, (name, detail) in enumerate(hypotheses):
        y = 240 + index * 82
        zone = page.zone(f"hyp{index}", 82, y, 548, 76)
        zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
        zone.text(f"hyp{index}-name", 102, y + 34, name, size=21, color=k.INK, weight="bold")
        zone.text(f"hyp{index}-tag", 462, y + 34, "chưa kiểm chứng", size=19,
                  color=k.AMBER, weight="bold")
        zone.text(f"hyp{index}-note", 102, y + 62, detail, size=19, color=k.INK_SOFT,
                  max_width=500)
        page.content(zone.done())

    page.content(page.text("fals-label", 640, 226,
                           "DỰ ĐOÁN NẾU ĐÚNG · BẰNG CHỨNG CẤN",
                           size=19, color=k.TEAL, weight="bold"))
    conditions = [
        "Chỉ ngoài phổi tụt xuống dưới mốc A0",
        "Test nằm ngoài khoảng tin cậy của val",
        "Hiệu gốc − ngoài phổi có CI chứa 0",
        "Xáo trộn khối ngoài phổi không làm đổi điểm",
    ]
    zone = page.zone("fals", 640, 240, 558, 266)
    zone.card()
    for index, item in enumerate(conditions):
        y = 272 + index * 40
        zone.text(f"cond{index}-num", 660, y, f"{index + 1}", size=21, color=k.TEAL_LIGHT,
                  weight="bold")
        zone.text(f"cond{index}-text", 688, y, item, size=21, color=k.INK, max_width=482)
    zone.line("fals-rule", 660, 414, 1178, 414, stroke=k.LINE)
    zone.text("fals-status", 660, 436,
              f"Đã xảy ra: {fmt(D['test']['macro_f1'])} nằm ngoài "
              f"{fmt_ci(*next(r for r in D['rq2'] if r['key'] == 'svm')['ci'])} của val; CI "
              f"của hiệu gốc − ngoài phổi chứa 0. Đi ngược: "
              f"chỉ ngoài phổi đạt "
              f"{fmt(D['rq3']['scenarios']['out_to_out']['macro_f1'])}.",
              size=19, color=k.INK, max_width=518, line_h=24)
    page.content(zone.done())

    page.content(k.note_zone(page, "d4-note", 82, 522, 1116, "Quy tắc D4: " + D4,
                             fill=k.TEAL_PALE, size=19, line_h=24))
    return page


def pages():
    return [slide_10(), slide_11(), slide_12(), slide_13(), slide_14(), slide_15(), slide_16(),
            slide_17(), slide_18()]
