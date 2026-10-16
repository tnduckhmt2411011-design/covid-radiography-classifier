"""Module dataset.py

Trách nhiệm:
- Quản lý nạp dữ liệu từ file split_v1.csv (phụ trách: Nguyễn Đức).
- Định nghĩa lớp CXRDataset cho bài toán phân loại 4 nhóm ảnh X-quang ngực (Machine Learning cổ điển).
- Đọc ảnh xám đơn sắc bằng PIL / NumPy theo manifest, không resize, giữ nguyên độ phân giải gốc (299x299).
- Ép toàn bộ ảnh về đơn sắc (grayscale 'L') để phòng ngừa rò rỉ kênh màu.
- Cài đặt cơ chế bảo vệ nghiêm ngặt: Khóa tập Test (allow_test=False).
- Tính toán Class Weights hỗ trợ xử lý mất cân bằng lớp.
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from PIL import Image

# 4 lớp bài toán phân loại X-quang ngực
CLASS_NAMES = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
LABEL_TO_IDX: Dict[str, int] = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_LABEL: Dict[int, str] = {idx: name for idx, name in enumerate(CLASS_NAMES)}


class CXRDataset:
    """Lớp Dataset nạp ảnh X-quang ngực từ split_v1.csv dưới dạng mảng NumPy xám.

    Hỗ trợ cơ chế khóa tập test: mặc định cấm truy cập split='test' (allow_test=False).
    """

    def __init__(
        self,
        split_df_or_path: Union[pd.DataFrame, str, Path],
        split: str = "train",
        data_root: Optional[Union[str, Path]] = None,
        transform: Optional[Callable] = None,
        allow_test: bool = False,
    ) -> None:
        """Khởi tạo CXRDataset.

        Args:
            split_df_or_path: Đường dẫn tới file split_v1.csv hoặc pandas DataFrame.
            split (str): Phân vùng cần nạp ('train', 'val', 'test').
            data_root: Thư mục gốc chứa ảnh (ví dụ /kaggle/input/.../COVID-19_Radiography_Dataset).
            transform: Hàm biến đổi hoặc trích chọn đặc trưng trên mảng NumPy (tùy chọn).
            allow_test (bool): Cờ cho phép đọc tập test. Mặc định là False.
        """
        split_lower = split.lower().strip()
        if split_lower not in {"train", "val", "test"}:
            raise ValueError(f"Split không hợp lệ: '{split}'. Chỉ chấp nhận 'train', 'val', hoặc 'test'.")

        # Cơ chế khóa nghiêm ngặt tập Test
        if split_lower == "test" and not allow_test:
            raise PermissionError(
                "TẬP TEST ĐÃ BỊ KHÓA NGHIÊM NGẶT!\n"
                "Theo quy tắc đạo đức nghiên cứu và chống rò rỉ dữ liệu của đồ án:\n"
                "- Không được phép truy cập, đánh giá hoặc tinh chỉnh siêu tham số trên tập test ở Tuần 3-9.\n"
                "- Mọi quyết định lựa chọn mô hình chỉ được thực hiện trên tập Validation.\n"
                "- Tập Test chỉ được mở DUY NHẤT một lần tại Tuần 10 trên mô hình tối ưu đã chốt."
            )

        if isinstance(split_df_or_path, (str, Path)):
            df_full = pd.read_csv(split_df_or_path)
        else:
            df_full = split_df_or_path.copy()

        self.df = df_full[df_full["split"] == split_lower].reset_index(drop=True)
        self.split = split_lower
        self.data_root = Path(data_root) if data_root is not None else None
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def _resolve_image_path(self, row: pd.Series) -> Path:
        """Định vị đường dẫn ảnh tuyệt đối một cách linh hoạt."""
        # 1. Thử qua data_root ghép với rel_image_path
        if self.data_root is not None:
            candidate = self.data_root / row["rel_image_path"]
            if candidate.exists():
                return candidate

        # 2. Thử rel_image_path trực tiếp từ thư mục hiện tại
        candidate = Path(row["rel_image_path"])
        if candidate.exists():
            return candidate

        # 3. Thử image_path lưu trong CSV nếu có
        if "image_path" in row and pd.notna(row["image_path"]):
            candidate = Path(row["image_path"])
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            f"Không thể tìm thấy file ảnh: {row['image_id']} (rel: {row['rel_image_path']})"
        )

    def __getitem__(self, idx: int) -> Tuple[np.ndarray, int]:
        """Đọc ảnh theo index, ép về đơn sắc và trả về (mảng numpy, nhãn)."""
        row = self.df.iloc[idx]
        img_path = self._resolve_image_path(row)

        with Image.open(img_path) as img:
            # Ép về ảnh xám (Grayscale 'L') để phòng ngừa rò rỉ kênh màu, không resize
            gray_img = img.convert("L")
            img_arr = np.array(gray_img, dtype=np.uint8)

        if self.transform is not None:
            img_arr = self.transform(img_arr)

        label_name = row["label"]
        label_idx = LABEL_TO_IDX[label_name]

        return img_arr, label_idx


def compute_class_weights(
    split_df_or_path: Union[pd.DataFrame, str, Path],
    split: str = "train",
    num_classes: int = 4,
) -> np.ndarray:
    """Tính toán trọng số nghịch đảo tần suất lớp (Balanced Class Weights) cho ML.

    Công thức: w_c = N / (C * N_c)
    Giúp giảm thiểu tác động tiêu cực của tình trạng mất cân bằng lớp (Normal chiếm ~48%).

    Args:
        split_df_or_path: Đường dẫn tới CSV hoặc DataFrame.
        split (str): Mặc định tính trên tập 'train'.
        num_classes (int): Số lớp (4).

    Returns:
        np.ndarray: Mảng trọng số 1D [w_0, w_1, w_2, w_3].
    """
    if isinstance(split_df_or_path, (str, Path)):
        df = pd.read_csv(split_df_or_path)
    else:
        df = split_df_or_path

    df_subset = df[df["split"] == split.lower()]
    total_samples = len(df_subset)

    class_counts = df_subset["label"].value_counts().to_dict()
    weights = np.zeros(num_classes, dtype=np.float32)

    for cls_name, cls_idx in LABEL_TO_IDX.items():
        count = class_counts.get(cls_name, 1)
        weights[cls_idx] = total_samples / (num_classes * count)

    return weights
