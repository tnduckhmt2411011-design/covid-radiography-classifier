"""Điểm vào chạy kernel Kaggle cho chế độ final test duy nhất (S5-04, S5-05).

Chế độ 'final': Thực hiện toàn bộ các cổng G1 -> G2 -> G3 -> G4 -> fit (1 lần) -> G5 -> G6 -> đọc test -> báo cáo.
Chỉ chạy đúng MỘT lần sau khi có sự chấp thuận bằng văn bản của người dùng.
"""

from __future__ import annotations

import os
from pathlib import Path

# Đảm bảo đường dẫn import cho src
input_root = Path(os.environ.get("KAGGLE_INPUT_PATH", "/kaggle/input"))
working_dir = Path(os.environ.get("KAGGLE_WORKING_PATH", "/kaggle/working"))

from src.final_test_runner import kaggle_main  # noqa: E402

if __name__ == "__main__":
    kaggle_main(
        input_root=input_root,
        working_dir=working_dir,
        expected_mode="final",
    )
