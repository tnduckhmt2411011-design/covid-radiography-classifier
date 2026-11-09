"""Kiểm thử cấu trúc notebooks/11_inference_demo.ipynb (S5-06) và tuân thủ cổng H7, H2, D4.

Notebook cần ảnh X-quang thật nên không thực thi ở đây; logic suy luận được kiểm thử bằng dữ liệu giả
trong tests/test_inference_demo.py. Test này kiểm tra cấu trúc, cú pháp và các ràng buộc tĩnh.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_11_PATH = REPO_ROOT / "notebooks" / "11_inference_demo.ipynb"
D4_RULE = "Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết chưa kiểm chứng, không nêu nguyên nhân."


@pytest.fixture(scope="module")
def nb() -> dict:
    assert NOTEBOOK_11_PATH.is_file(), f"Thieu notebook {NOTEBOOK_11_PATH}"
    return json.loads(NOTEBOOK_11_PATH.read_text(encoding="utf-8"))


def _cells(nb: dict, kind: str) -> List[str]:
    return ["".join(c.get("source", [])) for c in nb["cells"] if c["cell_type"] == kind]


def test_notebook_is_valid_nbformat(nb: dict) -> None:
    import nbformat

    nbformat.validate(nbformat.from_dict(nb))


def test_notebook_has_enough_cells(nb: dict) -> None:
    assert len([c for c in _cells(nb, "code") if c.strip()]) >= 6
    assert len([c for c in _cells(nb, "markdown") if c.strip()]) >= 5


def test_code_cells_parse_as_python(nb: dict) -> None:
    for idx, src in enumerate(_cells(nb, "code")):
        ast.parse(src, filename=f"cell_{idx}")


def test_notebook_has_no_deep_learning_or_gradio(nb: dict) -> None:
    code = "\n".join(_cells(nb, "code"))
    for lib in ("torch", "tensorflow", "keras", "timm", "fastai"):
        assert f"import {lib}" not in code
        assert f"from {lib}" not in code
    assert "gradio" not in code.lower(), "Gradio thuoc S6-02, khong dung trong notebook 11"


def test_notebook_never_reads_test_split(nb: dict) -> None:
    code = "\n".join(_cells(nb, "code"))
    assert "allow_test" not in code
    assert '"test"' not in code and "'test'" not in code
    assert "preds_test" not in code and "UNLOCK_RECORD" not in code


def test_notebook_uses_standard_functions_from_src(nb: dict) -> None:
    code = "\n".join(_cells(nb, "code"))
    for name in (
        "load_image_grayscale_299",
        "extract_152_features",
        "fit_or_load_model",
        "predict_image",
        "plot_probabilities",
    ):
        assert name in code, f"Notebook phai goi {name} tu src.inference_demo"
    assert "from src.inference_demo import" in code
    assert "152" in code


def test_notebook_documents_frozen_model_and_d4(nb: dict) -> None:
    md = "\n".join(_cells(nb, "markdown"))
    for needle in ("StandardScaler", "SVC", "C=10.0", "Histogram 64", "GLCM 60", "LBP 28"):
        assert needle in md, f"Thieu mo ta '{needle}' trong markdown"
    assert D4_RULE in md
    assert "không phải công cụ chẩn đoán" in md
    code = "\n".join(_cells(nb, "code"))
    assert "load_benchmark_metrics" in code, "Notebook phai doc so do tham chieu tu tep metrics, khong hardcode"


def test_notebook_has_standalone_bootstrap_for_kaggle(nb: dict) -> None:
    code = "\n".join(_cells(nb, "code"))
    assert "/kaggle/input" in code
    assert "COMMIT" in code
    assert "find_data_root" in code


def test_notebook_has_optional_val_check_default_off(nb: dict) -> None:
    code = "\n".join(_cells(nb, "code"))
    assert "RUN_VAL_CHECK = False" in code
    assert "verify_on_val" in code


def test_notebook_outputs_are_cleared_or_absent_of_errors(nb: dict) -> None:
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        for out in c.get("outputs", []):
            assert out.get("output_type") != "error"


# ------------------------------------------------------------ thực thi các cell trên dữ liệu giả


def _build_fake_dataset(root: Path) -> Path:
    """Tạo bộ ảnh 299x299 giả + split_v1.csv giả (có đủ train/val/test để kiểm tra G1)."""
    import hashlib

    import cv2
    import numpy as np
    import pandas as pd

    names = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    sizes = {"train": 24, "val": 8, "test": 4}
    rows = []
    seed = 0
    for split, n in sizes.items():
        for i in range(n):
            k = i % 4
            rel = f"{names[k]}/images/{split}-{i}.png"
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            rng = np.random.default_rng(seed)
            seed += 1
            img = np.clip(40 + 50 * k + rng.integers(-25, 26, size=(299, 299)), 0, 255).astype(np.uint8)
            cv2.imwrite(str(path), img)
            rows.append({"image_id": f"{split}-{i}.png", "label": names[k], "rel_image_path": rel, "split": split})
    csv_path = root / "split_v1.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return csv_path


def test_notebook_cells_execute_end_to_end_on_fake_data(
    nb: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Chạy nguyên bản từng code cell; chỉ thay SHA-256 split, đường dẫn dữ liệu và bộ nhớ đệm."""
    import functools
    import hashlib

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import src.inference_demo as demo

    monkeypatch.chdir(REPO_ROOT)  # _find_repo_root dùng Path.cwd(): cố định để test không phụ thuộc cwd
    data_root = tmp_path / "data"
    data_root.mkdir()
    fake_csv = _build_fake_dataset(data_root)
    fake_sha = hashlib.sha256(fake_csv.read_bytes()).hexdigest()
    sizes = {"train": 24, "val": 8, "test": 4}

    real_fit = demo.fit_or_load_model
    real_verify = demo.verify_on_val
    monkeypatch.setattr(
        demo,
        "fit_or_load_model",
        functools.partial(real_fit, expected_sha256=fake_sha, expected_sizes=sizes),
    )
    monkeypatch.setattr(demo, "verify_on_val", functools.partial(real_verify, reference=None))
    monkeypatch.setenv("CXR_DATA_ROOT", str(data_root))
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    ns: dict = {"__name__": "__main__"}
    for idx, src in enumerate(_cells(nb, "code")):
        exec(compile(src, f"11_inference_demo#cell_{idx}", "exec"), ns)
        if "ENV_NAME =" in src:  # sau cell bootstrap: trỏ sang dữ liệu giả
            ns["SPLIT_CSV"] = fake_csv
        if "CACHE_PATH =" in src:  # sau cell tham số: bật kiểm tra val, đổi chỗ cache
            ns["CACHE_PATH"] = tmp_path / "cache.joblib"
            ns["RUN_VAL_CHECK"] = True

    result = ns["result"]
    assert list(result["probabilities"]) == ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    assert abs(sum(result["probabilities"].values()) - 1.0) < 1e-6
    assert ns["feats"].shape == (152,)
    assert ns["info"]["source"] == "fit"
    assert (tmp_path / "cache.joblib").is_file()
    plt.close("all")


# ------------------------------------------------------------ review S5-06: nội dung, nhánh Kaggle


def test_notebook_handles_any_image_and_guards_heldout(nb: dict) -> None:
    code = "\n".join(_cells(nb, "code"))
    assert "RESIZE_TO_299" in code
    assert "resize=RESIZE_TO_299" in code
    assert "ensure_not_heldout_image" in code
    assert "CXR_DATA_ROOT" in code


def test_notebook_markdown_documents_kaggle_package_and_caveats(nb: dict) -> None:
    md = "\n".join(_cells(nb, "markdown"))
    assert "build_inference_code_package" in md
    assert "kaggle datasets create" in md
    assert "CXR_DATA_ROOT" in md
    assert "gói đánh giá test" in md and "không" in md  # cảnh báo không gắn gói niêm phong
    assert "argmax" in md  # nhãn từ predict() có thể khác cột xác suất cao nhất
    assert "RESIZE_TO_299" in md


def test_notebook_section8_does_not_overclaim(nb: dict) -> None:
    md = "\n".join(_cells(nb, "markdown"))
    assert "đúng mô hình này" not in md
    assert "RUN_VAL_CHECK=True" in md or "RUN_VAL_CHECK = True" in md
    for thousands in ("3.176", "14.815", "3.174"):
        assert thousands not in md, f"Dinh dang so lan lon: {thousands}"


def _find_cell(nb: dict, marker: str) -> str:
    matches = [c for c in _cells(nb, "code") if marker in c]
    assert len(matches) == 1, f"Can dung 1 cell chua '{marker}', tim thay {len(matches)}"
    return matches[0]


def test_notebook_kaggle_branch_bootstrap(nb: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Chạy cell bootstrap + tham số trong cây /kaggle giả: tìm gói COMMIT, chép src, xác định DATA_ROOT."""
    import sys

    from src.inference_demo import build_inference_code_package

    input_root = tmp_path / "kaggle_input"
    working = tmp_path / "kaggle_working"
    working.mkdir()
    pkg = input_root / "cxr-inference-demo-code"
    build_inference_code_package(REPO_ROOT, pkg, commit="d" * 40)
    ds_root = input_root / "covid19-radiography-database" / "COVID-19_Radiography_Dataset"
    (ds_root / "COVID" / "images").mkdir(parents=True)

    monkeypatch.setenv("KAGGLE_INPUT_PATH", str(input_root))
    monkeypatch.setenv("KAGGLE_WORKING_PATH", str(working))
    monkeypatch.delenv("CXR_DATA_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", list(sys.path))

    ns: dict = {"__name__": "__main__"}
    exec(compile(_find_cell(nb, "def _find_kaggle_code_package"), "cell_bootstrap", "exec"), ns)
    exec(compile(_find_cell(nb, "RESIZE_TO_299 ="), "cell_params", "exec"), ns)

    assert ns["ENV_NAME"] == "kaggle"
    assert ns["SPLIT_CSV"] == pkg / "split_v1.csv"
    assert (working / "code" / "src" / "inference_demo.py").is_file()
    assert (working / "code" / "reference" / "val_metrics.json").is_file()
    assert (working / "code" / "reference" / "final_test_metrics.json").is_file()
    assert ns["CODE_ROOT"] == working / "code"
    assert ns["DATA_ROOT"] == ds_root
    assert str(ns["CACHE_PATH"]).startswith(str(working))


def test_notebook_kaggle_bootstrap_from_real_package(
    nb: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kiểm tra mô phỏng Kaggle trực tiếp từ GÓI THẬT outputs/inference_pkg (không dựng tay).

    Xác minh sau khi cell bootstrap chạy, thư mục CODE_ROOT/reference chứa đầy đủ các file metrics
    và load_benchmark_metrics(CODE_ROOT) đọc thành công (không ném FileNotFoundError).
    """
    import shutil
    import sys

    from src.inference_demo import load_benchmark_metrics

    real_pkg = REPO_ROOT / "outputs" / "inference_pkg"
    assert real_pkg.is_dir(), "outputs/inference_pkg phai ton tai truoc khi chay test nay"
    assert (real_pkg / "COMMIT").is_file()

    input_root = tmp_path / "kaggle_input"
    working = tmp_path / "kaggle_working"
    working.mkdir()
    target_pkg = input_root / "cxr-inference-demo-code"
    shutil.copytree(real_pkg, target_pkg)

    ds_root = input_root / "covid19-radiography-database" / "COVID-19_Radiography_Dataset"
    (ds_root / "COVID" / "images").mkdir(parents=True)

    monkeypatch.setenv("KAGGLE_INPUT_PATH", str(input_root))
    monkeypatch.setenv("KAGGLE_WORKING_PATH", str(working))
    monkeypatch.delenv("CXR_DATA_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", list(sys.path))

    ns: dict = {"__name__": "__main__"}
    exec(compile(_find_cell(nb, "def _find_kaggle_code_package"), "cell_bootstrap", "exec"), ns)

    assert ns["ENV_NAME"] == "kaggle"
    code_root = ns["CODE_ROOT"]
    assert (code_root / "reference" / "val_metrics.json").is_file()
    assert (code_root / "reference" / "final_test_metrics.json").is_file()

    bench = load_benchmark_metrics(code_root)
    assert bench["val_macro_f1"] == pytest.approx(0.9024, abs=1e-4)
    assert bench["test_macro_f1"] == pytest.approx(0.8714, abs=1e-4)
    assert bench["diff"] == pytest.approx(-0.0310, abs=1e-4)


def test_notebook_kaggle_branch_fails_clearly_without_inference_package(
    nb: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Gói chỉ có COMMIT (ví dụ gói đánh giá test niêm phong) mà thiếu inference_demo.py phải bị từ chối."""
    import sys

    input_root = tmp_path / "kaggle_input"
    sealed = input_root / "cxr-final-test-code"
    sealed.mkdir(parents=True)
    (sealed / "COMMIT").write_text("e" * 40, encoding="utf-8")
    (sealed / "MODE").write_text("final", encoding="utf-8")
    monkeypatch.setenv("KAGGLE_INPUT_PATH", str(input_root))
    monkeypatch.setenv("KAGGLE_WORKING_PATH", str(tmp_path / "w"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", list(sys.path))
    with pytest.raises(FileNotFoundError, match="inference_demo"):
        exec(compile(_find_cell(nb, "def _find_kaggle_code_package"), "cell_bootstrap", "exec"), {"__name__": "__main__"})
