"""Kiểm thử tính nhất quán giữa results/baseline_summary.csv và results/baseline_metrics.json."""

from pathlib import Path
import json
import csv
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
METRICS_JSON_PATH = REPO_ROOT / "results" / "baseline_metrics.json"
SUMMARY_CSV_PATH = REPO_ROOT / "results" / "baseline_summary.csv"


def test_baseline_summary_and_metrics_consistency():
    """Kiểm tra mọi chỉ số trong baseline_summary.csv khớp với baseline_metrics.json (sai số < 1e-4)."""
    if not METRICS_JSON_PATH.exists():
        pytest.skip(f"Không tìm thấy tệp {METRICS_JSON_PATH}")
    if not SUMMARY_CSV_PATH.exists():
        pytest.skip(f"Không tìm thấy tệp {SUMMARY_CSV_PATH}")

    with open(METRICS_JSON_PATH, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    with open(SUMMARY_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    assert len(csv_rows) == 6, f"Kỳ vọng 6 runs trong summary CSV, thực tế có {len(csv_rows)}"

    for row in csv_rows:
        rid = row["run_id"]
        assert rid in metrics_data, f"Run ID {rid} không tồn tại trong metrics.json"

        run_obj = metrics_data[rid]
        if "metrics" not in run_obj or "confusion_matrix" not in run_obj["metrics"]:
            pytest.skip(f"Run {rid} thiếu ma trận nhầm lẫn trong metrics.json")

        m = run_obj["metrics"]
        cm = m["confusion_matrix"]
        n = sum(map(sum, cm))
        sup = [sum(r) for r in cm]

        # Kiểm tra tính toán từ ma trận nhầm lẫn
        acc_from_cm = sum(cm[i][i] for i in range(4)) / n
        rec_from_cm = [cm[i][i] / sup[i] if sup[i] else 0 for i in range(4)]
        pred_from_cm = [sum(cm[r][c] for r in range(4)) for c in range(4)]
        pre_from_cm = [cm[i][i] / pred_from_cm[i] if pred_from_cm[i] else 0 for i in range(4)]
        f1_from_cm = [2 * a * b / (a + b) if a + b else 0 for a, b in zip(pre_from_cm, rec_from_cm)]
        ba_from_cm = sum(rec_from_cm) / 4
        macro_f1_from_cm = sum(f1_from_cm) / 4

        # 1. So khớp Accuracy
        csv_acc = float(row["val_accuracy"])
        assert abs(csv_acc - acc_from_cm) < 1e-4, f"Lệch accuracy ở {rid}: csv={csv_acc}, cm={acc_from_cm}"

        # 2. So khớp Balanced Accuracy
        csv_ba = float(row["val_balanced_acc"])
        assert abs(csv_ba - ba_from_cm) < 1e-4, f"Lệch balanced_acc ở {rid}: csv={csv_ba}, cm={ba_from_cm}"

        # 3. So khớp Macro-F1
        csv_f1 = float(row["val_macro_f1"])
        assert abs(csv_f1 - macro_f1_from_cm) < 1e-4, f"Lệch macro_f1 ở {rid}: csv={csv_f1}, cm={macro_f1_from_cm}"

        # 4. So khớp Per-class F1
        assert abs(float(row["covid_f1"]) - f1_from_cm[0]) < 1e-4
        assert abs(float(row["lung_opacity_f1"]) - f1_from_cm[1]) < 1e-4
        assert abs(float(row["normal_f1"]) - f1_from_cm[2]) < 1e-4
        assert abs(float(row["viral_pneumonia_f1"]) - f1_from_cm[3]) < 1e-4

        # 5. So khớp Per-class Recall
        assert abs(float(row["recall_covid"]) - rec_from_cm[0]) < 1e-4
        assert abs(float(row["recall_lung_opacity"]) - rec_from_cm[1]) < 1e-4
        assert abs(float(row["recall_normal"]) - rec_from_cm[2]) < 1e-4
        assert abs(float(row["recall_viral_pneumonia"]) - rec_from_cm[3]) < 1e-4
