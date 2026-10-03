"""Kiểm thử đơn vị cho cơ chế checkpoint / resume và cổng khóa tập Test.

Tuần 3 (Sprint 2) - Track B.
Phụ trách: TV2 (kèm cặp: TV1).
"""

from pathlib import Path
import tempfile
import torch
import torch.nn as nn
import pytest

from src.train import save_checkpoint, load_checkpoint
from src.dataset import CXRDataset


class DummyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(8, 4)

    def forward(self, x):
        return self.fc(x)


def test_checkpoint_save_and_resume():
    """Kiểm tra lưu checkpoint và resume chính xác epoch tiếp theo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "last.pt"

        # 1. Khởi tạo mô hình và optimizer ban đầu
        model_orig = DummyModel()
        optimizer_orig = torch.optim.Adam(model_orig.parameters(), lr=0.01)

        # Chạy 1 bước giả lập để optimizer có state
        dummy_x = torch.randn(2, 8)
        dummy_y = torch.tensor([0, 1])
        loss = nn.CrossEntropyLoss()(model_orig(dummy_x), dummy_y)
        loss.backward()
        optimizer_orig.step()

        # Lưu checkpoint tại epoch 2
        state = {
            "epoch": 2,
            "model_state_dict": model_orig.state_dict(),
            "optimizer_state_dict": optimizer_orig.state_dict(),
            "best_val_f1": 0.8542,
        }
        save_checkpoint(state, ckpt_path)
        assert ckpt_path.exists()

        # 2. Khởi tạo mô hình mới và resume
        model_resumed = DummyModel()
        optimizer_resumed = torch.optim.Adam(model_resumed.parameters(), lr=0.01)

        start_epoch, best_val_f1 = load_checkpoint(
            checkpoint_path=ckpt_path,
            model=model_resumed,
            optimizer=optimizer_resumed,
        )

        # Kiểm tra start_epoch phải là epoch tiếp theo (2 + 1 = 3)
        assert start_epoch == 3
        assert best_val_f1 == 0.8542

        # Kiểm tra trọng số mô hình khớp chính xác 100%
        for k in model_orig.state_dict():
            assert torch.equal(model_orig.state_dict()[k], model_resumed.state_dict()[k])


def test_resume_non_existent_file():
    """Kiểm tra ném FileNotFoundError khi file checkpoint không tồn tại."""
    model = DummyModel()
    with pytest.raises(FileNotFoundError):
        load_checkpoint(Path("non_existent_file.pt"), model)


def test_dataset_allow_test_lock():
    """Kiểm tra cơ chế khóa tập test: ném PermissionError khi allow_test=False."""
    import pandas as pd

    # Tạo dataframe giả lập
    dummy_df = pd.DataFrame({
        "image_id": ["dummy.png"],
        "label": ["COVID"],
        "rel_image_path": ["dummy.png"],
        "split": ["test"]
    })

    # Cố tình truy cập split='test' khi allow_test=False -> BẮT BUỘC ném lỗi PermissionError
    with pytest.raises(PermissionError):
        CXRDataset(split_df_or_path=dummy_df, split="test", allow_test=False)


if __name__ == "__main__":
    test_checkpoint_save_and_resume()
    test_resume_non_existent_file()
    test_dataset_allow_test_lock()
    print("Tất cả bài kiểm tra resume và test locking đều ĐẠT!")
