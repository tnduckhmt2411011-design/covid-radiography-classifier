"""Kiểm thử đơn vị cho bộ rà soát tự động báo cáo (`scripts/audit_report.py`)."""
from __future__ import annotations

from pathlib import Path

from scripts.audit_report import (
    Finding,
    check_banned_phrases,
    check_captions_and_refs,
    check_citations,
    check_fixed_numbers,
    check_footnote_paths,
    check_h7_and_paths,
    check_section_counts,
    load_chapters,
)


def test_load_chapters_strips_technical_notes(tmp_path: Path) -> None:
    (tmp_path / "01_gioi_thieu.md").write_text(
        "# CHƯƠNG 1. GIỚI THIỆU\n\nNội dung chính.\n\n## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)\n\n- `results/a.csv`\n",
        encoding="utf-8",
    )
    (tmp_path / "07_tai_lieu_tham_khao.md").write_text("# Tài liệu tham khảo\n", encoding="utf-8")
    chapters = load_chapters(tmp_path)
    assert "01_gioi_thieu.md" in chapters
    assert "07_tai_lieu_tham_khao.md" not in chapters
    assert "Nội dung chính." in chapters["01_gioi_thieu.md"]
    assert "Ghi chú kỹ thuật" not in chapters["01_gioi_thieu.md"]
    assert "results/a.csv" not in chapters["01_gioi_thieu.md"]


def test_check_banned_phrases_d4_and_slop_and_connectors() -> None:
    d4_text = "Chênh lệch giữa val và test do đó phát sinh vì nguyên nhân quá khớp."
    findings = check_banned_phrases(d4_text, file="05_test.md")
    assert any(isinstance(f, Finding) and f.severity == "critical" and "D4" in f.rule for f in findings)

    negation_d4 = "Chênh lệch giữa validation và test được nêu như số đo, không nêu nguyên nhân."
    neg_findings = check_banned_phrases(negation_d4, file="05_test.md")
    assert not any(f.severity == "critical" and "D4" in f.rule for f in neg_findings)

    slop_text = (
        "Hơn nữa, nhóm đi sâu tìm hiểu dữ liệu. "
        "Thêm vào đó, kết quả là minh chứng hùng hồn cho phương pháp. "
        "Ngoài ra, bức tranh toàn cảnh hoàn hảo không tì vết."
    )
    slop_findings = check_banned_phrases(slop_text, file="01_gioi_thieu.md")
    assert any("slop" in f.rule.lower() for f in slop_findings)
    assert any("connector" in f.rule.lower() for f in slop_findings)


def test_check_fixed_numbers_catches_typos_dots_and_h2_leak() -> None:
    chapters = {
        "02_du_lieu_va_phuong_phap.md": "Tập validation có 3.714 ảnh và test đạt 0,8714.",
        "05_ket_qua_test_va_trien_khai.md": "Trên test: macro-F1 0.8714, tỷ lệ lỗi 71.19%.",
    }
    findings = check_fixed_numbers(chapters)
    rules = " ".join(f.rule for f in findings)
    excerpts = " ".join(f.excerpt for f in findings)
    assert "3.714" in excerpts or "fixed-number" in rules
    assert any(f.severity == "critical" and "H2" in f.rule for f in findings)
    assert any("decimal-dot" in f.rule for f in findings)


def test_check_fixed_numbers_ignores_doi_and_section_lists() -> None:
    chapters = {
        "01_gioi_thieu.md": (
            "Xem mục 2.3 và 2.4 hoặc (1.2, 1.3; 5.5.1).\n"
            "[1] Author, doi: 10.1109/ACCESS.2020.3010287.\n"
        ),
        "05_ket_qua_test_va_trien_khai.md": "| Viral Pneumonia | 200 | 0,8634 | 0,8850 | 0,8741 | 23 |\n",
    }
    findings = check_fixed_numbers(chapters)
    assert findings == []


def test_check_captions_and_refs_catches_gaps_and_unreferenced() -> None:
    chapters = {
        "03_ket_qua_rq1_rq2.md": (
            "Xem Bảng 3.1 dưới đây.\n\n"
            "**Bảng 3.1: Kết quả A**\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n"
            "**Bảng 3.3: Kết quả B**\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n"
            "![Hình minh họa](../figures/a.png)\n\n"
            "**Hình 3.1: Ảnh minh họa**\n"
        )
    }
    findings = check_captions_and_refs(chapters, check_totals=False)
    rules = [f.rule for f in findings]
    assert "caption-sequence" in rules
    assert "caption-unreferenced" in rules


def test_check_citations_order_missing_and_unused() -> None:
    chapters = {
        "01_gioi_thieu.md": "Nghiên cứu [2] trước rồi mới tới [1] và [9].",
    }
    refs = "[1] Ref one.\n[2] Ref two.\n[3] Unused ref.\n"
    findings = check_citations(chapters, refs)
    rules = {f.rule for f in findings}
    assert "citation-order" in rules
    assert "citation-missing-ref" in rules
    assert "citation-unused-ref" in rules


def test_check_section_counts_detects_mismatch() -> None:
    chapters = {
        "01_gioi_thieu.md": "\n".join(f"## 1.{i}. Mục {i}" for i in range(1, 6)),
        "02_du_lieu_va_phuong_phap.md": "\n".join(f"## 2.{i}. Mục {i}" for i in range(1, 8)),
    }
    findings = check_section_counts(chapters)
    assert any(f.file == "02_du_lieu_va_phuong_phap.md" and f.rule == "section-count" for f in findings)
    assert not any(f.file == "01_gioi_thieu.md" for f in findings)


def test_check_h7_and_paths() -> None:
    chapters = {
        "01_gioi_thieu.md": (
            "Một kiểm thử chặn `torch` và `tensorflow` trong mã.\n"
            "Nhóm dùng PyTorch để huấn luyện thêm.\n"
            "Số liệu nằm tại results/report_rq1/r1_summary.csv.\n"
        )
    }
    findings = check_h7_and_paths(chapters)
    assert any(f.severity == "critical" and f.rule == "H7" for f in findings)
    assert any(f.severity == "minor" and f.rule == "in-text-path" for f in findings)


def test_check_footnote_paths_flags_path(tmp_path: Path) -> None:
    (tmp_path / "01_gioi_thieu.md").write_text(
        "# CHƯƠNG 1. MỞ ĐẦU\n\n## Ghi chú kỹ thuật\n\n[^a]: xem docs/x.md\n[^b]: nguồn Kaggle 2020.\n",
        encoding="utf-8",
    )
    findings = check_footnote_paths(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "footnote-path"
    assert findings[0].severity == "minor"

    (tmp_path / "01_gioi_thieu.md").write_text(
        "# CHƯƠNG 1. MỞ ĐẦU\n\n## Ghi chú kỹ thuật\n\n[^b]: nguồn Kaggle 2020.\n",
        encoding="utf-8",
    )
    assert check_footnote_paths(tmp_path) == []
