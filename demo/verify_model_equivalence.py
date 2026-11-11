"""Cổng tương đương mô hình cho demo S6-02.

Chạy mô hình đóng băng trên một mẫu ảnh thuộc split 'val' và so nhãn với
``results/rq3_ghep_svm_orig_to_orig_s42/preds_val.csv``. Cổng này KHÔNG đọc ảnh test.

Ví dụ:
    python demo/verify_model_equivalence.py --dataset-root D:/cxr_data/COVID-19_Radiography_Dataset
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.inference_demo import extract_152_features, predict_image  # noqa: E402
from src.model_artifact import (  # noqa: E402
    DEFAULT_MODEL_FILE,
    DEFAULT_MODEL_SHA256,
    ModelArtifactError,
    load_model_artifact,
)

DEFAULT_SPLIT = REPO_ROOT / "splits" / "split_v1.csv"
DEFAULT_PREDS = REPO_ROOT / "results" / "rq3_ghep_svm_orig_to_orig_s42" / "preds_val.csv"
DEFAULT_ARTIFACT = REPO_ROOT / "outputs" / "k_v3_out" / DEFAULT_MODEL_FILE


def _force_utf8_output() -> None:
    """Bảo đảm console Windows không làm hỏng tiếng Việt khi in kết quả."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--split-csv", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--preds", type=Path, default=DEFAULT_PREDS)
    parser.add_argument("--expected-sha256", default=DEFAULT_MODEL_SHA256)
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args(argv)


def run_gate(
    *,
    dataset_root: Path,
    artifact: Path,
    split_csv: Path,
    preds: Path,
    expected_sha256: str,
    n: int,
    seed: int,
) -> int:
    """Chạy cổng và trả mã thoát 0 nếu mọi nhãn khớp, 1 nếu có sai lệch."""
    split = pd.read_csv(split_csv)
    val = split[split["split"] == "val"]
    if n > len(val):
        raise SystemExit(f"Số ảnh yêu cầu {n} vượt số dòng val {len(val)}.")
    sample = val.sample(n=n, random_state=seed, replace=False).reset_index(drop=True)
    print(f"val rows={len(val)} sample={len(sample)} classes={sample['label'].value_counts().to_dict()}")

    hash_ok = 0
    for row in sample.itertuples(index=False):
        path = dataset_root / row.rel_image_path
        if not path.is_file():
            raise SystemExit(f"Thiếu ảnh val: {path}")
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        if digest != row.file_hash:
            raise SystemExit(f"Băm tệp không khớp manifest: {path}")
        hash_ok += 1
    print(f"file_hash MD5 khớp: {hash_ok}/{len(sample)}")

    scaler, clf, meta = load_model_artifact(artifact, expected_sha256=expected_sha256)
    print(
        "artifact: "
        f"sklearn={meta['sklearn_version']} n_train={meta['n_train']} "
        f"split={str(meta['split_sha256'])[:12]}"
    )

    started = time.perf_counter()
    predicted = []
    for row in sample.itertuples(index=False):
        raw = np.fromfile(str(dataset_root / row.rel_image_path), dtype=np.uint8)
        image = cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise SystemExit(f"Không giải mã được ảnh val: {row.rel_image_path}")
        result = predict_image(scaler, clf, extract_152_features(image))
        predicted.append((row.image_id, int(result["label_idx"])))
    elapsed = time.perf_counter() - started

    gate = pd.DataFrame(predicted, columns=["image_id", "y_pred_gate"])
    reference = pd.read_csv(preds, usecols=["image_id", "y_true", "y_pred"])
    merged = gate.merge(reference, on="image_id", how="left", validate="one_to_one")
    if merged["y_pred"].isna().any():
        raise SystemExit("Thiếu nhãn tham chiếu cho một số image_id của mẫu val.")
    matches = int((merged["y_pred_gate"] == merged["y_pred"]).sum())
    print(f"dự đoán {len(merged)} ảnh trong {elapsed:.1f}s ({elapsed / len(merged):.3f}s/ảnh)")
    print(f"NHÃN KHỚP: {matches}/{len(merged)}")
    if matches != len(merged):
        mismatched = merged[merged["y_pred_gate"] != merged["y_pred"]]
        print(mismatched.head(20).to_string(index=False))
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    _force_utf8_output()
    args = _parse_args(argv)
    try:
        return run_gate(
            dataset_root=args.dataset_root,
            artifact=args.artifact,
            split_csv=args.split_csv,
            preds=args.preds,
            expected_sha256=args.expected_sha256,
            n=args.n,
            seed=args.seed,
        )
    except ModelArtifactError as exc:
        print(f"LỖI ARTIFACT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
