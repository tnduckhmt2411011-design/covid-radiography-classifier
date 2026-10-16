"""Kiểm thử phòng ngừa cho cơ chế tiền xử lý ảnh xám của CXRDataset."""

import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import pytest

from src.dataset import CXRDataset


def test_rgb_image_forced_grayscale_conversion():
    """Kiểm tra ảnh màu RGB giả lập được ép về mảng NumPy đơn sắc (L) không resize."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        img_file = tmp_path / "test_color_image.png"

        # Tạo ảnh màu nhân tạo có sự khác biệt rõ giữa R, G, B
        color_arr = np.zeros((100, 100, 3), dtype=np.uint8)
        color_arr[:, :, 0] = 255  # Kênh R đỏ
        color_arr[:, :, 1] = 50   # Kênh G
        color_arr[:, :, 2] = 10   # Kênh B
        orig_img = Image.fromarray(color_arr)
        orig_img.save(img_file)

        # Tạo DataFrame giả lập
        split_df = pd.DataFrame([
            {
                "image_id": "test_color_image.png",
                "label": "Viral Pneumonia",
                "rel_image_path": "test_color_image.png",
                "split": "train",
            }
        ])

        dataset = CXRDataset(
            split_df_or_path=split_df,
            split="train",
            data_root=tmp_path,
            allow_test=False,
        )

        img_out, label_idx = dataset[0]

        # 1. Đầu ra phải là mảng NumPy
        assert isinstance(img_out, np.ndarray), "Đầu ra phải là mảng NumPy"

        # 2. Không resize, giữ nguyên kích thước gốc (100, 100)
        assert img_out.shape == (100, 100), f"Kỳ vọng shape (100, 100), thực tế {img_out.shape}"

        # 3. Phải là mảng 2D đơn sắc (loại bỏ hoàn toàn chiều kênh màu)
        assert img_out.ndim == 2, f"Kỳ vọng ảnh đơn sắc 2D, thực tế ndim={img_out.ndim}"

        # 4. Giá trị pixel khớp chính xác với chuẩn chuyển đổi Grayscale 'L' của PIL
        expected_l = np.array(orig_img.convert("L"), dtype=np.uint8)
        np.testing.assert_array_equal(img_out, expected_l, err_msg="Giá trị pixel ảnh xám phải khớp chính xác")

        # 5. Nhãn đúng
        assert label_idx == 3, f"Nhãn Viral Pneumonia phải có index 3, thực tế {label_idx}"
