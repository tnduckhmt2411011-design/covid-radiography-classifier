"""Hang rao nhat quan noi bo giua cac chuong bao cao (sau dot ra review senior)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "report"


def _body(name: str) -> str:
    """Than bai cua mot tep: bo phan tai lieu tham khao va ghi chu ky thuat."""
    text = (REPORT / name).read_text(encoding="utf-8")
    for marker in ("## Tài liệu tham khảo phát sinh trong chương", "## Ghi chú kỹ thuật"):
        if marker in text:
            text = text.split(marker)[0]
    return text


def _rows(name: str, caption_re: str) -> list[str]:
    body = _body(name)
    m = re.search(caption_re, body)
    assert m, caption_re
    rows = []
    for line in body[m.end():].splitlines():
        if line.startswith("|"):
            rows.append(line)
        elif rows:
            break
    return rows


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def test_rq3_decision_rule_lists_registered_comparisons() -> None:
    """Dong RQ3 cua Bang 1.1 phai neu ca hai phep so da dang ky truoc."""
    rows = _rows("01_gioi_thieu.md", r"\*\*Bảng 1\.1:")
    rq3 = next(r for r in rows if _cells(r)[0] == "RQ3")
    rule = _cells(rq3)[-1]
    assert "chỉ phổi" in rule and "ngoài phổi" in rule, rule
    roles = " ".join(_cells(r)[-1] for r in _rows("04_hoc_loi_tat_rq3.md", r"\*\*Bảng 4\.2:"))
    assert "Phép so chính" in roles
    assert "Bắt buộc trình bày" in roles


def test_hamming_levels_are_even_levels_only() -> None:
    """Khoang cach Hamming chi o muc 2 va 4 o moi chuong neu so do."""
    for name in ("02_du_lieu_va_phuong_phap.md", "06_thao_luan_gioi_han_huong_phat_trien.md"):
        body = _body(name)
        assert "từ 1 đến 4" not in body, name
        assert ("từ 2 đến 4" in body) or ("mức 2 và 4" in body), name


def test_chapter1_has_no_internal_codes_or_overclaim() -> None:
    """Chuong 1 khong giu ma hieu noi bo va khong hua qua ve RQ3."""
    body = _body("01_gioi_thieu.md")
    for code in ("H2", "H6", "H7", "D4"):
        assert not re.search(rf"\b{code}\b", body), code
    for phrase in ("giải quyết RQ3", "đo nó trực tiếp", "hoặc cắt"):
        assert phrase not in body, phrase


def test_appendix_a_table_captions_in_order() -> None:
    """Bang A.1 (mo hinh dong bang) xuat hien truoc Bang A.2 (bien moi truong)."""
    body = _body("08_phu_luc_a_c.md")
    i1 = body.find("**Bảng A.1: Thông số mô hình đóng băng**")
    i2 = body.find("**Bảng A.2: Biến môi trường của ứng dụng demo**")
    assert i1 != -1, "thieu Bang A.1 Thong so mo hinh dong bang"
    assert i2 != -1, "thieu Bang A.2 Bien moi truong"
    assert i1 < i2, "Bang A.1 phai truoc Bang A.2"
    sha_row = next(r for r in body.splitlines() if r.startswith("| `CXR_MODEL_SHA256`"))
    assert "Bảng A.1" in sha_row and "Bảng A.2" not in sha_row, sha_row


def test_appendix_c1_class_weight_sentence() -> None:
    """Cau trong so lop o Phu luc C.1 phai dung co che tung bo phan loai."""
    from src.rq2_runner import CLASSIFIER_SPECS

    modes = {k: v["class_weight_mode"] for k, v in CLASSIFIER_SPECS.items()}
    assert modes["rf"] == "balanced_subsample"
    assert modes["gb"] == "sample_weight"
    assert modes["knn"] == "none"
    for k in ("lr", "dt", "svm"):
        assert modes[k] == "balanced"
    body = _body("08_phu_luc_a_c.md")
    assert "class_weight='balanced'" in body
    assert "class_weight='balanced_subsample'" in body, "thieu co che balanced_subsample cua Random Forest"
    assert "trọng số mẫu cân bằng truyền vào bước fit" in body, "thieu co trong so mau cua Gradient Boosting"
    assert "không có cơ chế cân bằng lớp" in body, "thieu cau knn khong can bang lop"
    assert "cân bằng bằng `weights='distance'`" not in body, "sai: weights='distance' khong can bang lop"
    assert "cổng H3" not in body, "khong dung ma hieu noi bo trong phu luc"


def test_reference_list_contiguous_and_matches_ch5() -> None:
    """Danh muc 07 phai co [1]..[13] lien tuc; hai muc cuoi khop danh muc Chuong 5."""
    ref = (REPORT / "07_tai_lieu_tham_khao.md").read_text(encoding="utf-8")
    numbered: dict[int, str] = {}
    for line in ref.splitlines():
        m = re.match(r"\[(\d+)\] ", line)
        if m:
            numbered[int(m.group(1))] = line
    assert sorted(numbered) == list(range(1, 14)), sorted(numbered)
    ch5 = (REPORT / "05_ket_qua_test_va_trien_khai.md").read_text(encoding="utf-8")
    for n in (12, 13):
        assert numbered[n] in ch5, f"[{n}] khong khop danh muc Chuong 5"
    # Cau dan danh muc Chuong 5 phai tro dung so bat dau cua danh muc do.
    ch5_numbers = [int(m.group(1)) for line in ch5.splitlines()
                   if (m := re.match(r"\[(\d+)\] ", line))]
    assert ch5_numbers, "danh muc Chuong 5 rong"
    lead = re.search(r"đánh tiếp từ \[(\d+)\]", ch5)
    assert lead, "thieu cau dan 'danh tiep tu [n]' o Chuong 5"
    assert int(lead.group(1)) == min(ch5_numbers), (
        f"cau dan ghi [{lead.group(1)}], danh muc bat dau [{min(ch5_numbers)}]")


def test_ch2_near_duplicate_claim_matches_json() -> None:
    """Ch2 khong duoc noi 'chua do muc chenh' khi JSON da co khoang tin cay."""
    body = _body("02_du_lieu_va_phuong_phap.md")
    assert "chưa đo mức chênh này" not in body
    assert "chưa tách được ảnh hưởng của bản gần trùng lúc huấn luyện" in body
    rec = json.loads((REPO_ROOT / "results/val_near_duplicate_subset/"
                      "val_near_duplicate_subset.json").read_text(encoding="utf-8"))
    ci = rec["bootstrap_ci"]
    lo_txt = f"{abs(ci['lo']):.4f}".replace(".", ",")
    hi_txt = f"{ci['hi']:.4f}".replace(".", ",")
    assert lo_txt in body and hi_txt in body, (lo_txt, hi_txt)


def test_readme_limit_count_matches_ch6() -> None:
    """So hang muc gioi han ghi trong README phai bang so hang muc cua Chuong 6."""
    body = _body("06_thao_luan_gioi_han_huong_phat_trien.md")
    section = re.search(r"(?s)## 6\.2\..*?(?=## 6\.3\.)", body)
    assert section, "thieu muc 6.2 cua Chuong 6"
    nums = [int(n) for n in re.findall(r"(?m)^(\d+)\. \*\*", section.group(0))]
    assert nums == list(range(1, len(nums) + 1)), nums
    assert len(nums) == 12, f"Chuong 6 co {len(nums)} hang muc, ky vong 12"
    readme = (REPORT / "README.md").read_text(encoding="utf-8")
    assert f"Gồm {len(nums)} hạng mục" in readme, f"README chua 'Gom {len(nums)} hang muc'"


def test_abstract_mentions_inference_masking() -> None:
    """Tom tat phai neu hai so macro-F1 khi chi con vung phoi / vung ngoai mat na."""
    ab = (REPORT / "09_tom_tat_abstract.md").read_text(encoding="utf-8")
    assert "0,0723" in ab and "0,2084" in ab, "tom tat thieu hai so RQ3 che mat na"
    joined = " ".join(_rows("04_hoc_loi_tat_rq3.md", r"\*\*Bảng 4\.1"))
    assert "0,0723" in joined and "0,2084" in joined, "Bang 4.1 thieu hai so nguon"
