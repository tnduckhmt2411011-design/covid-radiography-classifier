"""Bài kiểm tra neo cho slides/data.py.

Mười bốn giá trị phải khớp đúng tệp nguồn; nếu CSV/JSON đổi, giá trị ở đây đổi
theo vì không có con số nào được gõ cứng trong bộ slide.
"""

from slides.data import (D, fmt, fmt_ci, fmt_delta, fmt_int, fmt_pct, fmt_seconds)


def test_rq1_merged_macro_f1() -> None:
    ghep = next(row for row in D["rq1"] if row["key"] == "ghep")
    assert fmt(ghep["macro_f1"]) == "0,8599"


def test_rq2_svm_macro_f1() -> None:
    svm = next(row for row in D["rq2"] if row["key"] == "svm")
    assert fmt(svm["macro_f1"]) == "0,9024"


def test_final_test_macro_f1() -> None:
    assert fmt(D["test"]["macro_f1"]) == "0,8714"
    assert fmt_int(D["test"]["n"]) == "3.176"


def test_outside_lung_macro_f1() -> None:
    assert fmt(D["rq3"]["scenarios"]["out_to_out"]["macro_f1"]) == "0,8921"


def test_lung_drop_is_significant() -> None:
    diff = D["rq3"]["diffs"][("lung_to_lung", "orig_to_orig")]
    assert fmt_delta(diff["diff"]) == "\u22120,0535"
    assert not diff["contains_zero"]


def test_outside_beats_lung_inside_only() -> None:
    """Bằng chứng mạnh nhất của RQ3: chỉ ngoài phổi hơn chỉ trong phổi có ý nghĩa."""
    diff = D["rq3"]["diffs"][("lung_to_lung", "out_to_out")]
    assert fmt_delta(diff["diff"]) == "\u22120,0431"
    assert fmt_ci(*diff["ci"]) == "[\u22120,0582; \u22120,0281]"
    assert not diff["contains_zero"]


def test_test_error_count() -> None:
    assert fmt_int(D["test"]["errors"]) == "427"
    assert fmt_int(D["normal_lung_test"]) == "304"
    assert fmt_pct(D["normal_lung_pct"]) == "71,19%"


def test_split_totals() -> None:
    split = D["split"]
    assert fmt_int(split["total"]) == "21.165"
    assert [fmt_int(split["per_split"][k]) for k in ("train", "val", "test")] == [
        "14.815",
        "3.174",
        "3.176",
    ]


def test_test_ci() -> None:
    assert fmt_ci(*D["test_ci"]) == "[0,8579; 0,8840]"


def test_covqu_source_split() -> None:
    """18.479 ảnh thuộc bộ COVQU của Rahman và cộng sự (2021), không phải Chowdhury."""
    sources = D["sources"]
    assert fmt_int(sources["covqu"]) == "18.479"
    assert fmt_int(sources["mooney_total"]) == "2.686"
    assert sources["covid"] + sources["lung_opacity"] + sources["normal_rsna"] == 18479


def test_feature_cost_not_by_dimension() -> None:
    """HOG nhiều chiều hơn nhưng rẻ hơn: chi phí do phép trích, không do số chiều."""
    by_group = D["rq1_cost"]["by_group"]
    assert fmt_seconds(by_group["hog"]["per_image"]) == "0,0201 s"
    assert fmt_seconds(by_group["glcmlbp"]["per_image"]) == "0,0552 s"
    assert by_group["hog"]["per_image"] < by_group["glcmlbp"]["per_image"]
    assert D["features"]["hog"] > D["features"]["glcm"] + D["features"]["lbp"]


def test_svm_cv_grid() -> None:
    """SVM tất định nhưng siêu tham số vẫn chọn từ lưới bốn ứng viên."""
    cv = D["svm_cv"]
    assert cv["n_candidates"] == 4
    assert cv["n_splits"] == "5"
    assert cv["selected"]["C"] == "10.0"
    assert cv["selected"]["gamma"] == "scale"


def test_group_convention_threshold() -> None:
    """Ngưỡng 0,005 là quy ước nhóm, đọc từ threshold_v3.md."""
    rules = D["rules"]
    assert fmt(rules["delta_threshold"], 3) == "0,005"
    assert fmt_int(rules["bootstrap"]) == "2.000"
    assert rules["cv_folds"] == 5


def test_consensus_errors_are_three_models() -> None:
    """240 lỗi đồng thuận: SVM sai và GB, RF cũng sai (GB, RF theo đa số 2/3 seed)."""
    assert fmt_int(D["val_errors"]["consensus"]) == "240"


def test_latency_measured_on_laptop() -> None:
    """Độ trễ đo trên laptop, không phải máy deploy."""
    assert D["latency"]["cpu_short"] == "i5-13420H"
    assert fmt_seconds(D["latency"]["stages"]["total"], 3) == "0,132 s"
    assert D["latency"]["n_images"] == 200
