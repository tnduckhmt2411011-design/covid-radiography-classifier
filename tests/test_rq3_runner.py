"""Bộ kiểm thử TDD cho module src/rq3_runner.py (S4-07, S5-01, S5-02)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
import pandas as pd
import pytest
import yaml

from src.metrics import DEFAULT_CLASS_NAMES
from src.rq3_runner import (
    FEATURE_BLOCKS,
    FROZEN_CLASSIFIER,
    FROZEN_FEATURES,
    FROZEN_SEED,
    FROZEN_SVM_PARAMS,
    MASK_MODES,
    apply_mask_modes,
    build_rq3_code_package,
    compute_block_permutation_importance,
    compute_mask_alignment_metrics,
    generate_visual_mask_check,
    kaggle_main,
    make_rq3_run_id,
    mode_settings,
    resize_mask_nearest,
    run_rq3_experiment,
)


def _create_synthetic_rq3_dataset(
    base_dir: Path,
    n_train_per_class: int = 10,
    n_val_per_class: int = 5,
    n_test_per_class: int = 2,
) -> Tuple[Path, Path, str]:
    """Tạo bộ dữ liệu ảnh X-quang (299x299) và mask phổi (256x256 RGB {0,255}) giả lập."""
    ds_root = base_dir / "COVID-19_Radiography_Dataset"
    splits_dir = base_dir / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(1234)
    rows = []

    for c_idx, c_name in enumerate(DEFAULT_CLASS_NAMES):
        img_dir = ds_root / c_name / "images"
        mask_dir = ds_root / c_name / "masks"
        img_dir.mkdir(parents=True, exist_ok=True)
        mask_dir.mkdir(parents=True, exist_ok=True)

        total_c = n_train_per_class + n_val_per_class + n_test_per_class
        for i in range(total_c):
            if i < n_train_per_class:
                sp = "train"
            elif i < n_train_per_class + n_val_per_class:
                sp = "val"
            else:
                sp = "test"

            img_id = f"{c_name}-{i + 1}.png"
            rel_img = f"{c_name}/images/{img_id}"
            rel_mask = f"{c_name}/masks/{img_id}"

            # Ảnh xám 299x299 có tín hiệu phân biệt lớp cả trong và ngoài phổi
            base_val = 45 + c_idx * 45
            img = rng.integers(base_val - 20, base_val + 20, size=(299, 299), dtype=np.uint8)
            cv2.imwrite(str(ds_root / rel_img), img)

            # Mask 256x256 RGB chỉ gồm {0, 255} với 2 lá phổi ở giữa ảnh
            mask_2d = np.zeros((256, 256), dtype=np.uint8)
            mask_2d[50:200, 40:115] = 255
            mask_2d[50:200, 140:215] = 255
            mask_rgb = np.stack([mask_2d, mask_2d, mask_2d], axis=-1)
            cv2.imwrite(str(ds_root / rel_mask), mask_rgb)

            group_id = f"G_{c_idx}_{i // 2:03d}"
            rows.append({
                "image_id": img_id,
                "label": c_name,
                "rel_image_path": rel_img,
                "rel_mask_path": rel_mask,
                "has_mask": True,
                "group_id": group_id,
                "split": sp,
                "file_hash": f"hash_{c_idx}_{i}",
                "phash": f"{c_idx:04x}{i:012x}",
            })

    split_csv = splits_dir / "split_v1.csv"
    pd.DataFrame(rows).to_csv(split_csv, index=False)
    sha = hashlib.sha256(split_csv.read_bytes()).hexdigest()
    return ds_root, split_csv, sha


def test_t1_constants_and_run_id() -> None:
    """T1: Kiểm tra hằng số cấu hình đóng băng RQ3 và định dạng run_id."""
    assert MASK_MODES == ("original", "lung_only", "outside_only")
    assert FROZEN_FEATURES == "ghep"
    assert FROZEN_CLASSIFIER == "svm"
    assert FROZEN_SEED == 42
    assert FROZEN_SVM_PARAMS["kernel"] == "rbf"
    assert FROZEN_SVM_PARAMS["C"] == 10.0
    assert FROZEN_SVM_PARAMS["gamma"] == "scale"
    assert FROZEN_SVM_PARAMS["class_weight"] == "balanced"
    assert make_rq3_run_id("original", "lung_only", 42) == "rq3_ghep_svm_orig_to_lung_s42"
    assert make_rq3_run_id("lung_only", "lung_only", 42) == "rq3_ghep_svm_lung_to_lung_s42"
    assert make_rq3_run_id("outside_only", "outside_only", 42) == "rq3_ghep_svm_out_to_out_s42"


def test_t2_resize_mask_nearest_and_apply_mask_modes() -> None:
    """T2: Kiểm tra nội suy gần nhất 256x256 -> 299x299 và tính chất cộng tính của 3 chế độ che."""
    mask_256 = np.zeros((256, 256, 3), dtype=np.uint8)
    mask_256[64:192, 64:192, :] = 255

    mask_bin = resize_mask_nearest(mask_256, target_hw=(299, 299))
    assert mask_bin.shape == (299, 299)
    assert mask_bin.dtype == np.bool_
    assert mask_bin[150, 150] is np.True_ or bool(mask_bin[150, 150]) is True
    assert bool(mask_bin[5, 5]) is False

    rng = np.random.default_rng(42)
    img = rng.integers(10, 250, size=(299, 299), dtype=np.uint8)
    modes = apply_mask_modes(img, mask_bin)

    assert set(modes.keys()) == {"original", "lung_only", "outside_only"}
    assert np.array_equal(modes["original"], img)
    # Tổng lung_only + outside_only phải bằng chính xác ảnh gốc tại mọi điểm ảnh
    assert np.array_equal(
        modes["lung_only"].astype(np.int32) + modes["outside_only"].astype(np.int32),
        img.astype(np.int32),
    )
    assert np.all(modes["lung_only"][~mask_bin] == 0)
    assert np.all(modes["outside_only"][mask_bin] == 0)


def test_t3_compute_mask_alignment_metrics() -> None:
    """T3: Kiểm tra các chỉ số căn chỉnh vị trí mask phổi so với ảnh X-quang (S4-07)."""
    img = np.full((299, 299), 100, dtype=np.uint8)
    mask_bin = np.zeros((299, 299), dtype=bool)
    mask_bin[60:240, 50:130] = True
    mask_bin[60:240, 170:250] = True

    metrics = compute_mask_alignment_metrics(img, mask_bin, orig_mask_shape=(256, 256))
    assert metrics["orig_h"] == 256 and metrics["orig_w"] == 256
    assert 0.25 < metrics["lung_fraction"] < 0.40
    assert metrics["is_empty"] is False
    assert metrics["is_centered"] is True
    assert abs(metrics["left_lung_fraction"] - metrics["right_lung_fraction"]) < 0.05


def test_t4_generate_visual_mask_check(tmp_path: Path) -> None:
    """T4: Kiểm tra tạo bộ ảnh kiểm tra trực quan S4-07 (lưới ảnh + CSV + JSON, không chạm test)."""
    ds_root, split_csv, _ = _create_synthetic_rq3_dataset(
        tmp_path, n_train_per_class=6, n_val_per_class=6, n_test_per_class=2
    )
    out_dir = tmp_path / "mask_check"

    summary = generate_visual_mask_check(
        dataset_root=ds_root,
        split_csv=split_csv,
        out_dir=out_dir,
        samples_per_class=5,
        seed=42,
    )
    assert summary["total_visual_samples"] == 20  # 4 classes x 5 samples
    assert summary["all_centered"] is True
    assert (out_dir / "mask_visual_check_samples.csv").is_file()
    assert (out_dir / "mask_alignment_summary.json").is_file()
    for c_name in DEFAULT_CLASS_NAMES:
        safe_name = c_name.replace(" ", "_")
        assert (out_dir / f"mask_visual_check_{safe_name}.png").is_file()


def test_t5_compute_block_permutation_importance() -> None:
    """T5: Kiểm tra tính permutation importance theo 10 khối ngữ nghĩa của đặc trưng ghep (S5-02)."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    rng = np.random.default_rng(99)
    X_train = rng.normal(0, 1, size=(80, 152))
    y_train = np.repeat([0, 1, 2, 3], 20)
    # Tiêm tín hiệu mạnh vào khối hist_64 (cột 0..63)
    for c in range(4):
        X_train[y_train == c, 0:16] += c * 3.0

    X_val = rng.normal(0, 1, size=(40, 152))
    y_val = np.repeat([0, 1, 2, 3], 10)
    for c in range(4):
        X_val[y_val == c, 0:16] += c * 3.0

    scaler = StandardScaler().fit(X_train)
    clf = SVC(**FROZEN_SVM_PARAMS)
    clf.fit(scaler.transform(X_train), y_train)

    imp_df = compute_block_permutation_importance(
        model=clf,
        scaler=scaler,
        X_val_raw=X_val,
        y_val=y_val,
        n_repeats=5,
        rng_seed=42,
    )
    assert len(imp_df) == len(FEATURE_BLOCKS)
    # Khối hist_64 phải có độ quan trọng dương cao nhất
    top_block = imp_df.sort_values("importance_mean", ascending=False).iloc[0]
    assert top_block["block_name"] == "hist_64"
    assert float(top_block["importance_mean"]) > 0.10


def test_t6_run_rq3_experiment_t0_unscored_and_full_scored(tmp_path: Path) -> None:
    """T6: Kiểm tra chạy thử t0 (score=False, mù điểm) và chạy full (score=True) của RQ3."""
    ds_root, split_csv, sha = _create_synthetic_rq3_dataset(
        tmp_path, n_train_per_class=8, n_val_per_class=4, n_test_per_class=2
    )

    # 1. Chạy t0 (score=False)
    out_t0 = tmp_path / "out_t0"
    summary_t0 = run_rq3_experiment(
        dataset_root=ds_root,
        split_csv=split_csv,
        out_dir=out_t0,
        mode="t0",
        score=False,
        limit_train=24,
        limit_val=12,
        samples_per_class_visual=3,
        perm_repeats=2,
        commit="deadbeef",
        expected_split_sha256=sha,
    )
    assert summary_t0["scored"] is False
    forbidden = re.compile(r"macro|f1|accuracy|per_class|confusion_matrix", re.IGNORECASE)
    for p in out_t0.rglob("*"):
        if p.is_file() and p.suffix in {".json", ".yaml", ".csv", ".md"} and "mask_" not in p.name:
            text = p.read_text(encoding="utf-8")
            assert not forbidden.search(text), f"Phát hiện từ khóa điểm số trong chế độ mù t0 tại {p}"

    # 2. Chạy full (score=True)
    out_full = tmp_path / "out_full"
    summary_full = run_rq3_experiment(
        dataset_root=ds_root,
        split_csv=split_csv,
        out_dir=out_full,
        mode="full",
        score=True,
        limit_train=None,
        limit_val=None,
        samples_per_class_visual=3,
        perm_repeats=3,
        commit="deadbeef",
        expected_split_sha256=sha,
    )
    assert summary_full["scored"] is True
    assert len(summary_full["runs"]) == 5
    for run_id in summary_full["runs"]:
        run_dir = out_full / "results" / run_id
        for req in ("config.yaml", "metrics.json", "log", "preds_val.csv"):
            assert (run_dir / req).is_file(), f"Thiếu {req} trong {run_id}"
        cfg = yaml.safe_load((run_dir / "config.yaml").read_text(encoding="utf-8"))
        assert cfg["evaluation"]["allow_test"] is False

    assert (out_full / "results" / "rq3_mask_check" / "mask_alignment_summary.json").is_file()
    assert (out_full / "results" / "rq3_permutation_importance.csv").is_file()


def test_t7_mode_settings_and_package_sync(tmp_path: Path) -> None:
    """T7: Kiểm tra mode_settings, build_rq3_code_package và đồng bộ script Kaggle."""
    s_t0 = mode_settings("t0")
    assert s_t0["score"] is False
    s_full = mode_settings("full")
    assert s_full["score"] is True and s_full["limit_train"] is None

    pkg_dir = tmp_path / "pkg"
    build_rq3_code_package(
        repo_root=Path(__file__).resolve().parents[1],
        out_dir=pkg_dir,
        commit="1234567890abcdef",
        mode="t0",
    )
    assert (pkg_dir / "COMMIT").read_text(encoding="utf-8").strip() == "1234567890abcdef"
    assert (pkg_dir / "MODE").read_text(encoding="utf-8").strip() == "t0"
    assert (pkg_dir / "src" / "rq3_runner.py").is_file()

    ds_root, split_csv, sha = _create_synthetic_rq3_dataset(
        tmp_path / "kag", n_train_per_class=6, n_val_per_class=4, n_test_per_class=2
    )
    (pkg_dir / "split_v1.csv").write_bytes(split_csv.read_bytes())
    (pkg_dir / "EXPECTED_SHA256").write_text(sha, encoding="utf-8")

    work_dir = tmp_path / "work"
    res = kaggle_main(
        input_root=tmp_path,
        working_dir=work_dir,
        mode="t0",
        expected_split_sha256=sha,
    )
    assert res["mode"] == "t0"
