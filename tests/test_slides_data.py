"""Bài kiểm tra neo cho slides/data.py.

Sáu giá trị phải khớp đúng tệp nguồn; nếu CSV/JSON đổi, giá trị ở đây đổi theo
vì không có con số nào được gõ cứng trong bộ slide.
"""

from slides.data import (D, fmt, fmt_ci, fmt_delta, fmt_int, fmt_pct)


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
