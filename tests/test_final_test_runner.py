"""Kiểm thử TDD cho src/final_test_runner.py (S5-04, S5-05): đánh giá tập test MỘT lần duy nhất.

Toàn bộ test dùng dữ liệu giả; không đọc tập test thật.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import pytest
import yaml

from src.final_test_runner import (
    CONFIRM_STRING_SHA256,
    EXPECTED_SPLIT_SHA256,
    EXPECTED_SPLIT_SIZES,
    G5_TOLERANCE,
    REFERENCE_VAL_MACRO_F1,
    check_frozen_config,
    check_split_integrity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = REPO_ROOT / "results" / "rq3_ghep_svm_orig_to_orig_s42"
CLASS_LABELS = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]


def _write_split_csv(path: Path, sizes: Dict[str, int]) -> str:
    """Tạo split_v1.csv giả với số dòng cho từng split và trả về SHA256."""
    rows = []
    for split, n in sizes.items():
        for i in range(n):
            label = CLASS_LABELS[i % len(CLASS_LABELS)]
            rows.append({"image_id": f"{split}-{i}.png", "label": label, "split": split})
    pd.DataFrame(rows).to_csv(path, index=False)
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- Task 1: G1, G2


def test_constants_match_spec() -> None:
    assert EXPECTED_SPLIT_SHA256 == "f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98"
    assert EXPECTED_SPLIT_SIZES == {"train": 14815, "val": 3174, "test": 3176}
    assert REFERENCE_VAL_MACRO_F1 == 0.9024
    assert G5_TOLERANCE == 0.002


def test_g1_accepts_valid(tmp_path: Path) -> None:
    sizes = {"train": 6, "val": 3, "test": 2}
    csv_path = tmp_path / "split_v1.csv"
    sha = _write_split_csv(csv_path, sizes)
    assert check_split_integrity(csv_path, expected_sha256=sha, expected_sizes=sizes) == sha


def test_g1_rejects_wrong_sha(tmp_path: Path) -> None:
    sizes = {"train": 6, "val": 3, "test": 2}
    csv_path = tmp_path / "split_v1.csv"
    _write_split_csv(csv_path, sizes)
    with pytest.raises(ValueError, match="SHA256"):
        check_split_integrity(csv_path, expected_sha256="0" * 64, expected_sizes=sizes)


def test_g1_rejects_wrong_sizes(tmp_path: Path) -> None:
    csv_path = tmp_path / "split_v1.csv"
    sha = _write_split_csv(csv_path, {"train": 6, "val": 3, "test": 1})
    with pytest.raises(ValueError, match="test"):
        check_split_integrity(
            csv_path,
            expected_sha256=sha,
            expected_sizes={"train": 6, "val": 3, "test": 2},
        )


def test_g1_real_split_file_matches_constants() -> None:
    """Chỉ đọc tệp manifest splits/split_v1.csv (không đọc ảnh)."""
    assert (
        check_split_integrity(REPO_ROOT / "splits" / "split_v1.csv") == EXPECTED_SPLIT_SHA256
    )


def _reference_config() -> Dict[str, Any]:
    return yaml.safe_load((REFERENCE_DIR / "config.yaml").read_text(encoding="utf-8"))


def test_g2_accepts_repo_reference_config() -> None:
    check_frozen_config(_reference_config())


@pytest.mark.parametrize(
    "path,value",
    [
        (("hyperparameters", "probability"), False),
        (("hyperparameters", "C"), 1.0),
        (("hyperparameters", "gamma"), "auto"),
        (("hyperparameters", "class_weight"), None),
        (("hyperparameters", "random_state"), 7),
        (("seed",), 7),
        (("preprocessing", "scaler"), "MinMaxScaler"),
        (("eval_mask_mode",), "lung_only"),
        (("train_mask_mode",), "outside_only"),
        (("evaluation", "allow_test"), True),
        (("features",), "hist"),
        (("classifier_tag",), "rf"),
        (("split", "sha256"), "0" * 64),
    ],
)
def test_g2_rejects_each_changed_field(path: Tuple[str, ...], value: Any) -> None:
    cfg = copy.deepcopy(_reference_config())
    node = cfg
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError):
        check_frozen_config(cfg)


def test_g2_rejects_missing_field() -> None:
    cfg = copy.deepcopy(_reference_config())
    del cfg["hyperparameters"]["probability"]
    with pytest.raises(ValueError):
        check_frozen_config(cfg)


# ---------------------------------------------------------------- Task 2: G3, G4, G6

from src.final_test_runner import (  # noqa: E402
    UNLOCK_RECORD_NAME,
    check_confirm_final,
    check_not_already_unlocked,
    write_unlock_record,
)

TEST_CONFIRM_TEXT = "CHUOI-XAC-NHAN-DUNG-CHO-KIEM-THU"
TEST_CONFIRM_SHA = hashlib.sha256(TEST_CONFIRM_TEXT.encode("utf-8")).hexdigest()


def test_g3_passes_on_empty_dir(tmp_path: Path) -> None:
    check_not_already_unlocked(tmp_path)


def test_g3_refuses_when_record_exists(tmp_path: Path) -> None:
    final_dir = tmp_path / "final_test"
    final_dir.mkdir()
    (final_dir / UNLOCK_RECORD_NAME).write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="G3"):
        check_not_already_unlocked(tmp_path)


def test_g3_dry_dir_does_not_block(tmp_path: Path) -> None:
    (tmp_path / "dry").mkdir()
    (tmp_path / "dry" / "dry_summary.json").write_text("{}", encoding="utf-8")
    check_not_already_unlocked(tmp_path)


def test_g4_missing_file(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


def test_g4_wrong_string(tmp_path: Path) -> None:
    (tmp_path / "CONFIRM_FINAL").write_text("SAI-CHUOI", encoding="utf-8")
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


def test_g4_empty_string(tmp_path: Path) -> None:
    (tmp_path / "CONFIRM_FINAL").write_text("", encoding="utf-8")
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


def test_g4_rejects_string_with_extra_text(tmp_path: Path) -> None:
    (tmp_path / "CONFIRM_FINAL").write_text(TEST_CONFIRM_TEXT + " them", encoding="utf-8")
    with pytest.raises(PermissionError, match="G4"):
        check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA)


@pytest.mark.parametrize("tail", ["", "\n", "\r\n"])
def test_g4_correct_string_accepts_trailing_newline(tmp_path: Path, tail: str) -> None:
    (tmp_path / "CONFIRM_FINAL").write_bytes((TEST_CONFIRM_TEXT + tail).encode("utf-8"))
    assert check_confirm_final(tmp_path, expected_sha256=TEST_CONFIRM_SHA) == TEST_CONFIRM_SHA


def test_g6_record_contains_fields_and_is_valid_json(tmp_path: Path) -> None:
    final_dir = tmp_path / "final_test"
    path = write_unlock_record(
        final_dir,
        commit="a" * 40,
        split_sha256=EXPECTED_SPLIT_SHA256,
        val_macro_f1=0.9024,
        confirm_sha256=TEST_CONFIRM_SHA,
    )
    assert path == final_dir / UNLOCK_RECORD_NAME
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["commit"] == "a" * 40
    assert rec["split_sha256"] == EXPECTED_SPLIT_SHA256
    assert rec["val_macro_f1"] == 0.9024
    assert rec["confirm_sha256"] == TEST_CONFIRM_SHA
    assert rec["utc_time"].endswith("Z")


def test_g6_refuses_to_overwrite_existing_record(tmp_path: Path) -> None:
    final_dir = tmp_path / "final_test"
    kwargs = dict(
        commit="a" * 40,
        split_sha256=EXPECTED_SPLIT_SHA256,
        val_macro_f1=0.9024,
        confirm_sha256=TEST_CONFIRM_SHA,
    )
    write_unlock_record(final_dir, **kwargs)
    with pytest.raises(RuntimeError, match="G3"):
        write_unlock_record(final_dir, **kwargs)


# ------------------------------------------------ Task 3: mô hình, G5, nạp đặc trưng

import cv2  # noqa: E402

from src.final_test_runner import (  # noqa: E402
    check_val_reproduction,
    fit_frozen_model,
    load_split_features,
    predict_with_model,
)
from src.rq3_runner import FROZEN_SVM_PARAMS  # noqa: E402


def _toy_xy(n_per_class: int = 12, dims: int = 8, seed: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    xs, ys = [], []
    for c in range(4):
        xs.append(rng.normal(loc=c * 3.0, scale=1.0, size=(n_per_class, dims)))
        ys.append(np.full(n_per_class, c, dtype=np.int64))
    return np.vstack(xs), np.concatenate(ys)


def test_fit_uses_frozen_params_and_scaler_fit_on_train_only() -> None:
    x, y = _toy_xy()
    scaler, clf = fit_frozen_model(x, y)
    params = clf.get_params()
    for key, value in FROZEN_SVM_PARAMS.items():
        assert params[key] == value, key
    np.testing.assert_allclose(scaler.mean_, x.mean(axis=0))
    np.testing.assert_allclose(scaler.scale_, x.std(axis=0))


def test_predict_with_model_shapes_and_proba_rows_sum_to_one() -> None:
    x, y = _toy_xy()
    scaler, clf = fit_frozen_model(x, y)
    y_pred, proba = predict_with_model(scaler, clf, x)
    assert y_pred.shape == (len(x),)
    assert proba.shape == (len(x), 4)
    np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-6)


@pytest.mark.parametrize(
    "value,ok",
    [(0.9024, True), (0.9044, True), (0.9004, True), (0.9045, False), (0.9003, False), (0.0723, False)],
)
def test_g5_boundaries(value: float, ok: bool) -> None:
    if ok:
        check_val_reproduction(value)
    else:
        with pytest.raises(RuntimeError, match="G5"):
            check_val_reproduction(value)


def _write_images(base: Path, per_split: Dict[str, int]) -> pd.DataFrame:
    """Tạo ảnh xám giả 299x299 cho từng split và trả về split_df."""
    rng = np.random.default_rng(5)
    rows: List[Dict[str, Any]] = []
    classes = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    for split, n in per_split.items():
        for i in range(n):
            label = classes[i % 4]
            rel = f"{label}/images/{label}-{split}{i}.png"
            path = base / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(path), rng.integers(0, 255, size=(299, 299), dtype=np.uint8))
            rows.append(
                {
                    "image_id": f"{label}-{split}{i}.png",
                    "label": label,
                    "rel_image_path": rel,
                    "split": split,
                    "group_id": f"G{i}",
                }
            )
    return pd.DataFrame(rows)


def test_loader_refuses_test_without_allow(tmp_path: Path) -> None:
    split_df = _write_images(tmp_path, {"train": 4, "val": 4, "test": 4})
    with pytest.raises(PermissionError, match="allow_test"):
        load_split_features(split_df, "test", tmp_path)


def test_loader_rejects_unknown_split(tmp_path: Path) -> None:
    split_df = _write_images(tmp_path, {"train": 4})
    with pytest.raises(ValueError):
        load_split_features(split_df, "holdout", tmp_path)


def test_loader_reads_synthetic_val_with_152_dims(tmp_path: Path) -> None:
    split_df = _write_images(tmp_path, {"train": 4, "val": 8, "test": 4})
    x, ids, y, info = load_split_features(split_df, "val", tmp_path)
    assert x.shape == (8, 152)
    assert len(ids) == 8 and y.shape == (8,)
    assert set(y.tolist()) == {0, 1, 2, 3}
    assert info["n_images"] == 8


def test_loader_reads_synthetic_test_only_with_allow(tmp_path: Path) -> None:
    split_df = _write_images(tmp_path, {"train": 4, "val": 4, "test": 4})
    x, ids, y, _ = load_split_features(split_df, "test", tmp_path, allow_test=True)
    assert x.shape == (4, 152)
    assert all("test" in i for i in ids)


# ------------------------------------- Task 4: run_final_test (dry, final) và báo cáo

import src.final_test_runner as ftr  # noqa: E402
from src.bootstrap import macro_f1_from_labels  # noqa: E402
from src.final_test_runner import FINAL_DIRNAME, DRY_DIRNAME, build_final_report, run_final_test  # noqa: E402

THRESHOLD_PATH = REPO_ROOT / "results" / "threshold_v3.md"
CLASS_LABELS = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]


def _toy_split_df(n_train: int = 40, n_val: int = 20, n_test: int = 20) -> pd.DataFrame:
    rows = []
    for split, n in (("train", n_train), ("val", n_val), ("test", n_test)):
        for i in range(n):
            label = CLASS_LABELS[i % 4]
            rows.append({"image_id": f"{label}-{split}{i}.png", "label": label, "split": split})
    return pd.DataFrame(rows)


class FakeLoader:
    """Bộ nạp đặc trưng giả: ghi nhật ký lời gọi, không đọc ảnh."""

    def __init__(self, out_dir: Path, fail_on_test: bool = False, dims: int = 8) -> None:
        self.calls: List[Tuple[str, bool]] = []
        self.out_dir = out_dir
        self.fail_on_test = fail_on_test
        self.dims = dims
        self.unlock_existed_at_first_test_call: Any = None

    def __call__(self, split_df, split, dataset_root, *, allow_test=False):
        self.calls.append((split, allow_test))
        if split == "test":
            if not allow_test:
                raise PermissionError("test bi khoa")
            if self.unlock_existed_at_first_test_call is None:
                self.unlock_existed_at_first_test_call = (
                    self.out_dir / FINAL_DIRNAME / UNLOCK_RECORD_NAME
                ).exists()
            if self.fail_on_test:
                raise OSError("su co ha tang khi doc test")
        sub = split_df[split_df["split"] == split].reset_index(drop=True)
        y = np.array([CLASS_LABELS.index(lbl) for lbl in sub["label"]], dtype=np.int64)
        seed = {"train": 1, "val": 2, "test": 3}[split]
        rng = np.random.default_rng(seed)
        x = rng.normal(loc=y[:, None] * 3.0, scale=1.0, size=(len(y), self.dims))
        return x, sub["image_id"].tolist(), y, {"n_images": len(y), "glcm_nan_images": 0}


def _toy_val_f1(out_dir: Path) -> float:
    """Macro-F1 val của mô hình đóng băng trên dữ liệu giả (dùng làm tham chiếu G5 trong test)."""
    split_df = _toy_split_df()
    loader = FakeLoader(out_dir)
    x_tr, _, y_tr, _ = loader(split_df, "train", None)
    x_va, _, y_va, _ = loader(split_df, "val", None)
    scaler, clf = fit_frozen_model(x_tr, y_tr)
    pred, _ = predict_with_model(scaler, clf, x_va)
    return macro_f1_from_labels(y_va, pred)


@pytest.fixture
def env(tmp_path: Path) -> Dict[str, Any]:
    sizes = {"train": 40, "val": 20, "test": 20}
    split_csv = tmp_path / "split_v1.csv"
    sha = _write_split_csv(split_csv, sizes)
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    return {
        "tmp": tmp_path,
        "split_csv": split_csv,
        "pkg": pkg,
        "out": out_dir,
        "sha": sha,
        "sizes": sizes,
        "ref_f1": _toy_val_f1(out_dir),
    }


def _run(env: Dict[str, Any], mode: str, loader: Any = None, **overrides: Any) -> Dict[str, Any]:
    """Gọi run_final_test với ghi đè cổng (chỉ dùng trong test)."""
    split_df_path = env["split_csv"]
    # split_v1.csv giả chỉ có cột split; bộ nạp giả cần image_id/label -> dùng bản đầy đủ
    kwargs: Dict[str, Any] = dict(
        mode=mode,
        dataset_root=env["tmp"],
        split_csv=split_df_path,
        reference_dir=REFERENCE_DIR,
        pkg_dir=env["pkg"],
        out_dir=env["out"],
        commit="c" * 40,
        threshold_path=THRESHOLD_PATH,
        feature_loader=loader if loader is not None else FakeLoader(env["out"]),
        expected_split_sha256=env["sha"],
        expected_split_sizes=env["sizes"],
        reference_val_macro_f1=env["ref_f1"],
        g5_tolerance=G5_TOLERANCE,
        expected_confirm_sha256=TEST_CONFIRM_SHA,
        n_boot=50,
    )
    kwargs.update(overrides)
    return run_final_test(**kwargs)


def _confirm(env: Dict[str, Any]) -> None:
    (env["pkg"] / "CONFIRM_FINAL").write_text(TEST_CONFIRM_TEXT, encoding="utf-8")


def test_dry_never_requests_test_and_writes_no_unlock_record(env: Dict[str, Any]) -> None:
    loader = FakeLoader(env["out"])
    summary = _run(env, "dry", loader)
    assert [s for s, _ in loader.calls] == ["train", "val"]
    assert all(allow is False for _, allow in loader.calls)
    assert not (env["out"] / FINAL_DIRNAME).exists()
    assert (env["out"] / DRY_DIRNAME / "dry_summary.json").is_file()
    assert summary["test_read"] is False


def test_dry_runs_full_train_val_and_real_g5(env: Dict[str, Any]) -> None:
    summary = _run(env, "dry")
    assert summary["n_train"] == 40 and summary["n_val"] == 20
    assert abs(summary["val_macro_f1"] - env["ref_f1"]) <= G5_TOLERANCE
    saved = json.loads((env["out"] / DRY_DIRNAME / "dry_summary.json").read_text(encoding="utf-8"))
    assert saved["g5_passed"] is True


def test_dry_g5_failure_aborts(env: Dict[str, Any]) -> None:
    loader = FakeLoader(env["out"])
    with pytest.raises(RuntimeError, match="G5"):
        _run(env, "dry", loader, reference_val_macro_f1=0.5)
    assert "test" not in [s for s, _ in loader.calls]


def test_dry_does_not_need_confirm_final(env: Dict[str, Any]) -> None:
    assert not (env["pkg"] / "CONFIRM_FINAL").exists()
    _run(env, "dry")


def test_invalid_mode_rejected(env: Dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        _run(env, "t0")


def test_final_writes_unlock_before_first_test_load(env: Dict[str, Any]) -> None:
    _confirm(env)
    loader = FakeLoader(env["out"])
    _run(env, "final", loader)
    assert loader.unlock_existed_at_first_test_call is True
    assert loader.calls[-1] == ("test", True)
    assert [s for s, _ in loader.calls] == ["train", "val", "test"]


def test_final_fits_exactly_once_and_predicts_with_g5_model(
    env: Dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    _confirm(env)
    fits: List[Tuple[Any, Any]] = []
    predicts: List[Tuple[int, int, int]] = []
    real_fit = ftr.fit_frozen_model
    real_predict = ftr.predict_with_model

    def spy_fit(x, y):
        scaler, clf = real_fit(x, y)
        fits.append((scaler, clf))
        return scaler, clf

    def spy_predict(scaler, clf, x):
        predicts.append((id(scaler), id(clf), len(x)))
        return real_predict(scaler, clf, x)

    monkeypatch.setattr(ftr, "fit_frozen_model", spy_fit)
    monkeypatch.setattr(ftr, "predict_with_model", spy_predict)
    _run(env, "final")
    assert len(fits) == 1
    scaler, clf = fits[0]
    assert len(predicts) == 2  # val (G5) và test
    assert all(p[0] == id(scaler) and p[1] == id(clf) for p in predicts)
    assert predicts[-1][2] == 20  # lần cuối là test (20 ảnh giả)


@pytest.mark.parametrize("gate", ["G1", "G2", "G3", "G4", "G5"])
def test_final_aborts_before_test_when_any_gate_fails(env: Dict[str, Any], gate: str) -> None:
    loader = FakeLoader(env["out"])
    overrides: Dict[str, Any] = {}
    if gate != "G4":
        _confirm(env)
    if gate == "G1":
        overrides["expected_split_sha256"] = "0" * 64
    elif gate == "G2":
        cfg = yaml.safe_load((REFERENCE_DIR / "config.yaml").read_text(encoding="utf-8"))
        cfg["hyperparameters"]["probability"] = False
        ref_dir = env["tmp"] / "bad_ref"
        ref_dir.mkdir()
        (ref_dir / "config.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
        overrides["reference_dir"] = ref_dir
    elif gate == "G3":
        (env["out"] / FINAL_DIRNAME).mkdir()
        (env["out"] / FINAL_DIRNAME / UNLOCK_RECORD_NAME).write_text("{}", encoding="utf-8")
    elif gate == "G5":
        overrides["reference_val_macro_f1"] = 0.5
    with pytest.raises((ValueError, RuntimeError, PermissionError)):
        _run(env, "final", loader, **overrides)
    assert "test" not in [s for s, _ in loader.calls]
    if gate in ("G1", "G2", "G3", "G4"):
        assert loader.calls == []
    if gate == "G5":
        assert not (env["out"] / FINAL_DIRNAME / UNLOCK_RECORD_NAME).exists()


def test_final_infrastructure_failure_leaves_only_unlock_record(env: Dict[str, Any]) -> None:
    _confirm(env)
    loader = FakeLoader(env["out"], fail_on_test=True)
    with pytest.raises(OSError):
        _run(env, "final", loader)
    files = sorted(p.name for p in (env["out"] / FINAL_DIRNAME).iterdir())
    assert files == [UNLOCK_RECORD_NAME]


def test_final_outputs_and_report_fields(env: Dict[str, Any]) -> None:
    _confirm(env)
    summary = _run(env, "final")
    final_dir = env["out"] / FINAL_DIRNAME
    for name in (
        "config.yaml",
        "metrics.json",
        "log",
        "preds_test.csv",
        UNLOCK_RECORD_NAME,
        "final_test_report.json",
        "r5_gioi_han.md",
    ):
        assert (final_dir / name).is_file(), name
    assert summary["test_read"] is True
    report = json.loads((final_dir / "final_test_report.json").read_text(encoding="utf-8"))
    for key in (
        "macro_f1",
        "ci95_low",
        "ci95_high",
        "accuracy",
        "per_class",
        "confusion_matrix",
        "r2_normal_lung_opacity",
        "r4_sampling_error",
        "val_macro_f1",
        "test_minus_val",
        "interpretation_note",
    ):
        assert key in report, key
    assert report["test_minus_val"] == pytest.approx(report["macro_f1"] - report["val_macro_f1"], abs=1e-6)
    assert "gia thuyet chua kiem chung" in report["interpretation_note"]
    assert "cause" not in report and "explanation" not in report
    preds = pd.read_csv(final_dir / "preds_test.csv")
    assert len(preds) == 20
    assert list(preds.columns)[:3] == ["image_id", "y_true", "y_pred"]


def test_dry_then_final_same_out_dir_not_blocked(env: Dict[str, Any]) -> None:
    _run(env, "dry")
    _confirm(env)
    _run(env, "final")
    assert (env["out"] / DRY_DIRNAME).is_dir() and (env["out"] / FINAL_DIRNAME).is_dir()


def test_second_final_in_same_out_dir_is_refused(env: Dict[str, Any]) -> None:
    _confirm(env)
    _run(env, "final")
    loader = FakeLoader(env["out"])
    with pytest.raises(RuntimeError, match="G3"):
        _run(env, "final", loader)
    assert loader.calls == []


def test_build_final_report_ci_contains_point_estimate() -> None:
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 4, size=200)
    y_pred = np.where(rng.random(200) < 0.8, y_true, rng.integers(0, 4, size=200))
    rep = build_final_report(y_true, y_pred, 0.85, n_boot=100, rng_seed=42, threshold_path=THRESHOLD_PATH)
    assert rep["ci95_low"] <= rep["macro_f1"] <= rep["ci95_high"]
    assert rep["r4_sampling_error"]["n_all"] == 200
    assert len(rep["confusion_matrix"]) == 4
    assert set(rep["r2_normal_lung_opacity"]) == {"LO_to_LO", "LO_to_Normal", "Normal_to_LO", "Normal_to_Normal"}
