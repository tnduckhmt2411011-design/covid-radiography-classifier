# Biên bản chốt bộ phân loại tốt nhất của RQ2 và đóng băng tham số thực nghiệm (S4-04)

Ngày ghi: 07/11/2026
Người thực hiện: Cả nhóm — đại diện ghi nhận: Trần Nguyễn Đức (Leader), Nguyễn Minh Thuận & Lê Minh

## 1. Căn cứ quy tắc và biên bản đóng băng trước khi xem điểm
- Tiêu chí chấp nhận: Mục 4 (H1–H7) và Mục 5 của [`results/threshold_v3.md`](threshold_v3.md) (chốt ngày 16/10/2026).
- Biên bản chốt nhóm đặc trưng đầu vào từ RQ1 (S3-06): [`results/rq1_feature_selection_record.md`](rq1_feature_selection_record.md) — cố định nhóm đặc trưng **`ghep`** (`152` chiều = Histogram độ xám 64 bin + GLCM 60 thuộc tính + LBP đa bán kính 28 bin).
- Biên bản thứ hạng chi phí huấn luyện RQ2 (ghi và commit tại `e087300` trước khi mở điểm số): [`results/rq2_cost_rank_record.md`](rq2_cost_rank_record.md) và [`results/summary_rq2_full.json`](summary_rq2_full.json).
- Báo cáo thống kê và kiểm định bootstrap ghép cặp 2.000 lần (S4-03): [`results/report_rq2/r1_summary.csv`](report_rq2/r1_summary.csv) và [`results/report_rq2/r1_bootstrap_vs_reference.csv`](report_rq2/r1_bootstrap_vs_reference.csv).

## 2. Tóm tắt kết quả thực nghiệm RQ2 trên tập Validation (3.174 ảnh)

Nhóm đặc trưng cố định: **`ghep` (152 chiều)**. Siêu tham số của từng bộ phân loại được chọn bằng `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` trên tập `train` (`14.815` ảnh), chia nhóm theo `group_id` (nhóm pHash $T=0$). Các bộ phân loại nhạy cảm tỷ lệ (`lr`, `knn`, `svm`) dùng `StandardScaler` chỉ fit trên phần train của từng fold / tập `train`. Ba bộ phân loại tất định (`lr`, `knn`, `svm`) chạy 1 lần (`s42`) và ghi rõ không có độ lệch chuẩn theo Cổng H3; ba bộ phân loại ngẫu nhiên (`dt`, `rf`, `gb`) chạy trên 3 seed (`42, 43, 44`). Tất cả 12 run đều vượt qua các cổng hợp lệ H1–H7 (`macro_f1 > B0 = 0,1627` và `macro_f1 > A0 = 0,2397`).

| Hạng F1 | Mã | Bộ phân loại & Trọng số lớp (H3) | Siêu tham số chọn qua 5-fold CV (`group_id`) | Số seed | Macro-F1 Val (TB ± SD) | 95% CI Bootstrap | Recall COVID | Recall Lung_Opacity | Recall Normal | Recall Viral Pneumonia | Tổng giây CPU huấn luyện (Hạng chi phí) |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **`svm`** | `SVC(kernel='rbf', class_weight='balanced')` + `StandardScaler` | `C=10.0, gamma='scale'` | 1 (Tất định) | **0,9024** *(không có SD)* | `[0,8909 ; 0,9129]` | 0,9572 | 0,8494 | 0,8837 | 0,9409 | 479,848 s (Hạng 4) |
| **2** | **`gb`** | `GradientBoostingClassifier(max_features='sqrt')` + `sample_weight='balanced'` | `n_estimators=200, learning_rate=0.1, max_depth=5` | 3 (`42, 43, 44`) | **0,8868 ± 0,0030** | `[0,8749 ; 0,8976]` | 0,9485 ± 0,0028 | 0,8261 ± 0,0059 | 0,8707 ± 0,0030 | 0,8949 ± 0,0075 | 2.163,459 s (Hạng 5) |
| **3** | **`rf`** | `RandomForestClassifier(class_weight='balanced_subsample')` *(Tham chiếu)* | `n_estimators=300, max_depth=None` | 3 (`42, 43, 44`) | **0,8582 ± 0,0033** | `[0,8432 ; 0,8716]` | 0,9025 ± 0,0065 | 0,7697 ± 0,0019 | 0,9012 ± 0,0019 | 0,7619 ± 0,0124 | 3.541,833 s (Hạng 6) |
| **4** | **`lr`** | `LogisticRegression(solver='lbfgs', max_iter=1000, class_weight='balanced')` + `StandardScaler` | `C=10.0` | 1 (Tất định) | **0,8370** *(không có SD)* | `[0,8221 ; 0,8505]` | 0,8678 | 0,8306 | 0,8014 | 0,9458 | 272,507 s (Hạng 3) |
| **5** | **`knn`** | `KNeighborsClassifier` *(không hỗ trợ `class_weight`)* + `StandardScaler` | `n_neighbors=5, weights='distance'` | 1 (Tất định) | **0,8242** *(không có SD)* | `[0,8075 ; 0,8397]` | 0,8194 | 0,7464 | 0,8857 | 0,7438 | 18,506 s (Hạng 1) |
| **6** | **`dt`** | `DecisionTreeClassifier(class_weight='balanced')` | `max_depth=10, min_samples_leaf=1` | 3 (`42, 43, 44`) | **0,7271 ± 0,0017** | `[0,7090 ; 0,7449]` | 0,7616 ± 0,0019 | 0,7641 ± 0,0011 | 0,7133 ± 0,0013 | 0,7586 ± 0,0049 | 202,362 s (Hạng 2) |

## 3. Kết quả phép so sánh chính của RQ2

Theo Mục 5 của `results/threshold_v3.md` và Mục 4 của `results/rq2_cost_rank_record.md`:
> *"RQ2 dùng cùng quy tắc, tham chiếu là bộ phân loại đã dùng ở RQ1. Mỗi RQ chỉ có MỘT phép so sánh chính, đóng băng và ghi vào biên bản trước khi xem kết quả."*

Bộ phân loại ứng viên (khác `rf`) có Macro-F1 validation cao nhất là **`svm`** (`0,902445`). Đối chiếu với cấu hình tham chiếu **`rf`** trên 3.174 ảnh validation bằng bootstrap ghép cặp 2.000 lần (`rng_seed = 42`):

1. **So với tham chiếu `rf` của RQ2 (`rq2_ghep_rf`, `n_estimators=300`, `Macro-F1 = 0,858246`):**
   - **Hiệu số điểm ($\Delta \text{Macro-F1} = \text{svm} - \text{rf}$):** `+0,044198` ($\ge 0,005$ — vượt ngưỡng quy ước `0,005` gấp 8,84 lần).
   - **Khoảng tin cậy 95% của hiệu số:** `[+0,031983 ; +0,058032]`.
   - **Kiểm tra chứa 0 (`contains_zero`):** `False` (cận dưới `+0,031983 > 0`).
2. **Đối chiếu bổ sung với tham chiếu `rf` cố định của RQ1 (`rq1_ghep_rf`, `n_estimators=500`, `Macro-F1 = 0,859895`):**
   - **Hiệu số điểm ($\Delta \text{Macro-F1} = \text{svm} - \text{rq1\_rf}$):** `+0,042550` ($\ge 0,005$).
   - **Khoảng tin cậy 95% của hiệu số:** `[+0,029933 ; +0,056696]`, `contains_zero = False`.
3. **Lợi thế chi phí huấn luyện:** `svm` chỉ tốn `479,848` giây CPU (Hạng chi phí 4), nhanh hơn **7,38 lần** so với `rf` (`3.541,833` giây CPU, Hạng chi phí 6).

*(Thông tin bổ trợ từ `r1_bootstrap_vs_reference.csv`: `gb` so với `rf` đạt $\Delta = +0,028570$, 95% CI `[+0,018310 ; +0,039875]`, không chứa 0; `lr`, `knn`, `dt` đều thấp hơn `rf` với $\Delta$ lần lượt là `-0,021274`, `-0,034048`, `-0,131155`).*

## 4. Cấu hình mô hình tối ưu nhất được đóng băng chính thức (S4-04)

Vì bộ phân loại **`svm`** thỏa mãn đồng thời cả hai điều kiện bắt buộc tại Mục 5 `results/threshold_v3.md` ($\Delta \text{Macro-F1} \ge 0,005$ VÀ khoảng tin cậy 95% bootstrap ghép cặp không chứa 0), đồng thời rẻ hơn tham chiếu `rf` về chi phí CPU huấn luyện, nhóm quyết định **đóng băng hoàn toàn cấu hình mô hình tối ưu nhất** cho RQ3 (S5-01, S5-02), phân tích lỗi (S4-06) và đánh giá tập test một lần duy nhất ở Tuần 10 (S5-04) như sau:

- **Đầu vào ảnh:** Ảnh X-quang ngực mức xám 8-bit kích thước `299 × 299` nguyên bản (không resize, không cân bằng histogram), nạp qua `CXRDataset` theo thứ tự chuẩn của `splits/split_v1.csv` (`SHA256 = f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98`).
- **Nhóm đặc trưng cố định (`ghep` — 152 chiều):**
  - Histogram mức xám: `64` bin trên `[0, 255]`, chuẩn hoá tổng bằng `1` (`64` chiều).
  - GLCM: lượng tử hoá `32` mức (`img // 8`), khoảng cách `[1, 3, 5]`, 4 góc `[0, pi/4, pi/2, 3pi/4]`, `symmetric=True`, `normed=True`, 5 thuộc tính (`contrast`, `dissimilarity`, `homogeneity`, `energy`, `correlation`; thay `NaN` của `correlation` bằng `0,0`) (`60` chiều).
  - LBP uniform: `(P=8, R=1)` 10 bin + `(P=16, R=2)` 18 bin, mỗi histogram chuẩn hoá tổng bằng `1` (`28` chiều).
- **Tiền xử lý đặc trưng (Cổng H6):** `StandardScaler()` của `scikit-learn`, **chỉ `fit` trên tập `train`** (`14.815` ảnh), sau đó `transform` cho tập đánh giá.
- **Bộ phân loại và siêu tham số đóng băng:**
  - `sklearn.svm.SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced", probability=True, random_state=42)`.
  - Tính chất: mô hình giải bài toán quy hoạch bậc hai lồi có nghiệm tất định đối với nhãn dự đoán `predict(X)`; `random_state=42` cố định cho ước lượng xác suất Platt scaling (`predict_proba`).
