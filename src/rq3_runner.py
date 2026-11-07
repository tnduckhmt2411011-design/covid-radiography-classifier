"""Module điều phối thực thi S4-07 (kiểm tra bộ ảnh che phổi) và RQ3 (S5-01, S5-02: đánh giá shortcut learning).

Trách nhiệm:
- Cài đặt phép biến đổi ảnh X-quang 299x299 theo mặt nạ phổi 256x256 (đổi kích thước bằng nội suy gần nhất
  nearest-neighbor về 299x299 theo mục 1 của results/threshold_v3.md) cho 3 chế độ:
  'original' (ảnh gốc), 'lung_only' (chỉ giữ vùng trong phổi), 'outside_only' (chỉ giữ vùng ngoài phổi).
- Thực hiện kiểm tra căn chỉnh và xuất lưới ảnh kiểm tra bằng mắt >= 20 ảnh/lớp trên 4 lớp (S4-07),
  kèm thống kê diện tích/tâm khối phổi trên toàn bộ ảnh được nạp.
- Trích đặc trưng 'ghep' (152 chiều) trên cả 3 chế độ ảnh cho tập train và tập val (allow_test=False).
- Đánh giá cấu hình mô hình đóng băng từ S4-04 (StandardScaler chỉ fit trên train + SVC RBF C=10.0, gamma='scale',
  class_weight='balanced', probability=True, random_state=42) trên 5 kịch bản (S5-01 & R3):
  1. orig_to_orig: Huấn luyện trên train(original), đánh giá trên val(original)
  2. orig_to_lung: Huấn luyện trên train(original), đánh giá trên val(lung_only) (RQ3-A: nhiễu che nền khi suy luận)
  3. orig_to_out:  Huấn luyện trên train(original), đánh giá trên val(outside_only) (RQ3-A: nhiễu che phổi khi suy luận)
  4. lung_to_lung: Huấn luyện trên train(lung_only), đánh giá trên val(lung_only) (R3: đặc trưng chỉ từ trong phổi)
  5. out_to_out:   Huấn luyện trên train(outside_only), đánh giá trên val(outside_only) (R3: đặc trưng chỉ từ ngoài phổi)
- Tính permutation importance theo 10 khối ngữ nghĩa của đặc trưng 'ghep' trên tập validation (S5-02).
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import cv2
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import yaml

from src.bootstrap import macro_f1_from_labels
from src.dataset import CLASS_NAMES, LABEL_TO_IDX
from src.features_hog_ghep import extract_groups
from src.metrics import compute_metrics
from src.rq2_runner import (
    CHUNK_SIZE,
    EXPECTED_TRAIN_N,
    EXPECTED_VAL_N,
    EXPECTED_VERSIONS,
    HARD_PINNED_PACKAGES,
    PROBA_COLUMNS,
    check_pinned_versions,
    collect_versions,
    feature_params,
    find_data_root,
    stratified_subset,
    write_run_outputs,
)

RQ_NAME: str = "rq3"
MASK_MODES: Tuple[str, ...] = ("original", "lung_only", "outside_only")
MODE_SHORT_TAG: Dict[str, str] = {
    "original": "orig",
    "lung_only": "lung",
    "outside_only": "out",
}
EVAL_SCENARIOS: Tuple[Tuple[str, str], ...] = (
    ("original", "original"),
    ("original", "lung_only"),
    ("original", "outside_only"),
    ("lung_only", "lung_only"),
    ("outside_only", "outside_only"),
)
FROZEN_FEATURES: str = "ghep"
FROZEN_CLASSIFIER: str = "svm"
FROZEN_SEED: int = 42
FROZEN_SVM_PARAMS: Dict[str, Any] = {
    "kernel": "rbf",
    "C": 10.0,
    "gamma": "scale",
    "class_weight": "balanced",
    "probability": True,
    "random_state": 42,
}

# 10 khối ngữ nghĩa của vector đặc trưng ghep (152 chiều = 64 Hist + 60 GLCM + 28 LBP)
FEATURE_BLOCKS: Dict[str, Tuple[int, int]] = {
    "hist_64": (0, 64),
    "glcm_60": (64, 124),
    "lbp_28": (124, 152),
    "glcm_contrast_12": (64, 76),
    "glcm_dissimilarity_12": (76, 88),
    "glcm_homogeneity_12": (88, 100),
    "glcm_energy_12": (100, 112),
    "glcm_correlation_12": (112, 124),
    "lbp_r1_p8_10": (124, 134),
    "lbp_r2_p16_18": (134, 152),
}

PACKAGE_SRC_FILES: Tuple[str, ...] = (
    "dataset.py",
    "metrics.py",
    "bootstrap.py",
    "features_hist_glcm_lbp.py",
    "features_hog_ghep.py",
    "rq1_runner.py",
    "rq2_runner.py",
    "rq3_runner.py",
)
PACKAGE_SPLIT_FILES: Tuple[str, ...] = (
    "split_v1.csv",
    "split_v1.sha256",
)


def make_rq3_run_id(train_mode: str, eval_mode: str, seed: int = FROZEN_SEED) -> str:
    """Tạo mã định danh run_id chuẩn cho RQ3."""
    if train_mode not in MODE_SHORT_TAG or eval_mode not in MODE_SHORT_TAG:
        raise ValueError(f"Chế độ che không hợp lệ: train={train_mode}, eval={eval_mode}")
    tr_tag = MODE_SHORT_TAG[train_mode]
    ev_tag = MODE_SHORT_TAG[eval_mode]
    return f"rq3_{FROZEN_FEATURES}_{FROZEN_CLASSIFIER}_{tr_tag}_to_{ev_tag}_s{seed}"


def resize_mask_nearest(
    mask_raw: np.ndarray,
    target_hw: Tuple[int, int] = (299, 299),
) -> np.ndarray:
    """Đổi kích thước mặt nạ phổi (256x256) về kích thước ảnh (299x299) bằng nội suy gần nhất (nearest).

    Args:
        mask_raw: Mảng numpy 2D (H, W) hoặc 3D (H, W, C) của mask gốc.
        target_hw: Kích thước đích (height, width), mặc định (299, 299).

    Returns:
        np.ndarray: Mảng boolean 2D shape target_hw (True = trong phổi, False = ngoài phổi).
    """
    arr = np.asarray(mask_raw)
    if arr.ndim == 3:
        arr_2d = arr[..., 0]
    elif arr.ndim == 2:
        arr_2d = arr
    else:
        raise ValueError(f"mask_raw phải là mảng 2D hoặc 3D, nhận được shape={arr.shape}")

    th, tw = int(target_hw[0]), int(target_hw[1])
    if arr_2d.shape != (th, tw):
        resized = cv2.resize(
            arr_2d.astype(np.uint8),
            (tw, th),
            interpolation=cv2.INTER_NEAREST,
        )
    else:
        resized = arr_2d.astype(np.uint8)

    return resized > 127


def apply_mask_modes(img: np.ndarray, mask_bin: np.ndarray) -> Dict[str, np.ndarray]:
    """Tạo 3 phiên bản ảnh X-quang: original, lung_only và outside_only.

    Args:
        img: Ảnh xám uint8 shape (299, 299).
        mask_bin: Mặt nạ phổi boolean shape (299, 299).

    Returns:
        Dict ánh xạ tên chế độ ('original', 'lung_only', 'outside_only') sang mảng uint8 (299, 299).
    """
    if img.ndim != 2 or img.dtype != np.uint8:
        raise ValueError(f"img phải là mảng 2D uint8, nhận được shape={img.shape}, dtype={img.dtype}")
    if mask_bin.shape != img.shape or mask_bin.dtype != np.bool_:
        raise ValueError(
            f"mask_bin phải cùng shape {img.shape} và kiểu bool, nhận được shape={mask_bin.shape}, dtype={mask_bin.dtype}"
        )

    zero = np.uint8(0)
    return {
        "original": img.copy(),
        "lung_only": np.where(mask_bin, img, zero),
        "outside_only": np.where(~mask_bin, img, zero),
    }


def compute_mask_alignment_metrics(
    img: np.ndarray,
    mask_bin: np.ndarray,
    orig_mask_shape: Tuple[int, int] = (256, 256),
) -> Dict[str, Any]:
    """Tính các chỉ số kiểm tra căn chỉnh hình học giữa mặt nạ phổi và ảnh X-quang (S4-07)."""
    h, w = img.shape
    total_px = float(h * w)
    lung_px = int(np.sum(mask_bin))
    lung_fraction = float(lung_px / total_px) if total_px > 0 else 0.0
    is_empty = bool(lung_px == 0)

    if not is_empty:
        ys, xs = np.nonzero(mask_bin)
        bbox_ymin = int(np.min(ys))
        bbox_ymax = int(np.max(ys))
        bbox_xmin = int(np.min(xs))
        bbox_xmax = int(np.max(xs))
        centroid_y = float(np.mean(ys) / h)
        centroid_x = float(np.mean(xs) / w)
        mid_x = w // 2
        left_px = int(np.sum(mask_bin[:, :mid_x]))
        right_px = int(np.sum(mask_bin[:, mid_x:]))
        left_lung_fraction = float(left_px / total_px)
        right_lung_fraction = float(right_px / total_px)
        inside_mean_gray = float(np.mean(img[mask_bin]))
        outside_mean_gray = float(np.mean(img[~mask_bin])) if lung_px < h * w else 0.0
    else:
        bbox_ymin = bbox_ymax = bbox_xmin = bbox_xmax = 0
        centroid_y = centroid_x = 0.0
        left_lung_fraction = right_lung_fraction = 0.0
        inside_mean_gray = 0.0
        outside_mean_gray = float(np.mean(img))

    # Kiểm tra tâm khối vùng phổi nằm trong lồng ngực (không bị lệch góc) và tỉ lệ diện tích hợp lý
    is_centered = bool(
        (not is_empty)
        and (0.02 <= lung_fraction <= 0.75)
        and (0.15 <= centroid_y <= 0.85)
        and (0.18 <= centroid_x <= 0.82)
    )

    return {
        "orig_h": int(orig_mask_shape[0]),
        "orig_w": int(orig_mask_shape[1]),
        "target_h": int(h),
        "target_w": int(w),
        "lung_pixels": lung_px,
        "lung_fraction": round(lung_fraction, 6),
        "is_empty": is_empty,
        "bbox_ymin": bbox_ymin,
        "bbox_ymax": bbox_ymax,
        "bbox_xmin": bbox_xmin,
        "bbox_xmax": bbox_xmax,
        "centroid_y_norm": round(centroid_y, 4),
        "centroid_x_norm": round(centroid_x, 4),
        "left_lung_fraction": round(left_lung_fraction, 6),
        "right_lung_fraction": round(right_lung_fraction, 6),
        "inside_mean_gray": round(inside_mean_gray, 2),
        "outside_mean_gray": round(outside_mean_gray, 2),
        "is_centered": is_centered,
    }


def _load_gray_and_mask(
    dataset_root: Path,
    rel_img_path: str,
    rel_mask_path: str,
) -> Tuple[np.ndarray, np.ndarray, Tuple[int, int]]:
    """Đọc ảnh xám 299x299 và mặt nạ phổi, đổi kích thước mặt nạ bằng nearest về 299x299."""
    img_path = dataset_root / rel_img_path
    mask_path = dataset_root / rel_mask_path

    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Không thể đọc ảnh: {img_path}")
    if img.shape != (299, 299):
        raise ValueError(f"Kích thước ảnh {img_path} là {img.shape}, kỳ vọng (299, 299)")

    mask_raw = cv2.imread(str(mask_path), cv2.IMREAD_UNCHANGED)
    if mask_raw is None:
        raise FileNotFoundError(f"Không thể đọc mask: {mask_path}")
    orig_hw = (int(mask_raw.shape[0]), int(mask_raw.shape[1]))
    mask_bin = resize_mask_nearest(mask_raw, target_hw=(299, 299))
    return img, mask_bin, orig_hw


def _render_class_contact_sheet(
    triplets: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    out_png: Path,
    tile_size: int = 120,
) -> None:
    """Vẽ lưới ảnh kiểm tra trực quan (mỗi mẫu gồm 3 cột: Gốc+Viền phổi | Chỉ phổi | Ngoài phổi)."""
    n_samples = len(triplets)
    cols_per_sample = 3
    samples_per_row = 2 if n_samples >= 2 else 1
    n_rows = (n_samples + samples_per_row - 1) // samples_per_row
    n_cols = samples_per_row * cols_per_sample
    header_h = 22
    cell_h = tile_size + header_h
    cell_w = tile_size

    canvas = np.full((n_rows * cell_h, n_cols * cell_w, 3), 24, dtype=np.uint8)

    for idx, (img_id, orig, mask_bin, lung_only, out_only) in enumerate(triplets):
        r = idx // samples_per_row
        c_base = (idx % samples_per_row) * cols_per_sample
        y0 = r * cell_h

        # Tạo ảnh chồng viền mask màu xanh lá lên ảnh gốc
        orig_bgr = cv2.cvtColor(orig, cv2.COLOR_GRAY2BGR)
        mask_u8 = (mask_bin.astype(np.uint8)) * 255
        contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(orig_bgr, contours, -1, (0, 255, 0), 2)

        lung_bgr = cv2.cvtColor(lung_only, cv2.COLOR_GRAY2BGR)
        out_bgr = cv2.cvtColor(out_only, cv2.COLOR_GRAY2BGR)

        panels = [
            (f"{img_id} [Orig+Mask]", orig_bgr),
            ("Lung-Only", lung_bgr),
            ("Outside-Only", out_bgr),
        ]
        for p_idx, (title, panel_img) in enumerate(panels):
            x0 = (c_base + p_idx) * cell_w
            resized_panel = cv2.resize(panel_img, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
            canvas[y0 + header_h : y0 + cell_h, x0 : x0 + cell_w] = resized_panel
            cv2.putText(
                canvas,
                title[:22],
                (x0 + 3, y0 + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.36,
                (235, 235, 235),
                1,
                cv2.LINE_AA,
            )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_png), canvas)


def generate_visual_mask_check(
    dataset_root: Union[str, Path],
    split_csv: Union[str, Path],
    out_dir: Union[str, Path],
    samples_per_class: int = 20,
    seed: int = FROZEN_SEED,
) -> Dict[str, Any]:
    """Chọn mẫu phân tầng từ tập val (không chạm test) và xuất bộ ảnh kiểm tra trực quan S4-07."""
    ds_path = Path(dataset_root)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(split_csv)
    # Chỉ lấy mẫu từ val (hoặc train+val nếu val nhỏ trong test giả lập), tuyệt đối không đọc test
    val_df = df[df["split"] == "val"].copy()
    if len(val_df) < samples_per_class * len(CLASS_NAMES):
        val_df = df[df["split"].isin(["train", "val"])].copy()

    rng = np.random.default_rng(seed)
    sample_rows: List[Dict[str, Any]] = []
    png_files: Dict[str, str] = {}

    for c_name in CLASS_NAMES:
        c_df = val_df[val_df["label"] == c_name].sort_values("image_id").reset_index(drop=True)
        n_pick = min(samples_per_class, len(c_df))
        picked_indices = sorted(rng.choice(len(c_df), size=n_pick, replace=False).tolist())
        picked_df = c_df.iloc[picked_indices]

        triplets: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
        for _, row in picked_df.iterrows():
            img_id = str(row["image_id"])
            rel_img = str(row["rel_image_path"])
            rel_mask = str(row["rel_mask_path"])
            img, mask_bin, orig_hw = _load_gray_and_mask(ds_path, rel_img, rel_mask)
            modes = apply_mask_modes(img, mask_bin)
            align_met = compute_mask_alignment_metrics(img, mask_bin, orig_mask_shape=orig_hw)

            sample_rows.append({
                "image_id": img_id,
                "label": c_name,
                "split": str(row["split"]),
                **align_met,
            })
            triplets.append((img_id, modes["original"], mask_bin, modes["lung_only"], modes["outside_only"]))

        safe_cls = c_name.replace(" ", "_")
        out_png = out_path / f"mask_visual_check_{safe_cls}.png"
        _render_class_contact_sheet(triplets, out_png)
        png_files[c_name] = out_png.name

    samples_df = pd.DataFrame(sample_rows)
    csv_out = out_path / "mask_visual_check_samples.csv"
    samples_df.to_csv(csv_out, index=False)

    summary = {
        "samples_per_class": int(samples_per_class),
        "total_visual_samples": int(len(samples_df)),
        "empty_masks_count": int(samples_df["is_empty"].sum()),
        "centered_masks_count": int(samples_df["is_centered"].sum()),
        "all_centered": bool(samples_df["is_centered"].all()),
        "lung_fraction_mean": round(float(samples_df["lung_fraction"].mean()), 4),
        "lung_fraction_min": round(float(samples_df["lung_fraction"].min()), 4),
        "lung_fraction_max": round(float(samples_df["lung_fraction"].max()), 4),
        "contact_sheets": png_files,
    }
    with open(out_path / "mask_alignment_summary.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return summary


def compute_block_permutation_importance(
    model: SVC,
    scaler: StandardScaler,
    X_val_raw: np.ndarray,
    y_val: np.ndarray,
    n_repeats: int = 10,
    rng_seed: int = FROZEN_SEED,
) -> pd.DataFrame:
    """Tính độ quan trọng hoán vị (permutation importance) theo 10 khối ngữ nghĩa của đặc trưng ghep (S5-02)."""
    X_val_scaled = scaler.transform(X_val_raw)
    y_val_arr = np.asarray(y_val, dtype=np.int64)
    base_preds = model.predict(X_val_scaled).astype(np.int64)
    baseline_score = macro_f1_from_labels(y_val_arr, base_preds)

    rng = np.random.default_rng(rng_seed)
    n_samples = X_val_scaled.shape[0]
    rows: List[Dict[str, Any]] = []

    for block_name, (col_start, col_end) in FEATURE_BLOCKS.items():
        drops: List[float] = []
        perm_scores: List[float] = []
        for _ in range(n_repeats):
            X_perm = X_val_scaled.copy()
            perm_idx = rng.permutation(n_samples)
            X_perm[:, col_start:col_end] = X_val_scaled[perm_idx, col_start:col_end]
            y_perm_pred = model.predict(X_perm).astype(np.int64)
            sc = macro_f1_from_labels(y_val_arr, y_perm_pred)
            perm_scores.append(sc)
            drops.append(baseline_score - sc)

        rows.append({
            "block_name": block_name,
            "col_start": int(col_start),
            "col_end": int(col_end),
            "n_dims": int(col_end - col_start),
            "n_repeats": int(n_repeats),
            "baseline_score": float(baseline_score),
            "permuted_score_mean": float(np.mean(perm_scores)),
            "importance_mean": float(np.mean(drops)),
            "importance_std": float(np.std(drops, ddof=1)) if n_repeats > 1 else 0.0,
        })

    return pd.DataFrame(rows)


def _extract_three_modes_for_split(
    split_df: pd.DataFrame,
    split: str,
    dataset_root: Path,
    limit: Optional[int] = None,
    subset_seed: int = 0,
) -> Tuple[Dict[str, np.ndarray], List[str], np.ndarray, Dict[str, Any]]:
    """Đọc ảnh và mask của một split (train hoặc val, cấm test) và trích đặc trưng ghep cho cả 3 chế độ che."""
    if split not in ("train", "val"):
        raise ValueError(f"Split '{split}' bị chặn (allow_test=False). Chỉ cho phép 'train' hoặc 'val'.")

    sub_df = split_df[split_df["split"] == split].copy().reset_index(drop=True)
    if limit is not None and limit < len(sub_df):
        idx = stratified_subset(sub_df["label"].tolist(), limit, subset_seed)
        sub_df = sub_df.iloc[idx].reset_index(drop=True)
    y_all = np.array([LABEL_TO_IDX[str(lbl)] for lbl in sub_df["label"]], dtype=np.int64)

    image_ids = [str(x) for x in sub_df["image_id"].tolist()]
    rel_imgs = [str(x) for x in sub_df["rel_image_path"].tolist()]
    rel_masks = [str(x) for x in sub_df["rel_mask_path"].tolist()]
    ds_path = Path(dataset_root)

    features_by_mode: Dict[str, np.ndarray] = {}
    info_by_mode: Dict[str, Any] = {}

    for m_name in MASK_MODES:
        def _gen(mode_target: str = m_name):
            for r_img, r_msk in zip(rel_imgs, rel_masks):
                img, mask_bin, _ = _load_gray_and_mask(ds_path, r_img, r_msk)
                if mode_target == "original":
                    yield img
                elif mode_target == "lung_only":
                    yield np.where(mask_bin, img, np.uint8(0))
                else:
                    yield np.where(~mask_bin, img, np.uint8(0))

        feat_dict, ext_info = extract_groups(_gen(), groups=(FROZEN_FEATURES,), chunk_size=CHUNK_SIZE)
        features_by_mode[m_name] = feat_dict[FROZEN_FEATURES]
        info_by_mode[m_name] = ext_info

    return features_by_mode, image_ids, y_all, info_by_mode


def mode_settings(mode: str) -> Dict[str, Any]:
    """Cấu hình tham số cho từng chế độ chạy ('t0' thử nghiệm mù điểm và 'full' chính thức) của RQ3."""
    if mode == "t0":
        return {
            "limit_train": 120,
            "limit_val": 60,
            "subset_seed": 0,
            "samples_per_class_visual": 5,
            "perm_repeats": 2,
            "score": False,
            "out_subdir": "results_trial",
        }
    elif mode == "full":
        return {
            "limit_train": None,
            "limit_val": None,
            "subset_seed": 0,
            "samples_per_class_visual": 20,
            "perm_repeats": 10,
            "score": True,
            "out_subdir": "results",
        }
    else:
        raise ValueError(f"Mode '{mode}' không hợp lệ cho RQ3. Chỉ hỗ trợ ('t0', 'full').")


def run_rq3_experiment(
    dataset_root: Union[str, Path],
    split_csv: Union[str, Path],
    out_dir: Union[str, Path],
    mode: str = "full",
    score: bool = True,
    limit_train: Optional[int] = None,
    limit_val: Optional[int] = None,
    subset_seed: int = 0,
    samples_per_class_visual: int = 20,
    perm_repeats: int = 10,
    commit: str = "0" * 40,
    expected_split_sha256: Optional[str] = None,
) -> Dict[str, Any]:
    """Điều phối toàn bộ thực nghiệm S4-07 (kiểm tra mask) và RQ3 (S5-01, S5-02)."""
    ds_path = Path(dataset_root)
    csv_path = Path(split_csv)
    out_path = Path(out_dir)
    results_root = out_path / ("results" if score else "results_trial")
    results_root.mkdir(parents=True, exist_ok=True)

    actual_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest().lower()
    if expected_split_sha256 is not None and actual_sha != expected_split_sha256.strip().lower():
        raise ValueError(
            f"SHA256 của {csv_path} ({actual_sha}) khác kỳ vọng ({expected_split_sha256})"
        )

    split_df = pd.read_csv(csv_path)
    req_cols = {"image_id", "label", "rel_image_path", "rel_mask_path", "split", "group_id"}
    if not req_cols.issubset(split_df.columns):
        raise ValueError(f"split_v1.csv thiếu cột bắt buộc: {req_cols - set(split_df.columns)}")

    # 1. Thực hiện S4-07: Kiểm tra trực quan & căn chỉnh mask trên >= samples_per_class_visual ảnh/lớp
    mask_check_dir = results_root / "rq3_mask_check"
    mask_summary = generate_visual_mask_check(
        dataset_root=ds_path,
        split_csv=csv_path,
        out_dir=mask_check_dir,
        samples_per_class=samples_per_class_visual,
        seed=FROZEN_SEED,
    )

    # 2. Trích đặc trưng ghep (152 chiều) cho 3 chế độ che trên train và val
    X_train_modes, _, y_train, info_train_modes = _extract_three_modes_for_split(
        split_df=split_df,
        split="train",
        dataset_root=ds_path,
        limit=limit_train,
        subset_seed=subset_seed,
    )
    X_val_modes, image_ids_val, y_val, info_val_modes = _extract_three_modes_for_split(
        split_df=split_df,
        split="val",
        dataset_root=ds_path,
        limit=limit_val,
        subset_seed=subset_seed,
    )

    # 3. Huấn luyện mô hình đóng băng (StandardScaler + SVC RBF) trên từng chế độ train
    trained_models: Dict[str, Tuple[StandardScaler, SVC, float, float]] = {}
    for tr_mode in MASK_MODES:
        t_cpu0 = time.process_time()
        t_wall0 = time.perf_counter()
        scaler = StandardScaler()
        X_tr_scaled = scaler.fit_transform(X_train_modes[tr_mode])
        clf = SVC(**FROZEN_SVM_PARAMS)
        clf.fit(X_tr_scaled, y_train)
        fit_cpu = float(time.process_time() - t_cpu0)
        fit_wall = float(time.perf_counter() - t_wall0)
        trained_models[tr_mode] = (scaler, clf, fit_cpu, fit_wall)

    versions = collect_versions()
    runs_executed: List[str] = []
    fit_cpu_by_mode: Dict[str, float] = {m: round(trained_models[m][2], 3) for m in MASK_MODES}
    extract_cpu_train_map: Dict[str, float] = {
        m: round(float(info_train_modes[m]["cpu_seconds"][FROZEN_FEATURES]), 3) for m in MASK_MODES
    }
    extract_cpu_val_map: Dict[str, float] = {
        m: round(float(info_val_modes[m]["cpu_seconds"][FROZEN_FEATURES]), 3) for m in MASK_MODES
    }

    # 4. Đánh giá 5 kịch bản (S5-01 & R3)
    for tr_mode, ev_mode in EVAL_SCENARIOS:
        run_id = make_rq3_run_id(tr_mode, ev_mode, seed=FROZEN_SEED)
        runs_executed.append(run_id)
        scaler, clf, fit_cpu, fit_wall = trained_models[tr_mode]

        t_pred0 = time.perf_counter()
        X_ev_scaled = scaler.transform(X_val_modes[ev_mode])
        proba = clf.predict_proba(X_ev_scaled).astype(np.float64)
        y_pred = clf.predict(X_ev_scaled).astype(np.int64)
        pred_wall = float(time.perf_counter() - t_pred0)

        seconds = {
            "extract_cpu_train": extract_cpu_train_map[tr_mode],
            "extract_cpu_val": extract_cpu_val_map[ev_mode],
            "fit_cpu": round(fit_cpu, 3),
            "fit_wall": round(fit_wall, 3),
            "predict_wall": round(pred_wall, 3),
        }

        if score:
            raw_met = dict(compute_metrics(y_val, y_pred))
            metrics_obj: Dict[str, Any] = {
                **raw_met,
                "run_id": run_id,
                "rq": RQ_NAME,
                "mode": mode,
                "train_mask_mode": tr_mode,
                "eval_mask_mode": ev_mode,
                "features": FROZEN_FEATURES,
                "classifier": FROZEN_CLASSIFIER,
                "seed": FROZEN_SEED,
                "n_train": int(len(y_train)),
                "n_val": int(len(y_val)),
                "seconds": seconds,
            }
        else:
            row_sums = np.sum(proba, axis=1)
            metrics_obj = {
                "run_id": run_id,
                "rq": RQ_NAME,
                "mode": mode,
                "train_mask_mode": tr_mode,
                "eval_mask_mode": ev_mode,
                "features": FROZEN_FEATURES,
                "classifier": FROZEN_CLASSIFIER,
                "seed": FROZEN_SEED,
                "scored": False,
                "n_train": int(len(y_train)),
                "n_val": int(len(y_val)),
                "proba_row_sum_min": float(np.min(row_sums)),
                "proba_row_sum_max": float(np.max(row_sums)),
                "seconds": seconds,
            }

        config_obj: Dict[str, Any] = {
            "run_id": run_id,
            "rq": RQ_NAME,
            "mode": mode,
            "train_mask_mode": tr_mode,
            "eval_mask_mode": ev_mode,
            "mask_resize": "nearest_256x256_to_299x299",
            "features": FROZEN_FEATURES,
            "feature_params": feature_params(FROZEN_FEATURES),
            "classifier_tag": FROZEN_CLASSIFIER,
            "classifier": "SVC",
            "deterministic": True,
            "preprocessing": {
                "scaler": "StandardScaler",
                "fit_on": f"train_{tr_mode}_only",
            },
            "hyperparameters": dict(FROZEN_SVM_PARAMS),
            "seed": FROZEN_SEED,
            "commit": commit,
            "versions": versions,
            "split": {
                "file": str(split_csv),
                "sha256": actual_sha,
                "train_rows": int((split_df["split"] == "train").sum()),
                "val_rows": int((split_df["split"] == "val").sum()),
            },
            "evaluation": {
                "train_split": "train",
                "eval_split": "val",
                "allow_test": False,
            },
            "extraction": {
                "train_mode": tr_mode,
                "eval_mode": ev_mode,
                "n_train": int(info_train_modes[tr_mode]["n_images"]),
                "n_val": int(info_val_modes[ev_mode]["n_images"]),
                "glcm_nan_train": int(info_train_modes[tr_mode]["glcm_nan_images"]),
                "glcm_nan_val": int(info_val_modes[ev_mode]["glcm_nan_images"]),
            },
        }

        log_lines = [
            f"run_id={run_id}",
            f"mode={mode}",
            f"train_mask_mode={tr_mode}",
            f"eval_mask_mode={ev_mode}",
            f"mask_resize=nearest_256x256_to_299x299",
            f"features={FROZEN_FEATURES}",
            f"classifier={FROZEN_CLASSIFIER}",
            f"n_train={len(y_train)}",
            f"n_val={len(y_val)}",
            f"GLCM correlation NaN (train {tr_mode}): {info_train_modes[tr_mode]['glcm_nan_images']}/{info_train_modes[tr_mode]['n_images']}",
            f"GLCM correlation NaN (val {ev_mode}): {info_val_modes[ev_mode]['glcm_nan_images']}/{info_val_modes[ev_mode]['n_images']}",
            f"extract_cpu_train={seconds['extract_cpu_train']:.3f}",
            f"extract_cpu_val={seconds['extract_cpu_val']:.3f}",
            f"fit_cpu={seconds['fit_cpu']:.3f}",
            f"predict_wall={seconds['predict_wall']:.3f}",
        ]
        if score:
            log_lines.append(f"macro_f1={metrics_obj['macro_f1']}")

        write_run_outputs(
            run_dir=results_root / run_id,
            config=config_obj,
            metrics=metrics_obj,
            log_lines=log_lines,
            image_ids=image_ids_val,
            y_true=y_val,
            y_pred=y_pred,
            proba=proba,
        )

    # 5. Tính permutation importance theo khối cho cả 3 mô hình (original, lung_only, outside_only) khi score=True
    if score:
        perm_dfs: List[pd.DataFrame] = []
        for m_name in MASK_MODES:
            sc_m, clf_m, _, _ = trained_models[m_name]
            imp_m = compute_block_permutation_importance(
                model=clf_m,
                scaler=sc_m,
                X_val_raw=X_val_modes[m_name],
                y_val=y_val,
                n_repeats=perm_repeats,
                rng_seed=FROZEN_SEED,
            )
            imp_m.insert(0, "mask_mode", m_name)
            perm_dfs.append(imp_m)
        all_perm_df = pd.concat(perm_dfs, axis=0, ignore_index=True)
        all_perm_df.to_csv(results_root / "rq3_permutation_importance.csv", index=False)

    summary_out: Dict[str, Any] = {
        "rq": RQ_NAME,
        "mode": mode,
        "commit": commit,
        "features": FROZEN_FEATURES,
        "classifier": FROZEN_CLASSIFIER,
        "seed": FROZEN_SEED,
        "mask_modes": list(MASK_MODES),
        "scored": bool(score),
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "extract_cpu_seconds": {
            "train": extract_cpu_train_map,
            "val": extract_cpu_val_map,
        },
        "fit_cpu_seconds": fit_cpu_by_mode,
        "visual_mask_check": {
            "total_visual_samples": mask_summary["total_visual_samples"],
            "all_centered": mask_summary["all_centered"],
            "lung_fraction_mean": mask_summary["lung_fraction_mean"],
        },
        "runs": runs_executed,
    }

    summary_path = out_path / f"summary_rq3_{mode}.json"
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary_out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return summary_out


def build_rq3_code_package(
    repo_root: Union[str, Path],
    out_dir: Union[str, Path],
    commit: str,
    mode: str,
    dataset_id: str = "ductrannguyen/cxr-rq3-code",
) -> List[str]:
    """Đóng gói mã nguồn và split_v1.csv để đẩy lên Kaggle Dataset cho thực nghiệm RQ3."""
    if mode not in ("t0", "full"):
        raise ValueError(f"Mode '{mode}' không hợp lệ. Chỉ hỗ trợ ('t0', 'full').")

    repo_path = Path(repo_root)
    out_path = Path(out_dir)
    if out_path.exists() and any(out_path.iterdir()):
        raise ValueError(f"Thư mục '{out_dir}' đã tồn tại và không rỗng.")

    out_path.mkdir(parents=True, exist_ok=True)
    src_out = out_path / "src"
    src_out.mkdir(parents=True, exist_ok=True)

    for fname in PACKAGE_SRC_FILES:
        src_file = repo_path / "src" / fname
        if not src_file.is_file():
            raise FileNotFoundError(f"Thiếu tệp nguồn: {src_file}")
        shutil.copyfile(src_file, src_out / fname)
        shutil.copyfile(src_file, out_path / fname)

    for fname in PACKAGE_SPLIT_FILES:
        sp_file = repo_path / "splits" / fname
        if not sp_file.is_file():
            raise FileNotFoundError(f"Thiếu tệp split: {sp_file}")
        shutil.copyfile(sp_file, out_path / fname)

    sha_str = (repo_path / "splits" / "split_v1.sha256").read_text(encoding="utf-8").strip().split()[0]
    (out_path / "EXPECTED_SHA256").write_text(sha_str + "\n", encoding="utf-8", newline="\n")
    (out_path / "COMMIT").write_text(commit.strip() + "\n", encoding="utf-8", newline="\n")
    (out_path / "MODE").write_text(mode.strip() + "\n", encoding="utf-8", newline="\n")

    metadata = {
        "title": dataset_id.split("/")[-1],
        "id": dataset_id,
        "licenses": [{"name": "other"}],
    }
    with open(out_path / "dataset-metadata.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return sorted(p.name for p in out_path.iterdir())


def find_rq3_code_package(input_root: Union[str, Path]) -> Path:
    """Tìm gói mã nguồn RQ3 trên Kaggle qua tệp COMMIT."""
    input_path = Path(input_root)
    for pat in ("COMMIT", "*/COMMIT", "*/*/COMMIT", "*/*/*/COMMIT"):
        matches = sorted(input_path.glob(pat))
        if matches:
            return matches[0].parent
    raise FileNotFoundError(f"Không tìm thấy tệp COMMIT trong {input_root}")


def kaggle_main(
    input_root: Union[str, Path] = "/kaggle/input",
    working_dir: Union[str, Path] = "/kaggle/working",
    mode: Optional[str] = None,
    expected_split_sha256: Optional[str] = None,
) -> Dict[str, Any]:
    """Hàm điểm vào chính khi chạy trên Kaggle CPU cho S4-07 & RQ3."""
    versions = collect_versions()
    print("Phiên bản thư viện trên môi trường chạy:")
    for k, v in versions.items():
        print(f"  {k}: {v}")

    input_path = Path(input_root)
    working_path = Path(working_dir)
    pkg_dir = find_rq3_code_package(input_path)
    ds_root = find_data_root(input_path)

    commit = (pkg_dir / "COMMIT").read_text(encoding="utf-8").strip()
    run_mode = mode if mode is not None else (pkg_dir / "MODE").read_text(encoding="utf-8").strip()
    settings = mode_settings(run_mode)

    if expected_split_sha256 is None and (pkg_dir / "EXPECTED_SHA256").is_file():
        expected_split_sha256 = (pkg_dir / "EXPECTED_SHA256").read_text(encoding="utf-8").strip()

    summary = run_rq3_experiment(
        dataset_root=ds_root,
        split_csv=pkg_dir / "split_v1.csv",
        out_dir=working_path,
        mode=run_mode,
        score=bool(settings["score"]),
        limit_train=settings["limit_train"],
        limit_val=settings["limit_val"],
        subset_seed=settings["subset_seed"],
        samples_per_class_visual=settings["samples_per_class_visual"],
        perm_repeats=settings["perm_repeats"],
        commit=commit,
        expected_split_sha256=expected_split_sha256,
    )
    print(f"Hoàn tất chạy RQ3 mode={run_mode}: {summary['runs']}")
    return summary
