"""Module models.py

Trách nhiệm:
- Định nghĩa và khởi tạo kiến trúc mạng học sâu cho bài toán phân loại X-quang 4 lớp.
- Hỗ trợ mô hình ResNet-18 (tối thiểu cho Smoke Test Tuần 3), mở rộng DenseNet-121 và EfficientNet-B0.
- Cho phép khởi tạo không cần trọng số pretrained (pretrained=False) để chạy offline trên Kaggle khi tắt internet.
- Thay thế classifier head tương ứng với 4 lớp phân loại.
- Cung cấp tiện ích đóng băng (freeze) và mở khóa (unfreeze) backbone phục vụ transfer learning.

Ghi chú phân công:
- Theo docs/OWNERS.md, src/models.py hiện CHƯA có chủ sở hữu chính thức (được báo cáo lên Leader).
"""

from typing import Optional
import torch
import torch.nn as nn
from torchvision import models


def get_model(
    model_name: str = "resnet18",
    num_classes: int = 4,
    pretrained: bool = False,
) -> nn.Module:
    """Khởi tạo mô hình CNN và thay thế classifier head cho bài toán 4 lớp.

    Args:
        model_name (str): Tên kiến trúc ('resnet18', 'densenet121', 'efficientnet_b0').
        num_classes (int): Số lượng lớp phân loại (mặc định 4).
        pretrained (bool): True để tải trọng số ImageNet (yêu cầu internet hoặc file weights có sẵn).
                           False để khởi tạo trọng số ngẫu nhiên (dùng cho Smoke Test với internet=False).

    Returns:
        nn.Module: Mô hình PyTorch đã điều chỉnh classifier head.
    """
    name_clean = model_name.lower().replace("-", "").replace("_", "")

    if "resnet18" in name_clean:
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)

    elif "densenet121" in name_clean:
        weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
        model = models.densenet121(weights=weights)
        in_features = model.classifier.in_features
        model.classifier = nn.Linear(in_features, num_classes)

    elif "efficientnetb0" in name_clean:
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)

    else:
        raise ValueError(
            f"Kiến trúc '{model_name}' chưa được hỗ trợ! "
            f"Các tùy chọn hợp lệ: ['resnet18', 'densenet121', 'efficientnet_b0']."
        )

    return model


def freeze_backbone(model: nn.Module) -> None:
    """Đóng băng toàn bộ trọng số của backbone (chỉ huấn luyện classifier head)."""
    for param in model.parameters():
        param.requires_grad = False

    # Mở khóa head phân loại
    if hasattr(model, "fc"):
        for param in model.fc.parameters():
            param.requires_grad = True
    elif hasattr(model, "classifier"):
        for param in model.classifier.parameters():
            param.requires_grad = True


def unfreeze_all(model: nn.Module) -> None:
    """Mở khóa toàn bộ các tham số trong mạng (fine-tuning toàn bộ mô hình)."""
    for param in model.parameters():
        param.requires_grad = True
