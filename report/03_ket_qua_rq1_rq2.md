# CHƯƠNG 3. KẾT QUẢ RQ1 VÀ RQ2 TRÊN TẬP VALIDATION

## 3.1. RQ1: bốn nhóm đặc trưng trên Random Forest

RQ1 hỏi nhóm đặc trưng nào cho macro-F1 cao nhất khi bộ phân loại được cố định trước. Bộ phân loại đó là Random Forest với 500 cây và `class_weight = balanced_subsample`, chạy trên ba seed 42, 43 và 44. Bốn nhóm đặc trưng được so sánh trên cùng một tập validation 3.174 ảnh; histogram giữ vai trò mốc tham chiếu.

**Bảng 3.1: Macro-F1 bốn nhóm đặc trưng trên validation, trung bình 3 seed**

| Nhóm đặc trưng | Số chiều | Macro-F1 (TB ± SD) | 95% CI | Recall lớp Viral Pneumonia |
| :--- | ---: | ---: | :--- | ---: |
| Ghép | 152 | 0,8599 ± 0,0030 | [0,8452; 0,8732] | 0,7734 |
| GLCM kết hợp LBP | 88 | 0,8156 ± 0,0023 | [0,7986; 0,8309] | 0,7241 |
| Histogram | 64 | 0,7829 ± 0,0013 | [0,7643; 0,8002] | 0,6207 |
| HOG | 10.404 | 0,7625 ± 0,0038 | [0,7459; 0,7787] | 0,7849 |

*(SD là độ lệch chuẩn giữa ba seed. Khoảng tin cậy 95% tính bằng bootstrap 2.000 lần: trong mỗi lần lấy mẫu, một tập vị trí ảnh duy nhất được dùng cho cả ba seed, macro-F1 tính cho từng seed rồi lấy trung bình, và khoảng tin cậy lấy phân vị 2,5% cùng 97,5% của 2.000 giá trị đó.)*

Cả 12 lần chạy, gồm bốn nhóm nhân ba seed, đều vượt hai mốc nền: mốc tầm thường B0 = 0,1627 và mốc A0 = 0,2397. Như vậy không nhóm đặc trưng nào chỉ dừng ở mức của một mô hình đọc độ sáng và định dạng tệp.

Thứ tự xếp hạng không đi theo số chiều: nhóm 152 chiều đứng đầu, nhóm 64 chiều đứng thứ ba và nhóm 10.404 chiều đứng cuối. Nhóm ghép cao hơn histogram 0,0770 điểm macro-F1 nhưng tốn khoảng 42 lần thời gian trích đặc trưng mỗi ảnh (0,0568 so với 0,0013 giây CPU).

Thứ hạng này được đo với một bộ phân loại duy nhất. Với bộ phân loại khác, thứ tự có thể thay đổi; đề tài không đo phép đó. HOG với 10.404 chiều trên Random Forest là trường hợp đáng chú ý, vì mỗi cây của bộ này chỉ xem một tập con ngẫu nhiên của chiều.

Cột recall của lớp nhỏ nhất cho thấy hai nhóm có điểm mạnh khác nhau. Histogram đứng thứ ba về macro-F1 nhưng chỉ đạt 0,6207 recall trên lớp Viral Pneumonia; HOG đứng cuối về macro-F1 nhưng đứng đầu cột này với 0,7849. Histogram bỏ qua vị trí điểm ảnh và chỉ giữ phân bố mức xám, nên có thể ít thông tin để tách lớp nhỏ nhất. Hiện chưa có dữ liệu để giải thích sự đổi vai này.

## 3.2. Kiểm định thống kê và quyết định chọn nhóm ghép

Chênh lệch giữa các nhóm được kiểm bằng bootstrap ghép cặp 2.000 lần trên chính 3.174 ảnh validation, với histogram làm mốc. Quy tắc ra quyết định đã chốt trước khi chạy: một nhóm được nhận nếu chênh lệch macro-F1 so với histogram đạt ít nhất 0,005 và khoảng tin cậy 95% của chênh lệch đó không chứa 0.

**Bảng 3.2: Phép so sánh của RQ1 với histogram làm mốc**

| Ứng viên | Chênh lệch macro-F1 | 95% CI của chênh lệch | Khoảng chứa 0 | Vượt ngưỡng 0,005 |
| :--- | ---: | :--- | :---: | :---: |
| Ghép | +0,0770 | [+0,0611; +0,0925] | Không | Có |
| GLCM kết hợp LBP | +0,0328 | [+0,0131; +0,0513] | Không | Có |
| HOG | −0,0203 | [−0,0419; +0,0014] | Có | Không |

Nhóm ghép vượt ngưỡng quy tắc gấp 15,4 lần và khoảng tin cậy nằm hoàn toàn ở phía dương. Hai nhóm ghép và GLCM kết hợp LBP thỏa cả hai điều kiện; nhóm ghép có macro-F1 cao hơn nên được chọn để mang sang RQ2. HOG không đạt trên cả hai tiêu chí.

Phép so sánh giữa nhóm ghép và nhóm GLCM kết hợp LBP, chênh 0,0443, không nằm trong giao thức đã chốt vì mỗi câu hỏi chỉ có một phép so sánh chính. Chênh lệch đó vì thế không được kiểm định.

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

Phép so sánh chính của RQ2 đối chiếu ứng viên tốt nhất với mốc Random Forest bằng bootstrap ghép cặp 2.000 lần. SVM vượt mốc 0,0442 điểm, với khoảng tin cậy 95% là [+0,0320; +0,0580], không chứa 0. Trong bốn bộ còn lại, Gradient Boosting cao hơn mốc với chênh 0,0286 và khoảng tin cậy [+0,0183; +0,0399] không chứa 0; Logistic Regression, k-NN và Decision Tree đều thấp hơn mốc, từ −0,0213 đến −0,1312, và cả ba khoảng tin cậy đều không chứa 0. Vì vậy SVM RBF được chọn làm mô hình của đề tài.

Hai điểm cần chú ý khi đọc con số 0,8582 của Random Forest ở bảng trên. Random Forest ở RQ2 dùng 300 cây do kiểm định chéo chọn, khác cấu hình 500 cây cố định của RQ1, nên điểm này thấp hơn 0,8599 ở Bảng 3.1. Random Forest cũng chạy trên ba seed, còn SVM chạy một seed vì bộ này tất định; điểm của SVM vì thế không có độ lệch chuẩn theo seed. Trong mỗi lần lấy mẫu bootstrap, cùng một tập vị trí ảnh được dùng cho cả hai bộ đang so, nên phép so sánh là ghép cặp.

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

F1 các lớp trải từ 0,8415 của Lung_Opacity đến 0,9475 của COVID. Lớp nhỏ nhất, Viral Pneumonia với 203 ảnh, đạt F1 cao thứ hai; lớp đông thứ hai với 903 ảnh đạt thấp nhất.

**Bảng 3.5: Ma trận nhầm lẫn của SVM trên validation**

| Nhãn thực ↓ / Dự đoán → | COVID | Lung_Opacity | Normal | Viral Pneumonia |
| :--- | ---: | ---: | ---: | ---: |
| COVID (537) | 514 | 8 | 13 | 2 |
| Lung_Opacity (903) | 12 | 767 | 124 | 0 |
| Normal (1.531) | 18 | 144 | 1.353 | 16 |
| Viral Pneumonia (203) | 4 | 1 | 7 | 191 |

![Tỷ lệ lỗi theo hàng của ma trận nhầm lẫn](../figures/03_ma_tran_nham_lon_svm_val.png)

**Hình 3.1: Tỷ lệ lỗi theo hàng của ma trận nhầm lẫn của SVM trên 3.174 ảnh validation**

Mỗi hàng của Hình 3.1 là một nhãn thực, và các ô cùng hàng cộng lại gần bằng 100%; chênh lệch vài phần mười do làm tròn một chữ số thập phân. Ô trên đường chéo là recall của lớp đó, và các ô mép hiện được tỷ lệ nhỏ như 0,4% thay vì bị làm tròn thành 0%. Số đếm gốc của từng ô nằm ở Bảng 3.5.

Lỗi không dàn đều, và không đều theo số ảnh của lớp. Cặp Normal và Lung_Opacity chiếm 268 trong 349 lỗi, tức 76,79%: gồm 144 ảnh Normal bị đoán thành Lung_Opacity và 124 ảnh Lung_Opacity bị đoán thành Normal. Các lỗi còn lại chỉ còn 81. Hai lớp này lấy ảnh từ cùng cuộc thi RSNA, với toàn bộ 6.012 ảnh Lung_Opacity và 8.851 trong số 10.192 ảnh Normal; cặp này cũng gồm hai lớp đông nhất nên số lỗi thô có thể chỉ phản ánh quy mô. Vì vậy Bảng 3.6 dẫn tỷ lệ lỗi trên số ảnh của hai lớp thay vì số đếm.

**Bảng 3.6: Tỷ lệ lỗi của từng cặp lớp trên tập validation**

| Cặp lớp | Số lỗi | Tổng ảnh hai lớp | Tỷ lệ |
| :--- | ---: | ---: | ---: |
| Normal – Lung_Opacity | 268 | 2.434 | 11,0% |
| COVID – Normal | 31 | 2.068 | 1,50% |
| COVID – Lung_Opacity | 20 | 1.440 | 1,39% |
| Viral Pneumonia – Normal | 23 | 1.734 | 1,33% |
| COVID – Viral Pneumonia | 6 | 740 | 0,81% |
| Viral Pneumonia – Lung_Opacity | 1 | 1.106 | 0,09% |

Cặp Normal – Lung_Opacity cao gấp khoảng 7 lần cặp đứng thứ hai, nên sự chênh lệch này không do quy mô lớp. Hai lớp cùng nguồn RSNA, và mô hình phân biệt tốt hơn nhiều giữa các cặp khác nguồn so với cặp cùng nguồn. Kiểu phân bố này phù hợp với giả thuyết mô hình dùng được đặc điểm của nguồn ảnh, đồng thời chưa loại trừ khả năng hai lớp cùng nguồn có hình ảnh gần nhau hơn.

Một kiểu lỗi thứ hai nằm ở lớp Viral Pneumonia. Lớp này có 12 lỗi trên nhãn thật và xuất hiện trong 18 lỗi dương tính giả. Phần lớn lỗi của lớp rơi vào nhãn Normal: 7 ảnh bị đoán thành Normal và 16 ảnh Normal bị đoán thành Viral Pneumonia, cả hai chiều cộng 23 trường hợp. Nhưng nhìn trên Bảng 3.6 thì cặp Viral Pneumonia – Normal có tỷ lệ 1,33%, thấp hơn cặp COVID – Normal với 1,50%, nên việc lỗi dồn về nhãn Normal có thể chỉ do Normal là lớp đông nhất. Toàn bộ 1.345 ảnh Viral Pneumonia đến từ một bộ Kaggle, nhưng chỉ 1.341 trong số 10.192 ảnh Normal đến từ bộ đó, tức 13% lớp Normal. Con số 23 vì thế chưa cho thấy điều gì đặc biệt về nguồn ảnh.

Dấu hiệu rõ nhất của nguồn, tức 140 ảnh lưu ở hệ màu RGB, cũng không giải thích được lỗi của lớp. Trong số 12 ảnh Viral Pneumonia bị đoán sai thì 2 ảnh là RGB, tức 16,7%, trong khi RGB chiếm 10,3% cả lớp; tính riêng, nhóm 21 ảnh RGB trong validation đạt recall 90,5% so với 94,5% của 182 ảnh còn lại. Nếu mô hình bám vào đặc điểm xuất tệp đi kèm định dạng RGB thì nhóm này phải được phân loại tốt hơn, nhưng thực tế nó thấp hơn một chút. Cả hai con số đều rút từ 21 ảnh nên chưa đủ để kết luận phương hướng nào.

Bốn điểm cần thêm khi đọc kết quả của mục này. Pipeline ép mọi ảnh về ảnh xám trước khi trích đặc trưng, nên mô hình không hề thấy hệ màu của tệp; tác động của RGB nếu có chỉ đến gián tiếp, qua các đặc điểm đi kèm với cách xuất tệp. Về phân bố lỗi, 240 trong 349 lỗi (68,8%) bị cả ba mô hình SVM, Gradient Boosting và Random Forest đoán sai, nên phần lớn lỗi đến từ đặc trưng hoặc từ nhãn chứ không riêng một bộ phân loại. Về độ tin cậy, 138 trong 349 lỗi (39,5%) được mô hình đoán với xác suất từ 0,80 trở lên, tức mô hình tự tin trên các ca sai. Cuối cùng, điểm 0,9024 là cao nhất trong sáu bộ trên chính tập validation, nên nó chịu thiên lệch do chọn lọc và có thể cao hơn mức thực; Chương 5 kiểm lại trên tập test.

Các điểm trên đều nằm ngoài phạm vi kiểm định của chương này và được xét lại ở Chương 6.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 3.1:** `results/report_rq1/r1_summary.csv` (macro-F1 trung bình, SD, khoảng tin cậy, recall từng lớp), `results/report_rq1/r1_per_seed.csv` (điểm từng seed) và `results/rq1_feature_selection_record.md` mục 2 (cấu hình Random Forest 500 cây, 12 lần chạy, giây CPU mỗi ảnh). Cách bootstrap kết hợp ba seed mô tả ở mục 2.9 của Chương 2; cách cấu hình RQ1 và RQ2 khác nhau nêu ở mục 2.8 của Chương 2.
- **Nguồn mục 3.2:** `results/report_rq1/r1_bootstrap_vs_reference.csv` (ba phép so sánh với mốc histogram, 2.000 lần, `rng_seed = 42`) và `results/rq1_feature_selection_record.md` mục 3–4 (quy tắc chọn nhóm đặc trưng). Hệ số 15,4 là 0,0770/0,005 tính trong báo cáo, không có trong tệp nguồn.
- **Nguồn mục 3.3:** `results/report_rq2/r1_summary.csv` (sáu bộ, số seed, khoảng tin cậy) và `results/report_rq2/r1_bootstrap_vs_reference.csv` (năm phép so sánh với mốc Random Forest). Cấu hình SVM lấy từ `results/rq2_ghep_svm_s42/metrics.json`.
- **Nguồn mục 3.3 (bổ sung):** chênh lệch Gradient Boosting so với mốc `rf` là +0,0286 với CI [+0,0183; +0,0399], lấy từ `results/report_rq2/r1_bootstrap_vs_reference.csv`. Chênh lệch giữa nhóm ghép và nhóm GLCM kết hợp LBP ở mục 3.2 là 0,859895 − 0,815637 = 0,0443, tính từ `r1_summary.csv`; không có phép kiểm định cho con số này.
- **Số ảnh RGB trong lỗi Viral Pneumonia:** đối chiếu `image_id` trong `results/rq2_ghep_svm_s42/preds_val.csv` với cột `color_mode` của `splits/manifest.csv`: 2 trong 12 ảnh bị đoán sai là RGB (16,7%), còn RGB chiếm 10,3% lớp; trong validation có 21 ảnh RGB trên tổng 203 ảnh lớp, đạt recall 90,5% so với 94,5% của 182 ảnh còn lại. Các con số rút từ 21 ảnh nên không kết luận được phương hướng.
- **Phép tách ảnh Normal theo nguồn chưa làm được.** Cột `URL` của `Normal.metadata.xlsx` phân biệt được 8.851 ảnh RSNA và 1.341 ảnh của bộ Kaggle, và chính tệp đó đã được dùng để lập bảng nguồn ở mục 2.1 (`docs/dataset_provenance.md` mục 2.1–2.2). Tệp không nằm trong repo nên không kiểm chứng lại được, và máy soạn thảo hiện không có thông tin xác thực Kaggle để tải lại; việc này có thể làm nếu tải tệp metadata về. Đây là phép kiểm rẻ nhất cho giả thuyết cùng nguồn, nên nên làm nếu tải được tệp đó.
- **Nguồn mục 3.4:** `results/rq2_ghep_svm_s42/metrics.json` (accuracy, balanced accuracy, macro-F1, chỉ số từng lớp, ma trận nhầm lẫn), `results/rq2_ghep_svm_s42/preds_val.csv` (nhãn thực, nhãn dự đoán và bốn cột xác suất của từng ảnh; độ tin cậy 0,80 lấy từ cột nhãn dự đoán) và `results/error_analysis/error_analysis_summary.md` mục 1–2 (349 lỗi, 240 lỗi đồng thuận, 138 lỗi có `proba_pred` từ 0,80 trở lên). Bảng 3.6 tính từ `preds_val.csv`, mẫu số là tổng ảnh hai lớp trong validation.
- **Số 23 trong 30 lỗi của Viral Pneumonia:** 7 ảnh Viral Pneumonia bị đoán thành Normal (dòng cuối của Bảng 3.5) cộng 16 ảnh Normal bị đoán thành Viral Pneumonia (cột cuối). Con số 1.341 ảnh Normal cùng nguồn lấy từ `docs/dataset_provenance.md` mục 2.1 và đã dùng ở mục 2.1.
- **Hình 3.1:** sinh bằng `python -m scripts.report_figures` từ `confusion_matrix` trong `results/rq2_ghep_svm_s42/metrics.json`; mỗi hàng chia cho tổng hàng nên đường chéo là recall, khớp với cột recall ở Bảng 3.4 (kiểm thử `tests/test_report_figures.py` giữ điều này). Hình chỉ hiện tỷ lệ với một chữ số thập phân, số đếm gốc nằm ở Bảng 3.5.
- **Không dùng tệp test:** `results/final_test/confusion_matrix_test.png` và mọi số liệu trong `results/final_test/` thuộc Chương 5.
- **Các khẳng định nhân quả của tệp phân tích lỗi** (độ sáng, viền khung chụp, đặc điểm máy chụp) không được đưa vào báo cáo vì không kiểm chứng được từ ảnh; riêng nhận định về phụ thuộc nguồn ảnh được nêu lại dưới dạng khả năng và giao cho RQ3.
- **Chưa đưa vào chương:** thời gian huấn luyện của từng bộ, chỉ số theo từng seed riêng lẻ, và phân tích lỗi theo mức độ tin cậy chi tiết hơn.
