"""Chặn lệch giữa phép đo tập validation có ảnh gần trùng và số ghi trong báo cáo.

Phép đo này lấp giới hạn 1 của Chương 6 (ảnh gần trùng xuyên hai tập). Test đọc
`results/val_near_duplicate_subset/val_near_duplicate_subset.json` rồi:
1. Đếm lại cặp gần trùng từ `splits/split_v1.csv` và đối chiếu với số đã công bố
   (735 cặp, 325/335/75, 70/665 theo Hamming 2/4, 229 cặp lệch nhãn, 273/243 ảnh).
2. Tính lại macro-F1 từ `results/rq2_ghep_svm_s42/preds_val.csv` trên toàn tập,
   trên 273 ảnh có ảnh gần trùng và trên phần còn lại.
3. Đối chiếu ba số trong báo cáo (Chương 2 mục 2.5, Chương 6 giới hạn 1).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPLIT_CSV = REPO_ROOT / "splits/split_v1.csv"
PREDS_VAL = REPO_ROOT / "results/rq2_ghep_svm_s42/preds_val.csv"
RECORD = REPO_ROOT / "results/val_near_duplicate_subset/val_near_duplicate_subset.json"
CLASSES = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]


def _hamming_pairs() -> set[str]:
    """Tập hợp image_id validation có ít nhất một ảnh gần trùng ở tập khác."""
    df = pd.read_csv(SPLIT_CSV, dtype={"phash": str})
    df["h"] = df["phash"].apply(lambda x: int(x, 16)).astype(np.uint64)
    by_split = {s: g.reset_index(drop=True) for s, g in df.groupby("split")}
    hit_val: set[str] = set()
    for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
        g1, g2 = by_split[a], by_split[b]
        d = np.empty((len(g1), len(g2)), dtype=np.uint8)
        for start in range(0, len(g1), 512):
            stop = min(start + 512, len(g1))
            d[start:stop] = np.bitwise_count(g1["h"].to_numpy()[start:stop, None] ^ g2["h"].to_numpy()[None, :])
        mask = (d == 2) | (d == 4)
        i1, i2 = np.nonzero(mask)
        ids1 = set(g1["image_id"].to_numpy()[i1])
        ids2 = set(g2["image_id"].to_numpy()[i2])
        if a == "val":
            hit_val |= ids1
        if b == "val":
            hit_val |= ids2
    return hit_val


def _macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    f1s = []
    for c in range(4):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        denom = 2 * tp + fp + fn
        f1s.append(2 * tp / denom if denom else 0.0)
    return float(np.mean(f1s))


def test_record_matches_recomputation() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    hit_val = _hamming_pairs()
    assert record["n_val_subset"] == len(hit_val) == 273
    assert record["counts"]["pairs_total"] == 735
    assert record["counts"]["pairs_train_val"] == 335
    assert record["counts"]["val_images"] == 273

    preds = pd.read_csv(PREDS_VAL)
    subset = preds["image_id"].isin(hit_val).to_numpy()
    f1_full = round(_macro_f1(preds["y_true"].to_numpy(), preds["y_pred"].to_numpy()), 4)
    f1_sub = round(_macro_f1(preds["y_true"].to_numpy()[subset], preds["y_pred"].to_numpy()[subset]), 4)
    f1_rest = round(_macro_f1(preds["y_true"].to_numpy()[~subset], preds["y_pred"].to_numpy()[~subset]), 4)
    assert record["macro_f1_full"] == f1_full == 0.9024
    assert record["macro_f1_subset"] == f1_sub == 0.9068
    assert record["macro_f1_complement"] == f1_rest == 0.9017
    assert sum(record["subset_per_class"].values()) == 273


def test_report_numbers_match_record() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    ch2 = (REPO_ROOT / "report/02_du_lieu_va_phuong_phap.md").read_text(encoding="utf-8")
    ch6 = (REPO_ROOT / "report/06_thao_luan_gioi_han_huong_phat_trien.md").read_text(encoding="utf-8")
    sub = f"{record['macro_f1_subset']:.4f}".replace(".", ",")
    rest = f"{record['macro_f1_complement']:.4f}".replace(".", ",")
    full = f"{record['macro_f1_full']:.4f}".replace(".", ",")
    assert sub in ch2 and rest in ch2 and full in ch2
    assert sub in ch6 and rest in ch6
    assert "273 trong 3.174 ảnh validation (8,6%)" in ch2


def test_no_test_data_used() -> None:
    preds = pd.read_csv(PREDS_VAL)
    assert len(preds) == 3174  # toàn bộ tập validation, không ảnh test


def _load_script():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "val_near_duplicate_subset", REPO_ROOT / "scripts/val_near_duplicate_subset.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bootstrap_ci_reproducible() -> None:
    """Khoang tin cay bootstrap trong JSON phai tai lap duoc dung ham cua script."""
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    ci = record["bootstrap_ci"]
    assert ci["n_boot"] == 2000 and ci["seed"] == 42
    mod = _load_script()
    preds = pd.read_csv(PREDS_VAL)
    hit_val = _hamming_pairs()
    subset = preds["image_id"].isin(hit_val).to_numpy()
    y_true = preds["y_true"].to_numpy()
    y_pred = preds["y_pred"].to_numpy()
    out = mod.bootstrap_ci_diff(y_true, y_pred, subset)
    assert round(out["lo"], 4) == ci["lo"], f"{out['lo']} != {ci['lo']}"
    assert round(out["hi"], 4) == ci["hi"], f"{out['hi']} != {ci['hi']}"
    assert out["contains_zero"] == ci["contains_zero"]
