# CHƯƠNG 3. KẾT QUẢ RQ1 VÀ RQ2 TRÊN TẬP VALIDATION

## 3.1. RQ1: bốn nhóm đặc trưng trên Random Forest

Câu hỏi RQ1 hỏi nhóm đặc trưng nào cho macro-F1 cao nhất khi bộ phân loại được cố định trước. Bộ phân loại đó là Random Forest với 500 cây và `class_weight = balanced_subsample`, chạy trên ba seed 42, 43 và 44. Bốn nhóm đặc trưng được so sánh trên cùng một tập validation 3.174 ảnh; histogram giữ vai trò mốc tham chiếu.

**Bảng 3.1: Macro-F1 bốn nhóm đặc trưng trên validation, trung bình 3 seed**

| Nhóm đặc trưng | Số chiều | Macro-F1 (TB ± SD) | 95% CI | Recall lớp Viral Pneumonia |
| :--- | ---: | ---: | :--- | ---: |
| Ghép | 152 | 0,8599 ± 0,0030 | [0,8452; 0,8732] | 0,7734 |
| GLCM kết hợp LBP | 88 | 0,8156 ± 0,0023 | [0,7986; 0,8309] | 0,7241 |
| Histogram | 64 | 0,7829 ± 0,0013 | [0,7643; 0,8002] | 0,6207 |
| HOG | 10.404 | 0,7625 ± 0,0038 | [0,7459; 0,7787] | 0,7849 |

Cả 12 lần chạy, gồm bốn nhóm nhân ba seed, đều vượt hai mốc nền: mốc tầm thường B0 = 0,1627 và mốc A0 = 0,2397. Như vậy không nhóm đặc trưng nào chỉ dừng ở mức của một mô hình đọc độ sáng và định dạng tệp.

Thứ tự xếp hạng không đi theo số chiều: nhóm 152 chiều đứng đầu, nhóm 64 chiều đứng thứ ba và nhóm 10.404 chiều đứng cuối. Chi phí tính toán cũng chênh lệch: histogram tốn 0,0013 giây CPU cho mỗi ảnh, nhóm ghép tốn 0,0568 giây, tức đắt hơn khoảng 42 lần.

Một chi tiết đáng chú ý nằm ở cột recall của lớp nhỏ nhất. Histogram chỉ đạt 0,6207 trên lớp Viral Pneumonia, trong khi ba nhóm kia đạt từ 0,7241 đến 0,7849. Histogram bỏ qua vị trí điểm ảnh và chỉ giữ phân bố mức xám; ba nhóm còn lại dùng thêm kết cấu hoặc hướng biên.

## 3.2. Kiểm định thống kê và quyết định chọn nhóm ghép

Chênh lệch giữa các nhóm được kiểm bằng bootstrap ghép cặp 2.000 lần trên chính 3.174 ảnh validation, với histogram làm mốc. Quy tắc ra quyết định đã chốt trước khi chạy: một nhóm được nhận nếu chênh lệch macro-F1 so với histogram đạt ít nhất 0,005 và khoảng tin cậy 95% của chênh lệch đó không chứa 0.

**Bảng 3.2: Phép so sánh của RQ1 với histogram làm mốc**

| Ứng viên | Chênh lệch macro-F1 | 95% CI của chênh lệch | Khoảng chứa 0 | Vượt ngưỡng 0,005 |
| :--- | ---: | :--- | :---: | :---: |
| Ghép | +0,0770 | [+0,0611; +0,0925] | Không | Có |
| GLCM kết hợp LBP | +0,0328 | [+0,0131; +0,0513] | Không | Có |
| HOG | −0,0203 | [−0,0419; +0,0014] | Có | Không |

Nhóm ghép vượt ngưỡng quy tắc gấp 15,4 lần và khoảng tin cậy nằm hoàn toàn ở phía dương. Chỉ nhóm ghép thỏa đồng thời hai điều kiện, nên nó được chọn để mang sang RQ2. Nhóm GLCM kết hợp LBP đạt cả hai điều kiện nhưng không phải ứng viên tốt nhất; HOG không đạt trên cả hai tiêu chí.

## 3.3. RQ2: sáu bộ phân loại trên nhóm ghép

Sáu bộ phân loại được so sánh trên nhóm đặc trưng ghép 152 chiều, cùng tập validation 3.174 ảnh. Siêu tham số của từng bộ được chọn bằng kiểm định chéo 5 fold trên tập train như mô tả ở mục 2.8. Random Forest giữ vai trò mốc tham chiếu.

**Bảng 3.3: Macro-F1 sáu bộ phân loại trên validation**

| Bộ phân loại | Macro-F1 (TB ± SD) | Số seed | 95% CI |
| :--- | ---: | ---: | :--- |
| SVM | 0,9024 | 1 | [0,8909; 0,9129] |
| Gradient Boosting | 0,8868 ± 0,0030 | 3 | [0,8749; 0,8976] |
| Random Forest | 0,8582 ± 0,0033 | 3 | [0,8432; 0,8715] |
| Logistic Regression | 0,8370 | 1 | [0,8221; 0,8505] |
| k-NN | 0,8242 | 1 | [0,8074; 0,8396] |
| Decision Tree | 0,7271 ± 0,0017 | 3 | [0,7090; 0,7449] |

Cả sáu bộ đều vượt hai mốc nền B0 = 0,1627 và A0 = 0,2397. SVM đạt macro-F1 cao nhất và cũng là bộ duy nhất vượt mốc 0,90.

Phép so sánh chính của RQ2 đối chiếu ứng viên tốt nhất với mốc Random Forest bằng bootstrap ghép cặp 2.000 lần. SVM vượt mốc 0,0442 điểm, với khoảng tin cậy 95% là [+0,0320; +0,0580], không chứa 0. Năm bộ còn lại đều có chênh lệch âm so với mốc, từ −0,0213 của Logistic Regression đến −0,1312 của Decision Tree, và cả năm khoảng tin cậy đều không chứa 0. Vì vậy SVM RBF được chọn làm mô hình của đề tài.

Phép so sánh trực tiếp giữa SVM và Gradient Boosting, hai bộ đứng đầu, không nằm trong giao thức đã chốt vì mỗi câu hỏi chỉ có một phép so sánh chính. Khoảng cách giữa hai bộ này vì vậy không được kết luận bằng kiểm định thống kê.

## 3.4. Đánh giá SVM RBF trên validation

Mô hình được đánh giá ở mục này là SVM với kernel RBF, C = 10, gamma = scale và `class_weight = balanced`, đặt sau bước chuẩn hóa, trên nhóm đặc trưng ghép 152 chiều. Đây là cấu hình vừa được chọn ở mục 3.3.

Trên 3.174 ảnh validation, mô hình đạt accuracy 89,00%, balanced accuracy 0,9078 và macro-F1 0,9024. Có 349 ảnh bị đoán sai, tức 11,00% tập đánh giá.

**Bảng 3.4: Precision, Recall và F1 theo lớp của SVM trên validation**

| Lớp | Số ảnh | Precision | Recall | F1 |
| :--- | ---: | ---: | ---: | ---: |
| COVID | 537 | 0,9380 | 0,9572 | 0,9475 |
| Lung_Opacity | 903 | 0,8337 | 0,8494 | 0,8415 |
| Normal | 1.531 | 0,9038 | 0,8837 | 0,8937 |
| Viral Pneumonia | 203 | 0,9139 | 0,9409 | 0,9272 |

Cả bốn lớp đều đạt F1 trên 0,84. Lớp nhỏ nhất, Viral Pneumonia với 203 ảnh, đạt F1 0,9272; lớp yếu nhất là Lung_Opacity với F1 0,8415. Mô hình dùng cân bằng lớp nên khoảng cách giữa bốn lớp hẹp.

**Bảng 3.5: Ma trận nhầm lẫn của SVM trên validation**

| Nhãn thực ↓ / Dự đoán → | COVID | Lung_Opacity | Normal | Viral Pneumonia |
| :--- | ---: | ---: | ---: | ---: |
| COVID (537) | 514 | 8 | 13 | 2 |
| Lung_Opacity (903) | 12 | 767 | 124 | 0 |
| Normal (1.531) | 18 | 144 | 1.353 | 16 |
| Viral Pneumonia (203) | 4 | 1 | 7 | 191 |

Lỗi không dàn đều. Cặp Normal và Lung_Opacity chiếm 268 trong 349 lỗi, tức 76,79%: gồm 144 ảnh Normal bị đoán thành Lung_Opacity và 124 ảnh Lung_Opacity bị đoán thành Normal. Cặp còn lại chỉ chiếm 81 lỗi. Cả hai lớp đều lấy ảnh từ cuộc thi RSNA, với toàn bộ 6.012 ảnh Lung_Opacity và 8.851 trong số 10.192 ảnh Normal; bảng này không cho biết tại sao lỗi tập trung ở cặp đó.

Một kiểu lỗi thứ hai nằm ở lớp Viral Pneumonia. Lớp này có 30 lỗi, trong đó 23 lỗi (76,7%) xảy ra với nhãn Normal, cả hai chiều. Toàn bộ 1.345 ảnh Viral Pneumonia và 1.341 trong số 10.192 ảnh Normal đến từ cùng một bộ dữ liệu Kaggle (mục 2.1). Mô hình có thể đang bám vào đặc điểm của nguồn ảnh đó thay vì tổn thương phổi. Đây mới là quan sát trên tập validation; RQ3 đo mức phụ thuộc của mô hình vào vùng ngoài phổi ở Chương 4, và kết quả đó mới cho biết khả năng này có thật hay không.

Hai điểm cần thêm khi đọc số lỗi. Thứ nhất, 240 trong 349 lỗi (68,8%) bị cả ba mô hình SVM, Gradient Boosting và Random Forest đoán sai, nên phần lớn lỗi đến từ đặc trưng hoặc từ nhãn chứ không riêng một bộ phân loại. Thứ hai, 138 trong 349 lỗi (39,5%) được mô hình đoán với độ tin cậy từ 0,80 trở lên, tức mô hình tự tin trên các ca sai. Cả hai điểm đều nằm ngoài phạm vi kiểm định của chương này và được xét lại ở Chương 6.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 3.1:** `results/report_rq1/r1_summary.csv` (macro-F1 trung bình, SD, khoảng tin cậy, recall từng lớp) và `results/rq1_feature_selection_record.md` mục 2 (cấu hình Random Forest 500 cây, 12 lần chạy, giây CPU mỗi ảnh). Bộ phân loại RQ1 dùng `n_estimators = 500` theo mục 2.2 của Chương 2.
- **Nguồn mục 3.2:** `results/report_rq1/r1_bootstrap_vs_reference.csv` (ba phép so sánh với mốc histogram, 2.000 lần, `rng_seed = 42`) và `results/rq1_feature_selection_record.md` mục 3–4 (quy tắc chọn nhóm đặc trưng). Hệ số 15,4 là 0,0770/0,005 tính trong báo cáo, không có trong tệp nguồn.
- **Nguồn mục 3.3:** `results/report_rq2/r1_summary.csv` (sáu bộ, số seed, khoảng tin cậy) và `results/report_rq2/r1_bootstrap_vs_reference.csv` (năm phép so sánh với mốc Random Forest). Cấu hình SVM lấy từ `results/rq2_ghep_svm_s42/metrics.json`.
- **Nguồn mục 3.4:** `results/rq2_ghep_svm_s42/metrics.json` (accuracy, balanced accuracy, macro-F1, chỉ số từng lớp, ma trận nhầm lẫn) và `results/error_analysis/error_analysis_summary.md` mục 1–2 (349 lỗi, 240 lỗi đồng thuận, 138 lỗi có `proba_pred` từ 0,80 trở lên).
- **Số 23 trong 30 lỗi của Viral Pneumonia:** 7 ảnh Viral Pneumonia bị đoán thành Normal (dòng cuối của Bảng 3.5) cộng 16 ảnh Normal bị đoán thành Viral Pneumonia (cột cuối). Con số 1.341 ảnh Normal cùng nguồn lấy từ `docs/dataset_provenance.md` mục 2.1 và đã dùng ở mục 2.1.
- **Không dùng tệp test:** `results/final_test/confusion_matrix_test.png` và mọi số liệu trong `results/final_test/` thuộc Chương 5. Repo không có ma trận nhầm lẫn dạng hình cho validation, nên Bảng 3.5 dùng số đếm từ JSON.
- **Các khẳng định nhân quả của tệp phân tích lỗi** (độ sáng, viền khung chụp, đặc điểm máy chụp) không được đưa vào báo cáo vì không kiểm chứng được từ ảnh; riêng nhận định về phụ thuộc nguồn ảnh được nêu lại dưới dạng khả năng và giao cho RQ3.
- **Chưa đưa vào chương:** thời gian huấn luyện của từng bộ, chỉ số theo từng seed riêng lẻ, và phân tích lỗi theo mức độ tin cậy chi tiết hơn.
