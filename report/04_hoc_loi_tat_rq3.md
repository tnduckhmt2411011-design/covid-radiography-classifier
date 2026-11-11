# CHƯƠNG 4. MỨC PHỤ THUỘC VÀO VÙNG NGOÀI PHỔI (RQ3)

## 4.1. Năm kịch bản che mặt nạ phổi

RQ3 hỏi che vùng ảnh theo mặt nạ phổi có làm thay đổi macro-F1 không, và mức thay đổi đó cho biết gì về mức phụ thuộc của mô hình vào vùng ngoài phổi (mục 1.1). Phép che được thực hiện bằng cách đặt giá trị điểm ảnh về 0 (màu đen) ở vùng được giữ lại hoặc vùng bị loại, không cắt hay thu nhỏ khung ảnh. Ba chế độ mặt nạ – ảnh gốc, chỉ giữ vùng phổi, chỉ giữ vùng ngoài phổi – ghép thành năm kịch bản huấn luyện–đánh giá, đã đóng băng trong biên bản trước khi chạy lô full. Mô hình của cả năm kịch bản là cấu hình đã khóa từ RQ2: SVM kernel RBF, C = 10, gamma = scale, trọng số lớp cân bằng, kết hợp StandardScaler chỉ fit trên train tương ứng, trên nhóm đặc trưng ghép 152 chiều, seed 42.

Mặt nạ phổi đi kèm bộ dữ liệu ở kích thước 256 × 256 nên được nội suy về 299 × 299 bằng láng giềng gần nhất trước khi dùng (mục 2.2). Trong phiên chạy thử kỹ thuật trên 20 mẫu, không có mặt nạ rỗng sau nội suy, trọng tâm vùng phổi nằm gần trung tâm ảnh, và vùng phổi chiếm trung bình 23,6% diện tích ảnh. Phép kiểm này chỉ xác nhận mặt nạ dùng được, không kiểm được mặt nạ có khớp biên phổi thật. Vai trò của năm kịch bản như sau.

| Kịch bản | Ảnh train | Ảnh validation | Vai trò |
| :--- | :--- | :--- | :--- |
| `orig_to_orig` | `original` | `original` | Tham chiếu: cấu hình chuẩn đã khóa ở RQ2, ảnh gốc không che |
| `lung_to_lung` | `lung_only` | `lung_only` | Ứng viên thay thế cấu hình chính thức: chỉ còn vùng phổi ở cả hai tập |
| `out_to_out` | `outside_only` | `outside_only` | Đối chứng lối tắt: chỉ còn vùng ngoài phổi ở cả hai tập |
| `orig_to_lung` | `original` | `lung_only` | Nhiễu suy luận: bộ gốc gặp ảnh chỉ còn vùng phổi lúc đánh giá |
| `orig_to_out` | `original` | `outside_only` | Nhiễu suy luận: bộ gốc gặp ảnh chỉ còn vùng ngoài phổi lúc đánh giá |

**Bảng 4.1: Macro-F1, khoảng tin cậy và accuracy của năm kịch bản trên 3.174 ảnh validation**

| Kịch bản | Macro-F1 | 95% CI | Accuracy | Recall COVID | Recall Lung_Opacity | Recall Normal | Recall Viral Pneumonia |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| `orig_to_orig` | 0,9024 | [0,8909; 0,9129] | 89,00% | 95,72% | 84,94% | 88,37% | 94,09% |
| `lung_to_lung` | 0,8490 | [0,8333; 0,8625] | 85,44% | 86,59% | 81,40% | 86,54% | 92,12% |
| `out_to_out` | 0,8921 | [0,8807; 0,9031] | 87,84% | 94,79% | 83,17% | 87,26% | 94,58% |
| `orig_to_lung` | 0,0723 | [0,0677; 0,0770] | 16,89% | 99,81% | 0,00% | 0,00% | 0,00% |
| `orig_to_out` | 0,2084 | [0,1953; 0,2220] | 27,22% | 93,85% | 27,35% | 7,32% | 0,49% |

*(Macro-F1, khoảng tin cậy và recall từng lớp đọc từ tệp tổng hợp RQ3; accuracy đọc từ tệp sai số lấy mẫu. Khoảng tin cậy của từng kịch bản là bootstrap 2.000 lần trên 3.174 ảnh, seed 42. Đường dẫn tệp nằm ở Ghi chú kỹ thuật cuối chương.)*

Cả ba kịch bản huấn luyện–đánh giá cùng chế độ đều vượt xa hai mốc nền: B0 = 0,1627 của bộ đọc luôn nhãn Normal và A0 = 0,2397 của bộ Random Forest đọc thuộc tính tệp ảnh (độ sáng, hệ màu). Kịch bản chỉ giữ vùng ngoài mặt nạ phổi đạt 0,8921, cao hơn cả hai mốc này. Con số này cho thấy vùng ngoài mặt nạ phổi mang đủ thông tin để phân biệt bốn lớp, nhưng chưa cho biết thông tin đó là gì; phần giới hạn của phép che nằm ở cuối mục này. Hai kịch bản nhiễu suy luận nằm dưới các mốc nền: chỉ giữ vùng ngoài phổi lúc đánh giá đạt 0,2084 (trên B0, dưới A0); chỉ giữ vùng phổi lúc đánh giá đạt 0,0723, tương đương một bộ phân loại đọc một nhãn (macro-F1 0,0724 tính trên chính tập validation).

**Bảng 4.2: Phép so sánh ghép cặp giữa các kịch bản (bootstrap 2.000 lần, n = 3.174)**

| Cặp so sánh | Chênh macro-F1 | 95% CI của chênh | Khoảng chứa 0 | Vai trò của phép so |
| :--- | ---: | :--- | :---: | :--- |
| `orig_to_orig` − `lung_to_lung` | +0,0535 | [+0,0392; +0,0691] | Không | Phép so chính, đóng băng trước khi xem điểm |
| `orig_to_orig` − `out_to_out` | +0,0103 | [−0,0017; +0,0220] | Có | Đối chiếu bổ sung với mốc |
| `orig_to_orig` − `orig_to_lung` | +0,8302 | [+0,8181; +0,8415] | Không | Đối chiếu bổ sung với mốc |
| `orig_to_orig` − `orig_to_out` | +0,6940 | [+0,6772; +0,7110] | Không | Đối chiếu bổ sung với mốc |
| `out_to_out` − `lung_to_lung` | +0,0431 | [+0,0281; +0,0582] | Không | Bắt buộc trình bày theo biên bản RQ3 |

*(Năm dòng đọc từ tệp kết quả kiểm định RQ3: mỗi lần lấy mẫu dùng một tập vị trí ảnh chung cho cả hai kịch bản nên phép so là ghép cặp. Phép so chính và phép bắt buộc trình bày được đăng ký trong biên bản trước khi chạy; các dòng còn lại do pipeline báo cáo tính thêm.)*

Phép so sánh chính của RQ3, đã đóng băng trước khi xem điểm, đối chiếu ứng viên `lung_to_lung` với mốc `orig_to_orig` theo quy tắc chuyển đổi giống RQ1 và RQ2: chênh ít nhất +0,005 và khoảng tin cậy 95% không chứa 0. Chênh đo được là −0,0535 với khoảng [−0,0691; −0,0392], nên việc chỉ giữ vùng phổi làm giảm macro-F1 có ý nghĩa thống kê và không thỏa điều kiện thay thế. Cấu hình ảnh gốc `orig_to_orig` vì thế được giữ làm cấu hình chính thức để đánh giá một lần trên tập test (kết quả trên tập test thuộc Chương 5).

Chênh giữa ảnh gốc và ảnh chỉ còn vùng ngoài mặt nạ phổi là +0,0103, khoảng tin cậy [−0,0017; +0,0220] chứa 0. Kết quả này chưa đủ để nói hai mô hình khác nhau, nhưng cũng chưa đủ để nói chúng tương đương: cận trên +0,0220 vẫn lớn hơn ngưỡng 0,005 của quy tắc ở trên. Mô hình chỉ nhìn vùng ngoài mặt nạ phổi còn cao hơn mô hình chỉ nhìn vùng trong mặt nạ phổi 0,0431 [+0,0281; +0,0582]; phép so này không thuộc phép so sánh chính nên được xem là khảo sát bổ sung có đăng ký trước.

Mức giảm recall của kịch bản chỉ giữ vùng phổi so với ảnh gốc không đều giữa các lớp: COVID −9,13 điểm, Lung_Opacity −3,54, Viral Pneumonia −1,97 và Normal −1,83. Phần lớn macro-F1 mất đi do lớp COVID. Ở kịch bản chỉ giữ vùng ngoài phổi, COVID chỉ giảm 0,93 điểm.

Hai kịch bản nhiễu suy luận đi theo hướng khác: khi bộ phân loại học trên ảnh gốc gặp ảnh bị che một vùng ở thời điểm đánh giá, macro-F1 giảm 0,8302 và 0,6940. Ở kịch bản chỉ giữ vùng phổi lúc đánh giá, 3.172 trong 3.174 ảnh được đoán thành COVID, và recall COVID đạt 99,81% trong khi precision của lớp đó chỉ 0,1690.

**Bảng 4.3: Cặp nhầm lẫn Normal ↔ Lung_Opacity theo ba kịch bản cùng chế độ**

| Kịch bản | Lung_Opacity → Normal | Normal → Lung_Opacity | Tổng lỗi cặp | Tỷ lệ trên 2.434 ảnh hai lớp |
| :--- | ---: | ---: | ---: | ---: |
| `orig_to_orig` | 124 (13,73%) | 144 (9,41%) | 268 | 11,01% |
| `lung_to_lung` | 105 (11,63%) | 101 (6,60%) | 206 | 8,46% |
| `out_to_out` | 138 (15,28%) | 158 (10,32%) | 296 | 12,16% |

*(Bốn ô đếm đọc từ tệp tổng hợp cặp nhầm của RQ3; mẫu số cố định cho cả ba kịch bản là 903 ảnh Lung_Opacity và 1.531 ảnh Normal. Hai kịch bản nhiễu suy luận không đưa vào bảng vì mô hình đã không còn phân loại được các lớp: ở kịch bản chỉ giữ vùng phổi lúc đánh giá, 99,9% ảnh bị đoán thành COVID; ở kịch bản chỉ giữ vùng ngoài phổi lúc đánh giá, tỷ lệ này là 80,2%.)*

Cặp nhầm nặng nhất của Chương 3 giảm khi mô hình chỉ nhìn trong phổi: 268 lỗi của ảnh gốc xuống 206, và giảm ở cả hai chiều. Cặp này lại tăng lên 296 khi mô hình chỉ nhìn ngoài phổi. Tổng số lỗi của kịch bản chỉ giữ vùng phổi là 462, tức các cặp nhầm khác tệ hơn rõ: 256 lỗi ngoài cặp Normal–Lung_Opacity so với 81 của ảnh gốc, đúng với mức giảm macro-F1 0,0535. Chương không kết luận vì sao phép che làm lệch cặp nhầm theo hướng đó.

**Bảng 4.4: Phép tách theo nguồn ảnh trên ba kịch bản cùng chế độ**

| Kịch bản | Lỗi cặp Normal–Lung_Opacity trong 2.237 ảnh RSNA | 197 ảnh Normal nguồn Mooney bị đoán thành Viral Pneumonia |
| :--- | ---: | ---: |
| `orig_to_orig` | 243 (10,86%) | 0 |
| `lung_to_lung` | 186 (8,31%) | 0 |
| `out_to_out` | 265 (11,85%) | 0 |

*(Hai nhóm được lập từ chính tập validation nên tổng số ảnh không đổi giữa các kịch bản. Cách tính và nguồn từng cột ghi ở Ghi chú kỹ thuật.)*

Phép tách theo nguồn cho hai kết quả đo được. Thứ nhất, lớp Lung_Opacity và lớp Normal cùng nguồn RSNA, nên nguồn ảnh không thể là thứ tách hai lớp này; ở kịch bản chỉ giữ vùng ngoài mặt nạ phổi, lỗi cặp giữa chúng vẫn ở mức gần bằng ảnh gốc (11,85% so với 10,86%). Vùng ngoài mặt nạ phổi vì thế mang thông tin liên quan đến lớp, không chỉ liên quan đến nguồn ảnh. Thứ hai, 197 ảnh Normal nguồn Mooney – cùng nguồn với lớp Viral Pneumonia – không ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản, kể cả khi vùng phổi bị che hoàn toàn; chiều ngược lại, ảnh Viral Pneumonia bị đoán thành Normal là 7, 5 và 6 ảnh. Recall của lớp Viral Pneumonia ở ba kịch bản là 94,09%, 92,12% và 94,58% (Bảng 4.1); recall của 197 ảnh Normal nguồn Mooney là 87,31%, 83,25% và 83,25%.

Hai kết quả trên cần đọc cùng giới hạn của phép che. Ở chế độ chỉ còn vùng ngoài phổi, mô hình không thấy cường độ điểm ảnh bên trong mặt nạ phổi, nhưng vẫn thấy hình dạng, diện tích và vị trí của vùng bị che (trung bình 23,6% ảnh), và các đặc trưng histogram, GLCM, LBP đều có thể phản ứng với vùng đen này cùng đường viền của nó. Vùng ngoài mặt nạ còn gồm tim, trung thất, vòm hoành và thành ngực, là những vùng có thông tin lâm sàng. Mặt nạ trong bộ dữ liệu do mạng phân đoạn tự sinh chứ không phải bác sĩ vẽ: hai bài báo mô tả bộ dữ liệu không cung cấp mặt nạ chuẩn cho tập phân loại, và nguồn gốc mặt nạ của 2.686 ảnh thuộc nguồn Mooney không được mô tả (`docs/dataset_provenance.md` mục 3.2). Vì vậy "ngoài mặt nạ phổi" chưa chắc đã là "ngoài phổi", và mặt nạ cũng có thể không bao hết vùng tổn thương. Điểm của chế độ chỉ còn vùng ngoài phổi vì thế không cho biết thông tin được dùng là thông tin về nguồn ảnh hay là thông tin giải phẫu.

![Macro-F1 của năm kịch bản RQ3 kèm khoảng tin cậy và các mốc nền](../figures/04_macro_f1_kich_ban_rq3.png)

**Hình 4.1: Macro-F1 năm kịch bản RQ3 trên 3.174 ảnh validation, cột là điểm ước lượng và que chỉ khoảng tin cậy 95%**

Hai đường gạch ngang là mốc nền B0 (bộ đọc luôn nhãn Normal) và A0 (bộ Random Forest đọc thuộc tính tệp ảnh), cùng đọc từ tệp kết quả của hai mốc đó.

## 4.2. Tầm quan trọng đặc trưng theo 10 khối

Thí nghiệm hoán vị khối đo mức sụt macro-F1 khi xáo trộn ngẫu nhiên một nhóm chiều đặc trưng rồi suy luận lại, giữ nguyên các khối còn lại, trên đúng 3.174 ảnh validation. Mỗi khối được xáo trộn 10 lần; dao động giữa 10 lần xáo trộn trên cùng một tập ảnh được ghi sau dấu ±, không phải độ bất định theo mẫu ảnh. Mười khối gồm ba khối tổng hợp – histogram 64 chiều, GLCM 60 chiều, LBP 28 chiều – và bảy tiểu khối: năm thuộc tính GLCM 12 chiều mỗi khối và hai miền LBP của 10 và 18 chiều. Ba khối tổng hợp và bảy tiểu khối lồng trong nhau (ba khối tổng hợp đúng bằng 152 chiều của nhóm ghép), nên mức sụt của các khối không cộng được. Ba chế độ ảnh `original`, `lung_only`, `outside_only` được đo riêng, baseline mỗi chế độ là macro-F1 của chính kịch bản đó ở Bảng 4.1.

**Bảng 4.5: Mức sụt macro-F1 khi hoán vị từng khối (10 lần xáo trộn, trên 3.174 ảnh validation)**

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

*(Toàn bộ con số đọc từ tệp kết quả hoán vị khối của RQ3; baseline của ba chế độ là 0,9024, 0,8490 và 0,8921.)*

Trên ảnh gốc, thứ tự mức sụt của ba khối tổng hợp là LBP 0,3590, GLCM 0,3264 rồi histogram 0,2863; chênh giữa khối đầu và khối cuối là 0,0727, gấp hơn sáu lần dao động 10 lần xáo trộn. Kết quả thay đổi khi vùng phổi là vùng duy nhất còn lại: khối GLCM lên 0,4960 (+0,1696 so với ảnh gốc) và vượt LBP (0,4283), hai thuộc tính dẫn đầu trong chế độ này là dissimilarity (0,4655) và contrast (0,3163). Trên chế độ chỉ còn ngoài phổi, thứ tự quay về gần giống ảnh gốc: LBP 0,3590, GLCM 0,3526, histogram 0,2656, và tiểu khối LBP bán kính 2 (0,2746) cao nhất trong bảy tiểu khối.

Hai thuộc tính dissimilarity và contrast đo sự khác biệt cường độ giữa các cặp điểm ảnh kề nhau. Khi phần lớn ảnh là nền đen, hai thuộc tính này có thể chủ yếu đo độ dài đường viền vùng bị che; khả năng đó chưa được loại trừ, nên chưa kết luận được chúng đang đo kết cấu nhu mô phổi. Một điểm cần chú ý khác: baseline của ba chế độ khác nhau (0,9024, 0,8490 và 0,8921) nên con số trong bảng là mức sụt đo được trên từng mô hình; việc GLCM sụt nhiều hơn trên chế độ chỉ còn vùng phổi cho thấy khối này đóng góp nhiều hơn trong mô hình chỉ nhìn vùng phổi, chứ chưa cho phép kết luận khối GLCM quan trọng hơn LBP trong cùng một mô hình.

## 4.3. Các giả thuyết chưa kiểm chứng về vùng ngoài phổi

Các nhận định trong mục này là giả thuyết. Chúng không được kiểm chứng riêng trong đề tài và được nêu ra để đánh dấu ranh giới giữa phần đo được và phần diễn giải, theo cam kết đã ghi ở mục 1.1.

**Giả thuyết về đặc điểm giải phẫu lồng ngực trẻ nhỏ ở lớp Viral Pneumonia.** Bằng chứng đo được: với toàn bộ vùng phổi bị che đen, kịch bản chỉ còn vùng ngoài phổi vẫn phân loại đúng 94,58% ảnh lớp này và đạt recall 0,49 điểm cao hơn ảnh gốc, nhưng precision thấp hơn (89,72% so với 91,39%) nên F1 của lớp thấp hơn (0,9209 so với 0,9272). Cả 1.345 ảnh lớp thuộc nguồn Mooney, và Chương 1 đã ghi khả năng đây là X-quang nhi khoa từ nghiên cứu của Kermany và cộng sự [3]. Giả thuyết: mô hình dùng đặc điểm giải phẫu lồng ngực trẻ nhỏ để nhận ra lớp này mà không cần tổn thương phổi. Giả thuyết này chưa được kiểm chứng, và bằng chứng hiện có còn đi ngược một phần: 197 ảnh Normal cùng nguồn Mooney – vì thế cùng lứa tuổi suy ra – không ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản, kể cả kịch bản chỉ còn vùng ngoài phổi (Bảng 4.4). Nếu tín hiệu phân biệt chỉ là "ảnh nhi khoa", nhóm này đáng ra phải bị nhầm. Bộ dữ liệu không cung cấp tuổi, nên không có cách nào xác nhận các ảnh đó là của trẻ em hay phân tách đóng góp của hình học lồng ngực (`docs/dataset_provenance.md` mục 3.3; giới hạn tương tự ghi ở mục 2.5).

**Giả thuyết về ký hiệu thiết bị và dấu vết xuất tệp ở lớp COVID.** Bằng chứng đo được: kịch bản chỉ còn vùng ngoài phổi phân loại đúng 94,79% ảnh COVID (precision 93,39%, F1 0,9409) dù không nhìn thấy vùng mờ trong phổi. Lớp COVID ghép từ nhiều kho, gồm ảnh có ký hiệu máy chụp kỹ thuật số, chữ `L`/`R` in đậm ngoài thành ngực và độ tương phản nền đặc trưng (mục 2.1). Giả thuyết: các dấu hiệu xuất tệp và ký hiệu thiết bị đó là tín hiệu phân biệt được lớp COVID từ vùng ngoài phổi. Phần chưa kiểm chứng: thí nghiệm RQ3 không tách riêng đóng góp của từng loại dấu hiệu, và phép đo trong chương không chỉ ra được dấu hiệu nào cụ thể được dùng.

**Giả thuyết về dịch chuyển phân phối khi che lúc suy luận.** Bằng chứng đo được: kịch bản học trên ảnh gốc rồi gặp ảnh chỉ còn vùng phổi lúc đánh giá sụt xuống 0,0723, với 3.172 trong 3.174 ảnh bị đoán thành COVID; kịch bản gặp ảnh chỉ còn vùng ngoài phổi sụt 0,6940, với 80,2% ảnh bị đoán thành COVID. Giả thuyết: che một vùng làm thay đổi phân phối của cả ba khối đặc trưng – histogram cường độ, GLCM, LBP đều bị chi phối bởi dải giá trị 0 màu đen – nên mô hình đưa ra dự đoán lệch hẳn so với chế độ đã học. Phần chưa kiểm chứng: đề tài không đo phân phối đặc trưng theo từng chế độ ảnh, nên chưa có bằng chứng trực tiếp cho cơ chế này.

Chương đo được rằng mô hình vẫn đạt macro-F1 0,8921 khi chỉ còn vùng ngoài mặt nạ phổi, nên vùng này đủ thông tin để phân biệt bốn lớp; phép tách theo nguồn thêm cho thấy vùng này còn tách được hai lớp cùng nguồn RSNA. Che nhất quán ở cả huấn luyện và đánh giá chỉ làm giảm macro-F1 0,0103 (che phổi) hoặc 0,0535 (che ngoài phổi), trong khi che riêng lúc đánh giá làm mô hình học trên ảnh gốc gần như mất khả năng phân loại. Chương không xác định được mô hình dùng đặc điểm nào trong vùng ngoài phổi, và không xác định được đó có phải lối tắt theo nghĩa của Geirhos và cộng sự [4] hay không. Nghiên cứu [5] ghi nhận mô hình CXR giảm hiệu năng khi sang cơ sở y tế khác; điểm validation cao trên bộ ghép nhiều nguồn này chưa bảo đảm mô hình hoạt động tương tự ở nơi khác (mục 6.3).

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 4.1:** `results/report_rq3/r1_summary.csv` (macro-F1, khoảng tin cậy, precision/recall/F1 từng lớp của năm kịch bản), `results/report_rq3/r4_sampling_error.csv` (accuracy), `results/report_rq3/r3_shortcut_bootstrap.csv` (năm phép so ghép cặp), `results/report_rq3/r2_normal_lung_opacity.csv` (cặp nhầm Normal–Lung_Opacity của từng kịch bản) và `results/report_rq3/r1_confusion_matrices.json`. Thiết kế năm kịch bản, quy tắc phép so sánh chính và mục bắt buộc trình bày lấy từ `results/rq3_comparison_protocol_record.md` mục 2; quyết định giữ `orig_to_orig` lấy từ `results/rq3_shortcut_learning_conclusion.md` mục 2 và 4.
- **Mốc nền dùng ở mục 4.1:** B0 = 0,1627 đọc từ `results/b0_majority/metrics.json`; A0 = 0,2397 đọc từ `results/a0_shortcut/metrics.json` (khóa `random_forest`) – bộ này đọc thuộc tính tệp ảnh, cùng cách mô tả như mục 3.1 của Chương 3. Mốc histogram với Random Forest được đăng ký trước khi chạy lô full ở mức 0,7852 (`results/threshold_v3.md` mục 4); lô full RQ1 sau đó đo được 0,7829 (`results/report_rq1/r1_summary.csv`, dòng `hist`, trung bình ba seed), nên báo cáo dùng số đo có tệp nguồn đi kèm. Phép so đó khác bộ phân loại và nhóm đặc trưng nên chỉ mang tính mốc đăng ký trước, không phải so cùng điều kiện.
- **Con số 0,0724** là macro-F1 của một bộ phân loại đọc toàn bộ ảnh về nhãn COVID, tính từ chính cột nhãn thực trong `results/rq3_ghep_svm_orig_to_orig_s42/preds_val.csv`. Tỷ lệ ảnh bị đoán thành COVID (99,9% và 80,2%) đếm từ cột nhãn dự đoán của hai kịch bản nhiễu tương ứng.
- **Bảng 4.3:** `results/report_rq3/r2_normal_lung_opacity.csv`; mẫu số cố định 903 ảnh Lung_Opacity và 1.531 ảnh Normal, đúng mẫu số của Bảng 3.6. Tổng lỗi của kịch bản chỉ giữ vùng phổi là 462 ảnh, tính từ ma trận nhầm lẫn trong `r1_confusion_matrices.json` (3.174 − 2.712 nhãn đúng).
- **Bảng 4.4:** cột lỗi cặp tính trên nhóm 2.237 ảnh cùng nguồn RSNA (903 Lung_Opacity + 1.334 Normal RSNA); cột nguồn Mooney tính trên nhóm 400 ảnh (203 Viral Pneumonia + 197 Normal nguồn Mooney). Nguồn ảnh của lớp Normal lấy từ `results/eda/normal_source_labels.csv` ghép với `splits/split_v1.csv`; nhãn dự đoán của ba kịch bản lấy từ `results/rq3_ghep_svm_{orig_to_orig,lung_to_lung,out_to_out}_s42/preds_val.csv`. Tỷ lệ 10,86 / 8,31 / 11,85% là tổng hai chiều nhầm chia cho 2.237. Lớp Lung_Opacity toàn bộ thuộc cuộc thi RSNA và lớp Viral Pneumonia toàn bộ thuộc nguồn Mooney (mục 2.1 của Chương 2), nên hai nhóm này thực sự đồng nguồn.
- **Mặt nạ phổi:** kích thước 256 × 256 nội suy về 299 × 299 bằng láng giềng gần nhất như mục 2.2 của Chương 2; kết quả kiểm tra trên 20 mẫu thử (`empty_masks_count = 0`, trọng tâm gần trung tâm, `lung_fraction_mean = 0,2361`) lấy từ `results/rq3_comparison_protocol_record.md` mục 1. Mặt nạ do mạng Modified U-Net sinh, không có mặt nạ chuẩn cho tập phân loại và không có mô tả nguồn gốc mặt nạ cho 2.686 ảnh thuộc nguồn Mooney: `docs/dataset_provenance.md` mục 3.2 và hàng H5.
- **Mức giảm recall ở mục 4.1** (COVID −9,13 điểm, Lung_Opacity −3,54, Viral Pneumonia −1,97, Normal −1,83, và −0,93 của COVID ở kịch bản chỉ giữ vùng ngoài phổi) tính bằng phép trừ hai cột đã làm tròn của Bảng 4.1; nếu tính từ giá trị chưa làm tròn, mức COVID là −9,12.
- **Nguồn mục 4.2:** `results/rq3_permutation_importance.csv` (10 khối × 3 chế độ, `importance_mean`, `importance_std`, `n_repeats = 10`; seed 42 ghi ở `results/rq3_comparison_protocol_record.md` mục 2.3). Hoán vị chạy trên đúng 3.174 ảnh validation (`src/rq3_runner.py`, hàm `compute_block_permutation_importance`), `importance_std` tính theo mẫu (n − 1) và là dao động giữa các lần xáo trộn trên cùng tập ảnh.
- **Giả thuyết ở mục 4.3:** không lấy lại các khẳng định nhân quả của `results/error_analysis/error_analysis_summary.md` (độ sáng, viền khung chụp, thiết bị) vì chúng không kiểm chứng được từ ảnh. Nhận định về lứa tuổi gắn với [3] và `docs/dataset_provenance.md` mục 3.3 (không có tuổi trong metadata); các trích dẫn [3], [4], [5] đã có ở danh mục tài liệu của Chương 1 nên không phát sinh số thứ tự mới.
- **Hình 4.1:** sinh bằng `python -m scripts.report_figures_rq3` từ `results/report_rq3/r1_summary.csv` (macro-F1 và khoảng tin cậy năm kịch bản) cùng hai đường mốc đọc từ `results/b0_majority/metrics.json` và `results/a0_shortcut/metrics.json`. Kiểm thử `tests/test_report_figures_rq3.py` giữ thứ tự kịch bản và đối chiếu hai đường mốc với tệp nguồn.
