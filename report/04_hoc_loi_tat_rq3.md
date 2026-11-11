# CHƯƠNG 4. NGHIÊN CỨU HIỆN TƯỢNG HỌC LỐI TẮT (RQ3)

## 4.1. Năm kịch bản che mặt nạ phổi

RQ3 hỏi che hoặc cắt ảnh theo mặt nạ phổi có làm thay đổi macro-F1 không, và mức thay đổi đó cho biết gì về mức phụ thuộc của mô hình vào vùng ngoài phổi (mục 1.1). Ba chế độ mặt nạ (`original`, `lung_only`, `outside_only`) được ghép thành năm kịch bản huấn luyện–đánh giá, đã đóng băng trong biên bản trước khi chạy lô full. Mô hình dùng cho cả năm kịch bản là cấu hình đã khóa từ RQ2: SVM kernel RBF, C = 10, gamma = scale, trọng số lớp cân bằng, kết hợp StandardScaler chỉ fit trên train tương ứng, trên nhóm đặc trưng ghép 152 chiều, seed = 42.

Mặt nạ phổi đi kèm bộ dữ liệu ở kích thước 256 × 256 nên được nội suy về 299 × 299 bằng `cv2.INTER_NEAREST` trước khi dùng (mục 2.2); trong phiên chạy thử kỹ thuật trước khi mở điểm, không có mặt nạ rỗng sau nội suy và 20/20 mẫu thử có trọng tâm vùng phổi nằm trong khung trung tâm giải phẫu hợp lệ. Vai trò của năm kịch bản như sau.

| Kịch bản | Ảnh train | Ảnh validation | Vai trò |
| :--- | :--- | :--- | :--- |
| `orig_to_orig` | `original` | `original` | Tham chiếu: cấu hình chuẩn đã khóa ở RQ2, ảnh gốc không che |
| `lung_to_lung` | `lung_only` | `lung_only` | Ứng viên chính: chỉ huấn luyện và suy luận trong vùng phổi |
| `out_to_out` | `outside_only` | `outside_only` | Đối chứng lối tắt: chỉ huấn luyện và suy luận ngoài vùng phổi |
| `orig_to_lung` | `original` | `lung_only` | Nhiễu suy luận: bộ gốc gặp ảnh bị che ngoài phổi lúc đánh giá |
| `orig_to_out` | `original` | `outside_only` | Nhiễu suy luận: bộ gốc gặp ảnh bị che vùng phổi lúc đánh giá |

*(Vai trò của từng kịch bản lấy từ `results/rq3_comparison_protocol_record.md` mục 2.1; quy tắc phép so sánh chính lấy từ mục 2.2 của biên bản đó, trên cơ sở mục 5 của `results/threshold_v3.md`.)*

**Bảng 4.1: Macro-F1, khoảng tin cậy và accuracy của năm kịch bản trên 3.174 ảnh validation**

| Kịch bản | Macro-F1 | 95% CI | Accuracy | Recall COVID | Recall Lung_Opacity | Recall Normal | Recall Viral Pneumonia |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| `orig_to_orig` | 0,9024 | [0,8909; 0,9129] | 89,00% | 95,72% | 84,94% | 88,37% | 94,09% |
| `lung_to_lung` | 0,8490 | [0,8333; 0,8625] | 85,44% | 86,59% | 81,40% | 86,54% | 92,12% |
| `out_to_out` | 0,8921 | [0,8807; 0,9031] | 87,84% | 94,79% | 83,17% | 87,26% | 94,58% |
| `orig_to_lung` | 0,0723 | [0,0677; 0,0770] | 16,89% | 99,81% | 0,00% | 0,00% | 0,00% |
| `orig_to_out` | 0,2084 | [0,1953; 0,2220] | 27,22% | 93,85% | 27,35% | 7,32% | 0,49% |

*(Macro-F1, khoảng tin cậy và recall từng lớp lấy từ `results/report_rq3/r1_summary.csv`; accuracy lấy từ `results/report_rq3/r4_sampling_error.csv`. Khoảng tin cậy của từng kịch bản là bootstrap 2.000 lần trên 3.174 ảnh, seed 42.)*

Cột macro-F1 ở Bảng 4.1 cho thấy ba kịch bản huấn luyện–đánh giá cùng chế độ (`orig_to_orig`, `lung_to_lung`, `out_to_out`) đều vượt xa hai mốc nền B0 = 0,1627 (bộ đọc luôn nhãn Normal, `results/b0_majority/metrics.json`) và A0 = 0,2397 (bộ đọc metadata tệp bằng Random Forest, `results/a0_shortcut/metrics.json`). Kịch bản `out_to_out` – mô hình không nhìn thấy bất cứ điểm ảnh nào trong vùng phổi – đạt 0,8921, gấp 3,7 lần mốc A0 và cao hơn mốc histogram độ xám với Random Forest: mốc đó được đăng ký trước ở mức 0,7852 (`results/threshold_v3.md` mục 4), còn lô full RQ1 đo được 0,7829 (`results/report_rq1/r1_summary.csv`, khớp Bảng 3.1). Hai kịch bản nhiễu suy luận nằm dưới các mốc này: `orig_to_out` đạt 0,2084, trên B0 nhưng dưới A0; `orig_to_lung` đạt 0,0723, dưới cả B0.

**Bảng 4.2: Phép so sánh ghép cặp giữa các kịch bản (bootstrap 2.000 lần, n = 3.174)**

| Cặp so sánh | Chênh macro-F1 | 95% CI của chênh | Khoảng chứa 0 |
| :--- | ---: | :--- | :---: |
| `orig_to_orig` − `lung_to_lung` | +0,0535 | [+0,0392; +0,0691] | Không |
| `orig_to_orig` − `out_to_out` | +0,0103 | [−0,0017; +0,0220] | Có |
| `orig_to_orig` − `orig_to_lung` | +0,8302 | [+0,8181; +0,8415] | Không |
| `orig_to_orig` − `orig_to_out` | +0,6940 | [+0,6772; +0,7110] | Không |
| `out_to_out` − `lung_to_lung` | +0,0431 | [+0,0281; +0,0582] | Không |

*(Toàn bộ năm dòng lấy từ `results/report_rq3/r3_shortcut_bootstrap.csv`: mỗi lần lấy mẫu dùng một tập vị trí ảnh chung cho cả hai kịch bản, nên phép so là ghép cặp. Bốn dòng đầu cũng có trong `results/report_rq3/r1_bootstrap_vs_reference.csv` dưới dạng so với mốc `orig_to_orig`.)*

Phép so sánh chính của RQ3, đã đóng băng trước khi xem điểm, đối chiếu ứng viên `lung_to_lung` với mốc `orig_to_orig` theo quy tắc chuyển đổi giống RQ1 và RQ2: chênh ít nhất +0,005 và khoảng tin cậy 95% không chứa 0. Chênh đo được là −0,0535 với khoảng [−0,0691; −0,0392], nên việc chỉ giữ vùng phổi làm giảm macro-F1 có ý nghĩa thống kê và không thỏa điều kiện thay thế. Cấu hình ảnh gốc `orig_to_orig` vì thế được giữ làm cấu hình chính thức để đánh giá một lần trên tập test (`results/rq3_comparison_protocol_record.md` mục 2.2; kết quả trên tập test thuộc Chương 5).

Khoảng cách giữa `orig_to_orig` và `out_to_out` theo chiều ngược lại chỉ là +0,0103 và khoảng tin cậy [−0,0017; +0,0220] chứa 0. Sai số chuẩn của accuracy hai kịch bản này là 0,56 và 0,58 điểm phần trăm (`results/report_rq3/r4_sampling_error.csv`), tức khoảng cách nhỏ hơn sai số lấy mẫu của từng phép đo. Cả ba con số vừa nêu đều chỉ về một kết luận: dữ liệu ở đây chưa đủ để kết luận mô hình nhìn toàn bộ ảnh khác mô hình chỉ nhìn ngoài phổi. Đây là kết luận thống kê theo khoảng tin cậy, không phải bằng chứng về sự tương đương của hai mô hình.

Hai kịch bản nhiễu suy luận cho kết quả trái ngược: che một vùng của ảnh ở thời điểm đánh giá – dù mô hình không hề được huấn luyện trên ảnh bị che – làm macro-F1 giảm 0,8302 và 0,6940. Trong `orig_to_lung`, mô hình dồn gần như toàn bộ ảnh về nhãn COVID: recall COVID đạt 99,81% nhưng precision của lớp này chỉ 0,1690, các lớp còn lại có recall 0,00%. Mô hình vì thế không còn phân biệt được bốn lớp trên ảnh bị che; cơ chế bên dưới – thay đổi phân phối đặc trưng toàn cục do vùng bị che – là giả thuyết, xem mục 4.3.

**Bảng 4.3: Cặp nhầm lẫn Normal ↔ Lung_Opacity theo kịch bản**

| Kịch bản | Lung_Opacity → Normal | Normal → Lung_Opacity | Tổng lỗi cặp | Tỷ lệ trên 2.434 ảnh hai lớp |
| :--- | ---: | ---: | ---: | ---: |
| `orig_to_orig` | 124 (13,73%) | 144 (9,41%) | 268 | 11,01% |
| `lung_to_lung` | 105 (11,63%) | 101 (6,60%) | 206 | 8,46% |
| `out_to_out` | 138 (15,28%) | 158 (10,32%) | 296 | 12,16% |
| `orig_to_lung` | 1 (0,11%) | 0 (0,00%) | 1 | 0,04% |
| `orig_to_out` | 61 (6,76%) | 169 (11,04%) | 230 | 9,45% |

*(Bốn ô đếm mỗi kịch bản lấy từ `results/report_rq3/r2_normal_lung_opacity.csv`; mẫu số cố định cho cả năm kịch bản là 903 ảnh Lung_Opacity và 1.531 ảnh Normal của validation. Hai dòng `orig_to_lung` và `orig_to_out` phải đọc cùng kết quả sụp đổ ở Bảng 4.1: gần như toàn bộ ảnh đã bị dồn về nhãn COVID.)*

Cặp nhầm nặng nhất của Chương 3 giảm khi mô hình chỉ nhìn trong phổi: 268 lỗi của `orig_to_orig` xuống 206 của `lung_to_lung`, và giảm ở cả hai chiều. Che ngược lại – chỉ nhìn ngoài phổi – làm cặp này tăng lên 296 lỗi. Chiều của các thay đổi là dữ liệu đo được; chương không kết luận vì sao các kịch bản che làm lệch cặp nhầm theo hướng đó, giả thuyết tương ứng nằm ở mục 4.3.

![Macro-F1 của năm kịch bản RQ3 kèm khoảng tin cậy và các mốc nền](../figures/04_macro_f1_kich_ban_rq3.png)

**Hình 4.1: Macro-F1 năm kịch bản RQ3 trên 3.174 ảnh validation, cột là điểm ước lượng và que chỉ khoảng tin cậy 95%**

Ngoài hai mốc B0 và A0, Hình 4.1 kẻ thêm đường ngang tại 0,7829 – mức macro-F1 của nhóm histogram với Random Forest ở lô full RQ1 – để đối chiếu trực quan `out_to_out` với mốc đó; đường này lấy từ cùng tệp nguồn với Bảng 3.1 chứ không phải từ mốc đăng ký 0,7852.

## 4.2. Tầm quan trọng đặc trưng theo 10 khối

Thí nghiệm hoán vị khối đo mức sụt macro-F1 khi xáo trộn ngẫu nhiên một nhóm chiều đặc trưng rồi suy luận lại, giữ nguyên các khối còn lại. Mỗi khối được hoán vị 10 lần (`n_repeats = 10`, seed 42), trên đúng 3.174 ảnh validation. Mười khối gồm ba khối tổng hợp – histogram 64 chiều, GLCM 60 chiều, LBP 28 chiều – và bảy tiểu khối: năm thuộc tính GLCM 12 chiều mỗi khối và hai miền LBP của 10 và 18 chiều. Ba chế độ ảnh `original`, `lung_only`, `outside_only` được đo riêng, baseline mỗi chế độ là macro-F1 của chính kịch bản đó ở Bảng 4.1.

**Bảng 4.4: Mức sụt macro-F1 khi hoán vị từng khối (10 lần, trên 3.174 ảnh validation)**

| Khối | Số chiều | `original` | `lung_only` | `outside_only` |
| :--- | ---: | ---: | ---: | ---: |
| `hist_64` | 64 | 0,2863 ± 0,0098 | 0,2658 ± 0,0050 | 0,2656 ± 0,0112 |
| `glcm_60` | 60 | 0,3264 ± 0,0079 | 0,4960 ± 0,0035 | 0,3526 ± 0,0081 |
| `lbp_28` | 28 | 0,3590 ± 0,0119 | 0,4283 ± 0,0079 | 0,3590 ± 0,0103 |
| `glcm_contrast_12` | 12 | 0,0485 ± 0,0048 | 0,3163 ± 0,0058 | 0,0694 ± 0,0045 |
| `glcm_dissimilarity_12` | 12 | 0,0991 ± 0,0042 | 0,4655 ± 0,0066 | 0,1814 ± 0,0101 |
| `glcm_homogeneity_12` | 12 | 0,1164 ± 0,0072 | 0,1787 ± 0,0056 | 0,1477 ± 0,0080 |
| `glcm_energy_12` | 12 | 0,0598 ± 0,0036 | 0,0694 ± 0,0062 | 0,0359 ± 0,0039 |
| `glcm_correlation_12` | 12 | 0,0479 ± 0,0054 | 0,2277 ± 0,0088 | 0,0511 ± 0,0028 |
| `lbp_r1_p8_10` | 10 | 0,1548 ± 0,0063 | 0,2318 ± 0,0055 | 0,1341 ± 0,0043 |
| `lbp_r2_p16_18` | 18 | 0,3077 ± 0,0058 | 0,2877 ± 0,0107 | 0,2746 ± 0,0063 |

*(Toàn bộ con số lấy từ `results/rq3_permutation_importance.csv`: `importance_mean ± importance_std` của khối tương ứng trên mỗi chế độ; baseline của ba chế độ là 0,9024, 0,8490 và 0,8921.)*

Trên ảnh gốc, ba khối tổng hợp có mức sụt cách nhau không nhiều: LBP 0,3590, GLCM 0,3264, histogram 0,2863. Kết quả thay đổi khi vùng phổi là vùng duy nhất còn lại: khối GLCM vọt lên 0,4960 (+0,1696 so với ảnh gốc) và vượt LBP (0,4283); hai tiểu khối dẫn đầu trong chế độ này là `glcm_dissimilarity_12` (0,4655) và `glcm_contrast_12` (0,3163). Trên chế độ chỉ còn ngoài phổi, thứ tự quay về gần giống ảnh gốc: LBP 0,3590, GLCM 0,3526, histogram 0,2656, và tiểu khối LBP bán kính 2 (0,2746) cao nhất trong bảy tiểu khối.

Một điểm cần chú ý khi đọc bảng: baseline của ba chế độ khác nhau (0,9024, 0,8490 và 0,8921), nên con số trong bảng là mức sụt đo được trên từng mô hình. Việc GLCM sụt nhiều hơn trên `lung_only` cho thấy khối này đóng góp nhiều hơn trong mô hình chỉ nhìn phổi; điều đó chưa cho phép kết luận khối GLCM "quan trọng hơn" LBP ở cùng một mô hình, bởi các con số đo trên hai tập đặc trưng khác nhau sau khi che.

## 4.3. Các giả thuyết chưa kiểm chứng về thiên lệch ngoài phổi

Các nhận định trong mục này là giả thuyết. Chúng không được kiểm chứng riêng trong đề tài và được nêu ra để đánh dấu ranh giới giữa phần đo được và phần diễn giải, theo cam kết đã ghi ở mục 1.1 và quy tắc D4.

**Giả thuyết về hình học lồng ngực trẻ em ở lớp Viral Pneumonia.** Bằng chứng đo được: với toàn bộ vùng phổi bị che đen, `out_to_out` vẫn phân loại đúng 94,58% ảnh lớp này, cao nhất trong năm kịch bản. Cả 1.345 ảnh lớp thuộc một bộ Kaggle của P. Mooney, và chương 1 đã ghi khả năng đây là X-quang nhi khoa từ nghiên cứu của Kermany và cộng sự [3]. Giả thuyết: mô hình dùng các đặc điểm hình học lồng ngực trẻ em – xương sườn nằm ngang, vòm hoành cao, tỷ lệ lồng ngực nhỏ so với khung 299 × 299 – phân biệt được lớp này mà không cần tổn thương phổi. Phần chưa kiểm chứng: bộ dữ liệu không cung cấp tuổi, nên không có cách nào xác nhận các ảnh đó là của trẻ em hay phân tách đóng góp của hình học lồng ngực (`docs/dataset_provenance.md` mục 3.3; giới hạn tương tự ghi ở mục 2.5).

**Giả thuyết về ký hiệu thiết bị và nhãn nguồn ở lớp COVID.** Bằng chứng đo được: `out_to_out` phân loại đúng 94,79% ảnh COVID dù không nhìn thấy vùng mờ trong phổi. Lớp COVID ghép từ nhiều kho, gồm ảnh có ký hiệu máy chụp kỹ thuật số, chữ `L`/`R` in đậm ngoài thành ngực và độ tương phản nền đặc trưng (mục 2.1). Giả thuyết: các dấu hiệu xuất tệp và ký hiệu thiết bị đó là tín hiệu phân biệt được lớp COVID từ vùng ngoài phổi. Phần chưa kiểm chứng: thí nghiệm RQ3 không tách riêng đóng góp của từng loại dấu hiệu, và phép đo trong chương không chỉ ra được dấu hiệu nào cụ thể được dùng.

**Giả thuyết về dịch chuyển phân phối khi che lúc suy luận.** Bằng chứng đo được: `orig_to_lung` sụp xuống 0,0723 với toàn bộ ảnh dồn về nhãn COVID; `orig_to_out` sụt 0,6940 (Bảng 4.2). Giả thuyết: che một vùng làm thay đổi phân phối của cả ba khối đặc trưng – histogram cường độ, GLCM, LBP đều bị chi phối bởi dải giá trị 0 màu đen – nên mô hình đưa ra dự đoán lệch hẳn so với chế độ đã học. Phần chưa kiểm chứng: đề tài không đo phân phối đặc trưng theo từng chế độ ảnh, nên chưa có bằng chứng trực tiếp cho cơ chế này.

Các phép đo của chương đã cho thấy một điều: vùng ngoài phổi mang thông tin phân biệt được bốn lớp – mô hình chỉ nhìn vùng đó đạt 0,8921 và vượt xa các mốc nền. Chúng cũng cho thấy mô hình nhạy với sự thay đổi vùng ảnh: che khác đi ở bất kỳ thời điểm nào cũng làm giảm mạnh hiệu năng. Phần còn lại – mô hình dựa vào thuộc tính hình ảnh cụ thể nào, và liệu đó có phải là lối tắt theo nghĩa của Geirhos và cộng sự [4] – vẫn thuộc phần giả thuyết. Nguy cơ tương tự đã được ghi nhận trong y văn: mô hình phát hiện viêm phổi từ CXR giảm hiệu năng khi chuyển sang bệnh viện khác vì đã bám vào dấu hiệu đặc thù của cơ sở dữ liệu huấn luyện [5]. Một hệ thống đạt điểm cao trên bộ ghép nhiều nguồn này hoàn toàn có thể hoạt động kém khi gặp ảnh từ đường dây chụp khác; cảnh báo y khoa tương ứng nằm ở mục 6.3.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 4.1:** `results/report_rq3/r1_summary.csv` (macro-F1, khoảng tin cậy, precision/recall/F1 từng lớp của năm kịch bản), `results/report_rq3/r4_sampling_error.csv` (accuracy và sai số chuẩn theo p thực đo), `results/report_rq3/r3_shortcut_bootstrap.csv` (năm phép so ghép cặp) và `results/report_rq3/r1_bootstrap_vs_reference.csv` (bốn phép so với mốc `orig_to_orig`). Thiết kế năm kịch bản và quy tắc phép so sánh chính lấy từ `results/rq3_comparison_protocol_record.md` mục 2; quyết định giữ `orig_to_orig` lấy từ `results/rq3_shortcut_learning_conclusion.md` mục 2 và 4.
- **Mốc nền dùng ở mục 4.1:** B0 = 0,1627 đọc từ `results/b0_majority/metrics.json`; A0 = 0,2397 đọc từ `results/a0_shortcut/metrics.json` (khóa `random_forest`). Mốc histogram–RF: `results/threshold_v3.md` mục 4 đăng ký A1 = 0,7852 trước khi chạy; không tìm thấy tệp chạy nào trong repo cho ra đúng 0,7852, nên thân bài dùng số đo của lô full 0,7829 từ `results/report_rq1/r1_summary.csv` (dòng `hist`) và nêu cả hai. Kết luận "vượt mốc histogram" không đổi theo lựa chọn số nào: 0,8921 − 0,7829 = 0,1092 và 0,8921 − 0,7852 = 0,1069.
- **Ma trận nhầm lẫn của `orig_to_orig`:** giống hệt Bảng 3.5 của Chương 3 (`results/report_rq3/r1_confusion_matrices.json`), nên phân tích 349 lỗi ở mục 3.4 áp dụng nguyên cho kịch bản này; kênh chéo là cùng một cấu hình mô hình (`rq2_ghep_svm_s42` ở RQ2 và `rq3_ghep_svm_orig_to_orig_s42` ở RQ3).
- **Bảng 4.3:** `results/report_rq3/r2_normal_lung_opacity.csv` (hai ô 2×2 của mỗi kịch bản); mẫu số cố định 903 ảnh Lung_Opacity và 1.531 ảnh Normal. Tỷ lệ cặp tính trên 2.434 ảnh hai lớp, đúng mẫu số của Bảng 3.6.
- **Mặt nạ phổi:** kích thước 256 × 256 nội suy về 299 × 299 bằng `cv2.INTER_NEAREST` như mục 2.2 của Chương 2; kết quả kiểm tra hình học mặt nạ (`empty_masks_count = 0`, `all_centered = true` với 20/20 mẫu thử, `lung_fraction_mean = 0,2361`) lấy từ `results/rq3_comparison_protocol_record.md` mục 1.
- **Nguồn mục 4.2:** `results/rq3_permutation_importance.csv` (10 khối × 3 chế độ, `importance_mean`, `importance_std`, `n_repeats = 10`; seed 42 ghi ở `results/rq3_comparison_protocol_record.md` mục 2.3). Hoán vị chạy trên đúng 3.174 ảnh validation (`src/rq3_runner.py`, `compute_block_permutation_importance`, nhận `X_val`), `importance_std` tính theo mẫu (n − 1). Ba khối tổng hợp chiếm toàn bộ 152 chiều của nhóm ghép (64 + 60 + 28); bảy tiểu khối là 5 thuộc tính GLCM (12 chiều mỗi khối) và 2 miền LBP (10 và 18 chiều).
- **Giả thuyết ở mục 4.3:** không lấy lại các khẳng định nhân quả của `results/error_analysis/error_analysis_summary.md` (độ sáng, viền khung chụp, thiết bị) vì chúng không kiểm chứng được từ ảnh. Nhận định về lứa tuổi gắn với [3] và `docs/dataset_provenance.md` mục 3.3 (không có tuổi trong metadata); các trích dẫn [3], [4], [5] đã có ở danh mục tài liệu của Chương 1 nên không phát sinh số thứ tự mới.
- **Hình 4.1:** sinh bằng `python -m scripts.report_figures_rq3` từ `results/report_rq3/r1_summary.csv` (macro-F1 và khoảng tin cậy năm kịch bản) cùng ba đường mốc đọc từ `results/b0_majority/metrics.json`, `results/a0_shortcut/metrics.json` và `results/report_rq1/r1_summary.csv`. Kiểm thử `tests/test_report_figures_rq3.py` giữ thứ tự kịch bản và đối chiếu ba đường mốc với tệp nguồn.
