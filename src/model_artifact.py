"""Nạp artifact mô hình đóng băng cho demo suy luận (S6-02).

Artifact là tệp joblib chứa ``StandardScaler`` + ``SVC`` đã fit trên split 'train' của
``splits/split_v1.csv`` (xem ``src/inference_demo.py``). Module này:

- Kiểm SHA-256 của tệp TRƯỚC khi gọi ``joblib.load`` (joblib dựa trên pickle nên chỉ được nạp tệp
  có băm khớp bản đã công bố).
- Kiểm metadata của artifact (băm split, phiên bản scikit-learn, số mẫu train, siêu tham số SVM,
  băm mã trích đặc trưng) để từ chối artifact không tương thích.
- Tải artifact từ kho Hugging Face công khai và kiểm băm sau khi tải.

Module không đọc ảnh, không đọc split 'test', không huấn luyện lại mô hình.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple, Union

import joblib
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src import final_test_runner as _ftr
from src.dataset import CLASS_NAMES
from src.inference_demo import N_FEATURES, _feature_code_sha256

# Tên tệp và băm của artifact kernel-v3 đã dùng cho cổng tương đương 200/200 ảnh val.
DEFAULT_MODEL_FILE: str = "cxr_inference_model_cache.joblib"
DEFAULT_MODEL_SHA256: str = (
    "3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058"
)

# Tên biến môi trường / khóa Streamlit secrets dùng chung cho app và CLI.
ENV_MODEL_REPO: str = "CXR_MODEL_REPO"
ENV_MODEL_FILE: str = "CXR_MODEL_FILE"
ENV_MODEL_REVISION: str = "CXR_MODEL_REVISION"
ENV_MODEL_SHA256: str = "CXR_MODEL_SHA256"
ENV_MODEL_PATH: str = "CXR_MODEL_PATH"
ENV_HF_TOKEN: str = "HF_TOKEN"


class ModelArtifactError(RuntimeError):
    """Artifact mô hình thiếu, sai băm hoặc không tương thích với mã suy luận."""


def sha256_file(path: Union[str, Path], *, chunk_size: int = 1 << 20) -> str:
    """Trả về băm SHA-256 dạng hex của một tệp, đọc theo khối để không nạp cả tệp vào RAM."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ModelArtifactError(message)


def _validate_metadata(meta: Any, scaler: StandardScaler, clf: SVC) -> Dict[str, Any]:
    """Kiểm metadata và cấu trúc mô hình; ném ModelArtifactError nếu không khớp."""
    _require(isinstance(meta, Mapping), "Artifact thiếu khối 'meta' dạng ánh xạ.")
    meta = dict(meta)

    _require(
        meta.get("split_sha256") == _ftr.EXPECTED_SPLIT_SHA256,
        "Artifact không khớp băm split đã niêm phong (split_sha256).",
    )
    _require(
        meta.get("sklearn_version") == sklearn.__version__,
        "Artifact được fit bằng scikit-learn "
        f"{meta.get('sklearn_version')!r}, môi trường hiện tại là {sklearn.__version__!r}.",
    )
    _require(
        meta.get("feature_code_sha256") == _feature_code_sha256(),
        "Artifact không khớp băm mã trích đặc trưng (feature_code_sha256).",
    )
    _require(
        meta.get("n_train") == _ftr.EXPECTED_SPLIT_SIZES["train"],
        "Artifact có n_train="
        f"{meta.get('n_train')!r}, kỳ vọng {_ftr.EXPECTED_SPLIT_SIZES['train']}.",
    )
    _require(
        meta.get("svm_params") == dict(_ftr.FROZEN_SVM_PARAMS),
        "Artifact dùng siêu tham số SVM khác cấu hình đóng băng.",
    )

    _require(
        isinstance(scaler, StandardScaler),
        "Artifact thiếu StandardScaler hợp lệ.",
    )
    _require(isinstance(clf, SVC), "Artifact thiếu SVC hợp lệ.")
    _require(
        getattr(scaler, "n_features_in_", None) == N_FEATURES,
        f"StandardScaler nhận {getattr(scaler, 'n_features_in_', None)!r} đặc trưng, kỳ vọng {N_FEATURES}.",
    )
    _require(
        [int(c) for c in getattr(clf, "classes_", [])] == list(range(len(CLASS_NAMES))),
        f"SVC có thứ tự lớp khác kỳ vọng 0..{len(CLASS_NAMES) - 1} ({', '.join(CLASS_NAMES)}).",
    )
    _require(
        getattr(clf, "n_features_in_", None) == N_FEATURES,
        f"SVC nhận {getattr(clf, 'n_features_in_', None)!r} đặc trưng, kỳ vọng {N_FEATURES}.",
    )

    actual = clf.get_params()
    mismatched = {
        key: (actual.get(key), value)
        for key, value in _ftr.FROZEN_SVM_PARAMS.items()
        if actual.get(key) != value
    }
    _require(
        not mismatched,
        "SVC có siêu tham số thực tế khác cấu hình đóng băng: " + repr(mismatched),
    )
    return meta


def load_model_artifact(
    path: Union[str, Path],
    *,
    expected_sha256: Optional[str] = None,
) -> Tuple[StandardScaler, SVC, Dict[str, Any]]:
    """Nạp artifact, kiểm băm (nếu có) và metadata; trả về ``(scaler, clf, meta)``.

    Args:
        path: Đường dẫn tệp joblib.
        expected_sha256: Băm SHA-256 hex kỳ vọng. Nếu ``None`` thì bỏ qua bước kiểm băm
            (chỉ dùng cho test với artifact giả lập; app luôn truyền băm đã công bố).

    Raises:
        ModelArtifactError: Khi tệp không tồn tại, sai băm, không giải mã được hoặc metadata
            không tương thích.
    """
    artifact_path = Path(path)
    if not artifact_path.is_file():
        raise ModelArtifactError(f"Không tìm thấy tệp artifact: {artifact_path}")

    if expected_sha256 is not None:
        actual = sha256_file(artifact_path)
        if actual.lower() != expected_sha256.strip().lower():
            raise ModelArtifactError(
                "SHA-256 của artifact không khớp bản đã công bố: "
                f"nhận {actual}, kỳ vọng {expected_sha256}."
            )

    try:
        payload = joblib.load(artifact_path)
    except Exception as exc:  # joblib/pickle có thể ném nhiều loại lỗi khác nhau
        raise ModelArtifactError(
            f"Không giải mã được artifact joblib tại {artifact_path}: {exc}"
        ) from exc

    if not isinstance(payload, Mapping):
        raise ModelArtifactError("Artifact không phải ánh xạ gồm 'scaler', 'clf', 'meta'.")
    missing = {"scaler", "clf", "meta"} - set(payload)
    if missing:
        raise ModelArtifactError(f"Artifact thiếu khóa bắt buộc: {sorted(missing)}.")

    scaler, clf = payload["scaler"], payload["clf"]
    meta = _validate_metadata(payload["meta"], scaler, clf)
    return scaler, clf, meta


def download_and_verify_model(
    repo_id: str,
    *,
    expected_sha256: str = DEFAULT_MODEL_SHA256,
    filename: str = DEFAULT_MODEL_FILE,
    revision: Optional[str] = None,
    token: Optional[str] = None,
    cache_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """Tải artifact từ kho Hugging Face công khai rồi kiểm SHA-256.

    Chỉ gọi ``huggingface_hub`` khi cần tải; không import thư viện học sâu nào.

    Raises:
        ModelArtifactError: Khi thiếu ``repo_id``, tải thất bại hoặc băm không khớp.
    """
    if not str(repo_id).strip():
        raise ModelArtifactError(
            f"Thiếu mã kho mô hình: đặt biến môi trường {ENV_MODEL_REPO} "
            "(dạng 'tai-khoan/ten-kho') hoặc khóa tương ứng trong Streamlit secrets."
        )

    import huggingface_hub

    kwargs: Dict[str, Any] = {
        "repo_id": str(repo_id).strip(),
        "filename": filename,
    }
    if revision:
        kwargs["revision"] = revision
    if token:
        kwargs["token"] = token
    if cache_dir is not None:
        kwargs["cache_dir"] = str(cache_dir)

    try:
        downloaded = huggingface_hub.hf_hub_download(**kwargs)
    except Exception as exc:
        raise ModelArtifactError(
            f"Không tải được artifact '{filename}' từ kho '{repo_id}': {exc}"
        ) from exc

    downloaded_path = Path(downloaded)
    actual = sha256_file(downloaded_path)
    if actual.lower() != expected_sha256.strip().lower():
        raise ModelArtifactError(
            "SHA-256 của artifact tải về không khớp bản đã công bố: "
            f"nhận {actual}, kỳ vọng {expected_sha256}."
        )
    return downloaded_path
