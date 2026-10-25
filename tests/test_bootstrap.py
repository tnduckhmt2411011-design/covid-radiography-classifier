"""Bộ kiểm thử cho module src/bootstrap.py.

Bao gồm ít nhất 13 ca kiểm thử (T1 đến T13) kiểm tra tính đúng đắn toán học,
đáp án tính tay, tính ngẫu nhiên tái lập, xử lý ngoại lệ và xuất báo cáo.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score

from src.bootstrap import (
    align_predictions,
    bootstrap_ci_macro_f1,
    build_report,
    load_predictions,
    macro_f1_from_labels,
    paired_bootstrap_diff,
    r2_submatrix,
    r5_text,
    sampling_error,
)
from src.metrics import DEFAULT_CLASS_NAMES, compute_metrics


def test_t1_macro_f1_matches_sklearn():
    """T1: macro_f1_from_labels khớp sklearn f1_score trên ít nhất 5 bộ dữ liệu ngẫu nhiên.

    Lý do kỳ vọng:
    - Thuật toán tự cài bằng np.bincount phải tương đương tuyệt đối với công thức
      Macro-F1 của scikit-learn với average='macro', labels=[0, 1, 2, 3], zero_division=0.
    - Sai số cho phép nhỏ hơn 1e-12 trên nhiều cỡ mẫu và tỉ lệ mất cân bằng khác nhau.
    """
    rng = np.random.default_rng(101)
    for i in range(5):
        n = rng.integers(50, 500)
        # Sinh nhãn thực tế và dự đoán ngẫu nhiên trong [0, 3]
        y_true = rng.integers(0, 4, size=n)
        y_pred = rng.integers(0, 4, size=n)

        # Tính bằng hàm tự viết
        custom_f1 = macro_f1_from_labels(y_true, y_pred, num_classes=4)

        # Tính bằng scikit-learn chuẩn
        sk_f1 = float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
                labels=[0, 1, 2, 3],
                zero_division=0,
            )
        )

        assert abs(custom_f1 - sk_f1) < 1e-12, (
            f"Lần lặp {i}: custom={custom_f1} khác sklearn={sk_f1}"
        )


def test_t2_hand_calculated_macro_f1():
    """T2: Đối chiếu đáp án tính tay chi tiết trên mảng 8 phần tử.

    Đáp án tính tay:
    - Dữ liệu: y_true=[0,0,1,1,2,2,3,3], y_pred=[0,1,1,1,2,3,3,3]
    - Lớp 0: TP=1, FP=0, FN=1 -> F1 = 2*1 / (2*1 + 0 + 1) = 2/3
    - Lớp 1: TP=2, FP=1, FN=0 -> F1 = 2*2 / (2*2 + 1 + 0) = 4/5
    - Lớp 2: TP=1, FP=0, FN=1 -> F1 = 2*1 / (2*1 + 0 + 1) = 2/3
    - Lớp 3: TP=2, FP=1, FN=0 -> F1 = 2*2 / (2*2 + 1 + 0) = 4/5
    - Macro-F1 = (2/3 + 4/5 + 2/3 + 4/5) / 4 = 11/15 ≈ 0.7333333333333333
    """
    y_true = [0, 0, 1, 1, 2, 2, 3, 3]
    y_pred = [0, 1, 1, 1, 2, 3, 3, 3]

    calculated = macro_f1_from_labels(y_true, y_pred, num_classes=4)
    expected = 11.0 / 15.0

    assert abs(calculated - expected) < 1e-12


def test_t3_identical_predictions_zero_diff():
    """T3: Khi hai cấu hình A và B giống hệt nhau, hiệu số bootstrap phải luôn bằng 0.

    Lý do kỳ vọng:
    - Rút mẫu ngẫu nhiên cùng chỉ số idx cho cả hai cấu hình; nếu A == B thì f1_a == f1_b
      trong mọi lần lặp bootstrap.
    - Điểm ước lượng point_diff = 0, toàn bộ mảng boot_diffs = 0, ci_low = ci_high = 0,
      và contains_zero = True.
    """
    rng = np.random.default_rng(202)
    n = 200
    y_true = rng.integers(0, 4, size=n)
    preds_a = rng.integers(0, 4, size=n)
    preds_b = preds_a.copy()

    res = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=300, rng_seed=42)

    assert np.all(res["boot_diffs"] == 0.0)
    assert res["point_diff"] == 0.0
    assert res["ci_low"] == 0.0
    assert res["ci_high"] == 0.0
    assert res["contains_zero"] is True


def test_t4_known_synthetic_shift():
    """T4: Đáp án biết trước với phân phối nhân tạo cỡ mẫu n=400.

    Đáp án tính tay:
    - n=400, 100 mẫu mỗi lớp: y_true = np.repeat([0, 1, 2, 3], 100)
    - Cấu hình A hoàn hảo: A = y_true -> TP=100 cho mỗi lớp -> F1=1.0 -> Macro-F1=1.0
    - Cấu hình B: các chỉ số i % 10 == 0 (gồm 40 chỉ số, 10 chỉ số mỗi lớp) bị đổi sang (label+1)%4.
      Với mỗi lớp: TP=90, FN=10 (bị phân loại nhầm sang lớp khác), FP=10 (nhận từ lớp trước).
      F1 mỗi lớp = 2*90 / (2*90 + 10 + 10) = 180 / 200 = 0.9.
      Macro-F1(B) = 0.9.
    - point_diff = 1.0 - 0.9 = 0.1.
    - Với n_boot=500: A luôn vượt trội B trên mọi mẫu rút nên ci_low > 0 và contains_zero là False.
    """
    n = 400
    y_true = np.repeat(np.arange(4), 100)
    preds_a = y_true.copy()
    preds_b = y_true.copy()

    for idx in range(n):
        if idx % 10 == 0:
            preds_b[idx] = (preds_b[idx] + 1) % 4

    res = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=500, rng_seed=42)

    assert abs(res["point_a"] - 1.0) < 1e-12
    assert abs(res["point_b"] - 0.9) < 1e-12
    assert abs(res["point_diff"] - 0.1) < 1e-12
    assert res["ci_low"] > 0.0
    assert res["contains_zero"] is False


def test_t5_multiple_seeds_average_matches_sklearn():
    """T5: Khi có nhiều seed, point_a và point_b bằng trung bình macro-F1 từng seed.

    Lý do kỳ vọng:
    - Điểm ước lượng trên mẫu gốc của mỗi cấu hình phải là trung bình cộng Macro-F1
      qua các seed tính bằng scikit-learn độc lập.
    - point_diff = point_a - point_b.
    """
    rng = np.random.default_rng(303)
    n = 300
    y_true = rng.integers(0, 4, size=n)

    seeds_a = [rng.integers(0, 4, size=n) for _ in range(3)]
    seeds_b = [rng.integers(0, 4, size=n) for _ in range(3)]

    preds_a = np.stack(seeds_a, axis=0)
    preds_b = np.stack(seeds_b, axis=0)

    sk_f1_a = [
        float(f1_score(y_true, s_pred, average="macro", labels=[0, 1, 2, 3], zero_division=0))
        for s_pred in seeds_a
    ]
    sk_f1_b = [
        float(f1_score(y_true, s_pred, average="macro", labels=[0, 1, 2, 3], zero_division=0))
        for s_pred in seeds_b
    ]

    expected_point_a = float(np.mean(sk_f1_a))
    expected_point_b = float(np.mean(sk_f1_b))
    expected_diff = expected_point_a - expected_point_b

    res = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=100, rng_seed=42)

    assert abs(res["point_a"] - expected_point_a) < 1e-12
    assert abs(res["point_b"] - expected_point_b) < 1e-12
    assert abs(res["point_diff"] - expected_diff) < 1e-12


def test_t6_ci_percentile_definition():
    """T6: Kiểm tra ci_low và ci_high khớp đúng định nghĩa phân vị 2.5% và 97.5%.

    Lý do kỳ vọng:
    - Khoảng tin cậy 95% theo phương pháp percentile bootstrap được tính bằng
      np.percentile(boot_diffs, [2.5, 97.5]).
    """
    rng = np.random.default_rng(404)
    n = 250
    y_true = rng.integers(0, 4, size=n)
    preds_a = rng.integers(0, 4, size=n)
    preds_b = rng.integers(0, 4, size=n)

    res = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=400, rng_seed=42)

    expected_low, expected_high = np.percentile(res["boot_diffs"], [2.5, 97.5])
    assert np.isclose(res["ci_low"], expected_low)
    assert np.isclose(res["ci_high"], expected_high)


def test_t7_rng_seed_reproducibility():
    """T7: Kiểm tra tính tái lập khi cùng rng_seed và phân kỳ khi khác rng_seed.

    Lý do kỳ vọng:
    - Cùng rng_seed phải sinh chuỗi chỉ số bootstrap giống hệt nhau, cho kết quả boot_diffs trùng khớp.
    - Khác rng_seed sinh chuỗi rút mẫu khác nhau, dẫn tới boot_diffs khác biệt.
    """
    rng = np.random.default_rng(505)
    n = 200
    y_true = rng.integers(0, 4, size=n)
    preds_a = rng.integers(0, 4, size=n)
    preds_b = rng.integers(0, 4, size=n)

    res1 = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=200, rng_seed=42)
    res2 = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=200, rng_seed=42)
    res3 = paired_bootstrap_diff(y_true, preds_a, preds_b, n_boot=200, rng_seed=999)

    assert np.array_equal(res1["boot_diffs"], res2["boot_diffs"])
    assert not np.array_equal(res1["boot_diffs"], res3["boot_diffs"])


def test_t8_validation_errors_load_and_align(tmp_path: Path):
    """T8: load_predictions và align_predictions phải báo ValueError trong các tình huống vi phạm dữ liệu.

    Lý do kỳ vọng:
    - Thiếu cột, image_id trùng lặp, số dòng khác expected_n, nhãn ngoài 0..3,
      hoặc tập image_id / y_true không khớp giữa các run đều phải bị chặn lại ngay lập tức.
    """
    res_dir = tmp_path / "runs"
    res_dir.mkdir()

    def make_run_csv(feat: str, seed: int, data: dict):
        run_folder = res_dir / f"rq1_{feat}_rf_s{seed}"
        run_folder.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(data).to_csv(run_folder / "preds_val.csv", index=False)

    # 1. Thiếu cột
    make_run_csv("feat1", 42, {"image_id": ["img1", "img2"], "y_true": [0, 1]})
    with pytest.raises(ValueError, match="thiếu các cột bắt buộc"):
        load_predictions(res_dir, "feat1", 42, expected_n=None)

    # 2. image_id trùng
    make_run_csv("feat2", 42, {"image_id": ["img1", "img1"], "y_true": [0, 1], "y_pred": [0, 1]})
    with pytest.raises(ValueError, match="trùng lặp"):
        load_predictions(res_dir, "feat2", 42, expected_n=None)

    # 3. Số dòng khác expected_n
    make_run_csv("feat3", 42, {"image_id": ["img1", "img2"], "y_true": [0, 1], "y_pred": [0, 1]})
    with pytest.raises(ValueError, match="khác kỳ vọng"):
        load_predictions(res_dir, "feat3", 42, expected_n=3)

    # 4. Nhãn ngoài 0..3
    make_run_csv("feat4", 42, {"image_id": ["img1", "img2"], "y_true": [0, 4], "y_pred": [0, 1]})
    with pytest.raises(ValueError, match="ngoài phạm vi 0..3"):
        load_predictions(res_dir, "feat4", 42, expected_n=None)

    # 5. image_id khác nhau giữa các run khi align
    df_a = pd.DataFrame({"image_id": ["img1", "img2"], "y_true": [0, 1], "y_pred": [0, 1]})
    df_b = pd.DataFrame({"image_id": ["img1", "img3"], "y_true": [0, 1], "y_pred": [0, 1]})
    runs_diff_ids = {"f1": {42: df_a}, "f2": {42: df_b}}
    with pytest.raises(ValueError, match="không khớp"):
        align_predictions(runs_diff_ids)

    # 6. y_true khác nhau giữa các run khi align
    df_c = pd.DataFrame({"image_id": ["img1", "img2"], "y_true": [0, 2], "y_pred": [0, 1]})
    runs_diff_y = {"f1": {42: df_a}, "f2": {42: df_c}}
    with pytest.raises(ValueError, match="không khớp"):
        align_predictions(runs_diff_y)


def test_t9_r2_submatrix():
    """T9: Trích xuất ma trận con 2x2 cho lớp 1 (Lung Opacity) và lớp 2 (Normal).

    Đáp án tính tay:
    - Ma trận 4x4:
      [[5, 1, 2, 0],
       [0, 6, 3, 1],
       [1, 4, 7, 0],
       [0, 0, 1, 8]]
    - Hàng 1 (Lung Opacity): cột 1 là 6, cột 2 là 3 -> [6, 3]
    - Hàng 2 (Normal): cột 1 là 4, cột 2 là 7 -> [4, 7]
    - Ma trận con 2x2 kỳ vọng là [[6, 3], [4, 7]].
    """
    cm = [
        [5, 1, 2, 0],
        [0, 6, 3, 1],
        [1, 4, 7, 0],
        [0, 0, 1, 8],
    ]
    sub = r2_submatrix(cm)
    expected = np.array([[6, 3], [4, 7]])
    assert np.array_equal(sub, expected)


def test_t10_sampling_error():
    """T10: Kiểm tra công thức sai số chuẩn lấy mẫu sqrt(p*(1-p)/n) và xử lý ngoại lệ.

    Đáp án tính tay:
    - Với p=0.8, n=3174: sqrt(0.8 * 0.2 / 3174) = sqrt(0.16 / 3174) ≈ 0.00709997 -> làm tròn 0.0071
    - Với p=0.8, n=203: sqrt(0.8 * 0.2 / 203) = sqrt(0.16 / 203) ≈ 0.0280741 -> làm tròn 0.0281
    - Khi p < 0, p > 1 hoặc n <= 0 thì phải ném ValueError.
    """
    assert round(sampling_error(0.8, 3174), 4) == 0.0071
    assert round(sampling_error(0.8, 203), 4) == 0.0281

    with pytest.raises(ValueError, match="nằm ngoài khoảng"):
        sampling_error(-0.1, 100)
    with pytest.raises(ValueError, match="nằm ngoài khoảng"):
        sampling_error(1.1, 100)
    with pytest.raises(ValueError, match="phải lớn hơn 0"):
        sampling_error(0.5, 0)
    with pytest.raises(ValueError, match="phải lớn hơn 0"):
        sampling_error(0.5, -10)


def test_t11_r5_text(tmp_path: Path):
    """T11: Đọc dòng quy định R5 từ threshold_v3.md thật và kiểm tra ngoại lệ tệp giả.

    Lý do kỳ vọng:
    - Trên results/threshold_v3.md thật: dòng bắt đầu bằng '- R5 Giới hạn'
      và chứa chuỗi '735 cặp gần trùng khác split'.
    - Trên tệp giả: ném ValueError khi có 0 dòng hoặc 2 dòng bắt đầu bằng '- R5 '.
    """
    real_path = Path(__file__).resolve().parent.parent / "results" / "threshold_v3.md"
    assert real_path.is_file(), f"Không tìm thấy tệp {real_path}"

    real_text = r5_text(real_path)
    assert real_text.startswith("- R5 Giới hạn")
    assert "735 cặp gần trùng khác split" in real_text

    # Tệp giả 0 dòng R5
    fake_0 = tmp_path / "fake_0.md"
    fake_0.write_text("# Tiêu đề\n- R1 Mục 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Kỳ vọng đúng 1 dòng"):
        r5_text(fake_0)

    # Tệp giả 2 dòng R5
    fake_2 = tmp_path / "fake_2.md"
    fake_2.write_text("- R5 Giới hạn 1\n- R5 Giới hạn 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Kỳ vọng đúng 1 dòng"):
        r5_text(fake_2)


def test_t12_build_report_fake_data(tmp_path: Path):
    """T12: build_report trên dữ liệu giả lập (4 nhóm x 3 seed, n=300).

    Lý do kỳ vọng:
    - Tạo đủ 8 tệp báo cáo R1, R2, R4, R5 theo danh sách.
    - r1_per_seed.csv có đúng 12 dòng dữ liệu (4 nhóm x 3 seed).
    - r1_summary.csv có đúng 4 dòng dữ liệu (4 nhóm đặc trưng).
    - r1_bootstrap_vs_reference.csv có đúng 3 dòng (các nhóm khác so với reference, không có chính reference).
    - bootstrap_config.json lưu đúng các tham số và không chứa đường dẫn tuyệt đối.
    """
    results_dir = tmp_path / "results"
    out_dir = tmp_path / "report_rq1"
    features = ["hist", "glcmlbp", "hog", "ghep"]
    seeds = [42, 43, 44]
    n = 300

    rng = np.random.default_rng(606)
    image_ids = [f"img_{i:04d}" for i in range(n)]
    y_true = rng.integers(0, 4, size=n).tolist()

    for feat in features:
        for s in seeds:
            run_dir = results_dir / f"rq1_{feat}_rf_s{s}"
            run_dir.mkdir(parents=True, exist_ok=True)
            y_pred = rng.integers(0, 4, size=n).tolist()
            df = pd.DataFrame({
                "image_id": image_ids,
                "y_true": y_true,
                "y_pred": y_pred,
            })
            df.to_csv(run_dir / "preds_val.csv", index=False)

    threshold_path = Path(__file__).resolve().parent.parent / "results" / "threshold_v3.md"

    report_files = build_report(
        results_dir=results_dir,
        out_dir=out_dir,
        features=features,
        seeds=seeds,
        reference="hist",
        n_boot=50,
        rng_seed=42,
        expected_n=300,
        threshold_path=threshold_path,
    )

    expected_files = [
        "r1_per_seed.csv",
        "r1_summary.csv",
        "r1_confusion_matrices.json",
        "r1_bootstrap_vs_reference.csv",
        "r2_normal_lung_opacity.csv",
        "r4_sampling_error.csv",
        "r5_gioi_han.md",
        "bootstrap_config.json",
    ]

    for fname in expected_files:
        assert fname in report_files
        assert report_files[fname].is_file(), f"Tệp {fname} chưa được tạo"

    df_per_seed = pd.read_csv(report_files["r1_per_seed.csv"])
    assert len(df_per_seed) == 12

    df_summary = pd.read_csv(report_files["r1_summary.csv"])
    assert len(df_summary) == 4

    df_boot_ref = pd.read_csv(report_files["r1_bootstrap_vs_reference.csv"])
    assert len(df_boot_ref) == 3
    assert "hist" not in df_boot_ref["candidate"].tolist()

    # Kiểm tra config
    with open(report_files["bootstrap_config.json"], "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["features"] == features
    assert cfg["seeds"] == seeds
    assert cfg["reference"] == "hist"
    assert cfg["n"] == 300
    assert cfg["n_boot"] == 50
    assert "numpy_version" in cfg
    assert "pandas_version" in cfg
    assert "scikit_learn_version" in cfg
    for val in cfg.values():
        if isinstance(val, str):
            assert "tmp" not in val.lower() and "\\" not in val and "/" not in val


def test_t13_cross_check_with_metrics_module(tmp_path: Path):
    """T13: Đối chiếu chỉ số trong r1_per_seed.csv với compute_metrics của src/metrics.py.

    Lý do kỳ vọng:
    - Macro-F1, Precision, Recall và F1 từng lớp trong r1_per_seed.csv
      phải bằng kết quả trả về từ compute_metrics khi làm tròn đến 4 chữ số thập phân.
    """
    results_dir = tmp_path / "results"
    out_dir = tmp_path / "report_rq1"
    features = ["hist"]
    seeds = [42]
    n = 100

    rng = np.random.default_rng(707)
    image_ids = [f"img_{i:03d}" for i in range(n)]
    y_true = rng.integers(0, 4, size=n)
    y_pred = rng.integers(0, 4, size=n)

    run_dir = results_dir / "rq1_hist_rf_s42"
    run_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({
        "image_id": image_ids,
        "y_true": y_true,
        "y_pred": y_pred,
    }).to_csv(run_dir / "preds_val.csv", index=False)

    threshold_path = Path(__file__).resolve().parent.parent / "results" / "threshold_v3.md"

    report_files = build_report(
        results_dir=results_dir,
        out_dir=out_dir,
        features=features,
        seeds=seeds,
        reference="hist",
        n_boot=10,
        rng_seed=42,
        expected_n=100,
        threshold_path=threshold_path,
    )

    df_per_seed = pd.read_csv(report_files["r1_per_seed.csv"])
    row = df_per_seed.iloc[0]

    # Tính bằng compute_metrics trong src/metrics.py
    metrics_result = compute_metrics(y_true, y_pred, class_names=DEFAULT_CLASS_NAMES)

    assert round(row["macro_f1"], 4) == round(metrics_result["macro_f1"], 4)

    for c_name in DEFAULT_CLASS_NAMES:
        cm_prec = metrics_result["per_class"][c_name]["precision"]
        cm_rec = metrics_result["per_class"][c_name]["recall"]
        cm_f1 = metrics_result["per_class"][c_name]["f1"]

        assert round(row[f"precision_{c_name}"], 4) == round(cm_prec, 4)
        assert round(row[f"recall_{c_name}"], 4) == round(cm_rec, 4)
        assert round(row[f"f1_{c_name}"], 4) == round(cm_f1, 4)
