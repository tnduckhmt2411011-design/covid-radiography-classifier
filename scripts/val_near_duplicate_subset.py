"""Tai lap phep dem cap gan trung va do macro-F1 tren tap con validation bi anh huong.

Muc dich: so 273 anh validation co it nhat mot anh gan trung (Hamming 2 hoac 4) o
tap khac da ghi trong ghi chu ky thuat Chuong 2, nhung chua co phep do nao cho
biet tren tap con do mo hinh dat bao nhieu. Script nay:

1. Doc cot `phash`, `split`, `label` tu `splits/split_v1.csv`.
2. Dem lai cap gan trung giua cac tap (D thuoc {2, 4}) va doi chieu voi so da
   cong bo: 735 cap, 325 Train-Test, 335 Train-Val, 75 Val-Test, 229 cap lech
   nhan, 273 anh validation va 243 anh test co anh gan trung o tap khac.
3. Tinh macro-F1 cua SVM RBF tren tap con 273 anh validation (tu
   `results/rq2_ghep_svm_s42/preds_val.csv`) va tren phan con lai, doi chieu
   voi 0,9024 tren toan bo 3.174 anh.
4. Ghi ket qua ra `results/val_near_duplicate_subset/`.

Chay: python scripts/val_near_duplicate_subset.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SPLIT_CSV = REPO_ROOT / "splits/split_v1.csv"
PREDS_VAL = REPO_ROOT / "results/rq2_ghep_svm_s42/preds_val.csv"
OUT_DIR = REPO_ROOT / "results/val_near_duplicate_subset"
OUT_JSON = OUT_DIR / "val_near_duplicate_subset.json"
OUT_MD = OUT_DIR / "val_near_duplicate_subset.md"

CLASSES = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
EXPECTED = {
    "pairs_total": 735, "pairs_train_test": 325, "pairs_train_val": 335, "pairs_val_test": 75,
    "pairs_d2": 70, "pairs_d4": 665, "pairs_cross_label": 229,
    "val_images": 273, "test_images": 243,
}


def reconfigure() -> None:
    for stream in (sys.stdout, sys.stderr):
        fn = getattr(stream, "reconfigure", None)
        if fn:
            fn(encoding="utf-8", errors="replace")


def hamming_matrix(hashes_a: np.ndarray, hashes_b: np.ndarray, chunk: int = 512) -> np.ndarray:
    """Khoang cach Hamming giua hai tap hash 64 bit, theo khoi de gioi han bo nho."""
    dists = np.empty((len(hashes_a), len(hashes_b)), dtype=np.uint8)
    for start in range(0, len(hashes_a), chunk):
        stop = min(start + chunk, len(hashes_a))
        xor = hashes_a[start:stop, None] ^ hashes_b[None, :]
        dists[start:stop] = np.bitwise_count(xor)
    return dists


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int = 4) -> float:
    f1s = []
    for c in range(n_classes):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        denom = 2 * tp + fp + fn
        f1s.append(2 * tp / denom if denom else 0.0)
    return float(np.mean(f1s))


def per_class_recall(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Recall tung lop: tp / (tp + fn); lop khong co mau nao tra 0."""
    out: dict[str, float] = {}
    for c, name in enumerate(CLASSES):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        out[name] = round(tp / (tp + fn), 4) if (tp + fn) else 0.0
    return out


def bootstrap_ci_diff(
    y_true: np.ndarray, y_pred: np.ndarray, subset_mask: np.ndarray,
    n_boot: int = 2000, seed: int = 42,
) -> dict:
    """Khoang tin cay 95% cho hieu macro-F1 (tap con tru phan con lai).

    Lay mau lai doc lap trong tung tap con (giu nguyen so anh cua tung tap con),
    seed 42 cung voi bootstrap ghep cap cua RQ2. Khong huan luyen lai; day la
    do thi bien tren du doan co san nen khoang tin cay mang tinh xap xi.
    """
    rng = np.random.default_rng(seed)
    idx_sub = np.flatnonzero(subset_mask)
    idx_rest = np.flatnonzero(~subset_mask)
    diffs = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        s = rng.choice(idx_sub, size=idx_sub.size, replace=True)
        r = rng.choice(idx_rest, size=idx_rest.size, replace=True)
        diffs[i] = macro_f1(y_true[s], y_pred[s]) - macro_f1(y_true[r], y_pred[r])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {
        "n_boot": n_boot,
        "seed": seed,
        "lo": round(float(lo), 4),
        "hi": round(float(hi), 4),
        "contains_zero": bool(lo <= 0.0 <= hi),
        "method": "percentile bootstrap, independent resampling within each subset",
    }


def main() -> int:
    reconfigure()
    df = pd.read_csv(SPLIT_CSV, dtype={"phash": str})
    df["phash_int"] = df["phash"].apply(lambda h: int(h, 16)).astype(np.uint64)
    by_split = {s: g.reset_index(drop=True) for s, g in df.groupby("split")}
    counts = {"train_val": 0, "train_test": 0, "val_test": 0}
    pair_split_total = {"train-test": 0, "train-val": 0, "val-test": 0}
    d2 = d4 = cross_label = 0
    hit_val = set()   # image_id validation co anh gan trung o tap khac
    hit_test = set()
    for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
        key = f"{a}-{b}"
        g1, g2 = by_split[a], by_split[b]
        d = hamming_matrix(g1["phash_int"].to_numpy(), g2["phash_int"].to_numpy())
        mask = (d == 2) | (d == 4)
        idx1, idx2 = np.nonzero(mask)
        pair_split_total[key] = int(mask.sum())
        d2 += int((d[idx1, idx2] == 2).sum())
        d4 += int((d[idx1, idx2] == 4).sum())
        labels1 = g1["label"].to_numpy()[idx1]
        labels2 = g2["label"].to_numpy()[idx2]
        cross_label += int((labels1 != labels2).sum())
        ids1 = set(g1["image_id"].to_numpy()[idx1])
        ids2 = set(g2["image_id"].to_numpy()[idx2])
        if "val" in key:
            hit_val |= ids1 if a == "val" else ids2
        if "test" in key:
            hit_test |= ids1 if a == "test" else ids2

    got = {
        "pairs_total": sum(pair_split_total.values()), "pairs_train_test": pair_split_total["train-test"],
        "pairs_train_val": pair_split_total["train-val"], "pairs_val_test": pair_split_total["val-test"],
        "pairs_d2": d2, "pairs_d4": d4, "pairs_cross_label": cross_label,
        "val_images": len(hit_val), "test_images": len(hit_test),
    }
    for k, v in EXPECTED.items():
        if got[k] != v:
            print(f"CANH BAO: {k} tinh duoc {got[k]}, so da cong bo {v}")

    # --- macro-F1 tren tap con ---
    preds = pd.read_csv(PREDS_VAL)
    val_with_pair = preds["image_id"].isin(hit_val)
    y_true, y_pred = preds["y_true"].to_numpy(), preds["y_pred"].to_numpy()
    f1_all = macro_f1(y_true, y_pred)
    f1_sub = macro_f1(y_true[val_with_pair.to_numpy()], y_pred[val_with_pair.to_numpy()])
    f1_rest = macro_f1(y_true[~val_with_pair.to_numpy()], y_pred[~val_with_pair.to_numpy()])
    n_sub, n_rest = int(val_with_pair.sum()), int((~val_with_pair).sum())
    per_class_sub = {}
    for c, name in enumerate(CLASSES):
        m = val_with_pair & (preds["y_true"] == c)
        per_class_sub[name] = int(m.sum())

    result = {
        "method": "Hamming distance between cross-split pHash values (64-bit, distance 2 or 4); "
                  "distinct validation images involved in at least one such pair",
        "counts": got,
        "preds_source": "results/rq2_ghep_svm_s42/preds_val.csv",
        "n_val_total": int(len(preds)),
        "n_val_subset": n_sub,
        "n_val_complement": n_rest,
        "macro_f1_full": round(f1_all, 4),
        "macro_f1_subset": round(f1_sub, 4),
        "macro_f1_complement": round(f1_rest, 4),
        "subset_share_percent": round(100 * n_sub / len(preds), 2),
        "subset_per_class": per_class_sub,
        "bootstrap_ci": bootstrap_ci_diff(y_true, y_pred, val_with_pair.to_numpy()),
        "recall_subset": per_class_recall(y_true[val_with_pair.to_numpy()], y_pred[val_with_pair.to_numpy()]),
        "recall_complement": per_class_recall(y_true[~val_with_pair.to_numpy()], y_pred[~val_with_pair.to_numpy()]),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "# Phep do tren tap validation co anh gan trung o tap khac\n\n"
        "| Hang muc | Gia tri |\n| :--- | ---: |\n"
        f"| So anh validation co anh gan trung (train hoac test) | {n_sub} |\n"
        f"| Ty le trong 3.174 anh validation | {result['subset_share_percent']}% |\n"
        f"| Macro-F1 toan bo validation | {round(f1_all, 4):.4f} |\n"
        f"| Macro-F1 tren {n_sub} anh co anh gan trung | {round(f1_sub, 4):.4f} |\n"
        f"| Macro-F1 tren {n_rest} anh con lai | {round(f1_rest, 4):.4f} |\n"
        f"| Khoang tin cay 95% cho hieu macro-F1 (tap con tru phan con lai) | "
        f"[{result['bootstrap_ci']['lo']:.4f}; {result['bootstrap_ci']['hi']:.4f}] |\n"
        f"| Bootstrap (n_boot / seed) | {result['bootstrap_ci']['n_boot']} / {result['bootstrap_ci']['seed']} |\n"
        f"| Recall tung lop tren tap con | {result['recall_subset']} |\n"
        f"| Recall tung lop tren phan con lai | {result['recall_complement']} |\n\n"
        "Dem lai tu `splits/split_v1.csv` (cot `phash`), khoang cach Hamming 2 hoac 4 giua cac tap; "
        "ket qua khop so da cong bo: 735 cap, 325/335/75 theo cap tap, 229 cap lech nhan, "
        "273 anh validation va 243 anh test. Khoang tin cay lay mau lai doc lap trong tung tap con "
        "(2000 lan, seed 42), chi dung du doan co san, khong huan luyen lai.\n",
        encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
