"""Slide 19–28: chương 5 (kiểm chứng và triển khai), chương 6 (giới hạn), cảm ơn."""

from __future__ import annotations

from . import svgkit as k
from .data import CLASS_VI, D, fmt, fmt_ci, fmt_delta, fmt_int, fmt_pct, fmt_seconds
from .slides_act2 import divider
from .texts import (ARTIFACT_URL, D4, DEMO_URL, DISCLAIMER, REPO_URL, TITLE)

CH5 = "CHƯƠNG 5 · KIỂM CHỨNG VÀ TRIỂN KHAI"
CH6 = "CHƯƠNG 6 · GIỚI HẠN VÀ KẾT LUẬN"


# ------------------------------------------------------------------ slide 19
def slide_19() -> k.Page:
    return divider("19_mo_chuong5.svg", chapter="CHƯƠNG 5", page_no=19,
                   title="Một lần mở khóa, ba lớp kiểm chứng",
                   body="Mở khóa tập test đúng một lần; trước khi mở, ba lớp kiểm chứng đã chạy: "
                        "băm split, băm artifact và bộ kiểm thử.")


# ------------------------------------------------------------------ slide 20
def slide_20() -> k.Page:
    test = D["test"]
    page = k.Page("20_ket_qua_test.svg", layout="number", master="dark", page_no=20,
                  title=f"{fmt(test['macro_f1'])} trên {fmt_int(test['n'])} ảnh test",
                  title_size=38,
                  source="Nguồn: results/final_test/final_test_report.json, metrics.json")
    zone = page.zone("hero", 82, 220, 1116, 300)
    zone.card(fill=k.CARD_DARK, stroke=k.RULE_ON_DARK)
    zone.text("hero-num", 82, 386, fmt(test["macro_f1"]), size=172, color=k.TEAL_LIGHT,
              weight="bold")
    zone.text("hero-cap", 224, 300, "macro-F1 trên tập test", size=19, color=k.SOFT_ON_DARK)
    zone.line("hero-rule", 700, 250, 700, 470, stroke=k.RULE_ON_DARK, width=1)
    zone.text("hero-ci-cap", 736, 300, "Khoảng tin cậy 95%", size=19, color=k.SOFT_ON_DARK)
    zone.text("hero-ci", 736, 344, fmt_ci(*D["test_ci"]), size=34, color=k.TEXT_ON_DARK,
              weight="bold")
    zone.text("hero-acc-cap", 736, 404, "Accuracy", size=19, color=k.SOFT_ON_DARK)
    zone.text("hero-acc", 736, 448, fmt_pct(test["accuracy"]), size=34, color=k.TEXT_ON_DARK,
              weight="bold")
    zone.text("hero-n-cap", 990, 300, "Số ảnh đánh giá", size=19, color=k.SOFT_ON_DARK)
    zone.text("hero-n", 990, 344, fmt_int(test["n"]), size=34, color=k.TEXT_ON_DARK, weight="bold")
    zone.text("hero-err-cap", 990, 404, "Số ảnh dự đoán sai", size=19, color=k.SOFT_ON_DARK)
    zone.text("hero-err", 990, 448, fmt_int(test["errors"]), size=34, color=k.AMBER, weight="bold")
    page.content(zone.done())
    page.content(k.note_zone(page, "hero-note", 82, 528, 1116,
                             f"Tập test chỉ được mở một lần, sau khi mô hình và tham số đã đóng băng; "
                             f"macro-F1 trên validation là {fmt(D['rq3']['scenarios']['orig_to_orig']['macro_f1'])}.",
                             dark=True))
    return page


# ------------------------------------------------------------------ slide 21
def slide_21() -> k.Page:
    report = D["rq3"]["scenarios"]["orig_to_orig"]["macro_f1"]
    page = k.Page("21_val_vs_test.svg", layout="content", kicker=CH5, page_no=21,
                  title="Val 0,9024, test 0,8714: chênh 0,0310 — chỉ là quan sát",
                  source="Nguồn: results/final_test/final_test_report.json · "
                         "results/final_test/r5_gioi_han.md (D4)")
    zone = page.zone("chart", 82, 214, 700, 300)
    zone.card()
    zone.image("figure", "../images/fig_test_gap.png", 104, 244, 656, 218)
    zone.text("chart-cap", 104, 258, "Khoảng tin cậy 95% của macro-F1 test và giá trị điểm.",
              size=19, color=k.INK_SOFT)
    page.content(zone.done())

    zone = page.zone("pair", 810, 214, 388, 300)
    zone.card()
    zone.text("pair-val-cap", 836, 262, "Validation (3.174 ảnh)", size=19, color=k.INK_SOFT)
    zone.text("pair-val", 836, 312, fmt(report), size=54, color=k.TEAL, weight="bold")
    zone.text("pair-test-cap", 836, 386, "Test (3.176 ảnh)", size=19, color=k.INK_SOFT)
    zone.text("pair-test", 836, 436, fmt(D["test"]["macro_f1"]), size=54, color=k.INK,
              weight="bold")
    zone.line("pair-rule", 836, 462, 1170, 462, stroke=k.LINE)
    zone.text("pair-diff", 836, 500,
              f"Chênh test − val = {fmt_delta(D['test']['macro_f1'] - report)}",
              size=21, color=k.AMBER, weight="bold")
    page.content(zone.done())

    page.content(k.note_zone(page, "d4-note", 82, 528, 1116,
                             "Quy tắc D4: " + D4, fill=k.AMBER_PALE, size=21, line_h=30))
    return page


# ------------------------------------------------------------------ slide 22
def slide_22() -> k.Page:
    test = D["test"]
    page = k.Page("22_loi_test.svg", layout="content", kicker=CH5, page_no=22,
                  title="427 lỗi, 304 lỗi nằm giữa Normal và Lung_Opacity",
                  source="Nguồn: results/final_test/metrics.json · "
                         "results/final_test/final_test_report.json")
    zone = page.zone("chart", 82, 208, 640, 404)
    zone.card()
    zone.image("figure", "../images/fig_test_confusion.png", 98, 220, 608, 380)
    page.content(zone.done())

    page_content = [
        ("Sai", fmt_int(test["errors"]), f"trên {fmt_int(test['n'])} ảnh, tức "
         f"{fmt_pct(test['errors'] / test['n'], 2)}"),
        ("Cặp Normal ↔ LO", fmt_int(D["normal_lung_test"]),
         f"{fmt_pct(D['normal_lung_pct'])} số lỗi của toàn bộ tập test"),
        ("Precision thấp nhất", fmt(test["per_class"]["Lung_Opacity"]["precision"]),
         "của lớp Lung_Opacity trên tập test"),
    ]
    for index, (caption, value, note) in enumerate(page_content):
        y = 214 + index * 132
        zone = page.zone(f"card{index}", 760, y, 438, 124)
        zone.card()
        zone.text(f"card{index}-cap", 784, y + 34, caption, size=19, color=k.INK_SOFT)
        zone.text(f"card{index}-val", 784, y + 96, value, size=40, color=k.AMBER, weight="bold")
        zone.text(f"card{index}-note", 940, y + 74, note, size=19, color=k.INK, max_width=230,
                  line_h=24)
        page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 23
def slide_23() -> k.Page:
    latency = D["latency"]
    cpu = D["latency"]["cpu_short"]
    detail = D["latency_detail"]["stages"]
    page = k.Page("23_demo.svg", layout="content", kicker=CH5, page_no=23,
                  title=f"Demo chạy {fmt_seconds(latency['stages']['total'], 3)} "
                        f"một ảnh trên laptop {cpu}",
                  source="Nguồn: results/demo_latency_sustained/latency.json · "
                         "slides/assets/screenshot_demo.png")
    note = (f"Trung vị {latency['n_images']} ảnh val, {latency['repeats']} "
            f"lượt đo; p95 {fmt_seconds(detail['total']['p95'])}.")
    zone = page.zone("shot", 82, 200, 780, 428)
    zone.card()
    zone.image("figure", "../images/screenshot_demo.png", 106, 212, 694, 396)
    zone.text("lat-cap", 106, 618, note, size=19, color=k.INK_SOFT)
    page.content(zone.done())

    rows = [
        ("Giải mã", latency["stages"]["decode"]),
        ("Đặc trưng", latency["stages"]["features"]),
        ("Suy luận", latency["stages"]["inference"]),
        ("Tổng mỗi ảnh", latency["stages"]["total"]),
    ]
    for index, (caption, value) in enumerate(rows):
        y = 206 + index * 96
        zone = page.zone(f"card{index}", 890, y, 308, 88)
        zone.card()
        zone.text(f"card{index}-cap", 910, y + 32, caption, size=19, color=k.INK_SOFT)
        zone.text(f"card{index}-val", 910, y + 76, fmt_seconds(value), size=30,
                  color=k.TEAL if index == 3 else k.INK, weight="bold")
        page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 24
def slide_24() -> k.Page:
    cases = {case["image_id"]: case for case in D["cases"]}
    correct = cases["COVID-1006.png"]
    error = cases["Normal-9540.png"]
    page = k.Page("24_vi_du.svg", layout="content", kicker=CH5, page_no=24,
                  title="Hai ca minh hoạ: một đúng, một sai",
                  source="Nguồn: results/rq2_ghep_svm_s42/preds_val.csv · "
                         "slides/assets/case_correct.png, case_error.png")
    blocks = [
        ("correct", correct, "case_correct.png", "Đúng", k.TEAL, k.TEAL_PALE),
        ("error", error, "case_error.png", "Sai", k.AMBER, k.AMBER_PALE),
    ]
    for index, (key, case, image, verdict, color, fill) in enumerate(blocks):
        x = 82 + index * 578
        zone = page.zone(f"case-{key}", x, 208, 538, 332)
        zone.card()
        zone.image(f"case-image-{key}", f"../images/{image}", x + 22, 238, 232, 232)
        zone.text(f"case-id-{key}", x + 288, 262, case["image_id"], size=21, color=k.INK,
                  weight="bold")
        zone.text(f"case-true-{key}", x + 288, 300,
                  f"Nhãn thật: {CLASS_VI[case['y_true']]}", size=19, color=k.INK_SOFT)
        zone.text(f"case-pred-{key}", x + 288, 328,
                  f"Dự đoán: {CLASS_VI[case['y_pred']]}", size=21, color=color,
                  weight="bold")
        zone.text(f"case-proba-{key}", x + 288, 386, fmt(case["probability"]), size=54,
                  color=color, weight="bold")
        zone.text(f"case-proba-cap-{key}", x + 288, 414,
                  f"xác suất lớp {CLASS_VI[case['y_pred']]}", size=19,
                  color=k.INK_SOFT)
        zone.text(f"case-verdict-{key}", x + 288, 480, verdict, size=19, color=color,
                  weight="bold")
        page.content(zone.done())
    page.content(k.note_zone(page, "case-note", 82, 552, 1116,
                             f"Ca sai cho thấy mô hình có thể tự tin "
                             f"ở mức cao trên một ca sai: Normal bị "
                             f"đoán thành Lung_Opacity với xác suất "
                             f"{fmt(error['probability'])}. Cả hai ảnh thuộc split "
                             f"val; chưa có hình minh hoạ vùng ảnh "
                             f"mô hình dùng để ra quyết định.",
                             fill=k.AMBER_PALE, size=19, line_h=26))
    return page


# ------------------------------------------------------------------ slide 25
def slide_25() -> k.Page:
    pairs = D["pairs"]
    svm_ci = next(row for row in D["rq2"] if row["key"] == "svm")["ci"]
    page = k.Page("25_gioi_han.svg", layout="content", kicker=CH6, page_no=25,
                  title="Giới hạn: 735 cặp gần trùng và không có patient_id",
                  source="Nguồn: results/report_rq3/r5_gioi_han.md · "
                         "results/threshold_v3.md mục 6 (R5) · report/06 mục 6.2")
    limits = [
        ("Gần trùng còn sót", fmt_int(pairs["total"]),
         "cặp nằm khác tập, trong đó 229 cặp lệch nhãn"),
        ("Không có patient_id", "thiếu",
         "cùng một bệnh nhân có thể nằm ở cả train và val"),
        ("Nguồn ảnh chưa xác minh", "chưa kiểm chứng",
         "tuổi nhi và ký hiệu thiết bị chưa được "
         "kiểm chứng"),
        ("Val vừa chọn mô hình vừa báo cáo", "lạc quan",
         "cùng một tập val được dùng để chọn cấu "
         "hình và để báo cáo số"),
        ("Ngoại suy ngoài bộ", "chưa được đánh giá",
         "đổi nguồn hoặc đổi tiền xử lý thì chưa "
         "ai đo lại các con số này"),
    ]
    for index, (name, value, note) in enumerate(limits):
        y = 208 + index * 80
        zone = page.zone(f"lim{index}", 82, y, 1116, 72)
        zone.card()
        zone.text(f"lim{index}-name", 106, y + 30, name, size=21, color=k.INK, weight="bold")
        zone.text(f"lim{index}-value", 106, y + 62, value, size=19, color=k.AMBER,
                  weight="bold")
        zone.text(f"lim{index}-note", 420, y + 44, note, size=21, color=k.INK, max_width=746,
                  line_h=28)
        page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 26
def slide_26() -> k.Page:
    page = k.Page("26_khong_chan_doan.svg", layout="content", kicker=CH6, page_no=26,
                  title="Không dùng để chẩn đoán",
                  source="Nguồn: demo/streamlit_app.py (DISCLAIMER) · "
                         "results/final_test/r5_gioi_han.md (D4)")
    zone = page.zone("warn", 82, 214, 1116, 200)
    zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
    zone.text("warn-tag", 106, 262, "TUYÊN BỐ TRONG ỨNG DỤNG DEMO", size=19,
              color=k.AMBER, weight="bold")
    zone.text("warn-text", 106, 306, DISCLAIMER, size=26, color=k.INK, max_width=1068,
              line_h=36)
    page.content(zone.done())

    page.content(k.note_zone(page, "d4-note", 82, 440, 1116, "Quy tắc D4: " + D4,
                             fill=k.TEAL_PALE, size=21, line_h=30))
    zone = page.zone("scope", 82, 534, 1116, 76)
    zone.card()
    zone.text("scope-text", 106, 576,
              "Các con số trong đề tài này chỉ được "
              "đánh giá trên chính bộ dữ liệu và bước "
              "tiền xử lý đã dùng; đổi nguồn ảnh, "
              "thiết bị hoặc tiền xử lý thì chưa được "
              "đo lại.", size=21, color=k.INK, max_width=1068, line_h=28)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 27
def slide_27() -> k.Page:
    from .texts import TAKEAWAYS

    test = D["test"]
    svm_ci = next(row for row in D["rq2"] if row["key"] == "svm")["ci"]
    page = k.Page("27_ket_luan.svg", layout="content", kicker=CH6, page_no=27,
                  title="Ba điểm mang về và việc còn lại",
                  source="Nguồn: tổng hợp từ results/ và report/06")
    keys = {
        "T1": f"152 đặc trưng thủ công với SVM RBF đạt "
              f"macro-F1 {fmt(test['macro_f1'])} trên {fmt_int(test['n'])} ảnh test, "
              f"vượt xa hai mốc nền đo trên validation: B0 = "
              f"{fmt(D['baselines']['b0'])}, A0 = {fmt(D['baselines']['a0'])}.",
        "T2": f"Trên validation, mô hình chỉ nhìn ngoài phổi đạt "
              f"{fmt(D['rq3']['scenarios']['out_to_out']['macro_f1'])}, chênh ảnh gốc "
              f"{fmt_delta(D['rq3']['diffs'][('orig_to_orig', 'out_to_out')]['diff'])} nhưng "
              f"khoảng tin cậy của hiệu chứa 0.",
        "T3": TAKEAWAYS["T3"],
    }
    for index, key in enumerate(("T1", "T2", "T3")):
        y = 214 + index * 118
        zone = page.zone(key, 82, y, 640, 106)
        zone.card(fill=k.TEAL_PALE, stroke=k.TEAL_LIGHT)
        zone.text(f"{key}-key", 104, y + 36, key, size=22, color=k.TEAL, weight="bold")
        zone.text(f"{key}-text", 160, y + 34, keys[key], size=19, color=k.INK, max_width=536,
                  line_h=26)
        page.content(zone.done())

    page.content(page.text("next-label", 760, 222, "VIỆC CÒN LẠI", size=19,
                           color=k.TEAL, weight="bold"))
    nexts = [
        ("Bộ có patient_id", "bộ dữ liệu lớn hơn, có mã bệnh "
                                    "nhân để chặn rò rỉ bệnh nhân"),
        ("Gỡ gần trùng", "quy trình tách nhóm cho cả cặp gần "
                                    "trùng, không chỉ trùng tuyệt đối"),
        ("Kiểm chứng nguồn", "xác minh tuổi nhi và thiết bị "
                                       "để giả thuyết thành phép thử "
                                       "được"),
    ]
    for index, (name, detail) in enumerate(nexts):
        y = 252 + index * 124
        zone = page.zone(f"next{index}", 760, y, 438, 112)
        zone.card()
        zone.text(f"next{index}-name", 782, y + 34, name, size=21, color=k.INK, weight="bold")
        zone.text(f"next{index}-detail", 782, y + 64, detail, size=19, color=k.INK_SOFT,
                  max_width=394, line_h=26)
        page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 28
def slide_28() -> k.Page:
    page = k.Page("28_cam_on.svg", layout="closing", master="dark", page_no=28,
                  title=None, numbered=False)
    page.content(
        page.image("logo", "../images/logo_ctut.png", 82, 52, 92, 92),
        page.text("thanks", 82, 300, "Cảm ơn", size=64, color=k.TEXT_ON_DARK,
                  weight="bold"),
        page.text("thanks-body", 82, 356, "Mời hội đồng đặt câu hỏi.",
                  size=26, color=k.SOFT_ON_DARK),
        page.line("thanks-rule", 82, 392, 170, 392, stroke=k.TEAL, width=3),
    )
    links = [
        ("Mã nguồn", REPO_URL),
        ("Demo (Streamlit)", DEMO_URL),
        ("Artifact mô hình", ARTIFACT_URL),
    ]
    for index, (label, url) in enumerate(links):
        y = 436 + index * 58
        page.content(
            page.text(f"url-{index}", 82, y, label, size=19, color=k.TEAL_LIGHT,
                      weight="bold"),
            page.text(f"url-text-{index}", 300, y, url, size=21, color=k.TEXT_ON_DARK),
        )
    page.content(
        page.text("credit", 82, 620, TITLE, size=19, color=k.SOFT_ON_DARK, max_width=1000,
                  line_h=24),
    )
    return page


def pages():
    return [slide_19(), slide_20(), slide_21(), slide_22(), slide_23(), slide_24(), slide_25(),
            slide_26(), slide_27(), slide_28()]
