"""Kiểm thử TDD cho src/inference_demo.py (S5-06): suy luận một ảnh X-quang bằng mô hình đóng băng.

Toàn bộ test dùng ảnh và split giả; KHÔNG đọc ảnh thật và KHÔNG bao giờ đọc split 'test' (cổng H2).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from src import final_test_runner as ftr
from src.dataset import CLASS_NAMES
from src.features_hist_glcm_lbp import extract_glcm, extract_histogram, extract_lbp
from src.inference_demo import (
    build_inference_code_package,
    ensure_not_heldout_image,
    extract_152_features,
    fit_or_load_model,
    load_image_grayscale_299,
    plot_probabilities,
    predict_image,
    verify_on_val,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SIZES = {"train": 24, "val": 8, "test": 4}


def _make_image(label_idx: int, seed: int) -> np.ndarray:
    """Ảnh xám 299x299 giả, mỗi lớp có mức sáng nền khác nhau để mô hình học được."""
    rng = np.random.default_rng(seed)
    base = 40 + 50 * label_idx
    noise = rng.integers(-25, 26, size=(299, 299))
    return np.clip(base + noise, 0, 255).astype(np.uint8)


@pytest.fixture(scope="module")
def fake_env(tmp_path_factory: pytest.TempPathFactory) -> Dict[str, Any]:
    root = tmp_path_factory.mktemp("fake_dataset")
    rows: List[Dict[str, str]] = []
    seed = 0
    for split, n in SIZES.items():
        for i in range(n):
            label_idx = i % len(CLASS_NAMES)
            label = CLASS_NAMES[label_idx]
            rel = f"{label}/images/{split}-{i}.png"
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            assert cv2.imwrite(str(path), _make_image(label_idx, seed))
            seed += 1
            rows.append(
                {"image_id": f"{split}-{i}.png", "label": label, "rel_image_path": rel, "split": split}
            )
    split_csv = root / "split_v1.csv"
    pd.DataFrame(rows).to_csv(split_csv, index=False)
    sha = hashlib.sha256(split_csv.read_bytes()).hexdigest()
    return {"root": root, "split_csv": split_csv, "sha": sha}


@pytest.fixture()
def load_spy(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Ghi lại danh sách split mà load_split_features được gọi, vẫn gọi hàm thật."""
    calls: List[str] = []
    real = ftr.load_split_features

    def _spy(split_df, split, dataset_root, **kwargs):
        calls.append(split)
        return real(split_df, split, dataset_root, **kwargs)

    monkeypatch.setattr(ftr, "load_split_features", _spy)
    return calls


def _fit(fake_env: Dict[str, Any], cache_path: Any = None) -> Tuple[Any, Any, Dict[str, Any]]:
    return fit_or_load_model(
        fake_env["split_csv"],
        fake_env["root"],
        cache_path=cache_path,
        expected_sha256=fake_env["sha"],
        expected_sizes=SIZES,
    )


# ------------------------------------------------------------ nạp ảnh


def test_load_image_accepts_valid_grayscale(tmp_path: Path) -> None:
    p = tmp_path / "ok.png"
    cv2.imwrite(str(p), _make_image(0, 1))
    img = load_image_grayscale_299(p)
    assert img.shape == (299, 299) and img.dtype == np.uint8


def test_load_image_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_image_grayscale_299(tmp_path / "khong_ton_tai.png")


def test_load_image_rejects_wrong_size(tmp_path: Path) -> None:
    p = tmp_path / "small.png"
    cv2.imwrite(str(p), np.zeros((100, 100), dtype=np.uint8))
    with pytest.raises(ValueError, match="299"):
        load_image_grayscale_299(p)


# ------------------------------------------------------------ 152 đặc trưng


def test_extract_152_features_layout_matches_src_functions() -> None:
    img = _make_image(2, 7)
    feats = extract_152_features(img)
    assert feats.shape == (152,) and feats.dtype == np.float64
    assert np.isfinite(feats).all()
    hist = extract_histogram(img)
    glcm, _ = extract_glcm(img)
    lbp = extract_lbp(img)
    assert (hist.size, glcm.size, lbp.size) == (64, 60, 28)
    np.testing.assert_allclose(feats, np.concatenate([hist, glcm, lbp]))


# ------------------------------------------------------------ fit / cache


def test_fit_uses_only_train_split(fake_env: Dict[str, Any], load_spy: List[str]) -> None:
    scaler, clf, info = _fit(fake_env)
    assert load_spy == ["train"]
    assert "test" not in load_spy
    assert info["source"] == "fit"
    assert list(clf.classes_) == [0, 1, 2, 3]
    assert clf.probability is True


def test_fit_rejects_wrong_split_sha(fake_env: Dict[str, Any], load_spy: List[str]) -> None:
    with pytest.raises(ValueError, match="SHA256"):
        fit_or_load_model(
            fake_env["split_csv"],
            fake_env["root"],
            expected_sha256="0" * 64,
            expected_sizes=SIZES,
        )
    assert load_spy == []


def test_cache_roundtrip_skips_refit(fake_env: Dict[str, Any], load_spy: List[str], tmp_path: Path) -> None:
    cache = tmp_path / "model_cache.joblib"
    s1, c1, info1 = _fit(fake_env, cache)
    assert info1["source"] == "fit" and cache.is_file()
    load_spy.clear()
    s2, c2, info2 = _fit(fake_env, cache)
    assert info2["source"] == "cache"
    assert load_spy == []
    x = extract_152_features(_make_image(1, 99)).reshape(1, -1)
    np.testing.assert_allclose(
        c1.predict_proba(s1.transform(x)), c2.predict_proba(s2.transform(x))
    )


def test_stale_cache_with_other_sha_is_refit(
    fake_env: Dict[str, Any], load_spy: List[str], tmp_path: Path
) -> None:
    cache = tmp_path / "model_cache.joblib"
    _fit(fake_env, cache)
    import joblib

    payload = joblib.load(cache)
    payload["meta"]["split_sha256"] = "1" * 64
    joblib.dump(payload, cache)
    load_spy.clear()
    _, _, info = _fit(fake_env, cache)
    assert info["source"] == "fit"
    assert load_spy == ["train"]


def test_cache_with_other_sklearn_version_is_refit(
    fake_env: Dict[str, Any], load_spy: List[str], tmp_path: Path
) -> None:
    cache = tmp_path / "model_cache.joblib"
    _fit(fake_env, cache)
    import joblib

    payload = joblib.load(cache)
    payload["meta"]["sklearn_version"] = "0.0.0"
    joblib.dump(payload, cache)
    load_spy.clear()
    _, _, info = _fit(fake_env, cache)
    assert info["source"] == "fit"


def test_corrupt_cache_is_refit(fake_env: Dict[str, Any], tmp_path: Path) -> None:
    cache = tmp_path / "model_cache.joblib"
    cache.write_bytes(b"khong phai joblib")
    _, _, info = _fit(fake_env, cache)
    assert info["source"] == "fit"


# ------------------------------------------------------------ dự đoán


def test_predict_image_returns_four_probabilities(fake_env: Dict[str, Any]) -> None:
    scaler, clf, _ = _fit(fake_env)
    feats = extract_152_features(_make_image(3, 123))
    res = predict_image(scaler, clf, feats)
    assert list(res["probabilities"].keys()) == list(CLASS_NAMES)
    assert sum(res["probabilities"].values()) == pytest.approx(1.0, abs=1e-6)
    # Nhãn lấy từ clf.predict() (khớp số đo đã công bố); có thể khác argmax xác suất do Platt scaling.
    assert res["label"] in res["probabilities"]
    assert CLASS_NAMES[res["label_idx"]] == res["label"]
    expected_idx = int(clf.predict(scaler.transform(feats.reshape(1, -1)))[0])
    assert res["label_idx"] == expected_idx


def test_predict_image_rejects_wrong_feature_length(fake_env: Dict[str, Any]) -> None:
    scaler, clf, _ = _fit(fake_env)
    with pytest.raises(ValueError, match="152"):
        predict_image(scaler, clf, np.zeros(10))


# ------------------------------------------------------------ biểu đồ


def test_plot_probabilities_has_four_bars(fake_env: Dict[str, Any]) -> None:
    scaler, clf, _ = _fit(fake_env)
    res = predict_image(scaler, clf, extract_152_features(_make_image(0, 5)))
    fig = plot_probabilities(res)
    ax = fig.axes[0]
    assert len(ax.patches) == 4
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert labels == list(CLASS_NAMES)
    import matplotlib.pyplot as plt

    plt.close(fig)


# ------------------------------------------------------------ kiểm tra val tùy chọn


def test_verify_on_val_reads_only_val(fake_env: Dict[str, Any], load_spy: List[str]) -> None:
    scaler, clf, _ = _fit(fake_env)
    load_spy.clear()
    f1 = verify_on_val(
        scaler,
        clf,
        fake_env["split_csv"],
        fake_env["root"],
        reference=None,
    )
    assert load_spy == ["val"]
    assert 0.0 <= f1 <= 1.0


def test_verify_on_val_raises_when_far_from_reference(fake_env: Dict[str, Any]) -> None:
    scaler, clf, _ = _fit(fake_env)
    with pytest.raises(RuntimeError, match="G5"):
        verify_on_val(
            scaler,
            clf,
            fake_env["split_csv"],
            fake_env["root"],
            reference=-5.0,
            tolerance=0.002,
        )


# ------------------------------------------------------------ cổng H7 / H2 tĩnh


def test_module_has_no_deep_learning_imports_and_never_unlocks_test() -> None:
    text = (REPO_ROOT / "src" / "inference_demo.py").read_text(encoding="utf-8")
    for lib in ("torch", "tensorflow", "keras", "timm", "fastai"):
        assert f"import {lib}" not in text
        assert f"from {lib}" not in text
    assert "allow_test" not in text
    assert "Path" in text  # sanity: đã đọc đúng tệp nguồn
    assert 'load_split_features(split_df, "test"' not in text


# ------------------------------------------------------------ review S5-06: ảnh bất kỳ, đường dẫn Unicode, ảnh hỏng


def test_load_image_resize_option_accepts_any_size(tmp_path: Path) -> None:
    p = tmp_path / "big.png"
    cv2.imwrite(str(p), np.full((1024, 800), 128, dtype=np.uint8))
    with pytest.raises(ValueError, match="299"):
        load_image_grayscale_299(p)  # chế độ nghiêm ngặt giữ nguyên
    with pytest.warns(UserWarning, match="299"):
        img = load_image_grayscale_299(p, resize=True)
    assert img.shape == (299, 299) and img.dtype == np.uint8


def test_load_image_resize_true_on_299_does_not_warn(tmp_path: Path) -> None:
    import warnings

    p = tmp_path / "ok.png"
    cv2.imwrite(str(p), _make_image(1, 3))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        img = load_image_grayscale_299(p, resize=True)
    assert img.shape == (299, 299)


def test_load_image_accepts_non_ascii_path(tmp_path: Path) -> None:
    folder = tmp_path / "thư mục ảnh Lộ trình"
    folder.mkdir()
    p = folder / "phổi.png"
    ok, buf = cv2.imencode(".png", _make_image(2, 4))
    assert ok
    buf.tofile(str(p))
    img = load_image_grayscale_299(p)
    assert img.shape == (299, 299)


def test_load_image_corrupt_file_raises_value_error(tmp_path: Path) -> None:
    p = tmp_path / "hong.png"
    p.write_bytes(b"day khong phai anh")
    with pytest.raises(ValueError, match="doc"):
        load_image_grayscale_299(p)


# ------------------------------------------------------------ review: cache cứng hơn


def test_cache_with_non_dict_meta_is_refit_not_crash(fake_env: Dict[str, Any], tmp_path: Path) -> None:
    import joblib

    cache = tmp_path / "model_cache.joblib"
    s, c, _ = _fit(fake_env)
    joblib.dump({"scaler": s, "clf": c, "meta": 5}, cache)
    _, _, info = _fit(fake_env, cache)
    assert info["source"] == "fit"


def test_cache_with_wrong_object_types_is_refit(fake_env: Dict[str, Any], tmp_path: Path) -> None:
    import joblib

    cache = tmp_path / "model_cache.joblib"
    _fit(fake_env, cache)
    payload = joblib.load(cache)
    payload["clf"] = "khong phai SVC"
    joblib.dump(payload, cache)
    _, clf, info = _fit(fake_env, cache)
    assert info["source"] == "fit"
    assert clf.__class__.__name__ == "SVC"


def test_cache_with_other_feature_code_hash_is_refit(fake_env: Dict[str, Any], tmp_path: Path) -> None:
    import joblib

    cache = tmp_path / "model_cache.joblib"
    _fit(fake_env, cache)
    payload = joblib.load(cache)
    payload["meta"]["feature_code_sha256"] = "2" * 64
    joblib.dump(payload, cache)
    _, _, info = _fit(fake_env, cache)
    assert info["source"] == "fit"


def test_cache_write_is_atomic_leaves_no_tmp_files(fake_env: Dict[str, Any], tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache_dir"
    _fit(fake_env, cache_dir / "model_cache.joblib")
    assert sorted(p.name for p in cache_dir.iterdir()) == ["model_cache.joblib"]


# ------------------------------------------------------------ review: bám cấu hình đóng băng


def test_fitted_model_params_match_frozen_config_yaml(fake_env: Dict[str, Any]) -> None:
    import yaml

    cfg = yaml.safe_load((REPO_ROOT / "results" / "final_test" / "config.yaml").read_text(encoding="utf-8"))
    hp = cfg["hyperparameters"]
    _, clf, info = _fit(fake_env)
    params = clf.get_params()
    for key in ("C", "gamma", "kernel", "class_weight", "probability", "random_state"):
        assert params[key] == hp[key], key
    assert info["svm_params"] == {k: hp[k] for k in info["svm_params"]}


def test_production_split_sha_default_is_valid() -> None:
    """Đường mặc định (SHA thật) mà notebook dùng: G1 phải qua với splits/split_v1.csv."""
    assert (
        ftr.check_split_integrity(REPO_ROOT / "splits" / "split_v1.csv")
        == ftr.EXPECTED_SPLIT_SHA256
    )


# ------------------------------------------------------------ review: tinh thần H2 cho IMAGE_PATH


def test_guard_rejects_image_that_belongs_to_heldout_split(fake_env: Dict[str, Any]) -> None:
    held_out = fake_env["root"] / "COVID" / "images" / "test-0.png"
    assert held_out.is_file()
    with pytest.raises(PermissionError, match="H2"):
        ensure_not_heldout_image(held_out, fake_env["split_csv"])


def test_guard_allows_train_val_and_external_images(fake_env: Dict[str, Any], tmp_path: Path) -> None:
    ensure_not_heldout_image(fake_env["root"] / "COVID" / "images" / "val-0.png", fake_env["split_csv"])
    ensure_not_heldout_image(fake_env["root"] / "COVID" / "images" / "train-0.png", fake_env["split_csv"])
    ensure_not_heldout_image(tmp_path / "anh_cua_toi.png", fake_env["split_csv"])


# ------------------------------------------------------------ review: gói mã Kaggle riêng (không đụng gói niêm phong)


def test_build_inference_code_package_contents(tmp_path: Path) -> None:
    out = tmp_path / "pkg"
    files = build_inference_code_package(REPO_ROOT, out, commit="a" * 40)
    assert (out / "COMMIT").read_text(encoding="utf-8").strip() == "a" * 40
    assert (out / "split_v1.csv").is_file() and (out / "split_v1.sha256").is_file()
    assert (out / "src" / "inference_demo.py").is_file()
    assert (out / "src" / "final_test_runner.py").is_file()
    # Không mang tệp điều khiển của gói đánh giá test
    for forbidden in ("MODE", "CONFIRM_FINAL", "EXPECTED_SHA256"):
        assert not (out / forbidden).exists()
        assert forbidden not in files
    import json

    meta = json.loads((out / "dataset-metadata.json").read_text(encoding="utf-8"))
    assert meta["id"] == "ductrannguyen/cxr-inference-demo-code"


def test_build_inference_code_package_rejects_non_empty_dir(tmp_path: Path) -> None:
    out = tmp_path / "pkg"
    out.mkdir()
    (out / "x.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="khong rong"):
        build_inference_code_package(REPO_ROOT, out, commit="b" * 40)


def test_package_src_is_importable_standalone(tmp_path: Path) -> None:
    """Gói phải tự đủ: import src.inference_demo chỉ với nội dung gói (mô phỏng phiên Kaggle mới)."""
    import subprocess
    import sys

    out = tmp_path / "pkg"
    build_inference_code_package(REPO_ROOT, out, commit="c" * 40)
    run_dir = tmp_path / "run"
    (run_dir / "src").mkdir(parents=True)
    for f in (out / "src").glob("*.py"):
        (run_dir / "src" / f.name).write_bytes(f.read_bytes())
    proc = subprocess.run(
        [sys.executable, "-c", "import src.inference_demo as m; print(m.N_FEATURES)"],
        cwd=run_dir,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "152"
