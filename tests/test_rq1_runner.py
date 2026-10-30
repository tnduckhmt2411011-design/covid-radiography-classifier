"""Kiểm thử đơn vị cho module rq1_runner (S3-04).

Bao gồm 16 kiểm thử T1 đến T16 xác thực toàn diện các hàm chức năng, quy ước kết quả,
xử lý lỗi ngoại lệ và quy trình điều phối chạy thực nghiệm trên dữ liệu giả lập.
"""

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from typing import List

import numpy as np
import pandas as pd
from PIL import Image
import pytest
import yaml

from src.bootstrap import macro_f1_from_labels
from src.dataset import LABEL_TO_IDX
from src.features_hog_ghep import GROUP_NAMES
from src.rq1_runner import (
    CLASS_WEIGHT,
    EXPECTED_TRAIN_N,
    EXPECTED_VAL_N,
    EXPECTED_VERSIONS,
    FEATURE_GROUPS,
    N_ESTIMATORS,
    PACKAGE_SPLIT_FILES,
    PACKAGE_SRC_FILES,
    SEEDS,
    build_code_package,
    check_pinned_versions,
    collect_versions,
    feature_params,
    find_code_package,
    find_data_root,
    kaggle_main,
    load_split_images,
    make_run_id,
    mode_settings,
    run_experiment,
    run_one,
    stratified_subset,
    train_and_predict,
    verify_split_sha256,
    write_run_outputs,
)


def make_synthetic_dataset(tmp_path: Path) -> pd.DataFrame:
    """Tạo bộ dữ liệu giả lập phục vụ kiểm thử đơn vị.

    Dựng thư mục <tmp>/data/<lớp>/images/<tên>.png với 4 lớp:
    'COVID', 'Lung_Opacity', 'Normal', 'Viral Pneumonia'. Mỗi lớp có 6 ảnh train,
    3 ảnh val (ảnh xám uint8 40x40, phân bố ngẫu nhiên [40+50*c, 70+50*c)),
    và 1 hàng split 'test' có rel_image_path trỏ tới tệp không tồn tại.
    """
    rng = np.random.default_rng(12345)
    rows: List[dict] = []
    classes = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    data_dir = tmp_path / "data"

    for c, cls_name in enumerate(classes):
        cls_img_dir = data_dir / cls_name / "images"
        cls_img_dir.mkdir(parents=True, exist_ok=True)

        # 6 ảnh train
        for i in range(6):
            img_id = f"{cls_name}_train_{i}"
            file_name = f"{img_id}.png"
            file_path = cls_img_dir / file_name
            arr = rng.integers(
                40 + 50 * c, 70 + 50 * c, size=(40, 40), dtype=np.uint8
            )
            Image.fromarray(arr).save(file_path)
            rows.append(
                {
                    "image_id": img_id,
                    "label": cls_name,
                    "rel_image_path": f"{cls_name}/images/{file_name}",
                    "split": "train",
                }
            )

        # 3 ảnh val
        for i in range(3):
            img_id = f"{cls_name}_val_{i}"
            file_name = f"{img_id}.png"
            file_path = cls_img_dir / file_name
            arr = rng.integers(
                40 + 50 * c, 70 + 50 * c, size=(40, 40), dtype=np.uint8
            )
            Image.fromarray(arr).save(file_path)
            rows.append(
                {
                    "image_id": img_id,
                    "label": cls_name,
                    "rel_image_path": f"{cls_name}/images/{file_name}",
                    "split": "val",
                }
            )

        # 1 hàng test trỏ tới tệp không tồn tại
        img_id = f"{cls_name}_test_0"
        file_name = f"{img_id}_khong_ton_tai.png"
        rows.append(
            {
                "image_id": img_id,
                "label": cls_name,
                "rel_image_path": f"{cls_name}/images/{file_name}",
                "split": "test",
            }
        )

    return pd.DataFrame(rows, columns=["image_id", "label", "rel_image_path", "split"])


def test_t1_make_run_id():
    """T1: Kiểm tra hàm make_run_id sinh đúng định danh run_id và báo lỗi khi tham số sai."""
    assert make_run_id("hog", 44) == "rq1_hog_rf_s44"
    assert make_run_id("hist", 42) == "rq1_hist_rf_s42"

    with pytest.raises(ValueError):
        make_run_id("xyz", 42)
    with pytest.raises(ValueError):
        make_run_id("hog", -1)
    with pytest.raises(ValueError):
        make_run_id("hog", 4.5)  # type: ignore
    with pytest.raises(ValueError):
        make_run_id("hog", True)  # type: ignore


def test_t2_stratified_subset():
    """T2: Kiểm tra phân tầng theo nhãn stratified_subset khớp đáp án tính tay."""
    labels = ["a"] * 60 + ["b"] * 30 + ["c"] * 100 + ["d"] * 10
    n = 40
    seed = 0

    idx = stratified_subset(labels, n, seed)
    assert len(idx) == 43

    chosen_labels = [labels[i] for i in idx]
    counts = Counter(chosen_labels)
    assert counts == {"a": 12, "b": 6, "c": 20, "d": 5}

    assert np.all(np.diff(idx) > 0)

    idx_same = stratified_subset(labels, n, seed)
    np.testing.assert_array_equal(idx, idx_same)

    idx_diff = stratified_subset(labels, n, seed=1)
    assert not np.array_equal(idx, idx_diff)

    idx_all = stratified_subset(labels, 1000, seed)
    assert len(idx_all) == 200
    np.testing.assert_array_equal(idx_all, np.arange(200, dtype=np.int64))

    with pytest.raises(ValueError):
        stratified_subset(labels, 0, seed)


def test_t3_verify_split_sha256(tmp_path: Path):
    """T3: Kiểm tra xác thực mã băm SHA256 trả đúng mã khi khớp và ném ValueError khi sai."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("image_id,label\n1,COVID\n", encoding="utf-8")
    expected_hash = hashlib.sha256(csv_file.read_bytes()).hexdigest().lower()

    sha_file = tmp_path / "test.sha256"
    sha_file.write_text(f"{expected_hash}  split_v1.csv\n", encoding="utf-8")

    result = verify_split_sha256(csv_file, sha_file)
    assert result == expected_hash

    sha_file.write_text(f"{'0' * 64}  split_v1.csv\n", encoding="utf-8")
    with pytest.raises(ValueError):
        verify_split_sha256(csv_file, sha_file)


def test_t4_load_split_images(tmp_path: Path):
    """T4: Kiểm tra load_split_images trả đúng generator ảnh, danh sách ID và nhãn; chặn split test."""
    df = make_synthetic_dataset(tmp_path)
    data_root = tmp_path / "data"

    gen, image_ids, y = load_split_images(df, "val", data_root)
    val_df = df[df["split"] == "val"].reset_index(drop=True)

    assert image_ids == val_df["image_id"].tolist()
    expected_y = val_df["label"].map(LABEL_TO_IDX).to_numpy(dtype=np.int64)
    np.testing.assert_array_equal(y, expected_y)

    images = list(gen)
    assert len(images) == 12
    for img in images:
        assert isinstance(img, np.ndarray)
        assert img.dtype == np.uint8
        assert img.shape == (40, 40)

    with pytest.raises(ValueError):
        load_split_images(df, "test", data_root)
    with pytest.raises(ValueError):
        load_split_images(df, "xyz", data_root)


def test_t5_versions_and_pinned_check():
    """T5: Kiểm tra thu thập phiên bản thư viện và phát hiện sai lệch so với EXPECTED_VERSIONS."""
    versions = collect_versions()
    expected_keys = {
        "python",
        "numpy",
        "pandas",
        "scikit-learn",
        "scikit-image",
        "opencv-python-headless",
        "pyyaml",
        "pillow",
    }
    assert expected_keys.issubset(versions.keys())
    assert versions["numpy"] == np.__version__

    assert check_pinned_versions(dict(EXPECTED_VERSIONS)) == []

    mismatched = dict(EXPECTED_VERSIONS)
    mismatched["numpy"] = "0.0.0"
    res1 = check_pinned_versions(mismatched)
    assert len(res1) == 1
    assert "numpy" in res1[0]

    missing = dict(EXPECTED_VERSIONS)
    del missing["scikit-learn"]
    res2 = check_pinned_versions(missing)
    assert len(res2) == 1
    assert "scikit-learn" in res2[0]


def test_t6_feature_params():
    """T6: Kiểm tra feature_params trả đúng cấu trúc tham số từng nhóm và tương thích YAML."""
    hog_p = feature_params("hog")
    assert hog_p == {
        "orientations": 9,
        "pixels_per_cell": [16, 16],
        "cells_per_block": [2, 2],
        "block_norm": "L2-Hys",
    }

    hist_p = feature_params("hist")
    assert hist_p["bins"] == 64

    glcmlbp_p = feature_params("glcmlbp")
    assert list(glcmlbp_p.keys()) == ["glcm", "lbp"]
    assert glcmlbp_p["glcm"]["distances"] == [1, 3, 5]
    assert len(glcmlbp_p["glcm"]["angles"]) == 4

    ghep_p = feature_params("ghep")
    assert list(ghep_p.keys()) == ["hist", "glcm", "lbp"]

    with pytest.raises(ValueError):
        feature_params("xyz")

    for grp in ("hist", "glcmlbp", "hog", "ghep"):
        dumped = yaml.safe_dump(feature_params(grp))
        assert isinstance(dumped, str)


def test_t7_train_and_predict():
    """T7: Kiểm tra train_and_predict với dữ liệu phân tách rõ rệt đạt dự đoán chính xác và đo thời gian."""
    rng = np.random.default_rng(42)
    # X_train 4 lớp x 30 mẫu = 120 mẫu, 8 chiều
    x_train_list, y_train_list = [], []
    for c in range(4):
        x_c = rng.normal(loc=10.0 * c, scale=1.0, size=(30, 8))
        x_train_list.append(x_c)
        y_train_list.append(np.full(30, c, dtype=np.int64))
    x_train = np.vstack(x_train_list)
    y_train = np.concatenate(y_train_list)

    # X_val 4 lớp x 10 mẫu = 40 mẫu, 8 chiều
    x_val_list, y_val_list = [], []
    for c in range(4):
        x_c = rng.normal(loc=10.0 * c, scale=1.0, size=(10, 8))
        x_val_list.append(x_c)
        y_val_list.append(np.full(10, c, dtype=np.int64))
    x_val = np.vstack(x_val_list)
    y_val = np.concatenate(y_val_list)

    res = train_and_predict(x_train, y_train, x_val, seed=42, n_estimators=10)
    np.testing.assert_array_equal(res["y_pred"], y_val)
    assert res["proba"].shape == (40, 4)
    np.testing.assert_allclose(np.sum(res["proba"], axis=1), 1.0, atol=1e-9)

    params = res["params"]
    assert params["n_estimators"] == 10
    assert params["class_weight"] == "balanced_subsample"
    assert params["random_state"] == 42

    assert isinstance(res["fit_cpu_seconds"], float) and res["fit_cpu_seconds"] >= 0.0
    assert isinstance(res["fit_wall_seconds"], float) and res["fit_wall_seconds"] >= 0.0
    assert isinstance(res["predict_wall_seconds"], float) and res["predict_wall_seconds"] >= 0.0

    # y_train thiếu lớp 3 thì ValueError
    mask_no_3 = y_train != 3
    with pytest.raises(ValueError):
        train_and_predict(
            x_train[mask_no_3], y_train[mask_no_3], x_val, seed=42, n_estimators=10
        )


def test_t8_write_run_outputs(tmp_path: Path):
    """T8: Kiểm tra ghi đúng 4 tệp định dạng chuẩn UTF-8 LF và phát hiện lỗi lệch kích thước."""
    run_dir = tmp_path / "run_out"
    config = {"run_id": "test_run", "seed": 42}
    metrics = {"accuracy": 1.0, "macro_f1": 1.0}
    log_lines = ["Dòng 1", "Dòng 2", "Dòng 3"]
    image_ids = [f"img_{i}" for i in range(5)]
    y_true = np.array([0, 1, 2, 3, 0], dtype=np.int64)
    y_pred = np.array([0, 1, 2, 3, 0], dtype=np.int64)
    proba = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.7, 0.1, 0.1, 0.1],
        ],
        dtype=np.float64,
    )

    out_paths = write_run_outputs(
        run_dir, config, metrics, log_lines, image_ids, y_true, y_pred, proba
    )

    file_names = sorted(p.name for p in run_dir.iterdir())
    assert file_names == ["config.yaml", "log", "metrics.json", "preds_val.csv"]

    preds_df = pd.read_csv(out_paths["preds_val.csv"])
    expected_cols = [
        "image_id",
        "y_true",
        "y_pred",
        "proba_COVID",
        "proba_Lung_Opacity",
        "proba_Normal",
        "proba_Viral_Pneumonia",
    ]
    assert list(preds_df.columns) == expected_cols
    np.testing.assert_array_equal(preds_df["y_pred"].to_numpy(), y_pred)
    proba_cols = expected_cols[3:]
    np.testing.assert_allclose(preds_df[proba_cols].sum(axis=1), 1.0, atol=1e-6)

    with open(out_paths["config.yaml"], encoding="utf-8") as f:
        loaded_config = yaml.safe_load(f)
    assert loaded_config == config

    with open(out_paths["metrics.json"], encoding="utf-8") as f:
        loaded_metrics = json.load(f)
    assert loaded_metrics == metrics

    log_content = out_paths["log"].read_text(encoding="utf-8").splitlines()
    assert log_content == log_lines

    for p in out_paths.values():
        raw_bytes = p.read_bytes()
        assert b"\r" not in raw_bytes

    # Lỗi lệch độ dài
    with pytest.raises(ValueError):
        write_run_outputs(
            run_dir, config, metrics, log_lines, image_ids, y_true, y_pred[:4], proba
        )


def test_t9_run_one_scored(tmp_path: Path):
    """T9: Kiểm tra run_one ở chế độ score=True ghi đủ 4 tệp và tính toán đầy đủ các chỉ số."""
    rng = np.random.default_rng(42)
    x_tr = np.vstack(
        [rng.normal(loc=10.0 * c, scale=1.0, size=(30, 8)) for c in range(4)]
    )
    y_tr = np.concatenate([np.full(30, c, dtype=np.int64) for c in range(4)])
    x_v = np.vstack(
        [rng.normal(loc=10.0 * c, scale=1.0, size=(10, 8)) for c in range(4)]
    )
    y_v = np.concatenate([np.full(10, c, dtype=np.int64) for c in range(4)])
    img_ids_v = [f"val_img_{i}" for i in range(40)]

    context = {
        "mode": "full",
        "commit": "c" * 40,
        "versions": collect_versions(),
        "split": {
            "file": "splits/split_v1.csv",
            "sha256": "d" * 64,
            "train_rows": 120,
            "val_rows": 40,
        },
        "subset": {
            "limit_train": None,
            "limit_val": None,
            "subset_seed": 0,
        },
        "extraction": {
            "train": {
                "n_images": 120,
                "glcm_nan_images": 0,
                "cpu_seconds": {"hist": 1.5},
            },
            "val": {
                "n_images": 40,
                "glcm_nan_images": 0,
                "cpu_seconds": {"hist": 0.5},
            },
        },
    }

    out_root = tmp_path / "out"
    metrics = run_one(
        group="hist",
        seed=42,
        x_train=x_tr,
        y_train=y_tr,
        x_val=x_v,
        y_val=y_v,
        image_ids_val=img_ids_v,
        out_root=out_root,
        context=context,
        score=True,
        n_estimators=10,
    )

    run_dir = out_root / "rq1_hist_rf_s42"
    assert run_dir.is_dir()
    files = sorted(p.name for p in run_dir.iterdir())
    assert files == ["config.yaml", "log", "metrics.json", "preds_val.csv"]

    for k in (
        "accuracy",
        "balanced_accuracy",
        "macro_f1",
        "weighted_f1",
        "macro_precision",
        "macro_recall",
        "per_class",
        "confusion_matrix",
        "run_id",
        "mode",
        "n_train",
        "n_val",
        "seconds",
    ):
        assert k in metrics

    assert metrics["run_id"] == "rq1_hist_rf_s42"
    assert metrics["mode"] == "full"
    assert metrics["n_train"] == 120
    assert metrics["n_val"] == 40
    assert metrics["seconds"]["extract_cpu_train"] == 1.5
    assert metrics["seconds"]["extract_cpu_val"] == 0.5

    preds_df = pd.read_csv(run_dir / "preds_val.csv")
    computed_macro_f1 = macro_f1_from_labels(
        preds_df["y_true"].tolist(), preds_df["y_pred"].tolist()
    )
    assert abs(metrics["macro_f1"] - computed_macro_f1) < 1e-4

    cm = metrics["confusion_matrix"]
    assert sum(sum(row) for row in cm) == 40

    with open(run_dir / "config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["run_id"] == "rq1_hist_rf_s42"
    assert cfg["seed"] == 42
    assert cfg["commit"] == "c" * 40
    assert cfg["features"] == "hist"
    assert cfg["classifier"] == "RandomForestClassifier"
    assert cfg["hyperparameters"]["n_estimators"] == 10
    assert cfg["hyperparameters"]["class_weight"] == "balanced_subsample"
    assert cfg["split"]["sha256"] == "d" * 64
    assert cfg["evaluation"] == {
        "train_split": "train",
        "eval_split": "val",
        "allow_test": False,
    }
    assert cfg["feature_params"] == feature_params("hist")


def test_t10_run_one_unscored(tmp_path: Path):
    """T10: Kiểm tra run_one ở chế độ score=False (thử nghiệm t0) không tính toán hay rò rỉ macro_f1."""
    rng = np.random.default_rng(42)
    x_tr = np.vstack(
        [rng.normal(loc=10.0 * c, scale=1.0, size=(30, 8)) for c in range(4)]
    )
    y_tr = np.concatenate([np.full(30, c, dtype=np.int64) for c in range(4)])
    x_v = np.vstack(
        [rng.normal(loc=10.0 * c, scale=1.0, size=(10, 8)) for c in range(4)]
    )
    y_v = np.concatenate([np.full(10, c, dtype=np.int64) for c in range(4)])
    img_ids_v = [f"val_img_{i}" for i in range(40)]

    context = {
        "mode": "t0",
        "commit": "c" * 40,
        "versions": collect_versions(),
        "split": {
            "file": "splits/split_v1.csv",
            "sha256": "d" * 64,
            "train_rows": 120,
            "val_rows": 40,
        },
        "subset": {
            "limit_train": 400,
            "limit_val": 100,
            "subset_seed": 0,
        },
        "extraction": {
            "train": {
                "n_images": 120,
                "glcm_nan_images": 0,
                "cpu_seconds": {"hist": 1.5},
            },
            "val": {
                "n_images": 40,
                "glcm_nan_images": 0,
                "cpu_seconds": {"hist": 0.5},
            },
        },
    }

    out_root = tmp_path / "out"
    metrics = run_one(
        group="hist",
        seed=42,
        x_train=x_tr,
        y_train=y_tr,
        x_val=x_v,
        y_val=y_v,
        image_ids_val=img_ids_v,
        out_root=out_root,
        context=context,
        score=False,
        n_estimators=10,
    )

    expected_order = [
        "run_id",
        "mode",
        "scored",
        "n_train",
        "n_val",
        "classes_in_val",
        "proba_row_sum_min",
        "proba_row_sum_max",
        "seconds",
    ]
    assert list(metrics.keys()) == expected_order
    assert metrics["run_id"] == "rq1_hist_rf_s42"
    assert metrics["mode"] == "t0"
    assert metrics["scored"] is False
    assert metrics["classes_in_val"] == [0, 1, 2, 3]

    for forbidden in (
        "macro_f1",
        "accuracy",
        "balanced_accuracy",
        "weighted_f1",
        "per_class",
        "confusion_matrix",
    ):
        assert forbidden not in metrics

    assert abs(metrics["proba_row_sum_min"] - 1.0) < 1e-6
    assert abs(metrics["proba_row_sum_max"] - 1.0) < 1e-6


def test_t11_run_experiment_end_to_end(tmp_path: Path):
    """T11: Kiểm tra chạy thực nghiệm hoàn chỉnh end-to-end, không đụng tập test và xuất đủ 11 khóa summary."""
    df = make_synthetic_dataset(tmp_path)
    split_csv = tmp_path / "split_v1.csv"
    df.to_csv(split_csv, index=False, lineterminator="\n")

    data_root = tmp_path / "data"
    out_root = tmp_path / "out_results"

    mode_config = {
        "limit_train": None,
        "limit_val": None,
        "subset_seed": 0,
        "groups": FEATURE_GROUPS,
        "seeds": (42, 43),
        "score": True,
        "out_subdir": "results",
    }

    summary = run_experiment(
        split_csv=split_csv,
        data_root=data_root,
        out_root=out_root,
        mode="full",
        mode_config=mode_config,
        commit="e" * 40,
        versions=collect_versions(),
        n_estimators=10,
        expected_train_n=24,
        expected_val_n=12,
    )

    run_dirs = sorted(p.name for p in out_root.iterdir() if p.is_dir())
    expected_runs = [make_run_id(g, s) for g in FEATURE_GROUPS for s in (42, 43)]
    assert run_dirs == sorted(expected_runs)

    val_df = df[df["split"] == "val"].reset_index(drop=True)
    expected_image_ids = val_df["image_id"].tolist()
    expected_y_true = val_df["label"].map(LABEL_TO_IDX).tolist()

    for r_id in run_dirs:
        r_path = out_root / r_id
        assert sorted(p.name for p in r_path.iterdir()) == [
            "config.yaml",
            "log",
            "metrics.json",
            "preds_val.csv",
        ]
        preds = pd.read_csv(r_path / "preds_val.csv")
        assert len(preds) == 12
        assert preds["image_id"].tolist() == expected_image_ids
        assert preds["y_true"].tolist() == expected_y_true

        with open(r_path / "metrics.json", encoding="utf-8") as f:
            m = json.load(f)
        assert "macro_f1" in m

    expected_summary_keys = [
        "mode",
        "commit",
        "groups",
        "seeds",
        "scored",
        "n_train",
        "n_val",
        "extract_cpu_seconds",
        "extract_cpu_seconds_per_image",
        "cost_rank",
        "runs",
    ]
    assert list(summary.keys()) == expected_summary_keys
    assert summary["mode"] == "full"
    assert summary["commit"] == "e" * 40
    assert summary["groups"] == list(FEATURE_GROUPS)
    assert summary["seeds"] == [42, 43]
    assert summary["scored"] is True
    assert summary["n_train"] == 24
    assert summary["n_val"] == 12
    assert len(summary["runs"]) == 8
    assert sorted(summary["cost_rank"]) == sorted(FEATURE_GROUPS)

    for g in FEATURE_GROUPS:
        cost = summary["extract_cpu_seconds_per_image"][g]
        assert isinstance(cost, float) and cost >= 0.0


def test_t12_run_experiment_validation(tmp_path: Path):
    """T12: Kiểm tra kiểm thực đầu vào của run_experiment ném lỗi trước khi đọc ảnh."""
    df = pd.DataFrame(
        {
            "image_id": [f"img_{i}" for i in range(10)],
            "label": ["Normal"] * 10,
            "rel_image_path": [f"Normal/img_{i}.png" for i in range(10)],
            "split": ["train"] * 7 + ["val"] * 3,
        }
    )
    csv_file = tmp_path / "split_test.csv"
    df.to_csv(csv_file, index=False, lineterminator="\n")

    nonexistent_data = tmp_path / "nonexistent_dir"
    out_root = tmp_path / "out"
    mode_config = mode_settings("t0")

    with pytest.raises(ValueError):
        run_experiment(
            csv_file,
            nonexistent_data,
            out_root,
            "t0",
            mode_config,
            "a" * 40,
            {},
            expected_train_n=999,
            expected_val_n=3,
        )

    with pytest.raises(ValueError):
        run_experiment(
            csv_file,
            nonexistent_data,
            out_root,
            "t0",
            mode_config,
            "a" * 40,
            {},
            expected_train_n=7,
            expected_val_n=999,
        )

    bad_sha = tmp_path / "bad.sha256"
    bad_sha.write_text("0" * 64 + "  split.csv\n", encoding="utf-8")
    with pytest.raises(ValueError):
        run_experiment(
            csv_file,
            nonexistent_data,
            out_root,
            "t0",
            mode_config,
            "a" * 40,
            {},
            sha_path=bad_sha,
            expected_train_n=7,
            expected_val_n=3,
        )

    no_split_csv = tmp_path / "no_split.csv"
    df.drop(columns=["split"]).to_csv(
        no_split_csv, index=False, lineterminator="\n"
    )
    with pytest.raises(ValueError):
        run_experiment(
            no_split_csv,
            nonexistent_data,
            out_root,
            "t0",
            mode_config,
            "a" * 40,
            {},
            expected_train_n=None,
            expected_val_n=None,
        )


def test_t13_constants_and_script_sync():
    """T13: Kiểm tra tính nhất quán của hằng số runner với configs/base.yaml và script Kaggle."""
    assert N_ESTIMATORS == 500
    assert CLASS_WEIGHT == "balanced_subsample"
    assert SEEDS == (42, 43, 44)
    assert FEATURE_GROUPS == GROUP_NAMES
    assert EXPECTED_TRAIN_N == 14815
    assert EXPECTED_VAL_N == 3174

    repo_root = Path(__file__).resolve().parent.parent
    with open(repo_root / "configs/base.yaml", encoding="utf-8") as f:
        base_cfg = yaml.safe_load(f)
    assert base_cfg["seeds"] == [42, 43, 44]

    script_path = repo_root / "kaggle/rq1_rf/run_rq1_rf.py"
    spec = importlib.util.spec_from_file_location("kaggle_run_rq1_rf", script_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod.SRC_FILES == PACKAGE_SRC_FILES
    assert mod.SPLIT_FILES == PACKAGE_SPLIT_FILES


def test_t14_build_code_package(tmp_path: Path):
    """T14: Kiểm tra build_code_package đóng gói đúng 10 tệp phẳng và xử lý ngoại lệ chính xác."""
    mock_repo = tmp_path / "mock_repo"
    src_dir = mock_repo / "src"
    splits_dir = mock_repo / "splits"
    src_dir.mkdir(parents=True)
    splits_dir.mkdir(parents=True)

    for name in PACKAGE_SRC_FILES:
        (src_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    split_csv_content = "a,b\n1,2\n"
    (splits_dir / "split_v1.csv").write_text(split_csv_content, encoding="utf-8")
    (splits_dir / "split_v1.sha256").write_text(
        "some_hash  split_v1.csv\n", encoding="utf-8"
    )

    out_dir = tmp_path / "pkg_out"
    commit = "f" * 40
    res = build_code_package(mock_repo, out_dir, commit, "t1")

    expected_files = sorted(
        [
            "COMMIT",
            "MODE",
            "dataset-metadata.json",
            "dataset.py",
            "features_hist_glcm_lbp.py",
            "features_hog_ghep.py",
            "metrics.py",
            "rq1_runner.py",
            "split_v1.csv",
            "split_v1.sha256",
        ]
    )
    assert res == expected_files
    actual_files = sorted(p.name for p in out_dir.iterdir())
    assert actual_files == expected_files
    for p in out_dir.iterdir():
        assert p.is_file()

    assert (out_dir / "COMMIT").read_text(encoding="utf-8") == "f" * 40 + "\n"
    assert (out_dir / "MODE").read_text(encoding="utf-8") == "t1\n"
    assert (
        (out_dir / "split_v1.csv").read_bytes()
        == (splits_dir / "split_v1.csv").read_bytes()
    )

    with open(out_dir / "dataset-metadata.json", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta == {
        "title": "cxr-rq1-code",
        "id": "ductrannguyen/cxr-rq1-code",
        "licenses": [{"name": "other"}],
    }

    with pytest.raises(ValueError):
        build_code_package(mock_repo, tmp_path / "out2", "abc", "t1")

    with pytest.raises(ValueError):
        build_code_package(mock_repo, tmp_path / "out3", commit, "xyz")

    with pytest.raises(ValueError):
        build_code_package(mock_repo, out_dir, commit, "t1")

    (src_dir / "metrics.py").unlink()
    with pytest.raises(FileNotFoundError):
        build_code_package(mock_repo, tmp_path / "out4", commit, "t1")


def test_t15_mode_settings():
    """T15: Kiểm tra mode_settings trả đúng giá trị và thứ tự khoá cho t0, t1, full."""
    expected_keys = [
        "limit_train",
        "limit_val",
        "subset_seed",
        "groups",
        "seeds",
        "score",
        "out_subdir",
    ]

    t0 = mode_settings("t0")
    assert list(t0.keys()) == expected_keys
    assert t0 == {
        "limit_train": 400,
        "limit_val": 100,
        "subset_seed": 0,
        "groups": FEATURE_GROUPS,
        "seeds": (42,),
        "score": False,
        "out_subdir": "results_trial",
    }

    t1 = mode_settings("t1")
    assert list(t1.keys()) == expected_keys
    assert t1 == {
        "limit_train": None,
        "limit_val": None,
        "subset_seed": 0,
        "groups": ("hog",),
        "seeds": (42,),
        "score": False,
        "out_subdir": "results_trial",
    }

    full = mode_settings("full")
    assert list(full.keys()) == expected_keys
    assert full == {
        "limit_train": None,
        "limit_val": None,
        "subset_seed": 0,
        "groups": FEATURE_GROUPS,
        "seeds": SEEDS,
        "score": True,
        "out_subdir": "results",
    }

    with pytest.raises(ValueError):
        mode_settings("xyz")


def test_t16_kaggle_main_and_search_helpers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """T16: Kiểm tra find_data_root, find_code_package và kaggle_main chạy đúng trên môi trường giả lập Kaggle."""
    input_dir = tmp_path / "input"
    working_dir = tmp_path / "working"
    input_dir.mkdir()
    working_dir.mkdir()

    data_synth = tmp_path / "synth"
    df = make_synthetic_dataset(data_synth)

    data_dest = (
        input_dir
        / "datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset"
    )
    shutil.copytree(data_synth / "data", data_dest)

    pkg_dest = input_dir / "datasets/ductrannguyen/cxr-rq1-code"
    pkg_dest.mkdir(parents=True)
    split_csv_path = pkg_dest / "split_v1.csv"
    df.to_csv(split_csv_path, index=False, lineterminator="\n")
    actual_csv_sha = hashlib.sha256(split_csv_path.read_bytes()).hexdigest().lower()
    (pkg_dest / "split_v1.sha256").write_text(
        f"{actual_csv_sha}  split_v1.csv\n", encoding="utf-8"
    )
    (pkg_dest / "COMMIT").write_text("a" * 40 + "\n", encoding="utf-8")
    (pkg_dest / "MODE").write_text("t0\n", encoding="utf-8")

    assert find_data_root(input_dir) == data_dest
    assert find_code_package(input_dir) == pkg_dest

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        find_data_root(empty_dir)
    with pytest.raises(FileNotFoundError):
        find_code_package(empty_dir)

    nested_dir = tmp_path / "nested_input"
    nested_target = nested_dir / "lung/x/COVID-19_Radiography_Dataset"
    (nested_target / "COVID/images").mkdir(parents=True)
    assert find_data_root(nested_dir) == nested_target

    monkeypatch.setattr(
        "src.rq1_runner.collect_versions",
        lambda: {**EXPECTED_VERSIONS, "python": "3.12.0"},
    )

    summary = kaggle_main(
        input_root=input_dir,
        working_root=working_dir,
        n_estimators=10,
        expected_train_n=24,
        expected_val_n=12,
    )

    trial_dir = working_dir / "results_trial"
    assert trial_dir.is_dir()
    run_folders = sorted(p.name for p in trial_dir.iterdir() if p.is_dir())
    expected_run_folders = [f"rq1_{g}_rf_s42" for g in FEATURE_GROUPS]
    assert run_folders == sorted(expected_run_folders)

    for r_f in run_folders:
        r_path = trial_dir / r_f
        assert sorted(p.name for p in r_path.iterdir()) == [
            "config.yaml",
            "log",
            "metrics.json",
            "preds_val.csv",
        ]
        with open(r_path / "metrics.json", encoding="utf-8") as f:
            m = json.load(f)
        assert "macro_f1" not in m
        with open(r_path / "config.yaml", encoding="utf-8") as f:
            c = yaml.safe_load(f)
        assert c["commit"] == "a" * 40
        assert c["mode"] == "t0"

    summary_file = working_dir / "summary_t0.json"
    assert summary_file.is_file()
    with open(summary_file, encoding="utf-8") as f:
        s_data = json.load(f)
    assert s_data["mode"] == "t0"
    assert s_data["n_train"] == 24
    assert s_data["n_val"] == 12

    assert not (working_dir / "results").exists()

    monkeypatch.setattr(
        "src.rq1_runner.collect_versions",
        lambda: {**EXPECTED_VERSIONS, "python": "3.12.0", "scikit-learn": "0.0.0"},
    )
    with pytest.raises(RuntimeError) as exc_info:
        kaggle_main(
            input_root=input_dir,
            working_root=working_dir,
            n_estimators=10,
            expected_train_n=24,
            expected_val_n=12,
        )
    assert "scikit-learn" in str(exc_info.value)


def test_t17_soft_version_drift_does_not_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """T17: Chỉ lệch scikit-learn hoặc scikit-image mới làm kernel dừng.

    Lý do kỳ vọng:
    - numpy, opencv-python-headless, pillow và phiên bản Python lệch so với bản ghim chỉ
      được in lưu ý; kaggle_main đi qua bước kiểm tra phiên bản rồi dừng ở bước tìm gói mã
      (FileNotFoundError vì thư mục đầu vào rỗng).
    - scikit-image lệch thì kaggle_main dừng với RuntimeError có nhắc tên gói.
    """
    input_dir = tmp_path / "input_empty"
    working_dir = tmp_path / "working_empty"
    input_dir.mkdir()
    working_dir.mkdir()

    monkeypatch.setattr(
        "src.rq1_runner.collect_versions",
        lambda: {
            **EXPECTED_VERSIONS,
            "python": "3.13.15",
            "numpy": "2.1.3",
            "opencv-python-headless": "4.14.0.94",
            "pillow": "12.3.0",
        },
    )
    with pytest.raises(FileNotFoundError):
        kaggle_main(input_dir, working_dir, n_estimators=10)

    monkeypatch.setattr(
        "src.rq1_runner.collect_versions",
        lambda: {**EXPECTED_VERSIONS, "python": "3.13.15", "scikit-image": "0.0.0"},
    )
    with pytest.raises(RuntimeError) as exc_info:
        kaggle_main(input_dir, working_dir, n_estimators=10)
    assert "scikit-image" in str(exc_info.value)
