"""Kiểm thử TDD cho ``src.inference_latency.py`` (đo độ trễ suy luận của demo).

Module được thiết kế nhẹ: các hàm thuần (chọn mẫu, bấm giờ, thống kê, ghi bản
ghi) không kéo theo scikit-image nên bộ kiểm thử này thu thập được ở mọi môi
trường; các bài phụ thuộc kết quả đo thật sẽ tự bỏ qua nếu chưa có tệp.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd
import pytest

from src.inference_latency import (
    DEFAULT_ARTIFACT,
    DEFAULT_SPLIT,
    build_parser,
    collect_environment,
    decode_image,
    load_pipeline,
    measure_image,
    run_measurement,
    select_val_sample,
    summarize,
    write_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Hai ban ghi: che do tuong tac (luot ngan) va che do chay lien tuc (lo dai).
RECORD_DIRS = {
    "interactive": REPO_ROOT / "results" / "demo_latency_interactive",
    "sustained": REPO_ROOT / "results" / "demo_latency_sustained",
}
PUBLISHED_SHA256 = "3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058"
ARTIFACT_BYTES = 7842399


def _write_split(path: Path) -> None:
    """Ghi tệp split giả lập gồm cả ba tập, đủ để kiểm tra việc chọn mẫu."""
    rows = []
    for i in range(30):
        rows.append(
            {
                "image_id": f"val-{i}",
                "label": "COVID",
                "rel_image_path": f"COVID/val-{i}.png",
                "split": "val",
            }
        )
    for i in range(10):
        rows.append(
            {
                "image_id": f"train-{i}",
                "label": "Normal",
                "rel_image_path": f"Normal/train-{i}.png",
                "split": "train",
            }
        )
    for i in range(5):
        rows.append(
            {
                "image_id": f"test-{i}",
                "label": "Lung_Opacity",
                "rel_image_path": f"Lung_Opacity/test-{i}.png",
                "split": "test",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


# ------------------------------------------------------- chọn mẫu


def test_select_val_sample_only_val_ids(tmp_path: Path) -> None:
    """Mẫu đo chỉ được rút từ các dòng thuộc split 'val'."""
    split = tmp_path / "split.csv"
    _write_split(split)

    sample = select_val_sample(split, n=10, seed=42)

    assert len(sample) == 10
    assert set(sample["split"].unique()) == {"val"}
    assert all(str(x).startswith("val-") for x in sample["image_id"])


def test_select_val_sample_deterministic(tmp_path: Path) -> None:
    """Cùng seed cho cùng danh sách ảnh; seed khác cho danh sách khác."""
    split = tmp_path / "split.csv"
    _write_split(split)

    first = select_val_sample(split, n=10, seed=42)
    second = select_val_sample(split, n=10, seed=42)
    other = select_val_sample(split, n=10, seed=7)

    assert list(first["image_id"]) == list(second["image_id"])
    assert list(first["image_id"]) != list(other["image_id"])


def test_select_val_sample_rejects_oversized_n(tmp_path: Path) -> None:
    """Số ảnh yêu cầu vượt cỡ tập val thì phải báo lỗi, không lặng lẽ thu nhỏ."""
    split = tmp_path / "split.csv"
    _write_split(split)
    with pytest.raises(ValueError):
        select_val_sample(split, n=31, seed=42)
    with pytest.raises(ValueError):
        select_val_sample(split, n=0, seed=42)


def test_real_split_val_only_counts(tmp_path: Path) -> None:
    """Tệp split thật trong repo chỉ dùng cỡ val/val id cho mục đích kiểm tra."""
    pytest.importorskip("pandas")
    frame = pd.read_csv(DEFAULT_SPLIT)
    counts = frame["split"].value_counts().to_dict()
    assert counts["val"] == 3174
    assert counts["test"] == 3176
    assert counts["train"] == 14815


# ------------------------------------------------------- bấm giờ và thống kê


def test_decode_image_reads_png_bytes_in_memory() -> None:
    """Giải mã byte PNG trong bộ nhớ thành mảng xám, không đọc tệp."""
    ok, buffer = cv2_imencode_grayscale()
    raw = buffer.tobytes()

    image = decode_image(raw)

    assert image.shape == (299, 299)
    assert image.dtype == np.uint8


def cv2_imencode_grayscale():
    """Mã hóa một ảnh xám giả lập 299×299 thành buffer PNG."""
    import cv2

    img = np.full((299, 299), 120, dtype=np.uint8)
    img[10:40, 10:40] = 250
    ok, buffer = cv2.imencode(".png", img)
    assert ok
    return ok, buffer


def test_measure_image_accounts_three_stages() -> None:
    """measure_image phải trả về ba chặng và tổng bằng đúng tổng ba chặng."""
    calls: List[str] = []

    def decode_fn(raw: bytes) -> np.ndarray:
        calls.append("decode")
        return np.zeros((299, 299), dtype=np.uint8)

    def features_fn(image: np.ndarray) -> np.ndarray:
        calls.append("features")
        return np.zeros(152, dtype=np.float64)

    def inference_fn(feats: np.ndarray) -> Dict[str, object]:
        calls.append("inference")
        return {"label": "COVID"}

    result = measure_image(
        b"\x89PNG",
        scaler=object(),
        clf=object(),
        decode_fn=decode_fn,
        features_fn=features_fn,
        inference_fn=inference_fn,
    )

    assert calls == ["decode", "features", "inference"]
    for key in ("decode_seconds", "features_seconds", "inference_seconds", "total_seconds"):
        assert key in result
    assert result["total_seconds"] == pytest.approx(
        result["decode_seconds"] + result["features_seconds"] + result["inference_seconds"]
    )
    assert all(result[k] >= 0.0 for k in result)


def test_summarize_computes_expected_stats() -> None:
    """summarize phải khớp với numpy cho trung bình, trung vị và phân vị."""
    values = list(np.linspace(0.1, 1.0, 100))

    stats = summarize(values)

    assert stats["n"] == 100
    assert stats["mean"] == pytest.approx(float(np.mean(values)))
    assert stats["median"] == pytest.approx(float(np.median(values)))
    assert stats["p90"] == pytest.approx(float(np.percentile(values, 90)))
    assert stats["p95"] == pytest.approx(float(np.percentile(values, 95)))
    assert stats["min"] == pytest.approx(min(values))
    assert stats["max"] == pytest.approx(max(values))


def test_summarize_rejects_empty() -> None:
    """Không có phép đo nào thì không được thống kê."""
    with pytest.raises(ValueError):
        summarize([])


# ------------------------------------------------------- ghi bản ghi


def _fake_rows(n_images: int, repeats: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for i in range(n_images):
        for r in range(repeats):
            rows.append(
                {
                    "image_id": f"val-{i}",
                    "label": "COVID",
                    "repeat": r,
                    "decode_seconds": 0.01,
                    "features_seconds": 0.20,
                    "inference_seconds": 0.02,
                    "total_seconds": 0.23,
                }
            )
    return rows


def test_write_record_schema_and_csv_rows(tmp_path: Path) -> None:
    """write_record phải ghi JSON đủ khóa và CSV đủ n × repeats dòng."""
    rows = _fake_rows(4, 3)
    method = {
        "split": "val",
        "split_sha256": "a" * 64,
        "n_images": 4,
        "seed": 42,
        "repeats": 3,
        "warmup_images": 1,
        "timer": "time.perf_counter (wall)",
        "call_path": "cv2.imdecode -> extract_152_features -> predict_image",
        "decode_timed_on_bytes_in_memory": True,
        "percentile_method": "numpy.percentile (linear)",
    }
    record = {
        "record": "demo_inference_latency",
        "generated_utc": "2026-11-12T00:00:00Z",
        "method": method,
        "environment": {"os": "test", "cpu": "test", "cores": 8, "python": "3.12"},
        "artifact": {"sha256": PUBLISHED_SHA256, "bytes": ARTIFACT_BYTES, "n_train": 14815},
        "stats": {"per_image_median_seconds": {"total_seconds": summarize([r["total_seconds"] for r in rows])}},
        "totals": {"measurements": len(rows), "wall_seconds": 1.0},
    }

    out = write_record(tmp_path, record, rows)

    assert (tmp_path / "latency.json").is_file()
    assert (tmp_path / "per_image.csv").is_file()
    reloaded = json.loads((tmp_path / "latency.json").read_text(encoding="utf-8"))
    assert reloaded["method"]["n_images"] == 4
    assert reloaded["method"]["repeats"] == 3
    assert reloaded["totals"]["measurements"] == 12
    saved = pd.read_csv(tmp_path / "per_image.csv")
    assert len(saved) == 12
    assert list(saved.columns) == [
        "image_id",
        "label",
        "repeat",
        "decode_seconds",
        "features_seconds",
        "inference_seconds",
        "total_seconds",
    ]


# ------------------------------------------------------- môi trường


def test_collect_environment_has_required_fields() -> None:
    """Môi trường đo phải ghi đủ các trường dùng để tái lập."""
    env = collect_environment()

    for key in (
        "os",
        "cpu",
        "cores",
        "python",
        "numpy",
        "scikit_learn",
        "scikit_image",
        "opencv",
        "joblib",
        "pandas",
        "pyyaml",
    ):
        assert key in env, f"Thieu truong moi truong: {key}"
    assert str(env["cores"]) != ""
    assert str(env["python"]) != ""


# ------------------------------------------------------- CLI


def test_parser_defaults() -> None:
    """Mặc định CLI: 200 ảnh, seed 42, một lượt, một ảnh khởi động."""
    args = build_parser().parse_args([])

    assert args.n == 200
    assert args.seed == 42
    assert args.repeats == 1
    assert args.warmup == 1


def test_run_measurement_rejects_oversized_n_before_loading(tmp_path: Path) -> None:
    """run_measurement phải báo lỗi trước khi nạp artifact hay đọc ảnh."""
    split = tmp_path / "split.csv"
    _write_split(split)
    with pytest.raises(ValueError):
        run_measurement(
            dataset_root=tmp_path,
            artifact=tmp_path / "artifact.joblib",
            split_csv=split,
            n=31,
            seed=42,
            repeats=1,
            out_dir=tmp_path / "out",
        )


# ------------------------------------------------------- kết quả đo thật


@pytest.mark.parametrize("mode", sorted(RECORD_DIRS))
def test_recorded_result_uses_val_only_images(mode: str) -> None:
    """Bản ghi đã công bố chỉ được chứa ảnh val; không ảnh test nào xuất hiện."""
    record_json = RECORD_DIRS[mode] / "latency.json"
    record_csv = RECORD_DIRS[mode] / "per_image.csv"
    if not record_json.is_file():
        pytest.skip(f"Chưa có bản ghi chế độ {mode}")
    record = json.loads(record_json.read_text(encoding="utf-8"))
    saved = pd.read_csv(record_csv)
    split = pd.read_csv(DEFAULT_SPLIT)
    val_ids = set(split.loc[split["split"] == "val", "image_id"])
    test_ids = set(split.loc[split["split"] == "test", "image_id"])

    ids = set(saved["image_id"])
    assert ids, "per_image.csv rong"
    assert ids.issubset(val_ids), "Có ảnh không thuộc split val"
    assert ids.isdisjoint(test_ids), "Có ảnh thuộc split test"
    assert len(saved) == record["method"]["n_images"] * record["method"]["repeats"]
    assert saved["repeat"].nunique() == record["method"]["repeats"]


@pytest.mark.parametrize("mode", sorted(RECORD_DIRS))
def test_recorded_result_matches_frozen_artifact(mode: str) -> None:
    """Bản ghi phải ghi đúng băm và kích thước artifact đã công bố."""
    record_json = RECORD_DIRS[mode] / "latency.json"
    if not record_json.is_file():
        pytest.skip(f"Chưa có bản ghi chế độ {mode}")
    record = json.loads(record_json.read_text(encoding="utf-8"))
    artifact = record["artifact"]

    assert artifact["sha256"] == PUBLISHED_SHA256
    assert artifact["bytes"] == ARTIFACT_BYTES
    split = pd.read_csv(DEFAULT_SPLIT)
    n_train = int((split["split"] == "train").sum())
    assert artifact["n_train"] == n_train == 14815
    assert artifact["split_sha256"] == "f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98"


@pytest.mark.parametrize("mode", sorted(RECORD_DIRS))
def test_recorded_stats_are_positive_and_ordered(mode: str) -> None:
    """Trung vị phải nằm giữa min và max; các chặng đều dương."""
    record_json = RECORD_DIRS[mode] / "latency.json"
    if not record_json.is_file():
        pytest.skip(f"Chưa có bản ghi chế độ {mode}")
    record = json.loads(record_json.read_text(encoding="utf-8"))
    stats = record["stats"]["per_image_median_seconds"]

    for stage in ("decode_seconds", "features_seconds", "inference_seconds", "total_seconds"):
        assert stage in stats, f"Thieu thong ke chang {stage}"
        assert stats[stage]["min"] > 0.0
        assert stats[stage]["min"] <= stats[stage]["median"] <= stats[stage]["max"]
        assert stats[stage]["p95"] >= stats[stage]["median"]
        assert stats[stage]["n"] == record["method"]["n_images"]
