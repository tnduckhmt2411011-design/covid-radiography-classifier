"""Module dataset.py

Trách nhiệm:
- Quản lý nạp dữ liệu từ file split_v1.csv (phụ trách: TV1).
- Định nghĩa lớp PyTorch CXRDataset cho bài toán phân loại 4 nhóm ảnh X-quang ngực.
- Thiết kế Data Augmentation cho tập Train và Transform chuẩn hóa cho Validation (phụ trách: TV4).
- Cài đặt cơ chế bảo vệ nghiêm ngặt: Khóa tập Test (allow_test=False).
- Tính toán Class Weights hỗ trợ xử lý mất cân bằng lớp.
"""

import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

# 4 lớp bài toán phân loại X-quang ngực
CLASS_NAMES = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
LABEL_TO_IDX: Dict[str, int] = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_LABEL: Dict[int, str] = {idx: name for idx, name in enumerate(CLASS_NAMES)}

# Chuẩn hóa ImageNet
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms(
    img_size: int = 224,
    is_train: bool = True,
) -> transforms.Compose:
    """Tạo chuỗi biến đổi tiền xử lý và tăng cường dữ liệu ảnh X-quang.

    Quy tắc y khoa nghiêm ngặt (TV4 phụ trách):
    - TUYỆT ĐỐI KHÔNG sử dụng RandomHorizontalFlip (lật ngang).
      Lý do: Tim người nằm ở lồng ngực bên trái; lật ngang làm đảo ngược vị trí tim và
      bóng các cơ quan nội tạng (Situs Inversus nhân tạo), gây sai lệch đặc trưng y học.
    - Train augmentation an toàn: Xoay nhẹ (+/- 7 độ), co giãn nhẹ (scale 0.95-1.05),
      chỉnh sáng và tương phản nhẹ (+/- 10%).
    - Validation: Chỉ resize và normalize.

    Args:
        img_size (int): Kích thước cạnh ảnh đầu ra (mặc định 224).
        is_train (bool): True nếu áp dụng augmentation cho tập train, False cho val/test.

    Returns:
        transforms.Compose: Pipeline tiền xử lý của torchvision.
    """
    if is_train:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomRotation(degrees=(-7, 7)),
            transforms.RandomAffine(
                degrees=0,
                translate=(0.02, 0.02),
                scale=(0.95, 1.05),
            ),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])


class CXRDataset(Dataset):
    """Lớp Dataset nạp ảnh X-quang ngực từ split_v1.csv.

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
            transform: Chuỗi biến đổi ảnh. Nếu None sẽ tự tạo theo get_transforms.
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

        if transform is not None:
            self.transform = transform
        else:
            self.transform = get_transforms(img_size=224, is_train=(split_lower == "train"))

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

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        row = self.df.iloc[idx]
        img_path = self._resolve_image_path(row)

        with Image.open(img_path) as img:
            # Luôn chuyển đổi sang RGB 3 kênh để tương thích các kiến trúc CNN
            img = img.convert("RGB")
            tensor_img = self.transform(img)

        label_name = row["label"]
        label_idx = LABEL_TO_IDX[label_name]

        return tensor_img, label_idx


def compute_class_weights(
    split_df_or_path: Union[pd.DataFrame, str, Path],
    split: str = "train",
    num_classes: int = 4,
) -> torch.FloatTensor:
    """Tính toán trọng số nghịch đảo tần suất lớp (Balanced Class Weights) cho Loss Function.

    Công thức: w_c = N / (C * N_c)
    Giúp giảm thiểu tác động tiêu cực của tình trạng mất cân bằng lớp (Normal chiếm ~48%).

    Args:
        split_df_or_path: Đường dẫn tới CSV hoặc DataFrame.
        split (str): Mặc định tính trên tập 'train'.
        num_classes (int): Số lớp (4).

    Returns:
        torch.FloatTensor: Mảng trọng số 1D tensor [w_0, w_1, w_2, w_3].
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

    return torch.tensor(weights, dtype=torch.float32)


def build_dataloaders(
    split_csv_path: Union[str, Path],
    data_root: Optional[Union[str, Path]] = None,
    batch_size: int = 32,
    num_workers: int = 2,
    img_size: int = 224,
    allow_test: bool = False,
) -> Dict[str, DataLoader]:
    """Khởi tạo DataLoaders cho các phân vùng huấn luyện và kiểm định.

    Args:
        split_csv_path: Đường dẫn tới file split_v1.csv.
        data_root: Thư mục gốc chứa ảnh (nếu chạy trên Kaggle/Colab).
        batch_size: Kích thước mini-batch.
        num_workers: Số luồng nạp dữ liệu.
        img_size: Kích thước ảnh đầu vào mô hình.
        allow_test: Cờ cho phép nạp tập test (mặc định False).

    Returns:
        Dict[str, DataLoader]: Dict chứa 'train', 'val' (và 'test' nếu allow_test=True).
    """
    train_ds = CXRDataset(
        split_df_or_path=split_csv_path,
        split="train",
        data_root=data_root,
        transform=get_transforms(img_size=img_size, is_train=True),
        allow_test=False,
    )

    val_ds = CXRDataset(
        split_df_or_path=split_csv_path,
        split="val",
        data_root=data_root,
        transform=get_transforms(img_size=img_size, is_train=False),
        allow_test=False,
    )

    dataloaders = {
        "train": DataLoader(
            train_ds,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        ),
        "val": DataLoader(
            val_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        ),
    }

    if allow_test:
        test_ds = CXRDataset(
            split_df_or_path=split_csv_path,
            split="test",
            data_root=data_root,
            transform=get_transforms(img_size=img_size, is_train=False),
            allow_test=True,
        )
        dataloaders["test"] = DataLoader(
            test_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )

    return dataloaders
