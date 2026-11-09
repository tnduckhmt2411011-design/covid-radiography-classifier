"""Suy luận một ảnh X-quang bằng mô hình đóng băng (S5-06, notebook 11).

Mô hình đóng băng (theo results/rq3_shortcut_learning_conclusion.md): StandardScaler (chỉ fit trên
train) + SVC(kernel='rbf', C=10.0, gamma='scale', class_weight='balanced', probability=True,
random_state=42) trên 152 đặc trưng thủ công (Histogram 64 + GLCM 60 + LBP 28) của ảnh gốc xám 299x299.

Quy ước kiểm soát:
- Cổng H7: chỉ dùng học máy truyền thống, không import framework deep learning.
- Cổng H2: module này chỉ đọc ảnh của split 'train' (để fit) và, tùy chọn, 'val' (để kiểm tra tái lập).
  Module không bao giờ đọc ảnh của split 'test'; hàm ensure_not_heldout_image chỉ đọc cột manifest để
  TỪ CHỐI ảnh đầu vào thuộc tập giữ lại.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union
import warnings

import cv2
import joblib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src import final_test_runner as _ftr
from src.bootstrap import macro_f1_from_labels
from src.dataset import CLASS_NAMES
from src.features_hog_ghep import extract_ghep

N_FEATURES: int = 152
IMAGE_SIZE: Tuple[int, int] = (299, 299)


def load_image_grayscale_299(path: Union[str, Path], *, resize: bool = False) -> np.ndarray:
    """Đọc một ảnh và trả về mảng xám uint8 kích thước 299x299.

    Đọc qua np.fromfile + cv2.imdecode để hỗ trợ đường dẫn Unicode trên Windows.

    Args:
        path: Đường dẫn ảnh.
        resize: Nếu True, ảnh khác 299x299 được đổi cỡ bằng cv2.INTER_AREA kèm cảnh báo (mô hình chỉ
            được kiểm chứng trên ảnh 299x299 của bộ dữ liệu này). Nếu False (mặc định) thì ném lỗi.

    Raises:
        FileNotFoundError: Nếu tệp không tồn tại.
        ValueError: Nếu tệp không phải ảnh hợp lệ, hoặc kích thước khác 299x299 khi resize=False.
    """
    img_path = Path(path)
    if not img_path.is_file():
        raise FileNotFoundError(f"Khong tim thay anh: {img_path}")
    raw = np.fromfile(str(img_path), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE) if raw.size else None
    if img is None:
        raise ValueError(f"Khong the doc anh (khong phai tep anh hop le): {img_path}")
    if img.shape != IMAGE_SIZE:
        if not resize:
            raise ValueError(
                f"Kich thuoc anh {img_path} la {img.shape}, ky vong {IMAGE_SIZE} (299x299)."
            )
        warnings.warn(
            f"Anh {img_path.name} co kich thuoc {img.shape}; da doi co ve 299x299 (INTER_AREA). "
            "Mo hinh chi duoc kiem chung tren anh 299x299 cua bo du lieu COVID-19 Radiography; "
            "ket qua tren anh khac nguon/cach xu ly khong co gia tri danh gia.",
            UserWarning,
            stacklevel=2,
        )
        img = cv2.resize(img, (IMAGE_SIZE[1], IMAGE_SIZE[0]), interpolation=cv2.INTER_AREA)
    return img


def ensure_not_heldout_image(image_path: Union[str, Path], split_csv: Union[str, Path]) -> None:
    """Cổng H2 cho ảnh đầu vào: từ chối ảnh có tên trùng một ảnh thuộc split 'test'.

    Chỉ đọc hai cột manifest (image_id, split); không đọc nội dung ảnh nào của split 'test'.

    Raises:
        PermissionError: Nếu tên tệp trùng image_id của một dòng split == 'test'.
    """
    manifest = pd.read_csv(split_csv, usecols=["image_id", "split"])
    heldout_ids = set(manifest.loc[manifest["split"] == "test", "image_id"].astype(str))
    name = Path(image_path).name
    if name in heldout_ids:
        raise PermissionError(
            f"H2: anh '{name}' thuoc tap giu lai (test) da duoc danh gia mot lan duy nhat; "
            "khong dung lam dau vao suy luan. Hay chon anh train/val hoac anh ngoai bo du lieu."
        )


def extract_152_features(img: np.ndarray) -> np.ndarray:
    """Trích 152 đặc trưng 'ghep' (Histogram 64 + GLCM 60 + LBP 28) bằng hàm chuẩn trong src/."""
    feats, _ = extract_ghep(img)
    feats = np.asarray(feats, dtype=np.float64)
    if feats.shape != (N_FEATURES,):
        raise ValueError(f"Vector dac trung co shape {feats.shape}, ky vong ({N_FEATURES},).")
    return feats


def _feature_code_sha256() -> str:
    """Băm mã trích đặc trưng; đổi mã trích đặc trưng sẽ làm bộ nhớ đệm cũ mất hiệu lực."""
    hasher = hashlib.sha256()
    src_dir = Path(__file__).resolve().parent
    for name in ("features_hist_glcm_lbp.py", "features_hog_ghep.py"):
        hasher.update((src_dir / name).read_bytes())
    return hasher.hexdigest()


def _cache_meta(split_sha256: str, n_train: int) -> Dict[str, Any]:
    return {
        "split_sha256": split_sha256,
        "sklearn_version": sklearn.__version__,
        "n_train": int(n_train),
        "svm_params": dict(_ftr.FROZEN_SVM_PARAMS),
        "feature_code_sha256": _feature_code_sha256(),
    }


def _try_load_cache(
    cache_path: Path, split_sha256: str
) -> Optional[Tuple[StandardScaler, SVC, Dict[str, Any]]]:
    """Nạp bộ nhớ đệm nếu hợp lệ; mọi bất thường đều trả None để fit lại.

    Kiểm tra: kiểu đối tượng, số đặc trưng, SHA-256 split, phiên bản sklearn, siêu tham số, băm mã trích
    đặc trưng. Chỉ nạp tệp do chính notebook ghi trong thư mục làm việc cục bộ: joblib dựa trên pickle
    nên việc kiểm meta KHÔNG bảo vệ trước tệp bị can thiệp; không được nạp tệp từ nguồn không tin cậy.
    """
    if not cache_path.is_file():
        return None
    try:
        payload = joblib.load(cache_path)
        meta = payload["meta"]
        scaler, clf = payload["scaler"], payload["clf"]
        if not isinstance(meta, dict):
            return None
        if not isinstance(scaler, StandardScaler) or not isinstance(clf, SVC):
            return None
        if getattr(scaler, "n_features_in_", None) != N_FEATURES:
            return None
        if meta.get("split_sha256") != split_sha256:
            return None
        if meta.get("sklearn_version") != sklearn.__version__:
            return None
        if meta.get("svm_params") != dict(_ftr.FROZEN_SVM_PARAMS):
            return None
        if meta.get("feature_code_sha256") != _feature_code_sha256():
            return None
    except Exception:
        return None
    return scaler, clf, meta


def fit_or_load_model(
    split_csv: Union[str, Path],
    dataset_root: Union[str, Path],
    *,
    cache_path: Optional[Union[str, Path]] = None,
    expected_sha256: str = _ftr.EXPECTED_SPLIT_SHA256,
    expected_sizes: Mapping[str, int] = _ftr.EXPECTED_SPLIT_SIZES,
) -> Tuple[StandardScaler, SVC, Dict[str, Any]]:
    """Trả về (scaler, clf, info) của mô hình đóng băng, fit chỉ trên split 'train'.

    Thứ tự: kiểm SHA-256 và kích thước split (G1) -> nạp bộ nhớ đệm hợp lệ nếu có -> nếu không,
    trích đặc trưng train và gọi fit_frozen_model, rồi ghi bộ nhớ đệm (nếu có cache_path).
    info['source'] là 'cache' hoặc 'fit'.
    """
    sha = _ftr.check_split_integrity(
        split_csv, expected_sha256=expected_sha256, expected_sizes=expected_sizes
    )
    cache = Path(cache_path) if cache_path is not None else None
    if cache is not None:
        hit = _try_load_cache(cache, sha)
        if hit is not None:
            scaler, clf, meta = hit
            return scaler, clf, {**meta, "source": "cache"}

    split_df = pd.read_csv(split_csv)
    x_train, _, y_train, _ = _ftr.load_split_features(split_df, "train", dataset_root)
    scaler, clf = _ftr.fit_frozen_model(x_train, y_train)
    meta = _cache_meta(sha, len(y_train))
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = cache.with_name(cache.name + ".tmp")
        joblib.dump({"scaler": scaler, "clf": clf, "meta": meta}, tmp_path)
        os.replace(tmp_path, cache)  # ghi nguyên tử: không để lại tệp đệm dở dang
    return scaler, clf, {**meta, "source": "fit"}


INFERENCE_PACKAGE_SRC_FILES: Tuple[str, ...] = tuple(_ftr.FINAL_PACKAGE_SRC_FILES) + ("inference_demo.py",)
DEFAULT_INFERENCE_DATASET_ID: str = "ductrannguyen/cxr-inference-demo-code"


def build_inference_code_package(
    repo_root: Union[str, Path],
    out_dir: Union[str, Path],
    commit: str,
    dataset_id: str = DEFAULT_INFERENCE_DATASET_ID,
) -> List[str]:
    """Đóng gói mã nguồn + split_v1.csv cho notebook 11 chạy trên Kaggle (Dataset riêng).

    Gói KHÔNG chứa MODE, CONFIRM_FINAL hay EXPECTED_SHA256 của gói đánh giá test đã niêm phong, và không
    thay đổi FINAL_PACKAGE_SRC_FILES. Trả về danh sách đường dẫn tương đối của các tệp đã ghi.
    """
    repo_path = Path(repo_root)
    out_path = Path(out_dir)
    if out_path.exists() and any(out_path.iterdir()):
        raise ValueError(f"Thu muc '{out_dir}' da ton tai va khong rong.")
    written: List[str] = []
    (out_path / "src").mkdir(parents=True, exist_ok=True)
    for fname in INFERENCE_PACKAGE_SRC_FILES:
        src_file = repo_path / "src" / fname
        if not src_file.is_file():
            raise FileNotFoundError(f"Thieu tep nguon: {src_file}")
        shutil.copyfile(src_file, out_path / "src" / fname)
        written.append(f"src/{fname}")
    for fname in _ftr.FINAL_PACKAGE_SPLIT_FILES:
        sp_file = repo_path / "splits" / fname
        if not sp_file.is_file():
            raise FileNotFoundError(f"Thieu tep split: {sp_file}")
        shutil.copyfile(sp_file, out_path / fname)
        written.append(fname)
    (out_path / "COMMIT").write_text(commit.strip() + "\n", encoding="utf-8", newline="\n")
    written.append("COMMIT")
    metadata = {
        "title": dataset_id.split("/")[-1],
        "id": dataset_id,
        "licenses": [{"name": "other"}],
    }
    with open(out_path / "dataset-metadata.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    written.append("dataset-metadata.json")
    return written


def predict_image(scaler: StandardScaler, clf: SVC, feats: np.ndarray) -> Dict[str, Any]:
    """Dự đoán nhãn và xác suất 4 lớp cho một vector 152 đặc trưng.

    Returns:
        Dict gồm 'label_idx', 'label' và 'probabilities' (tên lớp -> xác suất, theo thứ tự CLASS_NAMES).
    """
    vec = np.asarray(feats, dtype=np.float64)
    if vec.shape != (N_FEATURES,):
        raise ValueError(f"Can vector {N_FEATURES} dac trung, nhan shape {vec.shape}.")
    y_pred, proba = _ftr.predict_with_model(scaler, clf, vec.reshape(1, -1))
    class_to_col = {int(c): j for j, c in enumerate(clf.classes_)}
    probs = {name: float(proba[0, class_to_col[i]]) for i, name in enumerate(CLASS_NAMES)}
    label_idx = int(y_pred[0])
    return {"label_idx": label_idx, "label": CLASS_NAMES[label_idx], "probabilities": probs}


def plot_probabilities(result: Mapping[str, Any]) -> Figure:
    """Vẽ biểu đồ cột phân phối xác suất 4 lớp; cột của lớp được dự đoán được tô đậm."""
    probs = result["probabilities"]
    names = list(CLASS_NAMES)
    values = [probs[n] for n in names]
    colors = ["#1f77b4" if n == result["label"] else "#c7c7c7" for n in names]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(range(len(names)), values, color=colors)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Xac suat")
    ax.set_title(f"Phan phoi xac suat 4 lop - du doan: {result['label']}")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center")
    fig.tight_layout()
    return fig


def verify_on_val(
    scaler: StandardScaler,
    clf: SVC,
    split_csv: Union[str, Path],
    dataset_root: Union[str, Path],
    *,
    reference: Optional[float] = _ftr.REFERENCE_VAL_MACRO_F1,
    tolerance: float = _ftr.G5_TOLERANCE,
) -> float:
    """Kiểm tra tái lập tùy chọn: Macro-F1 trên split 'val' (không đọc 'test').

    Nếu reference khác None thì áp dụng kiểm tra G5 (|Δ| <= tolerance), vi phạm sẽ ném RuntimeError.
    """
    split_df = pd.read_csv(split_csv)
    x_val, _, y_val, _ = _ftr.load_split_features(split_df, "val", dataset_root)
    y_pred, _ = _ftr.predict_with_model(scaler, clf, x_val)
    f1 = float(macro_f1_from_labels(y_val, y_pred))
    if reference is not None:
        _ftr.check_val_reproduction(f1, reference=reference, tolerance=tolerance)
    return f1
