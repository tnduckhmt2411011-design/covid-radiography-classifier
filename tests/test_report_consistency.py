"""Hang rao nhat quan noi bo giua cac chuong bao cao (sau dot ra review senior)."""

from __future__ import annotations

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
