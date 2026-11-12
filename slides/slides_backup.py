"""Sáu slide dự phòng B1–B6: chỉ mở khi hội đồng hỏi, không đánh số /28."""

from __future__ import annotations

from . import svgkit as k
from .data import CLASS_VI, D, fmt, fmt_ci, fmt_delta, fmt_int, fmt_pct, fmt_seconds

PREFIX = "DỰ PHÒNG"

_STAGES = {"decode": "Giải mã ảnh", "features": "Rút đặc trưng", "inference": "Suy luận SVM",
           "total": "Tổng mỗi ảnh"}


def _page(filename: str, title: str, source: str, kicker: str) -> k.Page:
    return k.Page(filename, layout="appendix", kicker=kicker, title=f"{PREFIX} · {title}",
                  source=source, page_no=None, numbered=False)


def slide_b1() -> k.Page:
    page = _page("b1_rq1_per_seed.svg", "RQ1 từng seed và khoảng tin cậy",
                 "Nguồn: results/report_rq1/r1_per_seed.csv, r1_summary.csv · "
                 "results/threshold_v3.md mục 1 (RQ1)",
                 "CHƯƠNG 3 · DỰ PHÒNG")
    names = {"hist": "Histogram 64", "glcmlbp": "GLCM + LBP 88", "hog": "HOG 10.404",
             "ghep": "Ghép 152"}
    seeds = {}
    for row in D["rq1_per_seed"]:
        seeds.setdefault(row["features"], []).append(row["macro_f1"])
    order = ["hist", "glcmlbp", "hog", "ghep"]
    for index, key in enumerate(order):
        values = seeds[key]
        summary = next(item for item in D["rq1"] if item["key"] == key)
        y = 206 + index * 84
        zone = page.zone(f"grp{key}", 82, y, 1116, 84)
        zone.card()
        zone.text(f"grp{key}-name", 106, y + 34, names[key], size=28, color=k.TEAL,
                  weight="bold")
        zone.text(f"grp{key}-mean", 106, y + 70, f"{fmt(summary['macro_f1'])} ± "
                  f"{fmt(summary['std'])}", size=30, color=k.INK, weight="bold")
        zone.text(f"grp{key}-seeds", 480, y + 34,
                  " · ".join(fmt(value) for value in values), size=28, color=k.INK_SOFT,
                  max_width=420, line_h=30)
        zone.text(f"grp{key}-ci", 480, y + 70, f"CI 95% {fmt_ci(*summary['ci'])}", size=28,
                  color=k.INK_SOFT)
        zone.text(f"grp{key}-seed-label", 950, y + 34, "seed 42 · 43 · 44", size=24,
                  color=k.INK_SOFT)
        page.content(zone.done())
    note = ("Các seed của cùng một nhóm lệch nhau vài phần "
            "nghìn macro-F1; chênh lệch giữa các nhóm lớn hơn "
            "nhiều lần.")
    page.content(k.note_zone(page, "note", 82, 546, 1116, note, size=24, line_h=28))
    return page


def slide_b2() -> k.Page:
    page = _page("b2_rq2_day_du.svg", "RQ2 đầy đủ sáu bộ phân loại",
                 "Nguồn: results/report_rq2/r1_summary.csv · "
                  "results/report_rq2/r1_per_seed.csv", "CHƯƠNG 3 · DỰ PHÒNG")
    names = {"lr": "Logistic Regression", "knn": "k-NN", "dt": "Decision Tree",
             "rf": "Random Forest", "gb": "Gradient Boosting", "svm": "SVM RBF"}
    for index, row in enumerate(D["rq2"]):
        x = 82 + index * 188
        zone = page.zone(f"cls{index}", x, 250, 176, 210)
        zone.card()
        zone.text(f"cls{index}-name", x + 14, 286, names[row["key"]], size=24, color=k.TEAL,
                  weight="bold", max_width=148, line_h=28)
        zone.text(f"cls{index}-val", x + 14, 356, fmt(row["macro_f1"]), size=38, color=k.INK,
                  weight="bold")
        zone.text(f"cls{index}-ci", x + 14, 396, fmt_ci(*row["ci"]), size=24, color=k.INK_SOFT,
                  max_width=150, line_h=28)
        zone.text(f"cls{index}-seed", x + 14, 440, f"{row['n_seeds']} seed", size=24,
                  color=k.INK_SOFT)
        page.content(zone.done())
    page.content(k.note_zone(page, "note", 82, 490, 1116,
                             "Thứ tự sáu bộ trong báo cáo; SVM có 0,0442 chênh so với Random Forest "
                             "và khoảng tin cậy không chứa 0.", size=24))
    return page


def slide_b3() -> k.Page:
    page = _page("b3_rq3_day_du.svg", "RQ3 đủ năm kịch bản",
                 "Nguồn: results/report_rq3/r1_summary.csv · r4_sampling_error.csv",
                 "CHƯƠNG 4 · DỰ PHÒNG")
    order = ["orig_to_orig", "lung_to_lung", "out_to_out", "orig_to_lung", "orig_to_out"]
    names = {"orig_to_orig": "Gốc → gốc", "lung_to_lung": "Chỉ phổi → chỉ phổi",
             "out_to_out": "Ngoài phổi → ngoài phổi", "orig_to_lung": "Gốc → chỉ phổi",
             "orig_to_out": "Gốc → ngoài phổi"}
    recalls = {row["scenario"]: row["recall"] for row in D["rq3_per_scenario"]}
    for index, key in enumerate(order):
        x = 82 + index * 228
        scenario = D["rq3"]["scenarios"][key]
        zone = page.zone(f"sc{index}", x, 250, 216, 230)
        zone.card()
        zone.text(f"sc{index}-name", x + 16, 286, names[key], size=24, color=k.TEAL,
                  weight="bold", max_width=184, line_h=28)
        zone.text(f"sc{index}-val", x + 16, 356, fmt(scenario["macro_f1"]), size=38,
                  color=k.INK, weight="bold")
        zone.text(f"sc{index}-ci", x + 16, 396, fmt_ci(*scenario["ci"]), size=24, color=k.INK_SOFT,
                  max_width=184, line_h=28)
        recall = recalls[key]
        zone.text(f"sc{index}-recall", x + 16, 444,
                  "Recall thấp nhất: " + fmt(min(recall.values())), size=24, color=k.INK_SOFT,
                  max_width=184, line_h=28)
        page.content(zone.done())
    page.content(k.note_zone(page, "note", 82, 500, 1116,
                              "Hai kịch bản cuối học trên ảnh gốc nhưng đánh giá trên ảnh đã bị che; "
                              "chúng cho thấy tập huần luyện và tập đánh giá là hai phân bố khác nhau. Quy ước A → B: huần luyện trên ảnh dạng A, đánh giá trên ảnh dạng B.",
                             size=24))
    return page


def slide_b4() -> k.Page:
    page = _page("b4_cap_gan_trung.svg", "735 cặp gần trùng",
                 "Nguồn: splits/README.md mục 3 · splits/split_v1.csv · "
                 "results/eda", "CHƯƠNG 4 · DỰ PHÒNG")
    detail = D["pairs_detail"]
    page.content(page.text("split-label", 82, 214, "THEO CẶP SPLIT", size=24, color=k.TEAL,
                           weight="bold"))
    labels = {"test-train": "test ↔ train", "train-val": "train ↔ val", "test-val": "test ↔ val"}
    for index, (key, count) in enumerate(detail["by_split"].items()):
        x = 82 + index * 380
        zone = page.zone(f"sp{index}", x, 240, 352, 140)
        zone.card()
        zone.text(f"sp{index}-val", x + 20, 310, fmt_int(count), size=48, color=k.TEAL,
                  weight="bold")
        zone.text(f"sp{index}-cap", x + 20, 342, labels.get(key, key), size=24, color=k.INK_SOFT)
        page.content(zone.done())
    page_content = [
        ("Khoảng cách 4", detail["by_distance"]["4"], "cặp có Hamming = 4"),
        ("Khoảng cách 2", detail["by_distance"]["2"], "cặp có Hamming = 2"),
        ("Lệch nhãn", detail["class_relation"]["Cross-Class_d4"] + detail["class_relation"]["Cross-Class_d2"],
         "cặp gần trùng nhưng ghi nhãn khác nhau"),
    ]
    for index, (name, value, note) in enumerate(page_content):
        x = 82 + index * 380
        zone = page.zone(f"d{index}", x, 392, 352, 132)
        zone.card()
        zone.text(f"d{index}-name", x + 20, 428, name, size=24, color=k.INK_SOFT)
        zone.text(f"d{index}-val", x + 20, 478, fmt_int(value), size=34, color=k.INK,
                  weight="bold")
        zone.text(f"d{index}-note", x + 190, 436, note, size=24, color=k.INK, max_width=150,
                  line_h=28)
        page.content(zone.done())
    page.content(k.note_zone(page, "note", 82, 536, 1116,
                             f"Trong toàn bộ dữ liệu có {fmt_int(detail['total_d1_4'])} cặp có "
                             "khoảng cách Hamming ≤ 4; 735 trong số đó nằm khác tập.", size=24))
    return page


def slide_b5() -> k.Page:
    page = _page("b5_loi_val.svg", "Ma trận nhầm lẫn validation",
                 "Nguồn: results/error_analysis/val_misclassified_cases.csv, "
                 "confusion_pairs_summary.csv", "CHƯƠNG 4 · DỰ PHÒNG")
    errors = D["val_errors"]
    items = [
        ("Lỗi trên validation", fmt_int(errors["n"]), "ảnh dự đoán sai trên 3.174 ảnh"),
        ("Lỗi cặp Normal ↔ LO", fmt_int(errors["normal_lung_opacity"]),
         "cặp nhầm lẫn đông nhất"),
        ("Lỗi đồng thuận", fmt_int(errors["consensus"]),
         "SVM sai và GB, RF cũng sai (GB, RF lấy đa số 2/3 seed)"),
        ("Lỗi p ≥ 0,80", fmt_int(errors["high_confidence"]),
         f"{fmt_pct(errors['high_confidence_pct'], 1)} số lỗi tự tin ở mức cao"),
    ]
    for index, (name, value, note) in enumerate(items):
        x = 82 + index * 284
        zone = page.zone(f"item{index}", x, 250, 268, 212)
        zone.card()
        zone.text(f"item{index}-name", x + 16, 286, name, size=24, color=k.INK_SOFT,
                  max_width=236, line_h=28)
        zone.text(f"item{index}-val", x + 16, 350, value, size=44, color=k.AMBER,
                  weight="bold")
        zone.text(f"item{index}-note", x + 16, 392, note, size=24, color=k.INK, max_width=236,
                  line_h=28)
        page.content(zone.done())
    page_content = ("138 lỗi trong tổng số 349 lỗi được mô hình dự đoán với xác suất từ 0,80 "
                    "trở lên, nên nói “mô hình không biết mình sai” là không đúng trên toàn bộ "
                    "tập lỗi.")
    page.content(k.note_zone(page, "note", 82, 474, 1116, page_content, size=28, line_h=34))
    return page


def slide_b6() -> k.Page:
    page = _page("b6_latency.svg", "Độ trễ đo trên 200 ảnh",
                 "Nguồn: results/demo_latency_sustained/latency.json · outputs/k_v3_out",
                 "CHƯƠNG 5 · DỰ PHÒNG")
    detail = D["latency_detail"]["stages"]
    for index, (key, value) in enumerate(detail.items()):
        zone = page.zone(f"st{index}", 82, 244 + index * 80, 658, 72)
        zone.card()
        zone.text(f"st{index}-name", 102, 280 + index * 80, _STAGES[key], size=28,
                  color=k.INK)
        zone.text(f"st{index}-median", 480, 280 + index * 80, fmt_seconds(value["median"]),
                  size=30, color=k.TEAL, weight="bold", anchor="end")
        zone.text(f"st{index}-p95", 720, 280 + index * 80, f"p95 {fmt_seconds(value['p95'])}",
                  size=24, color=k.INK_SOFT, anchor="end")
        page.content(zone.done())

    artifact = D["latency"]
    zone = page.zone("art", 762, 244, 436, 312)
    zone.card()
    zone.text("art-tag", 784, 280, "ARTIFACT ĐÓNG BĂNG", size=24, color=k.TEAL,
              weight="bold")
    items = [
        ("Kích thước", fmt(artifact["artifact_bytes"] / 1_000_000, 2) + " MB"),
        ("Số vector", fmt_int(artifact["n_support_vectors"])),
        ("Ảnh train", fmt_int(artifact["n_train"])),
        ("SHA-256", artifact["artifact_sha256"][:15] + "…"),
        ("Máy", artifact["cpu"]),
    ]
    for index, (name, value) in enumerate(items):
        y = 314 + index * 48
        zone.text(f"art{index}-name", 784, y, name, size=24, color=k.INK_SOFT)
        zone.text(f"art{index}-value", 930, y, value, size=24, color=k.INK, max_width=240,
                  line_h=28)
    page.content(zone.done())
    note = (f"Đo trên {artifact['n_images']} ảnh validation, {artifact['repeats']} lượt, máy {artifact['cpu']}.")
    page.content(k.note_zone(page, "note", 82, 570, 1116, note, size=24, line_h=28))
    return page


def pages():
    return [slide_b1(), slide_b2(), slide_b3(), slide_b4(), slide_b5(), slide_b6()]
