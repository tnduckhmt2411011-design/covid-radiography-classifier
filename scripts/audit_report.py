"""Kiểm tra tự động văn phong, số liệu, bảng/hình, trích dẫn và cổng H2/H7/D4 của báo cáo.

Chạy: python -m scripts.audit_report
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO_ROOT / "report"

CHAPTER_FILES = [
    "01_gioi_thieu.md",
    "02_du_lieu_va_phuong_phap.md",
    "03_ket_qua_rq1_rq2.md",
    "04_hoc_loi_tat_rq3.md",
    "05_ket_qua_test_va_trien_khai.md",
    "06_thao_luan_gioi_han_huong_phat_trien.md",
]
BODY_AND_APPENDIX_FILES = CHAPTER_FILES + ["08_phu_luc_a_c.md"]

EXPECTED_SUBSECTIONS = {
    "01_gioi_thieu.md": 5,
    "02_du_lieu_va_phuong_phap.md": 12,
    "03_ket_qua_rq1_rq2.md": 4,
    "04_hoc_loi_tat_rq3.md": 3,
    "05_ket_qua_test_va_trien_khai.md": 8,
    "06_thao_luan_gioi_han_huong_phat_trien.md": 5,
}

SLOP_PHRASES = [
    "bức tranh toàn cảnh",
    "bức tranh đa sắc",
    "miền đất màu mỡ",
    "miền đất mới",
    "minh chứng hùng hồn",
    "minh chứng sống động",
    "ngọn hải đăng",
    "lặn sâu",
    "đi sâu tìm hiểu",
    "mổ xẻ tường tận",
    "thấu suốt",
    "bản giao hưởng",
    "bản anh hùng ca",
    "vũ trụ bao la",
    "kỷ nguyên bùng nổ",
    "kỷ nguyên số",
    "chuyển mình mạnh mẽ",
    "không thể phủ nhận",
    "vai trò tối thượng",
    "chiếc chìa khóa vạn năng",
    "hoàn hảo không tì vết",
    "chính xác tuyệt đối",
    "cẩn trọng tột cùng",
    "hiệu năng thần kỳ",
    "sức mạnh vượt bậc",
    "bước ngoặt mang tính cách mạng",
    "liền mạch như dòng chảy",
    "nhịp nhàng như giao hưởng",
    "không thể không nhắc đến",
    "nhấn mạnh tầm quan trọng to lớn",
    "mở ra một chân trời mới",
    "đóng góp vào sự phát triển bền vững",
]

CONNECTOR_STARTERS = (
    "hơn thế nữa",
    "hơn nữa",
    "thêm vào đó",
    "ngoài ra",
    "mặt khác",
    "do đó",
    "vì vậy",
    "tóm lại",
)

D4_NEGATION_RE = re.compile(
    r"không\s+(?:được\s+)?(?:nêu|nối\s+chúng\s+với|kèm\s+diễn\s+giải|gán|giải\s+thích|kết\s+luận)\s+nguyên\s+nhân",
    re.IGNORECASE,
)

FIXED_NUMBER_TYPOS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?<!\d)3\.714(?!\d)"), "3.714 (nhầm với 3.174?)"),
    (re.compile(r"(?<!\d)3\.716(?!\d)"), "3.716 (nhầm với 3.176?)"),
    (re.compile(r"(?<!\d)14\.185(?!\d)"), "14.185 (nhầm với 14.815?)"),
    (re.compile(r"(?<!\d)21\.615(?!\d)"), "21.615 (nhầm với 21.165?)"),
    (re.compile(r"(?<!\d)0,8742(?!\d)"), "0,8742 (lệch với 0,8714/0,8741?)"),
    (re.compile(r"(?<!\d)0,8549(?!\d)"), "0,8549 (nhầm với 0,8599?)"),
    (re.compile(r"(?<!\d)0,9204(?!\d)"), "0,9204 (nhầm với 0,9024?)"),
    (re.compile(r"(?<!\d)3174(?!\d)"), "3174 (thiếu dấu chấm tách nghìn 3.174)"),
    (re.compile(r"(?<!\d)3176(?!\d)"), "3176 (thiếu dấu chấm tách nghìn 3.176)"),
    (re.compile(r"(?<!\d)14815(?!\d)"), "14815 (thiếu dấu chấm tách nghìn 14.815)"),
    (re.compile(r"(?<!\d)21165(?!\d)"), "21165 (thiếu dấu chấm tách nghìn 21.165)"),
]

TEST_ONLY_METRICS_RE = re.compile(
    r"(?<!\d)(?:0[.,]8714|0[.,]8579|0[.,]8840|86[.,]56%|−0[.,]0310|-0[.,]0310|71[.,]19%|427|0[.,]9214|0[.,]8152|0[.,]8751|0[.,]8741)(?!\d)"
)


class Finding(NamedTuple):
    severity: str
    file: str
    line: int
    rule: str
    excerpt: str


def strip_technical_notes(text: str) -> str:
    """Bỏ phần `## Ghi chú kỹ thuật` đến hết tệp."""
    out_lines: list[str] = []
    for line in text.splitlines():
        if re.match(r"^##\s+Ghi chú kỹ thuật\b", line.strip(), re.IGNORECASE):
            break
        out_lines.append(line)
    return "\n".join(out_lines)


def _strip_ref_section(text: str) -> str:
    """Bỏ mục `## Tài liệu tham khảo phát sinh trong chương` (chỉ phần liệt kê ở cuối chương)."""
    out_lines: list[str] = []
    in_refs = False
    for line in text.splitlines():
        if re.match(r"^##\s+Tài liệu tham khảo phát sinh trong chương\b", line.strip()):
            in_refs = True
            continue
        if in_refs and re.match(r"^#{1,2}\s+", line.strip()):
            in_refs = False
        if not in_refs:
            out_lines.append(line)
    return "\n".join(out_lines)


def _mask_inline_code_and_urls(line: str) -> str:
    """Thay nội dung trong backtick, URL, DOI và số phiên bản bằng khoảng trắng giữ độ dài."""
    masked = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)
    masked = re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), masked)
    masked = re.sub(r"\bdoi:\s*\S+", lambda m: " " * len(m.group(0)), masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bv?\d+\.\d+\.\d+(?:\.\d+)?\b", lambda m: " " * len(m.group(0)), masked)
    masked = re.sub(r"\b\d+\.\d+e\d+\b", lambda m: " " * len(m.group(0)), masked)
    return masked


def load_chapters(report_dir: Path | None = None) -> dict[str, str]:
    """Đọc các tệp chương (01–06) và phụ lục (08), đã bỏ Ghi chú kỹ thuật."""
    base = report_dir or REPORT_DIR
    chapters: dict[str, str] = {}
    for name in BODY_AND_APPENDIX_FILES:
        path = base / name
        if path.exists():
            chapters[name] = strip_technical_notes(path.read_text(encoding="utf-8"))
    return chapters


def check_banned_phrases(text: str, file: str = "<input>") -> list[Finding]:
    """Kiểm quy tắc D4, từ ngữ AI slop và nhồi nhét liên từ nối."""
    findings: list[Finding] = []
    lines = text.splitlines()

    # 1. Quy tắc D4: tìm từ cấm trong cửa sổ 200 ký tự quanh "val"/"validation" và "test"
    full = "\n".join(lines)
    d4_words = re.compile(r"\b(nguyên nhân|do đó|vì vậy)\b", re.IGNORECASE)
    val_test_re = re.compile(r"\b(val|validation|test)\b", re.IGNORECASE)
    seen_d4: set[tuple[int, str]] = set()
    for m in d4_words.finditer(full):
        start, end = m.start(), m.end()
        line_no = full[:start].count("\n") + 1
        line_text = lines[line_no - 1]
        if D4_NEGATION_RE.search(line_text):
            continue
        win = full[max(0, start - 200) : min(len(full), end + 200)]
        has_val = bool(re.search(r"\b(?:val|validation)\b", win, re.IGNORECASE))
        has_test = bool(re.search(r"\btest\b", win, re.IGNORECASE))
        if has_val and has_test and val_test_re.search(win):
            key = (line_no, m.group(1).lower())
            if key not in seen_d4:
                seen_d4.add(key)
                findings.append(
                    Finding("critical", file, line_no, "D4-causal", line_text.strip()[:140])
                )

    # 2. Cụm từ AI slop
    for idx, line in enumerate(lines, start=1):
        low = line.lower()
        for phrase in SLOP_PHRASES:
            if phrase in low:
                findings.append(
                    Finding("minor", file, idx, "ai-slop", f"'{phrase}': {line.strip()[:110]}")
                )

    # 3. Nhồi nhét liên từ nối (>= 3 câu liên tiếp ở đầu câu)
    in_code = False
    para_lines: list[tuple[int, str]] = []

    def _flush_para() -> None:
        if not para_lines:
            return
        joined = " ".join(p for _, p in para_lines)
        start_line = para_lines[0][0]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if s.strip()]
        streak = 0
        for sent in sentences:
            low_s = sent.lower().lstrip("(\"“' ")
            if any(low_s.startswith(c + " ") or low_s.startswith(c + ",") for c in CONNECTOR_STARTERS):
                streak += 1
                if streak >= 3:
                    findings.append(
                        Finding(
                            "minor",
                            file,
                            start_line,
                            "connector-stacking",
                            f"{streak} câu liên tiếp mở bằng liên từ nối: {sent[:90]}",
                        )
                    )
            else:
                streak = 0
        para_lines.clear()

    for idx, line in enumerate(lines, start=1):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            _flush_para()
            continue
        if in_code or not s or s.startswith(("#", "|", ">", "![", "**Bảng", "**Hình", "---")):
            _flush_para()
            continue
        para_lines.append((idx, s))
    _flush_para()

    return findings


def check_fixed_numbers(chapters: dict[str, str]) -> list[Finding]:
    """Kiểm số cố định sai chữ số, dấu chấm thập phân ở thân bài, và rò rỉ tập test vào Ch1–Ch4."""
    findings: list[Finding] = []
    for fname, content in chapters.items():
        in_code = False
        is_ch1_4 = fname.startswith(("01_", "02_", "03_", "04_"))
        is_appendix = fname.startswith("08_")
        for idx, line in enumerate(content.splitlines(), start=1):
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            masked = _mask_inline_code_and_urls(line)

            # Lỗi gõ sai chữ số hoặc thiếu dấu tách nghìn
            for pat, desc in FIXED_NUMBER_TYPOS:
                if pat.search(masked):
                    findings.append(
                        Finding("critical", fname, idx, "fixed-number", f"{desc} | {s[:110]}")
                    )

            # Dấu chấm thập phân kiểu tiếng Anh trong thân bài (không xét tên mục X.Y / Bảng X.Y / Hình X.Y / Phụ lục)
            if not is_appendix:
                cleaned = re.sub(
                    r"(?:Bảng|Hình|Mục|Chương|Phụ lục)\s+[A-Z0-9]+(?:\.\d+)+(?:\s*(?:và|đến|–|-|,|;)\s*\d+(?:\.\d+)+)*",
                    " ",
                    masked,
                )
                cleaned = re.sub(r"^\s*#{1,4}\s+\d+(?:\.\d+)+\.?", " ", cleaned)
                cleaned = re.sub(
                    r"\bmục\s+\d+(?:\.\d+)+(?:\s*(?:và|đến|–|-|,|;)\s*\d+(?:\.\d+)+)*",
                    " ",
                    cleaned,
                    flags=re.IGNORECASE,
                )
                cleaned = re.sub(
                    r"\(\s*\d+(?:\.\d+)+(?:[,;\s]+\d+(?:\.\d+)+)*[,;\s]*\)",
                    " ",
                    cleaned,
                )  # (2.1) hoặc (1.2, 1.3)
                cleaned = re.sub(r"\b\d+\.\d+\.\d+\b", " ", cleaned)  # 2.6.1
                for m in re.finditer(r"(?<![\d.])\d+\.\d{1,2}(?!\d)|(?<![\d.])\d+\.\d{4,}(?!\d)", cleaned):
                    # Bỏ qua số hàng nghìn kiểu 3.174 (chính xác 3 chữ số sau dấu chấm đã tách riêng)
                    findings.append(
                        Finding("minor", fname, idx, "decimal-dot", f"'{m.group(0)}' | {s[:110]}")
                    )

            # Rò rỉ số liệu đánh giá tập test vào Chương 1–4
            if is_ch1_4:
                if TEST_ONLY_METRICS_RE.search(masked):
                    findings.append(
                        Finding("critical", fname, idx, "H2-test-leak", f"Số liệu test ở {fname}: {s[:110]}")
                    )
                if fname.startswith(("03_", "04_")) and re.search(r"(?<!\d)3\.176(?!\d)", masked):
                    findings.append(
                        Finding("critical", fname, idx, "H2-test-leak", f"Cỡ mẫu test 3.176 ở {fname}: {s[:110]}")
                    )
    return findings


def check_captions_and_refs(chapters: dict[str, str], check_totals: bool = True) -> list[Finding]:
    """Kiểm đánh số liên tục Bảng/Hình, dẫn chiếu trong văn bản, tổng số 32 bảng và 4 hình."""
    findings: list[Finding] = []
    cap_re = re.compile(r"^\*\*(Bảng|Hình)\s+([A-Z0-9]+)\.(\d+):")
    total_tables = 0
    total_figures = 0

    for fname, content in chapters.items():
        lines = content.splitlines()
        seen_by_kind_group: dict[tuple[str, str], list[tuple[int, int, str]]] = {}

        for idx, line in enumerate(lines, start=1):
            m = cap_re.match(line.strip())
            if not m:
                continue
            kind, grp, num_s = m.group(1), m.group(2), m.group(3)
            num = int(num_s)
            label = f"{kind} {grp}.{num}"
            seen_by_kind_group.setdefault((kind, grp), []).append((num, idx, label))
            if kind == "Bảng":
                total_tables += 1
            else:
                total_figures += 1

            # Kiểm dẫn chiếu trong các dòng còn lại của cùng tệp
            body_wo_caption = "\n".join(l for j, l in enumerate(lines, start=1) if j != idx)
            if label not in body_wo_caption:
                findings.append(
                    Finding("major", fname, idx, "caption-unreferenced", f"Chưa dẫn chiếu {label} trong văn bản")
                )

        for (kind, grp), items in seen_by_kind_group.items():
            nums = [n for n, _, _ in items]
            expected = list(range(1, len(nums) + 1))
            if nums != expected:
                findings.append(
                    Finding(
                        "major",
                        fname,
                        items[0][1],
                        "caption-sequence",
                        f"{kind} nhóm {grp} đánh số {nums}, kỳ vọng {expected}",
                    )
                )

    if check_totals:
        if total_tables != 32:
            findings.append(
                Finding("major", "<all>", 0, "caption-total-tables", f"Đếm được {total_tables} bảng, kỳ vọng 32")
            )
        if total_figures != 4:
            findings.append(
                Finding("major", "<all>", 0, "caption-total-figures", f"Đếm được {total_figures} hình, kỳ vọng 4")
            )
    return findings


def _expand_citation_token(token: str) -> list[int]:
    """Giải `[1, 2]` hoặc `[4]-[7]` thành danh sách số nguyên."""
    nums: list[int] = []
    for part in token.split(","):
        part = part.strip()
        if re.fullmatch(r"\d+", part):
            nums.append(int(part))
    return nums


def check_citations(chapters: dict[str, str], refs_text: str) -> list[Finding]:
    """Kiểm thứ tự xuất hiện tăng dần của `[n]`, khớp với 07_tai_lieu_tham_khao.md."""
    findings: list[Finding] = []
    defined_refs: set[int] = set()
    for line in refs_text.splitlines():
        m = re.match(r"^\[(\d+)\]\s+", line.strip())
        if m:
            defined_refs.add(int(m.group(1)))

    first_seen_order: list[int] = []
    seen_set: set[int] = set()
    max_seen = 0
    order_broken = False

    ordered_files = [f for f in BODY_AND_APPENDIX_FILES if f in chapters] + [
        f for f in sorted(chapters) if f not in BODY_AND_APPENDIX_FILES
    ]
    for fname in ordered_files:
        body = _strip_ref_section(chapters[fname])
        in_code = False
        for idx, line in enumerate(body.splitlines(), start=1):
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            masked = _mask_inline_code_and_urls(line)
            for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\](?!\()", masked):
                # Bỏ qua mẫu số kiểu mảng ở chú thích hoặc [n] trong dấu nháy trích dẫn mô tả
                for n in _expand_citation_token(m.group(1)):
                    if n not in defined_refs:
                        findings.append(
                            Finding("major", fname, idx, "citation-missing-ref", f"[{n}] không có trong tài liệu tham khảo")
                        )
                    if n not in seen_set:
                        seen_set.add(n)
                        first_seen_order.append(n)
                        if n != max_seen + 1 and not order_broken:
                            order_broken = True
                            findings.append(
                                Finding(
                                    "major",
                                    fname,
                                    idx,
                                    "citation-order",
                                    f"[{n}] xuất hiện lần đầu khi mới tới [{max_seen}]",
                                )
                            )
                        if n > max_seen:
                            max_seen = n

    for ref_id in sorted(defined_refs - seen_set):
        findings.append(
            Finding("major", "07_tai_lieu_tham_khao.md", 0, "citation-unused-ref", f"[{ref_id}] không được trích trong thân bài")
        )
    return findings


def check_section_counts(chapters: dict[str, str]) -> list[Finding]:
    """Đếm tiểu mục lá (37 tiểu mục toàn 6 chương) so với report_standards.md mục 3.2."""
    findings: list[Finding] = []
    for fname, expected in EXPECTED_SUBSECTIONS.items():
        if fname not in chapters:
            continue
        body = _strip_ref_section(chapters[fname])
        h2_nums: list[str] = []
        h3_nums: list[str] = []
        for line in body.splitlines():
            m2 = re.match(r"^##\s+(\d+\.\d+)\.?\s+", line.strip())
            if m2:
                h2_nums.append(m2.group(1))
            m3 = re.match(r"^###\s+(\d+\.\d+\.\d+)\.?\s+", line.strip())
            if m3:
                h3_nums.append(m3.group(1))
        parents = {".".join(h.split(".")[:2]) for h in h3_nums}
        leaf_count = len([h for h in h2_nums if h not in parents]) + len(h3_nums)
        if leaf_count != expected:
            findings.append(
                Finding(
                    "major",
                    fname,
                    1,
                    "section-count",
                    f"Đếm được {leaf_count} tiểu mục, kỳ vọng {expected}",
                )
            )
    return findings


def check_h7_and_paths(chapters: dict[str, str]) -> list[Finding]:
    """Kiểm cổng H7 (cấm học sâu) và đường dẫn tệp trong thân bài Chương 1–6."""
    findings: list[Finding] = []
    dl_re = re.compile(r"\b(torch|torchvision|tensorflow|keras|timm|pytorch)\b", re.IGNORECASE)
    allow_dl_re = re.compile(r"(cấm|chặn|không\s+dùng|không\s+sử\s+dụng|gỡ|bỏ|ngoài\s+phạm\s+vi)", re.IGNORECASE)
    path_re = re.compile(
        r"(?:results/|src/|splits/|notebooks/|demo/|scripts/|docs/|outputs/|\b[a-zA-Z0-9_]+\.(?:py|csv|json|yaml|ipynb|joblib)\b)"
    )

    for fname, content in chapters.items():
        in_code = False
        is_appendix = fname.startswith("08_")
        for idx, line in enumerate(content.splitlines(), start=1):
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if dl_re.search(line) and not allow_dl_re.search(line):
                findings.append(
                    Finding("critical", fname, idx, "H7", f"Nhắc framework học sâu: {s[:110]}")
                )
            if not is_appendix and not s.startswith("![") and path_re.search(line):
                findings.append(
                    Finding("minor", fname, idx, "in-text-path", s[:120])
                )
    return findings


def run_all_checks(report_dir: Path | None = None) -> list[Finding]:
    """Chạy toàn bộ kiểm tra trên thư mục báo cáo."""
    base = report_dir or REPORT_DIR
    chapters = load_chapters(base)
    refs_path = base / "07_tai_lieu_tham_khao.md"
    refs_text = strip_technical_notes(refs_path.read_text(encoding="utf-8")) if refs_path.exists() else ""

    findings: list[Finding] = []
    for fname, text in chapters.items():
        if fname.startswith("08_"):
            continue
        findings.extend(check_banned_phrases(text, file=fname))
    # Kiểm tra cả 09_tom_tat_abstract.md phần tiếng Việt (mục 1) cho D4 & slop
    ab_path = base / "09_tom_tat_abstract.md"
    if ab_path.exists():
        ab_text = strip_technical_notes(ab_path.read_text(encoding="utf-8"))
        vi_part = ab_text.split("## 2. Abstract")[0]
        findings.extend(check_banned_phrases(vi_part, file="09_tom_tat_abstract.md"))

    findings.extend(check_fixed_numbers(chapters))
    findings.extend(check_captions_and_refs(chapters, check_totals=True))
    findings.extend(check_citations(chapters, refs_text))
    findings.extend(check_section_counts(chapters))
    findings.extend(check_h7_and_paths(chapters))
    return findings


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        fn = getattr(stream, "reconfigure", None)
        if fn:
            fn(encoding="utf-8", errors="replace")

    findings = run_all_checks()
    counts = {"critical": 0, "major": 0, "minor": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    print(f"Summary: critical={counts['critical']}, major={counts['major']}, minor={counts['minor']}, total={len(findings)}")
    for f in findings:
        print(f"[{f.severity.upper()}] {f.file}:{f.line} ({f.rule}) — {f.excerpt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
