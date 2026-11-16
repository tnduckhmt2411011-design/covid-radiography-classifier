"""Slide 1–9: mở đầu, chương 1 (đặt vấn đề) và chương 2 (dữ liệu, phương pháp)."""

from __future__ import annotations

from . import svgkit as k
from .data import CLASS_VI, D, fmt, fmt_int, fmt_pct, fmt_seconds
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
        page.text("course", 196, 52, COURSE.upper(), size=24, color=k.TEAL_LIGHT, weight="bold"),
        page.text("semester", 196, 92, SEMESTER, size=24, color=k.SOFT_ON_DARK),
        page.slot("title", 82, 236, lines, size=34, color=k.TEXT_ON_DARK, step=42,
                  carrier_gid="cover-title-carrier",
                  bounds=(82, 200, k.CONTENT_W, 132)),
        page.line("cover-rule", 82, 186, 170, 186, stroke=k.TEAL, width=3),
        page.text("supervisor", 82, 364, SUPERVISOR, size=28, color=k.TEAL_LIGHT, weight="bold"),
        page.text("class", 82, 416, CLASS, size=24, color=k.SOFT_ON_DARK),
        page.text("members-label", 82, 474, "SINH VIÊN THỰC HIỆN", size=24,
                  color=k.TEAL_LIGHT, weight="bold"),
    )
    for index, (name, mssv, _role) in enumerate(MEMBERS):
        column, row = divmod(index, 3)
        x = 82 + column * 618
        y = 548 + row * 56
        page.content(
            page.text(f"member-{index}", x, y, name, size=24, color=k.TEXT_ON_DARK,
                      max_width=300),
            page.text(f"member-id-{index}", x + 316, y, mssv, size=24, color=k.SOFT_ON_DARK),
        )
    page.content(
        page.text("school", k.W - 82, 396, SCHOOL, size=24, color=k.SOFT_ON_DARK, anchor="end"),
        page.text("faculty", k.W - 82, 440, FACULTY, size=24, color=k.SOFT_ON_DARK,
                  anchor="end"),
        page.text("place", k.W - 82, 484, PLACE, size=28, color=k.TEXT_ON_DARK,
                  anchor="end", weight="bold"),
        page.text("cover-data", 196, 140,
                  f"{fmt_int(split['total'])} ảnh · 4 lớp · mô hình học máy cổ điển",
                  size=24, color=k.SOFT_ON_DARK),
    )
    return page


# ------------------------------------------------------------------ slide 2
def slide_02() -> k.Page:
    from .texts import TAKEAWAYS

    page = k.Page("02_lotrinh.svg", layout="content", kicker=CH1, page_no=2,
                  title="Ba câu hỏi, sáu chương, ba điểm mang về",
                  source="Nguồn: report/README.md · slides/texts.py (T1–T3) · results/")
    page.content(page.text("roadmap-label", 82, 210, "SÁU CHƯƠNG BÁO CÁO", size=24,
                           color=k.TEAL, weight="bold"))
    for index, (number, name, hint) in enumerate(CHAPTERS):
        column, row = divmod(index, 3)
        x = 82 + column * 300
        y = 232 + row * 132
        zone = page.zone(f"ch{number}", x, y, 288, 124)
        zone.card()
        zone.text(f"ch{number}-num", x + 16, y + 36, f"Ch.{number}", size=28, color=k.TEAL,
                  weight="bold")
        zone.text(f"ch{number}-name", x + 16, y + 68, name, size=24, color=k.INK,
                  max_width=256, line_h=30)
        page.content(zone.done())

    page.content(page.text("take-label", 700, 210, "BA ĐIỂM MANG VỀ", size=24,
                           color=k.TEAL, weight="bold"))
    y = 232
    for key in ("T1", "T2", "T3"):
        zone = page.zone(key, 700, y, 498, 124)
        zone.card(fill=k.TEAL_PALE, stroke=k.TEAL_LIGHT)
        zone.text(f"{key}-key", 720, y + 36, key, size=28, color=k.TEAL, weight="bold")
        zone.text(f"{key}-text", 720, y + 70, TAKEAWAYS[key], size=24, color=k.INK,
                  max_width=458, line_h=30)
        page.content(zone.done())
        y += 132
    return page


# ------------------------------------------------------------------ slide 3
def slide_03() -> k.Page:
    split = D["split"]
    page = k.Page("03_dulieu.svg", layout="content", kicker=CH1, page_no=3,
                  title=f"{fmt_int(split['total'])} ảnh, bốn lớp, lớp đông nhất\n"
                        f"gấp {fmt(split['ratio'], 1)} lần lớp hiếm nhất",
                  source="Nguồn: splits/split_v1.csv · results/b0_majority/metrics.json")
    page.content(page.text("classes-label", 82, 210, "PHÂN BỐ BỐN LỚP", size=24,
                           color=k.TEAL, weight="bold"))
    order = ["Normal", "Lung_Opacity", "COVID", "Viral Pneumonia"]
    top = max(split["per_class"][name] for name in order)
    for index, name in enumerate(order):
        count = split["per_class"][name]
        y = 248 + index * 88
        zone = page.zone(f"cls{index}", 82, y, 700, 84)
        zone.add(page.text(f"cls{index}-name", 82, y + 24, CLASS_VI[name], size=24,
                           color=k.INK))
        zone.add(page.rect(f"cls{index}-track", 266, y, 300, 26, fill="#E6DFCF", radius=13))
        zone.add(page.rect(f"cls{index}-fill", 266, y, max(8, 300 * count / top), 26, fill=k.TEAL,
                           radius=13))
        zone.add(page.text(f"cls{index}-num", 646, y + 24, fmt_int(count), size=24,
                           color=k.INK, weight="bold", anchor="end"))
        zone.add(page.text(f"cls{index}-share", 266, y + 58,
                           f"{fmt_pct(count / split['total'], 1)} của toàn bộ", size=24,
                           color=k.INK_SOFT))
        page.content(zone.done())

    zone = page.zone("sum-card", 830, 240, 368, 268)
    zone.card()
    zone.text("sum-num", 856, 306, fmt_int(split["total"]), size=52, color=k.TEAL,
              weight="bold")
    zone.text("sum-cap", 856, 342, "ảnh trong bộ dữ liệu gốc", size=24, color=k.INK_SOFT)
    zone.line("sum-rule", 856, 368, 1174, 368, stroke=k.LINE)
    zone.text("sum-ratio", 856, 416, fmt(split["ratio"], 1) + "×", size=34, color=k.INK,
              weight="bold")
    zone.text("sum-ratio-cap", 856, 452, "tỉ lệ Normal trên Viral Pneumonia", size=24,
              color=k.INK_SOFT, max_width=320, line_h=30)
    page.content(zone.done())
    page.content(
        k.note_zone(page, "sum-note", 856, 520, 316,
                    f"Đoán toàn bộ là Normal: {fmt(D['baselines']['b0'])} (B0).",
                    size=24, line_h=30),
    )
    return page


# ------------------------------------------------------------------ slide 4
def slide_04() -> k.Page:
    page = k.Page("04_cauhoi.svg", layout="content", kicker=CH1, page_no=4,
                  title="Ba câu hỏi và một ranh giới: chỉ học máy cổ điển",
                  source="Nguồn: results/threshold_v3.md mục 1 · report/01 mục 1.4")
    questions = [
        ("RQ1", "Nhóm đặc trưng nào lấy được tín hiệu nhất?",
         "Bốn nhóm: histogram, GLCM+LBP, HOG, ghép; so bằng macro-F1 và CI 95%."),
        ("RQ2", "Bộ phân loại nào phù hợp với 152 chiều đặc trưng?",
         "Sáu bộ trên cùng vectơ; siêu tham số chọn bằng 5-fold CV. DT, RF, GB chạy ba seed."),
        ("RQ3", "Che và cắt vùng phổi có làm đổi macro-F1 không?",
         "Năm kịch bản: huấn luyện và đánh giá cùng một chế độ ảnh, đo lại trên cùng tập."),
    ]
    for index, (name, question, detail) in enumerate(questions):
        x = 82 + index * 380
        zone = page.zone(name, x, 204, 352, 292)
        zone.card()
        zone.text(f"{name}-tag", x + 20, 242, name, size=28, color=k.TEAL, weight="bold")
        zone.text(f"{name}-q", x + 20, 276, question, size=28, color=k.INK, max_width=312,
                  line_h=34)
        zone.text(f"{name}-d", x + 20, 386, detail, size=24, color=k.INK_SOFT, max_width=312,
                  line_h=30)
        page.content(zone.done())

    zone = page.zone("h7-band", 82, 508, 1116, 112)
    zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
    zone.text("h7-tag", 102, 536, "RANH GIỚI H7", size=24, color=k.AMBER, weight="bold")
    zone.text("h7-text", 102, 574,
              "Chỉ dùng học máy cổ điển với đặc trưng thủ công — không Deep Learning "
              "(mạng nơ-ron); ảnh gốc xám 299×299, không dữ liệu ngoài bộ đã công bố.",
              size=24, color=k.INK, max_width=1076, line_h=30)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 5
def slide_05() -> k.Page:
    sources = D["sources"]
    page = k.Page("05_nguon.svg", layout="content", kicker=CH2, page_no=5,
                  title="Nhãn lớp không độc lập với nguồn ảnh",
                  source="Nguồn: results/eda/normal_source_labels.csv · splits/split_v1.csv "
                         "· docs/dataset_provenance.md mục 2.1")
    blocks = [
        ("Rahman và cộng sự (2021) — bộ COVQU", fmt_int(sources["covqu"]),
         f"COVID {fmt_int(sources['covid'])} · Lung Opacity "
         f"{fmt_int(sources['lung_opacity'])} · Normal {fmt_int(sources['normal_rsna'])} "
         f"(nhóm RSNA)"),
        ("Mooney et al. — Normal", fmt_int(sources["normal_mooney"]),
         "mẫu Normal ghi nhãn từ bộ Chest X-Ray Images (Pneumonia)"),
        ("Mooney et al. — Viral Pneumonia", fmt_int(sources["viral"]),
         "toàn bộ lớp Viral Pneumonia đến từ một nguồn"),
    ]
    for index, (name, count, detail) in enumerate(blocks):
        x = 82 + index * 380
        zone = page.zone(f"src{index}", x, 204, 352, 318)
        zone.card()
        zone.text(f"src{index}-name", x + 20, 240, name, size=24, color=k.TEAL, weight="bold",
                  max_width=312, line_h=30)
        zone.text(f"src{index}-count", x + 20, 340, count, size=46, color=k.INK, weight="bold")
        zone.text(f"src{index}-detail", x + 20, 440, detail, size=24, color=k.INK_SOFT,
                  max_width=312, line_h=30)
        page.content(zone.done())
    page.content(
        k.note_zone(page, "src-note", 82, 534, 1116,
                    f"{fmt_int(sources['total'])} ảnh ghép từ nhiều nguồn công bố; "
                    f"{fmt_int(sources['mooney_total'])} ảnh thuộc bộ Kaggle của Mooney. "
                    f"Cùng nhãn Normal, hai nguồn có thể khác thiết bị, dải sáng và "
                    f"tỉ lệ bệnh.",
                    fill=k.TEAL_PALE, size=24, line_h=28),
    )
    return page


# ------------------------------------------------------------------ slide 6
def slide_06() -> k.Page:
    covid = next(row for row in D["brightness"] if row["label"] == "COVID")
    page = k.Page("06_dosang.svg", layout="content", kicker=CH2, page_no=6,
                  title="A0 chỉ đọc metadata tệp, không nhìn ảnh: 0,2397",
                  source="Nguồn: results/eda/brightness_by_class.csv · "
                         "results/a0_shortcut, b0_majority/metrics.json · "
                         "results/threshold_v3.md mục 3")
    zone = page.zone("chart", 82, 208, 748, 410)
    zone.card()
    zone.image("brightness", "../images/fig_brightness.png", 96, 222, 720, 300)
    zone.text("chart-cap", 96, 552,
              "Thanh: khoảng tứ phân vị · gạch: trung bình. Bốn lớp vẫn phủ lên nhau.",
              size=24, color=k.INK_SOFT, max_width=700, line_h=30)
    page.content(zone.done())

    stats = [
        ("AUC COVID/nền", fmt(covid["auc_vs_rest"]),
         "phân biệt COVID nhờ độ sáng trung bình"),
        ("A0 (chỉ metadata)", fmt(D["baselines"]["a0"]),
         "chỉ đọc thuộc tính tệp, không nhìn ảnh; "
         "B0 đoán toàn bộ là Normal"),
    ]
    for index, (caption, value, note) in enumerate(stats):
        y = 208 + index * 208
        zone = page.zone(f"num{index}", 858, y, 340, 196)
        zone.card()
        zone.text(f"num{index}-cap", 878, y + 32, caption, size=24, color=k.INK_SOFT)
        zone.text(f"num{index}-val", 878, y + 84, value, size=40, color=k.TEAL, weight="bold")
        zone.text(f"num{index}-note", 878, y + 124, note, size=24, color=k.INK, max_width=300,
                  line_h=28)
        page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 7
def slide_07() -> k.Page:
    split = D["split"]
    pairs = D["pairs"]
    dup = D["duplicates"]
    page = k.Page("07_trunglap.svg", layout="content", kicker=CH2, page_no=7,
                  title="Trùng tuyệt đối bị chặn, gần trùng thì không",
                  source="Nguồn: splits/README.md mục 3 · splits/split_v1.csv")
    page.content(page.text("split-label", 82, 222, "BA TẬP SAU KHI TÁCH NHÓM", size=24,
                           color=k.TEAL, weight="bold"))
    for index, (name, count) in enumerate([("train", split["per_split"]["train"]),
                                           ("val", split["per_split"]["val"]),
                                           ("test", split["per_split"]["test"])]):
        x = 82 + index * 220
        page.content(
            page.text(f"sp{index}", x, 272, fmt_int(count), size=40, color=k.TEAL, weight="bold"),
            page.text(f"sp{index}-cap", x, 314, name, size=24, color=k.INK_SOFT),
        )

    zone = page.zone("exact-card", 82, 336, 528, 196)
    zone.card()
    zone.text("exact-num", 102, 384, fmt_int(dup["exact_groups"]), size=34, color=k.INK,
              weight="bold")
    zone.text("exact-num2", 102 + k.measure(fmt_int(dup["exact_groups"]), 34, weight="bold") + 14,
              384, "nhóm trùng tuyệt đối", size=24, color=k.INK_SOFT)
    zone.text("exact-note", 102, 418,
              f"{fmt_int(dup['exact_images'])} ảnh nằm trong các nhóm này; nhóm trùng khác nhãn: "
              f"{dup['cross_class_groups']}.", size=24, color=k.INK, max_width=490, line_h=30)
    zone.text("exact-note2", 102, 484,
              "Cùng một nhóm pHash tuyệt đối bị ép về một tập, nên không thể xuất hiện ở cả hai.",
              size=24, color=k.INK_SOFT, max_width=490, line_h=30)
    page.content(zone.done())

    zone = page.zone("near-card", 640, 336, 558, 196)
    zone.card(fill=k.AMBER_PALE, stroke=k.AMBER)
    zone.text("near-num", 660, 384, fmt_int(pairs["total"]), size=34, color=k.AMBER, weight="bold")
    zone.text("near-num2", 660 + k.measure(fmt_int(pairs["total"]), 34, weight="bold") + 14, 384,
              "cặp gần trùng nằm khác tập", size=24, color=k.INK_SOFT)
    zone.text("near-note", 660, 418,
              "test–train 325 · train–val 335 · test–val 75; trong đó 229 cặp lệch nhãn.",
              size=24, color=k.INK, max_width=518, line_h=30)
    zone.text("near-note2", 660, 484,
              f"Cặp có khoảng cách Hamming ≤ 4 trong toàn bộ dữ liệu: "
              f"{fmt_int(D['pairs_detail']['total_d1_4'])}.",
              size=24, color=k.INK_SOFT, max_width=518, line_h=30)
    page.content(zone.done())

    zone = page.zone("sha-card", 82, 540, 1116, 78)
    zone.card(fill=k.PLATE, stroke=None)
    zone.text("sha-key", 102, 576, "SHA-256", size=24, color=k.INK_SOFT, weight="bold")
    zone.text("sha-val", 262, 576, f"{split['sha256'][:24]}…", size=24, color=k.INK)
    zone.text("sha-note", 262, 602, "băm của splits/split_v1.csv, ghi trong biên bản mở "
              "khóa test.", size=24, color=k.INK_SOFT)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 8
def slide_08() -> k.Page:
    features = D["features"]
    split = D["split"]
    hog = next(row for row in D["rq1"] if row["key"] == "hog")
    cost = D["rq1_cost"]["by_group"]
    hog_cost, glcm_cost = cost["hog"], cost["glcmlbp"]
    page = k.Page("08_dactrung.svg", layout="content", kicker=CH2, page_no=8,
                  title=f"{features['total']} chiều thủ công, chuẩn hóa chỉ trên train",
                  source="Nguồn: src/features_*.py · report/02 mục 2.6–2.7 "
                         "· results/report_rq1/r1_summary.csv")
    stations = [
        ("Ảnh gốc", "299×299", "một kênh xám, không resize lại"),
        ("Histogram", f"{features['hist']} chiều", "phân bố mức xám"),
        ("GLCM + LBP", f"{features['glcm'] + features['lbp']} chiều", "texture hai vùng"),
        ("Ghép", f"{features['total']} chiều", "ba khối cùng một vectơ"),
        ("Chuẩn hóa", "fit trên train", f"scaler học {fmt_int(split['per_split']['train'])} ảnh"),
        ("SVM RBF", "bộ phân loại", "mô hình đóng băng, một seed"),
    ]
    for index, (name, value, note) in enumerate(stations):
        x = 82 + index * 188
        zone = page.zone(f"st{index}", x, 208, 170, 252)
        zone.card()
        zone.text(f"st{index}-name", x + 14, 244, name, size=24, color=k.TEAL, weight="bold",
                  max_width=142, line_h=30)
        zone.text(f"st{index}-val", x + 14, 312, value, size=24, color=k.INK, weight="bold",
                  max_width=152, line_h=30)
        zone.text(f"st{index}-note", x + 14, 380, note, size=24, color=k.INK_SOFT,
                  max_width=142, line_h=30)
        page.content(zone.done())
        if index < len(stations) - 1:
            ax = x + 173
            ay = 344
            page.content(
                page.line(f"st{index}-arrow-shaft", ax, ay, ax + 12, ay,
                          stroke=k.TEAL_LIGHT, width=2.0),
                page.line(f"st{index}-arrow-head1", ax + 7, ay - 4.5, ax + 12, ay,
                          stroke=k.TEAL_LIGHT, width=2.0),
                page.line(f"st{index}-arrow-head2", ax + 7, ay + 4.5, ax + 12, ay,
                          stroke=k.TEAL_LIGHT, width=2.0),
            )

    zone = page.zone("hog-band", 82, 472, 1116, 148)
    zone.card(fill=k.TEAL_PALE, stroke=k.TEAL_LIGHT)
    zone.text("hog-tag", 102, 498, "HOG ĐO RIÊNG", size=24, color=k.TEAL, weight="bold")
    zone.text("hog-num", 102, 560, fmt_int(features["hog"]) + " chiều", size=34, color=k.INK,
              weight="bold")
    zone.text("hog-note", 420, 500,
              f"HOG sinh nhiều chiều nhất nhưng là nhóm yếu nhất: macro-F1 "
              f"{fmt(hog['macro_f1'])}. Chi phí do phép trích: HOG 10.404 chiều "
              f"{fmt_seconds(hog_cost['per_image'])}/ảnh, GLCM+LBP 88 chiều "
              f"{fmt_seconds(glcm_cost['per_image'])}/ảnh.",
              size=24, color=k.INK, max_width=746, line_h=32)
    page.content(zone.done())
    return page


# ------------------------------------------------------------------ slide 9
def slide_09() -> k.Page:
    svm = next(row for row in D["rq2"] if row["key"] == "svm")
    cv = D["svm_cv"]
    page = k.Page("09_giaithuat.svg", layout="content", kicker=CH2, page_no=9,
                  title="Sáu bộ phân loại, một thước đo duy nhất",
                  source="Nguồn: results/report_rq2/r1_summary.csv · "
                         "results/report_rq2/r1_bootstrap_vs_reference.csv · "
                         "results/threshold_v3.md mục 3 và 5")
    page.content(page.text("classifiers-label", 82, 216,
                           "SÁU BỘ PHÂN LOẠI TRÊN CÙNG VECTƠ 152 CHIỀU",
                           size=24, color=k.TEAL, weight="bold"))
    names = ["Logistic Regression", "k-NN", "Decision Tree", "Random Forest",
             "Gradient Boosting", "SVM RBF"]
    for index, name in enumerate(names):
        y = 252 + index * 40
        page.content(
            page.text(f"name{index}", 82, y, f"{index + 1}", size=28, color=k.TEAL_LIGHT,
                      weight="bold"),
            page.text(f"name-t{index}", 116, y, name, size=28, color=k.INK, max_width=460),
        )

    page.content(k.note_zone(page, "proto-note", 82, 536, 1116,
                             "SVM tất định, chạy một lần; siêu tham số chọn từ 4 ứng viên "
                             "bằng 5-fold CV. Mỗi con số trong chương 3 là macro-F1 trên "
                             f"{fmt_int(D['split']['per_split']['val'])} ảnh validation.",
                             size=24, line_h=28))

    zone = page.zone("proto", 610, 240, 588, 280)
    zone.card()
    zone.text("proto-tag", 634, 276, "GIAO THỨC ĐO", size=24, color=k.TEAL, weight="bold")
    protocol = [
        ("Siêu tham số", "5-fold StratifiedGroupKFold"),
        ("Seed", "42 · 43 · 44 cho DT, RF, GB"),
        ("Bootstrap", "2.000 lần, CI 95% mỗi F1"),
        ("Quy ước nhóm", f"Δ ≥ {fmt(D['rules']['delta_threshold'], 3)} và CI không chứa 0"),
        ("Tham chiếu", "Random Forest của RQ1"),
    ]
    for index, (name, detail) in enumerate(protocol):
        y = 322 + index * 40
        zone.text(f"proto-name{index}", 634, y, name, size=24, color=k.INK, weight="bold",
                  max_width=190, line_h=30)
        zone.text(f"proto-detail{index}", 834, y, detail, size=24, color=k.INK_SOFT,
                  max_width=340, line_h=30)
    page.content(zone.done())
    return page


def pages():
    return [slide_01(), slide_02(), slide_03(), slide_04(), slide_05(), slide_06(), slide_07(),
            slide_08(), slide_09()]
