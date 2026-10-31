"""Module điều phối thực thi huấn luyện Random Forest và đóng gói mã nguồn RQ1.

Trách nhiệm:
- Cung cấp runner chạy một run Random Forest cố định trên 4 nhóm đặc trưng cổ điển
  theo chuẩn H1 đến H7 của results/threshold_v3.md (phụ trách nhiệm vụ S3-04).
- Hỗ trợ các chế độ chạy thử nhỏ (t0, t1) và chạy lô hoàn chỉnh (full).
- Cung cấp tiện ích đóng gói mã nguồn và kernel Kaggle mỏng để chạy trên Kaggle.
"""

import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import time
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import yaml

from src.dataset import CLASS_NAMES, LABEL_TO_IDX, CXRDataset
from src.metrics import compute_metrics
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

RQ_NAME: str = "rq1"
CLASSIFIER_TAG: str = "rf"
FEATURE_GROUPS: Tuple[str, ...] = GROUP_NAMES
SEEDS: Tuple[int, ...] = (42, 43, 44)
N_ESTIMATORS: int = 500
CLASS_WEIGHT: str = "balanced_subsample"
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
    "rq1_runner.py",
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


def make_run_id(features: str, seed: int) -> str:
    """Tạo định danh duy nhất cho một lần chạy mô hình.

    Args:
        features: Tên nhóm đặc trưng.
        seed: Hạt giống ngẫu nhiên (số nguyên không âm).

    Returns:
        Chuỗi run_id có cấu trúc 'rq1_<features>_rf_s<seed>'.

    Raises:
        ValueError: Nếu tên nhóm đặc trưng không hợp lệ hoặc seed không hợp lệ.
    """
    if features not in FEATURE_GROUPS:
        raise ValueError(
            f"Nhom dac trung '{features}' khong hop le. Cac nhom hop le: {FEATURE_GROUPS}."
        )
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError(f"Seed phai la so nguyen khong am, nhan duoc: {seed!r}.")
    return f"{RQ_NAME}_{features}_{CLASSIFIER_TAG}_s{seed}"


def stratified_subset(
    labels: Sequence[str],
    n: int,
    seed: int,
    min_per_class: int = MIN_PER_CLASS,
) -> np.ndarray:
    """Lấy mẫu phân tầng theo nhãn đảm bảo số lượng mẫu tối thiểu cho mỗi lớp.

    Args:
        labels: Chuỗi nhãn của toàn bộ tập dữ liệu.
        n: Số lượng mẫu mong muốn lấy ra.
        seed: Hạt giống ngẫu nhiên.
        min_per_class: Số lượng mẫu tối thiểu mỗi lớp cần lấy.

    Returns:
        Mảng chỉ số nguyên int64 đã sắp xếp tăng dần theo thứ tự gốc.

    Raises:
        ValueError: Nếu n nhỏ hơn 1.
    """
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
    """Xác thực mã băm SHA256 của tệp phân chia dữ liệu CSV.

    Args:
        csv_path: Đường dẫn tới tệp CSV.
        sha_path: Đường dẫn tới tệp chứa mã băm SHA256 mong đợi.

    Returns:
        Mã băm SHA256 thực tế của tệp CSV (chuỗi chữ thường).

    Raises:
        ValueError: Nếu mã băm tính được không khớp mã băm kỳ vọng.
    """
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
) -> Tuple[Iterator[np.ndarray], List[str], np.ndarray]:
    """Nạp ảnh và nhãn cho một phân vùng dữ liệu hợp lệ (train hoặc val).

    Args:
        split_df: DataFrame chứa thông tin phân vùng dữ liệu.
        split: Tên phân vùng ('train' hoặc 'val').
        data_root: Đường dẫn thư mục gốc chứa ảnh.
        limit: Giới hạn số lượng mẫu cần nạp (tùy chọn).
        subset_seed: Hạt giống ngẫu nhiên khi lấy tập con.

    Returns:
        Tuple gồm (generator duyệt từng ảnh, danh sách image_id, mảng nhãn y dạng số nguyên).

    Raises:
        ValueError: Nếu split không thuộc VALID_SPLITS.
    """
    if split not in VALID_SPLITS:
        raise ValueError(
            f"Phan vung '{split}' khong hop le, chi chap nhan train hoac val (tap test bi khoa)."
        )

    df = split_df[split_df["split"] == split].reset_index(drop=True)
    if limit is not None:
        selected_idx = stratified_subset(
            df["label"].tolist(), limit, subset_seed
        )
        df = df.iloc[selected_idx].reset_index(drop=True)

    dataset = CXRDataset(df, split=split, data_root=data_root)
    image_ids = df["image_id"].tolist()
    y = df["label"].map(LABEL_TO_IDX).to_numpy(dtype=np.int64)

    def _yield_images() -> Iterator[np.ndarray]:
        for i in range(len(dataset)):
            img, _ = dataset[i]
            yield img

    return _yield_images(), image_ids, y


def collect_versions() -> Dict[str, str]:
    """Thu thập phiên bản của Python và các thư viện cốt lõi đã cài đặt.

    Returns:
        Dict ánh xạ tên gói hoặc môi trường sang chuỗi phiên bản.
    """
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
    """So sánh phiên bản hiện tại với danh sách phiên bản đã ghim.

    Args:
        versions: Dict phiên bản thu thập được.
        expected: Dict phiên bản kỳ vọng đã ghim.

    Returns:
        Danh sách các thông báo lỗi nếu có gói không khớp phiên bản.
    """
    mismatches: List[str] = []
    for pkg, exp_ver in expected.items():
        actual_ver = versions.get(pkg)
        if actual_ver != exp_ver:
            mismatches.append(
                f"Goi '{pkg}' khong khop phien ban: ky vong '{exp_ver}', thuc te '{actual_ver}'."
            )
    return mismatches


def feature_params(group: str) -> Dict[str, object]:
    """Trả về cấu hình tham số của từng nhóm đặc trưng theo kiểu Python gốc.

    Args:
        group: Tên nhóm đặc trưng ('hist', 'glcmlbp', 'hog', 'ghep').

    Returns:
        Dict cấu hình tham số đặc trưng.

    Raises:
        ValueError: Nếu tên nhóm đặc trưng không hợp lệ.
    """
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


def train_and_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    seed: int,
    n_estimators: int = N_ESTIMATORS,
    n_jobs: int = -1,
) -> Dict[str, object]:
    """Huấn luyện mô hình Random Forest và thực hiện dự đoán trên tập validation.

    Args:
        x_train: Ma trận đặc trưng tập huấn luyện.
        y_train: Mảng nhãn tập huấn luyện.
        x_val: Ma trận đặc trưng tập validation.
        seed: Hạt giống ngẫu nhiên.
        n_estimators: Số lượng cây trong rừng ngẫu nhiên.
        n_jobs: Số luồng song song (-1 là toàn bộ).

    Returns:
        Dict chứa y_pred, proba, params, fit_cpu_seconds, fit_wall_seconds, predict_wall_seconds.

    Raises:
        ValueError: Nếu y_train không đủ 4 lớp hoặc rf.classes_ khác [0, 1, 2, 3].
    """
    if set(np.unique(y_train)) != {0, 1, 2, 3}:
        raise ValueError(
            f"y_train phai chua day du 4 lop {{0, 1, 2, 3}}, thuc te co: {set(np.unique(y_train))}."
        )

    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight=CLASS_WEIGHT,
        random_state=seed,
        n_jobs=n_jobs,
    )

    t_fit_cpu_start = time.process_time()
    t_fit_wall_start = time.perf_counter()
    rf.fit(x_train, y_train)
    fit_cpu_seconds = time.process_time() - t_fit_cpu_start
    fit_wall_seconds = time.perf_counter() - t_fit_wall_start

    t_pred_wall_start = time.perf_counter()
    proba = rf.predict_proba(x_val).astype(np.float64)
    predict_wall_seconds = time.perf_counter() - t_pred_wall_start

    if rf.classes_.tolist() != [0, 1, 2, 3]:
        raise ValueError(
            f"rf.classes_ phai la [0, 1, 2, 3], thuc te nhan duoc: {rf.classes_.tolist()}."
        )

    y_pred = rf.classes_[np.argmax(proba, axis=1)].astype(np.int64)

    return {
        "y_pred": y_pred,
        "proba": proba,
        "params": rf.get_params(),
        "fit_cpu_seconds": float(fit_cpu_seconds),
        "fit_wall_seconds": float(fit_wall_seconds),
        "predict_wall_seconds": float(predict_wall_seconds),
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
    """Ghi đúng 4 tệp kết quả của một run vào thư mục run_dir.

    Args:
        run_dir: Thư mục lưu kết quả của run.
        config: Dict cấu hình thực nghiệm.
        metrics: Dict chỉ số đánh giá.
        log_lines: Danh sách các dòng nhật ký ghi lại quá trình chạy.
        image_ids: Danh sách mã định danh ảnh validation.
        y_true: Mảng nhãn thực tế.
        y_pred: Mảng nhãn dự đoán.
        proba: Ma trận xác suất dự đoán (n, 4).

    Returns:
        Dict ánh xạ tên tệp sang đối tượng Path.

    Raises:
        ValueError: Nếu độ dài các mảng không khớp nhau hoặc proba không đúng 4 cột.
    """
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
    group: str,
    seed: int,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    image_ids_val: List[str],
    out_root: Path,
    context: Dict[str, object],
    score: bool,
    n_estimators: int = N_ESTIMATORS,
    n_jobs: int = -1,
) -> Dict[str, object]:
    """Thực thi một run huấn luyện đơn lẻ cho một nhóm đặc trưng và một seed.

    Args:
        group: Tên nhóm đặc trưng.
        seed: Hạt giống ngẫu nhiên.
        x_train: Ma trận đặc trưng tập huấn luyện.
        y_train: Nhãn tập huấn luyện.
        x_val: Ma trận đặc trưng tập validation.
        y_val: Nhãn tập validation.
        image_ids_val: Danh sách image_id tập validation.
        out_root: Thư mục gốc lưu trữ kết quả.
        context: Dict ngữ cảnh môi trường và dữ liệu.
        score: Cờ cho biết có tính toán và lưu macro-F1 hay không.
        n_estimators: Số lượng cây trong Random Forest.
        n_jobs: Số luồng song song.

    Returns:
        Dict chỉ số đánh giá của run.
    """
    run_id = make_run_id(group, seed)
    fit_res = train_and_predict(
        x_train, y_train, x_val, seed, n_estimators=n_estimators, n_jobs=n_jobs
    )
    y_pred = fit_res["y_pred"]
    proba = fit_res["proba"]

    train_ext = context["extraction"]["train"]
    val_ext = context["extraction"]["val"]

    seconds = {
        "extract_cpu_train": round(float(train_ext["cpu_seconds"][group]), 3),
        "extract_cpu_val": round(float(val_ext["cpu_seconds"][group]), 3),
        "fit_cpu": round(float(fit_res["fit_cpu_seconds"]), 3),
        "fit_wall": round(float(fit_res["fit_wall_seconds"]), 3),
        "predict_wall": round(float(fit_res["predict_wall_seconds"]), 3),
    }

    if score:
        raw_metrics = dict(compute_metrics(y_val, y_pred))
        metrics = {
            **raw_metrics,
            "run_id": run_id,
            "mode": context["mode"],
            "n_train": int(x_train.shape[0]),
            "n_val": int(x_val.shape[0]),
            "seconds": seconds,
        }
    else:
        row_sums = np.sum(proba, axis=1)
        metrics = {
            "run_id": run_id,
            "mode": context["mode"],
            "scored": False,
            "n_train": int(x_train.shape[0]),
            "n_val": int(x_val.shape[0]),
            "classes_in_val": sorted(int(c) for c in np.unique(y_val)),
            "proba_row_sum_min": float(np.min(row_sums)),
            "proba_row_sum_max": float(np.max(row_sums)),
            "seconds": seconds,
        }

    config = {
        "run_id": run_id,
        "rq": RQ_NAME,
        "mode": context["mode"],
        "features": group,
        "feature_params": feature_params(group),
        "classifier": "RandomForestClassifier",
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
        f"features={group}",
        f"seed={seed}",
        f"n_train={x_train.shape[0]}",
        f"n_val={x_val.shape[0]}",
        f"GLCM correlation NaN (train): {train_ext['glcm_nan_images']}/{train_ext['n_images']} anh",
        f"GLCM correlation NaN (val): {val_ext['glcm_nan_images']}/{val_ext['n_images']} anh",
        f"Thoi gian trich (giay CPU) nhom {group} (train): {float(train_ext['cpu_seconds'][group]):.3f}",
        f"Thoi gian trich (giay CPU) nhom {group} (val): {float(val_ext['cpu_seconds'][group]):.3f}",
        f"Thoi gian fit (giay CPU): {float(fit_res['fit_cpu_seconds']):.3f}",
        f"Thoi gian fit (giay, dong ho tuong): {float(fit_res['fit_wall_seconds']):.3f}",
        f"Thoi gian du doan (giay, dong ho tuong): {float(fit_res['predict_wall_seconds']):.3f}",
        "classes_=[0, 1, 2, 3]",
    ]
    if score:
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


def mode_settings(mode: str) -> Dict[str, object]:
    """Cung cấp cấu hình tham số tương ứng với từng chế độ chạy (t0, t1, full).

    Args:
        mode: Tên chế độ chạy.

    Returns:
        Dict chứa các thiết lập của chế độ.

    Raises:
        ValueError: Nếu chế độ không hợp lệ.
    """
    if mode == "t0":
        return {
            "limit_train": 400,
            "limit_val": 100,
            "subset_seed": 0,
            "groups": FEATURE_GROUPS,
            "seeds": (42,),
            "score": False,
            "out_subdir": "results_trial",
        }
    elif mode == "t1":
        return {
            "limit_train": None,
            "limit_val": None,
            "subset_seed": 0,
            "groups": ("hog",),
            "seeds": (42,),
            "score": False,
            "out_subdir": "results_trial",
        }
    elif mode == "full":
        return {
            "limit_train": None,
            "limit_val": None,
            "subset_seed": 0,
            "groups": FEATURE_GROUPS,
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
    mode_config: Dict[str, object],
    commit: str,
    versions: Dict[str, str],
    sha_path: Optional[Union[str, Path]] = None,
    n_estimators: int = N_ESTIMATORS,
    n_jobs: int = -1,
    expected_train_n: Optional[int] = EXPECTED_TRAIN_N,
    expected_val_n: Optional[int] = EXPECTED_VAL_N,
) -> Dict[str, object]:
    """Điều phối toàn bộ thực nghiệm RQ1 theo cấu hình chế độ chỉ định.

    Args:
        split_csv: Đường dẫn tệp CSV phân chia dữ liệu.
        data_root: Thư mục chứa ảnh.
        out_root: Thư mục lưu kết quả đầu ra.
        mode: Tên chế độ thực thi ('t0', 't1', 'full').
        mode_config: Dict cấu hình chế độ sinh từ mode_settings.
        commit: Mã băm git commit tương ứng.
        versions: Dict phiên bản các gói phần mềm.
        sha_path: Đường dẫn tệp sha256 (tùy chọn).
        n_estimators: Số lượng cây trong Random Forest.
        n_jobs: Số luồng song song.
        expected_train_n: Số lượng mẫu train kỳ vọng để kiểm tra bảo vệ.
        expected_val_n: Số lượng mẫu val kỳ vọng để kiểm tra bảo vệ.

    Returns:
        Dict tóm tắt tổng kết thực nghiệm.

    Raises:
        ValueError: Nếu split_csv không hợp lệ hoặc số dòng train/val không khớp kỳ vọng.
    """
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
    required_cols = {"image_id", "label", "rel_image_path", "split"}
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

    train_imgs, image_ids_train, y_train = load_split_images(
        split_df=split_df,
        split="train",
        data_root=data_root,
        limit=mode_config["limit_train"],
        subset_seed=mode_config["subset_seed"],
    )
    val_imgs, image_ids_val, y_val = load_split_images(
        split_df=split_df,
        split="val",
        data_root=data_root,
        limit=mode_config["limit_val"],
        subset_seed=mode_config["subset_seed"],
    )

    train_features, info_train = extract_groups(
        train_imgs, groups=mode_config["groups"], chunk_size=CHUNK_SIZE
    )
    val_features, info_val = extract_groups(
        val_imgs, groups=mode_config["groups"], chunk_size=CHUNK_SIZE
    )

    context = {
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
    out_root_path = Path(out_root)

    for group in mode_config["groups"]:
        x_tr = train_features[group]
        x_v = val_features[group]
        for seed in mode_config["seeds"]:
            run_one(
                group=group,
                seed=seed,
                x_train=x_tr,
                y_train=y_train,
                x_val=x_v,
                y_val=y_val,
                image_ids_val=image_ids_val,
                out_root=out_root_path,
                context=context,
                score=mode_config["score"],
                n_estimators=n_estimators,
                n_jobs=n_jobs,
            )
            runs.append(make_run_id(group, seed))

    extract_cpu_seconds = {
        "train": {
            g: float(info_train["cpu_seconds"][g]) for g in mode_config["groups"]
        },
        "val": {
            g: float(info_val["cpu_seconds"][g]) for g in mode_config["groups"]
        },
    }

    extract_cpu_seconds_per_image = {
        g: round(
            (float(info_train["cpu_seconds"][g]) + float(info_val["cpu_seconds"][g]))
            / (n_train + n_val),
            6,
        )
        for g in mode_config["groups"]
    }

    cost_rank = sorted(
        mode_config["groups"],
        key=lambda g: (extract_cpu_seconds_per_image[g], GROUP_NAMES.index(g)),
    )

    return {
        "mode": mode,
        "commit": commit,
        "groups": list(mode_config["groups"]),
        "seeds": list(mode_config["seeds"]),
        "scored": bool(mode_config["score"]),
        "n_train": n_train,
        "n_val": n_val,
        "extract_cpu_seconds": extract_cpu_seconds,
        "extract_cpu_seconds_per_image": extract_cpu_seconds_per_image,
        "cost_rank": cost_rank,
        "runs": runs,
    }


def find_data_root(input_root: Union[str, Path]) -> Path:
    """Xác định đường dẫn thư mục gốc chứa ảnh X-quang.

    Args:
        input_root: Thư mục đầu vào để tìm kiếm.

    Returns:
        Đối tượng Path dẫn tới thư mục chứa ảnh hợp lệ.

    Raises:
        FileNotFoundError: Nếu không tìm thấy cấu trúc thư mục dữ liệu phù hợp.
    """
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
    """Xác định thư mục chứa gói mã nguồn tải lên Kaggle thông qua tệp COMMIT.

    Args:
        input_root: Thư mục đầu vào để tìm kiếm.

    Returns:
        Đối tượng Path dẫn tới thư mục chứa gói mã nguồn.

    Raises:
        FileNotFoundError: Nếu không tìm thấy tệp COMMIT.
    """
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
) -> List[str]:
    """Đóng gói mã nguồn và metadata thành cấu trúc phẳng để đẩy lên dataset Kaggle.

    Args:
        repo_root: Thư mục gốc của repository.
        out_dir: Thư mục đầu ra để tạo gói.
        commit: Mã băm git commit 40 ký tự thập lục phân chữ thường.
        mode: Chế độ chạy hợp lệ ('t0', 't1', 'full').

    Returns:
        Danh sách tên các tệp đã đóng gói theo thứ tự sắp xếp tăng dần.

    Raises:
        ValueError: Nếu commit hoặc mode không hợp lệ, hoặc out_dir đã tồn tại và không rỗng.
        FileNotFoundError: Nếu thiếu bất kỳ tệp nguồn hoặc tệp split nào.
    """
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

    metadata = {
        "title": "cxr-rq1-code",
        "id": "ductrannguyen/cxr-rq1-code",
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
    n_estimators: int = N_ESTIMATORS,
    expected_train_n: Optional[int] = EXPECTED_TRAIN_N,
    expected_val_n: Optional[int] = EXPECTED_VAL_N,
) -> Dict[str, object]:
    """Hàm điều phối thực thi chính bên trong môi trường kernel Kaggle.

    Args:
        input_root: Thư mục đầu vào /kaggle/input.
        working_root: Thư mục làm việc /kaggle/working.
        package_dir: Thư mục gói mã nguồn (tự tìm nếu None).
        n_estimators: Số lượng cây trong Random Forest.
        expected_train_n: Số lượng mẫu train kỳ vọng.
        expected_val_n: Số lượng mẫu val kỳ vọng.

    Returns:
        Dict tóm tắt tổng kết thực nghiệm.

    Raises:
        RuntimeError: Nếu phát hiện sai lệch phiên bản ghim.
        ValueError: Nếu mode trong tệp MODE không hợp lệ.
    """
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
        n_estimators=n_estimators,
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
