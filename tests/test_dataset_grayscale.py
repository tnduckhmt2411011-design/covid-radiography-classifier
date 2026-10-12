"""Kiểm thử phòng ngừa cho cơ chế tiền xử lý ảnh xám của CXRDataset."""

import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import torch
import pytest

from src.dataset import CXRDataset


def test_rgb_image_forced_grayscale_conversion():
    """Kiểm tra ảnh màu RGB giả lập được ép về đơn sắc trước khi nhân 3 kênh."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        img_file = tmp_path / "test_color_image.png"

        # Tạo ảnh màu nhân tạo có sự khác biệt rõ giữa R, G, B
        color_arr = np.zeros((100, 100, 3), dtype=np.uint8)
        color_arr[:, :, 0] = 255  # Kênh R đỏ
        color_arr[:, :, 1] = 50   # Kênh G
        color_arr[:, :, 2] = 10   # Kênh B
        Image.fromarray(color_arr).save(img_file)

        # Tạo DataFrame giả lập
        split_df = pd.DataFrame([
            {
                "image_id": "test_color_image.png",
                "label": "Viral Pneumonia",
                "rel_image_path": "test_color_image.png",
                "split": "train",
            }
        ])

        # Không dùng data augmentation ngẫu nhiên để kiểm tra giá trị pixel thô
        dataset = CXRDataset(
            split_df_or_path=split_df,
            split="train",
            data_root=tmp_path,
            transform=lambda img: np.array(img),
            allow_test=False,
        )

        tensor_out, label_idx = dataset[0]
        # Sau khi qua convert("L").convert("RGB"), 3 kênh phải bằng nhau tuyệt đối
        assert tensor_out.shape == (100, 100, 3)
        R = tensor_out[:, :, 0]
        G = tensor_out[:, :, 1]
        B = tensor_out[:, :, 2]

        np.testing.assert_array_equal(R, G, err_msg="Kênh R và G phải giống nhau hoàn toàn sau khi khử màu")
        np.testing.assert_array_equal(G, B, err_msg="Kênh G và B phải giống nhau hoàn toàn sau khi khử màu")
