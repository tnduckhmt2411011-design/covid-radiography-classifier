"""Module điều phối thực thi so sánh 6 bộ phân loại học máy cổ điển và đóng gói mã nguồn RQ2.

Trách nhiệm:
- Cung cấp runner so sánh 6 bộ phân loại (lr, knn, dt, rf, svm, gb) trên nhóm đặc trưng
  'ghep' (152 chiều, đã chốt ở S3-06) theo chuẩn H1 đến H7 của results/threshold_v3.md
  (phụ trách nhiệm vụ S4-03).
- Chọn siêu tham số bằng StratifiedGroupKFold 5 fold (shuffle=True, random_state=42)
  chia nhóm theo cột group_id trên tập train; chuẩn hoá StandardScaler chỉ fit trên train fold.
- Áp dụng trọng số lớp theo H3: class_weight='balanced' cho lr, dt, svm;
  class_weight='balanced_subsample' cho rf; sample_weight cân bằng cho gb;
  ghi chú k-NN không hỗ trợ trọng số lớp.
- Mô hình tất định (lr, knn, svm) chạy 1 lần và ghi rõ không có độ lệch chuẩn;
  mô hình ngẫu nhiên (dt, rf, gb) chạy 3 seed (42, 43, 44).
"""

import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

from joblib import Parallel, delayed
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight
import yaml

from src.dataset import CLASS_NAMES, CXRDataset, LABEL_TO_IDX
from src.features_hist_glcm_lbp import (
    GLCM_ANGLES,
    GLCM_DISTANCES,
    GLCM_LEVELS,
    GLCM_PROPS,
    HIST_BINS,
    LBP_PARAMS,
)
from src.features_hog_ghep import (
    GROUP_NAMES,
    HOG_BLOCK_NORM,
    HOG_CELLS_PER_BLOCK,
    HOG_ORIENTATIONS,
    HOG_PIXELS_PER_CELL,
    extract_groups,
)
from src.metrics import compute_metrics

RQ_NAME: str = "rq2"
FEATURE_GROUP: str = "ghep"
CLASSIFIERS: Tuple[str, ...] = ("lr", "knn", "dt", "rf", "svm", "gb")
DETERMINISTIC_CLASSIFIERS: Tuple[str, ...] = ("lr", "knn", "svm")
STOCHASTIC_CLASSIFIERS: Tuple[str, ...] = ("dt", "rf", "gb")
SEEDS: Tuple[int, ...] = (42, 43, 44)
CV_SPLITS: int = 5
CV_RANDOM_STATE: int = 42
EXPECTED_TRAIN_N: int = 14815
EXPECTED_VAL_N: int = 3174
CHUNK_SIZE: int = 64
MIN_PER_CLASS: int = 5
VALID_MODES: Tuple[str, ...] = ("t0", "t1", "full")
VALID_SPLITS: Tuple[str, ...] = ("train", "val")
PROBA_COLUMNS: Tuple[str, ...] = tuple(
    f"proba_{name.replace(' ', '_')}" for name in CLASS_NAMES
)
PACKAGE_SRC_FILES: Tuple[str, ...] = (
    "dataset.py",
    "metrics.py",
    "features_hist_glcm_lbp.py",
    "features_hog_ghep.py",
    "rq2_runner.py",
)
PACKAGE_SPLIT_FILES: Tuple[str, ...] = (
    "split_v1.csv",
    "split_v1.sha256",
)
HARD_PINNED_PACKAGES: Tuple[str, ...] = ("scikit-learn", "scikit-image")
EXPECTED_VERSIONS: Dict[str, str] = {
    "numpy": "2.0.2",
    "pandas": "2.3.3",
    "scikit-learn": "1.6.1",
    "scikit-image": "0.25.2",
    "opencv-python-headless": "4.13.0.92",
}

CLASSIFIER_SPECS: Dict[str, Dict[str, Any]] = {
    "lr": {
        "class_name": "LogisticRegression",
        "deterministic": True,
        "use_scaler": True,
        "class_weight_mode": "balanced",
        "class_weight_note": "class_weight='balanced' (H3)",
        "fixed_params": {
            "class_weight": "balanced",
            "solver": "lbfgs",
            "max_iter": 1000,
        },
    },
    "knn": {
        "class_name": "KNeighborsClassifier",
        "deterministic": True,
        "use_scaler": True,
        "class_weight_mode": "none",
        "class_weight_note": "k-NN khong ho tro trong so lop; ghi chu trong bao cao theo H3",
        "fixed_params": {},
    },
    "dt": {
        "class_name": "DecisionTreeClassifier",
        "deterministic": False,
        "use_scaler": False,
        "class_weight_mode": "balanced",
        "class_weight_note": "class_weight='balanced' (H3)",
        "fixed_params": {
            "class_weight": "balanced",
        },
    },
    "rf": {
        "class_name": "RandomForestClassifier",
        "deterministic": False,
        "use_scaler": False,
        "class_weight_mode": "balanced_subsample",
        "class_weight_note": "class_weight='balanced_subsample' (dong bo tham chieu RQ1)",
        "fixed_params": {
            "class_weight": "balanced_subsample",
        },
    },
    "svm": {
        "class_name": "SVC",
        "deterministic": True,
        "use_scaler": True,
        "class_weight_mode": "balanced",
        "class_weight_note": "class_weight='balanced' (H3)",
        "fixed_params": {
            "class_weight": "balanced",
            "kernel": "rbf",
        },
    },
    "gb": {
        "class_name": "GradientBoostingClassifier",
        "deterministic": False,
        "use_scaler": False,
        "class_weight_mode": "sample_weight",
        "class_weight_note": "sample_weight=compute_sample_weight('balanced', y_train) truyen vao fit() theo H3",
        "fixed_params": {
            "max_features": "sqrt",
        },
    },
}

PARAM_GRIDS: Dict[str, Tuple[Dict[str, Any], ...]] = {
    "lr": (
        {"C": 0.01},
        {"C": 0.1},
        {"C": 1.0},
        {"C": 10.0},
    ),
    "knn": (
        {"n_neighbors": 3, "weights": "uniform"},
        {"n_neighbors": 3, "weights": "distance"},
        {"n_neighbors": 5, "weights": "uniform"},
        {"n_neighbors": 5, "weights": "distance"},
        {"n_neighbors": 11, "weights": "uniform"},
        {"n_neighbors": 11, "weights": "distance"},
    ),
    "dt": (
        {"max_depth": 10, "min_samples_leaf": 1},
        {"max_depth": 10, "min_samples_leaf": 5},
        {"max_depth": 20, "min_samples_leaf": 1},
        {"max_depth": 20, "min_samples_leaf": 5},
        {"max_depth": None, "min_samples_leaf": 1},
        {"max_depth": None, "min_samples_leaf": 5},
    ),
    "rf": (
        {"n_estimators": 300, "max_depth": 20},
        {"n_estimators": 300, "max_depth": None},
        {"n_estimators": 500, "max_depth": 20},
        {"n_estimators": 500, "max_depth": None},
    ),
    "svm": (
        {"C": 1.0, "gamma": "scale"},
        {"C": 1.0, "gamma": "auto"},
        {"C": 10.0, "gamma": "scale"},
        {"C": 10.0, "gamma": "auto"},
    ),
    "gb": (
        {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
        {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 5},
        {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 3},
        {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 5},
    ),
}


def make_run_id(
    classifier: str,
    seed: int,
    features: str = FEATURE_GROUP,
) -> str:
    """Tạo định danh duy nhất cho một lần chạy mô hình RQ2.

    Args:
        classifier: Mã bộ phân loại ('lr', 'knn', 'dt', 'rf', 'svm', 'gb').
        seed: Hạt giống ngẫu nhiên (số nguyên không âm).
        features: Tên nhóm đặc trưng (mặc định 'ghep').

    Returns:
        Chuỗi run_id có cấu trúc 'rq2_ghep_<classifier>_s<seed>'.

    Raises:
        ValueError: Nếu bộ phân loại, nhóm đặc trưng hoặc seed không hợp lệ.
    """
    if classifier not in CLASSIFIERS:
        raise ValueError(
            f"Bo phan loai '{classifier}' khong hop le. Cac bo hop le: {CLASSIFIERS}."
        )
    if features != FEATURE_GROUP:
        raise ValueError(
            f"RQ2 chi su dung nhom dac trung da chot '{FEATURE_GROUP}', nhan duoc: '{features}'."
        )
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError(f"Seed phai la so nguyen khong am, nhan duoc: {seed!r}.")
    return f"{RQ_NAME}_{features}_{classifier}_s{seed}"


def seeds_for_classifier(
    classifier: str,
    seeds: Sequence[int] = SEEDS,
) -> Tuple[int, ...]:
    """Trả về danh sách seed cần chạy cho từng bộ phân loại theo cổng H3.

    Mô hình tất định (lr, knn, svm) chỉ chạy một lần với seed đầu tiên.
    Mô hình ngẫu nhiên (dt, rf, gb) chạy đủ danh sách seed được cấp.
    """
    if classifier not in CLASSIFIERS:
        raise ValueError(
            f"Bo phan loai '{classifier}' khong hop le. Cac bo hop le: {CLASSIFIERS}."
        )
    if not seeds:
        raise ValueError("Danh sach seeds khong duoc rong.")
    if CLASSIFIER_SPECS[classifier]["deterministic"]:
        return (int(seeds[0]),)
    return tuple(int(s) for s in seeds)


def stratified_subset(
    labels: Sequence[str],
    n: int,
    seed: int,
    min_per_class: int = MIN_PER_CLASS,
) -> np.ndarray:
    """Lấy mẫu phân tầng theo nhãn đảm bảo số lượng mẫu tối thiểu cho mỗi lớp."""
    if n < 1:
        raise ValueError(f"So luong mau n phai lon hon hoac bang 1, nhan duoc {n}.")
    total = len(labels)
    if n >= total:
        return np.arange(total, dtype=np.int64)

    rng = np.random.default_rng(seed)
    chosen_indices_list: List[np.ndarray] = []
    labels_arr = np.array(labels)
    unique_labels = sorted(set(labels))

    for lbl in unique_labels:
        idx_c = np.where(labels_arr == lbl)[0]
        size_c = len(idx_c)
        k = max(min_per_class, int(round(n * size_c / total)))
        k = min(k, size_c)
        chosen = rng.choice(idx_c, size=k, replace=False)
        chosen_indices_list.append(chosen)

    merged = np.concatenate(chosen_indices_list).astype(np.int64)
    return np.sort(merged)


def verify_split_sha256(
    csv_path: Union[str, Path],
    sha_path: Union[str, Path],
) -> str:
    """Xác thực mã băm SHA256 của tệp phân chia dữ liệu CSV."""
    expected_sha = Path(sha_path).read_text(encoding="utf-8").split()[0].lower()
    hasher = hashlib.sha256()
    with open(csv_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    actual_sha = hasher.hexdigest().lower()
    if actual_sha != expected_sha:
        raise ValueError(
            f"Ma bam SHA256 khong khop: ky vong '{expected_sha}', thuc te '{actual_sha}'."
        )
    return actual_sha


def load_split_images(
    split_df: pd.DataFrame,
    split: str,
    data_root: Optional[Union[str, Path]],
    limit: Optional[int] = None,
    subset_seed: int = 0,
) -> Tuple[Iterator[np.ndarray], List[str], np.ndarray, List[str]]:
    """Nạp ảnh, danh sách image_id, nhãn y và group_id cho phân vùng hợp lệ (train hoặc val)."""
    if split not in VALID_SPLITS:
        raise ValueError(
            f"Phan vung '{split}' khong hop le, chi chap nhan train hoac val (tap test bi khoa)."
        )
    if "group_id" not in split_df.columns:
        raise ValueError("split_df bat buoc phai co cot 'group_id' de chia StratifiedGroupKFold.")

    df = split_df[split_df["split"] == split].reset_index(drop=True)
    if limit is not None:
        selected_idx = stratified_subset(
            df["label"].tolist(), limit, subset_seed
        )
        df = df.iloc[selected_idx].reset_index(drop=True)

    dataset = CXRDataset(df, split=split, data_root=data_root)
    image_ids = df["image_id"].tolist()
    group_ids = df["group_id"].astype(str).tolist()
    y = df["label"].map(LABEL_TO_IDX).to_numpy(dtype=np.int64)

    def _yield_images() -> Iterator[np.ndarray]:
        for i in range(len(dataset)):
            img, _ = dataset[i]
            yield img

    return _yield_images(), image_ids, y, group_ids


def collect_versions() -> Dict[str, str]:
    """Thu thập phiên bản của Python và các thư viện cốt lõi đã cài đặt."""
    versions: Dict[str, str] = {"python": sys.version.split()[0]}
    packages = [
        "numpy",
        "pandas",
        "scikit-learn",
        "scikit-image",
        "opencv-python-headless",
        "pyyaml",
        "pillow",
    ]
    for pkg in packages:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "khong cai"
    return versions


def check_pinned_versions(
    versions: Dict[str, str],
    expected: Dict[str, str] = EXPECTED_VERSIONS,
) -> List[str]:
    """So sánh phiên bản hiện tại với danh sách phiên bản đã ghim."""
    mismatches: List[str] = []
    for pkg, exp_ver in expected.items():
        actual_ver = versions.get(pkg)
        if actual_ver != exp_ver:
            mismatches.append(
                f"Goi '{pkg}' khong khop phien ban: ky vong '{exp_ver}', thuc te '{actual_ver}'."
            )
    return mismatches


def feature_params(group: str = FEATURE_GROUP) -> Dict[str, object]:
    """Trả về cấu hình tham số của nhóm đặc trưng theo kiểu Python gốc."""
    hist = {
        "bins": HIST_BINS,
        "range": [0, 256],
        "normalize": "sum1",
    }
    glcm = {
        "levels": GLCM_LEVELS,
        "distances": list(GLCM_DISTANCES),
        "angles": list(GLCM_ANGLES),
        "props": list(GLCM_PROPS),
        "symmetric": True,
        "normed": True,
        "gray_reduction": "img // 8",
        "correlation_nan": "thay bang 0",
    }
    lbp = {
        "params": [[int(p[0]), int(p[1])] for p in LBP_PARAMS],
        "method": "uniform",
    }
    hog = {
        "orientations": HOG_ORIENTATIONS,
        "pixels_per_cell": list(HOG_PIXELS_PER_CELL),
        "cells_per_block": list(HOG_CELLS_PER_BLOCK),
        "block_norm": HOG_BLOCK_NORM,
    }
    if group == "hist":
        return hist
    elif group == "glcmlbp":
        return {"glcm": glcm, "lbp": lbp}
    elif group == "hog":
        return hog
    elif group == "ghep":
        return {"hist": hist, "glcm": glcm, "lbp": lbp}
    else:
        raise ValueError(f"Nhom dac trung '{group}' khong hop le.")


def _build_estimator(
    classifier: str,
    candidate_params: Mapping[str, Any],
    seed: int,
    for_cv: bool,
    n_jobs: int,
) -> Any:
    """Khởi tạo estimator của scikit-learn theo đúng cấu hình bộ phân loại."""
    spec = CLASSIFIER_SPECS[classifier]
    fixed = dict(spec["fixed_params"])
    merged = {**fixed, **dict(candidate_params)}

    if classifier == "lr":
        return LogisticRegression(**merged, random_state=seed)
    elif classifier == "knn":
        return KNeighborsClassifier(**merged, n_jobs=n_jobs)
    elif classifier == "dt":
        return DecisionTreeClassifier(**merged, random_state=seed)
    elif classifier == "rf":
        return RandomForestClassifier(**merged, random_state=seed, n_jobs=n_jobs)
    elif classifier == "svm":
        if for_cv:
            return SVC(**merged, probability=False)
        return SVC(**merged, probability=True, random_state=seed)
    elif classifier == "gb":
        return GradientBoostingClassifier(**merged, random_state=seed)
    else:
        raise ValueError(f"Bo phan loai '{classifier}' khong hop le.")


def _evaluate_single_fold(
    classifier: str,
    candidate_params: Mapping[str, Any],
    x_train_fold: np.ndarray,
    y_train_fold: np.ndarray,
    x_val_fold: np.ndarray,
    y_val_fold: np.ndarray,
    cv_seed: int,
    inner_n_jobs: int,
) -> Tuple[float, float, float]:
    """Đánh giá một fold đơn lẻ trong CV, chuẩn hoá độc lập bên trong fold để chống rò rỉ (H6)."""
    t_cpu_start = time.process_time()
    t_wall_start = time.perf_counter()

    spec = CLASSIFIER_SPECS[classifier]
    if spec["use_scaler"]:
        scaler = StandardScaler()
        x_tr = scaler.fit_transform(x_train_fold)
        x_va = scaler.transform(x_val_fold)
    else:
        x_tr = x_train_fold
        x_va = x_val_fold

    est = _build_estimator(
        classifier=classifier,
        candidate_params=candidate_params,
        seed=cv_seed,
        for_cv=True,
        n_jobs=inner_n_jobs,
    )

    if classifier == "gb":
        sw = compute_sample_weight("balanced", y_train_fold)
        est.fit(x_tr, y_train_fold, sample_weight=sw)
    else:
        est.fit(x_tr, y_train_fold)

    y_pred = est.predict(x_va).astype(np.int64)
    score = float(compute_metrics(y_val_fold, y_pred)["macro_f1"])

    cpu_elapsed = float(time.process_time() - t_cpu_start)
    wall_elapsed = float(time.perf_counter() - t_wall_start)
    return score, cpu_elapsed, wall_elapsed


def select_hyperparameters_cv(
    classifier: str,
    x_train: np.ndarray,
    y_train: np.ndarray,
    groups_train: Sequence[str],
    param_grid: Optional[Sequence[Mapping[str, Any]]] = None,
    n_splits: int = CV_SPLITS,
    cv_seed: int = CV_RANDOM_STATE,
    n_jobs: int = -1,
) -> Dict[str, Any]:
    """Chọn siêu tham số bằng StratifiedGroupKFold 5 fold trên tập train theo group_id (cổng H3, H6).

    Args:
        classifier: Tên mã bộ phân loại ('lr', 'knn', 'dt', 'rf', 'svm', 'gb').
        x_train: Ma trận đặc trưng tập train.
        y_train: Mảng nhãn tập train.
        groups_train: Danh sách group_id tương ứng từng mẫu tập train.
        param_grid: Lưới siêu tham số (mặc định dùng PARAM_GRIDS[classifier]).
        n_splits: Số fold CV (mặc định 5).
        cv_seed: Seed chia fold và khởi tạo estimator trong CV (mặc định 42).
        n_jobs: Số luồng xử lý song song.

    Returns:
        Dict kết quả CV gồm best_params, best_index, best_score, best_std, candidates,
        cv_cpu_seconds, cv_wall_seconds.
    """
    if classifier not in CLASSIFIERS:
        raise ValueError(
            f"Bo phan loai '{classifier}' khong hop le. Cac bo hop le: {CLASSIFIERS}."
        )
    if len(x_train) != len(y_train) or len(y_train) != len(groups_train):
        raise ValueError(
            f"Do dai x_train ({len(x_train)}), y_train ({len(y_train)}), "
            f"groups_train ({len(groups_train)}) khong khop."
        )
    if set(np.unique(y_train)) != {0, 1, 2, 3}:
        raise ValueError(
            f"y_train phai chua day du 4 lop {{0, 1, 2, 3}}, thuc te co: {set(np.unique(y_train))}."
        )

    grid = list(param_grid) if param_grid is not None else [dict(p) for p in PARAM_GRIDS[classifier]]
    if not grid:
        raise ValueError(f"Luoi sieu tham so cho '{classifier}' khong duoc rong.")

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=cv_seed)
    groups_arr = np.asarray(groups_train)
    folds: List[Tuple[np.ndarray, np.ndarray]] = list(
        sgkf.split(x_train, y_train, groups_arr)
    )

    t_parent_cpu_start = time.process_time()
    t_wall_start = time.perf_counter()

    # Với rf và knn đã đa luồng bên trong, chạy tuần tự các fold với inner_n_jobs=n_jobs;
    # với lr, dt, svm, gb đơn luồng, chạy song song các tác vụ (candidate, fold) qua Parallel.
    if classifier in ("rf", "knn") or n_jobs == 1:
        tasks_results: List[Tuple[float, float, float]] = []
        for cand in grid:
            for tr_idx, va_idx in folds:
                res = _evaluate_single_fold(
                    classifier=classifier,
                    candidate_params=cand,
                    x_train_fold=x_train[tr_idx],
                    y_train_fold=y_train[tr_idx],
                    x_val_fold=x_train[va_idx],
                    y_val_fold=y_train[va_idx],
                    cv_seed=cv_seed,
                    inner_n_jobs=n_jobs,
                )
                tasks_results.append(res)
    else:
        tasks_results = list(
            Parallel(n_jobs=n_jobs)(
                delayed(_evaluate_single_fold)(
                    classifier=classifier,
                    candidate_params=cand,
                    x_train_fold=x_train[tr_idx],
                    y_train_fold=y_train[tr_idx],
                    x_val_fold=x_train[va_idx],
                    y_val_fold=y_train[va_idx],
                    cv_seed=cv_seed,
                    inner_n_jobs=1,
                )
                for cand in grid
                for tr_idx, va_idx in folds
            )
        )

    parent_cpu_elapsed = float(time.process_time() - t_parent_cpu_start)
    sum_fold_cpu = float(sum(r[1] for r in tasks_results))
    cv_cpu_seconds = max(parent_cpu_elapsed, sum_fold_cpu)
    cv_wall_seconds = float(time.perf_counter() - t_wall_start)

    candidates_out: List[Dict[str, Any]] = []
    best_idx = 0
    best_mean = -1.0
    best_std = 0.0

    for c_idx, cand in enumerate(grid):
        slice_res = tasks_results[c_idx * n_splits : (c_idx + 1) * n_splits]
        fold_scores = [float(r[0]) for r in slice_res]
        mean_score = float(np.mean(fold_scores))
        std_score = float(np.std(fold_scores, ddof=1)) if n_splits > 1 else 0.0
        candidates_out.append(
            {
                "params": dict(cand),
                "fold_scores": fold_scores,
                "mean_score": mean_score,
                "std_score": std_score,
            }
        )
        if mean_score > best_mean + 1e-12:
            best_mean = mean_score
            best_std = std_score
            best_idx = c_idx

    return {
        "n_splits": int(n_splits),
        "cv_seed": int(cv_seed),
        "param_grid": [dict(p) for p in grid],
        "best_params": dict(grid[best_idx]),
        "best_index": int(best_idx),
        "best_score": float(best_mean),
        "best_std": float(best_std),
        "candidates": candidates_out,
        "cv_cpu_seconds": float(cv_cpu_seconds),
        "cv_wall_seconds": float(cv_wall_seconds),
    }


def _sanitize_params(params: Mapping[str, Any]) -> Dict[str, Any]:
    """Chuyển đổi dict get_params() sang các kiểu dữ liệu cơ bản an toàn với YAML/JSON."""
    clean: Dict[str, Any] = {}
    for k, v in params.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            clean[k] = v
        elif isinstance(v, np.generic):
            clean[k] = v.item()
        else:
            clean[k] = str(v)
    return clean


def train_and_predict_classifier(
    classifier: str,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    seed: int,
    best_params: Mapping[str, Any],
    n_jobs: int = -1,
) -> Dict[str, Any]:
    """Huấn luyện mô hình với siêu tham số đã chọn trên toàn bộ x_train và dự đoán trên x_val."""
    if classifier not in CLASSIFIERS:
        raise ValueError(
            f"Bo phan loai '{classifier}' khong hop le. Cac bo hop le: {CLASSIFIERS}."
        )
    if set(np.unique(y_train)) != {0, 1, 2, 3}:
        raise ValueError(
            f"y_train phai chua day du 4 lop {{0, 1, 2, 3}}, thuc te co: {set(np.unique(y_train))}."
        )

    spec = CLASSIFIER_SPECS[classifier]
    use_scaler = bool(spec["use_scaler"])

    t_fit_cpu_start = time.process_time()
    t_fit_wall_start = time.perf_counter()

    if use_scaler:
        scaler = StandardScaler()
        x_tr_fit = scaler.fit_transform(x_train)
        x_va_eval = scaler.transform(x_val)
    else:
        x_tr_fit = x_train
        x_va_eval = x_val

    est = _build_estimator(
        classifier=classifier,
        candidate_params=best_params,
        seed=seed,
        for_cv=False,
        n_jobs=n_jobs,
    )

    if classifier == "gb":
        sw = compute_sample_weight("balanced", y_train)
        est.fit(x_tr_fit, y_train, sample_weight=sw)
    else:
        est.fit(x_tr_fit, y_train)

    fit_cpu_seconds = float(time.process_time() - t_fit_cpu_start)
    fit_wall_seconds = float(time.perf_counter() - t_fit_wall_start)

    if est.classes_.tolist() != [0, 1, 2, 3]:
        raise ValueError(
            f"est.classes_ phai la [0, 1, 2, 3], thuc te nhan duoc: {est.classes_.tolist()}."
        )

    t_pred_wall_start = time.perf_counter()
    proba = est.predict_proba(x_va_eval).astype(np.float64)
    if classifier == "svm":
        y_pred = est.predict(x_va_eval).astype(np.int64)
    else:
        y_pred = est.classes_[np.argmax(proba, axis=1)].astype(np.int64)
    predict_wall_seconds = float(time.perf_counter() - t_pred_wall_start)

    return {
        "y_pred": y_pred,
        "proba": proba,
        "params": _sanitize_params(est.get_params()),
        "use_scaler": use_scaler,
        "class_weight_mode": str(spec["class_weight_mode"]),
        "class_weight_note": str(spec["class_weight_note"]),
        "deterministic": bool(spec["deterministic"]),
        "fit_cpu_seconds": fit_cpu_seconds,
        "fit_wall_seconds": fit_wall_seconds,
        "predict_wall_seconds": predict_wall_seconds,
    }


def write_run_outputs(
    run_dir: Path,
    config: Dict[str, object],
    metrics: Dict[str, object],
    log_lines: List[str],
    image_ids: List[str],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    proba: np.ndarray,
) -> Dict[str, Path]:
    """Ghi đúng 4 tệp kết quả của một run vào thư mục run_dir."""
    n = len(image_ids)
    if (
        len(y_true) != n
        or len(y_pred) != n
        or proba.shape[0] != n
        or proba.shape[1] != 4
    ):
        raise ValueError(
            f"Do dai khong khop: image_ids={n}, y_true={len(y_true)}, "
            f"y_pred={len(y_pred)}, proba={proba.shape}."
        )

    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    config_path = run_path / "config.yaml"
    with open(config_path, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

    metrics_path = run_path / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log_path = run_path / "log"
    with open(log_path, "w", encoding="utf-8", newline="\n") as f:
        for line in log_lines:
            f.write(line + "\n")

    preds_path = run_path / "preds_val.csv"
    preds_df = pd.DataFrame(
        {
            "image_id": image_ids,
            "y_true": y_true,
            "y_pred": y_pred,
            PROBA_COLUMNS[0]: proba[:, 0],
            PROBA_COLUMNS[1]: proba[:, 1],
            PROBA_COLUMNS[2]: proba[:, 2],
            PROBA_COLUMNS[3]: proba[:, 3],
        }
    )
    preds_df.to_csv(preds_path, index=False, float_format="%.8f", lineterminator="\n")

    return {
        "config.yaml": config_path,
        "metrics.json": metrics_path,
        "log": log_path,
        "preds_val.csv": preds_path,
    }


def run_one(
    classifier: str,
    seed: int,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    image_ids_val: List[str],
    cv_result: Mapping[str, Any],
    out_root: Path,
    context: Dict[str, Any],
    score: bool,
    n_jobs: int = -1,
) -> Dict[str, Any]:
    """Thực thi một run huấn luyện đơn lẻ cho một bộ phân loại và một seed sau khi đã có kết quả CV."""
    run_id = make_run_id(classifier, seed, features=FEATURE_GROUP)
    best_params = dict(cv_result["best_params"])

    fit_res = train_and_predict_classifier(
        classifier=classifier,
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        seed=seed,
        best_params=best_params,
        n_jobs=n_jobs,
    )
    y_pred = fit_res["y_pred"]
    proba = fit_res["proba"]
    spec = CLASSIFIER_SPECS[classifier]

    train_ext = context["extraction"]["train"]
    val_ext = context["extraction"]["val"]

    seconds = {
        "extract_cpu_train": round(float(train_ext["cpu_seconds"][FEATURE_GROUP]), 3),
        "extract_cpu_val": round(float(val_ext["cpu_seconds"][FEATURE_GROUP]), 3),
        "cv_cpu": round(float(cv_result["cv_cpu_seconds"]), 3),
        "cv_wall": round(float(cv_result["cv_wall_seconds"]), 3),
        "fit_cpu": round(float(fit_res["fit_cpu_seconds"]), 3),
        "fit_wall": round(float(fit_res["fit_wall_seconds"]), 3),
        "predict_wall": round(float(fit_res["predict_wall_seconds"]), 3),
    }

    if score:
        raw_metrics = dict(compute_metrics(y_val, y_pred))
        metrics: Dict[str, Any] = {
            **raw_metrics,
            "run_id": run_id,
            "mode": context["mode"],
            "classifier": classifier,
            "features": FEATURE_GROUP,
            "deterministic": bool(spec["deterministic"]),
            "n_train": int(x_train.shape[0]),
            "n_val": int(x_val.shape[0]),
            "selected_params": best_params,
            "cv_best_macro_f1": round(float(cv_result["best_score"]), 6),
            "cv_best_std": round(float(cv_result["best_std"]), 6),
            "cv_candidates": list(cv_result["candidates"]),
            "seconds": seconds,
        }
    else:
        row_sums = np.sum(proba, axis=1)
        metrics = {
            "run_id": run_id,
            "mode": context["mode"],
            "classifier": classifier,
            "features": FEATURE_GROUP,
            "deterministic": bool(spec["deterministic"]),
            "scored": False,
            "n_train": int(x_train.shape[0]),
            "n_val": int(x_val.shape[0]),
            "classes_in_val": sorted(int(c) for c in np.unique(y_val)),
            "proba_row_sum_min": float(np.min(row_sums)),
            "proba_row_sum_max": float(np.max(row_sums)),
            "selected_params": best_params,
            "seconds": seconds,
        }

    std_note = (
        "Mo hinh tat dinh chay 1 lan, khong co do lech chuan (H3)"
        if spec["deterministic"]
        else "Mo hinh ngau nhien chay 3 seed (42, 43, 44)"
    )

    config: Dict[str, Any] = {
        "run_id": run_id,
        "rq": RQ_NAME,
        "mode": context["mode"],
        "features": FEATURE_GROUP,
        "feature_params": feature_params(FEATURE_GROUP),
        "classifier_tag": classifier,
        "classifier": spec["class_name"],
        "deterministic": bool(spec["deterministic"]),
        "std_note": std_note,
        "preprocessing": {
            "scaler": "StandardScaler" if fit_res["use_scaler"] else "none",
            "fit_on": "train_only",
        },
        "class_weight_handling": {
            "mode": fit_res["class_weight_mode"],
            "note": fit_res["class_weight_note"],
        },
        "cv": {
            "scheme": "StratifiedGroupKFold",
            "n_splits": int(cv_result["n_splits"]),
            "shuffle": True,
            "random_state": int(cv_result["cv_seed"]),
            "group_column": "group_id",
            "param_grid": list(cv_result["param_grid"]),
            "selected_params": best_params,
            "selected_index": int(cv_result["best_index"]),
            "cv_cpu_seconds": round(float(cv_result["cv_cpu_seconds"]), 3),
            "cv_wall_seconds": round(float(cv_result["cv_wall_seconds"]), 3),
        },
        "hyperparameters": fit_res["params"],
        "seed": seed,
        "commit": context["commit"],
        "versions": context["versions"],
        "split": context["split"],
        "subset": context["subset"],
        "evaluation": {
            "train_split": "train",
            "eval_split": "val",
            "allow_test": False,
        },
        "extraction": {
            "chunk_size": CHUNK_SIZE,
            "train": {
                "n_images": int(train_ext["n_images"]),
                "glcm_nan_images": int(train_ext["glcm_nan_images"]),
            },
            "val": {
                "n_images": int(val_ext["n_images"]),
                "glcm_nan_images": int(val_ext["glcm_nan_images"]),
            },
        },
    }

    log_lines = [
        f"run_id={run_id}",
        f"mode={context['mode']}",
        f"features={FEATURE_GROUP}",
        f"classifier={classifier} ({spec['class_name']})",
        f"deterministic={spec['deterministic']}",
        f"std_note={std_note}",
        f"class_weight_note={fit_res['class_weight_note']}",
        f"scaler={'StandardScaler' if fit_res['use_scaler'] else 'none'}",
        f"selected_params={json.dumps(best_params, ensure_ascii=False)}",
        f"seed={seed}",
        f"n_train={x_train.shape[0]}",
        f"n_val={x_val.shape[0]}",
        f"GLCM correlation NaN (train): {train_ext['glcm_nan_images']}/{train_ext['n_images']} anh",
        f"GLCM correlation NaN (val): {val_ext['glcm_nan_images']}/{val_ext['n_images']} anh",
        f"Thoi gian trich (giay CPU) nhom {FEATURE_GROUP} (train): {float(train_ext['cpu_seconds'][FEATURE_GROUP]):.3f}",
        f"Thoi gian trich (giay CPU) nhom {FEATURE_GROUP} (val): {float(val_ext['cpu_seconds'][FEATURE_GROUP]):.3f}",
        f"Thoi gian CV 5-fold (giay CPU): {float(cv_result['cv_cpu_seconds']):.3f}",
        f"Thoi gian CV 5-fold (giay, dong ho tuong): {float(cv_result['cv_wall_seconds']):.3f}",
        f"Thoi gian fit (giay CPU): {float(fit_res['fit_cpu_seconds']):.3f}",
        f"Thoi gian fit (giay, dong ho tuong): {float(fit_res['fit_wall_seconds']):.3f}",
        f"Thoi gian du doan (giay, dong ho tuong): {float(fit_res['predict_wall_seconds']):.3f}",
        "classes_=[0, 1, 2, 3]",
    ]
    if score:
        log_lines.append(f"cv_best_macro_f1={cv_result['best_score']:.6f}")
        log_lines.append(f"macro_f1={metrics['macro_f1']}")

    write_run_outputs(
        run_dir=Path(out_root) / run_id,
        config=config,
        metrics=metrics,
        log_lines=log_lines,
        image_ids=image_ids_val,
        y_true=y_val,
        y_pred=y_pred,
        proba=proba,
    )
    return metrics


def mode_settings(mode: str) -> Dict[str, Any]:
    """Cung cấp cấu hình tham số tương ứng với từng chế độ chạy (t0, t1, full) của RQ2."""
    if mode == "t0":
        return {
            "limit_train": 400,
            "limit_val": 100,
            "subset_seed": 0,
            "classifiers": CLASSIFIERS,
            "seeds": (42,),
            "score": False,
            "out_subdir": "results_trial",
        }
    elif mode == "t1":
        return {
            "limit_train": None,
            "limit_val": None,
            "subset_seed": 0,
            "classifiers": ("svm",),
            "seeds": (42,),
            "score": False,
            "out_subdir": "results_trial",
        }
    elif mode == "full":
        return {
            "limit_train": None,
            "limit_val": None,
            "subset_seed": 0,
            "classifiers": CLASSIFIERS,
            "seeds": SEEDS,
            "score": True,
            "out_subdir": "results",
        }
    else:
        raise ValueError(
            f"Mode '{mode}' khong hop le. Cac mode hop le: {VALID_MODES}."
        )


def run_experiment(
    split_csv: Union[str, Path],
    data_root: Union[str, Path],
    out_root: Union[str, Path],
    mode: str,
    mode_config: Dict[str, Any],
    commit: str,
    versions: Dict[str, str],
    sha_path: Optional[Union[str, Path]] = None,
    param_grids: Optional[Mapping[str, Sequence[Mapping[str, Any]]]] = None,
    n_jobs: int = -1,
    expected_train_n: Optional[int] = EXPECTED_TRAIN_N,
    expected_val_n: Optional[int] = EXPECTED_VAL_N,
) -> Dict[str, Any]:
    """Điều phối toàn bộ thực nghiệm RQ2 trên nhóm đặc trưng 'ghep' (152 chiều)."""
    csv_path = Path(split_csv)
    if sha_path is not None:
        split_sha = verify_split_sha256(csv_path, Path(sha_path))
    else:
        hasher = hashlib.sha256()
        with open(csv_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        split_sha = hasher.hexdigest().lower()

    split_df = pd.read_csv(csv_path)
    required_cols = {"image_id", "label", "rel_image_path", "split", "group_id"}
    if not required_cols.issubset(split_df.columns):
        raise ValueError(
            f"Tep split CSV thieu cac cot bat buoc: {required_cols - set(split_df.columns)}."
        )

    train_rows = int((split_df["split"] == "train").sum())
    val_rows = int((split_df["split"] == "val").sum())

    if expected_train_n is not None and train_rows != expected_train_n:
        raise ValueError(
            f"So hang train thuc te ({train_rows}) khong khop ky vong ({expected_train_n})."
        )
    if expected_val_n is not None and val_rows != expected_val_n:
        raise ValueError(
            f"So hang val thuc te ({val_rows}) khong khop ky vong ({expected_val_n})."
        )

    train_imgs, image_ids_train, y_train, groups_train = load_split_images(
        split_df=split_df,
        split="train",
        data_root=data_root,
        limit=mode_config["limit_train"],
        subset_seed=mode_config["subset_seed"],
    )
    val_imgs, image_ids_val, y_val, _ = load_split_images(
        split_df=split_df,
        split="val",
        data_root=data_root,
        limit=mode_config["limit_val"],
        subset_seed=mode_config["subset_seed"],
    )

    train_features, info_train = extract_groups(
        train_imgs, groups=(FEATURE_GROUP,), chunk_size=CHUNK_SIZE
    )
    val_features, info_val = extract_groups(
        val_imgs, groups=(FEATURE_GROUP,), chunk_size=CHUNK_SIZE
    )

    x_tr = train_features[FEATURE_GROUP]
    x_v = val_features[FEATURE_GROUP]

    context: Dict[str, Any] = {
        "mode": mode,
        "commit": commit,
        "versions": versions,
        "split": {
            "file": str(split_csv),
            "sha256": split_sha,
            "train_rows": train_rows,
            "val_rows": val_rows,
        },
        "subset": {
            "limit_train": mode_config["limit_train"],
            "limit_val": mode_config["limit_val"],
            "subset_seed": mode_config["subset_seed"],
        },
        "extraction": {
            "train": info_train,
            "val": info_val,
        },
    }

    n_train = int(len(image_ids_train))
    n_val = int(len(image_ids_val))
    runs: List[str] = []
    runs_by_classifier: Dict[str, List[str]] = {}
    selected_hyperparameters: Dict[str, Dict[str, Any]] = {}
    cv_cpu_seconds_map: Dict[str, float] = {}
    fit_cpu_seconds_mean_map: Dict[str, float] = {}
    total_train_cpu_seconds_map: Dict[str, float] = {}

    out_root_path = Path(out_root)
    classifiers_to_run: Tuple[str, ...] = tuple(mode_config["classifiers"])
    configured_seeds: Tuple[int, ...] = tuple(mode_config["seeds"])

    for clf in classifiers_to_run:
        clf_grid = (
            param_grids[clf]
            if (param_grids is not None and clf in param_grids)
            else PARAM_GRIDS[clf]
        )
        cv_res = select_hyperparameters_cv(
            classifier=clf,
            x_train=x_tr,
            y_train=y_train,
            groups_train=groups_train,
            param_grid=clf_grid,
            n_splits=CV_SPLITS,
            cv_seed=CV_RANDOM_STATE,
            n_jobs=n_jobs,
        )
        selected_hyperparameters[clf] = dict(cv_res["best_params"])
        cv_cpu_seconds_map[clf] = round(float(cv_res["cv_cpu_seconds"]), 3)

        clf_seeds = seeds_for_classifier(clf, configured_seeds)
        clf_run_ids: List[str] = []
        fit_cpus: List[float] = []

        for seed in clf_seeds:
            m = run_one(
                classifier=clf,
                seed=seed,
                x_train=x_tr,
                y_train=y_train,
                x_val=x_v,
                y_val=y_val,
                image_ids_val=image_ids_val,
                cv_result=cv_res,
                out_root=out_root_path,
                context=context,
                score=bool(mode_config["score"]),
                n_jobs=n_jobs,
            )
            r_id = make_run_id(clf, seed, features=FEATURE_GROUP)
            runs.append(r_id)
            clf_run_ids.append(r_id)
            fit_cpus.append(float(m["seconds"]["fit_cpu"]))

        runs_by_classifier[clf] = clf_run_ids
        fit_cpu_seconds_mean_map[clf] = round(float(np.mean(fit_cpus)), 3)
        total_train_cpu_seconds_map[clf] = round(
            float(cv_res["cv_cpu_seconds"]) + float(np.sum(fit_cpus)), 3
        )

    extract_cpu_train = float(info_train["cpu_seconds"][FEATURE_GROUP])
    extract_cpu_val = float(info_val["cpu_seconds"][FEATURE_GROUP])
    extract_cpu_per_image = round(
        (extract_cpu_train + extract_cpu_val) / (n_train + n_val), 6
    )

    cost_rank = sorted(
        classifiers_to_run,
        key=lambda c: (total_train_cpu_seconds_map[c], CLASSIFIERS.index(c)),
    )

    return {
        "mode": mode,
        "commit": commit,
        "features": FEATURE_GROUP,
        "classifiers": list(classifiers_to_run),
        "seeds": list(configured_seeds),
        "deterministic_classifiers": [
            c for c in classifiers_to_run if CLASSIFIER_SPECS[c]["deterministic"]
        ],
        "runs_by_classifier": runs_by_classifier,
        "scored": bool(mode_config["score"]),
        "n_train": n_train,
        "n_val": n_val,
        "extract_cpu_seconds": {
            "train": {FEATURE_GROUP: extract_cpu_train},
            "val": {FEATURE_GROUP: extract_cpu_val},
        },
        "extract_cpu_seconds_per_image": {FEATURE_GROUP: extract_cpu_per_image},
        "selected_hyperparameters": selected_hyperparameters,
        "cv_cpu_seconds": cv_cpu_seconds_map,
        "fit_cpu_seconds_mean": fit_cpu_seconds_mean_map,
        "total_train_cpu_seconds": total_train_cpu_seconds_map,
        "cost_rank": cost_rank,
        "runs": runs,
    }


def find_data_root(input_root: Union[str, Path]) -> Path:
    """Xác định đường dẫn thư mục gốc chứa ảnh X-quang."""
    input_path = Path(input_root)
    candidates = [
        input_path / "datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset",
        input_path / "datasets/tawsifurrahman/covid19-radiography-database",
        input_path / "covid19-radiography-database/COVID-19_Radiography_Dataset",
        input_path / "covid19-radiography-database",
    ]
    for cand in candidates:
        if (cand / "COVID/images").is_dir():
            return cand

    for cand in input_path.rglob("COVID-19_Radiography_Dataset"):
        if (cand / "COVID/images").is_dir():
            return cand

    raise FileNotFoundError(
        f"Khong tim thay thu muc goc dataset trong {input_root}."
    )


def find_code_package(input_root: Union[str, Path]) -> Path:
    """Xác định thư mục chứa gói mã nguồn tải lên Kaggle thông qua tệp COMMIT."""
    input_path = Path(input_root)
    patterns = ["*/COMMIT", "*/*/COMMIT", "*/*/*/COMMIT"]
    for pat in patterns:
        matches = sorted(input_path.glob(pat))
        if matches:
            return matches[0].parent

    raise FileNotFoundError(
        f"Khong tim thay goi ma nguon qua tep COMMIT trong {input_root}."
    )


def build_code_package(
    repo_root: Union[str, Path],
    out_dir: Union[str, Path],
    commit: str,
    mode: str,
    dataset_id: str = "ductrannguyen/cxr-rq2-code",
) -> List[str]:
    """Đóng gói mã nguồn và metadata thành cấu trúc phẳng để đẩy lên dataset Kaggle cho RQ2."""
    if (
        not isinstance(commit, str)
        or len(commit) != 40
        or not all(c in "0123456789abcdef" for c in commit)
    ):
        raise ValueError(
            f"Commit phai la chuoi 40 ky tu thap luc phan chu thuong, nhan duoc: {commit!r}."
        )

    if mode not in VALID_MODES:
        raise ValueError(
            f"Mode '{mode}' khong hop le. Cac mode hop le: {VALID_MODES}."
        )

    out_path = Path(out_dir)
    if out_path.exists() and any(out_path.iterdir()):
        raise ValueError(
            f"Thu muc out_dir '{out_dir}' da ton tai va khong rong."
        )

    repo_path = Path(repo_root)

    for name in PACKAGE_SRC_FILES:
        src_file = repo_path / "src" / name
        if not src_file.is_file():
            raise FileNotFoundError(f"Thieu tep nguon: {src_file}.")

    for name in PACKAGE_SPLIT_FILES:
        split_file = repo_path / "splits" / name
        if not split_file.is_file():
            raise FileNotFoundError(f"Thieu tep split: {split_file}.")

    out_path.mkdir(parents=True, exist_ok=True)

    for name in PACKAGE_SRC_FILES:
        shutil.copyfile(repo_path / "src" / name, out_path / name)

    for name in PACKAGE_SPLIT_FILES:
        shutil.copyfile(repo_path / "splits" / name, out_path / name)

    with open(out_path / "COMMIT", "w", encoding="utf-8", newline="\n") as f:
        f.write(commit + "\n")

    with open(out_path / "MODE", "w", encoding="utf-8", newline="\n") as f:
        f.write(mode + "\n")

    title = dataset_id.split("/")[-1]
    metadata = {
        "title": title,
        "id": dataset_id,
        "licenses": [{"name": "other"}],
    }
    with open(
        out_path / "dataset-metadata.json", "w", encoding="utf-8", newline="\n"
    ) as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return sorted(p.name for p in out_path.iterdir())


def kaggle_main(
    input_root: Union[str, Path],
    working_root: Union[str, Path],
    package_dir: Optional[Union[str, Path]] = None,
    param_grids: Optional[Mapping[str, Sequence[Mapping[str, Any]]]] = None,
    n_jobs: int = -1,
    expected_train_n: Optional[int] = EXPECTED_TRAIN_N,
    expected_val_n: Optional[int] = EXPECTED_VAL_N,
) -> Dict[str, Any]:
    """Hàm điều phối thực thi chính của RQ2 bên trong môi trường kernel Kaggle."""
    versions = collect_versions()
    print("Danh sach phien ban:")
    for k, v in versions.items():
        print(f"  {k}: {v}")

    hard_expected = {k: v for k, v in EXPECTED_VERSIONS.items() if k in HARD_PINNED_PACKAGES}
    soft_expected = {k: v for k, v in EXPECTED_VERSIONS.items() if k not in HARD_PINNED_PACKAGES}
    for note in check_pinned_versions(versions, soft_expected):
        print(f"Luu y (khong dung chay): {note}")
    mismatches = check_pinned_versions(versions, hard_expected)
    if mismatches:
        for m in mismatches:
            print(f"Sai lech: {m}")
        raise RuntimeError(
            "Phat hien sai lech phien ban thu vien:\n" + "\n".join(mismatches)
        )

    input_path = Path(input_root)
    working_path = Path(working_root)

    if package_dir is None:
        pkg_path = find_code_package(input_path)
    else:
        pkg_path = Path(package_dir)

    commit = (pkg_path / "COMMIT").read_text(encoding="utf-8").strip()
    mode = (pkg_path / "MODE").read_text(encoding="utf-8").strip()

    if mode not in VALID_MODES:
        raise ValueError(
            f"Mode '{mode}' trong package khong hop le. Cac mode hop le: {VALID_MODES}."
        )

    data_root = find_data_root(input_path)
    settings = mode_settings(mode)
    out_root = working_path / settings["out_subdir"]

    summary = run_experiment(
        split_csv=pkg_path / "split_v1.csv",
        data_root=data_root,
        out_root=out_root,
        mode=mode,
        mode_config=settings,
        commit=commit,
        versions=versions,
        sha_path=pkg_path / "split_v1.sha256",
        param_grids=param_grids,
        n_jobs=n_jobs,
        expected_train_n=expected_train_n,
        expected_val_n=expected_val_n,
    )

    summary_file = working_path / f"summary_{mode}.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Hoan thanh chay mode: {mode}")
    print(f"  Runs: {summary['runs']}")
    print(f"  Cost rank: {summary['cost_rank']}")

    return summary
