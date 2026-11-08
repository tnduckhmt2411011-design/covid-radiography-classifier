# Biên bản Đóng băng Phép so sánh chính RQ3 và Kiểm toán Chạy thử `t0` (Trước khi mở điểm Validation)

- **Ngày lập biên bản:** 08/11/2026 (Lập và đóng băng trước khi phiên chạy `full` trên Kaggle hoàn tất mở điểm `score=True`)
- **Commit mã nguồn chạy thực nghiệm:** `9ce35960cac5ea48967ce2ef640c56515ed8933b` (PR #39 đã merge vào `main`)
- **Mô hình và đặc trưng đã khóa từ RQ1 & RQ2:** Nhóm đặc trưng `ghep` (`152` chiều = Histogram `64` + GLCM `60` + LBP `28`) + `StandardScaler` (chỉ fit trên `train`) + `SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced", probability=True, random_state=42)`.
- **Căn cứ quy tắc:** Mục 1, Mục 4 (H1–H7), Mục 5 và Mục 6 (R1–R5, đặc biệt R3) của [`results/threshold_v3.md`](threshold_v3.md).

---

## 1. Bằng chứng Kiểm toán Chạy thử Kỹ thuật `t0` (`score=False`, Cổng H5)

Trước khi chạy lô toàn bộ `14.815` ảnh `train` và `3.174` ảnh `val`, nhóm đã thực hiện phiên chạy thử mù điểm (`mode="t0"`, `score=False`) trên Kaggle Kernel `ductrannguyen/cxr-rq3-masked` (Version 1):

- **Trạng thái Cổng H5 & H2:** `scored = false` trong `summary_rq3_t0.json` và toàn bộ 5 tệp `metrics.json` của `results_trial/rq3_ghep_svm_*_s42` (hoàn toàn không tính hay xuất `macro_f1`, `accuracy`, `per_class` trên tập `val` trong bước chạy thử kỹ thuật).
- **Thời gian CPU đo được trên mẫu thử `t0` (`n_train = 121`, `n_val = 61`):**
  - Trích đặc trưng `ghep` (152 chiều) trên `train`: `original = 5,354s`, `lung_only = 5,341s`, `outside_only = 5,345s`.
  - Trích đặc trưng `ghep` (152 chiều) trên `val`: `original = 2,673s`, `lung_only = 2,710s`, `outside_only = 2,709s`.
  - Huấn luyện `StandardScaler + SVC(RBF)`: `0,011s – 0,012s` CPU mỗi chế độ.
- **Kiểm tra trực quan và hình học mặt nạ phổi bước thử (`S4-07`):**
  - `empty_masks_count = 0` (không có mặt nạ rỗng sau khi co giãn `256×256 -> 299×299` bằng nội suy `cv2.INTER_NEAREST`).
  - `all_centered = true` (`20/20` mẫu thử có trọng tâm vùng phổi nằm trong khung trung tâm giải phẫu hợp lệ, `lung_fraction_mean = 0,2361`).

---

## 2. Đóng băng Phép so sánh chính của RQ3 và Thiết kế Kiểm tra Lối tắt (R3)

Theo đúng quy định tại Mục 5 của [`results/threshold_v3.md`](threshold_v3.md) (*"Mỗi RQ chỉ có MỘT phép so sánh chính, đóng băng và ghi vào biên bản trước khi xem kết quả"*):

### 2.1. Năm kịch bản thực nghiệm của RQ3 (`S5-01` & `S5-02`)

| Mã kịch bản (`scenario`) | Mã run (`run_id`) | Ảnh huấn luyện (`train`) | Ảnh đánh giá (`val`) | Ý nghĩa khoa học & Vai trò trong RQ3 |
| :--- | :--- | :---: | :---: | :--- |
| **`orig_to_orig`** *(Tham chiếu)* | `rq3_ghep_svm_orig_to_orig_s42` | `original` | `original` | Cấu hình chuẩn đã khóa ở RQ2 trên ảnh X-quang gốc `299×299` không che. |
| **`lung_to_lung`** *(Ứng viên chính)* | `rq3_ghep_svm_lung_to_lung_s42` | `lung_only` | `lung_only` | Huấn luyện và suy luận **chỉ từ bên trong vùng phổi** (`mask > 0`, ngoài phổi = `0`). Đo lường năng lực phân loại thuần túy từ nhu mô phổi khi loại bỏ toàn bộ nền, chữ in và khung xương ngoài phổi. |
| **`out_to_out`** *(Đối chứng lối tắt R3)* | `rq3_ghep_svm_out_to_out_s42` | `outside_only` | `outside_only` | Huấn luyện và suy luận **chỉ từ bên ngoài vùng phổi** (`mask == 0`, trong phổi = `0`). Đo lường trực tiếp lượng thông tin lối tắt (shortcut learning: viền ảnh, chữ X-quang `L/R`, hình thái lồng ngực ngoài phổi, độ sáng nền máy chụp) khi hoàn toàn không nhìn thấy nhu mô phổi. |
| **`orig_to_lung`** *(Nhiễu suy luận RQ3-A)* | `rq3_ghep_svm_orig_to_lung_s42` | `original` | `lung_only` | Đánh giá độ nhạy của bộ phân loại gốc (`orig_to_orig`) khi đột ngột xóa đen vùng ngoài phổi lúc suy luận (dịch chuyển phân phối histogram/GLCM/LBP do nền đen). |
| **`orig_to_out`** *(Nhiễu suy luận RQ3-A)* | `rq3_ghep_svm_orig_to_out_s42` | `original` | `outside_only` | Đánh giá xem bộ phân loại gốc (`orig_to_orig`) còn giữ được bao nhiêu điểm khi xóa đen toàn bộ nhu mô phổi lúc suy luận. |

### 2.2. Phép so sánh chính duy nhất của RQ3 (Mục 5 `threshold_v3.md`)

- **Cấu hình tham chiếu (`Reference`):** `orig_to_orig` (`rq3_ghep_svm_orig_to_orig_s42` — ảnh gốc không cần mặt nạ phổi khi suy luận, chi phí tiền xử lý thấp hơn).
- **Cấu hình ứng viên (`Candidate`):** `lung_to_lung` (`rq3_ghep_svm_lung_to_lung_s42` — huấn luyện và đánh giá trên ảnh chỉ giữ vùng phổi).
- **Quy tắc quyết định (đóng băng trước khi xem điểm):**
  - Thực hiện kiểm định bootstrap ghép cặp theo ảnh (`2.000` lần lấy mẫu có hoàn lại với `rng_seed = 42` trên `n = 3.174` ảnh validation) cho hiệu số:
    $$\Delta_{\text{RQ3}} = \text{Macro-F1}(\text{lung\_to\_lung}) - \text{Macro-F1}(\text{orig\_to\_orig})$$
  - Cấu hình `lung_to_lung` chỉ thay thế `orig_to_orig` để làm cấu hình chính thức mở khóa tập `test` ở Tuần 10 (`S5-04`) khi và chỉ khi **đồng thời** thỏa mãn:
    1. $\Delta_{\text{RQ3}} \ge +0,005$, **VÀ**
    2. Khoảng tin cậy 95% bootstrap ghép cặp `[ci_low, ci_high]` của $\Delta_{\text{RQ3}}$ không chứa `0` (`ci_low > 0`).
  - Trong mọi trường hợp khác (tức việc cắt vùng phổi làm giảm Macro-F1 hoặc không tăng đủ $+0,005$ có ý nghĩa thống kê), giữ nguyên cấu hình ảnh gốc `orig_to_orig` (`rq2_ghep_svm_s42` / `rq3_ghep_svm_orig_to_orig_s42`) cho bước đánh giá tập `test` duy nhất ở `S5-04`.

### 2.3. Phép kiểm tra Lối tắt bắt buộc R3 (`S5-02` & `S5-03`)

Bất kể cấu hình nào đi tiếp sang `S5-04`, báo cáo RQ3 bắt buộc trình bày đầy đủ:
1. **So sánh trực tiếp Trong phổi vs Ngoài phổi (`lung_to_lung` vs `out_to_out`) kèm khoảng tin cậy 95% bootstrap ghép cặp 2.000 lần:**
   - Đối chiếu với hai mốc kiểm tra lối tắt trước đó là `A0` (metadata tệp, `Macro-F1 = 0,2397`) và `A1` (histogram độ xám với RF, `Macro-F1 = 0,7852`).
   - Nếu `out_to_out` vượt xa mốc ngẫu nhiên/tầm thường (`B0 = 0,1627`, `A0 = 0,2397`), đây là bằng chứng thực nghiệm trực tiếp chứng minh bộ dữ liệu `COVID-19 Radiography Database` chứa tín hiệu lối tắt mạnh ở vùng ngoài phổi (khung xương lồng ngực bệnh nhi vs người lớn, viền đen, ký hiệu chữ/thiết bị chụp).
2. **Độ quan trọng hoán vị theo khối đặc trưng (`Block Permutation Importance`, `n_repeats = 10`, `rng_seed = 42`):**
   - So sánh mức sụt giảm Macro-F1 ($\Delta \text{Macro-F1}$) khi hoán vị 3 khối chính (`hist_64`, `glcm_60`, `lbp_28`) và 7 tiểu khối (`glcm_contrast_12`, `glcm_dissimilarity_12`, `glcm_homogeneity_12`, `glcm_energy_12`, `glcm_correlation_12`, `lbp_r1_p8_10`, `lbp_r2_p16_18`) giữa 3 mô hình `original`, `lung_only` và `outside_only`.
