"""Slide 1–9: mở đầu, chương 1 (đặt vấn đề) và chương 2 (dữ liệu, phương pháp)."""

from __future__ import annotations

from . import svgkit as k
from .data import CLASS_VI, D, fmt, fmt_int, fmt_pct
from .texts import (CLASS, COURSE, FACULTY, MEMBERS, PLACE, SEMESTER, SCHOOL, SUPERVISOR,
                    TITLE)

CH1 = "CHƯƠNG 1 · ĐẶT VẤN ĐỀ"
CH2 = "CHƯƠNG 2 · DỮ LIỆU VÀ PHƯƠNG PHÁP"

CHAPTERS = [
    ("1", "Đặt vấn đề", "ba câu hỏi, ranh giới"),
    ("2", "Dữ liệu và phương pháp", "21.165 ảnh, 152 đặc trưng"),
    ("3", "Kết quả RQ1 và RQ2", "đặc trưng nào, bộ phân loại nào"),
    ("4", "Mô hình nhìn vào đâu", "che và cắt vùng phổi"),
    ("5", "Kiểm chứng và triển khai", "mở khóa test, demo"),
    ("6", "Giới hạn và kết luận", "ba điểm mang về"),
]


def _cover_title_slot(page: k.Page, lines: list[str], size: float, first: float, step: float) -> str:
    """Tiêu đề bìa trong một ô placeholder, carrier một khung chữ dy-stacked."""
    return page.slot("title", "cover-title", 82, first, lines, size=size,
                     color=k.TEXT_ON_DARK, step=step)


# ------------------------------------------------------------------ slide 1
def slide_01() -> k.Page:
    page = k.Page("01_cover.svg", layout="cover", master="dark", page_no=1, numbered=False)
    split = D["split"]
    lines = k.wrap(TITLE, 34, k.CONTENT_W - 40, weight="bold")
    if len(lines) > 3:
        raise ValueError("tiêu đề bìa quá 3 dòng")

    page.content(
        page.image("logo", "../images/logo_ctut.png", 82, 52, 92, 92),
        page.text("course", 196, 56, COURSE.upper(), size=19, color=k.TEAL_LIGHT, weight="bold"),
        page.text("semester", 196, 84, SEMESTER, size=19, color=k.SOFT_ON_DARK),
        page.slot("title", 82, 236, lines, size=34, color=k.TEXT_ON_DARK, step=42,
                  carrier_gid="cover-title-carrier",
                  bounds=(82, 200, k.CONTENT_W, 132)),
        page.line("cover-rule", 82, 186, 170, 186, stroke=k.TEAL, width=3),
        page.text("supervisor", 82, 372, SUPERVISOR, size=21, color=k.TEAL_LIGHT, weight="bold"),
        page.text("class", 82, 400, CLASS, size=19, color=k.SOFT_ON_DARK),
        page.text("members-label", 82, 448, "SINH VIÊN THỰC HIỆN", size=19,
                  color=k.TEAL_LIGHT, weight="bold"),
    )
    for index, (name, mssv, _role) in enumerate(MEMBERS):
        column, row = divmod(index, 3)
        x = 82 + column * 618
        y = 550 + row * 50
        page.content(
            page.text(f"member-{index}", x, y, name, size=20, color=k.TEXT_ON_DARK),
            page.text(f"member-id-{index}", x + 262, y, mssv, size=19, color=k.SOFT_ON_DARK),
        )
    page.content(
        page.text("school", k.W - 82, 420, SCHOOL, size=19, color=k.SOFT_ON_DARK, anchor="end"),
        page.text("faculty", k.W - 82, 450, FACULTY, size=19, color=k.SOFT_ON_DARK, anchor="end"),
        page.text("place", k.W - 82, 482, PLACE, size=21, color=k.TEXT_ON_DARK,
                  anchor="end", weight="bold"),
        page.text("cover-data", k.W - 82, 520,
                  f"{fmt_int(split['total'])} ảnh · 4 lớp · mô hình học máy cổ điển",
                  size=19, color=k.SOFT_ON_DARK, anchor="end"),
    )
    return page


# ------------------------------------------------------------------ slide 2
def slide_02() -> k.Page:
    from .texts import TAKEAWAYS

    page = k.Page("02_lotrinh.svg", layout="content", kicker=CH1, page_no=2,
                  title="Ba câu hỏi, sáu chương, ba điểm mang về",
                  source="Nguồn: report/README.md · slides/texts.py (T1–T3) · results/")
    page.content(page.text("roadmap-label", 82, 222, "SÁU CHƯƠNG BÁO CÁO", size=19,
                           color=k.TEAL, weight="bold"))
    for index, (number, name, hint) in enumerate(CHAPTERS):
        column, row = divmod(index, 2)
        x = 82 + column * 183
        y = 250 + row * 106
        zone = page.zone(f"ch{number}", x, y, 172, 92)
        zone.card()
        zone.text(f"ch{number}-num", x + 14, y + 36, f"Ch.{number}", size=22, color=k.TEAL, weight="bold")
        zone.text(f"ch{number}-name", x + 14, y + 64, name, size=19, color=k.INK, max_width=146,
                  line_h=24)
        page.content(zone.done())

    page.content(page.text("take-label", 660, 222, "BA ĐIỂM MANG VỀ", size=19,
                           color=k.TEAL, weight="bold"))
    y = 250
    for key in ("T1", "T2", "T3"):
        zone = page.zone(key, 660, y, 538, 104)
        zone.card(fill=k.TEAL_PALE, stroke=k.TEAL_LIGHT)
        zone.text(f"{key}-key", 680, y + 34, key, size=22, color=k.TEAL, weight="bold")
        zone.text(f"{key}-text", 680, y + 66, TAKEAWAYS[key], size=19, color=k.INK, max_width=498,
                  line_h=26)
        page.content(zone.done())
        y += 116
    return page


# ------------------------------------------------------------------ slide 3
def slide_03() -> k.Page:
    split = D["split"]
    page = k.Page("03_dulieu.svg", layout="content", kicker=CH1, page_no=3,
                  title=f"{fmt_int(split['total'])} ảnh, bốn lớp, lớp đông nhất gấp "
                        f"{fmt(split['ratio'], 1)} lần lớp hiếm nhất",
                  source="Nguồn: splits/split_v1.csv · results/b0_majority/metrics.json")
    page.content(page.text("classes-label", 82, 222, "PHÂN BỐ BỐN LỚP", size=19,
                           color=k.TEAL, weight="bold"))
    order = ["Normal", "Lung_Opacity", "COVID", "Viral Pneumonia"]
    top = max(split["per_class"][name] for name in order)
    for index, name in enumerate(order):
        count = split["per_class"][name]
        y = 250 + index * 86
        zone = page.zone(f"cls{index}", 82, y, 700, 30)
        zone.add(page.text(f"cls{index}-name", 82, y + 22, CLASS_VI[name], size=19, color=k.INK))
        zone.add(page.rect(f"cls{index}-track", 258, y, 340, 26, fill="#E6DFCF", radius=13))
        zone.add(page.rect(f"cls{index}-fill", 258, y, max(8, 340 * count / top), 26, fill=k.TEAL, radius=13))
        zone.add(page.text(f"cls{index}-num", 636, y + 22, fmt_int(count), size=19,
                           color=k.INK, weight="bold", anchor="end"))
        page.content(zone.done())
        page.content(page.text(f"cls{index}-share", 258, y + 56,
                               f"{fmt_pct(count / split['total'], 1)} của toàn bộ", size=19,
                               color=k.INK_SOFT))

    zone = page.zone("sum-card", 830, 240, 368, 292)
    zone.card()
    zone.text("sum-num", 856, 302, fmt_int(split["total"]), size=52, color=k.TEAL, weight="bold")
    zone.text("sum-cap", 856, 330, "ảnh trong bộ dữ liệu gốc", size=19, color=k.INK_SOFT)
    zone.line("sum-rule", 856, 352, 1174, 352, stroke=k.LINE)
    zone.text("sum-ratio", 856, 398, fmt(split["ratio"], 1) + "×", size=34, color=k.INK, weight="bold")
    zone.text("sum-ratio-cap", 856, 426, "tỉ lệ Normal trên Viral Pneumonia", size=19, color=k.INK_SOFT)
    page.content(zone.done())
    page.content(
        k.note_zone(page, "sum-note", 856, 556, 316,
                    f"Nếu chỉ đoán Normal, macro-F1 chỉ đạt {fmt(D['baselines']['b0'])} (B0)."),
    )
    return page


# ------------------------------------------------------------------ slide 4
def slide_04() -> k.Page:
    page = k.Page("04_cauhoi.svg", layout="content", kicker=CH1, page_no=4,
                  title="Ba câu hỏi và một ranh giới: chỉ học máy cổ điển",
                  source="Nguồn: results/threshold_v3.md · report/01 mục 1.4")
    questions = [
        ("RQ1", "Nhóm đặc trưng nào lấy được tín hiệu nhất?",
         "Bốn nhóm: histogram, GLCM+LBP, HOG, ghép; so sánh bằng macro-F1 và CI 95%."),
        ("RQ2", "Bộ phân loại nào phù hợp với 152 chiều đặc trưng?",
         "Sáu bộ phân loại cùng một thước đo, mỗi bộ ba seed, chênh lệch có bootstrap."),
        ("RQ3", "Mô hình dựa vào vùng phổi hay vùng ngoài phổi?",
         "Che và cắt vùng phổi trên cùng ảnh rồi đo lại macro-F1 từng kịch bản."),
    ]
    for index, (name, question, detail) in enumerate(questions):
        x = 82 + index * 380
        zone = page.zone(name, x, 214, 352, 244)
        zone.card()
        zone.text(f"{name}-tag", x + 20, 250, name, size=22, color=k.TEAL, weight="bold")
        zone.text(f"{name}-q", x + 20, 284, question, size=21, color=k.INK, max_width=312,
                  line_h=28)
        zone.text(f"{name}-d", x + 20, 396, detail, size=19, color=k.INK_SOFT, max_width=312,
                  line_h=26)
        page.content(zone.done())

    zone = page.zone("h7-band", 82, 482, 1116, 104)
    zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
    zone.text("h7-tag", 102, 520, "RANH GIỚI H7", size=19, color=k.AMBER, weight="bold")
    zone.text("h7-text", 102, 550,
              "Chỉ dùng học máy cổ điển với đặc trưng thủ công; ảnh gốc xám 299×299, "
              "không mạng tích hợp, không dữ liệu ngoài bộ đã công bố.",
              size=19, color=k.INK, max_width=1076, line_h=26)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 5
def slide_05() -> k.Page:
    split = D["split"]
    sources = D["sources"]
    page = k.Page("05_nguon.svg", layout="content", kicker=CH2, page_no=5,
                  title="Nhãn lớp không độc lập với nguồn ảnh",
                  source="Nguồn: results/eda/normal_source_labels.csv · splits/split_v1.csv "
                         "· report/02 mục 2.1")
    blocks = [
        ("Chowdhury et al.", fmt_int(sources["chowdhury"]),
         f"COVID {fmt_int(split['per_class']['COVID'])} · Lung Opacity "
         f"{fmt_int(split['per_class']['Lung_Opacity'])} · "
         f"Normal {fmt_int(sources['normal_rsna'])} (nhóm RSNA)",
         "một tệp nguồn, ảnh gốc của bộ dữ liệu"),
        ("Mooney et al. — Normal", fmt_int(sources["normal_mooney"]),
         "mẫu Normal ghi nhãn từ bộ của Mooney",
         f"nằm lẫn trong {fmt_int(split['per_class']['Normal'])} ảnh Normal"),
        ("Mooney et al. — Viral Pneumonia", fmt_int(sources["viral"]),
         "toàn bộ lớp Viral Pneumonia đến từ một nguồn", "lớp nhỏ nhất, một nguồn duy nhất"),
    ]
    for index, (name, count, detail, note) in enumerate(blocks):
        x = 82 + index * 380
        zone = page.zone(f"src{index}", x, 214, 352, 240)
        zone.card()
        zone.text(f"src{index}-name", x + 20, 250, name, size=19, color=k.TEAL, weight="bold",
                  max_width=312)
        zone.text(f"src{index}-count", x + 20, 308, count, size=46, color=k.INK, weight="bold")
        zone.text(f"src{index}-detail", x + 20, 344, detail, size=19, color=k.INK_SOFT,
                  max_width=312, line_h=26)
        zone.text(f"src{index}-note", x + 20, 418, note, size=19, color=k.INK, max_width=312,
                  line_h=26)
        page.content(zone.done())

    zone = page.zone("src-total", 82, 474, 1116, 112)
    zone.card(fill=k.TEAL_PALE, stroke=k.TEAL_LIGHT)
    zone.text("src-total-num", 108, 528, fmt_int(sources["total"]), size=34, color=k.TEAL,
              weight="bold")
    zone.text("src-total-text", 244, 522,
              "ảnh đến từ ít nhất hai nguồn công bố khác nhau, ghép lại trong một bộ dữ liệu.",
              size=21, color=k.INK, max_width=920, line_h=28)
    zone.text("src-total-note", 108, 562,
              "Khớp hai nguồn theo tên lớp chưa đủ: cùng nhãn Normal, hai nguồn có thể khác "
              "thiết bị, dải sáng và tỉ lệ bệnh.",
              size=19, color=k.INK_SOFT, max_width=1070, line_h=26)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 6
def slide_06() -> k.Page:
    covid = next(row for row in D["brightness"] if row["label"] == "COVID")
    page = k.Page("06_dosang.svg", layout="content", kicker=CH2, page_no=6,
                  title="Độ sáng và metadata chỉ chạm tới 0,2397",
                  source="Nguồn: results/eda/brightness_by_class.csv · results/a0_shortcut/metrics.json")
    zone = page.zone("chart", 82, 208, 748, 372)
    zone.card()
    zone.image("brightness", "../images/fig_brightness.png", 96, 222, 720, 330)
    zone.text("chart-cap", 96, 570, "Khoảng tứ phân vị và giá trị trung bình của bốn lớp "
              "(n = 21.165 ảnh).", size=19, color=k.INK_SOFT)
    page.content(zone.done())

    stats = [
        ("AUC COVID/nền", fmt(covid["auc_vs_rest"]), "phân biệt COVID nhờ độ sáng trung bình"),
        ("A0 (chỉ metadata)", fmt(D["baselines"]["a0"]), "macro-F1 khi không nhìn ảnh gốc"),
    ]
    for index, (caption, value, note) in enumerate(stats):
        y = 214 + index * 178
        zone = page.zone(f"num{index}", 858, y, 340, 160)
        zone.card()
        zone.text(f"num{index}-cap", 878, y + 38, caption, size=19, color=k.INK_SOFT)
        zone.text(f"num{index}-val", 878, y + 82, value, size=46, color=k.TEAL, weight="bold")
        zone.text(f"num{index}-note", 878, y + 124, note, size=19, color=k.INK, max_width=300,
                  line_h=24)
        page.content(zone.done())

    page.content(
        k.note_zone(page, "meta-note", 858, 566, 340,
                    f"B0 = {fmt(D['baselines']['b0'])}: chỉ cần độ sáng và nhãn nguồn, "
                    "không cần nhìn tổn thương."),
    )
    return page


# ------------------------------------------------------------------ slide 7
def slide_07() -> k.Page:
    split = D["split"]
    pairs = D["pairs"]
    dup = D["duplicates"]
    page = k.Page("07_trunglap.svg", layout="content", kicker=CH2, page_no=7,
                  title="Trùng tuyệt đối bị chặn, gần trùng thì không",
                  source="Nguồn: outputs/split_check/duplicates_summary.json, "
                         "cross_split_hamming_report.json · splits/split_v1.csv")
    page.content(page.text("split-label", 82, 222, "BA TẬP SAU KHI TÁCH NHÓM", size=19,
                           color=k.TEAL, weight="bold"))
    for index, (name, count) in enumerate([("train", split["per_split"]["train"]),
                                           ("val", split["per_split"]["val"]),
                                           ("test", split["per_split"]["test"])]):
        x = 82 + index * 220
        page.content(
            page.text(f"sp{index}", x, 272, fmt_int(count), size=40, color=k.TEAL, weight="bold"),
            page.text(f"sp{index}-cap", x, 314, name, size=19, color=k.INK_SOFT),
        )

    zone = page.zone("exact-card", 82, 340, 528, 168)
    zone.card()
    zone.text("exact-num", 102, 388, fmt_int(dup["exact_groups"]), size=34, color=k.INK,
              weight="bold")
    zone.text("exact-num2", 268, 386, "nhóm trùng tuyệt đối", size=19, color=k.INK_SOFT)
    zone.text("exact-note", 102, 424,
              f"{fmt_int(dup['exact_images'])} ảnh nằm trong các nhóm này; nhóm trùng khác nhãn: "
              f"{dup['cross_class_groups']}.", size=19, color=k.INK, max_width=490, line_h=26)
    zone.text("exact-note2", 102, 474,
              "Cùng một nhóm pHash tuyệt đối bị ép về một tập, nên không thể xuất hiện ở cả hai.",
              size=19, color=k.INK_SOFT, max_width=490, line_h=26)
    page.content(zone.done())

    zone = page.zone("near-card", 640, 340, 558, 168)
    zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
    zone.text("near-num", 660, 388, fmt_int(pairs["total"]), size=34, color=k.AMBER, weight="bold")
    zone.text("near-num2", 852, 386, "cặp gần trùng nằm khác tập", size=19, color=k.INK_SOFT)
    zone.text("near-note", 660, 424,
              "test–train 325 · train–val 335 · test–val 75; trong đó 229 cặp lệch nhãn.",
              size=19, color=k.INK, max_width=518, line_h=26)
    zone.text("near-note2", 660, 474,
              f"Cặp có khoảng cách Hamming ≤ 4 trong toàn bộ dữ liệu: "
              f"{fmt_int(D['pairs_detail']['total_d1_4'])}.",
              size=19, color=k.INK_SOFT, max_width=518, line_h=26)
    page.content(zone.done())

    zone = page.zone("sha-card", 82, 516, 1116, 78)
    zone.card(fill=k.PLATE, stroke=None)
    zone.text("sha-key", 102, 552, "SHA-256", size=19, color=k.INK_SOFT, weight="bold")
    zone.text("sha-val", 262, 552, f"{split['sha256'][:24]}…", size=19, color=k.INK)
    zone.text("sha-note", 262, 578, "băm của splits/split_v1.csv, ghi trong biên bản mở "
              "khóa test.", size=19, color=k.INK_SOFT)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 8
def slide_08() -> k.Page:
    features = D["features"]
    split = D["split"]
    hog = next(row for row in D["rq1"] if row["key"] == "hog")
    page = k.Page("08_dactrung.svg", layout="content", kicker=CH2, page_no=8,
                  title=f"{features['total']} chiều thủ công, chuẩn hóa chỉ trên train",
                  source="Nguồn: src/features_*.py · report/02 mục 2.6–2.7 "
                         "· results/report_rq1/r1_summary.csv")
    stations = [
        ("Ảnh gốc", "xám 299×299", "một kênh, không resize lại"),
        ("Histogram", f"{features['hist']} chiều", "phân bố mức xám"),
        ("GLCM + LBP", f"{features['glcm'] + features['lbp']} chiều", "texture hai vùng"),
        ("Ghép", f"{features['total']} chiều", "ba khối cùng một vectơ"),
        ("Chuẩn hóa", "fit trên train", f"scaler học {fmt_int(split['per_split']['train'])} ảnh"),
        ("SVM RBF", "bộ phân loại", "mô hình đóng băng, một seed"),
    ]
    for index, (name, value, note) in enumerate(stations):
        x = 82 + index * 188
        zone = page.zone(f"st{index}", x, 214, 166, 208)
        zone.card()
        zone.text(f"st{index}-name", x + 14, 250, name, size=19, color=k.TEAL, weight="bold",
                  max_width=138)
        zone.text(f"st{index}-val", x + 14, 294, value, size=21, color=k.INK, weight="bold",
                  max_width=138, line_h=26)
        zone.text(f"st{index}-note", x + 14, 376, note, size=19, color=k.INK_SOFT, max_width=138,
                  line_h=24)
        page.content(zone.done())
        if index < len(stations) - 1:
            page.content(page.text(f"st{index}-arrow", x + 168, 306, "→", size=20,
                                   color=k.TEAL_LIGHT))

    zone = page.zone("hog-band", 82, 440, 1116, 148)
    zone.card(fill=k.TEAL_PALE, stroke=k.TEAL_LIGHT)
    zone.text("hog-tag", 102, 464, "HOG ĐO RIÊNG", size=19, color=k.TEAL, weight="bold")
    zone.text("hog-num", 102, 518, fmt_int(features["hog"]) + " chiều", size=34, color=k.INK,
              weight="bold")
    zone.text("hog-note", 420, 508,
              f"HOG sinh nhiều chiều nhất nhưng lại là nhóm yếu nhất: macro-F1 "
              f"{fmt(hog['macro_f1'])} trên validation.",
              size=21, color=k.INK, max_width=746, line_h=28)
    zone.text("hog-note2", 420, 552,
              f"Chi phí tính toán cũng đi theo cỡ chiều: ghep tốn {fmt(D['rq1_cost']['ratio'], 1)} "
              "lần hist cho mỗi ảnh.",
              size=19, color=k.INK_SOFT, max_width=746, line_h=26)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 9
def slide_09() -> k.Page:
    page = k.Page("09_giaithuat.svg", layout="content", kicker=CH2, page_no=9,
                  title="Sáu bộ phân loại, một thước đo duy nhất",
                  source="Nguồn: results/report_rq2/r1_summary.csv · "
                         "results/report_rq2/r2_bootstrap_vs_reference.csv")
    page.content(page.text("classifiers-label", 82, 222, "SÁU BỘ PHÂN LOẠI TRÊN CÙNG VECTƠ 152 CHIỀU",
                           size=19, color=k.TEAL, weight="bold"))
    names = ["Logistic Regression", "k-NN", "Decision Tree", "Random Forest", "Gradient Boosting",
             "SVM RBF"]
    for index, name in enumerate(names):
        row, column = divmod(index, 2)
        x = 82 + column * 300
        y = 252 + row * 60
        page.content(
            page.text(f"name{index}", x, y, f"{index + 1}", size=21, color=k.TEAL_LIGHT,
                      weight="bold"),
            page.text(f"name-t{index}", x + 26, y, name, size=21, color=k.INK, max_width=258),
        )

    zone = page.zone("proto", 700, 214, 498, 306)
    zone.card()
    zone.text("proto-tag", 724, 250, "GIAO THỨC ĐO", size=19, color=k.TEAL, weight="bold")
    protocol = [
        ("Ba seed", "42 · 43 · 44 trên cùng một split"),
        ("Bootstrap", "2.000 lần, CI 95% cho mỗi macro-F1"),
        ("Ngưỡng chênh", "Δ ≥ 0,005 mới ghi nhận “tốt hơn”"),
        ("Mốc tham chiếu", "Random Forest, đối chiếu từng bộ"),
    ]
    for index, (name, detail) in enumerate(protocol):
        y = 290 + index * 54
        zone.text(f"proto-name{index}", 724, y, name, size=20, color=k.INK, weight="bold")
        zone.text(f"proto-detail{index}", 920, y, detail, size=19, color=k.INK_SOFT, max_width=252)
    page.content(zone.done())

    page.content(
        k.note_zone(page, "proto-note", 82, 462, 520,
                    "Mọi con số trong chương 3 là macro-F1 trên "
                    f"{fmt_int(D['split']['per_split']['val'])} ảnh validation."),
        k.note_zone(page, "proto-note2", 700, 538, 498,
                    "SVM là bộ tất định: một tham số duy nhất nên chỉ chạy một lần, "
                    "ba seed áp cho các bộ khác.", fill=k.AMBER_PALE),
    )
    return page


def pages():
    return [slide_01(), slide_02(), slide_03(), slide_04(), slide_05(), slide_06(), slide_07(),
            slide_08(), slide_09()]
