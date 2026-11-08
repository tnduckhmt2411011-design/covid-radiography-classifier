"""Module bootstrap.py

Trách nhiệm:
- Tính khoảng tin cậy bootstrap và bootstrap ghép cặp cho Macro-F1 giữa các mô hình RQ1 và RQ2.
- Xuất các bảng báo cáo R1, R2, R4, R5 theo quy định trong results/threshold_v3.md.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from src.metrics import DEFAULT_CLASS_NAMES


def macro_f1_from_labels(
    y_true: Union[Sequence[int], np.ndarray],
    y_pred: Union[Sequence[int], np.ndarray],
    num_classes: int = 4,
) -> float:
    """Tính Macro-F1 trực tiếp từ nhãn thực tế và nhãn dự đoán bằng np.bincount.

    Args:
        y_true: Nhãn thực tế (dạng số nguyên 0..num_classes-1).
        y_pred: Nhãn dự đoán (dạng số nguyên 0..num_classes-1).
        num_classes: Số lượng lớp (mặc định 4).

    Returns:
        float: Giá trị Macro-F1 (trung bình cộng F1 của các lớp).
    """
    y_true_arr = np.asarray(y_true, dtype=np.int64)
    y_pred_arr = np.asarray(y_pred, dtype=np.int64)

    idx = y_true_arr * num_classes + y_pred_arr
    cm = np.bincount(idx, minlength=num_classes * num_classes).reshape((num_classes, num_classes))

    tp = np.diag(cm)
    row_sum = np.sum(cm, axis=1)
    col_sum = np.sum(cm, axis=0)

    denom = row_sum + col_sum
    f1_per_class = np.zeros(num_classes, dtype=np.float64)
    mask = denom > 0
    f1_per_class[mask] = 2.0 * tp[mask] / denom[mask]

    return float(np.mean(f1_per_class))


def _validate_predictions_df(
    df: pd.DataFrame,
    run_id: str,
    expected_n: Optional[int] = 3174,
) -> pd.DataFrame:
    """Kiểm tra tính hợp lệ của DataFrame preds_val.csv và sắp xếp theo image_id."""
    req_cols = {"image_id", "y_true", "y_pred"}
    if not req_cols.issubset(df.columns):
        missing = req_cols - set(df.columns)
        raise ValueError(f"Run {run_id}: thiếu các cột bắt buộc {missing}")

    if df["image_id"].duplicated().any():
        raise ValueError(f"Run {run_id}: cột image_id bị trùng lặp")

    if expected_n is not None and len(df) != expected_n:
        raise ValueError(f"Run {run_id}: số dòng {len(df)} khác kỳ vọng {expected_n}")

    for col in ["y_true", "y_pred"]:
        if df[col].isna().any():
            raise ValueError(f"Run {run_id}: cột {col} chứa giá trị NaN/null")
        try:
            col_series = pd.to_numeric(df[col], errors="raise")
        except Exception as e:
            raise ValueError(f"Run {run_id}: cột {col} không thể chuyển thành số: {e}")

        int_col = col_series.astype(np.int64)
        if not np.array_equal(col_series, int_col):
            raise ValueError(f"Run {run_id}: cột {col} chứa giá trị không phải số nguyên")

        if not ((int_col >= 0) & (int_col <= 3)).all():
            raise ValueError(f"Run {run_id}: cột {col} chứa giá trị ngoài phạm vi 0..3")

        df[col] = int_col

    df = df.sort_values(by="image_id").reset_index(drop=True)
    return df


def load_predictions(
    results_dir: Union[str, Path],
    features: str,
    seed: int,
    expected_n: Optional[int] = 3174,
) -> pd.DataFrame:
    """Đọc tệp preds_val.csv của một run RQ1 và kiểm tra tính hợp lệ dữ liệu.

    Args:
        results_dir: Thư mục gốc chứa kết quả các run.
        features: Tên nhóm đặc trưng (hist, glcmlbp, hog, ghep).
        seed: Seed huấn luyện (42, 43, 44).
        expected_n: Số dòng kỳ vọng (3174 với tập validation, None nếu bỏ qua).

    Returns:
        pd.DataFrame: DataFrame đã sắp xếp theo image_id.
    """
    run_id = f"rq1_{features}_rf_s{seed}"
    csv_path = Path(results_dir) / run_id / "preds_val.csv"

    if not csv_path.is_file():
        raise ValueError(f"Run {run_id}: không tìm thấy tệp {csv_path}")

    df = pd.read_csv(csv_path)
    return _validate_predictions_df(df, run_id=run_id, expected_n=expected_n)


def load_rq2_predictions(
    results_dir: Union[str, Path],
    features: str,
    classifier: str,
    seed: int,
    expected_n: Optional[int] = 3174,
) -> pd.DataFrame:
    """Đọc tệp preds_val.csv của một run RQ2 và kiểm tra tính hợp lệ dữ liệu.

    Args:
        results_dir: Thư mục gốc chứa kết quả các run.
        features: Tên nhóm đặc trưng cố định (mặc định 'ghep').
        classifier: Tên bộ phân loại (lr, knn, dt, rf, svm, gb).
        seed: Seed huấn luyện (42, 43, 44).
        expected_n: Số dòng kỳ vọng (3174 với tập validation, None nếu bỏ qua).

    Returns:
        pd.DataFrame: DataFrame đã sắp xếp theo image_id.
    """
    run_id = f"rq2_{features}_{classifier}_s{seed}"
    csv_path = Path(results_dir) / run_id / "preds_val.csv"

    if not csv_path.is_file():
        raise ValueError(f"Run {run_id}: không tìm thấy tệp {csv_path}")

    df = pd.read_csv(csv_path)
    return _validate_predictions_df(df, run_id=run_id, expected_n=expected_n)


def load_rq3_predictions(
    results_dir: Union[str, Path],
    scenario: str,
    seed: int = 42,
    expected_n: Optional[int] = 3174,
) -> pd.DataFrame:
    """Đọc tệp preds_val.csv của một run RQ3 và kiểm tra tính hợp lệ dữ liệu.

    Args:
        results_dir: Thư mục gốc chứa kết quả các run.
        scenario: Tên kịch bản RQ3 (orig_to_orig, orig_to_lung, orig_to_out, lung_to_lung, out_to_out).
        seed: Seed huấn luyện (mặc định 42).
        expected_n: Số dòng kỳ vọng (3174 với tập validation, None nếu bỏ qua).

    Returns:
        pd.DataFrame: DataFrame đã sắp xếp theo image_id.
    """
    run_id = f"rq3_ghep_svm_{scenario}_s{seed}"
    csv_path = Path(results_dir) / run_id / "preds_val.csv"

    if not csv_path.is_file():
        raise ValueError(f"Run {run_id}: không tìm thấy tệp {csv_path}")

    df = pd.read_csv(csv_path)
    return _validate_predictions_df(df, run_id=run_id, expected_n=expected_n)


def align_predictions(
    runs: Dict[str, Dict[int, pd.DataFrame]]
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Căn chỉnh dự đoán giữa tất cả các run để đảm bảo tính nhất quán.

    Args:
        runs: Dict features/classifier -> Dict seed -> DataFrame.

    Returns:
        Tuple chứa:
        - y_true: mảng shape (n,)
        - preds: dict features/classifier -> mảng shape (n_seeds, n) theo thứ tự seed tăng dần.
    """
    if not runs:
        raise ValueError("runs không được để trống")

    ref_image_ids: Optional[np.ndarray] = None
    ref_y_true: Optional[np.ndarray] = None
    preds_dict: Dict[str, np.ndarray] = {}

    for feat, seed_dict in runs.items():
        if not seed_dict:
            raise ValueError(f"Nhóm đặc trưng '{feat}' không chứa seed nào")

        sorted_seeds = sorted(seed_dict.keys())
        feat_preds: List[np.ndarray] = []

        for s in sorted_seeds:
            df = seed_dict[s]
            if not df["image_id"].is_monotonic_increasing:
                df = df.sort_values(by="image_id").reset_index(drop=True)

            img_ids = df["image_id"].to_numpy()
            y_t = df["y_true"].to_numpy(dtype=np.int64)
            y_p = df["y_pred"].to_numpy(dtype=np.int64)

            if ref_image_ids is None:
                ref_image_ids = img_ids
                ref_y_true = y_t
            else:
                if len(img_ids) != len(ref_image_ids) or not np.array_equal(img_ids, ref_image_ids):
                    raise ValueError(
                        f"Tập image_id của nhóm '{feat}' seed {s} không khớp với các run khác"
                    )
                if not np.array_equal(y_t, ref_y_true):
                    raise ValueError(
                        f"y_true của nhóm '{feat}' seed {s} không khớp với các run khác"
                    )

            feat_preds.append(y_p)

        preds_dict[feat] = np.stack(feat_preds, axis=0)

    assert ref_y_true is not None
    return ref_y_true, preds_dict


def paired_bootstrap_diff(
    y_true: Union[Sequence[int], np.ndarray],
    preds_a: np.ndarray,
    preds_b: np.ndarray,
    n_boot: int = 2000,
    rng_seed: int = 42,
) -> Dict[str, Union[int, float, bool, np.ndarray]]:
    """Ước lượng khoảng tin cậy bootstrap ghép cặp cho hiệu số Macro-F1 (A trừ B).

    Args:
        y_true: Mảng nhãn thực tế shape (n,).
        preds_a: Mảng dự đoán cấu hình A shape (n_seeds_a, n) hoặc (n,).
        preds_b: Mảng dự đoán cấu hình B shape (n_seeds_b, n) hoặc (n,).
        n_boot: Số vòng lặp bootstrap (mặc định 2000).
        rng_seed: Seed cho bộ sinh số ngẫu nhiên.

    Returns:
        Dict chứa n, n_boot, rng_seed, point_a, point_b, point_diff, ci_low, ci_high,
        contains_zero, boot_diffs.
    """
    y_true_arr = np.asarray(y_true, dtype=np.int64)
    n = len(y_true_arr)

    arr_a = np.asarray(preds_a, dtype=np.int64)
    arr_b = np.asarray(preds_b, dtype=np.int64)

    if arr_a.ndim == 1:
        arr_a = arr_a.reshape(1, -1)
    if arr_b.ndim == 1:
        arr_b = arr_b.reshape(1, -1)

    s_a = arr_a.shape[0]
    s_b = arr_b.shape[0]

    point_a = float(np.mean([macro_f1_from_labels(y_true_arr, arr_a[s]) for s in range(s_a)]))
    point_b = float(np.mean([macro_f1_from_labels(y_true_arr, arr_b[s]) for s in range(s_b)]))
    point_diff = float(point_a - point_b)

    rng = np.random.default_rng(rng_seed)
    boot_diffs = np.empty(n_boot, dtype=np.float64)

    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        y_boot = y_true_arr[idx]
        boot_a = np.mean([macro_f1_from_labels(y_boot, arr_a[s, idx]) for s in range(s_a)])
        boot_b = np.mean([macro_f1_from_labels(y_boot, arr_b[s, idx]) for s in range(s_b)])
        boot_diffs[b] = boot_a - boot_b

    ci_low, ci_high = np.percentile(boot_diffs, [2.5, 97.5])
    ci_low = float(ci_low)
    ci_high = float(ci_high)
    contains_zero = bool(ci_low <= 0.0 <= ci_high)

    return {
        "n": n,
        "n_boot": n_boot,
        "rng_seed": rng_seed,
        "point_a": point_a,
        "point_b": point_b,
        "point_diff": point_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "contains_zero": contains_zero,
        "boot_diffs": boot_diffs,
    }


def bootstrap_ci_macro_f1(
    y_true: Union[Sequence[int], np.ndarray],
    preds: np.ndarray,
    n_boot: int = 2000,
    rng_seed: int = 42,
) -> Dict[str, Union[int, float, np.ndarray]]:
    """Ước lượng khoảng tin cậy 95% bootstrap cho Macro-F1 của một cấu hình.

    Args:
        y_true: Mảng nhãn thực tế shape (n,).
        preds: Mảng dự đoán shape (n_seeds, n) hoặc (n,).
        n_boot: Số vòng lặp bootstrap.
        rng_seed: Seed sinh số ngẫu nhiên.

    Returns:
        Dict chứa n, n_boot, rng_seed, point, ci_low, ci_high, boot_stats.
    """
    y_true_arr = np.asarray(y_true, dtype=np.int64)
    n = len(y_true_arr)

    arr = np.asarray(preds, dtype=np.int64)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    s = arr.shape[0]

    point = float(np.mean([macro_f1_from_labels(y_true_arr, arr[i]) for i in range(s)]))

    rng = np.random.default_rng(rng_seed)
    boot_stats = np.empty(n_boot, dtype=np.float64)

    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        y_boot = y_true_arr[idx]
        boot_stats[b] = np.mean([macro_f1_from_labels(y_boot, arr[i, idx]) for i in range(s)])

    ci_low, ci_high = np.percentile(boot_stats, [2.5, 97.5])
    ci_low = float(ci_low)
    ci_high = float(ci_high)

    return {
        "n": n,
        "n_boot": n_boot,
        "rng_seed": rng_seed,
        "point": point,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "boot_stats": boot_stats,
    }


def r2_submatrix(cm: Union[List[List[int]], np.ndarray]) -> np.ndarray:
    """Trích xuất ma trận con 2x2 giữa Normal và Lung Opacity từ ma trận 4x4.

    Hàng = nhãn thật, Cột = dự đoán.
    Lớp 1: Lung_Opacity, Lớp 2: Normal.
    [[cm[1][1], cm[1][2]],
     [cm[2][1], cm[2][2]]]
    """
    arr = np.asarray(cm)
    if arr.shape != (4, 4):
        raise ValueError(f"Ma trận nhầm lẫn phải có dạng 4x4, nhận được {arr.shape}")
    return np.array([[arr[1, 1], arr[1, 2]], [arr[2, 1], arr[2, 2]]], dtype=arr.dtype)


def sampling_error(p: float, n: int) -> float:
    """Tính sai số chuẩn lấy mẫu xấp xỉ sqrt(p*(1-p)/n)."""
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p={p} nằm ngoài khoảng [0, 1]")
    if n <= 0:
        raise ValueError(f"n={n} phải lớn hơn 0")
    return float(math.sqrt(p * (1.0 - p) / n))


def r5_text(threshold_path: Union[str, Path] = "results/threshold_v3.md") -> str:
    """Đọc tệp threshold_v3.md và trích xuất đúng một dòng bắt đầu bằng '- R5 '."""
    path = Path(threshold_path)
    if not path.is_file():
        raise ValueError(f"Không tìm thấy tệp {path}")
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f if line.startswith("- R5 ")]
    if len(lines) != 1:
        raise ValueError(f"Kỳ vọng đúng 1 dòng bắt đầu bằng '- R5 ', tìm thấy {len(lines)} dòng")
    return lines[0]


def build_report(
    results_dir: Union[str, Path],
    out_dir: Union[str, Path],
    features: Sequence[str] = ("hist", "glcmlbp", "hog", "ghep"),
    seeds: Sequence[int] = (42, 43, 44),
    reference: str = "hist",
    n_boot: int = 2000,
    rng_seed: int = 42,
    expected_n: Optional[int] = 3174,
    threshold_path: Union[str, Path] = "results/threshold_v3.md",
) -> Dict[str, Path]:
    """Tạo toàn bộ 8 tệp báo cáo R1, R2, R4, R5 cho RQ1 theo đặc tả."""
    if reference not in features:
        raise ValueError(f"Nhóm reference '{reference}' không nằm trong danh sách features {features}")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    runs: Dict[str, Dict[int, pd.DataFrame]] = {}
    for feat in features:
        runs[feat] = {}
        for s in seeds:
            runs[feat][s] = load_predictions(results_dir, feat, s, expected_n=expected_n)

    y_true, preds = align_predictions(runs)
    n = len(y_true)
    num_classes = len(DEFAULT_CLASS_NAMES)
    n_viral = int(np.sum(y_true == 3))

    per_seed_rows: List[Dict[str, Union[str, int, float]]] = []
    confusion_matrices: Dict[str, List[List[int]]] = {}
    r2_rows: List[Dict[str, Union[str, int]]] = []
    r4_rows: List[Dict[str, Union[str, int, float]]] = []

    for feat in features:
        for s in sorted(seeds):
            run_id = f"rq1_{feat}_rf_s{s}"
            y_pred = runs[feat][s]["y_pred"].to_numpy(dtype=np.int64)

            idx = y_true * num_classes + y_pred
            cm = np.bincount(idx, minlength=num_classes * num_classes).reshape((num_classes, num_classes))
            confusion_matrices[run_id] = cm.tolist()

            tp = np.diag(cm)
            row_sum = np.sum(cm, axis=1)
            col_sum = np.sum(cm, axis=0)

            prec = np.where(col_sum > 0, tp / col_sum, 0.0)
            rec = np.where(row_sum > 0, tp / row_sum, 0.0)
            denom = row_sum + col_sum
            f1 = np.where(denom > 0, 2.0 * tp / denom, 0.0)
            macro_f1 = float(np.mean(f1))

            row: Dict[str, Union[str, int, float]] = {
                "run_id": run_id,
                "features": feat,
                "seed": s,
                "macro_f1": macro_f1,
            }
            for c_idx, c_name in enumerate(DEFAULT_CLASS_NAMES):
                row[f"precision_{c_name}"] = float(prec[c_idx])
                row[f"recall_{c_name}"] = float(rec[c_idx])
                row[f"f1_{c_name}"] = float(f1[c_idx])
            per_seed_rows.append(row)

            r2_rows.append({
                "run_id": run_id,
                "features": feat,
                "seed": s,
                "LO_to_LO": int(cm[1, 1]),
                "LO_to_Normal": int(cm[1, 2]),
                "Normal_to_LO": int(cm[2, 1]),
                "Normal_to_Normal": int(cm[2, 2]),
            })

            acc = float(np.sum(tp) / n) if n > 0 else 0.0
            se_all = sampling_error(acc, n) if n > 0 else 0.0
            rec_viral = float(rec[3])
            se_viral = sampling_error(rec_viral, n_viral) if n_viral > 0 else 0.0

            r4_rows.append({
                "run_id": run_id,
                "features": feat,
                "seed": s,
                "p_accuracy": acc,
                "n_all": n,
                "se_all": se_all,
                "p_recall_viral": rec_viral,
                "n_viral": n_viral,
                "se_viral": se_viral,
            })

    df_per_seed = pd.DataFrame(per_seed_rows)
    summary_rows: List[Dict[str, Union[str, int, float]]] = []

    for feat in features:
        sub = df_per_seed[df_per_seed["features"] == feat]
        n_s = len(sub)
        f1_vals = sub["macro_f1"].to_numpy()
        f1_mean = float(np.mean(f1_vals))
        f1_std = float(np.std(f1_vals, ddof=1)) if n_s > 1 else 0.0

        boot_ci = bootstrap_ci_macro_f1(y_true, preds[feat], n_boot=n_boot, rng_seed=rng_seed)
        ci95_low = boot_ci["ci_low"]
        ci95_high = boot_ci["ci_high"]

        s_row: Dict[str, Union[str, int, float]] = {
            "features": feat,
            "n_seeds": n_s,
            "macro_f1_mean": f1_mean,
            "macro_f1_std": f1_std,
            "ci95_low": ci95_low,
            "ci95_high": ci95_high,
        }

        for metric in ["precision", "recall", "f1"]:
            for c_name in DEFAULT_CLASS_NAMES:
                vals = sub[f"{metric}_{c_name}"].to_numpy()
                s_row[f"{metric}_{c_name}_mean"] = float(np.mean(vals))
                s_row[f"{metric}_{c_name}_std"] = float(np.std(vals, ddof=1)) if n_s > 1 else 0.0

        summary_rows.append(s_row)

    boot_vs_ref_rows: List[Dict[str, Union[str, int, float, bool]]] = []
    for cand in features:
        if cand == reference:
            continue
        res_pair = paired_bootstrap_diff(
            y_true, preds[cand], preds[reference], n_boot=n_boot, rng_seed=rng_seed
        )
        boot_vs_ref_rows.append({
            "candidate": cand,
            "reference": reference,
            "point_candidate": res_pair["point_a"],
            "point_reference": res_pair["point_b"],
            "point_diff": res_pair["point_diff"],
            "ci_low": res_pair["ci_low"],
            "ci_high": res_pair["ci_high"],
            "contains_zero": res_pair["contains_zero"],
            "n": res_pair["n"],
            "n_boot": res_pair["n_boot"],
            "rng_seed": res_pair["rng_seed"],
        })

    r5_content = r5_text(threshold_path)

    try:
        sklearn_version = importlib.metadata.version("scikit-learn")
    except Exception:
        sklearn_version = "unknown"

    config_data = {
        "features": list(features),
        "seeds": list(seeds),
        "reference": reference,
        "n": int(n),
        "n_boot": int(n_boot),
        "rng_seed": int(rng_seed),
        "expected_n": int(expected_n) if expected_n is not None else None,
        "numpy_version": str(np.__version__),
        "pandas_version": str(pd.__version__),
        "scikit_learn_version": str(sklearn_version),
    }

    r1_per_seed_path = out_path / "r1_per_seed.csv"
    df_per_seed.to_csv(r1_per_seed_path, index=False)

    r1_summary_path = out_path / "r1_summary.csv"
    pd.DataFrame(summary_rows).to_csv(r1_summary_path, index=False)

    r1_cm_path = out_path / "r1_confusion_matrices.json"
    with open(r1_cm_path, "w", encoding="utf-8") as f:
        json.dump(confusion_matrices, f, indent=2)

    r1_boot_path = out_path / "r1_bootstrap_vs_reference.csv"
    pd.DataFrame(boot_vs_ref_rows).to_csv(r1_boot_path, index=False)

    r2_path = out_path / "r2_normal_lung_opacity.csv"
    pd.DataFrame(r2_rows).to_csv(r2_path, index=False)

    r4_path = out_path / "r4_sampling_error.csv"
    pd.DataFrame(r4_rows).to_csv(r4_path, index=False)

    r5_path = out_path / "r5_gioi_han.md"
    with open(r5_path, "w", encoding="utf-8") as f:
        f.write(r5_content + "\n")

    config_path = out_path / "bootstrap_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    return {
        "r1_per_seed.csv": r1_per_seed_path,
        "r1_summary.csv": r1_summary_path,
        "r1_confusion_matrices.json": r1_cm_path,
        "r1_bootstrap_vs_reference.csv": r1_boot_path,
        "r2_normal_lung_opacity.csv": r2_path,
        "r4_sampling_error.csv": r4_path,
        "r5_gioi_han.md": r5_path,
        "bootstrap_config.json": config_path,
    }


def build_rq2_report(
    results_dir: Union[str, Path],
    out_dir: Union[str, Path],
    features: str = "ghep",
    classifiers: Sequence[str] = ("lr", "knn", "dt", "rf", "svm", "gb"),
    seeds: Sequence[int] = (42, 43, 44),
    deterministic_classifiers: Sequence[str] = ("lr", "knn", "svm"),
    reference: str = "rf",
    n_boot: int = 2000,
    rng_seed: int = 42,
    expected_n: Optional[int] = 3174,
    threshold_path: Union[str, Path] = "results/threshold_v3.md",
) -> Dict[str, Path]:
    """Tạo toàn bộ 8 tệp báo cáo R1, R2, R4, R5 cho RQ2 theo đặc tả."""
    if reference not in classifiers:
        raise ValueError(f"Bộ phân loại reference '{reference}' không nằm trong danh sách {classifiers}")
    if not seeds:
        raise ValueError("seeds không được để trống")

    det_set = set(deterministic_classifiers)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    runs: Dict[str, Dict[int, pd.DataFrame]] = {}
    for clf in classifiers:
        runs[clf] = {}
        clf_seeds = [seeds[0]] if clf in det_set else list(seeds)
        for s in clf_seeds:
            runs[clf][s] = load_rq2_predictions(
                results_dir, features=features, classifier=clf, seed=s, expected_n=expected_n
            )

    y_true, preds = align_predictions(runs)
    n = len(y_true)
    num_classes = len(DEFAULT_CLASS_NAMES)
    n_viral = int(np.sum(y_true == 3))

    per_seed_rows: List[Dict[str, Union[str, int, float]]] = []
    confusion_matrices: Dict[str, List[List[int]]] = {}
    r2_rows: List[Dict[str, Union[str, int]]] = []
    r4_rows: List[Dict[str, Union[str, int, float]]] = []

    for clf in classifiers:
        clf_seeds = [seeds[0]] if clf in det_set else sorted(seeds)
        for s in clf_seeds:
            run_id = f"rq2_{features}_{clf}_s{s}"
            y_pred = runs[clf][s]["y_pred"].to_numpy(dtype=np.int64)

            idx = y_true * num_classes + y_pred
            cm = np.bincount(idx, minlength=num_classes * num_classes).reshape((num_classes, num_classes))
            confusion_matrices[run_id] = cm.tolist()

            tp = np.diag(cm)
            row_sum = np.sum(cm, axis=1)
            col_sum = np.sum(cm, axis=0)

            prec = np.where(col_sum > 0, tp / col_sum, 0.0)
            rec = np.where(row_sum > 0, tp / row_sum, 0.0)
            denom = row_sum + col_sum
            f1 = np.where(denom > 0, 2.0 * tp / denom, 0.0)
            macro_f1 = float(np.mean(f1))

            row: Dict[str, Union[str, int, float]] = {
                "run_id": run_id,
                "features": features,
                "classifier": clf,
                "seed": s,
                "macro_f1": macro_f1,
            }
            for c_idx, c_name in enumerate(DEFAULT_CLASS_NAMES):
                row[f"precision_{c_name}"] = float(prec[c_idx])
                row[f"recall_{c_name}"] = float(rec[c_idx])
                row[f"f1_{c_name}"] = float(f1[c_idx])
            per_seed_rows.append(row)

            r2_rows.append({
                "run_id": run_id,
                "features": features,
                "classifier": clf,
                "seed": s,
                "LO_to_LO": int(cm[1, 1]),
                "LO_to_Normal": int(cm[1, 2]),
                "Normal_to_LO": int(cm[2, 1]),
                "Normal_to_Normal": int(cm[2, 2]),
            })

            acc = float(np.sum(tp) / n) if n > 0 else 0.0
            se_all = sampling_error(acc, n) if n > 0 else 0.0
            rec_viral = float(rec[3])
            se_viral = sampling_error(rec_viral, n_viral) if n_viral > 0 else 0.0

            r4_rows.append({
                "run_id": run_id,
                "features": features,
                "classifier": clf,
                "seed": s,
                "p_accuracy": acc,
                "n_all": n,
                "se_all": se_all,
                "p_recall_viral": rec_viral,
                "n_viral": n_viral,
                "se_viral": se_viral,
            })

    df_per_seed = pd.DataFrame(per_seed_rows)
    summary_rows: List[Dict[str, Union[str, int, float, bool]]] = []

    for clf in classifiers:
        sub = df_per_seed[df_per_seed["classifier"] == clf]
        n_s = len(sub)
        is_det = bool(clf in det_set)
        f1_vals = sub["macro_f1"].to_numpy()
        f1_mean = float(np.mean(f1_vals))
        f1_std = float(np.std(f1_vals, ddof=1)) if n_s > 1 else 0.0

        boot_ci = bootstrap_ci_macro_f1(y_true, preds[clf], n_boot=n_boot, rng_seed=rng_seed)
        ci95_low = boot_ci["ci_low"]
        ci95_high = boot_ci["ci_high"]

        s_row: Dict[str, Union[str, int, float, bool]] = {
            "features": features,
            "classifier": clf,
            "is_deterministic": is_det,
            "n_seeds": n_s,
            "macro_f1_mean": f1_mean,
            "macro_f1_std": f1_std,
            "ci95_low": ci95_low,
            "ci95_high": ci95_high,
        }

        for metric in ["precision", "recall", "f1"]:
            for c_name in DEFAULT_CLASS_NAMES:
                vals = sub[f"{metric}_{c_name}"].to_numpy()
                s_row[f"{metric}_{c_name}_mean"] = float(np.mean(vals))
                s_row[f"{metric}_{c_name}_std"] = float(np.std(vals, ddof=1)) if n_s > 1 else 0.0

        summary_rows.append(s_row)

    boot_vs_ref_rows: List[Dict[str, Union[str, int, float, bool]]] = []
    for cand in classifiers:
        if cand == reference:
            continue
        res_pair = paired_bootstrap_diff(
            y_true, preds[cand], preds[reference], n_boot=n_boot, rng_seed=rng_seed
        )
        boot_vs_ref_rows.append({
            "candidate": cand,
            "reference": reference,
            "point_candidate": res_pair["point_a"],
            "point_reference": res_pair["point_b"],
            "point_diff": res_pair["point_diff"],
            "ci_low": res_pair["ci_low"],
            "ci_high": res_pair["ci_high"],
            "contains_zero": res_pair["contains_zero"],
            "n": res_pair["n"],
            "n_boot": res_pair["n_boot"],
            "rng_seed": res_pair["rng_seed"],
        })

    r5_content = r5_text(threshold_path)

    try:
        sklearn_version = importlib.metadata.version("scikit-learn")
    except Exception:
        sklearn_version = "unknown"

    config_data = {
        "rq": "rq2",
        "features": features,
        "classifiers": list(classifiers),
        "seeds": list(seeds),
        "deterministic_classifiers": list(deterministic_classifiers),
        "reference": reference,
        "n": int(n),
        "n_boot": int(n_boot),
        "rng_seed": int(rng_seed),
        "expected_n": int(expected_n) if expected_n is not None else None,
        "numpy_version": str(np.__version__),
        "pandas_version": str(pd.__version__),
        "scikit_learn_version": str(sklearn_version),
    }

    r1_per_seed_path = out_path / "r1_per_seed.csv"
    df_per_seed.to_csv(r1_per_seed_path, index=False)

    r1_summary_path = out_path / "r1_summary.csv"
    pd.DataFrame(summary_rows).to_csv(r1_summary_path, index=False)

    r1_cm_path = out_path / "r1_confusion_matrices.json"
    with open(r1_cm_path, "w", encoding="utf-8") as f:
        json.dump(confusion_matrices, f, indent=2)

    r1_boot_path = out_path / "r1_bootstrap_vs_reference.csv"
    pd.DataFrame(boot_vs_ref_rows).to_csv(r1_boot_path, index=False)

    r2_path = out_path / "r2_normal_lung_opacity.csv"
    pd.DataFrame(r2_rows).to_csv(r2_path, index=False)

    r4_path = out_path / "r4_sampling_error.csv"
    pd.DataFrame(r4_rows).to_csv(r4_path, index=False)

    r5_path = out_path / "r5_gioi_han.md"
    with open(r5_path, "w", encoding="utf-8") as f:
        f.write(r5_content + "\n")

    config_path = out_path / "bootstrap_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    return {
        "r1_per_seed.csv": r1_per_seed_path,
        "r1_summary.csv": r1_summary_path,
        "r1_confusion_matrices.json": r1_cm_path,
        "r1_bootstrap_vs_reference.csv": r1_boot_path,
        "r2_normal_lung_opacity.csv": r2_path,
        "r4_sampling_error.csv": r4_path,
        "r5_gioi_han.md": r5_path,
        "bootstrap_config.json": config_path,
    }


def build_rq3_report(
    results_dir: Union[str, Path],
    out_dir: Union[str, Path],
    scenarios: Sequence[str] = (
        "orig_to_orig",
        "lung_to_lung",
        "out_to_out",
        "orig_to_lung",
        "orig_to_out",
    ),
    seed: int = 42,
    reference: str = "orig_to_orig",
    n_boot: int = 2000,
    rng_seed: int = 42,
    expected_n: Optional[int] = 3174,
    threshold_path: Union[str, Path] = "results/threshold_v3.md",
) -> Dict[str, Path]:
    """Tạo toàn bộ các tệp báo cáo R1, R2, R3, R4, R5 cho RQ3 theo đặc tả."""
    if reference not in scenarios:
        raise ValueError(
            f"Kịch bản reference '{reference}' không nằm trong danh sách {scenarios}"
        )

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    runs: Dict[str, Dict[int, pd.DataFrame]] = {}
    for sc in scenarios:
        runs[sc] = {
            seed: load_rq3_predictions(
                results_dir, scenario=sc, seed=seed, expected_n=expected_n
            )
        }

    y_true, preds = align_predictions(runs)
    n = len(y_true)
    num_classes = len(DEFAULT_CLASS_NAMES)
    n_viral = int(np.sum(y_true == 3))

    per_scenario_rows: List[Dict[str, Union[str, int, float]]] = []
    confusion_matrices: Dict[str, List[List[int]]] = {}
    r2_rows: List[Dict[str, Union[str, int]]] = []
    r4_rows: List[Dict[str, Union[str, int, float]]] = []
    summary_rows: List[Dict[str, Union[str, int, float, bool]]] = []

    for sc in scenarios:
        run_id = f"rq3_ghep_svm_{sc}_s{seed}"
        y_pred = runs[sc][seed]["y_pred"].to_numpy(dtype=np.int64)

        idx = y_true * num_classes + y_pred
        cm = np.bincount(idx, minlength=num_classes * num_classes).reshape(
            (num_classes, num_classes)
        )
        confusion_matrices[run_id] = cm.tolist()

        tp = np.diag(cm)
        row_sum = np.sum(cm, axis=1)
        col_sum = np.sum(cm, axis=0)

        prec = np.where(col_sum > 0, tp / col_sum, 0.0)
        rec = np.where(row_sum > 0, tp / row_sum, 0.0)
        denom = row_sum + col_sum
        f1 = np.where(denom > 0, 2.0 * tp / denom, 0.0)
        macro_f1 = float(np.mean(f1))

        row: Dict[str, Union[str, int, float]] = {
            "run_id": run_id,
            "scenario": sc,
            "features": "ghep",
            "classifier": "svm",
            "seed": seed,
            "macro_f1": macro_f1,
        }
        for c_idx, c_name in enumerate(DEFAULT_CLASS_NAMES):
            row[f"precision_{c_name}"] = float(prec[c_idx])
            row[f"recall_{c_name}"] = float(rec[c_idx])
            row[f"f1_{c_name}"] = float(f1[c_idx])
        per_scenario_rows.append(row)

        boot_ci = bootstrap_ci_macro_f1(
            y_true, preds[sc], n_boot=n_boot, rng_seed=rng_seed
        )
        s_row: Dict[str, Union[str, int, float, bool]] = {
            "scenario": sc,
            "features": "ghep",
            "classifier": "svm",
            "seed": seed,
            "is_deterministic": True,
            "n_seeds": 1,
            "macro_f1": macro_f1,
            "ci95_low": boot_ci["ci_low"],
            "ci95_high": boot_ci["ci_high"],
        }
        for c_idx, c_name in enumerate(DEFAULT_CLASS_NAMES):
            s_row[f"precision_{c_name}"] = float(prec[c_idx])
            s_row[f"recall_{c_name}"] = float(rec[c_idx])
            s_row[f"f1_{c_name}"] = float(f1[c_idx])
        summary_rows.append(s_row)

        r2_rows.append({
            "run_id": run_id,
            "scenario": sc,
            "features": "ghep",
            "classifier": "svm",
            "seed": seed,
            "LO_to_LO": int(cm[1, 1]),
            "LO_to_Normal": int(cm[1, 2]),
            "Normal_to_LO": int(cm[2, 1]),
            "Normal_to_Normal": int(cm[2, 2]),
        })

        acc = float(np.sum(tp) / n) if n > 0 else 0.0
        se_all = sampling_error(acc, n) if n > 0 else 0.0
        rec_viral = float(rec[3])
        se_viral = sampling_error(rec_viral, n_viral) if n_viral > 0 else 0.0

        r4_rows.append({
            "run_id": run_id,
            "scenario": sc,
            "features": "ghep",
            "classifier": "svm",
            "seed": seed,
            "p_accuracy": acc,
            "n_all": n,
            "se_all": se_all,
            "p_recall_viral": rec_viral,
            "n_viral": n_viral,
            "se_viral": se_viral,
        })

    # Phép so sánh ghép cặp so với tham chiếu (orig_to_orig)
    boot_vs_ref_rows: List[Dict[str, Union[str, int, float, bool]]] = []
    for cand in scenarios:
        if cand == reference:
            continue
        res_pair = paired_bootstrap_diff(
            y_true, preds[cand], preds[reference], n_boot=n_boot, rng_seed=rng_seed
        )
        boot_vs_ref_rows.append({
            "candidate": cand,
            "reference": reference,
            "point_candidate": res_pair["point_a"],
            "point_reference": res_pair["point_b"],
            "point_diff": res_pair["point_diff"],
            "ci_low": res_pair["ci_low"],
            "ci_high": res_pair["ci_high"],
            "contains_zero": res_pair["contains_zero"],
            "n": res_pair["n"],
            "n_boot": res_pair["n_boot"],
            "rng_seed": res_pair["rng_seed"],
        })

    # Phép so sánh kiểm tra lối tắt R3 (các cặp tương phản chính)
    shortcut_pairs = [
        ("lung_to_lung", "orig_to_orig"),
        ("lung_to_lung", "out_to_out"),
        ("orig_to_orig", "out_to_out"),
        ("orig_to_orig", "orig_to_lung"),
        ("orig_to_orig", "orig_to_out"),
    ]
    shortcut_rows: List[Dict[str, Union[str, int, float, bool]]] = []
    for sc_a, sc_b in shortcut_pairs:
        if sc_a in preds and sc_b in preds:
            res_sc = paired_bootstrap_diff(
                y_true, preds[sc_a], preds[sc_b], n_boot=n_boot, rng_seed=rng_seed
            )
            shortcut_rows.append({
                "scenario_a": sc_a,
                "scenario_b": sc_b,
                "point_a": res_sc["point_a"],
                "point_b": res_sc["point_b"],
                "point_diff": res_sc["point_diff"],
                "ci_low": res_sc["ci_low"],
                "ci_high": res_sc["ci_high"],
                "contains_zero": res_sc["contains_zero"],
                "n": res_sc["n"],
                "n_boot": res_sc["n_boot"],
                "rng_seed": res_sc["rng_seed"],
            })

    r5_content = r5_text(threshold_path)

    try:
        sklearn_version = importlib.metadata.version("scikit-learn")
    except Exception:
        sklearn_version = "unknown"

    config_data = {
        "rq": "rq3",
        "features": "ghep",
        "classifier": "svm",
        "seed": seed,
        "scenarios": list(scenarios),
        "reference": reference,
        "n": int(n),
        "n_boot": int(n_boot),
        "rng_seed": int(rng_seed),
        "expected_n": int(expected_n) if expected_n is not None else None,
        "numpy_version": str(np.__version__),
        "pandas_version": str(pd.__version__),
        "scikit_learn_version": str(sklearn_version),
    }

    r1_per_sc_path = out_path / "r1_per_scenario.csv"
    pd.DataFrame(per_scenario_rows).to_csv(r1_per_sc_path, index=False)

    r1_summary_path = out_path / "r1_summary.csv"
    pd.DataFrame(summary_rows).to_csv(r1_summary_path, index=False)

    r1_cm_path = out_path / "r1_confusion_matrices.json"
    with open(r1_cm_path, "w", encoding="utf-8") as f:
        json.dump(confusion_matrices, f, indent=2)

    r1_boot_path = out_path / "r1_bootstrap_vs_reference.csv"
    pd.DataFrame(boot_vs_ref_rows).to_csv(r1_boot_path, index=False)

    r3_sc_path = out_path / "r3_shortcut_bootstrap.csv"
    pd.DataFrame(shortcut_rows).to_csv(r3_sc_path, index=False)

    r2_path = out_path / "r2_normal_lung_opacity.csv"
    pd.DataFrame(r2_rows).to_csv(r2_path, index=False)

    r4_path = out_path / "r4_sampling_error.csv"
    pd.DataFrame(r4_rows).to_csv(r4_path, index=False)

    r5_path = out_path / "r5_gioi_han.md"
    with open(r5_path, "w", encoding="utf-8") as f:
        f.write(r5_content + "\n")

    config_path = out_path / "bootstrap_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    return {
        "r1_per_scenario.csv": r1_per_sc_path,
        "r1_summary.csv": r1_summary_path,
        "r1_confusion_matrices.json": r1_cm_path,
        "r1_bootstrap_vs_reference.csv": r1_boot_path,
        "r3_shortcut_bootstrap.csv": r3_sc_path,
        "r2_normal_lung_opacity.csv": r2_path,
        "r4_sampling_error.csv": r4_path,
        "r5_gioi_han.md": r5_path,
        "bootstrap_config.json": config_path,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Hàm chính xử lý tham số dòng lệnh và khởi chạy build_report."""
    parser = argparse.ArgumentParser(
        description="Script bootstrap ghép cặp và lập báo cáo RQ1 (R1, R2, R4, R5)."
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Thư mục chứa kết quả các run",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="results/report_rq1",
        help="Thư mục xuất báo cáo",
    )
    parser.add_argument(
        "--features",
        nargs="+",
        default=["hist", "glcmlbp", "hog", "ghep"],
        help="Danh sách nhóm đặc trưng",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[42, 43, 44],
        help="Danh sách seed",
    )
    parser.add_argument(
        "--reference",
        type=str,
        default="hist",
        help="Nhóm đặc trưng làm mốc so sánh",
    )
    parser.add_argument(
        "--n-boot",
        type=int,
        default=2000,
        help="Số lần rút mẫu bootstrap",
    )
    parser.add_argument(
        "--rng-seed",
        type=int,
        default=42,
        help="Seed cho bộ sinh số ngẫu nhiên",
    )
    parser.add_argument(
        "--expected-n",
        type=int,
        default=3174,
        help="Số ảnh kỳ vọng trong tập validation",
    )
    parser.add_argument(
        "--threshold-path",
        type=str,
        default="results/threshold_v3.md",
        help="Đường dẫn tới threshold_v3.md",
    )

    args = parser.parse_args(argv)
    build_report(
        results_dir=args.results_dir,
        out_dir=args.out_dir,
        features=args.features,
        seeds=args.seeds,
        reference=args.reference,
        n_boot=args.n_boot,
        rng_seed=args.rng_seed,
        expected_n=args.expected_n,
        threshold_path=args.threshold_path,
    )
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
