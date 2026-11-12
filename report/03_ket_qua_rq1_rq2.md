# CHƯƠNG 3. KẾT QUẢ RQ1 VÀ RQ2 TRÊN TẬP VALIDATION

## 3.1. RQ1: bốn nhóm đặc trưng trên Random Forest

RQ1 so sánh bốn nhóm đặc trưng khi bộ phân loại được giữ cố định. Bộ phân loại chốt trước là Random Forest 500 cây, trọng số lớp cân bằng theo mẫu con (mục 2.8), chạy với ba seed 42, 43 và 44. Cả bốn nhóm đều được đánh giá trên cùng 3.174 ảnh validation, và histogram giữ vai trò mốc tham chiếu.

**Bảng 3.1: Macro-F1 bốn nhóm đặc trưng trên validation, trung bình 3 seed**

| Nhóm đặc trưng | Số chiều | Macro-F1 (TB ± SD) | 95% CI | Recall lớp Viral Pneumonia |
| :--- | ---: | ---: | :--- | ---: |
| Ghép (histogram + GLCM + LBP) | 152 | 0,8599 ± 0,0030 | [0,8452; 0,8732] | 0,7734 |
| GLCM kết hợp LBP | 88 | 0,8156 ± 0,0023 | [0,7986; 0,8309] | 0,7241 |
| Histogram | 64 | 0,7829 ± 0,0013 | [0,7643; 0,8002] | 0,6207 |
| HOG | 10.404 | 0,7625 ± 0,0038 | [0,7459; 0,7787] | 0,7849 |

*(SD là độ lệch chuẩn giữa ba seed, tính theo mẫu (n − 1). Khoảng tin cậy 95% tính bằng bootstrap 2.000 lần: trong mỗi lần lấy mẫu, một tập vị trí ảnh duy nhất được dùng cho cả ba seed, macro-F1 tính cho từng seed rồi lấy trung bình, và khoảng tin cậy lấy phân vị 2,5% cùng 97,5% của 2.000 giá trị đó.)*

Cả 12 lần chạy, tức bốn nhóm nhân ba seed, đều vượt hai mốc nền B0 = 0,1627 và A0 = 0,2397. Vì vậy không nhóm đặc trưng nào chỉ ngang một mô hình đọc độ sáng và định dạng tệp.

Thứ hạng macro-F1 gần như đi theo số chiều: 152, 88 rồi 64 chiều, riêng HOG với 10.404 chiều lại đứng cuối. Nhóm ghép hơn histogram 0,0770 điểm macro-F1, đổi lại thời gian trích đặc trưng gấp 42,5 lần (0,056773 so với 0,001337 giây CPU cho mỗi ảnh, tính từ giá trị chưa làm tròn). Nhóm ghép đã chứa histogram, nên khoảng chênh 0,0770 gắn với việc bổ sung GLCM và LBP.

Một cách giải thích cho vị trí cuối của HOG là mỗi lần chia nút, Random Forest chỉ xét một phần nhỏ trong 10.404 chiều. Đề tài không kiểm tra điều này. Thứ hạng cũng mới chỉ được đo với một bộ phân loại; với bộ khác, thứ tự có thể khác, và đề tài không đo phép đó.

Nếu nhìn riêng recall của lớp nhỏ nhất thì thứ hạng đảo khác hẳn. Histogram đứng thứ ba về macro-F1 nhưng có recall thấp nhất ở lớp Viral Pneumonia (0,6207), còn HOG đứng cuối lại có recall cao nhất (0,7849). Bảng chưa nêu precision của lớp này nên chưa thể nói HOG làm tốt hơn ở đây, và đề tài chưa có số liệu để giải thích chênh lệch đó.

## 3.2. Kiểm định thống kê và quyết định chọn nhóm ghép

Chênh lệch giữa các nhóm được kiểm bằng bootstrap ghép cặp 2.000 lần trên chính 3.174 ảnh validation, lấy histogram làm mốc. Quy tắc quyết định được chốt trước khi chạy: một nhóm được nhận khi macro-F1 hơn histogram ít nhất 0,005 và khoảng tin cậy 95% của chênh lệch không chứa 0.

**Bảng 3.2: Phép so sánh của RQ1 với histogram làm mốc**

| Ứng viên | Chênh lệch macro-F1 | 95% CI của chênh lệch | Khoảng chứa 0 | Vượt ngưỡng 0,005 |
| :--- | ---: | :--- | :---: | :---: |
| Ghép (histogram + GLCM + LBP) | +0,0770 | [+0,0611; +0,0925] | Không | Có |
| GLCM kết hợp LBP | +0,0328 | [+0,0131; +0,0513] | Không | Có |
| HOG | −0,0203 | [−0,0419; +0,0014] | Có | Không |

Nhóm ghép hơn histogram 0,0770 (Bảng 3.2), gấp 15,4 lần ngưỡng 0,005, và toàn bộ khoảng tin cậy nằm ở phía dương. GLCM kết hợp LBP cũng đạt cả hai điều kiện, nhưng nhóm ghép có macro-F1 cao hơn nên được đưa sang RQ2. HOG không đạt điều kiện nào: chênh lệch âm và khoảng tin cậy chứa 0.

Giao thức chỉ so từng ứng viên với histogram, nên phép so giữa nhóm ghép và GLCM kết hợp LBP (chênh 0,0443) nằm ngoài giao thức đã chốt và không được kiểm định.

## 3.3. RQ2: sáu bộ phân loại trên nhóm ghép

Sáu bộ phân loại được so trên nhóm ghép 152 chiều và cùng tập validation 3.174 ảnh. Siêu tham số của từng bộ chọn bằng kiểm định chéo 5 fold trên tập train như mô tả ở mục 2.8, và Random Forest làm mốc tham chiếu.

**Bảng 3.3: Macro-F1 sáu bộ phân loại trên validation**

| Bộ phân loại | Macro-F1 (TB) | SD | Số seed | 95% CI |
| :--- | ---: | ---: | ---: | :--- |
| SVM | 0,9024 | — | 1 | [0,8909; 0,9129] |
| Gradient Boosting | 0,8868 | 0,0030 | 3 | [0,8749; 0,8976] |
| Random Forest | 0,8582 | 0,0033 | 3 | [0,8432; 0,8716] |
| Logistic Regression | 0,8370 | — | 1 | [0,8221; 0,8505] |
| k-NN | 0,8242 | — | 1 | [0,8075; 0,8397] |
| Decision Tree | 0,7271 | 0,0017 | 3 | [0,7090; 0,7449] |

Cả sáu bộ trong Bảng 3.3 đều vượt B0 = 0,1627 và A0 = 0,2397. SVM đứng đầu và là bộ duy nhất vượt mức 0,90.

Phép so chính của RQ2 đặt bộ tốt nhất cạnh mốc Random Forest, bằng bootstrap ghép cặp 2.000 lần. SVM hơn mốc 0,0442, khoảng tin cậy 95% là [+0,0320; +0,0580] và không chứa 0. Gradient Boosting cũng hơn mốc 0,0286 với khoảng [+0,0183; +0,0399]. Ba bộ còn lại đều thấp hơn mốc, chênh từ −0,0213 đến −0,1312, và khoảng tin cậy của cả ba đều không chứa 0. Đề tài vì thế chọn SVM RBF làm mô hình chính.

Con số 0,8582 của Random Forest ở đây không đặt thẳng cạnh 0,8599 ở Bảng 3.1 được, vì cấu hình hai nơi khác nhau: RQ1 cố định 500 cây, còn RQ2 coi số cây là siêu tham số và kiểm định chéo chọn 300 cây. Hai điểm chỉ lệch 0,0017, nhỏ hơn độ lệch chuẩn giữa các seed của từng phép đo (0,0033 và 0,0030).

SVM chỉ chạy một seed vì nhãn dự đoán của bộ này không phụ thuộc seed, trong khi Random Forest chạy ba. Bốn cột xác suất của SVM thì có phụ thuộc seed, do nội suy Platt dùng kiểm định chéo nội bộ, nhưng mọi phép so macro-F1 trong chương đều dựa trên nhãn nên không chịu ảnh hưởng này. Trong mỗi lần lấy mẫu bootstrap, hai bộ đang so dùng chung một tập vị trí ảnh, nên phép so là ghép cặp.

Giao thức chỉ so từng bộ với mốc Random Forest. Do đó SVM và Gradient Boosting, hai bộ đứng đầu, không được so trực tiếp với nhau, và đề tài không đưa ra kết luận kiểm định nào về cặp này.

## 3.4. Đánh giá SVM RBF trên validation

Mô hình đánh giá ở mục này là cấu hình vừa được chọn ở mục 3.3: SVM kernel RBF với C = 10, gamma = scale và trọng số lớp cân bằng (mục 2.8), đặt sau bước chuẩn hóa, chạy trên nhóm đặc trưng ghép 152 chiều.

Trên 3.174 ảnh validation, mô hình đạt accuracy 89,00%, balanced accuracy 0,9078 và macro-F1 0,9024. Có 349 ảnh bị đoán sai, bằng 11,00% tập đánh giá.

**Bảng 3.4: Precision, Recall và F1 theo lớp của SVM trên validation**

| Lớp | Số ảnh | Precision | Recall | F1 |
| :--- | ---: | ---: | ---: | ---: |
| COVID | 537 | 0,9380 | 0,9572 | 0,9475 |
| Lung_Opacity | 903 | 0,8337 | 0,8494 | 0,8415 |
| Normal | 1.531 | 0,9038 | 0,8837 | 0,8937 |
| Viral Pneumonia | 203 | 0,9139 | 0,9409 | 0,9272 |

F1 của các lớp trong Bảng 3.4 dao động từ 0,8415 (Lung_Opacity) đến 0,9475 (COVID). Đáng chú ý là lớp nhỏ nhất, Viral Pneumonia với 203 ảnh, có F1 cao thứ hai, trong khi lớp đông thứ hai (903 ảnh) lại thấp nhất.

**Bảng 3.5: Ma trận nhầm lẫn của SVM trên validation**

| Nhãn thực ↓ / Dự đoán → | COVID | Lung_Opacity | Normal | Viral Pneumonia |
| :--- | ---: | ---: | ---: | ---: |
| COVID (537) | 514 | 8 | 13 | 2 |
| Lung_Opacity (903) | 12 | 767 | 124 | 0 |
| Normal (1.531) | 18 | 144 | 1.353 | 16 |
| Viral Pneumonia (203) | 4 | 1 | 7 | 191 |

![Ma trận nhầm lẫn của SVM chuẩn hóa theo hàng](../figures/03_ma_tran_nham_lon_svm_val.png)

**Hình 3.1: Ma trận nhầm lẫn của SVM chuẩn hóa theo hàng (nhãn thực), trên 3.174 ảnh validation**

Trong Hình 3.1, hàng là nhãn thực, cột là nhãn dự đoán, và mỗi hàng được chia cho số ảnh của lớp đó nên ô trên đường chéo chính là recall. Do làm tròn một chữ số thập phân, tổng một hàng có thể lệch tối đa 0,1 điểm phần trăm so với 100%; các ô nhỏ vẫn hiện tỷ lệ như 0,4% thay vì bị làm tròn thành 0%. Số đếm gốc của từng ô nằm ở Bảng 3.5.

Lỗi dồn về cặp Normal – Lung_Opacity: 268 trong 349 lỗi (76,79%), gồm 144 ảnh Normal bị đoán thành Lung_Opacity và 124 ảnh theo chiều ngược lại; 81 lỗi còn lại rải trên năm cặp khác. Hai lớp này đều lấy từ RSNA (toàn bộ 6.012 ảnh Lung_Opacity và 8.851 trong 10.192 ảnh Normal), đồng thời là hai lớp đông nhất, nên số lỗi thô có thể chỉ phản ánh quy mô. Bảng 3.6 vì vậy dùng tỷ lệ lỗi trên tổng số ảnh của hai lớp thay cho số đếm.

**Bảng 3.6: Tỷ lệ lỗi của từng cặp lớp trên tập validation**

| Cặp lớp | Số lỗi | Tổng ảnh hai lớp | Tỷ lệ |
| :--- | ---: | ---: | ---: |
| Normal – Lung_Opacity | 268 | 2.434 | 11,01% |
| COVID – Normal | 31 | 2.068 | 1,50% |
| COVID – Lung_Opacity | 20 | 1.440 | 1,39% |
| Viral Pneumonia – Normal | 23 | 1.734 | 1,33% |
| COVID – Viral Pneumonia | 6 | 740 | 0,81% |
| Viral Pneumonia – Lung_Opacity | 1 | 1.106 | 0,09% |

Tỷ lệ 11,01% của cặp Normal – Lung_Opacity gấp 7,3 lần cặp đứng thứ hai, nên mức chênh này không chỉ do hai lớp có nhiều ảnh. Tuy nhiên, hai lớp vừa cùng nguồn RSNA vừa là cặp khó tách về mặt lâm sàng, và kiểu lỗi trên phù hợp với cả hai cách giải thích: mô hình dựa vào đặc điểm của nguồn ảnh, hoặc mô hình không dùng lối tắt nào mà chỉ sai nhiều nhất ở cặp khó nhất. Chương này chưa phân biệt được hai khả năng đó.

Lớp Viral Pneumonia có một kiểu lỗi riêng. Lớp có 12 ảnh bị đoán sai, và 18 ảnh của lớp khác bị đoán nhầm vào nó. Phần lớn liên quan đến nhãn Normal: 7 ảnh Viral Pneumonia bị đoán thành Normal và 16 ảnh Normal bị đoán thành Viral Pneumonia, cộng lại 23 trường hợp. Dù vậy, theo Bảng 3.6, tỷ lệ lỗi của cặp Viral Pneumonia – Normal (1,33%) còn thấp hơn cặp COVID – Normal (1,50%), nên việc lỗi dồn về Normal có thể chỉ do Normal là lớp đông nhất.

Cặp này còn cho phép kiểm trực tiếp một dạng lối tắt theo nguồn ảnh. Trong 1.531 ảnh Normal của validation có 197 ảnh đến từ Mooney, cùng nguồn với toàn bộ 1.345 ảnh Viral Pneumonia (mục 2.1). Nếu mô hình đẩy ảnh Mooney sang Viral Pneumonia chỉ vì nguồn thì nhóm 197 ảnh này phải bị nhầm nhiều. Thực tế không ảnh nào trong số đó bị đoán thành Viral Pneumonia, còn cả 16 ảnh Normal bị nhầm sang lớp này đều thuộc nhóm RSNA. Dạng lối tắt đó vì thế không xuất hiện ở đây; các dạng khác thuộc phạm vi RQ3 (Chương 4).

Chiều ngược lại cũng không ủng hộ cách giải thích "cùng nguồn nên khó tách". Nếu 144 lỗi Normal → Lung_Opacity bắt nguồn từ việc hai lớp cùng thuộc RSNA thì 197 ảnh Mooney, vốn khác nguồn với Lung_Opacity, phải bị nhầm sang lớp này ít hơn ảnh RSNA. Số liệu cho thấy điều ngược lại: 25 trên 197 ảnh Mooney bị đoán thành Lung_Opacity (12,7%), so với 119 trên 1.334 ảnh RSNA còn lại (8,9%). Mẫu 197 ảnh nhỏ nên chưa thể kết luận về độ lớn của chênh lệch, nhưng chiều của các con số này không ủng hộ giả thuyết cùng nguồn.

Dấu hiệu xuất tệp cuối cùng là hệ màu. Cả 140 ảnh RGB của bộ dữ liệu đều thuộc lớp Viral Pneumonia (10,4% lớp này, mục 2.2); validation có 21 ảnh như vậy, bằng 10,3% của 203 ảnh lớp. Hai trong 12 lỗi của lớp là ảnh RGB, và recall của nhóm RGB là 90,5% (19 trên 21), so với 94,5% ở 182 ảnh còn lại. Chênh lệch này chỉ dựa trên 2 lỗi nên không cho phép kết luận theo chiều nào.

Ngoài các phép tách trên, còn bốn điểm cần giữ khi đọc kết quả. Thứ nhất, pipeline ép mọi ảnh về ảnh xám trước khi trích đặc trưng nên mô hình không hề thấy hệ màu của tệp; nếu RGB có tác động thì chỉ đến gián tiếp, qua những đặc điểm đi kèm cách xuất tệp. Thứ hai, 240 trong 349 lỗi (68,8%) bị cả SVM, Gradient Boosting và Random Forest cùng đoán sai, cho thấy phần lớn lỗi nằm ở đặc trưng hoặc ở nhãn chứ không riêng một bộ phân loại nào. Thứ ba, 138 trong 349 lỗi (39,5%) được mô hình gán xác suất từ 0,80 trở lên; đó là xác suất do nội suy Platt sinh ra và chưa được hiệu chỉnh trên dữ liệu ngoài, nên chỉ nên đọc là xác suất mô hình đưa ra chứ không phải xác suất sai thực. Cuối cùng, cả nhóm đặc trưng lẫn bộ phân loại đều được chọn trên chính tập validation này, nên điểm 0,9024 chịu thiên lệch do chọn lọc và có thể cao hơn mức thực; Chương 5 sẽ kiểm lại trên tập test.

Những điểm trên đều nằm ngoài phạm vi kiểm định của chương này. Mức phụ thuộc vào nguồn ảnh được kiểm ở Chương 4 (RQ3), còn các hạn chế còn lại được xét ở Chương 6.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 3.1:** `results/report_rq1/r1_summary.csv` (macro-F1 trung bình, SD, khoảng tin cậy, recall từng lớp), `results/report_rq1/r1_per_seed.csv` (điểm từng seed) và `results/rq1_feature_selection_record.md` mục 2 (cấu hình Random Forest 500 cây, 12 lần chạy, giây CPU mỗi ảnh). Cách bootstrap kết hợp ba seed mô tả ở mục 2.9 của Chương 2; cách cấu hình RQ1 và RQ2 khác nhau nêu ở mục 2.8 của Chương 2. Hệ số 42,5 là 0,056773/0,001337 tính trong báo cáo từ giá trị chưa làm tròn của `results/rq1_cost_rank_record.md` mục 2.
- **Nguồn mục 3.2:** `results/report_rq1/r1_bootstrap_vs_reference.csv` (ba phép so sánh với mốc histogram, 2.000 lần, `rng_seed = 42`) và `results/rq1_feature_selection_record.md` mục 3–4 (quy tắc chọn nhóm đặc trưng). Hệ số 15,4 là 0,0770/0,005 tính trong báo cáo, không có trong tệp nguồn.
- **Nguồn mục 3.3:** `results/report_rq2/r1_summary.csv` (sáu bộ, số seed, khoảng tin cậy) và `results/report_rq2/r1_bootstrap_vs_reference.csv` (năm phép so sánh với mốc Random Forest). Cấu hình SVM lấy từ `results/rq2_ghep_svm_s42/metrics.json`. Chênh lệch Gradient Boosting so với mốc `rf` là +0,0286 với CI [+0,0183; +0,0399], lấy từ `results/report_rq2/r1_bootstrap_vs_reference.csv`; chênh RF RQ2 so với RF RQ1 là 0,859895 − 0,858246 = 0,0017, tính từ hai tệp `r1_summary.csv`. Chênh lệch giữa nhóm ghép và nhóm GLCM kết hợp LBP ở mục 3.2 là 0,859895 − 0,815637 = 0,0443, cũng tính từ `r1_summary.csv`; không có phép kiểm định cho các con số này.
- **Số ảnh RGB:** đối chiếu `image_id` trong `results/rq2_ghep_svm_s42/preds_val.csv` với cột `color_mode` của `splits/manifest.csv`: trong validation có 21 ảnh RGB và cả 21 đều thuộc lớp Viral Pneumonia (10,3% của 203 ảnh lớp, so với 10,4% của toàn bộ lớp); 2 trong 12 ảnh lớp này bị đoán sai là RGB; nhóm RGB đạt recall 19/21 = 90,5% so với 94,5% của 182 ảnh còn lại.
- **Phép tách ảnh Normal theo nguồn:** `results/eda/normal_source_labels.csv` (10.192 dòng: 8.851 `rsna` và 1.341 `mooney`), sinh từ `Normal.metadata.xlsx` của dataset; số dòng và số lượng theo từng nguồn khớp với `docs/dataset_provenance.md` mục 2.1–2.2. Cách tải tệp xlsx, cách đọc bằng thư viện chuẩn và bộ kiểm thử parser ghi ở `docs/kaggle_setup_notes.md` mục 7.
- **Các số của đoạn nguồn trong mục 3.4:** 197 ảnh Normal cùng nguồn Mooney trong validation đếm từ `normal_source_labels.csv` ghép với `splits/split_v1.csv`; 0 trên 197 ảnh đó bị đoán thành Viral Pneumonia (và 0 bị đoán thành COVID), 25 ảnh bị đoán thành Lung_Opacity, đếm từ `results/rq2_ghep_svm_s42/preds_val.csv`; 16 ảnh bị đoán thành Viral Pneumonia đều thuộc nhóm RSNA; 119 = 144 − 25 ảnh RSNA bị đoán thành Lung_Opacity; 25/197 = 12,7% so với 119/1.334 = 8,9%.
- **Nguồn mục 3.4:** `results/rq2_ghep_svm_s42/metrics.json` (accuracy, balanced accuracy, macro-F1, chỉ số từng lớp, ma trận nhầm lẫn), `results/rq2_ghep_svm_s42/preds_val.csv` (nhãn thực, nhãn dự đoán và bốn cột xác suất của từng ảnh; mức 0,80 lấy từ xác suất của nhãn dự đoán) và `results/error_analysis/error_analysis_summary.md` mục 1–2 (349 lỗi, 240 lỗi đồng thuận, 138 lỗi có `proba_pred` từ 0,80 trở lên). Bảng 3.6 tính từ `preds_val.csv`, mẫu số là tổng ảnh hai lớp trong validation. SVM chạy một seed vì nhãn dự đoán của `SVC` không phụ thuộc seed; riêng xác suất sinh từ nội suy Platt có kiểm định chéo nội bộ theo seed (`SVC(probability=True, random_state=seed)` trong hàm huấn luyện của `src/rq2_runner.py`), nên mọi phép so sánh trong chương đều dựa trên nhãn.
- **Số 23 trong 30 lỗi của Viral Pneumonia:** 7 ảnh Viral Pneumonia bị đoán thành Normal (dòng cuối của Bảng 3.5) cộng 16 ảnh Normal bị đoán thành Viral Pneumonia (cột cuối). Con số 1.341 ảnh Normal cùng nguồn lấy từ `docs/dataset_provenance.md` mục 2.1 và đã dùng ở mục 2.1.
- **Số cặp còn lại:** 349 − 268 = 81 lỗi nằm trên năm cặp còn lại của Bảng 3.6 (31 + 20 + 23 + 6 + 1 = 81).
- **Hình 3.1:** sinh bằng `python -m scripts.report_figures` từ `confusion_matrix` trong `results/rq2_ghep_svm_s42/metrics.json`; mỗi hàng chia cho tổng hàng nên đường chéo là recall, khớp với cột recall ở Bảng 3.4 (kiểm thử `tests/test_report_figures.py` giữ điều này). Hình chỉ hiện tỷ lệ với một chữ số thập phân; sau làm tròn, chỉ hàng Lung_Opacity cộng 99,9%, các hàng còn lại 100,0%, số đếm gốc nằm ở Bảng 3.5.
- **Không dùng tệp test:** `results/final_test/confusion_matrix_test.png` và mọi số liệu trong `results/final_test/` thuộc Chương 5.
- **Bootstrap và ảnh gần trùng trong validation:** `src/bootstrap.py` lấy mẫu từng vị trí ảnh (`rng.integers(0, n, size=n)`), nên mọi khoảng tin cậy trong chương giả định 3.174 ảnh validation độc lập ở mức ảnh. Thực tế 27 nhóm pHash trong validation có hơn một ảnh (60 ảnh); mỗi nhóm chỉ nằm ở một split (`splits/split_v1.csv` cột `group_id`, mỗi nhóm một giá trị `split`), phép gom nhóm và đối chiếu gần trùng giữa các tập thuộc mục 2.3 và 2.5 của Chương 2.
- **Các khẳng định nhân quả của tệp phân tích lỗi** (độ sáng, viền khung chụp, đặc điểm máy chụp) không được đưa vào báo cáo vì không kiểm chứng được từ ảnh; riêng nhận định về phụ thuộc nguồn ảnh được nêu lại dưới dạng khả năng và giao cho RQ3.
