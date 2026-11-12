"""Sinh noi dung bang cho Phu luc B (danh sach bai kiem thu) cua bao cao.

Chay: python scripts/report_appendix_b.py

So phep kiem thu cua tung module dem theo dau ra `pytest --collect-only -q`
(cung cach do voi so ghi trong Chuong 5: mot phep kiem thu la mot node pytest,
nen test tham so hoa duoc dem theo tung bo tham so). Danh sach module lay tu
`git ls-files tests/test_*.py` (nhat quan voi Bang B.1, cung dem theo git):
tep test chua track trong thu muc lam viec khong thuoc kho nen khong dem.
Tong cong va so module duoc doc tai thoi diem chay; bao cao ghi so nay o
Chuong 5, Phu luc B va report/README.md.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


DESCRIPTIONS = {
    "src/": "Mã nguồn: nạp dữ liệu, trích đặc trưng, bộ chạy RQ1–RQ3, metrics, bootstrap, suy luận, đo độ trễ, kiểm artifact",
    "notebooks/": "Notebook theo trình tự: kiểm môi trường, EDA, trùng lặp và chia tập, RQ1, RQ2, RQ3, phân tích lỗi, đánh giá test một lần, suy luận",
    "demo/": "Ứng dụng Streamlit, kiểm tra tải/kiểm băm artifact, cổng tương đương, yêu cầu thư viện",
    "tests/": "Bộ kiểm thử tự động pytest (danh sách ở Bảng B.2)",
    "scripts/": "Sinh hình cho báo cáo, bảng Phụ lục B, mục lục và danh mục, khung viền bìa, phép đo tập validation có ảnh gần trùng",
    "results/": "Tệp kết quả và biên bản của các bước S1–S6",
    "kaggle/": "Mã và biên bản chạy thực nghiệm trên kernel Kaggle",
    "splits/": "Manifest, tệp phân chia và báo cáo kiểm tra sau chia",
    "outputs/": "Tệp kiểm tra trùng và gần trùng của notebook 02, được track làm nguồn cho ghi chú Chương 2",
    "docs/": "Quy chuẩn báo cáo, cẩn nang viết, phân công thành viên, kế hoạch, nguồn dữ liệu, nhật ký công việc",
    "report/": "Sáu chương, mở đầu quyển, tài liệu tham khảo, phụ lục, tóm tắt, hình vẽ, bản đồ nguồn",
    "slides/": "Chỗ để slide thuyết trình, mới có `.gitkeep` giữ chỗ",
}
ROOT_FILES = ["README.md", "requirements.txt", "pytest.ini", ".gitignore", ".gitattributes"]


def count_structure() -> dict[str, int]:
    r = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True)
    counts: dict[str, int] = {}
    for line in r.stdout.splitlines():
        top = line.split("/")[0] if "/" in line else "<root>"
        counts[top] = counts.get(top, 0) + 1
    return counts


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    tests_dir = REPO_ROOT / "tests"
    tracked = subprocess.run(
        ["git", "ls-files", "tests/test_*.py"], cwd=REPO_ROOT,
        capture_output=True, text=True,
    ).stdout.split()
    modules = sorted(tests_dir / Path(p).name for p in tracked)
    if not modules:
        print("Khong tim thay module test")
        return 1

    r = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *tracked],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    counts: dict[str, int] = {}
    collected = None
    for line in r.stdout.splitlines():
        stripped = line.strip()
        m = re.match(r"(\d+) tests? collected", stripped)
        if m:
            collected = int(m.group(1))
            continue
        if stripped.startswith("tests/") and "::" in stripped:
            key = stripped.split("::")[0]
            counts[key] = counts.get(key, 0) + 1
    for name in {p.name for p in modules}:
        counts.setdefault(f"tests/{name}", 0)

    struct = count_structure()
    others = struct.get("configs", 0) + struct.get(".github", 0) + struct.get(".streamlit", 0)

    # ----- Bảng B.1 -----
    print("| Thư mục / tệp | Số tệp | Nội dung |")
    print("| :--- | ---: | :--- |")
    b1_total = 0
    for d in ["src", "notebooks", "demo", "tests", "scripts", "results", "kaggle", "splits", "outputs", "docs", "report", "slides"]:
        n = struct.get(d, 0)
        b1_total += n
        print(f"| `{d}/` | {n} | {DESCRIPTIONS.get(d + '/', '')} |")
    b1_total += others
    print(f"| `configs/`, `.github/`, `.streamlit/` | {others} | Cấu hình cơ sở, mẫu pull request, cấu hình Streamlit |")
    b1_total += struct.get("<root>", 0)
    root_label = ", ".join(f"`{f}`" for f in ROOT_FILES)
    print(f"| Tệp gốc ({root_label}) | {struct.get('<root>', 0)} | Điều khiển dự án và môi trường |")
    print(f"| **Tổng cộng** | **{b1_total}** |")
    print()
    # ----- Bảng B.2 -----
    print("| Module | Số phép kiểm thử |")
    print("| :--- | ---: |")
    total = 0
    for m in modules:
        key = f"tests/{m.name}"
        n = counts.get(key, 0)
        total += n
        print(f"| `{m.name}` | {n} |")
    print(f"| **Tổng cộng** | **{total}** |")
    print()
    print(f"# so module: {len(modules)}")
    print(f"# tong theo collect: {total}")
    print(f"# pytest collect: {collected}")
    if collected is not None and total != collected:
        print("# CANH BAO: tong dem khong khop dong 'tests collected'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
