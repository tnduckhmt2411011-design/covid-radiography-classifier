"""Kiểm thử TDD cho src/model_artifact.py (S6-02).

Toàn bộ test dùng artifact giả lập nhỏ; không đọc ảnh thật và không đọc split 'test'.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import joblib
import numpy as np
import pytest
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.dataset import CLASS_NAMES
from src.final_test_runner import EXPECTED_SPLIT_SHA256, EXPECTED_SPLIT_SIZES, FROZEN_SVM_PARAMS
from src.inference_demo import N_FEATURES, _feature_code_sha256
from src.model_artifact import (
    DEFAULT_MODEL_FILE,
    DEFAULT_MODEL_SHA256,
    ModelArtifactError,
    download_and_verify_model,
    load_model_artifact,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _make_payload(
    path: Path,
    *,
    meta_overrides=None,
    n_features: int = N_FEATURES,
    classes=(0, 1, 2, 3),
) -> Path:
    """Tạo artifact giả lập có cùng cấu trúc meta với artifact thật."""
    rng = np.random.default_rng(42)
    x = rng.normal(size=(80, n_features))
    y = np.resize(np.arange(len(classes)), x.shape[0])
    scaler = StandardScaler().fit(x)
    clf = SVC(**FROZEN_SVM_PARAMS).fit(scaler.transform(x), y)
    meta = {
        "split_sha256": EXPECTED_SPLIT_SHA256,
        "sklearn_version": sklearn.__version__,
        "n_train": EXPECTED_SPLIT_SIZES["train"],
        "svm_params": dict(FROZEN_SVM_PARAMS),
        "feature_code_sha256": _feature_code_sha256(),
    }
    if meta_overrides:
        meta.update(meta_overrides)
    joblib.dump({"scaler": scaler, "clf": clf, "meta": meta}, path)
    return path


def test_sha256_file_matches_hashlib(tmp_path: Path) -> None:
    p = tmp_path / "x.bin"
    p.write_bytes(b"abc" * 1000)
    assert sha256_file(p) == hashlib.sha256(p.read_bytes()).hexdigest()


def test_valid_artifact_loads(tmp_path: Path) -> None:
    p = _make_payload(tmp_path / "model.joblib")
    scaler, clf, meta = load_model_artifact(p, expected_sha256=sha256_file(p))
    assert scaler.n_features_in_ == N_FEATURES
    assert [int(c) for c in clf.classes_] == list(range(len(CLASS_NAMES)))
    assert meta["n_train"] == EXPECTED_SPLIT_SIZES["train"]


def test_rejects_wrong_file_hash(tmp_path: Path) -> None:
    p = _make_payload(tmp_path / "model.joblib")
    with pytest.raises(ModelArtifactError, match="SHA-256"):
        load_model_artifact(p, expected_sha256="0" * 64)


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactError, match="Không tìm thấy"):
        load_model_artifact(tmp_path / "missing.joblib")


def test_rejects_garbage_joblib(tmp_path: Path) -> None:
    p = tmp_path / "garbage.joblib"
    p.write_bytes(b"not a joblib file")
    with pytest.raises(ModelArtifactError):
        load_model_artifact(p)


def test_rejects_incomplete_payload(tmp_path: Path) -> None:
    p = tmp_path / "incomplete.joblib"
    joblib.dump({"scaler": None, "clf": None}, p)
    with pytest.raises(ModelArtifactError):
        load_model_artifact(p)


@pytest.mark.parametrize(
    "overrides, match",
    [
        ({"split_sha256": "0" * 64}, "split"),
        ({"sklearn_version": "0.0.0"}, "scikit-learn"),
        ({"feature_code_sha256": "0" * 64}, "đặc trưng"),
        ({"n_train": 1}, "train"),
        ({"svm_params": {**FROZEN_SVM_PARAMS, "C": 1.0}}, "siêu tham số"),
    ],
)
def test_rejects_bad_metadata(tmp_path: Path, overrides, match: str) -> None:
    p = _make_payload(tmp_path / "model.joblib", meta_overrides=overrides)
    with pytest.raises(ModelArtifactError, match=match):
        load_model_artifact(p)


def test_rejects_wrong_feature_count(tmp_path: Path) -> None:
    p = _make_payload(tmp_path / "model.joblib", n_features=N_FEATURES - 1)
    with pytest.raises(ModelArtifactError, match=str(N_FEATURES)):
        load_model_artifact(p)


def test_rejects_wrong_class_order(tmp_path: Path) -> None:
    p = _make_payload(tmp_path / "model.joblib", classes=(0, 1, 2))
    with pytest.raises(ModelArtifactError, match="lớp"):
        load_model_artifact(p)


def test_download_and_verify_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = _make_payload(tmp_path / "model.joblib")
    import huggingface_hub

    monkeypatch.setattr(huggingface_hub, "hf_hub_download", lambda **kwargs: str(p))
    got = download_and_verify_model(
        "owner/repo", expected_sha256=sha256_file(p), filename=DEFAULT_MODEL_FILE
    )
    assert got == p


def test_download_and_verify_rejects_bad_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = _make_payload(tmp_path / "model.joblib")
    import huggingface_hub

    monkeypatch.setattr(huggingface_hub, "hf_hub_download", lambda **kwargs: str(p))
    with pytest.raises(ModelArtifactError, match="SHA-256"):
        download_and_verify_model("owner/repo", expected_sha256="0" * 64)


def test_download_requires_repo_id(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ModelArtifactError, match="CXR_MODEL_REPO"):
        download_and_verify_model("", expected_sha256=DEFAULT_MODEL_SHA256)


def test_default_model_file_name() -> None:
    assert DEFAULT_MODEL_FILE.endswith(".joblib")
    assert len(DEFAULT_MODEL_SHA256) == 64
    int(DEFAULT_MODEL_SHA256, 16)


@pytest.mark.skipif(
    not (REPO_ROOT / "outputs" / "k_v3_out" / DEFAULT_MODEL_FILE).is_file(),
    reason="artifact cục bộ không có trong môi trường này",
)
def test_default_sha256_matches_local_cache_artifact() -> None:
    p = REPO_ROOT / "outputs" / "k_v3_out" / DEFAULT_MODEL_FILE
    assert sha256_file(p) == DEFAULT_MODEL_SHA256
