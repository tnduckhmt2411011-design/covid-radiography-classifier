"""Đánh giá tập test MỘT lần duy nhất cho mô hình đã đóng băng (S5-04, S5-05).

Đây là module DUY NHẤT trong repo được phép đọc split == "test" (qua allow_test=True tường minh).

Mô hình đóng băng (theo results/rq3_shortcut_learning_conclusion.md và D1 trong
docs/superpowers/specs/2026-11-09-s504-final-test-eval-design.md):
StandardScaler + SVC(kernel='rbf', C=10.0, gamma='scale', class_weight='balanced',
probability=True, random_state=42) trên nhóm đặc trưng 'ghep' (152 chiều), ảnh gốc 299x299,
chỉ huấn luyện trên train.

Hai chế độ:
- 'dry': chạy đầy đủ train -> val, kiểm G5 thật; KHÔNG đọc test, KHÔNG ghi UNLOCK_RECORD.json.
- 'final': G1 -> G2 -> G3 -> G4 -> fit (một lần) -> G5 -> G6 -> đọc test -> dự đoán bằng đúng mô hình
  đã fit ở G5 -> báo cáo.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Mapping, Tuple, Union

import cv2
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import yaml

from src.bootstrap import bootstrap_ci_macro_f1, macro_f1_from_labels
from src.dataset import LABEL_TO_IDX
from src.features_hog_ghep import extract_groups
from src.metrics import DEFAULT_CLASS_NAMES, compute_metrics
from src.rq2_runner import CHUNK_SIZE, feature_params, find_data_root
from src.rq3_runner import FROZEN_CLASSIFIER, FROZEN_FEATURES, FROZEN_SEED, FROZEN_SVM_PARAMS

EXPECTED_SPLIT_SHA256: str = "f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98"
EXPECTED_SPLIT_SIZES: Dict[str, int] = {"train": 14815, "val": 3174, "test": 3176}
REFERENCE_VAL_MACRO_F1: float = 0.9024
G5_TOLERANCE: float = 0.002
# SHA-256 của chuỗi xác nhận mở khóa do người dùng gõ (bản rõ KHÔNG lưu trong repo).
CONFIRM_STRING_SHA256: str = "PENDING_USER_REGISTRATION"
FINAL_DIRNAME: str = "final_test"
DRY_DIRNAME: str = "dry"
UNLOCK_RECORD_NAME: str = "UNLOCK_RECORD.json"
CONFIRM_FILE_NAME: str = "CONFIRM_FINAL"

FINAL_PACKAGE_SRC_FILES: Tuple[str, ...] = (
    "dataset.py",
    "metrics.py",
    "bootstrap.py",
    "features_hist_glcm_lbp.py",
    "features_hog_ghep.py",
    "rq1_runner.py",
    "rq2_runner.py",
    "rq3_runner.py",
    "final_test_runner.py",
)
FINAL_PACKAGE_SPLIT_FILES: Tuple[str, ...] = (
    "split_v1.csv",
    "split_v1.sha256",
)


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def check_split_integrity(
    split_csv: Union[str, Path],
    expected_sha256: str = EXPECTED_SPLIT_SHA256,
    expected_sizes: Mapping[str, int] = EXPECTED_SPLIT_SIZES,
) -> str:
    """G1: kiểm mã băm SHA256 và số dòng từng split của split_v1.csv (chỉ đọc manifest, không đọc ảnh)."""
    csv_path = Path(split_csv)
    actual_sha = _sha256_file(csv_path)
    if actual_sha != expected_sha256.strip().lower():
        raise ValueError(
            f"G1: SHA256 cua {csv_path} ({actual_sha}) khac ky vong ({expected_sha256})."
        )
    counts = pd.read_csv(csv_path, usecols=["split"])["split"].value_counts().to_dict()
    for split, expected_n in expected_sizes.items():
        actual_n = int(counts.get(split, 0))
        if actual_n != int(expected_n):
            raise ValueError(
                f"G1: so dong split '{split}' la {actual_n}, ky vong {expected_n}."
            )
    return actual_sha


def _json_norm(obj: Any) -> Any:
    return json.loads(json.dumps(obj))


def _get_path(cfg: Mapping[str, Any], path: Tuple[str, ...]) -> Any:
    node: Any = cfg
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            raise ValueError(f"G2: cau hinh tham chieu thieu truong '{'.'.join(path)}'.")
        node = node[key]
    return node


def check_frozen_config(reference_config: Mapping[str, Any]) -> None:
    """G2: cấu hình tham chiếu phải khớp tuyệt đối với hằng số đóng băng."""
    expected: Dict[Tuple[str, ...], Any] = {
        ("features",): FROZEN_FEATURES,
        ("classifier_tag",): FROZEN_CLASSIFIER,
        ("classifier",): "SVC",
        ("seed",): FROZEN_SEED,
        ("train_mask_mode",): "original",
        ("eval_mask_mode",): "original",
        ("preprocessing", "scaler"): "StandardScaler",
        ("evaluation", "allow_test"): False,
        ("split", "sha256"): EXPECTED_SPLIT_SHA256,
    }
    for path, want in expected.items():
        got = _get_path(reference_config, path)
        if got != want:
            raise ValueError(f"G2: '{'.'.join(path)}' = {got!r}, ky vong {want!r}.")

    got_hp = _json_norm(_get_path(reference_config, ("hyperparameters",)))
    want_hp = _json_norm(dict(FROZEN_SVM_PARAMS))
    if got_hp != want_hp:
        raise ValueError(f"G2: hyperparameters = {got_hp!r}, ky vong {want_hp!r}.")

    got_fp = _json_norm(_get_path(reference_config, ("feature_params",)))
    want_fp = _json_norm(feature_params(FROZEN_FEATURES))
    if got_fp != want_fp:
        raise ValueError("G2: feature_params khac tham so trich dac trung da dong bang.")


def check_not_already_unlocked(out_dir: Union[str, Path]) -> None:
    """G3: từ chối nếu UNLOCK_RECORD.json đã tồn tại trong thư mục đầu ra.

    Lưu ý: trên Kaggle, /kaggle/working không được giữ lại giữa các lần chạy nên G3 chỉ là
    chốt chặn theo quy trình trong cùng một thư mục đầu ra; không phải biện pháp ngăn tuyệt đối.
    """
    record = Path(out_dir) / FINAL_DIRNAME / UNLOCK_RECORD_NAME
    if record.exists():
        raise RuntimeError(
            f"G3: da ton tai {record}; tap test da duoc mo khoa, tu choi chay lan hai."
        )


def check_confirm_final(
    pkg_dir: Union[str, Path],
    expected_sha256: str = CONFIRM_STRING_SHA256,
) -> str:
    """G4: CONFIRM_FINAL phải chứa đúng chuỗi cố định do người dùng gõ (so khớp theo SHA-256).

    Chỉ cắt CR/LF ở cuối; mọi ký tự khác phải khớp tuyệt đối. Trả về SHA-256 của nội dung đã cắt.
    """
    confirm_path = Path(pkg_dir) / CONFIRM_FILE_NAME
    if not confirm_path.is_file():
        raise PermissionError(f"G4: thieu tep {CONFIRM_FILE_NAME} trong goi ma nguon.")
    text = confirm_path.read_bytes().rstrip(b"\r\n")
    actual = hashlib.sha256(text).hexdigest()
    if not text or not hmac.compare_digest(actual, expected_sha256.strip().lower()):
        raise PermissionError(f"G4: noi dung {CONFIRM_FILE_NAME} khong khop chuoi xac nhan da dang ky.")
    return actual


def write_unlock_record(
    final_dir: Union[str, Path],
    *,
    commit: str,
    split_sha256: str,
    val_macro_f1: float,
    confirm_sha256: str,
) -> Path:
    """G6: ghi UNLOCK_RECORD.json và flush + fsync TRƯỚC khi nạp ảnh test đầu tiên."""
    final_path = Path(final_dir)
    final_path.mkdir(parents=True, exist_ok=True)
    record_path = final_path / UNLOCK_RECORD_NAME
    if record_path.exists():
        raise RuntimeError(f"G3: da ton tai {record_path}; khong ghi de ban ghi mo khoa.")
    record = {
        "utc_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": commit,
        "split_sha256": split_sha256,
        "val_macro_f1": float(val_macro_f1),
        "confirm_sha256": confirm_sha256,
    }
    with open(record_path, "x", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    return record_path


def fit_frozen_model(x_train: np.ndarray, y_train: np.ndarray) -> Tuple[StandardScaler, SVC]:
    """Fit StandardScaler (chỉ trên train) và SVC đóng băng; được gọi đúng MỘT lần trong mỗi lần chạy."""
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_train)
    clf = SVC(**FROZEN_SVM_PARAMS)
    clf.fit(x_scaled, y_train)
    return scaler, clf


def predict_with_model(
    scaler: StandardScaler,
    clf: SVC,
    x: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Dự đoán nhãn và xác suất bằng mô hình đã fit (không fit lại)."""
    x_scaled = scaler.transform(x)
    y_pred = clf.predict(x_scaled).astype(np.int64)
    proba = clf.predict_proba(x_scaled)
    return y_pred, proba


def check_val_reproduction(
    val_macro_f1: float,
    reference: float = REFERENCE_VAL_MACRO_F1,
    tolerance: float = G5_TOLERANCE,
) -> None:
    """G5: Macro-F1 val tái lập phải bằng giá trị tham chiếu với |Δ| <= tolerance."""
    diff = round(abs(float(val_macro_f1) - float(reference)), 10)
    if diff > tolerance:
        raise RuntimeError(
            f"G5: Macro-F1 val tai lap = {val_macro_f1:.4f}, tham chieu {reference:.4f}, "
            f"|delta| = {diff:.4f} > {tolerance}; dung truoc khi doc test."
        )


def load_split_features(
    split_df: pd.DataFrame,
    split: str,
    dataset_root: Union[str, Path],
    *,
    allow_test: bool = False,
) -> Tuple[np.ndarray, List[str], np.ndarray, Dict[str, Any]]:
    """Đọc ảnh gốc xám 299x299 của một split và trích đặc trưng 'ghep' (152 chiều).

    split == 'test' chỉ được phép khi allow_test=True (do run_final_test truyền sau cổng G6).
    """
    if split not in ("train", "val", "test"):
        raise ValueError(f"Split '{split}' khong hop le, chi chap nhan train, val hoac test.")
    if split == "test" and not allow_test:
        raise PermissionError("Tap test bi khoa: can allow_test=True (chi sau cong G6).")

    sub_df = split_df[split_df["split"] == split].reset_index(drop=True)
    root = Path(dataset_root)
    image_ids = [str(x) for x in sub_df["image_id"].tolist()]
    rel_imgs = [str(x) for x in sub_df["rel_image_path"].tolist()]
    y = np.array([LABEL_TO_IDX[str(lbl)] for lbl in sub_df["label"]], dtype=np.int64)

    def _gen():
        for rel in rel_imgs:
            img_path = root / rel
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Khong the doc anh: {img_path}")
            if img.shape != (299, 299):
                raise ValueError(f"Kich thuoc anh {img_path} la {img.shape}, ky vong (299, 299).")
            yield img

    feat_dict, info = extract_groups(_gen(), groups=(FROZEN_FEATURES,), chunk_size=CHUNK_SIZE)
    return feat_dict[FROZEN_FEATURES], image_ids, y, info


def build_final_report(
    y_true: Union[Sequence[int], np.ndarray],
    y_pred: Union[Sequence[int], np.ndarray],
    val_macro_f1: float,
    *,
    n_boot: int = 2000,
    rng_seed: int = 42,
    threshold_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Tổng hợp báo cáo đánh giá cuối cùng trên tập test (S5-05).

    Quy tắc D4: Báo cáo đúng số; mọi lời giải thích chỉ là giả thuyết chưa kiểm chứng,
    không suy diễn nguyên nhân (không dùng trường 'cause' hay 'explanation').
    """
    y_true_arr = np.asarray(y_true, dtype=np.int64)
    y_pred_arr = np.asarray(y_pred, dtype=np.int64)

    metrics = compute_metrics(y_true_arr, y_pred_arr, class_names=DEFAULT_CLASS_NAMES)
    ci_res = bootstrap_ci_macro_f1(y_true_arr, y_pred_arr, n_boot=n_boot, rng_seed=rng_seed)

    cm = metrics["confusion_matrix"]
    r2_normal_lung_opacity = {
        "LO_to_LO": int(cm[1][1]),
        "LO_to_Normal": int(cm[1][2]),
        "Normal_to_LO": int(cm[2][1]),
        "Normal_to_Normal": int(cm[2][2]),
    }

    r4_sampling_error = {
        "n_all": int(len(y_true_arr)),
        "ci_width": float(ci_res["ci_high"] - ci_res["ci_low"]),
        "n_boot": int(n_boot),
        "rng_seed": int(rng_seed),
    }

    test_macro_f1 = float(ci_res["point"])
    val_macro_f1_flt = float(val_macro_f1)

    report: Dict[str, Any] = {
        "macro_f1": test_macro_f1,
        "ci95_low": float(ci_res["ci_low"]),
        "ci95_high": float(ci_res["ci_high"]),
        "accuracy": float(metrics["accuracy"]),
        "per_class": metrics["per_class"],
        "confusion_matrix": cm,
        "r2_normal_lung_opacity": r2_normal_lung_opacity,
        "r4_sampling_error": r4_sampling_error,
        "val_macro_f1": val_macro_f1_flt,
        "test_minus_val": float(test_macro_f1 - val_macro_f1_flt),
        "interpretation_note": (
            "Moi loi giai thich ve su khac biet giua val va test deu la "
            "gia thuyet chua kiem chung; khong suy dien nguyen nhan."
        ),
    }
    return report


def run_final_test(
    *,
    mode: str,
    dataset_root: Union[str, Path],
    split_csv: Union[str, Path],
    reference_dir: Union[str, Path],
    pkg_dir: Union[str, Path],
    out_dir: Union[str, Path],
    commit: str,
    threshold_path: Optional[Union[str, Path]] = None,
    feature_loader: Any = load_split_features,
    expected_split_sha256: str = EXPECTED_SPLIT_SHA256,
    expected_split_sizes: Mapping[str, int] = EXPECTED_SPLIT_SIZES,
    reference_val_macro_f1: float = REFERENCE_VAL_MACRO_F1,
    g5_tolerance: float = G5_TOLERANCE,
    expected_confirm_sha256: str = CONFIRM_STRING_SHA256,
    n_boot: int = 2000,
    rng_seed: int = 42,
) -> Dict[str, Any]:
    """Thực thi pipeline đánh giá (dry hoặc final) với đầy đủ các cổng bảo vệ."""
    if mode not in ("dry", "final"):
        raise ValueError(f"Che do '{mode}' khong hop le, chi chap nhan 'dry' hoac 'final'.")

    # G1: kiểm tra split_v1.csv
    split_sha = check_split_integrity(
        split_csv,
        expected_sha256=expected_split_sha256,
        expected_sizes=expected_split_sizes,
    )

    # G2: kiểm tra cấu hình tham chiếu
    ref_path = Path(reference_dir) / "config.yaml"
    ref_config = yaml.safe_load(ref_path.read_text(encoding="utf-8"))
    check_frozen_config(ref_config)

    # G3, G4: kiểm tra trước khi nạp bất kỳ đặc trưng nào (kể cả train/val)
    confirm_sha = ""
    if mode == "final":
        check_not_already_unlocked(out_dir)
        confirm_sha = check_confirm_final(pkg_dir, expected_sha256=expected_confirm_sha256)

    # Nạp train và val (không nạp test)
    split_df = pd.read_csv(split_csv)
    x_tr, ids_tr, y_tr, info_tr = feature_loader(split_df, "train", dataset_root, allow_test=False)
    x_va, ids_va, y_va, info_va = feature_loader(split_df, "val", dataset_root, allow_test=False)

    # Fit mô hình duy nhất 1 lần
    scaler, clf = fit_frozen_model(x_tr, y_tr)

    # Dự đoán trên val
    y_pred_va, proba_va = predict_with_model(scaler, clf, x_va)
    val_macro_f1 = float(macro_f1_from_labels(y_va, y_pred_va))

    # G5: kiểm tra Macro-F1 val tái lập
    check_val_reproduction(val_macro_f1, reference=reference_val_macro_f1, tolerance=g5_tolerance)

    if mode == "dry":
        dry_dir = Path(out_dir) / DRY_DIRNAME
        dry_dir.mkdir(parents=True, exist_ok=True)
        summary = {
            "mode": "dry",
            "split_sha256": split_sha,
            "n_train": len(y_tr),
            "n_val": len(y_va),
            "val_macro_f1": val_macro_f1,
            "reference_val_macro_f1": float(reference_val_macro_f1),
            "g5_passed": True,
            "test_read": False,
            "utc_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        (dry_dir / "dry_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    # mode == "final"
    final_dir = Path(out_dir) / FINAL_DIRNAME
    final_dir.mkdir(parents=True, exist_ok=True)

    # G6: Ghi UNLOCK_RECORD.json TRƯỚC TIÊN (chốt chặn nếu hạ tầng gặp sự cố sau đó)
    write_unlock_record(
        final_dir,
        commit=commit,
        split_sha256=split_sha,
        val_macro_f1=val_macro_f1,
        confirm_sha256=confirm_sha,
    )

    # Đọc test và dự đoán bằng ĐÚNG mô hình đã fit ở G5
    x_te, ids_te, y_te, info_te = feature_loader(split_df, "test", dataset_root, allow_test=True)
    y_pred_te, proba_te = predict_with_model(scaler, clf, x_te)

    # Tính toán báo cáo
    report = build_final_report(
        y_te,
        y_pred_te,
        val_macro_f1,
        n_boot=n_boot,
        rng_seed=rng_seed,
        threshold_path=threshold_path,
    )
    metrics = compute_metrics(y_te, y_pred_te, class_names=DEFAULT_CLASS_NAMES)

    # Ghi toàn bộ kết quả vào final_dir
    (final_dir / "final_test_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (final_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (final_dir / "config.yaml").write_text(yaml.safe_dump(ref_config), encoding="utf-8")

    # preds_test.csv
    preds_df = pd.DataFrame(
        {
            "image_id": ids_te,
            "y_true": y_te,
            "y_pred": y_pred_te,
        }
    )
    for idx_cls, cls_name in enumerate(DEFAULT_CLASS_NAMES):
        preds_df[f"prob_{cls_name}"] = proba_te[:, idx_cls]
    preds_df.to_csv(final_dir / "preds_test.csv", index=False)

    # log
    log_content = (
        f"Mode: final\n"
        f"Commit: {commit}\n"
        f"Split SHA256: {split_sha}\n"
        f"G1, G2, G3, G4, G5, G6 passed successfully.\n"
        f"Val Macro-F1: {val_macro_f1:.4f}\n"
        f"Test Macro-F1: {report['macro_f1']:.4f}\n"
        f"N_train: {len(y_tr)}, N_val: {len(y_va)}, N_test: {len(y_te)}\n"
    )
    (final_dir / "log").write_text(log_content, encoding="utf-8")

    # r5_gioi_han.md
    r5_content = (
        f"# Báo cáo giới hạn (R5) - Đánh giá tập test duy nhất (S5-04, S5-05)\n\n"
        f"- **Val Macro-F1**: {val_macro_f1:.4f}\n"
        f"- **Test Macro-F1**: {report['macro_f1']:.4f} (95% CI: [{report['ci95_low']:.4f}, {report['ci95_high']:.4f}])\n"
        f"- **Hiệu số (Test - Val)**: {report['test_minus_val']:.4f}\n\n"
        f"## Lưu ý giải thích kết quả (D4):\n"
        f"{report['interpretation_note']}\n"
    )
    (final_dir / "r5_gioi_han.md").write_text(r5_content, encoding="utf-8")

    return {
        "mode": "final",
        "n_train": len(y_tr),
        "n_val": len(y_va),
        "n_test": len(y_te),
        "val_macro_f1": val_macro_f1,
        "test_macro_f1": report["macro_f1"],
        "test_read": True,
        "final_dir": str(final_dir),
        "report": report,
    }


def build_final_test_code_package(
    repo_root: Union[str, Path],
    out_dir: Union[str, Path],
    commit: str,
    mode: str,
    confirm_text: Optional[str] = None,
    expected_confirm_sha256: str = CONFIRM_STRING_SHA256,
    dataset_id: Optional[str] = None,
) -> List[str]:
    """Đóng gói mã nguồn, manifest split và cấu hình tham chiếu để đẩy lên Kaggle Dataset."""
    if mode not in ("dry", "final"):
        raise ValueError(f"Mode '{mode}' khong hop le, chi chap nhan 'dry' hoac 'final'.")

    # Kiểm tra xác nhận TRƯỚC khi tạo hoặc sao chép bất kỳ tệp nào
    clean_text: Optional[str] = None
    if mode == "final":
        if confirm_text is None:
            raise ValueError("confirm_text khong duoc de trong o che do final.")
        clean_text = confirm_text.rstrip("\r\n")
        confirm_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest().lower()
        if not hmac.compare_digest(confirm_hash, expected_confirm_sha256.strip().lower()):
            raise PermissionError(
                f"Ma hash cua chuoi xac nhan ({confirm_hash}) khong khop ({expected_confirm_sha256})."
            )

    repo_path = Path(repo_root)
    out_path = Path(out_dir)
    if out_path.exists() and any(out_path.iterdir()):
        raise ValueError(f"Thu muc '{out_dir}' da ton tai va khong rong.")

    out_path.mkdir(parents=True, exist_ok=True)
    src_out = out_path / "src"
    src_out.mkdir(parents=True, exist_ok=True)

    # Sao chép các tệp mã nguồn
    for fname in FINAL_PACKAGE_SRC_FILES:
        src_file = repo_path / "src" / fname
        if not src_file.is_file():
            raise FileNotFoundError(f"Thieu tep nguon: {src_file}")
        shutil.copyfile(src_file, src_out / fname)
        shutil.copyfile(src_file, out_path / fname)

    # Sao chép tệp split
    for fname in FINAL_PACKAGE_SPLIT_FILES:
        sp_file = repo_path / "splits" / fname
        if not sp_file.is_file():
            raise FileNotFoundError(f"Thieu tep split: {sp_file}")
        shutil.copyfile(sp_file, out_path / fname)

    # Sao chép cấu hình tham chiếu và metrics tham chiếu
    ref_out = out_path / "reference"
    ref_out.mkdir(parents=True, exist_ok=True)
    ref_src_dir = repo_path / "results" / "rq3_ghep_svm_orig_to_orig_s42"
    for r_file in ("config.yaml", "metrics.json"):
        src_f = ref_src_dir / r_file
        if not src_f.is_file():
            raise FileNotFoundError(f"Thieu tep tham chieu: {src_f}")
        shutil.copyfile(src_f, ref_out / r_file)

    # Sao chép threshold_v3.md nếu có
    thresh_src = repo_path / "results" / "threshold_v3.md"
    if thresh_src.is_file():
        shutil.copyfile(thresh_src, out_path / "threshold_v3.md")

    # Ghi tệp điều khiển
    sha_str = (repo_path / "splits" / "split_v1.sha256").read_text(encoding="utf-8").strip().split()[0]
    (out_path / "EXPECTED_SHA256").write_text(sha_str + "\n", encoding="utf-8", newline="\n")
    (out_path / "COMMIT").write_text(commit.strip() + "\n", encoding="utf-8", newline="\n")
    (out_path / "MODE").write_text(mode.strip() + "\n", encoding="utf-8", newline="\n")

    # Ghi CONFIRM_FINAL nếu ở chế độ final
    if mode == "final" and clean_text is not None:
        (out_path / CONFIRM_FILE_NAME).write_text(clean_text + "\n", encoding="utf-8", newline="\n")

    # Ghi dataset-metadata.json
    if dataset_id is None:
        dataset_id = (
            "ductrannguyen/cxr-final-test-dry-code"
            if mode == "dry"
            else "ductrannguyen/cxr-final-test-code"
        )
    metadata = {
        "title": dataset_id.split("/")[-1],
        "id": dataset_id,
        "licenses": [{"name": "other"}],
    }
    with open(out_path / "dataset-metadata.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return sorted(p.name for p in out_path.iterdir())


def find_final_test_code_package(input_root: Union[str, Path]) -> Path:
    """Tìm thư mục gói mã nguồn final test trên Kaggle."""
    input_path = Path(input_root)
    for pat in ("MODE", "*/MODE", "*/*/MODE", "*/*/*/MODE"):
        matches = sorted(input_path.glob(pat))
        if matches:
            return matches[0].parent
    for pat in ("COMMIT", "*/COMMIT", "*/*/COMMIT", "*/*/*/COMMIT"):
        matches = sorted(input_path.glob(pat))
        if matches:
            return matches[0].parent
    raise FileNotFoundError(f"Khong tim thay goi ma nguon final test trong {input_root}")


def kaggle_main(
    input_root: Union[str, Path] = "/kaggle/input",
    working_dir: Union[str, Path] = "/kaggle/working",
    expected_mode: str = "dry",
) -> Dict[str, Any]:
    """Điểm vào chính khi chạy kernel Kaggle cho S5-04 / S5-05."""
    input_path = Path(input_root)
    working_path = Path(working_dir)
    pkg_dir = find_final_test_code_package(input_path)

    mode_file = pkg_dir / "MODE"
    if not mode_file.is_file():
        raise FileNotFoundError(f"Thieu tep MODE trong goi ma: {pkg_dir}")
    mode = mode_file.read_text(encoding="utf-8").strip()
    if mode != expected_mode:
        raise ValueError(
            f"Che do trong goi ma ({mode}) khong khop voi che do du kien ({expected_mode}) cua kernel."
        )

    commit_file = pkg_dir / "COMMIT"
    commit = commit_file.read_text(encoding="utf-8").strip() if commit_file.is_file() else "unknown"
    ds_root = find_data_root(input_path)

    return run_final_test(
        mode=mode,
        dataset_root=ds_root,
        split_csv=pkg_dir / "split_v1.csv",
        reference_dir=pkg_dir / "reference",
        pkg_dir=pkg_dir,
        out_dir=working_path,
        commit=commit,
        threshold_path=pkg_dir / "threshold_v3.md",
    )
