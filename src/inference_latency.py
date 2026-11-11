"""Đo độ trễ suy luận của pipeline demo S6-02 và ghi bản ghi kết quả.

Mục đích: cung cấp số đo thực tế cho mục 5.5.4 của báo cáo (độ trễ suy luận),
đo trên đúng đường đi của ứng dụng demo:

    byte ảnh -> ``cv2.imdecode`` (xám) -> ``extract_152_features`` (152 chiều)
    -> ``predict_image`` (StandardScaler + SVC RBF, 4 xác suất)

Quy tắc bắt buộc:

- Chỉ đo trên ảnh thuộc split ``val``; không đọc ảnh của split ``test``.
- Không huấn luyện lại; artifact đóng băng được nạp từ đĩa và kiểm băm.
- Thời gian tải artifact từ Hugging Face (lần khởi động lạnh, phụ thuộc mạng)
  không tính vào độ trễ suy luận; chỉ ghi thời gian nạp từ tệp cục bộ.
- Đọc tệp ảnh nằm ngoài đồng hồ (ứng dụng nhận byte từ trình duyệt); đồng hồ chỉ
  bám các bước tính toán.

Hai chế độ đo (phát hiện khi đo thực tế trên máy Windows): sau vài chục ảnh,
CPU giảm tần và thời gian mỗi ảnh tăng gấp khoảng bốn lần rồi ổn định; nghỉ
giữa các ảnh không đưa máy về trạng thái lạnh. Vì vậy:

- **Chế độ tương tác** (người dùng tải từng ảnh, máy nghỉ giữa các lần): đo bằng
  lượt **ngắn** (ví dụ ``--n 20``) chạy ngay sau khi máy nghỉ, ghi ra một thư mục
  riêng (``results/demo_latency_interactive``).
- **Chế độ chạy liên tục** (xử lý hàng loạt): đo bằng lô dài
  (``--n 200 --repeats 3``), ghi ra ``results/demo_latency_sustained``.

Cùng một script, cùng seed nên hai bản ghi so trực tiếp được.

Chạy trên máy cục bộ::

    python -m src.inference_latency --dataset-root D:\\cxr_data\\COVID-19_Radiography_Dataset

Chạy trên Kaggle CPU (nếu cần mốc cùng môi trường thực nghiệm RQ1/RQ2): dựng
kernel theo khuôn ``kaggle/inference_demo/`` (cùng ``code_file``, trỏ
``--dataset-root`` tới thư mục dataset đính kèm và ``--artifact`` tới bản sao
artifact; artifact có thể kiểm băm từ kho công khai). Mẫu và seed giữ nguyên nên
số đo hai môi trường so trực tiếp được.

Đầu ra: ``latency.json`` (phương pháp, môi trường, artifact, thống kê) và
``per_image.csv`` (thời gian từng ảnh, từng lượt) trong thư mục ``--out-dir``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import cv2
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPLIT = REPO_ROOT / "splits" / "split_v1.csv"
DEFAULT_ARTIFACT = REPO_ROOT / "outputs" / "k_v3_out" / "cxr_inference_model_cache.joblib"
DEFAULT_OUT_DIR = REPO_ROOT / "results" / "demo_latency"
DEFAULT_DATASET = Path(r"D:\cxr_data\COVID-19_Radiography_Dataset")

STAGE_KEYS: Sequence[str] = ("decode_seconds", "features_seconds", "inference_seconds", "total_seconds")
PER_IMAGE_COLUMNS: Sequence[str] = ("image_id", "label", "repeat", *STAGE_KEYS)


def select_val_sample(split_csv: Path, n: int, seed: int) -> pd.DataFrame:
    """Chọn mẫu ngẫu nhiên trong split 'val', cùng seed cho cùng mẫu.

    Raises:
        ValueError: Nếu ``n`` nhỏ hơn 1 hoặc vượt số ảnh của tập val.
    """
    frame = pd.read_csv(split_csv)
    val = frame[frame["split"] == "val"].reset_index(drop=True)
    if n < 1:
        raise ValueError(f"So anh yeu cau phai >= 1, nhan {n}.")
    if n > len(val):
        raise ValueError(f"So anh yeu cau {n} vuot so anh val {len(val)}.")
    return val.sample(n=n, random_state=seed, replace=False).reset_index(drop=True)


def decode_image(raw: bytes) -> np.ndarray:
    """Giải mã byte ảnh thành mảng xám uint8, đúng đường đi của ứng dụng."""
    buffer = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Khong giai ma duoc byte anh thanh anh xam.")
    return image


def measure_image(
    raw: bytes,
    scaler: object,
    clf: object,
    *,
    decode_fn: Callable[[bytes], np.ndarray] = decode_image,
    features_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    inference_fn: Optional[Callable[[np.ndarray], Dict[str, object]]] = None,
) -> Dict[str, float]:
    """Bấm giờ ba chặng cho một ảnh; trả về thời gian từng chặng và tổng.

    Các hàm ``features_fn`` và ``inference_fn`` nhận vào để kiểm thử không cần
    nạp mô hình thật; khi bỏ trống, luồng chạy thật tự nạp từ ``src.inference_demo``.
    """
    if features_fn is None or inference_fn is None:
        from src.inference_demo import extract_152_features, predict_image

        features_fn = features_fn or extract_152_features
        inference_fn = inference_fn or (
            lambda feats: predict_image(scaler, clf, feats)  # noqa: E731
        )

    started = time.perf_counter()
    image = decode_fn(raw)
    after_decode = time.perf_counter()
    feats = features_fn(image)
    after_features = time.perf_counter()
    inference_fn(feats)
    after_inference = time.perf_counter()
    return {
        "decode_seconds": after_decode - started,
        "features_seconds": after_features - after_decode,
        "inference_seconds": after_inference - after_features,
        "total_seconds": after_inference - started,
    }


def summarize(values: Sequence[float]) -> Dict[str, float]:
    """Thống kê mô tả cho một dãy thời gian (giây).

    Raises:
        ValueError: Nếu dãy rỗng.
    """
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        raise ValueError("Khong co phep do nao de thong ke.")
    return {
        "n": int(array.size),
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p90": float(np.percentile(array, 90)),
        "p95": float(np.percentile(array, 95)),
        "min": float(np.min(array)),
        "max": float(np.max(array)),
    }


def _total_memory_gb() -> object:
    """Đọc tổng RAM; trả 'unknown' nếu không đọc được trên nền tảng này."""
    try:
        import ctypes

        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(MemoryStatusEx)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return round(status.ullTotalPhys / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    return round(int(line.split()[1]) / (1024 ** 2), 1)
    except Exception:
        pass
    return "unknown"


def _cpu_name() -> str:
    """Tên CPU; ưu tiên tên đầy đủ từ registry Windows, sau đó biến môi trường."""
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        ) as key:
            name = str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
            if name:
                return name
    except Exception:
        pass
    name = platform.processor() or ""
    if not name.strip():
        name = os.environ.get("PROCESSOR_IDENTIFIER", "")
    return name.strip() or "unknown"


def _version(dist: str) -> str:
    """Phiên bản gói phân phối; 'unknown' nếu không đọc được."""
    try:
        from importlib.metadata import version

        return version(dist)
    except Exception:
        return "unknown"


def collect_environment() -> Dict[str, object]:
    """Môi trường đo: hệ điều hành, CPU, RAM và phiên bản các thư viện dùng."""
    return {
        "os": platform.platform(),
        "cpu": _cpu_name(),
        "cores": os.cpu_count(),
        "ram_gb": _total_memory_gb(),
        "python": platform.python_version(),
        "numpy": _version("numpy"),
        "scikit_learn": _version("scikit-learn"),
        "scikit_image": _version("scikit-image"),
        "opencv": _version("opencv-python-headless"),
        "joblib": _version("joblib"),
        "pandas": _version("pandas"),
        "pyyaml": _version("pyyaml"),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_pipeline(artifact_path: Path) -> Tuple[object, object, Dict[str, object], float]:
    """Nạp artifact đóng băng; trả về (scaler, clf, meta, load_seconds).

    Import nằm trong hàm để bộ kiểm thử không phụ thuộc kho mô hình hay
    scikit-image ở thời điểm thu thập.
    """
    from src.model_artifact import load_model_artifact

    started = time.perf_counter()
    scaler, clf, meta = load_model_artifact(artifact_path, expected_sha256=None)
    load_seconds = time.perf_counter() - started
    return scaler, clf, meta, load_seconds


def _artifact_info(
    artifact_path: Path, meta: Mapping[str, object], load_seconds: float, clf: object
) -> Dict[str, object]:
    """Thông tin artifact ghi vào bản ghi, gồm bằng chứng đúng mô hình đã khóa."""
    path = Path(artifact_path)
    support = getattr(clf, "n_support_", None)
    n_support = int(sum(int(v) for v in support)) if support is not None else 0
    return {
        "path": path.as_posix(),
        "sha256": _sha256_file(path),
        "bytes": path.stat().st_size,
        "load_seconds": round(load_seconds, 6),
        "n_train": int(meta.get("n_train", -1)),
        "split_sha256": str(meta.get("split_sha256", "")),
        "sklearn_version": str(meta.get("sklearn_version", "")),
        "n_support_vectors": n_support,
        "classes": [int(c) for c in getattr(clf, "classes_", [])],
    }


def run_measurement(
    *,
    dataset_root: Path,
    artifact: Path,
    split_csv: Path,
    n: int,
    seed: int,
    repeats: int,
    warmup: int = 1,
    out_dir: Path,
) -> Dict[str, object]:
    """Chạy đo và ghi bản ghi; trả về nội dung bản ghi đã ghi.

    Lượt ngắn (ít ảnh) sau khi máy nghỉ đo được chế độ tương tác; lô dài đo
    chế độ chạy liên tục. Xem docstring module.

    Raises:
        ValueError: Nếu ``n`` vượt cỡ tập val (kiểm tra trước khi nạp mô hình).
    """
    if repeats < 1:
        raise ValueError(f"So luot do phai >= 1, nhan {repeats}.")
    sample = select_val_sample(split_csv, n=n, seed=seed)  # lỗi trước khi nạp mô hình

    scaler, clf, meta, load_seconds = load_pipeline(artifact)
    dataset_root = Path(dataset_root)

    rows: List[Dict[str, object]] = []
    wall_started = time.perf_counter()
    for repeat in range(repeats):
        for row in sample.itertuples(index=False):
            raw = (dataset_root / row.rel_image_path).read_bytes()
            measured = measure_image(raw, scaler, clf)
            entry: Dict[str, object] = {
                "image_id": row.image_id,
                "label": row.label,
                "repeat": repeat,
            }
            entry.update({key: round(measured[key], 6) for key in STAGE_KEYS})
            rows.append(entry)
    wall_seconds = time.perf_counter() - wall_started

    # Ảnh khởi động: đo riêng, không đưa vào thống kê.
    warmup_rows: List[Dict[str, object]] = []
    for row in sample.head(warmup).itertuples(index=False):
        raw = (dataset_root / row.rel_image_path).read_bytes()
        measured = measure_image(raw, scaler, clf)
        warmup_rows.append({"image_id": row.image_id, **{k: round(v, 6) for k, v in measured.items()}})

    frames = [pd.DataFrame(rows)]
    per_image = pd.concat(frames, ignore_index=True)
    medians: Dict[str, List[float]] = {key: [] for key in STAGE_KEYS}
    for image_id in sample["image_id"]:
        subset = per_image[per_image["image_id"] == image_id]
        for key in STAGE_KEYS:
            medians[key].append(float(subset[key].median()))
    stats = {
        "per_image_median_seconds": {key: summarize(medians[key]) for key in STAGE_KEYS}
    }

    record: Dict[str, object] = {
        "record": "demo_inference_latency",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": {
            "split": "val",
            "split_sha256": _sha256_file(split_csv),
            "n_images": int(len(sample)),
            "seed": int(seed),
            "repeats": int(repeats),
            "warmup_images": int(warmup),
            "timer": "time.perf_counter (wall)",
            "call_path": "cv2.imdecode -> extract_152_features -> predict_image",
            "decode_timed_on_bytes_in_memory": True,
            "percentile_method": "numpy.percentile (linear)",
            "stats_note": "thong ke tren trung vi tung anh qua cac luot do",
        },
        "environment": collect_environment(),
        "artifact": _artifact_info(artifact, meta, load_seconds, clf),
        "sample_class_distribution": {
            str(k): int(v) for k, v in sample["label"].value_counts().to_dict().items()
        },
        "warmup_seconds": warmup_rows,
        "stats": stats,
        "totals": {
            "measurements": int(len(per_image)),
            "wall_seconds": round(wall_seconds, 3),
        },
    }

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    per_image = per_image[list(PER_IMAGE_COLUMNS)]
    per_image.to_csv(out_dir / "per_image.csv", index=False, encoding="utf-8")
    (out_dir / "latency.json").write_text(
        json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    return record


def write_record(out_dir: Path, record: Mapping[str, object], rows: Sequence[Mapping[str, object]]) -> Path:
    """Ghi bản ghi JSON và CSV; trả về đường dẫn thư mục đầu ra."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    per_image = pd.DataFrame([dict(row) for row in rows])
    per_image = per_image[[str(c) for c in PER_IMAGE_COLUMNS]]
    with (out_dir / "per_image.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[str(c) for c in PER_IMAGE_COLUMNS])
        writer.writeheader()
        for row in per_image.to_dict("records"):
            writer.writerow(row)
    (out_dir / "latency.json").write_text(
        json.dumps(dict(record), indent=1, ensure_ascii=False), encoding="utf-8"
    )
    return out_dir


def build_parser() -> argparse.ArgumentParser:
    """Dựng bộ phân tích tham số dòng lệnh."""
    parser = argparse.ArgumentParser(description="Do do tre suy luan cua pipeline demo.")
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--split-csv", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Điểm vào CLI: chạy đo và in tóm tắt."""
    for stream in (__import__("sys").stdout, __import__("sys").stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    args = build_parser().parse_args(argv)
    record = run_measurement(
        dataset_root=args.dataset_root,
        artifact=args.artifact,
        split_csv=args.split_csv,
        n=args.n,
        seed=args.seed,
        repeats=args.repeats,
        warmup=args.warmup,
        out_dir=args.out_dir,
    )

    stats = record["stats"]["per_image_median_seconds"]  # type: ignore[index]
    artifact = record["artifact"]  # type: ignore[index]
    method = record["method"]  # type: ignore[index]
    print(f"Da ghi {args.out_dir / 'latency.json'}")
    print(
        f"Mau: {method['n_images']} anh val, seed {method['seed']}, "
        f"{method['repeats']} luot, {method['warmup_images']} anh khoi dong"
    )
    print(f"Nap artifact: {artifact['load_seconds'] * 1000:.0f} ms")
    for stage in STAGE_KEYS:
        value = stats[stage]
        print(
            f"{stage}: trung vi {value['median'] * 1000:.1f} ms | "
            f"p90 {value['p90'] * 1000:.1f} ms | p95 {value['p95'] * 1000:.1f} ms"
        )
    print(f"Moi truong: {record['environment']['cpu']} | Python {record['environment']['python']}")  # type: ignore[index]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
