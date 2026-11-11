# Kết luận Nghiên cứu về Hiện tượng Học Lối tắt (Shortcut Learning) và Đóng băng Cấu hình Mở khóa Test (S5-03)

- **Ngày lập:** 08/11/2026
- **Thực hiện:** Lê Minh (Phụ trách RQ3), duyệt chéo: Nguyễn Minh Thuận, Nguyễn Đức (Leader)
- **Cam kết phương pháp luận:** Tuân thủ Cổng H2 (tuyệt đối không mở khóa hay đọc tập `test`), Cổng H6 (chống rò rỉ), Mục 5 và Mục 6 (R1–R5, đặc biệt R3) của [`results/threshold_v3.md`](threshold_v3.md).

---

## 1. Tóm tắt Số liệu Thực nghiệm RQ3 trên Tập Validation ($n = 3.174$)

Thực nghiệm trên mô hình tối ưu đã đóng băng từ RQ2: `SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced")` kết hợp `StandardScaler` (chỉ fit trên train tương ứng) trên nhóm đặc trưng `ghep` (152 chiều = Histogram 64 + GLCM 60 + LBP 28), `seed = 42`.

### 1.1. Bảng tổng hợp hiệu năng 5 kịch bản (Bảng R1 & 95% CI Bootstrap 2.000 lần)

| Kịch bản (`scenario`) | Tập Train | Tập Val | Macro-F1 (Điểm ước lượng) | Khoảng tin cậy 95% Bootstrap | Accuracy | Recall COVID | Recall Lung Opacity | Recall Normal | Recall Viral Pneumonia |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`orig_to_orig`** *(Chuẩn)* | `original` | `original` | **0,9024** | **[0,8909, 0,9129]** | 89,00% | 95,72% | 84,94% | 88,37% | 94,09% |
| **`lung_to_lung`** *(Chỉ phổi)* | `lung_only` | `lung_only` | **0,8490** | **[0,8333, 0,8625]** | 85,44% | 86,59% | 81,40% | 86,54% | 92,12% |
| **`out_to_out`** *(Ngoài phổi)* | `outside_only` | `outside_only` | **0,8921** | **[0,8807, 0,9031]** | 87,84% | 94,79% | 83,17% | 87,26% | 94,58% |
| **`orig_to_lung`** *(Nhiễu RQ3-A)* | `original` | `lung_only` | **0,0723** | **[0,0677, 0,0770]** | 16,89% | 99,81% | 0,00% | 0,00% | 0,00% |
| **`orig_to_out`** *(Nhiễu RQ3-A)* | `original` | `outside_only` | **0,2084** | **[0,1953, 0,2220]** | 27,22% | 93,85% | 27,35% | 7,32% | 0,49% |

*Nguồn: `results/report_rq3/r1_summary.csv` (Macro-F1, khoảng tin cậy, Precision/Recall/F1 từng lớp) và `results/report_rq3/r4_sampling_error.csv` (Accuracy). Kiểm thử `tests/test_rq3_report_and_selection.py::test_rq3_shortcut_learning_conclusion_table_matches_csv` đối chiếu từng ô với hai tệp này.*

---

## 2. Kết quả Phép so sánh chính của RQ3 (Mục 5 `threshold_v3.md`)

- **Hiệu số Macro-F1 giữa Ứng viên (`lung_to_lung`) và Tham chiếu (`orig_to_orig`):**
  $$\Delta_{\text{RQ3}} = \text{Macro-F1}(\text{lung\_to\_lung}) - \text{Macro-F1}(\text{orig\_to\_orig}) = 0,8490 - 0,9024 = -0,0535$$
- **Khoảng tin cậy 95% Bootstrap ghép cặp (2.000 lần lấy mẫu theo ảnh):**
  $$\text{95\% CI} = [-0,0691, -0,0392] \quad (\text{contains\_zero} = \text{False})$$
- **Kết luận quy tắc:**
  - $\Delta_{\text{RQ3}} = -0,0535 < +0,005$, không đạt điều kiện cải thiện vượt ngưỡng.
  - Việc che đi vùng ngoài phổi và chỉ huấn luyện trên nhu mô phổi làm giảm Macro-F1 có ý nghĩa thống kê (giảm khoảng 5,35 điểm phần trăm).
  - **Quyết định:** Giữ nguyên cấu hình ảnh gốc **`orig_to_orig`** (`rq2_ghep_svm_s42` / `rq3_ghep_svm_orig_to_orig_s42`) làm cấu hình tối ưu chính thức để mở khóa đánh giá một lần duy nhất trên tập `test` ở Tuần 10 (`S5-04`).

---

## 3. Bằng chứng Thực nghiệm về Hiện tượng Học Lối tắt (Shortcut Learning — Bắt buộc R3)

Kết quả thực nghiệm trên cho thấy hiện tượng **Shortcut Learning** và thiên lệch nguồn dữ liệu của bộ ảnh `COVID-19 Radiography Database`:

### 3.1. Nghịch lý Mô hình chỉ nhìn vùng ngoài phổi (`out_to_out`)
- Một mô hình SVM hoàn toàn **bị che đen 100% vùng nhu mô phổi** (chỉ nhìn thấy viền xương ngực, bờ vai, chữ in ký hiệu thiết bị và phông nền đen/xám bên ngoài lồng ngực) vẫn đạt **Macro-F1 = 0,8921** (Accuracy = 87,84%).
- So sánh ghép cặp giữa mô hình nhìn toàn bộ ảnh (`orig_to_orig`) và mô hình chỉ nhìn ngoài phổi (`out_to_out`):
  $$\Delta = \text{Macro-F1}(\text{orig\_to\_orig}) - \text{Macro-F1}(\text{out\_to\_out}) = +0,0103$$
  $$\text{95\% CI} = [-0,0017, +0,0220] \quad (\text{contains\_zero} = \text{True}!)$$
- **Phát hiện quan trọng:** Khoảng tin cậy 95% chứa số 0, nên dữ liệu **chưa đủ để kết luận** hiệu năng của mô hình nhìn toàn bộ ảnh khác mô hình chỉ nhìn vùng ngoài phổi. Đây là kết luận thống kê theo khoảng tin cậy, không phải bằng chứng về sự tương đương.
- Hơn thế nữa, `out_to_out` đạt Macro-F1 cao hơn đáng kể so với `lung_to_lung` ($\Delta = +0,0431$, 95% CI `[+0,0281, +0,0582]`, không chứa 0).

### 3.2. Căn nguyên Y sinh và Nguồn gốc Dữ liệu của Lối tắt
1. **Thiên lệch lứa tuổi ở lớp `Viral Pneumonia`:**
   - 100% ảnh `Viral Pneumonia` (1.345 ảnh) và 1.341 ảnh `Normal` thuộc bộ Kaggle của Paul Mooney. Nhiều khả năng đây là ảnh **bệnh nhi 1–5 tuổi** từ nghiên cứu gốc của Kermany và cộng sự (2018) — đây là suy luận từ nguồn dữ liệu, không phải thông tin tuổi được ghi trực tiếp trong metadata (`docs/dataset_provenance.md`, mục 3.3).
   - Ngay cả khi bị xóa đen vùng phổi, mô hình `out_to_out` nhận diện lớp `Viral Pneumonia` với **Recall 94,58%**, cao nhất trong cả 5 kịch bản.
   - Giả thuyết: mô hình có thể đang dựa vào các đặc trưng hình học lồng ngực trẻ em — xương sườn nằm ngang và mảnh, vòm hoành cao, tỷ lệ lồng ngực nhỏ so với khung hình `299×299` — khác với lồng ngực người lớn ở các lớp còn lại. Giả thuyết này chưa được kiểm chứng riêng.
2. **Ký hiệu thiết bị chụp và nhãn nguồn ảnh ở lớp `COVID`:**
   - Ảnh COVID thu thập từ các kho BIMCV, SIRM, trường y tại Đức có các ký hiệu máy chụp kỹ thuật số (`DX`, `CX`), ký hiệu định hướng `L`/`R` in đậm ngoài thành ngực, và độ tương phản nền đặc trưng.
   - Mô hình `out_to_out` phân loại COVID đạt Recall **94,79%** mà không cần nhìn vào tổn thương đông đặc kính mờ trong phổi.
3. **Sự sụp đổ khi che ngoài phổi lúc suy luận (`orig_to_lung`):**
   - Khi mô hình huấn luyện trên ảnh gốc (`orig_to_orig`) gặp ảnh bị che ngoài phổi (`orig_to_lung`), Macro-F1 giảm còn **0,0723**. Giả thuyết: các đặc trưng toàn cục (Histogram 64 bin, GLCM, LBP) bị chi phối bởi vùng giá trị 0 màu đen bao quanh, tạo dịch chuyển phân phối đầu vào (*covariate shift*); giả thuyết này chưa được kiểm chứng riêng.

### 3.3. Phân tích Độ quan trọng Hoán vị Khối (Permutation Importance — S5-02)
- Khi huấn luyện trên **`lung_only`** (buộc phải tìm tổn thương trong phổi):
  - Khối **GLCM (đặc trưng kết cấu)** tăng vọt mức độ quan trọng lên hàng đầu: $\Delta \text{Macro-F1} = 0,4960 \pm 0,0035$, trong đó tiểu khối `glcm_dissimilarity_12` đóng góp $\Delta = 0,4655$ và `glcm_contrast_12` đóng góp $\Delta = 0,3163$.
  - Diễn giải: khi chỉ còn nhu mô phổi, tương phản giữa tổn thương thâm nhiễm mờ và vùng phổi lành là tín hiệu mà GLCM ghi nhận trực tiếp. Đây là diễn giải dựa trên kết quả hoán vị khối, chưa có thí nghiệm tách riêng để kiểm chứng.
- Ngược lại, trên **`outside_only`**:
  - Ba khối tổng hợp có mức sụt giảm Macro-F1 lớn nhất lần lượt là LBP 0,3590, GLCM 0,3526 và Histogram 0,2656. Kết cấu bề mặt (LBP và GLCM) chiếm ưu thế so với phân bố cường độ sáng, phù hợp với việc mô hình khai thác đường viền xương sườn, viền ảnh và ký hiệu chữ in ở vùng ngoài phổi.

---

## 4. Quyết định Đóng băng Tham số Thực nghiệm cho Tuần 10 (S5-04)

1. **Khóa cấu hình đánh giá Test:**
   - **Mô hình:** `SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced", probability=True, random_state=42)`
   - **Bộ tiền xử lý:** `StandardScaler` (chỉ fit trên `train` của ảnh gốc)
   - **Nhóm đặc trưng:** `ghep` (152 chiều = Histogram 64 + GLCM 60 + LBP 28)
   - **Kịch bản ảnh đầu vào:** Ảnh X-quang gốc nguyên bản `299×299` (`orig_to_orig`)
2. **Quy định Cổng H2 & H6 cho Tuần 10 (`10_final_test_eval.ipynb`):**
   - Tập `test` (3.176 ảnh) tiếp tục được **khóa chặt** cho đến khi nhóm bắt đầu Sprint 5 tuần 10 (`S5-04`).
   - Đánh giá tập test **chỉ được chạy đúng MỘT lần duy nhất**, không tinh chỉnh hay thử nghiệm bất kỳ phương án nào khác sau khi mở điểm.
   - Báo cáo cuối kỳ (`S6-01`) bắt buộc dành một phần trọng tâm phân tích sâu hiện tượng Shortcut Learning và cảnh báo y khoa về sự nguy hiểm khi triển khai lâm sàng các mô hình học máy trên bộ dữ liệu tổng hợp này.
