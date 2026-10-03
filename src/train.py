"""Module train.py

Trách nhiệm:
- Điều khiển vòng lặp huấn luyện (train loop) và kiểm định (val loop) cho mô hình (phụ trách: TV2).
- Hỗ trợ huấn luyện độ chính xác hỗn hợp (Mixed Precision) với torch.cuda.amp giúp tối ưu bộ nhớ GPU.
- Quản lý checkpoint nghiêm ngặt:
  + Tự động lưu 'last.pt' sau mỗi epoch để sẵn sàng phục hồi khi kernel bị ngắt phiên (preemption).
  + Tự động lưu 'best.pt' khi chỉ số Macro-F1 trên tập Validation đạt kỷ lục mới.
- Cơ chế Resume Training liền mạch: Nạp model, optimizer, scheduler, scaler và tiếp tục từ epoch tiếp theo.
- Quy ước đặt tên run chuẩn hóa phục vụ quản lý thực nghiệm.
"""

from datetime import datetime
import json
import os
from pathlib import Path
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from src.metrics import compute_metrics


def generate_run_id(model_name: str = "resnet18", seed: int = 42) -> str:
    """Tạo mã định danh duy nhất cho một lượt huấn luyện (run_id).

    Quy ước đặt tên: <model_name>_seed<seed>_<YYYYMMDD_HHMMSS>
    Ví dụ: resnet18_seed42_20261002_203000
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_model = model_name.lower().replace("-", "").replace("_", "")
    return f"{clean_model}_seed{seed}_{timestamp}"


def save_checkpoint(
    state: Dict[str, Any],
    filepath: Path,
) -> None:
    """Lưu checkpoint PyTorch an toàn vào đĩa."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    torch.save(state, str(filepath))


def load_checkpoint(
    checkpoint_path: Path,
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[Any] = None,
    scaler: Optional[Any] = None,
    device: str = "cpu",
) -> Tuple[int, float]:
    """Khôi phục trạng thái huấn luyện từ checkpoint .pt để resume phiên làm việc.

    Args:
        checkpoint_path: Đường dẫn tới file checkpoint (.pt).
        model: Mô hình PyTorch cần nạp trọng số.
        optimizer: Bộ tối ưu cần nạp trạng thái (tùy chọn).
        scheduler: Bộ điều chỉnh learning rate (tùy chọn).
        scaler: GradScaler của AMP (tùy chọn).
        device: Thiết bị tính toán ('cuda' hoặc 'cpu').

    Returns:
        Tuple[int, float]: (start_epoch, best_val_f1)
        start_epoch: Epoch tiếp theo cần chạy (epoch đã lưu + 1).
        best_val_f1: Điểm Macro-F1 tốt nhất từng ghi nhận.
    """
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file checkpoint để resume: {checkpoint_path}")

    checkpoint = torch.load(str(checkpoint_path), map_location=device)

    # 1. Nạp trọng số mô hình
    model.load_state_dict(checkpoint["model_state_dict"])

    # 2. Nạp trạng thái optimizer nếu có
    if optimizer is not None and "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    # 3. Nạp trạng thái scheduler nếu có
    if scheduler is not None and "scheduler_state_dict" in checkpoint and checkpoint["scheduler_state_dict"] is not None:
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    # 4. Nạp trạng thái AMP scaler nếu có
    if scaler is not None and "scaler_state_dict" in checkpoint and checkpoint["scaler_state_dict"] is not None:
        scaler.load_state_dict(checkpoint["scaler_state_dict"])

    saved_epoch = checkpoint.get("epoch", 0)
    best_val_f1 = checkpoint.get("best_val_f1", checkpoint.get("val_macro_f1", 0.0))
    start_epoch = saved_epoch + 1

    print(f"ĐÃ KHÔI PHỤC CHECKPOINT: Tiếp tục từ Epoch {start_epoch} (Kỷ lục Macro-F1 trước đó: {best_val_f1:.4f})")
    return start_epoch, best_val_f1


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: Optional[Any],
    device: torch.device,
    use_amp: bool = True,
) -> Tuple[float, float]:
    """Thực thi một epoch huấn luyện trên tập Train."""
    model.train()
    running_loss = 0.0
    correct_preds = 0
    total_samples = 0

    pbar = tqdm(dataloader, desc="Training", leave=False)
    for images, targets in pbar:
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        optimizer.zero_grad()

        # Mixed Precision context
        if use_amp and device.type == "cuda" and scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, targets)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

        batch_size = images.size(0)
        running_loss += loss.item() * batch_size
        _, preds = torch.max(outputs, 1)
        correct_preds += torch.sum(preds == targets.data).item()
        total_samples += batch_size

        pbar.set_postfix({"loss": f"{loss.item():.4f}"})

    epoch_loss = running_loss / total_samples
    epoch_acc = correct_preds / total_samples
    return epoch_loss, epoch_acc


def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    class_names: Optional[list] = None,
) -> Tuple[float, Dict[str, Any]]:
    """Thực thi đánh giá trên tập Validation."""
    model.eval()
    running_loss = 0.0
    total_samples = 0
    all_targets = []
    all_preds = []

    with torch.no_grad():
        for images, targets in tqdm(dataloader, desc="Validating", leave=False):
            images = images.to(device, non_blocking=True)
            targets = targets.to(device, non_blocking=True)

            outputs = model(images)
            loss = criterion(outputs, targets)

            batch_size = images.size(0)
            running_loss += loss.item() * batch_size
            total_samples += batch_size

            _, preds = torch.max(outputs, 1)
            all_targets.extend(targets.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    val_loss = running_loss / total_samples
    val_metrics = compute_metrics(all_targets, all_preds, class_names=class_names)
    return val_loss, val_metrics


def train_pipeline(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Optional[Any] = None,
    num_epochs: int = 5,
    device_name: str = "cuda" if torch.cuda.is_available() else "cpu",
    output_dir: Path = Path("outputs/checkpoints"),
    run_id: Optional[str] = None,
    resume_from: Optional[Path] = None,
    use_amp: bool = True,
    class_names: Optional[list] = None,
) -> Dict[str, Any]:
    """Pipeline điều phối toàn bộ quá trình huấn luyện và lưu checkpoint."""
    device = torch.device(device_name)
    model.to(device)

    if run_id is None:
        run_id = generate_run_id()

    checkpoint_dir = output_dir / run_id
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    last_pt_path = checkpoint_dir / "last.pt"
    best_pt_path = checkpoint_dir / "best.pt"
    history_path = checkpoint_dir / "train_history.json"

    # Cấu hình AMP GradScaler
    scaler = None
    if use_amp and device.type == "cuda":
        scaler = torch.cuda.amp.GradScaler()

    start_epoch = 1
    best_val_f1 = 0.0
    history = []

    # Xử lý Resume
    if resume_from is not None and Path(resume_from).exists():
        start_epoch, best_val_f1 = load_checkpoint(
            checkpoint_path=Path(resume_from),
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            scaler=scaler,
            device=device_name,
        )
        if history_path.exists():
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)

    print(f"=== BẮT ĐẦU HUẤN LUYỆN: Run ID = {run_id} | Thiết bị = {device} | Epochs = {start_epoch} -> {num_epochs} ===")

    for epoch in range(start_epoch, num_epochs + 1):
        t0 = time.time()
        print(f"\n--- Epoch {epoch}/{num_epochs} ---")

        train_loss, train_acc = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            scaler=scaler,
            device=device,
            use_amp=use_amp,
        )

        val_loss, val_metrics = validate(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
            class_names=class_names,
        )

        if scheduler is not None:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(val_loss)
            else:
                scheduler.step()

        elapsed = time.time() - t0
        val_f1 = val_metrics["macro_f1"]
        val_acc = val_metrics["accuracy"]

        print(
            f"Epoch {epoch:02d} [{elapsed:.1f}s]: "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | Val Macro-F1: {val_f1:.4f}"
        )

        # Trạng thái checkpoint
        ckpt_state = {
            "epoch": epoch,
            "run_id": run_id,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict() if scheduler else None,
            "scaler_state_dict": scaler.state_dict() if scaler else None,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_macro_f1": val_f1,
            "best_val_f1": max(best_val_f1, val_f1),
        }

        # 1. Luôn lưu last.pt phục vụ resume
        save_checkpoint(ckpt_state, last_pt_path)

        # 2. Lưu best.pt khi val_macro_f1 cải thiện
        is_best = val_f1 > best_val_f1
        if is_best:
            best_val_f1 = val_f1
            ckpt_state["best_val_f1"] = best_val_f1
            save_checkpoint(ckpt_state, best_pt_path)
            print(f"⭐ KỶ LỤC MỚI: Đã cập nhật best.pt (Macro-F1 = {best_val_f1:.4f})")

        # Lưu lịch sử log
        epoch_record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "val_macro_f1": round(val_f1, 4),
            "is_best": is_best,
            "elapsed_seconds": round(elapsed, 2),
        }
        history.append(epoch_record)
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"\nHUẤN LUYỆN HOÀN TẤT. Kỷ lục Macro-F1 đạt được: {best_val_f1:.4f}")
    return {
        "run_id": run_id,
        "best_val_f1": best_val_f1,
        "last_checkpoint": str(last_pt_path),
        "best_checkpoint": str(best_pt_path),
        "history": history,
    }
