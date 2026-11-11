# CHƯƠNG 5. KẾT QUẢ KIỂM TRA ĐỘC LẬP VÀ TRIỂN KHAI

## 5.1. Kết quả trên tập test độc lập, mở khóa một lần

Ba câu hỏi nghiên cứu (mục 1.2) được trả lời trên 3.174 ảnh validation. Tập test gồm 3.176 ảnh bị khóa từ đầu và chỉ được mở đúng một lần, sau khi cấu hình đã đóng băng; phép đánh giá trình bày dưới đây là lần duy nhất tập này bị đọc. Mô hình được đánh giá là cấu hình đã chọn ở mục 3.3 và giữ nguyên xuyên suốt Chương 4: SVM kernel RBF, C = 10, gamma = scale, trọng số lớp cân bằng, đặt sau bước chuẩn hóa StandardScaler, trên nhóm đặc trưng ghép 152 chiều, ảnh gốc xám 299 × 299, seed 42. Quy trình mở khóa và các cổng kiểm soát nằm ở mục 5.4.

**Bảng 5.1: Các chỉ số tổng thể của mô hình trên 3.176 ảnh tập test**

| Chỉ số | Giá trị |
| :--- | ---: |
| Macro-F1 | 0,8714 |
| Khoảng tin cậy 95% (bootstrap 2.000 lần, seed 42) | [0,8579; 0,8840] |
| Accuracy | 86,56% |
| Balanced accuracy | 87,44% |
| Weighted F1 | 0,8659 |
| Macro precision | 0,8687 |

Mô hình đoán đúng 2.749 trong 3.176 ảnh (Bảng 5.1); 427 ảnh còn lại bị đoán sai, bằng 13,45% tập test. Balanced accuracy bằng macro recall vì cả hai đều là trung bình cộng recall của bốn lớp.

**Bảng 5.2: Precision, Recall và F1 theo lớp của mô hình trên tập test**

| Lớp | Số ảnh | Precision | Recall | F1 | Số lỗi |
| :--- | ---: | ---: | ---: | ---: | ---: |
| COVID | 543 | 0,9257 | 0,9171 | 0,9214 | 45 |
| Lung_Opacity | 904 | 0,8013 | 0,8296 | 0,8152 | 154 |
| Normal | 1.529 | 0,8844 | 0,8659 | 0,8751 | 205 |
| Viral Pneumonia | 200 | 0,8634 | 0,8850 | 0,8741 | 23 |

*(Số ảnh là support của từng lớp trên tập test; số lỗi là tổng các ô ngoài đường chéo của hàng lớp đó trong Bảng 5.4.)*

F1 của bốn lớp (Bảng 5.2) nằm trong khoảng 0,8152 (Lung_Opacity) đến 0,9214 (COVID). Lung_Opacity có recall và F1 thấp nhất; Normal là lớp đông nhất, có 205 lỗi thô, nhiều nhất trong bốn lớp.

## 5.2. Chênh lệch validation và test (Quy tắc D4)

Cùng một cấu hình cho ra macro-F1 0,9024 trên validation và 0,8714 trên tập test; hiệu số test − val là −0,0310. Accuracy giảm 2,44 điểm, từ 89,00% xuống 86,56%.

**Bảng 5.3: Recall từng lớp trên validation và trên tập test**

| Lớp | Số ảnh validation | Recall validation | Số ảnh test | Recall test | Chênh (điểm phần trăm) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| COVID | 537 | 95,72% | 543 | 91,71% | −4,01 |
| Lung_Opacity | 903 | 84,94% | 904 | 82,96% | −1,98 |
| Normal | 1.531 | 88,37% | 1.529 | 86,59% | −1,78 |
| Viral Pneumonia | 203 | 94,09% | 200 | 88,50% | −5,59 |

Recall giảm ở cả bốn lớp (Bảng 5.3), mạnh nhất ở Viral Pneumonia (−5,59 điểm) và nhẹ nhất ở Normal (−1,78 điểm). Số ảnh của mỗi lớp giữa hai tập lệch vài đơn vị; phân chia được thực hiện theo tỷ lệ đã đăng ký (mục 2.4). Biên bản đánh giá không đăng ký khoảng tin cậy cho hiệu số test − val, nên con số −0,0310 là phép trừ trực tiếp hai giá trị đã ghi.

Quyết định thứ tư trong biên bản đánh giá tập test giữ nguyên văn: *"Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết chưa kiểm chứng, không nêu nguyên nhân."* Chương này vì thế dừng ở mức số đo: các con số ở trên là kết quả tính học giữa hai lần đánh giá, không kèm diễn giải nguyên nhân.

## 5.3. Phân tích lỗi sai và cặp nhầm lẫn Normal – Lung_Opacity

**Bảng 5.4: Ma trận nhầm lẫn trên 3.176 ảnh tập test**

| Nhãn thực ↓ / Dự đoán → | COVID | Lung_Opacity | Normal | Viral Pneumonia | Tổng lỗi |
| :--- | ---: | ---: | ---: | ---: | ---: |
| COVID (543) | 498 | 22 | 18 | 5 | 45 |
| Lung_Opacity (904) | 12 | 750 | 142 | 0 | 154 |
| Normal (1.529) | 20 | 162 | 1.324 | 23 | 205 |
| Viral Pneumonia (200) | 8 | 2 | 13 | 177 | 23 |

![Ma trận nhầm lẫn trên tập test](../figures/05_ma_tran_nham_lon_test.png)

**Hình 5.1: Ma trận nhầm lẫn của mô hình SVM trên 3.176 ảnh tập kiểm tra độc lập**

Trong Hình 5.1, hàng là nhãn thực, cột là nhãn dự đoán, ô càng đậm khi số ảnh càng lớn; số đếm gốc của từng ô nằm ở Bảng 5.4.

Lỗi dồn về một cặp: 304 trong 427 lỗi (71,19%) thuộc cặp Normal – Lung_Opacity, gồm 162 ảnh Normal bị đoán thành Lung_Opacity và 142 ảnh theo chiều ngược lại. Trên tổng 2.433 ảnh của hai lớp này, tỷ lệ lỗi cặp là 12,49%; cùng một phép tính trên validation cho 11,01% (Bảng 4.3 của Chương 4). 123 lỗi còn lại thuộc năm cặp còn lại, nhiều nhất là cặp Normal – COVID (38 ảnh). Không có ảnh Lung_Opacity nào bị đoán thành Viral Pneumonia. Các con số ở mục này là phép đo trên từng tập; phần nguyên nhân của chênh lệch giữa hai tập không được nêu theo quy tắc đã đăng ký.

## 5.4. Tính độc lập và khả năng tái lập của thực nghiệm

**Độc lập.** Quy trình đánh giá tập test được đăng ký và khóa trước khi mở khóa, gồm bốn quyết định: huấn luyện một mô hình duy nhất trên toàn bộ 14.815 ảnh train (D1); đánh giá đúng một mô hình trên đúng 3.176 ảnh test, không đánh giá thêm cấu hình che mặt nạ hay cấu hình train+val (D2); báo cáo một lần đầy đủ chỉ số, khoảng tin cậy, ma trận nhầm lẫn và giới hạn (D3); báo cáo trung thực số đo và không nêu nguyên nhân chênh lệch val–test (D4). Sáu cổng chạy theo thứ tự, cổng nào lỗi thì dừng trước khi đọc ảnh test: kiểm tra băm SHA-256 của tệp phân chia cùng ba cỡ mẫu (G1); đối chiếu cấu hình đóng băng (G2); từ chối chạy lần hai nếu đã tồn tại bản ghi mở khóa (G3); yêu cầu chuỗi xác nhận do người dùng gõ, chỉ đối chiếu qua băm SHA-256 (G4); tái lập macro-F1 validation trong dung sai 0,002 quanh mốc 0,9024 (G5); ghi bản ghi mở khóa ra đĩa trước khi đọc ảnh test đầu tiên (G6).

Bản ghi mở khóa lưu mốc thời gian, mã commit, băm SHA-256 của tệp phân chia và của chuỗi xác nhận. Giá trị macro-F1 validation tái lập ở cổng tái lập là 0,9024, nằm trong đoạn cho phép [0,9004; 0,9044]. Kernel chạy đánh giá trên Kaggle giữ đúng một phiên bản duy nhất, theo bản ghi tiến độ S5-04; quy trình kiểm toán phiên bản thủ công được đăng ký trong biên bản.

**Tái lập.** Hai lớp bằng chứng cho phép người khác kiểm lại kết quả mà không cần đọc lại ảnh. Thứ nhất, notebook đánh giá chỉ đọc các tệp kết quả đã công bố, mỗi bước tương ứng một bảng hoặc một hình trong báo cáo này. Thứ hai, bộ kiểm thử tự động gồm 275 hàm test trong 23 module. Các bộ gắn trực tiếp với tuyến test ép từng cổng: bộ kiểm thử của bộ chạy đánh giá (cấu trúc sáu cổng, chống chạy lần hai, dựng gói mã cuối), bộ kiểm thử tệp kết quả và notebook (đủ bảy tệp kết quả bắt buộc, nội dung bản ghi mở khóa, 3.176 dòng dự đoán với bốn cột xác suất có tổng 1, notebook đã được thực thi và không import framework học sâu), và các bộ kiểm thử artifact với giao diện (kiểm băm trước khi nạp mô hình, cổng từ chối theo tên tệp, cảnh báo y khoa).

## 5.5. Triển khai ứng dụng

### 5.5.1. Pipeline suy luận từ ảnh xám 299×299 đến xác suất dự đoán

Pipeline gồm năm bước. Ảnh tải lên được giải mã thành ảnh xám và đổi cỡ về 299 × 299 nếu cần, kèm cảnh báo khi ảnh bị đổi cỡ. Tên tệp bị từ chối trước khi giải mã nếu trùng với một ảnh thuộc tập test (cổng H2). Từ ảnh xám, pipeline trích 152 đặc trưng (histogram 64, GLCM 60, LBP 28), chuẩn hóa bằng StandardScaler đã fit trên tập train, rồi dự đoán bằng SVC kernel RBF đã đóng băng; đầu ra là xác suất của bốn lớp. Bộ chuẩn hóa và bộ phân loại được nạp từ một artifact duy nhất, kiểm tra băm SHA-256 trước khi nạp; artifact lấy từ kho công khai trên Hugging Face Hub [7]. Cổng tương đương chạy 200 ảnh validation (seed 42) cho khớp nhãn 200/200 với kết quả của pipeline huấn luyện. Toàn bộ pipeline chỉ dùng thư viện học máy cổ điển (mục 1.3).

### 5.5.2. Giao diện Streamlit và các thành phần tương tác

Giao diện viết bằng Streamlit [8]. Khu tải ảnh nhận PNG/JPG tối đa 10 MB. Khu kết quả hiển thị nhãn dự đoán, biểu đồ cột xác suất bốn lớp và bảng xác suất; khu ảnh hiển thị ảnh sau tiền xử lý kèm nút tải về dạng PNG. Thanh bên hiển thị ba số đo đã công bố – macro-F1 validation 0,9024, macro-F1 test 0,8714 và chênh lệch −0,0310 – đọc trực tiếp từ tệp kết quả, không ghi cứng trong mã. Ảnh tải lên chỉ nằm trong bộ nhớ của phiên; ứng dụng không ghi ảnh xuống đĩa và không ghi nội dung ảnh vào nhật ký.

### 5.5.3. Cảnh báo y khoa tích hợp trong ứng dụng

Cảnh báo hiện ở đầu trang, cuối trang và trong thanh bên, với nội dung chính: *"KHÔNG DÙNG ĐỂ CHẨN ĐOÁN. Đây là demo học thuật của mô hình học máy truyền thống, không phải thiết bị y tế và chưa được kiểm định lâm sàng."* Ứng dụng còn nhắc người dùng chỉ tải ảnh đã ẩn danh, không tải ảnh bệnh nhân thật hoặc ảnh có thông tin định danh, và hiển thị lại quy tắc đã đăng ký về chênh lệch giữa hai tập cùng giới hạn về ảnh khác nguồn. Phần giới hạn và đạo đức được thảo luận thêm ở mục 6.3.

### 5.5.4. Độ trễ suy luận thực tế

Độ trễ được đo bằng kịch bản `src/inference_latency.py`, chạy đúng đường đi của ứng dụng: giải mã byte thành ảnh xám, trích 152 đặc trưng, rồi suy luận. Mẫu đo là 200 ảnh validation (seed 42, cùng cách chọn mẫu với cổng tương đương), đo ba lượt nối tiếp nhau, tức 600 phép đo; đồng hồ là thời gian thực (wall time), thời gian đọc tệp nằm ngoài đồng hồ. Môi trường đo ghi trong bản ghi kết quả: máy Windows, CPU 13th Gen Core i5-13420H, Python 3.12.7, đúng bộ phiên bản mà ứng dụng dùng (numpy 2.0.2, scikit-learn 1.6.1, scikit-image 0.25.2, OpenCV 4.13.0.92).

**Bảng 5.5: Độ trễ đầu-cuối và theo từng chặng trên 600 phép đo (200 ảnh validation, seed 42, 3 lượt)**

| Chặng | Trung vị | p90 | p95 |
| :--- | ---: | ---: | ---: |
| Giải mã ảnh xám | 3,3 ms | 3,6 ms | 3,7 ms |
| Trích 152 đặc trưng | 119,2 ms | 127,7 ms | 130,2 ms |
| Suy luận (scaler + SVC) | 9,2 ms | 9,5 ms | 9,6 ms |
| **Đầu-cuối** | **131,8 ms** | **140,5 ms** | **144,5 ms** |

Chi phí trích đặc trưng chiếm khoảng 90% thời gian đầu-cuối (Bảng 5.5). Suy luận của riêng bộ phân loại tốn 9,2 ms ở mức trung vị; mô hình có 6.180 vector hỗ trợ. Thời gian nạp artifact từ đĩa, sau khi kiểm băm, là 5,2 ms.

Đo một lượt cho thấy điểm cần nói rõ: ảnh đầu tiên sau khi máy nghỉ chỉ mất 28–30 ms, nhưng sau vài chục ảnh liên tiếp, thời gian mỗi ảnh lên quanh 125–140 ms rồi ổn định. Hiện tượng đo được là CPU giảm tần sau khi hết thời gian boost; việc nghỉ một giây giữa các ảnh không đưa máy về trạng thái ban đầu (đã thử và không hiệu quả). Cả hai chế độ đều được ghi thành bản ghi riêng, cùng một script và cùng mẫu nên so trực tiếp được.

Ba giới hạn của số đo này: (1) độ trễ phụ thuộc phần cứng, nên con số trên mang tính minh họa cho môi trường đã ghi chứ không phải của máy chủ Streamlit Community Cloud; (2) chỉ đo trên ảnh 299×299 của bộ dữ liệu, nhánh đổi cỡ của ứng dụng chưa được đo; (3) tải artifact 7,8 MB từ Hugging Face ở lần khởi động lạnh không tính vào độ trễ suy luận vì phụ thuộc mạng. Làm mốc đối chiếu, bản ghi chi phí của RQ1 đo trích đặc trưng nhóm ghép trên Kaggle CPU ở mức 0,056773 giây CPU mỗi ảnh (17.989 ảnh); phép đó dùng đồng hồ CPU time trên máy khác nên hai con số không so trực tiếp được.

---

## Tài liệu tham khảo phát sinh trong chương

Các mục dưới đây đánh số tiếp theo cơ chế của Chương 1 (tài liệu của các chương sau đánh tiếp từ [7]).

[7] Hugging Face, "Hugging Face Hub documentation," 2026. [Online]. Available: https://huggingface.co/docs/hub/

[8] Streamlit, "Streamlit documentation," 2026. [Online]. Available: https://docs.streamlit.io/

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 5.1:** `results/final_test/final_test_report.json` (macro-F1 0,8714, CI [0,8579; 0,8840], chỉ số từng lớp, ma trận nhầm lẫn, khối `r2_normal_lung_opacity`, khối `r4_sampling_error`: n = 3.176, 2.000 lần bootstrap, seed 42, độ rộng CI 0,0261) và `results/final_test/metrics.json` (accuracy 0,8656, balanced accuracy 0,8744, weighted F1 0,8659, macro precision 0,8687, macro recall 0,8744). Số ảnh đoán đúng 2.749 = 3.176 − 427; 13,45% = 427/3.176. Số lỗi từng lớp là tổng hàng ngoài đường chéo của ma trận; đối chiếu chéo với `results/final_test/preds_test.csv` (427 dòng lệch nhãn trên 3.176 dòng).
- **Nguồn mục 5.2:** macro-F1 validation 0,9024 và recall từng lớp đọc từ `results/rq2_ghep_svm_s42/metrics.json` (nguồn của mục 3.4, Chương 3); các giá trị này trùng với dòng `orig_to_orig` của `results/report_rq3/r1_summary.csv` đến sáu chữ số thập phân. Hiệu `test_minus_val` = −0,0310 đọc từ `final_test_report.json`. Cột "Chênh" của Bảng 5.3 tính bằng phép trừ hai cột đã làm tròn; nếu tính từ giá trị chưa làm tròn, COVID là −4,00, Lung_Opacity −1,97, Normal −1,78 và Viral Pneumonia −5,59. Trường `interpretation_note` trong JSON lưu bản không dấu; báo cáo trích bản có dấu từ `docs/report_standards.md` mục 5.2 và `report/README.md` mục 2.
- **Nguồn mục 5.3:** 304 = 142 + 162 đọc từ ma trận nhầm lẫn trong `results/final_test/metrics.json` và khối `r2_normal_lung_opacity` trong `final_test_report.json` (750/142/162/1.324); 71,19% = 304/427; 12,49% = 304/(904 + 1.529) = 304/2.433. Mốc validation 11,01% lấy từ `results/report_rq3/r2_normal_lung_opacity.csv` (dòng `orig_to_orig`, 268/2.433), đã trình bày ở Bảng 4.3. Số 123 = 427 − 304; cặp Normal – COVID là 20 + 18 = 38; ô Lung_Opacity → Viral Pneumonia bằng 0.
- **Nguồn mục 5.4:** `results/final_test_protocol_record.md` (D1–D4, G1–G6, quy trình kiểm toán phiên bản thủ công, dung sai G5 0,002 quanh mốc 0,9024); `results/final_test/UNLOCK_RECORD.json` (`utc_time` 2026-11-09T07:43:34Z, commit `5720e4fdb6c1d827b800e51ef8be5559fe191dd6`, `split_sha256` `f99e03d3…`, `confirm_sha256` `9e935a10…`, `val_macro_f1` 0,9024447972521963); các hằng số trong `src/final_test_runner.py` (`EXPECTED_SPLIT_SIZES` 14.815/3.174/3.176, `REFERENCE_VAL_MACRO_F1`, `G5_TOLERANCE`, `CONFIRM_STRING_SHA256`); kernel `ductrannguyen/cxr-final-test` ở version duy nhất và hai pull request #41, #42 ghi ở `docs/roadmap.md` (dòng S5-04). Biên bản yêu cầu bằng chứng kiểm toán phiên bản (ảnh chụp màn hình hoặc kết quả API Kaggle) đính kèm vào báo cáo PR B; kho không lưu tệp bằng chứng đó nên chương không khẳng định đã đính kèm. Notebook đánh giá là `notebooks/10_final_test_eval.ipynb` (12 cell, 5 mục), chỉ đọc tệp kết quả.
- **Quy mô kiểm thử trong mục 5.4:** 275 hàm test trong 23 module là số đếm trước khi bộ `tests/test_report_figures_final_test.py` (10 hàm) được thêm trong cùng PR của chương này; sau khi thêm là 285 hàm trong 24 module. Bản ghi chạy đầy đủ gần nhất: 273 test pass (`docs/roadmap.md` dòng 158, S6-02, ngày 11/11/2026). Số 296 ở hàng Phụ lục B của `report/README.md` chưa rõ căn cứ, cần đối chiếu trước khi in. Trên môi trường Windows hiện tại, 10 trong 23 module không thu thập được do thiếu `scikit-image` (95 test thu thập được), nên các mô tả kiểm thử của chương đọc từ mã nguồn của các bộ test, không phải từ lần chạy trên máy này.
- **Nguồn mục 5.5:** `src/inference_demo.py` (dòng 39 `N_FEATURES = 152`, dòng 40 `IMAGE_SIZE = (299, 299)`, dòng 55 `load_image_grayscale_299`, dòng 92 `ensure_not_heldout_image`, dòng 110 `extract_152_features`, dòng 187 `fit_or_load_model`, dòng 338 `predict_image`, `load_benchmark_metrics` đọc `results/final_test/metrics.json` và `results/rq2_ghep_svm_orig_to_orig_s42/metrics.json`); artifact ở `src/model_artifact.py` (kho mặc định `duc16/cxr-svm-demo`, tệp `cxr_inference_model_cache.joblib`, SHA-256 `3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058`, kích thước 7.842.399 byte ghi ở `demo/README.md`); giao diện ở `demo/streamlit_app.py` (`MAX_UPLOAD_BYTES` = 10 MB ở dòng 56, `DISCLAIMER` ở dòng 60–64, `build_limitations_text` ở dòng 175–190); cổng tương đương 200/200 ảnh validation ghi ở `demo/README.md` và `docs/roadmap.md` (S6-02). Độ trễ suy luận: xem bullet riêng bên dưới.
- **Nguồn mục 5.5.4:** kịch bản `src/inference_latency.py` (`python -m src.inference_latency`), hai bản ghi `results/demo_latency_interactive/latency.json` (20 ảnh, một lượt, chế độ tương tác) và `results/demo_latency_sustained/latency.json` (200 ảnh × 3 lượt = 600 phép đo, chế độ liên tục), kèm `per_image.csv` của từng bản ghi. Cả hai dùng cùng mẫu val seed 42; các giá trị trong Bảng 5.5 đọc từ bản ghi chế độ liên tục (`stats.per_image_median_seconds`, thống kê trên trung vị từng ảnh qua ba lượt). Môi trường đo (CPU, RAM, Python, phiên bản numpy/scikit-learn/scikit-image/OpenCV/joblib/pandas/PyYAML) và thông tin artifact (băm SHA-256, kích thước, `n_train` = 14.815, 6.180 vector hỗ trợ, thời gian nạp) ghi trong chính hai tệp JSON. Lệnh tái lập: `python -m src.inference_latency --dataset-root <thư-mục-bộ-ảnh> --n 20 --seed 42 --repeats 1 --out-dir results/demo_latency_interactive` và bản `--n 200 --repeats 3 --out-dir results/demo_latency_sustained`. Phát hiện khi đo: sau vài chục ảnh liên tiếp trong cùng tiến trình, thời gian mỗi ảnh tăng gấp khoảng bốn lần rồi ổn định; thử nghiệm nghỉ một giây giữa các ảnh không khôi phục trạng thái ban đầu nên biện pháp đó đã bị loại bỏ khỏi kịch bản. Mốc Kaggle CPU 0,056773 giây CPU mỗi ảnh đọc từ `results/rq1_cost_rank_record.md` (17.989 ảnh, `time.process_time`) — khác đồng hồ và khác máy nên chỉ dùng làm mốc tham khảo. Nhánh đổi cỡ của ứng dụng (ảnh không phải 299×299) chưa được đo vì toàn bộ ảnh val đã là 299×299.
- **Hình 5.1:** sinh bằng `python -m scripts.report_figures_final_test` từ `results/final_test/metrics.json`; bộ `tests/test_report_figures_final_test.py` (10 test) đối chiếu từng ô của hình với tệp nguồn và chốt tổng support bằng 3.176. Tệp `results/final_test/confusion_matrix_test.png` do notebook đánh giá sinh trước đây, được giữ làm bằng chứng lịch sử và không dùng làm nguồn của báo cáo.
