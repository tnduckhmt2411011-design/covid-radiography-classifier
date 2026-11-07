"""Kernel Kaggle mỏng thực thi tác vụ RQ2 so sánh 6 bộ phân loại học máy cổ điển.

Phụ trách S4-03: Thiết lập môi trường mã nguồn phẳng từ dataset code trên Kaggle,
điều hướng import và gọi hàm chạy chính kaggle_main từ src.rq2_runner.
"""

from pathlib import Path
import shutil
import sys
from typing import Tuple

SRC_FILES: Tuple[str, ...] = (
    "dataset.py",
    "metrics.py",
    "features_hist_glcm_lbp.py",
    "features_hog_ghep.py",
    "rq2_runner.py",
)
SPLIT_FILES: Tuple[str, ...] = (
    "split_v1.csv",
    "split_v1.sha256",
)
INPUT_ROOT: Path = Path("/kaggle/input")
WORKING_ROOT: Path = Path("/kaggle/working")


def find_package_dir(input_root: Path) -> Path:
    """Tìm thư mục chứa gói mã nguồn dựa trên tệp đánh dấu COMMIT.

    Args:
        input_root: Thư mục gốc đầu vào trên Kaggle.

    Returns:
        Path tới thư mục chứa gói mã nguồn.

    Raises:
        FileNotFoundError: Nếu không tìm thấy tệp COMMIT.
    """
    patterns = ["*/COMMIT", "*/*/COMMIT", "*/*/*/COMMIT"]
    for pat in patterns:
        matches = sorted(input_root.glob(pat))
        if matches:
            return matches[0].parent
    raise FileNotFoundError(f"Khong tim thay goi ma nguon trong {input_root}")


def main() -> None:
    """Điểm nhập thực thi kernel Kaggle."""
    package_dir = find_package_dir(INPUT_ROOT)
    code_root = WORKING_ROOT / "code"
    src_dir = code_root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    for file_name in SRC_FILES:
        shutil.copyfile(package_dir / file_name, src_dir / file_name)

    sys.path.insert(0, str(code_root))
    from src.rq2_runner import kaggle_main

    kaggle_main(INPUT_ROOT, WORKING_ROOT, package_dir)


if __name__ == "__main__":
    main()
