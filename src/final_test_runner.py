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
from typing import Any, Dict, List, Mapping, Tuple, Union

import pandas as pd

from src.rq2_runner import feature_params
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
