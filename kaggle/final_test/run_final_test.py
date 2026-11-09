"""Điểm vào chạy kernel Kaggle cho chế độ final test duy nhất (S5-04, S5-05).

Chế độ 'final': Thực hiện toàn bộ các cổng G1 -> G2 -> G3 -> G4 -> fit (1 lần) -> G5 -> G6 -> đọc test -> báo cáo.
Chỉ chạy đúng MỘT lần sau khi có sự chấp thuận bằng văn bản của người dùng.
"""

from __future__ import annotations

import os
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
    "final_test_runner.py",
)
INPUT_ROOT: Path = Path(os.environ.get("KAGGLE_INPUT_PATH", "/kaggle/input"))
WORKING_ROOT: Path = Path(os.environ.get("KAGGLE_WORKING_PATH", "/kaggle/working"))


def find_package_dir(input_root: Path) -> Path:
    """Tìm thư mục chứa gói mã nguồn dựa trên tệp đánh dấu COMMIT."""
    patterns = ["COMMIT", "*/COMMIT", "*/*/COMMIT", "*/*/*/COMMIT", "*/*/*/*/COMMIT"]
    for pat in patterns:
        matches = sorted(input_root.glob(pat))
        if matches:
            return matches[0].parent
    raise FileNotFoundError(f"Khong tim thay goi ma nguon trong {input_root}")


def main() -> None:
    package_dir = find_package_dir(INPUT_ROOT)
    code_root = WORKING_ROOT / "code"
    src_dir = code_root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    for file_name in SRC_FILES:
        src_path = package_dir / file_name
        if src_path.is_file():
            shutil.copyfile(src_path, src_dir / file_name)
        elif (package_dir / "src" / file_name).is_file():
            shutil.copyfile(package_dir / "src" / file_name, src_dir / file_name)

    sys.path.insert(0, str(code_root))
    from src.final_test_runner import kaggle_main

    kaggle_main(
        input_root=INPUT_ROOT,
        working_dir=WORKING_ROOT,
        expected_mode="final",
    )


if __name__ == "__main__":
    main()
