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
        page.text("chapter", 82, 210, chapter, size=24, color=k.TEAL_LIGHT, weight="bold"),
        page.line("divider-rule", 82, 232, 170, 232, stroke=k.TEAL, width=3),
        page.slot("title", 82, 320, k.wrap(title, 52, k.CONTENT_W - 80, weight="bold"),
                  size=52, color=k.TEXT_ON_DARK, step=58,
                  carrier_gid="divider-title-carrier", bounds=(82, 268, k.CONTENT_W, 130)),
        page.text("divider-body", 82, 430, body, size=28, color=k.SOFT_ON_DARK,
                  max_width=k.CONTENT_W - 260, line_h=32),
    )
    return page


def chart_page(filename: str, *, kicker: str, title: str, source: str, page_no: int,
               image: str, image_w: int, image_h: int, cards: list[tuple[str, str, str]],
               note: tuple[str, str] | None = None) -> k.Page:
    """Khung chung cho slide bieu do: hinh ben trai, cac the so ben phai.

    ``cards`` la danh sach (khoa, gia tri, chu thich); ``note`` la (chu thich duoi
    hinh, mau nen). Hinh tu co lai neu chu thich dai, de khoi noi qua chan trang.
    """
    page = k.Page(filename, layout="content", kicker=kicker, title=title, source=source,
                  page_no=page_no)
    caption = note[0] if note else ""
    lines = k.wrap(caption, k.SIZE_SMALL, image_w - 24) if caption else []
    for _ in range(4):
        need = 46 + len(lines) * 32
        room = 620 - 208 - need
        if image_h <= room:
            break
        image_h = room
        image_w = max(430, int(image_w * room / image_h))
        lines = k.wrap(caption, k.SIZE_SMALL, image_w - 24) if caption else []
    need = 46 + len(lines) * 32
    zone = page.zone("chart", 82, 208, image_w + 32, image_h + need)
    zone.card()
    zone.image("figure", image, 98, 222, image_w, image_h)
    if lines:
        zone.text("chart-caption", 110, 222 + image_h + 40, caption, size=k.SIZE_SMALL,
                  color=k.INK, max_width=image_w - 24, line_h=32)
    page.content(zone.done())

    x = 82 + image_w + 44
    width = 1198 - x
    for index, (key, value, caption_text) in enumerate(cards[:3]):
        y = 190 + index * 140
        zone = page.zone(f"card-{key}", x, y, width, 140)
        zone.card()
        label, sep, rest = caption_text.rpartition(" · CI ")
        if sep:
            # Nhãn và khoảng tin cậy xuống hai dòng riêng: chuỗi "CI [a; b]" dài hơn
            # bề rộng thẻ nên nếu để tự ngắt, dấu "[" hoặc số thứ hai sẽ rơi xuống
            # dòng dưới và đọc thành một con số khác.
            zone.text(f"card-{key}-cap", x + 16, y + 30, label, size=24, color=k.INK_SOFT,
                      max_width=width - 32, line_h=28)
            zone.text(f"card-{key}-ci", x + 16, y + 60, "CI " + rest, size=24, color=k.INK_SOFT)
        else:
            zone.text(f"card-{key}-cap", x + 16, y + 30, caption_text, size=24, color=k.INK_SOFT,
                      max_width=width - 32, line_h=28)
        zone.text(f"card-{key}-val", x + 16, y + 116, value, size=38, color=k.TEAL,
                  weight="bold")
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
    rows = sorted(D["rq1"], key=lambda row: row["macro_f1"], reverse=True)
    cards = [(row["key"], fmt(row["macro_f1"]), f"{_NAME_RQ1[row['key']]} · CI {fmt_ci(*row['ci'])}")
             for row in rows]
    return chart_page(
        "11_rq1.svg", kicker=CH3, page_no=11,
        title=f"Nhóm ghép dẫn đầu với {fmt(ghep['macro_f1'])} ± {fmt(ghep['std'], 4)}",
        source="Nguồn: results/report_rq1/r1_summary.csv · "
               "results/b0_majority, a0_shortcut/metrics.json",
        image="../images/fig_rq1_ci.png", image_w=736, image_h=270,
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
         f"Ghép − Histogram · CI {fmt_ci(*ghep['delta']['ci'])}"),
        ("glcm", fmt_delta(glcmlbp["delta"]["diff"]),
         f"GLCM + LBP − Histogram · CI {fmt_ci(*glcmlbp['delta']['ci'])}"),
        ("hog", fmt_delta(hog["delta"]["diff"]),
         f"HOG − Histogram · CI {fmt_ci(*hog['delta']['ci'])}"),
    ]
    page = chart_page(
        "12_rq1_delta.svg", kicker=CH3, page_no=12,
        title=f"Chỉ ghi nhận “tốt hơn” khi Δ ≥ {fmt(rules['delta_threshold'], 3)}\nvà CI không chứa 0",
        source="Nguồn: results/report_rq1/r1_bootstrap_vs_reference.csv · "
               "results/rq1_cost_rank_record.md",
        image="../images/fig_rq1_delta.png", image_w=736, image_h=260,
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
        title=f"SVM RBF {fmt(svm['macro_f1'])}, hơn Random Forest {fmt(delta['diff'])}",
        source="Nguồn: results/report_rq2/r1_summary.csv · "
               "results/report_rq2/r1_bootstrap_vs_reference.csv",
        image="../images/fig_rq2_ci.png", image_w=736, image_h=272,
        cards=cards,
        note=(f"Δ SVM − RF = {fmt_delta(delta['diff'])} {fmt_ci(*delta['ci'])}; validation "
              f"còn {fmt_int(D['val_errors']['n'])} lỗi, "
              f"{fmt_int(D['val_errors']['normal_lung_opacity'])} lỗi thuộc cặp "
              "Normal ↔ Lung_Opacity. RF ở RQ2 chọn siêu tham số bằng CV "
              f"({fmt(rf_rq2['macro_f1'])}), khác RF cố định ở RQ1 "
              f"({fmt(rf_rq1['macro_f1'])}).", k.TEAL_PALE),
    )


# ------------------------------------------------------------------ slide 14
def slide_14() -> k.Page:
    return divider("14_mo_chuong4.svg", chapter="CHƯƠNG 4", page_no=14,
                   title="Nếu che mất vùng phổi thì sao?",
                   body="Câu hỏi 3: che và cắt theo mask phổi có làm "
                        "đổi macro-F1 không. Năm kịch bản: huấn luyện "
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
        image="../images/fig_rq3_scenarios.png", image_w=736, image_h=270,
        cards=cards,
        note=(f"Chỉ phổi − gốc = "
              f"{fmt_delta(D['rq3']['diffs'][('lung_to_lung', 'orig_to_orig')]['diff'])}; "
              f"chỉ phổi − chỉ ngoài phổi = "
              f"{fmt_delta(gap_lung_out['diff'])} "
              f"{fmt_ci(*gap_lung_out['ci'])}, không chứa 0. "
              "Quy ước A → B: huấn luyện trên ảnh dạng A, đánh giá trên ảnh dạng B.",
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
    zone = page.zone("trio", 82, 204, 624, 352)
    zone.card()
    zone.image("trio-image", "../images/mask_trio.png", 98, 218, 592, 197)
    zone.text("trio-cap", 98, 448, "Ba chế độ của một ảnh validation", size=24,
              color=k.INK_SOFT)
    zone.text("trio-cap2", 98, 480,
              "Ảnh gốc · chỉ giữ vùng phổi · chỉ giữ vùng ngoài phổi. Cả ba đều là ảnh "
              "split val; chưa đủ căn cứ để nói vùng phổi là nguồn tín hiệu duy nhất.",
              size=24, color=k.INK, max_width=592, line_h=30)
    page.content(zone.done())

    zone = page.zone("pair", 730, 204, 468, 416)
    zone.card()
    zone.text("pair-full-cap", 756, 248, "Ảnh gốc (gốc → gốc)", size=24, color=k.INK_SOFT)
    zone.text("pair-full", 756, 330, fmt(full), size=72, color=k.TEAL, weight="bold")
    zone.text("pair-out-cap", 756, 382, "Chỉ vùng ngoài phổi", size=24, color=k.INK_SOFT)
    zone.text("pair-out-cap2", 756, 414, "(ngoài phổi → ngoài phổi)", size=24,
              color=k.INK_SOFT)
    zone.text("pair-out", 756, 480, fmt(outside), size=72, color=k.TEAL, weight="bold")
    zone.line("pair-rule", 756, 516, 1172, 516, stroke=k.LINE)
    zone.text("pair-delta", 756, 552,
              f"Δ {fmt_delta(diff['diff'])} {fmt_ci(*diff['ci'])}", size=26, color=k.AMBER,
              weight="bold")
    zone.text("pair-delta-flag", 756, 586, "khoảng tin cậy của hiệu chứa 0", size=24,
              color=k.AMBER, weight="bold")
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
        ("glcm", fmt(lung["glcm_60"]["importance"]), "Chỉ phổi · GLCM 60"),
        ("lbp", fmt(blocks["lbp_28"]["importance"]), "Ngoài phổi · LBP 28"),
        ("hist", fmt(blocks["hist_64"]["importance"]), "Ngoài phổi · Histogram 64"),
    ]
    return chart_page(
        "17_rq3_perm.svg", kicker=CH4, page_no=17,
        title=f"GLCM cao nhất khi chỉ nhìn trong phổi: {fmt(lung['glcm_60']['importance'])}",
        source="Nguồn: results/rq3_permutation_importance.csv",
        image="../images/fig_rq3_perm.png", image_w=736, image_h=270,
        cards=cards,
        note=(f"GLCM ngoài phổi {fmt(glcm_out['importance'])} và LBP "
              f"{fmt(lbp_out['importance'])}: chênh {fmt(gap, 4)}, nhỏ hơn độ lệch "
              f"{fmt(noise, 4)} của 10 lần xáo trộn. Mức giảm chưa chuẩn hóa theo cỡ "
              f"khối (60 chiều so với 28).", k.AMBER_PALE),
    )


# ------------------------------------------------------------------ slide 18
def slide_18() -> k.Page:
    page = k.Page("18_phan_chung.svg", layout="content", kicker=CH4, page_no=18,
                  title="Ba giả thuyết, bốn câu hỏi cần bằng chứng",
                  source="Nguồn: report/04_hoc_loi_tat_rq3.md mục 4.3 · "
                         "results/threshold_v3.md (R3) · results/final_test/r5_gioi_han.md")
    page.content(page.text("hyp-label", 82, 222, "BA GIẢ THUYẾT (CHƯA KIỂM CHỨNG)",
                           size=24, color=k.TEAL, weight="bold"))
    hypotheses = [
        ("Tuổi nhi", "Giải phẫu lồng ngực trẻ nhỏ"),
        ("Ký hiệu thiết bị", "Dấu vận máy chụp ngoài vùng phổi"),
        ("Dịch chuyển phân phối", "Che vùng làm đổi phân phối đặc trưng"),
    ]
    for index, (name, detail) in enumerate(hypotheses):
        x = 82 + index * 380
        zone = page.zone(f"hyp{index}", x, 252, 352, 136)
        zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
        zone.text(f"hyp{index}-name", x + 20, 282, name, size=24, color=k.INK, weight="bold",
                  max_width=312, line_h=30)
        zone.text(f"hyp{index}-note", x + 20, 326, detail, size=24, color=k.INK_SOFT,
                  max_width=312, line_h=30)
        page.content(zone.done())

    page.content(page.text("fals-label", 82, 416,
                           "DỰ ĐOÁN NẾU ĐÚNG · BẰNG CHỨNG CẦN", size=24, color=k.TEAL,
                           weight="bold"))
    conditions = [
        "Ngoài phổi tụt dưới A0",
        "Test ngoài CI của val",
        "Hiệu có CI chứa 0",
        "Xáo trộn không đổi điểm",
    ]
    for index, item in enumerate(conditions):
        x = 82 + index * 282
        zone = page.zone(f"cond{index}", x, 448, 268, 80)
        zone.card()
        zone.text(f"cond{index}-num", x + 16, 472, f"{index + 1}", size=24,
                  color=k.TEAL_LIGHT, weight="bold")
        zone.text(f"cond{index}-text", x + 48, 472, item, size=24, color=k.INK,
                  max_width=204, line_h=30)
        page.content(zone.done())

    page.content(k.note_zone(page, "d4-note", 82, 540, 1116, "Quy tắc D4: " + D4,
                             fill=k.TEAL_PALE, size=24, line_h=26))
    return page


def pages():
    return [slide_10(), slide_11(), slide_12(), slide_13(), slide_14(), slide_15(), slide_16(),
            slide_17(), slide_18()]
