"""Điểm vào chạy kernel Kaggle cho chế độ dry-run (S5-04, S5-05).

Chế độ 'dry': Chạy đầy đủ train (14.815) -> val (3.174), kiểm tra G5 thật.
Tuyệt đối KHÔNG đọc tập test và KHÔNG ghi UNLOCK_RECORD.json.
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
        expected_mode="dry",
    )
