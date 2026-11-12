"""Sinh tep report/00c_muc_luc_va_danh_muc.md tu 6 chuong + tai lieu tham khao + phu luc.

Chay: python scripts/report_frontmatter.py
Muc luc, danh muc bang va danh muc hinh doc truc tiep tu cac tep bao cao, nen
khong lech khi chuong them tieu de hoac bang moi. So trang de trong; khi chuyen
sang Word, dung Reference > Table of Contents de Word tu danh so trang.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "report"

FRONT = [
    ("i", "Trang bìa chính"),
    ("ii", "Trang bìa phụ"),
    ("iii", "Lời cảm ơn"),
    ("iv", "Lời cam đoan"),
    ("v", "Tóm tắt tiếng Việt và Abstract"),
    ("vi", "Danh mục ký hiệu và chữ viết tắt"),
    ("vii", "Mục lục"),
    ("viii", "Danh mục bảng biểu"),
    ("ix", "Danh mục hình ảnh"),
]


def reconfigure() -> None:
    for stream in (sys.stdout, sys.stderr):
        fn = getattr(stream, "reconfigure", None)
        if fn:
            fn(encoding="utf-8", errors="replace")


def chapter_structure(name: str) -> list[tuple[int, str]]:
    text = (REPORT / name).read_text(encoding="utf-8")
    out: list[tuple[int, str]] = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,3}) (.+?)\s*$", line)
        if not m:
            continue
        level, title = len(m.group(1)), m.group(2).strip()
        if title.startswith("Ghi chú kỹ thuật"):
            continue
        out.append((level, title))
    return out


def captions(name: str) -> list[tuple[str, str, str]]:
    text = (REPORT / name).read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        m = re.match(r"\*\*((?:Bảng|Hình) [A-Z0-9.]+): (.+?)\*\*", line.strip())
        if m:
            out.append((m.group(1), m.group(2), name))
    return out


def build() -> tuple[list[str], int, int]:
    """Tra ve (dong tep, so bang, so hinh) — dung cho ca main() va test."""
    chapters = ["01_gioi_thieu.md", "02_du_lieu_va_phuong_phap.md", "03_ket_qua_rq1_rq2.md",
                "04_hoc_loi_tat_rq3.md", "05_ket_qua_test_va_trien_khai.md",
                "06_thao_luan_gioi_han_huong_phat_trien.md"]
    back = ["07_tai_lieu_tham_khao.md", "08_phu_luc_a_c.md"]

    lines: list[str] = []
    lines.append("# Mục lục và danh mục")
    lines.append("")
    lines.append("Tệp này gộm ba mục đầu cuối của phần mở đầu quyển: mục lục, danh mục bảng biểu và")
    lines.append("danh mục hình ảnh. Nội dung sinh tự động từ sáu chương, tài liệu tham khảo và phụ lục")
    lines.append("bằng `scripts/report_frontmatter.py`, nên không lệch khi chương thêm tiểu mục hoặc bảng mới.")
    lines.append("Số trang để trống; khi dựng bản Word, dùng *References → Table of Contents* của Word")
    lines.append("để sinh số trang thật, rồi dán hai danh mục dưới dạng bảng hai cột (đề mục – trang).")
    lines.append("")
    lines.append("## 1. Mục lục")
    lines.append("")
    lines.append("**Phần mở đầu (đánh số La Mã)**")
    lines.append("")
    for num, title in FRONT:
        lines.append(f"- {num}. {title}")
    lines.append("")
    lines.append("**Phần nội dung chính (đánh số Ả Rập)**")
    lines.append("")
    for ch in chapters:
        for level, title in chapter_structure(ch):
            prefix = "  " * (level - 1)
            lines.append(f"{prefix}- {title}")
    lines.append("")
    lines.append("**Phần cuối quyển (đánh số tiếp)**")
    lines.append("")
    for f in back:
        for level, title in chapter_structure(f):
            prefix = "  " * (level - 1)
            lines.append(f"{prefix}- {title}")
    lines.append("")

    lines.append("")
    lines.append("## 2. Danh mục bảng biểu")
    lines.append("")
    def sort_key(label: str) -> tuple[str, list[int]]:
        parts = label.split()[1].split(".")
        return (parts[0], [int(p) if p.isdigit() else 0 for p in parts[1:]])

    n_tab = 0
    all_tab: list[tuple[str, str, str]] = []
    for f in chapters + back:
        all_tab.extend((label, title, f) for label, title, _ in captions(f) if label.startswith("Bảng"))
    all_tab.sort(key=lambda r: sort_key(r[0]))
    for label, title, _ in all_tab:
        n_tab += 1
        lines.append(f"- **{label}:** {title}")
    lines.append(f"- Tổng cộng: {n_tab} bảng.")

    lines.append("")
    lines.append("## 3. Danh mục hình ảnh")
    lines.append("")
    src_map = {
        "Hình 2.1": "`results/eda/brightness_distribution.png`",
        "Hình 3.1": "`report/figures/03_ma_tran_nham_lon_svm_val.png`",
        "Hình 4.1": "`report/figures/04_macro_f1_kich_ban_rq3.png`",
        "Hình 5.1": "`report/figures/05_ma_tran_nham_lon_test.png`",
    }
    n_fig = 0
    for f in chapters:
        for label, title, _ in captions(f):
            if label.startswith("Hình"):
                n_fig += 1
                lines.append(f"- **{label}:** {title} — tệp nguồn {src_map.get(label, '')}")
    lines.append(f"- Tổng cộng: {n_fig} hình.")

    lines.append("")
    lines.append("## Ghi chú kỹ thuật")
    lines.append("")
    lines.append("- Nguồn: tiêu đề đọc từ sáu tệp `report/0*.md` (cấp `#`, `##`, `###`), bỏ hạng mục ")
    lines.append("  \"Ghi chú kỹ thuật\" không thuộc nội dung báo cáo; bảng và hình đọc từ dòng chú thích in đậm.")
    lines.append("- Sinh lại bằng `python scripts/report_frontmatter.py` (ghi đè tệp này).")
    lines.append("- Hình 2.1 nằm ở `results/eda/` do notebook EDA sinh, không nằm trong `report/figures/`;")
    lines.append("  khi chuyển Word, chèn ảnh từ đúng đường dẫn đó rồi đặt chú thích Hình 2.1 bên dưới.")
    lines.append("")

    return lines, n_tab, n_fig


def main() -> int:
    reconfigure()
    lines, n_tab, n_fig = build()
    (REPORT / "00c_muc_luc_va_danh_muc.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Da ghi report/00c_muc_luc_va_danh_muc.md ({n_tab} bang, {n_fig} hinh)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
