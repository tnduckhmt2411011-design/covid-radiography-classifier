"""Nguồn số duy nhất cho bộ slide bảo vệ cuối kỳ (S6-03).

Mọi con số hiển thị trên slide đi qua tệp này. Không hàm nào nhận tham số số:
giá trị đọc trực tiếp từ ``results/``, ``splits/`` và ``outputs/`` tại thời điểm
dựng, nên khi nguồn đổi thì slide đổi theo.

Định dạng theo tiếng Việt: dấu phẩy thập phân, dấu chấm phân cách hàng nghìn.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "results"
SPLITS = REPO / "splits"
OUTPUTS = REPO / "outputs"

CLASSES = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
CLASS_VI = {
    "COVID": "COVID-19",
    "Lung_Opacity": "Lung Opacity",
    "Normal": "Normal",
    "Viral Pneumonia": "Viral Pneumonia",
}


# ---------------------------------------------------------------- định dạng
def fmt(value: float, digits: int = 4) -> str:
    """Số thập phân kiểu Việt Nam: 0,8714; số âm dùng dấu trừ U+2212."""
    sign = "\u2212" if value < 0 else ""
    text = f"{abs(value):,.{digits}f}"
    return sign + text.replace(",", "\u00a0").replace(".", ",").replace("\u00a0", ".")


def fmt_int(value: float) -> str:
    """Số nguyên có phân cách hàng nghìn: 3.176."""
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_pct(value: float, digits: int = 2) -> str:
    """Tỉ lệ 0..1 thành phần trăm: 86,56%."""
    return f"{fmt(value * 100, digits)}%"


def fmt_delta(value: float, digits: int = 4) -> str:
    """Chênh lệch luôn kèm dấu: +0,0103 hoặc −0,0535."""
    sign = "+" if value >= 0 else "\u2212"
    return sign + fmt(abs(value), digits)


def fmt_ci(low: float, high: float, digits: int = 4) -> str:
    """Khoảng tin cậy: [0,8579; 0,8840]."""
    return f"[{fmt(low, digits)}; {fmt(high, digits)}]"


def fmt_seconds(value: float, digits: int = 4) -> str:
    """Thời lượng giây: 0,1192 s."""
    return f"{fmt(value, digits)} s"


def fmt_bytes(value: int) -> str:
    """Dung lượng tệp: 7,84 MB."""
    return f"{fmt(value / 1_000_000, 2)} MB"


# ---------------------------------------------------------------- nạp nguồn
def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_split() -> dict:
    """Cỡ tập và phân bố nhãn từ ``splits/split_v1.csv``."""
    frame = pd.read_csv(SPLITS / "split_v1.csv")
    per_class = frame["label"].value_counts()
    per_split = frame["split"].value_counts()
    groups = frame.groupby("group_id").size()
    return {
        "total": int(len(frame)),
        "per_split": {k: int(v) for k, v in per_split.items()},
        "per_class": {k: int(per_class[k]) for k in CLASSES},
        "ratio": float(per_class.max() / per_class.min()),
        "n_groups": int(len(groups)),
        "n_multi_groups": int((groups > 1).sum()),
        "n_multi_images": int(groups[groups > 1].sum()),
        "sha256": str(
            __import__("hashlib").sha256((SPLITS / "split_v1.csv").read_bytes()).hexdigest()
        ),
    }


def load_pairs() -> dict:
    """Cặp gần trùng giữa các split từ ``outputs/split_check``."""
    report = _json(OUTPUTS / "split_check" / "cross_split_hamming_report.json")
    relation = report["class_relation"]
    return {
        "total": int(report["cross_split_pairs_count"]),
        "by_split": report["split_pairs_distribution"],
        "by_distance": report["dist_distribution"],
        "same_label": int(relation.get("Same_d4", 0) + relation.get("Same_d2", 0)),
        "cross_label": int(relation.get("Cross-Class_d4", 0) + relation.get("Cross-Class_d2", 0)),
    }


def load_baselines() -> dict:
    """Hai mốc nền B0 và A0 trên tập validation."""
    b0 = _json(RESULTS / "b0_majority" / "metrics.json")
    a0 = _json(RESULTS / "a0_shortcut" / "metrics.json")
    a0_models = {
        key: float(payload["macro_f1"])
        for key, payload in a0.items()
        if isinstance(payload, dict) and "macro_f1" in payload
    }
    best_key = max(a0_models, key=a0_models.get)
    return {
        "b0": float(b0["macro_f1"]),
        "a0": a0_models[best_key],
        "a0_model": best_key,
        "a0_all": a0_models,
    }


def load_rules() -> dict:
    """Ng\u01b0\u1ee1ng v\u00e0 quy \u01b0\u1edbc \u0111\u00e3 ch\u1ed1t, \u0111\u1ecdc t\u1eeb
    ``results/threshold_v3.md``.

    Ng\u01b0\u1ee1ng 0,005 l\u00e0 quy \u01b0\u1edbc c\u1ee7a nh\u00f3m, kh\u00f4ng c\u00f3 c\u0103n c\u1ee9 d\u1eef
    li\u1ec7u; \u0111i\u1ec1u ki\u1ec7n \u0111i k\u00e8m l\u00e0 kho\u1ea3ng tin c\u1eady 95% c\u1ee7a hi\u1ec7u s\u1ed1
    kh\u00f4ng ch\u1ee9a 0.
    """
    text = (RESULTS / "threshold_v3.md").read_text(encoding="utf-8")
    threshold = re.search(r">=\s*(\d,\d+)", text)
    boot = re.search(r"(\d\.\d+)\s*l\u1ea7n", text)
    folds = re.search(r"cross-validation (\d+) fold", text)
    return {
        "delta_threshold": float(threshold.group(1).replace(",", ".")),
        "bootstrap": int(boot.group(1).replace(".", "")),
        "cv_folds": int(folds.group(1)),
    }


def load_rq1() -> list[dict]:
    """Bốn nhóm đặc trưng với CI và chênh lệch so với histogram."""
    summary = pd.read_csv(RESULTS / "report_rq1" / "r1_summary.csv")
    deltas = pd.read_csv(RESULTS / "report_rq1" / "r1_bootstrap_vs_reference.csv")
    delta_by_candidate = {
        row.candidate: {
            "diff": float(row.point_diff),
            "ci": (float(row.ci_low), float(row.ci_high)),
            "contains_zero": bool(row.contains_zero),
        }
        for row in deltas.itertuples()
    }
    rows = []
    for row in summary.itertuples():
        rows.append(
            {
                "key": row.features,
                "macro_f1": float(row.macro_f1_mean),
                "std": float(row.macro_f1_std),
                "ci": (float(row.ci95_low), float(row.ci95_high)),
                "n_seeds": int(row.n_seeds),
                "delta": delta_by_candidate.get(row.features),
            }
        )
    return rows


def load_rq1_cost() -> dict:
    """Chi phí CPU mỗi ảnh, đọc từ biên bản ``rq1_cost_rank_record.md``."""
    text = (RESULTS / "rq1_cost_rank_record.md").read_text(encoding="utf-8")
    values = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] in {"Nhóm", "---"} or not cells[3].replace(",", "").replace(".", "").isdigit():
            continue
        values[cells[0]] = {
            "train": float(cells[1].replace(".", "").replace(",", ".")),
            "val": float(cells[2].replace(".", "").replace(",", ".")),
            "per_image": float(cells[3].replace(".", "").replace(",", ".")),
        }
    return {
        "by_group": values,
        "ratio": values["ghep"]["per_image"] / values["hist"]["per_image"],
    }


def load_rq2() -> list[dict]:
    """Sáu bộ phân loại trên nhóm đặc trưng ghép."""
    summary = pd.read_csv(RESULTS / "report_rq2" / "r1_summary.csv")
    rows = []
    for row in summary.itertuples():
        rows.append(
            {
                "key": row.classifier,
                "macro_f1": float(row.macro_f1_mean),
                "std": float(row.macro_f1_std),
                "ci": (float(row.ci95_low), float(row.ci95_high)),
                "n_seeds": int(row.n_seeds),
            }
        )
    rows.sort(key=lambda item: item["macro_f1"], reverse=True)
    deltas = pd.read_csv(RESULTS / "report_rq2" / "r1_bootstrap_vs_reference.csv") if (
        RESULTS / "report_rq2" / "r1_bootstrap_vs_reference.csv"
    ).exists() else None
    if deltas is not None:
        for item in rows:
            match = deltas[deltas["candidate"] == item["key"]]
            if len(match):
                row = match.iloc[0]
                item["delta"] = {
                    "diff": float(row["point_diff"]),
                    "ci": (float(row["ci_low"]), float(row["ci_high"])),
                    "contains_zero": bool(row["contains_zero"]),
                    "reference": str(row["reference"]),
                }
    return rows


def load_rq3() -> dict:
    """Năm kịch bản che/cắt vùng phổi và các phép so sánh bootstrap."""
    summary = pd.read_csv(RESULTS / "report_rq3" / "r1_summary.csv")
    scenarios = {}
    for row in summary.to_dict("records"):
        scenarios[row["scenario"]] = {
            "macro_f1": float(row["macro_f1"]),
            "ci": (float(row["ci95_low"]), float(row["ci95_high"])),
            "per_class": {
                label: {
                    "precision": float(row[f"precision_{label}"]),
                    "recall": float(row[f"recall_{label}"]),
                    "f1": float(row[f"f1_{label}"]),
                }
                for label in CLASSES
            },
        }
    bootstrap = pd.read_csv(RESULTS / "report_rq3" / "r3_shortcut_bootstrap.csv")
    diffs = {}
    for row in bootstrap.itertuples():
        diffs[(row.scenario_a, row.scenario_b)] = {
            "diff": float(row.point_diff),
            "ci": (float(row.ci_low), float(row.ci_high)),
            "contains_zero": bool(row.contains_zero),
        }
    return {"scenarios": scenarios, "diffs": diffs}


def load_permutation() -> dict:
    """Permutation importance 10 khối, ba chế độ mask."""
    frame = pd.read_csv(RESULTS / "rq3_permutation_importance.csv")
    out = {}
    for mode, block in frame.groupby("mask_mode"):
        out[mode] = [
            {
                "block": row.block_name,
                "dims": int(row.n_dims),
                "importance": float(row.importance_mean),
                "std": float(row.importance_std),
                "baseline": float(row.baseline_score),
            }
            for row in block.itertuples()
        ]
    return out


def load_test() -> dict:
    """Kết quả cuối trên tập test và ma trận nhầm lẫn."""
    metrics = _json(RESULTS / "final_test" / "metrics.json")
    matrix = metrics["confusion_matrix"]
    errors = int(sum(sum(row) for row in matrix) - sum(matrix[i][i] for i in range(4)))
    correct = int(sum(matrix[i][i] for i in range(4)))
    support = {label: int(metrics["per_class"][label]["support"]) for label in CLASSES}
    return {
        "macro_f1": float(metrics["macro_f1"]),
        "accuracy": float(metrics["accuracy"]),
        "balanced_accuracy": float(metrics["balanced_accuracy"]),
        "macro_precision": float(metrics["macro_precision"]),
        "macro_recall": float(metrics["macro_recall"]),
        "matrix": matrix,
        "n": int(sum(support.values())),
        "errors": errors,
        "correct": correct,
        "per_class": {
            label: {
                "precision": float(metrics["per_class"][label]["precision"]),
                "recall": float(metrics["per_class"][label]["recall"]),
                "f1": float(metrics["per_class"][label]["f1"]),
                "support": support[label],
            }
            for label in CLASSES
        },
    }


def load_test_interval() -> dict:
    """Khoảng tin cậy bootstrap của macro-F1 test, đọc từ báo cáo cuối."""
    path = RESULTS / "final_test" / "final_test_report.json"
    if not path.exists():
        return {}
    report = _json(path)
    if {"ci95_low", "ci95_high"} <= set(report):
        return {"ci": (float(report["ci95_low"]), float(report["ci95_high"]))}
    for key in ("ci95", "bootstrap_ci", "macro_f1_ci95"):
        value = report.get(key)
        if isinstance(value, dict) and {"low", "high"} <= set(value):
            return {"ci": (float(value["low"]), float(value["high"]))}
        if isinstance(value, list) and len(value) == 2:
            return {"ci": (float(value[0]), float(value[1]))}
    return {}


def load_val_errors() -> dict:
    """349 lỗi validation: cặp nhầm lẫn và cờ đồng thuận."""
    frame = pd.read_csv(RESULTS / "error_analysis" / "val_misclassified_cases.csv")
    errors = frame[frame["is_error"].astype(bool)] if "is_error" in frame else frame
    pairs = pd.read_csv(RESULTS / "error_analysis" / "confusion_pairs_summary.csv")
    normal_lung = 0
    for row in pairs.itertuples():
        if {row.true_label, row.pred_label} == {"Normal", "Lung_Opacity"}:
            normal_lung += int(row.count)
    consensus = int(errors["consensus_hard_error"].astype(bool).sum()) if "consensus_hard_error" in errors else 0
    high_conf = int((errors["proba_pred"] >= 0.80).sum()) if "proba_pred" in errors else 0
    return {
        "n": int(len(errors)),
        "normal_lung_opacity": normal_lung,
        "consensus": consensus,
        "high_confidence": high_conf,
        "high_confidence_pct": float((errors["proba_pred"] >= 0.80).mean()) if "proba_pred" in errors else 0.0,
    }


def load_latency() -> dict:
    """Độ trễ suy luận đo trên 200 ảnh validation, 3 lượt."""
    data = _json(RESULTS / "demo_latency_sustained" / "latency.json")
    stages = {}
    for key, payload in data.get("stats", {}).get("per_image_median_seconds", {}).items():
        if isinstance(payload, dict) and "median" in payload:
            stages[key.replace("_seconds", "")] = float(payload["median"])
    artifact = data["artifact"]
    return {
        "stages": stages,
        "n_images": int(data["method"]["n_images"]),
        "repeats": int(data["method"]["repeats"]),
        "artifact_bytes": int(artifact["bytes"]),
        "artifact_sha256": str(artifact["sha256"]),
        "n_support_vectors": int(artifact.get("n_support_vectors", 0)),
        "n_train": int(artifact.get("n_train", 0)),
        "cpu": data["environment"]["cpu"],
        "cpu_short": re.search(r"(i\d-\w+)", data["environment"]["cpu"]).group(1),
        "cores": int(data["environment"]["cores"]),
        "python": data["environment"]["python"],
    }


def load_brightness() -> list[dict]:
    """Phân bố độ sáng trung bình theo lớp và AUC phân biệt."""
    frame = pd.read_csv(RESULTS / "eda" / "brightness_by_class.csv")
    return [
        {
            "label": row.label,
            "n": int(row.n),
            "mean": float(row.mean),
            "sd": float(row.sd),
            "q1": float(row.q1),
            "q3": float(row.q3),
            "auc_vs_rest": float(row.auc_vs_rest),
        }
        for row in frame.itertuples()
    ]


def load_unlock() -> dict:
    """Biên bản mở khóa tập test."""
    data = _json(RESULTS / "final_test" / "UNLOCK_RECORD.json")
    return {
        "utc": str(data["utc_time"]),
        "commit": str(data["commit"])[:7],
        "split_sha256": str(data["split_sha256"])[:12],
        "val_macro_f1": float(data["val_macro_f1"]),
    }


def load_sources() -> dict:
    """Nguồn ảnh của từng lớp, từ ``results/eda/normal_source_labels.csv`` và ``splits``.

    Phân chia theo ``docs/dataset_provenance.md`` mục 2.1: ``18.479`` ảnh thuộc bộ
    ``COVQU`` do Rahman và cộng sự (2021) phát hành — ``3.616`` COVID + ``6.012``
    Lung Opacity + ``8.851`` Normal RSNA; ``2.686`` ảnh còn lại đến từ bộ Kaggle
    Chest X-Ray Images (Pneumonia) của Mooney — ``1.345`` Viral Pneumonia +
    ``1.341`` Normal. Lớp COVID ghép từ nhiều kho ảnh riêng lẻ, nên cùng nhãn
    COVID không đồng nghĩa cùng một nguồn chụp.
    """
    frame = pd.read_csv(RESULTS / "eda" / "normal_source_labels.csv")
    per_source = frame["source"].value_counts().to_dict()
    split = load_split()
    per_class = split["per_class"]
    rsna = int(per_source.get("rsna", 0))
    mooney = int(per_source.get("mooney", 0))
    covqu = per_class["COVID"] + per_class["Lung_Opacity"] + rsna
    return {
        "covqu": int(covqu),
        "mooney_total": mooney + per_class["Viral Pneumonia"],
        "normal_rsna": rsna,
        "normal_mooney": mooney,
        "viral": per_class["Viral Pneumonia"],
        "covid": per_class["COVID"],
        "lung_opacity": per_class["Lung_Opacity"],
        "total": split["total"],
    }


def load_svm_cv() -> dict:
    """Siêu tham số SVM: lưới ứng viên và bộ được chọn, đọc từ ``config.yaml``.

    SVM là bộ tất định nên chỉ chạy một lần, nhưng siêu tham số vẫn chọn bằng
    cross-validation trên train: lưới có bốn ứng viên và 5-fold
    ``StratifiedGroupKFold`` chia nhóm theo ``group_id``.
    """
    text = (RESULTS / "rq2_ghep_svm_s42" / "config.yaml").read_text(encoding="utf-8")
    block = text.split("param_grid:", 1)[1].split("selected_params:", 1)[0]
    candidates = [line for line in block.splitlines() if line.strip().startswith("- C:")]
    selected = text.split("selected_params:", 1)[1]
    values = {}
    for line in selected.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("cv_", "hyperparameters:", "selected_index")):
            break
        key, _, value = line.partition(":")
        values[key.strip()] = value.strip()
    folds = ""
    for line in text.splitlines():
        if "n_splits:" in line:
            folds = line.split(":", 1)[1].strip()
    return {
        "n_candidates": len(candidates),
        "n_splits": folds,
        "selected": values,
    }


def load_duplicates() -> dict:
    """Nhóm trùng pHash tuyệt đối và gần trùng, từ ``outputs/split_check``."""
    report = _json(OUTPUTS / "split_check" / "duplicates_summary.json")
    exact = next(item for item in report if item["threshold"] == 0)
    near = next(item for item in report if item["threshold"] == 8)
    return {
        "exact_groups": int(exact["num_duplicate_groups"]),
        "exact_images": int(exact["num_grouped_images"]),
        "near_groups": int(near["num_duplicate_groups"]),
        "near_images": int(near["num_grouped_images"]),
        "cross_class_groups": int(exact["cross_class_groups"]),
    }


def load_rq1_per_seed() -> list[dict]:
    """12 lượt chạy RQ1: 4 nhóm đặc trưng × 3 seed."""
    frame = pd.read_csv(RESULTS / "report_rq1" / "r1_per_seed.csv")
    return [
        {
            "features": row["features"],
            "seed": int(row["seed"]),
            "macro_f1": float(row["macro_f1"]),
            "f1_lo": float(row["f1_Lung_Opacity"]),
            "f1_vp": float(row["f1_Viral Pneumonia"]),
        }
        for row in frame.to_dict("records")
    ]


def load_rq3_per_scenario() -> list[dict]:
    """Các kịch bản RQ3 kèm accuracy ra recall từng lớp."""
    frame = pd.read_csv(RESULTS / "report_rq3" / "r1_per_scenario.csv")
    columns = [column for column in frame.columns if column.startswith("recall_")]
    return [
        {
            "scenario": row["scenario"],
            "macro_f1": float(row["macro_f1"]),
            "accuracy": None,
            "recall": {column[len("recall_"):]: float(row[column]) for column in columns},
        }
        for row in frame.to_dict("records")
    ]


def load_pairs_detail() -> dict:
    """Phân bố 735 cặp gần trùng theo cặp split và theo khoảng cách."""
    report = _json(OUTPUTS / "split_check" / "cross_split_hamming_report.json")
    return {
        "by_split": report["split_pairs_distribution"],
        "by_distance": report["dist_distribution"],
        "class_relation": report["class_relation"],
        "total": int(report["cross_split_pairs_count"]),
        "total_d1_4": int(report["total_pairs_d1_4"]),
    }


def load_latency_detail() -> dict:
    """Toàn bộ phân bố độ trễ theo từng chặng và từng phần trăm."""
    data = _json(RESULTS / "demo_latency_sustained" / "latency.json")
    medians = data["stats"]["per_image_median_seconds"]
    return {
        "stages": {
            key.replace("_seconds", ""): {
                "median": float(payload["median"]),
                "p90": float(payload["p90"]),
                "p95": float(payload["p95"]),
                "max": float(payload["max"]),
                "mean": float(payload["mean"]),
            }
            for key, payload in medians.items()
        },
        "warmup": data.get("warmup_seconds"),
        "repeats": int(data["method"]["repeats"]),
        "n_images": int(data["method"]["n_images"]),
        "artifact": data["artifact"],
        "environment": data["environment"],
    }


def load_cases() -> list[dict]:
    """Hai ảnh minh hoạ input → output trên slide 24, đọc từ preds_val của SVM."""
    frame = pd.read_csv(RESULTS / "rq2_ghep_svm_s42" / "preds_val.csv")
    out = []
    for image_id in ("COVID-1006.png", "Normal-9540.png"):
        row = frame[frame["image_id"] == image_id].iloc[0]
        y_true = CLASSES[int(row["y_true"])]
        y_pred = CLASSES[int(row["y_pred"])]
        probability = float(row[f"proba_{y_pred.replace(' ', '_')}"])
        out.append(
            {
                "image_id": image_id,
                "y_true": y_true,
                "y_pred": y_pred,
                "probability": probability,
                "correct": y_true == y_pred,
            }
        )
    return out


def build() -> dict:
    """Gom toàn bộ nguồn số đã định dạng sẵn cho tầng nội dung."""
    split = load_split()
    pairs = load_pairs()
    baselines = load_baselines()
    rq1 = load_rq1()
    rq2 = load_rq2()
    rq3 = load_rq3()
    test = load_test()
    val_errors = load_val_errors()
    latency = load_latency()
    unlock = load_unlock()
    interval = load_test_interval()

    val_scenario = rq3["scenarios"]["orig_to_orig"]["macro_f1"]
    gap = val_scenario - test["macro_f1"]
    normal_lung_test = int(test["matrix"][1][2] + test["matrix"][2][1])

    return {
        "split": split,
        "pairs": pairs,
        "baselines": baselines,
        "rq1": rq1,
        "rq1_cost": load_rq1_cost(),
        "rq2": rq2,
        "rq3": rq3,
        "permutation": load_permutation(),
        "test": test,
        "test_ci": interval.get("ci"),
        "val_errors": val_errors,
        "latency": latency,
        "brightness": load_brightness(),
        "unlock": unlock,
        "sources": load_sources(),
        "svm_cv": load_svm_cv(),
        "rules": load_rules(),
        "duplicates": load_duplicates(),
        "rq1_per_seed": load_rq1_per_seed(),
        "rq3_per_scenario": load_rq3_per_scenario(),
        "pairs_detail": load_pairs_detail(),
        "latency_detail": load_latency_detail(),
        "cases": load_cases(),
        "gap": gap,
        "normal_lung_test": normal_lung_test,
        "normal_lung_pct": normal_lung_test / test["errors"],
        "features": {"total": 152, "hist": 64, "glcm": 60, "lbp": 28, "hog": 10404},
    }


D = build()
