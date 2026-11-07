"""Kernel Kaggle mỏng thực thi tác vụ S4-07 (kiểm tra ảnh che phổi) và RQ3 (S5-01, S5-02).

Thiết lập môi trường mã nguồn phẳng từ dataset code trên Kaggle, điều hướng import và
gọi hàm chạy chính kaggle_main từ src.rq3_runner.
"""

from pathlib import Path
import shutil
import sys
from typing import Tuple

SRC_FILES: Tuple[str, ...] = (
    "dataset.py",
    "metrics.py",
    "bootstrap.py",
    "features_hist_glcm_lbp.py",
    "features_hog_ghep.py",
    "rq1_runner.py",
    "rq2_runner.py",
    "rq3_runner.py",
)
INPUT_ROOT: Path = Path("/kaggle/input")
WORKING_ROOT: Path = Path("/kaggle/working")


def find_package_dir(input_root: Path) -> Path:
    """Tìm thư mục chứa gói mã nguồn dựa trên tệp đánh dấu COMMIT."""
    patterns = ["COMMIT", "*/COMMIT", "*/*/COMMIT", "*/*/*/COMMIT"]
    for pat in patterns:
        matches = sorted(input_root.glob(pat))
        if matches:
            return matches[0].parent
    raise FileNotFoundError(f"Khong tim thay goi ma nguon trong {input_root}")


def main() -> None:
    """Điểm nhập thực thi kernel Kaggle cho S4-07 & RQ3."""
    package_dir = find_package_dir(INPUT_ROOT)
    code_root = WORKING_ROOT / "code"
    src_dir = code_root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    for file_name in SRC_FILES:
        shutil.copyfile(package_dir / file_name, src_dir / file_name)

    sys.path.insert(0, str(code_root))
    from src.rq3_runner import kaggle_main

    kaggle_main(input_root=INPUT_ROOT, working_dir=WORKING_ROOT)


if __name__ == "__main__":
    main()
