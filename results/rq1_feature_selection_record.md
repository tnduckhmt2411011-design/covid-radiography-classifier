# Biên bản chốt nhóm đặc trưng tốt nhất của RQ1 cho RQ2 (S3-06)

Ngày ghi: 07/11/2026
Người thực hiện: Trần Nguyễn Đức (Leader) & Lê Hải Lý (Cặp 1)

## 1. Căn cứ quy tắc và biên bản đóng băng trước khi xem điểm
- Tiêu chí chấp nhận: Mục 5 của [`results/threshold_v3.md`](threshold_v3.md) (chốt ngày 16/10/2026).
- Biên bản thứ hạng chi phí trích đặc trưng (ghi và commit tại `84c68a1` trước khi mở điểm số): [`results/rq1_cost_rank_record.md`](rq1_cost_rank_record.md) và [`results/summary_full.json`](summary_full.json).
- Báo cáo thống kê và kiểm định bootstrap ghép cặp 2.000 lần (S3-09 / S3-05): [`results/report_rq1/r1_summary.csv`](report_rq1/r1_summary.csv) và [`results/report_rq1/r1_bootstrap_vs_reference.csv`](report_rq1/r1_bootstrap_vs_reference.csv).

## 2. Tóm tắt kết quả thực nghiệm RQ1 trên tập Validation (3.174 ảnh, 3 seed 42/43/44)

Bộ phân loại cố định: `RandomForestClassifier(n_estimators=500, class_weight="balanced_subsample")`. Tất cả 12 run đều vượt qua các cổng hợp lệ H1–H7 (`macro_f1 > B0 = 0,1627` và `macro_f1 > A0 = 0,2397`).

| Hạng F1 | Nhóm đặc trưng | Số chiều | Macro-F1 (TB ± SD) | 95% CI Bootstrap | Recall COVID | Recall Lung_Opacity | Recall Normal | Recall Viral Pneumonia | Giây CPU trích/ảnh (Hạng chi phí) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **`ghep` (hist + GLCM + LBP)** | 152 | **0,8599 ± 0,0030** | `[0,8452 ; 0,8732]` | 0,9032 ± 0,0037 | 0,7689 ± 0,0039 | 0,8994 ± 0,0011 | 0,7734 ± 0,0085 | 0,056773 s (Hạng 4) |
| **2** | **`glcmlbp` (GLCM + LBP)** | 88 | **0,8156 ± 0,0023** | `[0,7986 ; 0,8309]` | 0,8107 ± 0,0047 | 0,7453 ± 0,0059 | 0,8774 ± 0,0010 | 0,7241 ± 0,0000 | 0,055240 s (Hạng 3) |
| **3** | **`hist` (Tham chiếu A1)** | 64 | **0,7829 ± 0,0013** | `[0,7643 ; 0,8002]` | 0,7995 ± 0,0057 | 0,7143 ± 0,0011 | 0,8922 ± 0,0007 | 0,6207 ± 0,0049 | 0,001337 s (Hạng 1) |
| **4** | **`hog` (HOG ô 16×16)** | 10.404 | **0,7625 ± 0,0038** | `[0,7459 ; 0,7787]` | 0,4389 ± 0,0109 | 0,7575 ± 0,0048 | 0,9214 ± 0,0010 | 0,7849 ± 0,0028 | 0,020073 s (Hạng 2) |

## 3. Kết quả phép so sánh chính của RQ1

Theo Mục 5 của `results/threshold_v3.md`:
> *"Phép so sánh chính của RQ1: nhóm đặc trưng (khác histogram) có macro-F1 trung bình cao nhất so với histogram."*

Nhóm đặc trưng (khác `hist`) có Macro-F1 trung bình cao nhất là **`ghep`** (`0,859895`). Đối chiếu với cấu hình tham chiếu **`hist`** (`0,782852`) trên 3.174 ảnh validation bằng bootstrap ghép cặp 2.000 lần (`rng_seed = 42`):

- **Hiệu số điểm ($\Delta \text{Macro-F1} = \text{ghep} - \text{hist}$):** `+0,077042` ($\ge 0,005$ — vượt ngưỡng quy ước `0,005` gấp 15,4 lần).
- **Khoảng tin cậy 95% của hiệu số:** `[+0,061106 ; +0,092456]`.
- **Kiểm tra chứa 0 (`contains_zero`):** `False` (cận dưới `+0,061106 > 0`).

*(Thông tin bổ trợ từ `r1_bootstrap_vs_reference.csv`: `glcmlbp` so với `hist` đạt $\Delta = +0,032785$, 95% CI `[+0,013076 ; +0,051280]`, không chứa 0; `hog` so với `hist` đạt $\Delta = -0,020330$, 95% CI `[-0,041918 ; +0,001381]`, chứa 0).*

## 4. Quyết định chính thức cho RQ2 (S3-06)

Vì nhóm đặc trưng **`ghep`** thỏa mãn đồng thời cả hai điều kiện bắt buộc tại Mục 5 `results/threshold_v3.md` ($\Delta \text{Macro-F1} \ge 0,005$ VÀ khoảng tin cậy 95% bootstrap ghép cặp không chứa 0):

1. **Nhóm đặc trưng được chọn đi tiếp sang RQ2 (S4-03):** **`ghep`** (152 chiều = Histogram độ xám 64 bin + GLCM 60 thuộc tính + LBP đa bán kính 28 bin).
2. **Cấu hình tham chiếu cho RQ2:** Bộ phân loại Random Forest trên nhóm đặc trưng `ghep` (`Macro-F1 = 0,859895`).
