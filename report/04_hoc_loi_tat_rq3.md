# CHƯƠNG 4. MỨC PHỤ THUỘC VÀO VÙNG NGOÀI PHỔI (RQ3)

## 4.1. Năm kịch bản che mặt nạ phổi

RQ3 hỏi hai điều: che vùng ảnh theo mặt nạ phổi có làm macro-F1 thay đổi không, và mức thay đổi đó cho biết mô hình dựa vào vùng ngoài mặt nạ phổi đến đâu (mục 1.2).

Phép che đặt điểm ảnh về 0 (màu đen) ở vùng bị loại. Khung ảnh giữ nguyên, không cắt hay thu nhỏ. Ba chế độ ảnh gồm ảnh gốc, chỉ giữ vùng phổi và chỉ giữ vùng ngoài mặt nạ phổi được ghép thành năm kịch bản huấn luyện–đánh giá, và năm kịch bản này đã được chốt trong biên bản trước khi chạy lô đầy đủ. Cả năm dùng đúng cấu hình đã khóa ở RQ2: SVM kernel RBF, C = 10, gamma = scale, trọng số lớp cân bằng, đặt sau StandardScaler chỉ fit trên tập train tương ứng, trên nhóm đặc trưng ghép 152 chiều, seed 42.

Mặt nạ phổi đi kèm bộ dữ liệu có kích thước 256 × 256, nên được nội suy láng giềng gần nhất lên 299 × 299 trước khi dùng (mục 2.1). Chạy thử kỹ thuật trên 20 mẫu cho thấy không có mặt nạ rỗng sau nội suy, trọng tâm vùng phổi nằm gần trung tâm ảnh và vùng phổi chiếm trung bình 23,6% diện tích. Phép thử này chỉ xác nhận mặt nạ dùng được, không xác nhận mặt nạ khớp với biên phổi thật.

Để gọn, từ đây ba kịch bản dùng cùng một chế độ ở cả hai tập được gọi là "ảnh gốc", "chỉ phổi" và "chỉ ngoài phổi". Hai kịch bản còn lại giữ tên như ở Hình 4.1.

| Kịch bản | Ảnh train | Ảnh validation | Vai trò | Mã trong kho mã nguồn |
| :--- | :--- | :--- | :--- | :--- |
| Ảnh gốc cả hai tập | Gốc | Gốc | Tham chiếu: cấu hình chuẩn đã khóa ở RQ2, ảnh không che | `orig_to_orig` |
| Chỉ phổi cả hai tập | Chỉ phổi | Chỉ phổi | Ứng viên thay thế cấu hình chính thức: chỉ còn vùng phổi ở cả hai tập | `lung_to_lung` |
| Chỉ ngoài phổi cả hai tập | Chỉ ngoài phổi | Chỉ ngoài phổi | Đối chứng lối tắt: chỉ còn vùng ngoài mặt nạ phổi ở cả hai tập | `out_to_out` |
| Gốc học, phổi đánh giá | Gốc | Chỉ phổi | Nhiễu suy luận: bộ học trên ảnh gốc gặp ảnh chỉ còn vùng phổi lúc đánh giá | `orig_to_lung` |
| Gốc học, ngoài phổi đánh giá | Gốc | Chỉ ngoài phổi | Nhiễu suy luận: bộ học trên ảnh gốc gặp ảnh chỉ còn vùng ngoài mặt nạ phổi lúc đánh giá | `orig_to_out` |

**Bảng 4.1: Macro-F1, khoảng tin cậy và accuracy của năm kịch bản trên 3.174 ảnh validation**

| Kịch bản | Macro-F1 | 95% CI | Accuracy | Recall COVID | Recall Lung_Opacity | Recall Normal | Recall Viral Pneumonia |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| Ảnh gốc cả hai tập | 0,9024 | [0,8909; 0,9129] | 89,00% | 95,72% | 84,94% | 88,37% | 94,09% |
| Chỉ phổi cả hai tập | 0,8490 | [0,8333; 0,8625] | 85,44% | 86,59% | 81,40% | 86,54% | 92,12% |
| Chỉ ngoài phổi cả hai tập | 0,8921 | [0,8807; 0,9031] | 87,84% | 94,79% | 83,17% | 87,26% | 94,58% |
| Gốc học, phổi đánh giá | 0,0723 | [0,0677; 0,0770] | 16,89% | 99,81% | 0,00% | 0,00% | 0,00% |
| Gốc học, ngoài phổi đánh giá | 0,2084 | [0,1953; 0,2220] | 27,22% | 93,85% | 27,35% | 7,32% | 0,49% |

*(Khoảng tin cậy của từng kịch bản là bootstrap 2.000 lần trên 3.174 ảnh, seed 42.)*

Ba kịch bản dùng cùng một chế độ ảnh ở cả hai tập đều vượt xa hai mốc nền: B0 = 0,1627 (bộ luôn đoán Normal) và A0 = 0,2397 (Random Forest chỉ đọc độ sáng và hệ màu của tệp ảnh). Đáng chú ý nhất là kịch bản chỉ ngoài phổi, đạt 0,8921 dù mô hình không nhìn thấy cường độ điểm ảnh bên trong mặt nạ phổi. Vậy vùng ngoài mặt nạ mang đủ thông tin để phân biệt bốn lớp. Thông tin đó là gì thì phép đo chưa trả lời được, và giới hạn của phép che sẽ được bàn ở cuối mục.

Hai kịch bản nhiễu suy luận thì rơi xuống gần hoặc dưới các mốc nền. Khi chỉ giữ vùng ngoài mặt nạ phổi lúc đánh giá, macro-F1 là 0,2084, trên B0 nhưng dưới A0. Khi chỉ giữ vùng phổi lúc đánh giá, macro-F1 chỉ còn 0,0723, ngang một bộ phân loại chỉ trả về một nhãn (macro-F1 của bộ đó trên chính tập validation là 0,0724).

**Bảng 4.2: Phép so sánh ghép cặp giữa các kịch bản (bootstrap 2.000 lần, n = 3.174)**

| Cặp so sánh | Chênh macro-F1 | 95% CI của chênh | Khoảng chứa 0 | Vai trò của phép so |
| :--- | ---: | :--- | :---: | :--- |
| Ảnh gốc − chỉ phổi | +0,0535 | [+0,0392; +0,0691] | Không | Phép so chính, chốt trước khi xem điểm |
| Ảnh gốc − chỉ ngoài phổi | +0,0103 | [−0,0017; +0,0220] | Có | Đối chiếu bổ sung với mốc |
| Ảnh gốc − gốc học, phổi đánh giá | +0,8302 | [+0,8181; +0,8415] | Không | Đối chiếu bổ sung với mốc |
| Ảnh gốc − gốc học, ngoài phổi đánh giá | +0,6940 | [+0,6772; +0,7110] | Không | Đối chiếu bổ sung với mốc |
| Chỉ ngoài phổi − chỉ phổi | +0,0431 | [+0,0281; +0,0582] | Không | Bắt buộc trình bày theo biên bản RQ3 |

*(Mỗi lần lấy mẫu dùng một tập vị trí ảnh chung cho cả hai kịch bản nên phép so là ghép cặp. Phép so chính và phép bắt buộc trình bày được đăng ký trong biên bản trước khi chạy; các dòng còn lại do pipeline báo cáo tính thêm.)*

Phép so chính của RQ3 được chốt trước khi xem điểm: đối chiếu "chỉ phổi" với "ảnh gốc" theo quy tắc quen thuộc từ RQ1 và RQ2, tức chênh lệch phải đạt ít nhất +0,005 và khoảng tin cậy 95% không chứa 0. Kết quả là "chỉ phổi" thấp hơn "ảnh gốc" 0,0535 (Bảng 4.2), với khoảng [−0,0691; −0,0392]. Như vậy việc chỉ giữ vùng phổi làm macro-F1 giảm có ý nghĩa thống kê, và cấu hình này không đủ điều kiện thay thế. Cấu hình "ảnh gốc" được giữ làm cấu hình chính thức để đánh giá một lần trên tập test (kết quả ở Chương 5).

Giữa "ảnh gốc" và "chỉ ngoài phổi", chênh lệch là +0,0103 và khoảng tin cậy [−0,0017; +0,0220] chứa 0. Kết quả này chưa đủ để nói hai mô hình khác nhau, nhưng cũng chưa đủ để nói chúng tương đương, vì cận trên +0,0220 vẫn lớn hơn ngưỡng 0,005 của quy tắc trên. Mô hình "chỉ ngoài phổi" còn cao hơn mô hình "chỉ phổi" 0,0431 [+0,0281; +0,0582]. Phép so này không thuộc phép so chính; biên bản RQ3 vẫn yêu cầu trình bày nó, nên đây là khảo sát bổ sung có đăng ký trước.

Mức giảm recall của "chỉ phổi" so với "ảnh gốc" không đều giữa các lớp: COVID giảm 9,13 điểm, Lung_Opacity 3,54, Viral Pneumonia 1,97 và Normal 1,83. Phần lớn macro-F1 mất đi nằm ở lớp COVID. Với "chỉ ngoài phổi", recall COVID chỉ giảm 0,93 điểm.

Hai kịch bản nhiễu suy luận đi theo hướng khác. Khi bộ phân loại học trên ảnh gốc gặp ảnh bị che lúc đánh giá, macro-F1 giảm 0,8302 (ảnh chỉ phổi) và 0,6940 (ảnh chỉ ngoài phổi). Với ảnh chỉ phổi, 3.172 trong 3.174 ảnh bị đoán thành COVID: recall COVID đạt 99,81% nhưng precision của lớp này chỉ là 0,1690.

**Bảng 4.3: Cặp nhầm lẫn Normal ↔ Lung_Opacity theo ba kịch bản cùng chế độ**

| Kịch bản | Lung_Opacity → Normal | Normal → Lung_Opacity | Tổng lỗi cặp | Tỷ lệ trên 2.434 ảnh hai lớp |
| :--- | ---: | ---: | ---: | ---: |
| Ảnh gốc | 124 (13,73%) | 144 (9,41%) | 268 | 11,01% |
| Chỉ phổi | 105 (11,63%) | 101 (6,60%) | 206 | 8,46% |
| Chỉ ngoài phổi | 138 (15,28%) | 158 (10,32%) | 296 | 12,16% |

*(Mẫu số cố định cho cả ba kịch bản là 903 ảnh Lung_Opacity và 1.531 ảnh Normal. Hai kịch bản nhiễu suy luận không đưa vào bảng vì mô hình đã không còn phân loại được các lớp: 99,9% ảnh bị đoán thành COVID khi đánh giá bằng ảnh chỉ phổi, và 80,2% khi đánh giá bằng ảnh chỉ ngoài phổi.)*

Cặp nhầm nặng nhất ở Chương 3 giảm khi mô hình chỉ nhìn vùng phổi, từ 268 lỗi xuống 206 (Bảng 4.3), và giảm ở cả hai chiều. Khi chỉ nhìn ngoài phổi, cặp này lại tăng lên 296 lỗi. Tuy vậy "chỉ phổi" không tốt hơn: tổng lỗi của nó là 462, trong đó 256 lỗi nằm ngoài cặp Normal – Lung_Opacity (ảnh gốc chỉ có 81). Điều này khớp với mức giảm macro-F1 0,0535. Chương này không giải thích được vì sao phép che làm lệch cặp nhầm theo hướng đó.

**Bảng 4.4: Phép tách theo nguồn ảnh trên ba kịch bản cùng chế độ**

| Kịch bản | Lỗi cặp Normal–Lung_Opacity trong 2.237 ảnh RSNA | 197 ảnh Normal nguồn Mooney bị đoán thành Viral Pneumonia | Nhầm trực tiếp trong nhóm 400 ảnh Mooney |
| :--- | ---: | ---: | ---: |
| Ảnh gốc | 243 (10,86%) | 0 | 7/400 (1,75%) |
| Chỉ phổi | 186 (8,31%) | 0 | 5/400 (1,25%) |
| Chỉ ngoài phổi | 265 (11,85%) | 0 | 6/400 (1,50%) |

*(Nhóm 2.237 ảnh RSNA gồm 903 ảnh Lung_Opacity và 1.334 ảnh Normal nguồn RSNA; tỷ lệ là tổng lỗi hai chiều chia cho 2.237. Hai nhóm đều lập từ chính tập validation nên tổng số ảnh không đổi giữa các kịch bản.)*

Phép tách theo nguồn cho hai kết quả. Thứ nhất, trong nhóm 2.237 ảnh RSNA, Lung_Opacity và Normal cùng một nguồn, nên nguồn ảnh không thể là thứ tách hai lớp này. Vậy mà ở kịch bản "chỉ ngoài phổi", lỗi giữa chúng vẫn gần bằng ảnh gốc (11,85% so với 10,86%). Nghĩa là vùng ngoài mặt nạ phổi mang thông tin liên quan đến lớp, chứ không chỉ liên quan đến nguồn ảnh.

Thứ hai, trong 197 ảnh Normal nguồn Mooney, cùng nguồn với lớp Viral Pneumonia, không ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản, kể cả khi vùng phổi bị che hoàn toàn. Chiều ngược lại, số ảnh Viral Pneumonia bị đoán thành Normal là 7, 5 và 6. Như vậy nhầm trực tiếp giữa hai lớp trong nhóm 400 ảnh của Mooney là 7/400 = 1,75% (ảnh gốc), 5/400 = 1,25% (chỉ phổi) và 6/400 = 1,50% (chỉ ngoài phổi): cặp cùng nguồn này vẫn tách tốt khi chỉ còn vùng ngoài mặt nạ phổi. Recall của lớp Viral Pneumonia ở ba kịch bản là 94,09%, 92,12% và 94,58% (Bảng 4.1), còn recall của 197 ảnh Normal nguồn Mooney là 87,31%, 83,25% và 83,25%.

Hai kết quả này phải đọc cùng giới hạn của phép che. Ở chế độ chỉ ngoài phổi, mô hình không thấy cường độ điểm ảnh bên trong mặt nạ phổi, nhưng vẫn thấy hình dạng, diện tích và vị trí của vùng bị che (trung bình 23,6% ảnh, đo trên 20 mẫu thử). Các đặc trưng histogram, GLCM và LBP đều có thể phản ứng với vùng đen này và với đường viền của nó. Vùng ngoài mặt nạ cũng không phải vùng vô nghĩa: nó gồm tim, trung thất, vòm hoành và thành ngực, những nơi có thông tin lâm sàng.

Bản thân mặt nạ cũng có điểm yếu. Nó do mạng phân đoạn tự sinh chứ không phải bác sĩ vẽ: hai bài báo mô tả bộ dữ liệu không cung cấp mặt nạ chuẩn cho tập phân loại, và nguồn gốc mặt nạ của 2.686 ảnh thuộc nguồn Mooney không được mô tả. Vì vậy "ngoài mặt nạ phổi" chưa chắc là "ngoài phổi", và mặt nạ cũng có thể không bao hết vùng tổn thương. Tóm lại, điểm của chế độ chỉ ngoài phổi không cho biết thông tin mô hình dùng là thông tin về nguồn ảnh hay thông tin giải phẫu.

![Macro-F1 của năm kịch bản RQ3 kèm khoảng tin cậy và các mốc nền](../figures/04_macro_f1_kich_ban_rq3.png)

**Hình 4.1: Macro-F1 năm kịch bản RQ3 trên 3.174 ảnh validation, cột là điểm ước lượng và que chỉ khoảng tin cậy 95%**

Hai đường gạch ngang là mốc nền B0 (bộ luôn đoán Normal) và A0 (Random Forest đọc thuộc tính tệp ảnh), đọc từ tệp kết quả của hai mốc đó.

## 4.2. Tầm quan trọng đặc trưng theo 10 khối

Thí nghiệm hoán vị khối đo mức sụt macro-F1 khi một nhóm chiều đặc trưng bị xáo trộn ngẫu nhiên rồi mô hình suy luận lại, các khối còn lại giữ nguyên. Phép đo chạy trên đúng 3.174 ảnh validation. Mỗi khối được xáo trộn 10 lần, và con số sau dấu ± là dao động giữa 10 lần xáo trộn trên cùng tập ảnh, không phải độ bất định do chọn mẫu ảnh.

Mười khối gồm ba khối tổng hợp (histogram 64 chiều, GLCM 60 chiều, LBP 28 chiều) và bảy tiểu khối (năm thuộc tính GLCM, mỗi thuộc tính 12 chiều, cùng hai miền LBP 10 và 18 chiều). Ba khối tổng hợp cộng lại đúng bằng 152 chiều của nhóm ghép, còn bảy tiểu khối nằm lồng trong chúng, nên mức sụt của các khối không cộng được với nhau. Ba chế độ ảnh được đo riêng, với baseline là macro-F1 của chính kịch bản đó ở Bảng 4.1.

**Bảng 4.5: Mức sụt macro-F1 khi hoán vị từng khối (10 lần xáo trộn, trên 3.174 ảnh validation)**

| Khối | Số chiều | Ảnh gốc | Chỉ phổi | Chỉ ngoài phổi |
| :--- | ---: | ---: | ---: | ---: |
| Histogram | 64 | 0,2863 ± 0,0098 | 0,2658 ± 0,0050 | 0,2656 ± 0,0112 |
| GLCM | 60 | 0,3264 ± 0,0079 | 0,4960 ± 0,0035 | 0,3526 ± 0,0081 |
| LBP | 28 | 0,3590 ± 0,0119 | 0,4283 ± 0,0079 | 0,3590 ± 0,0103 |
| GLCM – contrast | 12 | 0,0485 ± 0,0048 | 0,3163 ± 0,0058 | 0,0694 ± 0,0045 |
| GLCM – dissimilarity | 12 | 0,0991 ± 0,0042 | 0,4655 ± 0,0066 | 0,1814 ± 0,0101 |
| GLCM – homogeneity | 12 | 0,1164 ± 0,0072 | 0,1787 ± 0,0056 | 0,1477 ± 0,0080 |
| GLCM – energy | 12 | 0,0598 ± 0,0036 | 0,0694 ± 0,0062 | 0,0359 ± 0,0039 |
| GLCM – correlation | 12 | 0,0479 ± 0,0054 | 0,2277 ± 0,0088 | 0,0511 ± 0,0028 |
| LBP bán kính 1, 8 điểm | 10 | 0,1548 ± 0,0063 | 0,2318 ± 0,0055 | 0,1341 ± 0,0043 |
| LBP bán kính 2, 16 điểm | 18 | 0,3077 ± 0,0058 | 0,2877 ± 0,0107 | 0,2746 ± 0,0063 |

*(Baseline của ba chế độ là 0,9024, 0,8490 và 0,8921.)*

Trên ảnh gốc, ba khối tổng hợp xếp theo mức sụt (Bảng 4.5) như sau: LBP 0,3590, GLCM 0,3264, histogram 0,2863. Khoảng cách giữa khối đầu và khối cuối là 0,0727, hơn sáu lần dao động giữa các lần xáo trộn. Khi chỉ còn vùng phổi, thứ tự đổi: GLCM nhảy lên 0,4960 (tăng 0,1696 so với ảnh gốc) và vượt LBP (0,4283). Hai thuộc tính dẫn đầu ở chế độ này là dissimilarity (0,4655) và contrast (0,3163). Khi chỉ còn vùng ngoài mặt nạ phổi, thứ tự quay về gần giống ảnh gốc: LBP 0,3590, GLCM 0,3526, histogram 0,2656. Trong bảy tiểu khối, LBP bán kính 2 (0,2746) cao nhất.

Dissimilarity và contrast đo độ chênh cường độ giữa các cặp điểm ảnh kề nhau. Khi phần lớn ảnh là nền đen, hai thuộc tính này có thể chủ yếu đo độ dài đường viền của vùng bị che. Khả năng đó chưa được loại trừ, nên chưa thể nói chúng đang đo kết cấu nhu mô phổi.

Cần lưu ý thêm rằng baseline của ba chế độ khác nhau (0,9024, 0,8490 và 0,8921), nên mỗi con số trong bảng là mức sụt của riêng mô hình đó. GLCM sụt nhiều hơn ở chế độ chỉ phổi cho thấy khối này đóng góp nhiều hơn trong mô hình chỉ nhìn vùng phổi, nhưng chưa cho phép kết luận GLCM quan trọng hơn LBP trong cùng một mô hình.

## 4.3. Các giả thuyết chưa kiểm chứng về vùng ngoài mặt nạ phổi

Các nhận định trong mục này là giả thuyết. Chúng không được kiểm chứng riêng trong đề tài, và được nêu ra để phân định rõ phần đo được với phần diễn giải, đúng cam kết ở mục 1.4.

**Đặc điểm giải phẫu lồng ngực trẻ nhỏ ở lớp Viral Pneumonia.** Khi toàn bộ vùng phổi bị che đen, mô hình vẫn phân loại đúng 94,58% ảnh lớp này, recall cao hơn ảnh gốc 0,49 điểm. Precision lại thấp hơn (89,72% so với 91,39%), nên F1 của lớp thấp hơn (0,9209 so với 0,9272). Cả 1.345 ảnh lớp đều thuộc nguồn Mooney, và Chương 1 đã nêu khả năng đây là X-quang nhi khoa từ nghiên cứu của Kermany và cộng sự [3]. Từ đó có giả thuyết rằng mô hình nhận ra lớp này nhờ đặc điểm giải phẫu lồng ngực trẻ nhỏ chứ không cần tổn thương phổi.

Giả thuyết này chưa được kiểm chứng, và bằng chứng hiện có còn đi ngược một phần. 197 ảnh Normal cùng nguồn Mooney, vì thế nhiều khả năng cùng lứa tuổi, không ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản, kể cả khi chỉ còn vùng ngoài mặt nạ phổi (Bảng 4.4). Nếu tín hiệu phân biệt chỉ là "ảnh nhi khoa" thì nhóm này đáng ra phải bị nhầm. Bộ dữ liệu không có thông tin tuổi, nên không thể xác nhận các ảnh đó là của trẻ em, cũng không tách được phần đóng góp của hình học lồng ngực (giới hạn tương tự đã nêu ở mục 2.5).

**Ký hiệu thiết bị và dấu vết xuất tệp ở lớp COVID.** Khi chỉ còn vùng ngoài mặt nạ phổi, mô hình vẫn phân loại đúng 94,79% ảnh COVID (precision 93,39%, F1 0,9409) dù không thấy vùng mờ trong phổi. Lớp COVID ghép từ nhiều kho nên có thể mang theo ký hiệu máy chụp, chữ L/R in đậm ngoài thành ngực hay độ tương phản nền riêng của từng kho. Giả thuyết là những dấu vết xuất tệp và ký hiệu thiết bị đó giúp mô hình nhận ra COVID từ vùng ngoài mặt nạ phổi. Thí nghiệm RQ3 không tách riêng từng loại dấu hiệu, nên chưa chỉ ra được dấu hiệu cụ thể nào đang được dùng.

**Dịch chuyển phân phối khi che lúc suy luận.** Khi học trên ảnh gốc rồi gặp ảnh chỉ còn vùng phổi, macro-F1 tụt xuống 0,0723 và 3.172 trong 3.174 ảnh bị đoán thành COVID. Khi gặp ảnh chỉ còn vùng ngoài mặt nạ phổi, macro-F1 giảm 0,6940 so với ảnh gốc và 80,2% ảnh bị đoán thành COVID. Giả thuyết là việc che một vùng làm đổi phân phối của cả ba khối đặc trưng, vì histogram, GLCM và LBP đều bị chi phối bởi dải giá trị 0 màu đen, nên mô hình dự đoán lệch hẳn so với chế độ đã học. Đề tài không đo phân phối đặc trưng theo từng chế độ ảnh, nên chưa có bằng chứng trực tiếp cho cơ chế này.

Tổng hợp lại, chương này đo được ba điều. Thứ nhất, mô hình vẫn đạt macro-F1 0,8921 khi chỉ còn vùng ngoài mặt nạ phổi, tức vùng này đủ thông tin để phân biệt bốn lớp, và phép tách theo nguồn cho thấy nó còn tách được hai lớp cùng nguồn RSNA. Thứ hai, che nhất quán ở cả huấn luyện lẫn đánh giá chỉ làm macro-F1 giảm 0,0103 (che vùng trong phổi) hoặc 0,0535 (che vùng ngoài mặt nạ phổi). Thứ ba, che riêng lúc đánh giá khiến mô hình học trên ảnh gốc gần như mất khả năng phân loại.

Điều chưa biết cũng rõ không kém. Chương này không xác định được mô hình dùng đặc điểm nào trong vùng ngoài mặt nạ phổi, và không xác định được đó có phải lối tắt theo nghĩa của Geirhos và cộng sự [4] hay không. Nghiên cứu [5] ghi nhận mô hình CXR có thể giảm hiệu năng khi sang cơ sở y tế khác. Vì vậy điểm validation cao trên bộ dữ liệu ghép nhiều nguồn này chưa bảo đảm mô hình hoạt động tương tự ở nơi khác (mục 6.3).

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Nguồn mục 4.1:** `results/report_rq3/r1_summary.csv` (macro-F1, khoảng tin cậy, precision/recall/F1 từng lớp của năm kịch bản), `results/report_rq3/r4_sampling_error.csv` (accuracy), `results/report_rq3/r3_shortcut_bootstrap.csv` (năm phép so ghép cặp), `results/report_rq3/r2_normal_lung_opacity.csv` (cặp nhầm Normal–Lung_Opacity của từng kịch bản) và `results/report_rq3/r1_confusion_matrices.json`. Thiết kế năm kịch bản, quy tắc phép so sánh chính và mục bắt buộc trình bày lấy từ `results/rq3_comparison_protocol_record.md` mục 2; quyết định giữ `orig_to_orig` lấy từ `results/rq3_shortcut_learning_conclusion.md` mục 2 và 4.
- **Mốc nền dùng ở mục 4.1:** B0 = 0,1627 đọc từ `results/b0_majority/metrics.json`; A0 = 0,2397 đọc từ `results/a0_shortcut/metrics.json` (khóa `random_forest`) – bộ này đọc thuộc tính tệp ảnh, cùng cách mô tả như mục 3.1 của Chương 3. Mốc histogram với Random Forest được đăng ký trước khi chạy lô full ở mức 0,7852 (`results/threshold_v3.md` mục 4); lô full RQ1 sau đó đo được 0,7829 (`results/report_rq1/r1_summary.csv`, dòng `hist`, trung bình ba seed), nên báo cáo dùng số đo có tệp nguồn đi kèm. Phép so đó khác bộ phân loại và nhóm đặc trưng nên chỉ mang tính mốc đăng ký trước, không phải so cùng điều kiện.
- **Con số 0,0724** là macro-F1 của một bộ phân loại đọc toàn bộ ảnh về nhãn COVID, tính từ chính cột nhãn thực trong `results/rq3_ghep_svm_orig_to_orig_s42/preds_val.csv`. Tỷ lệ ảnh bị đoán thành COVID (99,9% và 80,2%) đếm từ cột nhãn dự đoán của hai kịch bản nhiễu tương ứng.
- **Bảng 4.3:** `results/report_rq3/r2_normal_lung_opacity.csv`; mẫu số cố định 903 ảnh Lung_Opacity và 1.531 ảnh Normal, đúng mẫu số của Bảng 3.6. Tổng lỗi của kịch bản chỉ giữ vùng phổi là 462 ảnh, tính từ ma trận nhầm lẫn trong `r1_confusion_matrices.json` (3.174 − 2.712 nhãn đúng).
- **Bảng 4.4:** cột lỗi cặp tính trên nhóm 2.237 ảnh cùng nguồn RSNA (903 Lung_Opacity + 1.334 Normal RSNA); cột nguồn Mooney tính trên nhóm 400 ảnh (203 Viral Pneumonia + 197 Normal nguồn Mooney). Cột nhầm trực tiếp của nhóm 400 ảnh là tổng hai chiều nhầm giữa Viral Pneumonia và Normal nguồn Mooney (7 + 0, 5 + 0, 6 + 0) chia cho 400, đếm từ ba tệp `preds_val.csv` cùng nguồn với cột trước. Nguồn ảnh của lớp Normal lấy từ `results/eda/normal_source_labels.csv` ghép với `splits/split_v1.csv`; nhãn dự đoán của ba kịch bản lấy từ `results/rq3_ghep_svm_{orig_to_orig,lung_to_lung,out_to_out}_s42/preds_val.csv`. Tỷ lệ 10,86 / 8,31 / 11,85% là tổng hai chiều nhầm chia cho 2.237. Lớp Lung_Opacity toàn bộ thuộc cuộc thi RSNA và lớp Viral Pneumonia toàn bộ thuộc nguồn Mooney (mục 2.1 của Chương 2), nên hai nhóm này thực sự đồng nguồn.
- **Mặt nạ phổi:** kích thước 256 × 256 nội suy về 299 × 299 bằng láng giềng gần nhất như mục 2.1 của Chương 2; kết quả kiểm tra trên 20 mẫu thử (`empty_masks_count = 0`, trọng tâm gần trung tâm, `lung_fraction_mean = 0,2361`) lấy từ `results/rq3_comparison_protocol_record.md` mục 1. Mặt nạ do mạng Modified U-Net sinh, không có mặt nạ chuẩn cho tập phân loại và không có mô tả nguồn gốc mặt nạ cho 2.686 ảnh thuộc nguồn Mooney: `docs/dataset_provenance.md` mục 3.2 và hàng H5.
- **Mức giảm recall ở mục 4.1** (COVID −9,13 điểm, Lung_Opacity −3,54, Viral Pneumonia −1,97, Normal −1,83, và −0,93 của COVID ở kịch bản chỉ giữ vùng ngoài mặt nạ phổi) tính bằng phép trừ hai cột đã làm tròn của Bảng 4.1; nếu tính từ giá trị chưa làm tròn, mức COVID là −9,12.
- **Nguồn mục 4.2:** `results/rq3_permutation_importance.csv` (10 khối × 3 chế độ, `importance_mean`, `importance_std`, `n_repeats = 10`; seed 42 ghi ở `results/rq3_comparison_protocol_record.md` mục 2.3). Hoán vị chạy trên đúng 3.174 ảnh validation (`src/rq3_runner.py`, hàm `compute_block_permutation_importance`), `importance_std` tính theo mẫu (n − 1) và là dao động giữa các lần xáo trộn trên cùng tập ảnh. Ba khối tổng hợp chiếm toàn bộ 152 chiều của nhóm ghép (64 + 60 + 28); bảy tiểu khối là 5 thuộc tính GLCM (12 chiều mỗi khối) và 2 miền LBP (10 và 18 chiều). Hai ô LBP ở chế độ ảnh gốc và chỉ ngoài phổi cùng là 0,3590 sau làm tròn bốn chữ số; giá trị gốc trong `results/rq3_permutation_importance.csv` là 0,359017 và 0,359022, nên đây là trùng hợp làm tròn chứ không phải lỗi chép.
- **Giả thuyết ở mục 4.3:** không lấy lại các khẳng định nhân quả của `results/error_analysis/error_analysis_summary.md` (độ sáng, viền khung chụp, thiết bị) vì chúng không kiểm chứng được từ ảnh. Thành phần nhiều nguồn của lớp COVID lấy theo mục 2.1 của Chương 2 và chú thích chân trang của mục đó; nhận định về lứa tuổi gắn với [3] và `docs/dataset_provenance.md` mục 3.3 (không có tuổi trong metadata). Các trích dẫn [3], [4], [5] đã có ở danh mục tài liệu của Chương 1 nên không phát sinh số thứ tự mới.
- **Hình 4.1:** sinh bằng `python -m scripts.report_figures_rq3` từ `results/report_rq3/r1_summary.csv` (macro-F1 và khoảng tin cậy năm kịch bản) cùng hai đường mốc đọc từ `results/b0_majority/metrics.json` và `results/a0_shortcut/metrics.json`. Kiểm thử `tests/test_report_figures_rq3.py` giữ thứ tự kịch bản và đối chiếu hai đường mốc với tệp nguồn.
