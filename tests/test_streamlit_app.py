"""Kiểm thử TDD cho demo/streamlit_app.py (S6-02).

Test dùng ảnh giả lập trong bộ nhớ và manifest giả; không đọc ảnh thật,
không đọc nội dung split 'test', không gọi mạng.
"""

from __future__ import annotations

import ast
import base64
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

from demo import streamlit_app as app

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "demo"


def _png(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


def _fake_manifest(tmp_path: Path) -> Path:
    p = tmp_path / "split.csv"
    pd.DataFrame(
        [("val-1.png", "val"), ("test-1.png", "test")],
        columns=["image_id", "split"],
    ).to_csv(p, index=False)
    return p


def test_valid_299_png_is_accepted(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    img = np.full((299, 299), 128, dtype=np.uint8)
    got, resized, warning = app.decode_upload("val-1.png", _png(img), split_csv=manifest)
    assert got.shape == (299, 299)
    assert got.dtype == np.uint8
    assert resized is False
    assert warning is None


def test_color_png_is_converted_to_grayscale(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    img = np.zeros((299, 299, 3), dtype=np.uint8)
    img[:, :, 0] = 255
    got, _, _ = app.decode_upload("val-1.png", _png(img), split_csv=manifest)
    assert got.ndim == 2


def test_non_299_is_resized_and_warns(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    img = np.zeros((320, 256), dtype=np.uint8)
    got, resized, warning = app.decode_upload("val-1.png", _png(img), split_csv=manifest)
    assert got.shape == (299, 299)
    assert resized is True
    assert warning is not None
    assert "299" in warning
    assert "kiểm chứng" in warning


def test_rejects_heldout_filename_before_decoding(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    with pytest.raises(PermissionError, match="test"):
        app.decode_upload("test-1.png", b"not an image", split_csv=manifest)


def test_rejects_non_image_bytes(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    with pytest.raises(ValueError, match="giải mã"):
        app.decode_upload("val-1.png", b"not an image", split_csv=manifest)


def test_rejects_disallowed_extension(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    with pytest.raises(ValueError, match="PNG"):
        app.decode_upload("val-1.gif", _png(np.zeros((299, 299), np.uint8)), split_csv=manifest)


def test_rejects_empty_file(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    with pytest.raises(ValueError, match="rỗng"):
        app.decode_upload("val-1.png", b"", split_csv=manifest)


def test_rejects_oversized_file(tmp_path: Path) -> None:
    manifest = _fake_manifest(tmp_path)
    with pytest.raises(ValueError, match="MB"):
        app.decode_upload("val-1.png", b"0" * (app.MAX_UPLOAD_BYTES + 1), split_csv=manifest)


def test_to_data_url_is_in_memory_and_valid_png() -> None:
    img = np.full((299, 299), 200, dtype=np.uint8)
    url = app.to_data_url(img)
    assert url.startswith("data:image/png;base64,")
    raw = base64.b64decode(url.split(",", 1)[1])
    decoded = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
    assert decoded is not None
    assert decoded.shape == (299, 299)


def test_upload_path_does_not_write_to_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = _fake_manifest(tmp_path)
    workdir = tmp_path / "work"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    img = np.full((299, 299), 100, dtype=np.uint8)
    got, _, _ = app.decode_upload("val-1.png", _png(img), split_csv=manifest)
    app.to_data_url(got)
    assert list(workdir.iterdir()) == []


def test_limitations_text_uses_metrics_and_d4() -> None:
    text = app.build_limitations_text(
        {"val_macro_f1": 0.9024, "test_macro_f1": 0.8714, "diff": -0.0310}
    )
    assert "0.9024" in text
    assert "0.8714" in text
    assert "-0.0310" in text
    assert "chưa được kiểm chứng" in text
    assert "không nêu nguyên nhân" in text
    assert "rq3_shortcut_learning_conclusion.md" in text


def test_metrics_are_read_from_repo_json_not_hardcoded() -> None:
    metrics = app.load_benchmark_metrics(REPO_ROOT)
    val_json = json.loads(
        (REPO_ROOT / "results" / "rq3_ghep_svm_orig_to_orig_s42" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )
    test_json = json.loads(
        (REPO_ROOT / "results" / "final_test" / "metrics.json").read_text(encoding="utf-8")
    )
    assert metrics["val_macro_f1"] == pytest.approx(float(val_json["macro_f1"]))
    assert metrics["test_macro_f1"] == pytest.approx(float(test_json["macro_f1"]))
    assert metrics["diff"] == pytest.approx(
        float(test_json["macro_f1"]) - float(val_json["macro_f1"])
    )


def test_resolve_model_file_uses_public_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CXR_MODEL_PATH", raising=False)
    monkeypatch.delenv("CXR_MODEL_REPO", raising=False)
    target = tmp_path / "model.joblib"
    target.write_bytes(b"x")
    seen = {}

    def fake(repo_id: str, **kwargs):
        seen["repo_id"] = repo_id
        return target

    monkeypatch.setattr(app, "download_and_verify_model", fake)
    assert app.resolve_model_file() == target
    assert seen["repo_id"] == "duc16/cxr-svm-demo"


def test_app_source_has_no_hardcoded_metrics() -> None:
    source = (DEMO_DIR / "streamlit_app.py").read_text(encoding="utf-8")
    assert "0.9024" not in source
    assert "0.8714" not in source


def test_no_forbidden_deep_learning_imports() -> None:
    forbidden = {"torch", "tensorflow", "keras", "timm"}
    for path in (DEMO_DIR / "streamlit_app.py", REPO_ROOT / "src" / "model_artifact.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = {node.module.split(".")[0]}
            else:
                continue
            assert not (names & forbidden), f"{path} imports {names & forbidden}"


def test_app_never_reads_test_split_images() -> None:
    source = (DEMO_DIR / "streamlit_app.py").read_text(encoding="utf-8")
    assert "allow_test" not in source
    assert "load_split_features" not in source
    assert "CXRDataset" not in source
    assert "ensure_not_heldout_image" in source


def test_app_does_not_write_uploaded_images() -> None:
    source = (DEMO_DIR / "streamlit_app.py").read_text(encoding="utf-8")
    assert "cv2.imwrite" not in source
    assert "write_bytes" not in source
    assert "joblib.dump" not in source


def test_medical_disclaimers_present() -> None:
    source = (DEMO_DIR / "streamlit_app.py").read_text(encoding="utf-8")
    assert "KHÔNG DÙNG ĐỂ CHẨN ĐOÁN" in source
    assert "ảnh bệnh nhân thật" in source


def test_no_sample_dataset_images_in_demo() -> None:
    for pattern in ("*.png", "*.jpg", "*.jpeg"):
        assert list(DEMO_DIR.glob(pattern)) == []


def test_demo_requirements_pins_streamlit() -> None:
    text = (DEMO_DIR / "requirements.txt").read_text(encoding="utf-8")
    assert "streamlit==1.66.1" in text


def test_root_requirements_includes_streamlit_for_tests() -> None:
    text = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "streamlit==1.66.1" in text


def test_plot_probabilities_has_four_bars() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from src.inference_demo import plot_probabilities

    result = {
        "label": "COVID",
        "probabilities": {
            "COVID": 0.7,
            "Lung_Opacity": 0.1,
            "Normal": 0.15,
            "Viral Pneumonia": 0.05,
        },
    }
    fig = plot_probabilities(result)
    assert len(fig.axes) == 1
    assert len(fig.axes[0].patches) == 4
    plt.close(fig)
