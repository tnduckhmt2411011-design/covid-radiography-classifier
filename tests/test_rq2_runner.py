"""Kiểm thử đơn vị cho module rq2_runner (S4-03).

Xác thực toàn diện quy trình chạy thực nghiệm RQ2 trên nhóm đặc trưng 'ghep' (152 chiều)
với 6 bộ phân loại cổ điển (lr, knn, dt, rf, svm, gb), chọn siêu tham số bằng
StratifiedGroupKFold 5 fold theo group_id, xử lý trọng số lớp theo cổng H3,
chống rò rỉ chuẩn hoá theo cổng H6, và bảo đảm không lộ điểm số trong config.yaml / summary.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from typing import Dict, List

import numpy as np
import pandas as pd
from PIL import Image
import pytest
import yaml

from src.bootstrap import macro_f1_from_labels
from src.dataset import LABEL_TO_IDX
from src.rq2_runner import (
    CLASSIFIER_SPECS,
    CLASSIFIERS,
    CV_RANDOM_STATE,
    CV_SPLITS,
    DETERMINISTIC_CLASSIFIERS,
    EXPECTED_TRAIN_N,
    EXPECTED_VAL_N,
    EXPECTED_VERSIONS,
    FEATURE_GROUP,
    PACKAGE_SPLIT_FILES,
    PACKAGE_SRC_FILES,
    PARAM_GRIDS,
    SEEDS,
    STOCHASTIC_CLASSIFIERS,
    build_code_package,
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
    seeds_for_classifier,
    select_hyperparameters_cv,
    train_and_predict_classifier,
)

FORBIDDEN_SCORE_PATTERN = re.compile(
    r"macro|f1|accuracy|per_class|confusion_matrix", re.IGNORECASE
)


def make_synthetic_rq2_dataset(tmp_path: Path) -> pd.DataFrame:
    """Tạo bộ dữ liệu giả lập có cột group_id phục vụ kiểm thử RQ2 (5 fold CV).

    Mỗi lớp trong 4 lớp ('COVID', 'Lung_Opacity', 'Normal', 'Viral Pneumonia') có:
    - 10 ảnh train chia vào 5 group_id khác nhau (mỗi group 2 ảnh cùng lớp để đủ 5 fold).
    - 3 ảnh val.
    - 1 hàng split 'test' trỏ tới tệp không tồn tại để kiểm tra khoá test (cổng H2).
    """
    rng = np.random.default_rng(2026)
    rows: List[Dict[str, object]] = []
    classes = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    data_dir = tmp_path / "data"

    for c, cls_name in enumerate(classes):
        cls_img_dir = data_dir / cls_name / "images"
        cls_img_dir.mkdir(parents=True, exist_ok=True)

        # 10 ảnh train chia đều vào 5 nhóm (group_id) cho mỗi lớp -> tổng 40 ảnh train, 20 nhóm
        for i in range(10):
            img_id = f"{cls_name}_train_{i}"
            file_name = f"{img_id}.png"
            file_path = cls_img_dir / file_name
            arr = rng.integers(
                35 + 50 * c, 75 + 50 * c, size=(40, 40), dtype=np.uint8
            )
            Image.fromarray(arr).save(file_path)
            group_id = f"G_{c}_{i // 2:02d}"
            rows.append(
                {
                    "image_id": img_id,
                    "label": cls_name,
                    "rel_image_path": f"{cls_name}/images/{file_name}",
                    "group_id": group_id,
                    "split": "train",
                }
            )

        # 3 ảnh val mỗi lớp -> tổng 12 ảnh val
        for i in range(3):
            img_id = f"{cls_name}_val_{i}"
            file_name = f"{img_id}.png"
            file_path = cls_img_dir / file_name
            arr = rng.integers(
                35 + 50 * c, 75 + 50 * c, size=(40, 40), dtype=np.uint8
            )
            Image.fromarray(arr).save(file_path)
            rows.append(
                {
                    "image_id": img_id,
                    "label": cls_name,
                    "rel_image_path": f"{cls_name}/images/{file_name}",
                    "group_id": f"G_val_{c}_{i:02d}",
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
                "group_id": f"G_test_{c}",
                "split": "test",
            }
        )

    return pd.DataFrame(
        rows, columns=["image_id", "label", "rel_image_path", "group_id", "split"]
    )


def test_t1_make_run_id_and_seeds():
    """T1: Kiểm tra make_run_id và seeds_for_classifier tuân thủ quy ước đặt tên và tính tất định."""
    assert make_run_id("lr", 42) == "rq2_ghep_lr_s42"
    assert make_run_id("knn", 42) == "rq2_ghep_knn_s42"
    assert make_run_id("dt", 43) == "rq2_ghep_dt_s43"
    assert make_run_id("rf", 44) == "rq2_ghep_rf_s44"
    assert make_run_id("svm", 42) == "rq2_ghep_svm_s42"
    assert make_run_id("gb", 44) == "rq2_ghep_gb_s44"

    with pytest.raises(ValueError):
        make_run_id("xgb", 42)
    with pytest.raises(ValueError):
        make_run_id("lr", 42, features="hog")
    with pytest.raises(ValueError):
        make_run_id("lr", -1)
    with pytest.raises(ValueError):
        make_run_id("lr", 42.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        make_run_id("lr", True)  # type: ignore[arg-type]

    # Mô hình tất định chỉ chạy 1 lần với seed đầu tiên (mặc định 42)
    for clf in DETERMINISTIC_CLASSIFIERS:
        assert seeds_for_classifier(clf, (42, 43, 44)) == (42,)

    # Mô hình ngẫu nhiên chạy đủ danh sách seed truyền vào
    for clf in STOCHASTIC_CLASSIFIERS:
        assert seeds_for_classifier(clf, (42, 43, 44)) == (42, 43, 44)
        assert seeds_for_classifier(clf, (42,)) == (42,)

    with pytest.raises(ValueError):
        seeds_for_classifier("invalid", (42,))
    with pytest.raises(ValueError):
        seeds_for_classifier("rf", ())


def test_t2_classifier_specs_and_param_grids():
    """T2: Kiểm tra cấu hình 6 bộ phân loại, trọng số lớp theo cổng H3 và lưới siêu tham số."""
    assert FEATURE_GROUP == "ghep"
    assert CLASSIFIERS == ("lr", "knn", "dt", "rf", "svm", "gb")
    assert DETERMINISTIC_CLASSIFIERS == ("lr", "knn", "svm")
    assert STOCHASTIC_CLASSIFIERS == ("dt", "rf", "gb")
    assert CV_SPLITS == 5
    assert CV_RANDOM_STATE == 42

    # Kiểm tra trọng số lớp theo đúng H3 của results/threshold_v3.md
    assert CLASSIFIER_SPECS["lr"]["fixed_params"]["class_weight"] == "balanced"
    assert CLASSIFIER_SPECS["dt"]["fixed_params"]["class_weight"] == "balanced"
    assert CLASSIFIER_SPECS["svm"]["fixed_params"]["class_weight"] == "balanced"
    assert CLASSIFIER_SPECS["rf"]["fixed_params"]["class_weight"] == "balanced_subsample"
    assert CLASSIFIER_SPECS["gb"]["class_weight_mode"] == "sample_weight"
    assert CLASSIFIER_SPECS["knn"]["class_weight_mode"] == "none"
    assert "k-NN" in CLASSIFIER_SPECS["knn"]["class_weight_note"]

    # Kiểm tra scaler: lr, knn, svm dùng StandardScaler; dt, rf, gb không cần scaler
    for clf in ("lr", "knn", "svm"):
        assert CLASSIFIER_SPECS[clf]["use_scaler"] is True
        assert CLASSIFIER_SPECS[clf]["deterministic"] is True
    for clf in ("dt", "rf", "gb"):
        assert CLASSIFIER_SPECS[clf]["use_scaler"] is False
        assert CLASSIFIER_SPECS[clf]["deterministic"] is False

    for clf in CLASSIFIERS:
        grid = PARAM_GRIDS[clf]
        assert isinstance(grid, tuple) and len(grid) >= 2
        dumped = yaml.safe_dump(list(grid))
        assert isinstance(dumped, str)


def test_t3_load_split_images_with_groups(tmp_path: Path):
    """T3: Kiểm tra load_split_images trả về đúng group_ids và chặn split test."""
    df = make_synthetic_rq2_dataset(tmp_path)
    data_root = tmp_path / "data"

    gen, image_ids, y, group_ids = load_split_images(df, "train", data_root)
    train_df = df[df["split"] == "train"].reset_index(drop=True)

    assert image_ids == train_df["image_id"].tolist()
    assert group_ids == train_df["group_id"].tolist()
    expected_y = train_df["label"].map(LABEL_TO_IDX).to_numpy(dtype=np.int64)
    np.testing.assert_array_equal(y, expected_y)
    assert len(list(gen)) == 40

    with pytest.raises(ValueError):
        load_split_images(df, "test", data_root)


def test_t4_select_hyperparameters_cv_and_no_leakage():
    """T4: Kiểm tra StratifiedGroupKFold 5 fold chọn đúng siêu tham số và xử lý ngoại lệ."""
    rng = np.random.default_rng(42)
    x_list, y_list, g_list = [], [], []
    # 4 lớp x 30 mẫu = 120 mẫu, 8 chiều; mỗi lớp chia vào 5 group_id (mỗi group 6 mẫu)
    for c in range(4):
        x_c = rng.normal(loc=8.0 * c, scale=1.0, size=(30, 8))
        x_list.append(x_c)
        y_list.append(np.full(30, c, dtype=np.int64))
        for i in range(30):
            g_list.append(f"grp_{c}_{i // 6}")
    x_train = np.vstack(x_list)
    y_train = np.concatenate(y_list)

    small_grids = {
        "lr": ({"C": 0.01}, {"C": 1.0}),
        "knn": ({"n_neighbors": 3, "weights": "uniform"}, {"n_neighbors": 5, "weights": "distance"}),
        "dt": ({"max_depth": 2, "min_samples_leaf": 1}, {"max_depth": 10, "min_samples_leaf": 1}),
        "rf": ({"n_estimators": 10, "max_depth": 10}, {"n_estimators": 20, "max_depth": None}),
        "svm": ({"C": 1.0, "gamma": "scale"}, {"C": 10.0, "gamma": "scale"}),
        "gb": (
            {"n_estimators": 10, "learning_rate": 0.1, "max_depth": 2},
            {"n_estimators": 20, "learning_rate": 0.1, "max_depth": 3},
        ),
    }

    for clf in CLASSIFIERS:
        cv_res = select_hyperparameters_cv(
            classifier=clf,
            x_train=x_train,
            y_train=y_train,
            groups_train=g_list,
            param_grid=small_grids[clf],
            n_splits=5,
            cv_seed=42,
            n_jobs=1,
        )
        assert cv_res["best_params"] in small_grids[clf]
        assert cv_res["best_index"] in (0, 1)
        assert cv_res["best_score"] > 0.85
        assert len(cv_res["candidates"]) == 2
        for cand in cv_res["candidates"]:
            assert len(cand["fold_scores"]) == 5
        assert cv_res["cv_cpu_seconds"] >= 0.0
        assert cv_res["cv_wall_seconds"] >= 0.0

    # Lỗi khi thiếu lớp hoặc lệch độ dài groups_train
    with pytest.raises(ValueError):
        select_hyperparameters_cv("lr", x_train, y_train, g_list[:-1], n_jobs=1)
    mask_no_3 = y_train != 3
    with pytest.raises(ValueError):
        select_hyperparameters_cv(
            "lr",
            x_train[mask_no_3],
            y_train[mask_no_3],
            [g for g, m in zip(g_list, mask_no_3) if m],
            n_jobs=1,
        )


def test_t5_train_and_predict_all_six_classifiers():
    """T5: Kiểm tra huấn luyện và dự đoán trên cả 6 bộ phân loại đạt độ chính xác cao và xác suất hợp lệ."""
    rng = np.random.default_rng(42)
    x_tr = np.vstack([rng.normal(loc=10.0 * c, scale=1.0, size=(30, 8)) for c in range(4)])
    y_tr = np.concatenate([np.full(30, c, dtype=np.int64) for c in range(4)])
    x_v = np.vstack([rng.normal(loc=10.0 * c, scale=1.0, size=(10, 8)) for c in range(4)])
    y_v = np.concatenate([np.full(10, c, dtype=np.int64) for c in range(4)])

    test_params = {
        "lr": {"C": 1.0},
        "knn": {"n_neighbors": 5, "weights": "distance"},
        "dt": {"max_depth": 10, "min_samples_leaf": 1},
        "rf": {"n_estimators": 15, "max_depth": None},
        "svm": {"C": 1.0, "gamma": "scale"},
        "gb": {"n_estimators": 15, "learning_rate": 0.1, "max_depth": 3},
    }

    for clf in CLASSIFIERS:
        res_42 = train_and_predict_classifier(
            classifier=clf,
            x_train=x_tr,
            y_train=y_tr,
            x_val=x_v,
            seed=42,
            best_params=test_params[clf],
            n_jobs=1,
        )
        np.testing.assert_array_equal(res_42["y_pred"], y_v)
        assert res_42["proba"].shape == (40, 4)
        np.testing.assert_allclose(np.sum(res_42["proba"], axis=1), 1.0, atol=1e-6)
        assert res_42["deterministic"] is (clf in DETERMINISTIC_CLASSIFIERS)
        assert res_42["use_scaler"] is (clf in ("lr", "knn", "svm"))
        assert res_42["fit_cpu_seconds"] >= 0.0
        assert res_42["fit_wall_seconds"] >= 0.0
        assert res_42["predict_wall_seconds"] >= 0.0

        # Kiểm tra tính tất định của lr, knn, svm khi đổi seed
        if clf in DETERMINISTIC_CLASSIFIERS:
            res_43 = train_and_predict_classifier(
                classifier=clf,
                x_train=x_tr,
                y_train=y_tr,
                x_val=x_v,
                seed=43,
                best_params=test_params[clf],
                n_jobs=1,
            )
            np.testing.assert_array_equal(res_42["y_pred"], res_43["y_pred"])


def test_t6_run_one_scored_and_blind_config(tmp_path: Path):
    """T6: Kiểm tra run_one ở chế độ score=True ghi đủ 4 tệp và config.yaml không chứa từ khoá điểm số."""
    rng = np.random.default_rng(42)
    x_tr = np.vstack([rng.normal(loc=10.0 * c, scale=1.0, size=(30, 8)) for c in range(4)])
    y_tr = np.concatenate([np.full(30, c, dtype=np.int64) for c in range(4)])
    x_v = np.vstack([rng.normal(loc=10.0 * c, scale=1.0, size=(10, 8)) for c in range(4)])
    y_v = np.concatenate([np.full(10, c, dtype=np.int64) for c in range(4)])
    img_ids_v = [f"val_img_{i}" for i in range(40)]

    cv_result = {
        "n_splits": 5,
        "cv_seed": 42,
        "param_grid": [{"C": 1.0, "gamma": "scale"}, {"C": 10.0, "gamma": "scale"}],
        "best_params": {"C": 1.0, "gamma": "scale"},
        "best_index": 0,
        "best_score": 0.99,
        "best_std": 0.01,
        "candidates": [
            {
                "params": {"C": 1.0, "gamma": "scale"},
                "fold_scores": [0.99, 0.99, 0.99, 0.99, 0.99],
                "mean_score": 0.99,
                "std_score": 0.0,
            }
        ],
        "cv_cpu_seconds": 1.25,
        "cv_wall_seconds": 0.75,
    }

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
                "cpu_seconds": {"ghep": 2.5},
            },
            "val": {
                "n_images": 40,
                "glcm_nan_images": 0,
                "cpu_seconds": {"ghep": 0.8},
            },
        },
    }

    out_root = tmp_path / "out"
    metrics = run_one(
        classifier="svm",
        seed=42,
        x_train=x_tr,
        y_train=y_tr,
        x_val=x_v,
        y_val=y_v,
        image_ids_val=img_ids_v,
        cv_result=cv_result,
        out_root=out_root,
        context=context,
        score=True,
        n_jobs=1,
    )

    run_dir = out_root / "rq2_ghep_svm_s42"
    assert run_dir.is_dir()
    assert sorted(p.name for p in run_dir.iterdir()) == [
        "config.yaml",
        "log",
        "metrics.json",
        "preds_val.csv",
    ]

    assert metrics["run_id"] == "rq2_ghep_svm_s42"
    assert metrics["classifier"] == "svm"
    assert metrics["features"] == "ghep"
    assert metrics["deterministic"] is True
    assert metrics["selected_params"] == {"C": 1.0, "gamma": "scale"}
    assert metrics["cv_best_macro_f1"] == 0.99
    assert metrics["seconds"]["cv_cpu"] == 1.25

    preds_df = pd.read_csv(run_dir / "preds_val.csv")
    computed_f1 = macro_f1_from_labels(
        preds_df["y_true"].tolist(), preds_df["y_pred"].tolist()
    )
    assert abs(metrics["macro_f1"] - computed_f1) < 1e-4

    # Kiểm tra quy tắc mù điểm: config.yaml tuyệt đối KHÔNG chứa macro|f1|accuracy|per_class|confusion_matrix
    cfg_raw = (run_dir / "config.yaml").read_text(encoding="utf-8")
    assert FORBIDDEN_SCORE_PATTERN.search(cfg_raw) is None

    cfg = yaml.safe_load(cfg_raw)
    assert cfg["run_id"] == "rq2_ghep_svm_s42"
    assert cfg["rq"] == "rq2"
    assert cfg["features"] == "ghep"
    assert cfg["feature_params"] == feature_params("ghep")
    assert cfg["classifier_tag"] == "svm"
    assert cfg["classifier"] == "SVC"
    assert cfg["deterministic"] is True
    assert cfg["cv"]["scheme"] == "StratifiedGroupKFold"
    assert cfg["cv"]["n_splits"] == 5
    assert cfg["cv"]["group_column"] == "group_id"
    assert cfg["cv"]["selected_params"] == {"C": 1.0, "gamma": "scale"}
    assert cfg["evaluation"]["allow_test"] is False


def test_t7_run_one_unscored(tmp_path: Path):
    """T7: Kiểm tra run_one ở chế độ score=False không rò rỉ bất kỳ từ khoá điểm số nào."""
    rng = np.random.default_rng(42)
    x_tr = np.vstack([rng.normal(loc=10.0 * c, scale=1.0, size=(30, 8)) for c in range(4)])
    y_tr = np.concatenate([np.full(30, c, dtype=np.int64) for c in range(4)])
    x_v = np.vstack([rng.normal(loc=10.0 * c, scale=1.0, size=(10, 8)) for c in range(4)])
    y_v = np.concatenate([np.full(10, c, dtype=np.int64) for c in range(4)])
    img_ids_v = [f"val_img_{i}" for i in range(40)]

    cv_result = {
        "n_splits": 5,
        "cv_seed": 42,
        "param_grid": [{"n_neighbors": 3, "weights": "uniform"}],
        "best_params": {"n_neighbors": 3, "weights": "uniform"},
        "best_index": 0,
        "best_score": 0.95,
        "best_std": 0.02,
        "candidates": [],
        "cv_cpu_seconds": 0.5,
        "cv_wall_seconds": 0.3,
    }

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
            "train": {"n_images": 120, "glcm_nan_images": 0, "cpu_seconds": {"ghep": 1.0}},
            "val": {"n_images": 40, "glcm_nan_images": 0, "cpu_seconds": {"ghep": 0.4}},
        },
    }

    out_root = tmp_path / "out"
    metrics = run_one(
        classifier="knn",
        seed=42,
        x_train=x_tr,
        y_train=y_tr,
        x_val=x_v,
        y_val=y_v,
        image_ids_val=img_ids_v,
        cv_result=cv_result,
        out_root=out_root,
        context=context,
        score=False,
        n_jobs=1,
    )

    assert metrics["scored"] is False
    run_dir = out_root / "rq2_ghep_knn_s42"
    for fname in ("config.yaml", "metrics.json", "log"):
        content = (run_dir / fname).read_text(encoding="utf-8")
        assert FORBIDDEN_SCORE_PATTERN.search(content) is None


def test_t8_run_experiment_end_to_end(tmp_path: Path):
    """T8: Kiểm tra run_experiment chạy end-to-end 6 bộ phân loại, đúng số seed tất định/ngẫu nhiên và không chạm test."""
    df = make_synthetic_rq2_dataset(tmp_path)
    split_csv = tmp_path / "split_v1.csv"
    df.to_csv(split_csv, index=False, lineterminator="\n")

    data_root = tmp_path / "data"
    out_root = tmp_path / "out_results"

    fast_grids = {
        "lr": ({"C": 0.1}, {"C": 1.0}),
        "knn": ({"n_neighbors": 3, "weights": "uniform"}, {"n_neighbors": 5, "weights": "distance"}),
        "dt": ({"max_depth": 5, "min_samples_leaf": 1}, {"max_depth": 10, "min_samples_leaf": 1}),
        "rf": ({"n_estimators": 10, "max_depth": 10}, {"n_estimators": 15, "max_depth": None}),
        "svm": ({"C": 1.0, "gamma": "scale"}, {"C": 5.0, "gamma": "scale"}),
        "gb": (
            {"n_estimators": 10, "learning_rate": 0.1, "max_depth": 2},
            {"n_estimators": 15, "learning_rate": 0.1, "max_depth": 3},
        ),
    }

    mode_config = {
        "limit_train": None,
        "limit_val": None,
        "subset_seed": 0,
        "classifiers": CLASSIFIERS,
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
        param_grids=fast_grids,
        n_jobs=1,
        expected_train_n=40,
        expected_val_n=12,
    )

    # 3 tất định x 1 seed (42) + 3 ngẫu nhiên x 2 seed (42, 43) = 9 run
    expected_runs = [
        "rq2_ghep_lr_s42",
        "rq2_ghep_knn_s42",
        "rq2_ghep_dt_s42",
        "rq2_ghep_dt_s43",
        "rq2_ghep_rf_s42",
        "rq2_ghep_rf_s43",
        "rq2_ghep_svm_s42",
        "rq2_ghep_gb_s42",
        "rq2_ghep_gb_s43",
    ]
    assert summary["runs"] == expected_runs
    run_dirs = sorted(p.name for p in out_root.iterdir() if p.is_dir())
    assert run_dirs == sorted(expected_runs)

    # summary_full.json tuyệt đối không chứa từ khoá điểm số
    summary_json = json.dumps(summary, ensure_ascii=False)
    assert FORBIDDEN_SCORE_PATTERN.search(summary_json) is None
    assert sorted(summary["cost_rank"]) == sorted(CLASSIFIERS)

    for r_id in expected_runs:
        r_path = out_root / r_id
        assert sorted(p.name for p in r_path.iterdir()) == [
            "config.yaml",
            "log",
            "metrics.json",
            "preds_val.csv",
        ]
        cfg_text = (r_path / "config.yaml").read_text(encoding="utf-8")
        assert FORBIDDEN_SCORE_PATTERN.search(cfg_text) is None
        with open(r_path / "metrics.json", encoding="utf-8") as f:
            m = json.load(f)
        assert "macro_f1" in m


def test_t9_mode_settings_and_package_sync(tmp_path: Path):
    """T9: Kiểm tra mode_settings, build_code_package và đồng bộ với script Kaggle RQ2."""
    t0 = mode_settings("t0")
    assert t0["classifiers"] == CLASSIFIERS
    assert t0["seeds"] == (42,)
    assert t0["score"] is False
    assert t0["out_subdir"] == "results_trial"

    t1 = mode_settings("t1")
    assert t1["classifiers"] == ("svm",)
    assert t1["seeds"] == (42,)
    assert t1["score"] is False
    assert t1["out_subdir"] == "results_trial"

    full = mode_settings("full")
    assert full["classifiers"] == CLASSIFIERS
    assert full["seeds"] == SEEDS
    assert full["score"] is True
    assert full["out_subdir"] == "results"

    with pytest.raises(ValueError):
        mode_settings("invalid")

    repo_root = Path(__file__).resolve().parent.parent
    script_path = repo_root / "kaggle/rq2_classifiers/run_rq2_classifiers.py"
    spec = importlib.util.spec_from_file_location(
        "kaggle_run_rq2_classifiers", script_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod.SRC_FILES == PACKAGE_SRC_FILES
    assert mod.SPLIT_FILES == PACKAGE_SPLIT_FILES

    # Kiểm tra đóng gói phẳng 10 tệp
    mock_repo = tmp_path / "mock_repo"
    (mock_repo / "src").mkdir(parents=True)
    (mock_repo / "splits").mkdir(parents=True)
    for name in PACKAGE_SRC_FILES:
        (mock_repo / "src" / name).write_text(f"# {name}\n", encoding="utf-8")
    (mock_repo / "splits/split_v1.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (mock_repo / "splits/split_v1.sha256").write_text(
        "hash  split_v1.csv\n", encoding="utf-8"
    )

    out_dir = tmp_path / "pkg_out"
    res = build_code_package(mock_repo, out_dir, "f" * 40, "t0")
    expected_files = sorted(
        [
            "COMMIT",
            "MODE",
            "dataset-metadata.json",
            "dataset.py",
            "features_hist_glcm_lbp.py",
            "features_hog_ghep.py",
            "metrics.py",
            "rq2_runner.py",
            "split_v1.csv",
            "split_v1.sha256",
        ]
    )
    assert res == expected_files
    meta = json.loads((out_dir / "dataset-metadata.json").read_text(encoding="utf-8"))
    assert meta == {
        "title": "cxr-rq2-code",
        "id": "ductrannguyen/cxr-rq2-code",
        "licenses": [{"name": "other"}],
    }


def test_t10_kaggle_main_and_version_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """T10: Kiểm tra kaggle_main chạy đúng chế độ t0 giả lập và dừng khi lệch phiên bản cứng."""
    input_dir = tmp_path / "input"
    working_dir = tmp_path / "working"
    input_dir.mkdir()
    working_dir.mkdir()

    data_synth = tmp_path / "synth"
    df = make_synthetic_rq2_dataset(data_synth)

    data_dest = (
        input_dir
        / "datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset"
    )
    shutil.copytree(data_synth / "data", data_dest)

    pkg_dest = input_dir / "datasets/ductrannguyen/cxr-rq2-code"
    pkg_dest.mkdir(parents=True)
    split_csv_path = pkg_dest / "split_v1.csv"
    df.to_csv(split_csv_path, index=False, lineterminator="\n")
    actual_sha = hashlib.sha256(split_csv_path.read_bytes()).hexdigest().lower()
    (pkg_dest / "split_v1.sha256").write_text(
        f"{actual_sha}  split_v1.csv\n", encoding="utf-8"
    )
    (pkg_dest / "COMMIT").write_text("a" * 40 + "\n", encoding="utf-8")
    (pkg_dest / "MODE").write_text("t0\n", encoding="utf-8")

    assert find_data_root(input_dir) == data_dest
    assert find_code_package(input_dir) == pkg_dest

    monkeypatch.setattr(
        "src.rq2_runner.collect_versions",
        lambda: {**EXPECTED_VERSIONS, "python": "3.12.0"},
    )

    fast_grids = {
        "lr": ({"C": 1.0},),
        "knn": ({"n_neighbors": 3, "weights": "uniform"},),
        "dt": ({"max_depth": 5, "min_samples_leaf": 1},),
        "rf": ({"n_estimators": 10, "max_depth": 10},),
        "svm": ({"C": 1.0, "gamma": "scale"},),
        "gb": ({"n_estimators": 10, "learning_rate": 0.1, "max_depth": 2},),
    }

    summary = kaggle_main(
        input_root=input_dir,
        working_root=working_dir,
        param_grids=fast_grids,
        n_jobs=1,
        expected_train_n=40,
        expected_val_n=12,
    )

    assert summary["mode"] == "t0"
    summary_file = working_dir / "summary_t0.json"
    assert summary_file.is_file()
    assert FORBIDDEN_SCORE_PATTERN.search(summary_file.read_text(encoding="utf-8")) is None

    trial_dir = working_dir / "results_trial"
    run_folders = sorted(p.name for p in trial_dir.iterdir() if p.is_dir())
    assert run_folders == sorted(f"rq2_ghep_{c}_s42" for c in CLASSIFIERS)

    monkeypatch.setattr(
        "src.rq2_runner.collect_versions",
        lambda: {**EXPECTED_VERSIONS, "python": "3.12.0", "scikit-learn": "0.0.0"},
    )
    with pytest.raises(RuntimeError) as exc_info:
        kaggle_main(
            input_root=input_dir,
            working_root=working_dir,
            param_grids=fast_grids,
            n_jobs=1,
            expected_train_n=40,
            expected_val_n=12,
        )
    assert "scikit-learn" in str(exc_info.value)
