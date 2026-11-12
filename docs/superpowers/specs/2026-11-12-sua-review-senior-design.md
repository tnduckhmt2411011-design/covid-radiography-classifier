# Spec: Sửa các điểm review senior trên sáu chương báo cáo

- Ngày: 12/11/2026
- Trạng thái: đã duyệt thiết kế (bản vá 12 lỗ hổng), chờ thi công
- Nguồn: review senior "Rà chéo sáu chương (bản sửa)" + đợt kiểm chứng của AI agent đối với mã nguồn và CSV/JSON/record trong kho

## 1. Mục tiêu

Dọn các mâu thuẫn nội bộ và lỗi trình bày mà senior nêu, đã được kiểm chứng lại từng điểm đối với tệp báo cáo và nguồn số liệu. Sau đợt này: sáu chương không còn tự mâu thuẫn; mọi khẳng định trong thân bài truy được về nguồn; các mâu thuẫn đã sửa bị chặn bởi phép kiểm thử.

Phạm vi không gồm: thay đổi môi trường chạy (không thêm `nbformat` vào `demo/requirements.txt`), đo mới trên dữ liệu ngoài kho (mặt nạ phổi 21.165 tệp nằm ngoài repo), sinh lại hình, và đồng bộ `slides/` (các tệp này chưa tracked, xử lý ở lượt riêng).

## 2. Nguyên tắc thực thi

1. Số liệu mới chỉ từ nguồn có sẵn trong kho, tính lại bằng script rồi mới ghi vào báo cáo: tỷ lệ nhóm Mooney 400 ảnh tính từ `results/rq3_ghep_svm_{orig_to_orig,lung_to_lung,out_to_out}_s42/preds_val.csv` ghép `results/eda/normal_source_labels.csv`; hai giá trị LBP đọc từ `results/rq3_permutation_importance.csv`.
2. Văn phong theo `docs/report_standards.md` và `docs/academic_writing_guide.md`: dấu phẩy thập phân, chấm phân cách hàng nghìn, không dấu gạch dài trong câu mới, câu ngắn, số liệu làm chủ ngữ.
3. Chương 1–4 chỉ dùng số validation. Mọi câu mới không nói nguyên nhân chênh lệch validation–test.
4. Sửa ghi chú kỹ thuật chỉ để chỉ nguồn số; bỏ lịch sử sửa đổi và tham chiếu số dòng.
5. Không stage tệp không liên quan (`results/report_rq*/bootstrap_config.json` đang modified).

## 3. Bảng sửa đổi (nguyên văn cũ → mới)

### 3.1. `report/01_gioi_thieu.md`

E1.1 (N2). Cũ: "nhờ nhận ra khung viền, độ sáng nền, cách xử lý hậu kỳ hoặc kích thước ảnh đặc trưng của nguồn đó, trong khi không hề định vị tổn thương phổi."
Mới: "nhờ nhận ra khung viền, độ sáng nền hoặc cách xử lý hậu kỳ đặc trưng của nguồn đó, trong khi không hề định vị tổn thương phổi."
Cơ sở: cả 21.165 ảnh đều 299 × 299 (ghi chú mục 2.2), kích thước không thể là tín hiệu phân biệt nguồn.

E1.2 (N1). Cũ: "Bộ dữ liệu ghép từ nhiều nguồn nên nguy cơ trên là thực tế, và đề tài đo nó trực tiếp."
Mới: "Bộ dữ liệu ghép từ nhiều nguồn nên nguy cơ trên là thực tế. Đề tài kiểm tra khả năng đó bằng phép che vùng ảnh ở RQ3, không tách riêng từng loại dấu vết."

E1.3 (N1). Cũ: "Câu hỏi thứ ba dùng để kiểm tra nghi vấn lối tắt: nếu mô hình vẫn cho macro-F1 cao khi chỉ còn vùng ngoài mặt nạ phổi thì nhiều khả năng nó dựa vào tín hiệu không liên quan đến tổn thương; nếu macro-F1 giảm mạnh thì vùng phổi đóng góp phần lớn thông tin."
Mới: "Câu hỏi thứ ba khảo sát bằng phép che: nếu mô hình vẫn đạt macro-F1 cao khi chỉ còn vùng ngoài mặt nạ phổi thì vùng này đủ thông tin để phân loại; thông tin đó có phải tín hiệu của nguồn ảnh hay là thông tin giải phẫu thì phép đo không tự phân biệt được."

E1.4 (N7). Cũ: "**RQ3.** Che hoặc cắt ảnh theo mặt nạ phổi có làm thay đổi macro-F1 không, và mức thay đổi đó cho biết gì về mức phụ thuộc của mô hình vào vùng ngoài mặt nạ phổi?"
Mới: "**RQ3.** Che vùng ảnh theo mặt nạ phổi có làm thay đổi macro-F1 không, và mức thay đổi đó cho biết gì về mức phụ thuộc của mô hình vào vùng ngoài mặt nạ phổi?"
Cơ sở: mục 4.1 ghi khung ảnh giữ nguyên, không cắt.

E1.5 (N8). Cũ: "Mọi thành phần ngẫu nhiên dùng seed 42, 43 và 44."
Mới: "Các bộ phân loại có thành phần ngẫu nhiên chạy trên ba seed 42, 43 và 44; các bộ còn lại và RQ3 dùng seed 42."
Cơ sở: mục 2.7 (ba bộ tất định chạy một seed 42), Bảng 3.3 (1 seed đối với SVM/LR/k-NN), mục 4.1 (RQ3 seed 42).

E1.6 (N10). Cũ: "Vì vậy hai lần chạy cho 0,8599 và 0,8582, chênh nhau xấp xỉ 0,002."
Mới: "Hai lần chạy cho 0,8599 và 0,8582, chênh nhau xấp xỉ 0,002, nhỏ hơn độ lệch chuẩn giữa các seed của từng phép đo (mục 3.3)."
Cơ sở: mục 3.3 đã thận trọng về chênh 0,0017 này.

E1.7 (N6, Bảng 1.1, dòng RQ3, cột quy tắc). Cũ: "Báo cáo toàn bộ 5 kịch bản, không loại kịch bản nào khỏi báo cáo"
Mới: "Báo cáo toàn bộ 5 kịch bản, không loại kịch bản nào; phép so chính (ảnh gốc − chỉ phổi, chênh tối thiểu +0,005 và khoảng tin cậy 95% không chứa 0) và phép so bắt buộc (chỉ ngoài phổi − chỉ phổi) đã chốt trước khi xem điểm"
Cơ sở: Bảng 4.2 của Chương 4 ghi hai vai trò "Phép so chính, chốt trước khi xem điểm" và "Bắt buộc trình bày theo biên bản RQ3".

E1.8 (bỏ mã nội bộ). Cũ: "Đề tài không dùng học sâu (ràng buộc H7): một bài kiểm thử tự động quét…"
Mới: "Đề tài không dùng học sâu: một bài kiểm thử tự động quét…"

E1.9. Cũ (Bảng 1.2): "| Không đọc tập test cho bất kỳ quyết định nào trong RQ1–RQ3 (H2) |"
Mới: "| Không đọc tập test cho bất kỳ quyết định nào trong RQ1–RQ3 |"

E1.10. Cũ (Bảng 1.2): "| Mọi bước học từ dữ liệu chỉ fit trên train (H6) |"
Mới: "| Mọi bước học từ dữ liệu chỉ fit trên train |"

E1.11 (N1). Cũ: "4. **Đo mức phụ thuộc vào vùng ngoài mặt nạ phổi (RQ3).** Năm kịch bản che mặt nạ phổi kết hợp permutation importance trên 10 khối đặc trưng định lượng phần đóng góp của vùng phổi so với phần còn lại của ảnh. Chương 4 trình bày số đo; mọi diễn giải về chênh lệch đều ghi là giả thuyết chưa kiểm chứng (Quy tắc D4)."
Mới: "4. **Đo mức phụ thuộc vào vùng ngoài mặt nạ phổi (RQ3).** Năm kịch bản che mặt nạ phổi và phép hoán vị 10 khối đặc trưng đo mức thay đổi hiệu năng khi vùng phổi bị che, trên 3.174 ảnh validation. Chương 4 trình bày số đo; mọi diễn giải về chênh lệch đều ghi là giả thuyết chưa kiểm chứng."

E1.12 (N1). Cũ: "Chương 4 giải quyết RQ3 bằng năm kịch bản che mặt nạ phổi."
Mới: "Chương 4 khảo sát RQ3 bằng năm kịch bản che mặt nạ phổi."

E1.13 (N3). Cũ: "tài liệu của các chương sau đánh tiếp từ [9]."
Mới: "tài liệu của các chương sau đánh tiếp từ [7]."

E1.14 (ghi chú, sửa chú thích D4 sai và bỏ mã). Cũ: "- **Mã hiệu:** H2, H6, H7 và Quy tắc D4 chỉ dùng trong ngoặc để tra cứu chéo với `results/threshold_v3.md`; nội dung đã diễn giải bằng lời trong chương. `UNLOCK_RECORD.json` là biên bản ghi lần mở khóa tập test duy nhất, có commit và thời điểm."
Mới: "- **Mã hiệu nội bộ:** các ràng buộc trong chương diễn giải bằng lời, không dùng mã hiệu; mã H2, H6, H7 trong `results/threshold_v3.md` chỉ để tra cứu chéo. `UNLOCK_RECORD.json` là biên bản ghi lần mở khóa tập test duy nhất, có commit và thời điểm."
Cơ sở: D4 không tồn tại trong `results/threshold_v3.md` (đã grep); D4–D1 trong `results/final_test_protocol_record.md` mang nghĩa khác.

### 3.2. `report/02_du_lieu_va_phuong_phap.md`

E2.1 (N4 + N5). Cũ: "Lựa chọn này có cái giá của nó: các cặp có khoảng cách Hamming lớn hơn 0 và không quá 4 không được gom, nên có thể nằm ở hai tập khác nhau."
Mới: "Giá của lựa chọn này là các cặp có khoảng cách Hamming lớn hơn 0 và không quá 4 không được gom, nên có thể nằm ở hai tập khác nhau; mục 2.5 chứng minh các mức này chỉ có thể là 2 và 4."

E2.2 (N4). Cũ: "Bản ghi mở khóa lưu lần mở khóa đó cùng commit, mã băm SHA-256 của tệp split, mã băm của chuỗi xác nhận do tác giả ký, và macro-F1 validation 0,9024 của mô hình dùng cho lần chạy, chính là mốc được trình bày lại ở Chương 3."
Mới: "Bản ghi mở khóa lưu lần mở khóa đó cùng commit, mã băm SHA-256 của tệp split, mã băm của chuỗi xác nhận do người dùng gõ, và macro-F1 validation 0,9024 của mô hình dùng cho lần chạy, chính là mốc được trình bày lại ở Chương 3."
Cơ sở: `results/final_test_protocol_record.md` mục 2, cổng G4.

E2.3 (N4). Cũ: "4. Chuỗi xác nhận do tác giả ký phải khớp mã băm đã đăng ký."
Mới: "4. Người dùng gõ chuỗi xác nhận và bộ chạy chỉ đối chiếu qua mã băm SHA-256."

E2.4 (N4 + vá 4). Cũ: "5. Macro-F1 validation phải tái lập được trên cùng cấu hình."
Mới: "5. Macro-F1 validation phải tái lập được trong dung sai 0,002 quanh mốc 0,9024 trên cùng cấu hình."
Cơ sở: Chương 5 và cổng G5.

E2.5 (N4). Cũ: "6. Báo cáo phải công bố đầy đủ các chỉ số đã đăng ký trước."
Mới: "6. Bản ghi mở khóa phải được ghi ra đĩa trước khi đọc ảnh test đầu tiên."
Cơ sở: cổng G6. Yêu cầu "công bố đầy đủ chỉ số" vẫn còn trong báo cáo ở mục 5.4 (bốn quyết định), nên không mất nội dung.

E2.6 (N5). Cũ: "Trên toàn bộ dữ liệu vẫn còn 1.570 cặp có khoảng cách Hamming lớn hơn 0 và không quá 4, trong đó 735 cặp nằm ở hai tập khác nhau (Bảng 2.4)."
Mới: "Trên toàn bộ dữ liệu vẫn còn 1.570 cặp có khoảng cách Hamming lớn hơn 0 và không quá 4, tức mức 2 và 4, trong đó 735 cặp nằm ở hai tập khác nhau (Bảng 2.4)."

E2.7 (điểm nhỏ). Cũ: "Thông tin đó đến từ vùng phổi hay từ đặc điểm nguồn ảnh là điều RQ3 phải đo."
Mới: "Thông tin đó đến từ đâu là điều RQ3 khảo sát bằng phép che."
Cơ sở: Chương 4 cho thấy còn tim, trung thất, vòm hoành, không chỉ hai lựa chọn.

E2.8 (điểm nhỏ). Cũ: "HOG không nằm trong nhóm này, nên kích thước của nó chỉ bằng khoảng 1/68 nhóm HOG (152 so với 10.404 chiều)."
Mới: "HOG không nằm trong nhóm này, nên nhóm ghép chỉ có khoảng 1/68 số chiều của HOG (152 so với 10.404 chiều)."

E2.9 (N9). Cũ: "Ba bộ phân loại tất định (Logistic Regression, k-NN, SVM) mỗi bộ chạy một lần với seed 42."
Mới: "Ba bộ phân loại tất định về nhãn dự đoán (Logistic Regression, k-NN, SVM) mỗi bộ chạy một lần với seed 42; riêng bốn cột xác suất của SVM có phụ thuộc seed do nội suy Platt (mục 3.3)."
Cơ sở: mục 3.3 của Chương 3.

E2.10 (điểm nhỏ). Cũ: "Câu hỏi mô hình khái quát ra sao trên ảnh chưa từng thấy thuộc về Chương 4 và Chương 5."
Mới: "Câu hỏi mô hình khái quát ra sao trên ảnh chưa từng thấy thuộc về Chương 5, và được xét lại trong giới hạn của Chương 6 (mục 6.2)."

E2.11 (N5). Cũ: "Ảnh trong cùng nhóm pHash được gom về cùng một tập, nhưng các cặp gần trùng ở khoảng cách Hamming từ 1 đến 4 thì không, và bộ dữ liệu cũng không có mã bệnh nhân để gom theo bệnh nhân."
Mới: "Ảnh trong cùng nhóm pHash được gom về cùng một tập, nhưng các cặp gần trùng ở khoảng cách Hamming từ 2 đến 4 thì không, và bộ dữ liệu cũng không có mã bệnh nhân để gom theo bệnh nhân."

E2.12 (ghi chú). Cũ: "Tiêu đề cũng được đổi ở `docs/report_standards.md` mục 3.2 và `report/README.md` dòng 2.2, cả ba chỗ giờ khớp nhau."
Mới: "Tiêu đề cũng được đổi ở `docs/report_standards.md` mục 3.2 và `report/README.md` mục 3, hàng 2.2, cả ba chỗ giờ khớp nhau."

E2.13 (ghi chú, nhãm bảng). Cũ: "số trong Bảng 2.1 và các số dẫn xuất (AUC, khoảng cách đến 0,5, 46,5%, 140 ảnh RGB) sinh bằng `python -m src.eda_brightness`"
Mới: "số trong Bảng 2.2 và các số dẫn xuất (AUC, khoảng cách đến 0,5, 46,5%, 140 ảnh RGB) sinh bằng `python -m src.eda_brightness`"

E2.14 (ghi chú). Cũ: "`splits/README.md` mục 3 (phương pháp MD5 + pHash + Union-Find, 178 nhóm, 401 ảnh, 0 nhóm lệch nhãn ở $T = 0$) và `notebooks/02_duplicates_and_split.ipynb` cell 4–5."
Mới: "`splits/README.md` mục 3 (phương pháp MD5 + pHash + Union-Find, 178 nhóm, 401 ảnh, 0 nhóm lệch nhãn ở $T = 0$) và các cell định nghĩa pHash, so ngưỡng và chia tập của `notebooks/02_duplicates_and_split.ipynb`."

E2.15 (ghi chú). Cũ: "- **Nguồn mục 2.5:** `docs/roadmap.md` dòng 187 (735 cặp: 325 Train–Test, 335 Train–Val, 75 Val–Test; 229 lệch nhãn, 506 cùng nhãn) và …"
Mới: "- **Nguồn mục 2.5:** bảng quyết định của `docs/roadmap.md`, hàng "Quyết định giữ `split_v1` hay tạo `split_v2`" (735 cặp: 325 Train–Test, 335 Train–Val, 75 Val–Test; 229 lệch nhãn, 506 cùng nhãn) và …"

E2.16 (ghi chú, bỏ lịch sử sửa). Cũ: "Tỷ lệ: 273/3.174 = 8,60% → 8,6%; 243/3.176 = 7,65% → 7,7% (bản trước ghi 7,6%, đã sửa theo quy tắc làm tròn)."
Mới: "Tỷ lệ: 273/3.174 = 8,60% → 8,6%; 243/3.176 = 7,65% → 7,7%."

### 3.3. `report/03_ket_qua_rq1_rq2.md`

E3.1 (điểm nhỏ). Cũ: "hai lớp vừa cùng nguồn RSNA vừa là cặp khó tách nhất về mặt lâm sàng"
Mới: "hai lớp vừa cùng nguồn RSNA vừa là cặp khó tách về mặt lâm sàng"
Cơ sở: khẳng định y khoa không có nguồn; bỏ "nhất" theo đề xuất senior.

E3.2 (ghi chú). Cũ: "SVM chạy một seed vì nhãn dự đoán của `SVC` không phụ thuộc seed; riêng xác suất sinh từ nội suy Platt có kiểm định chéo nội bộ theo seed (`src/rq2_runner.py` dòng 433, `SVC(probability=True, random_state=seed)`), nên mọi phép so sánh trong chương đều dựa trên nhãn."
Mới: "SVM chạy một seed vì nhãn dự đoán của `SVC` không phụ thuộc seed; riêng xác suất sinh từ nội suy Platt có kiểm định chéo nội bộ theo seed (`SVC(probability=True, random_state=seed)` trong hàm huấn luyện của `src/rq2_runner.py`), nên mọi phép so sánh trong chương đều dựa trên nhãn."

E3.3 (ghi chú, bỏ lịch sử sửa). Cũ: "349 − 268 = 81 lỗi nằm trên năm cặp còn lại của Bảng 3.6 (31 + 20 + 23 + 6 + 1 = 81). Bản trước ghi "bốn cặp", đã sửa thành năm."
Mới: "349 − 268 = 81 lỗi nằm trên năm cặp còn lại của Bảng 3.6 (31 + 20 + 23 + 6 + 1 = 81)."

### 3.4. `report/04_hoc_loi_tat_rq3.md`

E4.1 (điểm nhỏ). Cũ: "vị trí của vùng bị che (trung bình 23,6% ảnh)"
Mới: "vị trí của vùng bị che (trung bình 23,6% ảnh, đo trên 20 mẫu thử)"
Lần nhắc đầu ở đầu mục 4.1 đã ghi "Chạy thử kỹ thuật trên 20 mẫu", chỉ bổ sung định tính tại lần nhắc sau.

E4.2 (Mooney 400, nội dung mới). Cũ: "Chiều ngược lại, số ảnh Viral Pneumonia bị đoán thành Normal là 7, 5 và 6."
Mới: "Chiều ngược lại, số ảnh Viral Pneumonia bị đoán thành Normal là 7, 5 và 6. Như vậy nhầm trực tiếp giữa hai lớp trong nhóm 400 ảnh của Mooney là 7/400 = 1,75% (ảnh gốc), 5/400 = 1,25% (chỉ phổi) và 6/400 = 1,50% (chỉ ngoài phổi): cặp cùng nguồn này vẫn tách tốt khi chỉ còn vùng ngoài mặt nạ phổi."
Số đã kiểm lại từ CSV (VP→Normal = 7, 5, 6; Normal nguồn Mooney→Viral Pneumonia = 0, 0, 0).

E4.3 (Bảng 4.4, thêm cột). Đầu bảng:
Cũ: "| Kịch bản | Lỗi cặp Normal–Lung_Opacity trong 2.237 ảnh RSNA | 197 ảnh Normal nguồn Mooney bị đoán thành Viral Pneumonia |"
Mới: "| Kịch bản | Lỗi cặp Normal–Lung_Opacity trong 2.237 ảnh RSNA | 197 ảnh Normal nguồn Mooney bị đoán thành Viral Pneumonia | Nhầm trực tiếp trong nhóm 400 ảnh Mooney |"
Ba hàng dữ liệu thêm ô: "7/400 (1,75%)", "5/400 (1,25%)", "6/400 (1,50%)".

E4.4 (ghi chú Bảng 4.4). Bổ sung sau câu mô tả cột nguồn Mooney:
"Cột nhầm trực tiếp của nhóm 400 ảnh là tổng hai chiều nhầm giữa Viral Pneumonia và Normal nguồn Mooney (7 + 0, 5 + 0, 6 + 0) chia cho 400, đếm từ ba tệp `preds_val.csv` cùng nguồn với cột trước."

E4.5 (ghi chú, trùng hợp LBP). Bổ sung vào bullet nguồn mục 4.2:
"Hai ô LBP ở chế độ ảnh gốc và chỉ ngoài phổi cùng là 0,3590 sau làm tròn bốn chữ số; giá trị gốc trong `results/rq3_permutation_importance.csv` là 0,359017 và 0,359022, nên đây là trùng hợp làm tròn chứ không phải lỗi chép."

E4.6 (điểm nhỏ). Cũ: "197 ảnh Normal cùng nguồn Mooney, vì thế cùng lứa tuổi suy ra, không ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản"
Mới: "197 ảnh Normal cùng nguồn Mooney, vì thế nhiều khả năng cùng lứa tuổi, không ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản"

### 3.5. `report/05_ket_qua_test_va_trien_khai.md`

E5.1 (N12). Cũ: "Thứ hai, bộ kiểm thử tự động gồm 341 phép kiểm thử trong 27 module (đếm tại thời điểm nộp), chạy đầy đủ được trên môi trường đã ghi ở mục 5.5.4."
Mới: "Thứ hai, bộ kiểm thử tự động gồm 344 phép kiểm thử trong 28 module (đếm tại thời điểm nộp), chạy được trên môi trường đã ghi ở mục 5.5.4. Trên môi trường đó một phép kiểm thử tính hợp lệ của notebook bị bỏ qua vì thiếu `nbformat`; các tính chất ép buộc nêu dưới đây do các phép còn lại của hai bộ kiểm thử notebook thực hiện, và các phép đó vẫn chạy trên môi trường đã ghi."

E5.2 (N12, ghi chú). Cũ: "…phần bỏ qua là bộ kiểm thử notebook khi môi trường không có `nbformat` (không thuộc `requirements.txt`)."
Mới: "…phần bỏ qua là `tests/test_inference_demo_notebook.py::test_notebook_is_valid_nbformat` (cần `nbformat`, không thuộc `requirements.txt`); 16 phép còn lại của bộ này, gồm phép chặn import framework học sâu, và toàn bộ `tests/test_final_test_report_and_notebook.py`, gồm phép kiểm tra notebook đánh giá đã được thực thi, đều chạy pass trên môi trường đã ghi."

E5.3 (N11). Cũ: "Trong lô 200 ảnh, 14 ảnh đầu của mỗi lượt nằm ở mức khoảng 27–30 ms; từ ảnh thứ 15, thời gian nhảy lên quanh 130 ms, kèm một đợt ngắn 200–349 ms ở ảnh 29 đến ảnh 86. Các lượt thứ hai và thứ ba ở mức cao ngay từ ảnh đầu tiên."
Mới: "Trong lô 200 ảnh, 14 ảnh đầu của lượt đầu nằm ở mức khoảng 27–30 ms; từ ảnh thứ 15, thời gian nhảy lên quanh 130 ms, kèm một đợt ngắn 200–349 ms ở ảnh 29 đến ảnh 86. Các lượt thứ hai và thứ ba ở mức cao ngay từ ảnh đầu tiên, không có ảnh nào trở lại mức dưới 35 ms."
Cơ sở: `results/demo_latency_sustained/per_image.csv`: chỉ 14 ảnh của lượt đầu dưới 0,035 giây; lượt 2 và 3 không có ảnh nào.

E5.4 (điểm nhỏ, dấu gạch dài). Cũ: "Chế độ tương tác của người dùng — tải lần lượt một ảnh, mỗi ảnh đứng sau một khoảng nghỉ — chỉ gần với bản ghi đầu khi số ảnh còn ít:"
Mới: "Chế độ tương tác của người dùng, tức tải lần lượt một ảnh và mỗi ảnh đứng sau một khoảng nghỉ, chỉ gần với bản ghi đầu khi số ảnh còn ít:"

E5.5 (điểm nhỏ, cổng theo tên tệp). Cũ: "Pipeline gồm năm bước. Tên tệp bị từ chối trước khi giải mã nếu trùng với một ảnh thuộc tập test."
Mới: "Pipeline gồm năm bước. Tên tệp bị từ chối trước khi giải mã nếu trùng với một ảnh thuộc tập test; cổng này đối chiếu theo tên tệp chứ không theo nội dung ảnh, nên đổi tên tệp là qua được, và nó chống nhầm lẫn chứ không chống cố ý."

E5.6 ([7], trích dẫn kho cụ thể, ghi theo nhóm). Cũ: "[7] Hugging Face, \"Hugging Face Hub documentation,\" 2026. [Online]. Available: https://huggingface.co/docs/hub/. [Accessed: 12-11-2026]."
Mới: "[7] Nhóm 10, Lớp Khoa học máy tính 2024, \"cxr-svm-demo: artifact bộ phân loại CXR bốn lớp,\" Hugging Face Hub, 2026. [Online]. Available: https://huggingface.co/duc16/cxr-svm-demo. [Accessed: 12-11-2026]."

E5.7 (ghi chú, dấu gạch dài). Cũ: "(17.989 ảnh, `time.process_time`) — khác đồng hồ và khác máy nên chỉ dùng làm mốc tham khảo."
Mới: "(17.989 ảnh, `time.process_time`); khác đồng hồ và khác máy nên chỉ dùng làm mốc tham khảo."

### 3.6. `report/06_thao_luan_gioi_han_huong_phat_trien.md`

E6.1 (N1). Cũ: "phép che mặt nạ định lượng được mức phụ thuộc vào vùng ngoài mặt nạ phổi (mục 4.1)"
Mới: "phép che mặt nạ đo được mức giữ hiệu năng khi chỉ còn vùng ngoài mặt nạ phổi (mục 4.1)"

E6.2 (lỗi chính tả). Cũ: "nên phần lệch do bước chọn có lẻ nhỏ."
Mới: "nên phần lệch do bước chọn có lẽ nhỏ."

E6.3 (N13). Cũ: "2. **Chặn gần trùng rồi đánh giá lại.** Chặn cả các cặp Hamming 2–4, chia lại tập, huấn luyện và đánh giá cùng cấu hình, để đo mức chênh trên chính tập validation hiện có (giới hạn 1)."
Mới: "2. **Chia lại tập sau khi chặn gần trùng.** Chặn cả các cặp Hamming 2–4, chia lại tập, rồi huấn luyện và đánh giá lại cùng cấu hình trên tập mới; phép đo bổ sung đã chạy (macro-F1 trên 273 ảnh có ảnh gần trùng và 2.901 ảnh còn lại, mục 2.5) chỉ dùng dự đoán có sẵn nên chưa tách được ảnh hưởng của bản gần trùng lúc huấn luyện (giới hạn 1)."

E6.4 (điểm nhỏ, tách vế). Cũ: "Thứ hai, kết quả RQ3 cho thấy mô hình dựa được vào vùng ngoài mặt nạ phổi, nên mô hình chỉ là minh hoạ phương pháp, chưa phải một công cụ chẩn đoán."
Mới: "Thứ hai, kết quả RQ3 cho thấy mô hình dựa được vào vùng ngoài mặt nạ phổi. Riêng về phạm vi sử dụng, mô hình là minh hoạ phương pháp chứ chưa phải một công cụ chẩn đoán, vì chưa được kiểm định lâm sàng."
Cơ sở: lý do "chưa phải công cụ chẩn đoán" là chưa kiểm định lâm sàng, không phải kết quả RQ3; mục 6.1 đã tách hai ý này.

E6.5 (ghi chú, dấu gạch dài). Thay toàn bộ dấu gạch dài trong ghi chú của chương bằng dấu chấm câu hoặc dấu hai chấm (kiểm tại thời điểm thi công, 1 vị trí).

### 3.7. `report/07_tai_lieu_tham_khao.md`

E7.1. Thay mục [7] bằng nguyên văn ở E5.6 (hai tệp phải giống nhau từng ký tự).

### 3.8. `docs/roadmap.md`

E8.1. Cũ: "Đã thống kê 735 cặp gần trùng (Hamming 1-4) khác split"
Mới: "Đã thống kê 735 cặp gần trùng (Hamming 2 hoặc 4) khác split"
Cơ sở: mục 2.5 của Chương 2 chứng minh khoảng cách luôn chẵn; đây là nguồn được báo cáo trích dẫn.

## 4. Hàng rào kiểm thử mới

Tệp mới `tests/test_report_consistency.py`, 3 phép, không phụ thuộc thư viện ngoài thư viện chuẩn nên chạy được trên cả hai môi trường:

1. `test_rq3_decision_rule_lists_registered_comparisons`: dòng RQ3 của Bảng 1.1 phải nêu cả hai phép so đã đăng ký (ô quy tắc chứa "chỉ phổi" và "ngoài phổi"); Bảng 4.2 phải có vai trò "Phép so chính" và "Bắt buộc trình bày".
2. `test_hamming_levels_are_even_levels_only`: thân bài `02_du_lieu_va_phuong_phap.md` và `06_thao_luan_gioi_han_huong_phat_trien.md` không được chứa "từ 1 đến 4" và phải chứa "từ 2 đến 4" hoặc "mức 2 và 4".
3. `test_chapter1_has_no_internal_codes_or_overclaim`: thân bài Chương 1 không chứa mã H2/H6/H7/D4 (theo ranh giới từ) và không chứa "giải quyết RQ3", "đo nó trực tiếp", "hoặc cắt".

Thân bài của một tệp = phần trước "## Tài liệu tham khảo phát sinh trong chương" và "## Ghi chú kỹ thuật".

## 5. Đồng bộ số và sinh lại nội dung

Thêm 3 phép → thu thập 344 phép trong 28 module; chạy đầy đủ 343 pass, 1 bỏ qua. Trình tự:

1. Tạo tệp mới (spec, nhật ký công việc, tệp test) rồi `git add` ba tệp đó trước khi chạy script sinh (Bảng B.1 đếm tệp đã tracked).
2. Chạy `python scripts/report_appendix_b.py` trên `.venv-demo`, dán Bảng B.1 và B.2 vào `report/08_phu_luc_a_c.md`; sửa câu Phụ lục A.1 thành "Toàn bộ 344 phép kiểm thử trong 28 module đã chạy được trên môi trường này (343 pass, 1 bỏ qua; mục 5.4 của Chương 5)."
3. Sửa `scripts/report_appendix_b.py`: docstring đổi "334 phép kiểm thử trong 26 module" thành câu đọc số tại thời điểm chạy.
4. Đồng bộ 344/28 và 343 pass: Chương 5 (thân bài E5.1 và ghi chú), Phụ lục A.1, `report/09_tom_tat_abstract.md` (cả bản tiếng Việt và English, cả dòng ghi nguồn), `docs/report_standards.md` mục 3.3, `report/README.md` (mọi chỗ chứa 341/27/340 pass).
5. Chạy `python scripts/report_frontmatter.py`; mục lục phải không đổi (32 bảng, 4 hình) vì không thêm bảng mới.
6. Quét `report/` và `docs/` tìm số cũ (334, 337, 341, "340 pass", "27 module") trước khi commit.

## 6. Xác minh

1. `pytest -q` trên `.venv-demo`: 343 passed, 1 skipped; `pytest --collect-only -q`: 344 tests collected.
2. Chạy bộ đối chiếu tổng hợp (script tạm, không commit) kiểm từng điểm: không còn "từ 1 đến 4", "tác giả ký", mã nội bộ ở Ch1, Bảng 1.1 dòng RQ3 đủ hai phép so, mục 5.5.4 ghi "lượt đầu", cổng tên tệp, [7] trùng khớp hai tệp, cột Mooney, dấu gạch dài đã bỏ.
3. Kiểm tra idempotent: chạy lại hai script sinh, `git diff` không đổi.
4. Chạy bộ test mới trên `.venv` (môi trường thiếu thư viện) để chắc chắn không bị lỗi thu thập.

## 7. Ngoài phạm vi

- Đồng bộ `slides/` (chưa tracked): số phép kiểm thử và cách diễn đạt RQ3 trong slide cần rà lại sau.
- Đo diện tích vùng phổi trên 21.165 mặt nạ: cần dataset root, đã ghi ở hướng phát triển 1.
- Thay đổi `demo/requirements.txt` hoặc môi trường đo.

## 8. Thứ tự thi công

1. Sửa sáu chương và tệp 07, roadmap (mục 3).
2. Viết `tests/test_report_consistency.py`, chạy thử trên cả hai môi trường.
3. Sinh lại Phụ lục B, đồng bộ số ở năm vị trí còn lại, sinh lại mục lục.
4. Xác minh toàn bộ, hai commit (nội dung; đồng bộ số và sinh lại), mở PR để người dùng tự merge.
